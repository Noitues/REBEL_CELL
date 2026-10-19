// NA-23c: the street netrun's lane lines. The mainline lane strips (vertex colour = the lane's hue) drawn emission-only like the
// lane branch of wet_street, but desaturated (`lane_sat` 0 = grey of the same luma, 1 = the hue as is) and scaled by
// `street_gain`, so the kerb and lane lines stay quiet and the streak lanes of the dressing carry the street (PIPELINE_SPEC 12.2:
// the saturated amber stripes dominated DECISION).
shader_type spatial;
render_mode cull_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float street_gain = 0.45;
uniform float lane_sat = 0.3;
uniform float emission_multiplier = 1.0;

void fragment() {
	ALBEDO = vec3(0.0);
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
	float luma = dot(COLOR.rgb, vec3(0.2126, 0.7152, 0.0722));
	EMISSION = mix(vec3(luma), COLOR.rgb, lane_sat) * street_gain * emission_multiplier;
}
