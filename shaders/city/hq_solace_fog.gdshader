shader_type fog;
// LOOK Solace HQ: the plates' volumetric haze (hq_preset `hq_fog`): thin, exponential in height, a clumpy ground bank round the
// park, scattering the compound's own lights. Art-owned; only the Solace HQ page carries it.
uniform float peak = 0.0045;
uniform float height_scale = 70.0;
uniform float bank_peak = 0.008;
uniform float bank_r0 = 150.0;
uniform float bank_r1 = 210.0;
uniform float bank_h = 9.0;
uniform vec3 albedo : source_color = vec3(0.86, 0.95, 0.9);
uniform vec3 centre = vec3(0.0);

void fragment() {
	vec3 p = WORLD_POSITION - centre;
	float h = max(p.y, 0.0);
	float d = peak * exp(-h / height_scale);
	float r = length(p.xz);
	float ring = smoothstep(bank_r0, bank_r0 + 30.0, r) * (1.0 - smoothstep(bank_r1 - 30.0, bank_r1, r)) * (1.0 - smoothstep(0.0, bank_h, h));
	d += bank_peak * ring;
	DENSITY = d;
	ALBEDO = albedo;
}
