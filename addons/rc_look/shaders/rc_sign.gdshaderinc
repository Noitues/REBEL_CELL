// LOOK-TOOLBOX module 11: signage and neon. One set of helpers for neon tubes, sign strokes, their glow and their
// flicker. The forms the game already uses are kept exact, so a view moves onto them with identical pixels:
//   - rcl_gauss(r, sigma): exp(-0.5 (r / sigma)^2) (beam_shaft's core and skirt).
//   - rcl_hot(col, core01, hot): mix(col, white, hot x core01) (beam_shaft, city_building's bit glyphs).
//   - rcl_hot_to(col, core_col, k): the same toward a core colour (the NEON_CORE token).
//   - rcl_tube_cov(d, half_w, pix): a stroke's antialiased coverage at distance d from its centre line (dress_sign's
//     frame form).
//   - rcl_tube_core(d, core_w): 1 on the centre line falling to 0 at core_w (the thin hot core).
//   - rcl_flicker(t01, bursts, seed, burst_len, hum_hz, hum_floor): dress_neon's flicker (bursts per loop at t01 in
//     0..1, a hum under them).
//   - rcl_blink(ph, duty, off), rcl_beacon(ph): city_glow's blink and beacon.
// Whether tubes get a white-hot core is the designer's call (DECISIONS: open question, module 11); the lab sheet
// shows flat / lightened / hot side by side. Numbers in addons/rc_look/config/look_sign.tres; RcLookSign mirrors.
//   #include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"
#ifndef RC_SIGN_INCLUDED
#define RC_SIGN_INCLUDED

float rcl_gauss(float r, float sigma) {
	return exp(-0.5 * (r / sigma) * (r / sigma));
}

vec3 rcl_hot(vec3 col, float core01, float hot) {
	return mix(col, vec3(1.0), hot * clamp(core01, 0.0, 1.0));
}

vec3 rcl_hot_to(vec3 col, vec3 core_col, float k) {
	return mix(col, core_col, clamp(k, 0.0, 1.0));
}

float rcl_tube_cov(float d, float half_w, float pix) {
	return clamp((half_w - d) / max(pix, 1e-5) + 0.5, 0.0, 1.0);
}

float rcl_tube_core(float d, float core_w) {
	return 1.0 - smoothstep(0.0, max(core_w, 1e-5), d);
}

float rcl_flicker(float t01, float bursts, float seed, float burst_len, float hum_hz, float hum_floor) {
	float u = fract(t01 * bursts + seed);
	float burst = 1.0 - smoothstep(0.0, burst_len, u);
	float hum = 0.5 + 0.5 * sin(6.2831853 * (t01 * hum_hz + seed));
	return burst * (hum_floor + (1.0 - hum_floor) * hum);
}

float rcl_blink(float ph, float duty, float off) {
	return ph < duty ? 1.0 : off;
}

float rcl_beacon(float ph) {
	return 0.2 + 0.8 * pow(max(0.0, cos(ph * 6.2831853)), 4.0);
}
#endif
