// REBEL_CELL material kit (ART-1 1B, shared with ART-5 5a's city): the toon bands and the
// banded light spill as one include, so the props / busts material (toon_ink.gdshader) and the
// city's building and ground shaders (shaders/city/) band light and spill the same way.
// Spill sources come from LightSpill.uniforms_3d (ToonInkMaterial.set_spill sets them on any
// material that includes this file).

uniform vec4 spill_lights[8];
uniform vec4 spill_colors[8];
uniform int spill_count = 0;

// The band a lit share `x` falls in: 0 shadow, 1 mid, 2 lit (edges lo < hi).
int toon_band_index(float x, float lo, float hi) {
	return x > hi ? 2 : (x > lo ? 1 : 0);
}

// The light the spill sources throw on a surface at `world_pos` facing `n_world`, banded like
// the key light (shade_mid / shade_low: the mid and shadow bands' share of full light).
vec3 toon_spill(vec3 world_pos, vec3 n_world, float lo, float hi, float shade_mid, float shade_low) {
	vec3 spill = vec3(0.0);
	for (int i = 0; i < 8; i++) {
		if (i >= spill_count) {
			break;
		}
		vec3 d = spill_lights[i].xyz - world_pos;
		float r = max(spill_lights[i].w, 0.001);
		float fall = clamp(1.0 - length(d) / r, 0.0, 1.0);
		float facing = clamp(dot(n_world, normalize(d)) * 0.7 + 0.3, 0.0, 1.0);
		int b = toon_band_index(fall * fall * facing, lo, hi);
		float s = b == 2 ? 1.0 : (b == 1 ? shade_mid : shade_low);
		s = fall > 0.0 ? s * fall : 0.0;
		spill += spill_colors[i].rgb * spill_colors[i].a * s;
	}
	return spill;
}
