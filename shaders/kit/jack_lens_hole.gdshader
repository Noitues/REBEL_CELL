shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"
// NA-25b r3 (ART_BIBLE 4.6, the wheel lens): the hub core opening. The jack's wheel is drawn into a sub-viewport (the combat's own
// WheelView, enlarged until its hub core covers the screen); this cuts a hole out of it, centred on the hub, that grows until it
// clears the screen. The hole's rim is lit in the Cell's cyan so the opening reads as the hub's CRT disc being burnt through.
// All lengths are in canvas units (`canvas_size` is the screen's size in them), whatever the sub-viewport's pixel size.
uniform vec2 canvas_size = vec2(1280.0, 720.0);
uniform vec2 hole_center = vec2(0.0);
uniform float hole_r = 0.0;
uniform float rim_px = 6.0;
uniform vec4 rim_color : source_color = vec4(0.36, 0.86, 0.96, 1.0);
uniform float rim_gain = 1.4;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (hole_r <= 0.0) {
		COLOR = c;
	} else {
		float d = distance(UV * canvas_size, hole_center);
		float inside = smoothstep(hole_r - 1.0, hole_r + 1.0, d);
		float rim = (1.0 - smoothstep(0.0, rim_px, d - hole_r)) * step(hole_r, d);
		COLOR = vec4(c.rgb + rim_color.rgb * rim_gain * rim * c.a, c.a * inside);
	}
}
