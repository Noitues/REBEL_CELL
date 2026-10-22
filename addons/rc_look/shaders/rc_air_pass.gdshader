// LOOK-TOOLBOX module 7: the 3D air pass. A full-screen quad (RcLookAir.pass_node) that reads the depth buffer, finds
// each pixel's distance from the eye and its world height, and lays the air over it (rcl_air), blended in the render
// buffer's linear light toward the air colour (the sky's horizon). The sky itself (no geometry) is left alone. Static.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, depth_test_disabled, cull_disabled, shadows_disabled, fog_disabled;

#include "res://addons/rc_look/shaders/rc_air.gdshaderinc"

uniform sampler2D depth_tex : hint_depth_texture, filter_nearest;
uniform vec3 air = vec3(0.275, 0.247, 0.361);
uniform vec4 air_a = vec4(0.0, 0.002, 30.0, 0.15);
// Height of the ground the air sits on (world y).
uniform float ground_y = 0.0;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

void fragment() {
	float depth = texture(depth_tex, SCREEN_UV).r;
	if (depth <= 0.0) {
		discard;  // reverse-Z far plane: the sky
	}
	vec4 view = INV_PROJECTION_MATRIX * vec4(SCREEN_UV * 2.0 - 1.0, depth, 1.0);
	view.xyz /= view.w;
	vec3 world = (INV_VIEW_MATRIX * vec4(view.xyz, 1.0)).xyz;
	float a = rcl_air(length(view.xyz), world.y - ground_y, air_a);
	ALBEDO = rcl_to_lin(air);
	ALPHA = a;
}
