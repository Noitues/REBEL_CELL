class_name ZinePanel
extends Control
## Zine paper panel (STYLE_GUIDE 1, 4): halftone paper, ink border, tape strips, a
## slight tilt. Put content in `content` (a MarginContainer).

const PAPER_SHADER := preload("res://shaders/zine_paper.gdshader")

@export var tilt_degrees: float = 0.0
@export var tape: bool = true
@export var title: String = ""

var content: MarginContainer
var _paper: ColorRect


func _init(p_title: String = "", p_tilt: float = 0.0) -> void:
	title = p_title
	tilt_degrees = p_tilt
	_paper = ColorRect.new()
	_paper.material = ShaderMaterial.new()
	_paper.material.shader = PAPER_SHADER
	_paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_paper.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_paper)
	content = MarginContainer.new()
	content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	content.add_theme_constant_override("margin_left", 12)
	content.add_theme_constant_override("margin_right", 12)
	content.add_theme_constant_override("margin_top", 26 if p_title != "" else 12)
	content.add_theme_constant_override("margin_bottom", 12)
	add_child(content)


func _ready() -> void:
	rotation_degrees = tilt_degrees
	pivot_offset = size / 2.0


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Palette.INK, false, 2.0)
	if title != "":
		draw_string(Palette.marker(), Vector2(12, 20), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.INK)
	if tape:
		draw_rect(Rect2(size.x * 0.35, -6, 60, 14), Palette.TAPE)
		draw_rect(Rect2(-8, size.y * 0.4, 16, 40), Palette.TAPE)
