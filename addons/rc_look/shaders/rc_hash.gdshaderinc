// LOOK-TOOLBOX module 1: rc_look's hash and value noise on their own (deterministic: no time, no state, no
// derivatives, no globals), so any shader type can include it, fog included (rc_look itself cannot go into a fog
// shader: its facet helpers use dFdx). rc_look includes this file; a fog shader includes it alone:
//   #include "res://addons/rc_look/shaders/rc_hash.gdshaderinc"
#ifndef RC_HASH_INCLUDED
#define RC_HASH_INCLUDED

// ---- Hash and value noise (deterministic: no time, no state) ----

float rcl_hash12(vec2 p) {
	vec3 q = fract(vec3(p.xyx) * 0.1031);
	q += dot(q, q.yzx + 33.33);
	return fract((q.x + q.y) * q.z);
}

float rcl_hash13(vec3 p) {
	p = fract(p * 0.1031);
	p += dot(p, p.zyx + 31.32);
	return fract((p.x + p.y) * p.z);
}

vec2 rcl_hash22(vec2 p) {
	vec3 q = fract(vec3(p.xyx) * vec3(0.1031, 0.1030, 0.0973));
	q += dot(q, q.yzx + 33.33);
	return fract((q.xx + q.yz) * q.zy);
}

// The older sin hashes and their value noise (toon_ink / toon_ink_hull grain, the sea, its plane, smears and seabed),
// kept bit-exact so those views keep their pixels; new code uses rcl_hash13 / rcl_vnoise3.
float rcl_hash13_sin(vec3 p) {
	return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

float rcl_hash12_sin(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float rcl_vnoise2_sin(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(rcl_hash12_sin(i), rcl_hash12_sin(i + vec2(1.0, 0.0)), u.x), mix(rcl_hash12_sin(i + vec2(0.0, 1.0)), rcl_hash12_sin(i + vec2(1.0, 1.0)), u.x), u.y);
}

float rcl_vnoise3_sin(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * (3.0 - 2.0 * f);
	float a = mix(mix(rcl_hash13_sin(i), rcl_hash13_sin(i + vec3(1, 0, 0)), u.x), mix(rcl_hash13_sin(i + vec3(0, 1, 0)), rcl_hash13_sin(i + vec3(1, 1, 0)), u.x), u.y);
	float b = mix(mix(rcl_hash13_sin(i + vec3(0, 0, 1)), rcl_hash13_sin(i + vec3(1, 0, 1)), u.x), mix(rcl_hash13_sin(i + vec3(0, 1, 1)), rcl_hash13_sin(i + vec3(1, 1, 1)), u.x), u.y);
	return mix(a, b, u.z);
}

float rcl_vnoise2(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(rcl_hash12(i), rcl_hash12(i + vec2(1.0, 0.0)), u.x),
			mix(rcl_hash12(i + vec2(0.0, 1.0)), rcl_hash12(i + vec2(1.0)), u.x), u.y);
}

float rcl_vnoise3(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * (3.0 - 2.0 * f);
	float a = mix(mix(rcl_hash13(i), rcl_hash13(i + vec3(1, 0, 0)), u.x), mix(rcl_hash13(i + vec3(0, 1, 0)), rcl_hash13(i + vec3(1, 1, 0)), u.x), u.y);
	float b = mix(mix(rcl_hash13(i + vec3(0, 0, 1)), rcl_hash13(i + vec3(1, 0, 1)), u.x), mix(rcl_hash13(i + vec3(0, 1, 1)), rcl_hash13(i + vec3(1)), u.x), u.y);
	return mix(a, b, u.z);
}

// Fractal value noise, `oct` octaves (at most 6), lacunarity 2, gain 0.5, normalised to 0..1.
float rcl_fbm2(vec2 p, int oct) {
	float s = 0.0;
	float a = 0.5;
	float n = 0.0;
	for (int k = 0; k < 6; k++) {
		if (k >= oct) {
			break;
		}
		s += a * rcl_vnoise2(p);
		n += a;
		p = p * 2.0 + vec2(17.3, 9.1);
		a *= 0.5;
	}
	return s / max(n, 1e-4);
}
#endif
