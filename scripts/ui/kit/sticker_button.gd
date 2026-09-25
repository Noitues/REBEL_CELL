class_name StickerButton
extends Button
## A taped paper sticker that presses like a button (combat actions around the spinner:
## NUDGE, RESPIN, UNDO and the toggles). Marker text on note paper, a tilt, tape; hover or
## focus lifts it with an acid glow. The scene decides what a press means.

var paper: Color = Palette.NOTE_YELLOW
var tilt: float = 0.0
var _hot: bool = false


func _init(p_text: String = "", p_paper: Color = Palette.NOTE_YELLOW, p_tilt: float = 0.0) -> void:
	text = p_text
	paper = p_paper
	tilt = p_tilt
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		add_theme_color_override(key, Color(0, 0, 0, 0))  # the sticker draws its own text
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())
	_fit()


func _fit() -> void:
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 14).x + 22
	custom_minimum_size = Vector2(maxf(64.0, w), 30)
	size = custom_minimum_size


func set_label(t: String) -> void:
	if t != text:
		text = t
		_fit()
		queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_set_transform(size * 0.5, deg_to_rad(tilt), Vector2.ONE)
	var rr := Rect2(-size * 0.5, size)
	if _hot and not disabled:
		draw_rect(rr.grow(3), Color(Palette.CELL_ACID, 0.5))
	draw_rect(Rect2(rr.position + Vector2(3, 4), rr.size), Palette.SHADOW)
	draw_rect(rr, paper if not disabled else paper.darkened(0.45))
	draw_rect(rr, Color(Palette.INK, 0.45), false, 1.0)
	draw_rect(Rect2(Vector2(-12, rr.position.y - 5), Vector2(24, 9)), Palette.NOTE_TAPE)
	draw_string(Palette.marker(), rr.position + Vector2(0, 21), text, HORIZONTAL_ALIGNMENT_CENTER, rr.size.x, 14, Palette.INK if not disabled else Color(Palette.INK, 0.5))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	r = r
