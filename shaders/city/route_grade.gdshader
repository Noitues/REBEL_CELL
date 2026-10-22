shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"
// NA-23: the hover power cut (PIPELINE_SPEC 9.4): one full-screen 2D grade over the street netrun's frame. `mask` is the hovered
// branch's room boxes (grown and blurred); outside it the picture drops to `cut_level` of its value and loses `cut_desat` of its
// colour, inside it the picture is brightened by `branch_boost`; `k` (0..1, the hover ease) fades the grade in and out.
// The overlay (stickers, pencil, the TARGET arrow) is drawn above this pass and is never dimmed.
uniform sampler2D mask : filter_linear, repeat_disable;
uniform float k = 0.0;
uniform float cut_level = 0.2;
uniform float cut_desat = 0.7;
uniform float branch_boost = 1.35;
uniform vec2 mask_texel = vec2(0.004, 0.007);
uniform float blur = 1.0;

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (k <= 0.0) {
		COLOR = c;
	} else {
		float m = 0.0;
		for (int i = -1; i <= 1; i++) {
			for (int j = -1; j <= 1; j++) {
				m += texture(mask, UV + vec2(float(i), float(j)) * mask_texel * blur).r;
			}
		}
		m /= 9.0;
		vec3 outside = mix(c.rgb, vec3(rcl_luma(c.rgb)), cut_desat) * cut_level;  // rc_look luma
		vec3 inside = c.rgb * branch_boost;
		vec3 g = mix(outside, inside, m);
		COLOR = vec4(mix(c.rgb, g, k), c.a);
	}
}
