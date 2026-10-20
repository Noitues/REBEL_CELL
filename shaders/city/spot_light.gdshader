// LOOK L5 (designer 2026-10-20, whole-city pose): the helicopters' searchlights: a soft additive cone down to the city and
// the pool it lights there. COLOR.rgb is the light's colour, COLOR.a its strength at the vertex (the cone fades toward the
// ground, the pool toward its rim); the cone's sides fade as they turn edge-on (|N.V|^soft). x `gain` x `on` (the night).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, shadows_disabled;

#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float gain = 1.2;
uniform float soft = 1.5;
uniform float on = 1.0;

void fragment() {
	float f = pow(abs(dot(normalize(NORMAL), VIEW)), soft);
	ALBEDO = COLOR.rgb * COLOR.a * f * gain * on;
}
