// ART-5 5a (from ART-1 1D's spike): the ground (asphalt, plazas, street lots) on the same toon ramp, and the
// lane glow strips (`lane` = 1: vertex colour is emission, scaled by lane_gain so the
// management zooms can step the street glow back to 28 %). ROUGHNESS 0 marks not-a-building
// for the post pass.
shader_type spatial;
render_mode cull_disabled, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/kit/toon_bands.gdshaderinc"

uniform vec3 ramp_shadow;
uniform vec3 ramp_mid;
uniform vec3 ramp_lit;
uniform vec2 ramp_edges = vec2(0.147, 0.393);
// LOOK L5 (whole city): above 0 the bands blend over +/- band_soft of N.L (the outer land's relief reads as shading,
// not as hard dark blobs); 0 keeps the hard toon bands.
uniform float band_soft = 0.0;
uniform bool lane = false;
uniform float lane_gain = 1.0;
uniform float spill_gain = 1.9;
uniform float spill_mid = 0.62;
uniform float spill_low = 0.32;
// LOOK L5 (whole city, the plate's drifting cloud shadows): above 0 a world-space value-noise field (cloud_scale units
// a blob, offset cloud_off) darkens the land's N.L by cloud_k where it passes cloud_edge; 0 is off.
uniform float cloud_k = 0.0;
uniform float cloud_scale = 45.0;
uniform vec2 cloud_off = vec2(0.0);
uniform vec2 cloud_edge = vec2(0.5, 0.62);
varying vec3 v_world;
varying float v_cloud;

float cl_hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float cl_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(cl_hash(i), cl_hash(i + vec2(1.0, 0.0)), u.x), mix(cl_hash(i + vec2(0.0, 1.0)), cl_hash(i + vec2(1.0)), u.x), u.y);
}

float cloud_shadow(vec2 xz) {
	vec2 p = xz / cloud_scale + cloud_off;
	float n = 0.6 * cl_noise(p) + 0.28 * cl_noise(p * 2.1 + 5.3) + 0.12 * cl_noise(p * 4.3 + 1.7);
	return smoothstep(cloud_edge.x, cloud_edge.y, n);
}

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ROUGHNESS = 0.0;
	v_cloud = cloud_k > 0.0 ? cloud_k * cloud_shadow(v_world.xz) : 0.0;
	if (lane) {
		ALBEDO = vec3(0.0);
		EMISSION = COLOR.rgb * lane_gain;
	} else {
		ALBEDO = COLOR.rgb;
		// Light spill on the streets (1B's banded spill, the key light's bands).
		vec3 spill = toon_spill(v_world, vec3(0.0, 1.0, 0.0), ramp_edges.x, ramp_edges.y, spill_mid, spill_low);
		EMISSION = COLOR.rgb * spill * spill_gain;
	}
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	ndl *= 1.0 - v_cloud;
	if (band_soft > 0.0) {
		float t1 = smoothstep(ramp_edges.x - band_soft, ramp_edges.x + band_soft, ndl);
		float t2 = smoothstep(ramp_edges.y - band_soft, ramp_edges.y + band_soft, ndl);
		DIFFUSE_LIGHT = mix(mix(ramp_shadow, ramp_mid, t1), ramp_lit, t2);
	} else {
		int b = toon_band_index(ndl, ramp_edges.x, ramp_edges.y);
		vec3 band = b == 0 ? ramp_shadow : (b == 1 ? ramp_mid : ramp_lit);
		DIFFUSE_LIGHT = band;
	}
}
