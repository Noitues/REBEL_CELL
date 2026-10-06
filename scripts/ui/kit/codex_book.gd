class_name CodexBook
extends VBoxContainer
## Parity CODEX-01 (designer group ruling 2026-10-05: the build reworked in v2). Ported from
## art-m13-final `scripts/ui/kit/codex_spread.gd` (CodexSpread) and reworked in the v2 kit:
## the Codex's sections as terminal tabs (the round 31 tab plates, MenuChip `tab`) in as many
## rows as the width needs (two at 1280), and under them one paper page (the art pass's paper
## stock, `corp_paper.gdshader`) with the section's name in Anton ink and its entries in two
## columns when they fit (one in the pause menu or at big text). Each entry is its glyph, a
## title in Courier Prime Bold and its text in Plex, in ink. The glyph is the 1C atlas's
## (`GlyphIcon`: slices, statuses, class hubs, cards' first effect, Firmware, Daemons, ring
## segments), the corporation's crest (`CorpSeal`, the art pass's exported emblems) for a
## corporation or an enemy, else the section's StatIcon (the art pass's icon set) in ink.
## The STORY section (HQ-B Q8) heads the tabs while a campaign is loaded.
## Pad / keyboard: the tabs are a row (LB / RB switch them from anywhere in the book); the page
## takes focus as one stop: up / down scroll it by a quarter view and move on at either end.
## Reads Codex entries only. View only.
## B5 (integration review D11 / Q13, round 44 B_menus `codex.png`): the Codex is the Cell's own knowledge, so it is
## TERMINAL GLASS, never paper: one CrtWindow `> CODEX // WHAT THE CELL KNOWS` (its tag the number of entries) holds
## the tab plates and the page; each entry is a glyph-tile row (the 26 px glyph in a navy tile with an accent edge,
## then its title and words in Plex, as the tooltips' rows). The CORPORATIONS section lists the corporations and
## opens the selected one's intercepted HOLO card beside the list (CodexHoloCard: hacked intel on a corporation);
## up / down on the focused page (or a click) picks the corporation, the selected row lit with the cyan wash, the
## lime focus brackets and the caret.

## The characters a body line holds (≤ 70 a line), and the sample its width is measured on.
const COLUMN_CHARS := 60
const SAMPLE := "the cell runs quiet nets through the corporate city at night, "
## An entry's glyph box at text scale 1.0 (px); a drawn object grows with the text only to
## GLYPH_SCALE_MAX (STYLE_GUIDE 5.6).
const GLYPH := 26.0
const GLYPH_SCALE_MAX := 1.3
## The page's margins on its paper (px at 1.0: sides, top / bottom), the gap between its
## columns and between entries, and its drop shadow's offset.
const PAGE_PAD := Vector2(22, 10)
const COLUMN_GAP := 28
const ENTRY_GAP := 10
const SHADOW_OFFSET := Vector2(3, 5)
## Up / down on the focused page scroll it by this share of the view.
const SCROLL_STEP := 0.25
## From this text scale the tabs are one row that scrolls sideways and the page drops its
## caption and heading lines (the open tab, filled, names the section): the entries keep the
## room (at 2.0 the view was at its least height).
const ONE_ROW_FROM := 1.6
## The page's caption (a key): the terminal window's header.
const CAPTION := "CODEX // WHAT THE CELL KNOWS" # TR
## B5: the window's tag (a key) and the section whose entries open the holo card.
const ENTRIES_TAG := "%d ENTRIES" # TR
const CORP_SECTION := "Corporations"
## B5: the glyph tile's fill and its edge's alpha (round 44 b44.glyph_tile: navy (8, 18, 34), the accent at 200/255),
## and the selected row's cyan wash (alpha).
const TILE_FILL := Color8(8, 18, 34)
const TILE_EDGE_ALPHA := 0.78
const ROW_WASH := 0.12
## B5: the holo card's share of the page's width beside the corporations' list.
const HOLO_SHARE := 0.48
## Each section's StatIcon (the art pass's set): the glyph of an entry with no atlas glyph.
const SECTION_ICONS := {"Story": StatIcon.TERMINAL, "Slices": StatIcon.FIGHT, "Statuses & precision": StatIcon.CHECK,
	"Classes": StatIcon.OPERATIVE, "Corporations": StatIcon.MAP, "Cards": StatIcon.CARDS, "Firmware": StatIcon.FIRMWARE,
	"Daemons": StatIcon.DAEMON, "Ring segments": StatIcon.RANK, "Enemies": StatIcon.FIGHT, "Nodes": StatIcon.LINKS,
	"Home servers": StatIcon.HOME, "Defense assets": StatIcon.ARMORY, "Threats": StatIcon.RAIDS, "Lexicon": StatIcon.INFO}
