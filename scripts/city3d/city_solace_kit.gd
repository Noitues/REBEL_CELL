class_name CitySolaceKit
extends RefCounted
## LOOK Solace S1 (DIRECTION_REVIEW 2026-10-20, concept district/D_raid_park_r5): the Solace district's building kits.
## A capsule tower, B cell cluster, C clinic tower, assigned per bundle of neighbouring lots, deterministically from the
## layout seed and the lot (no dictionary order, no RNG stream). Pure functions of the config; the meshes are unit meshes
## in the unit_prism convention (the footprint -0.5..0.5, height 0..1, scaled to the lot by CityMeshKit.instance_transform).
##
## Mesh convention (read by shaders/city/city_building.gdshader's vertex()): every vertex carries UV = (dy, anchor) and
## CUSTOM0 = (tone, 0, 0, part code). Its height is anchor * h + dy * u, where h is the prism's height and u the lot's shorter
## side (BU), and x / z are scaled by u: so caps, spheres and slabs keep their true shape whatever the building's height.
## The part code picks the material (CODE_*).

## Family keys at or above this are kits: KEY_BASE + kit * 10 + variant.
const KEY_BASE := 100000
const KIT_A := 0
const KIT_B := 1
const KIT_C := 2
## Part codes (CUSTOM0.w): the capsule / core body with its ribbon bands, a lime glass sphere, a pink nucleus, porcelain,
## the clinic wall (porcelain with leaf-green glass bands), the capsule cap, a lime neon ring, a green terrace.
const CODE_BODY := 1
const CODE_GLASS := 2
const CODE_NUCLEUS := 3
const CODE_PORCELAIN := 4
const CODE_CLINIC := 5
const CODE_CAP := 6
const CODE_RING := 7
const CODE_TERRACE := 8

## kit mesh cache: "key|lod|segments|config" -> ArrayMesh
static var _cache: Dictionary = {}

const _PERMS: Array[Vector3i] = [Vector3i(0, 1, 2), Vector3i(0, 2, 1), Vector3i(1, 0, 2), Vector3i(1, 2, 0), Vector3i(2, 0, 1),
	Vector3i(2, 1, 0)]
const _ROW := 0.8660254


# --- assignment -----------------------------------------------------------------------------------------------------------

## True when prism `pr` draws as a kit: a Solace building (not an HQ plaza lot) on a four-corner footprint, tall enough.
static func eligible(cfg: CityConfig, pr: Dictionary) -> bool:
	if not cfg.solace_kits or StringName(pr.get("terr", &"")) != &"solace" or bool(pr.get("hq", false)):
		return false
	return (pr["poly"] as PackedVector2Array).size() == 4 and float(pr["h"]) >= cfg.solace_kit_min_h


## The bundle (lattice seed, axial (gi, gj)) lot `cell` belongs to: the nearest jittered seed of a triangular lattice shifted by
## the layout seed; ties break by (gj, gi).
static func bundle_of(cfg: CityConfig, cell: Rect2i, city_seed: int) -> Vector2i:
	var p := cfg.solace_bundle_pitch
	var s := city_seed + cfg.solace_kit_salt
	var origin := Vector2(CityMeshKit.hash01(s, 1, 11), CityMeshKit.hash01(s, 2, 12)) * p
	var c := Vector2(cell.position) + Vector2(cell.size) * 0.5 - origin
	var gj0 := roundi(c.y / (p * _ROW))
	var best := Vector2i.ZERO
	var best_d := INF
	for gj in range(gj0 - 1, gj0 + 2):
		var gi0 := roundi(c.x / p - gj * 0.5)
		for gi in range(gi0 - 2, gi0 + 3):
			var d := _seed_pos(cfg, gi, gj, s).distance_squared_to(c)
			if d < best_d - 0.000001 or (absf(d - best_d) <= 0.000001 and (gj < best.y or (gj == best.y and gi < best.x))):
				best_d = d
				best = Vector2i(gi, gj)
	return best


