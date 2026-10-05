shader_type canvas_item;
// The wheel disc (ART-2 2A; ART_BIBLE v2 3.2-3.10, 6.2): every radial layer of one wheel in one pass,
// ported from the concept recipes on tag art-concepts-r43 (round 41 slicelib.render_slice, frames._d4,
// frames.machined / disc_shadow / threat_ring, d4corp, ringlock). Master units throughout (R_OUT = 360 is
// the slice rim); the node's rect is a square `ext` master units from the centre to each edge.
// Bottom to top: disc base, slice screens (dimmed but the active one) with tier, state overlay and
// landing flash, the bezel lip and hub shadows, the D4 machined bezel with its glass channel and the
// rail tint, the boss threat ring, the inner ring and the hub CRT disc, the lifted active slice with its
// cream outline, the glass crescent. Text, glyphs, blades and plates are drawn by WheelView on top.
render_mode blend_premul_alpha;

const float R_OUT = 360.0;
const float R_IN = 130.0;
const float GAP = 1.6;
const float BW = 8.5;
const float R_LIP = 356.0;
const float RCH0 = 368.0;
const float RCH1 = 404.0;
const float R1 = 414.0;
const float RING0 = 100.0;
const float RING1 = 127.0;

// Recipe colours (slicelib.CORPS bezel, tiles.TIER_COLS, frames, ringlock.SEG_COL): kit tables indexed by
// `theme` (0 player, 1 meridian, 2 solace, 3 halcyon, 4 orbital, 5 rebel_cell). Not UI tokens: material.
const vec3 SLICE_BEZEL[6] = vec3[6](vec3(0.085, 0.08, 0.11), vec3(0.17, 0.115, 0.075), vec3(0.22, 0.24, 0.18),
	vec3(0.16, 0.09, 0.24), vec3(0.20, 0.22, 0.28), vec3(0.11, 0.04, 0.05));
const vec3 FRAME_BASE[6] = vec3[6](vec3(0.16, 0.15, 0.19), vec3(0.36, 0.21, 0.09), vec3(0.62, 0.66, 0.64),
	vec3(0.30, 0.18, 0.44), vec3(0.47, 0.55, 0.59), vec3(0.20, 0.05, 0.06));
const vec3 THREAT = vec3(1.0, 0.204, 0.251);
const vec3 SEG_COL[8] = vec3[8](vec3(0.47, 0.47, 0.53), vec3(1.0, 0.839, 0.251), vec3(0.745, 0.961, 1.0),
	vec3(1.0, 0.157, 0.627), vec3(0.745, 0.784, 0.843), vec3(1.0, 0.627, 0.157), vec3(0.361, 0.882, 1.0),
	vec3(0.69, 0.549, 1.0));
const vec3 PINK = vec3(1.0, 0.24, 0.66);
const vec3 GREENG = vec3(0.3, 1.0, 0.55);
const vec3 CYANS = vec3(0.36, 0.88, 1.0);
const vec3 HEAT = vec3(1.0, 0.55, 0.12);

uniform float ext = 470.0;
uniform float px = 1.6;
uniform int n = 6;
uniform float span = 60.0;
uniform float mids[8];
uniform int kinds[8];
uniform vec4 cols[8];
uniform int stat[8];
uniform float flash[8];
uniform vec2 plate[8];
uniform int active = -1;
uniform float dim_others = 0.68;
uniform float lift = 1.025;
uniform sampler2D screens : filter_linear, repeat_disable;
uniform sampler2D scenes : filter_linear, repeat_disable;
uniform bool has_scene = false;
uniform float scene_yc = 0.5;
uniform float scene_cut = -1.0;
uniform float frame_pos = 0.0;
uniform int frames = 12;
uniform int rows = 10;
uniform vec2 tex_size = vec2(374.0, 215.0);
uniform float r_out_s = 349.9;
uniform int theme = 0;
uniform int tier = 1;
// Tier colours (3.7): the kit's primary and secondary (Palette.corp_color / corp_secondary; the
// player's RESIST_GOLD / PAPER), set by WheelKit.
uniform vec4 tier_prim : source_color = vec4(1.0, 0.804, 0.353, 1.0);
uniform vec4 tier_sec : source_color = vec4(1.0, 0.941, 0.784, 1.0);
uniform vec4 accent : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform vec4 hub_tint : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform float hub_r = 96.0;
uniform bool ring_on = false;
uniform int seg_kind[3];
uniform float ring_rot = 0.0;
uniform int seg_active = -1;
uniform float lockdown = 0.0;
uniform bool boss = false;
uniform bool elite = false;
uniform float threat_rot = 0.0;
uniform float rail_half = 50.0;
uniform vec4 rail_col : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform float needles[4];
uniform int needle_n = 1;
uniform float t_s = 0.0;
uniform float invert = 0.0;
uniform float hit = 0.0;
uniform float grey = 0.0;
uniform float alpha = 1.0;
uniform float needle_gap = 8.0;
// Tier I screen gain (bible 3.7 says 60 %; the combat v4 mocks show tier I at full gain: DECISIONS
// "Art direction - ART-2 2A wheel stack").
uniform float tier1_gain = 1.0;
// The screens' phosphor gain at combat size (the recipe's bloom pass, `frames.add_glow`, lifts them).
uniform float screen_gain = 1.6;
// Precision landing (3.19): the landed slice's flash tint (gold PERFECT, white GOOD, amber WEAK) and
// the WEAK slice's dim.
uniform vec4 land_tint : source_color = vec4(1.0);
uniform int land_slot = -1;
uniform float land_dim = 0.0;
// The player's defeat (3.3, round 40): the core's rows release from the bottom (0..1).
uniform float drain = 0.0;
// PARASITE (3.8): the large translucent bug, pumping (its glyph, outlined).
uniform sampler2D bug_tex : filter_linear, repeat_disable;
uniform bool has_bug = false;
uniform float bug_size = 170.0;
// The boss phase (3.16, round 14): 2 = a hot threat ring, 3 = screens overdrive and armour bolts on.
uniform int phase = 1;