## The atlas key prefix of a section whose entries carry their content `id`.
const ID_PREFIX := {"Firmware": "firmware_", "Daemons": "daemon_", "Ring segments": "seg_"}
## The glyph's fill per section: the class hubs the Cell's pink, the cards the atlas's white; the
## Firmware, Daemons and ring segments their StatIcon's own colour (the game's colour for those
## things); a slice takes its slice colour, a status its own. The ink outline reads on the paper.
const SECTION_FILLS := {"Classes": Palette.CELL_PINK, "Cards": Palette.GLYPH_FILL}
const ICON_FILLED: Array[String] = ["Firmware", "Daemons", "Ring segments"]
const STATUS_FILLS := {RC.Status.CORRUPTED: Palette.HARM, RC.Status.OVERCLOCKED: Palette.WARN, RC.Status.ENCRYPTED: Palette.PROTECT,
	RC.Status.PARASITE: Palette.SLICE_INFECT}

## Emitted after a section's entries are rebuilt (a host relinks its focus).
signal section_shown(name: String)

## {section: [{title, text, slice?, status?, tier?, corporation?, hub?, id?, effect?}]} (Codex.entries).
var entries: Dictionary = {}
var section: String = ""
## The tabs' row: an HFlowContainer (rows as the width needs), or at big text an HBoxContainer
## in `tab_scroll` (one row that scrolls sideways).
var tabs: Container
var tab_scroll: ScrollContainer = null
## The page: one focus stop (a Button) over its paper, holding the heading and the scroll.
var page: Button
var heading: Label
var columns: HBoxContainer
var fit: FitScroll
## The widest the book may be (px); two columns only when they fit.
var max_width: float = 0.0
## The tallest the whole book may be (px; 0: no cap): the page's view scrolls past it.
var max_height: float = 0.0:
	set(v):
		max_height = v
		_queue_fit()
var _tab_buttons: Dictionary = {}
## B5: the terminal window round the tabs and the page (the Codex's glass).
var frame: CrtWindow
var _content: VBoxContainer
var _marks: Control
## B5: the corporations' rows (their entries), the one picked, and its holo card (null in other sections).
var _corp_rows: Array[Control] = []
var _corp_items: Array = []
var selected_corp: int = 0
var holo_card: CodexHoloCard = null


