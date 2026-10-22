// LOOK-TOOLBOX module 13: the chrome (verb) sticker fill (shaders/chrome/vinyl_sticker.gdshader) rebuilt on
// rc_vinyl.gdshaderinc: marker colours per vertex, gradient + rest gloss + white sweep, glitch bands, the x + y band.
// Same uniforms; the stale colour defaults are replaced by the real stock values. Lab only.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_vinyl.gdshaderinc"

uniform vec4 top_color : source_color = vec4(1.0, 0.376, 0.675, 1.0);
uniform vec4 bottom_color : source_color = vec4(0.871, 0.071, 0.439, 1.0);
uniform vec4 white_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 glitch_a : source_color = vec4(1.0, 0.239, 0.659, 1.0);
uniform vec4 glitch_b : source_color = vec4(0.588, 1.0, 0.275, 1.0);
uniform float fill_top = 0.0;
uniform float fill_bottom = 40.0;
uniform float gloss = 0.22;
uniform float sweep = -10000.0;
uniform float sweep_width = 14.0;
uniform float grey = 0.0;
uniform float rainbow : hint_range(0.0, 1.0) = 0.0;
uniform float scan_period = 5.0;
uniform float band_h = 10.0;

varying vec2 v_local;
varying float v_kind;
varying float v_band;
varying float v_bright;

void vertex() {
	v_local = VERTEX;
	float kind;
	float bright;
	float band;
	rcv_chrome_marker(COLOR, kind, bright, band);
	v_kind = kind;
	v_bright = bright;
	v_band = band;
}

void fragment() {
	vec4 c = COLOR;
	if (v_kind > 0.5) {
		vec3 rgb;
		if (v_kind < 1.5) {
			rgb = rcv_chrome_marker_fill(v_local, fill_top, fill_bottom, top_color.rgb, bottom_color.rgb, gloss, sweep, sweep_width, rc_live());
		} else {
			if (!rcv_chrome_glitch_keep(v_local, fill_top, v_band, band_h)) {
				discard;
			}
			rgb = rcv_chrome_glitch(v_local, fill_top, scan_period, white_color.rgb, glitch_a.rgb, glitch_b.rgb);
		}
		c = vec4(rgb * v_bright, c.a);
	}
	if (rainbow > 0.0 && sweep > -1000.0) {
		float dd = rcv_chrome_band_dd(v_local, sweep, sweep_width);
		c.rgb = rcv_band_mix(c.rgb, rcv_foil(dd), rcv_band_w(dd), rainbow, c.a);
	}
	c.rgb = rcv_grey(c.rgb, grey);
	COLOR = c;
}
