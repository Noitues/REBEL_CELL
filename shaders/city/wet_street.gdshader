// NA-22 (PIPELINE_SPEC 4.1 "wet ground", 4.3 rule 3): the ground of city_ground.gdshader (asphalt, plazas, street lots, the
// lane glow strips) with the wet-street look blended in by look_blend. At look_blend 0 it draws exactly as city_ground
// (same toon ramp, spill and lane strips); above 0 the colour goes x albedo_mul, the roughness comes from a puddle noise
// (value noise, noise_octaves, scale noise_scale; remapped rough_noise -> rough_wet), the specular rises to wet_specular and
// a GGX-like sun highlight appears. `puddles_sharp` (0..1, the LOD band of the same name) blends the puddle roughness
// toward its blurry mean while the camera is far. ROUGHNESS stays under 0.5, so the ink pass still reads the ground as
// not-a-building.
shader_type spatial;
render_mode cull_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"
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

uniform float look_blend = 0.0;
uniform float emission_multiplier = 1.0;
uniform float noise_scale = 0.09;
uniform int noise_octaves = 5;
uniform vec2 rough_noise = vec2(0.45, 0.6);
uniform vec2 rough_wet = vec2(0.3, 0.03);
uniform float wet_specular = 0.7;
uniform float albedo_mul = 0.55;
uniform float puddles_sharp = 1.0;
varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float puddle_noise(vec3 p) {
	float a = 0.5;
	float s = 0.0;
	float w = 0.0;
	for (int i = 0; i < 8; i++) {
		if (i >= noise_octaves) {
			break;
		}
		s += a * nr_noise3(p);
		w += a;
		p *= 2.0;
		a *= 0.5;
	}
	return s / max(w, 0.0001);
}

void fragment() {
	ROUGHNESS = 0.0;
	if (lane) {
		ALBEDO = vec3(0.0);
		EMISSION = COLOR.rgb * lane_gain * emission_multiplier;
	} else {
		vec3 col = COLOR.rgb;
		if (look_blend > 0.0) {
			float n = puddle_noise(vec3(v_world.x, 0.0, v_world.z) * noise_scale);
			float k = smoothstep(rough_noise.x, rough_noise.y, n);
			float rough = mix(rough_wet.x, rough_wet.y, k);
			rough = mix(rough_wet.x, rough, clamp(puddles_sharp, 0.0, 1.0));
			// NA-25b: the wet roughness at every look_blend (it used to scale with it: a half blend was a near mirror).
			ROUGHNESS = rough;
			SPECULAR = mix(0.5, wet_specular, look_blend);
			col *= mix(1.0, albedo_mul, look_blend);
		}
		ALBEDO = col;
		// Light spill on the streets (1B's banded spill, the key light's bands).
		vec3 spill = toon_spill(v_world, vec3(0.0, 1.0, 0.0), ramp_edges.x, ramp_edges.y, spill_mid, spill_low);
		EMISSION = col * spill * spill_gain * emission_multiplier;
	}
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	int b = toon_band_index(ndl, ramp_edges.x, ramp_edges.y);
	vec3 band = b == 0 ? ramp_shadow : (b == 1 ? ramp_mid : ramp_lit);
	if (look_blend > 0.0) {
		band = mix(band, mix(ramp_shadow, ramp_lit, clamp(ndl, 0.0, 1.0)), look_blend);
		// A GGX-like sun highlight on the wet surface.
		float a = max(ROUGHNESS * ROUGHNESS, 0.002);
		vec3 h = normalize(LIGHT + VIEW);
		float nh = max(dot(NORMAL, h), 0.0);
		float dd = a * a / (3.14159265 * pow(nh * nh * (a * a - 1.0) + 1.0, 2.0));
		// NA-25b: the glint also comes in with `puddles_sharp` (the camera near the street, spec 5.2). A far camera (the dive)
		// saw the sun lobe on lit ground clip to flat white patches.
		SPECULAR_LIGHT += LIGHT_COLOR * ATTENUATION * min(dd * 0.25 * SPECULAR_AMOUNT, 6.0) * max(dot(NORMAL, LIGHT), 0.0) * look_blend * clamp(puddles_sharp, 0.0, 1.0);
	}
	DIFFUSE_LIGHT = band;
}
