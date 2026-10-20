// NA-12 r2 / r3 (art-pass items 17, A-030): a generated city's sea, and the void past the city (`void_mode`). Flat
// emission (no light: DIFFUSE_LIGHT 0) so the toon ramp never greys it; ROUGHNESS 0 marks not-a-building for the post pass.
// UV.x = lots from the shore into the sea (0 at the sea wall), UV.y = lots along the shore. The sea: its deep tone
// blending to a lighter shallows tone over `shallow_lots`, a slow two-octave ripple, a marbled caustic (domain-warped
// ridges on a `caustic_bu` cell, big enough to read at whole-city zoom) and a foam line along the shore. The shore
// lights' reflections are their own smear meshes (city_water_smear.gdshader). `night` 1 = night tones, 0 = day;
// `look_blend` / `look_gain` lift it under the netrun look (NA-22); `time_scale` 0 freezes it (reduce motion).
shader_type spatial;
render_mode cull_disabled, specular_disabled, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform bool void_mode = false;
uniform float night = 1.0;
uniform vec3 deep_night;
uniform vec3 deep_day;
uniform vec3 shore_night;
uniform vec3 shore_day;
uniform vec3 void_night;
uniform vec3 void_day;
uniform float ripple_bu = 9.0;
uniform float ripple_speed = 0.12;
uniform float ripple_gain = 0.35;
uniform float shallow_lots = 14.0;
uniform float caustic_bu = 70.0;
uniform float caustic_speed = 0.04;
uniform float caustic_gain = 0.9;
uniform vec3 caustic_night;
uniform vec3 caustic_day;
uniform float foam_lots = 1.5;
uniform float foam_gain = 0.7;
uniform float look_blend = 0.0;
uniform float look_gain = 1.6;
uniform float time_scale = 1.0;
varying vec3 v_world;

float h2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(h2(i), h2(i + vec2(1.0, 0.0)), u.x), mix(h2(i + vec2(0.0, 1.0)), h2(i + vec2(1.0, 1.0)), u.x), u.y);
}

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	ROUGHNESS = 0.0;
	ALBEDO = vec3(0.0);
	float gain = mix(1.0, look_gain, look_blend);
	if (void_mode) {
		EMISSION = mix(void_day, void_night, night) * gain;
	} else {
		float tt = rc_time(TIME) * time_scale;
		float t = tt * ripple_speed;
		vec2 w = v_world.xz / max(ripple_bu, 0.001);
		float rip = vnoise(w + vec2(t, t * 0.7)) * 0.65 + vnoise(w * 2.3 - vec2(t * 1.3, -t)) * 0.35;
		float d = max(UV.x, 0.0);
		float shallow = exp(-d / max(shallow_lots, 0.001));
		vec3 deep = mix(deep_day, deep_night, night);
		vec3 shore = mix(shore_day, shore_night, night);
		vec3 col = mix(deep, shore, shallow) * (1.0 + (rip - 0.5) * ripple_gain);
		// Marbled caustic: ridges of a warped noise (veins) over broad lighter blotches, drifting slowly.
		float tc = tt * caustic_speed;
		vec2 p = v_world.xz / max(caustic_bu, 0.001);
		vec2 q = p + 0.7 * vec2(vnoise(p * 1.6 + vec2(tc, 0.0)), vnoise(p * 1.6 + vec2(5.2, -tc)));
		float n = vnoise(q * 2.0) * 0.6 + vnoise(q * 4.3 + 3.1) * 0.4;
		float ridge = 1.0 - abs(2.0 * n - 1.0);
		float veins = smoothstep(0.85, 0.97, ridge);
		float blotch = smoothstep(0.4, 0.75, vnoise(p * 0.7 + vec2(-tc, tc)));
		vec3 ctone = mix(caustic_day, caustic_night, night);
		col += ctone * (veins * 0.85 + blotch * 0.3) * caustic_gain * (0.55 + 0.45 * shallow);
		// Foam: a broken white line hugging the shore, and foam on the strongest veins.
		float broken = smoothstep(0.3, 0.7, vnoise(w * 3.0 + vec2(t * 3.0, 0.0)));
		float foam = exp(-d / max(foam_lots, 0.001)) * (0.35 + 0.65 * broken) + veins * veins * 0.25;
		col += mix(vec3(0.95, 0.98, 1.0), vec3(0.6, 0.9, 1.0), night) * foam * foam_gain * mix(1.0, 0.7, night);
		EMISSION = col * gain;
	}
}

void light() {
	DIFFUSE_LIGHT = vec3(0.0);
}
