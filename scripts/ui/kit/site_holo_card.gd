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

## The sub line under the title (already translated).
var sub: String = ""


func _init(p_corporation: StringName = &"halcyon", p_title: String = "", p_sub: String = "") -> void:
	super(p_corporation, p_title, "")
	sub = p_sub
	name = "SelectedSite"


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
	if box != null and not is_equal_approx(box.content_margin_bottom, PAD * _k + foot):
		box.content_margin_bottom = PAD * _k + foot
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
## ink (RaidHolo's header with the Site's own sub line).
func _header(on: Control) -> void:
	var f := Palette.display()
	var title_px := UiTheme.font_px(UiTheme.LABEL)
	var x := PAD * _k
	var room := size.x - x * 2.0
	on.draw_string(f, Vector2(x, PAD * 0.5 * _k + f.get_ascent(title_px)), title, HORIZONTAL_ALIGNMENT_LEFT, room, title_px, DecryptedHoloPanel.ink(skin.holo))
	var meta_px := UiTheme.font_px(UiTheme.CAPTION)
	var mono := Palette.mono()
	on.draw_string(mono, Vector2(x, PAD * 0.5 * _k + f.get_height(title_px) + mono.get_ascent(meta_px)), sub, HORIZONTAL_ALIGNMENT_LEFT, room, meta_px,
		DecryptedHoloPanel.ink(skin.holo))
