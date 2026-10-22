class_name GreasePencilMark
extends Node2D
## A grease pencil mark (ART-1 1B; ART_BIBLE v2 §1.2 "Grease pencil", §6.3, §6.4): plans and
## annotations that are true to the rules. One mark is one or more strokes in writing order
## (a circle; an arrow's shaft and its two head flicks; a route). Each stroke is a `Line2D`
## with round caps and `shaders/kit/marker_stroke.gdshader` (the port of the concepts' own wax
## generator, round 3 `tg_lib.wax_stroke`: opaque wax, alpha 0.96, bristles, dropouts every
## 40-70 px, ragged edge, a 1 px sheen line at 35 % white, the glint) over a copy of it as the
## under-shadow, offset SHADOW_OFFSET in PENCIL_SHADOW (#060308 at 85 %). Yellow `PENCIL_PLAN`
## = our plan / valid; red `PENCIL_THREAT` = threat / invalid / loss. Solid = what will happen;
## dashed = what-if.
##
## B1b (integration review D3, "one wax material everywhere"): the stroke is one width on
## screen, `stroke_width()`, scaled with the text size as the kit's stickers are (up to
## VerbSticker.SCALE_MAX), whatever the mark's own scale (a map's zoom): the mark undoes its
## global scale on its lines. No caller sets a width. LOOK-TOOLBOX 12 (AUDIT "pencil: fail"):
## two weights from RcPencilLook (addons/rc_look/config/pencil_look.tres): a mark (10 px at
## 1080p) and a `hero` mark (16 px: the aim arc and its loop, a TARGET ring), and every stroke
## carries a hand's pressure (RcPencilPressure: it lands light, swells, lifts off in a thin
## flick), sampled along the stroke so writing on never moves it. A word (GreasePencilWord)
## sets `local_width`: its wax scales with its letters.
##
## Writes on in writing order (`pencil_write_on`, its duration: ~0.4 s) and wipes off with a
## cloth wipe (`pencil_wipe`, ~0.4 s), both by trimming points, never alpha. B1b (D25: pencil
## never appears whole): a mark with `auto_write` (the default) writes itself on the first
## time it shows with strokes, and again each time it shows after being hidden; a mark whose
## owner drives `progress` (RaidPencilPool, the aim) turns `auto_write` off. Reduce effects /
## headless / switched off: written whole at once, wiped at once, no glint. MotionSkip: one
## press completes the write or the wipe. Pencil is above all UI and no UI ever covers it:
## every mark is in the `GROUP` group, which `PencilLint` checks. A view only.

signal written
signal wiped

## PLAN_NETRUN: the netrun plan (the HQ page's plan pencil), orange through
## Palette.PENCIL_PLAN_NETRUN (art-pass ruling d, 2026-10-21); PLAN is yellow everywhere else.
enum Ink { PLAN, THREAT, PLAN_NETRUN, THREAT_ROUTE, THREAT_CORE, THREAT_EDGE }

