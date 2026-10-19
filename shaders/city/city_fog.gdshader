// NA-22 (PIPELINE_SPEC 4.1 "Fog: one heterogeneous scatter volume", 11.1 Fog, 12.1 value band): the netrun fog as a FogVolume
// shader (`shader_type fog`), the Blender volume of `onecity_cycles.py:373-541` per fragment. Heights are world Y above the
// ground; plan axes: x = world X, y = -world Z. All heights scale with h_front (the median frontage roof across the street)
// and h_sky = h_sky_k * h_front. Terms: body (clumps x strata layers, banks / wisps octaves), the wisp layer just above the
// frontage roofs, the ground bank on the camera side, mid banks, back haze above h_sky; only behind the street face
// (front), never in front of it. Emission carries the underlight, ground glow and mid glow tints. `look_blend` scales the
// whole density (0 = no volume: the mainline post fog patches carry the page). `octave_w` (x banks, y wisps, z clumps) is the
// LOD band weight of `fog_octaves`. The clock is `anim_t`, frozen at `anim_t_frozen` under reduce effects.
shader_type fog;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"

uniform float look_blend = 1.0;
uniform float density_mul = 1.0;
// The multiplier on the sky haze and the backdrop haze (they are thin and keep the spec numbers; `density_mul` is the street's body calibration).
uniform float haze_mul = 1.0;
uniform float peak = 0.0507;
uniform float h_front = 14.0;
uniform float h_sky = 30.8;
uniform float strata_k = 0.42;
uniform float warp_k = 0.22;
uniform float tilt = 0.07;
uniform vec3 bank_freq = vec3(0.004, 0.012, 0.075);
uniform vec3 wisp_freq = vec3(0.009, 0.02, 0.33);
uniform vec2 bank_mix = vec2(0.62, 0.38);
uniform vec2 remap_oct = vec2(0.47, 0.64);
uniform vec3 clump_freq = vec3(0.0075, 0.014, 0.022);
uniform vec2 remap_clump = vec2(0.40, 0.62);
uniform float wisp_at = 1.08;
uniform float wisp_half = 0.12;
uniform float wisp_k = 1.2;
uniform vec2 front = vec2(7.0, 17.0);
uniform vec2 floor_range = vec2(0.08, 0.3);
uniform vec2 gb_off = vec2(0.5, 4.0);
uniform float gb_top = 2.2;
uniform float ground_bank = 0.04;
uniform vec2 mid_range = vec2(0.05, 0.8);
uniform vec2 mid_remap = vec2(0.42, 0.62);
uniform float mid_bank = 0.035;
uniform float haze = 0.0008;
uniform float haze_efold = 40.0;
// AAA-2 backdrop haze (MATERIAL_SPEC 6): `back_haze` per BU behind the street line, from `back_depth.x` to `back_depth.y` BU deep,
// falling with height as exp(-z / (back_h_k * h_sky)): the far skyline's violet.
uniform float back_haze = 0.0;
uniform vec2 back_depth = vec2(30.0, 120.0);
uniform float back_h_k = 2.4;
uniform vec3 scatter = vec3(0.85, 0.80, 1.0);
uniform float underlight_k = 0.07;
uniform float ground_glow = 0.05;
uniform float mid_glow = 0.3;
// Gain on the emitted tints (the volume's own glow; calibrated against the plates, 12.1).
uniform float emit_gain = 40.0;
uniform vec3 tint_a = vec3(1.0, 0.16, 0.6);
uniform vec3 tint_b = vec3(0.16, 0.8, 1.0);
uniform vec3 tint_c = vec3(0.62, 0.38, 1.0);
uniform vec3 wind = vec3(1.2, 0.0, 0.4);
uniform vec3 octave_w = vec3(1.0, 1.0, 1.0);
// The street (plan x, y): segment a -> c, the camera side is dot(p - a, nrm) < 0; kerb = half street width.
uniform vec2 sec_a = vec2(0.0);
uniform vec2 sec_c = vec2(0.0, 1.0);
uniform vec2 sec_nrm = vec2(1.0, 0.0);
uniform float kerb = 4.0;
// 1 = the front mask uses |side| (a canyon view along the street: fog on both sides), 0 = behind the street face only.
uniform float front_sym = 0.0;
uniform float anim_t = 0.0;
uniform float anim_t_frozen = 0.0;

