// ART-1 1D spike: the ground (asphalt, plazas, street lots) on the same toon ramp, and the
// lane glow strips (`lane` = 1: vertex colour is emission, scaled by lane_gain so the
// management zooms can step the street glow back to 28 %). ROUGHNESS 0 marks not-a-building
// for the post pass.
shader_type spatial;
render_mode cull_disabled, specular_disabled;

uniform vec3 ramp_shadow;
uniform vec3 ramp_mid;
uniform vec3 ramp_lit;
uniform vec2 ramp_edges = vec2(0.147, 0.393);
uniform bool lane = false;
uniform float lane_gain = 1.0;

void fragment() {
	ROUGHNESS = 0.0;
	if (lane) {
		ALBEDO = vec3(0.0);
		EMISSION = COLOR.rgb * lane_gain;
	} else {
		ALBEDO = COLOR.rgb;
	}
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	vec3 band = ndl < ramp_edges.x ? ramp_shadow : (ndl < ramp_edges.y ? ramp_mid : ramp_lit);
	DIFFUSE_LIGHT = band;
}
