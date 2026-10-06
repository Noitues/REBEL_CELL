class_name CaseFileCard
extends VBoxContainer
## One campaign slot as a case file on the title's CAMPAIGN SLOTS page. Parity SLOTS-01 /
## SLOTS-02 (designer 2026-10-05: take the M13 build's slot cards, rework them in the v2
## concept language): ported from art-m13-final `scripts/ui/kit/case_file_card.gd` (the
## build's three-card layout and content), reworked on ART_BIBLE v2 §1.2 / §4.12 / §4.13.
## B5 (round 44 B_menus `campaign_slots.png`; review D21 / section c, D24; designer ruling 2026-10-06 2):
## - A used slot is a manila case folder: the CELL's own file, so it carries the Cell's marks, never a corp
##   letterhead: on round 21's manila stock (`AuditDossier.MANILA_ART`), its tab holds the Cell's terminal tab-clip
##   label ("SLOT 1 // CELL-01", TabClipLabel), the fields are printed in Share Tech Mono (the Cell's printer): the
##   corporation's name over a rule with its crest in ink, HEAT (number, band word and bar) / ICE / RUNS / FILED,
##   the Cell's red hex-and-fist rubber stamp with the campaign's state (CellStamp, the concept's own image), and the
##   crew as portrait chips (v2 busts' prints, `CrewChip`; a flatlined operative crossed out in red pencil).
## - D24: the folder lies on the glass at a seeded 1-2 degree tilt with a soft contact shadow (PaperLie); the slot
##   that holds the focus lies straight and lifted.
## - An empty slot is a dashed outline on the terminal glass: EMPTY SLOT / No campaign filed here yet., and its NEW
##   CAMPAIGN terminal chip.
## - A sliver of paper pokes out of each used folder's top (the art pass's print stock): a document filed inside.
## - The actions sit under the folder on the glass (materials never mix). Designer ruling 2026-10-06 (2): LOAD and
##   DELETE stickers on every folder: LOAD is the pink verb (the newest campaign's, `primary`, takes the first focus
##   and the page's one scheduled sweep), DELETE the neutral white vinyl (round 44 FILL_WHITE: it is not the page's
##   verb), and each DELETE carries the red grease-pencil "Can't Undo" under it with its arrow up to it (up to
##   PENCIL_UP_TO; past it the words are in DELETE's tooltip). The confirm DELETE opens is 4C's abandon dialog.
## Signals up; the title screen acts. View only.

signal load_pressed(slot: String)
signal delete_pressed(slot: String)
signal new_pressed(slot: String)

## The folder's width at text scale 1.0 (px), the tab's height and share of the width and the crew chip's size.
const FOLDER_W := 300.0
const TAB_H := 24.0
## The tab stops growing at this text scale (its caption still fits): the card stays short
## enough for a row of case files to fit the room at 1.6.
const TAB_SCALE_MAX := 1.3
const TAB_SHARE := 0.58
## The folder's inner margin (px at 1.0) and the crest's size beside the corporation's name (px at 1.0).
const INNER := 12.0
const CREST := 18.0
## The most crew chips shown (the rest as "+n").
const CREW_MAX := 4
## The crew chips stop growing at this text scale, so a row of case files fits the page's room
## above the ticker.
const CREW_SCALE_MAX := 1.15
## The Heat bar's height (px at 1.0).
const HEAT_BAR_H := 8.0
## The empty outline's dash (px) and the folder's ink edge alpha (opaque in high contrast).
const DASH := 8.0
const EDGE_ALPHA := 0.6
## Round 44's ink and field-name ink on manila (campaign_slots.py INKP and the field names' (96, 80, 60)).
const INK := Color8(40, 34, 30)
const FIELD_INK := Color8(96, 80, 60)
## The tab's cut corner (px) and the tab clip's inset from the tab's left (px at 1.0).
const TAB_CUT := 12.0
const CLIP_INSET := 10.0
## The LOAD and DELETE stickers' lettering (px at 1.0; round 44: LOAD 50, DELETE 34 on the 1080p board) and tilts.
const VERB_PX := 30.0
const DELETE_PX := 21.0
const VERB_TILT := -2.0
const DELETE_TILT := 2.0
## The stickers grow with the text only up to this scale (a row of case files fits the room at 1.6), and from
## COMPACT_FROM the ICE / RUNS / FILED fields share a line (the folder stays short enough).
const VERB_GROW_MAX := 1.0
const COMPACT_FROM := 1.3
## The Cell stamp's seeded tilt range (degrees; round 44: -6 + 2 n).
const STAMP_TILT := -6.0
const STAMP_TILT_STEP := 2.0
## The "Can't Undo" pencil: shown up to this text scale (past it DELETE's tooltip says it), its
## lettering grows up to NOTE_SCALE_MAX, its tilt (radians), and the gap the arrow's head keeps from the sticker
## (px at 1.0).
const PENCIL_UP_TO := 1.6
const NOTE_SCALE_MAX := 1.0
const NOTE_TILT := -0.06
const ARROW_GAP := 4.0
const ARROW_MIN := 34.0
## The arrow's bend (share of the note's height) and where it lands up DELETE's left edge (share of its height).
const ARROW_BEND := 0.5
const ARROW_LAND := 0.7
## The paper sliver poking out of the folder: its rise over the folder's top (share of the tab's
## height), its inset from the tab and the folder's right edge (px at 1.0) and its tilt (degrees).
const SLIVER_RISE := 0.55
const SLIVER_INSET := 10.0
const SLIVER_TILT := 1.2
## The flatlined chip's pencil X: inset and width (shares of the chip's width).
const KIA_INSET := 0.12
const KIA_SEED := 61
## The seed of a slot's paper tilt (PaperLie; one per slot).
const TILT_SEED := 4400

