// CRT/net overlay: scanlines, flicker and chromatic aberration (STYLE_GUIDE 5-6).
// Every effect has a uniform so the reduce-effects setting can zero them.
shader_type canvas_item;
render_mode blend_mix;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear;
uniform float scanline_strength : hint_range(0.0, 1.0) = 0.12;
uniform float scanline_density = 360.0;
uniform float flicker_strength : hint_range(0.0, 1.0) = 0.04;
uniform float aberration : hint_range(0.0, 0.02) = 0.0012;
uniform float vignette : hint_range(0.0, 1.0) = 0.25;

void fragment() {
	vec2 uv = SCREEN_UV;
	vec3 col;
	col.r = texture(screen_texture, uv + vec2(aberration, 0.0)).r;
	col.g = texture(screen_texture, uv).g;
	col.b = texture(screen_texture, uv - vec2(aberration, 0.0)).b;
	float line = 0.5 + 0.5 * sin(uv.y * scanline_density * 3.14159);
	col *= 1.0 - scanline_strength * line;
	float flick = 1.0 - flicker_strength * (0.5 + 0.5 * sin(TIME * 47.0));
	col *= flick;
	float d = distance(uv, vec2(0.5));
	col *= 1.0 - vignette * smoothstep(0.45, 0.85, d);
	COLOR = vec4(col, 1.0);
}
