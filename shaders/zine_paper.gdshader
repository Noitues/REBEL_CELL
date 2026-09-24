// Zine paper: paper colour with halftone dots and faint fibre noise (STYLE_GUIDE 1).
// Static (no time), so it is unaffected by reduce-effects.
shader_type canvas_item;

uniform vec4 paper : source_color = vec4(0.949, 0.933, 0.894, 1.0);
uniform vec4 ink : source_color = vec4(0.067, 0.067, 0.067, 1.0);
uniform float halftone : hint_range(0.0, 1.0) = 0.12;
uniform float dot_scale = 90.0;
uniform float grain : hint_range(0.0, 1.0) = 0.05;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec2 cell = fract(UV * dot_scale) - 0.5;
	float dots = smoothstep(0.32, 0.28, length(cell)) * halftone;
	float g = (hash(floor(UV * 400.0)) - 0.5) * grain;
	vec3 col = mix(paper.rgb, ink.rgb, dots) + g;
	COLOR = vec4(col, paper.a) * COLOR;
}
