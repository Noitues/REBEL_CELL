// LOOK-TOOLBOX module 13: the vinyl sticker look. The forms of shaders/kit/vinyl_sticker (rim and cut line, gloss
// bands, peel / fold with the flap, the holographic band, dissolve, grey, drop shadow), shaders/kit/sticker_fill (holo
// foil fill), shaders/chrome/vinyl_sticker (marker fills, glitch bands, the x + y band, the white sweep) and
// shaders/fx/card_sticker_fx (scan front, card gloss), each the EXACT arithmetic of its source so a later migration
// is pixel-identical. Where the kit and the chrome sticker differ, both forms are kept and named (rcv_kit_*,
// rcv_chrome_*); the differences are listed in addons/rc_look/README.md "Open rulings".
// Pure functions: the wrapper shaders (rc_vinyl_kit / _chrome / _fill / _card.gdshader) own the uniforms. Every
// literal is a `const RCV_*` here, mirrored by the same-named field of look_vinyl.tres (a test keeps them equal).
// reduce effects: this file animates nothing; a wrapper passes rc_live() / rc_time(TIME) where its source did.
#ifndef RC_VINYL_INCLUDED
#define RC_VINYL_INCLUDED
#include "res://addons/rc_look/shaders/rc_hash.gdshaderinc"

// ---- rim and cut line (kit)
const float RCV_RIM_OFFSET = 2.0;
const float RCV_RIM_KRAFT_SHARE = 0.35;
const float RCV_RIM_LIGHT_K = 0.85;
const vec3 RCV_RIM_SHADE_COLOR = vec3(0.157, 0.141, 0.173);
const float RCV_RIM_SHADE_K = 0.45;
const vec3 RCV_CUT_COLOR = vec3(0.133, 0.118, 0.149);
const float RCV_CUT_K = 0.7;
const float RCV_CUT_STEP = 1.0;

// ---- gloss (kit): a soft band and two sharp lines on a diagonal
const float RCV_SOFT_W_KRAFT = 0.25;
const float RCV_SOFT_W_GLOSSY = 0.13;
const float RCV_SOFT_K_KRAFT = 0.10;
const float RCV_SOFT_K_GLOSSY = 0.30;
const float RCV_SHARP_OFF = 0.05;
const float RCV_SHARP_W = 0.016;
const float RCV_SHARP_K = 0.65;
const float RCV_SHARP2_OFF = 0.085;
const float RCV_SHARP2_W = 0.007;
const float RCV_SHARP2_K = 0.45;
const vec3 RCV_GLOSS_WARM = vec3(1.0, 0.96, 0.88);

// ---- the holographic band (kit and chrome share the foil and the band edge)
const float RCV_FOIL_TAU = 6.28318;
const vec3 RCV_FOIL_PHASE = vec3(0.0, 0.33, 0.67);
const float RCV_FOIL_DD = 0.7;
const float RCV_FOIL_POW = 0.55;
const float RCV_FOIL_GAIN = 1.3;
const float RCV_BAND_MIX = 1.6;
const float RCV_BAND_ADD = 0.25;
const float RCV_DIAG = 0.70710678;

// ---- peel / fold and the flap (kit)
const float RCV_BACK_SHADE = 0.27;
const float RCV_BACK_SHADE_POW = 1.3;
const float RCV_CREASE_K = 0.67;
const float RCV_CREASE_W = 0.10;
const float RCV_PEEL_LIGHT = 0.35;
const float RCV_FLAP_EDGE_OFF = 1.2;
const vec3 RCV_FLAP_EDGE_COLOR = vec3(0.275, 0.259, 0.282);
const float RCV_FLAP_EDGE_K = 0.5;
const vec2 RCV_FLAP_SHADOW_OFF = vec2(2.0, 3.0);
const float RCV_FLAP_SHADOW_REACH = 8.0;
const float RCV_FLAP_SHADOW_K = 0.4;

