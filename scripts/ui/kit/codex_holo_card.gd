class_name CodexHoloCard
extends PanelContainer
## B5 (integration review D11 / Q13, round 44 B_menus `codex.png`): a Codex entry about a corporation opens an
## intercepted HOLO card (hacked intel on the target; never paper): the kit's DecryptedHoloPanel in the corp's tint
## (its scanlines, slow bands, RGB-split edge, local 0.88 scrim, the cracked seal under the DECRYPTED stamp), and
## on it the header (INTERCEPTED // CORP // FILE), the crest with its glow, the corporation's name, its HQ, the
## entry's words, and BOSSES ON FILE: the corporation's bosses the Cell has met, as glyph rows (crest tile, name,
## its rank: HQ BOSS / MINI BOSS / ELITE, and its words). A container laid out by its host; a view only.

## The words' room round the edge and the crest's size (px at text scale 1.0); the type steps.
const PAD := 14.0
const CREST := 64.0
const ROW_GLYPH := 22.0
## The ranks a boss row shows (keys).
const RANK_WORDS := {"boss": "HQ BOSS", "mini": "MINI BOSS", "elite": "ELITE"} # TR
const HEADER := "INTERCEPTED  //  %s  //  CORP FILE" # TR
const BOSSES := "BOSSES ON FILE" # TR
const NONE_YET := "No boss of theirs met yet." # TR
const HQ_LINE := "HQ: %s" # TR

var corporation: StringName = &""
var holo: DecryptedHoloPanel
var body: VBoxContainer
## The header's corner the DECRYPTED stamp stands in.
var stamp_room: Control = null
var _tint: Color = Palette.CORP_SOLACE


## `corp_id` the corporation; `words` the Codex entry's text; `bosses` [{title, text, rank}] (the Cell's met
## bosses of that corporation, ranked).
func _init(corp_id: StringName = &"", words: String = "", bosses: Array = []) -> void:
	corporation = corp_id
	name = "HoloCard"
	_tint = Palette.corp_color(corp_id)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var k := Settings.text_scale
	var box := StyleBoxEmpty.new()
	for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP]:
		box.set_content_margin(side, PAD * k)
	box.set_content_margin(SIDE_BOTTOM, PAD * k)
	add_theme_stylebox_override(&"panel", box)
	holo = DecryptedHoloPanel.new()
	holo.name = "Holo"
	holo.scrim = false
	holo.corp_color = _tint
	holo.corporation = corp_id
	holo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(holo, false, Node.INTERNAL_MODE_FRONT)
	body = VBoxContainer.new()
	body.name = "HoloBody"
	body.add_theme_constant_override(&"separation", roundi(UiTheme.SP_XS * k))
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(body)
	var corp := RunManager.lookup().get_content(corp_id) as CorporationData
	var corp_name := TextDb.t(corp, "display_name") if corp != null else String(corp_id)
	# Art director (B5 fix 5): the DECRYPTED stamp sits in the header's right corner (always on screen at 720, the
	# card may scroll); the header's words keep clear of its slot.
	var head_row := HBoxContainer.new()
	head_row.name = "HeaderRow"
	head_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var header := _label(tr(HEADER) % corp_name.to_upper(), Chrome.caps_font(UiTheme.LABEL), UiTheme.LABEL, DecryptedHoloPanel.ink(_tint), "Header")
	header.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	head_row.add_child(header)
	stamp_room = Control.new()
	stamp_room.name = "StampRoom"
	stamp_room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stamp_room.custom_minimum_size = DecryptedHoloPanel.STAMP_SLOT
	head_row.add_child(stamp_room)
	body.add_child(head_row)
	var top := HBoxContainer.new()
	top.name = "Top"
	top.add_theme_constant_override(&"separation", roundi(UiTheme.SP_M * k))
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var crest := Control.new()
	crest.name = "Crest"
	crest.custom_minimum_size = Vector2.ONE * CREST * minf(k, CodexBook.GLYPH_SCALE_MAX)
	crest.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	crest.mouse_filter = Control.MOUSE_FILTER_IGNORE
	crest.draw.connect(_draw_crest.bind(crest))
	top.add_child(crest)
	var words_box := VBoxContainer.new()
	words_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	words_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	words_box.add_child(_label(corp_name.to_upper(), Palette.display(), UiTheme.HEADING, Palette.TEXT_HI, "Name"))
	if corp != null and corp.final_boss != null:
		words_box.add_child(_label(tr(HQ_LINE) % TextDb.t(corp.final_boss, "display_name"), Palette.mono(), UiTheme.CAPTION, DecryptedHoloPanel.ink(_tint), "Hq"))
	words_box.add_child(_label(words, Palette.body(), UiTheme.BODY, Palette.TEXT_HI, "Words"))
	top.add_child(words_box)
	body.add_child(top)
	var rule := ColorRect.new()
	rule.color = Color(_tint, 0.45)
	rule.custom_minimum_size.y = 1
	rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(rule)
	body.add_child(_label(tr(BOSSES), Chrome.caps_font(UiTheme.CAPTION), UiTheme.CAPTION, DecryptedHoloPanel.ink(_tint), "BossesHead"))
	if bosses.is_empty():
		body.add_child(_label(tr(NONE_YET), Palette.body(), UiTheme.BODY, Palette.TEXT_MID, "NoBoss"))
	for b in bosses:
		body.add_child(_boss_row(b as Dictionary))