// Three octaves at the frequencies f (weights 0.5 / 0.3 / 0.2), the higher two scaled by the band weight w.
float oct3(vec3 p, vec3 f, float w) {
	float a = 0.5 * nr_noise3(p * f.x);
	float b = 0.3 * w * nr_noise3(p * f.y + 17.0);
	float c = 0.2 * w * nr_noise3(p * f.z + 43.0);
	return (a + b + c) / (0.5 + 0.5 * w);
}

void fog() {
	vec3 wp = WORLD_POSITION;
	float clk = nr_clock(anim_t, anim_t_frozen);
	vec3 q = wp - wind * clk;
	float z = max(wp.y, 0.0);
	vec2 pp = vec2(wp.x, -wp.z);
	vec2 ac = sec_c - sec_a;
	float slen = max(length(ac), 0.0001);
	vec2 tdir = ac / slen;
	float along = dot(pp - sec_a, tdir);
	float side = dot(pp - sec_a, sec_nrm);

	float fall = exp(-max(z - 0.5 * h_front, 0.0) / h_sky);
	float warp = ((oct3(q, vec3(0.006, 0.010, 0.02), 1.0) - 0.5) * 2.0) * warp_k * h_front;
	float zw = z + warp + tilt * along;
	float strata = 0.5 + 0.5 * sin(6.2831853 * zw / (strata_k * h_front));
	float banks = oct3(q, bank_freq, octave_w.x);
	float wisps = oct3(q, wisp_freq, octave_w.y);
	float mixed = bank_mix.x * banks + bank_mix.y * wisps;
	float layers = smoothstep(remap_oct.x, remap_oct.y, mixed) * strata;
	float clumps = smoothstep(remap_clump.x, remap_clump.y, oct3(q, clump_freq, octave_w.z));
	float body = clumps * 0.08 + layers * clumps;
	float wisp = wisp_k * (1.0 - smoothstep(0.0, wisp_half * h_front, abs(z - wisp_at * h_front))) * smoothstep(0.5, 0.62, wisps);
	body = max(body, wisp);

	float behind = smoothstep(front.x, front.y, mix(side, abs(side), front_sym));
	float flo = smoothstep(floor_range.x * h_front, floor_range.y * h_front, z);
	float dens = peak * body * fall * behind * flo;

	// Ground bank: camera side beyond the kerb + gb_off, thick to 0.2 gb_top, gone at gb_top.
	float cam_d = -side - kerb;
	float gb = ground_bank * smoothstep(gb_off.x, gb_off.y, cam_d) * (1.0 - smoothstep(0.2 * gb_top, gb_top, z))
		* smoothstep(0.38, 0.55, banks);
	// Mid banks: 0.05 .. 0.8 h_front.
	float mb = mid_bank * smoothstep(mid_range.x * h_front, mid_range.x * h_front * 2.0, z) * (1.0 - smoothstep(mid_range.y * 0.6 * h_front, mid_range.y * h_front, z))
		* smoothstep(mid_remap.x, mid_remap.y, banks);
	// Back haze above h_sky.
	float hz = haze * exp(-max(0.0, z - h_sky) / haze_efold);
	float bh = back_haze * smoothstep(back_depth.x, back_depth.y, side) * exp(-z / (back_h_k * h_sky));
	float body_total = dens + gb + mb;
	float total = body_total + hz + bh;

	// Underlight ramp by zw / (2.2 h_front): tint_a -> tint_b -> tint_c, and the glow tints.
	float ramp = clamp(zw / (2.2 * h_front), 0.0, 1.0);
	vec3 under = ramp < 0.5 ? mix(tint_a, tint_b, ramp * 2.0) : mix(tint_b, tint_c, ramp * 2.0 - 1.0);
	float nglow = nr_noise3(q * 0.02);
	vec3 gcol = mix(tint_a, tint_b, nglow);
	vec3 mcol = nglow < 0.5 ? mix(tint_b, tint_c, nglow * 2.0) : mix(tint_c, tint_a, nglow * 2.0 - 1.0);
	vec3 emis = under * dens * underlight_k + gcol * gb * ground_glow + mcol * mb * mid_glow;

	DENSITY = (body_total * density_mul + (hz + bh) * haze_mul) * clamp(look_blend, 0.0, 1.0);
	ALBEDO = scatter;
	EMISSION = emis * emit_gain * clamp(look_blend, 0.0, 1.0);
}