var slot: String = ""
## The slot's summary (RunManager.slot_summary) or {} when empty.
var summary: Dictionary = {}
## [{id, name, class_id, alive}] of the slot's crew.
var crew: Array = []
## The newest campaign: its LOAD takes the page's first focus.
var primary: bool = false
var folder: MarginContainer
var load_button: Button = null
var delete_button: Button = null
var new_button: Button = null
## The Cell's tab-clip label on the tab (null on an empty slot).
var tab_clip: TabClipLabel = null
## The Cell's rubber stamp (null on an empty slot).
var stamp: CellStamp = null
var _content: VBoxContainer
var _tab_words: String = ""
## The red grease-pencil "Can't Undo" pointing at DELETE (null past PENCIL_UP_TO).
var cant_undo: PencilNote = null
var _note_room: Control = null
## The folder's seeded tilt (degrees; D24) and whether the slot holds the focus (it lies straight then).
var tilt: float = 0.0
var _held: bool = false


func _init(p_slot: String = "", p_summary: Dictionary = {}, p_crew: Array = [], p_primary: bool = false) -> void:
	slot = p_slot
	summary = p_summary
	crew = p_crew
	primary = p_primary and not p_summary.is_empty()
	name = "Slot%s" % slot
	_tab_words = tr("SLOT %s") % slot
	tilt = PaperLie.tilt_deg(TILT_SEED + slot.to_int())
	add_theme_constant_override("separation", UiTheme.SP_S)
	var s := Settings.text_scale
	folder = MarginContainer.new()
	folder.name = "Folder"
	folder.custom_minimum_size = Vector2(width(), 0)
	folder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	folder.add_theme_constant_override("margin_left", roundi(INNER * s))
	folder.add_theme_constant_override("margin_top", roundi(tab_height() + INNER * s * 0.5))
	folder.add_theme_constant_override("margin_right", roundi(INNER * s))
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
	tab_clip = TabClipLabel.new(tr("SLOT %s // CELL-%02d") % [slot, slot.to_int()])
	tab_clip.name = "TabClip"
	_folder_marks().add_child(tab_clip)  # placed by _lay (a Node2D layer: never laid out by the folder)
	var load_tip := tr("Load the campaign in slot %s.") % slot
	# Every used slot's LOAD is the pink sticker (designer rulings 2026-10-05 SLOTS c, 2026-10-06 2); the newest
	# campaign's (`primary`) takes the page's first focus and its one scheduled sweep (B1d).
	var verb := VerbSticker.new(tr("LOAD"), VerbSticker.Fill.PINK, VERB_PX * verb_grow(), VERB_TILT)
	verb.pre_translated = true
	verb.sweep_primary = primary
	verb.tooltip_text = UiTip.fold(load_tip)
	verb.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	actions.add_child(verb)
	load_button = verb
	load_button.name = "Load"
	load_button.pressed.connect(func() -> void: load_pressed.emit(slot))
	# The room between LOAD and DELETE: it holds the pencil note (never laid out by the row): the words low in it,
	# the arrow up to DELETE's side (round 44: the words under-left of DELETE, the arrow up to it).
	var gap := Control.new()
	gap.name = "NoteRoom"
	gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	actions.add_child(gap)
	var undo := tr("Can't Undo")
	var tip := tr("Delete the campaign in slot %s (asks first).") % slot
	if Settings.text_scale <= PENCIL_UP_TO:
		cant_undo = PencilNote.new("
".join(undo.split(" ", false, 1)), Palette.PENCIL_THREAT, NOTE_TILT,
			roundi(PencilNote.FONT_PX * minf(Settings.text_scale, NOTE_SCALE_MAX)))
		cant_undo.name = "CantUndo"
		_note_layer().add_child(cant_undo)  # placed in its room by _place_note (a Node2D layer: never laid out by the card)
		_note_layer().z_index = 1  # over the stickers beside it (no UI ever covers pencil)
		gap.custom_minimum_size = cant_undo.text_size() + Vector2(ARROW_MIN * Settings.text_scale, 0)
		gap.resized.connect(_place_note)
		actions.sort_children.connect(_place_note)
		sort_children.connect(_place_note)
		_note_room = gap
	else:
		tip = "%s (%s)" % [tip, undo]
	# DELETE: the neutral white vinyl (round 44 FILL_WHITE; not the page's verb, so never pink).
	var del := VerbSticker.new(tr("DELETE"), VerbSticker.Fill.WHITE, DELETE_PX * verb_grow(), DELETE_TILT)
	del.pre_translated = true
	del.tooltip_text = UiTip.fold(tip)
	del.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	actions.add_child(del)
	delete_button = del
	delete_button.name = "Delete"
	delete_button.pressed.connect(func() -> void: delete_pressed.emit(slot))
	for b in [load_button, delete_button]:
		(b as Control).focus_entered.connect(_hold.bind(true))
		(b as Control).focus_exited.connect(_hold.bind(false))


