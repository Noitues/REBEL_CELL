// ART-8 8p: the HQ compound glTF in the 1D spike's look (tools/spike/city/shaders/city_building.gdshader light():
// three hard bands of N.L with shadow -> the night ramp; facet normal from screen derivatives; the spike's post pass
// draws ink, spill, bloom, haze and rain). COLOR = the concept's face colour x per-triangle tone (baked by
// build_hq_compound.py); COLOR.a = a part bit -> ROUGHNESS, so the post pass inks part boundaries (its material edge).
// `role` follows the glTF material name: 0 hq_toon, 1 hq_lit, 2 hq_neon, 3 hq_win, 4 hq_sign. Prototype until 1B's
// shared toon / ink material lands (spike report "What ART-5 needs" 5).
shader_type spatial;
render_mode cull_disabled, specular_disabled;

uniform vec3 ramp_shadow = vec3(0.09, 0.08, 0.21);
uniform vec3 ramp_mid = vec3(0.20, 0.17, 0.36);
uniform vec3 ramp_lit = vec3(0.36, 0.30, 0.54);
uniform vec2 ramp_edges = vec2(0.118, 0.363);
// target_corps.TINT per corporation (manifest settings.ramp_tint).
uniform vec3 ramp_tint = vec3(1.0);
uniform int role = 0;
uniform float neon_gain = 1.2;
uniform float window_gain = 1.4;
// heroes26 LIT: floodlit surfaces add a self-light of their own colour (concept 0.42; 0.25 here because the spike post
// blooms every bright pixel, where the concept bloomed emissives only).
uniform float lit_gain = 0.25;
uniform float sign_gain = 1.0;

void fragment() {
	vec3 n = normalize(cross(dFdx(VERTEX), dFdy(VERTEX)));
	if (n.z < 0.0) {
		n = -n;
	}
	NORMAL = n;
	ROUGHNESS = COLOR.a > 0.5 ? 1.0 : 0.55;
	vec3 c = COLOR.rgb;
	if (role >= 2) {
		float g = role == 2 ? neon_gain : (role == 3 ? window_gain : sign_gain);
		ALBEDO = c * 0.3;
		EMISSION = c * g;
	} else {
		ALBEDO = c;
		EMISSION = role == 1 ? c * lit_gain : vec3(0.0);
	}
}

void light() {
	float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
	vec3 band = ndl < ramp_edges.x ? ramp_shadow : (ndl < ramp_edges.y ? ramp_mid : ramp_lit);
	DIFFUSE_LIGHT = min(band * ramp_tint, vec3(1.0));
}
