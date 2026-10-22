// LOOK-TOOLBOX module 8: wet and water. One set of helpers for the wet street (wet_street), the wet plinth
// (city_building), the sea and its plane (city_water, city_water_plane, city_water_smear) and the seabed. Exact forms of
// the existing code, so a view moves onto them with identical pixels:
//   - rcl_fbm3_n(p, oct): the puddle noise, a normalised octave sum (gain 0.5, lacunarity 2, at most 8) of
//     rcl_vnoise3 (= netrun_clock's nr_noise3, the same hash).
//   - rcl_puddle_rough(n, rough_noise, rough_wet): roughness over the puddle noise, rough_wet.x (dry) to .y (puddle)
//     across rough_noise.x..y.
//   - rcl_fresnel(cos_t, f0): Schlick, power 5. rcl_f0_ior(ior): the dielectric F0 from an index of refraction.
//   - rcl_ggx_d(nh, a): the isotropic GGX (Trowbridge-Reitz) distribution, a = roughness^2.
//   - rcl_ridge(n, width): 1 on the noise's mid line fading over `width` (caustic / marble veins).
//   - rcl_shore(d, len): exp(-d / len), a fade with the distance from the shore.
// The F0 policy stays per view (street, plinth and water differ; a look decision, not this file's).
// Numbers in addons/rc_look/config/look_wet.tres; RcLookWet mirrors these exactly.
//   #include "res://addons/rc_look/shaders/rc_wet.gdshaderinc"
#ifndef RC_WET_INCLUDED
#define RC_WET_INCLUDED
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"

float rcl_fbm3_n(vec3 p, int oct) {
	float a = 0.5;
	float s = 0.0;
	float w = 0.0;
	for (int i = 0; i < 8; i++) {
		if (i >= oct) {
			break;
		}
		s += a * rcl_vnoise3(p);
		w += a;
		p *= 2.0;
		a *= 0.5;
	}
	return s / max(w, 0.0001);
}

float rcl_puddle_rough(float n, vec2 rough_noise, vec2 rough_wet) {
	return mix(rough_wet.x, rough_wet.y, smoothstep(rough_noise.x, rough_noise.y, n));
}

float rcl_fresnel(float cos_t, float f0) {
	return f0 + (1.0 - f0) * pow(1.0 - cos_t, 5.0);
}

float rcl_f0_ior(float ior) {
	return pow((ior - 1.0) / (ior + 1.0), 2.0);
}

float rcl_ggx_d(float nh, float a) {
	return a * a / (3.14159265 * pow(nh * nh * (a * a - 1.0) + 1.0, 2.0));
}

float rcl_ridge(float n, float width) {
	return 1.0 - smoothstep(0.0, width, abs(2.0 * n - 1.0));
}

float rcl_shore(float d, float len) {
	return exp(-d / max(len, 0.001));
}
#endif
