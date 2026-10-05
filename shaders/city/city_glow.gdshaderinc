// ART-5 5c: the city's point lights as camera-facing soft sprites (ART_BIBLE §4.2 aviation
// lights and lane-guide dots, §4.3 Heat: alarm beacons, police strobes, the hardened nodes'
// circling lights). One MultiMesh per layer; INSTANCE_CUSTOM = (phase 0-1, size BU, radius
// BU (mode 4), 0); COLOR = the light's colour. `mode`: 0 steady (guide dots), 1 blink (lit
// for `duty` of each `period`), 2 strobe (the same, a harder edge), 3 rotating beacon (a
// lobe sweeping past), 4 circling (round a ring of `radius` on the ground plane). `steady`
// (reduce motion / reduce effects) shows the light on and still. Sizes never fall below
// `min_px` screen pixels (`bu_per_px` = ortho / viewport width). Additive, depth-tested, so
// the buildings hide what is behind them.
// Shared body of city_glow.gdshader and city_glow_xray.gdshader (the x-ray one draws through buildings).
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform int mode = 0;
uniform float clock = 0.0;
uniform float period = 1.6;
uniform float duty = 0.35;
uniform bool steady = false;
uniform float gain = 1.0;
uniform float alpha = 1.0;
uniform float bu_per_px = 0.23;
uniform float min_px = 2.5;
// A blinking light's brightness between blinks (aviation lights read as red dots in a still).
uniform float off_level = 0.25;

varying float v_lit;

void vertex() {
	float ph = fract(clock / max(period, 0.001) + INSTANCE_CUSTOM.x);
	float lit = 1.0;
	vec3 origin = MODEL_MATRIX[3].xyz;
	if (!steady) {
		if (mode == 1 || mode == 2) {
			lit = ph < duty ? 1.0 : (mode == 1 ? off_level : 0.0);
		} else if (mode == 3) {
			lit = 0.2 + 0.8 * pow(max(0.0, cos(ph * TAU)), 4.0);
		}
	}
	if (mode == 4) {
		float th = (steady ? INSTANCE_CUSTOM.x : ph) * TAU;
		origin += vec3(cos(th), 0.0, sin(th)) * INSTANCE_CUSTOM.z;
	}
	v_lit = lit;
	float size = max(INSTANCE_CUSTOM.y, min_px * bu_per_px);
	mat4 m = mat4(INV_VIEW_MATRIX[0] * size, INV_VIEW_MATRIX[1] * size, INV_VIEW_MATRIX[2] * size, vec4(origin, 1.0));
	MODELVIEW_MATRIX = VIEW_MATRIX * m;
}

void fragment() {
	vec2 q = UV * 2.0 - 1.0;
	float r2 = dot(q, q);
	float a = exp(-r2 * 5.0) + 0.6 * smoothstep(0.18, 0.0, r2);
	ALBEDO = COLOR.rgb * gain;
	ALPHA = clamp(a * v_lit * alpha, 0.0, 1.0);
}
