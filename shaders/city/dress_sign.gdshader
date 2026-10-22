// NA-24c: a street sign piece (a unit box on a MultiMesh): an OPAQUE emissive panel (luma `panel_level` at full district chroma, no
// blend over the facade) with saturated core strokes (text-block rows, luma `core_level`, clamp `core_max`) and a frame trim in the
// district's second light. Colour = the instance colour (the panel's hue); INSTANCE_CUSTOM.x = glyph seed, .z = the gain (HQ band
// emit and per-panel brightness), .w = the second light packed 0xRRGGBB (0 = a lightened panel hue). A far tier block yields to the
// tier that covers it (`yield_range`, alpha). Back faces are not drawn; side faces dim by `side_dim`. Static: no clock.
shader_type spatial;
render_mode unshaded, cull_back, depth_draw_opaque, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/city/dress_sign.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"
// LOOK Solace THE BLOOM (A Necrosis): the skin over the street's buildings and ground (strength 0 = the shader as before).
#define BL_STREET
#include "res://shaders/city/bloom_necrosis.gdshaderinc"
// LOOK-TOOLBOX module 11 (designer DIRECTION_REVIEW f4678fca, b727956a): each neon tube's hot core, rcl_neon_hot. Values =
// addons/rc_look/config/look_sign.tres "hot" (pinned by test_rc_look_sign).
uniform float neon_hot = 0.90;
uniform float neon_core_share = 0.35;
uniform float neon_core_min_px = 1.00;
uniform float neon_core_tint = 0.15;
uniform vec3 neon_core_col = vec3(1.0);
uniform float neon_core_thin_px = 3.00;
uniform float neon_core_thin_hot = 0.45;

uniform float emission_multiplier = 1.0;
uniform float look_blend = 1.0;
// AAA-2 emissive hierarchy (MATERIAL_SPEC 8): the tier radiance the panel colours are multiplied by (hero 4.0, secondary 2.6).
uniform float tier_emit = 1.0;
// (end, near) of the tier that covers this one; end 0 = no yield.
uniform vec2 yield_range = vec2(0.0, 0.0);

varying flat vec4 cust;
varying vec3 lpos;
varying vec3 lnrm;
varying vec3 lscale;
varying vec3 bl_w;

void vertex() {
	cust = INSTANCE_CUSTOM;
	lpos = VERTEX;
	lnrm = NORMAL;
	lscale = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
	bl_w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float yw = 1.0;
	if (yield_range.x > 0.0) {
		float d = length(VERTEX);
		float k = clamp((yield_range.x - d) / max(yield_range.x - yield_range.y, 0.001), 0.0, 1.0);
		yw = 1.0 - k * k * (3.0 - 2.0 * k);
	}
	vec3 sc = max(lscale, vec3(0.0001));
	float front = step(0.5, abs(lnrm.z));
	vec2 p = lpos.xy * sc.xy;
	vec2 fw = vec2(fwidth(p.x), fwidth(p.y));
	vec4 cd;
	vec2 m = sg_core(p, sc.xy, cust.x, fw, cd) * front;
	float gain = cust.z;
	float lp = panel_level * (1.0 - bright_var * sg_hash(vec2(3.0, 5.0), cust.x)) * gain * mix(side_dim, 1.0, front);
	float lc = min(core_level * gain, core_max);
	vec3 panel = sg_at_luma(COLOR.rgb, lp);
	vec3 sec = COLOR.rgb * 0.5 + vec3(0.5);
	int pk = int(cust.w);
	if (pk > 0) {
		sec = vec3(float((pk >> 16) & 255), float((pk >> 8) & 255), float(pk & 255)) / 255.0;
	}
	float fpx = max(fw.x, fw.y);
	vec3 rgb = mix(panel, rcl_neon_hot(sg_at_luma(COLOR.rgb, lc), cd.z, cd.w, fw.y, neon_hot, neon_core_share, neon_core_min_px, neon_core_col, neon_core_tint, neon_core_thin_px, neon_core_thin_hot), m.y);
	rgb = mix(rgb, rcl_neon_hot(sg_at_luma(sec, lc), cd.x, cd.y, fpx, neon_hot, neon_core_share, neon_core_min_px, neon_core_col, neon_core_tint, neon_core_thin_px, neon_core_thin_hot), m.x);
	ALBEDO = rgb * emission_multiplier * look_blend * tier_emit;
	ALBEDO = bl_unlit_street(bl_w, ALBEDO);
	// AAA-2: opaque (so the post chain tone-maps and blooms it; a transparent draw is after the screen copy): the yield is a dither.
	if (yw < 1.0 && fract(52.9829189 * fract(dot(FRAGCOORD.xy, vec2(0.06711056, 0.00583715)))) > yw) {
		discard;
	}
}
