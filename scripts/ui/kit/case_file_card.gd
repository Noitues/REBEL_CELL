class_name CaseFileCard
extends VBoxContainer
## One campaign slot as a case file on the title's CAMPAIGN SLOTS page. Parity SLOTS-01 /
## SLOTS-02 (designer 2026-10-05: take the M13 build's slot cards, rework them in the v2
## concept language): ported from art-m13-final `scripts/ui/kit/case_file_card.gd` (the
## build's three-card layout and content), reworked on ART_BIBLE v2 §1.2 / §4.12 / §4.13 and
## round 33 `ui_kit.png` / `abandon_dialog.png`:
## - A used slot is a manila case folder (corp paper, §1.2: the corporation's file on the
##   Cell's campaign), on round 21's own manila stock (`AuditDossier.MANILA_ART`, the art
##   pass's asset): a SLOT n tab, the corporation's letterhead stripe in its hue and its emblem
##   disc at the foot (`CorpSeal`, the art pass's exported emblems), the corporation's name as the document
##   title in Courier Prime Bold (v2 drops the build's stencil: stencils are rejected, §1.2),
##   the typed fields HEAT (bar in the Heat colour + number) / ICE / RUNS / FILED, the state as
##   an Anton rubber stamp (IN A RUN / WON / LOST) and the crew as portrait chips (v2 busts'
##   prints, `CrewChip`; a flatlined operative crossed out in red pencil).
## - An empty slot is a dashed outline on the terminal glass: EMPTY SLOT / No campaign filed
##   here yet., and its NEW CAMPAIGN terminal chip.
## - A sliver of paper pokes out of each used folder's top (the art pass's print stock, round
##   21 `sheet`, `DossierPhoto.STOCK_ART`): a document filed inside.
## - The actions sit under the folder on the glass (materials never mix). Designer ruling
##   2026-10-05 (SLOTS b, overriding §2.10's one sticker verb per screen on this page): LOAD on
##   the primary slot is the pink sticker verb (every other LOAD a terminal chip) and DELETE is
##   a sticker on every used slot, 4C's own baked `dialog_delete` art (abandon.py), shown at
##   LOAD's size; a red grease-pencil "Can't Undo" with an arrow points at it (up to
##   PENCIL_UP_TO; past it the words are in DELETE's tooltip). The confirm DELETE opens is 4C's
##   abandon dialog.
## Signals up; the title screen acts. View only.

signal load_pressed(slot: String)
signal delete_pressed(slot: String)
signal new_pressed(slot: String)

## The folder's width at text scale 1.0 (px), the tab's height and share of the width, the
## letterhead stripe's width, the emblem disc's diameter and the crew chip's size.
const FOLDER_W := 300.0
const TAB_H := 24.0
## The tab stops growing at this text scale (its caption still fits): the card stays short
## enough for a row of case files to fit the room at 1.6.
const TAB_SCALE_MAX := 1.3
const TAB_SHARE := 0.42
const STRIPE_W := 10.0
const EMBLEM := 40.0
## The emblem's half size as a share of the disc's radius.
const EMBLEM_SHARE := 0.62
## The most crew chips shown (the rest as "+n").
const CREW_MAX := 4
## The crew chips stop growing at this text scale, so a row of case files fits the page's room
## above the ticker.
const CREW_SCALE_MAX := 1.3
## The Heat bar's height (px at 1.0).
const HEAT_BAR_H := 10.0
## The folder's tilt (degrees; paper carries a slight rotation), its hard shadow's offset (px),
## the empty outline's dash (px) and the folder's ink edge alpha (opaque in high contrast).
const TILT := -1.0
const SHADOW := Vector2(4, 5)
const DASH := 8.0
const EDGE_ALPHA := 0.6
## The tab's cut corner (px) and the words' inset in it.
const TAB_CUT := 12.0
## The LOAD sticker's lettering (px at 1.0) and tilt; the state stamp's tilt.
const VERB_PX := 24.0
const VERB_TILT := -2.0
const STAMP_TILT := -6.0
## DELETE: 4C's baked sticker (abandon.py `dialog_delete`) at this share of its game size (about
## the LOAD sticker's size), growing with the text only up to DELETE_GROW_MAX (a row of case files
## still fits the room at 1.6), and its tilt (abandon.py's verb tilt).
const DELETE_ART := "dialog_delete"
const DELETE_ART_SCALE := 0.65
const DELETE_GROW_MAX := 1.15
const DELETE_TILT := 3.0
## The "Can't Undo" pencil: shown up to this text scale (past it DELETE's tooltip says it), its
## lettering grows up to NOTE_SCALE_MAX, its tilt (radians), the least shaft of its arrow and
## the gap the arrow's head keeps from the sticker (px at 1.0).
const PENCIL_UP_TO := 1.6
const NOTE_SCALE_MAX := 1.0
const NOTE_TILT := -0.06
const ARROW_MIN := 34.0
const ARROW_GAP := 4.0
## The paper sliver poking out of the folder: its rise over the folder's top (share of the tab's
## height), its inset from the tab and the folder's right edge (px at 1.0) and its tilt (degrees).
const SLIVER_RISE := 0.55
const SLIVER_INSET := 10.0
const SLIVER_TILT := 1.2
## The flatlined chip's pencil X: inset and width (shares of the chip's width).
const KIA_INSET := 0.12
const KIA_WIDTH := 0.06

