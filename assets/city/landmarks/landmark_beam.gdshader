// ART-5 5b: the landmark light cones (role lm_beam: Solace's down-light cones and spotlight, Halcyon's searchlight,
// Meridian's crane lamp), the glTF side of the concept's hq_scene.mat_beam (emission mixed 0.22 over transparent).
// They stay out of the depth buffer, so the ink pass never draws them (the concept kept them out of its ink passes).
shader_type spatial;
render_mode blend_mix, unshaded, cull_disabled, depth_draw_never, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float beam_alpha = 0.22;
uniform float beam_gain = 1.0;
// LOOK L5 (designer 2026-10-20, whole-city pose): a volumetric read instead of a solid cone: the opacity falls to the
// silhouette (|N.V| ^ beam_soft; 0 = flat, the mainline look) and shimmers along a slow noise.
uniform float beam_soft = 0.0;
uniform float beam_shimmer = 0.0;
varying vec3 v_local;

void vertex() {
	v_local = VERTEX;
}

void fragment() {
	ALBEDO = COLOR.rgb * beam_gain;
	float a = beam_alpha;
	if (beam_soft > 0.0) {
		a *= pow(clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0), beam_soft);
		a *= 1.0 - beam_shimmer * (0.5 + 0.5 * sin(dot(v_local, vec3(0.7, 1.9, 0.4)) * 0.8 - TIME * 0.6));
	}
	ALPHA = a;
}