// ---- dissolve (kit)
const vec2 RCV_DISSOLVE_HASH = vec2(41.3, 289.1);
const float RCV_DISSOLVE_X = 0.7;
const float RCV_DISSOLVE_H = 0.3;
const float RCV_DISSOLVE_OVER = 1.15;
const float RCV_DISSOLVE_EDGE = 0.08;
const float RCV_DISSOLVE_WHITE = 0.9;

// ---- grey (Rec.601 on display values, kit and chrome)
const vec3 RCV_GREY_LUMA = vec3(0.299, 0.587, 0.114);

// ---- drop shadow (kit): a soft disc raised by lift, and a contact shadow
const float RCV_BLUR_GOLDEN = 2.39996;
const vec2 RCV_SHADOW_OFF = vec2(6.0, 10.0);
const vec2 RCV_SHADOW_OFF_LIFT = vec2(26.0, 34.0);
const float RCV_SHADOW_R = 10.0;
const float RCV_SHADOW_R_LIFT = 22.0;
const float RCV_SHADOW_K = 0.38;
const float RCV_SHADOW_K_LIFT = 0.4;
const vec2 RCV_CONTACT_OFF = vec2(2.0, 3.0);
const float RCV_CONTACT_R = 2.0;
const float RCV_CONTACT_K = 0.55;
const float RCV_CONTACT_LIFT_MAX = 0.5;
const float RCV_CONTACT_LIFT_FALL = 2.0;

// ---- chrome markers and fills
const float RCV_MARKER_MIN = 0.02;
const float RCV_MARKER_OFF = 0.01;
const float RCV_MARKER_EQ = 0.02;
const float RCV_GLITCH_BANDS = 8.0;
const float RCV_FILL_GLOSS_END = 0.42;
const float RCV_SWEEP_WHITE_K = 0.6;
const float RCV_SWEEP_SLANT = 0.45;
const float RCV_SCAN_LINE_PX = 1.0;

// ---- holo foil fill (sticker_fill mode 1)
const float RCV_HOLO_TAU = 6.28;
const vec2 RCV_HOLO_UV = vec2(0.85, 0.55);
const float RCV_HOLO_WARP1 = 0.10;
const vec2 RCV_HOLO_WARP1_F = vec2(7.0, 0.0);
const float RCV_HOLO_WARP2 = 0.08;
const vec2 RCV_HOLO_WARP2_F = vec2(6.0, 3.0);
const float RCV_HOLO_VAL = 0.93;
const float RCV_HOLO_VAL_AMP = 0.07;
const float RCV_HOLO_VAL_F = 9.0;
const float RCV_HOLO_SILVER = 0.78;
const vec3 RCV_HOLO_SILVER_ADD = vec3(0.20, 0.20, 0.22);
const float RCV_HOLO_LINE_PX = 5.0;
const float RCV_HOLO_LINE_SLANT = 0.6;
const float RCV_HOLO_LINE_STEP = 0.82;
const float RCV_HOLO_LINE_K = 0.18;
const float RCV_HOLO_SPARK_CELL = 9.0;
const vec2 RCV_HOLO_SPARK_SALT = vec2(3.1, 7.7);
const float RCV_HOLO_SPARK_STEP = 0.86;
const vec2 RCV_HOLO_SPARK_EDGE = vec2(1.6, 0.4);
const float RCV_HOLO_SPARK_K = 0.8;

// ---- card stand-in
const float RCV_CARD_SCAN_K = 0.85;

// ============================================================================================================
// Art sampling and the fold
// ============================================================================================================

struct RcvFold {
	vec2 P;
	vec2 u;
	float depth;
	bool on;
};

vec4 rcv_art(sampler2D tex, vec2 px, vec2 tps) {
	return texture(tex, px * tps);
}

