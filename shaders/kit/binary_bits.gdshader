// REBEL_CELL material kit (ART-1 1B): binary bits, the particle process shader (ART_BIBLE
// v2 §1.2 "Binary bits", §6.3 "Bits"). Stock attractors are 3D, so each bit is lerped along
// a quadratic Bezier from its source cell to the target; around a wheel the control point
// sits on the rim-side bisector at 1.5 x R_out, so bits go round the rim, never across the
// face. Every number per bit (start, control, spawn delay, flight time, flip phase) is
// computed by the view (BinaryBits / BitsPath) and handed in: the view knows each bit's
// arrival time without reading particles back. The emitter's own clock comes in `clock`.
// Reduce effects: the view emits no bits at all (end states at once); the include keeps
// the one control and freezes the tumble.
shader_type particles;
#include "res://shaders/lib/rc_common.gdshaderinc"

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
uniform float flip_seconds = 0.06;
uniform float bit_scale = 1.0;
// Frames in the atlas: 0, 1, +, bit-rot; the flips use the first two.
uniform float frames = 4.0;

vec2 bezier(vec2 a, vec2 b, vec2 c, float t) {
	float u = 1.0 - t;
	return u * u * a + 2.0 * u * t * b + t * t * c;
}

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
		// ease in: the bits are sucked along the curve (slow, then fast)
		float e = t * t * (3.0 - 2.0 * t) * 0.35 + t * t * 0.65;
		vec2 pos = bezier(s.xy, k.xy, target, e);
		bool shown = age >= 0.0 && t < 1.0;
		float spin = rc_time(clock) * k.w + k.z * 6.28;
		float sc = bit_scale * (shown ? mix(1.0, 0.55, t) : 0.0);
		TRANSFORM[0].xy = vec2(cos(spin), sin(spin)) * sc;
		TRANSFORM[1].xy = vec2(-sin(spin), cos(spin)) * sc;
		TRANSFORM[3].xy = pos;
		float hot = clamp(age / max(hot_seconds, 0.001), 0.0, 1.0);
		COLOR = vec4(mix(vec3(1.0), color.rgb, hot), shown ? 1.0 : 0.0);
		float flip = mod(floor(max(age, 0.0) / flip_seconds + k.z * 7.0), 2.0);
		CUSTOM.z = (flip + 0.5) / frames;
	}
}
