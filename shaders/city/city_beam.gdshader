// ART-5 5c: light beams (ART_BIBLE §4.3: the searchlights' sweeps, the choppers' and drones'
// spotlights). A unit cone (apex at the origin, opening along -Y to radius 1 at length 1,
// UV.y = 0 at the apex .. 1 at the open end) placed per instance by the layer (CPU: a
// handful of beams). Brightest at the apex, fading along the beam and toward its soft
// edges. COLOR = the beam colour, INSTANCE_CUSTOM.x = its alpha. Additive, depth-tested.
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float gain = 1.0;

varying float v_alpha;

void vertex() {
	v_alpha = INSTANCE_CUSTOM.x;
}

void fragment() {
	float along = pow(1.0 - clamp(UV.y, 0.0, 1.0), 1.3);
	float edge = pow(abs(dot(normalize(NORMAL), normalize(VIEW))), 1.4);
	ALBEDO = COLOR.rgb * gain;
	ALPHA = clamp(v_alpha * along * (0.25 + 0.75 * edge), 0.0, 1.0);
}