var slot: String = ""
## The slot's summary (RunManager.slot_summary) or {} when empty.
var summary: Dictionary = {}
## [{id, name, class_id, alive}] of the slot's crew.
var crew: Array = []
## The page's one sticker verb sits on this card (LOAD).
var primary: bool = false
var folder: MarginContainer
var load_button: Button = null
var delete_button: Button = null
var new_button: Button = null
var _content: VBoxContainer
var _tab_words: String = ""
## The red grease-pencil "Can't Undo" pointing at DELETE (null past PENCIL_UP_TO).
var cant_undo: PencilNote = null
var _note_room: Control = null


func _init(p_slot: String = "", p_summary: Dictionary = {}, p_crew: Array = [], p_primary: bool = false) -> void:
	slot = p_slot
	summary = p_summary
	crew = p_crew
	primary = p_primary and not p_summary.is_empty()
	name = "Slot%s" % slot
	_tab_words = tr("SLOT %s") % slot
	add_theme_constant_override("separation", UiTheme.SP_S)
	var s := Settings.text_scale
	folder = MarginContainer.new()
	folder.name = "Folder"
	folder.custom_minimum_size = Vector2(width(), 0)
	folder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	folder.add_theme_constant_override("margin_left", roundi(STRIPE_W * s) + UiTheme.SP_S)
	folder.add_theme_constant_override("margin_top", roundi(tab_height()) + UiTheme.SP_S)
	folder.add_theme_constant_override("margin_right", UiTheme.SP_S)
	folder.add_theme_constant_override("margin_bottom", UiTheme.SP_S)
	folder.draw.connect(_draw_folder)
	# Folders in a row stand as tall as the tallest (their actions line up under them).
	folder.size_flags_vertical = Control.SIZE_EXPAND_FILL
	add_child(folder)
	_content = VBoxContainer.new()
	_content.name = "Fields"
	_content.add_theme_constant_override("separation", UiTheme.SP_XS)
	_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	folder.add_child(_content)
	var actions := HBoxContainer.new()
	actions.name = "Actions"
	actions.add_theme_constant_override("separation", UiTheme.SP_S)
	actions.alignment = BoxContainer.ALIGNMENT_BEGIN
	add_child(actions)
	if summary.is_empty():
		_fill_empty()
		new_button = _chip(actions, tr("New campaign"), "", tr("Start a new campaign in slot %s.") % slot)
		new_button.name = "New"
		new_button.pressed.connect(func() -> void: new_pressed.emit(slot))
		return
	_fill()
	var load_tip := tr("Load the campaign in slot %s.") % slot
	if primary:
		var verb := VerbSticker.new(tr("LOAD"), VerbSticker.Fill.PINK, VERB_PX, VERB_TILT)
		verb.pre_translated = true
		verb.tooltip_text = UiTip.fold(load_tip)
		verb.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		actions.add_child(verb)
		load_button = verb
	else:
		load_button = _chip(actions, tr("Load"), "", load_tip)
	load_button.name = "Load"
	load_button.pressed.connect(func() -> void: load_pressed.emit(slot))
	var undo := tr("Can't Undo")
	var tip := tr("Delete the campaign in slot %s (asks first).") % slot
	# The room between LOAD and DELETE: it holds the pencil note (never laid out by the row).
	var gap := Control.new()
	gap.name = "NoteRoom"
	gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	actions.add_child(gap)
	if Settings.text_scale <= PENCIL_UP_TO:
		cant_undo = PencilNote.new("
".join(undo.split(" ", false, 1)), Palette.PENCIL_THREAT, NOTE_TILT,
			roundi(PencilNote.FONT_PX * minf(Settings.text_scale, NOTE_SCALE_MAX)))
		cant_undo.name = "CantUndo"
		gap.add_child(cant_undo)
		gap.custom_minimum_size = cant_undo.text_size() + Vector2(ARROW_MIN * Settings.text_scale, 0)
		gap.resized.connect(_place_note)
		_note_room = gap
	else:
		tip = "%s (%s)" % [tip, undo]
	var shown := tr("DELETE")
	var art := DELETE_ART if shown == "DELETE" and ResourceLoader.exists(VerbSticker.ART_DIR + DELETE_ART + ".png") else ""
	var del := VerbSticker.new(shown, VerbSticker.Fill.PINK, VERB_PX, DELETE_TILT, art)
	del.pre_translated = true
	if art != "":
		var ts := Settings.text_scale
		del.set_art_scale(DELETE_ART_SCALE * minf(ts, DELETE_GROW_MAX) / clampf(ts, 1.0, VerbSticker.SCALE_MAX))
	del.tooltip_text = UiTip.fold(tip)
	del.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	actions.add_child(del)
	delete_button = del
	delete_button.name = "Delete"
	delete_button.pressed.connect(func() -> void: delete_pressed.emit(slot))


