class_name CaseFileCard
extends VBoxContainer
## One campaign slot as a case file (ART_BIBLE §11 Campaign slots; critique 02: "a plain text
## list"): a PAPER folder with a tab ("SLOT 1"), the target corporation's hue stripe filled
## with its `CorpPattern` down the left edge and its landmark glyph (SVG) in the corner, the
## corporation's name, a Heat bar in `Palette.heat_color` with its number, the runs and the
## last-played date as icon + number fields, the state (a stamp: IN A RUN / WON / LOST) and
## the crew as mini Polaroids. Under the folder, on the glass (materials never mix, §2), the
## actions: Load (Primary for the newest slot, else Secondary) and Delete (Danger, a trash
## glyph, never the power glyph; the screen asks first). An empty slot is a dashed, empty
## folder with New campaign. Signals up; the title screen acts. View only.

signal load_pressed(slot: String)
signal delete_pressed(slot: String)
signal new_pressed(slot: String)

## The folder's width (and least height) at text scale 1.0 (px), the tab's height and share of the width, the
## hue stripe's width, the landmark glyph's side and the crew Polaroid's size.
const FOLDER := Vector2(300, 250)
const TAB_H := 26.0
const TAB_SHARE := 0.42
const STRIPE_W := 14.0
const LANDMARK := 40.0
const POLAROID := Vector2(46, 56)
## The most crew Polaroids shown (the rest as "+n").
const CREW_MAX := 4
## Heat bar: height (px) and the Heat it shows full (the HUNTED band's top).
const HEAT_BAR_H := 10.0
const HEAT_FULL := 100
## The folder's tilt (degrees; paper carries a slight rotation, §2).
const TILT := -1.0
const DASH := 8.0
## The folder's ink edge alpha (opaque in high contrast).
const EDGE_ALPHA := 0.6

var slot: String = ""
## The slot's summary (RunManager.slot_summary) or {} when empty.
var summary: Dictionary = {}
## [{id, name, class_id, alive}] of the slot's crew.
var crew: Array = []
var primary: bool = false
var folder: Control
var load_button: Button = null
var delete_button: Button = null
var new_button: Button = null
var _content: VBoxContainer


func _init(p_slot: String, p_summary: Dictionary, p_crew: Array = [], p_primary: bool = false) -> void:
	slot = p_slot
	summary = p_summary
	crew = p_crew
	primary = p_primary
	name = "Slot%s" % slot
	add_theme_constant_override("separation", UiTheme.SP_S)
	var s := Settings.text_scale
	# The folder sizes to what is filed in it (§5.3), FOLDER wide at the text scale.
	var box := MarginContainer.new()
	box.name = "Folder"
	box.custom_minimum_size = Vector2(FOLDER.x * s, 0)
	box.mouse_filter = Control.MOUSE_FILTER_PASS
	box.add_theme_constant_override("margin_left", roundi(STRIPE_W * s) + UiTheme.SP_S)
	box.add_theme_constant_override("margin_top", roundi(TAB_H * s) + UiTheme.SP_S)
	box.add_theme_constant_override("margin_right", roundi(LANDMARK * s) + UiTheme.SP_M)
	box.add_theme_constant_override("margin_bottom", UiTheme.SP_M)
	box.draw.connect(_draw_folder)
	# Folders in a row stand as tall as the tallest (their actions line up under them).
	box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	folder = box
	add_child(folder)
	_content = VBoxContainer.new()
	_content.name = "Fields"
	_content.add_theme_constant_override("separation", UiTheme.SP_XS)
	_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	folder.add_child(_content)
	var actions := HBoxContainer.new()
	actions.name = "Actions"
	actions.add_theme_constant_override("separation", UiTheme.SP_S)
	add_child(actions)
	if summary.is_empty():
		_fill_empty()
		new_button = _action(actions, tr("New campaign"), StatIcon.PLAY, UiTheme.PRIMARY if primary else UiTheme.SECONDARY,
			tr("Start a new campaign in slot %s.") % slot, func() -> void: new_pressed.emit(slot))
		new_button.name = "New"
	else:
		_fill()
		load_button = _action(actions, tr("Load"), StatIcon.CONTINUE, UiTheme.PRIMARY if primary else UiTheme.SECONDARY,
			tr("Load the campaign in slot %s.") % slot, func() -> void: load_pressed.emit(slot))
		load_button.name = "Load"
		var gap := Control.new()
		gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
		actions.add_child(gap)
		delete_button = _action(actions, tr("Delete"), StatIcon.TRASH, UiTheme.DANGER,
			tr("Delete the campaign in slot %s (asks first).") % slot, func() -> void: delete_pressed.emit(slot))
		delete_button.name = "Delete"


func _ready() -> void:
	folder.pivot_offset = folder.size * 0.5
	folder.rotation_degrees = TILT


