// REBEL_CELL material kit (ART-1 1B): corp paper (ART_BIBLE v2 §1.2 "Corp paper": intercepted
// corp documents: the raid work order, after-action report, audit dossier, seizure notices,
// event memos). A printed sheet: the paper stock with fibres and a fine tooth, a faint
// toner speckle, a soft darkening toward the edges (handled paper) and a hard die edge.
// Scales like a 9-patch (the edge and corner treatment are in px, the field fills): one draw
// over the panel's rect. Static: nothing animates, so reduce effects changes nothing here;
// the include keeps the one control.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec4 panel = vec4(0.0, 0.0, 100.0, 100.0);
uniform vec4 stock : source_color = vec4(0.949, 0.933, 0.894, 1.0);
uniform vec4 fibre : source_color = vec4(0.373, 0.259, 0.141, 1.0);
uniform float seed = 3.0;
uniform float edge_dark = 0.12;
uniform float fibre_strength = 0.10;

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

void fragment() {
	vec2 p = local_px - panel.xy;
	vec3 c = stock.rgb;
	// cloudy formation and fine tooth
	float cloud = vnoise(p * 0.02 + seed) * 0.6 + vnoise(p * 0.07 + seed * 2.0) * 0.4;
	c *= 0.96 + 0.06 * cloud;
	float tooth = hsh(floor(p) + seed);
	c *= 0.985 + 0.03 * tooth;
	// fibres: thin streaks stretched along x
	float f = vnoise(vec2(p.x * 0.05, p.y * 0.9) + seed * 7.0);
	c = mix(c, fibre.rgb, smoothstep(0.82, 0.95, f) * fibre_strength);
	// toner speckle
	c = mix(c, vec3(0.1), step(0.9985, hsh(floor(p * 0.5) + seed * 3.0)) * 0.5);
	// handled edges: darker toward the border
	vec2 e = min(p, panel.zw - p);
	float ed = min(e.x, e.y);
	c *= 1.0 - edge_dark * (1.0 - smoothstep(0.0, 24.0, ed));
	COLOR = vec4(c, 1.0);
}