## `p_entries` from Codex.entries; the book stays under `p_max_height` px (its page scrolls)
## and uses two columns while they fit in `p_max_width` px.
func _init(p_entries: Dictionary, p_max_height: float = 0.0, p_max_width: float = 1200.0) -> void:
	name = "CodexBook"
	entries = p_entries
	max_width = p_max_width
	add_theme_constant_override("separation", UiTheme.SP_S)
	# B5 (D11): one terminal window holds the tabs and the page.
	frame = CrtWindow.new(tr(CAPTION))
	frame.name = "Frame"
	var count := 0
	for k in entries:
		count += (entries[k] as Array).size()
	frame.tag_label.text = tr(ENTRIES_TAG) % count
	frame.tag_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	frame.body.add_theme_constant_override("separation", UiTheme.SP_XS if one_row() else UiTheme.SP_S)  # big text: the entries keep the room
	add_child(frame)
	if one_row():
		# Big text: the tabs in one row that scrolls sideways (focus follows), so the page keeps
		# its room (rows of big tabs took most of the screen at 2.0).
		tab_scroll = ScrollContainer.new()
		tab_scroll.name = "TabScroll"
		tab_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
		# No bar (its room is the page's): the wheel, the focus and LB / RB move the row.
		tab_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_SHOW_NEVER
		tab_scroll.follow_focus = true
		tab_scroll.custom_minimum_size.x = p_max_width - CrtWindow.PAD_H * 2.0
		frame.body.add_child(tab_scroll)
		tabs = HBoxContainer.new()
		tabs.add_theme_constant_override("separation", UiTheme.SP_XS)
		tab_scroll.add_child(tabs)
	else:
		tabs = HFlowContainer.new()
		tabs.add_theme_constant_override("h_separation", UiTheme.SP_XS)
		tabs.add_theme_constant_override("v_separation", UiTheme.SP_XS)
		frame.body.add_child(tabs)
	tabs.name = "Tabs"
	for key in entries:
		var b := MenuChip.new(tr(String(key)))
		b.plate = &"tab"  # round 31 ui31.tabs plates
		b.pre_translated = true
		b.name = tab_name(String(key))
		b.set_meta(UiFocus.META_NO_SCALE, true)
		var n: String = key
		b.pressed.connect(show_section.bind(n))
		tabs.add_child(b)
		_tab_buttons[key] = b
	page = Button.new()
	page.name = "Page"
	page.focus_mode = Control.FOCUS_ALL
	page.mouse_filter = Control.MOUSE_FILTER_PASS
	# As wide as its columns (no empty paper beside them); at big text as wide as the tabs' row
	# over it (one column there).
	page.size_flags_horizontal = Control.SIZE_FILL if one_row() else Control.SIZE_SHRINK_BEGIN
	page.set_meta(UiFocus.META_NO_SCALE, true)
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]:
		page.add_theme_stylebox_override(box, StyleBoxEmpty.new())
	page.gui_input.connect(_on_page_input)
	page.focus_entered.connect(_redraw_marks)
	page.focus_exited.connect(_redraw_marks)
	frame.body.add_child(page)
	var margin := MarginContainer.new()
	margin.name = "Margin"
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	for side in ["left", "right"]:
		margin.add_theme_constant_override("margin_" + side, roundi(PAGE_PAD.x))
	for side in ["top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, roundi(page_pad_y()))
	page.add_child(margin)
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_content = VBoxContainer.new()
	_content.name = "Content"
	_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_content.add_theme_constant_override("separation", 2)
	margin.add_child(_content)
	# B5: the section's name as the terminal's mono caps heading (the window's header is the caption).
	heading = Chrome.caps_label("", UiTheme.CAPTION, Palette.NET_CYAN)
	heading.name = "Heading"
	heading.visible = not one_row()
	_content.add_child(heading)
	columns = HBoxContainer.new()
	columns.name = "Columns"
	columns.mouse_filter = Control.MOUSE_FILTER_IGNORE
	columns.add_theme_constant_override("separation", COLUMN_GAP)
	fit = FitScroll.new(columns)
	fit.name = "PageScroll"
	fit.scroll.follow_focus = false
	# The view scrolls whole pages of prose: no snap to its entries (an entry at 2.0 is a third of
	# the view; snapping left most of the page's room empty), as the slots page's view.
	fit.hint.snap_rows = false
	_content.add_child(fit)
	margin.minimum_size_changed.connect(_size_page.bind(margin))
	page.resized.connect(_place_page.bind(margin))
	# The focus brackets over the paper (the page's own focus box would draw under it).
	_marks = Control.new()
	_marks.name = "FocusMarks"
	_marks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_marks.draw.connect(_draw_marks)
	page.add_child(_marks)
	_marks.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_size_page(margin)
	max_height = p_max_height
	if not entries.is_empty():
		show_section(String(entries.keys()[0]))


func _ready() -> void:
	tabs.resized.connect(_fit_page)
	_queue_fit()


## The page's view is fitted now and again over FIT_PASSES frames: the tabs' rows and the
## entries' wrapped lines are only measured once laid out at their width.
const FIT_PASSES := 3
var _fit_left: int = 0


func _queue_fit() -> void:
	_fit_left = FIT_PASSES
	_fit_page.call_deferred()
	if is_inside_tree() and not get_tree().process_frame.is_connected(_fit_pass):
		get_tree().process_frame.connect(_fit_pass, CONNECT_ONE_SHOT)


func _fit_pass() -> void:
	_fit_page()
	_fit_left -= 1
	if _fit_left > 0 and is_inside_tree() and not get_tree().process_frame.is_connected(_fit_pass):
		get_tree().process_frame.connect(_fit_pass, CONNECT_ONE_SHOT)


func _exit_tree() -> void:
	if get_tree().process_frame.is_connected(_fit_pass):
		get_tree().process_frame.disconnect(_fit_pass)


## True at big text: one row of tabs, no caption line.
static func one_row() -> bool:
	return Settings.text_scale >= ONE_ROW_FROM


## B5: the page's top and bottom margin (px): PAGE_PAD.y, half of it at big text (one row of tabs), so the entries
## keep the room the terminal window's header takes.
static func page_pad_y() -> float:
	return PAGE_PAD.y * (0.5 if one_row() else 1.0)


## A section's tab node name ("Tab_Statuses_and_precision").
static func tab_name(key: String) -> String:
	return "Tab_%s" % key.replace(" ", "_").replace("&", "and")


## The body text's width for COLUMN_CHARS characters at the player's text size (px).
static func column_width() -> float:
	var px := Chrome.px(UiTheme.BODY)
	return Palette.body().get_string_size(SAMPLE, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x * COLUMN_CHARS / SAMPLE.length()


## The glyph's box on screen (px).
static func glyph_px() -> float:
	return GLYPH * minf(Settings.text_scale, GLYPH_SCALE_MAX)


## One entry's width: its glyph, the gap and its text column.
static func entry_width() -> float:
	return GlyphIcon.cell_size_for(glyph_px()).x + UiTheme.SP_S + column_width()


## How many columns fit a page `width` px wide (2 or 1).
static func columns_for(width: float) -> int:
	var two := entry_width() * 2.0 + COLUMN_GAP + PAGE_PAD.x * 2.0
	return 2 if two <= width else 1


## Shows section `name_key` (its tab selected, its heading and its entries).
func show_section(name_key: String) -> void:
	if not entries.has(name_key):
		return
	section = name_key
	for k in _tab_buttons:
		(_tab_buttons[k] as MenuChip).selected = k == name_key
	heading.text = tr(name_key).to_upper()
	for c in columns.get_children():
		columns.remove_child(c)
		c.queue_free()
	_corp_rows.clear()
	_corp_items.clear()
	holo_card = null
	var items: Array = entries.get(name_key, [])
	if name_key == CORP_SECTION and not items.is_empty():
		_show_corporations(items)
		if fit.scroll != null:
			fit.scroll.scroll_vertical = 0
		_queue_fit()
		section_shown.emit(name_key)
		return
	var n := columns_for(max_width)
	var cols: Array[VBoxContainer] = []
	for i in n:
		var col := VBoxContainer.new()
		col.name = "Column%d" % (i + 1)
		col.mouse_filter = Control.MOUSE_FILTER_IGNORE
		col.add_theme_constant_override("separation", ENTRY_GAP)
		columns.add_child(col)
		cols.append(col)
	var per := ceili(items.size() / float(n))
	for i in items.size():
		cols[mini(i / maxi(1, per), n - 1)].add_child(_entry(name_key, items[i]))
	if fit.scroll != null:
		fit.scroll.scroll_vertical = 0
	_queue_fit()
	section_shown.emit(name_key)


## The tab of the section shown.
func current_tab() -> MenuChip:
	return _tab_buttons.get(section) as MenuChip


## Moves `step` tabs on (wrapping) and focuses that tab (LB / RB).
func step_section(step: int) -> void:
	var keys := entries.keys()
	if keys.is_empty():
		return
	var i := wrapi(keys.find(section) + step, 0, keys.size())
	show_section(String(keys[i]))
	if current_tab() != null and current_tab().is_inside_tree():
		current_tab().grab_focus()


func _unhandled_input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventJoypadButton and event.pressed:
		var b := (event as InputEventJoypadButton).button_index
		if b == JOY_BUTTON_LEFT_SHOULDER or b == JOY_BUTTON_RIGHT_SHOULDER:
			step_section(1 if b == JOY_BUTTON_RIGHT_SHOULDER else -1)
			get_viewport().set_input_as_handled()


func _entry(name_key: String, item: Dictionary, text_w: float = -1.0) -> Control:
	var w := column_width() if text_w < 0.0 else text_w
	var row := HBoxContainer.new()
	row.name = "Entry"
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("separation", UiTheme.SP_S)
	# B5 (D11): the glyph in its navy tile with the accent edge (round 44 b44.glyph_tile; the tooltips' rows).
	var g := _glyph(name_key, item)
	var tile := Control.new()
	tile.name = "Tile"
	tile.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tile.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	tile.custom_minimum_size = g.get_combined_minimum_size()
	var tile_col := glyph_tile_edge(name_key, item)
	tile.set_meta(&"tile_edge", tile_col)
	tile.draw.connect(func() -> void: draw_tile(tile, tile_col))
	tile.add_child(g)
	row.add_child(tile)
	var words := VBoxContainer.new()
	words.mouse_filter = Control.MOUSE_FILTER_IGNORE
	words.add_theme_constant_override("separation", 0)
	var t := Label.new()
	t.name = "Title"
	t.text = title_text(String(item.get("title", "")), String(item.get("text", ""))).to_upper()
	t.add_theme_font_override(&"font", Palette.body_medium())
	t.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.LABEL))
	t.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	UiWrap.whole_words(t)
	t.custom_minimum_size.x = w
	words.add_child(t)
	var body := Label.new()
	body.name = "Body"
	body.text = body_text(String(item.get("title", "")), String(item.get("text", "")))
	body.add_theme_font_override(&"font", Palette.body())
	body.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.BODY))
	body.add_theme_color_override(&"font_color", Palette.TEXT_MID)
	UiWrap.whole_words(body)
	body.custom_minimum_size.x = w
	words.add_child(body)
	row.add_child(words)
	return row


