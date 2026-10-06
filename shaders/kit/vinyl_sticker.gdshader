// REBEL_CELL material kit (ART-1 1B): the vinyl sticker (ART_BIBLE v2 §1.2, §6.3 "one
// CanvasItem shader for peel and gloss"; ported from round 3 combined_v2 `sticker_lib.py`
// build_sticker / apply_curl / place). Drawn over the sticker's baked art (a SubViewport:
// die-cut body, extrude, keyline, fill), it adds what needs the art's alpha:
// - the vinyl's thickness: rim light top-left, rim shade bottom-right, a dark cut line;
// - the specular gloss: a soft band and two sharp lines on a diagonal (gloss_k 0.22 at
//   rest, 1.0 while a sweep crosses; gloss_pos moves for the sweep);
// - the peel (fold): a corner folded back over the sticker, the adhesive back shaded across
//   the fold with a bright crease, the flap's cast shadow on the sticker;
// - the drop shadow (two layers; `lift` raises it: hover / peel) inside the padding;
// - dissolve (cells go in order of x with a white-hot edge: the temporary word dissolve);
// - grey (disabled: greyscale vinyl).
// Every effect is a uniform the script drives (Motion entries). Nothing here animates on
// TIME, so reduce effects is the script's end state; the include keeps the one control.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

// The die-cut body's bounding box in the art texture (px): fold corners and gloss coords.
// The sticker's baked art (its SubViewport texture; functions sample it, so it is a uniform).
uniform sampler2D art_tex : filter_linear;
uniform vec4 body_rect = vec4(0.0, 0.0, 100.0, 100.0);
uniform float gloss_k : hint_range(0.0, 1.0) = 0.22;
uniform float gloss_pos = 0.32;
uniform float gloss_angle_deg = 28.0;
// 1 = gloss vinyl, 0 = kraft (soft broad sheen, weak rim).
uniform float glossy : hint_range(0.0, 1.0) = 1.0;
uniform float rim : hint_range(0.0, 2.0) = 0.8;
uniform float fold : hint_range(0.0, 1.0) = 0.0;
// 0 top-left, 1 top-right, 2 bottom-left, 3 bottom-right.
uniform int corner = 1;
uniform vec4 backing_color : source_color = vec4(0.878, 0.867, 0.839, 1.0);
uniform vec4 shadow_color : source_color = vec4(0.024, 0.016, 0.039, 1.0);
uniform float shadow_k : hint_range(0.0, 1.0) = 1.0;
uniform float lift : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve_cell = 4.0;
uniform float grey : hint_range(0.0, 1.0) = 0.0;
// Focus: the gloss band runs in holo-foil colours (the fill keeps its own colour).
uniform float rainbow : hint_range(0.0, 1.0) = 0.0;
uniform float opacity : hint_range(0.0, 1.0) = 1.0;

float h21(vec2 p) {
	return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453);
}

vec4 art(vec2 px, vec2 tps) {
	return texture(art_tex, px * tps);
}

// The fold geometry: corner C, unit direction u (corner -> centre), fold point P, depth.
void fold_frame(out vec2 P, out vec2 u, out float depth) {
	vec2 c0 = body_rect.xy;
	vec2 c1 = body_rect.xy + body_rect.zw;
	vec2 C = vec2(corner == 1 || corner == 3 ? c1.x : c0.x, corner >= 2 ? c1.y : c0.y);
	vec2 O = (c0 + c1) * 0.5;
	vec2 d = O - C;
	float L = max(length(d), 1.0);
	u = d / L;
	depth = fold * L;
	P = C + u * depth;
}

// The sticker's alpha after the fold (what stays plus the flap folded over it).
float folded_alpha(vec2 px, vec2 tps, vec2 P, vec2 u, float depth) {
	if (fold <= 0.0) {
		return art(px, tps).a;
	}
	float s = dot(px - P, u);
	if (s < 0.0) {
		return 0.0;
	}
	float a = art(px, tps).a;
	if (s <= depth) {
		a = max(a, art(px - 2.0 * s * u, tps).a);
	}
	return a;
}

float blurred(vec2 px, vec2 tps, float radius, vec2 P, vec2 u, float depth) {
	float acc = 0.0;
	const int N = 16;
	for (int i = 0; i < N; i++) {
		float r = radius * sqrt((float(i) + 0.5) / float(N));
		float a = float(i) * 2.39996;
		acc += folded_alpha(px + vec2(cos(a), sin(a)) * r, tps, P, u, depth);
	}
	return acc / float(N);
}

