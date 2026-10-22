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
#include "res://shaders/lib/netrun_clock.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"
// LOOK Solace THE BLOOM (A Necrosis): the skin over the street's buildings and ground (strength 0 = the shader as before).
#define BL_STREET
#include "res://shaders/city/bloom_necrosis.gdshaderinc"
// LOOK-TOOLBOX module 11 (designer DIRECTION_REVIEW f4678fca, b727956a): each neon tube's hot core, rcl_neon_hot. Values =
// addons/rc_look/config/look_sign.tres "hot" (pinned by test_rc_look_sign).
uniform float neon_hot = 0.90;
uniform float neon_core_share = 0.35;
uniform float neon_core_min_px = 1.00;
uniform float neon_core_tint = 0.15;
uniform vec3 neon_core_col = vec3(1.0);
uniform float neon_core_thin_px = 3.00;
uniform float neon_core_thin_hot = 0.45;

uniform vec3 ramp_shadow;
uniform vec3 ramp_mid;
uniform vec3 ramp_lit;
uniform vec2 ramp_edges = vec2(0.118, 0.363);
uniform float tone_min = 0.86;
uniform float tone_max = 1.12;
uniform float roof_gain = 1.08;
uniform vec3 window_colors[6];
// LOOK L5 (whole-city night): the territory's corporation, carried in COLOR.a as 1 - index / 8 (1 = none; CityMeshKit
// instance_buffer): its colour pulls the lit windows (terr_win_k) and lights the facades faintly (terr_wall_emit).
uniform vec3 terr_colors[5];
uniform float terr_win_k = 0.0;
uniform float terr_wall_emit = 0.0;
// ... and tints the facades toward it at the same brightness (the plate's districts read by colour by day too).
uniform float terr_albedo_k = 0.0;
uniform vec2 window_pitch = vec2(1.6, 1.9);
uniform vec2 window_size = vec2(0.8, 0.7);
uniform float window_first = 1.6;
uniform float window_share = 0.3;
uniform float window_dim_min = 0.5;
uniform float window_gain = 1.0;
uniform vec3 ink_colors[16];
uniform float trim_bu = 0.22;
// LOOK L5: the roof trim's least width in pixels (1.5 keeps it a line at any zoom; 0 lets it fall under a pixel at the
// whole-city pose, where it otherwise paints whole small roofs in the ink).
uniform float trim_px_min = 1.5;
// LOOK L5: the facade's foot darkened to `foot_dark` of its albedo, rising to full over `foot_h_bu` (the plate's deep street
// canyons; 1.0 = off).
uniform float foot_dark = 1.0;
uniform float foot_h_bu = 12.0;
uniform float neon_gain = 1.2;
uniform float ledge_every = 6.0;
uniform float ledge_bu = 0.16;
// 0 city, 1 raid, 2 transit (CityLod.Detail).
uniform int detail = 0;
// Light spill: the shadow / mid bands' share of a source's light, and its emission share.
uniform float spill_mid = 0.62;
uniform float spill_low = 0.32;
uniform float spill_gain = 1.9;

