// CRT overlay (STYLE_GUIDE 1.1, ART_BIBLE 2, 13): the one clean CRT look, for the CITY
// and GLASS materials only (never paper, Polaroids or stamps). On a CanvasItem's own
// texture (a glass panel, the city sprite, a ColorRect) it adds fine static scanlines, a
// slow soft roll band (T0: one pass every `roll_period` s, at least 3 s), a faint flicker,
// an optional colour fringe and a vignette. Reduce effects: the roll, the flicker and the
// fringe stop; the static scanlines and the vignette stay. The older crt_panel / scanline
// shaders keep working; new uses take this one.
shader_type canvas_item;
// Reduce effects (rc_common): roll, flicker and fringe stop.
#include "res://shaders/lib/rc_common.gdshaderinc"

// Scanline darkening and its row pitch (screen px).
uniform float scan_strength : hint_range(0.0, 1.0) = 0.08;
uniform float scan_pitch : hint_range(1.0, 8.0) = 3.0;
// The roll band's brightening and its period (s).
uniform float roll_strength : hint_range(0.0, 0.5) = 0.05;
uniform float roll_period : hint_range(3.0, 30.0) = 6.0;
// Flicker depth (a fast shimmer well under the flash limiter: no step changes).
uniform float flicker : hint_range(0.0, 0.1) = 0.006;
// Colour fringe (red left, blue right) in texture px; 0 = none.
uniform float fringe_px : hint_range(0.0, 4.0) = 0.0;
// Vignette depth at the item's corners.
uniform float vignette : hint_range(0.0, 1.0) = 0.0;

// The roll band's half-height (a share of the item's height).
const float ROLL_BAND = 0.08;
// Flicker speed (rad/s).
const float FLICKER_RATE = 43.0;

void fragment() {
	vec4 c = COLOR;
	float live = rc_live();
	float f = fringe_px * live;
	if (f > 0.0) {
		vec2 o = vec2(TEXTURE_PIXEL_SIZE.x * f, 0.0);
		vec4 base = texture(TEXTURE, UV);
		c.r += (texture(TEXTURE, UV - o).r - base.r) * c.a;
		c.b += (texture(TEXTURE, UV + o).b - base.b) * c.a;
	}
	c.rgb *= 1.0 - scan_strength * rc_scanline(FRAGCOORD.xy, scan_pitch);
	float t = rc_time(TIME);
	float band = 1.0 - smoothstep(0.0, ROLL_BAND, abs(fract(UV.y - t / roll_period) - 0.5));
	c.rgb *= 1.0 + roll_strength * live * band;
	c.rgb *= 1.0 - flicker * live * (0.5 + 0.5 * sin(t * FLICKER_RATE));
	c.rgb *= 1.0 - vignette * smoothstep(0.35, 0.75, distance(UV, vec2(0.5)));
	COLOR = c;
}
