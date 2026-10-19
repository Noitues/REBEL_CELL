// NA-22: the netrun shaders' one clock. Moving things are functions of `anim_t` (PIPELINE_SPEC 3.6 rule 4, seconds in the
// 4.0 s loop), set by the view. Under reduce effects (the global `reduce_effects`, shaders/lib/rc_common.gdshaderinc) the
// clock stops at the plate's recorded value `frozen_t`, so a beam, a streak and a ghost are static end states (ruling W1
// NA-22 Q1: "reduce effects = end state", and the golden plates carry their `anim_t`).
#ifndef NETRUN_CLOCK_INCLUDED
#define NETRUN_CLOCK_INCLUDED
#include "res://shaders/lib/rc_common.gdshaderinc"

// The clock: `live_t` while effects play, `frozen_t` under reduce effects.
float nr_clock(float live_t, float frozen_t) {
	return mix(live_t, frozen_t, clamp(reduce_effects, 0.0, 1.0));
}

// A 3D value noise in 0..1 (a hash lattice, smooth interpolation): the fog, beam breakup and puddle noise.
float nr_hash3(vec3 p) {
	p = fract(p * 0.1031);
	p += dot(p, p.zyx + 31.32);
	return fract((p.x + p.y) * p.z);
}

float nr_noise3(vec3 p) {
	vec3 i = floor(p);
	vec3 f = fract(p);
	vec3 u = f * f * (3.0 - 2.0 * f);
	float a = mix(mix(nr_hash3(i), nr_hash3(i + vec3(1, 0, 0)), u.x), mix(nr_hash3(i + vec3(0, 1, 0)), nr_hash3(i + vec3(1, 1, 0)), u.x), u.y);
	float b = mix(mix(nr_hash3(i + vec3(0, 0, 1)), nr_hash3(i + vec3(1, 0, 1)), u.x), mix(nr_hash3(i + vec3(0, 1, 1)), nr_hash3(i + vec3(1, 1, 1)), u.x), u.y);
	return mix(a, b, u.z);
}
#endif