// AAA-2 PBR (A-022 / MATERIAL_SPEC 4; values from `CityShaderConfigData.aaa.pbr`, used above look_blend 0 only): concrete
// (rough, spec IOR level, metal), the glass of the unlit window panes (colour, rough, metal, spec, tone range) and the gains on
// the diffuse and specular of every light (the moon, the street's coloured local lights).
uniform vec3 pbr_concrete = vec3(0.55, 0.0, 0.5);
uniform vec3 pbr_glass = vec3(0.12, 0.2, 1.0);
uniform vec3 glass_col = vec3(0.22, 0.26, 0.34);
uniform vec2 glass_tone = vec2(0.8, 1.2);
// The six concrete colour families of the plates (MATERIAL_SPEC 3), picked per building by its seed; blended in by look_blend.
uniform vec3 concrete_fam[6];
uniform float pbr_diffuse_k = 1.0;
uniform float pbr_spec_k = 1.0;
// The wet top of a cut near-side block (MATERIAL_SPEC 7: the plinth tops take the street's wet recipe): value-noise roughness
// `wet_rough_noise` -> `wet_rough` at `wet_noise_scale`, spec `wet_spec`; the base colour is (plinth_albedo, plinth_albedo, plinth_albedo * plinth_blue).
uniform float wet_noise_scale = 0.09;
uniform vec2 wet_rough_noise = vec2(0.45, 0.6);
uniform vec2 wet_rough = vec2(0.3, 0.03);
uniform float wet_spec = 0.7;
// (rough, metal, spec) of this fragment for light().
varying vec3 v_pbr;

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
// LOOK L5 (whole city, the plate's neon signage): above 0 this share of the off-territory facade faces carries one vertical
// sign strip, sign_w BU wide from sign_z0 to sign_z1 of the height, in one of sign_colors, lit at sign_emit (x look_blend).
uniform float sign_share = 0.0;
uniform float sign_emit = 3.0;
uniform float sign_w = 1.0;
uniform float sign_z0 = 0.3;
uniform float sign_z1 = 0.85;
uniform vec3 sign_colors[4];
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
// NA-22d: the trims fade in over smoothstep(edge_blend.x, edge_blend.y, look_blend), so frames below x stay clean.
uniform vec2 edge_blend = vec2(0.3, 0.8);
// NA-23c floor-band trims (the street netrun): a thin emissive band on the walls every `band_every` BU (first at `band_first` plus a
// per-building phase of up to one `band_every`),
// `band_bu` thick, on `band_share` of the buildings (by seed), in the edge hues; `band_emit` 0 = none (the default).
uniform float band_emit = 0.0;
uniform float band_every = 11.4;
uniform float band_first = 7.6;
uniform float band_bu = 0.2;
uniform float band_share = 0.5;
// Depth haze (spec 4.1 cityglow, perspective views only): colour, density per BU of view distance, height e-fold (BU above the
// local ground) and the share of the haze the highest parts keep.
uniform vec3 haze_col = vec3(0.0);
uniform float haze_k = 0.0;
uniform float haze_h = 30.0;
uniform float haze_hi = 0.15;
// LOOK L5 (whole city): the view distance (BU) the haze starts at (0 = at the eye); the whole-city pose sets its target's.
uniform float haze_d0 = 0.0;
// The id pass (PIPELINE_SPEC 12.0): unlit class colour in R, G = 255 and B = 0 for a cut / ghosted / dissolved building.
uniform bool id_mode = false;
uniform float id_class = 2.0;
// NA-23: the route rooms. A route building (instance bit `route`) loses the pixels of its walls inside a room volume
// (`room_box` = plan x0, y0, x1, y1; `room_z` = height range; plan y = -world z), so the room's own mesh shows as a lit
// window. `room_n` of the 32 slots are used.
const int ROOM_MAX = 32;
uniform int room_n = 0;
uniform vec4 room_box[32];
uniform vec2 room_z[32];
// NA-25b: how far each room's window has dissolved open, 0 = the closed facade, 1 = the window cut. Between, the facade breaks into
// binary bits (ART_BIBLE 1.2: 0 / 1 glyphs in the window colour, white-hot for the first `bit_hot` share of a cell's life, flipping 0 <-> 1
// at `bit_flip` Hz, pulled toward the room, never shrunk: they thin out as cells finish); cells (a 5 x 7 glyph, `bit_px` tall on screen) go in a staggered order, the glyph's pixels stay
// and the rest of the cell is cut, so the room shows through. The room mesh behind comes up with the same share.
uniform float room_open[32];
// NA-25b r5: the glyph height (render px at 1080p), its box (half width / cell size as shares of that height), the stroke share, and the
// white share of the stroke's core. The 0 / 1 are drawn analytically (bit_glyph), so they stay crisp at any size.
uniform float bit_px = 12.0;
uniform float bit_core = 0.7;
const vec2 BIT_CELL = vec2(1.0, 1.4);
const float BIT_HALF_W = 0.3;
const float BIT_STROKE = 0.17;
uniform float bit_hot = 0.3;
uniform float bit_flip = 14.0;
uniform float bit_gain = 2.4;
// the netrun clock (NetrunShaderKit.set_clock via RouteRig): the bits flip on anim_t, held at anim_t_frozen under reduce effects
uniform float anim_t = 0.0;
uniform float anim_t_frozen = 0.0;

