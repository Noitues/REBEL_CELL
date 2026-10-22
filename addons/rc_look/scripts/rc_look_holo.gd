class_name RcLookHolo
extends RefCounted
## LOOK-TOOLBOX module 15: the decrypted holo (ART_BIBLE §1.2: hacked corp intel). A translucent tinted glass over a
## blurred city, scanlines, slow scan bands, an edge-only RGB split and a cracked corp seal. A panel makes two
## materials with `material` (GLASS under its words, OVER above them), calls `apply` with its size, tint and the
## player's look state whenever either changes, and draws the seal with `draw_seal`. Every number comes from
## look_holo.tres and look_quality.tres (module "holo"); a flag or tier never reaches the panel, only `settings`.
## Pure apart from the materials it fills. View only.

const MODULE := &"holo"
const SHADER_PATH := "res://addons/rc_look/shaders/rc_holo.gdshader"
## Shader pass: the glass under the words, the scanlines and bands over them.
const GLASS := 0
const OVER := 1
## The seal's reference radius the config's px values are given at.
const SEAL_REF_RADIUS := 40.0
## Integer-hash multipliers of the seal's jitter (odd primes) and the hash's mixing multiplier.
const HASH_A := 73856093
const HASH_B := 19349663
const HASH_MIX := 1274126177
const HASH_BUCKETS := 10000
## Branch placement: the second kink index offset, and the sideways lift (share of the radius) of a branch tip.
const BRANCH_SALT := 100
const BRANCH_TIP_SALT := 200
const BRANCH_TIP_DROP := 0.3

static var _config: RcLookHoloConfig = null


## The default config (addons/rc_look/config/look_holo.tres), loaded once.
static func config() -> RcLookHoloConfig:
	if _config == null:
		_config = load(RcLookHoloConfig.DEFAULT_PATH)
	return _config


## A holo material for `pass_id` (GLASS or OVER).
static func material(pass_id: int) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(SHADER_PATH)
	m.set_shader_parameter(&"mode", pass_id)
	return m


