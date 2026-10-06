// Parity END-01 (ported from art-m13-final run_end_stage.gd GRADE_CODE, art pass W8c / W9F): the city
// behind a lost run's end drawn through greyscale and dimmed: the screen as drawn under the page is
// read back, mixed to its luminance by `grey` and darkened by `dim`. Static (no animation; the page's
// own entrance brings it in, reduce effects shows it at once).
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
uniform float grey : hint_range(0.0, 1.0) = 1.0;
uniform float dim : hint_range(0.0, 1.0) = 0.35;

void fragment() {
	vec3 c = textureLod(screen_texture, SCREEN_UV, 0.0).rgb;
	float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
	COLOR = vec4(mix(c, vec3(l), grey) * (1.0 - dim), 1.0);
}
