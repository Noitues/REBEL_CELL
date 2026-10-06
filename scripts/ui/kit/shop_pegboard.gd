class_name ShopPegboard
extends MarginContainer
## ART-9 4A (ART_BIBLE v2 §4.10, round 34 `shop_v5`): the MAINFRAME's pegboard under the sign
## plate, as the concept drew it (MainframeArt "pegboard": shop.pegboard, its frame kept and its
## hole grid cut to the board's size), its section titles on the concept's label-maker tape
## (shop.dymo: CARDS, FIRMWARE, DAEMONS; lettered live in another language), and the strip of pink
## anti-static foam the Firmware chips are pushed into (shop_v5.foam). Holds the shelves (laid out
## by the caller). View only.

## The board's art frame (concept px) and the board's inner margin (px at scale 1).
const ART_EDGE := 12.0
const MARGIN := 26.0
## A tape's lettering (px at scale 1) when lettered live, and its padding.
const TAPE_PX := 20
const TAPE_PAD := Vector2(10, 3)
## The foam strip's height (game px at scale 1: shop_v5.foam 34 x MainframeArt.SCALE).
const FOAM_H := 23.0

## The row whose items stand in the foam (the Firmware chips), if any.
var foam_row: Control = null


func _init(ts: float = 1.0) -> void:
	name = "Pegboard"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	for side in ["left", "right", "top", "bottom"]:
		add_theme_constant_override("margin_" + side, roundi(MARGIN * ts))


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	draw_rect(Rect2(r.position + Vector2(6, 8), r.size), Palette.SHADOW)
	MainframeArt.draw_9(self, "pegboard", r, ART_EDGE)
	_draw_foam()


## The foam strip across the Firmware row, at the chips' pins (behind the chips).
func _draw_foam() -> void:
	if foam_row == null or not is_instance_valid(foam_row) or not foam_row.is_visible_in_tree():
		return
	var row := Rect2(foam_row.global_position - global_position, foam_row.size)
	var line := row.position.y + 10.0
	var k := 1.0
	for c in foam_row.get_children():
		var item := c as ShopItem
		if item != null:
			var o := item.object_rect()
			line = row.position.y + item.position.y + o.position.y + o.size.y * ShopItem.CHIP_PIN_LINE
			k = item.obj_scale()
			break
	var h := FOAM_H * k
	MainframeArt.draw_h3(self, "foam", Rect2(Vector2(row.position.x - 8.0, line - h * 0.5), Vector2(row.size.x + 16.0, h)), 6.0, 6.0)


## A section title on label-maker tape: the concept's own tape for `key` ("CARDS") in English,
## lettered live (black tape, white Anton) in another language.
static func tape(key: String, ts: float = 1.0) -> Control:
	var art := MainframeArt.dymo(key)
	if art != null:
		var t := TextureRect.new()
		t.name = "Tape"
		t.texture = art
		t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		t.custom_minimum_size = art.get_size() * MainframeArt.SCALE * ts
		t.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		t.mouse_filter = Control.MOUSE_FILTER_IGNORE
		t.tooltip_text = ""
		t.set_meta(&"words", key)
		return t
	var l := Label.new()
	l.text = TranslationServer.translate(key).to_upper()
	l.name = "Tape"
	l.add_theme_font_override(&"font", Palette.display())
	l.add_theme_font_size_override(&"font_size", roundi(TAPE_PX * ts))
	l.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	l.add_theme_color_override(&"font_shadow_color", Palette.SHADOW)
	l.add_theme_constant_override(&"shadow_offset_y", 1)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Palette.LABEL_TAPE
	sb.content_margin_left = TAPE_PAD.x * ts
	sb.content_margin_right = TAPE_PAD.x * ts
	sb.content_margin_top = TAPE_PAD.y * ts
	sb.content_margin_bottom = TAPE_PAD.y * ts
	sb.shadow_color = Palette.SHADOW
	sb.shadow_size = 3
	sb.shadow_offset = Vector2(2, 2)
	l.add_theme_stylebox_override(&"normal", sb)
	l.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l