const SHADER := preload("res://shaders/kit/marker_stroke.gdshader")
## Every mark on screen (PencilLint).
const GROUP := &"grease_pencil"
const WRITE := &"pencil_write_on"
const WIPE := &"pencil_wipe"
const GLINT := &"pencil_glint"
## The concepts' boards are 1920 x 1080; the game's canvas is 1280 x 720.
const BOARD_TO_CANVAS := 2.0 / 3.0
## The look numbers (LOOK-TOOLBOX 12): widths, pressure, the hand.
const LOOK: RcPencilLook = preload("res://addons/rc_look/config/pencil_look.tres")
## The under-shadow's offset (integration review D3, bible §6.3), in 1080p (board) px.
const SHADOW_1080 := Vector2(2.0, 3.0)
## The under-shadow copy is this much wider (1080p px) so it shows as a dark rim under the wax
## on a light street as well as on a dark one.
const SHADOW_GROW_1080 := 2.0
## The same in canvas px (at text size 1.0).
const SHADOW_OFFSET := SHADOW_1080 * BOARD_TO_CANVAS
const SHADOW_GROW := SHADOW_GROW_1080 * BOARD_TO_CANVAS
## Wax opacity (bible §1.2: 0.96) and the sheen line's strength (D3: 35 % white).
const WAX_ALPHA := 0.96
const SHEEN := 0.35
## The wax dropouts (D3 lock), in 1080p px along a stroke: each gap drawn uniformly from
## DROPOUT_GAP (40-70 px, seeded; `dropout_hit`), each stretch DROPOUT_LEN long (LOOK-TOOLBOX 12:
## 5-9 px, was 2-4: at the 10-16 px widths a 3 px bite read as a crack across the stroke), where
## the wax's alpha falls to DROPOUT_ALPHA. Words take fewer (WORD_DROPOUT_GAP). The shader draws
## them with the same hash (`dhash`).
const DROPOUT_GAP := Vector2(40.0, 70.0)
const DROPOUT_LEN := Vector2(5.0, 9.0)
const DROPOUT_ALPHA := 0.35
const WORD_DROPOUT_GAP := Vector2(70.0, 110.0)
## B1b fix c: a dropout is a nibble, a ragged bite this share of the stroke's width (LOOK-TOOLBOX 12:
## 25-45 %, was 40-70)
## from one edge (its side from the seed), never a full-width break; the under-shadow fades
## over the whole gap and its offset past it (`dropout_pad`: SHADOW_1080's length). Words bite
## across this share of their ascent (the cap height).
const DROPOUT_BITE := Vector2(0.25, 0.45)
const WORD_CAP_SHARE := 0.72
## Seeds fold into 0..SEED_FOLD-1 before they reach the shader.
const SEED_FOLD := 997
## The resample step (px).
const STEP_PX := 3.0
## The wipe drags the wax this way (a palm down-left) while it trims from the start.
## `wobble`'s knots along a stroke, and the share of the width a stroke's two ends keep.
const WOBBLE_KNOTS := 14
const WIPE_DRAG := Vector2(-0.6, 0.8)

## M14 perf slice: the setters below do nothing when the value is unchanged (a pool owner lays
## every mark again each frame; a Settings change re-syncs through _on_settings).
@export var ink: Ink = Ink.PLAN:
	set(v):
		if v == ink:
			return
		ink = v
		_sync()
## RAID-FIX C2: the share of the kit's one width this stroke keeps (1 = the kit's; the white-hot core of a
## threat route is a third, laid over the cobalt stroke, with no under-shadow of its own).
@export var width_share: float = 1.0
@export var dashed: bool = false:
	set(v):
		if v == dashed:
			return
		dashed = v
		_sync()
## The wax's seed (grain and dropouts).
@export var seed: int = 1:
	set(v):
		if v == seed:
			return
		seed = v
		_sync()
		_set_curves()
## Writes itself on when it first shows (and each time it shows again after being hidden).
@export var auto_write: bool = true:
	set(v):
		auto_write = v
		_arm()

## Extra pressure wobble on top of the look's (a share; 0 = the look's pressure only), from `seed`.
@export var wobble: float = 0.0:
	set(v):
		if v == wobble:
			return
		wobble = v
		_set_curves()
## A hero mark (the aim arc and its loop, a TARGET ring): the look's hero width and pressure.
@export var hero: bool = false:
	set(v):
		if v == hero:
			return
		hero = v
		_apply()
		_sync()
## A width in this mark's local px that scales with it (a word's wax, sized by its font): > 0
## replaces the screen width (and the word's pressure profile is used).
var local_width: float = 0.0:
	set(v):
		if v == local_width:
			return
		local_width = v
		_apply()

## The dropouts' gap range (1080p px): DROPOUT_GAP, or WORD_DROPOUT_GAP for a word's letters.
var dropout_gap: Vector2 = DROPOUT_GAP:
	set(v):
		if v == dropout_gap:
			return
		dropout_gap = v
		_sync()

