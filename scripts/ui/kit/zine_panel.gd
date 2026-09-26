class_name ZinePanel
extends Control
## Zine paper panel (STYLE_GUIDE 1, 4): halftone paper, ink border, tape strips, a
## slight tilt. Put content in `content` (a MarginContainer).

const PAPER_SHADER := preload("res://shaders/zine_paper.gdshader")

@export var tilt_degrees: float = 0.0
@export var tape: bool = true
@export var title: String = ""
## System dialogs (options, pause, confirm) render as terminal glass instead of paper:
## DISPATCH-style system surfaces stay clean (STYLE_GUIDE 3).
var terminal: bool = false

var content: MarginContainer
var _paper: ColorRect


func _init(p_title: String = "", p_tilt: float = 0.0, p_terminal: bool = false) -> void:
	title = p_title
	tilt_degrees = p_tilt
	terminal = p_terminal
	tape = not p_terminal
	_paper = ColorRect.new()
	if terminal:
		_paper.color = Palette.TERMINAL_BG
		_paper.color.a = 0.97
		_paper.material = UiTheme.crt_material()
	else:
		_paper.material = ShaderMaterial.new()
		_paper.material.shader = PAPER_SHADER
	# Behind the panel's own drawing, so the border and title stay on top of the paper.
	_paper.show_behind_parent = true
	_paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_paper.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_paper)
	content = MarginContainer.new()
	content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	content.add_theme_constant_override("margin_left", 12)
	content.add_theme_constant_override("margin_right", 12)
	content.add_theme_constant_override("margin_top", (34 if p_terminal else 26) if p_title != "" else 12)
	content.add_theme_constant_override("margin_bottom", 12)
	add_child(content)


func _ready() -> void:
	rotation_degrees = tilt_degrees
	pivot_offset = size / 2.0


func _draw() -> void:
	if terminal:
		_draw_terminal()
		return
	# The drop shadow only where it shows (right and bottom edges): the paper sits behind
	# this drawing, so a full shadow rect would darken the whole sheet.
	draw_rect(Rect2(Vector2(size.x, 6), Vector2(5, size.y)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(5, size.y), Vector2(size.x - 5, 6)), Palette.SHADOW)
	draw_rect(Rect2(Vector2.ZERO, size), Palette.INK, false, 2.0)
	if title != "":
		draw_string(Palette.marker(), Vector2(12, 20), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.INK)
	if tape:
		draw_rect(Rect2(size.x * 0.35, -6, 60, 14), Palette.TAPE)
		draw_rect(Rect2(-8, size.y * 0.4, 16, 40), Palette.TAPE)


func _draw_terminal() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(Vector2(size.x, 8), Vector2(6, size.y)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(6, size.y), Vector2(size.x - 6, 8)), Palette.SHADOW)
	draw_rect(r, Palette.TERMINAL_EDGE, false, 1.0)
	if title != "":
		draw_string(Palette.mono(), Vector2(14, 22), title, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.PAPER)
		draw_rect(Rect2(12, 28, size.x - 24, 2), Color(Palette.CELL_PINK, 0.85))
	for c in [r.position, Vector2(r.end.x, 0), r.end, Vector2(0, r.end.y)]:
		var sx := 1.0 if c.x <= 0.0 else -1.0
		var sy := 1.0 if c.y <= 0.0 else -1.0
		draw_line(c, c + Vector2(14 * sx, 0), Palette.NET_CYAN, 2.0)
		draw_line(c, c + Vector2(0, 14 * sy), Palette.NET_CYAN, 2.0)
