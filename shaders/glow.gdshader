// Wireframe glow for net geometry (STYLE_GUIDE 4): brightens and blooms a CanvasItem's
// own texture. Applied to the wheel/grid drawing layers via a SubViewport-free trick:
// the view draws its lines twice (wide + soft, thin + bright); this shader adds the
// additive tint so the layer reads as glowing. Optional; reduce-effects leaves it on
// because it neither flashes nor flickers.
shader_type canvas_item;
render_mode blend_add;

uniform float strength : hint_range(0.0, 2.0) = 0.6;

void fragment() {
	vec4 c = texture(TEXTURE, UV) * COLOR;
	COLOR = vec4(c.rgb * strength, c.a * strength);
}
