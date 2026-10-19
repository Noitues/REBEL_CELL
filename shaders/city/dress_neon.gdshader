// NA-24 (PIPELINE_SPEC 5.2b, 9.1, 9.6): the street dressing's emissive pieces as one unshaded additive shader on a MultiMesh.
// Colour = the instance colour (a palette colour resolved by the builder); INSTANCE_CUSTOM.x = a 0..1 seed (burst count), .z = the gain (HQ band emit), .y = a
// 0..1 phase. `shape` 0 = a solid piece (sign block, panel, band, lamp dot), 1 = a soft radial disc on a quad (lamp spill, ground
// glow, facade wash: UV radial falloff), 2 = the flicker overlay of a sign (tier 3): 1 .. 3 short bursts per loop on a hum of
// whole cycles, so the frame at t equals the frame at t + loop_s. Every moving term is a pure function of the clock
// (`nr_clock`: `anim_t` live, `anim_t_frozen` under reduce effects).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"

uniform int shape = 0;
uniform float emit = 1.0;
uniform float loop_s = 4.0;
uniform float anim_t = 0.0;
uniform float anim_t_frozen = 0.0;
uniform vec2 bursts = vec2(1.0, 3.0);
uniform float disc_power = 2.0;
uniform float emission_multiplier = 1.0;
uniform float look_blend = 1.0;

varying vec3 cust;

void vertex() {
	cust = INSTANCE_CUSTOM.xyz;
}

void fragment() {
	float g = 1.0;
	if (shape == 1) {
		float r = clamp(length(UV - vec2(0.5)) * 2.0, 0.0, 1.0);
		g = pow(1.0 - r, disc_power);
	} else if (shape == 2) {
		float t = mod(nr_clock(anim_t, anim_t_frozen), loop_s) / loop_s;
		float k = floor(mix(bursts.x, bursts.y + 1.0, clamp(cust.x, 0.0, 0.999)));
		float u = fract(t * k + cust.y);
		float burst = 1.0 - smoothstep(0.0, 0.14, u);
		float hum = 0.5 + 0.5 * sin(6.2831853 * (t * 4.0 + cust.y));
		g = burst * (0.6 + 0.4 * hum);
	}
	ALBEDO = COLOR.rgb * emit * g * cust.z * emission_multiplier * look_blend;
	ALPHA = 1.0;
}