static func _seed_pos(cfg: CityConfig, gi: int, gj: int, s: int) -> Vector2:
	var p := cfg.solace_bundle_pitch
	var j := cfg.solace_bundle_jitter * p
	return Vector2((gi + gj * 0.5) * p + (CityMeshKit.hash01(gi, gj, s + 21) - 0.5) * 2.0 * j,
		gj * p * _ROW + (CityMeshKit.hash01(gi, gj, s + 22) - 0.5) * 2.0 * j)


## The kit (KIT_A, KIT_B, KIT_C) of a bundle: the lattice is 3-coloured ((gi - gj) mod 3) and the layout seed permutes which
## kit takes which colour, so touching bundles differ and the kits stay balanced.
static func kit_of_bundle(cfg: CityConfig, bundle: Vector2i, city_seed: int) -> int:
	var s := city_seed + cfg.solace_kit_salt
	var perm := _PERMS[mini(int(CityMeshKit.hash01(s, 3, 13) * 6.0), 5)]
	var col := posmod(bundle.x - bundle.y, 3)
	return perm[col]


## (kit, variant) of prism `pr`, or (-1, 0) when it draws as an ordinary prism. A prism's variant is a hash of its lot; the
## base and setback prisms of one building share the lot, so they share the kit and variant.
static func kit_of(cfg: CityConfig, pr: Dictionary, city_seed: int) -> Vector2i:
	if not eligible(cfg, pr):
		return Vector2i(-1, 0)
	var cell: Rect2i = pr["cell"]
	var kit := kit_of_bundle(cfg, bundle_of(cfg, cell, city_seed), city_seed)
	var nv := maxi(1, cfg.solace_kit_variants[kit])
	var v := int(CityMeshKit.hash01(cell.position.x, cell.position.y, city_seed + cfg.solace_kit_salt + 31) * nv) % nv
	return Vector2i(kit, v)


## The family key of a kit prism (-1 for an ordinary one).
static func family_key(cfg: CityConfig, pr: Dictionary, city_seed: int) -> int:
	var kv := kit_of(cfg, pr, city_seed)
	return -1 if kv.x < 0 else KEY_BASE + kv.x * 10 + kv.y


static func is_kit_key(key: int) -> bool:
	return key >= KEY_BASE


# --- material -------------------------------------------------------------------------------------------------------------

## Sets the kit's uniforms on building material `m` for night share `night` (1 night .. 0 day).
static func apply_material(m: ShaderMaterial, cfg: CityConfig, night: float) -> void:
	m.set_shader_parameter(&"kit_lime", _v3(cfg.solace_lime))
	m.set_shader_parameter(&"kit_pink", _v3(cfg.solace_pink))
	m.set_shader_parameter(&"kit_porcelain", _v3(cfg.solace_porcelain))
	m.set_shader_parameter(&"kit_leaf", _v3(cfg.solace_leaf))
	m.set_shader_parameter(&"kit_body", _v3(cfg.solace_body))
	m.set_shader_parameter(&"kit_dome", _v3(cfg.solace_dome))
	m.set_shader_parameter(&"kit_terrace", _v3(cfg.solace_terrace))
	m.set_shader_parameter(&"kit_band", cfg.solace_band)
	m.set_shader_parameter(&"kit_clinic_band", cfg.solace_clinic_band)
	m.set_shader_parameter(&"kit_emit", lerpf(cfg.solace_kit_emit.y, cfg.solace_kit_emit.x, night))
	m.set_shader_parameter(&"kit_glass_emit", cfg.solace_glass_emit)
	m.set_shader_parameter(&"kit_nucleus_emit", cfg.solace_nucleus_emit)
	m.set_shader_parameter(&"kit_clinic_emit", cfg.solace_clinic_emit)
	m.set_shader_parameter(&"kit_porcelain_glow", cfg.solace_porcelain_glow)


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)


