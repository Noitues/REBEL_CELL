// NA-22 (PIPELINE_SPEC 4.1 "Beams: soft volumetric cones, never solid rods", 11.1 Beams; AD ruling C4): the visible shaft of a
// beam, an additive soft cone with the radial and axial profile of the Blender shaft material. The mesh is an open unit tube
// (NetrunShaderKit.beam_mesh: rings of unit-circle vertices, VERTEX.y = UV.y = 0 at the base .. 1 at the far end); the
// shader sizes it (start radius -> end radius over beam_len), leans it (dress `beams[].lean_deg` = [x, y] degrees in plan
// axes: direction (tan x, tan y, 1) with plan y = -world Z), and sweeps it (sweep_deg, phase, a function of the clock, period
// loop_s): the lean angles gain sweep * sin(2 pi (t / loop_s + phase)) in x and pitch_share * sweep * cos(...) in y.
// Radial: r = 1 - facing (0 on the axis side), core = core_w exp(-(r / core_sigma)^2 / 2), skirt = skirt_w
// exp(-(r / skirt_sigma)^2 / 2) * (1 - r^2); both vanish at the silhouette (rule 2). Axial: exp(-t / efold) with a smoothstep
// to 0 over fade_from .. fade (no disc end) and a fade-in. Breakup: world noise. Hot core: toward white.
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"

uniform vec3 beam_col = vec3(1.0, 0.4, 0.7);
uniform float beam_len = 50.0;
uniform float start_radius = 0.18;
uniform float end_radius = 5.2;
uniform vec2 lean_deg = vec2(5.0, 8.0);
uniform float sweep_deg = 0.0;
uniform float phase = 0.0;
uniform float loop_s = 4.0;
uniform float pitch_share = 0.25;
uniform float anim_t = 0.0;
uniform float anim_t_frozen = 0.0;
uniform float core_sigma = 0.13;
uniform float core_w = 1.0;
uniform float skirt_sigma = 0.42;
uniform float skirt_w = 0.5;
uniform float efold = 0.22;
uniform float fade = 0.6;
uniform float fade_from = 0.27;
uniform float fade_in = 0.025;
uniform float noise_scale = 0.09;
uniform vec2 noise_range = vec2(0.35, 0.65);
uniform float hot = 0.5;
uniform float emit = 3.0;
uniform float emission_multiplier = 1.0;
uniform float look_blend = 1.0;

varying vec3 v_nw;
varying vec3 v_pw;

void vertex() {
	float t = UV.y;
	float rad = mix(start_radius, end_radius, t);
	vec3 v = vec3(VERTEX.x * rad, t * beam_len, VERTEX.z * rad);
	vec3 nrm = normalize(vec3(VERTEX.x, 0.0, VERTEX.z));
	float clk = nr_clock(anim_t, anim_t_frozen);
	float ph = 6.2831853 * (clk / max(loop_s, 0.001) + phase);
	float ax = radians(lean_deg.x + sweep_deg * sin(ph));
	float ay = radians(lean_deg.y + sweep_deg * pitch_share * cos(ph));
	// Plan (x east, y north, z up) -> Godot (x, y up, z = -north).
	vec3 d = normalize(vec3(tan(ax), 1.0, -tan(ay)));
	vec3 k = cross(vec3(0.0, 1.0, 0.0), d);
	float c = d.y;
	mat3 K = mat3(vec3(0.0, k.z, -k.y), vec3(-k.z, 0.0, k.x), vec3(k.y, -k.x, 0.0));
	mat3 R = mat3(1.0) + K + K * K * (1.0 / (1.0 + c));
	VERTEX = R * v;
	v_nw = normalize(mat3(MODEL_MATRIX) * (R * nrm));
	v_pw = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 vw = normalize((INV_VIEW_MATRIX * vec4(VIEW, 0.0)).xyz);
	float facing = abs(dot(normalize(v_nw), vw));
	float r = 1.0 - clamp(facing, 0.0, 1.0);
	float s2 = 1.0 - r * r;
	float core = core_w * exp(-0.5 * (r / core_sigma) * (r / core_sigma));
	float skirt = skirt_w * exp(-0.5 * (r / skirt_sigma) * (r / skirt_sigma)) * s2;
	float t = UV.y;
	float axial = exp(-t / efold) * (1.0 - smoothstep(fade_from, fade, t)) * smoothstep(0.0, fade_in, t);
	float n = nr_noise3(v_pw * noise_scale);
	float breakup = 0.55 + 0.45 * smoothstep(noise_range.x, noise_range.y, n);
	float prof = (core + skirt) * axial * breakup;
	vec3 col = mix(beam_col, vec3(1.0), hot * clamp(core / max(core_w, 0.0001), 0.0, 1.0));
	ALBEDO = col * emit * prof * emission_multiplier * look_blend;
	ALPHA = 1.0;
}
