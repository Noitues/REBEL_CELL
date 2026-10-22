// LOOK-TOOLBOX module 16: binary_bits.gdshader rebuilt on rc_bits.gdshaderinc, a drop-in for it (same uniforms, same
// pixels: the lab's probe renders both and reports the largest difference). Lab-only until the designer lifts the raid
// redesign pause and the call site (BinaryBits) moves onto it; adds two uniforms whose defaults are today's values:
// hot_color (the colour a bit starts in, white-hot) and spin_turn (a turn in the tumble, 6.28).
shader_type particles;
#include "res://addons/rc_look/shaders/rc_bits.gdshaderinc"

const int MAX_BITS = 64;

// xy = start, z = spawn delay (s), w = flight time (s)
uniform vec4 bit_start[64];
// xy = Bezier control point, z = flip phase, w = tumble speed (rad/s)
uniform vec4 bit_ctrl[64];
uniform int count = 0;
uniform vec2 target = vec2(0.0);
uniform float clock = 0.0;
uniform float hot_seconds = 0.08;
uniform vec4 color : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform vec3 hot_color = vec3(1.0);
uniform float flip_seconds = 0.06;
uniform float bit_scale = 1.0;
uniform float spin_turn = 6.28;
// Frames in the atlas: 0, 1, +, bit-rot; the flips use the first two.
uniform float frames = 4.0;

void start() {
	TRANSFORM = mat4(vec4(0.0), vec4(0.0), vec4(0.0, 0.0, 1.0, 0.0), vec4(0.0, 0.0, 0.0, 1.0));
	COLOR = vec4(0.0);
}

void process() {
	int i = int(INDEX);
	if (i >= count || i >= MAX_BITS) {
		COLOR = vec4(0.0);
		TRANSFORM[0].xy = vec2(0.0);
		TRANSFORM[1].xy = vec2(0.0);
	} else {
		vec4 s = bit_start[i];
		vec4 k = bit_ctrl[i];
		float age = clock - s.z;
		float t = clamp(age / max(s.w, 0.001), 0.0, 1.0);
		vec2 pos = rcl_bits_at(s.xy, k.xy, target, rcl_bits_eased(t));
		bool shown = age >= 0.0 && t < 1.0;
		float spin = rcl_bits_spin_turn(clock, k.w, k.z, spin_turn);
		float sc = rcl_bits_scale(bit_scale, t, shown);
		TRANSFORM[0].xy = vec2(cos(spin), sin(spin)) * sc;
		TRANSFORM[1].xy = vec2(-sin(spin), cos(spin)) * sc;
		TRANSFORM[3].xy = pos;
		COLOR = vec4(rcl_bits_color(hot_color, color.rgb, age, hot_seconds), shown ? 1.0 : 0.0);
		CUSTOM.z = rcl_bits_flip(age, flip_seconds, k.z, frames);
	}
}
