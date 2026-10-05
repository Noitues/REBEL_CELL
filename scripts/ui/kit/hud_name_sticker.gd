class_name HudNameSticker
extends Control
## ART-2 2D (ART_BIBLE v2 §3.1): the operative's name plate, a pink vinyl sticker slapped
## just above the RAM readout, bottom left: "CELL-9 // BREAKER" (the operative's name, then
## the class) in Anton ink on the Cell's pink, a white die-cut and a slight tilt. Static;
## words arrive translated. View only.

## Lettering size, padding, die-cut and tilt (px / degrees at text scale 1.0).
const NAME_FONT := 24
const PAD_X := 16.0
const PAD_Y := 6.0
const TILT := -2.5
## A sticker is a baked object: it grows with the text up to this scale (§2.9).
const MAX_SCALE := 1.3

var words: String = ""


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_PASS
	tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	material = HudSkin.vinyl_material()


## Shows "<name> // <class>" (both already translated); one word when they are the same.
func set_names(operative: String, class_word: String) -> void:
	var a := operative.strip_edges().to_upper()
	var b := class_word.strip_edges().to_upper()
	var w := b if a == "" or a == b else ("%s // %s" % [a, b] if b != "" else a)
	if w == words:
		return
	words = w
	tooltip_text = w
	_fit()
	queue_redraw()


static func font_px() -> int:
	return roundi(NAME_FONT * minf(Settings.text_scale, MAX_SCALE))


func _fit() -> void:
	var s := minf(Settings.text_scale, MAX_SCALE)
	var w := HudSkin.display().get_string_size(words, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px()).x
	custom_minimum_size = Vector2(w + PAD_X * 2.0 * s + HudSkin.VINYL_DIE_CUT_PX * s, HudSkin.display().get_height(font_px()) + PAD_Y * 2.0 * s + HudSkin.VINYL_DIE_CUT_PX * s)


func _draw() -> void:
	if words == "":
		return
	var s := minf(Settings.text_scale, MAX_SCALE)
	var cut := HudSkin.VINYL_DIE_CUT_PX * s * 0.5
	var r := Rect2(Vector2(cut, cut), size - Vector2(cut, cut) * 2.0)
	draw_set_transform(size * 0.5, deg_to_rad(TILT), Vector2.ONE)
	r.position -= size * 0.5
	draw_rect(Rect2(r.position + Vector2(3.0, 5.0) * s, r.size).grow(cut), Color(Palette.NIGHT_SKY, 0.5))
	draw_rect(r.grow(cut), HudSkin.VINYL_DIE_CUT)
	draw_rect(r, HudSkin.VINYL_PINK.lightened(HudSkin.VINYL_LIGHT * 0.4))
	draw_rect(Rect2(r.position + Vector2(0.0, r.size.y * 0.55), Vector2(r.size.x, r.size.y * 0.45)), HudSkin.VINYL_PINK)
	draw_rect(Rect2(r.position, Vector2(r.size.x, r.size.y * 0.18)), Color(HudSkin.VINYL_DIE_CUT, HudSkin.VINYL_GLOSS_REST))
	var f := HudSkin.display()
	var fs := font_px()
	var base := Vector2(r.position.x + PAD_X * s, r.position.y + (r.size.y + f.get_ascent(fs) - f.get_descent(fs)) * 0.5)
	draw_string(f, base, words, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, HudSkin.VINYL_KEYLINE)
	draw_set_transform(Vector2.ZERO)
