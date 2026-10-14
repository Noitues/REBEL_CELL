// The inner ring's ghost wedge (round 45, designer-approved 2026-10-13; docs/concepts/round45_inner_ring on
// art-pass 2216c126): over the slice under the needle, the modifier its active ring segment puts on it. One quad
// per wheel (WheelWedge, placed like the disc), one draw call. Master units (R_OUT = 360) throughout; angles
// are compass degrees clockwise from the top. Bottom to top: an ink shade, a tint wash, an ink halo under
// each mark, the marks (the modifier's mark tiled in the slice's own polar frame, halved in the read window),
// then the edge: a tint line with a soft glow. Static, but PIERCE streams and CORRUPT re-rolls on `time`,
// which the view holds at 0 under reduce effects (and rc_live() stops here too).
// Mark families (`kind`, RingMods.Kind): 0 a glyph from the glyph SDF atlas (x2 and the segment glyphs),
// 1 an outward chevron (an analytic SDF), 2 CORRUPT's dead blocks in polar cells plus three scan tears.
shader_type canvas_item;
render_mode blend_premul_alpha;

#include "res://shaders/lib/rc_common.gdshaderinc"

const vec3 INK = vec3(0.024, 0.02, 0.039);
const vec3 HALO_INK = vec3(0.024, 0.02, 0.039);

uniform float ext = 470.0;
uniform float px = 1.6;
// The modifier (RingMods id, -1 = none: nothing draws) and its tint.
uniform int mod = -1;
uniform vec4 tint : source_color = vec4(1.0, 0.824, 0.302, 1.0);
// The slice under the needle: its centre and half span (degrees).
uniform float a_mid = 0.0;
uniform float half_span = 30.0;
// The mark: family, size, row pitch, arc pitch (a chevron's column step in degrees), ink keyline.
uniform int kind = 0;
uniform float mark_size = 75.0;
uniform float mark_row = 68.0;
uniform float mark_arc = 92.0;
uniform float keyline = 0.0;
// The glyph's cell in the SDF atlas (uv rect), its box share of the cell and its distance spread
// (atlas px each side of the edge, over the cell's px).
uniform sampler2D atlas : filter_linear, repeat_disable;
uniform vec4 cell = vec4(0.0, 0.0, 0.0625, 0.125);
uniform float box_share = 0.75;
uniform float spread = 0.125;
// RingMods: geometry and the fill's strengths.
uniform float r_in = 133.0;
uniform float r_out = 353.0;
uniform float inset = 5.0;
uniform float shade = 0.25;
uniform float wash = 0.10;
uniform float halo = 0.40;
uniform float pattern = 0.38;
uniform float halo_grow = 5.0;
uniform float halo_blur = 3.0;
uniform float read_r = 268.0;
uniform vec2 read_radii = vec2(96.0, 50.0);
uniform float read_feather = 10.0;
uniform float read_clear = 0.5;
uniform float edge_w = 3.0;
uniform float edge_a = 0.9;
uniform float glow_a = 0.45;
uniform float glow_blur = 7.0;
uniform float row_lead = 0.55;
uniform float pierce_rate = 2.0;
uniform float glitch_rate = 12.0;
uniform float glitch_fill = 0.55;
uniform float glitch_pink_at = 0.88;
uniform vec4 glitch_pink : source_color = vec4(1.0, 0.239, 0.659, 1.0);
uniform float seed = 3.0;
uniform float time = 0.0;
uniform float alpha = 1.0;

// mod() by hand: the modifier uniform is named `mod` (NOTES).
float fmodp(float x, float y) {
	return x - y * floor(x / y);
}

