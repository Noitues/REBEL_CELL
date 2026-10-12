class_name SiteHoloCard
extends RaidHolo
## B4 (M14 integration review section c "HQ page, direction B"; round 44 `hq_idle.png`): the
## selected corporate Site's file at the HQ is hacked intel, so it is a decrypted holo (round 37
## DEPOT 15), not a terminal (the Cell's own nodes keep their terminal cards). RaidHolo's look
## (the corp's tint, 4 px scanlines, slow bands, the RGB split on the edge, the cracked seal and
## the DECRYPTED stamp at its foot) with the Site's header: "T2  //  PRIORITY LANE EXCHANGE"
## over "MERIDIAN FREIGHT  //  SITE FILE 207", then its rows (TYPE, REWARDS, LINK: a caption in
## the holo's ink, the value in paper white) and what the HQ adds under them (IF CLEARED, the
## runner, why it can't be run). A container like RaidHolo: the scene fills `body`. View only.

## The sub line's words (a translation key): the corporation and the file number.
const FILE_LINE := "%s  //  SITE FILE %s" # TR
## The file numbers run 0..FILE_NUMBERS - 1 (a hash of the Site's id, never an RNG).
const FILE_NUMBERS := 1000
## A row's caption column (px at text scale 1.0) and the gap to its value.
const CAPTION_W := 96.0
const ROW_GAP := 10.0
## M14 12Q-HQ: the header's least height (RaidHolo's HEAD_H) and the pad above the header and under
## the rows grow with the text only to this scale (STYLE 5.6's x1.3 for drawn objects); past it the
## header is as tall as its words (at 2.0 the floor and pads left the rows no room in the HQ's card
## column).
const HEAD_SCALE_MAX := 1.3

## The sub line under the title (already translated).
var sub: String = ""


func _init(p_corporation: StringName = &"halcyon", p_title: String = "", p_sub: String = "") -> void:
	super(p_corporation, p_title, "")
	sub = p_sub
	name = "SelectedSite"
	resized.connect(_fit_head)


## The file number of Site `site_id` (a hash, stable across runs).
static func file_number(site_id: StringName) -> int:
	return absi(hash(String(site_id))) % FILE_NUMBERS


## A row: `caption` (mono caps, the holo's ink) and `value` (paper white, wraps). Returns the
## value's Label.
func add_row(row_name: String, caption: String, value: String) -> Label:
	var row := HBoxContainer.new()
	row.name = row_name
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", roundi(ROW_GAP * _k))
	var cap := Label.new()
	cap.name = "Caption"
	cap.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	cap.text = caption
	cap.custom_minimum_size.x = CAPTION_W * _k
	cap.add_theme_font_override("font", Palette.mono())
	cap.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	cap.add_theme_color_override("font_color", DecryptedHoloPanel.ink(skin.holo))
	cap.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	cap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_child(cap)
	var v := Label.new()
	v.name = "Value"
	v.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	v.text = value
	v.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.BODY))
	v.add_theme_color_override("font_color", Palette.PAPER)
	v.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	UiWrap.whole_words(v)
	v.mouse_filter = Control.MOUSE_FILTER_PASS
	row.add_child(v)
	body.add_child(row)
	return v


## B4 polish (art director): the DECRYPTED stamp and its cracked seal at this share of the raid
## holo's, in the card's lower-right corner, under the rows (never over IF CLEARED).
const STAMP_SHARE := 0.6


func _place_stamp() -> void:
	if holo == null or holo.stamp_slot == null:
		return
	var slot := holo.stamp_slot
	slot.scale = Vector2.ONE * STAMP_SHARE
	slot.position = size - slot.size * STAMP_SHARE - Vector2(UiTheme.SP_S, UiTheme.SP_XS)


func _fit_stamp(_n: Node = null) -> void:
	var foot := DecryptedHoloPanel.STAMP_SLOT.y * STAMP_SHARE + UiTheme.SP_XS
	var box := get_theme_stylebox(&"panel") as StyleBoxEmpty
	if box != null and not is_equal_approx(box.content_margin_bottom, PAD * minf(_k, HEAD_SCALE_MAX) + foot):
		box.content_margin_bottom = PAD * minf(_k, HEAD_SCALE_MAX) + foot
		queue_sort()


