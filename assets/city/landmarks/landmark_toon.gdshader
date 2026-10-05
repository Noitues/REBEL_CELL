// ART-5 5b: the landmark material (every lm_* role but the light cones), the glTF side of the concept's
// target_corps.mat_toon / mat_glow / hq_scene LITM: 3-band toon on N.L (the spike's city_building light(), so a
// landmark shades like the city around it), emissive neon / windows / signs, and the REBEL_CELL reveal. COLOR is the
// glTF COLOR_0 (linear): rgb = base colour (x tone jitter for toon roles), a = the part value 0.55-1.0 (toon roles:
// written to ROUGHNESS so the ink pass draws part edges and treats the landmark as a building) or a window's own
// seeded value. Same convention as 8p's compounds (art_export/1).
// Prototype until 1B's shared toon + ink material lands (the spike shaders are prototypes too).
shader_type spatial;
render_mode cull_disabled, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

// 0 toon, 1 toon on a detail line (darkens with the reveal), 2 lit (toon + self-light), 3 neon, 4 window,
// 5 window in the blackout ring, 6 window on a detail line, 7 red fist window, 8 sign
uniform int role = 0;
uniform vec3 ramp_shadow = vec3(0.09, 0.08, 0.21);
uniform vec3 ramp_mid = vec3(0.20, 0.17, 0.36);
uniform vec3 ramp_lit = vec3(0.36, 0.30, 0.54);
uniform vec2 ramp_edges = vec2(0.118, 0.363);
uniform float lit_emission = 0.42;
uniform float neon_gain = 1.0;
uniform float window_gain = 1.0;
uniform vec3 glass = vec3(0.0);
uniform float glass_mix = 0.0;
uniform float sign_gain = 1.0;
// REBEL_CELL reveal: 0 = the sector fully lit (washed out), 1 = the fist revealed.
uniform float reveal_q = 1.0;
uniform float flicker_band = 0.12;
uniform float lines_window_share = 0.85;
uniform vec3 lines_dark = vec3(0.031, 0.024, 0.047);
uniform float lines_dark_k = 0.55;
uniform float flicker_frame = 0.0;
// The red fist burns brighter than the city's windows (map34 lights it denser and adds a red glow), so it blooms.
uniform float fist_gain = 1.0;

varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float hash13(vec3 p) {
	p = fract(p * 0.1031);
	p += dot(p, p.zyx + 31.32);
	return fract((p.x + p.y) * p.z);
}

void fragment() {
	vec3 n = normalize(cross(dFdx(VERTEX), dFdy(VERTEX)));
	if (dot(n, VIEW) < 0.0) {
		n = -n;
	}
	NORMAL = n;
	vec3 c = COLOR.rgb;
	ROUGHNESS = COLOR.a;
	if (role <= 2) {
		ALBEDO = c;
		if (role == 1) {
			ALBEDO = mix(c, lines_dark, lines_dark_k * reveal_q);
		} else if (role == 2) {
			EMISSION = c * lit_emission;
		}
	} else if (role == 3) {
		ALBEDO = vec3(0.0);
		EMISSION = c * neon_gain;
		ROUGHNESS = 0.5;
	} else if (role == 8) {
		ALBEDO = vec3(0.0);
		EMISSION = c * sign_gain;
		ROUGHNESS = 0.5;
	} else {
		float a = COLOR.a;
		if (role == 5) {
			// The blackout front: off once q passes the window's value, flickering within the band.
			float front = (a - reveal_q) / flicker_band;
			if (front < -1.0 || (front < 1.0 && hash13(floor(v_world * 3.0) + flicker_frame) < 0.55)) {
				discard;
			}
		} else if (role == 6) {
			if (a > (1.0 - reveal_q) * lines_window_share) {
				discard;
			}
		}
		ALBEDO = vec3(0.0);
		EMISSION = mix(c * window_gain * (role == 7 ? fist_gain : 1.0), glass, glass_mix);
		ROUGHNESS = 0.5;
	}
}

void light() {
	if (role <= 2) {
		float ndl = dot(NORMAL, LIGHT) * ATTENUATION;
		DIFFUSE_LIGHT = ndl < ramp_edges.x ? ramp_shadow : (ndl < ramp_edges.y ? ramp_mid : ramp_lit);
	} else {
		DIFFUSE_LIGHT = vec3(0.0);
	}
}