## B5: the glyph tile's edge colour for an entry: the glyph's own hue (a slice's colour, a corporation's), else the
## Cell's cyan.
static func glyph_tile_edge(name_key: String, item: Dictionary) -> Color:
	var corp := StringName(String(item.get("corporation", "")))
	if corp != &"":
		return Palette.corp_color(corp)
	if item.has("slice") or item.has("status") or name_key in ICON_FILLED:
		return glyph_fill(name_key, item)
	return Palette.NET_CYAN


## B5 (D11, round 44 b44.glyph_tile): a glyph's tile: the navy chip with the accent edge, under the glyph.
static func draw_tile(ci: Control, edge: Color) -> void:
	var r := Rect2(Vector2.ZERO, ci.size)
	ci.draw_rect(r, TILE_FILL)
	ci.draw_rect(r.grow(-0.5), Color(PaletteSkins.chrome(edge), TILE_EDGE_ALPHA), false, 1.0)


## B5 (D11, Q13): the corporations' list at the left (glyph-tile rows; the picked one lit) and the picked
## corporation's intercepted holo card at the right.
func _show_corporations(items: Array) -> void:
	var inner := max_width - CrtWindow.PAD_H * 2.0 - PAGE_PAD.x * 2.0
	var card_w := floorf(inner * HOLO_SHARE)
	var list_w := inner - card_w - COLUMN_GAP
	var col := VBoxContainer.new()
	col.name = "Column1"
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_theme_constant_override("separation", ENTRY_GAP)
	col.custom_minimum_size.x = list_w
	columns.add_child(col)
	var text_w := maxf(list_w - GlyphIcon.cell_size_for(glyph_px()).x - UiTheme.SP_S * 2.0, column_width() * 0.5)
	for i in items.size():
		var row := _entry(CORP_SECTION, items[i], text_w)
		row.mouse_filter = Control.MOUSE_FILTER_STOP
		row.gui_input.connect(_on_corp_row_input.bind(i))
		row.draw.connect(_draw_corp_row.bind(row, i))
		col.add_child(row)
		_corp_rows.append(row)
		_corp_items.append(items[i])
	selected_corp = clampi(selected_corp, 0, items.size() - 1)
	_show_holo(card_w)


