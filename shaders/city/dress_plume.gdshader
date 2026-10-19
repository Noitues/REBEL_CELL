// NA-24 (PIPELINE_SPEC 5.2 plumes, 9.6): rooftop steam plumes. A MultiMesh of sources (instance origin = the roof vent); the
// mesh holds `puffs` camera-facing quads, vertex COLOR.r = the puff's phase 0..1, UV 0..1 over the quad. Each puff rises and
// grows over one loop and fades in and out; the clock is `nr_clock`, one cycle per loop, so the frame at t equals the frame at
// t + loop_s. INSTANCE_CUSTOM.x = a 0..1 per-source phase offset (whole fractions of a cycle are still seamless).
shader_type spatial;
render_mode unshaded, blend_mix, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"

uniform float loop_s = 4.0;
uniform float anim_t = 0.0;
uniform float anim_t_frozen = 0.0;
uniform float rise = 9.0;
uniform float size0 = 1.0;
uniform float size1 = 4.0;
uniform float alpha = 0.5;
uniform float emit = 0.9;
uniform vec3 col = vec3(0.6, 0.7, 0.85);
uniform float look_blend = 1.0;

varying float ph;

void vertex() {
	float t = mod(nr_clock(anim_t, anim_t_frozen), loop_s) / loop_s;
	ph = fract(t + COLOR.r + INSTANCE_CUSTOM.x);
	float s = mix(size0, size1, ph);
	vec3 corner = vec3((UV - vec2(0.5)) * 2.0 * s, 0.0);
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	VERTEX = vec3(0.0, ph * rise, 0.0) + corner;
}

void fragment() {
	float r = clamp(length(UV - vec2(0.5)) * 2.0, 0.0, 1.0);
	float soft = (1.0 - r) * (1.0 - r);
	float life = sin(3.14159265 * ph);
	ALBEDO = col * emit;
	ALPHA = soft * life * alpha * look_blend;
}