func _ready() -> void:
	if not summary.is_empty():
		folder.resized.connect(_lay)
		# The card's own sort fits the folder (fit_child_in_rect sets its rotation back to 0): the tilt after it.
		sort_children.connect(_lay)
		_lay()


## D24: the folder's seeded tilt round its centre (straight while the slot holds the focus), and the tab clip and
## the stamp in their places.
func _lay() -> void:
	folder.pivot_offset = folder.size * 0.5
	folder.rotation_degrees = 0.0 if _held else tilt
	if tab_clip != null:
		var s := Settings.text_scale
		tab_clip.position = Vector2(CLIP_INSET * s, (tab_height() - tab_clip.size.y) * 0.5)
	if stamp != null:
		stamp.position = Vector2(folder.size.x - stamp.size.x - INNER * Settings.text_scale * 0.5, tab_height() + (folder.size.y - tab_height()) * 0.36)
	folder.queue_redraw()


## The slot takes / gives back the focus: it lies straight and lifted while it holds it (round 44).
func _hold(_on: bool) -> void:
	_held = load_button.has_focus() or delete_button.has_focus()
	_lay()


## True while one of the slot's actions holds the focus (the folder lies straight).
func held() -> bool:
	return _held


## Lays the pencil note in its room between LOAD and DELETE (round 44: the words low, under-left of DELETE; the
## arrow from them up to just short of DELETE's side). In the room's own space (the row lays the room, LOAD and
## DELETE out side by side): UI drawn after the pencil never covers it (PencilLint).
func _place_note() -> void:
	if cant_undo == null or _note_room == null or delete_button == null:
		return
	var t := cant_undo.text_size()
	var s := Settings.text_scale
	var room := _note_room.size
	var y := maxf(0.0, room.y - t.y)
	var at := _note_room.position + (_note_room.get_parent() as Control).position
	cant_undo.position = at + Vector2(0.0, floorf(y))
	# The head stops short of the row's separation and DELETE by the wax's own reach (half its width, its
	# under-shadow), at ARROW_LAND of DELETE's height (the room is as tall as the row: DELETE's centre is its centre).
	var reach := GreasePencilMark.stroke_width() * 0.5 + GreasePencilMark.SHADOW_OFFSET.x
	var del_top := (room.y - delete_button.size.y) * 0.5
	var head := Vector2(room.x + UiTheme.SP_S - reach - ARROW_GAP * s, del_top + delete_button.size.y * ARROW_LAND)
	var from := Vector2(t.x + ARROW_GAP, t.y * 0.5)
	# The head in the note's space (the note sits at the room's left, `y` down it).
	cant_undo.with_arrow(from, Vector2(maxf(from.x + 1.0, head.x), head.y - floorf(y)), -t.y * ARROW_BEND)


