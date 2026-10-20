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
// NA-22: the share of the ink the netrun look (look_blend) removes; 0 = the page as before.
uniform float ink_fade = 0.0;
uniform float ink_wobble_px = 1.4;
uniform float ink_width = 1.0;
// M14 perf slice: the ink runs only inside this box (view px: x0, y0, x1, y1) while ink_keep_on,
// fading out over ink_keep_feather px past it (the HQ idle: the network rect and its vignette).
uniform bool ink_keep_on = false;
uniform vec4 ink_keep = vec4(0.0, 0.0, 1.0, 1.0);
uniform float ink_keep_feather = 24.0;
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
// B2 (art director): 1 = the streaks never lift the blacks (they show by the light under them).
uniform float rain_keep_blacks = 0.0;
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

// --- AAA-2 "Realistic night" chain (A-022, MATERIAL_SPEC section 10), the netrun street at look_blend above 0 ---------------------
// The mainline passes above (ink, grime, spill, mainline bloom / fog / rain / grade) are not run: no toon bands and no ink. The
// chain: exposure, 3-radius HDR bloom, hue-preserving ACES shoulder, 3 rain layers, shadow / highlight tint, vignette, sRGB,
// contrast, display knee, chromatic aberration (on the input taps), grain. Every number is a uniform from `CityShaderConfigData.aaa.post`.
uniform bool aaa_on = false;
uniform float aaa_exposure = 0.6;
uniform float aaa_ref_w = 1920.0;
uniform float aaa_bloom_thr = 1.2;
uniform vec3 aaa_bloom_sigma = vec3(4.5, 18.0, 101.25);
uniform vec3 aaa_bloom_w = vec3(0.12, 0.10, 0.08);
uniform float aaa_bloom_lod_k = 1.5;
uniform vec3 aaa_aces_abc = vec3(2.51, 0.03, 2.43);
uniform vec2 aaa_aces_de = vec2(0.59, 0.14);
uniform vec3 aaa_aces_blend = vec3(3.0, 5.0, 0.2);
uniform vec3 aaa_shadow_tint = vec3(0.25, 0.45, 0.6);
uniform vec2 aaa_shadow = vec2(0.30, 2.2);
uniform vec3 aaa_hi_tint = vec3(1.0, 0.86, 0.86);
uniform vec3 aaa_hi = vec3(0.25, 0.6, 2.0);
uniform vec3 aaa_lift = vec3(0.0, 0.0, 0.004);
uniform vec3 aaa_vig = vec3(0.38, 0.35, 1.6);
uniform vec2 aaa_contrast = vec2(1.12, 0.18);
uniform vec3 aaa_knee = vec3(0.66, 0.93, 0.27);
uniform vec3 aaa_ca = vec3(2.4, 0.3, 1.5);
uniform vec2 aaa_grain = vec2(0.03, 0.6);
uniform vec3 aaa_rain0 = vec3(4000.0, 3.0, 6.0);
uniform vec3 aaa_rain0b = vec3(0.05, 1.0, 0.6);
uniform vec3 aaa_rain1 = vec3(1800.0, 14.0, 24.0);
uniform vec3 aaa_rain1b = vec3(0.10, 1.0, 1.0);
uniform vec3 aaa_rain2 = vec3(60.0, 60.0, 95.0);
uniform vec3 aaa_rain2b = vec3(0.25, 3.0, 1.6);
uniform vec2 aaa_rain_fall = vec2(1400.0, 0.2);
uniform float aaa_rain_on = 1.0;
// AAA-2 P6 (A-034 items 1-2): the wet street's reflections in screen space. For a ground pixel the march climbs the screen to the
// base of the first thing standing on the street (or the horizon), and the picture mirrored about that contact row is added: long
// colored smears under signs and lamp heads (the plate's wet asphalt), blurred along the column in step with the distance below
// the contact. Where the ground is rough (nr_tex roughness) the same mirrored spot is read through a wide ring of taps that keep
// only the highlights: soft colored discs, the foreground bokeh (rough reflections; no separate bokeh pass, MATERIAL_SPEC 7 / 10).
uniform bool aaa_wr_on = false;
uniform int aaa_wr_steps = 40;
// x: first step (screen fraction), y: growth per step, z: the farthest the march climbs (screen fraction), w: strength.
uniform vec4 aaa_wr_march = vec4(0.004, 1.12, 0.7, 0.9);
// x: ground height tolerance factor of the plane depth, y: tolerance in BU, z: fade per screen fraction below the contact, w: smear length per distance below the contact.
uniform vec4 aaa_wr_shape = vec4(0.03, 0.3, 3.0, 0.35);
// x, y: roughness range (sharp .. rough), z: strength kept on rough ground, w: blur lod gain.
uniform vec4 aaa_wr_rough = vec4(0.03, 0.3, 0.5, 1.0);
// x: bokeh ring radius at 1920 px, y: bokeh threshold (scene units), z: bokeh gain, w: smear column jitter (px at 1920).
uniform vec4 aaa_wr_bokeh = vec4(60.0, 0.8, 0.5, 6.0);
// Share of the reflection kept where the march meets the horizon (the haze band, not a thing standing on the street).
uniform float aaa_wr_sky = 0.3;

