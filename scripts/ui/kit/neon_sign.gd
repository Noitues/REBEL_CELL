class_name NeonSign
extends Control
## A vertical neon shop sign (reference: the MODEM cyber shop): stacked display letters
## in a glowing tube frame with a small subtitle. Flickers a letter now and then unless
## reduce-effects. Decoration only; ignores the mouse.

var text: String = "MODEM"
var subtitle: String = ""
var color: Color = Palette.CELL_PINK
var _t: float = 0.0


func _init(p_text: String = "MODEM", p_subtitle: String = "", p_color: Color = Palette.CELL_PINK) -> void:
	text = p_text
	subtitle = p_subtitle
	color = p_color
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(78, 60 + text.length() * 50 + (70 if subtitle != "" else 0))


func _process(delta: float) -> void:
	if Settings.reduce_effects:
		return
	_t += delta
	queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2(6, 6), Vector2(size.x - 12, custom_minimum_size.y - 12))
	draw_rect(r, Color(Palette.NIGHT_SKY, 0.85))
	draw_rect(r.grow(2), Color(color, 0.15), false, 6.0)
	draw_rect(r, color, false, 2.0)
	var dead := int(_t * 0.7) % (text.length() + 3)  # one letter dips now and then
	for i in text.length():
		var ch := text[i]
		var p := Vector2(r.position.x, r.position.y + 54 + i * 50)
		var a := 0.35 if (i == dead and fmod(_t, 1.4) < 0.12) else 1.0
		for k in 3:
			draw_string(Palette.display(), p + Vector2(0, 0), ch, HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 44 + k * 2, Color(color, 0.12 * a))
		draw_string(Palette.display(), p, ch, HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 44, Color(color.lightened(0.35), a))
	if subtitle != "":
		var y := r.position.y + 40 + text.length() * 50
		var words := subtitle.split(" ")
		for w in words.size():
			draw_string(Palette.marker(), Vector2(r.position.x, y + 22 + w * 22), words[w], HORIZONTAL_ALIGNMENT_CENTER, r.size.x, 18, Palette.NET_CYAN)