var _marks: Node2D = null
var _notes: Node2D = null


## The folder's marks layer (the tab clip, the stamp): a Node2D, so the folder's layout never moves them; drawn
## after the fields.
func _folder_marks() -> Node2D:
	if _marks == null:
		_marks = Node2D.new()
		_marks.name = "Marks"
		folder.add_child(_marks)
	return _marks


## The card's pencil layer (the Can't Undo note): a Node2D drawn after the stickers.
func _note_layer() -> Node2D:
	if _notes == null:
		_notes = Node2D.new()
		_notes.name = "Notes"
		add_child(_notes)
	return _notes


## The stickers' growth with the text, capped at VERB_GROW_MAX (a share of the size VerbSticker grows them to).
static func verb_grow() -> float:
	var s := Settings.text_scale
	return minf(s, VERB_GROW_MAX) / clampf(s, 1.0, VerbSticker.SCALE_MAX)


## The tab's height at the text size now (px).
static func tab_height() -> float:
	return TAB_H * minf(Settings.text_scale, TAB_SCALE_MAX)


## The card's width at the text size now (px).
static func width() -> float:
	return FOLDER_W * Settings.text_scale


## The width of what is filed in the folder (px): the folder less its margins.
static func inner_width() -> float:
	return width() - roundi(INNER * Settings.text_scale) * 2.0


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
	# The corporation's name printed in the Cell's mono, its crest in ink at the right, a rule under them.
	var head := HBoxContainer.new()
	head.name = "Head"
	head.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var name_l := _label(corp_name.to_upper(), UiTheme.LABEL, Palette.mono(), INK)
	name_l.name = "CorpName"
	name_l.custom_minimum_size.x = inner_width() - CREST * Settings.text_scale - UiTheme.SP_XS
	name_l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(name_l)
	var crest := Control.new()
	crest.name = "Crest"
	crest.custom_minimum_size = Vector2.ONE * CREST * Settings.text_scale
	crest.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	crest.mouse_filter = Control.MOUSE_FILTER_IGNORE
	crest.draw.connect(func() -> void: CorpSeal.draw_crest(crest, crest.size * 0.5, crest.size.x * 0.5, _corp_id(), PaperInk.text(INK)))
	head.add_child(crest)
	_content.add_child(head)
	var rule := ColorRect.new()
	rule.name = "Rule"
	rule.color = PaperInk.edge(Color(INK, EDGE_ALPHA))
	rule.custom_minimum_size.y = maxf(1.0, roundf(Settings.text_scale))
	rule.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_content.add_child(rule)
	# Heat: the number, the band word and the bar (never colour alone).
	var heat := int(summary.get("heat", 0))
	var heat_row := HBoxContainer.new()
	heat_row.name = "HeatRow"
	heat_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	heat_row.add_theme_constant_override("separation", UiTheme.SP_S)
	heat_row.add_child(_field(tr("HEAT")))
	var heat_n := _field(str(heat), true)
	heat_n.name = "HeatValue"
	heat_row.add_child(heat_n)
	var band := _field(heat_band_word(heat), true)
	band.name = "HeatBand"
	heat_row.add_child(band)
	var bar := Control.new()
	bar.name = "HeatBar"
	bar.custom_minimum_size = Vector2(0, HEAT_BAR_H * Settings.text_scale)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.set_meta(&"heat", heat)
	bar.draw.connect(_draw_heat.bind(bar, heat))
	heat_row.add_child(bar)
	_content.add_child(heat_row)
	# ICE / RUNS / FILED: a printed line each (round 44); from COMPACT_FROM they share lines (a flow).
	var facts: Container = VBoxContainer.new() if Settings.text_scale < COMPACT_FROM else HFlowContainer.new()
	facts.name = "Facts"
	facts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if facts is HFlowContainer:
		facts.add_theme_constant_override("h_separation", UiTheme.SP_M)
	else:
		facts.add_theme_constant_override("separation", UiTheme.SP_XS)
	_content.add_child(facts)
	facts.add_child(_pair(tr("ICE"), str(int(summary.get("ice", 0))), "Ice"))
	facts.add_child(_pair(tr("RUNS"), str(int(summary.get("runs", 0))), "Runs"))
	var when := last_played(float(summary.get("saved_at", 0.0)))
	if when != "":
		var date := _pair(tr("FILED"), when, "LastPlayed")
		date.tooltip_text = tr("Last played")
		date.mouse_filter = Control.MOUSE_FILTER_PASS
		facts.add_child(date)
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
	_content.add_child(foot)
	# The Cell's own rubber stamp: the campaign's state (it overlaps the fields as a stamp does; no layout room).
	stamp = CellStamp.new(state_word(), STAMP_TILT + STAMP_TILT_STEP * slot.to_int())
	stamp.name = "State"
	_folder_marks().add_child(stamp)  # over the fields, placed by _lay


