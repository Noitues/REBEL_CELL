// Glass blur (ART_BIBLE 3.3 SCRIM, 13): the backing of every glass panel and modal that
// sits over the city. It blurs what is behind it (the screen texture) by `blur_px` and
// lays the SCRIM tint over that at `tint_alpha` (bible: #02030A at 55% + 6 px blur). Put
// it on a ColorRect sized to the panel, under the panel's own glass. The view sets `tint`
// from Palette.SCRIM. Nothing here animates: reduce effects leaves it as it is (high
// contrast's opaque panels are the view's choice, ART_BIBLE 12).
shader_type canvas_item;
// Reduce effects (rc_common): static already (no TIME).
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
// Blur radius in screen px (bible 3.3: 6).
uniform float blur_px : hint_range(0.0, 32.0) = 6.0;
// The scrim colour and how much of it covers the blurred city (bible 3.3: 55%).
uniform vec4 tint : source_color = vec4(0.008, 0.012, 0.039, 1.0);
uniform float tint_alpha : hint_range(0.0, 1.0) = 0.55;

// Two rings of six taps (at half and full radius) round a centre tap, read from a mip
// level matched to the tap spacing: a smooth, cheap, wide kernel.
const float W_CENTRE = 0.16;
const float W_INNER = 0.09;
const float W_OUTER = 0.05;

void fragment() {
	vec2 step_uv = SCREEN_PIXEL_SIZE * blur_px;
	float lod = log2(max(blur_px * 0.5, 1.0));
	vec3 acc = textureLod(screen_texture, SCREEN_UV, lod).rgb * W_CENTRE;
	for (int k = 0; k < 6; k++) {
		float a = TAU * float(k) / 6.0;
		vec2 d = vec2(cos(a), sin(a));
		acc += textureLod(screen_texture, SCREEN_UV + d * step_uv * 0.5, lod).rgb * W_INNER;
		vec2 d2 = vec2(cos(a + PI / 6.0), sin(a + PI / 6.0));
		acc += textureLod(screen_texture, SCREEN_UV + d2 * step_uv, lod).rgb * W_OUTER;
	}
	COLOR = vec4(mix(acc, tint.rgb, tint_alpha), COLOR.a);
}