// LOOK Solace S1 (CitySolaceKit): the Solace building kits. A mesh vertex with CUSTOM0.w > 0 is a kit part: its height is
// UV.y * h + UV.x * u (u = the lot's shorter side, so caps and spheres keep their shape), x / z scale by u; CUSTOM0.w is the part
// code (1 body with ribbon bands, 2 lime glass, 3 pink nucleus, 4 porcelain, 5 clinic wall, 6 cap, 7 lime ring, 8 terrace).
uniform vec3 kit_lime = vec3(0.588, 1.0, 0.275);
uniform vec3 kit_pink = vec3(1.0, 0.275, 0.588);
uniform vec3 kit_porcelain = vec3(0.74, 0.70, 0.62);
uniform vec3 kit_leaf = vec3(0.30, 0.78, 0.30);
uniform vec3 kit_body = vec3(0.12, 0.26, 0.22);
uniform vec3 kit_dome = vec3(0.14, 0.34, 0.24);
uniform vec3 kit_terrace = vec3(0.20, 0.42, 0.22);
// Ribbon bands: pitch (BU), lit share, pink share, dark share. Clinic bands: pitch, glass share.
uniform vec4 kit_band = vec4(2.0, 0.5, 0.16, 0.1);
uniform vec2 kit_clinic_band = vec2(2.6, 0.55);
uniform float kit_emit = 1.0;
uniform float kit_glass_emit = 0.5;
uniform float kit_nucleus_emit = 1.1;
uniform float kit_clinic_emit = 0.6;
uniform float kit_porcelain_glow = 0.12;
uniform vec4 hq_pool = vec4(0.0);      // LOOK Solace HQ (aaa2 page): the helix' soft green wash on the nearest facades: xyz centre (world), w radius (BU)
uniform vec3 hq_pool_col = vec3(0.0);   // its colour times gain (0 = off)
uniform float kit_band_k = 1.0;  // aaa2 page: the kit bands' emission factor
uniform float kit_dark = 1.0;  // LOOK Solace HQ (aaa2 page only): the kits' albedo factor, so dark bodies carry their lit stripes

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
	if (CUSTOM0.w > 0.5) {
		float kx = length(MODEL_MATRIX[0].xyz);
		float kz = length(MODEL_MATRIX[2].xyz);
		float ku = min(kx, kz);
		VERTEX.x *= ku / kx;
		VERTEX.z *= ku / kz;
		VERTEX.y = max(UV.y + UV.x * ku / max(length(MODEL_MATRIX[1].xyz), 0.01), 0.0);
	} else {
		VERTEX.xz *= mix(1.0, taper, VERTEX.y);
	}
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

// NA-25b r5: how deep inside a 0 / 1 stroke the point `q` (px from the glyph's centre, up positive) is; <= 0 is outside. `hb` the half box.
float bit_seg(vec2 p, vec2 a, vec2 b) {
	vec2 pa = p - a;
	vec2 ba = b - a;
	return length(pa - ba * clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0));
}

