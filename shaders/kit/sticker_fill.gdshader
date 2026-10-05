// REBEL_CELL material kit (ART-1 1B): the fill of a vinyl sticker's lettering or face
// (ART_BIBLE v2 §1.2 "Vinyl sticker"; ported from the round 3 combined_v2 concept toolkit
// `sticker_lib.py` holo_tex / vgrad_tex). Drawn on the glyphs (or a face shape) inside the
// sticker's SubViewport: the glyph coverage comes in COLOR (so MSDF and plain faces both
// work), the shader only replaces the colour.
//   mode 0: a vertical gradient fill_top -> fill_bottom over [band_top, band_bottom] (px).
//   mode 1: holo foil: a silvered hue field, diffraction lines and sparkles; the hue drifts
//           (holo_drift, the lifecycle IDLE "holo foil hue drifts") and stops under reduce
//           effects.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int mode = 0;
uniform vec4 fill_top : source_color = vec4(1.0, 0.376, 0.675, 1.0);
uniform vec4 fill_bottom : source_color = vec4(0.871, 0.071, 0.439, 1.0);
uniform float band_top = 0.0;
uniform float band_bottom = 100.0;
// Holo: hue cycles per second of drift (0 = still) and the seed of its field.
uniform float holo_drift = 0.0;
uniform float holo_seed = 11.0;
uniform float holo_sat : hint_range(0.0, 1.0) = 0.55;
// Size of the holo field (px): the hue sweeps once across it.
uniform vec2 field_size = vec2(400.0, 160.0);

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float rc_hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

vec3 hsv2rgb(vec3 c) {
	vec3 p = abs(fract(c.xxx + vec3(1.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
	return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

vec3 holo(vec2 px) {
	vec2 uv = px / max(field_size, vec2(1.0));
	float a1 = rc_hash(vec2(holo_seed, 1.0)) * 6.28;
	float a2 = rc_hash(vec2(holo_seed, 2.0)) * 6.28;
	float a3 = rc_hash(vec2(holo_seed, 3.0)) * 6.28;
	float phase = rc_time(TIME) * holo_drift;
	float hue = fract(0.85 * uv.x + 0.55 * uv.y + 0.10 * sin(7.0 * uv.x + a1) + 0.08 * sin(6.0 * uv.y + 3.0 * uv.x + a2) + phase);
	float val = 0.93 + 0.07 * sin(9.0 * (uv.x - uv.y) + a3 + phase * 6.28);
	vec3 c = hsv2rgb(vec3(hue, holo_sat, val));
	// pulled toward silver for a metallic base
	c = c * 0.78 + vec3(0.20, 0.20, 0.22);
	// fine diffraction lines (every 5 px, slanted)
	float line = step(0.82, fract((px.x - px.y * 0.6) / 5.0));
	c = mix(c, vec3(1.0), line * 0.18);
	// sparkles
	vec2 cell = floor(px / 9.0);
	float sp = rc_hash(cell + holo_seed);
	vec2 at = (cell + vec2(rc_hash(cell + 3.1), rc_hash(cell + 7.7))) * 9.0;
	float d = length(px - at);
	c = mix(c, vec3(1.0), step(0.86, sp) * smoothstep(1.6, 0.4, d) * 0.8);
	return clamp(c, 0.0, 1.0);
}

void fragment() {
	vec3 rgb;
	if (mode == 1) {
		rgb = holo(local_px);
	} else {
		float t = clamp((local_px.y - band_top) / max(band_bottom - band_top, 1.0), 0.0, 1.0);
		rgb = mix(fill_top.rgb, fill_bottom.rgb, t);
	}
	COLOR = vec4(rgb, COLOR.a);
}
