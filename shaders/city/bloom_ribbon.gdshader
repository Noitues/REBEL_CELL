// LOOK Solace THE BLOOM A "Necrosis": the vein ribbons on the road (bloom3d_ribbons.py: an emission of pink at `strength`), as an OPAQUE
// unshaded emitter so the post chain (exposure, bloom, tone map) sees it, like dress_solid. Art-owned, no clock.
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_opaque, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec3 pink = vec3(1.0, 0.0612, 0.305);
uniform float strength = 1.1;

void fragment() {
	ALBEDO = pink * strength;
}