## The picked corporation's holo card (none for a corporation still a secret).
func _show_holo(card_w: float = -1.0) -> void:
	if holo_card != null and is_instance_valid(holo_card):
		if card_w < 0.0:
			card_w = holo_card.custom_minimum_size.x
		columns.remove_child(holo_card)
		holo_card.queue_free()
	holo_card = null
	if _corp_items.is_empty():
		return
	var item: Dictionary = _corp_items[selected_corp]
	var corp := StringName(String(item.get("corporation", "")))
	if corp != &"":
		holo_card = CodexHoloCard.new(corp, String(item.get("text", "")), bosses_of(corp))
		holo_card.custom_minimum_size.x = maxf(card_w, 0.0)
		holo_card.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		columns.add_child(holo_card)
	for r in _corp_rows:
		r.queue_redraw()


## The bosses of `corp` the Codex knows (its Enemies entries for that corporation), as card rows ranked HQ BOSS,
## MINI BOSS, ELITE (then the rest), each {title, text, rank}.
func bosses_of(corp: StringName) -> Array:
	var out: Array = []
	for e in entries.get("Enemies", []):
		var item := e as Dictionary
		if StringName(String(item.get("corporation", ""))) != corp:
			continue
		var res := RunManager.lookup().get_content(StringName(String(item.get("id", "")))) as EnemyData
		var rank := ""
		if res != null:
			rank = "boss" if res.is_boss else ("mini" if res.is_mini_boss else ("elite" if res.is_elite else ""))
		if rank == "":
			continue
		out.append({"title": String(item.get("title", "")), "text": body_text(String(item.get("title", "")), String(item.get("text", ""))), "rank": rank})
	var order := {"boss": 0, "mini": 1, "elite": 2}
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var ra: int = order.get(a["rank"], 3)
		var rb: int = order.get(b["rank"], 3)
		return ra < rb if ra != rb else String(a["title"]) < String(b["title"]))
	return out


