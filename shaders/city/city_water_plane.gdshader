// LOOK L5 (whole-city plate parity; the designer's ruling: terrain, then one textured water plane over it), ported from the
// Blender plate's water (city_render.mat_water_aaa). The depth feel is the seabed's own (city_seabed.gdshader fades it
// through the water); this sheet adds what the surface does: a Fresnel mirror of the sky (IOR 1.33, a little more at
// grazing angles) on a broad swell plus a fine ripple, a sun glint, and by day a diffuse body from deep to shallow blue
// whose opacity rises toward the shore (0.40 + 0.52 x shallow; `shallow` from the shore distance the seabed bake carries in
// its green channel). A surf band breaks on the first shelf. Drawn after the city post (render_priority above it), so it
// takes the grade itself; unshaded, the scene fog still lays the haze on it.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, specular_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D bed_tex : filter_linear, repeat_disable;
uniform vec2 bed_origin = vec2(0.0);
uniform vec2 bed_size = vec2(1.0);
uniform float night = 1.0;
// Blender: the swell (noise 0.07 over (0.22, 0.34) of the position), the base noise (0.35) and a fine ripple (1.1).
uniform vec2 swell_scale = vec2(0.0154, 0.0238);
uniform float base_scale = 0.35;
uniform float ripple_scale = 1.1;
uniform vec3 wave_w = vec3(0.8, 0.65, 0.22);
uniform float wave_k = 0.35;
uniform float wave_speed = 0.05;
uniform float ior = 1.33;
uniform float fresnel_boost = 0.35;
uniform vec3 sky_horizon_day = vec3(0.62, 0.66, 0.70);
uniform vec3 sky_zenith_day = vec3(0.30, 0.45, 0.65);
uniform vec3 sky_horizon_night = vec3(0.10, 0.08, 0.16);
uniform vec3 sky_zenith_night = vec3(0.01, 0.02, 0.05);
uniform vec3 sun_dir = vec3(0.4, 0.6, 0.3);
uniform vec3 sun_col = vec3(1.0, 0.92, 0.80);
uniform float glint_pow = 220.0;
uniform float glint_gain = 0.6;
uniform vec3 deep_day = vec3(0.022, 0.15, 0.31);
uniform vec3 shallow_day = vec3(0.09, 0.46, 0.50);
uniform vec3 body_emit_day = vec3(0.01, 0.07, 0.14);
uniform float body_alpha = 0.40;
uniform float body_alpha_shallow = 0.52;
uniform vec2 shallow_lots = vec2(20.0, 34.0);
uniform float far_shore_lots = 60.0;
uniform float depth_add = 0.0;
uniform vec2 surf_lots = vec2(0.2, 1.6);
uniform float surf_gain = 0.5;
uniform vec3 surf_col = vec3(0.85, 0.93, 1.0);
uniform float surf_period = 6.0;
// By night the plate's sea glows teal with caustic marbling over all of it (Cycles carries the seabed's caustics through
// the whole water column); here the sheet carries them: a dark teal body and two ridge-noise layers, brighter inshore.
uniform vec3 night_body = vec3(0.012, 0.035, 0.065);
uniform float night_alpha = 0.82;
uniform vec3 marble_col = vec3(0.05, 0.20, 0.24);
uniform float marble_scale = 0.05;
uniform float marble_width = 0.22;
uniform float marble_distort = 0.9;
uniform float marble_floor = 0.15;
uniform float marble_shore = 0.6;
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

float fbm(vec2 p) {
	return vnoise(p) * 0.55 + vnoise(p * 2.03 + 3.1) * 0.3 + vnoise(p * 4.1 - 1.7) * 0.15;
}

// The finer layers fade out where a pixel spans more than their wavelength (Cycles averages them; here they would alias).
float height(vec2 p, float t, float px) {
	float kb = 1.0 - smoothstep(0.25, 0.8, px * base_scale * 2.4);
	float kr = 1.0 - smoothstep(0.25, 0.8, px * ripple_scale * 1.7);
	return fbm(p * swell_scale + vec2(t * 0.3, t * 0.2)) * wave_w.x
		+ fbm(p * base_scale * vec2(1.0, 2.4) + vec2(-t, t * 0.6)) * wave_w.y * kb
		+ fbm(p * ripple_scale * vec2(1.0, 1.7) + vec2(t * 1.7, -t)) * wave_w.z * kr;
}

