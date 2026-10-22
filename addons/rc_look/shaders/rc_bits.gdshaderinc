// LOOK-TOOLBOX module 16: binary bits. The math of shaders/kit/binary_bits.gdshader (the bit particle process shader,
// ART_BIBLE v2 §1.2 / §6.3) as helpers, each the exact form of the line it comes from, so the particle shader can move
// onto them with identical pixels (proven in the lab: bits_stage's probe renders both and reports the largest pixel
// difference). RcLookBits mirrors them in GDScript. The inputs per bit (start, control point, delay, flight, flip phase,
// spin speed) come from the view (RcLookBits.plan, the mirror of BitsPath.plan); nothing here is random.
//   - rcl_bits_eased(t): the slow-then-sucked-in ease (binary_bits.gdshader:50).
//   - rcl_bits_at(a, c, b, t): the quadratic Bezier a -> c -> b (:30).
//   - rcl_bits_scale(base, t, shown): the bit's size, shrinking to RCL_BITS_END_SCALE.
//   - rcl_bits_flip(age, flip_s, phase, frames): the atlas frame channel (CUSTOM.z): the 0 / 1 glyph flips every flip_s.
//   - rcl_bits_spin(clock, speed, phase): the tumble angle, a turn being RCL_BITS_TURN (6.28, not TAU: bit-exact with
//     today; a designer ruling, rcl_bits_spin_turn takes the turn so the lab can show TAU beside it).
//   - rcl_bits_color(hot_col, col, age, hot_s): white-hot (hot_col) for the first hot_s seconds, then the bit's colour,
//     through rc_sign's rcl_hot_to.
// Includes rc_common (rc_time freezes the tumble under reduce effects); a particles shader needs only:
//   #include "res://addons/rc_look/shaders/rc_bits.gdshaderinc"
#ifndef RC_BITS_INCLUDED
#define RC_BITS_INCLUDED
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_sign.gdshaderinc"

// The ease: a smoothstep share and a quadratic share (they sum to 1, so the ease ends at 1).
const float RCL_BITS_EASE_SMOOTH = 0.35;
const float RCL_BITS_EASE_QUAD = 0.65;
// A bit ends at this share of its size (it starts at 1).
const float RCL_BITS_END_SCALE = 0.55;
// A turn in the tumble: today's 6.28 (TAU is 6.2831853; a ruling).
const float RCL_BITS_TURN = 6.28;
// The flip phase spreads over this many flips, so bits do not all show the same glyph at once.
const float RCL_BITS_FLIP_SPREAD = 7.0;

float rcl_bits_eased(float t) {
	return t * t * (3.0 - 2.0 * t) * RCL_BITS_EASE_SMOOTH + t * t * RCL_BITS_EASE_QUAD;
}

vec2 rcl_bits_at(vec2 a, vec2 c, vec2 b, float t) {
	float u = 1.0 - t;
	return u * u * a + 2.0 * u * t * c + t * t * b;
}

float rcl_bits_scale(float base, float t, bool shown) {
	return base * (shown ? mix(1.0, RCL_BITS_END_SCALE, t) : 0.0);
}

float rcl_bits_flip(float age, float flip_s, float phase, float frames) {
	float flip = mod(floor(max(age, 0.0) / flip_s + phase * RCL_BITS_FLIP_SPREAD), 2.0);
	return (flip + 0.5) / frames;
}

float rcl_bits_spin_turn(float clock, float speed, float phase, float turn) {
	return rc_time(clock) * speed + phase * turn;
}

float rcl_bits_spin(float clock, float speed, float phase) {
	return rcl_bits_spin_turn(clock, speed, phase, RCL_BITS_TURN);
}

vec3 rcl_bits_color(vec3 hot_col, vec3 col, float age, float hot_s) {
	return rcl_hot_to(hot_col, col, clamp(age / max(hot_s, 0.001), 0.0, 1.0));
}
#endif