## False drops the 1 px sheen line (a flat wax stroke, no lit side).
@export var highlight: bool = true:
	set(v):
		if v == highlight:
			return
		highlight = v
		_sync()

## Hand-mark wax grain (COMBAT-LOCK r3): the share of both edges whose wax drops out, and how
## much the core breaks into lighter streaks. 0 = the raid pencil, unchanged.
@export_range(0.0, 1.0) var edge_grain: float = 0.0:
	set(v):
		if v == edge_grain:
			return
		edge_grain = v
		_sync()
@export_range(0.0, 1.0) var core_break: float = 0.0:
	set(v):
		if v == core_break:
			return
		core_break = v
		_sync()

## White added at the stroke's middle, fading to its edges (a hero word's lighter core); 0 = none.
var core_light: float = 0.0:
	set(v):
		if v == core_light:
			return
		core_light = v
		_sync()

## The wax's (and its shadow's) top alpha: WAX_ALPHA, or lower where the mark runs over a label
## that must stay readable (COMBAT-LOCK r4: the RESPIN chip's slash).
var wax_alpha: float = WAX_ALPHA:
	set(v):
		if v == wax_alpha:
			return
		wax_alpha = v
		_sync()

## Written share 0..1 (by length, in writing order) and the wiped share from the start.
var progress: float = 1.0:
	set(v):
		var c := clampf(v, 0.0, 1.0)
		if c == progress:
			return
		progress = c
		_apply()
var wiped_share: float = 0.0:
	set(v):
		var c := clampf(v, 0.0, 1.0)
		if c == wiped_share:
			return
		wiped_share = c
		_apply()
var smear: float = 0.0:
	set(v):
		smear = v
		_sync()

var _paths: Array[PackedVector2Array] = []
var _lens: Array[float] = []
var _lines: Array[Line2D] = []
var _shadows: Array[Line2D] = []
var _mat: ShaderMaterial = null
var _shadow_mat: ShaderMaterial = null
var _tween: Tween = null
var _tween_kind: StringName = &""
var _tile: Texture2D = null
## True while an auto write waits for the mark to show with strokes.
var _pending: bool = true
var _screen_k: float = 1.0


func _init() -> void:
	add_to_group(GROUP)
	set_notify_transform(true)
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_shadow_mat = ShaderMaterial.new()
	_shadow_mat.shader = SHADER
	_shadow_mat.set_shader_parameter(&"mode", 1)
	var img := Image.create(4, 4, false, Image.FORMAT_L8)
	img.fill(Palette.NO_TINT)
	_tile = ImageTexture.create_from_image(img)
	_sync()


func _ready() -> void:
	MotionSkip.register_passive(self)  # ANIM-R6 D7: a mark writing on ends with any press that ends a motion
	Settings.changed.connect(_on_settings)
	_sync()
	_arm()


## The stroke width (canvas px on screen) at the current text size: a mark's, or a hero mark's.
static func stroke_width(p_hero: bool = false) -> float:
	return base_width(p_hero) * ui_scale()


## The stroke width (canvas px) at text size 1.0.
static func base_width(p_hero: bool = false) -> float:
	return (LOOK.hero_width_1080 if p_hero else LOOK.mark_width_1080) * BOARD_TO_CANVAS


## The pencil's scale with the text size (as the kit's stickers: up to VerbSticker.SCALE_MAX).
static func ui_scale() -> float:
	return clampf(Settings.text_scale, 1.0, VerbSticker.SCALE_MAX)


## `seed` folded into the shader's float range (a hash seed of 2^31 loses the noise's precision:
## the grain collapses and the wax turns thin and dark).
static func shader_seed(s: int) -> float:
	return float(posmod(s, SEED_FOLD))


## A 32-bit integer hash in 0..1 (the shader's `dhash`, bit for bit).
static func dhash(k: int, s: int) -> float:
	var n := (k * 374761393 + s * 668265263) & 0xFFFFFFFF
	n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65535.0


