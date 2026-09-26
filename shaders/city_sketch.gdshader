// Neon city pass (STYLE_GUIDE 1, "Neon city"): wobbles vertices a little so outlines
// read as hand-inked, breaks line alpha with grain, boosts saturation, and adds faint
// CRT scanlines. Static wobble (no time): lines never "boil". `scan_strength` and
// `flicker` go to 0 under reduce-effects.
shader_type canvas_item;

uniform float wobble = 0.0;
uniform float jitter = 0.0;
uniform float saturation = 1.6;
uniform float grain : hint_range(0.0, 1.0) = 0.12;
uniform float scan_strength : hint_range(0.0, 1.0) = 0.07;
uniform float flicker : hint_range(0.0, 0.1) = 0.0;
// Design option: wall texture on the dark grey fills only (not lines, windows or signs),
// anchored to the city so it pans with it. 0 none, 1 concrete grain, 2 matte stone,
// 3 brushed metal, 4 painted grain (slate, gentler
// saturation), 5 painted grain on tinted walls (full saturation).
uniform int wall_mode = 0;

varying vec2 world;

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
	world = VERTEX;
	vec2 q = VERTEX * 0.06;
	vec2 f = VERTEX * 0.23;
	VERTEX += (vec2(noise(q), noise(q + vec2(17.3, 5.1))) - 0.5) * 2.0 * wobble;
	VERTEX += (vec2(noise(f + vec2(3.7, 9.2)), noise(f + vec2(11.1, 2.3))) - 0.5) * 2.0 * jitter;
}

void fragment() {
	vec4 c = COLOR * texture(TEXTURE, UV);
	float g = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	if (wall_mode > 0) {
		float spread = max(c.r, max(c.g, c.b)) - min(c.r, min(c.g, c.b));
		float greyish = (1.0 - smoothstep(0.14, 0.24, spread)) * smoothstep(0.03, 0.07, g) * (1.0 - smoothstep(0.3, 0.45, g));
		if (wall_mode == 1) {
			float n = noise(world * 0.8) * 0.45 + noise(world * 2.6) * 0.35 + hash(floor(world * 1.3)) * 0.2;
			c.rgb *= 1.0 + greyish * (n - 0.5) * 1.8;
		} else if (wall_mode == 5) {
			// Tinted painted slate: the same brush grain on any dark wall tone, whatever
			// its hue (lines and windows are too bright or too saturated to be touched).
			float wall = (1.0 - smoothstep(0.3, 0.45, spread)) * smoothstep(0.03, 0.07, g) * (1.0 - smoothstep(0.3, 0.45, g));
			float n = (noise(world * 0.07) - 0.5) * 0.28 + (noise(world * 0.35) - 0.5) * 0.16 + (hash(floor(world * 1.4)) - 0.5) * 0.08;
			c.rgb *= 1.0 + wall * n;
		} else if (wall_mode == 4) {
			// Painted: soft brush blotches and a fine tooth, keeping the slate's colour.
			float n = (noise(world * 0.07) - 0.5) * 0.28 + (noise(world * 0.35) - 0.5) * 0.16 + (hash(floor(world * 1.4)) - 0.5) * 0.08;
			c.rgb *= 1.0 + greyish * n;
		} else {
			// Matte: take the blue out of the fill and darken it a touch.
			vec3 matte = vec3(g) * 0.9;
			float n;
			if (wall_mode == 2) {
				// Stone: broad blotches, a mid mottle, fine grit and the odd dark pit.
				n = (noise(world * 0.09) - 0.5) * 0.5 + (noise(world * 0.45) - 0.5) * 0.3 + (hash(floor(world * 1.6)) - 0.5) * 0.22;
				n -= step(0.95, hash(floor(world * 0.9))) * 0.35;
			} else {
				// Metal: long vertical brush streaks, finer streaks, a light speckle.
				n = (noise(vec2(world.x * 1.1, world.y * 0.035)) - 0.5) * 0.45 + (noise(vec2(world.x * 3.7, world.y * 0.08)) - 0.5) * 0.2;
				n += (hash(floor(world * 2.0)) - 0.5) * 0.08;
			}
			c.rgb = mix(c.rgb, matte * (1.0 + n), greyish);
		}
	}
	float sat = saturation;
	if (wall_mode == 4) {
		// Painted slate stays a cool grey: a gentler saturation boost on the walls.
		float spread2 = max(c.r, max(c.g, c.b)) - min(c.r, min(c.g, c.b));
		sat = mix(saturation, 1.3, 1.0 - smoothstep(0.1, 0.22, spread2));
	}
	c.rgb = clamp(mix(vec3(g), c.rgb, sat), 0.0, 1.0);
	c.a *= 1.0 - grain * noise(FRAGCOORD.xy * 0.45);
	float line = step(0.5, fract(FRAGCOORD.y / 3.0));
	c.rgb *= 1.0 - scan_strength * line;
	c.rgb *= 1.0 - flicker * (0.5 + 0.5 * sin(TIME * 41.0));
	COLOR = c;
}
