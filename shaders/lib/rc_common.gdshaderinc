// REBEL_CELL shader library: the shared include (ART_BIBLE 13, 8, 12).
//
// Every shader in res://shaders includes this file and reads ONE reduce-effects control:
// the global uniform `reduce_effects` (0 = effects on, 1 = reduce effects), registered in
// project.godot [shader_globals] and set by the Fx autoload from Settings.reduce_effects on
// start and on Settings.changed. Under reduce effects every animated component of a shader
// (scroll, flicker, roll, chromatic aberration, jitter, boil) goes static; a shader's
// static look (scanline pattern, paper grain, halftone, blur) stays.
//
// Convention for library shaders:
//   #include "res://shaders/lib/rc_common.gdshaderinc"
//   float t = rc_time(TIME);          // frozen at 0 under reduce effects
//   float f = flicker * rc_live();    // an animated strength, 0 under reduce effects
// Helpers are prefixed rc_ so they never clash with a shader's own functions. Decoration
// noise comes from hashes (never an RNG), so a still frame is repeatable.

global uniform float reduce_effects;

// 1.0 while effects play, 0.0 under reduce effects.
float rc_live() {
	return 1.0 - clamp(reduce_effects, 0.0, 1.0);
}

// A clock that stops (at 0) under reduce effects: pass TIME.
float rc_time(float t) {
	return t * rc_live();
}

// Hash noise 0..1 of a 2D point (decoration only).
float rc_hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// Smooth value noise 0..1.
float rc_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(rc_hash(i), rc_hash(i + vec2(1.0, 0.0)), u.x),
		mix(rc_hash(i + vec2(0.0, 1.0)), rc_hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

// Perceived brightness (Rec. 601), the greyscale the accessibility checks use.
float rc_luma(vec3 c) {
	return dot(c, vec3(0.299, 0.587, 0.114));
}

// Scanline mask 0..1 on a `pitch`-px row pattern in screen px (static: never rolls).
float rc_scanline(vec2 frag, float pitch) {
	return step(0.5, fract(frag.y / max(pitch, 1.0)));
}