## The dropout at `d` (1080p px along a stroke) for `seed` with gaps from `gap`: {inside: 0..1
## (1 inside a stretch, half-px soft ends), side: -1 or 1 (the edge it bites from), bite: share
## of the width (DROPOUT_BITE)}. The shader's `dropout_hit` computes the same: the dropouts come
## in pairs `gap.x + gap.y` long, one at the pair's start and one a seeded gap g on (uniform in
## `gap`), so every gap, g or the pair's rest, is uniform in the range; a seeded phase shifts them.
static func dropout_hit(s: int, d: float, gap: Vector2 = DROPOUT_GAP) -> Dictionary:
	var sd := int(shader_seed(s))
	var pair := gap.x + gap.y
	var dd := d + dhash(0, sd + 5) * pair
	var k := floori(dd / pair)
	var best := {"inside": 0.0, "side": 1, "bite": DROPOUT_BITE.x}
	for pi in [-1, 0, 1]:
		var p: int = k + pi
		for j in [0, 1]:
			var kk: int = 2 * p + j
			var c := float(p) * pair + (lerpf(gap.x, gap.y, dhash(p, sd + 4)) if j == 1 else 0.0)
			var half_len := lerpf(DROPOUT_LEN.x, DROPOUT_LEN.y, dhash(kk, sd + 1)) * 0.5
			var inside := 1.0 - smoothstep(half_len - 0.5, half_len + 0.5, absf(dd - c))
			if inside > float(best["inside"]):
				best = {"inside": inside, "side": -1 if dhash(kk, sd + 2) < 0.5 else 1,
					"bite": lerpf(DROPOUT_BITE.x, DROPOUT_BITE.y, dhash(kk, sd + 3))}
	return best


## The wax's dropout at `d` (1080p px along a stroke) for `seed`: 1 inside a dropout stretch,
## 0 outside (its alpha falls to DROPOUT_ALPHA there, under the nibble).
static func dropout_factor(s: int, d: float, gap: Vector2 = DROPOUT_GAP) -> float:
	return float(dropout_hit(s, d, gap)["inside"])


## The nibble of the dropout stretch at `d`: {side, bite} (see `dropout_hit`).
static func dropout_bite(s: int, d: float, gap: Vector2 = DROPOUT_GAP) -> Dictionary:
	return dropout_hit(s, d, gap)


## Local px (under global scale `k`) to the dropouts' 1080p px, at the current text size.
static func dropout_scale(k: float) -> float:
	return k / (BOARD_TO_CANVAS * ui_scale())


## Sets the dropout uniforms on `mat` (strokes: DROPOUT_GAP; words: WORD_DROPOUT_GAP).
static func set_dropouts(mat: ShaderMaterial, gap: Vector2) -> void:
	mat.set_shader_parameter(&"dropout_gap", gap)
	mat.set_shader_parameter(&"dropout_len", DROPOUT_LEN)
	mat.set_shader_parameter(&"dropout_alpha", DROPOUT_ALPHA)
	mat.set_shader_parameter(&"dropout_bite", DROPOUT_BITE)


## The colour of `ink`.
static func ink_color(i: Ink) -> Color:
	match i:
		Ink.THREAT:
			return Palette.PENCIL_THREAT
		Ink.PLAN_NETRUN:
			return Palette.PENCIL_PLAN_NETRUN
		Ink.THREAT_EDGE:
			return Palette.INK
		Ink.THREAT_CORE:
			return Palette.WHITE_HOT
		Ink.THREAT_ROUTE:
			return Palette.THREAT_ROUTE
	return Palette.PENCIL_PLAN


## The stroke's width in this mark's local px (the screen width over its global scale).
func width() -> float:
	return (local_width if local_width > 0.0 else stroke_width(hero) / _screen_k) * width_share


## The pressure profile this mark draws with (a word's, a hero's or a mark's).
func pressure() -> RcPencilPressure:
	if local_width > 0.0:
		return LOOK.word_pressure
	return LOOK.hero_pressure if hero else LOOK.mark_pressure