func _action(row: HBoxContainer, words: String, kind: StringName, variant: StringName, tip: String, on_press: Callable) -> Button:
	var b := Button.new()
	b.text = words
	b.theme_type_variation = variant
	b.tooltip_text = UiTip.fold(tip)
	b.pressed.connect(on_press)
	IconMark.attach(b, kind)
	row.add_child(b)
	return b


## The width of what is filed in the folder (px): the folder less its stripe and landmark
## margins.
static func inner_width() -> float:
	var s := Settings.text_scale
	return FOLDER.x * s - (roundi(STRIPE_W * s) + UiTheme.SP_S) - (roundi(LANDMARK * s) + UiTheme.SP_M)


func _corp_id() -> StringName:
	return StringName(String(summary.get("corporation", "")))


func _label(words: String, step: int, font: Font, col: Color = Palette.INK) -> Label:
	var l := Label.new()
	l.text = words
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", UiTheme.font_px(step))
	UiTheme.track_label(l)  # art pass W9F (§4.2): Anton and mono CAPS tracked
	# Art pass WF (§12): words filed on the paper go INK in high contrast (the empty
	# folder's words sit on the glass and keep theirs).
	l.add_theme_color_override("font_color", col if summary.is_empty() else PaperInk.text(col))
	UiWrap.whole_words(l)  # art pass W9F §4.3.3: whole words, never mid-word
	# A wrapped line knows its height only at its width: set it now, so the folder is never
	# measured at width 0 (a transient 2600 px page made the scrolling slot page chase itself).
	l.custom_minimum_size.x = inner_width()
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_content.add_child(l)
	return l


func _fill_empty() -> void:
	# An empty folder is only its dashed outline on the glass: glass words (§3.7: 4.5:1 there).
	var l := _label(tr("EMPTY SLOT"), UiTheme.LABEL, Palette.display(), Palette.TEXT_HI)
	l.name = "Empty"
	var hint := _label(tr("No campaign filed here yet."), UiTheme.BODY, Palette.mono(), Palette.TEXT_HI)
	hint.name = "EmptyHint"


func _fill() -> void:
	var corp := RunManager.lookup().get_content(_corp_id()) as CorporationData
	var corp_name := TextDb.t(corp, "display_name") if corp != null else String(_corp_id())
	var name_l := _label(corp_name.to_upper(), UiTheme.LABEL, Palette.display())
	name_l.name = "CorpName"
	# Heat: the bar and its number (colour + number + icon, §12: never colour alone).
	var heat := int(summary.get("heat", 0))
	var heat_row := HBoxContainer.new()
	heat_row.name = "HeatRow"
	heat_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	heat_row.add_theme_constant_override("separation", UiTheme.SP_S)
	heat_row.add_child(StatField.new(StatIcon.HEAT, str(heat), UiTheme.font_px(UiTheme.BODY), Palette.INK))
	var bar := Control.new()
	bar.name = "HeatBar"
	bar.custom_minimum_size = Vector2(0, HEAT_BAR_H * Settings.text_scale)
	bar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.set_meta(&"heat", heat)
	bar.draw.connect(func() -> void: _draw_heat(bar, heat))
	heat_row.add_child(bar)
	_content.add_child(heat_row)
	var facts := HFlowContainer.new()
	facts.name = "Facts"
	facts.mouse_filter = Control.MOUSE_FILTER_IGNORE
	facts.add_theme_constant_override("h_separation", UiTheme.SP_M)
	facts.add_child(StatField.new(StatIcon.RUNS, str(int(summary.get("runs", 0))), UiTheme.font_px(UiTheme.BODY), Palette.INK))
	facts.add_child(StatField.new(StatIcon.ICE, str(int(summary.get("ice", 0))), UiTheme.font_px(UiTheme.BODY), Palette.INK))
	var when := last_played(float(summary.get("saved_at", 0.0)))
	if when != "":
		var date := StatField.new(StatIcon.SAVE, when, UiTheme.font_px(UiTheme.BODY), Palette.INK)
		date.name = "LastPlayed"
		date.tooltip_text = tr("Last played")
		facts.add_child(date)
	_content.add_child(facts)
	var state := state_word()
	if state != "":
		var st := _label(state, UiTheme.BODY, Palette.display(), Palette.HARM_INK if String(summary.get("state", "")) == "lost" else Palette.INK)
		st.name = "State"
	var photos := HBoxContainer.new()
	photos.name = "Crew"
	photos.mouse_filter = Control.MOUSE_FILTER_IGNORE
	photos.add_theme_constant_override("separation", UiTheme.SP_XS)
	var shown := 0
	for op in crew:
		if shown >= CREW_MAX:
			break
		var p := Polaroid.new("", "[%s PORTRAIT]" % String(op.get("class_id", "")).to_upper(), -3.0 + shown * 2.0)
		p.custom_minimum_size = POLAROID * Settings.text_scale
		p.set_operative(StringName(String(op.get("class_id", ""))), StringName(String(op.get("id", ""))))
		if not bool(op.get("alive", true)):
			p.set_expression(PortraitArt.Expr.FLATLINED)
		p.tooltip_text = String(op.get("name", ""))
		photos.add_child(p)
		shown += 1
	if crew.size() > CREW_MAX:
		var more := Label.new()
		more.text = "+%d" % (crew.size() - CREW_MAX)
		more.add_theme_color_override("font_color", Palette.INK)
		more.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.BODY))
		more.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		photos.add_child(more)
	_content.add_child(photos)


