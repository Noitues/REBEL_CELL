// NA-24 (PIPELINE_SPEC 5.2b, 9.1, 9.6): the street dressing's emissive pieces as one unshaded additive shader on a MultiMesh.
// Colour = the instance colour (a palette colour resolved by the builder); INSTANCE_CUSTOM.x = a 0..1 seed (burst count), .z = the gain (HQ band emit), .y = a
// 0..1 phase. `shape` 0 = a solid piece (shop strip, billboard panel, lamp dot), 1 = a soft radial disc on a quad (lamp spill, ground
// glow, facade wash: UV radial falloff), 2 = the flicker overlay of a sign (tier 3): 1 .. 3 short bursts per loop on a hum of
// whole cycles, so the frame at t equals the frame at t + loop_s, added on the panel only (never over a core stroke).
// The sign panels themselves are `dress_sign` (NA-24c). Every moving term is a pure function of the clock (`nr_clock`: `anim_t` live,
// `anim_t_frozen` under reduce effects).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"
#include "res://shaders/city/dress_sign.gdshaderinc"
// LOOK-TOOLBOX module 11: the flicker is rc_sign's.
#include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"

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
varying vec3 lpos;
varying vec3 lnrm;
varying vec3 lscale;

void vertex() {
	cust = INSTANCE_CUSTOM.xyz;
	lpos = VERTEX;
	lnrm = NORMAL;
	lscale = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
}

void fragment() {
	float g = 1.0;
	if (shape == 1) {
		float r = clamp(length(UV - vec2(0.5)) * 2.0, 0.0, 1.0);
		g = pow(1.0 - r, disc_power);
	} else if (shape == 2) {
		if (!FRONT_FACING) {
			discard;
		}
		float t = mod(nr_clock(anim_t, anim_t_frozen), loop_s) / loop_s;
		float k = floor(mix(bursts.x, bursts.y + 1.0, clamp(cust.x, 0.0, 0.999)));
		g = rcl_flicker(t, k, cust.y, 0.14, 4.0, 0.6);
		vec3 sc = max(lscale, vec3(0.0001));
		vec2 p = lpos.xy * sc.xy;
		vec2 m = sg_core(p, sc.xy, cust.x, vec2(fwidth(p.x), fwidth(p.y)));
		g *= 1.0 - step(0.5, abs(lnrm.z)) * max(m.x, m.y);
	}
	ALBEDO = COLOR.rgb * emit * g * cust.z * emission_multiplier * look_blend;
	ALPHA = 1.0;
}