## Adds a stroke (local points) after the others in writing order.
func add_stroke(points: PackedVector2Array) -> void:
	var p := PencilShapes.resample(points, STEP_PX)
	_paths.append(p)
	_lens.append(PencilShapes.length_of(p))
	var sh := _make_line(_shadow_mat)
	_shadows.append(sh)
	var ln := _make_line(_mat)
	_lines.append(ln)
	# shadows under every wax line: keep them first in the tree
	move_child(sh, _shadows.size() - 1)
	_apply()


## Removes every stroke.
func clear() -> void:
	for l in _lines + _shadows:
		l.queue_free()
	_lines.clear()
	_shadows.clear()
	_paths.clear()
	_lens.clear()


## The strokes (local points) in writing order.
func strokes() -> Array[PackedVector2Array]:
	return _paths


## The whole length of the mark (px).
func total_length() -> float:
	var l := 0.0
	for x in _lens:
		l += x
	return l


## The strokes' rect in global coordinates, grown by half the width and the shadow (the
## area no UI may cover).
func global_rect() -> Rect2:
	var r := Rect2()
	var first := true
	for p in _paths:
		var b := PencilShapes.bounds(p, (width() + SHADOW_GROW * ui_scale() / _screen_k) * 0.5)
		b.end += SHADOW_OFFSET / _screen_k
		r = b if first else r.merge(b)
		first = false
	return get_global_transform() * r


## Rects (global) that cover each drawn stroke segment run, tighter than `global_rect`.
func segment_rects(chunk_px: float = 24.0) -> Array[Rect2]:
	var out: Array[Rect2] = []
	var xf := get_global_transform()
	for ln in _lines:
		var pts := ln.points
		var i := 0
		while i < pts.size() - 1:
			var j := mini(i + maxi(1, int(chunk_px / STEP_PX)), pts.size() - 1)
			var seg := PackedVector2Array()
			for k in range(i, j + 1):
				seg.append(pts[k])
			out.append(xf * PencilShapes.bounds(seg, width() * 0.5))
			i = j
	return out


## The wax lines (tests: width, caps, material) and their under-shadow copies.
func wax_lines() -> Array[Line2D]:
	return _lines


func shadow_lines() -> Array[Line2D]:
	return _shadows


func _make_line(mat: ShaderMaterial) -> Line2D:
	var l := Line2D.new()
	l.width = width()
	l.begin_cap_mode = Line2D.LINE_CAP_ROUND
	l.end_cap_mode = Line2D.LINE_CAP_ROUND
	l.joint_mode = Line2D.LINE_JOINT_ROUND
	# B1b fix c: STRETCH (UV.x 0..1 over the drawn part) with the part's span along the stroke
	# per line (`seg_from_px` / `seg_to_px`), so the dropouts are spaced in screen px.
	l.texture_mode = Line2D.LINE_TEXTURE_STRETCH
	l.texture = _tile
	l.antialiased = true
	l.material = mat.duplicate() as ShaderMaterial
	l.default_color = Palette.NO_TINT
	add_child(l)
	return l


## The pressure curve over the drawn part [`from_len`, `to_len`] of stroke `i` (its length
## `length`): the look's profile sampled at the stroke's own distances (so it never slides while
## the stroke writes on or wipes off), times the extra `wobble`.
func _pressure_curve(i: int, from_len: float, to_len: float, length: float) -> Curve:
	var c := Curve.new()
	c.min_value = 0.0
	c.max_value = 2.0
	var prof := pressure()
	var w := width()
	var n := clampi(ceili(absf(to_len - from_len) / maxf(w * LOOK.pressure_knot_widths, 0.001)) + 1,
		maxi(LOOK.pressure_knots, 2), maxi(LOOK.pressure_knots_max, 2))
	var s_i := seed * 13 + i * 101
	var path := _paths[i]
	for j in n:
		var u := float(j) / float(n - 1)
		var d := lerpf(from_len, to_len, u)
		var y := prof.factor(d, length, w, s_i)
		if local_width > 0.0 and path.size() > 1:
			# a word's broad nib: thin along its edge, full across it (designer 2026-10-21)
			var k := clampi(int(d / STEP_PX), 0, path.size() - 2)
			y *= RcPencilPressure.nib(path[k + 1] - path[k], LOOK.word_nib_deg, LOOK.word_nib_contrast)
		if wobble > 0.0:
			y *= 1.0 + wobble * (KitNoise.smooth(s_i + 7, d / maxf(w * WOBBLE_KNOTS, 0.001)) * 2.0 - 1.0)
		c.add_point(Vector2(u, clampf(y, 0.0, c.max_value)))
	return c


