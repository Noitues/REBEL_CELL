// Terminal glass (STYLE_GUIDE 5-6): faint scanlines and flicker on terminal panels, the
// HUD and log strips only; paper, Polaroids and stamps never get it. Every effect is a
// uniform so reduce-effects can zero it.
shader_type canvas_item;
// Reduce effects (rc_common): the flicker stops; the static scanlines stay.
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float scan_strength : hint_range(0.0, 1.0) = 0.12;
uniform float flicker : hint_range(0.0, 0.1) = 0.01;

void fragment() {
	vec4 c = COLOR * texture(TEXTURE, UV);
	float line = step(0.5, fract(FRAGCOORD.y / 3.0));
	c.rgb *= 1.0 - scan_strength * line;
	c.rgb *= 1.0 - flicker * rc_live() * (0.5 + 0.5 * sin(rc_time(TIME) * 43.0));
	COLOR = c;
}
