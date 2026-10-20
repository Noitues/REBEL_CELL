// LOOK L5 (whole-city plate parity; the designer's ruling: terrain, then one textured water plane over it). A transparent
// sheet at sea level over the real seabed (CitySeabedKit): the water's thickness along the view ray comes from the bed's
// depth texture (CitySeabedKit.depth_image, the same bed as the mesh; open sea past it is `far_bu` deep), so the bed shows through the shallows (absorbed per channel, red first) and the deep water and open sea go
// opaque. On top: a slow two-scale ripple normal with a sky fresnel and a sun glint, light caustic ribbons in the shallows
// and a foam rim where the water thins to nothing on the shore. Drawn after the city post (render_priority above the
// post's), so it takes the night / day grade itself; unshaded, the scene fog still lays the haze on it.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D bed_tex : filter_linear, repeat_disable;
uniform vec2 bed_origin = vec2(0.0);
uniform vec2 bed_size = vec2(1.0);
uniform float far_bu = 60.0;
// Added to the bed's depth (the drowned quarter's sheet lies over flooded streets, not over the bed).
uniform float depth_add = 0.0;
uniform float night = 1.0;
uniform vec3 deep_day = vec3(0.03, 0.16, 0.30);
uniform vec3 deep_night = vec3(0.01, 0.07, 0.10);
uniform vec3 shallow_day = vec3(0.10, 0.45, 0.55);
uniform vec3 shallow_night = vec3(0.04, 0.30, 0.32);
uniform vec3 absorb = vec3(0.30, 0.10, 0.07);
uniform float alpha_min = 0.15;
uniform vec3 sky_day = vec3(0.55, 0.62, 0.70);
uniform vec3 sky_night = vec3(0.04, 0.08, 0.10);
uniform float fresnel_f0 = 0.04;
uniform float fresnel_gain = 0.6;
uniform vec3 sun_dir = vec3(0.4, 0.6, 0.3);
uniform float glint_pow = 180.0;
uniform float glint_gain = 0.5;
uniform float ripple_bu = 14.0;
uniform float ripple_speed = 0.05;
uniform float ripple_k = 0.35;
uniform float caustic_bu = 22.0;
uniform float caustic_gain = 0.25;
uniform vec3 caustic_day = vec3(0.6, 0.9, 1.0);
uniform vec3 caustic_night = vec3(0.2, 0.7, 0.7);
uniform float foam_bu = 0.6;
uniform float foam_gain = 0.55;
uniform vec3 grade = vec3(1.0);
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

float waves(vec2 p, float t) {
	return vnoise(p + vec2(t, t * 0.6)) * 0.6 + vnoise(p * 2.7 - vec2(t * 1.4, -t * 0.8)) * 0.4;
}

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float t = rc_time(TIME) * time_scale * ripple_speed;
	// Thickness along the view ray: the bed's depth under this point over the ray's sine.
	vec3 V = normalize(CAMERA_POSITION_WORLD - v_world);
	vec2 buv = (v_world.xz - bed_origin) / bed_size;
	bool inside = all(greaterThanEqual(buv, vec2(0.0))) && all(lessThanEqual(buv, vec2(1.0)));
	float depth = inside ? texture(bed_tex, buv).r : far_bu;
	float path = (depth + depth_add) / max(V.y, 0.05);
	vec3 trans = exp(-absorb * path);
	float tm = (trans.r + trans.g + trans.b) / 3.0;
	// Ripple normal from the wave height's gradient.
	vec2 p = v_world.xz / max(ripple_bu, 0.001);
	float e = 0.15;
	float h0 = waves(p, t);
	vec3 nw = normalize(vec3(-(waves(p + vec2(e, 0.0), t) - h0) / e * ripple_k, 1.0, -(waves(p + vec2(0.0, e), t) - h0) / e * ripple_k));
	float fr = fresnel_f0 + (1.0 - fresnel_f0) * pow(1.0 - clamp(dot(nw, V), 0.0, 1.0), 5.0);
	vec3 deep = mix(deep_day, deep_night, night);
	vec3 shallow = mix(shallow_day, shallow_night, night);
	vec3 body = mix(deep, shallow, tm);
	vec3 col = body + mix(sky_day, sky_night, night) * fr * fresnel_gain;
	vec3 H = normalize(normalize(sun_dir) + V);
	col += vec3(1.0, 0.95, 0.85) * pow(max(dot(nw, H), 0.0), glint_pow) * glint_gain * (1.0 - night);
	// Caustic ribbons over the shallows.
	vec2 cp = v_world.xz / max(caustic_bu, 0.001);
	float cn = vnoise(cp + vec2(t * 0.7, -t * 0.4)) * 0.6 + vnoise(cp * 2.1 + vec2(-t, t * 0.5)) * 0.4;
	float rib = smoothstep(0.82, 0.96, 1.0 - abs(2.0 * cn - 1.0));
	col += mix(caustic_day, caustic_night, night) * rib * caustic_gain * tm;
	// Foam where the sheet thins out on the shore, broken by the waves.
	float foam = (1.0 - smoothstep(0.0, foam_bu, path)) * smoothstep(0.25, 0.65, h0);
	col = mix(col, vec3(0.92, 0.96, 1.0) * mix(1.0, 0.6, night), foam * foam_gain);
	ALBEDO = col * grade;
	ALPHA = clamp(max(1.0 - tm, alpha_min) + foam * foam_gain, 0.0, 1.0);
}
