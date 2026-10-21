shader_type spatial;
render_mode cull_disabled;
// LOOK Solace HQ: the AAA-2 "Realistic night" PBR of the v5 plates (art-owned). One shader for every opaque role of the compound
// (hq_sx_*): vertex colour = base colour; alpha = emission gain on the lit roles. The strand skin is a lime glossy body with a
// uniform lime glow and a fresnel rim, its back side the warm office wall (the plates' backface mix).

uniform float roughness : hint_range(0.0, 1.0) = 0.5;
uniform float metallic : hint_range(0.0, 1.0) = 0.0;
uniform float specular : hint_range(0.0, 1.0) = 0.5;
uniform float clearcoat : hint_range(0.0, 1.0) = 0.0;
uniform float clearcoat_roughness : hint_range(0.0, 1.0) = 0.05;
uniform float albedo_k = 1.0;
uniform float emit_gain = 0.0;     // emission = vertex colour * vertex alpha * emit_gain (lit roles)
uniform float glow_k = 0.0;        // a uniform glow of glow_col (the skin's lime body glow)
uniform vec3 glow_col = vec3(0.30, 1.0, 0.06);
uniform float rim_k = 0.0;         // fresnel rim of glow_col
uniform float rim_pow = 4.0;
uniform vec3 back_albedo = vec3(0.52, 0.50, 0.47);
uniform vec3 back_emit = vec3(0.85, 0.82, 0.76);
uniform float back_k = 0.0;        // > 0: the back side is the office wall
uniform float emit_self = 0.0;     // emission = vertex colour * emit_self (built interiors: the colour lit by its own alpha)

void fragment() {
	vec4 vc = COLOR;
	vec3 base = vc.rgb * albedo_k;
	float nv = clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0);
	vec3 em = vc.rgb * vc.a * emit_gain + vc.rgb * emit_self;
	if (!FRONT_FACING && back_k > 0.0) {
		ALBEDO = back_albedo;
		EMISSION = back_emit * back_k;
		ROUGHNESS = 0.7;
		METALLIC = 0.0;
		NORMAL = -NORMAL;
	} else {
		ALBEDO = base;
		ROUGHNESS = roughness;
		METALLIC = metallic;
		SPECULAR = specular;
		CLEARCOAT = clearcoat;
		CLEARCOAT_ROUGHNESS = clearcoat_roughness;
		EMISSION = em + glow_col * (glow_k + rim_k * pow(1.0 - nv, rim_pow));
	}
}
