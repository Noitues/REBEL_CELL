// ART-5 5a: the network ground decal (bible §4.1 "Network decal by zoom", §6.1 "Network = one
// ground decal shader"; prototype art-concepts-r43 post36.Net36 / netdecal21). One quad on the
// ground over the network, reading CityNetworkData's buffers:
// - City zoom (city_share 1): a single bright trace (~3 px) with a halo; a node is a glow disc
//   with its tier ring.
// - Raid / transit (city_share 0): a 3-trace bus with vias at the bends and packets on the
//   flowing links; the node disc grows to a full socket.
// - Border / not-yet links (FLAG_DASHED) are dashed. Sizes are screen px (bu_per_px).
// Drawn on the ground render layer, so it shows under see-through buildings; the x-ray
// variant (city_network_xray.gdshader, depth test inverted) draws it where buildings hide it.

uniform sampler2D nodes_tex : filter_nearest;
uniform int node_count = 0;
uniform sampler2D segs_tex : filter_nearest;
uniform int seg_count = 0;
uniform float bu_per_px = 0.25;
uniform float city_share = 1.0;
uniform float trace_px = 3.0;
uniform float halo_px = 12.0;
uniform float node_px = 13.0;
uniform float ring_px = 3.0;
uniform float bus_gap_px = 4.0;
uniform float packet_speed = 24.0;
uniform float packet_gap = 30.0;
uniform vec2 dash_bu = vec2(4.0, 3.0);
uniform float gain = 1.6;
uniform float halo = 0.35;
uniform float strength = 1.0;
uniform float time_scale = 1.0;
uniform vec3 keyline = vec3(0.02, 0.02, 0.05);

varying vec3 v_world;

void vertex() {
	v_world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

float line_px(float d_px, float half_px) {
	return 1.0 - smoothstep(half_px - 0.75, half_px + 0.75, d_px);
}

void over(inout vec3 c, inout float a, vec3 src, float sa) {
	sa = clamp(sa, 0.0, 1.0);
	c = src * sa + c * (1.0 - sa);
	a = sa + a * (1.0 - sa);
}

void fragment() {
	vec2 p = v_world.xz;
	float t = TIME * time_scale;
	float px = max(bu_per_px, 0.0001);
	vec3 col = vec3(0.0);
	float al = 0.0;
	float mgmt = 1.0 - clamp(city_share, 0.0, 1.0);
	// Links.
	for (int k = 0; k < seg_count; k++) {
		vec4 s0 = texelFetch(segs_tex, ivec2(k, 0), 0);
		vec4 s1 = texelFetch(segs_tex, ivec2(k, 1), 0);
		vec4 s2 = texelFetch(segs_tex, ivec2(k, 2), 0);
		vec2 a = s0.xy;
		vec2 b = s0.zw;
		vec2 ab = b - a;
		float l2 = max(dot(ab, ab), 1e-6);
		float h = clamp(dot(p - a, ab) / l2, 0.0, 1.0);
		float d = length(p - a - ab * h) / px;
		float reach = halo_px + trace_px * 4.0 + bus_gap_px * 2.0;
		if (d > reach) {
			continue;
		}
		int flags = int(s1.a + 0.5);
		float u = s2.x + h * sqrt(l2);
		float w = trace_px * max(s2.z, 0.6) * 0.5;
		// The dark keyline under the trace, then the halo.
		over(col, al, keyline, line_px(d, w + 2.0 + mgmt * bus_gap_px) * 0.7);
		over(col, al, s1.rgb, exp(-pow(d / halo_px, 2.0)) * halo);
		float dash = 1.0;
		if ((flags & 1) != 0) {
			float period = dash_bu.x + dash_bu.y;
			dash = step(mod(u - ((flags & 2) != 0 ? t * packet_speed * 0.25 : 0.0), period), dash_bu.x);
		}
		float core = line_px(d, w) * (1.0 - mgmt);
		// The bus: three thinner traces at management zooms.
		float bus = max(line_px(abs(d - bus_gap_px), w * 0.6), max(line_px(d, w * 0.6), 0.0)) * mgmt;
		over(col, al, s1.rgb, max(core, bus) * dash);
		// Vias at segment ends (the bends) and packets along flowing links (management).
		if (mgmt > 0.0) {
			float via_d = min(length(p - a), length(p - b)) / px;
			over(col, al, s1.rgb, line_px(via_d, w + bus_gap_px) * mgmt);
			if ((flags & 2) != 0 && (flags & 1) == 0) {
				float ph = mod(u - t * packet_speed, packet_gap);
				float pk = line_px(abs(ph - packet_gap * 0.5) / px, trace_px * 1.5) * line_px(d, w * 1.5);
				over(col, al, vec3(1.0), pk * mgmt);
			}
		}
	}
	// Nodes: a glow disc, the tier ring, a full socket at management zooms.
	for (int k = 0; k < node_count; k++) {
		vec4 n0 = texelFetch(nodes_tex, ivec2(k, 0), 0);
		vec4 n1 = texelFetch(nodes_tex, ivec2(k, 1), 0);
		float d = length(p - n0.xy) / px;
		float r = node_px * n0.z * (1.0 + mgmt * 0.7);
		if (d > r + halo_px * 2.0) {
			continue;
		}
		over(col, al, n1.rgb, exp(-pow(d / (r + halo_px), 2.0)) * halo * 1.6);
		over(col, al, keyline, line_px(d, r) * 0.85);
		over(col, al, n1.rgb * 0.45, line_px(d, r - ring_px) * (0.35 + 0.3 * mgmt));
		over(col, al, n1.rgb, line_px(abs(d - r + ring_px * 0.5), ring_px * 0.5));
		// Tier: an inner ring per tier step (T1 one, T3 three).
		for (int q = 1; q <= 3; q++) {
			if (float(q) > n1.a) {
				break;
			}
			float rq = r - ring_px * (1.0 + 1.6 * float(q));
			over(col, al, n1.rgb, line_px(abs(d - rq), 0.6) * 0.8);
		}
	}
	// `over` keeps premultiplied colour; the blend wants it straight.
	ALBEDO = (al > 0.0001 ? col / al : vec3(0.0)) * gain;
	ALPHA = al * strength;
}
