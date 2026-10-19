// AAA-2 (A-022): the solid emissive pieces of the street dressing (shop strips and awnings, billboard panels, lamp heads) as an OPAQUE
// unshaded emitter, so the post chain (exposure, bloom, tone map) sees them: Godot copies the screen texture before the transparent
// pass, so an additive piece is never bloomed. Colour = the instance colour, INSTANCE_CUSTOM.z = the gain, `emit` the tier radiance of
// the emissive hierarchy (MATERIAL_SPEC 8). Static; the clock uniforms are accepted and ignored (the netrun clock sets them on every
// dressing material).
shader_type spatial;
render_mode unshaded, cull_back, depth_draw_opaque, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float emit = 1.0;
uniform float emission_multiplier = 1.0;
uniform float look_blend = 1.0;

varying vec3 cust;

void vertex() {
	cust = INSTANCE_CUSTOM.xyz;
}

void fragment() {
	ALBEDO = COLOR.rgb * emit * cust.z * emission_multiplier * look_blend;
}
