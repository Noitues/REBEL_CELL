shader_type canvas_item;
// ART-11 4D: a rubber stamp's uneven ink on corp paper (ART_BIBLE v2 §1.2 "Anton stamps
// (CLASSIFIED, CASE CLOSED, PROCESSED)"; round 21 dossier21.py `stamp`): the ink's coverage
// breaks up in blotches and fine grain. Static (no TIME), so nothing changes under reduce
// effects. Decoration only: the hash is no game RNG.

uniform float seed = 1.0;
// The least and most ink a spot keeps, and the grain's cell (px).
uniform float ink_min = 0.35;
uniform float ink_max = 1.0;
uniform float grain = 2.0;

float h(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233)) + seed * 5.31) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h(i), h(i + vec2(1.0, 0.0)), f.x), mix(h(i + vec2(0.0, 1.0)), h(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	vec2 px = FRAGCOORD.xy;
	float blotch = vnoise(px / 18.0) * 0.6 + vnoise(px / 5.0) * 0.4;
	float fine = h(floor(px / grain));
	float ink = mix(ink_min, ink_max, smoothstep(0.25, 0.75, blotch)) * mix(0.75, 1.0, fine);
	COLOR.a *= clamp(ink, 0.0, 1.0);
}
