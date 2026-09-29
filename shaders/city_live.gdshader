// The live pass over the baked neon city (H20): the sketch look (wobble, grain,
// saturation, wall textures) is already in the baked image, so this only adds the
// screen-space parts that must stay live: faint CRT scanlines and a gentle flicker.
// Both go to 0 under reduce-effects (NeonCity._apply_effects).
//
// Art pass W7 (ART_BIBLE 9.1, 9.3, 9.5, 2): with `lit` on (CityAtmosphere sets it), the
// composite also lights and grades the city, all in this one pass (no screen copy, so glass
// panels over the city blur the graded picture):
//   - per-ink glow: bright ink pixels bloom, each of the five inks by its own gain;
//   - wet streets: dark ground pixels reflect the lights above them, with a slow ripple;
//   - haze: two or three bands in depth (screen height), drifting slowly;
//   - rim light: the brightest signs light the edges round them; FLAGGED corp buildings
//     get a red/blue rim that alternates at most once a second (off under reduce effects);
//   - NOTICED searchlights sweep from the target corp's district; claimed territory leaks
//     CELL_TURF light into the haze;
//   - the grade: contrast, saturation, warmth, dirty lift, a lean toward the target corp's
//     hue (campaign progress), the context's dim and map mode's dim and blur;
//   - UI calm zones: behind text the city darkens and desaturates, and (mode 1, the live
//     layer of traffic dashes and signs) its motion is hidden.
// Positions are screen fractions (FRAGCOORD * SCREEN_PIXEL_SIZE): every draw of the city
// (the image, the live layer under its own transform) reads the same space.
// mode 0: the view (the baked image, the sky and the shade); 1: the live layer; 2: grade only
// (the silhouette and the veil over a bake fading in).
shader_type canvas_item;
// Reduce effects (rc_common): the flicker, haze drift, ripple, sweep and rim flicker stop;
// the static scanlines and the lighting's still look stay.
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float scan_strength : hint_range(0.0, 1.0) = 0.07;
uniform float flicker : hint_range(0.0, 0.1) = 0.0;

uniform int mode = 0;
uniform bool lit = false;
// Width over height of the screen (distances in units of the screen's height).
uniform float aspect = 1.7777778;

// The grade (CityGrade.params).
uniform float g_contrast = 1.0;
uniform float g_saturation = 1.0;
uniform float g_warmth = 0.0;
uniform float g_lift = 0.0;
uniform float g_dim = 0.0;
uniform float g_map_dim = 0.0;
uniform vec4 g_tint : source_color = vec4(1.0);
uniform float g_tint_amount = 0.0;
// Keep equal to CityGrade.WARM_R / WARM_G / WARM_B / PIVOT.
const float WARM_R = 0.14;
const float WARM_G = 0.03;
const float WARM_B = 0.16;
const float PIVOT = 0.3;

// Per-ink glow.
uniform vec4 inks[5];
uniform float ink_gain[5];
uniform float glow_threshold = 0.3;
uniform float glow_radius = 5.0;
uniform float glow_strength = 0.0;
uniform int glow_taps = 0;

// Haze bands: (centre y, half-width, density) each.
uniform vec3 haze_bands[3];
uniform int haze_count = 0;
uniform vec4 haze_color : source_color = vec4(0.17, 0.18, 0.36, 1.0);
uniform float haze_gain = 1.0;
uniform float haze_drift = 0.02;
uniform float haze_period = 26.0;

// Wet streets.
uniform float refl_strength = 0.0;
uniform float refl_reach = 16.0;
uniform float refl_period = 5.0;
uniform float refl_ripple = 1.5;

// Rim lights: (x, y, radius, strength) and colour; lights from `flicker_from` on alternate
// police red and blue at `flicker_hz`.
uniform vec4 rim_pos[8];
uniform vec4 rim_col[8];
uniform int rim_count = 0;
uniform int flicker_from = 8;
uniform float flicker_hz = 0.8;
uniform vec4 police_red : source_color = vec4(1.0, 0.13, 0.22, 1.0);
uniform vec4 police_blue : source_color = vec4(0.16, 0.42, 1.0, 1.0);

// Searchlights: (base x, base y, phase, length).
uniform vec4 search[4];
uniform int search_count = 0;
uniform float search_period = 11.0;
uniform float search_arc = 0.66;
uniform float search_width = 0.09;
uniform float search_alpha = 0.16;
uniform vec4 search_color : source_color = vec4(0.81, 0.89, 1.0, 1.0);

