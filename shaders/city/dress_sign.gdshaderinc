// NA-24c: the sign face shared by `dress_sign` (the opaque panel) and `dress_neon` (the flicker overlay): a panel with a frame trim
// and text-block rows in local box coordinates. Strokes are at least `core_px` pixels wide whatever the distance.
#ifndef DRESS_SIGN_INCLUDED
#define DRESS_SIGN_INCLUDED

uniform float panel_level = 0.42;
uniform float core_level = 0.9;
uniform float core_max = 0.95;
uniform float frame_w = 0.05;
uniform vec2 cell = vec2(0.16, 0.3);
uniform float stroke_h = 0.09;
uniform float fill = 0.65;
uniform float cell_gap = 0.22;
uniform float bright_var = 0.2;
uniform float side_dim = 0.6;
uniform float core_px = 2.5;

float sg_hash(vec2 c, float seed) {
	return fract(sin(dot(c + seed * 17.0, vec2(12.9898, 78.233))) * 43758.5453);
}

// Coverage of the interval [lo, hi] at x, antialiased over the pixel footprint `fw`.
float sg_band(float x, float lo, float hi, float fw) {
	float f = max(fw, 0.0001);
	return clamp((x - lo) / f + 0.5, 0.0, 1.0) * clamp((hi - x) / f + 0.5, 0.0, 1.0);
}

// (frame coverage, text-row coverage) of a sign face at coordinates `p` (BU from the piece centre) of size `sz`; `cd` = each
// stroke's (distance from its centre line, half width) for the hot core: frame in .xy, text row in .zw.
vec2 sg_core(vec2 p, vec2 sz, float seed, vec2 fw, out vec4 cd) {
	cd = vec4(1.0, 1.0, 1.0, 1.0);
	vec2 q = p + sz * 0.5;
	float pix = max(max(fw.x, fw.y), 0.0001);
	float fwid = max(frame_w, core_px * pix);
	float de = min(min(q.x, sz.x - q.x), min(q.y, sz.y - q.y));
	float frame_cov = clamp((fwid - de) / pix + 0.5, 0.0, 1.0);
	cd.xy = vec2(abs(de - fwid * 0.5), fwid * 0.5);
	vec2 inner = q - vec2(fwid * 2.0);
	vec2 isz = sz - vec2(fwid * 4.0);
	float text = 0.0;
	if (inner.x > 0.0 && inner.y > 0.0 && inner.x < isz.x && inner.y < isz.y) {
		float rows = max(floor(isz.y / cell.y), 1.0);
		float ch = isz.y / rows;
		float cols = max(floor(isz.x / cell.x), 1.0);
		float cw = isz.x / cols;
		float r = floor(inner.y / ch);
		float c = floor(inner.x / cw);
		float h = sg_hash(vec2(c, r), seed);
		float h2 = sg_hash(vec2(c + 7.0, r + 3.0), seed);
		float present = step(h, fill);
		float cx = fract(inner.x / cw) * cw;
		float cy = fract(inner.y / ch) * ch;
		float run = sg_band(cx, cw * cell_gap * 0.5, cw * (1.0 - cell_gap * 0.5), fw.x);
		float thick = min(max(stroke_h * (0.6 + 0.8 * h2), core_px * fw.y), ch * 0.6);
		float row = sg_band(cy, ch * 0.5 - thick * 0.5, ch * 0.5 + thick * 0.5, fw.y);
		text = present * run * row;
		cd.zw = vec2(abs(cy - ch * 0.5), thick * 0.5);
	}
	return vec2(frame_cov, text);
}

// `c` rescaled to luma `l` at full chroma (max channel capped at 1).
vec3 sg_at_luma(vec3 c, float l) {
	float y = max(dot(c, vec3(0.2126, 0.7152, 0.0722)), 0.001);
	vec3 o = c * l / y;
	return o / max(max(o.r, max(o.g, o.b)), 1.0);
}

#endif
