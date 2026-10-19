// NA-ID: the flat class colour of the id pass (PIPELINE_SPEC 12.0), used as a material_override by IdCapture on landmark,
// link-structure and mover meshes. Unshaded and unfiltered: the bytes (R = class, G, B) / 255 come out exact in the 8-bit frame.
shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec3 id_rgb = vec3(0.0);

vec3 id_lin(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

void fragment() {
	ALBEDO = id_lin(id_rgb / 255.0);
}