## One boss row: a crest tile, the boss's name and rank, its words.
func _boss_row(b: Dictionary) -> HBoxContainer:
	var k := Settings.text_scale
	var row := HBoxContainer.new()
	row.name = "Boss"
	row.add_theme_constant_override(&"separation", roundi(UiTheme.SP_S * k))
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var tile := Control.new()
	tile.custom_minimum_size = Vector2.ONE * (ROW_GLYPH + UiTheme.SP_S) * minf(k, CodexBook.GLYPH_SCALE_MAX)
	tile.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	tile.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tile.draw.connect(func() -> void:
		CodexBook.draw_tile(tile, _tint)
		CorpSeal.draw_crest(tile, tile.size * 0.5, tile.size.x * 0.32, corporation, Palette.TEXT_HI))
	row.add_child(tile)
	var words := VBoxContainer.new()
	words.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	words.add_theme_constant_override(&"separation", 0)
	words.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var head := _label("%s   %s" % [String(b.get("title", "")).to_upper(), tr(String(RANK_WORDS.get(b.get("rank", ""), ""))).to_upper()],
		Palette.body_medium(), UiTheme.BODY, Palette.TEXT_HI, "BossName")
	words.add_child(head)
	words.add_child(_label(String(b.get("text", "")).get_slice("\n", 0), Palette.body(), UiTheme.CAPTION, Palette.TEXT_MID, "BossWords"))
	row.add_child(words)
	return row


func _label(words: String, font: Font, step: int, col: Color, node_name: String) -> Label:
	var l := Label.new()
	l.name = node_name
	l.text = words
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.add_theme_font_override(&"font", font)
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(step))
	l.add_theme_color_override(&"font_color", col)
	UiWrap.whole_words(l)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _draw_crest(c: Control) -> void:
	var r := c.size.x * 0.5
	c.draw_circle(c.size * 0.5, r, Color(_tint, 0.18))
	c.draw_arc(c.size * 0.5, r - 1.0, 0.0, TAU, 48, Color(_tint, 0.8), 2.0, true)
	CorpSeal.draw_crest(c, c.size * 0.5, r * DecryptedHoloPanel.CREST_SHARE, corporation, DecryptedHoloPanel.ink(_tint))


func _notification(what: int) -> void:
	if (what == NOTIFICATION_RESIZED or what == NOTIFICATION_SORT_CHILDREN) and holo != null:
		holo.position = Vector2.ZERO
		holo.size = size
		_place_stamp.call_deferred()


## The DECRYPTED stamp over the header's corner room (art director B5 fix 5: always on screen, never over words).
func _place_stamp() -> void:
	if holo == null or stamp_room == null or not is_instance_valid(stamp_room):
		return
	holo.stamp_slot.position = stamp_room.get_global_rect().position - global_position
