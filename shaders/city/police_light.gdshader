// LOOK L5 (designer 2026-10-20, whole-city pose): the police light bars on the highways and the helicopters' blinkers:
// unshaded, emission alternating between `col_a` and `col_b` (COLOR.a = the light's phase), x `gain`.
shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec3 col_a = vec3(1.0, 0.1, 0.12);
uniform vec3 col_b = vec3(0.15, 0.35, 1.0);
uniform float gain = 4.0;
uniform float rate = 1.6;
uniform float on = 1.0;

void fragment() {
	float t = fract(rc_time(TIME) * rate + COLOR.a);
	// White vertices are police bars (red / blue); any other colour blinks in itself.
	bool police = COLOR.r > 0.9 && COLOR.g > 0.9 && COLOR.b > 0.9;
	vec3 c = police ? (t < 0.5 ? col_a : col_b) : COLOR.rgb * step(0.8, t);
	ALBEDO = vec3(0.0);
	EMISSION = c * gain * on;
}
