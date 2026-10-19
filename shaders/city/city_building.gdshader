// ART-5 5a (from ART-1 1D's spike): Cv2 faceted buildings with the E 3-band toon ramp (target_corps.mat_toon:
// colour * ramp(band of N.L with shadow) * tone jitter per triangle), procedural window
// grid, ledges, shopfronts and the neon roof trim (unified40.city_building). Prototype of
// the shared toon material: the bands and the light spill come from 1B's kit include
// (shaders/kit/toon_bands.gdshaderinc, ToonInkMaterial.set_spill feeds it); the ink is the
// city's post pass (city_post.gdshader), not the hull (it splits at hard corners). Instances: MultiMesh,
// COLOR = base colour, INSTANCE_CUSTOM = (taper, trim ink index + 1 or 0, seed 0-1, crest + 2 * packed occlusion state).
// NA-22 (netrun look): look_blend 0 is the page above, unchanged. Above 0 the per-instance cut / Bayer ghost / dissolve
// in INSTANCE_CUSTOM.w apply (PIPELINE_SPEC 7.4; NetrunInstancePack is the CPU side), the toon ramp blends to a smooth
// lambert ramp, and the street section (5.3) clips by `sec_on` / `z_cut`. Uniform table: NA22_SHADER_PARAMS.md.
shader_type spatial;
render_mode cull_disabled, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
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

// NA-22. 0 = the mainline page, 1 = the netrun (AAA-2) look. The per-instance cut / ghost / dissolve start above 0.
uniform float look_blend = 0.0;
// Scales every emissive output (windows, trims, shopfronts, spill, ghost edges); 1 = as before.
uniform float emission_multiplier = 1.0;
// Street section (PIPELINE_SPEC 5.3): the corridor beside the street segment a -> c (plan x, y; plan y = -world Z), the
// camera side is dot(p - a, nrm) < sec_side, along the street -pad .. len + pad. Above ground + z_cut nothing is drawn;
// beyond the camera-side kerb (plinth_off) and below the cut the block goes near-black and wet, switching on as z_cut
// falls from plinth_on.x to plinth_on.y.
uniform bool sec_on = false;
uniform vec2 sec_a = vec2(0.0);
uniform vec2 sec_c = vec2(0.0, 1.0);
uniform vec2 sec_nrm = vec2(1.0, 0.0);
uniform float sec_pad = 30.0;
uniform float sec_side = -0.4;
uniform float sec_ground = 0.0;
uniform float z_cut = 10000.0;
uniform vec2 plinth_on = vec2(5.0, 1.5);
uniform float plinth_off = 4.2;
uniform float plinth_albedo = 0.012;
uniform float plinth_blue = 1.2;
// Cut / ghost look: the poche (cut top, back faces), the ghost edge colour, strength, band (BU), and the extra Bayer
// coverage the edge pixels get.
uniform vec3 poche = vec3(0.01, 0.01, 0.013);
uniform vec3 edge_col = vec3(0.55, 0.68, 0.85);
uniform float edge_gain = 0.6;
uniform float edge_band = 0.095;
uniform float edge_boost = 0.22;
// 1 = the windows dim with the ghost opacity, 0 = they stay.
uniform float ghost_dim = 1.0;
// NA-22b (the lights-out street): at look_blend 1 the diffuse facade is near-black and the light comes from the emissives.
// `facade_albedo` / `facade_light` multiply the facade albedo and the diffuse light, `win_share` is the share of windows lit
// (the carpet; any facade face, tapered or not), `win_floor` / `win_pow` the per-window brightness spread, `win_emit` and
// `trim_emit` the emission gains. All blend in with look_blend (0 = the page as before).
uniform float facade_albedo = 1.0;
uniform float facade_light = 1.0;
uniform float win_share = 0.3;
uniform float win_floor = 0.5;
uniform float win_pow = 1.0;
uniform float win_emit = 1.0;
uniform float trim_emit = 1.0;
// NA-22c (the street-level wash, art-pass ruling on W1 NA-22): the lowest floors take the street's sign hues so the facade luma
// rises toward the street. `wash_floors` = floors (window_pitch.y BU each) kept at full strength and floors where it reaches 0
// (the fade), `wash_a` / `wash_b` the two hues (pink, violet; one per building by its seed), `wash_gain` the emission at full
// strength. Applies to every wall, windowed or not. Blends in with look_blend.
uniform vec2 wash_floors = vec2(2.5, 6.5);
uniform vec3 wash_a = vec3(1.0, 0.16, 0.6);
uniform vec3 wash_b = vec3(0.62, 0.38, 1.0);
uniform float wash_gain = 0.0;
// NA-22c edge trims: a thin emissive trim on the roof edge (and the top band of the walls) of `edge_share` of the buildings
// (by seed), cyan (`edge_a`) or pink (`edge_b`), `edge_emit` emission, `edge_bu` wide.
uniform float edge_share = 0.34;
uniform vec3 edge_a = vec3(0.16, 0.8, 1.0);
uniform vec3 edge_b = vec3(1.0, 0.16, 0.6);
uniform float edge_emit = 0.0;
uniform float edge_bu = 0.16;
// Depth haze (spec 4.1 cityglow, perspective views only): colour, density per BU of view distance, height e-fold (BU above the
// local ground) and the share of the haze the highest parts keep.
uniform vec3 haze_col = vec3(0.0);
uniform float haze_k = 0.0;
uniform float haze_h = 30.0;
uniform float haze_hi = 0.15;
// The id pass (PIPELINE_SPEC 12.0): unlit class colour in R, G = 255 and B = 0 for a cut / ghosted / dissolved building.
uniform bool id_mode = false;
uniform float id_class = 2.0;

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

