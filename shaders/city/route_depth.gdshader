// NA-23c: the depth pass of PIPELINE_SPEC 12.0 (PNG capture only). A full-screen quad that reads the scene's depth buffer and
// writes the linear camera depth in BU x `depth_scale` as a 16-bit value: R = high byte, G = low byte (bytes / 255, drawn unlit
// like the id pass, so the 8-bit frame holds the exact bytes). Depth beyond 65535 / depth_scale BU (and the sky) is 65535.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_test_disabled, depth_draw_never, shadows_disabled, skip_vertex_transform;
#include "res://shaders/lib/rc_common.gdshaderinc"
// LOOK-TOOLBOX step 8: the id bytes decode through rc_look's rcl_to_lin (the same sRGB transfer).
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"

uniform sampler2D depth_tex : hint_depth_texture, repeat_disable, filter_nearest;
uniform float depth_scale = 100.0;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

void fragment() {
	float d = texture(depth_tex, SCREEN_UV).x;
	vec3 ndc = vec3(SCREEN_UV * 2.0 - 1.0, d);
	vec4 v = INV_PROJECTION_MATRIX * vec4(ndc, 1.0);
	v.xyz /= v.w;
	float bu = d <= 0.0 ? 1.0e6 : -v.z;
	float q = clamp(floor(bu * depth_scale + 0.5), 0.0, 65535.0);
	float hi = floor(q / 256.0);
	float lo = q - hi * 256.0;
	ALBEDO = rcl_to_lin(vec3(hi, lo, 0.0) / 255.0);
}
