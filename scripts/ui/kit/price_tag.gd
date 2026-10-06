class_name PriceTag
extends Control
## HQ-B (M14, designer ruling Q11; `q11_a_claim.png`, `direction_B_market.jpg`): a price as a
## gold terminal tag (`30  SCHEMATICS`) under a sticker. Bible 1.2: values that change are
## never on a sticker, so the verb's sticker keeps its word and its price sits here. Words
## grow with the text (they are words). View only; `text` is what it reads.

## Lettering (px at 1.0), padding (px at 1.0).
const PX := 12
const PAD := Vector2(8, 3)
const LETTER_SPACING := 1.5

var text: String = "":
	set(v):
		text = v
		_refit()
var color: Color = Palette.RESIST_GOLD


func _init(p_text: String = "", p_color: Color = Palette.RESIST_GOLD) -> void:
	name = "PriceTag"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	color = p_color
	text = p_text


func _ready() -> void:
	Settings.changed.connect(_refit)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_refit):
		Settings.changed.disconnect(_refit)


func _px() -> int:
	return roundi(PX * Settings.text_scale)


func _width() -> float:
	var f := Palette.mono()
	var w := 0.0
	for ch in text:
		w += f.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, _px()).x + LETTER_SPACING
	return w


func _refit() -> void:
	var s := Settings.text_scale
	custom_minimum_size = Vector2(ceilf(_width() + PAD.x * 2.0 * s), ceilf(Palette.mono().get_height(_px()) + PAD.y * 2.0 * s))
	queue_redraw()


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(r, Color(Palette.NIGHT_SKY, 0.92))
	draw_rect(r, color, false, 1.5)
	var f := Palette.mono()
	var px := _px()
	var x := (size.x - _width()) * 0.5
	var y := size.y * 0.5 + f.get_ascent(px) * 0.5 - f.get_descent(px) * 0.3
	for ch in text:
		draw_string(f, Vector2(x, y), ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px, color)
		x += f.get_string_size(ch, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x + LETTER_SPACING