float bit_glyph(vec2 q, vec2 hb, float sw, bool one) {
	float half_s = sw * 0.5;
	if (!one) {
		float e = (length(q / hb) - 1.0) * min(hb.x, hb.y);
		return half_s - abs(e + half_s);
	}
	float stem = (abs(q.y) < hb.y) ? half_s - abs(q.x) : -1.0;
	float flag = half_s - bit_seg(q, vec2(0.0, hb.y), vec2(-hb.x, hb.y * 0.45));
	float foot = (abs(q.x) < hb.x * 0.9) ? half_s * 0.8 - abs(q.y + hb.y - half_s * 0.8) : -1.0;
	return max(stem, max(flag, foot));
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
	float neon_px = max(length(dFdx(v_world)), length(dFdy(v_world)));  // one pixel in BU (the neon cores)
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
	bool route_bld = look_blend > 0.0 && ((bits >> 22) & 1) == 1;
	float bit_k = 0.0;
	vec3 bit_ctr = vec3(0.0);
	bool bit_on = false;
	vec3 bit_em = vec3(0.0);
	if (route_bld && room_n > 0) {
		vec3 pw = vec3(v_world.x, -v_world.z, v_world.y);
		for (int i = 0; i < ROOM_MAX; i++) {
			if (i >= room_n) {
				break;
			}
			vec4 bx = room_box[i];
			vec2 zr = room_z[i];
			if (pw.x > bx.x && pw.x < bx.z && pw.y > bx.y && pw.y < bx.w && pw.z > zr.x && pw.z < zr.y) {
				if (room_open[i] >= 0.999) {
					discard;
				}
				if (room_open[i] > 0.0) {
					bit_k = room_open[i];
					bit_ctr = vec3((bx.x + bx.z) * 0.5, (bx.y + bx.w) * 0.5, (zr.x + zr.y) * 0.5);
				}
			}
		}
		if (bit_k > 0.0) {
			float tl = max(length(v_edge), 0.0001);
			vec3 tt = v_edge / tl;
			// NA-25b r5: a cell holds one glyph `bit_px` tall on screen at 1080p, at any zoom (px_per_bu: render px per BU on this wall).
			float gh = bit_px * VIEWPORT_SIZE.y / 1080.0;
			float ppb = max(abs(PROJECTION_MATRIX[1][1]) * VIEWPORT_SIZE.y * 0.5 / (persp ? view_d : 1.0), 0.001);
			vec2 cell_px = gh * BIT_CELL;
			vec2 cell = vec2(dot(v_world - v_corner, tt), v_world.y) * ppb / cell_px;
			vec2 ci = floor(cell);
			float h = hash1(vec3(ci, v_inst.z * 13.0));
			float tc = clamp((bit_k - h * 0.6) / 0.4, 0.0, 1.0);
			if (tc >= 1.0) {
				discard;
			}
			if (tc > 0.0) {
				vec3 cw = vec3(bit_ctr.x, bit_ctr.z, -bit_ctr.y);
				vec2 cc = (ci + 0.5) * cell_px / ppb;
				vec2 to_room = vec2(dot(cw - v_corner, tt), cw.y) - cc;
				vec2 off = normalize(to_room + vec2(0.0001)) * 0.35 * tc * tc;
				// The glyphs keep their size and thin out (cells finish and are cut), they never shrink into dots.
				vec2 q = (fract(cell) - 0.5 - off) * cell_px;
				bool one = (int(floor(nr_clock(anim_t, anim_t_frozen) * bit_flip * (0.6 + h) + h * 7.0)) & 1) == 1;
				float sw = max(gh * BIT_STROKE, 1.0);
				float depth = bit_glyph(q, vec2(gh * BIT_HALF_W, gh * 0.5), sw, one);
				if (depth <= 0.0) {
					discard;
				}
				// Emission core: the middle of the stroke burns whiter than its edge.
				float core = smoothstep(0.0, sw * 0.5, depth);
				bit_on = true;
				bit_em = mix(tc < bit_hot ? vec3(1.0) : window_colors[int(h * 6.0) % 6], vec3(1.0), core * bit_core) * bit_gain;
			}
		}
	}
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
	// NA-25b r3 (art-pass A-019): a ghosted building is see-through (7.1), so its inner walls keep the facade look; the flat poche is for a
	// cut that is not ghosted (the section, a cut at full opacity). A ghost easing in or out was a solid black windowless prism.
	bool poche_face = !FRONT_FACING && was_cut && !ghosted;
	float seed = v_inst.z;
	// AAA-2: the per-triangle tone jitter is Eevee-only in the plates (Cycles ignores it): the facets show by their own light.
	float tone = mix(mix(tone_min, tone_max, fract(v_c0.x + seed * 7.13)), 1.0, look_blend);
	bool roof = v_c0.y > 0.5;
	vec3 body = COLOR.rgb;
	if (look_blend > 0.0) {
		body = mix(body, concrete_fam[int(floor(fract(seed * 17.31) * 6.0)) % 6], look_blend);
	}
	vec3 base = body * tone * (roof ? roof_gain : 1.0) * mix(1.0, facade_albedo, look_blend);
	int terr_i = int(floor((1.0 - COLOR.a) * 8.0 + 0.5));
	vec3 terr_c = terr_i > 0 ? terr_colors[min(terr_i - 1, 4)] : vec3(0.0);
	if (terr_i > 0 && terr_albedo_k > 0.0) {
		vec3 lw = vec3(0.2126, 0.7152, 0.0722);
		base = mix(base, terr_c * dot(base, lw) / max(dot(terr_c, lw), 1e-3), terr_albedo_k);
	}
	vec3 em = vec3(0.0);
	float z = zl;
	bool edge_px = false;
	v_pbr = pbr_concrete;
	int kit = int(floor(v_c0.w + 0.5));
	if (kit > 0) {
		vec3 kb = kit_body;
		if (kit == 1) {
			float bp = max(kit_band.x, 0.1);
			float bi = floor(zl / bp + seed * 7.0);
			float bf = fract(zl / bp + seed * 7.0);
			float bh = hash1(vec3(bi, seed * 31.0, 5.0));
			if (bf < kit_band.y && bh >= kit_band.w) {
				vec3 bc = hash1(vec3(bi, seed * 17.0, 9.0)) < kit_band.z ? kit_pink : kit_lime;
				em = bc * kit_emit * kit_band_k * (0.85 + 0.3 * hash1(vec3(bi, seed, 3.0)));
				kb = bc * 0.3;
			}
			base = kb * tone;
		} else if (kit == 2) {
			// LOOK Solace cells: dark green glass, shaded, a lime rim light (the concept's cells), not a flat lime blob.
			float rim = pow(1.0 - clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0), 2.2);
			base = kit_leaf * 0.2 * tone;
			em = kit_lime * kit_emit * kit_glass_emit * (0.10 + 1.1 * rim) * (0.85 + 0.3 * tone);
		} else if (kit == 3) {
			base = kit_pink * 0.18 * tone;
			em = kit_pink * kit_emit * kit_nucleus_emit * 0.7;
		} else if (kit == 4) {
			base = kit_porcelain * tone;
			em = kit_porcelain * kit_porcelain_glow * kit_emit * kit_dark;
		} else if (kit == 5) {
			float cp = max(kit_clinic_band.x, 0.1);
			float cf = fract(zl / cp + seed * 5.0);
			if (cf < kit_clinic_band.y && zl > 0.8) {
				base = kit_leaf * 0.55 * tone;
				em = kit_leaf * kit_emit * kit_clinic_emit;
			} else {
				base = kit_porcelain * tone;
				em = kit_porcelain * kit_porcelain_glow * kit_emit * kit_dark;
			}
		} else if (kit == 6) {
			base = kit_dome * tone;
			em = kit_lime * kit_emit * 0.05;
		} else if (kit == 7) {
			base = kit_lime * 0.4;
			em = kit_lime * kit_emit * 1.6;
		} else {
			base = kit_terrace * tone;
		}
		base *= kit_dark;
	} else if (!roof) {
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
			if (look_blend > 0.0 && L > 1.55) {
				// NA-23c: a narrow face still carries one column of the carpet (the netrun look; the page at 0 is unchanged).
				nx = max(nx, 1.0);
			}
			float nz = floor((v_h - window_first) / window_pitch.y);
			float ui = floor((along - 0.7) / window_pitch.x);
			float lu = along - 0.7 - ui * window_pitch.x;
			float vi = floor((z - window_first) / window_pitch.y);
			float lv = z - window_first - vi * window_pitch.y;
			if (look_blend > 0.0) {
				// NA-23c bay rhythm: each window sits at its own offset inside its cell (per column and 3-floor band), the same size.
				float bnd = floor((vi + floor(hash1(vec3(seed * 8.3, 4.0, 2.0)) * 3.0)) / 3.0);
				lu -= hash1(vec3(ui, bnd, seed * 2.1)) * (window_pitch.x - window_size.x);
				lv -= hash1(vec3(vi, seed * 6.7, 3.0)) * (window_pitch.y - window_size.y);
			}
			if (ui >= 0.0 && ui < nx && vi >= 0.0 && vi < nz && lu >= 0.0 && lv >= 0.0 && lu < window_size.x && lv < window_size.y) {
				vec3 key = vec3(ui + floor(v_corner.x * 3.0), vi + floor(v_corner.z * 3.0), seed * 977.0);
				float r = hash1(key);
				if (look_blend > 0.0) {
					// An unlit pane is glass (AAA-2: its own colour, tone, rough, metal); a lit one below overwrites it with light.
					base = mix(base, glass_col * mix(glass_tone.x, glass_tone.y, hash1(key + 3.0)), look_blend);
					v_pbr = mix(pbr_concrete, vec3(pbr_glass.x, pbr_glass.y, pbr_glass.z), look_blend);
				}
				float share = v_crest > 0.5 ? 0.6 : mix(window_share, win_share, look_blend);
				if (look_blend > 0.0 && v_crest < 0.5) {
					// NA-23c (art-pass r2_facade.py, repetition.guard): a lit fraction per building, floor bands of 3 floors that are dark
					// or fully lit, and skipped columns on wide faces. Same window size; the page at 0 keeps its grid.
					float lit = mix(0.55, 1.0, hash1(vec3(seed * 5.7, 1.0, 3.0)));
					float band = floor((vi + floor(hash1(vec3(seed * 8.3, 4.0, 2.0)) * 3.0)) / 3.0);
					float bh = hash1(vec3(band, seed * 13.1, 7.0));
					float bm = bh < 0.22 ? 0.12 : (bh > 0.8 ? 2.0 : 1.0);
					float skip = (L > 5.0 && hash1(vec3(ui, band * 0.37, seed * 3.3)) < 0.2) ? 0.0 : 1.0;
					share = mix(share, min(lit * bm, 1.0) * skip, look_blend);
				}
				if (r < share) {
					int ci = int(hash1(key + 17.0) * 6.0) % 6;
					vec3 wc = v_crest > 0.5 && hash1(key + 5.0) < 0.8 ? vec3(0.95, 0.24, 0.22) : window_colors[ci];
					float s = window_dim_min + (1.0 - window_dim_min) * hash1(key + 9.0);
					float s_nr = win_floor + (1.0 - win_floor) * pow(hash1(key + 9.0), win_pow);
					s = mix(s, s_nr, look_blend);
					if (terr_i > 0) {
						wc = mix(wc, terr_c * max(max(wc.r, wc.g), wc.b) / max(max(max(terr_c.r, terr_c.g), terr_c.b), 1e-3), terr_win_k);
					}
					em = wc * s * window_gain * mix(1.0, win_emit, look_blend);
					base = wc * s * 0.25;
				}
			}
		}
		if (sign_share > 0.0 && look_blend > 0.0 && terr_i == 0 && L > sign_w + 0.4 && v_h > 3.0) {
			float hs = hash1(vec3(floor(v_corner.x * 3.0), floor(v_corner.z * 3.0), seed * 53.0));
			if (hs < sign_share) {
				float sa = dot(v_world - v_corner, v_edge / L);
				float a0 = 0.2 + hash1(vec3(hs * 71.0, seed, 2.0)) * (L - sign_w - 0.4);
				if (sa > a0 && sa < a0 + sign_w && z > sign_z0 * v_h && z < sign_z1 * v_h) {
					vec3 sgc = sign_colors[int(hash1(vec3(hs * 13.0, seed * 7.0, 9.0)) * 4.0) % 4];
					em = rcl_neon_hot(sgc, abs(sa - (a0 + sign_w * 0.5)), sign_w * 0.5, neon_px, neon_hot, neon_core_share, neon_core_min_px, neon_core_col, neon_core_tint, neon_core_thin_px, neon_core_thin_hot) * sign_emit * look_blend;
					base = sgc * 0.2;
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
		float tw = max(trim_bu, px * trim_px_min);
		if (dist < tw) {
			int ii = clamp(int(v_inst.y) - 1, 0, 15);
			em = rcl_neon_hot(ink_colors[ii], abs(dist - tw * 0.5), tw * 0.5, neon_px, neon_hot, neon_core_share, neon_core_min_px, neon_core_col, neon_core_tint, neon_core_thin_px, neon_core_thin_hot) * neon_gain * mix(1.0, trim_emit, look_blend);
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
			float ed = 0.0;
			float eh = edge_bu * 0.5;
			if (roof) {
				float rd = (1.0 - v_rim) * v_half * v_inst.x;
				float rpx = fwidth(v_rim) * v_half * v_inst.x;
				float ew = max(edge_bu, rpx * 1.5);
				on_edge = rd < ew;
				eh = ew * 0.5;
				ed = abs(rd - eh);
			} else {
				on_edge = (v_h - zl) < edge_bu;
				ed = abs((v_h - zl) - eh);
			}
			if (on_edge) {
				float eb = smoothstep(edge_blend.x, edge_blend.y, look_blend);
				em += rcl_neon_hot(ec, ed, eh, neon_px, neon_hot, neon_core_share, neon_core_min_px, neon_core_col, neon_core_tint, neon_core_thin_px, neon_core_thin_hot) * edge_emit * eb;
				base = mix(base, ec * 0.3, eb);
			}
		}
	}
	if (look_blend > 0.0 && band_emit > 0.0 && !roof && hash1(vec3(seed * 53.7, 1.0, 6.0)) < band_share) {
		float b0 = band_first + hash1(vec3(seed * 19.3, 2.0, 5.0)) * band_every;
		float bz = mod(zl - b0, band_every);
		if (zl >= b0 && bz < band_bu && zl < v_h - 0.5) {
			vec3 bc = hash1(vec3(seed * 71.9, 3.0, 8.0)) < 0.5 ? edge_a : edge_b;
			float bb = smoothstep(edge_blend.x, edge_blend.y, look_blend);
			em += rcl_neon_hot(bc, abs(bz - band_bu * 0.5), band_bu * 0.5, neon_px, neon_hot, neon_core_share, neon_core_min_px, neon_core_col, neon_core_tint, neon_core_thin_px, neon_core_thin_hot) * band_emit * bb;
			base = mix(base, bc * 0.3, bb);
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
		float hz = (1.0 - exp(-max(view_d - haze_d0, 0.0) * haze_k)) * mix(1.0, haze_hi, 1.0 - exp(-max(zl, 0.0) / haze_h)) * look_blend;
		base *= 1.0 - hz;
		em = em * (1.0 - hz) + haze_col * hz;
	}
	if (!roof && foot_dark < 1.0) {
		base *= mix(foot_dark, 1.0, smoothstep(0.0, foot_h_bu, zl));
	}
	if (hq_pool.w > 0.0) {
		float pf = clamp(1.0 - length(v_world - hq_pool.xyz) / hq_pool.w, 0.0, 1.0);
		em += hq_pool_col * pf * pf * look_blend;
	}
	ALBEDO = base;
	vec3 nw = normalize((INV_VIEW_MATRIX * vec4(n, 0.0)).xyz);
	vec3 spill = toon_spill(v_world, nw, ramp_edges.x, ramp_edges.y, spill_mid, spill_low);
	EMISSION = (em + base * spill * spill_gain + terr_c * terr_wall_emit) * emission_multiplier;
	if (poche_face) {
		// The open top of a cut building: its back faces show the near-black poche.
		ALBEDO = poche;
		EMISSION = vec3(0.0);
		if (look_blend > 0.0) {
			// AAA-2: the cut top is a wet plinth top: (a, a, 1.2 a), a puddle roughness by noise, spec 0.7, an up normal: it takes the
			// lamps' pools and the SSR reflections of the street like the ground does.
			float wn = 0.0;
			float wa = 0.5;
			vec3 wp = vec3(v_world.x, 0.0, v_world.z) * wet_noise_scale;
			for (int i = 0; i < 5; i++) {
				wn += wa * nr_noise3(wp);
				wp *= 2.0;
				wa *= 0.5;
			}
			wn /= 0.96875;
			float wr = mix(wet_rough.x, wet_rough.y, smoothstep(wet_rough_noise.x, wet_rough_noise.y, wn));
			ALBEDO = mix(poche, vec3(plinth_albedo, plinth_albedo, plinth_albedo * plinth_blue), look_blend);
			NORMAL = normalize((VIEW_MATRIX * vec4(0.0, 1.0, 0.0, 0.0)).xyz);
			ROUGHNESS = wr;
			SPECULAR = wet_spec;
			v_pbr = vec3(wr, 0.0, wet_spec);
		}
	}
	if (bl_strength > 0.0 && !bit_on && !id_mode) {
		float blf = bl_apply_street(v_world, ALBEDO, EMISSION);
		v_pbr = vec3(mix(v_pbr.x, bl_rough, blf), v_pbr.y * (1.0 - blf), v_pbr.z * (1.0 - blf));
	}
	if (bit_on) {
		ALBEDO = vec3(0.0);
		EMISSION = bit_em;
	}
	if (id_mode) {
		ALBEDO = vec3(0.0);
		// A route building is a room column: its walls are class 2 with B > 0 (12.6 reads them as cut surfaces, not occluders).
		EMISSION = id_lin(vec3(id_class, (occ_cut || ghosted || dissolved) ? 255.0 : 0.0, route_bld ? 1.0 : 0.0) / 255.0);
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
	if (look_blend <= 0.0) {
		DIFFUSE_LIGHT = id_mode ? vec3(0.0) : band;
	} else if (id_mode) {
		DIFFUSE_LIGHT = vec3(0.0);
	} else {
		// AAA-2: a Lambert diffuse and a GGX specular (rough / metal / spec of the fragment) of the light's own colour, added per light
	// (the moon, the street's coloured local lights). At look_blend 1 the toon ramp is gone; between, the ramp fades out.
	vec3 lc = LIGHT_COLOR * ATTENUATION;
	float nl = max(dot(NORMAL, LIGHT), 0.0);
	float rough = max(v_pbr.x, 0.04);
	float metal = v_pbr.y;
	float a = rough * rough;
	vec3 h = normalize(LIGHT + VIEW);
	float nh = max(dot(NORMAL, h), 0.0);
	float vh = max(dot(VIEW, h), 0.0);
	float nv = max(dot(NORMAL, VIEW), 0.001);
	float dd = a * a / (3.14159265 * pow(nh * nh * (a * a - 1.0) + 1.0, 2.0));
	float k = (rough + 1.0) * (rough + 1.0) / 8.0;
	float gg = (nl / (nl * (1.0 - k) + k)) * (nv / (nv * (1.0 - k) + k));
	vec3 f0 = mix(vec3(0.08 * v_pbr.z), ALBEDO, metal);
	vec3 fr = f0 + (vec3(1.0) - f0) * pow(1.0 - vh, 5.0);
	vec3 spec = dd * gg * fr / max(4.0 * nl * nv, 0.001) * nl;
	vec3 pbr_d = lc * nl * (1.0 - metal) * pbr_diffuse_k;
	DIFFUSE_LIGHT += mix(band * mix(1.0, facade_light, look_blend), pbr_d, look_blend);
	SPECULAR_LIGHT += lc * spec * pbr_spec_k * look_blend;
	}
}
