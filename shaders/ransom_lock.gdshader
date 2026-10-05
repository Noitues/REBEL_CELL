shader_type canvas_item;
// Reduce effects (rc_common): the takeover's scan edge and tearing hold still.
#include "res://shaders/lib/rc_common.gdshaderinc"
// ART-11 4D: the campaign lost lock, option A "ransomware lock" (ART_BIBLE v2 §4.8, ref
// docs/art_reference/campaign_end/round20_raid_world/campaign_lost.jpg; the generator
// art-concepts-r43 round20 lost20.py `ransom`, `glitch`, `crt_off`). Over the screen behind it:
// the home server falls (`glitch`: band tearing and an RGB split), the winning corporation's
// ransomware rolls down the screen (`wipe`, a bright scan edge) and recolours what it covers in
// its house hue with its motif, and at the wipe the CRT collapses to a line (`collapse`).
// Decoration only: the cells' hash is no game RNG.

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
// 0 nothing taken .. 1 the whole screen taken (the edge's travel includes its feather).
uniform float wipe = 0.0;
// 0 calm .. 1 the strongest tearing.
uniform float glitch = 0.0;
// 0 the picture .. 1 black (the CRT squashes to a line, then a dot).
uniform float collapse = 0.0;
uniform vec4 house : source_color = vec4(0.69, 0.43, 1.0, 1.0);
uniform vec4 back : source_color = vec4(0.07, 0.05, 0.16, 1.0);
// 0 blueprint, 1 hazard, 2 cells, 3 stars, 4 glitch (CorpHouseStyle.Motif).
uniform int motif = 0;
uniform vec2 screen = vec2(1280.0, 720.0);
uniform float seed = 1.0;
// The motif's strength and the tint's share of the picture's light (round 20 values).
uniform float motif_strength = 0.32;
uniform float lum_share = 0.55;

float h(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233)) + seed * 3.17) * 43758.5453);
}

float line_at(float v, float period, float width) {
	float d = abs(fract(v / period + 0.5) - 0.5) * period;
	return 1.0 - smoothstep(0.0, width, d);
}

float motif_mask(vec2 px) {
	if (motif == 0) {
		// Blueprint: a fine grid, a heavier one every fifth line, and drafting circles.
		float g = max(line_at(px.x, 32.0, 0.8), line_at(px.y, 32.0, 0.8)) * 0.28;
		g = max(g, max(line_at(px.x, 160.0, 1.0), line_at(px.y, 160.0, 1.0)) * 0.55);
		vec2 c = floor(px / 240.0);
		vec2 o = (c + vec2(h(c), h(c + 7.0))) * 240.0;
		float r = 40.0 + h(c + 3.0) * 110.0;
		g = max(g, (1.0 - smoothstep(0.0, 1.0, abs(length(px - o) - r))) * 0.43);
		return g;
	} else if (motif == 1) {
		// Hazard: diagonal stripes and barcode runs.
		float s = step(fract((px.x + px.y) / 60.0), 0.5) * 0.24;
		vec2 c = floor(px / vec2(140.0, 46.0));
		float bars = step(0.72, h(c)) * step(0.5, h(vec2(floor(px.x / 3.5), c.y)));
		return max(s, bars * 0.47);
	} else if (motif == 2) {
		// Cells: hexagons and floating bubbles.
		vec2 p = px / 38.0;
		vec2 a = mod(p, vec2(1.732, 1.0)) - vec2(0.866, 0.5);
		vec2 b = mod(p - vec2(0.866, 0.5), vec2(1.732, 1.0)) - vec2(0.866, 0.5);
		vec2 q = dot(a, a) < dot(b, b) ? a : b;
		q = abs(q);
		float hex = max(dot(q, normalize(vec2(1.0, 1.732))), q.x);
		float edge = 1.0 - smoothstep(0.0, 0.05, abs(hex - 0.5));
		vec2 c = floor(px / 90.0);
		float bub = 1.0 - smoothstep(0.0, 1.2, abs(length(px - (c + vec2(h(c), h(c + 2.0))) * 90.0) - (8.0 + h(c + 5.0) * 24.0)));
		return max(edge * 0.43, bub * 0.35);
	} else if (motif == 3) {
		// Stars and orbit rings round the screen's centre.
		vec2 c = floor(px / 9.0);
		float star = step(0.985, h(c)) * (0.4 + 0.6 * h(c + 1.0));
		vec2 d = (px - screen * 0.5) / vec2(1.0, 0.35);
		float ring = line_at(length(d), 107.0, 0.9) * step(200.0, length(d));
		return max(star, ring * 0.35);
	}
	// Glitch: corrupted blocks.
	vec2 c = floor(px / vec2(120.0, 9.0));
	return step(0.86, h(c)) * (0.25 + 0.55 * h(c + 4.0));
}

void fragment() {
	vec2 px = UV * screen;
	vec2 suv = SCREEN_UV;
	float live = rc_live();
	// The home server falls: bands tear sideways, the channels split.
	float g = glitch * live;
	if (g > 0.0) {
		float band = floor(px.y / (6.0 + 40.0 * h(vec2(floor(px.y / 46.0), 1.0))));
		float pick = step(h(vec2(band, 2.0)), 0.25 + 0.6 * g);
		suv.x += (h(vec2(band, 3.0)) - 0.5) * 0.16 * g * pick;
	}
	float split = 0.006 * g;
	vec3 src = vec3(texture(screen_tex, suv + vec2(split, 0.0)).r, texture(screen_tex, suv).g, texture(screen_tex, suv - vec2(split, 0.0)).b);
	src *= 1.0 - 0.25 * g * step(0.66, fract(px.y / 3.0));
	// The ransomware's cover: the picture's light in the house hue, its back, its motif.
	float lum = dot(src, vec3(0.3333));
	vec3 tinted = lum * lum_share * (0.5 + house.rgb * 0.8) + back.rgb * 0.6 + motif_mask(px) * house.rgb * motif_strength;
	float edge = wipe * 1.12 - 0.06;
	float cover = clamp((edge - UV.y) / 0.05, 0.0, 1.0);
	float scan = exp(-pow((UV.y - edge) / 0.008, 2.0)) * step(wipe, 0.999) * step(0.001, wipe);
	vec3 col = mix(src, tinted, cover) + scan * house.rgb * 1.4;
	// The cut: the picture squashes to a bright line (0..0.6), the line to a dot, then black.
	if (collapse > 0.0) {
		float v = collapse;
		if (v < 0.6) {
			float k = v / 0.6;
			float half_h = 0.5 * pow(1.0 - k, 2.0) + 0.002;
			float inside = step(abs(UV.y - 0.5), half_h);
			col = col * (1.0 + 2.5 * k) * inside;
		} else {
			float k = clamp((v - 0.6) / 0.35, 0.0, 1.0);
			float half_w = 0.5 * pow(1.0 - k, 3.0);
			float line_on = step(abs(UV.y - 0.5), 1.5 / screen.y) * step(abs(UV.x - 0.5), half_w);
			col = vec3(0.85, 0.95, 1.0) * line_on;
		}
	}
	COLOR = vec4(col, 1.0);
}
