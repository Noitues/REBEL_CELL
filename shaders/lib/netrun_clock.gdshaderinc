// NA-22: the netrun shaders' one clock. Moving things are functions of `anim_t` (PIPELINE_SPEC 3.6 rule 4, seconds in the
// 4.0 s loop), set by the view. Under reduce effects (the global `reduce_effects`, shaders/lib/rc_common.gdshaderinc) the
// clock stops at the plate's recorded value `frozen_t`, so a beam, a streak and a ghost are static end states (ruling W1
// NA-22 Q1: "reduce effects = end state", and the golden plates carry their `anim_t`).
#ifndef NETRUN_CLOCK_INCLUDED
#define NETRUN_CLOCK_INCLUDED
#include "res://shaders/lib/rc_common.gdshaderinc"
// LOOK-TOOLBOX step 7: the hash and value noise are rc_look's (rcl_hash13, rcl_vnoise3; the same arithmetic). rc_hash,
// not rc_look: city_fog is a fog shader and includes this file.
#include "res://addons/rc_look/shaders/rc_hash.gdshaderinc"

// The clock: `live_t` while effects play, `frozen_t` under reduce effects.
float nr_clock(float live_t, float frozen_t) {
	return mix(live_t, frozen_t, clamp(reduce_effects, 0.0, 1.0));
}

// A 3D value noise in 0..1 (a hash lattice, smooth interpolation): the fog, beam breakup and puddle noise.
float nr_hash3(vec3 p) {
	return rcl_hash13(p);
}

float nr_noise3(vec3 p) {
	return rcl_vnoise3(p);
}
#endif
