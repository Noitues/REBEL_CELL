shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;
// Opaque (no depth_test_disabled: that would move it to the alpha pass, after the screen copy). The quad UV runs bottom-up.
// L3 post parity lab: a linear HDR frame drawn 1:1 into the opaque pass, so city_post's screen_tex holds exactly that frame.

uniform sampler2D src : filter_nearest;

void vertex() {
	POSITION = vec4(VERTEX.xy, 0.5, 1.0);
}

void fragment() {
	ALBEDO = texture(src, vec2(UV.x, 1.0 - UV.y)).rgb;
}
