// Heat pulse distortion (GDD 9.4): driven by `intensity`, which the FX layer tweens
// up on a threshold event and back to 0. Zero = no visible effect.
shader_type canvas_item;
render_mode blend_mix;

uniform sampler2D screen_texture : hint_screen_texture, filter_linear;
uniform float intensity : hint_range(0.0, 1.0) = 0.0;
uniform vec4 tint : source_color = vec4(0.24, 1.0, 0.545, 1.0);

void fragment() {
	vec2 uv = SCREEN_UV;
	float wave = sin(uv.y * 80.0 + TIME * 30.0) * 0.012 * intensity;
	float slice_jump = step(0.97, fract(sin(floor(uv.y * 40.0) * 12.9898 + TIME * 3.0) * 43758.5453)) * 0.03 * intensity;
	vec3 col = texture(screen_texture, uv + vec2(wave + slice_jump, 0.0)).rgb;
	col = mix(col, col * tint.rgb, intensity * 0.35);
	COLOR = vec4(col, 1.0);
}
