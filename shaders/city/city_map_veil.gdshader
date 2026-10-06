// S-MAPVIEW (designer ruling 2026-10-05): the map mode's veil. One full-screen quad drawn after
// the city's post pass and its ambient motion (sky lanes, searchlights, holo signs, pools: the
// additive layers draw after the post) and before the network decal (render priority between
// them): the whole city shows through at 1 - veil_alpha, its opacity lowered toward the night
// sky, while the network and the map's marks stay at full strength on top.
shader_type spatial;
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, depth_test_disabled, shadows_disabled, fog_disabled;

uniform vec3 veil_color : source_color = vec3(0.075, 0.06, 0.13);
uniform float veil_alpha = 0.32;

void vertex() {
	POSITION = vec4(VERTEX.xy, 1.0, 1.0);
}

void fragment() {
	ALBEDO = veil_color;
	ALPHA = veil_alpha;
}