float marble(vec2 p, float t) {
	vec2 dq = vec2(vnoise(p + vec2(5.2, 1.3 + t)), vnoise(p + vec2(-3.1, 7.7 - t))) * 2.0 - 1.0;
	float n = fbm(p + dq * marble_distort);
	return 1.0 - smoothstep(0.0, marble_width, abs(2.0 * n - 1.0));
}

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float t = rc_time(TIME) * time_scale * wave_speed;
	vec2 p = v_world.xz;
	float px = length(fwidth(p));
	float e = max(px, 0.3);
	float h0 = height(p, t, px);
	vec3 nw = normalize(vec3(-(height(p + vec2(e, 0.0), t, px) - h0) / e * wave_k, 1.0, -(height(p + vec2(0.0, e), t, px) - h0) / e * wave_k));
	vec3 V = normalize(CAMERA_POSITION_WORLD - v_world);
	float f0 = pow((ior - 1.0) / (ior + 1.0), 2.0);
	float fr = f0 + (1.0 - f0) * pow(1.0 - clamp(dot(nw, V), 0.0, 1.0), 5.0);
	fr = min(fr * (1.0 + fresnel_boost), 1.0);
	vec3 R = reflect(-V, nw);
	float up = clamp(R.y, 0.0, 1.0);
	vec3 sky = mix(mix(sky_horizon_day, sky_zenith_day, sqrt(up)), mix(sky_horizon_night, sky_zenith_night, sqrt(up)), night);
	vec3 refl = sky + sun_col * pow(max(dot(R, normalize(sun_dir)), 0.0), glint_pow) * glint_gain * (1.0 - night);
	// The shore distance (lots) under this point: open sea past the bake.
	vec2 buv = (p - bed_origin) / bed_size;
	bool inside = all(greaterThanEqual(buv, vec2(0.0))) && all(lessThanEqual(buv, vec2(1.0)));
	vec2 bed = inside ? texture(bed_tex, buv).rg : vec2(1e3, far_shore_lots);
	float shallow = 1.0 - smoothstep(shallow_lots.x, shallow_lots.y, bed.g);
	// By day a diffuse body (Blender's day water); by night the sheet is clear and the seabed's fade carries it.
	float ab = mix(body_alpha + body_alpha_shallow * shallow, night_alpha, night);
	vec3 body = mix(deep_day, shallow_day, min(shallow * 0.9 + h0 * 0.12, 1.0)) + body_emit_day;
	if (night > 0.001) {
		float mt = rc_time(TIME) * time_scale * 0.02;
		float m = (marble(p * marble_scale, mt) + marble(p * marble_scale * 1.6 + 3.3, -mt * 0.7)) * 0.5;
		float km = 1.0 - smoothstep(0.4, 1.2, px * marble_scale);
		vec3 nb = night_body + marble_col * (marble_floor + m * km * (1.0 - marble_floor)) * mix(1.0, 1.0 + marble_shore, shallow);
		body = mix(body, nb, night);
	}
	// Surf: bands rolling in on the first shelf, broken by the waves.
	float sb = (1.0 - smoothstep(surf_lots.x, surf_lots.y, bed.g)) * step(0.001, bed.r + depth_add);
	float roll = 0.5 + 0.5 * sin((bed.g * surf_period - rc_time(TIME) * time_scale * 0.8) * 6.2831853);
	float surf = sb * smoothstep(0.45, 0.85, roll * 0.6 + h0 * 0.6) * surf_gain;
	float a = fr + (1.0 - fr) * ab;
	vec3 col = (refl * fr + body * (1.0 - fr) * ab) / max(a, 1e-4);
	col = mix(col, surf_col * mix(1.0, 0.5, night), surf);
	ALBEDO = col * grade;
	// No water over dry ground (the bake's depth is 0 there); bilinear, so the coast softens over half a lot.
	float wetk = inside ? smoothstep(0.0, 0.6, bed.r + depth_add) : 1.0;
	ALPHA = clamp(max(a, surf), 0.0, 1.0) * wetk;
}
