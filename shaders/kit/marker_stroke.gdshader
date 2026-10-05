// REBEL_CELL material kit (ART-1 1B): grease pencil wax (ART_BIBLE v2 §1.2 "Grease pencil",
// §6.3 marker_stroke.gdshader; ported from the round 3 tactical-glass concept `tg_lib.py`
// Layer.wax_stroke / light). On a Line2D (texture mode TILE: UV.x runs along the stroke in
// stroke widths, UV.y across it):
//   mode 0 wax: an opaque core with bristle striations along the stroke and dropouts toward
//          the edges, a ragged edge from the wax grain, a sheen line, alpha 0.96;
//   mode 1 shadow: the dark under-shadow (soft edge) under the wax, offset by the script;
//   mode 2 text: wax grain on glyph coverage (COLOR.a) for pencil words.
// Dashed (what-if) cuts hand-dashes along UV.x. The glint runs across the wax every
// `glint_period` s (pencil_glint) and stops under reduce effects; the wax itself is static.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int mode = 0;
uniform vec4 ink : source_color = vec4(1.0, 0.886, 0.0, 1.0);
uniform float alpha_max = 0.96;
uniform float seed = 1.0;
uniform bool dashed = false;
// Dash and gap lengths in stroke widths.
uniform float dash_len = 3.2;
uniform float gap_len = 1.9;
// Glint: seconds of the run, seconds between runs, strength; the span (px) it crosses.
uniform float glint_run = 0.6;
uniform float glint_rest = 3.0;
uniform float glint_strength = 0.55;
uniform vec2 glint_span = vec2(400.0, 300.0);
// Wipe smear 0..1: the wax breaks up as the palm drags it (the cloth wipe).
uniform float smear = 0.0;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float hsh(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hsh(i), hsh(i + vec2(1.0, 0.0)), u.x), mix(hsh(i + vec2(0.0, 1.0)), hsh(i + vec2(1.0, 1.0)), u.x), u.y);
}

float glint_band(vec2 p) {
	float period = glint_run + glint_rest;
	float t = mod(rc_time(TIME), max(period, 0.01));
	float run = clamp(t / max(glint_run, 0.01), 0.0, 1.0);
	float on = step(t, glint_run) * rc_live();
	float pos = mix(-0.15, 1.15, run);
	float s = (p.x / max(glint_span.x, 1.0) * 0.78 + p.y / max(glint_span.y, 1.0) * 0.42) / 1.2;
	float band = exp(-pow((s - pos) / 0.035, 2.0)) + exp(-pow((s - pos + 0.06) / 0.012, 2.0)) * 0.6;
	return band * on * glint_strength;
}

void fragment() {
	float grain = vnoise(local_px * 0.62 + seed * 17.0) * 0.6 + vnoise(local_px * 0.25 + seed * 3.0) * 0.4;
	float mid = vnoise(local_px * 0.055 + seed * 9.0);
	if (mode == 2) {
		float a = COLOR.a;
		float tooth = smoothstep(0.06, 0.16, grain);
		a = smoothstep(0.22, 0.62, a * (0.8 + 0.2 * tooth) + (grain - 0.5) * 0.18);
		vec3 c = ink.rgb * (0.88 + 0.12 * mid);
		c += vec3(1.0, 0.98, 0.95) * glint_band(local_px) * a;
		COLOR = vec4(c, a * alpha_max);
	} else {
		float across = UV.y * 2.0 - 1.0;
		float edge_d = abs(across);
		float along = UV.x;
		if (dashed) {
			float cycle = dash_len + gap_len;
			float k = floor(along / cycle);
			float jit = (hsh(vec2(k, seed)) - 0.5) * 0.5;
			if (mod(along, cycle) > dash_len * (1.0 + jit)) {
				discard;
			}
		}
		if (mode == 1) {
			float a = (1.0 - smoothstep(0.55, 1.0, edge_d)) * 0.42;
			COLOR = vec4(ink.rgb, a);
		} else {
			// bristles: bands across the stroke, each with its own dropouts along it
			float nb = 9.0;
			float b = floor(UV.y * nb);
			float bu = abs(b / (nb - 1.0) - 0.5) * 2.0;
			float val = vnoise(vec2(along * (1.2 + hsh(vec2(b, seed)) * 0.9), b * 13.0 + seed * 5.0));
			float thr = 0.02 + 0.30 * pow(bu, 3.0) + smear * 0.55;
			float bristle = step(thr, val);
			float core = 1.0 - smoothstep(0.62, 0.72, edge_d);
			float m = max(core * 0.74 * (1.0 - smear * 0.6), bristle * (1.0 - smoothstep(0.86, 1.0, edge_d)));
			float tooth = smoothstep(0.06, 0.16, grain);
			float a = m * (0.80 + 0.20 * tooth);
			a = smoothstep(0.22, 0.62, a + (grain - 0.5) * 0.18) * (0.74 + 0.26 * smoothstep(0.75, 1.0, m));
			a = clamp(a * 1.08, 0.0, 1.0);
			vec3 c = ink.rgb * (0.88 + 0.12 * mid + 0.08 * bristle);
			// the wax's round body: lit along one side, shaded along the other, a sheen line
			c *= 1.0 + 0.30 * (-across) - 0.10;
			float sheen = exp(-pow((across + 0.42) / 0.12, 2.0)) * 0.45 * (0.8 + 0.4 * mid);
			c += vec3(1.0, 0.98, 0.95) * (sheen + glint_band(local_px) * (0.25 + 0.5 * grain));
			COLOR = vec4(min(c, vec3(1.25)), a * alpha_max);
		}
	}
}
