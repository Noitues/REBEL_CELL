// NA-12 r3 (A-030 item 2): one shore light's reflection on the sea, a soft smear hanging straight down the screen under
// the light. UV.x = 0 at the light .. 1 at the end of the smear (fading to nothing), UV.y = -1..1 across; COLOR.rgb is
// the light's colour, COLOR.a a per-smear seed. The ripple breaks it into short wobbling pieces (never an even dash).
// Additive; `night` fades it out by day; `time_scale` 0 freezes the ripple (reduce motion).
shader_type spatial;
render_mode blend_add, cull_disabled, depth_draw_never, specular_disabled, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
// LOOK-TOOLBOX module 8: the sin hash and 2D value noise are rc_look's (rcl_hash12_sin / rcl_vnoise2_sin).
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"

uniform float night = 1.0;
uniform float gain = 1.3;
uniform float length_bu = 40.0;
uniform float ripple_bu = 9.0;
uniform float ripple_speed = 0.12;
uniform float look_blend = 0.0;
uniform float look_gain = 1.6;
uniform float time_scale = 1.0;


void fragment() {
	float t = rc_time(TIME) * time_scale * ripple_speed;
	float s = UV.x * length_bu / max(ripple_bu, 0.001);
	float wob = (rcl_vnoise2_sin(vec2(COLOR.a * 31.0, s * 1.3 + t * 4.0)) - 0.5) * 0.5;
	float across = 1.0 - smoothstep(0.0, 1.0, abs(UV.y + wob));
	float fade = pow(1.0 - UV.x, 1.7);
	float brk = 0.35 + 0.65 * smoothstep(0.25, 0.65, rcl_vnoise2_sin(vec2(COLOR.a * 17.0 + UV.y * 0.8, s * 2.2 + t * 6.0)));
	ALBEDO = vec3(0.0);
	ROUGHNESS = 0.0;
	EMISSION = COLOR.rgb * across * across * fade * brk * gain * night * mix(1.0, look_gain, look_blend);
	ALPHA = 1.0;
}

void light() {
	DIFFUSE_LIGHT = vec3(0.0);
}
