// Blinking city lights (H20): window lights and beacons over the baked city blink on
// the GPU, so their geometry is built once per camera and never redrawn per frame.
// Per vertex: UV.x = phase (0-1), UV.y = +period (seconds; shown while lit) or -period
// (shown while dark). A light is lit for `duty` of its period. `animate` is 0 under
// reduce-effects: every light holds its t = 0 state. Periods are seconds long, far under
// the flash limiter's 3 per second.
// Art pass W7 (ART_BIBLE 8 T0, 2): no light toggles faster than `min_period` seconds (T0's
// slow-loop floor, from city_look.tres), and inside a UI calm zone (screen fractions, as in
// city_live) the blinking lights are hidden: nothing moves behind text.
shader_type canvas_item;
// Reduce effects (rc_common): the clock stops, so every light holds its t = 0 state.
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float duty : hint_range(0.0, 1.0) = 0.5;
uniform float animate = 1.0;
uniform float min_period = 0.0;
uniform vec4 calm[8];
uniform int calm_count = 0;
uniform float calm_feather = 0.04;
uniform float aspect = 1.7777778;

void fragment() {
	float period = max(abs(UV.y), max(min_period, 0.001));
	float lit = 1.0 - step(duty, fract(rc_time(TIME) * animate / period + UV.x));
	float shown = UV.y > 0.0 ? lit : 1.0 - lit;
	vec2 sp = FRAGCOORD.xy * SCREEN_PIXEL_SIZE;
	float hide = 0.0;
	for (int i = 0; i < 8; i++) {
		if (i >= calm_count) {
			break;
		}
		vec4 r = calm[i];
		vec2 d = max(max(r.xy - sp, sp - r.zw), vec2(0.0));
		hide = max(hide, 1.0 - smoothstep(0.0, max(calm_feather, 0.0001), length(d * vec2(aspect, 1.0))));
	}
	COLOR.a *= shown * (1.0 - hide);
}
