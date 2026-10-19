// NA-22b (PIPELINE_SPEC 4.1 cityglow): the netrun night sky. A near-black zenith over a warm city-glow band at the horizon:
// colour = top + (horizon - top) * exp(-k * sin(elevation)); below the horizon it falls to `ground`. `base` is the mainline
// flat background colour and `look_blend` mixes from it (0 = the page as before), so the blend is continuous.
shader_type sky;
// No clock (a still sky); the include keeps the shared reduce-effects global every shader declares.
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform vec3 base = vec3(0.0);
uniform vec3 top = vec3(0.004, 0.004, 0.012);
uniform vec3 horizon = vec3(0.1, 0.035, 0.03);
uniform vec3 ground = vec3(0.01, 0.008, 0.016);
// Falloff of the glow band with sin(elevation): larger = a thinner band at the horizon.
uniform float glow_k = 6.0;
uniform float look_blend = 1.0;

void sky() {
	float e = EYEDIR.y;
	vec3 up = top + (horizon - top) * exp(-glow_k * max(e, 0.0));
	vec3 col = e >= 0.0 ? up : mix(horizon, ground, clamp(-e * 8.0, 0.0, 1.0));
	COLOR = mix(base, col, clamp(look_blend, 0.0, 1.0));
}