func _ready() -> void:
	if not summary.is_empty():
		folder.resized.connect(_tilt)
		_tilt()


## The folder's slight paper tilt round its centre.
func _tilt() -> void:
	folder.pivot_offset = folder.size * 0.5
	folder.rotation_degrees = TILT


## Lays the pencil note in its room: the words at the left, centred, the arrow from them to
## just short of DELETE (UI drawn after the pencil never covers it: PencilLint).
func _place_note() -> void:
	if cant_undo == null or _note_room == null:
		return
	var t := cant_undo.text_size()
	cant_undo.position = Vector2(0.0, floorf((_note_room.size.y - t.y) * 0.5))
	var y := t.y * 0.5
	# The head stops short of the row's separation and DELETE by the wax's own reach (half its width,
	# its under-shadow).
	var reach := GreasePencilMark.WIDTH * 0.5 + GreasePencilMark.SHADOW_OFFSET.x + GreasePencilMark.SHADOW_GROW
	var to_x := _note_room.size.x + UiTheme.SP_S - reach - ARROW_GAP * Settings.text_scale
	cant_undo.with_arrow(Vector2(t.x + ARROW_GAP, y), Vector2(maxf(t.x + ARROW_GAP + 1.0, to_x), y), -t.y * 0.25)


## The tab's height at the text size now (px).
static func tab_height() -> float:
	return TAB_H * minf(Settings.text_scale, TAB_SCALE_MAX)


## The card's width at the text size now (px).
static func width() -> float:
	return FOLDER_W * Settings.text_scale


## The width of what is filed in the folder (px): the folder less its stripe and margins.
static func inner_width() -> float:
	var s := Settings.text_scale
	return width() - (roundi(STRIPE_W * s) + UiTheme.SP_S) - UiTheme.SP_S


## The focusable actions of the card, left to right (LOAD, DELETE; or NEW CAMPAIGN).
func actions() -> Array[Control]:
	var out: Array[Control] = []
	for b in [load_button, delete_button, new_button]:
		if b != null:
			out.append(b)
	return out


## A terminal chip (MenuChip, drawn: the Cell's cyan edge and caret, following the skin) under
## the folder.
func _chip(row: HBoxContainer, words: String, line: String, tip: String) -> MenuChip:
	var b := MenuChip.new(words, line)
	b.pre_translated = true
	b.plate = &""  # drawn: the Cell accent marks its edge
	b.line_step = UiTheme.CAPTION
	b.tooltip_text = UiTip.fold(tip)
	b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	b.refit()
	row.add_child(b)
	return b


