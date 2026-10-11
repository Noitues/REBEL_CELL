shader_type canvas_item;
// M14 perf slice: the city map's crawling dashes and threat chevrons (CityMapOverlay's flow
// layer) as one still mesh (CityFlowMesh): every dash and chevron is laid once at phase 0 in its
// track's frame (VERTEX = along, across), and this shader slides it along its track by the
// track's phase, so the map no longer re-lays them on the CPU every frame. A track's row in
// `tracks`: (origin.xy, dir.xy), (length, period, base, flow), (kind, 0, 0, 0). UV = (row,
// anchor: the element's start along the track at phase 0). A dash (kind 0) is clipped at the
// track's end per pixel (the CPU's min(t + on, length)); a chevron (kind 1) is drawn whole
// while its anchor lies before the end, else not at all (the CPU's count of them).

uniform sampler2D tracks : filter_nearest, repeat_disable;
// The dashes' and the chevrons' phase (px; CityMapOverlay: fmod(travel, period)).
uniform float dash_phase = 0.0;
uniform float chevron_phase = 0.0;

varying float v_u;
varying float v_end;

void vertex() {
	int row = int(UV.x + 0.5);
	vec4 t0 = texelFetch(tracks, ivec2(0, row), 0);
	vec4 t1 = texelFetch(tracks, ivec2(1, row), 0);
	float kind = texelFetch(tracks, ivec2(2, row), 0).x;
	float phase = kind < 0.5 ? dash_phase : chevron_phase;
	float shift = mod(phase * t1.w + t1.z, t1.y);
	vec2 dir = t0.zw;
	vec2 side = vec2(dir.y, -dir.x);
	float along = VERTEX.x + shift;
	v_u = along;
	v_end = kind < 0.5 ? t1.x : 1e30;
	if (UV.y + shift >= t1.x) {
		VERTEX = t0.xy;
	} else {
		VERTEX = t0.xy + dir * along + side * VERTEX.y;
	}
}

void fragment() {
	if (v_u > v_end) {
		discard;
	}
}
