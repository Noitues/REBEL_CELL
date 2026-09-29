class_name IconLine
extends Control
## A second line under a button's words (H24 S13: the title's Continue line ran into two
## lines of words reading like debug output): a lead word or two, then numbers each after
## its StatIcon ("Solace Biosystems   [flame] 14   [snowflake] 0   [runs] 3"), in the
## button's font a size smaller. `attach` puts it under the button's words and gives the
## button room for it. Draw only; the words come translated.

## Icon radius, the gap after an icon and between items at text scale 1.0 (px).
const ICON_R := 7.0
const ICON_GAP := 3.0
const ITEM_GAP := 12.0
## The line's lettering as a share of the button's.
const FONT_SHARE := 0.85

## The words before the numbers (translated).
var lead: String = ""
## [{kind: StringName, text: String}] drawn in order after the lead.
var items: Array[Dictionary] = []
## The colour of the words.
var color: Color = Palette.TERMINAL_TEXT
## The icons' colour (art pass W8a: on a filled primary they take the words' ink, 3:1 and
## more, ART_BIBLE 3.7); Palette.AUTO = each icon's own colour.
var icon_color: Color = Palette.AUTO


func _init(p_lead: String = "", p_items: Array[Dictionary] = []) -> void:
	name = "IconLine"
	lead = p_lead
	items = p_items
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE


## Puts `line` under the words of button `b` (the button's boxes get room at the bottom).
static func attach(b: Button, line: IconLine) -> void:
	b.add_child(line)
	line._fit_parent.call_deferred()


func _scale() -> float:
	return maxf(1.0, get_theme_font_size(&"font_size", &"Label") / float(UiTheme.BASE_SIZE))


func _fs() -> int:
	return maxi(8, roundi(get_theme_font_size(&"font_size", &"Label") * FONT_SHARE))


func _font() -> Font:
	return get_theme_font(&"font", &"Label")


## The line's width and height as drawn.
func _get_minimum_size() -> Vector2:
	var s := _scale()
	var fs := _fs()
	var w := _font().get_string_size(lead, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	for it in items:
		w += ITEM_GAP * s + (ICON_R * 2.0 + ICON_GAP) * s + _font().get_string_size(String(it["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	return Vector2(w, maxf(ICON_R * 2.0 * s, _font().get_height(fs)))


## The rects of the lead words and of each item (icon and text), local (tests: nothing
## overlaps).
func part_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var s := _scale()
	var fs := _fs()
	var h := size.y
	var x := 0.0
	var lw := _font().get_string_size(lead, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	out.append(Rect2(0, 0, lw, h))
	x += lw
	for it in items:
		x += ITEM_GAP * s
		var w := (ICON_R * 2.0 + ICON_GAP) * s + _font().get_string_size(String(it["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		out.append(Rect2(x, 0, w, h))
		x += w
	return out


func _notification(what: int) -> void:
	if what == NOTIFICATION_THEME_CHANGED:
		update_minimum_size()
		_fit_parent.call_deferred()
		queue_redraw()


## Room at the bottom of the parent button for the line; the line placed in it.
func _fit_parent() -> void:
	var b := get_parent() as Button
	if b == null:
		return
	var h := get_combined_minimum_size().y
	var left := 0.0
	var bottom := 0.0
	for st in [&"normal", &"hover", &"pressed", &"hover_pressed", &"focus", &"disabled"]:
		b.remove_theme_stylebox_override(st)
		var sb := b.get_theme_stylebox(st)
		if sb == null:
			continue
		if st == &"normal":
			left = sb.get_margin(SIDE_LEFT)
			bottom = sb.get_margin(SIDE_BOTTOM)
		var room := sb.duplicate() as StyleBox
		room.content_margin_bottom = sb.get_margin(SIDE_BOTTOM) + h + 2.0
		b.add_theme_stylebox_override(st, room)
	set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	# Under the words: past the button's icon slot (IconMark) when it has one.
	var icon_room := (b.icon.get_width() + b.get_theme_constant(&"h_separation")) if b.icon != null else 0
	offset_left = left + icon_room
	offset_right = -left
	offset_bottom = -bottom
	offset_top = -bottom - h
	b.custom_minimum_size.x = maxf(b.custom_minimum_size.x, offset_left + get_combined_minimum_size().x + left)


func _draw() -> void:
	var s := _scale()
	var fs := _fs()
	var font := _font()
	var mid := size.y * 0.5
	var base := mid + font.get_ascent(fs) * 0.5 - font.get_descent(fs) * 0.25
	draw_string(font, Vector2(0, base), lead, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, color)
	var x := font.get_string_size(lead, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	for it in items:
		x += ITEM_GAP * s
		var kind := StringName(it["kind"])
		StatIcon.draw(self, Vector2(x + ICON_R * s, mid), ICON_R * s, kind, icon_color if icon_color.a > 0.0 else StatIcon.color_of(kind))
		x += (ICON_R * 2.0 + ICON_GAP) * s
		var t := String(it["text"])
		draw_string(font, Vector2(x, base), t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, color)
		x += font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
