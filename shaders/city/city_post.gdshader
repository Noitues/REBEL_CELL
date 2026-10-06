// ART-1 1D spike: the finish of the unified city in one full-screen pass, a port of
// art-concepts-r43 round 40 `post40.finish`: see-through buildings by view band (the ground
// pass under them), wobbly ink from normal / depth / material edges, grime, light spill and
// bloom from the glowing pixels, low fog patches, depth haze, rain and the night grade. Like
// post40 it works on display (sRGB) values. Godot has no emission-only buffer: the bright
// part of the frame (screen mips over a threshold) stands in for post40's glow pass.
// Prototype of the shared ink pass (1B owns shaders/kit/; unified later).
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform sampler2D depth_tex : hint_depth_texture, filter_nearest;
uniform sampler2D nr_tex : hint_normal_roughness_texture, filter_nearest;
uniform sampler2D ground_tex : filter_linear;
uniform bool has_ground = false;

uniform float opacity = 1.0;
uniform float see_dark = 0.86;
uniform float see_chroma = 1.35;
uniform float see_window = 0.15;
uniform bool ink_on = true;
uniform vec3 ink_color = vec3(0.05, 0.04, 0.09);
uniform float ink_normal_edge = 0.42;
uniform float ink_depth_edge = 1.2;
uniform float ink_alpha = 0.85;
uniform float ink_wobble_px = 1.4;
uniform float ink_width = 1.0;
uniform float ortho = 440.0;
uniform float cam_distance = 2600.0;
uniform float grime = 0.15;
uniform float spill = 0.5;
uniform float bloom = 0.75;
uniform float glow_threshold = 0.5;
uniform float glow_lod = 1.5;
uniform vec3 haze_color = vec3(0.08, 0.06, 0.16);
uniform float haze_k = 0.34;
uniform bool fog_on = true;
uniform vec3 fog_color = vec3(0.20, 0.17, 0.33);
uniform float fog_amount = 0.22;
uniform float fog_city = 0.0;
uniform bool rain_on = true;
uniform vec3 rain_color = vec3(0.75, 0.82, 1.0);
uniform float rain_alpha = 0.11;
uniform float rain_density = 0.1;
uniform vec3 grade = vec3(0.94, 0.92, 1.04);
uniform float time_scale = 1.0;
// S-MAPVIEW: map mode (raid and netrun views): the city greyed toward its own grey and its
// contrast lowered round `map_mid`, after the night grade (display values), its bloom cut to
// `map_bloom`. CityView3D.map_graded mirrors it on the CPU for the tests.
uniform bool map_on = false;
uniform float map_saturation = 1.0;
uniform float map_contrast = 1.0;
uniform float map_mid = 0.22;
uniform float map_bloom = 1.0;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

float hash12(vec2 p) {
	vec3 p3 = fract(vec3(p.xyx) * 0.1031);
	p3 += dot(p3, p3.yzx + 33.33);
	return fract((p3.x + p3.y) * p3.z);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash12(i), hash12(i + vec2(1, 0)), u.x), mix(hash12(i + vec2(0, 1)), hash12(i + vec2(1, 1)), u.x), u.y);
}

vec3 to_srgb(vec3 c) {
	c = max(c, vec3(0.0));
	return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c));
}

