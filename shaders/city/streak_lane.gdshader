// NA-22 (PIPELINE_SPEC 4.1 light streaks, 11.1 "Streaks", DERIVE_V2_REVIEW AD item 14): one traffic lane as an unshaded
// additive strip. The mesh is a strip along the lane: UV.x = BU along the lane (0 .. lane_len), UV.y = across (-1 .. 1).
// The lane's streaks come from the derive (dress `streak_lanes[].streaks` = u0, len, gap, bright), as an N x 1 float texture
// (u0, len, bright) read with texelFetch. Each streak slides by dir * speed * t and wraps on its own, modulo lane_len; the
// speed is quantized so lane_len = k * speed * loop_s, which makes the lane loop seamlessly on loop_s. The streak's brightness
// rises toward its head: floor + (1 - floor) * f^power.
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"

uniform sampler2D streaks : filter_nearest, repeat_disable;
uniform int streak_count = 0;
uniform float lane_len = 80.0;
uniform float speed = 20.0;
// +1: the streaks run toward +U (head lights), -1: toward -U (tails).
uniform float dir = 1.0;
uniform float loop_s = 4.0;
uniform float anim_t = 0.0;
uniform float anim_t_frozen = 0.0;
uniform vec3 lane_col = vec3(1.0, 0.85, 0.6);
uniform float emit = 2.5;
uniform float emission_multiplier = 1.0;
uniform float bright_floor = 0.15;
uniform float bright_pow = 1.6;
uniform float look_blend = 1.0;
const int MAX_STREAKS = 64;

void fragment() {
	float t = mod(nr_clock(anim_t, anim_t_frozen), loop_s);
	float u = UV.x;
	float acc = 0.0;
	for (int i = 0; i < MAX_STREAKS; i++) {
		if (i >= streak_count) {
			break;
		}
		vec4 s = texelFetch(streaks, ivec2(i, 0), 0);
		float d = mod(u - (s.x + dir * speed * t), lane_len);
		if (d < s.y) {
			float f = dir > 0.0 ? d / s.y : 1.0 - d / s.y;
			acc = max(acc, s.z * (bright_floor + (1.0 - bright_floor) * pow(f, bright_pow)));
		}
	}
	float across = 1.0 - smoothstep(0.5, 1.0, abs(UV.y));
	ALBEDO = lane_col * emit * acc * across * emission_multiplier * look_blend;
	ALPHA = 1.0;
}