float sm(float e0, float e1, float x) {
	float t = clamp((x - e0) / (e1 - e0), 0.0, 1.0);
	return t * t * (3.0 - 2.0 * t);
}

float round_min(float a, float b, float r) {
	if (a < r && b < r) {
		return r - sqrt(max(r - a, 0.0) * max(r - a, 0.0) + max(r - b, 0.0) * max(r - b, 0.0));
	}
	return min(a, b);
}

float wrapd(float d) {
	return mod(d + 180.0, 360.0) - 180.0;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

vec2 dir_of(float deg) {
	float a = radians(deg);
	return vec2(sin(a), -cos(a));
}

vec4 atlas(sampler2D tex, int row, float sx, float sy) {
	// Two neighbouring frames cross-faded so the 12-frame loop reads smooth.
	vec2 ts = vec2(textureSize(tex, 0));
	vec2 cell = ts / vec2(float(frames), float(rows));
	float u = clamp(sx / tex_size.x, 0.5 / cell.x, 1.0 - 0.5 / cell.x);
	float v = clamp(sy / tex_size.y, 0.5 / cell.y, 1.0 - 0.5 / cell.y);
	float f0 = floor(frame_pos);
	float k = frame_pos - f0;
	float c0 = mod(f0, float(frames));
	float c1 = mod(f0 + 1.0, float(frames));
	vec2 a = vec2((c0 + u) * cell.x, (float(row) + v) * cell.y) / ts;
	vec2 b = vec2((c1 + u) * cell.x, (float(row) + v) * cell.y) / ts;
	return mix(texture(tex, a), texture(tex, b), k);
}

// An inner-ring segment's texture (ringlock.texture, 3.10) at arc length u from its midline and radius
// rho (master units); `mid_r` is the band's middle (the anchor chain's line).
float seg_tex(int sk, float u, float rho, float mid_r) {
	if (sk == 1) {
		float fr = fract(u / 13.0);
		return (step(0.18, fr) - step(0.30, fr) + step(0.42, fr) - step(0.54, fr)) * 0.75;
	} else if (sk == 2) {
		float x = abs(fract(u / 14.0) - 0.5) * 14.0;
		return step(fract((rho - x * 0.9) / 14.0 - t_s * 0.5), 0.28) * 0.8;
	} else if (sk == 3) {
		return step(0.7, hash(vec2(floor(u / 6.0), floor(rho / 6.0) + floor(t_s * 4.0)))) * 0.8;
	} else if (sk == 4) {
		float lk = fract(u / 16.0);
		return (1.0 - sm(0.0, 1.5, abs(length(vec2((lk - 0.5) * 16.0, (rho - mid_r) * 1.2)) - 5.0))) * 0.7;
	} else if (sk == 5) {
		return step(0.82, fract(u / 9.0 + t_s * 0.8 + hash(vec2(floor(rho / 4.0), 2.0)))) * 0.6;
	} else if (sk == 6) {
		return (0.5 + 0.5 * sin(rho * 0.9 - t_s * 4.0 + abs(u) * 0.2)) * 0.45;
	}
	return (hash(vec2(floor(u * 2.0), 3.0)) - 0.5) * 0.12 + 0.06;
}

vec3 flash_col(int i) {
	return i == land_slot ? mix(cols[i].rgb, land_tint.rgb, 0.8) : mix(cols[i].rgb, vec3(1.0), 0.45);
}

// One slice tile at point p (master units, y down), its index i, scaled about the centre by `sc`
// (the lifted active slice). Returns premultiplied rgba.
vec4 slice_tile(vec2 p, int i, float sc) {
	vec2 q = p / sc;
	float rho = length(q);
	float th = mod(degrees(atan(q.x, -q.y)), 360.0);
	float mid = mids[i];
	float half_span = span * 0.5;
	float d = wrapd(th - mid);
	float e_side = rho * sin(radians(clamp(half_span - abs(d), -90.0, 90.0))) - GAP;
	float e_out = R_OUT - GAP - rho;
	float e_in = rho - R_IN - GAP;
	float e_tile = round_min(round_min(e_side, e_out, 4.0), e_in, 4.0);
	float a_tile = clamp(e_tile / px + 0.5, 0.0, 1.0);
	if (a_tile <= 0.0) {
		return vec4(0.0);
	}
	float e_scr = round_min(round_min(e_side - BW, e_out - BW, 11.0), e_in - BW * 0.85, 9.0);
	float a_scr = clamp(e_scr / px + 0.5, 0.0, 1.0);
	float W = tex_size.x;
	float H = tex_size.y;
	float tx = W * 0.5 + rho * radians(d);
	float ty = r_out_s - rho;
	int st = stat[i];
	// CORRUPTED (3.8): tear bands re-rolled every 83 ms shift the screen sideways.
	float tear = 0.0;
	if (st == 1) {
		float roll = floor(t_s / 0.083);
		float band = floor(ty / 14.0);
		float hb = hash(vec2(band + float(i) * 7.0, roll));
		if (hb > 0.45) {
			tear = (hash(vec2(band, roll + 3.0)) - 0.5) * 2.0 * mix(6.0, 20.0, hb);
		}
	}
	float nx = (tx + tear - W * 0.5) / (W * 0.5);
	float ny = (ty - H * 0.5) / (H * 0.5);
	float f = 1.0 - 0.055 * (nx * nx + ny * ny);
	float sx = W * 0.5 + (tx + tear - W * 0.5) * f;
	float sy = H * 0.5 + (ty - H * 0.5) * f;
	// Narrow or wide slices: the 60-degree screen mirrors across its edges.
	if (sx < 0.0 || sx > W) {
		sx = W - mod(sx, W);
	}
	vec3 col = cols[i].rgb;
	int row = kinds[i];
	vec3 scr = atlas(screens, row, sx, sy).rgb * screen_gain * (phase >= 3 ? 1.3 : 1.0);
	if (st == 1) {
		// pink / green ghost split +-4
		vec3 gl = atlas(screens, row, sx + 4.0, sy).rgb;
		vec3 gr = atlas(screens, row, sx - 4.0, sy).rgb;
		scr = vec3(gl.r, gr.g, scr.b) * 0.8 + 0.2 * scr;
	}
	if (has_scene) {
		// round 16: the corp animation stays upright in screen space, centred on the slice.
		float rc_s = r_out_s - scene_yc * H;
		vec2 pc = dir_of(mid) * rc_s;
		float sxs = (q.x - pc.x) + W * 0.5;
		float sys = (q.y - pc.y) + scene_yc * H;
		if (sxs > 0.0 && sxs < W && sys > 0.0 && sys < H) {
			vec4 smp = atlas(scenes, row, sxs, sys);
			float sa = smp.a;
			if (scene_cut > 0.0) {
				sa *= sm(scene_cut * H + 2.0, scene_cut * H - 2.0, ty);
			}
			scr = scr * (1.0 - sa) + smp.rgb * sa;
		}
	}
	// scanlines: 3 screen px (rows of constant radius, so they bend into arcs)
	float sl_p = max(3.0, 3.0 * px);
	scr *= 0.70 + 0.30 * (0.5 + 0.5 * cos(2.0 * PI * ty / sl_p));
	scr *= 0.35 + 0.65 * sm(0.0, 26.0, e_scr);
	// the read plate: an upright ellipse under the glyph + value block
	float rc = R_IN + 0.6 * (R_OUT - R_IN);
	vec2 bc = dir_of(mid) * rc;
	vec2 pr = (q - bc) / max(plate[i], vec2(1.0));
	float qq = dot(pr, pr);
	float in_plate = exp(-qq * 1.4);
	scr *= 1.0 - 0.62 * in_plate;
	scr += exp(-pow((ny + 0.75) * 2.6, 2.0)) * clamp(0.6 - nx * 0.5, 0.0, 1.0) * 0.07;
	// state overlays (3.8): their own wash, thinned to 35 % inside the read window
	float wash_k = mix(1.0, 0.35, clamp(in_plate * 1.6, 0.0, 1.0));
	if (st == 1) {
		float roll = floor(t_s / 0.083);
		float cb = hash(vec2(floor(ty / 9.0), roll + 11.0));
		vec3 band_c = cb > 0.5 ? PINK : GREENG;
		float bmask = step(0.55, hash(vec2(floor(ty / 9.0) + 40.0, roll)));
		float flick = 1.0 - 0.18 * step(0.5, hash(vec2(floor(ty / sl_p), roll)));
		float tl = step(0.94, fract(t_s)) * exp(-pow((ty - H * fract(t_s * 3.7)) / 2.0, 2.0));
		scr = scr * flick;
		scr = mix(scr, band_c, 0.6 * bmask * wash_k);
		scr += mix(PINK, GREENG, step(0.5, fract(tx / 7.0))) * 0.1 * wash_k;
		scr += vec3(1.0, 0.9, 1.0) * tl * wash_k;
	} else if (st == 3) {
		// ENCRYPTED: asterisks scrolling outward
		vec2 g = vec2(tx, ty + t_s * 26.0) / 18.0;
		vec2 cell = fract(g) - 0.5;
		float ang = atan(cell.y, cell.x);
		float star = (0.5 + 0.5 * cos(ang * 6.0)) * 0.2 + 0.09 - length(cell);
		float on = step(0.45, hash(floor(g)));
		float am = clamp(star * 40.0, 0.0, 1.0) * on;
		scr = mix(scr, CYANS * 1.3, am * 0.8 * wash_k);
		scr += CYANS * 0.1 * wash_k;
	} else if (st == 2) {
		// OVERCLOCKED: a translucent heat look, rising shimmer from the hub side
		float heat = sm(H, 0.0, ty) * 0.5 + 0.5;
		float wob = 0.5 + 0.5 * sin(ty * 0.12 - t_s * 6.0 + tx * 0.05);
		scr = mix(scr, HEAT * (0.8 + 0.4 * wob), 0.42 * heat * wash_k);
	} else if (st == 4) {
		// PARASITE: the large translucent bug only, legs crawling, body pumping (alpha about 0.5)
		scr = mix(scr, vec3(0.45, 0.9, 0.25) * 0.6, 0.12 * wash_k);
		if (has_bug) {
			float pump = 1.0 + 0.06 * sin(t_s * 7.0);
			vec2 bc2 = dir_of(mid) * (R_IN + 0.5 * (R_OUT - R_IN));
			vec2 bq = (q - bc2) / (bug_size * pump);
			bq.x += 0.03 * sin(t_s * 11.0 + bq.y * 9.0) * step(0.25, abs(bq.x));
			vec2 buv = bq + 0.5;
			if (buv.x > 0.0 && buv.x < 1.0 && buv.y > 0.0 && buv.y < 1.0) {
				vec4 b = texture(bug_tex, buv);
				scr = mix(scr, vec3(0.55, 1.0, 0.3) * mix(1.2, 0.25, 1.0 - b.r), b.a * 0.62 * wash_k);
			}
		}
	}
	// the inner ring's active segment extends its texture into the slice it modifies (3.10)
	if (ring_on && i == active && seg_active >= 0) {
		int sk2 = seg_kind[seg_active];
		float ext_a = (1.0 - sm(132.0, 182.0, rho)) * sm(R_IN, 136.0, rho) * (1.0 - 0.65 * in_plate);
		float tx2 = seg_tex(sk2, rho * radians(d), rho, 157.0);
		scr = mix(scr, SEG_COL[sk2] * 1.2, clamp(tx2, 0.0, 1.0) * ext_a * (tier >= 3 ? 0.47 : 0.8));
	}
	// landing flash: the slice lights in its tint and fades; a WEAK landing dims its slice 20 %
	scr = mix(scr, flash_col(i), clamp(flash[i], 0.0, 1.0) * 0.55);
	if (i == land_slot) {
		scr *= 1.0 - land_dim;
	}
	// ---- bezel
	vec3 base = SLICE_BEZEL[theme];
	float light = 0.85 + 0.3 * cos(radians(th - 315.0));
	vec3 bez = base * light;
	bez += exp(-pow(e_tile / 1.2, 2.0)) * 0.22;
	bez *= 1.0 - 0.6 * sm(-5.0, 0.0, e_scr);
	bez += exp(-pow((e_scr + 1.3) / 0.9, 2.0)) * col * 1.1;
	float led_r = R_OUT - GAP - BW * 0.5;
	float led_lat = radians(half_span - min(4.0, half_span * 0.35)) * led_r * 0.86;
	float ld = length(vec2(rho * radians(d) - led_lat, rho - led_r));
	float led = clamp(1.6 - ld, 0.0, 1.0) + exp(-pow(ld / 3.5, 2.0)) * 0.5;
	vec3 led_col = theme == 0 ? col : tier_prim.rgb;
	bez += led * led_col * 1.3;
	vec3 rgb = scr * a_scr + bez * (1.0 - a_scr);
	// tiers (3.7, V2 strong): I primary border, II secondary border + inset line, III gold strip + hatch
	if (theme != 0 || tier > 1) {
		vec3 prim = tier_prim.rgb;
		vec3 sec = tier_sec.rgb;
		vec3 tcol = (tier == 2) ? sec : prim;
		float band_b = clamp(1.0 - abs(e_scr + BW * 0.45) / (BW * 0.42), 0.0, 1.0) * a_tile;
		rgb = rgb * (1.0 - band_b * 0.75) + tcol * (0.55 + 0.45 * light) * band_b * 0.75;
		float edge = exp(-pow((e_scr + 1.0) / 0.9, 2.0)) * a_tile;
		rgb += edge * tcol * 0.9;
		float gb = 10.0;
		float line = clamp(2.1 - abs(e_scr - gb - 1.1) / 1.0, 0.0, 1.0) * a_scr;
		if (tier == 2) {
			line = max(line, clamp(1.0 - abs(e_scr - gb - 1.1) / max(1.0, 0.75 * px), 0.0, 1.0) * a_scr);
			rgb = rgb * (1.0 - line) + (sec * 0.8 + 0.2) * line;
		} else if (tier >= 3) {
			float uu = rho * radians(d);
			float bandm = step(0.6, e_scr) * step(e_scr, gb) * a_scr;
			float p1 = fract((uu + ty) / 5.4);
			float p2 = fract((uu - ty) / 5.4);
			float hatch = max(step(p1, 0.46), step(p2, 0.46)) * step(3.4, e_scr);
			float strip = step(0.3, e_scr) * step(e_scr, 2.6) * a_scr;
			rgb = rgb * (1.0 - bandm * 0.85) + vec3(0.04, 0.03, 0.04) * bandm * 0.85;
			rgb = rgb * (1.0 - bandm * hatch) + prim * bandm * hatch;
			rgb = rgb * (1.0 - line) + sec * line;
			rgb = rgb * (1.0 - strip) + (prim * 0.8 + 0.2) * strip;
			rgb *= 1.0 + 0.42 * step(gb + 2.2, e_scr) * a_scr;
		} else {
			rgb *= tier1_gain + (1.0 - tier1_gain) * (1.0 - step(0.0, e_scr) * a_scr);
		}
	} else {
		// the player's tier I: matte (tiers are a game to-do)
		rgb *= tier1_gain + (1.0 - tier1_gain) * (1.0 - step(0.0, e_scr) * a_scr);
	}
	return vec4(rgb * a_tile, a_tile);
}

// Height derivative of the machined bezel profile (frames._d4 knots), smoothed like the recipe.
float bezel_slope(float r) {
	float kr[8] = float[8](R_LIP, R_LIP + 3.0, RCH0 - 3.0, RCH0, RCH1, RCH1 + 3.0, R1 - 4.0, R1);
	float kh[8] = float[8](0.0, 6.0, 7.0, 2.0, 2.0, 7.0, 8.0, 0.0);
	float s = 0.0;
	for (int k = 0; k < 7; k++) {
		float slope = (kh[k + 1] - kh[k]) / (kr[k + 1] - kr[k]);
		float w = sm(kr[k] - 1.2, kr[k] + 1.2, r) - sm(kr[k + 1] - 1.2, kr[k + 1] + 1.2, r);
		s += slope * w;
	}
	return s;
}

vec3 machined(vec2 p, float rho, float th, vec3 base, vec3 acc) {
	vec3 L = normalize(vec3(-0.45, -0.72, 0.53));
	vec3 Hh = normalize(L + vec3(0.0, 0.0, 1.0));
	float g = bezel_slope(rho);
	vec2 u = p / max(rho, 0.001);
	vec3 nrm = normalize(vec3(-g * u.x, -g * u.y, 1.0));
	float diff = clamp(dot(nrm, L), 0.0, 1.0);
	float spec = pow(clamp(dot(nrm, Hh), 0.0, 1.0), 48.0);
	float refl = exp(-pow((nrm.y + 0.55) / 0.22, 2.0)) * step(nrm.z, 0.995);
	float streak = hash(vec2(floor(rho * 3.0), 1.7));
	float ang_var = 0.5 + 0.5 * sin(radians(th) * 3.0 + 1.3);
	vec3 c = base * (0.32 + 0.85 * diff);
	c += spec * 0.9 * 0.8;
	c += refl * 0.35 * 0.8 * (0.4 + base);
	c += (streak - 0.5) * 0.04 * (0.6 + ang_var);
	float sm_ch = sm(RCH0, RCH0 + 1.2, rho) * (1.0 - sm(RCH1 - 1.2, RCH1, rho));
	vec3 glass = vec3(0.012, 0.016, 0.022) + exp(-pow(wrapd(th - 315.0 + 180.0), 2.0) / 2400.0) * 0.05;
	c = mix(c, glass, sm_ch);
	c += exp(-pow((rho - RCH0 - 0.5) / max(0.9, px * 0.6), 2.0)) * 0.8 * acc;
	c += exp(-pow((rho - RCH1 + 0.5) / max(0.9, px * 0.6), 2.0)) * 0.8 * acc;
	c += exp(-pow((rho - R1 + 0.8) / max(1.0, px * 0.6), 2.0)) * 1.0 * acc;
	return c;
}

float near_needle(float th) {
	float best = 999.0;
	for (int k = 0; k < 4; k++) {
		if (k < needle_n) {
			best = min(best, abs(wrapd(th - needles[k])));
		}
	}
	return best;
}

void fragment() {
	vec2 p = (UV - 0.5) * 2.0 * ext;
	float rho = length(p);
	float th = mod(degrees(atan(p.x, -p.y)), 360.0);
	vec4 o = vec4(0.0);
	// 1. disc base
	float bp = clamp((R_OUT + 4.0 - rho) / px + 0.5, 0.0, 1.0);
	o = vec4(vec3(0.02, 0.018, 0.03) * bp, bp);
	// 2. slices (the active one is drawn lifted later)
	if (rho > R_IN - 2.0 && rho < R_OUT + 2.0) {
		int best = 0;
		float bd = 999.0;
		for (int i = 0; i < 8; i++) {
			if (i < n) {
				float dd = abs(wrapd(th - mids[i]));
				if (dd < bd) {
					bd = dd;
					best = i;
				}
			}
		}
		vec4 s = slice_tile(p, best, 1.0);
		if (best != active) {
			s.rgb *= dim_others;
		}
		o = s + o * (1.0 - s.a);
	}
	// 3. shadows: the bezel lip and the raised hub cast onto the disc
	float rs = length(p - vec2(5.0, 9.0));
	float sh = max(sm(R_LIP - 6.0, R_LIP + 6.0, rs), 0.45 * sm(R_LIP - 26.0, R_LIP, rho)) * step(rho, R_LIP + 0.5);
	o.rgb *= 1.0 - 0.5 * sh;
	float hub_cast = ring_on ? RING1 : hub_r;
	float rs2 = length(p - vec2(6.0, 10.0));
	float sh2 = sm(hub_cast + 7.0, hub_cast - 7.0, rs2) * step(hub_cast - 1.0, rho) * step(rho, R_OUT);
	o.rgb *= 1.0 - 0.45 * sh2;
	// 4. the D4 machined bezel and its glass telemetry channel
	if (rho > R_LIP - 1.0 && rho < R1 + 1.0) {
		float al = clamp((rho - R_LIP) / px + 0.5, 0.0, 1.0) * clamp((R1 - rho) / px + 0.5, 0.0, 1.0);
		vec3 c = machined(p, rho, th, FRAME_BASE[theme], accent.rgb);
		// elite collar (3.2): a band of corp-colour chevrons on the outer bevel
		if (elite && rho > RCH1 + 2.0) {
			float cv = step(0.5, fract(th / 6.0 + (rho - RCH1) * 0.02));
			c = mix(c, tier_prim.rgb, 0.55 * cv);
		}
		// the readout rail: static, tinted the program colour, bracketed, split round each needle
		float dn = near_needle(th);
		float in_ch = sm(RCH0 + 1.0, RCH0 + 3.0, rho) * (1.0 - sm(RCH1 - 3.0, RCH1 - 1.0, rho));
		float on_rail = step(dn, rail_half) * step(needle_gap, dn);
		c = mix(c, rail_col.rgb * 0.42, on_rail * in_ch);
		float arcd = abs(dn - rail_half) * PI / 180.0 * rho;
		float bracket = (1.0 - sm(1.5, 1.5 + px, arcd)) * step(RCH0 - 2.0, rho) * step(rho, RCH1 + 2.0);
		c = mix(c, rail_col.rgb, clamp(bracket, 0.0, 1.0));
		if (phase >= 3) {
			// twelve bolted armour plates over the outer bevel (frames.armour)
			float a12 = mod(th, 30.0);
			float plate_m = step(1.2, a12) * step(a12, 28.8) * step(RCH1 + 1.0, rho);
			c = mix(c, FRAME_BASE[theme] * 0.7 + 0.05, plate_m);
			float bolt = 1.0 - sm(2.6, 3.6, length(vec2((a12 - 2.4) * PI / 180.0 * rho, rho - 409.0)));
			bolt = max(bolt, 1.0 - sm(2.6, 3.6, length(vec2((a12 - 27.6) * PI / 180.0 * rho, rho - 409.0))));
			c = mix(c, vec3(0.8, 0.78, 0.74), bolt * plate_m);
		}
		o = vec4(c * al, al) + o * (1.0 - al);
	}
	// 5. boss threat ring: counter-rotating red chevrons on a dark band
	if (boss && rho > R1 && rho < R1 + 32.0) {
		float r0 = R1 + 1.0;
		float r1 = R1 + 30.0;
		float al = clamp((rho - r0) / px + 0.5, 0.0, 1.0) * clamp((r1 - rho) / px + 0.5, 0.0, 1.0);
		vec3 c = vec3(0.118, 0.031, 0.047);
		c = mix(c, vec3(0.47, 0.1, 0.13), 1.0 - sm(0.0, 2.0 * px, rho - r0));
		float rm = (r0 + r1) * 0.5;
		float hw = (r1 - r0) * 0.32;
		float a = wrapd(th + threat_rot);
		float cell = 10.0;
		float local = mod(a, cell) - cell * 0.5;
		float lat = local * PI / 180.0 * rm;
		float radial = rho - rm;
		float chev = abs(radial) * 0.9 - (lat + 5.0) * 0.8;
		float chev_m = step(abs(radial), hw) * step(-hw * 0.5, chev) * step(chev, hw * 0.55);
		vec3 thr = phase >= 2 ? mix(THREAT, vec3(1.0, 0.75, 0.3), 0.35 + 0.25 * sin(t_s * 6.0)) : THREAT;
		c = mix(c, thr, chev_m);
		c += phase >= 2 ? THREAT * 0.18 : vec3(0.0);
		c = mix(c, vec3(0.04), 1.0 - sm(0.0, 1.5 * px, r1 - rho));
		o = vec4(c * al, al) + o * (1.0 - al);
	}
	// 6. inner ring (3.10) and the hub CRT disc (3.3)
	if (ring_on && rho > RING0 - 1.0 && rho < RING1 + 1.0) {
		float al = clamp((rho - RING0) / px + 0.5, 0.0, 1.0) * clamp((RING1 - rho) / px + 0.5, 0.0, 1.0);
		float a = mod(th - ring_rot, 360.0);
		int seg = int(floor(mod(a + 60.0, 360.0) / 120.0)) % 3;
		float local = mod(a + 60.0, 120.0) - 60.0;
		vec3 sc = SEG_COL[seg_kind[seg]];
		vec3 c = vec3(0.13, 0.14, 0.16) * (0.85 + 0.3 * cos(radians(th - 315.0)));
		float u = local * PI / 180.0 * (RING0 + RING1) * 0.5;
		// per-segment texture across the band (ringlock.texture, simplified)
		int sk = seg_kind[seg];
		float tex = seg_tex(sk, u, rho, (RING0 + RING1) * 0.5);
		c = mix(c, sc, clamp(tex, 0.0, 1.0) * 0.55);
		// grooves between the segments, the lips with accent hairlines, a glass sheen
		float groove = 1.0 - sm(0.0, 2.2, abs(abs(local) - 60.0) * PI / 180.0 * rho);
		c *= 1.0 - 0.7 * groove;
		c += exp(-pow((rho - RING1 + 1.0) / 0.9, 2.0)) * accent.rgb * 0.9;
		c += exp(-pow((rho - RING0 - 1.0) / 0.9, 2.0)) * accent.rgb * 0.6;
		c *= seg == seg_active ? 1.0 : 0.72;
		if (seg == seg_active) {
			c += exp(-pow((rho - RING1 + 2.0) / 2.5, 2.0)) * sc * 0.8;
		}
		o = vec4(c * al, al) + o * (1.0 - al);
	}
	float hr = hub_r;
	if (rho < hr + 8.0) {
		// machined rim
		float rim_al = clamp((hr + 7.0 - rho) / px + 0.5, 0.0, 1.0);
		vec3 rim = vec3(0.16, 0.16, 0.19) * (0.8 + 0.4 * cos(radians(th - 315.0)));
		o = vec4(rim * rim_al, rim_al) + o * (1.0 - rim_al);
		float al = clamp((hr - rho) / px + 0.5, 0.0, 1.0);
		vec3 tint = hub_tint.rgb;
		vec3 c = vec3(0.035, 0.03, 0.05) + tint * 0.10 * (1.0 - rho / hr);
		// the enemy hub's slow chevron sweep / the player's concentric CRT rings
		if (theme != 0) {
			float sweep = fract((p.x + p.y * 0.4) / 46.0 - t_s * 0.08);
			c += tint * 0.08 * step(0.5, sweep) * (1.0 - rho / hr);
		} else {
			c += vec3(1.0) * 0.035 * step(0.85, fract(rho / 9.0));
		}
		c *= 0.82 + 0.18 * (0.5 + 0.5 * cos(2.0 * PI * p.y / max(3.0, 3.0 * px)));
		c *= 0.55 + 0.45 * (1.0 - sm(hr * 0.55, hr, rho));
		c += exp(-pow((rho - hr + 1.2) / max(0.9, px * 0.7), 2.0)) * accent.rgb * 1.1;
		// the defeat: the core's rows go dark from the bottom as their bits fall (the view draws them)
		if (drain > 0.0) {
			float y_rel = hr - 2.0 * hr * drain * 1.15;
			c = mix(c, vec3(0.015, 0.012, 0.02), step(y_rel, p.y));
		}
		// LOCKDOWN (round 40): the hub dims under the waterline (the bits are drawn by the view)
		float water_y = hr - 2.0 * hr * lockdown;
		c *= 1.0 - 0.45 * step(water_y, p.y) * step(0.001, lockdown);
		o = vec4(c * al, al) + o * (1.0 - al);
	}
	// 7. the active slice, lifted 2.5 % with its drop shadow and cream outline
	if (active >= 0) {
		vec2 dsh = vec2(6.0, 11.0);
		vec4 sh_t = slice_tile((p - dsh) / lift, active, 1.0);
		o.rgb *= 1.0 - 0.55 * sh_t.a;
		vec2 shift = dir_of(mids[active]) * 1.0;
		vec4 s = slice_tile(p - shift, active, lift);
		o = s + o * (1.0 - s.a);
		// the outline: ink under cream, a soft glow in the program colour
		vec2 q = (p - shift) / lift;
		float r2 = length(q);
		float t2 = mod(degrees(atan(q.x, -q.y)), 360.0);
		float dd = wrapd(t2 - mids[active]);
		float es = r2 * sin(radians(clamp(span * 0.5 - 0.9 - abs(dd), -90.0, 90.0)));
		float eo = R_OUT - 1.5 - r2;
		float ei = r2 - R_IN - 2.0;
		float e = min(min(es, eo), ei);
		float ink = 1.0 - sm(4.0, 4.0 + px, abs(e));
		float cream = 1.0 - sm(2.0, 2.0 + px, abs(e));
		float glow = exp(-pow(e / 8.0, 2.0)) * 0.5;
		o.rgb += cols[active].rgb * glow * (1.0 - ink);
		o = mix(o, vec4(0.04, 0.03, 0.06, 1.0), ink * step(-8.0, e));
		o = mix(o, vec4(0.98, 0.94, 0.84, 1.0), cream);
	}
	// 8. the glass crescent over the disc (d3-lite)
	float cres = exp(-pow((rho / R_LIP - 0.88) / 0.06, 2.0)) * pow(clamp(cos(radians(th - 315.0)), 0.0, 1.0), 2.0) * 0.10;
	o.rgb += cres * step(rho, R_LIP) * o.a;
	// whole-wheel states: the Perfect inversion, a hit flash, the defeated grey
	o.rgb = mix(o.rgb, (vec3(1.0) - o.rgb / max(o.a, 0.001)) * o.a, invert);
	o.rgb += vec3(1.0, 0.27, 0.2) * hit * o.a;
	float lum = dot(o.rgb, vec3(0.299, 0.587, 0.114));
	o.rgb = mix(o.rgb, vec3(lum) * 0.7, grey);
	COLOR = o * alpha;
}
