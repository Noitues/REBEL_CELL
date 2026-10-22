// LOOK-TOOLBOX module 13: the fill of a vinyl sticker's lettering or face (shaders/kit/sticker_fill.gdshader) rebuilt
// on rc_vinyl.gdshaderinc. mode 0 vertical gradient, mode 1 holo foil (the hue drifts with rc_time). Lab only.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_vinyl.gdshaderinc"

uniform int mode = 0;
uniform vec4 fill_top : source_color = vec4(1.0, 0.376, 0.675, 1.0);
uniform vec4 fill_bottom : source_color = vec4(0.871, 0.071, 0.439, 1.0);
uniform float band_top = 0.0;
uniform float band_bottom = 100.0;
uniform float holo_drift = 0.0;
uniform float holo_seed = 11.0;
uniform float holo_sat : hint_range(0.0, 1.0) = 0.55;
uniform vec2 field_size = vec2(400.0, 160.0);

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

void fragment() {
	vec3 rgb;
	if (mode == 1) {
		rgb = rcv_holo_fill(local_px, field_size, holo_seed, rc_time(TIME) * holo_drift, holo_sat);
	} else {
		rgb = rcv_gradient_fill(local_px.y, band_top, band_bottom, fill_top.rgb, fill_bottom.rgb);
	}
	COLOR = vec4(rgb, COLOR.a);
}
