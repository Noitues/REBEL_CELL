// REBEL_CELL material kit (ART-1 1B): grease pencil wax (ART_BIBLE v2 §1.2 "Grease pencil",
// §6.3 marker_stroke.gdshader; ported from the round 3 tactical-glass concept `tg_lib.py`
// Layer.wax_stroke / light). On a Line2D (texture mode TILE: UV.x runs along the stroke in
// stroke widths, UV.y across it):
//   mode 0 wax: an opaque core with bristle striations along the stroke and dropouts toward
//          the edges, a ragged edge from the wax grain, a sheen line, alpha 0.96;
//   mode 1 shadow: the dark under-shadow (soft edge) under the wax, offset by the script;
//   mode 2 text: wax grain on glyph coverage (COLOR.a) for pencil words;
//   mode 3 art: the concepts' own baked pencil art (TEXTURE), revealed left to right to
//          `reveal` 0..1 with a ragged wax edge (B1b: it writes on, never appears whole).
// Dashed (what-if) cuts hand-dashes along UV.x. The glint runs across the wax every
// `glint_period` s (pencil_glint) and stops under reduce effects; the wax itself is static.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int mode = 0;
uniform vec4 ink : source_color = vec4(1.0, 0.886, 0.0, 1.0);
uniform float alpha_max = 0.96;
// mode 3: the share of the baked art written on (left to right).
uniform float reveal = 1.0;
uniform float seed = 1.0;
uniform bool dashed = false;
// Dash and gap lengths in stroke widths.
uniform float dash_len = 3.2;
uniform float gap_len = 1.9;
// Glint: seconds of the run, seconds between runs, strength; the span (px) it crosses.
uniform float glint_run = 0.6;
uniform float glint_rest = 3.0;
uniform float glint_strength = 0.55;
uniform vec2 glint_span = vec2(400.0, 300.0);
// Wipe smear 0..1: the wax breaks up as the palm drags it (the cloth wipe).
uniform float smear = 0.0;
// B1b (integration review D3): the stroke's width in local px (UV.x runs in widths along it)
// and the sheen line's strength (35 % white). The wax dropouts (D3 lock): each gap drawn
// uniformly from `dropout_gap` (1080p px: 40-70, seeded), a stretch `dropout_len` px long (2-4)
// where the wax's alpha falls to `dropout_alpha` (0.35), seeded (the same integer hash as
// GreasePencilMark.dropout_hit); `dropout_scale` turns local px into those 1080p px.
uniform float width_px = 6.0;
uniform float sheen = 0.35;
uniform vec2 dropout_gap = vec2(40.0, 70.0);
uniform vec2 dropout_len = vec2(2.0, 4.0);
uniform float dropout_alpha = 0.35;
uniform float dropout_scale = 1.5;
// B1b fix c: a dropout is a nibble, a ragged bite `dropout_bite` (0.4-0.7) of the stroke's width
// from one edge (the side from the seed), never a full-width break; the under-shadow fades over
// the whole gap, `dropout_pad` 1080p px past its ends (its offset), so no dark tick shows.
// Strokes are drawn with the texture STRETCHED (UV.x 0..1 over the drawn part) and
// `seg_from_px` / `seg_to_px` give that part's span along the stroke (local px), so the
// dropouts are spaced in screen px whatever the curve. Words: `word_cap_px` is the lettering's
// cap height (local px) the bite runs across.
uniform vec2 dropout_bite = vec2(0.4, 0.7);
uniform float dropout_pad = 0.0;
// The shadow's bite: this much deeper than the wax's (its offset), at most this share.
uniform float dropout_shadow_extra = 0.15;
uniform float dropout_shadow_max = 0.75;
uniform float seg_from_px = 0.0;
uniform float seg_to_px = 1.0;
uniform float word_cap_px = 20.0;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float hsh(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hsh(i), hsh(i + vec2(1.0, 0.0)), u.x), mix(hsh(i + vec2(0.0, 1.0)), hsh(i + vec2(1.0, 1.0)), u.x), u.y);
}

