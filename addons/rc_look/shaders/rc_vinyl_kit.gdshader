// LOOK-TOOLBOX module 13: the kit vinyl sticker (shaders/kit/vinyl_sticker.gdshader) rebuilt on rc_vinyl.gdshaderinc.
// Same uniforms, same defaults except shadow_color (the stale default is now VINYL_EXTRUDE, which the builder always set),
// same pixels. Drawn over the sticker's baked art; see rc_vinyl.gdshaderinc. Lab only: no view uses it yet.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_vinyl.gdshaderinc"

uniform sampler2D art_tex : filter_linear;
uniform vec4 body_rect = vec4(0.0, 0.0, 100.0, 100.0);
uniform float gloss_k : hint_range(0.0, 1.0) = 0.22;
uniform float gloss_pos = 0.32;
uniform float gloss_angle_deg = 28.0;
uniform float glossy : hint_range(0.0, 1.0) = 1.0;
uniform float rim : hint_range(0.0, 2.0) = 0.8;
uniform float fold : hint_range(0.0, 1.0) = 0.0;
uniform int corner = 1;
uniform vec4 backing_color : source_color = vec4(0.878, 0.867, 0.839, 1.0);
uniform vec4 shadow_color : source_color = vec4(0.035, 0.031, 0.047, 1.0);
uniform float shadow_k : hint_range(0.0, 1.0) = 1.0;
uniform float lift : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
uniform float dissolve_cell = 4.0;
uniform float grey : hint_range(0.0, 1.0) = 0.0;
uniform float rainbow : hint_range(0.0, 1.0) = 0.0;
uniform float band_t = -1.0;
uniform float band_width = 0.22;
uniform float band_alpha = 0.55;
uniform float band_deg = 45.0;
uniform float peel_back : hint_range(0.0, 1.0) = 0.0;
uniform float peel_px = 34.0;
uniform float opacity : hint_range(0.0, 1.0) = 1.0;

void fragment() {
	vec2 tps = TEXTURE_PIXEL_SIZE;
	vec2 px = UV / tps;
	RcvFold f = rcv_fold_frame(body_rect, corner, fold, peel_back, peel_px);
	vec4 base = rcv_art(art_tex, px, tps);
	float s = dot(px - f.P, f.u);
	if (f.on && s < 0.0) {
		base = vec4(0.0);
	}
	vec3 rgb = base.rgb;
	float a = base.a;
	if (a > 0.0) {
		rgb = rcv_kit_rim(rgb, a, art_tex, px, tps, rim, glossy);
		rgb = rcv_kit_gloss(rgb, px, body_rect, gloss_k, gloss_pos, gloss_angle_deg, glossy);
		if (rainbow > 0.0 && band_t >= 0.0) {
			float dd = rcv_kit_band_dd(px, body_rect, band_t, band_width, band_deg);
			rgb = rcv_band_mix(rgb, rcv_foil(dd), rcv_band_w(dd), band_alpha, 1.0);
		}
	}
	rcv_kit_flap(art_tex, px, tps, f, s, backing_color.rgb, peel_back, rgb, a);
	rcv_kit_dissolve(px, body_rect, dissolve, dissolve_cell, rgb, a);
	rgb = rcv_grey(rgb, grey);
	float shadow = rcv_kit_shadow(art_tex, px, tps, f, lift, shadow_k, dissolve);
	COLOR = rcv_kit_composite(rgb, a, shadow_color.rgb, shadow, opacity, COLOR.a);
}
