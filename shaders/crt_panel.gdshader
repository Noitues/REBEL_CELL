// Terminal glass (STYLE_GUIDE 5-6): faint scanlines and flicker on terminal panels, the
// HUD and log strips only; paper, Polaroids and stamps never get it. Every effect is a
// uniform so reduce-effects can zero it.
// M14 B1c (integration review D23): the faint scrolling hex dump at `hexdump` (6 % by default,
// hex_dump.gdshaderinc, the same dump as the kit's CRT glass) on the panel's dark glass only:
// it fades out over bright pixels, so the panel's own words and edge never carry it.
shader_type canvas_item;
// Reduce effects (rc_common): the flicker stops and the hex dump holds still; the static
// scanlines stay.
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/kit/hex_dump.gdshaderinc"

uniform float scan_strength : hint_range(0.0, 1.0) = 0.12;
uniform float flicker : hint_range(0.0, 0.1) = 0.01;
// The glass the dump marks: pixels darker than `hex_glass_luma` (fading out to it from
// `hex_glass_luma * 0.5`) with at least `hex_glass_alpha` coverage.
uniform float hex_glass_luma : hint_range(0.0, 1.0) = 0.3;
uniform float hex_glass_alpha : hint_range(0.0, 1.0) = 0.5;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

void fragment() {
	vec4 c = COLOR * texture(TEXTURE, UV);
	float luma = dot(c.rgb, vec3(0.2126, 0.7152, 0.0722));
	float glass = (1.0 - smoothstep(hex_glass_luma * 0.5, hex_glass_luma, luma)) * step(hex_glass_alpha, c.a);
	c.rgb = mix(c.rgb, hex_tint.rgb, hexdump * glass * rc_hex_dump(local_px));
	float line = step(0.5, fract(FRAGCOORD.y / 3.0));
	c.rgb *= 1.0 - scan_strength * line;
	c.rgb *= 1.0 - flicker * rc_live() * (0.5 + 0.5 * sin(rc_time(TIME) * 43.0));
	COLOR = c;
}