// Territory light leaking into the haze: (x, y, radius, strength).
uniform vec4 leaks[8];
uniform int leak_count = 0;
uniform vec4 leak_color : source_color = vec4(0.83, 1.0, 0.0, 1.0);

// UI calm zones: (x0, y0, x1, y1) screen fractions.
uniform vec4 calm[8];
uniform int calm_count = 0;
uniform float calm_dim = 0.45;
uniform float calm_desat = 0.75;
uniform float calm_feather = 0.04;

// Map mode's blur (texture px).
uniform float blur_px = 0.0;

vec3 grade(vec3 c) {
	c = c * (1.0 - g_lift) + vec3(g_lift, g_lift * 0.85, g_lift * 0.6);
	c *= vec3(1.0 + WARM_R * g_warmth, 1.0 + WARM_G * g_warmth, 1.0 - WARM_B * g_warmth);
	c = (c - PIVOT) * g_contrast + PIVOT;
	float l = rc_luma(c);
	c = mix(vec3(l), c, g_saturation);
	vec3 hue = g_tint.rgb * (rc_luma(c) / max(rc_luma(g_tint.rgb), 0.01));
	c = mix(c, hue, g_tint_amount);
	c *= (1.0 - g_dim) * (1.0 - g_map_dim);
	return clamp(c, 0.0, 1.0);
}

float calm_at(vec2 sp) {
	float w = 0.0;
	for (int i = 0; i < 8; i++) {
		if (i >= calm_count) {
			break;
		}
		vec4 r = calm[i];
		vec2 d = max(max(r.xy - sp, sp - r.zw), vec2(0.0));
		float dist = length(d * vec2(aspect, 1.0));
		w = max(w, 1.0 - smoothstep(0.0, max(calm_feather, 0.0001), dist));
	}
	return w;
}

// The gain of the ink nearest in hue to `s` (the inks arrive normalised: CityAtmosphere).
float ink_gain_of(vec3 s) {
	vec3 n = normalize(s + vec3(0.0001));
	float best = -1.0;
	float gain = 1.0;
	for (int k = 0; k < 5; k++) {
		float d = dot(n, inks[k].rgb);
		if (d > best) {
			best = d;
			gain = ink_gain[k];
		}
	}
	return gain;
}

