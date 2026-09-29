// Marker stroke (PAPER, ART_BIBLE 6.6, 13): a hand-drawn marker line that draws itself on,
// from a signed-distance shape, for stamps, circled items and strike-throughs. Put it on
// a ColorRect sized to the mark and set `size_px` to that size. `shape`: 0 a loop circling
// the rect (an ellipse that overshoots its start like a hand-drawn ring), 1 a stamp's box
// frame, 2 an underline / strike-through along the middle. `progress` 0..1 is the share of
// the stroke drawn (the view tweens it; the end state is 1). The line wobbles a little
// from value noise and its ink streaks along its length. Reduce effects: the ink's "boil"
// (the wobble re-drawn `boil_fps` times a second) stops; the stroke holds still.
shader_type canvas_item;
// Reduce effects (rc_common): no boil.
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int shape : hint_range(0, 2) = 0;
uniform float progress : hint_range(0.0, 1.0) = 1.0;
// The mark's size in px (the view sets it), the stroke's width and wobble (px).
uniform vec2 size_px = vec2(160.0, 160.0);
uniform float width_px : hint_range(1.0, 24.0) = 6.0;
uniform float wobble_px : hint_range(0.0, 8.0) = 2.0;
// Where a loop or frame starts (turns from the right, clockwise) and how far a loop runs
// past its start (a share of a turn).
uniform float start_turn : hint_range(0.0, 1.0) = 0.35;
uniform float overshoot : hint_range(0.0, 0.3) = 0.08;
// Wobble re-draws per second while effects play (0 = never).
uniform float boil_fps : hint_range(0.0, 12.0) = 0.0;
uniform vec4 ink : source_color = vec4(1.0, 0.24, 0.66, 1.0);

// Noise scale of the wobble (per px) and the streak texture along the stroke.
const float WOBBLE_SCALE = 0.045;
const float STREAKS = 60.0;
const float STREAK_DEPTH = 0.25;

void fragment() {
	vec2 p = (UV - 0.5) * size_px;
	float seed = floor(rc_time(TIME) * boil_fps);
	float n = (rc_noise(p * WOBBLE_SCALE + vec2(seed * 7.1, seed * 3.3)) - 0.5) * 2.0 * wobble_px;
	vec2 half_size = max(size_px * 0.5 - vec2(width_px + wobble_px), vec2(1.0));
	float d;
	float along;
	float length_total = 1.0;
	if (shape == 0) {
		vec2 q = p / half_size;
		d = abs(length(q) - 1.0) * min(half_size.x, half_size.y);
		along = fract(atan(q.y, q.x) / TAU - start_turn);
		length_total = 1.0 + overshoot;
	} else if (shape == 1) {
		vec2 q = abs(p) - half_size;
		d = abs(length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0));
		along = fract(atan(p.y * half_size.x, p.x * half_size.y) / TAU - start_turn);
	} else {
		d = abs(p.y);
		along = UV.x;
	}
	float stroke = 1.0 - smoothstep(width_px * 0.5 - 1.0, width_px * 0.5 + 1.0, d + n);
	float reach = progress * length_total;
	// A loop's overshoot draws its first stretch a second time.
	float drawn = max(step(along, reach), step(along + 1.0, reach));
	float streak = 1.0 - STREAK_DEPTH * rc_noise(vec2(along * STREAKS, d * 0.5));
	COLOR = vec4(ink.rgb, ink.a * stroke * drawn * streak * COLOR.a);
}
