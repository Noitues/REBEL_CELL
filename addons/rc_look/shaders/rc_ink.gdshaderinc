// LOOK-TOOLBOX module 5: ink. The two ways the game draws a line, as one set of helpers in exact forms of the existing
// code (toon_ink_hull for props / busts / aircraft, city_post's edge pass for the city):
//   - rcl_hull_width(width_px, wobble, n01): the hull's width with a wobble (n01: a 0..1 noise at the vertex).
//   - rcl_hull_clip(clip, n_clip, width_px, viewport): the hull vertex grown `width_px` px outward on screen (clip space).
//   - rcl_ink_normal_edge(c0, cn, thr): 1 where the normal / material code changes past thr
//     (length(dn) * 0.5 + |dmaterial|; c = vec4(normal, material)).
//   - rcl_ink_depth_thr(edge, ortho, ortho_ref): the depth step that counts as an edge, scaled with the view's size.
//   - rcl_ink_depth_edge(zc, zn, thr): 1 where the view depth jumps past thr.
// Numbers in addons/rc_look/config/look_ink.tres (hull and post presets); RcLookInk mirrors these exactly.
//   #include "res://addons/rc_look/shaders/rc_ink.gdshaderinc"
#ifndef RC_INK_INCLUDED
#define RC_INK_INCLUDED

float rcl_hull_width(float width_px, float wobble, float n01) {
	return width_px * (1.0 + wobble * (n01 - 0.5) * 2.0);
}

vec4 rcl_hull_clip(vec4 clip, vec2 n_clip, float width_px, vec2 viewport) {
	clip.xy += n_clip * width_px * 2.0 / viewport * clip.w;
	return clip;
}

float rcl_ink_normal_edge(vec4 c0, vec4 cn, float thr) {
	return step(thr, length(cn.xyz - c0.xyz) * 0.5 + abs(cn.w - c0.w));
}

float rcl_ink_depth_thr(float edge, float ortho, float ortho_ref) {
	return edge * (ortho / ortho_ref);
}

float rcl_ink_depth_edge(float zc, float zn, float thr) {
	return step(thr, abs(zn - zc));
}
#endif
