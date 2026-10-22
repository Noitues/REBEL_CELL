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
// LOOK-TOOLBOX module 8: the puddle noise and roughness are rc_wet's.
#include "res://addons/rc_look/shaders/rc_wet.gdshaderinc"

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
// AAA-2 P6 (A-034 item 2): the wet road lit by each light's own colour. `streak_k` is how much longer the specular lobe is along
// the view direction (screen-vertical smears of lamps and glows) on a sharp (puddle) patch; it falls to 1 (a round soft blob, the
// "bokeh" of the plate) as the roughness rises to `rough_wet.x`. `spec_max` caps one light's lobe; `pool_k` scales the diffuse pool.
uniform float streak_k = 7.0;
uniform float spec_max = 8.0;
uniform float pool_k = 0.3;
uniform float spill_k = 0.25;
// LOOK L5 (designer 2026-10-20): `slope_spec` 0..1 keeps the lobe to flat ground only (world normal y over `slope_flat`), so the
// moon no longer flecks the whole-city mountains white. 0 = the old lobe everywhere.
uniform float slope_spec = 0.0;
uniform vec2 slope_flat = vec2(0.97, 0.995);
varying vec3 v_world;
varying float v_ny;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_ny = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz).y;
}


void fragment() {
	ROUGHNESS = 0.0;
	if (lane) {
		ALBEDO = vec3(0.0);
		EMISSION = COLOR.rgb * lane_gain * emission_multiplier;
	} else {
		vec3 col = COLOR.rgb;
		if (look_blend > 0.0) {
			float n = rcl_fbm3_n(vec3(v_world.x, 0.0, v_world.z) * noise_scale, noise_octaves);
			float rough = rcl_puddle_rough(n, rough_noise, rough_wet);
			rough = mix(rough_wet.x, rough, clamp(puddles_sharp, 0.0, 1.0));
			// NA-25b: the wet roughness at every look_blend (it used to scale with it: a half blend was a near mirror).
			ROUGHNESS = rough;
			SPECULAR = mix(0.5, wet_specular, look_blend);
			col *= mix(1.0, albedo_mul, look_blend);
		}
		ALBEDO = col;
		// Light spill on the streets (1B's banded spill, the key light's bands).
		vec3 spill = toon_spill(v_world, vec3(0.0, 1.0, 0.0), ramp_edges.x, ramp_edges.y, spill_mid, spill_low);
		EMISSION = col * spill * spill_gain * emission_multiplier * mix(1.0, spill_k, look_blend);
	}
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	if (look_blend > 0.0) {
		// AAA-2 P6: a Lambert pool and an anisotropic GGX lobe of each light's own colour (lamp pools, long reflection streaks,
		// round soft blobs on the rough patches). The sun glint of NA-25b is the same lobe on the moon.
		vec3 lc = LIGHT_COLOR * ATTENUATION;
		float nl = max(dot(NORMAL, LIGHT), 0.0);
		float rough = max(ROUGHNESS, 0.02);
		float ab = max(rough * rough, 0.0036);
		float round_k = smoothstep(rough_wet.y, rough_wet.x, rough);
		float at = min(ab * mix(streak_k, 1.0, round_k), 0.5);
		vec3 tv = VIEW - NORMAL * dot(NORMAL, VIEW);
		vec3 t = tv / max(length(tv), 0.0001);
		vec3 bt = cross(NORMAL, t);
		vec3 h = normalize(LIGHT + VIEW);
		float ht = dot(h, t) / at;
		float hb = dot(h, bt) / ab;
		float hn = max(dot(h, NORMAL), 0.0);
		float q = ht * ht + hb * hb + hn * hn;
		float dd = 1.0 / (3.14159265 * at * ab * q * q);
		float vh = max(dot(VIEW, h), 0.0);
		float f0 = 0.08 * SPECULAR_AMOUNT * 2.0;
		float fr = f0 + (1.0 - f0) * pow(1.0 - vh, 5.0);
		float nv = max(dot(NORMAL, VIEW), 0.02);
		vec3 spec = lc * min(dd * fr * nl / (4.0 * nv), spec_max) * look_blend * clamp(puddles_sharp, 0.0, 1.0);
		spec *= mix(1.0, smoothstep(slope_flat.x, slope_flat.y, v_ny), slope_spec);
		vec3 pool = lc * nl * pool_k;
		SPECULAR_LIGHT += spec;
		int b0 = toon_band_index(ndl, ramp_edges.x, ramp_edges.y);
		vec3 band0 = b0 == 0 ? ramp_shadow : (b0 == 1 ? ramp_mid : ramp_lit);
		band0 = mix(band0, mix(ramp_shadow, ramp_lit, clamp(ndl, 0.0, 1.0)), look_blend);
		DIFFUSE_LIGHT += mix(band0, pool, look_blend);
	} else {
		int b = toon_band_index(ndl, ramp_edges.x, ramp_edges.y);
		vec3 band = b == 0 ? ramp_shadow : (b == 1 ? ramp_mid : ramp_lit);
		DIFFUSE_LIGHT = band;
	}
}
