class_name RcLookBitsView
extends Control
## LOOK-TOOLBOX module 16: one lab panel of bits: RcLookBits' plan drawn at a clock under an RcLookBitsPreset, as text
## glyphs with a rim (BitsSeam's way, normal blend, so panels compare the preset alone; the game's GPU bits use the
## atlas in additive blend). `grid` draws the bits at rest (hot colour, outline, spin), `flight` along their paths.
## The dark half and, when `split`, a light half. Lab only; view only.

const BITS := 28
const SEED := 11
const BIT_COLORS: Array[Color] = [Color(1.0, 0.24, 0.66), Color(0.25, 0.85, 1.0)]
const GLYPH_PX := 30.0
const DARK := Color(0.02, 0.025, 0.05)
const LIGHT := Color(0.52, 0.5, 0.46)
## The flight's seconds and spawn spread (bits_flight today), the hot time (s).
const FLIGHT_S := 0.55
const SPREAD_S := 0.12
const HOT_S := 0.08

var preset: RcLookBitsPreset
var mode: StringName = &"grid"
## The clock (s); below 0 it is `clock_share` of the last arrival (flight). `age_s` below 0 is each bit's own age.
var clock_s: float = 0.0
var clock_share: float = 0.55
var age_s: float = 0.0
var split: bool = false
## How many bits and how big (px): the sheets with narrow panels use fewer and smaller.
var bits: int = BITS
var glyph_px: float = GLYPH_PX


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
			starts = BitsPath.points_in_rect(Rect2(area.position + area.size * 0.06, area.size * 0.88), bits)
		else:
			starts = BitsPath.points_in_rect(Rect2(area.position + area.size * Vector2(0.06, 0.15), area.size * Vector2(0.25, 0.7)), bits)
		var path_rim := radius if preset.path == RcLookBitsPreset.Path.RIM else 0.0
		var plan := RcLookBits.plan(starts, target, FLIGHT_S, SPREAD_S, SEED, target, path_rim)
		var clock := clock_s if clock_s >= 0.0 else clock_share * float(RcLookBits.arrivals(plan)[plan.size() - 1])
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
			var px := maxi(cfg.min_px, roundi(glyph_px * RcLookBits.scale_at(t)))
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
