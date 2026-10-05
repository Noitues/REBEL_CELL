// ART-1 1D spike: a sky-lane car tier (bible §4.1 car LOD). The instance frame sits at the
// lane start (local X = lane direction, Z = side); the car slides along X by
// fract(phase + TIME * speed) * length. INSTANCE_CUSTOM = (phase, speed, lane length, dir).
// COLOR = lane colour. Vertex CUSTOM0.x: 0 body, 1 lane-colour light, 2 headlight, 3 tail.
// mode 0 FAR (dot + line), 1 MEDIUM (translucent box + line), 2 CLOSE (model + thick line).
shader_type spatial;
render_mode cull_disabled, specular_disabled, unshaded, blend_mix, depth_draw_opaque;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float gain = 1.0;
uniform float body_alpha = 1.0;
uniform float time_scale = 1.0;
uniform vec3 body_color = vec3(0.10, 0.09, 0.14);

varying flat float v_part;

void vertex() {
	float s = fract(INSTANCE_CUSTOM.x + rc_time(TIME) * time_scale * INSTANCE_CUSTOM.y);
	if (INSTANCE_CUSTOM.w < 0.0) {
		s = 1.0 - s;
		VERTEX.xz = -VERTEX.xz;
	}
	VERTEX.x += s * INSTANCE_CUSTOM.z;
	v_part = CUSTOM0.x;
}

void fragment() {
	vec3 lane_col = COLOR.rgb;
	if (v_part < 0.5) {
		ALBEDO = mix(body_color, lane_col, body_alpha < 0.99 ? 1.0 : 0.0);
		ALPHA = body_alpha;
	} else if (v_part < 1.5) {
		ALBEDO = lane_col * gain;
		ALPHA = 1.0;
	} else if (v_part < 2.5) {
		ALBEDO = vec3(1.0, 0.97, 0.9) * gain * 1.6;
		ALPHA = 1.0;
	} else {
		ALBEDO = vec3(1.0, 0.15, 0.12) * gain;
		ALPHA = 1.0;
	}
}
