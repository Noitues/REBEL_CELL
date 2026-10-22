// LOOK-TOOLBOX module 15: the decrypted holo (ART_BIBLE §1.2: hacked corp intel, never anything the Cell owns).
// A translucent tinted glass (the city shows through, blurred and dimmed), 4 px scanlines, slow scan bands, and an
// edge that splits into three offset channels (edge only, never the words). Two passes over one panel rect:
//   glass (under the words): rcl_holo_glass;  over (above the words): rcl_holo_over.
// Include rc_look.gdshaderinc first. Pure functions: the wrapper shader (rc_holo.gdshader) owns the uniforms.
#ifndef RC_HOLO_INCLUDED
#define RC_HOLO_INCLUDED

// Signed distance to the panel rect (panel = x, y, w, h in the same space as p).
float rcl_holo_sd(vec2 p, vec4 panel) {
	vec2 q = abs(p - (panel.xy + panel.zw * 0.5)) - panel.zw * 0.5;
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0);
}

// The edge line of width `w` at p, 0..1.
float rcl_holo_edge(vec2 p, vec4 panel, float w) {
	float d = abs(rcl_holo_sd(p, panel) + w * 0.5);
	return 1.0 - smoothstep(w * 0.5, w * 0.5 + 1.0, d);
}

// The outer glow of the edge: falls off over `glow_px` outside (and a little inside) the rect.
float rcl_holo_glow(vec2 p, vec4 panel, float glow_px) {
	float d = rcl_holo_sd(p, panel);
	return exp(-max(d, 0.0) / max(glow_px, 0.5)) * step(0.0, d) * 0.9 + exp(-max(-d, 0.0) / (glow_px * 0.5)) * step(d, 0.0) * 0.35;
}

// The edge ink: the tint lifted toward white, so the channel split shows as a fringe whatever the corp's hue.
vec3 rcl_holo_edge_ink(vec3 tint, float lift) {
	return mix(tint, vec3(1.0), lift);
}

// The edge in three channels split `split_px` horizontally: red out one side, blue out the other, green in the middle,
// each channel scaled by the ink. Returns rgb in .rgb and the coverage in .a. split_px 0 gives the plain edge.
vec4 rcl_holo_split_edge(vec2 p, vec4 panel, float w, float split_px, vec3 ink) {
	float er = rcl_holo_edge(p + vec2(split_px, 0.0), panel, w);
	float eg = rcl_holo_edge(p, panel, w);
	float eb = rcl_holo_edge(p - vec2(split_px, 0.0), panel, w);
	float a = max(max(er, eg), eb);
	return vec4(vec3(er, eg, eb) * ink / max(a, 0.001), a);
}

// The scan bands at height share y (0..1 down the panel): `count` bands, each a sharp leading edge and a soft trail.
// `phase` is the roll (one unit = one band period); frozen bands pass a fixed phase.
float rcl_holo_bands(float y, float count, float phase, float trail) {
	float f = fract(y * count - phase);
	return pow(1.0 - f, trail) * smoothstep(0.0, 0.03, f);
}

// The 4 px scanline pattern: 1 on the bright half of each period.
float rcl_holo_scan(float y_px, float period_px) {
	return step(0.5, fract(y_px / max(period_px, 1.0)));
}

// The dark glass colour at height share t: the tint's share over the deep colour, graded toward the foot.
vec3 rcl_holo_body(vec3 tint, vec3 deep, float fill_share, float foot_share, float t) {
	return mix(deep, tint, fill_share * mix(1.0, foot_share, t));
}

#endif
