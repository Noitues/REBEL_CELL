class_name RunReceipt
extends Button
## Parity STATS-01 (designer group ruling 2026-10-05: the build reworked in v2): one run of the
## history as a paper run card, ported from art-m13-final `scripts/ui/kit/run_receipt.gd` (the
## build's taped till receipt). In the v2 kit it is paper (the art pass's paper stock, the
## corp_paper shader) with a strip of tape and a torn foot: the corporation in Anton, the tier
## and Site typed in Courier Prime, a rule, the outcome as a rubber-stamp word (HARM for a
## flatline, GAIN for a clean exit) and Cycles earned / banked typed by their StatIcons.
## `empty()` is the designed "no runs yet" slip. A focus stop (the pad walks the cards: the
## sheet scrolls to them). View only.

## The card's width at text scale 1.0 (px), its pads, the torn foot's tooth, the tape's size
## and tilt, and the tilt step between cards (deg).
const WIDTH := 190.0
const PAD := Vector2(10, 12)
const TOOTH := 6.0
const TAPE := Vector2(46, 12)
const TAPE_TILT := -0.06
const TILT_STEP := 1.5
const SHADOW_OFFSET := Vector2(3, 4)
## The paper's ink edge alpha (opaque in high contrast), and how far GAIN is darkened to read
## as ink on the paper (a clean exit's stamp).
const EDGE_ALPHA := 0.35
const STAMP_DARKEN := 0.45
const PAPER_SHADER := preload("res://shaders/kit/corp_paper.gdshader")
## The outcomes the stamp colours (run_history "outcome", RunState.Outcome lower-cased) and
## the stamp's words (keys).
const OUTCOME_DIED := "died"
const OUTCOMES := ["completed", "died", "aborted", "none"]
const OUTCOME_WORDS := ["Completed", "Died", "Aborted", "Unfinished"] # TR
## The empty slip's words (keys).
const EMPTY_WORDS := ["NO RUNS YET", "Jack in from the HQ: each run you finish prints a card here."] # TR

var lines: VBoxContainer
var tilt: float = 0.0
var _paper: Control
var _marks: Control
var _mat: ShaderMaterial


func _init(p_tilt: float = 0.0) -> void:
	name = "Receipt"
	tilt = p_tilt
	focus_mode = Control.FOCUS_ALL
	set_meta(UiFocus.META_NO_SCALE, true)
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]:
		add_theme_stylebox_override(box, StyleBoxEmpty.new())
	_mat = ShaderMaterial.new()
	_mat.shader = PAPER_SHADER
	_paper = Control.new()
	_paper.name = "Paper"
	_paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_paper.material = _mat
	_paper.draw.connect(_draw_paper)
	add_child(_paper)
	lines = VBoxContainer.new()
	lines.name = "Lines"
	lines.mouse_filter = Control.MOUSE_FILTER_IGNORE
	lines.add_theme_constant_override("separation", 0)
	add_child(lines)
	_marks = Control.new()
	_marks.name = "Marks"
	_marks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_marks.draw.connect(_draw_marks)
	add_child(_marks)
	for c in [_paper, _marks]:
		(c as Control).set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	lines.set_anchors_preset(Control.PRESET_FULL_RECT)
	lines.offset_left = PAD.x
	lines.offset_top = PAD.y
	lines.offset_right = -PAD.x
	lines.offset_bottom = -(PAD.y + TOOTH)
	lines.minimum_size_changed.connect(_refit)
	resized.connect(_place)
	focus_entered.connect(_marks.queue_redraw)
	focus_exited.connect(_marks.queue_redraw)
	_refit()


func _ready() -> void:
	pivot_offset = Vector2(size.x * 0.5, 0)
	rotation_degrees = tilt


## The card's text width (px).
static func text_width() -> float:
	return WIDTH * Settings.text_scale - PAD.x * 2.0


## Adds a line of ink text in `font` (Courier Prime unless given) at `step`; "-" is a rule.
func line(words: String, step: int = UiTheme.BODY, font: Font = null, col: Color = Palette.PAPER_TYPE_INK) -> Label:
	var l := Label.new()
	l.text = words if words != "-" else "- - - - - - - - - -"
	l.add_theme_font_override(&"font", font if font != null else Chrome.paper_font())
	l.add_theme_font_size_override(&"font_size", Chrome.px(step))
	l.add_theme_color_override(&"font_color", col)
	UiWrap.whole_words(l)
	l.custom_minimum_size.x = text_width()
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	lines.add_child(l)
	return l


