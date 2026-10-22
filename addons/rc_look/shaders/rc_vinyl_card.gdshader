// LOOK-TOOLBOX module 13: the played-card stand-in (shaders/fx/card_sticker_fx.gdshader) rebuilt on
// rc_vinyl.gdshaderinc: the scan-front dissolve and the diagonal white gloss. Lab only.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_vinyl.gdshaderinc"

uniform vec2 card_size = vec2(112.0, 148.0);
uniform float scan_y : hint_range(0.0, 1.0) = 0.0;
uniform float scan_band : hint_range(0.0, 0.2) = 0.04;
uniform float edge_share : hint_range(0.0, 0.3) = 0.1;
uniform float gloss_t = -1.0;
uniform float gloss_width : hint_range(0.0, 1.0) = 0.18;
uniform float gloss_alpha : hint_range(0.0, 1.0) = 0.55;
uniform vec4 front_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);

varying vec2 local_pos;

void vertex() {
	local_pos = VERTEX;
}

void fragment() {
	vec2 uv = local_pos / max(card_size, vec2(1.0));
	float front = rcv_card_front(scan_y, edge_share);
	if (scan_y > 0.0 && uv.y < front) {
		discard;
	}
	vec4 c = COLOR;
	if (scan_y > 0.0 && uv.y < front + scan_band) {
		c.rgb = rcv_card_scan_line(c.rgb, front_color.rgb);
	}
	if (gloss_t >= 0.0) {
		c.rgb = rcv_card_gloss(c.rgb, uv, gloss_t, gloss_width, gloss_alpha, rc_live());
	}
	COLOR = c;
}