## Picks corporation `i` (its row lit, its holo card shown).
func pick_corporation(i: int) -> void:
	if _corp_items.is_empty():
		return
	selected_corp = clampi(i, 0, _corp_items.size() - 1)
	_show_holo()
	_queue_fit()


func _on_corp_row_input(event: InputEvent, i: int) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).pressed and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		pick_corporation(i)
		page.grab_focus()


## The picked row: the cyan wash, the caret, and the lime focus brackets while the page holds the focus.
func _draw_corp_row(row: Control, i: int) -> void:
	if i != selected_corp:
		return
	var r := Rect2(Vector2.ZERO, row.size).grow(UiTheme.SP_XS)
	row.draw_rect(r, Color(PaletteSkins.chrome(Palette.NET_CYAN), ROW_WASH))
	row.draw_rect(r, Color(PaletteSkins.chrome(Palette.NET_CYAN), TILE_EDGE_ALPHA), false, 1.0)
	if page.has_focus():
		StyleBoxBrackets.draw_on(row, r)


## An entry's text under its title, without saying the title again (the audit's "SHIM SHIM:"):
## a leading "TITLE: " goes; a first line that is the title with its kind before it ("Firmware
## X", "Daemon X") goes; a first line that is the title with numbers after it ("X (RAM 1)",
## "X (12 HP)") keeps the numbers.
static func body_text(title: String, text: String) -> String:
	if title == "":
		return text
	if text.begins_with(title + ": "):
		return text.substr(title.length() + 2)
	var word := full_word(title, text)
	if word != "":
		return text.substr(word.length() + 2)
	var first := text.get_slice("\n", 0)
	var rest := text.substr(first.length() + 1) if text.contains("\n") else ""
	if first == title or first.ends_with(" " + title):
		return rest
	if first.begins_with(title + " ("):
		return first.substr(title.length() + 1) + ("\n" + rest if rest != "" else "")
	return text