## The state as a stamp word ("" while the campaign is simply active).
func state_word() -> String:
	if bool(summary.get("in_run", false)):
		return tr("IN A RUN")
	match String(summary.get("state", "active")):
		"won":
			return tr("WON")
		"lost":
			return tr("LOST")
	return ""


## The save time as a date ("2026-09-29"); "" when unknown.
static func last_played(unix: float) -> String:
	if unix <= 0.0:
		return ""
	var d := Time.get_date_dict_from_unix_time(int(unix))
	return "%04d-%02d-%02d" % [int(d["year"]), int(d["month"]), int(d["day"])]


func _draw_heat(bar: Control, heat: int) -> void:
	var r := Rect2(Vector2.ZERO, bar.size)
	bar.draw_rect(r, PaperInk.opaque(Color(Palette.INK, 0.12)))
	var k := clampf(float(heat) / HEAT_FULL, 0.0, 1.0)
	bar.draw_rect(Rect2(r.position, Vector2(r.size.x * k, r.size.y)), Palette.heat_color(heat))
	bar.draw_rect(r, Palette.INK, false, PaperInk.edge_width(1.0))


func _draw_folder() -> void:
	var s := Settings.text_scale
	var sz := folder.size
	var tab_w := sz.x * TAB_SHARE
	var tab_h := TAB_H * s
	var body := Rect2(0, tab_h, sz.x, sz.y - tab_h)
	var shadow := Vector2(4, 5)
	if summary.is_empty():
		# An empty folder: a dashed outline on the glass, nothing filed.
		_dashed(Rect2(Vector2(0, tab_h), body.size), Palette.TEXT_MID)
		_dashed(Rect2(Vector2.ZERO, Vector2(tab_w, tab_h)), Palette.TEXT_MID)
		folder.draw_string(Palette.mono(), Vector2(UiTheme.SP_S, tab_h * 0.72), tr("SLOT %s") % slot, HORIZONTAL_ALIGNMENT_LEFT, tab_w, UiTheme.font_px(UiTheme.CAPTION), Palette.TEXT_HI)
		return
	# The tab and the folder, with a hard shadow (paper, §2).
	var tab := PackedVector2Array([Vector2(0, tab_h), Vector2(0, 4), Vector2(4, 0), Vector2(tab_w - 12, 0), Vector2(tab_w, tab_h)])
	var sh := PackedVector2Array()
	for p in tab:
		sh.append(p + shadow)
	folder.draw_colored_polygon(sh, Palette.SHADOW)
	folder.draw_rect(Rect2(body.position + shadow, body.size), Palette.SHADOW)
	folder.draw_colored_polygon(tab, Palette.NOTE_PAPER)
	folder.draw_rect(body, Palette.PAPER)
	folder.draw_polyline(tab, edge_color(), edge_width())
	folder.draw_rect(body, edge_color(), false, edge_width())
	folder.draw_string(Palette.mono(), Vector2(UiTheme.SP_S, tab_h * 0.72), tr("SLOT %s") % slot, HORIZONTAL_ALIGNMENT_LEFT, tab_w, UiTheme.font_px(UiTheme.CAPTION), Palette.INK)
	# The corporation: hue stripe with its pattern, and its landmark glyph.
	var corp := _corp_id()
	var col := Palette.corp_color(corp)
	var stripe := Rect2(body.position, Vector2(STRIPE_W * s, body.size.y))
	folder.draw_rect(stripe, col)
	CorpPattern.fill_rect(folder, stripe, Palette.corp_pattern_id(corp), Palette.INK)
	var path := SvgArt.landmark_path(corp)
	if path != "":
		var side := LANDMARK * s
		var tex := SvgArt.texture(path, side)
		var at := Rect2(Vector2(sz.x - side - UiTheme.SP_S, tab_h + UiTheme.SP_S), Vector2(side, side))
		folder.draw_circle(at.get_center(), side * 0.56, Palette.INK)
		if tex != null:
			folder.draw_texture_rect(tex, at, false, col)


## The folder's edge (§12: opaque INK, PaperInk.EDGE_PX, in high contrast).
func edge_color() -> Color:
	return PaperInk.edge(Color(Palette.INK, EDGE_ALPHA))


## The folder's edge width (px).
func edge_width() -> float:
	return PaperInk.edge_width(1.0)


func _dashed(r: Rect2, col: Color) -> void:
	var pts := [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y), r.position]
	for i in 4:
		folder.draw_dashed_line(pts[i], pts[i + 1], col, 1.0, DASH)