// The fold geometry: corner C (0 top-left, 1 top-right, 2 bottom-left, 3 bottom-right), unit direction u (corner ->
// centre), fold point P, depth. peel_back > 0 is the fixed 45 degree fold with legs of peel_back * peel_px.
RcvFold rcv_fold_frame(vec4 body, int corner, float fold, float peel_back, float peel_px) {
	RcvFold f;
	f.on = fold > 0.0 || peel_back > 0.0;
	vec2 c0 = body.xy;
	vec2 c1 = body.xy + body.zw;
	vec2 C = vec2(corner == 1 || corner == 3 ? c1.x : c0.x, corner >= 2 ? c1.y : c0.y);
	vec2 O = (c0 + c1) * 0.5;
	vec2 d = O - C;
	float L = max(length(d), 1.0);
	f.u = d / L;
	f.depth = fold * L;
	if (peel_back > 0.0) {
		f.u = vec2(sign(d.x), sign(d.y)) * RCV_DIAG;
		f.depth = peel_back * peel_px * RCV_DIAG;
	}
	f.P = C + f.u * f.depth;
	return f;
}

// The sticker's alpha after the fold (what stays plus the flap folded over it).
float rcv_folded_alpha(sampler2D tex, vec2 px, vec2 tps, RcvFold f) {
	if (!f.on) {
		return rcv_art(tex, px, tps).a;
	}
	float s = dot(px - f.P, f.u);
	if (s < 0.0) {
		return 0.0;
	}
	float a = rcv_art(tex, px, tps).a;
	if (s <= f.depth) {
		a = max(a, rcv_art(tex, px - 2.0 * s * f.u, tps).a);
	}
	return a;
}

float rcv_blurred(sampler2D tex, vec2 px, vec2 tps, float radius, RcvFold f) {
	float acc = 0.0;
	const int N = 16;
	for (int i = 0; i < N; i++) {
		float r = radius * sqrt((float(i) + 0.5) / float(N));
		float a = float(i) * RCV_BLUR_GOLDEN;
		acc += rcv_folded_alpha(tex, px + vec2(cos(a), sin(a)) * r, tps, f);
	}
	return acc / float(N);
}

// ============================================================================================================
// Kit: rim, gloss, band, flap, dissolve, grey, shadow, composite
// ============================================================================================================

// The vinyl's thickness: rim light top-left, rim shade bottom-right, a dark cut line. `a` is the pixel's alpha.
vec3 rcv_kit_rim(vec3 rgb, float a, sampler2D tex, vec2 px, vec2 tps, float rim, float glossy) {
	float k = rim * mix(RCV_RIM_KRAFT_SHARE, 1.0, glossy);
	float tl = rcv_art(tex, px - vec2(RCV_RIM_OFFSET), tps).a;
	float br = rcv_art(tex, px + vec2(RCV_RIM_OFFSET), tps).a;
	rgb = mix(rgb, vec3(1.0), clamp(a - tl, 0.0, 1.0) * RCV_RIM_LIGHT_K * k);
	rgb = mix(rgb, RCV_RIM_SHADE_COLOR, clamp(a - br, 0.0, 1.0) * RCV_RIM_SHADE_K * k);
	float m = min(min(rcv_art(tex, px + vec2(RCV_CUT_STEP, 0.0), tps).a, rcv_art(tex, px - vec2(RCV_CUT_STEP, 0.0), tps).a),
			min(rcv_art(tex, px + vec2(0.0, RCV_CUT_STEP), tps).a, rcv_art(tex, px - vec2(0.0, RCV_CUT_STEP), tps).a));
	rgb = mix(rgb, RCV_CUT_COLOR, clamp(a - m, 0.0, 1.0) * RCV_CUT_K * glossy);
	return rgb;
}