## The Heat band's word for `heat` (COOL, NOTICED, FLAGGED, HUNTED, PURGE), translated, in caps.
static func heat_band_word(heat: int) -> String:
	var band := HeatPoster.band_of(heat, RunManager.config().heat_band_levels())
	return TranslationServer.translate(HeatPoster.BAND_WORDS[mini(band, HeatPoster.BAND_WORDS.size() - 1)]).to_upper()


## A printed field word in the Cell's mono (`bold` for a value: the ink, else the field name's lighter ink).
func _field(words: String, bold: bool = false) -> Label:
	var l := Label.new()
	l.text = words
	l.add_theme_font_override(&"font", Palette.mono())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.BODY if bold else UiTheme.CAPTION))
	l.add_theme_color_override(&"font_color", PaperInk.text(INK if bold else FIELD_INK))
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## A printed field: its name (a fixed column) and its value.
func _pair(field_name: String, value: String, node_name: String) -> HBoxContainer:
	var p := HBoxContainer.new()
	p.name = node_name
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.add_theme_constant_override("separation", UiTheme.SP_XS)
	var n := _field(field_name)
	n.custom_minimum_size.x = Palette.mono().get_string_size(tr("FILED") + "  ", HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.CAPTION)).x
	p.add_child(n)
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


## The state as the Cell's stamp word (a key): ACTIVE while the campaign simply runs.
func state_word() -> String:
	if bool(summary.get("in_run", false)):
		return "IN A RUN"
	match String(summary.get("state", "active")):
		"won":
			return "WON"
		"lost":
			return "LOST"
		"abandoned":
			return "ABANDONED"
	return "ACTIVE"


## The stamp words (keys) the slot shows.
const STAMP_WORDS := ["ACTIVE", "IN A RUN", "WON", "LOST", "ABANDONED"] # TR


## The save time as a date ("2026-09-29"); "" when unknown.
static func last_played(unix: float) -> String:
	if unix <= 0.0:
		return ""
	var d := Time.get_date_dict_from_unix_time(int(unix))
	return "%04d-%02d-%02d" % [int(d["year"]), int(d["month"]), int(d["day"])]


func _draw_flatlined(chip: Control) -> void:
	# B1b: the kit's wax X (one material, written on).
	PencilSet.show_on(chip, PencilSet.cross_strokes(Rect2(Vector2.ZERO, chip.size), chip.size.x * KIA_INSET), GreasePencilMark.Ink.THREAT, KIA_SEED)


func _draw_heat(bar: Control, heat: int) -> void:
	var r := Rect2(Vector2.ZERO, bar.size)
	var full := maxi(1, RunManager.config().heat_max)
	var k := clampf(float(heat) / full, 0.0, 1.0)
	var inset := maxf(1.0, roundf(Settings.text_scale * 1.5))
	bar.draw_rect(Rect2(r.position + Vector2.ONE * inset, Vector2((r.size.x - inset * 2.0) * k, r.size.y - inset * 2.0)), Palette.heat_color(heat))
	bar.draw_rect(r, PaperInk.edge(Color(INK, 0.86)), false, PaperInk.edge_width(maxf(1.0, roundf(Settings.text_scale))))


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
	var screen_h := folder.get_viewport_rect().size.y
	# D24: the folder's soft contact shadow on the glass (lifted further while it holds the focus).
	var tab := PackedVector2Array([Vector2(0, tab_h), Vector2(0, 0), Vector2(tab_w - TAB_CUT * s, 0), Vector2(tab_w, tab_h)])
	PaperLie.draw_contact_shadow(folder, body, screen_h * (2.0 if _held else 1.0))
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