# --- meshes ---------------------------------------------------------------------------------------------------------------

## The unit mesh of kit family `key` at building LOD `lod` (cached).
static func mesh(cfg: CityConfig, key: int, lod: int) -> ArrayMesh:
	var far := lod >= 2
	var k := "%d|%d|%s" % [key, int(far), cfg.resource_path]
	if not _cache.has(k):
		var n: int = cfg.solace_kit_segments.y if far else cfg.solace_kit_segments.x
		var kit := (key - KEY_BASE) / 10
		var variant := (key - KEY_BASE) % 10
		var acc := _Acc.new()
		acc.salt = key
		match kit:
			KIT_A:
				_build_a(acc, cfg, variant, n)
			KIT_B:
				_build_b(acc, cfg, variant, n)
			_:
				_build_c(acc, cfg, variant)
		_cache[k] = acc.to_mesh()
	return _cache[k]


## The triangles of a kit mesh under construction. A point is Vector4(x, z, anchor, dy): see the file header.
class _Acc:
	extends RefCounted
	var v := PackedVector3Array()
	var uv := PackedVector2Array()
	var c := PackedFloat32Array()
	var salt: int = 0
	var n_tri: int = 0

	func tri(code: int, a: Vector4, b: Vector4, d: Vector4) -> void:
		var tone := CityMeshKit.hash01(n_tri, salt, 7)
		n_tri += 1
		for p: Vector4 in [a, b, d]:
			v.append(Vector3(p.x, p.z, p.y))
			uv.append(Vector2(p.w, p.z))
			c.append_array([tone, 0.0, 0.0, float(code)])

	func quad(code: int, a: Vector4, b: Vector4, d: Vector4, e: Vector4) -> void:
		tri(code, a, b, d)
		tri(code, a, d, e)

	func to_mesh() -> ArrayMesh:
		var uv2 := PackedVector2Array()
		uv2.resize(v.size())
		return CityMeshKit._mesh(v, uv, uv2, c)


static func _ring(n: int, r: float, anchor: float, dy: float, cx: float = 0.0, cz: float = 0.0, rot: float = 0.0) -> Array[Vector4]:
	var out: Array[Vector4] = []
	for k in n:
		var a := rot + TAU * k / n
		out.append(Vector4(cx + r * cos(a), cz + r * sin(a), anchor, dy))
	return out


static func _strip(acc: _Acc, code: int, lo: Array[Vector4], hi: Array[Vector4]) -> void:
	var n := lo.size()
	for k in n:
		var k1 := (k + 1) % n
		acc.quad(code, lo[k], lo[k1], hi[k1], hi[k])


static func _fan(acc: _Acc, code: int, ring: Array[Vector4], centre: Vector4) -> void:
	var n := ring.size()
	for k in n:
		acc.tri(code, centre, ring[k], ring[(k + 1) % n])


## A sphere (centre (cx, cz), height anchor + dy, radius r in lot units). Triangles whose direction from the centre lies within
## `patch_cos` of `patch_dir` (unit space; zero = none) take `patch_code`, the rest `code`.
static func _sphere(acc: _Acc, cx: float, cz: float, anchor: float, dy: float, r: float, n: int, code: int,
		patch_dir: Vector3 = Vector3.ZERO, patch_cos: float = 1.0, patch_code: int = CODE_NUCLEUS) -> void:
	var rings := maxi(3, n / 2)
	var lat: Array = []
	for j in rings + 1:
		var phi := -PI * 0.5 + PI * j / rings
		if j == 0 or j == rings:
			lat.append([Vector4(cx, cz, anchor, dy + r * sin(phi))])
		else:
			lat.append(_ring(n, r * cos(phi), anchor, dy + r * sin(phi), cx, cz, 0.5 * j))
	for j in rings:
		var lo: Array = lat[j]
		var hi: Array = lat[j + 1]
		for k in n:
			var k1 := (k + 1) % n
			var tris: Array = []
			if lo.size() == 1:
				tris.append([lo[0], hi[k1], hi[k]])
			elif hi.size() == 1:
				tris.append([lo[k], lo[k1], hi[0]])
			else:
				tris.append([lo[k], lo[k1], hi[k]])
				tris.append([lo[k1], hi[k1], hi[k]])
			for t: Array in tris:
				var cen := Vector3.ZERO
				for p: Vector4 in t:
					cen += Vector3(p.x - cx, p.w - dy, p.y - cz)
				var cc := code
				if patch_dir != Vector3.ZERO and cen.normalized().dot(patch_dir) > patch_cos:
					cc = patch_code
				acc.tri(cc, t[0], t[1], t[2])


