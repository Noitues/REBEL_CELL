shader_type spatial;
render_mode blend_mix, depth_draw_never, cull_disabled, specular_schlick_ggx;
#include "res://shaders/lib/rc_common.gdshaderinc"
// LOOK Solace HQ: clear glass of the v5 plates (transparent, a faint fresnel reflection; the bridge walls, window patches, crown).
uniform float roughness = 0.12;
uniform float reflect_k = 0.15;
void fragment() {
	float nv = clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0);
	float fr = pow(1.0 - nv, 3.0);
	ALBEDO = COLOR.rgb;
	ROUGHNESS = roughness;
	SPECULAR = 0.8;
	METALLIC = 0.0;
	ALPHA = clamp(0.05 + reflect_k * 0.5 + fr * 0.6, 0.0, 0.9);
}