void fragment() {
	vec2 tps = TEXTURE_PIXEL_SIZE;
	vec2 px = UV / tps;
	vec2 P; vec2 u; float depth;
	fold_frame(P, u, depth);
	vec4 base = art(px, tps);
	float s = dot(px - P, u);
	bool removed = fold > 0.0 && s < 0.0;
	if (removed) {
		base = vec4(0.0);
	}
	vec3 rgb = base.rgb;
	float a = base.a;

	// ---- vinyl thickness (rim) and the cut line
	if (a > 0.0) {
		float k = rim * mix(0.35, 1.0, glossy);
		float tl = art(px - vec2(2.0), tps).a;
		float br = art(px + vec2(2.0), tps).a;
		rgb = mix(rgb, vec3(1.0), clamp(a - tl, 0.0, 1.0) * 0.85 * k);
		rgb = mix(rgb, vec3(0.157, 0.141, 0.173), clamp(a - br, 0.0, 1.0) * 0.45 * k);
		float m = min(min(art(px + vec2(1.0, 0.0), tps).a, art(px - vec2(1.0, 0.0), tps).a),
				min(art(px + vec2(0.0, 1.0), tps).a, art(px - vec2(0.0, 1.0), tps).a));
		rgb = mix(rgb, vec3(0.133, 0.118, 0.149), clamp(a - m, 0.0, 1.0) * 0.7 * glossy);
		// ---- specular gloss on a diagonal across the body
		float ang = radians(gloss_angle_deg);
		vec2 dir = vec2(cos(ang), sin(ang));
		vec2 q = (px - body_rect.xy) / max(body_rect.zw, vec2(1.0));
		vec2 qs = q * body_rect.zw;
		float p00 = 0.0;
		float p10 = body_rect.z * dir.x;
		float p01 = body_rect.w * dir.y;
		float p11 = p10 + p01;
		float mn = min(min(p00, p10), min(p01, p11));
		float mx = max(max(p00, p10), max(p01, p11));
		float t = (dot(qs, dir) - mn) / max(mx - mn, 1.0);
		float soft_w = mix(0.25, 0.13, glossy);
		float soft = exp(-pow((t - gloss_pos) / soft_w, 2.0)) * mix(0.10, 0.30, glossy);
		float sharp = exp(-pow((t - gloss_pos - 0.05) / 0.016, 2.0)) * 0.65 * glossy;
		float sharp2 = exp(-pow((t - gloss_pos - 0.085) / 0.007, 2.0)) * 0.45 * glossy;
		float spec = max(max(soft, sharp), sharp2) * gloss_k;
		rgb = mix(rgb, mix(vec3(1.0, 0.96, 0.88), vec3(1.0), glossy), spec);
		if (rainbow > 0.0) {
			float band = exp(-pow((t - gloss_pos) / 0.2, 2.0));
			vec3 foil = 0.5 + 0.5 * cos(6.28318 * (vec3(0.0, 0.33, 0.67) + (t - gloss_pos) * 2.4));
			rgb = mix(rgb, foil, clamp(band * min(1.0, gloss_k * 1.4) * 0.8 * rainbow, 0.0, 1.0));
		}
	}

	// ---- the flap: the adhesive back folded over the sticker
	if (fold > 0.0 && s >= 0.0 && s <= depth) {
		float fa = art(px - 2.0 * s * u, tps).a;
		if (fa > 0.0) {
			float sf = s / max(depth, 1.0);
			vec3 back = backing_color.rgb;
			back = mix(back, vec3(0.0), 0.27 * pow(sf, 1.3));
			back = mix(back, vec3(1.0), 0.67 * exp(-pow(sf / 0.10, 2.0)));
			// the flap's own cut edge
			float fe = art(px - 2.0 * s * u + u * 1.2, tps).a;
			back = mix(back, vec3(0.275, 0.259, 0.282), clamp(fa - fe, 0.0, 1.0) * 0.5);
			rgb = mix(rgb, back, fa);
			a = max(a, fa);
		} else if (a > 0.0) {
			// the flap's cast shadow on what stays
			vec2 sp = px - vec2(4.0, 7.0);
			float ss = dot(sp - P, u);
			float fsh = 0.0;
			if (ss >= 0.0 && ss <= depth + 8.0) {
				fsh = art(sp - 2.0 * ss * u, tps).a;
			}
			rgb = mix(rgb, vec3(0.0), fsh * 0.45);
		}
	}

	// ---- dissolve: cells drop out left to right with a white-hot rim
	if (dissolve > 0.0 && a > 0.0) {
		vec2 cell = floor(px / dissolve_cell);
		float order = clamp((px.x - body_rect.x) / max(body_rect.z, 1.0), 0.0, 1.0) * 0.7 + h21(cell) * 0.3;
		float cut = dissolve * 1.15;
		if (order < cut - 0.08) {
			a = 0.0;
		} else if (order < cut) {
			rgb = mix(rgb, vec3(1.0), 0.9);
		}
	}

	// ---- disabled: greyscale vinyl
	float l = dot(rgb, vec3(0.299, 0.587, 0.114));
	rgb = mix(rgb, vec3(l), grey);

	// ---- the drop shadow under everything (contact + soft, raised by lift)
	float shadow = 0.0;
	if (shadow_k > 0.0) {
		vec2 off_soft = vec2(6.0, 10.0) + vec2(26.0, 34.0) * lift;
		float soft_a = blurred(px - off_soft, tps, 10.0 + 22.0 * lift, P, u, depth) * 0.38 * (1.0 - 0.4 * lift);
		float contact = 0.0;
		if (lift < 0.5) {
			contact = blurred(px - vec2(2.0, 3.0), tps, 2.0, P, u, depth) * 0.55 * (1.0 - 2.0 * lift);
		}
		shadow = clamp(max(soft_a, contact) * shadow_k * (1.0 - dissolve), 0.0, 1.0);
	}
	vec4 top = vec4(rgb, a);
	vec4 under = vec4(shadow_color.rgb, shadow);
	float out_a = top.a + under.a * (1.0 - top.a);
	vec3 out_rgb = (top.rgb * top.a + under.rgb * under.a * (1.0 - top.a)) / max(out_a, 0.0001);
	COLOR = vec4(out_rgb, out_a * opacity) * vec4(1.0, 1.0, 1.0, COLOR.a);
}