vec3 aaa_aces(vec3 x) {
	return clamp((x * (aaa_aces_abc.x * x + aaa_aces_abc.y)) / (x * (aaa_aces_abc.z * x + aaa_aces_de.x) + aaa_aces_de.y), 0.0, 1.0);
}

// Hue-preserving max-RGB shoulder (MATERIAL_SPEC 10 stage 3).
vec3 aaa_tonemap(vec3 c) {
	c = max(c, vec3(0.0));
	float m = max(max(c.r, c.g), c.b);
	if (m < 0.00001) {
		return vec3(0.0);
	}
	vec3 hp = c * (aaa_aces(vec3(m)).x / m);
	float w = aaa_aces_blend.z * clamp((m - aaa_aces_blend.x) / max(aaa_aces_blend.y - aaa_aces_blend.x, 0.0001), 0.0, 1.0);
	return mix(hp, aaa_aces(c), w);
}

// Gaussian-weighted hot (above the threshold) taps around `uv`: `sig` px at the reference width, taps on a spiral, each read at
// the mip that covers its spacing (so a wide bloom is a mean of coarse texels).
vec3 aaa_bloom_at(vec2 uv, float sig, float sc, vec2 vps) {
	const int N = 14;
	vec3 acc = vec3(0.0);
	float wsum = 0.0;
	float s = sig * sc;
	float lod = max(log2(max(s * aaa_bloom_lod_k / sqrt(float(N)), 1.0)), 0.0);
	vec2 inv = 1.0 / vps;
	for (int i = 0; i < N; i++) {
		float rr = 2.2 * s * sqrt((float(i) + 0.5) / float(N));
		float a = float(i) * 2.399963;
		vec2 o = vec2(cos(a), sin(a)) * rr;
		float w = exp(-0.5 * rr * rr / (s * s));
		vec3 c = textureLod(screen_tex, uv + o * inv, lod).rgb * aaa_exposure;
		acc += max(c - vec3(aaa_bloom_thr), vec3(0.0)) * w;
		wsum += w;
	}
	return acc / max(wsum, 0.0001);
}

// One rain layer (count, len lo, len hi | alpha, width, speed): a drop per cell of an area-1/count grid, falling, slightly slanted.
float aaa_rain_layer(vec2 p, vec3 a, vec3 b, float tt, float seed) {
	float cell = sqrt(aaa_ref_w * aaa_ref_w * 0.5625 / a.x);
	float yy = p.y + tt * aaa_rain_fall.x * b.z;
	float u = p.x - aaa_rain_fall.y * yy;
	vec2 cuv = vec2(u, yy) / cell;
	vec2 ci = floor(cuv);
	float hit = 0.0;
	for (int dj = -1; dj <= 0; dj++) {
		vec2 c = ci + vec2(0.0, float(dj));
		float hx = hash12(c * 1.7 + seed);
		float hy = hash12(c * 2.3 + seed + 5.0);
		float hl = hash12(c * 3.1 + seed + 9.0);
		float hb = hash12(c * 4.7 + seed + 13.0);
		float sx = (c.x + hx) * cell;
		float sy = (c.y + hy) * cell;
		float len = mix(a.y, a.z, hl);
		float along = yy - sy;
		if (along >= 0.0 && along <= len) {
			float across = abs(u - sx);
			float wd = max(b.y, 1.0) * 0.5 + 0.5;
			float prof = 1.0 - smoothstep(wd - 0.5, wd + 0.5, across);
			float fade = smoothstep(0.0, 0.2 * len, along) * (1.0 - 0.5 * along / len);
			hit = max(hit, prof * fade * mix(0.47, 1.0, hb));
		}
	}
	return hit * b.x;
}

// The ground plane (world y = 0) depth along the view axis at `uv`, or -1 above the horizon.
float aaa_plane_depth(vec2 uv, mat4 ip, mat4 iv) {
	vec4 p = ip * vec4(uv * 2.0 - 1.0, 0.5, 1.0);
	vec3 dv = normalize(p.xyz / p.w);
	vec3 dw = (iv * vec4(dv, 0.0)).xyz;
	if (dw.y > -0.0005) {
		return -1.0;
	}
	return (iv[3].y / -dw.y) * -dv.z;
}

