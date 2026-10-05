// ART-5 5c: a car tier on the baked lane paths (ART_BIBLE §4.1 car LOD, §4.2 sky lanes v4,
// round 40 cars_lod). Every vertex follows its row: the car's share s = fract(phase + clock
// * speed); a vertex `x` BU along the car (nose at 0, the speed line behind) sits at share
// s + x / length, so the whole car and its line bend along loops, ramps and the spiral.
// INSTANCE_CUSTOM = (phase, speed, row, streak BU); COLOR = the car's colour (lane colour, or
// head / tail light for street cars). CUSTOM0 = (part, stretch, 0, 0): part 0 body, 1 lane
// line / stripe, 2 head light, 3 tail light, 4 cabin, 5 under-glow; stretch 1 marks the
// line's tail end, pushed back by the streak. `clock` is the layer's own time (the layers
// pause it; reduce effects holds it at 0). CLOSE bodies take the shared toon bands
// (ToonInkMaterial's band edges and shades).
shader_type spatial;
render_mode unshaded, cull_disabled, specular_disabled, blend_mix, depth_draw_opaque;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/city/motion_path.gdshaderinc"

uniform float clock = 0.0;
uniform float gain = 1.0;
// The lane-colour line's share at management zooms (bible 4.1: sky lanes at 35 %); the car
// itself stays at full strength.
uniform float line_gain = 1.0;
uniform float body_alpha = 1.0;
uniform bool body_lane_fill = false;
uniform bool streak_on = true;
uniform float night = 1.0;
uniform float end_fade = 0.04;
uniform vec3 headlight = vec3(1.0, 0.97, 0.9);
uniform float headlight_gain = 1.6;
uniform vec3 taillight = vec3(1.0, 0.15, 0.12);
// Street cars (a negative streak marks a car showing its tail): the night head light.
uniform vec3 street_head = vec3(1.0, 0.93, 0.78);
uniform bool street = false;
uniform vec3 body_color = vec3(0.10, 0.09, 0.14);
uniform vec3 to_light = vec3(-0.705, 0.591, 0.392);
uniform float band_hi = 0.55;
uniform float band_lo = 0.12;
uniform float shade_mid = 0.62;
uniform float shade_low = 0.32;
uniform bool toon = false;

varying flat float v_part;
varying flat float v_tail;
varying float v_fade;
varying vec3 v_normal;

void vertex() {
	int row = int(INSTANCE_CUSTOM.z + 0.5);
	float len = max(path_length(row), 0.001);
	float s = fract(INSTANCE_CUSTOM.x + clock * INSTANCE_CUSTOM.y);
	v_tail = INSTANCE_CUSTOM.w < 0.0 ? 1.0 : 0.0;
	float x = VERTEX.x - (streak_on ? CUSTOM0.y * abs(INSTANCE_CUSTOM.w) : 0.0);
	float sv = s + x / len;
	vec3 p = path_at(row, sv);
	float e = 1.0 / float(textureSize(path_tex, 0).x);
	vec3 t = path_at(row, sv + e) - path_at(row, sv - e);
	t = length(t) > 1e-5 ? normalize(t) : vec3(1.0, 0.0, 0.0);
	vec3 right = normalize(vec3(-t.z, 0.0, t.x) + vec3(1e-6, 0.0, 0.0));
	vec3 up = normalize(cross(right, t));
	vec3 wp = p + up * VERTEX.y + right * VERTEX.z;
	v_normal = normalize(t * NORMAL.x + up * NORMAL.y + right * NORMAL.z);
	VERTEX = (inverse(MODEL_MATRIX) * vec4(wp, 1.0)).xyz;
	v_part = CUSTOM0.x;
	v_fade = smoothstep(0.0, end_fade, s) * smoothstep(0.0, end_fade, 1.0 - s);
}

void fragment() {
	vec3 lane = COLOR.rgb;
	float a = 1.0;
	vec3 c;
	if (v_part < 0.5) {
		c = body_lane_fill ? lane : body_color;
		if (toon) {
			float ndl = dot(v_normal, normalize(to_light));
			c *= ndl > band_hi ? 1.0 : (ndl > band_lo ? shade_mid : shade_low);
		}
		a = body_alpha;
	} else if (v_part < 1.5) {
		c = (street ? mix(lane, v_tail > 0.5 ? taillight : street_head, night) : lane) * gain * line_gain;
	} else if (v_part < 2.5) {
		vec3 lamp = street ? (v_tail > 0.5 ? taillight : street_head) : headlight * headlight_gain;
		c = mix(lane, lamp, night) * gain;
	} else if (v_part < 3.5) {
		c = mix(lane, taillight, night) * gain;
	} else if (v_part < 4.5) {
		c = body_color * 0.45;
	} else {
		c = lane * gain * 1.2;
		a = 0.8;
	}
	ALBEDO = c;
	ALPHA = a * v_fade;
}
