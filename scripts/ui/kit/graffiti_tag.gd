class_name GraffitiTag
extends Control
## Graffiti tag with drips (STYLE_GUIDE 4, HQ): marker text in cell_pink with a spray
## halo and paint drips. Original motif; the Cell mascot is a grinning hexagon "cell".

var text: String = "REBEL_CELL"


## Lettering (px), the words' left edge and the room the mascot takes at the right (px).
const FONT_SIZE := UiTheme.DISPLAY
const LEFT := 12.0
const MASCOT_ROOM := 80.0
const MIN_WIDTH := 340.0


## The lettering drawn now (FONT_SIZE, or smaller when `fit_width` shrank it).
var font_size: int = FONT_SIZE
## ANIM-R4 C7: the smallest the lettering shrinks to fit a window.
const MIN_FONT := UiTheme.TITLE


## `p_text` is shown as given (the caller translates it; H24 S3); the tag is as wide as its
## words and the mascot (H24: a translated "LOOT: pick a card" ran under the mascot).
func _init(p_text: String = "REBEL_CELL") -> void:
	text = p_text
	_fit()
	mouse_filter = Control.MOUSE_FILTER_IGNORE


## ANIM-R4 C7: the words shrink until the tag (words and mascot) fits `width` px (the loot
## window: under pseudolocalisation the tag ran out of it and the mascot sat on the words).
func fit_width(width: float) -> GraffitiTag:
	font_size = FONT_SIZE
	while font_size > MIN_FONT and words_width() + LEFT + MASCOT_ROOM > width:
		font_size -= 1
	_fit()
	return self


## The words' width as drawn (px).
func words_width() -> float:
	return Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x


func _fit() -> void:
	custom_minimum_size = Vector2(maxf(MIN_WIDTH, LEFT + words_width() + MASCOT_ROOM), 104)
	queue_redraw()


func _draw() -> void:
	var base := Vector2(LEFT, 58)
	for i in 6:
		draw_string(Palette.marker(), base + Vector2(i - 3, (i * 7) % 5 - 2), text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size, Color(Palette.CELL_PINK, 0.08))
	# ANIM-R4 C7: the words arrive translated: drawn as given (translated again, the
	# pseudolocalised tag grew past its measured width and under the mascot).
	DripButton.draw_drip_text(self, base, text, font_size, DripButton.DRIP_PINK, DripButton.auto_drips(text), true, true, false)
	# The Cell mascot: a grinning hexagon.
	var c := Vector2(size.x - 40, 40)
	var pts := PackedVector2Array()
	for k in 6:
		pts.append(c + Vector2(cos(k * TAU / 6.0), sin(k * TAU / 6.0)) * 22)
	draw_colored_polygon(pts, Palette.CELL_ACID)
	draw_polyline(pts + PackedVector2Array([pts[0]]), Palette.INK, 2.0)
	draw_circle(c + Vector2(-7, -5), 3, Palette.INK)
	draw_circle(c + Vector2(7, -5), 3, Palette.INK)
	draw_arc(c + Vector2(0, 2), 10, 0.3, PI - 0.3, 12, Palette.INK, 2.0)
