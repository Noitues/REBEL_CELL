// Street r2 sign board (P2 step 2): the sign texture (rasterized from the plate's draw list) shown as an emission, over a dark base, so
// a sign reads lit at night whatever the key light does. `emit` is the plan's sign emission times the config gain.
shader_type spatial;
render_mode cull_disabled, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
// LOOK Solace THE BLOOM (A Necrosis): the skin over a sign board (strength 0 = the shader as before).
#define BL_STREET
#include "res://shaders/city/bloom_necrosis.gdshaderinc"

uniform sampler2D board : source_color, filter_linear_mipmap, repeat_disable;
uniform float emit = 1.5;
uniform float base_k = 0.04;

varying vec3 bl_w;

void vertex() {
	bl_w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 t = texture(board, UV).rgb;
	ALBEDO = t * base_k;
	EMISSION = t * emit;
	ROUGHNESS = 0.6;
	if (bl_strength > 0.0) {
		bl_apply_street(bl_w, ALBEDO, EMISSION);
	}
}