// The gloss coordinate t (0..1 along the diagonal across the body) of pixel px.
float rcv_kit_gloss_t(vec2 px, vec4 body, float angle_deg) {
	float ang = radians(angle_deg);
	vec2 dir = vec2(cos(ang), sin(ang));
	vec2 q = (px - body.xy) / max(body.zw, vec2(1.0));
	vec2 qs = q * body.zw;
	float p00 = 0.0;
	float p10 = body.z * dir.x;
	float p01 = body.w * dir.y;
	float p11 = p10 + p01;
	float mn = min(min(p00, p10), min(p01, p11));
	float mx = max(max(p00, p10), max(p01, p11));
	return (dot(qs, dir) - mn) / max(mx - mn, 1.0);
}

// The specular strength (0..1) at gloss coordinate t.
float rcv_kit_spec(float t, float gloss_k, float gloss_pos, float glossy) {
	float soft_w = mix(RCV_SOFT_W_KRAFT, RCV_SOFT_W_GLOSSY, glossy);
	float soft = exp(-pow((t - gloss_pos) / soft_w, 2.0)) * mix(RCV_SOFT_K_KRAFT, RCV_SOFT_K_GLOSSY, glossy);
	float sharp = exp(-pow((t - gloss_pos - RCV_SHARP_OFF) / RCV_SHARP_W, 2.0)) * RCV_SHARP_K * glossy;
	float sharp2 = exp(-pow((t - gloss_pos - RCV_SHARP2_OFF) / RCV_SHARP2_W, 2.0)) * RCV_SHARP2_K * glossy;
	return max(max(soft, sharp), sharp2) * gloss_k;
}

vec3 rcv_kit_gloss(vec3 rgb, vec2 px, vec4 body, float gloss_k, float gloss_pos, float angle_deg, float glossy) {
	float spec = rcv_kit_spec(rcv_kit_gloss_t(px, body, angle_deg), gloss_k, gloss_pos, glossy);
	return mix(rgb, mix(RCV_GLOSS_WARM, vec3(1.0), glossy), spec);
}

// The holographic foil colour at band coordinate dd (-1..1 across the band). Kit and chrome use this one form.
vec3 rcv_foil(float dd) {
	return clamp(pow(0.5 + 0.5 * cos(RCV_FOIL_TAU * (RCV_FOIL_PHASE + dd * RCV_FOIL_DD)), vec3(RCV_FOIL_POW)) * RCV_FOIL_GAIN, 0.0, 1.0);
}

// The band's falloff at dd.
float rcv_band_w(float dd) {
	return 1.0 - smoothstep(0.0, 1.0, abs(dd));
}

// The foil laid over base: w the band falloff, alpha the band strength, cover the coverage (kit 1.0, chrome the
// glyph's alpha).
vec3 rcv_band_mix(vec3 base, vec3 foil, float w, float alpha, float cover) {
	return clamp(mix(base, foil, clamp(w * alpha * RCV_BAND_MIX, 0.0, 1.0) * cover) + vec3(w * alpha * RCV_BAND_ADD * cover), 0.0, 1.0);
}

// Kit band coordinate dd of pixel px: ONE band at band_deg crossing the body (band_t 0..1 across it).
float rcv_kit_band_dd(vec2 px, vec4 body, float band_t, float band_width, float band_deg) {
	float bd = radians(band_deg);
	vec2 bdir = vec2(cos(bd), sin(bd));
	vec2 n = vec2(-bdir.y, bdir.x);
	float half_w = 0.5 * band_width * body.z;
	float n0 = dot(body.xy, n);
	float n1 = dot(body.xy + vec2(body.z, 0.0), n);
	float n2 = dot(body.xy + vec2(0.0, body.w), n);
	float n3 = dot(body.xy + body.zw, n);
	float lo = min(min(n0, n1), min(n2, n3)) - half_w;
	float hi = max(max(n0, n1), max(n2, n3)) + half_w;
	float centre = mix(lo, hi, band_t);
	return (dot(px, n) - centre) / max(half_w, 1.0);
}

