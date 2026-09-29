class_name CodexSpread
extends VBoxContainer
## The codex as an illustrated zine spread (ART_BIBLE §11 Codex; critique 16: "a wall of
## monospace text about 1,200 px wide, with section headers the same size as body text"):
## section tabs on the glass above (one per Codex section), and under them one PAPER spread
## with the section's heading (`heading` step, Anton) and its entries in two columns when the
## room allows (one column when it doesn't: big text, the pause menu). Each entry is a 24 px
## glyph (SliceIcon for a slice, StatIcon.draw_status for a status, the corporation's
## landmark, else the section's StatIcon) beside its title (`label`, Anton) and its text in
## the Plex body face (`BodyText`), wrapped at COLUMN_CHARS characters (≤ 70 per line, §4.2).
## A long section scrolls inside the spread (§5.3). Reads Codex entries only. View only.

## The characters a body line holds at most (§4.2: ≤ 70), and a sample of average text the
## column width is measured on.
const COLUMN_CHARS := 64
const MAX_LINE_CHARS := 70
const SAMPLE := "the cell runs quiet nets through the corporate city at night, "
## The chosen tab's rule (px).
const TAB_MARK_H := 3.0
## The glyph's side at text scale 1.0 (px, §11: 24).
const GLYPH := 24.0
## Section StatIcons (a section without one uses CODEX).
const SECTION_ICONS := {"Classes": StatIcon.OPERATIVE, "Cards": StatIcon.CARDS, "Firmware": StatIcon.FIRMWARE, "Daemons": StatIcon.DAEMON,
	"Ring segments": StatIcon.RANK, "Enemies": StatIcon.FIGHT, "Nodes": StatIcon.LINKS, "Home servers": StatIcon.HOME,
	"Defense assets": StatIcon.ARMORY, "Threats": StatIcon.RAIDS, "Lexicon": StatIcon.INFO, "Statuses & precision": StatIcon.CHECK,
	"Corporations": StatIcon.MAP, "Slices": StatIcon.FIGHT}

## {section: [{title, text, slice?, status?, corporation?}]} (Codex.entries).
var entries: Dictionary = {}
var section: String = ""
var tabs: HFlowContainer
var spread: ZinePanel
var heading: Label
var columns: HBoxContainer
## The widest the spread may be (px); two columns only when they fit.
var max_width: float = 0.0
var _group: ButtonGroup


## `p_entries` from Codex.entries; the spread scrolls past `max_height` px and uses two
## columns while they fit in `p_max_width` px.
func _init(p_entries: Dictionary, max_height: float = 420.0, p_max_width: float = 1180.0) -> void:
	name = "CodexSpread"
	entries = p_entries
	max_width = p_max_width
	add_theme_constant_override("separation", UiTheme.SP_S)
	tabs = HFlowContainer.new()
	tabs.name = "Tabs"
	tabs.add_theme_constant_override("h_separation", UiTheme.SP_XS)
	tabs.add_theme_constant_override("v_separation", UiTheme.SP_XS)
	add_child(tabs)
	_group = ButtonGroup.new()
	for name_key in entries:
		var b := Button.new()
		b.name = "Tab_%s" % String(name_key).replace(" ", "_").replace("&", "and")
		b.text = tr(String(name_key))
		b.toggle_mode = true
		b.button_group = _group
		b.theme_type_variation = UiTheme.SECONDARY
		IconMark.attach(b, SECTION_ICONS.get(name_key, StatIcon.CODEX))
		tab_marker(b)
		var n: String = name_key
		b.pressed.connect(func() -> void: show_section(n))
		tabs.add_child(b)
	spread = ZinePanel.new(tr("CODEX"), 0.0)
	spread.name = "Spread"
	# As wide as its columns (§5.3: no empty paper beside them).
	spread.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	var page := VBoxContainer.new()
	page.name = "Page"
	page.add_theme_constant_override("separation", UiTheme.SP_S)
	heading = Label.new()
	heading.name = "Heading"
	heading.add_theme_font_override("font", Palette.display())
	heading.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.HEADING))
	heading.add_theme_color_override("font_color", Palette.INK)
	page.add_child(heading)
	columns = HBoxContainer.new()
	columns.name = "Columns"
	columns.add_theme_constant_override("separation", UiTheme.GUTTER * 2)
	page.add_child(columns)
	spread.content.add_child(page)
	spread.scroll_content(max_height)
	add_child(spread)
	if not entries.is_empty():
		show_section(String(entries.keys()[0]))