## Adds numbers, each after its StatIcon (Cycles, banked), typed on one line.
func fields(items: Array) -> void:
	var row := HFlowContainer.new()
	row.name = "Fields"
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("h_separation", UiTheme.SP_M)
	for it in items:
		var f := HBoxContainer.new()
		f.mouse_filter = Control.MOUSE_FILTER_IGNORE
		f.tooltip_text = TranslationServer.translate(String(StatIcon.NAMES.get(it[0], String(it[0]))))
		var icon := Control.new()
		var px := Chrome.px(UiTheme.BODY)
		icon.custom_minimum_size = Vector2.ONE * px
		icon.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var kind: StringName = it[0]
		icon.draw.connect(func() -> void: StatIcon.draw(icon, icon.size * 0.5, icon.size.y * 0.45, kind, Palette.INK))
		f.add_child(icon)
		var v := Label.new()
		v.text = str(it[1])
		v.add_theme_font_override(&"font", Chrome.paper_bold_font())
		v.add_theme_font_size_override(&"font_size", px)
		v.add_theme_color_override(&"font_color", Palette.PAPER_TYPE_INK)
		v.mouse_filter = Control.MOUSE_FILTER_IGNORE
		f.add_child(v)
		row.add_child(f)
	lines.add_child(row)


## A card for one run_history entry (`corp_name` translated by the caller).
static func of_run(r: Dictionary, corp_name: String, index: int) -> RunReceipt:
	var card := RunReceipt.new(TILT_STEP * (1 if index % 2 == 0 else -1))
	card.name = "Receipt%d" % index
	card.line(corp_name.to_upper(), UiTheme.LABEL, Palette.display(), Palette.INK)
	card.line("T%d  %s" % [int(r.get("tier", 1)), String(r.get("site", "?"))])
	card.line("-")
	var outcome := String(r.get("outcome", "?"))
	var at := OUTCOMES.find(outcome)
	var word: String = String(TranslationServer.translate(String(OUTCOME_WORDS[at]))) if at >= 0 else outcome
	card.line(word.to_upper(), UiTheme.LABEL, Palette.display(), Palette.HARM if outcome == OUTCOME_DIED else Palette.GAIN.darkened(STAMP_DARKEN))
	card.fields([[StatIcon.CYCLES, int(r.get("cycles", 0))], [StatIcon.BANKED, int(r.get("banked", 0))]])
	card.tooltip_text = UiTip.fold("%s T%d %s: %s" % [corp_name, int(r.get("tier", 1)), String(r.get("site", "?")), word])
	return card


## The designed empty state: a blank slip that says what fills it.
static func empty() -> RunReceipt:
	var card := RunReceipt.new(-TILT_STEP)
	card.name = "NoRuns"
	card.line(TranslationServer.translate(EMPTY_WORDS[0]), UiTheme.LABEL, Palette.display(), Palette.INK)
	card.line("-")
	card.line(TranslationServer.translate(EMPTY_WORDS[1]), UiTheme.CAPTION)
	return card


## Every word on the card (tests).
func words() -> PackedStringArray:
	var out := PackedStringArray()
	for l in lines.find_children("*", "Label", true, false):
		out.append((l as Label).text)
	return out


func _refit() -> void:
	var m := lines.get_combined_minimum_size()
	custom_minimum_size = Vector2(WIDTH * Settings.text_scale, ceilf(m.y + PAD.y * 2.0 + TOOTH))


## The card's paper takes its new size (the lines, paper and marks follow by their anchors).
func _place() -> void:
	_mat.set_shader_parameter(&"panel", Vector4(0, 0, size.x, size.y))
	_mat.set_shader_parameter(&"stock", Palette.PAPER)
	_mat.set_shader_parameter(&"fibre", Palette.KRAFT_FIBRE)
	_mat.set_shader_parameter(&"seed", float(get_index()))
	pivot_offset = Vector2(size.x * 0.5, 0)
	_paper.queue_redraw()
	_marks.queue_redraw()
	queue_redraw()


## The card's outline with its torn foot (local).
func outline() -> PackedVector2Array:
	var w := size.x
	var h := size.y - TOOTH
	var pts := PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, h)])
	var n := maxi(2, int(w / (TOOTH * 2.0)))
	for i in range(n, -1, -1):
		pts.append(Vector2(w * i / n, h + (TOOTH if i % 2 == 1 else 0.0)))
	return pts


func _draw_paper() -> void:
	_paper.draw_colored_polygon(outline(), Palette.NO_TINT)


## The shadow under the paper (the card's own layer, under its children).
func _draw() -> void:
	var shadow := PackedVector2Array()
	for p in outline():
		shadow.append(p + SHADOW_OFFSET)
	draw_colored_polygon(shadow, Palette.SHADOW)


## Over the paper and its words: the ink edge, the tape and the focus brackets.
func _draw_marks() -> void:
	var pts := outline()
	var edge := Palette.INK if Settings.high_contrast else Color(Palette.INK, EDGE_ALPHA)
	_marks.draw_polyline(pts + PackedVector2Array([pts[0]]), edge, 2.0 if Settings.high_contrast else 1.0)
	_marks.draw_set_transform(Vector2(size.x * 0.5 - TAPE.x * 0.5, -TAPE.y * 0.5), TAPE_TILT, Vector2.ONE)
	_marks.draw_rect(Rect2(Vector2.ZERO, TAPE), Palette.NOTE_TAPE)
	_marks.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	if has_focus():
		StyleBoxBrackets.draw_on(_marks, Rect2(Vector2.ZERO, size))