// The flap: the adhesive back folded over the sticker, or the flap's cast shadow on what stays. s = dot(px - P, u).
void rcv_kit_flap(sampler2D tex, vec2 px, vec2 tps, RcvFold f, float s, vec3 backing, float peel_back, inout vec3 rgb, inout float a) {
	if (f.on && s >= 0.0 && s <= f.depth) {
		float fa = rcv_art(tex, px - 2.0 * s * f.u, tps).a;
		if (fa > 0.0) {
			float sf = s / max(f.depth, 1.0);
			vec3 back = backing;
			back = mix(back, vec3(0.0), RCV_BACK_SHADE * pow(sf, RCV_BACK_SHADE_POW));
			back = mix(back, vec3(1.0), RCV_CREASE_K * exp(-pow(sf / RCV_CREASE_W, 2.0)));
			back = mix(back, vec3(1.0), RCV_PEEL_LIGHT * peel_back);
			float fe = rcv_art(tex, px - 2.0 * s * f.u + f.u * RCV_FLAP_EDGE_OFF, tps).a;
			back = mix(back, RCV_FLAP_EDGE_COLOR, clamp(fa - fe, 0.0, 1.0) * RCV_FLAP_EDGE_K);
			rgb = mix(rgb, back, fa);
			a = max(a, fa);
		} else if (a > 0.0) {
			vec2 sp = px - RCV_FLAP_SHADOW_OFF;
			float ss = dot(sp - f.P, f.u);
			float fsh = 0.0;
			if (ss >= 0.0 && ss <= f.depth + RCV_FLAP_SHADOW_REACH) {
				fsh = rcv_art(tex, sp - 2.0 * ss * f.u, tps).a;
			}
			rgb = mix(rgb, vec3(0.0), fsh * RCV_FLAP_SHADOW_K);
		}
	}
}

float rcv_h21(vec2 p) {
	return fract(sin(dot(p, RCV_DISSOLVE_HASH)) * 43758.5453);
}

// The dissolve order of pixel px (0..1: x across the body, the cell hash on top).
float rcv_dissolve_order(vec2 px, vec4 body, float cell_px) {
	vec2 cell = floor(px / cell_px);
	return clamp((px.x - body.x) / max(body.z, 1.0), 0.0, 1.0) * RCV_DISSOLVE_X + rcv_h21(cell) * RCV_DISSOLVE_H;
}

void rcv_kit_dissolve(vec2 px, vec4 body, float dissolve, float cell_px, inout vec3 rgb, inout float a) {
	if (dissolve > 0.0 && a > 0.0) {
		float order = rcv_dissolve_order(px, body, cell_px);
		float cut = dissolve * RCV_DISSOLVE_OVER;
		if (order < cut - RCV_DISSOLVE_EDGE) {
			a = 0.0;
		} else if (order < cut) {
			rgb = mix(rgb, vec3(1.0), RCV_DISSOLVE_WHITE);
		}
	}
}

vec3 rcv_grey(vec3 rgb, float grey) {
	float l = dot(rgb, RCV_GREY_LUMA);
	return mix(rgb, vec3(l), grey);
}

// The drop shadow alpha under everything (contact + soft, raised by lift).
float rcv_kit_shadow(sampler2D tex, vec2 px, vec2 tps, RcvFold f, float lift, float shadow_k, float dissolve) {
	float shadow = 0.0;
	if (shadow_k > 0.0) {
		vec2 off_soft = RCV_SHADOW_OFF + RCV_SHADOW_OFF_LIFT * lift;
		float soft_a = rcv_blurred(tex, px - off_soft, tps, RCV_SHADOW_R + RCV_SHADOW_R_LIFT * lift, f) * RCV_SHADOW_K * (1.0 - RCV_SHADOW_K_LIFT * lift);
		float contact = 0.0;
		if (lift < RCV_CONTACT_LIFT_MAX) {
			contact = rcv_blurred(tex, px - RCV_CONTACT_OFF, tps, RCV_CONTACT_R, f) * RCV_CONTACT_K * (1.0 - RCV_CONTACT_LIFT_FALL * lift);
		}
		shadow = clamp(max(soft_a, contact) * shadow_k * (1.0 - dissolve), 0.0, 1.0);
	}
	return shadow;
}