// 4 x 4 Bayer order 0..15 of a pixel (spec 7.4 rule 5); the ghost draws a pixel when its order < the drawn levels.
int bayer4(ivec2 p) {
	int x = p.x & 3;
	int y = p.y & 3;
	int m[16] = int[16](0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5);
	return m[y * 4 + x];
}

vec3 id_lin(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
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
	// The facet normal first: its derivatives must run before any discard or early return.
	vec3 n = normalize(cross(dFdx(VERTEX), dFdy(VERTEX)));
	if (n.z < 0.0) {
		n = -n;
	}
	float view_d = length(VERTEX);
	bool persp = PROJECTION_MATRIX[3][3] < 0.5;
	NORMAL = n;
	ROUGHNESS = 1.0;
	// INSTANCE_CUSTOM.w = crest + 2 * bits (NetrunInstancePack): cut 9, ghost 5, edge 3, dissolve 5 bits. Decoded here, not
	// in vertex(): touching the vertex stage moves a few ink-edge pixels of the old page (parity at look_blend 0).
	int iw = int(floor(v_inst.w + 0.5));
	int bits = iw >> 1;
	float v_crest = float(iw & 1);
	// Cut share, ghost code (16 - drawn Bayer levels), edge strength, dissolve share; none below look_blend > 0.
	vec4 v_occ = look_blend > 0.0 ? vec4(float(bits & 511) / 511.0, float((bits >> 9) & 31), float((bits >> 14) & 7) / 7.0, float((bits >> 17) & 31) / 16.0) : vec4(0.0);
	float zl = v_world.y - v_h0;
	bool occ_cut = v_occ.x > 0.0;
	bool ghosted = v_occ.y > 0.0;
	bool dissolved = v_occ.w > 0.0;
	float cut_h = v_h * (1.0 - v_occ.x);
	if (occ_cut && zl > cut_h) {
		discard;
	}
	bool sec_cutting = false;
	float plinth_w = 0.0;
	if (sec_on) {
		vec2 pp = vec2(v_world.x, -v_world.z);
		vec2 ac = sec_c - sec_a;
		float slen = max(length(ac), 0.0001);
		float s_along = dot(pp - sec_a, ac / slen);
		float s_side = dot(pp - sec_a, sec_nrm);
		if (s_along > -sec_pad && s_along < slen + sec_pad && s_side < sec_side) {
			if (v_world.y > sec_ground + z_cut) {
				discard;
			}
			sec_cutting = z_cut < 1000.0;
			if (s_side < -plinth_off) {
				plinth_w = 1.0 - smoothstep(plinth_on.y, plinth_on.x, z_cut);
			}
		}
	}
	bool was_cut = occ_cut || sec_cutting;
	// Dissolve (route walls): a second Bayer order (transposed), the share v_occ.w of the pixels goes.
	if (dissolved && float(bayer4(ivec2(FRAGCOORD.yx))) < v_occ.w * 16.0) {
		discard;
	}
	float g_open = ghosted ? 1.0 - v_occ.y / 16.0 : 1.0;
	bool poche_face = !FRONT_FACING && was_cut;
	float seed = v_inst.z;
	float tone = mix(tone_min, tone_max, fract(v_c0.x + seed * 7.13));
	bool roof = v_c0.y > 0.5;
	vec3 base = COLOR.rgb * tone * (roof ? roof_gain : 1.0) * mix(1.0, facade_albedo, look_blend);
	vec3 em = vec3(0.0);
	float z = zl;
	bool edge_px = false;
	if (!roof) {
		if (ghosted && v_occ.z > 0.0) {
			float eL = length(v_edge);
			float ea = dot(v_world - v_corner, v_edge / max(eL, 0.0001));
			float ed = min(min(ea, eL - ea), min(v_h, cut_h) - z);
			edge_px = ed < edge_band;
		}
		// Ledges every ledge_every BU (the concept's beams at 3.9, 9.9, ...).
		if (detail >= 1 && v_h > 7.0) {
			float lz = mod(z - (ledge_every * 0.5 + 0.9), ledge_every);
			if (lz < ledge_bu * 2.0 && z < v_h - 1.0) {
				base *= 0.8;
			}
		}
		float L = length(v_edge);
		if ((v_inst.x > 0.99 || look_blend > 0.0) && v_h > 2.4 && L > 1.2) {
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
				float share = v_crest > 0.5 ? 0.6 : mix(window_share, win_share, look_blend);
				if (r < share) {
					int ci = int(hash1(key + 17.0) * 6.0) % 6;
					vec3 wc = v_crest > 0.5 && hash1(key + 5.0) < 0.8 ? vec3(0.95, 0.24, 0.22) : window_colors[ci];
					float s = window_dim_min + (1.0 - window_dim_min) * hash1(key + 9.0);
					float s_nr = win_floor + (1.0 - win_floor) * pow(hash1(key + 9.0), win_pow);
					s = mix(s, s_nr, look_blend);
					em = wc * s * window_gain * mix(1.0, win_emit, look_blend);
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
			em = ink_colors[ii] * neon_gain * mix(1.0, trim_emit, look_blend);
			base = ink_colors[ii] * 0.3;
		}
	}
	if (look_blend > 0.0) {
		// NA-22c: street wash and edge trims, chosen per building from its seed (the layout's look seed, never gameplay RNG).
		float pick = hash1(vec3(seed * 311.7, 5.0, 2.0));
		if (!roof && wash_gain > 0.0) {
			float fl = zl / window_pitch.y;
			float wash = 1.0 - smoothstep(wash_floors.x, wash_floors.y, fl);
			em += mix(wash_a, wash_b, step(0.5, pick)) * wash_gain * wash * look_blend;
		}
		if (edge_emit > 0.0 && hash1(vec3(seed * 137.3, 9.0, 4.0)) < edge_share) {
			vec3 ec = hash1(vec3(seed * 71.9, 3.0, 8.0)) < 0.5 ? edge_a : edge_b;
			bool on_edge = false;
			if (roof) {
				float rd = (1.0 - v_rim) * v_half * v_inst.x;
				float rpx = fwidth(v_rim) * v_half * v_inst.x;
				on_edge = rd < max(edge_bu, rpx * 1.5);
			} else {
				on_edge = (v_h - zl) < edge_bu;
			}
			if (on_edge) {
				em += ec * edge_emit * look_blend;
				base = mix(base, ec * 0.3, look_blend);
			}
		}
	}
	if (plinth_w > 0.0) {
		// Plinth rule (5.3): near-black wet block, no trims, no emission.
		base = mix(base, vec3(plinth_albedo, plinth_albedo, plinth_albedo * plinth_blue), plinth_w);
		em *= 1.0 - plinth_w;
	}
	if (ghosted) {
		// Ghost (7.1 rule 5): windows dim with it, a Bayer 4 x 4 screen door against the opacity, edges stay (boosted).
		em *= mix(1.0, g_open, ghost_dim);
		int drawn = 16 - int(v_occ.y + 0.5);
		int extra = edge_px ? int(edge_boost * 16.0 + 0.5) : 0;
		if (bayer4(ivec2(FRAGCOORD.xy)) >= drawn + extra) {
			discard;
		}
		if (edge_px) {
			em += edge_col * edge_gain * v_occ.z;
		}
	}
	if (persp && look_blend > 0.0 && haze_k > 0.0) {
		// Depth haze: far blocks lose contrast into the glow colour, low parts more than high ones; layers separate by distance.
		float hz = (1.0 - exp(-view_d * haze_k)) * mix(1.0, haze_hi, 1.0 - exp(-max(zl, 0.0) / haze_h)) * look_blend;
		base *= 1.0 - hz;
		em = em * (1.0 - hz) + haze_col * hz;
	}
	ALBEDO = base;
	vec3 nw = normalize((INV_VIEW_MATRIX * vec4(n, 0.0)).xyz);
	vec3 spill = toon_spill(v_world, nw, ramp_edges.x, ramp_edges.y, spill_mid, spill_low);
	EMISSION = (em + base * spill * spill_gain) * emission_multiplier;
	if (poche_face) {
		// The open top of a cut building: its back faces show the near-black poche.
		ALBEDO = poche;
		EMISSION = vec3(0.0);
	}
	if (id_mode) {
		ALBEDO = vec3(0.0);
		EMISSION = id_lin(vec3(id_class, (occ_cut || ghosted || dissolved) ? 255.0 : 0.0, 0.0) / 255.0);
	}
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	int b = toon_band_index(ndl, ramp_edges.x, ramp_edges.y);
	vec3 band = b == 0 ? ramp_shadow : (b == 1 ? ramp_mid : ramp_lit);
	if (look_blend > 0.0) {
		// Toon ramp -> a smooth lambert ramp over the same colours (the AAA-2 PBR diffuse stand-in).
		band = mix(band, mix(ramp_shadow, ramp_lit, clamp(ndl, 0.0, 1.0)), look_blend);
	}
	DIFFUSE_LIGHT = id_mode ? vec3(0.0) : band * mix(1.0, facade_light, look_blend);
}
