// LOOK Solace THE BLOOM, direction A "Necrosis" (designer 2026-10-22): the skin that creeps over the street and the HQ helix, as one shader
// include. A port of art-pass docs/concepts/solace_vertical/bloom/scripts: street3d/bloom3d_mat.py (BL_FIELD / BL_SHADER) for the street
// and hq3d/bloom3d_hq.py (BL_TUBE_FIELD / BL_TUBE_SHADER / BL_WINDIM) for the helix. Art-owned, view side only: it draws a front it is
// GIVEN (the uniforms below); it knows no game state. At `bl_strength` 0 every entry point returns at once, so a shader that includes it
// draws exactly as before.
//
//   #define BL_STREET            // before the include: the street field (a function of the world position in the street frame)
//   #define BL_TUBE              // or: the HQ helix field (tube coordinates z, phi, tower from the compound's plate-unit position)
//   #include "res://shaders/city/bloom_necrosis.gdshaderinc"
//   ...
//   fragment(): bl_apply_street(wp, ALBEDO, EMISSION) / bl_apply_tube(wp, ALBEDO, EMISSION) (the skin: plum body, pink veins, hot hairline
//   edge, the 45 degree hatch), bl_dim_tube(wp, EMISSION) (the window light dying below the front).
//
// Numbers: content in addons/rc_look/config/look_bloom.tres, set on the materials by BloomLook.apply. The structure constants below
// (noise frequencies, thresholds) are the node graphs' own and carry the Blender line they come from. Never colour alone: the front
// reads by its edge (hot hairline) and the hatch too.
#ifndef BLOOM_NECROSIS_INCLUDED
#define BLOOM_NECROSIS_INCLUDED

// 0 = off. Between 0 and 1 the skin's cover is scaled (the look API's `strength`).
uniform float bl_strength = 0.0;
uniform vec3 bl_pink = vec3(1.0, 0.0612, 0.305);   // the vein / edge emission colour (linear)
uniform vec3 bl_plum = vec3(0.075, 0.030, 0.058);  // the body (a diffuse, roughness bl_rough)
uniform float bl_rough = 0.7;
uniform float bl_cover_k = 0.89;     // the skin's share of the original surface at full cover
uniform float bl_veins = 1.1;        // emission strength of the veins / the hot edge / the hatch
uniform float bl_edge_k = 1.4;
uniform float bl_hatch_k = 0.30;
uniform float bl_vein_dens = 0.0;    // shifts the vein density gate up: fewer, sparser veins
uniform float bl_body_emit = 0.0;    // the body's own glow (share of the plum): the street's lit plum under the signs' light
uniform float bl_seed = 7.0;         // the noise seed (the Blender `W`)
uniform float bl_vscale = 0.7;       // vein cell scale (cells per BU) and its line half width in cell units
uniform float bl_vw = 0.045;
uniform float bl_ew = 0.09;          // the hot edge's half width (BU), at least bl_edge_px pixels
uniform float bl_edge_px = 0.0;      // the street's hairline: its half width in pixels (the front stays a thin line at any distance)
uniform float bl_hatch_scale = 2.5;  // hatch lines per BU along the 45 degree diagonal

// Gradient noise gain: Blender's noise node is Perlin scaled to about +-1, this one's random-direction gradients are weaker.
const float BL_NOISE_GAIN = 2.0;
const int BL_BOXES = 128;

struct BlField {
	float cover;   // 0..1, the skin's mask before bl_strength and bl_cover_k (keep-outs already taken out)
	float vein;
	float edge;
	float hatch;
	float ahead;   // veins crawling out ahead of the front over the clean surface (tube only)
	float depth;   // BU behind the local front (positive = infected)
};

vec3 bl_hash3(vec3 p) {
	p = fract(p * vec3(0.1031, 0.1030, 0.0973));
	p += dot(p, p.yxz + 33.33);
	return fract((p.xxy + p.yxx) * p.zyx);
}

float bl_grad(vec3 i, vec3 f) {
	return dot(bl_hash3(i) * 2.0 - 1.0, f);
}