// The wet street's reflected light at a ground pixel (scene-linear, added before exposure), 0 elsewhere.
vec3 aaa_wet_reflection(vec2 uv, vec2 vps, mat4 ip, mat4 iv) {
	float zp0 = aaa_plane_depth(uv, ip, iv);
	if (zp0 < 0.0) {
		return vec3(0.0);
	}
	float zs0 = -view_pos(uv, ip).z;
	if (abs(zs0 - zp0) > max(aaa_wr_shape.y, aaa_wr_shape.x * zp0)) {
		return vec3(0.0);
	}
	float yb = -1.0;
	float horizon = 1.0;
	float st = aaa_wr_march.x;
	for (int i = 0; i < 64; i++) {
		if (i >= aaa_wr_steps || st > aaa_wr_march.z) {
			break;
		}
		float y = uv.y - st;
		if (y < 0.0) {
			break;
		}
		vec2 uk = vec2(uv.x, y);
		float zpk = aaa_plane_depth(uk, ip, iv);
		if (zpk < 0.0) {
			yb = y;
			horizon = aaa_wr_sky;
			break;
		}
		float zsk = min(-view_pos(uk, ip).z, 100000.0);
		if (zsk < zpk - max(aaa_wr_shape.y, aaa_wr_shape.x * zpk)) {
			yb = y;
			break;
		}
		st *= aaa_wr_march.y;
	}
	if (yb < 0.0) {
		return vec3(0.0);
	}
	float d = uv.y - yb;
	float yr = yb - d;
	if (yr < 0.0) {
		return vec3(0.0);
	}
	float sc = vps.x / aaa_ref_w;
	float rough = nr(uv).w;
	float rk = smoothstep(aaa_wr_rough.x, aaa_wr_rough.y, rough);
	float fade = exp(-d * aaa_wr_shape.z) * aaa_wr_march.w * mix(1.0, aaa_wr_rough.z, rk) * horizon;
	float len = d * aaa_wr_shape.w;
	float lod = max(log2(max(len * vps.y / 8.0 * aaa_wr_rough.w, 1.0)), 0.0);
	vec3 acc = vec3(0.0);
	for (int j = 0; j < 8; j++) {
		float o = (float(j) + 0.5) / 8.0 - 0.5;
		float jx = (hash12(vec2(float(j), floor(uv.x * vps.x * 0.25))) - 0.5) * aaa_wr_bokeh.w * sc / vps.x;
		acc += textureLod(screen_tex, vec2(uv.x + jx, yr + o * len), lod).rgb;
	}
	vec3 smear = acc / 8.0 * fade * (1.0 - rk);
	// Bokeh: a ring of taps around the mirrored spot keeps only the highlights, so a lamp or a sign reads as a soft disc.
	vec3 bk = vec3(0.0);
	if (rk > 0.01) {
		float rad = aaa_wr_bokeh.x * sc * rk;
		float blod = max(log2(max(rad * 0.5, 1.0)), 0.0);
		for (int k = 0; k < 12; k++) {
			float a = float(k) * 2.399963;
			float rr = sqrt((float(k) + 0.5) / 12.0) * rad;
			vec2 o = vec2(cos(a), sin(a)) * rr / vps;
			vec3 c = textureLod(screen_tex, vec2(uv.x, yr) + o, blod).rgb * aaa_exposure;
			bk += max(c - vec3(aaa_wr_bokeh.y), vec3(0.0));
		}
		bk = bk / 12.0 / max(aaa_exposure, 0.0001) * aaa_wr_bokeh.z * rk * fade * 8.0;
	}
	return smear + bk;
}

