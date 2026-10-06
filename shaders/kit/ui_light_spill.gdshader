// B1a (M14 integration review D19; round 3 combined_v2's light spill from glowing base elements):
// emissive UI over the city (a neon sign, the pink verb sticker, the TARGET pencil) lights the
// world round it. One full-screen quad, additive, drawn after the pools and the panel shadows
// (the light falls on the darkened city): each spill adds its colour times `strength` under its
// element, falling off ((1 - t)^2) to nothing at `reach` px past the element's edge. An element
// is a box (a Control's rect: lit as a stadium from its middle line, so a word's light has no box
// edge) or a stroke segment (a pencil line: lit from the line). UiSpillShadows.spill_at mirrors it for the tests.
// Static: nothing animates (a source that dims passes its own strength).
shader_type canvas_item;
render_mode blend_add, unshaded;
#include "res://shaders/lib/rc_common.gdshaderinc"

// Keep equal to UiSpillShadows.MAX_SPILLS.
const int MAX_SPILLS = 16;

uniform int count = 0;
// A box: xy = the element's centre (px), zw = its half size (px). A stroke segment (a pencil
// line): xy = one end, zw = the other.
uniform vec4 spill_rect[MAX_SPILLS];
// rgb = colour, a = strength.
uniform vec4 spill_color[MAX_SPILLS];
// x = reach past the element's edge (px), y = a segment's half width (px), z = kind (0 box,
// 1 segment).
uniform vec4 spill_params[MAX_SPILLS];

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float sd_box(vec2 p, vec2 b, float r) {
	vec2 q = abs(p) - b + vec2(r);
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	vec3 add = vec3(0.0);
	for (int i = 0; i < MAX_SPILLS; i++) {
		if (i >= count) {
			break;
		}
		vec4 r = spill_rect[i];
		vec4 q = spill_params[i];
		float d;
		float m = 0.0;
		if (q.z > 0.5) {
			vec2 ab = r.zw - r.xy;
			float t = clamp(dot(local_px - r.xy, ab) / max(dot(ab, ab), 0.0001), 0.0, 1.0);
			d = max(length(local_px - (r.xy + ab * t)) - q.y, 0.0);
		} else {
			// A stadium round the element, its light falling from its middle line: no box edges.
			m = min(r.z, r.w);
			d = sd_box(local_px - r.xy, r.zw, m);
		}
		float k = clamp(1.0 - (d + m) / max(q.x + m, 0.001), 0.0, 1.0);
		add += spill_color[i].rgb * spill_color[i].a * k * k;
	}
	COLOR = vec4(min(add, vec3(1.0)), 1.0);
}
