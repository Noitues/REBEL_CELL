// LOOK-TOOLBOX module 1: the rc_look shader library. Every rc_look module shader includes this one file:
//   #include "res://addons/rc_look/shaders/rc_look.gdshaderinc"
// It brings
//   - rc_common (the global `reduce_effects`, rc_live(), rc_time()),
//   - the ART_BIBLE §2 colour tokens as global uniforms (rc_tokens.gdshaderinc: rc_cell_pink, rc_pencil_plan, ...;
//     values from Palette, written into project.godot by addons/rc_look/tools/sync_tokens.gd),
//   - the hash / value noise (rc_hash.gdshaderinc),
//   - colour space, facet (per-triangle) ids and screen helpers below.
// Helpers are prefixed rcl_ so they never clash with a shader's own functions (rc_ belongs to rc_common).
#ifndef RC_LOOK_INCLUDED
#define RC_LOOK_INCLUDED
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_tokens.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_hash.gdshaderinc"

// ---- Colour space (exact sRGB transfer, as the Python post) ----

vec3 rcl_to_srgb(vec3 lin) {
	vec3 c = max(lin, vec3(0.0));
	return mix(c * 12.92, 1.055 * pow(c, vec3(1.0 / 2.4)) - 0.055, step(vec3(0.0031308), c));
}

vec3 rcl_to_lin(vec3 srgb) {
	vec3 c = max(srgb, vec3(0.0));
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

// Rec.709 luminance of a linear colour.
float rcl_luma(vec3 lin) {
	return dot(lin, vec3(0.2126, 0.7152, 0.0722));
}

// Saturation scale around the Rec.709 luminance (0 = grey, 1 = unchanged).
vec3 rcl_saturate(vec3 c, float s) {
	return mix(vec3(rcl_luma(c)), c, s);
}

// A token (sRGB, as Palette holds it) in linear light, for lighting maths.
vec3 rcl_token_lin(vec4 token) {
	return rcl_to_lin(token.rgb);
}

// ---- Facets (the Cv2 low-poly look: one tone per triangle face) ----

// The flat (face) normal at a fragment from its world position's screen derivatives. Pass the world position.
vec3 rcl_facet_normal(vec3 world_pos) {
	return normalize(cross(dFdx(world_pos), dFdy(world_pos)));
}

// A stable id in 0..1 for the face a fragment lies on: its plane (normal and distance from the origin), quantised so
// every fragment of one flat face hashes the same, and neighbouring faces of one plane differ by `cell` (world units).
float rcl_facet_id(vec3 world_pos, vec3 face_n, float cell) {
	vec3 nq = floor(face_n * 48.0 + 0.5);
	float dq = floor(dot(world_pos, face_n) * 8.0 + 0.5);
	vec3 along = world_pos - face_n * dot(world_pos, face_n);
	vec3 c = floor(along / max(cell, 1e-3));
	return rcl_hash13(nq + vec3(dq * 0.37) + c * 7.13);
}

// ---- Screen helpers ----

// The size of one screen pixel in UV.
vec2 rcl_px(vec2 viewport_size) {
	return 1.0 / max(viewport_size, vec2(1.0));
}

// Screen UV with x scaled to the aspect, so a circle in it is round on screen.
vec2 rcl_aspect_uv(vec2 uv, vec2 viewport_size) {
	return vec2(uv.x * viewport_size.x / max(viewport_size.y, 1.0), uv.y);
}

#endif
