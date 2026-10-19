// NA-ID: the flat class colour of the id pass (PIPELINE_SPEC 12.0), used as a material_override by IdCapture on landmark,
// link-structure and mover meshes. Unshaded and unfiltered: the bytes (R = class, G, B) / 255 come out exact in the 8-bit frame.
// NA-ID-b: a fragment of the mesh at or below `ground_max_y` (world y, BU) is drawn `ground_rgb` instead (the class 4 parts of a
// compound that lie on the ground); the default -1000 turns that off.
shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec3 id_rgb = vec3(0.0);
uniform vec3 ground_rgb = vec3(0.0);
uniform float ground_max_y = -1000.0;

varying float v_world_y;

vec3 id_lin(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

void vertex() {
	v_world_y = (MODEL_MATRIX * vec4(VERTEX, 1.0)).y;
}

void fragment() {
	vec3 rgb = v_world_y <= ground_max_y ? ground_rgb : id_rgb;
	ALBEDO = id_lin(rgb / 255.0);
}
