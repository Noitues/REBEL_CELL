// REBEL_CELL shader library: the shared include (ART_BIBLE v2 5.4, 6.4; ported from the
// art-pass W6 rc_common in ART-0 E; the global ported from art-pass 290ae4c in ART-0 E2).
//
// Every shader in res://shaders that animates includes this file and reads ONE
// reduce-effects control: the global uniform `reduce_effects` (0 = effects on, 1 = reduce
// effects), registered in project.godot [shader_globals] and set by the Fx autoload
// (RenderingServer.global_shader_parameter_set) from Settings.reduce_effects on start and on
// every Settings change. Being global, it reaches every material on these shaders, however
// it was built (script, scene or .tres), with no per-material bookkeeping.
// Under reduce effects every animated component of a shader (scroll, flicker, roll,
// chromatic aberration, jitter, boil) goes static; a shader's static look (scanline
// pattern, paper grain, blur) stays. The scripts' own zeroing of shader strengths stays too.
//
// Convention:
//   #include "res://shaders/lib/rc_common.gdshaderinc"
//   float t = rc_time(TIME);          // frozen at 0 under reduce effects
//   float f = flicker * rc_live();    // an animated strength, 0 under reduce effects
// Helpers are prefixed rc_ so they never clash with a shader's own functions.

global uniform float reduce_effects;

// 1.0 while effects play, 0.0 under reduce effects.
float rc_live() {
	return 1.0 - clamp(reduce_effects, 0.0, 1.0);
}

// A clock that stops (at 0) under reduce effects: pass TIME.
float rc_time(float t) {
	return t * rc_live();
}
