shader_type spatial;
render_mode unshaded, cull_disabled, shadows_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
// NA-23: a street netrun room interior (the lit window of a route building). Unshaded: the vertex colour is the lit surface
// (back wall glow, dark floor, near-black props, the bright frame); `energy` brightens it (the hovered branch, the options).
// The id pass (PIPELINE_SPEC 12.0) draws the flat `id_color` (R = class 5, G = room index, B = layer, bytes / 255).
uniform float energy = 1.0;
// NA-23c: the frame bars (vertex alpha < 0.75) scale with the zoom: half at OVERVIEW, full at DECISION (`look.frame`).
uniform float frame_k = 1.0;
uniform bool id_mode = false;
uniform vec3 id_color = vec3(0.0);

vec3 id_lin(vec3 c) {
	return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(vec3(0.04045), c));
}

void fragment() {
	vec3 c = COLOR.rgb * energy * (COLOR.a < 0.75 ? frame_k : 1.0);
	ALBEDO = id_mode ? id_lin(id_color) : c;
}