// Perlin-style gradient noise, about -1..1 after the gain.
float bl_pnoise(vec3 p) {
	vec3 i = floor(p);
	vec3 f = p - i;
	vec3 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);
	float a = mix(mix(bl_grad(i, f), bl_grad(i + vec3(1, 0, 0), f - vec3(1, 0, 0)), u.x),
			mix(bl_grad(i + vec3(0, 1, 0), f - vec3(0, 1, 0)), bl_grad(i + vec3(1, 1, 0), f - vec3(1, 1, 0)), u.x), u.y);
	float b = mix(mix(bl_grad(i + vec3(0, 0, 1), f - vec3(0, 0, 1)), bl_grad(i + vec3(1, 0, 1), f - vec3(1, 0, 1)), u.x),
			mix(bl_grad(i + vec3(0, 1, 1), f - vec3(0, 1, 1)), bl_grad(i + vec3(1, 1, 1), f - vec3(1, 1, 1)), u.x), u.y);
	return clamp(mix(a, b, u.z) * BL_NOISE_GAIN, -1.0, 1.0);
}

// Blender's Noise Texture "Fac" (fBm, roughness 0.5, lacunarity 2, normalised): `detail` + 1 octaves, 0..1 around 0.5. The 4D `w` is
// folded into the position as an offset (a different field per w).
float bl_noise(vec3 p, int detail, float w) {
	p += vec3(17.13, 31.71, 23.37) * w;
	float s = 0.0;
	float amp = 1.0;
	float sum = 0.0;
	for (int k = 0; k < 4; k++) {
		if (k > detail) {
			break;
		}
		s += amp * bl_pnoise(p);
		sum += amp;
		amp *= 0.5;
		p = p * 2.0 + vec3(5.2, 1.3, 8.7);
	}
	return 0.5 * s / sum + 0.5;
}

// Blender's Voronoi "Distance To Edge" (3D, randomness 1): the distance to the nearest cell border, in cell units.
float bl_vor_edge(vec3 x) {
	vec3 ci = floor(x);
	vec3 lf = x - ci;
	vec3 to_closest = vec3(0.0);
	vec3 cell_closest = vec3(0.0);
	float mind = 8.0;
	for (int k = -1; k <= 1; k++) {
		for (int j = -1; j <= 1; j++) {
			for (int i = -1; i <= 1; i++) {
				vec3 co = vec3(float(i), float(j), float(k));
				vec3 pt = co + bl_hash3(ci + co) - lf;
				float d = dot(pt, pt);
				if (d < mind) {
					mind = d;
					to_closest = pt;
					cell_closest = co;
				}
			}
		}
	}
	float md = 8.0;
	for (int k = -1; k <= 1; k++) {
		for (int j = -1; j <= 1; j++) {
			for (int i = -1; i <= 1; i++) {
				vec3 co = cell_closest + vec3(float(i), float(j), float(k));
				vec3 pt = co + bl_hash3(ci + co) - lf;
				vec3 perp = pt - to_closest;
				if (dot(perp, perp) > 0.0001) {
					md = min(md, dot(0.5 * (to_closest + pt), normalize(perp)));
				}
			}
		}
	}
	return md;
}

float bl_smooth(float v, float a, float b) {
	return smoothstep(a, b, v);
}

#ifdef BL_STREET
// ---- Street: the field is a function of the world position in the STREET FRAME ----------------------------------------------
// bl_origin / bl_dir / bl_perp: the street's start point (plan), its unit direction and the unit across axis toward the frontage
// (plan = world x, -world z). The street frame is x = frame0.x - along, y = frame0.y + across, z = height, with frame0 the concept
// plate's street start (135, 9): a street that runs along -x there (dir -1, 0) gives the plate's own world coordinates.
// bl_front: where the front stands on that x (infected where x is larger: behind it). Boxes (route rooms, links) are in the same frame.
uniform vec2 bl_origin = vec2(0.0);   // the street's start (plan)
uniform vec2 bl_frame0 = vec2(135.0, 9.0);   // the street frame's x / y at the start (the concept plate's own, so its numbers hold)
uniform vec2 bl_dir = vec2(-1.0, 0.0);
uniform vec2 bl_perp = vec2(0.0, 1.0);
uniform float bl_front = 0.0;
uniform float bl_tend = 24.0;        // tendril reach ahead of the front at low heights (BU) and the height it fades out at
uniform float bl_tend_h = 6.0;
uniform float bl_len_k = 1.0;        // the front's BU-scaled raggedness (fingers, height lean) in layers: layer spacing over the plate's
uniform float bl_lean = 1.1;         // BU the front leans back per BU of height (before bl_len_k)
uniform float bl_wall_vw = 1.0;      // walls: vein width x
uniform float bl_wall_veins = 1.0;   // walls: vein emission x
uniform float bl_wall_hatch = 1.0;   // walls: hatch emission x
uniform int bl_box_n = 0;
uniform vec3 bl_box_lo[BL_BOXES];
uniform vec3 bl_box_hi[BL_BOXES];

