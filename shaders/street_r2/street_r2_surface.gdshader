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
// The street-level wash of the city building (NA-22c, `CityShaderConfigData.building.wash_*`): the lowest floors take the street's
// sign hues (pink / violet, one per building cell) so the facade luma rises toward the street. 0 = off (the lit materials).
uniform float wash_gain = 0.0;
uniform vec2 wash_h = vec2(4.75, 12.35);
uniform vec3 wash_a = vec3(1.0, 0.16, 0.6);
uniform vec3 wash_b = vec3(0.62, 0.38, 1.0);
uniform float wash_cell = 12.0;

varying vec3 v_col;
varying vec3 v_wpos;

void vertex() {
	v_wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
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
	} else if (wash_gain > 0.0) {
		float pick = fract(sin(floor(v_wpos.x / wash_cell) * 12.9898 + floor(v_wpos.z / wash_cell) * 78.233) * 43758.5453);
		float wash = 1.0 - smoothstep(wash_h.x, wash_h.y, v_wpos.y);
		EMISSION = mix(wash_a, wash_b, step(0.5, pick)) * wash_gain * wash;
	}
	if (!FRONT_FACING) {
		NORMAL = -NORMAL;
	}
}
