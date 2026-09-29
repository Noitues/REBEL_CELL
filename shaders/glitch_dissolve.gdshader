// Glitch dissolve (jack in / jack out, ART_BIBLE 8 T4, 13): a screen or a texture breaks
// into horizontal glitch bands with a colour split and falls away cell by cell as
// `progress` runs 0 (whole) to 1 (gone); run it backwards for an arrival. The glitch peaks
// mid-way. Band offsets change `steps` times a second from a hash of the band and the step
// (decoration only, no RNG). Reduce effects (T4 becomes a cross-fade): no bands, no split,
// no cells; the item simply fades by `progress`.
shader_type canvas_item;
// Reduce effects (rc_common): a plain cross-fade.
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float progress : hint_range(0.0, 1.0) = 0.0;
// Horizontal bands across the item, their largest sideways shift and the colour split
// (both in texture px), and how many times a second the bands jump.
uniform float bands : hint_range(4.0, 96.0) = 28.0;
uniform float shift_px : hint_range(0.0, 64.0) = 18.0;
uniform float split_px : hint_range(0.0, 8.0) = 3.0;
uniform float steps : hint_range(1.0, 30.0) = 12.0;
// Dissolve cells across the item's width, and how much of a cell's turn comes from its
// height (a top-down wipe) rather than its hash.
uniform float cells : hint_range(4.0, 128.0) = 48.0;
uniform float wipe : hint_range(0.0, 1.0) = 0.35;
// A tint the bands pick up (the net's cyan by default).
uniform vec4 tint : source_color = vec4(0.36, 0.88, 1.0, 1.0);

void fragment() {
	float live = rc_live();
	float glitch = clamp(progress * (1.0 - progress) * 4.0, 0.0, 1.0) * live;
	float step_t = floor(rc_time(TIME) * steps);
	float band = floor(UV.y * bands);
	float jump = (rc_hash(vec2(band, step_t)) - 0.5) * 2.0;
	float on = step(0.55, rc_hash(vec2(step_t, band * 1.7)));
	vec2 off = vec2(jump * on * shift_px * glitch * TEXTURE_PIXEL_SIZE.x, 0.0);
	vec2 split = vec2(split_px * glitch * TEXTURE_PIXEL_SIZE.x, 0.0);
	vec4 c = texture(TEXTURE, UV + off);
	c.r = texture(TEXTURE, UV + off - split).r;
	c.b = texture(TEXTURE, UV + off + split).b;
	c.rgb = mix(c.rgb, c.rgb * tint.rgb + tint.rgb * 0.15, on * glitch * 0.5);
	vec2 aspect = vec2(1.0, TEXTURE_PIXEL_SIZE.x / max(TEXTURE_PIXEL_SIZE.y, 1e-6));
	vec2 cell = floor(UV * cells * aspect);
	float thr = rc_hash(cell) * (1.0 - wipe) + UV.y * wipe;
	float kept = 1.0 - step(thr, progress * 1.02);
	// Under reduce effects: a cross-fade by progress instead of the cells.
	float a = mix(1.0 - progress, kept, live);
	COLOR = vec4(c.rgb, c.a * a) * vec4(1.0, 1.0, 1.0, COLOR.a);
}