## An upright box of half width `w` (rotated by `rot`) from point (anchor_lo, dy_lo) to (anchor_hi, dy_hi): walls `code`, top
## `top_code` (0 = none).
static func _box(acc: _Acc, code: int, top_code: int, w: float, rot: float, a_lo: float, dy_lo: float, a_hi: float, dy_hi: float) -> void:
	var lo := _ring(4, w * sqrt(2.0), a_lo, dy_lo, 0.0, 0.0, rot + PI * 0.25)
	var hi := _ring(4, w * sqrt(2.0), a_hi, dy_hi, 0.0, 0.0, rot + PI * 0.25)
	_strip(acc, code, lo, hi)
	if top_code > 0:
		acc.quad(top_code, hi[0], hi[1], hi[2], hi[3])


static func _rnd(a: int, b: int, c: int) -> float:
	return CityMeshKit.hash01(a, b, c)


static func _build_a(acc: _Acc, cfg: CityConfig, variant: int, n: int) -> void:
	var r := cfg.solace_a_radius
	var rise := cfg.solace_a_cap_rise
	var pod: Vector2 = cfg.solace_a_podium
	# Podium skirt, body (stretches with the height), neon ring under the cap, the cap.
	_strip(acc, CODE_PORCELAIN, _ring(n, pod.x, 0.0, 0.0), _ring(n, r + 0.03, 0.0, pod.y))
	_strip(acc, CODE_BODY, _ring(n, r, 0.0, pod.y), _ring(n, r, 1.0, -rise - cfg.solace_a_ring_h))
	_strip(acc, CODE_RING, _ring(n, r + 0.012, 1.0, -rise - cfg.solace_a_ring_h), _ring(n, r + 0.012, 1.0, -rise))
	var prev := _ring(n, r, 1.0, -rise)
	for k in range(1, 4):
		var th := PI * 0.5 * k / 4.0
		var cur := _ring(n, r * cos(th), 1.0, -rise + rise * sin(th))
		_strip(acc, CODE_CAP, prev, cur)
		prev = cur
	_fan(acc, CODE_CAP, prev, Vector4(0, 0, 1.0, 0.0))
	if variant == 1:
		var m: Vector3 = cfg.solace_a_mast
		_strip(acc, CODE_PORCELAIN, _ring(4, m.y, 1.0, 0.0), _ring(4, m.y, 1.0, m.x))
		_sphere(acc, 0.0, 0.0, 1.0, m.x + m.z * 0.5, m.z, 6, CODE_NUCLEUS)