void fragment() {
	// COLOR already holds the texture's colour (Godot 4 canvas fragment input): sampling
	// TEXTURE again at the same UV would square it and crush the city's mid-tones.
	vec4 c = COLOR;
	vec2 sp = FRAGCOORD.xy * SCREEN_PIXEL_SIZE;
	float t = rc_time(TIME);
	float calm_w = lit ? calm_at(sp) : 0.0;
	bool textured = TEXTURE_PIXEL_SIZE.x < 0.01;
	if (lit && mode == 0 && textured) {
		vec2 px = TEXTURE_PIXEL_SIZE;
		vec3 base = c.rgb;
		if (blur_px > 0.0) {
			vec3 acc = base * 0.2;
			for (int k = 0; k < 8; k++) {
				float a = TAU * float(k) / 8.0;
				acc += texture(TEXTURE, UV + vec2(cos(a), sin(a)) * px * blur_px).rgb * 0.1;
			}
			base = acc;
		}
		vec3 outc = base;
		// Per-ink glow (none behind text: the calm zone keeps it off).
		vec3 g = vec3(0.0);
		if (glow_taps > 0 && glow_strength > 0.0) {
			for (int k = 0; k < 12; k++) {
				if (k >= glow_taps) {
					break;
				}
				float a = TAU * (float(k) + 0.5) / float(glow_taps);
				float r = glow_radius * (k % 2 == 0 ? 1.0 : 2.2);
				vec3 s = texture(TEXTURE, UV + vec2(cos(a), sin(a)) * px * r).rgb;
				float b = max(rc_luma(s) - glow_threshold, 0.0) / max(1.0 - glow_threshold, 0.01);
				g += s * b * (k % 2 == 0 ? 1.0 : 0.6);
			}
			// Per ink: the neighbourhood's glow takes the gain of its dominant ink (one hue
			// match per pixel, not one per tap: §13's budget).
			g *= ink_gain_of(g) / float(glow_taps);
			outc += g * glow_strength * 2.0 * (1.0 - calm_w);
		}
		// Wet streets: a dark ground pixel mirrors the lights above it, rippling slowly.
		float ground = 1.0 - smoothstep(0.05, 0.14, rc_luma(base));
		if (refl_strength > 0.0 && ground > 0.0) {
			vec3 r = vec3(0.0);
			for (int k = 1; k <= 4; k++) {
				float fk = float(k);
				float sway = sin(UV.y / px.y * 0.35 + fk * 1.7 + t * TAU / refl_period) * refl_ripple;
				vec3 s = texture(TEXTURE, UV - vec2(sway, fk * refl_reach * 0.25) * px).rgb;
				r += s * max(rc_luma(s) - glow_threshold * 0.8, 0.0) * (1.0 - fk * 0.2);
			}
			outc += r * refl_strength * ground;
		}
		// Rim light round the brightest signs (and FLAGGED's red/blue on corp buildings).
		float edge = rim_count > 0 ? clamp(fwidth(rc_luma(base)) * 5.0, 0.0, 1.0) : 0.0;
		for (int i = 0; i < 8; i++) {
			if (i >= rim_count) {
				break;
			}
			vec4 p = rim_pos[i];
			float d = length((sp - p.xy) * vec2(aspect, 1.0)) / max(p.z, 0.0001);
			float fall = exp(-d * d * 2.0);
			vec3 col = rim_col[i].rgb;
			if (i >= flicker_from) {
				col = mix(police_red.rgb, police_blue.rgb, step(0.5, fract(t * flicker_hz + float(i) * 0.5)));
			}
			outc += col * fall * (edge + 0.15) * p.w * 0.6;
		}
		// Haze bands in depth.
		float h = 0.0;
		for (int i = 0; i < 3; i++) {
			if (i >= haze_count) {
				break;
			}
			vec3 b = haze_bands[i];
			float y = b.x + haze_drift * sin(t * TAU / haze_period + float(i) * 2.1);
			float q = (sp.y - y) / max(b.y, 0.001);
			h += b.z * exp(-q * q);
		}
		h = clamp(h * haze_gain, 0.0, 0.6);
		// The haze is lit by the neon round it (the glow's light scatters in it).
		outc = mix(outc, haze_color.rgb + g * 1.5, h);
		// Searchlights (NOTICED): beams sweeping from the target corp's district.
		for (int i = 0; i < 4; i++) {
			if (i >= search_count) {
				break;
			}
			vec4 s = search[i];
			float ang = -1.5708 + search_arc * sin(t * TAU / search_period + s.z);
			vec2 dir = vec2(cos(ang), sin(ang));
			vec2 v = (sp - s.xy) * vec2(aspect, 1.0);
			float along = dot(v, dir);
			if (along > 0.0 && along < s.w) {
				float off = abs(dir.x * v.y - dir.y * v.x) / max(along, 0.001);
				float beam = 1.0 - smoothstep(search_width * 0.5, search_width, off);
				outc += search_color.rgb * beam * (1.0 - along / s.w) * search_alpha * (0.6 + h * 3.0);
			}
		}
		// Claimed territory: CELL_TURF light leaking into the haze.
		for (int i = 0; i < 8; i++) {
			if (i >= leak_count) {
				break;
			}
			vec4 l = leaks[i];
			float d = length((sp - l.xy) * vec2(aspect, 1.0)) / max(l.z, 0.0001);
			outc += leak_color.rgb * l.w * exp(-d * d * 2.5) * (0.3 + h * 2.5);
		}
		c.rgb = outc;
	}
	if (lit) {
		c.rgb = grade(c.rgb);
		c.rgb = mix(c.rgb, vec3(rc_luma(c.rgb)), calm_w * calm_desat) * (1.0 - calm_w * calm_dim);
		if (mode == 1) {
			// The live layer's motion (traffic dashes, sign flicker) never plays behind text.
			c.a *= 1.0 - calm_w;
		}
	}
	float line = step(0.5, fract(FRAGCOORD.y / 3.0));
	c.rgb *= 1.0 - scan_strength * line;
	c.rgb *= 1.0 - flicker * rc_live() * (0.5 + 0.5 * sin(rc_time(TIME) * 41.0));
	COLOR = c;
}
