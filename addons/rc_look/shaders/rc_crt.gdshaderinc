// LOOK-TOOLBOX module 14: the CRT / terminal glass (ART_BIBLE §1.2, §6.4): scanlines, flicker, the rolling band, the
// vignette and the edge glow, each the exact form of the shader it names. Standalone (no rc_look, no rc_common, no
// globals, no TIME): a caller passes its own clock and applies rc_live() / rc_time() itself, so the same include serves a
// canvas_item, a spatial or a fog shader.
//   scan      crt_terminal.gdshader:77 (y_px = p.y - panel.y, phase 0.08) and the FRAGCOORD form of crt_panel /
//             city_sketch / city_live (y_px = FRAGCOORD.y, phase 0)
//   flicker   the one-liner of crt_panel (rate 43), city_sketch / city_live (41) and scanline (47)
//   roll      crt_terminal.gdshader:82
//   vignette  crt_terminal.gdshader:54-55 (_sd) and scanline.gdshader:26-27 (_uv)
//   glow      crt_terminal.gdshader:71
// Reduce effects: the caller folds rc_live() into `amount` / the strength (the three conventions are in the README).
#ifndef RC_CRT_INCLUDED
#define RC_CRT_INCLUDED

// The glow's falloff length as a share of its reach (crt_terminal: exp(-sd / (glow_px * 0.42))), and its floor (px).
const float RCL_CRT_GLOW_REACH = 0.42;
const float RCL_CRT_GLOW_MIN_PX = 0.5;
// scanline.gdshader's pi (3.14159, not PI).
const float RCL_CRT_SINE_PI = 3.14159;

// Scanline mask, 1 on the dark line: step(0.5, fract(y_px / period - phase)). Caller scales it by the strength.
float rcl_crt_scan(float y_px, float period_px, float phase) {
	return step(0.5, fract(y_px / period_px - phase));
}

// scanline.gdshader's sine scanlines: 0..1 across `density` cycles of pi per unit of the screen's y.
float rcl_crt_scan_sine(float y01, float density) {
	return 0.5 + 0.5 * sin(y01 * density * RCL_CRT_SINE_PI);
}

// The flicker gain: 1 - amount x (0.5 + 0.5 sin(t rate)). Pass amount x rc_live() and t = rc_time(TIME).
float rcl_crt_flicker(float t, float rate_rad_s, float amount) {
	return 1.0 - amount * (0.5 + 0.5 * sin(t * rate_rad_s));
}

// The rolling band's profile at height share y01 (0..1 down the panel) with the band at `band` (0..1): a gaussian of
// half-width `width`. Caller multiplies by the strength x rc_live().
float rcl_crt_roll(float y01, float band, float width) {
	return exp(-pow((y01 - band) / width, 2.0));
}

// The inner vignette of the glass at signed distance sd (px, negative inside): the glass keeps `floor_gain` at the edge
// and is whole from `reach_px` in. Multiply the glass rgb by it.
float rcl_crt_vignette_sd(float sd, float reach_px, float floor_gain) {
	return mix(floor_gain, 1.0, smoothstep(0.0, reach_px, -sd));
}

// The screen vignette: 1 - amount x smoothstep(inner, outer, distance from the centre). Multiply the colour by it.
float rcl_crt_vignette_uv(vec2 uv, float amount, float inner, float outer) {
	return 1.0 - amount * smoothstep(inner, outer, distance(uv, vec2(0.5)));
}

// The outer edge glow's alpha at signed distance sd (px, positive outside): exp(-sd / (glow_px 0.42)) x strength.
float rcl_crt_glow(float sd, float glow_px, float strength) {
	return exp(-sd / max(glow_px * RCL_CRT_GLOW_REACH, RCL_CRT_GLOW_MIN_PX)) * strength;
}

#endif
