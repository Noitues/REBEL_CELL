shader_type spatial;
render_mode cull_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
// LOOK Solace park (concept round 5 D_*_park_r5): the lawn, paths, lit lime lines, ponds and plinth of CitySolaceParkKit. Vertex colour =
// base colour, its alpha the part: 0.2 lawn, 0.4 path, 0.6 lit line (emission, strongest at night), 0.8 water, 1.0 stone. look_blend 0 is
// the cel map look (flat colour with a top / side step, no specular); 1 the AAA-2 look (PBR under the moon, wet gloss). `night` 0..1
// scales the lit lines; by day the base colours are lifted.
uniform float look_blend : hint_range(0.0, 1.0) = 0.0;
uniform float night : hint_range(0.0, 1.0) = 1.0;
uniform float lit_gain = 1.6;
uniform float day_lift = 1.5;
uniform float side_shade = 0.62;
uniform float cel_k = 0.8;
uniform float aaa_glow = 0.12;  // the AAA-2 look: the park's own lamps and path lights lift its surfaces (the plates' lit park)

void fragment() {
	float part = COLOR.a;
	vec3 base = COLOR.rgb * mix(day_lift, 1.0, night);
	vec3 nw = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	float top = smoothstep(0.35, 0.8, abs(nw.y));
	float shade = mix(side_shade, 1.0, top);
	bool lit = part > 0.5 && part < 0.7;
	bool water = part > 0.7 && part < 0.9;
	bool stone = part > 0.9;
	float rough = water ? 0.06 : (stone ? 0.55 : (lit ? 0.5 : 0.85));
	vec3 cel = base * shade * (1.0 - look_blend) * cel_k;  // the cel look is self-lit flat colour (no light dependence)
	ALBEDO = lit ? vec3(0.0) : base * mix(0.0, 1.0, look_blend);
	ROUGHNESS = mix(1.0, rough, look_blend);
	SPECULAR = mix(0.0, water ? 0.9 : 0.5, look_blend);
	METALLIC = 0.0;
	EMISSION = lit ? COLOR.rgb * lit_gain * mix(0.35, 1.0, night) : cel + base * aaa_glow * look_blend;
	if (water) {
		EMISSION = cel + COLOR.rgb * 0.35 * night * look_blend;
	}
}
