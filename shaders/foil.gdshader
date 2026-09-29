// Foil (PAPER, ART_BIBLE 6.3, 13; W4): the holographic stock of a rare card. Rainbow
// bands run diagonally across the card and slide with `tilt` (the pointer, the right
// stick or the card's place under a pad focus), a bright glint follows the tilt, and a
// few hash sparkles twinkle. Drawn additively over the card's foil regions only (its
// border band and art window; the vertex colour's alpha is the region's strength), never
// over its words. Reduce effects: the tilt is ignored (a fixed `static_tilt`) and the
// sparkles stop, so the foil is a static sheen.
shader_type canvas_item;
render_mode blend_add;
#include "res://shaders/lib/rc_common.gdshaderinc"

// The foil's tilt, -1..1 on each axis (set by ZineCard from the pointer or stick).
uniform vec2 tilt = vec2(0.0);
// The fixed tilt shown under reduce effects (a static sheen).
uniform vec2 static_tilt = vec2(0.35, -0.2);
// The card's size in px (the pattern is laid out across the whole card).
uniform vec2 card_size = vec2(112.0, 148.0);
// How bright the foil adds over the stock, and the width of one rainbow band (px).
uniform float strength : hint_range(0.0, 1.0) = 0.42;
uniform float band_px = 22.0;
// Sparkle density (share of 2 px cells) and brightness.
uniform float sparkle_share : hint_range(0.0, 0.2) = 0.02;
uniform float sparkle = 0.6;
// How far one unit of tilt slides the bands (bands) and the glint (share of the card).
const float BAND_SLIDE = 1.6;
const float GLINT_SLIDE = 0.35;
// The glint's sharpness and the share of the rainbow always shown outside it.
const float GLINT_SHARP = 4.0;
const float BASE_SHEEN = 0.35;
const vec2 BAND_DIR = vec2(0.857, 0.514);
const float SPARKLE_CELL = 2.0;
const float SPARKLE_RATE = 3.0;

varying vec2 local;

void vertex() {
	local = VERTEX;
}

vec3 hue(float h) {
	return clamp(abs(mod(h * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
}

void fragment() {
	vec2 t = mix(static_tilt, tilt, rc_live());
	vec2 uv = local / max(card_size, vec2(1.0));
	float d = dot(uv - 0.5, BAND_DIR);
	float phase = d * card_size.y / band_px + t.x * BAND_SLIDE + t.y * BAND_SLIDE * 0.5;
	vec3 rainbow = hue(fract(phase * 0.25));
	float glint = pow(max(0.0, 1.0 - abs(d - t.x * GLINT_SLIDE) * GLINT_SHARP), 3.0);
	vec2 cell = floor(local / SPARKLE_CELL);
	float lit = step(1.0 - sparkle_share, rc_hash(cell));
	float twinkle = 0.5 + 0.5 * sin(rc_time(TIME) * SPARKLE_RATE + rc_hash(cell + 7.0) * 6.2832);
	vec3 col = rainbow * (BASE_SHEEN + (1.0 - BASE_SHEEN) * glint) + vec3(lit * sparkle * twinkle);
	COLOR = vec4(col * strength, COLOR.a);
}
