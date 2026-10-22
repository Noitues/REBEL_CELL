// LOOK-TOOLBOX module 4: toon (cel) bands, one set of helpers for the props / busts (toon_ink), the city
// (city_building, landmark_toon, hq_compound_toon) and the spill (toon_bands). Exact forms of the existing code, so a view
// moves onto them with identical pixels:
//   - rcl_band(x, lo, hi): 0 shadow, 1 mid, 2 lit (edges lo < hi; toon_band_index).
//   - rcl_band_shade(x, lo, hi, mid, low): the band's share of full light, 1 / mid / low (toon_ink band()).
//   - rcl_band_tint(shade, low, shadow_tint): the band's tint, shadow_tint in the shadow band to white when lit.
//   - rcl_band_ramp(x, lo, hi, c_low, c_mid, c_lit): a three-colour ramp by band (city_building ramp).
//   - rcl_rim(n, v, p): (1 - n . v)^p, the fresnel rim (hq_solace_pbr; AAA-2 shares it).
// Edge caveat: landmark_toon / hq_compound_toon test ndl < lo / ndl < hi, so exactly on an edge they give the upper band
// (mid at x == lo, lit at x == hi) where rcl_band gives the lower one. Identical away from the edges; a migration of those
// two needs an edge form (or a proof that no pixel lands on an edge) first.
// Numbers in addons/rc_look/config/look_toon.tres (presets "props", "city"); RcLookToon mirrors these exactly.
//   #include "res://addons/rc_look/shaders/rc_toon.gdshaderinc"
#ifndef RC_TOON_INCLUDED
#define RC_TOON_INCLUDED

int rcl_band(float x, float lo, float hi) {
	return x > hi ? 2 : (x > lo ? 1 : 0);
}

float rcl_band_shade(float x, float lo, float hi, float mid, float low) {
	return x > hi ? 1.0 : (x > lo ? mid : low);
}

vec3 rcl_band_tint(float shade, float low, vec3 shadow_tint) {
	return mix(shadow_tint, vec3(1.0), (shade - low) / max(1.0 - low, 0.001));
}

vec3 rcl_band_ramp(float x, float lo, float hi, vec3 c_low, vec3 c_mid, vec3 c_lit) {
	int b = rcl_band(x, lo, hi);
	return b == 2 ? c_lit : (b == 1 ? c_mid : c_low);
}

float rcl_rim(vec3 n, vec3 v, float p) {
	return pow(1.0 - clamp(dot(n, v), 0.0, 1.0), p);
}
#endif
