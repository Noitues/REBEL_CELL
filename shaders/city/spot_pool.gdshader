// LOOK L5 (designer 2026-10-20, whole-city pose): spot_light.gdshader for the searchlights. pools, drawn over the roofs (no
// depth test: the pool lights whatever stands under it). COLOR.rgb the light's colour, COLOR.a its strength (falling to
// the rim), x `gain` x `on` (the night).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, depth_test_disabled, shadows_disabled;

#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_light.gdshaderinc"

uniform float gain = 1.2;
uniform float soft = 1.5;
uniform float on = 1.0;

void fragment() {
	float f = rcl_facing(NORMAL, VIEW, soft);  // rc_look module 6
	ALBEDO = COLOR.rgb * COLOR.a * f * gain * on;
}
