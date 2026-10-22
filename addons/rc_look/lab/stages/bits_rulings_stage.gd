extends RcLookLabStage
## LOOK-TOOLBOX module 16: the rulings sheet. Bits run through two systems (the GPU BinaryBits / BitsPath and the CPU
## combat BitPath / BitsSeam) that look different in five ways; each row shows one difference as two panels, A | B, drawn
## by one routine from RcLookBits' plan and RcLookBitsPreset, so the only change between the panels is the ruling.
## The lab decides nothing: the designer picks per ruling (README "Open rulings"). Glyphs are drawn as text with a
## rim (BitsSeam's way) in normal blend for both panels, so the comparison is the ruling alone; the game's GPU bits use
## the baked atlas in additive blend, which reads slightly brighter. Run as `--module=bits_rulings`. View only.

## Layout (px): margins, gap between the two panels, the label size.
const MARGIN := Vector2(40.0, 50.0)
const GAP := 16.0
const ROW_GAP := 34.0
const LABEL_SIZE := 13
## A bit's age in the hot row as a share of the hot time (0: fully hot), in the pure-colour rows (s), and the spin row's clock (s).
const HOT_AGE_SHARE := 0.0
const PURE_AGE := 1.0
const SPIN_CLOCK := 0.06

## The rows: title, the two captions, the two preset edits [preset, field, value], mode ("grid" or "flight").
## Each side starts from a shipped preset (base_a / base_b) with the listed fields set.
var _rows: Array[Dictionary] = []
var _views: Array[Control] = []


func _ready() -> void:
	_rows = [
		{"title": "1  Hot colour: the first 0.08 s of a bit", "a": "A: WHITE_HOT (GPU bits, CPU fallback)", "b": "B: PAPER #F2EEE4 (BitsSeam, streams)",
			"base_a": &"wheel", "base_b": &"seam", "edit_a": {}, "edit_b": {"outline": 0, "life": 0, "spin_phase": true}, "mode": &"grid",
			"clock": 0.0, "age": HOT_AGE_SHARE * RcLookBitsView.HOT_S, "split": false},
		{"title": "2  Outline: same colour as the bit, or a NIGHT_SKY rim (shown on dark and on light)", "a": "A: same-colour outline (the atlas)",
			"b": "B: NIGHT_SKY rim at 95 % (BitsSeam)", "base_a": &"wheel", "base_b": &"wheel", "edit_a": {}, "edit_b": {"outline": 1},
			"mode": &"grid", "clock": 0.0, "age": PURE_AGE, "split": true},
		{"title": "3  Life in flight: flip 0 / 1 and tumble, or a steady glyph with a trail copy", "a": "A: flip + tumble (GPU)",
			"b": "B: trail copy, no tumble (BitsSeam)", "base_a": &"wheel", "base_b": &"wheel", "edit_a": {}, "edit_b": {"life": 1},
			"mode": &"flight", "clock": -1.0, "age": -1.0, "split": false},
		{"title": "4  Spin phase: each bit's tumble starts at its flip phase x a turn (GPU) or all start upright (CPU fallback today)",
			"a": "A: phase offset (GPU shader)", "b": "B: no offset (CPU fallback today)", "base_a": &"wheel", "base_b": &"cpu",
			"edit_a": {}, "edit_b": {}, "mode": &"grid", "clock": SPIN_CLOCK, "age": PURE_AGE, "split": false},
		{"title": "5  A turn: 6.28 (today, bit-exact) or TAU", "a": "A: 6.28", "b": "B: TAU = 6.2831853", "base_a": &"wheel", "base_b": &"wheel",
			"edit_a": {}, "edit_b": {"spin_turn": TAU}, "mode": &"grid", "clock": SPIN_CLOCK, "age": PURE_AGE, "split": false},
	]
	var view := get_viewport_rect().size
	var panel_w := (view.x - MARGIN.x * 2.0 - GAP) / 2.0
	var panel_h := (view.y - MARGIN.y - 20.0 - ROW_GAP * _rows.size()) / _rows.size()
	for r in _rows.size():
		var row := _rows[r]
		var y := MARGIN.y + r * (panel_h + ROW_GAP)
		_label(String(row["title"]), Vector2(MARGIN.x, y - LABEL_SIZE - 6.0))
		for side in 2:
			var key := "a" if side == 0 else "b"
			var v := RcLookBitsView.new()
			v.position = Vector2(MARGIN.x + side * (panel_w + GAP), y)
			v.size = Vector2(panel_w, panel_h)
			v.preset = _preset(StringName(row["base_" + key]), row["edit_" + key])
			v.mode = row["mode"]
			v.clock_s = float(row["clock"])
			v.age_s = float(row["age"])
			v.split = bool(row["split"])
			add_child(v)
			_views.append(v)
			_label(String(row[key]), Vector2(v.position.x, y + panel_h + 1.0), 11)
	var turn_deg := rad_to_deg(TAU - RcLookBits.preset(&"wheel").spin_turn)
	_label("Row 5: the two turns differ by %.3f degrees at most (phase 1.0), %.3f px at the rim of a %.0f px glyph: invisible." % [
			turn_deg, deg_to_rad(turn_deg) * RcLookBitsView.GLYPH_PX * 0.5, RcLookBitsView.GLYPH_PX], Vector2(MARGIN.x, view.y - 20.0), 11)


func apply(_time: StringName, _quality: RcLookQualityState) -> void:
	for v in _views:
		v.queue_redraw()


## A copy of a shipped preset with fields set (enum ints and values).
static func _preset(base: StringName, edit: Dictionary) -> RcLookBitsPreset:
	var p := RcLookBits.preset(base).duplicate() as RcLookBitsPreset
	for k: String in edit:
		p.set(k, edit[k])
	return p


func _label(text: String, at: Vector2, size: int = LABEL_SIZE) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", size)
	add_child(l)