func _corp_id() -> StringName:
	return StringName(String(summary.get("corporation", "")))


## A line of words filed in the folder (`font` at type step `step`), INK on the paper (or
## glass words on the empty slot's glass).
func _label(words: String, step: int, font: Font, col: Color) -> Label:
	var l := Label.new()
	l.text = words
	l.add_theme_font_override(&"font", font)
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(step))
	l.add_theme_color_override(&"font_color", col if summary.is_empty() else PaperInk.text(col))
	UiWrap.whole_words(l)
	# A wrapped line knows its height only at its width: set it now (never measured at 0).
	l.custom_minimum_size.x = inner_width()
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _fill_empty() -> void:
	# An empty slot is only its dashed outline on the glass: terminal words (the Cell's own).
	var l := _label(tr("EMPTY SLOT"), UiTheme.LABEL, Chrome.caps_font(UiTheme.LABEL), Palette.TEXT_HI)
	l.name = "Empty"
	_content.add_child(l)
	var hint := _label(tr("No campaign filed here yet."), UiTheme.BODY, Palette.body(), Palette.TEXT_MID)
	hint.name = "EmptyHint"
	_content.add_child(hint)


func _fill() -> void:
	var corp := RunManager.lookup().get_content(_corp_id()) as CorporationData
	var corp_name := TextDb.t(corp, "display_name") if corp != null else String(_corp_id())
	var name_l := _label(corp_name.to_upper(), UiTheme.LABEL, Palette.paper_bold(), Palette.PAPER_TYPE_INK)
	name_l.name = "CorpName"
	_content.add_child(name_l)
	# Heat: the word, the bar and the number (never colour alone).
	var heat := int(summary.get("heat", 0))
	var heat_row := HBoxContainer.new()
	heat_row.name = "HeatRow"
	heat_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	heat_row.add_theme_constant_override("separation", UiTheme.SP_S)
	heat_row.add_child(_field(tr("HEAT")))
	var bar := Control.new()
	bar.name = "HeatBar"
	bar.custom_minimum_size = Vector2(0, HEAT_BAR_H * Settings.text_scale)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.set_meta(&"heat", heat)
	bar.draw.connect(_draw_heat.bind(bar, heat))
	heat_row.add_child(bar)
	var heat_n := _field(str(heat), true)
	heat_n.name = "HeatValue"
	heat_row.add_child(heat_n)
	_content.add_child(heat_row)
	var facts := HFlowContainer.new()
	facts.name = "Facts"
	facts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	facts.add_theme_constant_override("h_separation", UiTheme.SP_M)
	facts.add_child(_pair(tr("ICE"), str(int(summary.get("ice", 0))), "Ice"))
	facts.add_child(_pair(tr("RUNS"), str(int(summary.get("runs", 0))), "Runs"))
	var when := last_played(float(summary.get("saved_at", 0.0)))
	if when != "":
		var date := _pair(tr("FILED"), when, "LastPlayed")
		date.tooltip_text = tr("Last played")
		date.mouse_filter = Control.MOUSE_FILTER_PASS
		facts.add_child(date)
	_content.add_child(facts)
	var foot := HBoxContainer.new()
	foot.name = "Foot"
	foot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foot.add_theme_constant_override("separation", UiTheme.SP_XS)
	var shown := 0
	for op in crew:
		if shown >= CREW_MAX:
			break
		foot.add_child(_crew_chip(op as Dictionary))
		shown += 1
	if crew.size() > CREW_MAX:
		var more := _field("+%d" % (crew.size() - CREW_MAX), true)
		more.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		foot.add_child(more)
	# The stamp and the corporation's seal at the foot's right, as on a filed document.
	var room := Control.new()
	room.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	room.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foot.add_child(room)
	var state := state_word()
	if state != "":
		var st := RubberStamp.new(state, PaperInk.text(Palette.END_STAMP_RED), UiTheme.BODY, STAMP_TILT)
		st.name = "State"
		st.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		foot.add_child(st)
	var disc := Control.new()
	disc.name = "Emblem"
	disc.custom_minimum_size = Vector2.ONE * EMBLEM * Settings.text_scale
	disc.size_flags_vertical = Control.SIZE_SHRINK_END
	disc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	disc.draw.connect(_draw_emblem.bind(disc))
	foot.add_child(disc)
	_content.add_child(foot)