// The sticker over its shadow (straight alpha), times the opacity.
vec4 rcv_kit_composite(vec3 rgb, float a, vec3 shadow_rgb, float shadow, float opacity, float canvas_a) {
	vec4 top = vec4(rgb, a);
	vec4 under = vec4(shadow_rgb, shadow);
	float out_a = top.a + under.a * (1.0 - top.a);
	vec3 out_rgb = (top.rgb * top.a + under.rgb * under.a * (1.0 - top.a)) / max(out_a, 0.0001);
	return vec4(out_rgb, out_a * opacity) * vec4(1.0, 1.0, 1.0, canvas_a);
}

// ============================================================================================================
// Chrome: marker decode, gradient + rest gloss + white sweep, glitch bands, the x + y band
// ============================================================================================================

// Decodes the vertex colour: kind 1 magenta (r = b, g = 0), kind 2 green (r = 0, g >= b; band = b / g * 8). The caller
// starts with kind 0, band 0, bright 1.
void rcv_chrome_marker(vec4 col, out float kind, out float bright, out float band) {
	kind = 0.0;
	bright = 1.0;
	band = 0.0;
	float hi = max(col.r, max(col.g, col.b));
	if (hi > RCV_MARKER_MIN) {
		if (col.g < RCV_MARKER_OFF * hi && abs(col.r - col.b) < RCV_MARKER_EQ * hi) {
			kind = 1.0;
			bright = col.r;
		} else if (col.r < RCV_MARKER_OFF * hi && col.g >= col.b) {
			kind = 2.0;
			bright = col.g;
			band = floor(col.b / col.g * RCV_GLITCH_BANDS + 0.5);
		}
	}
}

// The magenta fill: vertical gradient, the rest gloss at the top of the fill, then the WHITE sweep band (live = rc_live()).
vec3 rcv_chrome_marker_fill(vec2 local, float fill_top, float fill_bottom, vec3 top_c, vec3 bottom_c, float gloss, float sweep, float sweep_width, float live) {
	float t = clamp((local.y - fill_top) / max(1.0, fill_bottom - fill_top), 0.0, 1.0);
	vec3 rgb = mix(top_c, bottom_c, t);
	rgb = mix(rgb, vec3(1.0), gloss * (1.0 - smoothstep(0.0, RCV_FILL_GLOSS_END, t)));
	float d = abs((local.x - sweep) + (local.y - fill_top) * RCV_SWEEP_SLANT);
	rgb = mix(rgb, vec3(1.0), RCV_SWEEP_WHITE_K * live * (1.0 - smoothstep(0.0, sweep_width, d)));
	return rgb;
}

// The glitch fill's band cut: false = discard this pixel (band > 0 keeps only its horizontal band).
bool rcv_chrome_glitch_keep(vec2 local, float fill_top, float band, float band_h) {
	if (band > 0.5) {
		float y0 = fill_top + (band - 1.0) * band_h;
		if (local.y < y0 || local.y >= y0 + band_h) {
			return false;
		}
	}
	return true;
}

// The glitch fill colour: white with thin scan lines alternating glitch_a / glitch_b.
vec3 rcv_chrome_glitch(vec2 local, float fill_top, float scan_period, vec3 white_c, vec3 a_c, vec3 b_c) {
	vec3 rgb = white_c;
	float row = floor((local.y - fill_top) / scan_period);
	if (mod(local.y - fill_top, scan_period) < RCV_SCAN_LINE_PX) {
		rgb = mod(row, 2.0) < 0.5 ? a_c : b_c;
	}
	return rgb;
}

// The chrome band coordinate dd: the band lines are x + y = sweep.
float rcv_chrome_band_dd(vec2 local, float sweep, float sweep_width) {
	return (local.x + local.y - sweep) * RCV_DIAG / max(sweep_width, 1.0);
}

