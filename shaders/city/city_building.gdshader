// ART-5 5a (from ART-1 1D's spike): Cv2 faceted buildings with the E 3-band toon ramp (target_corps.mat_toon:
// colour * ramp(band of N.L with shadow) * tone jitter per triangle), procedural window
// grid, ledges, shopfronts and the neon roof trim (unified40.city_building). Prototype of
// the shared toon material: the bands and the light spill come from 1B's kit include
// (shaders/kit/toon_bands.gdshaderinc, ToonInkMaterial.set_spill feeds it); the ink is the
// city's post pass (city_post.gdshader), not the hull (it splits at hard corners). Instances: MultiMesh,
// COLOR = base colour, INSTANCE_CUSTOM = (taper, trim ink index + 1 or 0, seed 0-1, crest).
shader_type spatial;
render_mode cull_disabled, specular_disabled;
#include "res://shaders/kit/toon_bands.gdshaderinc"

uniform vec3 ramp_shadow;
uniform vec3 ramp_mid;
uniform vec3 ramp_lit;
uniform vec2 ramp_edges = vec2(0.147, 0.393);
uniform float tone_min = 0.86;
uniform float tone_max = 1.12;
uniform float roof_gain = 1.08;
uniform vec3 window_colors[6];
uniform vec2 window_pitch = vec2(1.6, 1.9);
uniform vec2 window_size = vec2(0.8, 0.7);
uniform float window_first = 1.6;
uniform float window_share = 0.3;
uniform float window_dim_min = 0.5;
uniform float window_gain = 1.0;
uniform vec3 ink_colors[16];
uniform float trim_bu = 0.22;
uniform float neon_gain = 1.0;
uniform float ledge_every = 6.0;
uniform float ledge_bu = 0.16;
// 0 city, 1 raid, 2 transit (CityLod.Detail).
uniform int detail = 0;
// Light spill: the shadow / mid bands' share of a source's light, and its emission share.
uniform float spill_mid = 0.62;
uniform float spill_low = 0.32;
uniform float spill_gain = 1.9;

varying flat vec3 v_corner;
varying flat vec3 v_edge;
varying vec3 v_world;
varying flat vec4 v_inst;
varying flat float v_h0;
varying flat float v_h;
varying flat vec4 v_c0;
varying float v_rim;
varying flat float v_iid;
varying flat float v_half;

float hash1(vec3 p) {
	p = fract(p * 0.1031);
	p += dot(p, p.zyx + 31.32);
	return fract((p.x + p.y) * p.z);
}

void vertex() {
	float taper = INSTANCE_CUSTOM.x;
	VERTEX.xz *= mix(1.0, taper, VERTEX.y);
	v_corner = (MODEL_MATRIX * vec4(UV.x, 0.0, UV.y, 1.0)).xyz;
	v_edge = (MODEL_MATRIX * vec4(UV2.x, 0.0, UV2.y, 0.0)).xyz;
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	v_inst = INSTANCE_CUSTOM;
	v_h0 = MODEL_MATRIX[3].y;
	v_h = length(MODEL_MATRIX[1].xyz);
	v_c0 = CUSTOM0;
	v_rim = CUSTOM0.z;
	v_iid = float(INSTANCE_ID);
	v_half = 0.5 * length(MODEL_MATRIX[0].xyz);
}

void fragment() {
	vec3 n = normalize(cross(dFdx(VERTEX), dFdy(VERTEX)));
	if (n.z < 0.0) {
		n = -n;
	}
	NORMAL = n;
	ROUGHNESS = 1.0;
	float seed = v_inst.z;
	float tone = mix(tone_min, tone_max, fract(v_c0.x + seed * 7.13));
	bool roof = v_c0.y > 0.5;
	vec3 base = COLOR.rgb * tone * (roof ? roof_gain : 1.0);
	vec3 em = vec3(0.0);
	float z = v_world.y - v_h0;
	if (!roof) {
		// Ledges every ledge_every BU (the concept's beams at 3.9, 9.9, ...).
		if (detail >= 1 && v_h > 7.0) {
			float lz = mod(z - (ledge_every * 0.5 + 0.9), ledge_every);
			if (lz < ledge_bu * 2.0 && z < v_h - 1.0) {
				base *= 0.8;
			}
		}
		float L = length(v_edge);
		if (v_inst.x > 0.99 && v_h > 2.4 && L > 1.2) {
			vec3 t = v_edge / L;
			float along = dot(v_world - v_corner, t);
			float nx = floor((L - 0.6) / window_pitch.x);
			float nz = floor((v_h - window_first) / window_pitch.y);
			float ui = floor((along - 0.7) / window_pitch.x);
			float lu = along - 0.7 - ui * window_pitch.x;
			float vi = floor((z - window_first) / window_pitch.y);
			float lv = z - window_first - vi * window_pitch.y;
			if (ui >= 0.0 && ui < nx && vi >= 0.0 && vi < nz && lu < window_size.x && lv < window_size.y) {
				vec3 key = vec3(ui + floor(v_corner.x * 3.0), vi + floor(v_corner.z * 3.0), seed * 977.0);
				float r = hash1(key);
				float share = v_inst.w > 0.5 ? 0.6 : window_share;
				if (r < share) {
					int ci = int(hash1(key + 17.0) * 6.0) % 6;
					vec3 wc = v_inst.w > 0.5 && hash1(key + 5.0) < 0.8 ? vec3(0.95, 0.24, 0.22) : window_colors[ci];
					float s = window_dim_min + (1.0 - window_dim_min) * hash1(key + 9.0);
					em = wc * s * window_gain;
					base = wc * s * 0.25;
				}
			}
		}
		// Transit detail: a lit shopfront band at street level on some faces.
		if (detail >= 2 && v_h0 < 0.5 && z > 0.15 && z < 1.05 && L > 2.5) {
			float r = hash1(vec3(floor(v_corner.x * 5.0), floor(v_corner.z * 5.0), seed * 31.0));
			if (r < 0.55) {
				float along = dot(v_world - v_corner, v_edge / L);
				if (along > 0.4 && along < L - 0.4) {
					int ci = int(hash1(vec3(r * 91.0, 3.0, 1.0)) * 4.0);
					vec3 sc = ci == 0 ? vec3(1.0, 0.75, 0.45) : (ci == 1 ? vec3(1.0, 0.5, 0.8) : (ci == 2 ? vec3(0.5, 0.9, 1.0) : vec3(1.0, 0.85, 0.6)));
					em = sc * 0.8;
				}
			}
		}
	} else if (v_inst.y > 0.5) {
		// Neon roof trim in the building's ink: the rim of the roof fan.
		float dist = (1.0 - v_rim) * v_half * v_inst.x;
		float px = fwidth(v_rim) * v_half * v_inst.x;
		if (dist < max(trim_bu, px * 1.5)) {
			int ii = clamp(int(v_inst.y) - 1, 0, 15);
			em = ink_colors[ii] * neon_gain;
			base = ink_colors[ii] * 0.3;
		}
	}
	ALBEDO = base;
	vec3 nw = normalize((INV_VIEW_MATRIX * vec4(n, 0.0)).xyz);
	vec3 spill = toon_spill(v_world, nw, ramp_edges.x, ramp_edges.y, spill_mid, spill_low);
	EMISSION = em + base * spill * spill_gain;
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	int b = toon_band_index(ndl, ramp_edges.x, ramp_edges.y);
	vec3 band = b == 0 ? ramp_shadow : (b == 1 ? ramp_mid : ramp_lit);
	DIFFUSE_LIGHT = band;
}