## A typed field word in Courier Prime (`bold` for a value).
func _field(words: String, bold: bool = false) -> Label:
	var l := Label.new()
	l.text = words
	l.add_theme_font_override(&"font", Palette.paper_bold() if bold else Palette.paper())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.BODY))
	l.add_theme_color_override(&"font_color", PaperInk.text(Palette.PAPER_TYPE_INK))
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## A typed field: its name and its value (bold).
func _pair(field_name: String, value: String, node_name: String) -> HBoxContainer:
	var p := HBoxContainer.new()
	p.name = node_name
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.add_theme_constant_override("separation", UiTheme.SP_XS)
	p.add_child(_field(field_name))
	var v := _field(value, true)
	v.name = "Value"
	p.add_child(v)
	return p


## One operative's portrait chip (the v2 bust's print; the name under it); flatlined: crossed
## out in red pencil. Not a control of its own (it names the operative on hover).
func _crew_chip(op: Dictionary) -> CrewChip:
	var chip := CrewChip.new(StringName(String(op.get("class_id", ""))), StringName(String(op.get("id", ""))), String(op.get("name", "")))
	chip.name = "Crew_%s" % String(op.get("id", ""))
	chip.custom_minimum_size = CrewChip.CHIP_SIZE * minf(Settings.text_scale, CREW_SCALE_MAX)
	chip.focus_mode = Control.FOCUS_NONE
	chip.disabled = true  # a picture, not a button: no hover light, no press
	chip.mouse_filter = Control.MOUSE_FILTER_PASS
	chip.tooltip_text = String(op.get("name", ""))
	chip.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	if not bool(op.get("alive", true)):
		chip.set_meta(&"flatlined", true)
		chip.tooltip_text = "%s (%s)" % [chip.tooltip_text, tr("flatlined")]
		chip.draw.connect(_draw_flatlined.bind(chip))
	return chip


## The state as a stamp word ("" while the campaign is simply active).
func state_word() -> String:
	if bool(summary.get("in_run", false)):
		return tr("IN A RUN")
	match String(summary.get("state", "active")):
		"won":
			return tr("WON")
		"lost":
			return tr("LOST")
		"abandoned":
			return tr("ABANDONED")
	return ""


## The save time as a date ("2026-09-29"); "" when unknown.
static func last_played(unix: float) -> String:
	if unix <= 0.0:
		return ""
	var d := Time.get_date_dict_from_unix_time(int(unix))
	return "%04d-%02d-%02d" % [int(d["year"]), int(d["month"]), int(d["day"])]


func _draw_flatlined(chip: Control) -> void:
	var m := chip.size.x * KIA_INSET
	var w := maxf(2.0, chip.size.x * KIA_WIDTH)
	var red := PortraitFeed.pencil_red()
	chip.draw_line(Vector2(m, m), chip.size - Vector2(m, m), red, w, true)
	chip.draw_line(Vector2(chip.size.x - m, m), Vector2(m, chip.size.y - m), red, w, true)


func _draw_heat(bar: Control, heat: int) -> void:
	var r := Rect2(Vector2.ZERO, bar.size)
	bar.draw_rect(r, PaperInk.opaque(Color(Palette.INK, 0.12)))
	var full := maxi(1, RunManager.config().heat_max)
	var k := clampf(float(heat) / full, 0.0, 1.0)
	bar.draw_rect(Rect2(r.position, Vector2(r.size.x * k, r.size.y)), Palette.heat_color(heat))
	bar.draw_rect(r, Palette.INK, false, PaperInk.edge_width(1.0))


## The corporation's emblem disc: an ink disc with the emblem in the corporation's hue.
func _draw_emblem(disc: Control) -> void:
	var c := disc.size * 0.5
	var r := minf(c.x, c.y)
	disc.draw_circle(c, r, Palette.INK)
	CorpSeal.draw_crest(disc, c, r * EMBLEM_SHARE, _corp_id(), Palette.corp_color(_corp_id()))