## A slice's text opens with its full word in CAPS ("OVERFLOW: ...") under its short code
## ("OVFL"): that word ("" when the text opens otherwise). The title then reads "OVFL  OVERFLOW"
## and the text goes on after it.
static func full_word(title: String, text: String) -> String:
	var at := text.find(": ")
	if at <= 0:
		return ""
	var word := text.substr(0, at)
	if word == title or word != word.to_upper() or word.contains(" ") or word.to_lower() == word:
		return ""
	return word


## The title an entry shows: its own, with a slice's full word after its code.
static func title_text(title: String, text: String) -> String:
	var word := full_word(title, text)
	return title if word == "" else "%s  %s" % [title, word]


## The atlas glyph of an entry (an atlas name), or &"" when it has none in the 1C atlas.
static func atlas_glyph(name_key: String, item: Dictionary) -> StringName:
	var t := GlyphIcon.table()
	var key := &""
	if item.has("slice"):
		key = GlyphTableData.key_for_slice_type(int(item["slice"]))
	elif item.has("status"):
		key = GlyphTableData.key_for_status(int(item["status"]))
	elif String(item.get("hub", "")) != "":
		key = StringName("hub_" + String(item["hub"]))
	elif item.has("effect"):
		key = GlyphTableData.key_for_effect(int(item["effect"]))
	elif ID_PREFIX.has(name_key) and item.has("id"):
		key = StringName(String(ID_PREFIX[name_key]) + String(item["id"]))
	if key == &"":
		return &""
	var glyph := t.glyph_for(key)
	return &"" if glyph == GlyphTableData.PENDING else glyph


## The fill an entry's atlas glyph takes.
static func glyph_fill(name_key: String, item: Dictionary) -> Color:
	if item.has("slice"):
		return Palette.slice_color(int(item["slice"]))
	if item.has("status"):
		return STATUS_FILLS.get(int(item["status"]), Palette.GLYPH_FILL)
	if name_key in ICON_FILLED:
		return StatIcon.color_of(SECTION_ICONS[name_key])
	return SECTION_FILLS.get(name_key, Palette.GLYPH_FILL)


func _glyph(name_key: String, item: Dictionary) -> Control:
	var side := glyph_px()
	var glyph := atlas_glyph(name_key, item)
	if glyph != &"":
		var gi := GlyphIcon.make(glyph, side)
		gi.name = "Glyph"
		gi.fill = glyph_fill(name_key, item)
		return gi
	var g := Control.new()
	g.name = "Glyph"
	g.custom_minimum_size = GlyphIcon.cell_size_for(side)
	g.mouse_filter = Control.MOUSE_FILTER_IGNORE
	g.set_meta(&"item", item)
	g.draw.connect(_draw_drawn_glyph.bind(g, name_key, item, side))
	return g


## A glyph with no atlas art: the corporation's crest on an ink disc, or the section's StatIcon
## (a corporation still a secret: the lock) in ink.
func _draw_drawn_glyph(g: Control, name_key: String, item: Dictionary, side: float) -> void:
	var c := g.size * 0.5
	var r := side * 0.5
	var corp := StringName(String(item.get("corporation", "")))
	if corp != &"":
		CorpSeal.draw_crest(g, c, r * DecryptedHoloPanel.CREST_SHARE, corp, Palette.corp_color(corp))  # B5: on its navy tile
		return
	var kind: StringName = StatIcon.LOCK if name_key == "Corporations" else SECTION_ICONS.get(name_key, StatIcon.CODEX)
	StatIcon.draw(g, c, r * 0.9, kind, Palette.TEXT_HI)


## The page's least size: its content's (a Button's own ignores its children); deferred, so a
## rewrap of the words never re-enters the layout that caused it.
func _size_page(margin: Control) -> void:
	if not _sizing:
		_sizing = true
		_apply_page_size.call_deferred(margin)


