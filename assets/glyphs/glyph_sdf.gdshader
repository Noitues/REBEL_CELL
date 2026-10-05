// ART-1 1C: draws one cell of the glyph atlas (ART_BIBLE 3.5, 6.2): a flat fill at the
// field's 0.5 edge and a dark rounded outline, both anti-aliased from the field's screen
// derivative (smoothstep 0.5 +/- aa), so one 128 px cell serves 16-64 px and text scale 2.0.
// Colours come from Palette tokens (GLYPH_FILL / GLYPH_INK) through GlyphIcon; the node's
// modulate multiplies the result. Geometry comes from content/config/glyph_table.tres.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec4 fill_color : source_color = vec4(1.0);
uniform vec4 outline_color : source_color = vec4(0.047, 0.039, 0.086, 1.0);
// Outline width as a fraction of the glyph box (0 = no outline).
uniform float outline_width = 0.075;
// The glyph box and the field's range, in atlas pixels (glyph_table.tres box_px / spread_px).
uniform float box_px = 96.0;
uniform float spread_px = 16.0;

varying vec4 modulate;

void vertex() {
	modulate = COLOR;
}

void fragment() {
	float v = texture(TEXTURE, UV).r;
	float aa = max(fwidth(v) * 0.75, 0.0005);
	float fill = smoothstep(0.5 - aa, 0.5 + aa, v);
	float edge = 0.5 - outline_width * box_px / (2.0 * spread_px);
	float outer = outline_width > 0.0 ? smoothstep(edge - aa, edge + aa, v) : fill;
	vec4 c = mix(outline_color, fill_color, outline_width > 0.0 ? fill : 1.0);
	COLOR = vec4(c.rgb, c.a * outer) * modulate;
}
