// W10 review-pack post filter (harness only, never in game code): greyscale or a
// deuteranopia simulation over the whole screen (ART_BIBLE §12 "Test every screen in
// greyscale"). mode 1 = grey (Rec. 709 luminance), 2 = deutan (Machado, Oliveira and
// Fernandes 2009, severity 1.0). Both work in linear light. The same maths lives in
// tools/visual_qa/filters.py for the Pillow path.
shader_type canvas_item;

uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform int mode = 0;

vec3 to_linear(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

vec3 to_srgb(vec3 c) {
	c = clamp(c, 0.0, 1.0);
	return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c));
}

void fragment() {
	vec3 lin = to_linear(texture(screen_tex, SCREEN_UV).rgb);
	vec3 outc = lin;
	if (mode == 1) {
		outc = vec3(dot(lin, vec3(0.2126, 0.7152, 0.0722)));
	} else if (mode == 2) {
		mat3 m = mat3(
			vec3(0.367322, 0.280085, -0.011820),
			vec3(0.860646, 0.672501, 0.042940),
			vec3(-0.227968, 0.047413, 0.968881));
		outc = m * lin;
	}
	COLOR = vec4(to_srgb(outc), 1.0);
}
