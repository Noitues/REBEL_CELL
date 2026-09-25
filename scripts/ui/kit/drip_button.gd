class_name DripButton
extends Button
## Words sprayed in dripping marker (the Cell's voice) that still press like a button:
## no box and no circle, just the tag with paint drips and an optional key hint in system
## mono underneath ("SEND IT" / "[SPACE]", "LEAVE THE MODEM"). Hover/focus brighten the
## paint and add a halo so pad and mouse players see where they are.

var tag_text: String = ""
var key_hint: String = ""
var paint: Color = Palette.CELL_PINK
var font_size: int = 44
var _hot: bool = false


func _init(p_text: String = "SEND IT", p_hint: String = "", p_color: Color = Palette.CELL_PINK, p_size: int = 44) -> void:
	tag_text = p_text
	key_hint = p_hint
	paint = p_color
	font_size = p_size
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	var w := Palette.marker().get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	custom_minimum_size = Vector2(w + 24, font_size * 1.1 + 30 + (18 if key_hint != "" else 0))
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


func _draw() -> void:
	var col := paint if not disabled else Color(paint, 0.35)
	if _hot and not disabled:
		col = paint.lightened(0.25)
	var base := Vector2(12, font_size * 1.0)
	var f := Palette.marker()
	var w := f.get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	if _hot and not disabled:
		for k in 6:
			draw_string(f, base + Vector2(k - 3, (k * 7) % 5 - 2), tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(Palette.CELL_ACID, 0.12))
	draw_string(f, base + Vector2(3, 3), tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(0, 0, 0, 0.7))
	draw_string(f, base, tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, col)
	# Drips: deterministic from the text, under the letters.
	var drips := maxi(3, tag_text.length())
	for i in drips:
		var h := absi(hash([tag_text, i]))
		var x := 16.0 + (w - 20.0) * float(i) / drips + float(h % 11)
		var length := 6.0 + float(h % 23) * (1.0 + font_size / 60.0)
		var y0 := base.y + 2.0
		draw_line(Vector2(x, y0), Vector2(x, y0 + length), col, maxf(2.0, font_size / 16.0))
		draw_circle(Vector2(x, y0 + length), maxf(1.8, font_size / 20.0), col)
	if key_hint != "":
		draw_string(Palette.mono(), Vector2(14, size.y - 6), key_hint, HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color(Palette.PAPER, 0.75))