float wrapd(float d) {
	return fmodp(d + 180.0, 360.0) - 180.0;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

vec2 dir_of(float deg) {
	float a = radians(deg);
	return vec2(sin(a), -cos(a));
}

// Coverage of a signed distance (master units, negative inside) at this pixel.
float cov(float sd) {
	return clamp(0.5 - sd / px, 0.0, 1.0);
}

// The point p in the frame of a mark centred at radius r, angle deg: x clockwise, y outward.
vec2 cell_frame(vec2 p, float r, float deg) {
	vec2 o = dir_of(deg);
	vec2 t = vec2(-o.y, o.x);
	vec2 q = p - o * r;
	return vec2(dot(q, t), dot(q, o));
}

// The glyph's signed distance (master units) at q in its frame (box = mark_size).
float glyph_sd(vec2 q) {
	float side = mark_size / box_share;
	vec2 uv = vec2(0.5 + q.x / side, 0.5 - q.y / side);
	if (uv.x <= 0.0 || uv.x >= 1.0 || uv.y <= 0.0 || uv.y >= 1.0) {
		return 1e4;
	}
	float v = texture(atlas, cell.xy + uv * cell.zw).r;
	return -(v - 0.5) * 2.0 * spread * side;
}

float seg_sd(vec2 q, vec2 a, vec2 b) {
	vec2 pa = q - a;
	vec2 ba = b - a;
	float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
	return length(pa - ba * h);
}

// The chevron pointing outward: mark_size wide, 0.55 of it tall, a stroke 0.24 of it.
float chevron_sd(vec2 q) {
	float w = mark_size * 0.5;
	float h = mark_size * 0.275;
	vec2 tip = vec2(0.0, h);
	float d = min(seg_sd(q, vec2(-w, -h), tip), seg_sd(q, vec2(w, -h), tip));
	return d - mark_size * 0.12;
}

// The nearest glyph-family mark (two rows checked so tall marks overlap cleanly). x = sd.
float glyph_field(vec2 p, float rho, float d) {
	float best = 1e4;
	float j0 = floor((rho - r_in - mark_row * row_lead) / mark_row);
	for (int s = 0; s < 2; s++) {
		float j = j0 + float(s);
		if (j < 0.0) {
			continue;
		}
		float rj = r_in + mark_row * row_lead + j * mark_row;
		float off = fmodp(j, 2.0) * 0.5;
		float u = radians(d) * rj;
		float k = floor(u / mark_arc - off + 0.5);
		float deg = a_mid + degrees((k + off) * mark_arc / rj);
		best = min(best, glyph_sd(cell_frame(p, rj, deg)));
	}
	return best;
}

// PIERCE: five fixed columns (0, +-1, +-2 steps of mark_arc degrees), rows every mark_row streaming outward.
float chevron_field(vec2 p, float rho, float d) {
	float k = clamp(floor(d / mark_arc + 0.5), -2.0, 2.0);
	float deg = a_mid + k * mark_arc;
	float ph = fract(time * pierce_rate);
	float base = r_in + mark_row * (ph - 0.5);
	float j = floor((rho - base) / mark_row + 0.5);
	float best = 1e4;
	for (int s = -1; s < 2; s++) {
		float rj = base + (j + float(s)) * mark_row;
		best = min(best, chevron_sd(cell_frame(p, rj, deg)));
	}
	return best;
}

// CORRUPT: dead blocks (mark_size square-ish polar cells, 1-3 wide per row) and three scan tears. x = sd,
// y = 1 when the hit is pink.
vec2 glitch_field(float rho, float d) {
	float q = mark_size;
	float frame = floor(time * glitch_rate);
	float row = floor((rho - r_in) / q);
	float w = 1.0 + floor(hash(vec2(row, seed)) * 3.0);
	float u = radians(d) * rho;
	float c = floor(u / (q * w));
	float h = hash(vec2(c + 17.0 * row, frame + seed));
	float sd = 1e4;
	float pink = 0.0;
	if (h > glitch_fill) {
		float ru = rho - (r_in + row * q);
		float uu = u - c * q * w;
		vec2 e = vec2(min(uu, q * w - 2.0 - uu), min(ru, q - 2.0 - ru));
		sd = -min(e.x, e.y);
		pink = step(glitch_pink_at, h);
	}
	for (int k = 0; k < 3; k++) {
		float fk = float(k);
		float rt = r_in + (r_out - r_in) * (0.18 + 0.3 * fk + 0.08 * hash(vec2(fk, seed + 1.0)));
		float s0 = -half_span + 20.0 * hash(vec2(fk, seed + 2.0));
		float s1 = s0 + half_span + half_span * hash(vec2(fk, seed + 3.0));
		float sh = (3.0 + 3.0 * hash(vec2(fk, seed + 4.0))) * (fmodp(fk, 2.0) > 0.5 ? 1.0 : -1.0);
		if (d > s0 && d < s1) {
			float tp = abs(rho - rt) - 2.5;
			if (tp < sd) {
				sd = tp;
				pink = 1.0;
			}
			float tg = abs(rho - rt - sh) - 1.5;
			if (tg < sd) {
				sd = tg;
				pink = 0.0;
			}
		}
	}
	return vec2(sd, pink);
}

vec4 over(vec4 dst, vec3 src, float a) {
	return vec4(src * a, a) + dst * (1.0 - a);
}

void fragment() {
	vec4 o = vec4(0.0);
	if (mod >= 0) {
		vec2 p = (UV - 0.5) * 2.0 * ext;
		float rho = length(p);
		float th = fmodp(degrees(atan(p.x, -p.y)), 360.0);
		float d = wrapd(th - a_mid);
		// the band: radial and angular (a constant inset on both radial edges) distances
		float side = abs(radians(d)) * rho - (radians(half_span) * rho - inset);
		float band = max(max(r_in - rho, rho - r_out), side);
		float inside = cov(band);
		vec3 tc = tint.rgb;
		if (inside > 0.0) {
			o = over(o, INK, shade * inside);
			o = over(o, tc, wash * inside);
			float sd = 1e4;
			vec3 mc = tc;
			if (kind == 0) {
				sd = glyph_field(p, rho, d);
			} else if (kind == 1) {
				sd = chevron_field(p, rho, d);
			} else {
				vec2 g = glitch_field(rho, d);
				sd = g.x;
				mc = mix(tc, glitch_pink.rgb, g.y);
			}
			// the read window: an ellipse in the slice's frame round the read block, marks and halo halved
			vec2 rq = cell_frame(p, read_r, a_mid);
			float ell = length(rq / read_radii) - 1.0;
			float win = 1.0 - smoothstep(0.0, read_feather / read_radii.y, ell);
			float keep = inside * (1.0 - read_clear * win);
			float hal = 1.0 - smoothstep(halo_grow - halo_blur, halo_grow + halo_blur, sd);
			o = over(o, HALO_INK, halo * hal * keep);
			float fill = cov(sd);
			// the keyline: the mark's outer `keyline` units in ink
			vec3 ink_mix = mix(mc, INK, keyline > 0.0 ? 1.0 - cov(sd + keyline) : 0.0);
			o = over(o, ink_mix, pattern * fill * keep);
		}
		// the edge: a glow both sides of the outline, then the line
		float g = glow_a * exp(-pow(band / glow_blur, 2.0));
		o = over(o, tc, g * (1.0 - inside * 0.5));
		o = over(o, tc, edge_a * cov(abs(band) - edge_w * 0.5));
	}
	COLOR = o * alpha;
}
