// REBEL_CELL colour-blind correction (ART_BIBLE §12, art pass W9): a full-screen
// DALTONIZE pass (a correction, not a simulation). It runs on the top canvas layer
// (ColorblindLayer, layer 127) only while Settings.colorblind_mode is not "off"; off means
// no layer at all, so no cost.
//
// Why a global pass: "remap corp and semantic hues" (§12) can't be a per-token swap,
// because Palette's colours are compile-time constants read everywhere. Daltonizing the
// final frame moves the information a player with a colour-vision deficiency can't see
// (the error between the image and its simulation) into channels they can see, on every
// screen at once. The bible's patterns and glyphs stay the primary cue; this is an aid.
//
// Maths (Fidaner, Lin and Ozguven 2005, the "daltonize" LMS method), in linear light:
//   lms = RGB2LMS * rgb;  sim = LMS2RGB * (DEFICIENCY[mode] * lms);
//   err = rgb - sim;      out = rgb + SHIFT[mode] * err
// The same maths lives in scripts/ui/fx/colorblind_layer.gd (`correct`) for the tests.
// mode 1 = deutan, 2 = protan, 3 = tritan; 0 passes the frame through.
// No animation, so reduce effects changes nothing here (rc_common is included for the
// shared conventions only).
shader_type canvas_item;

#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform int mode = 0;
// 0..1: how much of the correction is applied (1 = the full daltonize shift).
uniform float strength : hint_range(0.0, 1.0) = 1.0;

vec3 cb_to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

vec3 cb_to_srgb(vec3 c) {
	c = clamp(c, 0.0, 1.0);
	return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c));
}

// GLSL mat3 takes columns; each vec3 below is one column of the row-major matrix in the
// comment above it.
vec3 cb_simulate(vec3 rgb, int m) {
	// RGB -> LMS
	mat3 rgb2lms = mat3(
		vec3(17.8824, 3.45565, 0.0299566),
		vec3(43.5161, 27.1554, 0.184309),
		vec3(4.11935, 3.86714, 1.46709));
	// LMS -> RGB
	mat3 lms2rgb = mat3(
		vec3(0.0809444479, -0.0102485335, -0.000365296938),
		vec3(-0.130504409, 0.0540193266, -0.00412161469),
		vec3(0.116721066, -0.113614708, 0.693511405));
	mat3 d = mat3(1.0);
	if (m == 1) {
		// deuteranopia: M from L and S
		d = mat3(vec3(1.0, 0.494207, 0.0), vec3(0.0, 0.0, 0.0), vec3(0.0, 1.24827, 1.0));
	} else if (m == 2) {
		// protanopia: L from M and S
		d = mat3(vec3(0.0, 0.0, 0.0), vec3(2.02344, 1.0, 0.0), vec3(-2.52581, 0.0, 1.0));
	} else if (m == 3) {
		// tritanopia: S from L and M
		d = mat3(vec3(1.0, 0.0, -0.395913), vec3(0.0, 1.0, 0.801109), vec3(0.0, 0.0, 0.0));
	}
	return lms2rgb * (d * (rgb2lms * rgb));
}

vec3 cb_correct(vec3 rgb, int m) {
	vec3 err = rgb - cb_simulate(rgb, m);
	mat3 shift;
	if (m == 3) {
		// tritan: the lost blue-yellow error goes into red and green
		shift = mat3(vec3(1.0, 0.0, 0.0), vec3(0.0, 1.0, 0.0), vec3(0.7, 0.7, 0.0));
	} else {
		// deutan / protan: the lost red-green error goes into green and blue
		shift = mat3(vec3(0.0, 0.7, 0.7), vec3(0.0, 1.0, 0.0), vec3(0.0, 0.0, 1.0));
	}
	return rgb + shift * err;
}

void fragment() {
	vec4 src = texture(screen_tex, SCREEN_UV);
	vec3 lin = cb_to_linear(src.rgb);
	vec3 outc = lin;
	if (mode > 0) {
		outc = mix(lin, cb_correct(lin, mode), clamp(strength, 0.0, 1.0));
	}
	COLOR = vec4(cb_to_srgb(outc), 1.0);
}
