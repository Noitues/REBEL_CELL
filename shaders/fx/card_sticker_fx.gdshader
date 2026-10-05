// ART-2 2C (ART_BIBLE v2 §3.18, §6.3): the played sticker card's slap gloss and dissolve A
// scan, on a flying card copy (CombatFxLayer.play_card through StickerSeam). Until Group 1's
// sticker material (1B) lands, this is the seam's stand-in: `scan_y` hides the card above
// the scan front (the bits take its place), `gloss_t` sweeps a white gloss band across it.
// Under reduce effects no gloss sweeps (the card play slides and fades instead).
shader_type canvas_item;

#include "res://shaders/lib/rc_common.gdshaderinc"

// The card's size (px, its own local frame).
uniform vec2 card_size = vec2(112.0, 148.0);
// Share of the card (from the top) already decoded into bits: 0 = the whole card shows.
uniform float scan_y : hint_range(0.0, 1.0) = 0.0;
// The scan front's bright line (share of the card's height).
uniform float scan_band : hint_range(0.0, 0.2) = 0.04;
// How far the die-cut edge and shadow stand past the card (share of its height).
uniform float edge_share : hint_range(0.0, 0.3) = 0.1;
// The gloss band's place along the card's diagonal (-1 = none, 0..1 across).
uniform float gloss_t = -1.0;
uniform float gloss_width : hint_range(0.0, 1.0) = 0.18;
uniform float gloss_alpha : hint_range(0.0, 1.0) = 0.55;
uniform vec4 front_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);

varying vec2 local_pos;

void vertex() {
	local_pos = VERTEX;
}

void fragment() {
	vec2 uv = local_pos / max(card_size, vec2(1.0));
	// The scan runs over the die-cut edge and shadow too (they stand past the card's rect).
	float front = mix(-edge_share, 1.0 + edge_share, scan_y);
	if (scan_y > 0.0 && uv.y < front) {
		discard;
	}
	vec4 c = COLOR;
	// The scan front: a white-hot line just under the decoded part.
	if (scan_y > 0.0 && uv.y < front + scan_band) {
		c.rgb = mix(c.rgb, front_color.rgb, 0.85);
	}
	if (gloss_t >= 0.0) {
		float d = abs((uv.x + uv.y) * 0.5 - gloss_t);
		float g = smoothstep(gloss_width, 0.0, d) * gloss_alpha * rc_live();
		c.rgb = mix(c.rgb, vec3(1.0), g);
	}
	COLOR = c;
}
