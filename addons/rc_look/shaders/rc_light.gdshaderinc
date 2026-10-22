// LOOK-TOOLBOX module 6: light, spill, glow. One falloff family and one light space for every view, so a neon sign
// reaches as far in the UI as in the 3D city:
//   - rcl_fall_exp(d, reach, k): exp(-(d / reach)^k), unbounded (k 1: exponential, 2: gaussian); glows and halos.
//   - rcl_fall_pow(d, reach, p): (1 - d / reach)^p, zero at reach (finite support); pools and spills on surfaces.
//   - rcl_light_add(base_srgb, light_lin): adds light in LINEAR light under a soft ceiling, 1 - (1 - b) exp(-L / (1 - b))
//     per channel, applied as ONE scale on the light (the channel that saturates first sets it), so the light keeps its
//     hue and overlapping neon holds its colour instead of drifting to white (designer 2026-10-21). The base unchanged at
//     L = 0, b + L for a little light, never past white; returns sRGB (never add glow to display values).
//   - rcl_bright(lin, threshold, knee, key): the bloom bright pass, a soft knee in linear light on a key: 0 = the
//     brightest channel (HDR 3D, where lamps pass 1), 1 = linear chroma, max - min (2D layers, where paper is as bright
//     as neon: only saturated light blooms).
// RcLookLight (GDScript) mirrors these exactly; numbers in addons/rc_look/config/look_light.tres.
//   #include "res://addons/rc_look/shaders/rc_light.gdshaderinc"
#ifndef RC_LIGHT_INCLUDED
#define RC_LIGHT_INCLUDED
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"

float rcl_fall_exp(float d, float reach, float k) {
	return exp(-pow(max(d, 0.0) / max(reach, 1e-5), k));
}

float rcl_fall_pow(float d, float reach, float p) {
	return pow(clamp(1.0 - max(d, 0.0) / max(reach, 1e-5), 0.0, 1.0), p);
}

// Preset falloff: kind 0 = exp (shape = k), 1 = pow (shape = p).
float rcl_fall(float d, float reach, float shape, int kind) {
	return kind == 0 ? rcl_fall_exp(d, reach, shape) : rcl_fall_pow(d, reach, shape);
}

vec3 rcl_light_add(vec3 base_srgb, vec3 light_lin) {
	vec3 b = min(rcl_to_lin(base_srgb), vec3(1.0));
	vec3 l = max(light_lin, vec3(0.0));
	vec3 room = max(vec3(1.0) - b, vec3(1e-5));
	vec3 ceil_add = room - room * exp(-l / room);
	vec3 ratio = mix(vec3(1.0), ceil_add / max(l, vec3(1e-6)), step(vec3(1e-6), l));
	float s = clamp(min(min(ratio.r, ratio.g), ratio.b), 0.0, 1.0);
	return rcl_to_srgb(min(b + l * s, vec3(1.0)));
}

// Soft-knee bright pass (linear) on key `key` (0 brightest channel, 1 chroma): 0 below threshold - knee, quadratic
// through the knee, linear above; the colour is scaled, so its hue is kept.
vec3 rcl_bright(vec3 lin, float threshold, float knee, int key) {
	float hi = max(max(lin.r, lin.g), lin.b);
	float l = key == 0 ? hi : hi - min(min(lin.r, lin.g), lin.b);
	float k = max(knee, 1e-5);
	float soft = clamp(l - threshold + k, 0.0, 2.0 * k);
	soft = soft * soft / (4.0 * k);
	float w = max(soft, l - threshold) / max(l, 1e-5);
	return lin * w;
}
#endif
