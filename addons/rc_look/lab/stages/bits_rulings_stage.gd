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
## The bits: how many, the seed, the colour, their glyph size (px), the dark and the light backdrop.
const BITS := 28
const SEED := 11
const BIT_COLORS: Array[Color] = [Color(1.0, 0.24, 0.66), Color(0.25, 0.85, 1.0)]
const GLYPH_PX := 30.0
const DARK := Color(0.02, 0.025, 0.05)
const LIGHT := Color(0.52, 0.5, 0.46)
## A bit's age in the hot row as a share of the hot time (0: fully hot), in the pure-colour rows (s), and the spin row's clock (s).
const HOT_AGE_SHARE := 0.0
const PURE_AGE := 1.0
const SPIN_CLOCK := 0.06
## The flight row's clock as a share of the last arrival; the flight's seconds and spread (bits_flight today).
const FLIGHT_SHARE := 0.55
const FLIGHT_S := 0.55
const SPREAD_S := 0.12
const HOT_S := 0.08

## The rows: title, the two captions, the two preset edits [preset, field, value], mode ("grid" or "flight").
## Edits: "w" starts from the wheel preset, "c" from cpu, "s" from stream.
var _rows: Array[Dictionary] = []
var _views: Array[Control] = []


func _ready() -> void:
	_rows = [
		{"title": "1  Hot colour: the first 0.08 s of a bit", "a": "A: WHITE_HOT (GPU bits, CPU fallback)", "b": "B: PAPER #F2EEE4 (BitsSeam, streams)",
			"base_a": &"wheel", "base_b": &"stream", "edit_a": {}, "edit_b": {"outline": 0, "life": 0, "spin_phase": true}, "mode": &"grid",
			"clock": 0.0, "age": HOT_AGE_SHARE * HOT_S, "split": false},
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
			var v := _Ruling.new()
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
			turn_deg, deg_to_rad(turn_deg) * GLYPH_PX * 0.5, GLYPH_PX], Vector2(MARGIN.x, view.y - 20.0), 11)


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


## One panel: the plan drawn at a clock under a preset.
class _Ruling extends Control:
	var preset: RcLookBitsPreset
	var mode: StringName = &"grid"
	var clock_s: float = 0.0
	var age_s: float = 0.0
	var split: bool = false

	func _draw() -> void:
		var cfg := RcLookBits.default_config()
		var font := Palette.mono()
		var halves := 2 if split else 1
		for h in halves:
			var bg := DARK if h == 0 else LIGHT
			var area := Rect2(Vector2(size.x * h / halves, 0.0), Vector2(size.x / halves, size.y))
			draw_rect(area, bg)
			var starts: PackedVector2Array
			var target := area.position + Vector2(area.size.x * 0.75, area.size.y * 0.5)
			var radius := area.size.y * 0.3
			if mode == &"grid":
				starts = BitsPath.points_in_rect(Rect2(area.position + area.size * 0.06, area.size * 0.88), BITS)
			else:
				starts = BitsPath.points_in_rect(Rect2(area.position + area.size * Vector2(0.06, 0.15), area.size * Vector2(0.25, 0.7)), BITS)
			var plan := RcLookBits.plan(starts, target, FLIGHT_S, SPREAD_S, SEED, target, radius)
			var clock := clock_s if clock_s >= 0.0 else FLIGHT_SHARE * float(RcLookBits.arrivals(plan)[plan.size() - 1])
			for i in plan.size():
				var b: Dictionary = plan[i]
				var col := BIT_COLORS[i % BIT_COLORS.size()]
				var age := age_s if age_s >= 0.0 else clock - float(b["delay"])
				var t := 0.0
				var pos: Vector2 = b["start"]
				if mode == &"flight":
					t = (clock - float(b["delay"])) / float(b["flight"])
					if clock < float(b["delay"]) or t >= 1.0:
						continue
					pos = RcLookBits.at(b["start"], b["ctrl"], target, RcLookBits.eased(t))
				var px := maxi(cfg.min_px, roundi(GLYPH_PX * RcLookBits.scale_at(t)))
				var phase: float = b["phase"]
				var glyph: String
				var angle := 0.0
				if preset.life == RcLookBitsPreset.Life.FLIP_TUMBLE:
					var fa := (clock - float(b["delay"])) if mode == &"flight" else clock
					glyph = str(RcLookBits.flip_frame(fa, cfg.flip_seconds, phase))
					angle = RcLookBits.spin_angle(clock, b["spin"], phase, preset.spin_turn, preset.spin_phase)
				else:
					glyph = "1" if phase > 0.5 else "0"
					if mode == &"flight" and clock - cfg.trail_lag > float(b["delay"]):
						var tb := (clock - cfg.trail_lag - float(b["delay"])) / float(b["flight"])
						var back := RcLookBits.at(b["start"], b["ctrl"], target, RcLookBits.eased(tb))
						_glyph(font, back, 0.0, glyph, px, Color(col, cfg.trail_alpha), Color(col, 0.0), 0)
				var hot_col := RcLookBits.bit_color(preset.hot_color, col, age, HOT_S)
				var rim_w := maxi(cfg.rim_px, roundi(px * cfg.outline_share) + cfg.rim_px - 1)
				var rim := Color(hot_col, 1.0) if preset.outline == RcLookBitsPreset.Outline.SAME_COLOUR \
						else Color(Palette.NIGHT_SKY, cfg.rim_alpha)
				_glyph(font, pos, angle, glyph, px, hot_col, rim, rim_w)
		draw_set_transform(Vector2.ZERO, 0.0)

	func _glyph(font: Font, at: Vector2, angle: float, glyph: String, px: int, col: Color, rim: Color, rim_w: int) -> void:
		draw_set_transform(at, angle)
		var base := Vector2(-px * 0.3, px * 0.35)
		if rim_w > 0:
			draw_char_outline(font, base, glyph, px, rim_w, rim)
		draw_char(font, base, glyph, px, col)
		draw_set_transform(Vector2.ZERO, 0.0)