// ============================================================================================================
// Holo foil fill (sticker_fill mode 1)
// ============================================================================================================

vec3 rcv_hsv2rgb(vec3 c) {
	vec3 p = abs(fract(c.xxx + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
	return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

// phase = rc_time(TIME) * holo_drift (the caller supplies it, so reduce effects freezes it).
vec3 rcv_holo_fill(vec2 px, vec2 field_size, float seed, float phase, float sat) {
	vec2 uv = px / max(field_size, vec2(1.0));
	float a1 = rcl_hash12_sin(vec2(seed, 1.0)) * RCV_HOLO_TAU;
	float a2 = rcl_hash12_sin(vec2(seed, 2.0)) * RCV_HOLO_TAU;
	float a3 = rcl_hash12_sin(vec2(seed, 3.0)) * RCV_HOLO_TAU;
	float hue = fract(RCV_HOLO_UV.x * uv.x + RCV_HOLO_UV.y * uv.y + RCV_HOLO_WARP1 * sin(RCV_HOLO_WARP1_F.x * uv.x + a1)
			+ RCV_HOLO_WARP2 * sin(RCV_HOLO_WARP2_F.x * uv.y + RCV_HOLO_WARP2_F.y * uv.x + a2) + phase);
	float val = RCV_HOLO_VAL + RCV_HOLO_VAL_AMP * sin(RCV_HOLO_VAL_F * (uv.x - uv.y) + a3 + phase * RCV_HOLO_TAU);
	vec3 c = rcv_hsv2rgb(vec3(hue, sat, val));
	c = c * RCV_HOLO_SILVER + RCV_HOLO_SILVER_ADD;
	float line = step(RCV_HOLO_LINE_STEP, fract((px.x - px.y * RCV_HOLO_LINE_SLANT) / RCV_HOLO_LINE_PX));
	c = mix(c, vec3(1.0), line * RCV_HOLO_LINE_K);
	vec2 cell = floor(px / RCV_HOLO_SPARK_CELL);
	float sp = rcl_hash12_sin(cell + seed);
	vec2 at = (cell + vec2(rcl_hash12_sin(cell + RCV_HOLO_SPARK_SALT.x), rcl_hash12_sin(cell + RCV_HOLO_SPARK_SALT.y))) * RCV_HOLO_SPARK_CELL;
	float d = length(px - at);
	c = mix(c, vec3(1.0), step(RCV_HOLO_SPARK_STEP, sp) * smoothstep(RCV_HOLO_SPARK_EDGE.x, RCV_HOLO_SPARK_EDGE.y, d) * RCV_HOLO_SPARK_K);
	return clamp(c, 0.0, 1.0);
}

// The gradient fill over [band_top, band_bottom].
vec3 rcv_gradient_fill(float y, float band_top, float band_bottom, vec3 top_c, vec3 bottom_c) {
	float t = clamp((y - band_top) / max(band_bottom - band_top, 1.0), 0.0, 1.0);
	return mix(top_c, bottom_c, t);
}

// ============================================================================================================
// Card stand-in (card_sticker_fx)
// ============================================================================================================

// The scan front's height share for scan_y.
float rcv_card_front(float scan_y, float edge_share) {
	return mix(-edge_share, 1.0 + edge_share, scan_y);
}

// The white-hot line just under the decoded part.
vec3 rcv_card_scan_line(vec3 rgb, vec3 front_c) {
	return mix(rgb, front_c, RCV_CARD_SCAN_K);
}

// The diagonal gloss band (live = rc_live()).
vec3 rcv_card_gloss(vec3 rgb, vec2 uv, float gloss_t, float gloss_width, float gloss_alpha, float live) {
	float d = abs((uv.x + uv.y) * 0.5 - gloss_t);
	float g = smoothstep(gloss_width, 0.0, d) * gloss_alpha * live;
	return mix(rgb, vec3(1.0), g);
}

#endif
