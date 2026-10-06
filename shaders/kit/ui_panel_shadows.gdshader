// B1a (M14 integration review D19): the panels' soft drop shadows on the world. One full-screen
// quad in multiply, drawn after the scrim's pools and before the spill: each registered panel's
// rect, dropped by its offset, leaves the world at `1 - alpha` under it and fades to nothing over
// `soft` px past its edge ((1 - d / soft)^2). UiSpillShadows.shadow_at mirrors it for the tests.
// Static: nothing animates.
shader_type canvas_item;
render_mode blend_mul, unshaded;
#include "res://shaders/lib/rc_common.gdshaderinc"

// Keep equal to UiSpillShadows.MAX_SHADOWS.
const int MAX_SHADOWS = 24;

uniform int count = 0;
// xy = the dropped rect's centre (px), zw = its half size (px).
uniform vec4 shadow_rect[MAX_SHADOWS];
// x = corner radius (px), y = soft edge (px), z = alpha.
uniform vec4 shadow_params[MAX_SHADOWS];

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float sd_box(vec2 p, vec2 b, float r) {
	vec2 q = abs(p) - b + vec2(r);
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	float s = 0.0;
	for (int i = 0; i < MAX_SHADOWS; i++) {
		if (i >= count) {
			break;
		}
		vec4 r = shadow_rect[i];
		vec4 q = shadow_params[i];
		float d = max(sd_box(local_px - r.xy, r.zw, q.x), 0.0);
		float k = clamp(1.0 - d / max(q.y, 0.001), 0.0, 1.0);
		s = max(s, q.z * k * k);
	}
	COLOR = vec4(vec3(1.0 - s), 1.0);
}