## The DECRYPTED stamp's rect (local, as drawn: scaled).
func stamp_rect() -> Rect2:
	if holo == null or holo.stamp_slot == null:
		return Rect2()
	return Rect2(holo.stamp_slot.position, holo.stamp_slot.size * STAMP_SHARE)


## The words of every row ("TYPE: ..."), for tests and screen readers.
func rows_text() -> PackedStringArray:
	var out := PackedStringArray()
	for r in body.get_children():
		if r is HBoxContainer and r.get_node_or_null("Caption") != null:
			out.append("%s: %s" % [(r.get_node("Caption") as Label).text, (r.get_node("Value") as Label).text])
	return out


## The header: the title in the display face and the sub line in the mono, both in the holo's
## ink (RaidHolo's header with the Site's own sub line), each wrapped at a word onto more lines
## when it is wider than the card (ART-5 acceptance: draw_string cut the line at the card's edge;
## Meridian's file number was lost at 1.0, every long title at 2.0). The header grows to hold them.
func _header(on: Control) -> void:
	var lay := header_lines()
	var x := PAD * _k
	var ink := DecryptedHoloPanel.ink(skin.holo)
	var f := Palette.display()
	var mono := Palette.mono()
	var tpx := int(lay["title_px"])
	var spx := int(lay["sub_px"])
	var y := PAD * 0.5 * _k
	for line in lay["title"] as PackedStringArray:
		HighContrast.draw_text(on, f, Vector2(x, y + f.get_ascent(tpx)), line, HORIZONTAL_ALIGNMENT_LEFT, -1, tpx, ink)
		y += f.get_height(tpx)
	for line in lay["sub"] as PackedStringArray:
		HighContrast.draw_text(on, mono, Vector2(x, y + mono.get_ascent(spx)), line, HORIZONTAL_ALIGNMENT_LEFT, -1, spx, ink)
		y += mono.get_height(spx)


## The header as drawn: {"title", "sub" (each one's lines), "title_px", "sub_px", "room" (px
## the lines get), "widest" (px of the widest line), "height" (px the header takes: never under
## RaidHolo's HEAD_H)}.
func header_lines() -> Dictionary:
	var room := size.x - PAD * _k * 2.0
	var tpx := UiTheme.font_px(UiTheme.LABEL)
	var spx := UiTheme.font_px(UiTheme.CAPTION)
	var f := Palette.display()
	var mono := Palette.mono()
	var tl := _wrap_line(title, f, tpx, room)
	var sl := _wrap_line(sub, mono, spx, room)
	var widest := 0.0
	for line in tl:
		widest = maxf(widest, f.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, tpx).x)
	for line in sl:
		widest = maxf(widest, mono.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, spx).x)
	var h := PAD * minf(_k, HEAD_SCALE_MAX) + tl.size() * f.get_height(tpx) + sl.size() * mono.get_height(spx)
	return {"title": tl, "sub": sl, "title_px": tpx, "sub_px": spx, "room": room, "widest": widest, "height": maxf(HEAD_H * minf(_k, HEAD_SCALE_MAX), h)}


## `text` as one line when it fits `room` px, else wrapped at its words (a word longer than the
## room stands alone on its line).
static func _wrap_line(text: String, font: Font, px: int, room: float) -> PackedStringArray:
	if room <= 0.0 or font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= room:
		return PackedStringArray([text])
	var out := PackedStringArray()
	var line := ""
	for word in text.split(" ", false):
		var trial := word if line == "" else line + " " + word
		if line != "" and font.get_string_size(trial, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > room:
			out.append(line)
			line = word
		else:
			line = trial
	if line != "":
		out.append(line)
	return out


## Grows the header's room (the panel's top margin) to the wrapped header's height.
func _fit_head() -> void:
	var box := get_theme_stylebox(&"panel") as StyleBoxEmpty
	if box == null:
		return
	var h := float(header_lines()["height"])
	if not is_equal_approx(box.content_margin_top, h):
		box.content_margin_top = h
		queue_sort()
		update_minimum_size()
