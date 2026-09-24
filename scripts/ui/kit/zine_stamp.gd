class_name ZineStamp
extends Button
## Circular rubber stamp button (STYLE_GUIDE 4: "SEND IT" for End Turn).

var stamp_text: String = "SEND IT"
var stamp_color: Color = Palette.CELL_PINK
var _hot: bool = false


func _init(p_text: String = "SEND IT", p_color: Color = Palette.CELL_PINK) -> void:
	stamp_text = p_text
	stamp_color = p_color
	custom_minimum_size = Vector2(112, 112)
	flat = true
	focus_mode = Control.FOCUS_ALL
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


func _draw() -> void:
	var c := size / 2.0
	var r := minf(size.x, size.y) / 2.0 - 4
	var col := stamp_color if not disabled else Color(stamp_color, 0.35)
	if _hot and not disabled:
		draw_circle(c, r + 4, Color(Palette.CELL_ACID, 0.45))
	draw_arc(c, r, 0, TAU, 48, col, 4.0)
	draw_arc(c, r - 9, 0, TAU, 48, col, 1.5)
	draw_string(Palette.display(), c + Vector2(-r + 12, 8), stamp_text, HORIZONTAL_ALIGNMENT_CENTER, r * 2 - 24, 20, col)
	draw_string(Palette.mono(), c + Vector2(-r + 12, 26), "[SPACE]", HORIZONTAL_ALIGNMENT_CENTER, r * 2 - 24, 11, col)