## Every look value under `state` (shader parameter -> value, plus `backing_alpha`, the panel's local backdrop), from
## the config and the quality rules. `body_k` scales the glass tint and the scanlines for a bright hue (a corp's own
## luminance factor; 1 for none). Pure.
static func settings(state: RcLookQualityState, body_k: float = 1.0, cfg: RcLookHoloConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var q := RcLookQuality.of(MODULE, state)
	return {
		&"fill_share": float(q["fill_share"]) * body_k,
		&"fill_foot_share": c.fill_foot_share,
		&"glass_alpha": q["glass_alpha"],
		&"city_dim": c.city_dim,
		&"blur_lod": q["blur_lod"],
		&"scan_px": c.scan_px,
		&"scan_strength": float(q["scan_strength"]) * body_k,
		&"band_count": c.band_count,
		&"band_strength": q["band_strength"],
		&"band_trail": c.band_trail,
		&"band_seconds": c.band_seconds,
		&"band_roll": q["band_roll"],
		&"band_pose": c.band_pose,
		&"edge_px": c.edge_px,
		&"edge_glow_px": c.edge_glow_px,
		&"edge_glow_strength": q["edge_glow_strength"],
		&"edge_lift": c.edge_lift,
		&"split_px": q["split_px"],
		&"backing_alpha": q["backing_alpha"],
	}


## Fills `mat` (either pass) for a panel of `size` px: `settings` plus the panel rect, the corp `tint` and the dark
## `deep` colour. `overrides` replaces any shader parameter afterwards (a panel's own motion hook, an edge widened for
## contrast).
static func apply(mat: ShaderMaterial, size: Vector2, tint: Color, deep: Color, state: RcLookQualityState,
		body_k: float = 1.0, overrides: Dictionary = {}) -> void:
	var s := settings(state, body_k)
	s.erase(&"backing_alpha")
	s.merge(overrides, true)
	mat.set_shader_parameter(&"panel", Vector4(0.0, 0.0, size.x, size.y))
	mat.set_shader_parameter(&"tint", tint)
	mat.set_shader_parameter(&"deep", deep)
	for k: StringName in s:
		mat.set_shader_parameter(k, s[k])


## How far past its rect a panel's glass control must draw so the edge's split and glow are not cut (px).
static func bleed_px(state: RcLookQualityState) -> float:
	var s := settings(state)
	return float(s[&"split_px"]) + float(s[&"edge_glow_px"]) * 2.0 + 2.0


## The seal's fracture: a jagged line top to bottom through `centre` (a hash of `seed_id` kinks each point sideways; the
## same inputs always give the same line) and the side cracks as point lists.
## Returns {"line": PackedVector2Array, "branches": Array[PackedVector2Array]}.
static func crack(centre: Vector2, radius: float, seed_id: int, cfg: RcLookHoloConfig = null) -> Dictionary:
	var c := cfg if cfg != null else config()
	var line := PackedVector2Array()
	var n := maxi(c.crack_segments, 2)
	for i in n + 1:
		var t := float(i) / float(n)
		var j := 0.0 if i == 0 or i == n else (hash01(seed_id, i) - 0.5) * 2.0 * c.crack_jitter
		line.append(centre + Vector2(j * radius, (t - 0.5) * 2.0 * radius))
	var branches: Array[PackedVector2Array] = []
	for b in c.crack_branches:
		var at := clampi(1 + int(hash01(seed_id, BRANCH_SALT + b) * float(n - 1)), 1, n - 1)
		var dir := -1.0 if (b % 2) == 0 else 1.0
		var from := line[at]
		var tip := from + Vector2(dir * c.crack_branch_len * radius, (hash01(seed_id, BRANCH_TIP_SALT + b) - BRANCH_TIP_DROP) * radius)
		branches.append(PackedVector2Array([from, from.lerp(tip, 0.5), tip]))
	return {"line": line, "branches": branches}


## Draws the cracked seal on `ci` (call from its draw): the faint disc, the ring and an inner ring in `tint` cut open
## where the fracture crosses them, the crest (`crest` texture, or none) as two halves offset along the crack, then the
## fracture in `crack_color` with a glow. `radius` px; the config's px values scale with it. The crack reads by shape
## (a cut ring, offset halves), never by its colour alone. `seed_id` < 0 uses the config's seed.
static func draw_seal(ci: CanvasItem, centre: Vector2, radius: float, tint: Color, crack_color: Color,
		crest: Texture2D = null, seed_id: int = -1, cfg: RcLookHoloConfig = null) -> void:
	var c := cfg if cfg != null else config()
	var k := radius / SEAL_REF_RADIUS
	var sid := c.seal_seed if seed_id < 0 else seed_id
	var disc := tint
	disc.a = c.seal_disc_alpha
	ci.draw_circle(centre, radius, disc)
	var ring := tint
	ring.a = c.seal_ring_alpha
	var inner := radius - c.seal_inner_gap * k
	for pole in [-PI * 0.5, PI * 0.5]:
		ci.draw_arc(centre, radius, pole + c.ring_gap, pole + PI - c.ring_gap, 24, ring, c.seal_ring_px * k, true)
		ci.draw_arc(centre, inner, pole + c.ring_gap, pole + PI - c.ring_gap, 24, ring, c.seal_ring_inner_px * k, true)
	if crest != null:
		var half := radius * c.crest_share
		var ts := crest.get_size()
		var box := Rect2(centre - Vector2(half, half), Vector2(half, half) * 2.0)
		ci.draw_texture_rect_region(crest, Rect2(box.position + c.crack_left * k, Vector2(box.size.x * 0.5, box.size.y)),
			Rect2(Vector2.ZERO, Vector2(ts.x * 0.5, ts.y)), ring)
		ci.draw_texture_rect_region(crest, Rect2(box.position + Vector2(box.size.x * 0.5, 0.0) + c.crack_right * k,
			Vector2(box.size.x * 0.5, box.size.y)), Rect2(Vector2(ts.x * 0.5, 0.0), Vector2(ts.x * 0.5, ts.y)), ring)
	var cr := crack(centre, radius, sid, c)
	var glow := crack_color
	glow.a = c.crack_glow_alpha
	ci.draw_polyline(cr["line"], glow, c.crack_glow_px * k, true)
	ci.draw_polyline(cr["line"], crack_color, c.crack_px * k, true)
	for br: PackedVector2Array in cr["branches"]:
		ci.draw_polyline(br, crack_color, c.crack_px * k * 0.6, true)


## A stable 0..1 value from (seed, index): an integer hash, no RNG.
static func hash01(seed_id: int, i: int) -> float:
	var h := ((seed_id * HASH_A) ^ (i * HASH_B)) & 0x7fffffff
	h = (((h >> 13) ^ h) * HASH_MIX) & 0x7fffffff
	return float(h % HASH_BUCKETS) / float(HASH_BUCKETS)