// A 32-bit integer hash in 0..1 (GreasePencilMark.dhash computes the same).
float dhash(int k, int s) {
	uint n = uint(k) * 374761393u + uint(s) * 668265263u;
	n = (n ^ (n >> 13u)) * 1274126177u;
	n = n ^ (n >> 16u);
	return float(n & 65535u) / 65535.0;
}

// The dropout at `d` (1080p px along the stroke), its stretch grown `pad` px each way:
// (inside 0..1 with half-px soft ends, t 0..1 along the stretch, the bitten side +-1, the bite
// as a share of the width). GreasePencilMark.dropout_hit computes the same.
vec4 dropout_hit(float d, float pad) {
	int s = int(seed);
	float pair = dropout_gap.x + dropout_gap.y;
	float dd = d + dhash(0, s + 5) * pair;  // a seeded phase: no stroke starts on a dropout
	int k = int(floor(dd / pair));
	vec4 best = vec4(0.0, 0.5, 1.0, dropout_bite.x);
	for (int pi = -1; pi <= 1; pi++) {
		int p = k + pi;
		for (int j = 0; j < 2; j++) {
			// a pair's two dropouts: at its start and one uniform gap on (the next pair's start
			// is the rest of the pair on, uniform in the same range)
			int kk = 2 * p + j;
			float c = float(p) * pair + (j == 1 ? mix(dropout_gap.x, dropout_gap.y, dhash(p, s + 4)) : 0.0);
			float half_len = mix(dropout_len.x, dropout_len.y, dhash(kk, s + 1)) * 0.5 + pad;
			float inside = 1.0 - smoothstep(half_len - 0.5, half_len + 0.5, abs(dd - c));
			if (inside > best.x) {
				float side = dhash(kk, s + 2) < 0.5 ? -1.0 : 1.0;
				float bite = mix(dropout_bite.x, dropout_bite.y, dhash(kk, s + 3));
				best = vec4(inside, clamp((dd - c) / max(half_len * 2.0, 0.001) + 0.5, 0.0, 1.0), side, bite);
			}
		}
	}
	return best;
}

// How much of the bite covers the point `across` (-1..1 over the width) for hit `h`: a ragged
// bite from the hit's side, deepest mid-stretch (`grain` roughens its front).
float bite_at(vec4 h, float across, float grain) {
	float depth = h.w * (0.7 + 0.3 * sin(3.14159 * h.y)) + (grain - 0.5) * 0.12;
	float into = h.z * across;  // 1 at the bitten edge, -1 at the far one
	return h.x * smoothstep(1.0 - 2.0 * depth - 0.06, 1.0 - 2.0 * depth + 0.06, into);
}

float glint_band(vec2 p) {
	float period = glint_run + glint_rest;
	float t = mod(rc_time(TIME), max(period, 0.01));
	float run = clamp(t / max(glint_run, 0.01), 0.0, 1.0);
	float on = step(t, glint_run) * rc_live();
	float pos = mix(-0.15, 1.15, run);
	float s = (p.x / max(glint_span.x, 1.0) * 0.78 + p.y / max(glint_span.y, 1.0) * 0.42) / 1.2;
	float band = exp(-pow((s - pos) / 0.035, 2.0)) + exp(-pow((s - pos + 0.06) / 0.012, 2.0)) * 0.6;
	return band * on * glint_strength;
}

