// NA-12 r2 (art-pass item 17): a generated city's sea, and the void past the city (`void_mode`). Flat emission (no
// light: DIFFUSE_LIGHT 0) so the toon ramp never greys it; ROUGHNESS 0 marks not-a-building for the post pass.
// UV.x = lots from the shore into the sea (0 at the sea wall), UV.y = lots along the shore. The sea: its deep tone
// blending to the near-shore tone over the reflection reach, a slow two-octave ripple, and the shore lights smeared
// into it (streaks along the shore, one colour each, fading with the distance from the wall and flickering with the
// ripple). `night` 1 = night tones, 0 = day; `look_blend` / `look_gain` lift it under the netrun look (NA-22);
// `time_scale` 0 freezes it (reduce motion).
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
uniform float reflect_reach = 7.0;
uniform float reflect_gain = 1.4;
uniform float reflect_streak = 1.0;
uniform float reflect_width = 0.3;
uniform float reflect_share = 0.4;
uniform vec3 reflect_a;
uniform vec3 reflect_b;
uniform vec3 reflect_c;
uniform vec3 reflect_d;
uniform float look_blend = 0.0;
uniform float look_gain = 1.6;
uniform float time_scale = 1.0;
varying vec3 v_world;

float h1(float n) {
	return fract(sin(n * 127.1) * 43758.5453);
}

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
		float t = rc_time(TIME) * time_scale * ripple_speed;
		vec2 w = v_world.xz / max(ripple_bu, 0.001);
		float rip = vnoise(w + vec2(t, t * 0.7)) * 0.65 + vnoise(w * 2.3 - vec2(t * 1.3, -t)) * 0.35;
		float d = max(UV.x, 0.0);
		float near = exp(-d / max(reflect_reach, 0.001));
		vec3 deep = mix(deep_day, deep_night, night);
		vec3 shore = mix(shore_day, shore_night, night);
		vec3 col = mix(deep, shore, near) * (1.0 + (rip - 0.5) * ripple_gain);
		// Shore lights smeared into the sea: a thin streak in some bands along the shore (`reflect_share` of them,
		// `reflect_width` of the band wide), broken into dashes by the ripple and fading with the distance.
		float bu = UV.y / max(reflect_streak, 0.001);
		float band = floor(bu);
		float pick = h1(band);
		float lit = step(1.0 - reflect_share, h1(band + 17.0));
		float x = abs(fract(bu) - 0.5) * 2.0;
		float edge = 1.0 - smoothstep(reflect_width * 0.5, reflect_width, x);
		float dash = smoothstep(0.35, 0.7, vnoise(vec2(band * 3.1, d * 2.5 + t * 2.0)));
		vec3 rc = pick < 0.5 ? reflect_a : (pick < 0.7 ? reflect_b : (pick < 0.88 ? reflect_c : reflect_d));
		col += rc * lit * edge * dash * near * near * reflect_gain * night;
		EMISSION = col * gain;
	}
}

void light() {
	DIFFUSE_LIGHT = vec3(0.0);
}