vec3 to_lin(vec3 c) {
	c = max(c, vec3(0.0));
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

vec3 view_pos(vec2 uv, mat4 inv_proj) {
	float d = texture(depth_tex, uv).r;
	vec4 v = inv_proj * vec4(uv * 2.0 - 1.0, d, 1.0);
	return v.xyz / v.w;
}

vec4 nr(vec2 uv) {
	vec4 t = texture(nr_tex, uv);
	return vec4(normalize(t.xyz * 2.0 - 1.0), t.w);
}

// The glow stand-in at mip `lod`: what is brighter than the threshold (display values).
vec3 glow_at(vec2 uv, float lod) {
	vec3 c = to_srgb(textureLod(screen_tex, uv, lod).rgb);
	float m = max(max(c.r, c.g), c.b);
	return c * smoothstep(glow_threshold, glow_threshold + 0.3, m);
}

void fragment() {
	vec2 uv = SCREEN_UV;
	vec2 px = 1.0 / VIEWPORT_SIZE;
	float t = rc_time(TIME) * time_scale;
	vec3 lin = textureLod(screen_tex, uv, 0.0).rgb;
	vec3 vp = view_pos(uv, INV_PROJECTION_MATRIX);
	vec4 here = nr(uv);
	float bld = step(0.5, here.w) * step(-vp.z, cam_distance * 2.0);
	// See-through buildings (raid / transit band): the ground pass under, the building
	// darkened and less grey on top.
	if (has_ground && opacity < 0.999 && bld > 0.5) {
		vec3 g = texture(ground_tex, uv).rgb;
		float lum = dot(lin, vec3(0.3333));
		vec3 b = max(vec3(0.0), vec3(lum) + (lin - vec3(lum)) * see_chroma);
		lin = g * (1.0 - opacity) + b * opacity * see_dark;
	}
	vec3 img = to_srgb(lin);
	vec3 g0 = glow_at(uv, 0.0);
	float emis = clamp(max(max(g0.r, g0.g), g0.b) * 2.0, 0.0, 1.0);
	// Ink: normal, material and depth edges at wobbled offsets (the round 2 wobbly line).
	if (ink_on) {
		vec2 sp = SCREEN_UV * VIEWPORT_SIZE;
		vec2 wob = (vec2(vnoise(sp / 7.0), vnoise(sp / 7.0 + 19.0)) - 0.5) * 2.0 * ink_wobble_px * px;
		vec2 u2 = uv + wob;
		vec4 c0 = nr(u2);
		float zc = -view_pos(u2, INV_PROJECTION_MATRIX).z;
		float e = 0.0;
		float dthr = ink_depth_edge * (ortho / 300.0);
		// Both sides of the pixel, so the line is about 2 x ink_width px wide (post40 maxf 3).
		for (int k = 0; k < 8; k++) {
			float ang = float(k) * 0.785398;
			vec2 o = vec2(cos(ang), sin(ang)) * ink_width;
			vec2 uo = u2 + o * px;
			vec4 cn = nr(uo);
			float zn = -view_pos(uo, INV_PROJECTION_MATRIX).z;
			e = max(e, step(ink_normal_edge, length(cn.xyz - c0.xyz) * 0.5 + abs(cn.w - c0.w)));
			e = max(e, step(dthr, abs(zn - zc)));
		}
		float a = e * ink_alpha;
		if (has_ground && opacity < 0.999) {
			a *= 1.0 - (1.0 - opacity) * 0.55 * bld;
		}
		a *= 1.0 - clamp(emis * 1.6 - 0.4, 0.0, 1.0);
		img = mix(img, ink_color, a);
	}
	// Grime: low-frequency blots on the unlit surfaces.
	vec2 sp2 = SCREEN_UV * VIEWPORT_SIZE;
	float blot = vnoise(sp2 / 90.0) * 0.6 + vnoise(sp2 / 22.0 + 7.0) * 0.4;
	img *= mix(1.0 - grime * (blot - 0.5) * 1.4, 1.0, emis);
	// Light spill (multiplies the surroundings) and bloom (adds), post40's three blurs.
	vec3 b1 = glow_at(uv, glow_lod + 1.0);
	vec3 b2 = glow_at(uv, glow_lod + 3.0);
	vec3 b3 = glow_at(uv, glow_lod + 4.6);
	float bl = bloom * (map_on ? map_bloom : 1.0);
	img = img * (1.0 + spill * (b2 * 0.8 + b3)) + bl * (b1 * 0.5 + b2 * 0.4 + b3 * 0.12);
	// World position (fog height) and the distance past the target (haze).
	vec3 wp = (INV_VIEW_MATRIX * vec4(vp, 1.0)).xyz;
	float dep = -vp.z - cam_distance;
	if (fog_on) {
		vec2 q = wp.xz / 160.0 * 6.0 + vec2(t * 0.02, 0.0);
		float fnz = vnoise(q) * 0.6 + vnoise(q * 2.7 + 3.0) * 0.4;
		float low = clamp(1.0 - wp.y / 24.0, 0.0, 1.0) * 0.6 + 0.4 * fog_city;
		float fa = clamp((fnz - 0.5) * 2.6, 0.0, 1.0) * low * fog_amount;
		img = mix(img, fog_color + b3 * 1.2, fa);
	}
	float far = pow(clamp((dep - 0.05 * ortho) / (1.2 * ortho), 0.0, 1.0), 1.2);
	img = mix(img, haze_color, far * haze_k);
	if (rain_on) {
		vec2 r = sp2;
		r.x -= r.y * 0.2;
		vec2 cell = vec2(floor(r.x / 6.0), floor((r.y + t * 900.0 * (0.8 + 0.4 * hash12(vec2(floor(r.x / 6.0), 3.0)))) / 70.0));
		float h = hash12(cell);
		float inx = 1.0 - abs(fract(r.x / 6.0) - 0.5) * 6.0;
		float ra = step(1.0 - rain_density, h) * clamp(inx, 0.0, 1.0) * (0.3 + 0.7 * hash12(cell + 7.0));
		img = mix(img, rain_color, ra * rain_alpha);
	}
	img = clamp(img * grade, 0.0, 1.0);
	if (map_on) {
		float grey = dot(img, vec3(0.2126, 0.7152, 0.0722));
		img = mix(vec3(grey), img, map_saturation);
		img = clamp(vec3(map_mid) + (img - vec3(map_mid)) * map_contrast, 0.0, 1.0);
	}
	ALBEDO = to_lin(img);
}