vec3 aaa_fragment(vec2 uv, vec2 vps, float tt, mat4 ip, mat4 iv) {
	vec2 px = 1.0 / vps;
	float sc = vps.x / aaa_ref_w;
	vec2 cq = (uv - 0.5) * 2.0;
	float r = length(cq) / 1.41421356;
	// Chromatic aberration (stage 10) on the input taps: R outward, B inward by ca * sc * clip(r - r0, 0, 1)^pow px.
	float cam = aaa_ca.x * sc * pow(clamp(r - aaa_ca.y, 0.0, 1.0), aaa_ca.z);
	vec2 dir = length(cq) > 0.0001 ? normalize(cq * vps) : vec2(0.0);
	vec3 lin = vec3(textureLod(screen_tex, uv + dir * cam * px, 0.0).r, textureLod(screen_tex, uv, 0.0).g, textureLod(screen_tex, uv - dir * cam * px, 0.0).b) * aaa_exposure;
	if (aaa_wr_on) {
		lin += aaa_wet_reflection(uv, vps, ip, iv) * aaa_exposure;
	}
	vec3 b1 = aaa_bloom_at(uv, aaa_bloom_sigma.x, sc, vps);
	vec3 b2 = aaa_bloom_at(uv, aaa_bloom_sigma.y, sc, vps);
	vec3 b3 = aaa_bloom_at(uv, aaa_bloom_sigma.z, sc, vps);
	vec3 hdr = lin + aaa_bloom_w.x * b1 + aaa_bloom_w.y * b2 + aaa_bloom_w.z * b3;
	vec3 img = aaa_tonemap(hdr);
	// Rain (stage 4): three layers over the tone-mapped picture, tinted by the picture's own blurred colour, lit by the glow.
	if (aaa_rain_on > 0.5) {
		vec2 p = uv * vps / sc;
		float ra = aaa_rain_layer(p, aaa_rain0, aaa_rain0b, tt, 1.0) + aaa_rain_layer(p, aaa_rain1, aaa_rain1b, tt, 21.0) + aaa_rain_layer(p, aaa_rain2, aaa_rain2b, tt, 41.0);
		vec3 rc = clamp(aaa_tonemap(textureLod(screen_tex, uv, log2(max(30.0 * sc * 1.7, 1.0))).rgb * aaa_exposure) * 1.6 + 0.25, 0.0, 1.0);
		float glow_l = dot(aaa_tonemap(b2 + 1.5 * b3), vec3(0.2126, 0.7152, 0.0722));
		float lit = clamp(0.25 + 2.4 * glow_l, 0.25, 2.2);
		img = mix(img, rc, clamp(ra * lit, 0.0, 1.0));
	}
	// Grade (stage 5): teal-navy shadow tint, warm-pink highlight tint, lift.
	float lum = dot(img, vec3(0.2126, 0.7152, 0.0722));
	float sh_w = clamp(1.0 - aaa_shadow.y * lum, 0.0, 1.0) * aaa_shadow.x;
	vec3 st = aaa_shadow_tint / max(dot(aaa_shadow_tint, vec3(0.2126, 0.7152, 0.0722)), 0.0001);
	img *= mix(vec3(1.0), st, sh_w);
	float hi_w = clamp(aaa_hi.z * lum - aaa_hi.y, 0.0, 1.0) * aaa_hi.x;
	img *= mix(vec3(1.0), aaa_hi_tint, hi_w);
	img = img + aaa_lift * (1.0 - img);
	// Vignette (stage 6, linear), sRGB (7), contrast (8), knee (9).
	img *= 1.0 - aaa_vig.x * pow(clamp(r - aaa_vig.y, 0.0, 1.0), aaa_vig.z);
	vec3 d = to_srgb(img);
	d = aaa_contrast.y * pow(max(d, vec3(0.0)) / aaa_contrast.y, vec3(aaa_contrast.x));
	vec3 over = max(d - aaa_knee.x, vec3(0.0));
	d = mix(d, aaa_knee.x + (aaa_knee.y - aaa_knee.x) * tanh(over / aaa_knee.z), step(vec3(aaa_knee.x), d));
	// Film grain (stage 11): noise at pixel scale, weaker on bright pixels.
	vec2 gp = floor(uv * vps / max(sc * 0.55 * 1.5, 0.5));
	float gn = (hash12(gp) + hash12(gp + 31.7) + hash12(gp + 77.3) - 1.5) * 1.15;
	d += gn * aaa_grain.x * (1.0 - aaa_grain.y * dot(d, vec3(0.2126, 0.7152, 0.0722)));
	return to_lin(clamp(d, 0.0, 1.0));
}

void fragment() {
	vec2 uv = SCREEN_UV;
	if (aaa_on) {
		ALBEDO = aaa_fragment(uv, VIEWPORT_SIZE, rc_time(TIME) * time_scale, INV_PROJECTION_MATRIX, INV_VIEW_MATRIX);
	} else {
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
		float ink_k = 1.0;
		if (ink_keep_on) {
			vec2 kp = SCREEN_UV * VIEWPORT_SIZE;
			vec2 kd = max(max(ink_keep.xy - kp, kp - ink_keep.zw), vec2(0.0));
			ink_k = 1.0 - smoothstep(0.0, max(ink_keep_feather, 0.001), length(kd));
		}
		if (ink_on && ink_k > 0.0) {
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
			float a = e * ink_alpha * ink_k * (1.0 - ink_fade);
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
			float lit = mix(1.0, smoothstep(0.02, 0.3, dot(img, vec3(0.2126, 0.7152, 0.0722))), rain_keep_blacks);
			img = mix(img, rain_color, ra * rain_alpha * lit);
		}
		img = clamp(img * grade, 0.0, 1.0);
		if (map_on) {
			float grey = dot(img, vec3(0.2126, 0.7152, 0.0722));
			img = mix(vec3(grey), img, map_saturation);
			img = clamp(vec3(map_mid) + (img - vec3(map_mid)) * map_contrast, 0.0, 1.0);
		}
		ALBEDO = to_lin(img);
	}
}
