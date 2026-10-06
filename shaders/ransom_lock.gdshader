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
// The house motif mask (CorpHouseStyle.Motif: blueprint, hazard, cells, stars, glitch).
uniform sampler2D motif_tex : hint_default_black, filter_linear;
uniform vec2 screen = vec2(1280.0, 720.0);
uniform float seed = 1.0;
// The motif's strength and the tint's share of the picture's light (round 20 values).
uniform float motif_strength = 0.32;
uniform float lum_share = 0.55;

float h(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233)) + seed * 3.17) * 43758.5453);
}

// M14 asset parity: the house motif is round 20's own `motif(style, 1)` mask (1920 x 1080,
// assets/campaign_end/motif_<style>.png), stretched over the screen; the shader only tints it.
float motif_mask(vec2 uv) {
	return texture(motif_tex, uv).r;
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
	vec3 tinted = lum * lum_share * (0.5 + house.rgb * 0.8) + back.rgb * 0.6 + motif_mask(UV) * house.rgb * motif_strength;
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