func _set_curves() -> void:
	_apply()


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSFORM_CHANGED or what == NOTIFICATION_ENTER_TREE:
		_rescale()
	elif what == NOTIFICATION_VISIBILITY_CHANGED and not is_visible_in_tree():
		_arm()  # D25: shown again, it writes on again


func _on_settings() -> void:
	_sync()
	_rescale()


func _rescale() -> void:
	var k := absf(get_global_transform().get_scale().x) if is_inside_tree() else 1.0
	_screen_k = k if k > 0.0001 else 1.0
	_apply()


## The wax materials (the template and each line's own) or the shadow's.
func _mats(shadow: bool) -> Array[ShaderMaterial]:
	var out: Array[ShaderMaterial] = [_shadow_mat if shadow else _mat]
	for l in (_shadows if shadow else _lines):
		if l.material is ShaderMaterial:
			out.append(l.material as ShaderMaterial)
	return out


func _set_param(shadow: bool, param: StringName, value: Variant) -> void:
	for m in _mats(shadow):
		m.set_shader_parameter(param, value)


func _sync() -> void:
	if _mat == null:
		return
	_set_param(false, &"ink", ink_color(ink))
	_set_param(false, &"seed", shader_seed(seed))
	_set_param(false, &"dashed", dashed)
	_set_param(false, &"smear", smear)
	_set_param(false, &"alpha_max", wax_alpha)
	_set_param(true, &"alpha_max", wax_alpha)
	_set_param(false, &"sheen", SHEEN if highlight else 0.0)
	_set_param(false, &"edge_grain", maxf(edge_grain, LOOK.hero_edge_grain if hero else 0.0))
	_set_param(false, &"core_break", maxf(core_break, LOOK.hero_core_break if hero else 0.0))
	_set_param(false, &"core_light", core_light)
	for sh in [false, true]:
		for m in _mats(sh):
			set_dropouts(m, dropout_gap)
	_set_param(true, &"dropout_pad", SHADOW_1080.length())
	_set_param(true, &"ink", Palette.PENCIL_SHADOW)
	_set_param(true, &"dashed", dashed)
	_set_param(true, &"seed", shader_seed(seed))
	if Motion.has(GLINT):
		var e := Motion.entry(GLINT)
		_set_param(false, &"glint_run", e.duration)
		_set_param(false, &"glint_rest", e.delay)
		_set_param(false, &"glint_strength", e.amplitude if Motion.live(GLINT) else 0.0)


