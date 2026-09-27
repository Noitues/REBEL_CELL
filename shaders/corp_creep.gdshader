shader_type canvas_item;
// Heat threshold (GDD 9.4, Animation pass ANIM-5 4.12): the corporate wireframe creeps in
// over the zine layer from the screen's edges and recedes (`reach` tweens 0 -> peak -> 0,
// so it pulses and never stays on). Iso lattice lines in the corporation's colour, strong
// at the edges and fading to nothing `reach` (a share of the screen's half-height) in.

uniform vec4 tint : source_color = vec4(0.0, 0.94, 1.0, 1.0);
uniform float reach = 0.0;
uniform vec2 tile = vec2(34.0, 17.0);
uniform float strength = 0.55;

void fragment() {
	vec2 size = 1.0 / SCREEN_PIXEL_SIZE;
	vec2 px = UV * size;
	float edge = min(min(px.x, size.x - px.x), min(px.y, size.y - px.y)) / (size.y * 0.5);
	float mask = reach > 0.0 ? 1.0 - smoothstep(0.0, reach, edge) : 0.0;
	float gx = abs(fract((px.x / tile.x + px.y / tile.y) / 3.0) - 0.5);
	float gy = abs(fract((px.x / tile.x - px.y / tile.y) / 3.0) - 0.5);
	float line = smoothstep(0.44, 0.5, max(gx, gy));
	COLOR = vec4(tint.rgb, (line * 0.85 + 0.12) * mask * strength);
}