## The body text's width for COLUMN_CHARS characters at the player's text size (px).
static func column_width() -> float:
	var px := UiTheme.font_px(UiTheme.BODY)
	return Palette.body().get_string_size(SAMPLE, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x * COLUMN_CHARS / SAMPLE.length()


## One entry's width: its glyph, the gap and its text column.
static func entry_width() -> float:
	return GLYPH * Settings.text_scale + UiTheme.SP_S + column_width()


## How many columns fit `width` px of spread (2 or 1).
static func columns_for(width: float) -> int:
	var two := entry_width() * 2.0 + UiTheme.GUTTER * 2 + UiTheme.PANEL_PAD_H * 2
	return 2 if two <= width else 1


## Shows section `name` (its tab pressed, its heading and entries).
func show_section(name_key: String) -> void:
	section = name_key
	for b in tabs.get_children():
		(b as Button).set_pressed_no_signal((b as Button).text == tr(name_key))
		show_tab(b as Button, (b as Button).text == tr(name_key))
	heading.text = tr(name_key).to_upper()
	for c in columns.get_children():
		columns.remove_child(c)
		c.queue_free()
	var items: Array = entries.get(name_key, [])
	var n := columns_for(max_width)
	var cols: Array[VBoxContainer] = []
	for i in n:
		var col := VBoxContainer.new()
		col.name = "Column%d" % (i + 1)
		col.add_theme_constant_override("separation", UiTheme.SP_M)
		columns.add_child(col)
		cols.append(col)
	var per := ceili(items.size() / float(n))
	for i in items.size():
		cols[mini(i / maxi(1, per), n - 1)].add_child(_entry(name_key, items[i]))


func _entry(name_key: String, item: Dictionary) -> Control:
	var row := HBoxContainer.new()
	row.name = "Entry"
	row.add_theme_constant_override("separation", UiTheme.SP_S)
	var g := Control.new()
	g.name = "Glyph"
	var side := GLYPH * Settings.text_scale
	g.custom_minimum_size = Vector2(side, side)
	g.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	g.set_meta(&"item", item)
	g.draw.connect(func() -> void: _draw_glyph(g, name_key, item))
	row.add_child(g)
	var words := VBoxContainer.new()
	words.add_theme_constant_override("separation", 0)
	var t := Label.new()
	t.name = "Title"
	t.text = String(item.get("title", ""))
	t.add_theme_font_override("font", Palette.display())
	t.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.LABEL))
	t.add_theme_color_override("font_color", Palette.INK)
	UiWrap.whole_words(t)  # art pass W9F §4.3.3: whole words, never mid-word
	t.custom_minimum_size.x = column_width()
	words.add_child(t)
	var body := Label.new()
	body.name = "Body"
	body.text = String(item.get("text", ""))
	body.theme_type_variation = UiTheme.BODY_TEXT
	body.add_theme_color_override("font_color", Palette.INK)
	UiWrap.whole_words(body)  # art pass W9F §4.3.3: whole words, never mid-word
	body.custom_minimum_size.x = column_width()
	words.add_child(body)
	row.add_child(words)
	return row


func _draw_glyph(g: Control, name_key: String, item: Dictionary) -> void:
	var c := g.size * 0.5
	var r := g.size.x * 0.5
	if item.has("slice"):
		SliceIcon.draw_icon(g, c, r * 0.9, int(item["slice"]), Palette.slice_color(int(item["slice"])))
	elif item.has("status"):
		StatIcon.draw_status(g, c, r * 0.9, int(item["status"]), Palette.INK)
	elif item.has("corporation"):
		var corp: StringName = item["corporation"]
		g.draw_circle(c, r, Palette.INK)
		var path := SvgArt.landmark_path(corp)
		if path != "":
			var tex := SvgArt.texture(path, r * 1.5)
			if tex != null:
				g.draw_texture_rect(tex, Rect2(c - Vector2.ONE * r * 0.75, Vector2.ONE * r * 1.5), false, Palette.corp_color(corp))
	else:
		StatIcon.draw(g, c, r * 0.9, SECTION_ICONS.get(name_key, StatIcon.CODEX), Palette.INK)


## A glass tab's "chosen" mark: a CELL_PINK rule along its foot (the glass title rule's
## colour), shown by `show_tab`. Shared by the Options tabs.
static func tab_marker(b: Button) -> void:
	var mark := ColorRect.new()
	mark.name = "TabMark"
	mark.color = Palette.CELL_PINK
	mark.mouse_filter = Control.MOUSE_FILTER_IGNORE
	mark.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	mark.offset_top = -TAB_MARK_H
	mark.visible = false
	b.add_child(mark)


## Shows or hides tab `b`'s chosen mark (and its label in TEXT_HI when chosen).
static func show_tab(b: Button, chosen: bool) -> void:
	var mark := b.get_node_or_null("TabMark") as Control
	if mark != null:
		mark.visible = chosen
	if chosen:
		b.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	else:
		b.remove_theme_color_override(&"font_color")


## Every word on the spread now (tests: "Lexicon" is a tab, entries are searchable).
func all_text() -> String:
	var out := PackedStringArray()
	for b in tabs.get_children():
		out.append((b as Button).text)
	for n in columns.find_children("*", "Label", true, false):
		out.append((n as Label).text)
	return "\n".join(out)


## The number of body columns shown now.
func column_count() -> int:
	return columns.get_child_count()


## The characters on each line `text` wraps to at `width` px in the body face at `px`
## (tests: ≤ MAX_LINE_CHARS).
static func line_lengths(text: String, width: float, px: int) -> PackedInt32Array:
	var ts := TextServerManager.get_primary_interface()
	var out := PackedInt32Array()
	for para in text.split("\n"):
		var rid := ts.create_shaped_text()
		ts.shaped_text_add_string(rid, para, Palette.body().get_rids(), px)
		var breaks := ts.shaped_text_get_line_breaks(rid, width, 0, TextServer.BREAK_MANDATORY | TextServer.BREAK_WORD_BOUND)
		for i in range(0, breaks.size(), 2):
			out.append(para.substr(breaks[i], breaks[i + 1] - breaks[i]).strip_edges().length())
		ts.free_rid(rid)
	return out
