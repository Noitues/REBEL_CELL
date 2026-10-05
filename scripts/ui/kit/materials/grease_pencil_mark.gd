class_name GreasePencilMark
extends Node2D
## A grease pencil mark (ART-1 1B; ART_BIBLE v2 §1.2 "Grease pencil", §6.3, §6.4): plans and
## annotations that are true to the rules. One mark is one or more strokes in writing order
## (a circle; an arrow's shaft and its two head flicks; a route). Each stroke is a `Line2D`
## with round caps, width 8-10, `shaders/kit/marker_stroke.gdshader` (opaque wax, alpha 0.96,
## bristles, dropouts, ragged edge, sheen line, the glint) over a duplicate under-shadow
## offset SHADOW_OFFSET. Yellow `PENCIL_PLAN` = our plan / valid; red `PENCIL_THREAT` = threat
## / invalid / loss. Solid = what will happen; dashed = what-if.
##
## Writes on in writing order (`pencil_write_on`) and wipes off with a cloth wipe
## (`pencil_wipe`), both by trimming points, never alpha. `PencilShapes.snap_to` keeps a
## mark on a real edge. Pencil is above all UI and no UI ever covers it: every mark is in
## the `GROUP` group, which `PencilLint` checks. Reduce effects / headless / switched off:
## written whole at once, wiped at once, no glint. A view only.

signal written
signal wiped

enum Ink { PLAN, THREAT }

const SHADER := preload("res://shaders/kit/marker_stroke.gdshader")
## Every mark on screen (PencilLint).
const GROUP := &"grease_pencil"
const WRITE := &"pencil_write_on"
const WIPE := &"pencil_wipe"
const GLINT := &"pencil_glint"
## Look (§6.3): width, under-shadow offset (round 3 kit: a 4 px cast shadow), resample step.
const WIDTH := 10.0
const SHADOW_OFFSET := Vector2(3.0, 4.0)
const SHADOW_GROW := 3.0
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
@export var width: float = WIDTH:
	set(v):
		width = v
		_apply()
## The wax's seed (grain and dropouts).
@export var seed: int = 1:
	set(v):
		seed = v
		_sync()

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


func _init() -> void:
	add_to_group(GROUP)
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
	Settings.changed.connect(_sync)
	_sync()


## The colour of `ink`.
static func ink_color(i: Ink) -> Color:
	return Palette.PENCIL_THREAT if i == Ink.THREAT else Palette.PENCIL_PLAN


## Adds a stroke (local points) after the others in writing order.
func add_stroke(points: PackedVector2Array) -> void:
	var p := PencilShapes.resample(points, STEP_PX)
	_paths.append(p)
	_lens.append(PencilShapes.length_of(p))
	var sh := _make_line(_shadow_mat, width + SHADOW_GROW)
	sh.position = SHADOW_OFFSET
	_shadows.append(sh)
	var ln := _make_line(_mat, width)
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
		var b := PencilShapes.bounds(p, width * 0.5 + SHADOW_GROW)
		b.end += SHADOW_OFFSET
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
			out.append(xf * PencilShapes.bounds(seg, width * 0.5))
			i = j
	return out


func _make_line(mat: ShaderMaterial, w: float) -> Line2D:
	var l := Line2D.new()
	l.width = w
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


func _sync() -> void:
	if _mat == null:
		return
	_mat.set_shader_parameter(&"ink", ink_color(ink))
	_mat.set_shader_parameter(&"seed", float(seed))
	_mat.set_shader_parameter(&"dashed", dashed)
	_mat.set_shader_parameter(&"smear", smear)
	_shadow_mat.set_shader_parameter(&"ink", Palette.PENCIL_SHADOW)
	_shadow_mat.set_shader_parameter(&"dashed", dashed)
	_shadow_mat.set_shader_parameter(&"seed", float(seed))
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
	for i in _paths.size():
		var l := _lens[i]
		var pts := PencilShapes.trim(_paths[i], clampf(from - acc, 0.0, l), clampf(to - acc, 0.0, l))
		if smear > 0.0 and pts.size() > 1:
			# the palm drags the trailing wax along with it
			var drag := WIPE_DRAG * smear * Motion.amplitude(WIPE)
			for k in pts.size():
				var w := 1.0 - float(k) / float(pts.size() - 1)
				pts[k] += drag * w
		_lines[i].points = pts
		_lines[i].width = width
		_shadows[i].points = pts
		_shadows[i].width = width + SHADOW_GROW
		acc += l


# --- Motion ------------------------------------------------------------------------------

func motion_running() -> bool:
	return _tween != null and _tween.is_valid() and _tween.is_running()


func complete_motion() -> void:
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


## Writes the mark on in writing order at `pencil_write_on`'s speed (px/s), capped at its
## duration. Returns the seconds (0: written whole at once).
func write_on() -> float:
	if motion_running():
		complete_motion()
	wiped_share = 0.0
	smear = 0.0
	if not Motion.live(WRITE):
		progress = 1.0
		_end(WRITE)
		return 0.0
	var e := Motion.entry(WRITE)
	var d := minf(total_length() / maxf(e.amplitude, 1.0), e.duration) / maxf(Motion.speed, Motion.SPEED_MIN)
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
