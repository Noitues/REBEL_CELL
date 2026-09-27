// The live pass over the baked neon city (H20): the sketch look (wobble, grain,
// saturation, wall textures) is already in the baked image, so this only adds the
// screen-space parts that must stay live: faint CRT scanlines and a gentle flicker.
// Both go to 0 under reduce-effects (NeonCity._apply_effects).
shader_type canvas_item;

uniform float scan_strength : hint_range(0.0, 1.0) = 0.07;
uniform float flicker : hint_range(0.0, 0.1) = 0.0;

void fragment() {
	// COLOR already holds the texture's colour (Godot 4 canvas fragment input): sampling
	// TEXTURE again would square it and crush the city's mid-tones.
	vec4 c = COLOR;
	float line = step(0.5, fract(FRAGCOORD.y / 3.0));
	c.rgb *= 1.0 - scan_strength * line;
	c.rgb *= 1.0 - flicker * (0.5 + 0.5 * sin(TIME * 41.0));
	COLOR = c;
}
