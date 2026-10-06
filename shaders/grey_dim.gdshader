// ART-9 4A (ART_BIBLE v2 4.10 "the rest greyscale, darkened 60 %, padlocked"): the stock wheel's
// slices not on sale: the concept's own slice art drawn through greyscale and darkened. `grey` 0..1
// mixes to luminance, `dim` 0..1 darkens. Static (no animation, nothing for reduce effects to stop).
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float grey : hint_range(0.0, 1.0) = 1.0;
uniform float dim : hint_range(0.0, 1.0) = 0.6;

void fragment() {
	vec4 c = COLOR * texture(TEXTURE, UV);
	float l = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	c.rgb = mix(c.rgb, vec3(l), grey) * (1.0 - dim);
	COLOR = c;
}
