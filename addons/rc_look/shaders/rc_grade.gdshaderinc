// LOOK-TOOLBOX module 9 (post chain): the grade. One exposure for every view that shows a rendered image, so a
// close-up, a page and a lab read the same light:
//   sRGB in -> linear -> x exposure -> highlight shoulder -> sRGB -> x tint (clamped) -> saturation.
// The shoulder is extended Reinhard l (1 + l / W^2) / (1 + l): exposed linear light W lands on 1; W = 0 is a plain
// clip. Saturation scales around the Rec.709 luma of the display value. RcLookGrade (GDScript) mirrors it exactly;
// presets (cel, aaa2) are in addons/rc_look/config/look_grade.tres.
//   #include "res://addons/rc_look/shaders/rc_grade.gdshaderinc"
#ifndef RC_GRADE_INCLUDED
#define RC_GRADE_INCLUDED
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"

// Extended Reinhard on linear light (white <= 0: unchanged).
vec3 rcl_shoulder(vec3 lin, float white) {
	if (white <= 0.0) {
		return lin;
	}
	return lin * (1.0 + lin / (white * white)) / (1.0 + lin);
}

// An sRGB value exposed in linear light and returned as sRGB.
vec3 rcl_expose(vec3 srgb, float exposure, float white) {
	return rcl_to_srgb(rcl_shoulder(max(rcl_to_lin(srgb) * exposure, vec3(0.0)), white));
}

// The whole grade on an sRGB value (returns sRGB).
vec3 rcl_grade(vec3 srgb, float exposure, float white, vec3 tint, float saturation) {
	vec3 g = clamp(rcl_expose(srgb, exposure, white) * tint, 0.0, 1.0);
	return rcl_saturate(g, saturation);
}
#endif