vec3 bl_street_pos(vec3 wp) {
	vec2 r = vec2(wp.x, -wp.z) - bl_origin;
	return vec3(bl_frame0.x - dot(r, bl_dir), bl_frame0.y + dot(r, bl_perp), wp.y);
}

// 1 inside any keep-out box (route rooms +10 %, jamb, frame ring; link boxes).
float bl_keep(vec3 p) {
	float keep = 0.0;
	for (int i = 0; i < BL_BOXES; i++) {
		if (i >= bl_box_n) {
			break;
		}
		vec3 lo = bl_box_lo[i];
		vec3 hi = bl_box_hi[i];
		if (p.x > lo.x && p.x < hi.x && p.y > lo.y && p.y < hi.y && p.z > lo.z && p.z < hi.z) {
			keep = 1.0;
			break;
		}
	}
	return keep;
}

// The street's depth behind the front at P (BU, positive = infected): bloom3d_mat.build_field's `d`.
float bl_street_depth(vec3 P) {
	float sd = bl_seed;
	// ragged front: fingers that follow the surface (a function of height and depth), tendrils crawling ahead at low heights
	float fn = bl_noise(vec3(P.z * 0.5, P.y * 0.08, 0.0), 3, sd);
	float fn2 = bl_noise(vec3(P.z * 1.7, P.x * 0.05, 0.0), 2, sd + 5.0);
	float fing = ((fn - 0.35) * 7.5 + (fn2 - 0.5) * 3.5) * bl_len_k;
	float tn = bl_noise(vec3(P.y * 0.35, P.z * 0.9, 0.0), 3, sd + 3.0);
	float tend = bl_smooth(tn, 0.42, 0.58) * bl_tend * (1.0 - bl_smooth(P.z, 0.4, bl_tend_h));
	float zc = min(max(P.z, 0.0), 14.0);
	float local = bl_front + zc * bl_lean * bl_len_k - fing - tend;
	return P.x - local;
}

