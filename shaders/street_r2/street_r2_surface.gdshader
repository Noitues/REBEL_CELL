// Street r2 surface (P2 step 2): flat world colour from the vertex COLOR (the plate's `col` attribute, linear), one material per
// accumulator (conc / glass / panel / solid / win / neon). No toon ramp: MATERIAL_SPEC section 4 is a Principled surface (albedo
// colour x albedo_k, roughness, metal) and an Emission (colour x emit) for the lit materials, so the scene look (P1: exposure, fog,
// wet street) applies on top. MultiMesh props pass a tint in INSTANCE_CUSTOM (rgb, a = mix toward the tint) so one glb serves every colour.
shader_type spatial;
render_mode cull_disabled, specular_schlick_ggx;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float albedo_k = 0.85;
uniform float rough = 0.55;
uniform float metal = 0.0;
uniform float emit = 0.0;
uniform float use_tint = 0.0;

varying vec3 v_col;

void vertex() {
	vec3 tint = INSTANCE_CUSTOM.rgb;
	float k = INSTANCE_CUSTOM.a * use_tint;
	v_col = mix(COLOR.rgb, tint, k);
}

void fragment() {
	ALBEDO = v_col * albedo_k;
	ROUGHNESS = rough;
	METALLIC = metal;
	if (emit > 0.0) {
		EMISSION = v_col * emit;
	}
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
}
