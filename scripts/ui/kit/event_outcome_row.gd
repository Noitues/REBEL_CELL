class_name EventOutcomeRow
extends OutcomeRow
## Art pass W8c (ART_BIBLE §3.1 "never colour alone", §3.3, critique 59/60: good vs bad was
## green vs red only): an event choice's outcome row (OutcomeRow's icons and signed
## amounts, the one place a choice's numbers show) with a shape per item: an up triangle
## (▲) when it helps, a down triangle (▼) when it costs, drawn before the icon, so the row
## reads in greyscale. A neutral "no change" item gets no triangle. View only.

## The triangle's half-size as a share of the icon radius, and the gap after it.
const TRI_SHARE := 0.55
const TRI_GAP := 2.0


## The triangle's width at the row's text size (px).
func _tri_w() -> float:
	return ICON_R * TRI_SHARE * 2.0 * _scale()


func _item_width(it: Dictionary) -> float:
	var w := super(it)
	if not bool(it.get("neutral", false)):
		w += _tri_w() + TRI_GAP * _scale()
	return w


## True when `it` is shown as good (▲) — the same judgement as its colour.
static func is_good(it: Dictionary) -> bool:
	return bool(it.get("good", false))


func _draw() -> void:
	var s := _scale()
	var fs := get_theme_font_size(&"font_size", &"Label")
	var font := _font()
	var line_h := _line_height()
	var y0 := 0.0
	for line: Array in lines_at(size.x):
		var x := 0.0
		var mid := y0 + line_h * 0.5
		for k: int in line:
			var it: Dictionary = items[k]
			var neutral := bool(it.get("neutral", false))
			var col := GOOD if is_good(it) else BAD
			if neutral:
				col = Palette.INK
			if not neutral:
				# ▲ helps, ▼ costs: the shape carries what the colour says.
				var hw := _tri_w() * 0.5
				var c := Vector2(x + hw, mid)
				var pts := PackedVector2Array([c + Vector2(-hw, hw * 0.8), c + Vector2(hw, hw * 0.8), c + Vector2(0, -hw * 0.9)]) if is_good(it) \
					else PackedVector2Array([c + Vector2(-hw, -hw * 0.8), c + Vector2(hw, -hw * 0.8), c + Vector2(0, hw * 0.9)])
				draw_colored_polygon(pts, col)
				x += _tri_w() + TRI_GAP * s
			if StringName(it["kind"]) == NO_CHANGE:
				var cc := Vector2(x + ICON_R * s, mid)
				var ring := ICON_R * s * NULL_RING
				draw_arc(cc, ring, 0.0, TAU, 18, Palette.INK, 1.6 * s, true)
				var arm := Vector2(ring, -ring) * NULL_SLASH
				draw_line(cc - arm, cc + arm, Palette.INK, 1.6 * s, true)
			else:
				StatIcon.draw(self, Vector2(x + ICON_R * s, mid), ICON_R * s, StringName(it["kind"]), Palette.INK)
			x += (ICON_R * 2.0 + ICON_GAP) * s
			var t := String(it["text"])
			draw_string(font, Vector2(x, mid + font.get_ascent(fs) * 0.5 - font.get_descent(fs) * 0.25), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
			x += font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x + ITEM_GAP * s
		y0 += line_h + LINE_GAP * s
