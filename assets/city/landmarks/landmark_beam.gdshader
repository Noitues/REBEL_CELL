// ART-5 5b: the landmark light cones (role lm_beam: Solace's down-light cones and spotlight, Halcyon's searchlight,
// Meridian's crane lamp), the glTF side of the concept's hq_scene.mat_beam (emission mixed 0.22 over transparent).
// They stay out of the depth buffer, so the ink pass never draws them (the concept kept them out of its ink passes).
shader_type spatial;
render_mode blend_mix, unshaded, cull_disabled, depth_draw_never, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float beam_alpha = 0.22;
uniform float beam_gain = 1.0;

void fragment() {
	ALBEDO = COLOR.rgb * beam_gain;
	ALPHA = beam_alpha;
}
