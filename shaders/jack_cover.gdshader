shader_type canvas_item;
// Jack in / jack out (Animation pass ANIM-5, handoff 4.1): the cover between the HQ and the
// net. As `progress` runs 0 -> 1 the screen dissolves cell by cell, from the deck CRT
// (`focus`) outward, into the wireframe city (the net's iso lattice on night blue), with
// scanlines rolling down it. At 1 it is opaque: the scene changes under it, so no frame
// shows both scenes. Cell order is a hash of the cell (decoration only, no RNG).

uniform float progress = 0.0;
uniform vec4 base : source_color = vec4(0.02, 0.03, 0.07, 1.0);
uniform vec4 lattice : source_color = vec4(0.36, 0.88, 1.0, 1.0);
// Dissolve cell (px), the screen size (px) and the CRT point it spreads from (px).
uniform float cell = 12.0;
uniform vec2 screen = vec2(1280.0, 720.0);
uniform vec2 focus = vec2(640.0, 360.0);
// The iso lattice's tile (px) and the scanlines' phase (0..1 per roll) and strength.
uniform vec2 tile = vec2(34.0, 17.0);
uniform float roll = 0.0;
uniform float scan = 0.35;
// Share of a cell's threshold from its distance to the focus (the rest is its hash).
uniform float spread = 0.6;

float h(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec2 px = UV * screen;
	vec2 c = floor(px / cell);
	float d = length((c + 0.5) * cell - focus) / length(screen);
	float thr = d * spread + h(c) * (1.0 - spread);
	float a = progress > 0.0 ? step(thr, progress * 1.02) : 0.0;
	float gx = abs(fract((px.x / tile.x + px.y / tile.y) / 6.0) - 0.5);
	float gy = abs(fract((px.x / tile.x - px.y / tile.y) / 6.0) - 0.5);
	float line = smoothstep(0.46, 0.5, max(gx, gy));
	vec3 col = mix(base.rgb, lattice.rgb, line * 0.55);
	float lines = 0.5 + 0.5 * sin(px.y * 2.0944 + roll * 6.28318);
	col *= 1.0 - scan * lines;
	float band = 1.0 - smoothstep(0.0, 0.06, abs(fract(UV.y - roll) - 0.5));
	col += lattice.rgb * 0.18 * band;
	COLOR = vec4(col, a);
}
