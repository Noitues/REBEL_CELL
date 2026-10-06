class_name RubberStamp
extends Control
## ART-11 4D: an Anton rubber stamp on corp paper (ART_BIBLE v2 §1.2: CASE CLOSED, PROCESSED,
## the corporation's verb on its ransom notice): framed lettering in uneven ink, tilted. It
## slams down with a motion entry (a pop from big to its rest size), or shows at rest when that
## motion does not play. Look only; the screen says when it lands.

const SHADER := preload("res://shaders/rubber_stamp.gdshader")

var text: String = ""
var color: Color = Palette.END_STAMP_RED
## The lettering size at text scale 1.0 (px) and the tilt (degrees).
var font_size: int = UiTheme.DISPLAY
var tilt: float = -8.0
## The stamp has landed (it shows); before `slam` it is hidden.
var landed: bool = true

## The frame's line and the gap between frame and words (share of the lettering size).
const FRAME_SHARE := 0.09
const GAP_SHARE := 0.32


func _init(p_text: String = "", p_color: Color = Palette.END_STAMP_RED, p_font_size: int = UiTheme.DISPLAY, p_tilt: float = -8.0) -> void:
	text = p_text
	color = p_color
	font_size = p_font_size
	tilt = p_tilt
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	var m := ShaderMaterial.new()
	m.shader = SHADER
	m.set_shader_parameter(&"seed", float(p_text.hash() % 97))
	material = m
	refit()
	MotionSkip.register_passive(self)  # ANIM-R6 D7: the slam lands with any press that ends a motion


## The lettering size now (px).
func font_px() -> int:
	return roundi(font_size * Settings.text_scale)


## Measures the stamp at the text size now.
func refit() -> void:
	var f := Palette.display()
	var fs := font_px()
	var gap := fs * GAP_SHARE
	custom_minimum_size = Vector2(f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + gap * 2.0, f.get_ascent(fs) * 0.92 + gap * 2.0)
	size = custom_minimum_size
	pivot_offset = size * 0.5
	rotation_degrees = tilt
	queue_redraw()


## Hidden until `slam` lands it.
func hold_back() -> void:
	landed = false
	visible = false


## Lands the stamp with motion `id` (a pop down from `amplitude` x its size); at rest at once
## when the motion does not play. Returns the tween or null.
func slam(id: StringName) -> Tween:
	landed = true
	visible = true
	_slam = Motion.pop(self, id)
	return _slam


var _slam: Tween = null


## MotionSkip (ANIM-R6 D7, a short motion: `register_passive`): the slam still lands.
func motion_running() -> bool:
	return _slam != null and _slam.is_valid() and _slam.is_running()


## MotionSkip: the stamp at rest (its size).
func complete_motion() -> void:
	Motion.settle(self, ^"scale")
	_slam = null


func _draw() -> void:
	var f := Palette.display()
	var fs := font_px()
	var line := maxf(2.0, fs * FRAME_SHARE)
	var r := Rect2(Vector2.ONE * line * 0.5, size - Vector2.ONE * line)
	draw_rect(r, color, false, line)
	var gap := fs * GAP_SHARE
	draw_string(f, Vector2(gap, gap + f.get_ascent(fs) * 0.92), text, HORIZONTAL_ALIGNMENT_CENTER, size.x - gap * 2.0, fs, color)
