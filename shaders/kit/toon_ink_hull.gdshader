// REBEL_CELL material kit (ART-1 1B): the ink lines of the 3D world (ART_BIBLE v2 §1.2
// "wobbly ink lines from id/normal/depth edges"). The inverted-hull approach: the mesh drawn
// again as `next_pass` of `toon_ink.gdshader`, front faces culled, grown along its normals by
// `width_px` screen pixels (constant on screen at any zoom, orthographic or perspective),
// wobbling along the line by a world-space noise (`wobble`), in flat ink. Silhouettes and
// creases between facets read as hand-inked lines. A post-process edge pass (depth/normal)
// is area 1D's choice for the city; this hull suits props and single buildings.
// Static (no TIME): reduce effects changes nothing; the include keeps the one control.
shader_type spatial;
render_mode unshaded, cull_front, depth_draw_opaque;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec4 ink : source_color = vec4(0.047, 0.039, 0.086, 1.0);
uniform float width_px = 2.5;
uniform float wobble : hint_range(0.0, 1.0) = 0.35;
uniform float wobble_scale = 2.2;

float h31(vec3 p) {
	return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453);
}

float vn3(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * (3.0 - 2.0 * f);
	float a = mix(mix(h31(i), h31(i + vec3(1, 0, 0)), u.x), mix(h31(i + vec3(0, 1, 0)), h31(i + vec3(1, 1, 0)), u.x), u.y);
	float b = mix(mix(h31(i + vec3(0, 0, 1)), h31(i + vec3(1, 0, 1)), u.x), mix(h31(i + vec3(0, 1, 1)), h31(i + vec3(1, 1, 1)), u.x), u.y);
	return mix(a, b, u.z);
}

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float w = width_px * (1.0 + wobble * (vn3(wp * wobble_scale) - 0.5) * 2.0);
	vec4 clip = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
	vec3 n_view = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec2 n_clip = normalize((PROJECTION_MATRIX * vec4(n_view, 0.0)).xy + vec2(1e-5));
	clip.xy += n_clip * w * 2.0 / VIEWPORT_SIZE * clip.w;
	POSITION = clip;
}

void fragment() {
	ALBEDO = ink.rgb;
}
