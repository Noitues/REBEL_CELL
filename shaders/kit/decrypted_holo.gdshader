// REBEL_CELL material kit (ART-1 1B): the decrypted holo (ART_BIBLE v2 §1.2 "Decrypted holo":
// hacked corp intel: the selected Site file, THREAT INTEL, intercepted corp news). Corp tint
// at about 78 %, 4 px scanlines at 12 %, three slow bands (6 s), a +-2 px RGB split on the edge only (never
// on the text). Two passes over the panel's rect:
//   mode 0 (under the text): the tinted glass, the edge in three offset channels;
//   mode 1 (over the text): the scanlines and the slow bands.
// The bands roll on TIME (holo_bands) and stop under reduce effects; the RGB split is static
// and zeroed by the script under reduce effects (§5.4: no RGB split).
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int mode = 0;
uniform vec4 panel = vec4(0.0, 0.0, 100.0, 100.0);
uniform vec4 tint : source_color = vec4(0.24, 1.0, 0.545, 1.0);
uniform vec4 deep : source_color = vec4(0.008, 0.012, 0.039, 1.0);
// B1c-b (art director, round 21 / round 44): the body is the dark 0.88 scrim with the corp tint
// at about 28 % over it; the FULL tint goes on the edge, the scanlines and the bands (and the
// words, at 78 %, in the script).
uniform float tint_share : hint_range(0.0, 1.0) = 0.78;
uniform float fill_share : hint_range(0.0, 1.0) = 0.28;
uniform float glass_alpha : hint_range(0.0, 1.0) = 0.88;
uniform float scan_px = 4.0;
uniform float scan_strength : hint_range(0.0, 1.0) = 0.12;
uniform float band_count = 3.0;
uniform float band_strength : hint_range(0.0, 0.3) = 0.1;
uniform float band_seconds = 6.0;
uniform float split_px = 2.0;
uniform float edge_px = 1.5;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float sd_rect(vec2 p) {
	vec2 c = panel.xy + panel.zw * 0.5;
	vec2 q = abs(p - c) - panel.zw * 0.5;
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0);
}

float edge_at(vec2 p) {
	float d = abs(sd_rect(p) + edge_px * 0.5);
	return 1.0 - smoothstep(edge_px * 0.5, edge_px * 0.5 + 1.0, d);
}

void fragment() {
	vec2 p = local_px;
	float sd = sd_rect(p);
	vec4 col = vec4(0.0);
	if (mode == 0) {
		if (sd <= 0.0) {
			// dark glass: the corp hue at fill_share over the deep, a little darker toward the bottom
			float t = clamp((p.y - panel.y) / max(panel.w, 1.0), 0.0, 1.0);
			vec3 g = mix(deep.rgb, tint.rgb, fill_share * mix(1.0, 0.7, t));
			col = vec4(g, glass_alpha);
		}
		// the edge in three channels, split +-split_px horizontally (edge only)
		float er = edge_at(p + vec2(split_px, 0.0));
		float eg = edge_at(p);
		float eb = edge_at(p - vec2(split_px, 0.0));
		vec3 e = vec3(er, eg, eb) * tint.rgb;
		float ea = max(max(er, eg), eb);
		col = vec4(mix(col.rgb, e / max(ea, 0.001), ea), max(col.a, ea));
	} else {
		if (sd <= 0.0) {
			float line = step(0.5, fract((p.y - panel.y) / scan_px));
			float y = (p.y - panel.y) / max(panel.w, 1.0);
			float roll = rc_time(TIME) / max(band_seconds, 0.1);
			float bands = pow(0.5 + 0.5 * sin((y * band_count - roll) * 6.2832), 6.0);
			// the scanlines in the full corp tint
			col = vec4(tint.rgb, scan_strength * line);
			col = mix(col, vec4(tint.rgb, 1.0), bands * band_strength);
			col.a = max(col.a, bands * band_strength);
		}
	}
	COLOR = col;
}
