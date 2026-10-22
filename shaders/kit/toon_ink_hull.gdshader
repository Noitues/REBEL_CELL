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
// LOOK-TOOLBOX module 5: the hull's width and screen offset (rc_ink), its grain (rc_look's sin noise).
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_ink.gdshaderinc"

uniform vec4 ink : source_color = vec4(0.047, 0.039, 0.086, 1.0);
uniform float width_px = 2.5;
uniform float wobble : hint_range(0.0, 1.0) = 0.35;
uniform float wobble_scale = 2.2;

void vertex() {
	vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float w = rcl_hull_width(width_px, wobble, rcl_vnoise3_sin(wp * wobble_scale));
	vec4 clip = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0);
	vec3 n_view = normalize((MODELVIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
	vec2 n_clip = normalize((PROJECTION_MATRIX * vec4(n_view, 0.0)).xy + vec2(1e-5));
	POSITION = rcl_hull_clip(clip, n_clip, w, VIEWPORT_SIZE);
}

void fragment() {
	ALBEDO = ink.rgb;
}