var _sizing: bool = false


func _apply_page_size(margin: Control) -> void:
	_sizing = false
	if is_instance_valid(margin) and is_instance_valid(page):
		page.custom_minimum_size = margin.get_combined_minimum_size()


## The page's paper takes its new size (the margin, paper and marks follow it by their anchors:
## no size is set here, so a rewrap can never re-enter this).
func _place_page(_margin: Control) -> void:
	page.queue_redraw()


## The page's view: the room `max_height` leaves after the tabs, the caption and the heading.
func _fit_page() -> void:
	if fit == null or not is_instance_valid(fit):
		return
	if max_height <= 0.0:
		fit.max_height = 0.0
		return
	# Everything but the view, measured part by part (the page's own least size follows its
	# content a frame later): the tabs' rows, the gap, the paper's margins, the caption and the
	# heading with their gaps, and the view's MORE BELOW room under it.
	var tabs_part: Control = tab_scroll if tab_scroll != null else tabs
	var gap := float(get_theme_constant(&"separation"))
	var inner := float(_content.get_theme_constant(&"separation"))
	var chrome := tabs_part.get_combined_minimum_size().y + gap + page_pad_y() * 2.0
	# B5: the terminal window's header strip and pads round its body.
	chrome += frame.get_combined_minimum_size().y - frame.body.get_combined_minimum_size().y
	chrome += float(frame.body.get_theme_constant(&"separation"))
	for c in _content.get_children():
		if c != fit and (c as Control).visible:
			chrome += (c as Control).get_combined_minimum_size().y + inner
	chrome += fit.get_combined_minimum_size().y - fit.scroll.get_combined_minimum_size().y
	fit.max_height = maxf(FitScroll.MIN_VIEW * Settings.text_scale, max_height - chrome)


## Up / down on the focused page scroll it by SCROLL_STEP of its view; at either end they move
## on (a pad never gets trapped).
func _on_page_input(event: InputEvent) -> void:
	var down := event.is_action_pressed("ui_down", true)
	var up := event.is_action_pressed("ui_up", true)
	if not (down or up):
		return
	if not _corp_items.is_empty():
		# B5: on the corporations' page up / down pick the corporation; past either end they move on.
		var to := selected_corp + (1 if down else -1)
		if to >= 0 and to < _corp_items.size():
			pick_corporation(to)
			fit.scroll.ensure_control_visible(_corp_rows[to])
		else:
			var away := page.find_valid_focus_neighbor(SIDE_BOTTOM if down else SIDE_TOP)
			if away != null:
				away.grab_focus()
		page.accept_event()
		return
	var bar := fit.scroll.get_v_scroll_bar()
	var at_edge := bar == null or bar.max_value - bar.page <= 0.5 or (down and bar.value >= bar.max_value - bar.page - 0.5) or (up and bar.value <= bar.min_value + 0.5)
	if at_edge:
		var next := page.find_valid_focus_neighbor(SIDE_BOTTOM if down else SIDE_TOP)
		if next != null:
			next.grab_focus()
	else:
		fit.scroll.scroll_vertical = roundi(clampf(bar.value + (1.0 if down else -1.0) * maxf(1.0, bar.page * SCROLL_STEP), bar.min_value, bar.max_value - bar.page))
	page.accept_event()


func _redraw_marks() -> void:
	_marks.queue_redraw()
	for r in _corp_rows:
		r.queue_redraw()


func _draw_marks() -> void:
	if page.has_focus() and _corp_items.is_empty():  # B5: on the corporations the picked row carries them
		StyleBoxBrackets.draw_on(_marks, Rect2(Vector2.ZERO, _marks.size))



## Every word on the book now (tests: a tab per section, the entries shown).
func all_text() -> String:
	var out := PackedStringArray()
	for b in tabs.get_children():
		out.append((b as MenuChip).shown_text())
	out.append(heading.text)
	for n in columns.find_children("*", "Label", true, false):
		out.append((n as Label).text)
	return "\n".join(out)


## The number of body columns shown now.
func column_count() -> int:
	return columns.get_child_count()
