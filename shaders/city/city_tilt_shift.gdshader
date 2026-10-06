// Parity fix TITLE-01 (concept round 33 `title_screen.png`; `title.py` backdrop(), art-concepts-r43
// dcfdf74): the 3D city behind a menu, tilt-shifted and darkened. A ColorRect over the city reads the
// screen (the city drawn just before it) and mixes a soft copy (glass_blur's two-ring kernel read from
// a matched mip) with the sharp one by the focus band, then darkens it: the menu side (left), the foot
// and a vignette, times a gain. The numbers come from CityBackdropLook (BlurredCityBackdrop sets them);
// CityBackdropLook.focus_at / field_at are this shader's maths in GDScript (the legibility test reads
// them). Static: nothing here animates (no TIME); reduce effects leaves it as it is.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;
// The soft copy's Gaussian sigma (px of this view).
uniform float sigma_px = 5.0;
uniform float focus_centre = 0.56;
uniform float focus_half = 0.36;
uniform float focus_power = 0.8;
uniform float side_dark = 0.62;
uniform float side_reach = 0.46875;
uniform float side_power = 1.4;
uniform float foot_dark = 0.35;
uniform float foot_from = 0.82;
uniform float vignette = 0.35;
uniform vec2 vignette_centre = vec2(0.6, 0.5);
uniform vec2 vignette_scale = vec2(1.3, 1.1);
uniform float gain = 0.86;
// TITLE-01b: the backdrop's own grade (CityBackdropLook.grade_*; the city's shared grade is
// untouched): col * grade_gain + grade_lift * (1 + haze_out_of_focus * (1 - band)), before the
// darkening, after a saturation step (mix from the Rec. 709 luma). Plain vec3 (no source_color),
// so CityBackdropLook.shown is the same maths.
const vec3 LUMA = vec3(0.2126, 0.7152, 0.0722);
uniform float grade_saturation = 1.0;
uniform vec3 grade_gain = vec3(1.0);
uniform vec3 grade_lift = vec3(0.0);
uniform float haze_out_of_focus = 0.0;

// glass_blur's kernel: a centre tap and two rings of six (half and full radius); the ring's
// radius is two sigmas, so the soft copy spreads like a Gaussian of `sigma_px`.
const float RING_PER_SIGMA = 2.0;
const float W_CENTRE = 0.16;
const float W_INNER = 0.09;
const float W_OUTER = 0.05;

vec3 soft_at(vec2 uv, vec2 px) {
	float r = sigma_px * RING_PER_SIGMA;
	vec2 step_uv = px * r;
	float lod = log2(max(r * 0.5, 1.0));
	vec3 acc = textureLod(screen_texture, uv, lod).rgb * W_CENTRE;
	for (int k = 0; k < 6; k++) {
		float a = TAU * float(k) / 6.0;
		acc += textureLod(screen_texture, uv + vec2(cos(a), sin(a)) * step_uv * 0.5, lod).rgb * W_INNER;
		float a2 = a + PI / 6.0;
		acc += textureLod(screen_texture, uv + vec2(cos(a2), sin(a2)) * step_uv, lod).rgb * W_OUTER;
	}
	return acc;
}

void fragment() {
	vec2 uv = UV;
	vec3 sharp = textureLod(screen_texture, SCREEN_UV, 0.0).rgb;
	vec3 soft = soft_at(SCREEN_UV, SCREEN_PIXEL_SIZE);
	float band = pow(clamp(1.0 - abs(uv.y - focus_centre) / max(focus_half, 0.0001), 0.0, 1.0), focus_power);
	vec3 col = mix(soft, sharp, band);
	col = mix(vec3(dot(col, LUMA)), col, grade_saturation);
	col = col * grade_gain + grade_lift * (1.0 + haze_out_of_focus * (1.0 - band));
	float side = pow(clamp(1.0 - uv.x / max(side_reach, 0.0001), 0.0, 1.0), side_power);
	float foot = clamp((uv.y - foot_from) / max(1.0 - foot_from, 0.0001), 0.0, 1.0);
	float dark = 1.0 - side_dark * side - foot_dark * foot;
	vec2 d = (uv - vignette_centre) * vignette_scale;
	float vig = 1.0 - vignette * dot(d, d);
	COLOR = vec4(col * max(dark * vig * gain, 0.0), 1.0);
}
