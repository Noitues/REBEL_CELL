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
## screen, `stroke_width()` (9 px at 1080p, 6 px of the 1280x720 canvas, scaled with the text
## size as the kit's stickers are, up to VerbSticker.SCALE_MAX), whatever the mark's own scale
## (a map's zoom): the mark undoes its global scale on its lines. No caller sets a width.
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

enum Ink { PLAN, THREAT }

const SHADER := preload("res://shaders/kit/marker_stroke.gdshader")
## Every mark on screen (PencilLint).
const GROUP := &"grease_pencil"
const WRITE := &"pencil_write_on"
const WIPE := &"pencil_wipe"
const GLINT := &"pencil_glint"
## The concepts' boards are 1920 x 1080; the game's canvas is 1280 x 720.
const BOARD_TO_CANVAS := 2.0 / 3.0
## The look (integration review D3, bible §6.3), in 1080p (board) px: the stroke's width and
## the range every stroke keeps to (bible: 8-10), the under-shadow's offset.
const WIDTH_1080 := 9.0
const WIDTH_MIN_1080 := 8.0
const WIDTH_MAX_1080 := 10.0
const SHADOW_1080 := Vector2(2.0, 3.0)
## The same in canvas px (at text size 1.0).
const WIDTH := WIDTH_1080 * BOARD_TO_CANVAS
const SHADOW_OFFSET := SHADOW_1080 * BOARD_TO_CANVAS
## Wax opacity (bible §1.2: 0.96) and the sheen line's strength (D3: 35 % white).
const WAX_ALPHA := 0.96
const SHEEN := 0.35
## The pressure dropouts' spacing along a stroke (px: D3 "dropouts every 40 to 70 px").
const DROPOUT_PX := Vector2(40.0, 70.0)
## Seeds fold into 0..SEED_FOLD-1 before they reach the shader.
const SEED_FOLD := 997
## The resample step (px).
const STEP_PX := 3.0
## The wipe drags the wax this way (a palm down-left) while it trims from the start.
const WIPE_DRAG := Vector2(-0.6, 0.8)

@export var ink: Ink = Ink.PLAN:
	set(v):
		ink = v
		_sync()
@export var dashed: bool = false:
	set(v):
		dashed = v
		_sync()
## The wax's seed (grain and dropouts).
@export var seed: int = 1:
	set(v):
		seed = v
		_sync()
## Writes itself on when it first shows (and each time it shows again after being hidden).
@export var auto_write: bool = true:
	set(v):
		auto_write = v
		_arm()

## Written share 0..1 (by length, in writing order) and the wiped share from the start.
var progress: float = 1.0:
	set(v):
		progress = clampf(v, 0.0, 1.0)
		_apply()
var wiped_share: float = 0.0:
	set(v):
		wiped_share = clampf(v, 0.0, 1.0)
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


## The one stroke width (canvas px on screen) at the current text size.
static func stroke_width() -> float:
	return WIDTH * ui_scale()


## The pencil's scale with the text size (as the kit's stickers: up to VerbSticker.SCALE_MAX).
static func ui_scale() -> float:
	return clampf(Settings.text_scale, 1.0, VerbSticker.SCALE_MAX)


## `seed` folded into the shader's float range (a hash seed of 2^31 loses the noise's precision:
## the grain collapses and the wax turns thin and dark).
static func shader_seed(s: int) -> float:
	return float(posmod(s, SEED_FOLD))


## The colour of `ink`.
static func ink_color(i: Ink) -> Color:
	return Palette.PENCIL_THREAT if i == Ink.THREAT else Palette.PENCIL_PLAN


## The stroke's width in this mark's local px (the screen width over its global scale).
func width() -> float:
	return stroke_width() / _screen_k


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
		var b := PencilShapes.bounds(p, width() * 0.5)
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
	l.texture_mode = Line2D.LINE_TEXTURE_TILE
	l.texture = _tile
	l.antialiased = true
	l.material = mat
	l.default_color = Palette.NO_TINT
	add_child(l)
	return l


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


func _sync() -> void:
	if _mat == null:
		return
	_mat.set_shader_parameter(&"ink", ink_color(ink))
	_mat.set_shader_parameter(&"seed", shader_seed(seed))
	_mat.set_shader_parameter(&"dashed", dashed)
	_mat.set_shader_parameter(&"smear", smear)
	_mat.set_shader_parameter(&"alpha_max", WAX_ALPHA)
	_mat.set_shader_parameter(&"sheen", SHEEN)
	_mat.set_shader_parameter(&"dropout_px", DROPOUT_PX)
	_shadow_mat.set_shader_parameter(&"ink", Palette.PENCIL_SHADOW)
	_shadow_mat.set_shader_parameter(&"dashed", dashed)
	_shadow_mat.set_shader_parameter(&"seed", shader_seed(seed))
	if Motion.has(GLINT):
		var e := Motion.entry(GLINT)
		_mat.set_shader_parameter(&"glint_run", e.duration)
		_mat.set_shader_parameter(&"glint_rest", e.delay)
		_mat.set_shader_parameter(&"glint_strength", e.amplitude if Motion.live(GLINT) else 0.0)


## Shows the strokes between the wiped share and the written share (by length, in order).
func _apply() -> void:
	var total := total_length()
	var from := wiped_share * total
	var to := progress * total
	var acc := 0.0
	var w := width()
	if _mat != null:
		_mat.set_shader_parameter(&"width_px", w)
		_shadow_mat.set_shader_parameter(&"width_px", w)
	for i in _paths.size():
		var l := _lens[i]
		var pts := PencilShapes.trim(_paths[i], clampf(from - acc, 0.0, l), clampf(to - acc, 0.0, l))
		if smear > 0.0 and pts.size() > 1:
			# the palm drags the trailing wax along with it
			var drag := WIPE_DRAG * smear * Motion.amplitude(WIPE)
			for k in pts.size():
				var f := 1.0 - float(k) / float(pts.size() - 1)
				pts[k] += drag * f
		_lines[i].points = pts
		_lines[i].width = w
		_shadows[i].points = pts
		_shadows[i].width = w
		_shadows[i].position = SHADOW_OFFSET / _screen_k
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
