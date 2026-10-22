// LOOK-TOOLBOX module 7: atmosphere. One air term for every view (3D fog / haze, 2D backdrop depth, map veils), mixed in
// linear light, and one sky gradient:
//   - rcl_air(d, y, a): the air between the eye and a point at distance d and height y, 0..1:
//       (1 - exp(-max(d - start, 0) * density)) * mix(1, high, 1 - exp(-max(y, 0) / height))
//     a Beer-Lambert extinction (the city_building per-building haze) thinned with height down to `high`.
//     a = vec4(start, density, height, high).
//   - rcl_air_mix(srgb, air_srgb, amount): the point seen through that much air (linear-light mix, returns sRGB).
//   - rcl_sky(e, top, horizon, ground, glow_k, ground_k): sky by elevation e (sin of the view angle), sRGB in and out,
//     mixed in linear light: top + (horizon - top) exp(-glow_k e) above the horizon, to `ground` below over ground_k.
// RcLookAir (GDScript) mirrors these exactly; numbers in addons/rc_look/config/look_air.tres.
//   #include "res://addons/rc_look/shaders/rc_air.gdshaderinc"
#ifndef RC_AIR_INCLUDED
#define RC_AIR_INCLUDED
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"

float rcl_air(float d, float y, vec4 a) {
	float depth = 1.0 - exp(-max(d - a.x, 0.0) * a.y);
	float thin = mix(1.0, a.w, 1.0 - exp(-max(y, 0.0) / max(a.z, 1e-5)));
	return clamp(depth * thin, 0.0, 1.0);
}

vec3 rcl_air_mix(vec3 srgb, vec3 air_srgb, float amount) {
	return rcl_to_srgb(mix(rcl_to_lin(srgb), rcl_to_lin(air_srgb), clamp(amount, 0.0, 1.0)));
}

vec3 rcl_sky(float e, vec3 top, vec3 horizon, vec3 ground, float glow_k, float ground_k) {
	vec3 t = rcl_to_lin(top);
	vec3 h = rcl_to_lin(horizon);
	vec3 up = t + (h - t) * exp(-glow_k * max(e, 0.0));
	vec3 down = mix(h, rcl_to_lin(ground), clamp(-e * ground_k, 0.0, 1.0));
	return rcl_to_srgb(e >= 0.0 ? up : down);
}
#endif
