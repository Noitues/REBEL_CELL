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
uniform bool lane = false;
uniform float lane_gain = 1.0;
uniform float spill_gain = 1.9;
uniform float spill_mid = 0.62;
uniform float spill_low = 0.32;
varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ROUGHNESS = 0.0;
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
	int b = toon_band_index(ndl, ramp_edges.x, ramp_edges.y);
	vec3 band = b == 0 ? ramp_shadow : (b == 1 ? ramp_mid : ramp_lit);
	DIFFUSE_LIGHT = band;
}
