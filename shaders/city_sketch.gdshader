// Neon city pass (STYLE_GUIDE 1, "Neon city"): wobbles vertices a little so outlines
// read as hand-inked, breaks line alpha with grain, boosts saturation, and adds faint
// CRT scanlines. Static wobble (no time): lines never "boil". `scan_strength` and
// `flicker` go to 0 under reduce-effects.
shader_type canvas_item;

uniform float wobble = 1.6;
uniform float jitter = 0.5;
uniform float saturation = 1.6;
uniform float grain : hint_range(0.0, 1.0) = 0.12;
uniform float scan_strength : hint_range(0.0, 1.0) = 0.07;
uniform float flicker : hint_range(0.0, 0.1) = 0.0;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void vertex() {
	// Two octaves: a slow drift of the whole stroke and a fine hand tremor.
	vec2 q = VERTEX * 0.06;
	vec2 f = VERTEX * 0.23;
	VERTEX += (vec2(noise(q), noise(q + vec2(17.3, 5.1))) - 0.5) * 2.0 * wobble;
	VERTEX += (vec2(noise(f + vec2(3.7, 9.2)), noise(f + vec2(11.1, 2.3))) - 0.5) * 2.0 * jitter;
}

void fragment() {
	vec4 c = COLOR * texture(TEXTURE, UV);
	float g = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	c.rgb = clamp(mix(vec3(g), c.rgb, saturation), 0.0, 1.0);
	c.a *= 1.0 - grain * noise(FRAGCOORD.xy * 0.45);
	float line = step(0.5, fract(FRAGCOORD.y / 3.0));
	c.rgb *= 1.0 - scan_strength * line;
	c.rgb *= 1.0 - flicker * (0.5 + 0.5 * sin(TIME * 41.0));
	COLOR = c;
}