static func _build_b(acc: _Acc, cfg: CityConfig, variant: int, n: int) -> void:
	var cr := cfg.solace_b_core_r
	var top := cfg.solace_b_core_share
	_strip(acc, CODE_BODY, _ring(n, cr, 0.0, 0.0), _ring(n, cr, top, 0.0))
	_fan(acc, CODE_CAP, _ring(n, cr, top, 0.0), Vector4(0, 0, top, 0.0))
	var count := cfg.solace_b_cells.x + int(_rnd(variant, 5, 41) * (cfg.solace_b_cells.y - cfg.solace_b_cells.x + 1))
	count = mini(count, cfg.solace_b_cells.y)
	var sn := maxi(6, n - 2)
	for k in count:
		var f := (k + 0.5) / count
		var rad := lerpf(cfg.solace_b_cell_r.y, cfg.solace_b_cell_r.x, f) * (0.8 + 0.4 * _rnd(variant, k, 42))
		var ang := _rnd(variant, k, 43) * TAU + k * 2.2
		var d := clampf(cr + rad * 0.6, 0.0, 0.5 - rad)
		var cx := d * cos(ang)
		var cz := d * sin(ang)
		var anchor := (0.1 + 0.8 * f) * top
		var pd := Vector3(cos(ang) * 0.55, 0.85, sin(ang) * 0.55).normalized()
		var nuc := _rnd(variant, k, 44) < cfg.solace_b_nucleus_share
		_sphere(acc, cx, cz, anchor, 0.0, rad, sn, CODE_GLASS, pd if nuc else Vector3.ZERO, cfg.solace_b_patch_cos)
		if _rnd(variant, k, 45) < 0.5:
			var a2 := ang + (_rnd(variant, k, 46) - 0.5) * 1.6
			var r2 := rad * 0.55
			var cx2 := cx + (rad + r2 * 0.55) * cos(a2)
			var cz2 := cz + (rad + r2 * 0.55) * sin(a2)
			if absf(cx2) + r2 <= 0.5 and absf(cz2) + r2 <= 0.5:
				_sphere(acc, cx2, cz2, anchor, (_rnd(variant, k, 47) - 0.5) * rad, r2, sn, CODE_GLASS, pd if not nuc else Vector3.ZERO,
					cfg.solace_b_patch_cos)
	var big := cfg.solace_b_cell_r.y * 0.95
	_sphere(acc, 0.0, 0.0, top, big * 0.35, big, sn, CODE_GLASS, Vector3(0, 1, 0), cfg.solace_b_patch_cos * 0.7)


static func _build_c(acc: _Acc, cfg: CityConfig, variant: int) -> void:
	var tiers := cfg.solace_c_tiers
	var tops := cfg.solace_c_tier_tops
	var slab := cfg.solace_c_slab
	var crown: Vector3 = cfg.solace_c_crown
	var crown_h := crown.x * crown.y
	var lo_a := 0.0
	var lo_dy := 0.0
	var wscale := 1.0 if variant == 0 else 0.92
	for t in tiers.size():
		var w := tiers[t] * wscale
		var last := t == tiers.size() - 1
		var hi_a := 1.0 if last else tops[t]
		var hi_dy := -crown_h if last else 0.0
		_box(acc, CODE_CLINIC, 0, w, 0.0, lo_a, lo_dy, hi_a, hi_dy)
		# The setback slab: porcelain edge, its top a green terrace under the next tier.
		_box(acc, CODE_PORCELAIN, CODE_TERRACE if not last else CODE_PORCELAIN, w + 0.03, 0.0, hi_a, hi_dy - slab, hi_a, hi_dy + 0.005)
		lo_a = hi_a
		lo_dy = hi_dy
	# The crown: slabs, each twisted a little more than the one below (lit lime on every other one).
	var w0 := tiers[tiers.size() - 1] * wscale * 0.84
	var cnt := int(crown.x) if variant == 0 else int(crown.x) + 1
	var tw := deg_to_rad(crown.z) * (1.0 if variant == 0 else -1.0)
	for s in cnt:
		var w := w0 * (1.0 - cfg.solace_c_crown_shrink * s)
		var y0 := -crown_h + s * crown.y
		_box(acc, CODE_RING if s % 2 == 1 else CODE_PORCELAIN, CODE_PORCELAIN, w, tw * s, 1.0, y0 + 0.01, 1.0, y0 + crown.y * 0.85)
	_sphere(acc, 0.0, 0.0, 1.0, crown.y * 0.9 + 0.02, 0.04, 6, CODE_NUCLEUS)
