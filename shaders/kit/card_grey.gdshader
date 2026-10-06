// B2 (integration review D15, round 41 combat_typical_v4): an unaffordable hand card shows its own
// face in greyscale, a little darkened; its NEED tag draws in colour over it (ZineCard's NeedTag
// layer has no material). COLOR already holds the texture (and the MSDF text's coverage), so only
// its colour changes. Static: nothing animates, nothing for reduce effects to stop.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

// Share of the mix toward luminance and how much darker the grey face is.
uniform float grey : hint_range(0.0, 1.0) = 1.0;
uniform float dim : hint_range(0.0, 1.0) = 0.18;

void fragment() {
	float l = dot(COLOR.rgb, vec3(0.2126, 0.7152, 0.0722));
	COLOR.rgb = mix(COLOR.rgb, vec3(l), grey) * (1.0 - dim);
}
