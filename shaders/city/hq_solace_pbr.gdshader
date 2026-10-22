shader_type spatial;
render_mode cull_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"
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
uniform bool neon_core = false;   // the neon role (hq_sx_neon): its tubes get the hot core
// LOOK-TOOLBOX module 11 (designer DIRECTION_REVIEW f4678fca, b727956a): each neon tube's hot core, rcl_neon_hot. Values =
// addons/rc_look/config/look_sign.tres "hot" (pinned by test_rc_look_sign).
uniform float neon_hot = 0.90;
uniform float neon_core_share = 0.35;
uniform float neon_core_min_px = 1.00;
uniform float neon_core_tint = 0.15;
uniform vec3 neon_core_col = vec3(1.0);
uniform float neon_core_thin_px = 3.00;
uniform float neon_core_thin_hot = 0.45;

void fragment() {
	vec4 vc = COLOR;
	vec3 base = vc.rgb * albedo_k;
	float nv = clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0);
	// The tube's centre line faces the camera: d = sin of the view angle (0 on the centre line, 1 at the silhouette).
	float nd = sqrt(max(1.0 - nv * nv, 0.0));
	float nd_px = fwidth(nd);
	vec3 ec = neon_core ? rcl_neon_hot(vc.rgb, nd, 1.0, nd_px, neon_hot, neon_core_share, neon_core_min_px, neon_core_col, neon_core_tint, neon_core_thin_px, neon_core_thin_hot) : vc.rgb;
	vec3 em = ec * vc.a * emit_gain + vc.rgb * emit_self;
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