void fragment() {
	float grain = vnoise(local_px * 0.62 + seed * 17.0) * 0.6 + vnoise(local_px * 0.25 + seed * 3.0) * 0.4;
	float mid = vnoise(local_px * 0.055 + seed * 9.0);
	if (mode == 3) {
		vec4 t = texture(TEXTURE, UV);
		float edge = reveal * 1.08 - 0.04 + (vnoise(vec2(UV.y * 40.0, seed)) - 0.5) * 0.04;
		float a = t.a * (1.0 - smoothstep(edge - 0.01, edge, UV.x));
		COLOR = vec4(t.rgb, a);
	} else if (mode == 2) {
		float a = COLOR.a;
		float tooth = smoothstep(0.06, 0.16, grain);
		a = smoothstep(0.22, 0.62, a * (0.8 + 0.2 * tooth) + (grain - 0.5) * 0.18);
		vec3 c = ink.rgb * (0.88 + 0.12 * mid);
		c += vec3(1.0, 0.98, 0.95) * glint_band(local_px) * a;
		vec4 wh = dropout_hit(local_px.x * dropout_scale, 0.0);
		float wacross = clamp(local_px.y / max(word_cap_px, 1.0) * 2.0 + 1.0, -1.0, 1.0);
		a = mix(a, min(a, dropout_alpha / alpha_max), bite_at(wh, wacross, grain));
		COLOR = vec4(c, a * alpha_max);
	} else {
		float across = UV.y * 2.0 - 1.0;
		float edge_d = abs(across);
		float along_px = mix(seg_from_px, seg_to_px, UV.x);
		float along = along_px / max(width_px, 0.001);
		if (dashed) {
			float cycle = dash_len + gap_len;
			float k = floor(along / cycle);
			float jit = (hsh(vec2(k, seed)) - 0.5) * 0.5;
			if (mod(along, cycle) > dash_len * (1.0 + jit)) {
				discard;
			}
		}
		if (mode == 1) {
			// the under-shadow: a copy of the stroke in PENCIL_SHADOW (its alpha: 85 %), a firm edge
			// so it reads under the wax on a light street too; it fades over the whole gap (and its
			// offset past it) so a nibble shows the street, never a dark tick
			float a = (1.0 - smoothstep(0.8, 1.0, edge_d)) * ink.a;
			// only under the bite (a little deeper, to cover the shadow's offset), never across
			// the far edge: the dark rim on the other side runs on unbroken, so it never reads dashed
			vec4 hs = dropout_hit(along_px * dropout_scale, dropout_pad);
			hs.w = min(hs.w + dropout_shadow_extra, dropout_shadow_max);
			a = mix(a, a * dropout_alpha, bite_at(hs, across, grain));
			COLOR = vec4(ink.rgb, a);
		} else {
			// bristles: bands across the stroke, each with its own dropouts along it
			float nb = 9.0;
			float b = floor(UV.y * nb);
			float bu = abs(b / (nb - 1.0) - 0.5) * 2.0;
			float val = vnoise(vec2(along * (1.2 + hsh(vec2(b, seed)) * 0.9), b * 13.0 + seed * 5.0));
			float thr = 0.02 + 0.30 * pow(bu, 3.0) + smear * 0.55;
			float bristle = step(thr, val);
			// the opaque body: the full wax across all but its ragged edge (bristles carry the edge)
			float core = 1.0 - smoothstep(0.8, 0.92, edge_d);
			float m = max(core * (1.0 - smear * 0.6), bristle * (1.0 - smoothstep(0.86, 1.0, edge_d)));
			float tooth = smoothstep(0.06, 0.16, grain);
			float a = m * (0.80 + 0.20 * tooth);
			a = smoothstep(0.22, 0.62, a + (grain - 0.5) * 0.18) * (0.74 + 0.26 * smoothstep(0.75, 1.0, m));
			a = clamp(a * 1.08, 0.0, 1.0);
			// the dropouts: a ragged nibble from one edge where the wax thins to ~0.35
			a = mix(a, min(a, dropout_alpha / alpha_max), bite_at(dropout_hit(along_px * dropout_scale, 0.0), across, grain));
			vec3 c = ink.rgb * (0.88 + 0.12 * mid + 0.08 * bristle);
			// the wax's round body: lit along one side, shaded along the other, a sheen line
			c *= 1.0 + 0.18 * (-across) - 0.06;
			// the sheen: a line about 1 px wide at 35 % white along the lit side
			float sh = exp(-pow((across + 0.42) / max(0.5 / max(width_px * 0.5, 1.0), 0.04), 2.0)) * sheen * (0.8 + 0.4 * mid);
			c += vec3(1.0, 0.98, 0.95) * (sh + glint_band(local_px) * (0.25 + 0.5 * grain));
			COLOR = vec4(min(c, vec3(1.25)), a * alpha_max);
		}
	}
}
