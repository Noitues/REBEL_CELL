// REBEL_CELL material kit (M14 B1c, integration review D23): the CRT glass's faint scrolling
// hex dump (ART_BIBLE v2 §1.2 "CRT terminal", §6.4 crt_panel: "hex-dump 6 %"). One shared
// include for every terminal glass: crt_terminal.gdshader (CrtTerminalPanel, CrtWindow, the
// kit's terminals) and crt_panel.gdshader (UiTheme.crt_material: the older terminal panels,
// the HUD and log strips), so each gets the dump by default with no per-screen work.
//
// Rows of `HEX_BYTES` bytes behind a 4-digit address ("0000 3F A1 ..."), `HEX_ROWS` rows to a
// block that repeats; the row's columns repeat across the panel's width (a blank column
// between) so a wide panel is filled edge to edge as in the round 44 terminals, glyphs from shaders/kit/hex_atlas.png (Share Tech Mono 0-F, baked by
// tools/design_lab/hex_atlas_bake.py), one atlas cell per character of a `hex_cell` grid (the
// mono advance and line height at the caption size, set by the script). It scrolls up at
// `hex_scroll` px/s (the crt_hex_scroll motion entry's amplitude; 0 when the motion is off)
// on rc_time, so reduce effects hold it still. `hexdump` is its alpha (0 removes it).
#ifndef RC_HEX_DUMP_INCLUDED
#define RC_HEX_DUMP_INCLUDED

#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D hex_atlas : hint_default_transparent, filter_linear_mipmap, repeat_disable;
uniform float hexdump : hint_range(0.0, 1.0) = 0.06;
uniform vec2 hex_cell = vec2(6.5, 13.5);
uniform vec2 hex_origin = vec2(8.0, 0.0);
uniform float hex_scroll = 14.0;
uniform float hex_seed = 7.0;
uniform vec4 hex_tint : source_color = vec4(0.361, 0.882, 1.0, 1.0);

const float HEX_BYTES = 12.0;
const float HEX_ROWS = 48.0;
const float HEX_COLS = 41.0; // 4 address digits, a space, then HEX_BYTES x "XX "
const float HEX_SPAN = 42.0; // a dump column block and the blank column after it

float rc_hex_hash(float seed, float row, float b) {
	return fract(sin(dot(vec3(seed, row, b), vec3(12.9898, 78.233, 37.719))) * 43758.5453);
}

// The dump's coverage (0..1) at panel-local px `p`.
float rc_hex_dump(vec2 p) {
	if (hexdump <= 0.0) {
		return 0.0;
	}
	vec2 cell = max(hex_cell, vec2(1.0));
	float block = cell.y * HEX_ROWS;
	float y = p.y - hex_origin.y + mod(rc_time(TIME) * hex_scroll, block);
	float x = p.x - hex_origin.x;
	float span_col = floor(x / cell.x);
	float block_x = floor(span_col / HEX_SPAN);
	float col = mod(span_col, HEX_SPAN);
	if (x < 0.0 || col >= HEX_COLS) {
		return 0.0;
	}
	float row = mod(floor(y / cell.y), HEX_ROWS) + block_x * HEX_ROWS;
	float digit = -1.0;
	if (col < 4.0) {
		digit = mod(floor(row * HEX_BYTES / pow(16.0, 3.0 - col)), 16.0);
	} else if (col >= 5.0) {
		float j = col - 5.0;
		float k = mod(j, 3.0);
		if (k < 2.0) {
			float byte_v = floor(rc_hex_hash(hex_seed, row, floor(j / 3.0)) * 255.0);
			digit = k < 1.0 ? floor(byte_v / 16.0) : mod(byte_v, 16.0);
		}
	}
	if (digit < 0.0) {
		return 0.0;
	}
	vec2 f = vec2(fract(x / cell.x), fract(y / cell.y));
	vec2 uv = vec2((digit + f.x) / 16.0, f.y);
	vec2 scale = vec2(1.0 / (cell.x * 16.0), 1.0 / cell.y);
	return textureGrad(hex_atlas, uv, dFdx(p) * scale, dFdy(p) * scale).a;
}

#endif
