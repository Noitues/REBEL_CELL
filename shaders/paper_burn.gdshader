// Paper burn (PAPER material, ART_BIBLE 13): burns a paper item away (an exhausted card, a
// shredded note, a spent sticker). `progress` runs 0 (whole) to 1 (gone); the view tweens
// it from its motion entry and, under reduce effects or headless, sets the end state at
// once. The front follows value noise out from `origin` (UV): the paper scorches brown
// ahead of an ember rim, and what is burnt is gone (alpha 0). Reduce effects: the ember
// rim stops flickering (a static glow).
shader_type canvas_item;
// Reduce effects (rc_common): the ember flicker stops.
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float progress : hint_range(0.0, 1.0) = 0.0;
// Where the fire starts (UV) and how ragged its front is (noise cells across the item).
uniform vec2 origin = vec2(0.5, 1.0);
uniform float noise_scale : hint_range(1.0, 24.0) = 6.0;
// Width of the scorched band ahead of the front (a share of the burn).
uniform float edge : hint_range(0.01, 0.3) = 0.08;
uniform vec4 ember : source_color = vec4(1.0, 0.69, 0.0, 1.0);
uniform vec4 char_color : source_color = vec4(0.17, 0.1, 0.05, 1.0);

// Share of the front's field from distance (the rest is noise), the rim's width (a share
// of `edge`) and the ember flicker (depth, rate rad/s).
const float DIST_SHARE = 0.6;
const float RIM_SHARE = 0.35;
const float FLICKER_DEPTH = 0.15;
const float FLICKER_RATE = 23.0;

void fragment() {
	vec4 c = COLOR;
	float n = rc_noise(UV * noise_scale) * 0.6 + rc_noise(UV * noise_scale * 3.0) * 0.4;
	float field = clamp(distance(UV, origin) / 1.2, 0.0, 1.0) * DIST_SHARE + n * (1.0 - DIST_SHARE);
	float front = progress * (1.0 + edge * 2.0) - edge;
	float burnt = step(field, front);
	float scorch = 1.0 - smoothstep(front, front + edge, field);
	float rim = 1.0 - smoothstep(front, front + edge * RIM_SHARE, field);
	float flick = 1.0 - FLICKER_DEPTH * rc_live() * (0.5 + 0.5 * sin(rc_time(TIME) * FLICKER_RATE + n * 40.0));
	c.rgb = mix(c.rgb, char_color.rgb, scorch * 0.85);
	c.rgb = mix(c.rgb, ember.rgb, rim * flick);
	c.a *= 1.0 - burnt;
	COLOR = c;
}
