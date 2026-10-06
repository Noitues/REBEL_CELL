// B1a (M14 integration review D1, section d; ART_BIBLE v2 3.1, 4.1): the world's darkening under
// the UI. One full-screen quad drawn between the world (3D city, backdrop stills) and the UI, in
// multiply: it leaves the world at `1 - removal` inside each shape's pool and dark bands under the
// bars, and 1.0 (untouched) everywhere else. The shapes come from the rects of the panels, wheels
// and bars the screen registered (UiScrimPools), refreshed each frame; UiScrimPools.factor_at
// mirrors this maths for the tests.
// Static: nothing animates (reduce effects has nothing to stop); rc_common keeps the convention.
shader_type canvas_item;
render_mode blend_mul, unshaded;
#include "res://shaders/lib/rc_common.gdshaderinc"

// Keep equal to UiScrimPools.MAX_SHAPES.
const int MAX_SHAPES = 32;

uniform int count = 0;
// xy = centre (px, this quad's own space), zw = half size (px; a disc has 0, 0).
uniform vec4 shape_rect[MAX_SHAPES];
// x = kind (0 disc pool, 1 rect pool, 2 band), y = corner radius (px; a disc: its edge's softness,
// a share of its radius), z = reach (px: the disc's radius, a rect's fade past its edge), w =
// removal (1 - what it leaves of the world).
uniform vec4 shape_params[MAX_SHAPES];
uniform float falloff = 4.0;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float sd_box(vec2 p, vec2 b, float r) {
	vec2 q = abs(p) - b + vec2(r);
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	float pool = 0.0;
	float band = 0.0;
	for (int i = 0; i < MAX_SHAPES; i++) {
		if (i >= count) {
			break;
		}
		vec4 r = shape_rect[i];
		vec4 q = shape_params[i];
		float reach = max(q.z, 0.001);
		float m;
		if (q.x < 0.5) {
			m = 1.0 - smoothstep(reach * (1.0 - q.y), reach * (1.0 + q.y), length(local_px - r.xy));
		} else {
			float d = max(sd_box(local_px - r.xy, r.zw, q.y), 0.0);
			m = exp(-pow(d / reach, falloff));
		}
		if (q.x > 1.5) {
			band = max(band, q.w * m);
		} else {
			pool = max(pool, q.w * m);
		}
	}
	float f = (1.0 - pool) * (1.0 - band);
	COLOR = vec4(vec3(f), 1.0);
}
