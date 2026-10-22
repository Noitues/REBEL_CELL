// REBEL_CELL material kit (ART-1 1B): cel / toon for the 3D world (ART_BIBLE v2 §1.2
// "World": Cv2 gritty triangulated low-poly + E cel shading: 3 hard toon bands, grime, light
// spill from glowing elements onto walls and streets, depth haze). Shared with area 1D's
// city spike (it owns the city; this is the material). Use with `toon_ink_hull.gdshader` as
// next_pass for the ink lines (ToonInkMaterial builds both).
// - 3 hard bands from N.L (band edges and shades are uniforms);
// - per-triangle tone jitter (Cv2): flat normals per face give flat facets; a hash of the
//   face's world position jitters its tone by `tone_jitter`;
// - grime: a world-space noise darkening, stronger low on a wall;
// - light spill: up to 8 sources (LightSpill.uniforms_3d) light the albedo they reach
//   (multiply + a little emission), banded like the light;
// - haze: fades toward `haze_color` with view depth.
// Nothing animates (spill sources move from script), so reduce effects changes nothing; the
// include keeps the one control.
shader_type spatial;
render_mode diffuse_lambert, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
// ART-5 5a: the bands' spill (and its uniforms) shared with the city shaders.
#include "res://shaders/kit/toon_bands.gdshaderinc"

uniform vec4 albedo : source_color = vec4(0.42, 0.40, 0.48, 1.0);
uniform float band_hi = 0.55;
uniform float band_lo = 0.12;
uniform float shade_mid = 0.62;
uniform float shade_low = 0.32;
uniform vec4 shadow_tint : source_color = vec4(0.16, 0.12, 0.30, 1.0);
uniform float tone_jitter = 0.08;
uniform float grime = 0.18;
uniform float grime_scale = 0.35;
uniform float spill_emission = 0.35;
uniform vec4 haze_color : source_color = vec4(0.10, 0.08, 0.20, 1.0);
uniform float haze_start = 20.0;
uniform float haze_end = 120.0;
uniform float haze_max = 0.6;

varying vec3 world_pos;
varying vec3 face_seed;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	face_seed = floor(world_pos * 1.7) + NORMAL * 3.1;
}

void fragment() {
	float j = (rcl_hash13_sin(floor(face_seed * 4.0)) - 0.5) * 2.0 * tone_jitter;
	vec3 base = albedo.rgb * (1.0 + j) * COLOR.rgb;
	float g = rcl_vnoise3_sin(world_pos * grime_scale);
	float low = 1.0 - clamp(world_pos.y / 6.0, 0.0, 1.0);
	base *= 1.0 - grime * g * (0.5 + 0.5 * low);
	ALBEDO = base;
	// light spill, banded (toon_bands.gdshaderinc)
	vec3 n = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec3 spill = toon_spill(world_pos, n, band_lo, band_hi, shade_mid, shade_low);
	EMISSION = base * spill * 1.9 + spill * spill_emission * 0.15;
	// depth haze
	float depth = length(VERTEX);
	float hz = smoothstep(haze_start, haze_end, depth) * haze_max;
	ALBEDO = mix(ALBEDO, haze_color.rgb, hz);
	EMISSION = mix(EMISSION, haze_color.rgb * 0.4, hz);
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	float b = rcl_band_shade(ndl, band_lo, band_hi, shade_mid, shade_low);
	vec3 lit = rcl_band_tint(b, shade_low, shadow_tint.rgb);
	// the renderer multiplies DIFFUSE_LIGHT by ALBEDO
	DIFFUSE_LIGHT += LIGHT_COLOR * b * lit;
}
