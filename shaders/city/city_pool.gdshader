// ART-5 5c: flat light on the ground (ART_BIBLE §4.3): the spotlights' bright pools and the
// strobes' spill (mode 0, a soft disc) and the hardened nodes' thin HEAT_B rings (mode 1).
// A unit quad on the ground plane (XZ, -1..1) per instance; COLOR = colour, INSTANCE_CUSTOM.x
// = alpha, .y = the ring's width as a share of its radius. Additive, depth-tested.
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int mode = 0;
uniform float gain = 1.0;

varying vec2 v_custom;

void vertex() {
	v_custom = INSTANCE_CUSTOM.xy;
}

void fragment() {
	float r = length(UV * 2.0 - 1.0);
	float a;
	if (mode == 1) {
		float w = max(v_custom.y, 0.01);
		a = smoothstep(1.0 - w * 2.0, 1.0 - w, r) * (1.0 - smoothstep(1.0 - w * 0.4, 1.0, r));
	} else {
		a = pow(max(0.0, 1.0 - r), 1.6);
	}
	ALBEDO = COLOR.rgb * gain;
	ALPHA = clamp(a * v_custom.x, 0.0, 1.0);
}
