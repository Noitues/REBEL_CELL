// REBEL_CELL material kit (ART-1 1B): the CRT terminal ("Screens & Data", ART_BIBLE v2 §1.2,
// §6.4 crt_panel: scanlines 3 px @ 10 %, hex-dump 6 %, edge glow). The Cell's own systems.
// Two passes of one shader over the panel's rect (grown by `glow_px` for the outer glow):
//   mode 0 (glass, under the panel's text): navy glass graded top to bottom with a soft
//          inner vignette, the accent edge line, the outer edge glow and the corner notch;
//   mode 1 (overlay, over the text): the 3 px scanlines at `scan_strength`, a faint
//          rolling brightness band and the inner edge glow. The band rolls on TIME and stops
//          under reduce effects (static scanlines stay, §5.4).
// Every effect is a uniform so a view (or high contrast) can zero it.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int mode = 0;
// The panel itself inside the drawn rect (px, local): x, y, w, h.
uniform vec4 panel = vec4(0.0, 0.0, 100.0, 100.0);
uniform vec4 glass_top : source_color = vec4(0.043, 0.086, 0.188, 0.94);
uniform vec4 glass_bottom : source_color = vec4(0.020, 0.039, 0.102, 0.94);
uniform vec4 accent : source_color = vec4(0.361, 0.882, 1.0, 1.0);
uniform float edge_px = 1.5;
uniform float glow_px = 10.0;
uniform float glow_strength : hint_range(0.0, 1.0) = 0.45;
uniform float inner_glow : hint_range(0.0, 1.0) = 0.18;
uniform float scan_px = 3.0;
uniform float scan_strength : hint_range(0.0, 1.0) = 0.10;
uniform float roll_strength : hint_range(0.0, 0.2) = 0.03;
uniform float roll_seconds = 7.0;
uniform float notch_px = 14.0;
uniform float corner_px = 3.0;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

// Signed distance to the panel's rounded rect (negative inside).
float panel_sd(vec2 p) {
	vec2 c = panel.xy + panel.zw * 0.5;
	vec2 q = abs(p - c) - panel.zw * 0.5 + vec2(corner_px);
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - corner_px;
}

void fragment() {
	vec2 p = local_px;
	float sd = panel_sd(p);
	vec4 col = vec4(0.0);
	if (mode == 0) {
		if (sd <= 0.0) {
			float t = clamp((p.y - panel.y) / max(panel.w, 1.0), 0.0, 1.0);
			vec4 g = mix(glass_top, glass_bottom, t);
			// soft inner vignette toward the edge
			float vig = smoothstep(0.0, 28.0, -sd);
			g.rgb *= mix(0.78, 1.0, vig);
			// faint accent wash near the edge (glass catches the edge light)
			g.rgb += accent.rgb * (1.0 - smoothstep(0.0, 18.0, -sd)) * inner_glow * 0.5;
			col = g;
			// the edge line
			float edge = 1.0 - smoothstep(edge_px - 0.5, edge_px + 0.5, -sd);
			col = mix(col, vec4(accent.rgb, 1.0), edge);
			// the corner notch (top-left accent triangle)
			vec2 n = p - panel.xy;
			if (n.x + n.y < notch_px) {
				col = vec4(accent.rgb * 0.85, 1.0);
			}
		} else {
			// the outer edge glow
			float gl = exp(-sd / max(glow_px * 0.42, 0.5)) * glow_strength;
			col = vec4(accent.rgb, gl);
		}
	} else {
		if (sd <= 0.0) {
			float line = step(0.5, fract((p.y - panel.y) / scan_px));
			float roll = 0.0;
			float h = max(panel.w, 1.0);
			float band = fract(rc_time(TIME) / max(roll_seconds, 0.1));
			float y = (p.y - panel.y) / h;
			roll = exp(-pow((y - band) / 0.08, 2.0)) * roll_strength * rc_live();
			float ig = (1.0 - smoothstep(0.0, 10.0, -sd)) * inner_glow;
			// darken the scanlines, lift the roll band and the inner glow
			col = vec4(0.0, 0.0, 0.0, scan_strength * line);
			col = mix(col, vec4(accent.rgb, 1.0), clamp(roll + ig * 0.5, 0.0, 1.0) * 0.6);
			col.a = max(col.a, (roll + ig * 0.5) * 0.6);
		}
	}
	COLOR = col;
}
