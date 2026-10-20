// LOOK L5 (whole-city plate parity): the seabed under the water plane, lit on the ground's toon ramp and seen through the
// Blender plate's clear-water recipe (city_render.water_fade). Below the sea a surface is seen through d / |V.y| + d BU of
// water (the view leg plus its light's down leg); the transmittance T = exp(-sigma * path) per channel (red dies first)
// darkens its colour and the water's own in-scatter (deep blue) fills (1 - T). So the shallows stay clear and the water
// fades to deep blue with depth and with a grazing view. Caustics: two soft ridge-noise ripple layers on up-facing faces,
// lit floor, drifting patches, fading exp(-d / caustic_depth_bu); emission, so they read at night as the plate's marbling.
shader_type spatial;
render_mode cull_disabled, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/kit/toon_bands.gdshaderinc"

uniform vec3 ramp_shadow;
uniform vec3 ramp_mid;
uniform vec3 ramp_lit;
uniform vec2 ramp_edges = vec2(0.147, 0.393);
uniform float band_soft = 0.14;
uniform float sea_y = 0.0;
uniform vec3 sigma = vec3(0.090, 0.034, 0.016);
uniform vec3 inscatter = vec3(0.003, 0.018, 0.055);
uniform float inscatter_gain = 1.0;
// By day the sky lights the water column: the in-scatter this many times stronger at night 0.
uniform float inscatter_day_gain = 1.0;
uniform float night = 1.0;
// The caustics by day, as a share of their night strength (the sun washes the plate's day bay smooth).
uniform float caustic_day_k = 1.0;
uniform float path_cap = 600.0;
uniform float caustic_k = 1.1;
uniform float caustic_scale = 0.05;
uniform float caustic_width = 0.22;
uniform float caustic_distort = 0.9;
uniform float caustic_floor = 0.12;
uniform float caustic_patch = 0.05;
uniform float caustic_patch_scale = 0.025;
uniform float caustic_depth_bu = 30.0;
uniform vec3 caustic_col = vec3(0.22, 0.72, 0.78);
uniform float caustic_speed = 0.02;
uniform float time_scale = 1.0;
varying vec3 v_world;
varying vec3 v_nw;

float h3(vec3 p) {
	return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

float vnoise3(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * (3.0 - 2.0 * f);
	float a = mix(mix(h3(i), h3(i + vec3(1.0, 0.0, 0.0)), u.x), mix(h3(i + vec3(0.0, 1.0, 0.0)), h3(i + vec3(1.0, 1.0, 0.0)), u.x), u.y);
	float b = mix(mix(h3(i + vec3(0.0, 0.0, 1.0)), h3(i + vec3(1.0, 0.0, 1.0)), u.x), mix(h3(i + vec3(0.0, 1.0, 1.0)), h3(i + vec3(1.0)), u.x), u.y);
	return mix(a, b, u.z);
}

// Two octaves (Blender's noise at detail 1.5), domain-distorted by a second field (its Distortion input).
float fbm_d(vec2 p, float w) {
	vec3 q = vec3(p, w);
	vec2 dq = vec2(vnoise3(q + vec3(5.2, 1.3, 0.0)), vnoise3(q + vec3(-3.1, 7.7, 0.0))) * 2.0 - 1.0;
	q.xy += dq * caustic_distort;
	return vnoise3(q) * 0.67 + vnoise3(q * 2.0 + vec3(1.7, 9.2, 0.0)) * 0.33;
}

float ripple(vec2 p, float scale, float off, float w) {
	float n = fbm_d(p * scale + vec2(off, off * 0.7), w);
	return 1.0 - smoothstep(0.0, caustic_width, abs(2.0 * n - 1.0));
}

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_nw = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

void fragment() {
	ROUGHNESS = 0.0;
	float d = max(sea_y - v_world.y, 0.0);
	vec3 V = normalize(CAMERA_POSITION_WORLD - v_world);
	float path = min(d / max(abs(V.y), 0.12) + d, path_cap);
	vec3 T = exp(-sigma * path);
	ALBEDO = COLOR.rgb * T;
	vec3 e = (1.0 - T) * inscatter * inscatter_gain * mix(inscatter_day_gain, 1.0, night);
	if (d > 0.05) {
		float t = rc_time(TIME) * time_scale * caustic_speed;
		vec2 p = v_world.xz;
		float rip = (ripple(p, caustic_scale, 0.0, 1.3 + t) + ripple(p, caustic_scale * 1.6, 3.3, 7.9 - t * 0.7)) * 0.5;
		float cnet = caustic_floor + rip * (1.0 - caustic_floor);
		float pm = smoothstep(0.42, 0.68, vnoise3(vec3(p * caustic_patch_scale, t * 0.3)));
		cnet *= caustic_patch + pm * (1.0 - caustic_patch);
		float up = v_nw.y * v_nw.y;
		e += caustic_col * cnet * up * exp(-d / caustic_depth_bu) * caustic_k * mix(caustic_day_k, 1.0, night);
	}
	EMISSION = e;
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	float t1 = smoothstep(ramp_edges.x - band_soft, ramp_edges.x + band_soft, ndl);
	float t2 = smoothstep(ramp_edges.y - band_soft, ramp_edges.y + band_soft, ndl);
	DIFFUSE_LIGHT = mix(mix(ramp_shadow, ramp_mid, t1), ramp_lit, t2);
}