BlField bl_street_field(vec3 wp, float wall) {
	BlField o = BlField(0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
	vec3 P = bl_street_pos(wp);
	float diag = (P.x + P.z + P.y * 0.25) * bl_hatch_scale;
	float fw = max(fwidth(diag), 0.002);  // (before any early out: derivatives need the whole quad)
	float d = bl_street_depth(P);
	float dpx = fwidth(d);  // (before any early out)
	o.depth = d;
	float cover = bl_smooth(d, -0.05, 0.15);
	float edge = 1.0 - bl_smooth(abs(d - 0.03), 0.0, max(bl_ew, bl_edge_px * dpx));
	if (cover <= 0.0 && edge <= 0.0) {
		return o;
	}
	float keep = bl_keep(P);
	if (keep > 0.5) {
		return o;
	}
	// veins: borders of a domain-warped 3D Voronoi (cracked necrotic skin), two scales, density-masked, sparse near the front
	float wv = bl_noise(P * 0.35, 2, bl_seed + 9.0) * 1.1;
	vec3 wpos = P + vec3(wv);
	float vein = 0.0;
	for (int k = 0; k < 2; k++) {
		float sc = bl_vscale * (k == 0 ? 1.0 : 2.1);
		float w = bl_vw * (k == 0 ? 1.0 : 1.7) * mix(1.0, bl_wall_vw, wall);
		float line = 1.0 - bl_smooth(bl_vor_edge(wpos * sc), 0.0, w);
		float dens = bl_smooth(bl_noise(P * (0.12 + 0.05 * float(k)), 2, bl_seed + 20.0 + float(k)), 0.46 + bl_vein_dens, 0.64 + bl_vein_dens);
		vein = max(vein, line * dens * (k == 0 ? 1.0 : 0.7));
	}
	vein *= 0.45 + bl_smooth(d, 0.0, 9.0) * 0.55;
	// 45 degree world hatch (x + z diagonal on facades, x + y on the ground), fading in behind the front; antialiased on the pixel
	float hatch = (1.0 - smoothstep(0.22 - fw, 0.22 + fw, fract(diag))) * bl_smooth(d, 0.0, 3.0);
	o.cover = cover;
	o.vein = vein;
	o.edge = edge;
	o.hatch = hatch;
	return o;
}

// The Bloom skin on a street surface: the body and the emission mixed by the cover. `wp` the world position.
// `wall` 0 on a flat floor .. 1 on a vertical face (the walls take bl_wall_*).
float bl_apply_street_w(vec3 wp, float wall, inout vec3 albedo, inout vec3 emission) {
	if (bl_strength <= 0.0) {
		return 0.0;
	}
	BlField f = bl_street_field(wp, wall);
	float fac = clamp(f.cover * bl_cover_k, 0.0, 1.0) * clamp(bl_strength, 0.0, 1.0);
	// the hot edge and the veins are drawn where the mix is: at the front's hairline (edge) the fac is partial by design
	float k = f.vein * bl_veins * mix(1.0, bl_wall_veins, wall) + f.hatch * bl_hatch_k * mix(1.0, bl_wall_hatch, wall);
	albedo = mix(albedo, bl_plum, fac);
	// the front's hairline is the hottest line of the skin: added over the mix (not weighted by the cover), so it reads at the front
	emission = mix(emission, bl_pink * k + bl_plum * bl_body_emit, fac) + bl_pink * f.edge * bl_edge_k * clamp(bl_strength, 0.0, 1.0);
	return fac;
}

float bl_apply_street(vec3 wp, inout vec3 albedo, inout vec3 emission) {
	return bl_apply_street_w(wp, 0.0, albedo, emission);
}

// The same for an unlit emitter (signs, strips): the colour goes to the body plus the pink emission by the cover. Returns the colour.
vec3 bl_unlit_street(vec3 wp, vec3 col) {
	if (bl_strength <= 0.0) {
		return col;
	}
	BlField f = bl_street_field(wp, 1.0);
	float fac = clamp(f.cover * bl_cover_k, 0.0, 1.0) * clamp(bl_strength, 0.0, 1.0);
	float k = f.vein * bl_veins * bl_wall_veins + f.hatch * bl_hatch_k * bl_wall_hatch;
	return mix(col, bl_plum * (1.0 + bl_body_emit) + bl_pink * k, fac) + bl_pink * f.edge * bl_edge_k * clamp(bl_strength, 0.0, 1.0);
}

// The skin's cover at `wp` (0..1 times the strength): for the lights that must follow it (the specular fades on the skin).
float bl_cover_street(vec3 wp) {
	if (bl_strength <= 0.0) {
		return 0.0;
	}
	vec3 P = bl_street_pos(wp);
	float d = bl_street_depth(P);
	if (d <= -0.05) {
		return 0.0;
	}
	return clamp(bl_smooth(d, -0.05, 0.15) * (1.0 - bl_keep(P)) * bl_cover_k, 0.0, 1.0) * clamp(bl_strength, 0.0, 1.0);
}
#endif  // BL_STREET

#ifdef BL_TUBE
// ---- HQ helix: tube coordinates --------------------------------------------------------------------------------------------
// The compound's plate-unit frame (Blender x, y, z up; the glTF is (x, z, -y) times unit_k): bl_w2p takes the world position there.
// The helix is two swept tubes round one axis (hq_graph.py: radius R, floor_h FH, theta(f) = theta0 + twist f, strand B opposite);
// the position gives (z, phi round the tube from its front normal, tower) exactly as the Blender mesh's `tube` attribute did.
uniform mat4 bl_w2p = mat4(1.0);
uniform float bl_zfront = 0.0;       // the front's height (plate units), one for both strands
uniform float bl_swell = 4.5;
uniform float bl_tongue = 40.0;
uniform float bl_reach = 45.0;       // how far ahead of the front (plate units) the fingers crawl
uniform float bl_ahead_k = 1.0;
uniform float bl_tube_r = 10.0;
uniform vec4 bl_helix = vec4(40.0, 12.5, 90.0, 13.3333);   // radius, floor height, theta0 (deg), twist per floor (deg)
uniform float bl_podium = 9.9;
uniform vec2 bl_stair = vec2(-0.6109, 0.6109);              // the UP stair band's phi on strand A / B (rad)
uniform float bl_stair_w = 2.3;                              // its half width (plate units)
uniform float bl_win_dim = 0.03;     // the dim pink the window light dies to below the front (emission strength)
uniform float bl_win_r = 48.0;       // the helix' lit parts lie inside this radius (plate units)
uniform float bl_win_bias = 0.0;
uniform int bl_room_n = 0;           // route rooms (spheres, plate units): their emission stays clean
uniform vec4 bl_room[BL_BOXES];      // xyz = centre, w = radius

// (z, phi, tower) of a point on the helix: tower 0 = A, 1 = B (the nearer strand's axis at that height).
vec3 bl_tube_coords(vec3 pp) {
	float f = (pp.z - bl_podium) / bl_helix.y;
	float th = radians(bl_helix.z + bl_helix.w * f);
	vec2 rv = vec2(sin(th), cos(th));
	vec2 ca = rv * bl_helix.x;
	vec2 cb = -ca;
	float tw = distance(pp.xy, cb) < distance(pp.xy, ca) ? 1.0 : 0.0;
	vec2 c = tw > 0.5 ? cb : ca;
	vec2 n = vec2(cos(th), -sin(th));       // az_vec(theta + 90 deg)
	vec2 tx = vec2(n.y, -n.x);
	vec2 dv = pp.xy - c;
	return vec3(pp.z, atan(dot(dv, tx), dot(dv, n)), tw);
}

// The front's height at (phi, tower, z): a spiral swell, tongues that are functions of phi only (they run along the strand), a ragged edge.
float bl_tube_front(float Z, float PHI, float TW) {
	float sd = bl_seed;
	float cphi = cos(PHI);
	float sphi = sin(PHI);
	float ph0 = TW * 3.14159265;
	float swell = cos(PHI - ph0 - 0.6) * bl_swell;
	float tg = bl_noise(vec3(cphi * 2.2 + TW * 17.0, sphi * 2.2, 3.0), 3, sd);
	float tongue = bl_smooth(tg, 0.42, 0.72) * bl_tongue;
	float rg = bl_noise(vec3(Z * 0.45, cphi * 3.0 + TW, sphi * 3.0), 3, sd + 4.0);
	float ragged = (rg - 0.5) * 2.2 * 2.0;
	return bl_zfront + swell + tongue + ragged;
}

BlField bl_tube_field(vec3 pp) {
	BlField o = BlField(0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
	vec3 tc = bl_tube_coords(pp);
	float Z = tc.x;
	float PHI = tc.y;
	float TW = tc.z;
	float diag = (PHI * bl_tube_r + Z) * bl_hatch_scale;
	float fw = max(fwidth(diag), 0.002);  // (before any early out: derivatives need the whole quad)
	float d = bl_tube_front(Z, PHI, TW) - Z;
	o.depth = d;
	float cover = bl_smooth(d, -0.2, 0.6);
	if (d < -bl_reach) {
		return o;
	}
	float cphi = cos(PHI);
	float sphi = sin(PHI);
	// keep-out: the UP stair band (the solid strip between the two windows) keeps the skin clean
	for (int ti = 0; ti < 2; ti++) {
		float sp = ti == 0 ? bl_stair.x : bl_stair.y;
		float dph = abs(mod(PHI - sp + 3.14159265, 6.2831853) - 3.14159265);
		if (dph < bl_stair_w / bl_tube_r && abs(TW - float(ti)) < 0.5) {
			cover = 0.0;
		}
	}
	// veins: cell borders of a Voronoi on the tube cylinder, stretched along the strand (z * 0.3): they run with the twist
	float vs0 = 0.0;
	float vein = 0.0;
	for (int k = 0; k < 2; k++) {
		float sc = bl_vscale * (k == 0 ? 1.0 : 2.0);
		float w = bl_vw * (k == 0 ? 1.0 : 1.7);
		float zk = k == 0 ? 0.30 : 0.4;
		vec3 cyl = vec3(cphi * bl_tube_r + TW * (31.0 + 3.0 * float(k)), sphi * bl_tube_r, Z * zk);
		float line = 1.0 - bl_smooth(bl_vor_edge(cyl * sc), 0.0, w);
		float dens = bl_smooth(bl_noise(vec3(cphi * 2.0, sphi * 2.0, Z * (0.02 + 0.01 * float(k))), 2, bl_seed + 20.0 + float(k)), 0.38 + bl_vein_dens, 0.55 + bl_vein_dens);
		float v = line * dens * (k == 0 ? 1.0 : 0.7);
		if (k == 0) {
			vs0 = v;
		}
		vein = max(vein, v);
	}
	vein *= 0.5 + bl_smooth(d, 0.0, 25.0) * 0.5;
	float edge = (1.0 - bl_smooth(abs(d - 0.1), 0.0, bl_ew)) * step(0.02, cover);
	float hatch = (1.0 - smoothstep(0.22 - fw, 0.22 + fw, fract(diag))) * bl_smooth(d, 0.0, 6.0);
	// fingers: thin veins that crawl out ahead of the front over the clean skin (d < 0), gated by a slow noise along the strand
	float fing = bl_smooth(bl_noise(vec3(cphi * 3.0, sphi * 3.0, Z * 0.03), 2, bl_seed + 40.0), 0.45, 0.62);
	float ahead = vs0 * fing * bl_smooth(d, -bl_reach, -1.0) * (1.0 - cover);
	o.cover = cover;
	o.vein = vein;
	o.edge = edge;
	o.hatch = hatch;
	o.ahead = ahead;
	return o;
}

// The Bloom skin on the helix strand's front face; `wp` the world position.
float bl_apply_tube(vec3 wp, inout vec3 albedo, inout vec3 emission) {
	if (bl_strength <= 0.0) {
		return 0.0;
	}
	vec3 pp = (bl_w2p * vec4(wp, 1.0)).xyz;
	BlField f = bl_tube_field(pp);
	float st = clamp(bl_strength, 0.0, 1.0);
	float fac = clamp(f.cover * bl_cover_k, 0.0, 1.0) * st;
	float k = f.vein * bl_veins + f.edge * bl_edge_k + f.hatch * bl_hatch_k;
	albedo = mix(albedo, bl_plum, fac);
	emission = mix(emission, bl_pink * k, fac) + bl_pink * f.ahead * bl_ahead_k * st;
	return fac;
}

// The window light dying below the front: the lit emission of the helix' neon / office / window roles fades to a dim pink on the
// helix (axis radius under bl_win_r, above the podium) below the front's height; route rooms (spheres) and the stair band stay lit.
vec3 bl_dim_tube(vec3 wp, vec3 emission) {
	if (bl_strength <= 0.0) {
		return emission;
	}
	vec3 pp = (bl_w2p * vec4(wp, 1.0)).xyz;
	if (length(pp.xy) >= bl_win_r || pp.z <= bl_podium + 2.0) {
		return emission;
	}
	for (int i = 0; i < BL_BOXES; i++) {
		if (i >= bl_room_n) {
			break;
		}
		if (distance(pp, bl_room[i].xyz) < bl_room[i].w) {
			return emission;
		}
	}
	float az = atan(pp.y, pp.x);
	float zf = bl_zfront + cos(az - 0.6) * bl_swell + bl_win_bias;
	float below = bl_smooth(zf - pp.z, -0.2, 0.8);
	return mix(emission, bl_pink * bl_win_dim, below * clamp(bl_strength, 0.0, 1.0));
}
#endif  // BL_TUBE

#endif  // BLOOM_NECROSIS_INCLUDED
