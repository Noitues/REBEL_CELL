// ART-10 4C: the vinyl sticker word (ART_BIBLE v2 1.2, 4.13; round 33 ui_kit / title_screen).
// VinylSticker draws the die-cut, ink keyline and extrude as plain colours; the lettering's
// fill is drawn in a marker colour this shader recognises per vertex and paints:
//   magenta (r = b, g = 0)        -> the vertical fill gradient + rest gloss + hover sweep;
//   green   (r = 0, b = band / 8) -> the CORRUPTED glitch fill (white, thin pink / green scan
//                                    lines); band 1..8 keeps only that horizontal band of the
//                                    letters (the burst shifts bands sideways), 0 the whole word.
// The marker's brightness (r for magenta, g for green) carries any modulate dimming.
// `grey` turns everything grey (disabled, 80 %). Reduce effects: the sweep never shows.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec4 top_color : source_color = vec4(1.0, 0.54, 0.83, 1.0);
uniform vec4 bottom_color : source_color = vec4(0.88, 0.08, 0.5, 1.0);
uniform vec4 white_color : source_color = vec4(0.98, 0.98, 0.96, 1.0);
uniform vec4 glitch_a : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform vec4 glitch_b : source_color = vec4(0.24, 1.0, 0.55, 1.0);
// Local y of the lettering's top and bottom (the gradient's ends).
uniform float fill_top = 0.0;
uniform float fill_bottom = 40.0;
// Rest gloss (0.22, the bible's value): the top of the fill lightens by this share.
uniform float gloss = 0.22;
// Hover sweep: the band's centre (local x at the lettering's top) and half width; off < -1e3.
uniform float sweep = -10000.0;
uniform float sweep_width = 14.0;
uniform float grey = 0.0;
// Focus: the sweep band is holo-foil colours over the sticker (any pixel with alpha), not white.
uniform float rainbow : hint_range(0.0, 1.0) = 0.0;
// Glitch fill: scan line period and the height of one burst band (px).
uniform float scan_period = 5.0;
uniform float band_h = 10.0;

varying vec2 v_local;
varying float v_kind;
varying float v_band;
varying float v_bright;

void vertex() {
	v_local = VERTEX;
	v_kind = 0.0;
	v_band = 0.0;
	v_bright = 1.0;
	float hi = max(COLOR.r, max(COLOR.g, COLOR.b));
	if (hi > 0.02) {
		if (COLOR.g < 0.01 * hi && abs(COLOR.r - COLOR.b) < 0.02 * hi) {
			v_kind = 1.0;
			v_bright = COLOR.r;
		} else if (COLOR.r < 0.01 * hi && COLOR.g >= COLOR.b) {
			v_kind = 2.0;
			v_bright = COLOR.g;
			v_band = floor(COLOR.b / COLOR.g * 8.0 + 0.5);
		}
	}
}

void fragment() {
	vec4 c = COLOR;
	if (v_kind > 0.5) {
		float t = clamp((v_local.y - fill_top) / max(1.0, fill_bottom - fill_top), 0.0, 1.0);
		vec3 rgb;
		if (v_kind < 1.5) {
			rgb = mix(top_color.rgb, bottom_color.rgb, t);
			rgb = mix(rgb, vec3(1.0), gloss * (1.0 - smoothstep(0.0, 0.42, t)));
			float d = abs((v_local.x - sweep) + (v_local.y - fill_top) * 0.45);
			rgb = mix(rgb, vec3(1.0), 0.6 * rc_live() * (1.0 - smoothstep(0.0, sweep_width, d)));
		} else {
			if (v_band > 0.5) {
				float y0 = fill_top + (v_band - 1.0) * band_h;
				if (v_local.y < y0 || v_local.y >= y0 + band_h) {
					discard;
				}
			}
			rgb = white_color.rgb;
			float row = floor((v_local.y - fill_top) / scan_period);
			if (mod(v_local.y - fill_top, scan_period) < 1.0) {
				rgb = mod(row, 2.0) < 0.5 ? glitch_a.rgb : glitch_b.rgb;
			}
		}
		c = vec4(rgb * v_bright, c.a);
	}
	if (rainbow > 0.0 && sweep > -1000.0) {
		// ONE narrow band at 45 degrees (x + y = sweep), `sweep_width` its half width across it, soft rainbow across the
		// band only, added over the vinyl and the letters (`rainbow` carries the band's alpha).
		float dd = (v_local.x + v_local.y - sweep) * 0.70710678 / max(sweep_width, 1.0);
		float band = 1.0 - smoothstep(0.0, 1.0, abs(dd));
		vec3 foil = clamp(pow(0.5 + 0.5 * cos(6.28318 * (vec3(0.0, 0.33, 0.67) + dd * 0.7)), vec3(0.55)) * 1.3, 0.0, 1.0);
		c.rgb = clamp(mix(c.rgb, foil, clamp(band * rainbow * 1.6, 0.0, 1.0) * c.a) + vec3(band * rainbow * 0.25 * c.a), 0.0, 1.0);
	}
	float g = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	c.rgb = mix(c.rgb, vec3(g), grey);
	COLOR = c;
}