## Shows the strokes between the wiped share and the written share (by length, in order).
func _apply() -> void:
	var total := total_length()
	var from := wiped_share * total
	var to := progress * total
	var acc := 0.0
	var w := width()
	if _mat != null:
		var ds := dropout_scale(_screen_k)
		for sh in [false, true]:
			_set_param(sh, &"width_px", w)
			_set_param(sh, &"dropout_scale", ds)
	for i in _paths.size():
		var l := _lens[i]
		var seg_from := clampf(from - acc, 0.0, l)
		var seg_to := clampf(to - acc, 0.0, l)
		var pts := PencilShapes.trim(_paths[i], seg_from, seg_to)
		var word := local_width > 0.0
		for ln: Line2D in [_lines[i], _shadows[i]]:
			(ln.material as ShaderMaterial).set_shader_parameter(&"seg_from_px", seg_from)
			(ln.material as ShaderMaterial).set_shader_parameter(&"seg_to_px", maxf(seg_to, seg_from + 0.001))
			# designer 2026-10-21: a word's stroke starts cut square by the chisel and ends uneven, fading
			(ln.material as ShaderMaterial).set_shader_parameter(&"stroke_len_px", l)
			(ln.material as ShaderMaterial).set_shader_parameter(&"tail_px", w * LOOK.word_tail_len if word else 0.0)
			(ln.material as ShaderMaterial).set_shader_parameter(&"tail_fade", LOOK.word_tail_fade if word else 0.0)
			ln.begin_cap_mode = Line2D.LINE_CAP_BOX if word else Line2D.LINE_CAP_ROUND
		if smear > 0.0 and pts.size() > 1:
			# the palm drags the trailing wax along with it
			var drag := WIPE_DRAG * smear * Motion.amplitude(WIPE)
			for k in pts.size():
				var f := 1.0 - float(k) / float(pts.size() - 1)
				pts[k] += drag * f
		_lines[i].points = pts
		_lines[i].width = w
		var curve := _pressure_curve(i, seg_from, seg_to, l) if pts.size() > 1 else null
		_lines[i].width_curve = curve
		_shadows[i].width_curve = curve
		_shadows[i].points = pts
		_shadows[i].width = w + SHADOW_GROW * ui_scale() / (1.0 if local_width > 0.0 else _screen_k)
		_shadows[i].visible = width_share >= 1.0
		_shadows[i].position = SHADOW_OFFSET / (1.0 if local_width > 0.0 else _screen_k)
		acc += l


# --- Motion ------------------------------------------------------------------------------

## D25: an auto mark waits to show, then writes itself on.
func _arm() -> void:
	if not auto_write:
		_pending = false
		set_process(false)
		return
	_pending = true
	if Motion.live(WRITE) and not motion_running():
		progress = 0.0
	set_process(true)


func _process(_delta: float) -> void:
	if not _pending or not auto_write:
		set_process(false)
		return
	if total_length() > 0.0 and is_visible_in_tree():
		_pending = false
		set_process(false)
		write_on()


func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


func complete_motion() -> void:
	if _pending and auto_write and total_length() > 0.0:
		_pending = false
		set_process(false)
		progress = 1.0
	if not motion_running():
		return
	var kind := _tween_kind
	_tween.kill()
	_tween = null
	_end(kind)


func _end(kind: StringName) -> void:
	_tween_kind = &""
	if kind == WRITE:
		progress = 1.0
		written.emit()
	elif kind == WIPE:
		smear = 0.0
		wiped_share = 1.0
		wiped.emit()


## Writes the mark on in writing order over `pencil_write_on`'s duration. Returns the seconds
## (0: written whole at once).
func write_on() -> float:
	if motion_running():
		complete_motion()
	_pending = false
	wiped_share = 0.0
	smear = 0.0
	if not Motion.live(WRITE):
		progress = 1.0
		_end(WRITE)
		return 0.0
	var e := Motion.entry(WRITE)
	var d := Motion.seconds(WRITE)
	progress = 0.0
	_tween_kind = WRITE
	_tween = create_tween()
	_tween.tween_property(self, "progress", 1.0, d).set_ease(e.ease).set_trans(e.trans)
	_tween.tween_callback(func() -> void:
		_tween = null
		_end(WRITE))
	return d


## The cloth wipe (`pencil_wipe`): trims from the start while the palm drags the wax (the
## smear), never an alpha fade. Returns the seconds (0: gone at once).
func wipe() -> float:
	if motion_running():
		complete_motion()
	_pending = false
	set_process(false)
	if not Motion.live(WIPE):
		_end(WIPE)
		return 0.0
	var e := Motion.entry(WIPE)
	var d := Motion.seconds(WIPE)
	_tween_kind = WIPE
	_tween = create_tween()
	_tween.tween_property(self, "wiped_share", 1.0, d).set_ease(e.ease).set_trans(e.trans)
	_tween.parallel().tween_property(self, "smear", 1.0, d)
	_tween.tween_callback(func() -> void:
		_tween = null
		_end(WIPE))
	return d
