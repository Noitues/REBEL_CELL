class_name RunReceipt
extends MarginContainer
## One run in the history as a taped till receipt (ART_BIBLE §11 Stats and achievements: "run
## history as taped receipts"): a narrow PAPER slip with a torn zig-zag foot and a strip of
## tape, mono INK lines (the corporation and tier, the Site, the outcome as a stamp word,
## Cycles earned and banked by their icons). `empty()` makes the designed "no runs yet"
## slip (critique 18: not a big empty sheet). Sized to its lines. View only.

## The slip's width at text scale 1.0 (px), the zig-zag's tooth and the tape's size.
const WIDTH := 190.0
const TOOTH := 6.0
const TAPE := Vector2(46, 12)
const TILT_STEP := 1.5
## The slip's ink edge alpha (opaque in high contrast).
const EDGE_ALPHA := 0.35

var lines: VBoxContainer
var tilt: float = 0.0


func _init(p_tilt: float = 0.0) -> void:
	name = "Receipt"
	tilt = p_tilt
	var s := Settings.text_scale
	custom_minimum_size.x = WIDTH * s
	add_theme_constant_override("margin_left", UiTheme.SP_S)
	add_theme_constant_override("margin_right", UiTheme.SP_S)
	add_theme_constant_override("margin_top", UiTheme.SP_M)
	add_theme_constant_override("margin_bottom", UiTheme.SP_M + roundi(TOOTH))
	mouse_filter = Control.MOUSE_FILTER_PASS
	lines = VBoxContainer.new()
	lines.name = "Lines"
	lines.add_theme_constant_override("separation", 0)
	lines.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(lines)


func _ready() -> void:
	pivot_offset = Vector2(size.x * 0.5, 0)
	rotation_degrees = tilt


## Adds a line of mono INK text at `step` (a rule of dashes when `words` is "-").
func line(words: String, step: int = UiTheme.BODY, font: Font = null) -> Label:
	var l := Label.new()
	l.text = words if words != "-" else "- - - - - - - - - -"
	l.add_theme_font_override("font", font if font != null else Palette.mono())
	l.add_theme_font_size_override("font_size", UiTheme.font_px(step))
	UiTheme.track_label(l)  # art pass W9F (§4.2): Anton and mono CAPS tracked
	l.add_theme_color_override("font_color", PaperInk.text(Palette.INK))
	UiWrap.whole_words(l)  # art pass W9F §4.3.3: whole words, never mid-word
	# Wrapped at the slip's width from the start (never measured at width 0).
	l.custom_minimum_size.x = WIDTH * Settings.text_scale - UiTheme.SP_S * 2
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	lines.add_child(l)
	return l


## Adds numbers each after its icon (Cycles, banked) on one line.
func fields(items: Array) -> void:
	var row := HFlowContainer.new()
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	row.add_theme_constant_override("h_separation", UiTheme.SP_M)
	for it in items:
		row.add_child(StatField.new(it[0], str(it[1]), UiTheme.font_px(UiTheme.BODY), Palette.INK))
	lines.add_child(row)


## A receipt for one run_history entry (`corp_name` translated by the caller).
static func of_run(r: Dictionary, corp_name: String, index: int) -> RunReceipt:
	var slip := RunReceipt.new(TILT_STEP * (1 if index % 2 == 0 else -1))
	slip.name = "Receipt%d" % index
	slip.line(corp_name.to_upper(), UiTheme.BODY, Palette.display())
	slip.line("T%d  %s" % [int(r.get("tier", 1)), String(r.get("site", "?"))])
	slip.line("-")
	slip.line(String(r.get("outcome", "?")).to_upper(), UiTheme.LABEL, Palette.display())
	slip.fields([[StatIcon.CYCLES, int(r.get("cycles", 0))], [StatIcon.BANKED, int(r.get("banked", 0))]])
	return slip


## The designed empty state: a blank slip that says what fills it (critique 18).
static func empty() -> RunReceipt:
	var slip := RunReceipt.new(-TILT_STEP)
	slip.name = "NoRuns"
	slip.line(TranslationServer.translate("NO RUNS YET"), UiTheme.LABEL, Palette.display())
	slip.line("-")
	slip.line(TranslationServer.translate("Jack in from the HQ: each run you finish prints a receipt here."), UiTheme.CAPTION)
	return slip


## The slip's edge (§12: opaque INK, PaperInk.EDGE_PX, in high contrast).
func edge_color() -> Color:
	return PaperInk.edge(Color(Palette.INK, EDGE_ALPHA))


## The slip's edge width (px).
func edge_width() -> float:
	return PaperInk.edge_width(1.0)


func _draw() -> void:
	var w := size.x
	var h := size.y - TOOTH
	var pts := PackedVector2Array([Vector2(0, 0), Vector2(w, 0), Vector2(w, h)])
	var n := maxi(2, int(w / (TOOTH * 2.0)))
	for i in range(n, -1, -1):
		pts.append(Vector2(w * i / n, h + (TOOTH if i % 2 == 1 else 0.0)))
	var shadow := PackedVector2Array()
	for p in pts:
		shadow.append(p + Vector2(3, 4))
	draw_colored_polygon(shadow, Palette.SHADOW)
	draw_colored_polygon(pts, Palette.PAPER)
	draw_polyline(pts + PackedVector2Array([pts[0]]), edge_color(), edge_width())
	draw_set_transform(Vector2(w * 0.5 - TAPE.x * 0.5, -TAPE.y * 0.5), -0.06, Vector2.ONE)
	draw_rect(Rect2(Vector2.ZERO, TAPE), PaperInk.opaque(Palette.NOTE_TAPE))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
