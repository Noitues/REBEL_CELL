class_name RunLogRow
extends Button
## B5 (integration review section c / f: "Run history on paper receipts is wrong, because they are the Cell's records:
## make them terminal log rows, Anton outcome word on a sticker only for FLATLINED or COMPLETED"; round 44 B_menus
## `stats.png`): one run of the history as a row of the Cell's terminal log: the target (its crest and name), the run
## (tier and Site), the Cycles earned (+n), the Schematics banked, and the outcome: COMPLETED and FLATLINED as a small
## Anton sticker (fixed facts of a finished run), the rest a mono word. `header()` is the columns' names row and
## `empty()` the designed "no runs yet" line. A focus stop (MenuItem: the cyan wash, the lime brackets and the
## caret); the pad walks the rows. View only.

## Column widths (shares of the row: target, run, cycles, banked, outcome) and the crest's size (px at 1.0).
const COLUMNS: Array[float] = [0.26, 0.24, 0.14, 0.12, 0.24]
const CREST := 16.0
## The outcome sticker's lettering (px at 1.0) and tilt.
const STICKER_PX := 16.0
const STICKER_TILT := -2.0
## The run_history outcomes (RunState.Outcome lower-cased) and their words (keys); the two that get a sticker.
const OUTCOMES := ["completed", "died", "aborted", "none"]
const OUTCOME_WORDS := ["COMPLETED", "FLATLINED", "JACKED OUT", "UNFINISHED"] # TR
const STICKER_OUTCOMES := ["completed", "died"]
const HEADER_WORDS := ["TARGET", "RUN", "CYCLES", "BANKED", "OUTCOME"] # TR
const EMPTY_WORDS := ["NO RUNS YET", "jack in from the HQ: each run you finish logs a line here"] # TR
## The row's height (px at 1.0).
const ROW_H := 30.0

var cells: HBoxContainer
var outcome: String = ""
## The outcome's sticker (COMPLETED / FLATLINED), null otherwise.
var sticker: VerbSticker = null


func _init() -> void:
	name = "RunRow"
	focus_mode = Control.FOCUS_ALL
	theme_type_variation = &"MenuItem"
	set_meta(UiFocus.META_NO_SCALE, true)
	custom_minimum_size.y = ROW_H * Settings.text_scale
	cells = HBoxContainer.new()
	cells.name = "Cells"
	cells.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cells.add_theme_constant_override(&"separation", 0)
	add_child(cells)
	cells.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	cells.offset_left = UiTheme.SP_L


## One run_history entry `r` (`corp_name` translated by the caller), the row `index` (its seed).
static func of_run(r: Dictionary, corp_name: String, index: int) -> RunLogRow:
	var row := RunLogRow.new()
	row.name = "Run%d" % index
	var corp := StringName(String(r.get("corporation", "")))
	row._crest_cell(corp, corp_name.to_upper())
	row._cell("T%d  %s" % [int(r.get("tier", 1)), String(r.get("site", "?"))], Palette.TEXT_HI)
	row._cell("+%d" % int(r.get("cycles", 0)), Palette.GAIN)
	row._cell(str(int(r.get("banked", 0))), Palette.RESIST_GOLD)
	row.outcome = String(r.get("outcome", "?"))
	var at := OUTCOMES.find(row.outcome)
	var word: String = TranslationServer.translate(String(OUTCOME_WORDS[at])) if at >= 0 else row.outcome.to_upper()
	if row.outcome in STICKER_OUTCOMES:
		row._sticker_cell(word, row.outcome == "died")
	else:
		row._cell(word, Palette.TEXT_MID)
	row.tooltip_text = UiTip.fold("%s T%d %s: %s" % [corp_name, int(r.get("tier", 1)), String(r.get("site", "?")), word])
	return row


## The columns' names (not a focus stop).
static func header() -> RunLogRow:
	var row := RunLogRow.new()
	row.name = "RunHeader"
	row.focus_mode = Control.FOCUS_NONE
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.theme_type_variation = &""
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]:
		row.add_theme_stylebox_override(box, StyleBoxEmpty.new())
	for w in HEADER_WORDS:
		row._cell(TranslationServer.translate(w), Palette.TEXT_LO, UiTheme.CAPTION, true)
	return row


## The designed empty state: one log line that says what fills it.
static func empty() -> RunLogRow:
	var row := RunLogRow.new()
	row.name = "NoRuns"
	row._cell(TranslationServer.translate(EMPTY_WORDS[0]), Palette.TEXT_HI, UiTheme.BODY, true, 0.3)
	row._cell(TranslationServer.translate(EMPTY_WORDS[1]), Palette.TEXT_MID, UiTheme.CAPTION, false, 0.7)
	return row


## Every word on the row (tests).
func words() -> PackedStringArray:
	var out := PackedStringArray()
	for l in cells.find_children("*", "Label", true, false):
		out.append((l as Label).text)
	if sticker != null:
		out.append(sticker.shown_text())
	return out


func _slot(share: float) -> HBoxContainer:
	var box := HBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	box.size_flags_stretch_ratio = share
	box.add_theme_constant_override(&"separation", UiTheme.SP_XS)
	box.alignment = BoxContainer.ALIGNMENT_BEGIN
	cells.add_child(box)
	return box


func _cell(words: String, col: Color, step: int = UiTheme.BODY, caps: bool = false, share: float = -1.0) -> Label:
	var box := _slot(share if share > 0.0 else COLUMNS[mini(cells.get_child_count(), COLUMNS.size() - 1)])
	var l := Label.new()
	l.text = words
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.add_theme_font_override(&"font", Chrome.caps_font(step) if caps else Palette.mono())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(step))
	l.add_theme_color_override(&"font_color", col)
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	l.clip_text = true
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(l)
	return l


func _crest_cell(corp: StringName, words: String) -> void:
	var box := _slot(COLUMNS[0])
	var crest := Control.new()
	crest.name = "Crest"
	crest.custom_minimum_size = Vector2.ONE * CREST * minf(Settings.text_scale, CodexBook.GLYPH_SCALE_MAX)
	crest.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	crest.mouse_filter = Control.MOUSE_FILTER_IGNORE
	crest.draw.connect(func() -> void: CorpSeal.draw_crest(crest, crest.size * 0.5, crest.size.x * 0.5, corp, Palette.corp_color(corp)))
	box.add_child(crest)
	var l := Label.new()
	l.text = words
	l.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	l.add_theme_font_override(&"font", Palette.mono())
	l.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.BODY))
	l.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	l.clip_text = true
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(l)


## COMPLETED (yellow vinyl) / FLATLINED (red vinyl): a small Anton sticker, not a focus stop of its own.
func _sticker_cell(word: String, harm: bool) -> void:
	var box := _slot(COLUMNS[4])
	sticker = VerbSticker.new(word, VerbSticker.Fill.RED if harm else VerbSticker.Fill.YELLOW, STICKER_PX, STICKER_TILT)
	sticker.name = "Outcome"
	sticker.pre_translated = true
	sticker.focus_mode = Control.FOCUS_NONE
	sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sticker.ambient_sweep = false  # a record, never the page's verb
	sticker.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	box.add_child(sticker)
	custom_minimum_size.y = maxf(custom_minimum_size.y, sticker.get_combined_minimum_size().y)
