// Halftone (PAPER, ART_BIBLE 7.3, 13): turns a texture into two-colour risograph print:
// ink dots sized by the source's darkness on a `dot_px` grid turned by `angle`, over paper,
// with an optional second ink printed a little off register. For card illustrations and
// photocopied paper. Nothing animates: reduce effects leaves it as it is.
shader_type canvas_item;
// Reduce effects (rc_common): static already (no TIME).
#include "res://shaders/lib/rc_common.gdshaderinc"

// Dot cell (px of the item) and screen angle (rad; 15 degrees by default).
uniform float dot_px : hint_range(2.0, 24.0) = 6.0;
uniform float angle : hint_range(0.0, 1.571) = 0.2618;
// The item's size in px (0 = the texture's own size).
uniform vec2 size_px = vec2(0.0);
uniform vec4 paper : source_color = vec4(0.949, 0.933, 0.894, 1.0);
uniform vec4 ink : source_color = vec4(0.067, 0.067, 0.067, 1.0);
// The second ink, how much of it prints and how far off register (px).
uniform vec4 ink2 : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform float ink2_amount : hint_range(0.0, 1.0) = 0.0;
uniform float misregister_px : hint_range(0.0, 6.0) = 1.5;

// The largest dot's radius (a share of the cell) and its edge softness.
const float DOT_MAX = 0.72;
const float DOT_SOFT = 0.06;

float dots(vec2 px, float dark, float a) {
	mat2 rot = mat2(vec2(cos(a), sin(a)), vec2(-sin(a), cos(a)));
	vec2 f = fract(rot * px / dot_px) - 0.5;
	float r = sqrt(clamp(dark, 0.0, 1.0)) * DOT_MAX;
	return 1.0 - smoothstep(r - DOT_SOFT, r + DOT_SOFT, length(f));
}

void fragment() {
	vec2 size = size_px.x > 0.0 ? size_px : 1.0 / TEXTURE_PIXEL_SIZE;
	vec2 px = UV * size;
	vec4 src = texture(TEXTURE, UV);
	float dark = 1.0 - rc_luma(src.rgb);
	vec3 col = mix(paper.rgb, ink.rgb, dots(px, dark, angle));
	if (ink2_amount > 0.0) {
		vec2 off = vec2(misregister_px) / size;
		float dark2 = 1.0 - rc_luma(texture(TEXTURE, UV + off).rgb);
		col = mix(col, ink2.rgb, dots(px + vec2(misregister_px), dark2, angle + 0.5236) * ink2_amount);
	}
	COLOR = vec4(col, src.a * COLOR.a);
}
