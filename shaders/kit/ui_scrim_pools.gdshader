// B1a (M14 integration review D1, section d; ART_BIBLE v2 3.1, 4.1): the world's darkening under
// the UI. One full-screen quad drawn between the world (3D city, backdrop stills) and the UI. It
// reads the world drawn so far and, inside each registered shape, desaturates it toward its own
// luma (Rec. 709) by the pools' cap (D1: 0.6) and multiplies it by what the shape leaves
// (`1 - removal`); outside every shape it draws nothing. Pools round wheels and panels, bands under
// bars. On a map page the network's links and node discs (the 3D city's ground decal, bible 4.1:
// full strength) are kept out of it: the same segments and nodes the decal draws, mapped from this
// quad's px to the ground plane (`keep_*`). UiScrimPools.apply_at mirrors this maths for the tests.
// Static: nothing animates (reduce effects has nothing to stop); rc_common keeps the convention.
shader_type canvas_item;
render_mode blend_mix, unshaded;
#include "res://shaders/lib/rc_common.gdshaderinc"

// Keep equal to UiScrimPools.MAX_SHAPES.
const int MAX_SHAPES = 32;

uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform int count = 0;
// xy = centre (px, this quad's own space), zw = half size (px; a disc has 0, 0).
uniform vec4 shape_rect[MAX_SHAPES];
// x = kind (0 disc pool, 1 rect pool, 2 band), y = the distance (px; from a disc's centre, past a
// rect's edge) it holds full darkness to, z = the distance it has faded out at, w = removal
// (1 - what it leaves of the world).
uniform vec4 shape_params[MAX_SHAPES];
uniform float pool_saturation = 0.6;
// B2 (art director): emissives (signs, lit windows: the brightest channel from emissive_from up,
// fully at emissive_to) are never capped.
uniform float emissive_from = 0.72;
uniform float emissive_to = 0.9;

// The network kept at full strength (UiScrimPools.keep_network): ground XZ (BU) =
// keep_o + px.x * keep_x + px.y * keep_y; the decal's buffers and sizes (CityNetworkData, the
// decal's view px: keep_bu_per_px BU each).
uniform bool keep_on = false;
uniform vec2 keep_o = vec2(0.0);
uniform vec2 keep_x = vec2(1.0, 0.0);
uniform vec2 keep_y = vec2(0.0, 1.0);
uniform sampler2D keep_nodes : filter_nearest;
uniform int keep_node_count = 0;
uniform sampler2D keep_segs : filter_nearest;
uniform int keep_seg_count = 0;
uniform float keep_bu_per_px = 0.25;
uniform float keep_mgmt = 0.0;
uniform float keep_trace_px = 3.0;
uniform float keep_node_px = 13.0;
uniform float keep_bus_gap_px = 4.0;
uniform float keep_edge_px = 2.0;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float sd_box(vec2 p, vec2 b) {
	vec2 q = abs(p) - b;
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0);
}

float inside_px(float d_px, float half_px) {
	return 1.0 - smoothstep(half_px - 0.75, half_px + 0.75, d_px);
}

// 1 on the network's traces and node discs (with their keyline), 0 off them.
float network_keep(vec2 px) {
	vec2 p = keep_o + px.x * keep_x + px.y * keep_y;
	float bu = max(keep_bu_per_px, 0.0001);
	float k = 0.0;
	// The widest a trace's keep can be (link widths up to 4x the reference; CityNetworkData).
	float w_max = keep_trace_px * 2.0 + keep_edge_px + keep_mgmt * keep_bus_gap_px + 1.0;
	for (int i = 0; i < keep_seg_count; i++) {
		vec4 s0 = texelFetch(keep_segs, ivec2(i, 0), 0);
		vec2 ab = s0.zw - s0.xy;
		float h = clamp(dot(p - s0.xy, ab) / max(dot(ab, ab), 1e-6), 0.0, 1.0);
		float d = length(p - s0.xy - ab * h) / bu;
		if (d > w_max) {
			continue;
		}
		vec4 s2 = texelFetch(keep_segs, ivec2(i, 2), 0);
		float w = keep_trace_px * max(s2.z, 0.6) * 0.5 + keep_edge_px + keep_mgmt * keep_bus_gap_px;
		k = max(k, inside_px(d, w));
	}
	for (int i = 0; i < keep_node_count; i++) {
		vec4 n0 = texelFetch(keep_nodes, ivec2(i, 0), 0);
		float d = length(p - n0.xy) / bu;
		float r = keep_node_px * n0.z * (1.0 + keep_mgmt * 0.7) + keep_edge_px;
		k = max(k, inside_px(d, r));
	}
	return k;
}

void fragment() {
	float pool = 0.0;
	float band = 0.0;
	float sat = 0.0;
	for (int i = 0; i < MAX_SHAPES; i++) {
		if (i >= count) {
			break;
		}
		vec4 r = shape_rect[i];
		vec4 q = shape_params[i];
		float d = q.x < 0.5 ? length(local_px - r.xy) : max(sd_box(local_px - r.xy, r.zw), 0.0);
		float m = 1.0 - smoothstep(q.y, max(q.z, q.y + 0.001), d);
		if (q.x > 1.5) {
			band = max(band, q.w * m);
		} else {
			pool = max(pool, q.w * m);
			sat = max(sat, m);
		}
	}
	if (pool <= 0.0005 && band <= 0.0005) {
		discard;
	}
	if (keep_on) {
		float k = 1.0 - network_keep(local_px);
		pool *= k;
		band *= k;
		sat *= k;
	}
	vec3 c = texture(screen_tex, SCREEN_UV).rgb;
	float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
	sat *= 1.0 - smoothstep(emissive_from, emissive_to, max(max(c.r, c.g), c.b));
	c = mix(vec3(l), c, mix(1.0, pool_saturation, sat));
	COLOR = vec4(c * (1.0 - pool) * (1.0 - band), 1.0);
}