func _draw_folder() -> void:
	var s := Settings.text_scale
	var sz := folder.size
	var tab_w := sz.x * TAB_SHARE
	var tab_h := tab_height()
	var body := Rect2(0, tab_h, sz.x, sz.y - tab_h)
	var words_at := Vector2(UiTheme.SP_S, tab_h * 0.72)
	var px := UiTheme.font_px(UiTheme.CAPTION)
	if summary.is_empty():
		# An empty slot: a dashed outline on the glass, nothing filed.
		_dashed(body, Palette.TEXT_MID)
		_dashed(Rect2(Vector2.ZERO, Vector2(tab_w, tab_h)), Palette.TEXT_MID)
		folder.draw_string(Chrome.caps_font(UiTheme.CAPTION), words_at, _tab_words, HORIZONTAL_ALIGNMENT_LEFT, tab_w - UiTheme.SP_S, px, Palette.TEXT_HI)
		return
	# The tab and the folder on manila, with a hard shadow (paper).
	var tab := PackedVector2Array([Vector2(0, tab_h), Vector2(0, 0), Vector2(tab_w - TAB_CUT * s, 0), Vector2(tab_w, tab_h)])
	var sh := PackedVector2Array()
	for p in tab:
		sh.append(p + SHADOW)
	folder.draw_colored_polygon(sh, Palette.SHADOW)
	folder.draw_rect(Rect2(body.position + SHADOW, body.size), Palette.SHADOW)
	# A document filed inside pokes out of the top, right of the tab (behind the folder's front).
	var stock := print_stock()
	if stock != null:
		var inset := SLIVER_INSET * s
		var sheet := Rect2(tab_w + inset, tab_h * (1.0 - SLIVER_RISE), sz.x - tab_w - inset * 2.0, tab_h * SLIVER_RISE + inset)
		folder.draw_set_transform(sheet.get_center(), deg_to_rad(SLIVER_TILT), Vector2.ONE)
		var local := Rect2(-sheet.size * 0.5, sheet.size)
		folder.draw_texture_rect_region(stock, local, Rect2(Vector2.ZERO, sheet.size.min(stock.get_size())))
		folder.draw_rect(local, PaperInk.edge(Color(Palette.INK, EDGE_ALPHA * 0.5)), false, PaperInk.edge_width(1.0))
		folder.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var manila := manila_stock()
	if manila != null:
		folder.draw_texture_rect_region(manila, body, Rect2(Vector2.ZERO, body.size.min(manila.get_size())))
		var uv := PackedVector2Array()
		for p in tab:
			uv.append(p / manila.get_size())  # the stock 1:1, as the body
		folder.draw_colored_polygon(tab, Palette.NO_TINT, uv, manila)
	else:
		folder.draw_colored_polygon(tab, Palette.NOTE_PAPER)
		folder.draw_rect(body, Palette.NOTE_PAPER)
	var edge := PaperInk.edge(Color(Palette.END_MANILA_EDGE, EDGE_ALPHA))
	var ew := PaperInk.edge_width(1.0)
	folder.draw_polyline(tab, edge, ew)
	folder.draw_rect(body, edge, false, ew)
	folder.draw_string(Palette.paper_bold(), words_at, _tab_words, HORIZONTAL_ALIGNMENT_LEFT, tab_w - UiTheme.SP_S, px, PaperInk.text(Palette.PAPER_TYPE_INK))
	# The corporation's letterhead stripe down the left edge, in its hue.
	folder.draw_rect(Rect2(body.position, Vector2(STRIPE_W * s, body.size.y)), Palette.corp_color(_corp_id()))


## Round 21's manila stock (the art pass's asset), held once: a texture loaded inside a draw
## and let go at its end is freed before the frame renders (it drew white).
static func manila_stock() -> Texture2D:
	if _manila == null:
		_manila = load(AuditDossier.MANILA_ART) as Texture2D
	return _manila


static var _manila: Texture2D = null


## The art pass's print stock (round 21 `sheet`, DossierPhoto.STOCK_ART), held once.
static func print_stock() -> Texture2D:
	if _stock == null:
		_stock = load(DossierPhoto.STOCK_ART) as Texture2D
	return _stock


static var _stock: Texture2D = null


func _dashed(r: Rect2, col: Color) -> void:
	var pts := [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y), r.position]
	for i in 4:
		folder.draw_dashed_line(pts[i], pts[i + 1], col, 1.0, DASH)
