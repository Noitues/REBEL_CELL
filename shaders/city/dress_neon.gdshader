// NA-24 (PIPELINE_SPEC 5.2b, 9.1, 9.6): the street dressing's emissive pieces as one unshaded additive shader on a MultiMesh.
// Colour = the instance colour (a palette colour resolved by the builder); INSTANCE_CUSTOM.x = a 0..1 seed (burst count, glyph pattern), .z = the gain (HQ band emit), .y = a
// 0..1 phase. `shape` 0 = a solid piece (shop strip, billboard panel, lamp dot), 1 = a soft radial disc on a quad (lamp spill, ground
// glow, facade wash: UV radial falloff), 2 = the flicker overlay of a sign (tier 3): 1 .. 3 short bursts per loop on a hum of
// whole cycles, so the frame at t equals the frame at t + loop_s, added on the panel only (never over a core stroke), 3 = a sign
// piece (NA-24c): a softer panel (`panel_level`) with a thin bright core (`core_level`: frame trim and text-block strokes) taken
// with max inside the one piece, so the layers never sum; a far tier block yields to the tier that covers it (`yield_range`).
// Every moving term is a pure function of the clock (`nr_clock`: `anim_t` live, `anim_t_frozen` under reduce effects).
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"
#include "res://shaders/lib/netrun_clock.gdshaderinc"

uniform int shape = 0;
uniform float emit = 1.0;
uniform float loop_s = 4.0;
uniform float anim_t = 0.0;
uniform float anim_t_frozen = 0.0;
uniform vec2 bursts = vec2(1.0, 3.0);
uniform float disc_power = 2.0;
uniform float emission_multiplier = 1.0;
uniform float look_blend = 1.0;
uniform float panel_level = 0.42;
uniform float core_level = 0.9;
uniform float core_max = 0.95;
uniform float frame_w = 0.05;
uniform vec2 cell = vec2(0.16, 0.3);
uniform float stroke_h = 0.09;
uniform float fill = 0.65;
uniform float cell_gap = 0.22;
uniform float bright_var = 0.2;
uniform float side_dim = 0.6;
// (end, near) of the tier that covers this one; end 0 = no yield.
uniform vec2 yield_range = vec2(0.0, 0.0);

varying vec3 cust;
varying vec3 lpos;
varying vec3 lnrm;
varying vec3 lscale;

void vertex() {
	cust = INSTANCE_CUSTOM.xyz;
	lpos = VERTEX;
	lnrm = NORMAL;
	lscale = vec3(length(MODEL_MATRIX[0].xyz), length(MODEL_MATRIX[1].xyz), length(MODEL_MATRIX[2].xyz));
}

float sg_hash(vec2 c, float seed) {
	return fract(sin(dot(c + seed * 17.0, vec2(12.9898, 78.233))) * 43758.5453);
}

// Coverage of the interval [lo, hi] at x, antialiased over the pixel footprint `fw`.
float sg_band(float x, float lo, float hi, float fw) {
	float f = max(fw, 0.0001);
	return clamp((x - lo) / f + 0.5, 0.0, 1.0) * clamp((hi - x) / f + 0.5, 0.0, 1.0);
}

// The core mask (0..1) of a sign face at coordinates `p` (BU from the piece centre) of size `sz`: frame trim + text-block rows.
float sg_core(vec2 p, vec2 sz, float seed, vec2 fw) {
	vec2 q = p + sz * 0.5;
	float de = min(min(q.x, sz.x - q.x), min(q.y, sz.y - q.y));
	float frame_cov = clamp((frame_w - de) / max(max(fw.x, fw.y), 0.0001) + 0.5, 0.0, 1.0);
	vec2 inner = q - vec2(frame_w * 2.0);
	vec2 isz = sz - vec2(frame_w * 4.0);
	float text = 0.0;
	if (inner.x > 0.0 && inner.y > 0.0 && inner.x < isz.x && inner.y < isz.y) {
		float rows = max(floor(isz.y / cell.y), 1.0);
		float ch = isz.y / rows;
		float cols = max(floor(isz.x / cell.x), 1.0);
		float cw = isz.x / cols;
		float r = floor(inner.y / ch);
		float c = floor(inner.x / cw);
		float h = sg_hash(vec2(c, r), seed);
		float h2 = sg_hash(vec2(c + 7.0, r + 3.0), seed);
		float present = step(h, fill);
		float cx = fract(inner.x / cw) * cw;
		float cy = fract(inner.y / ch) * ch;
		float run = sg_band(cx, cw * cell_gap * 0.5, cw * (1.0 - cell_gap * 0.5), fw.x);
		float thick = stroke_h * (0.6 + 0.8 * h2);
		float row = sg_band(cy, ch * 0.5 - thick * 0.5, ch * 0.5 + thick * 0.5, fw.y);
		text = present * run * row;
	}
	return max(frame_cov, text);
}

void fragment() {
	float g = 1.0;
	if (shape == 1) {
		float r = clamp(length(UV - vec2(0.5)) * 2.0, 0.0, 1.0);
		g = pow(1.0 - r, disc_power);
	} else if (shape == 2) {
		float t = mod(nr_clock(anim_t, anim_t_frozen), loop_s) / loop_s;
		float k = floor(mix(bursts.x, bursts.y + 1.0, clamp(cust.x, 0.0, 0.999)));
		float u = fract(t * k + cust.y);
		float burst = 1.0 - smoothstep(0.0, 0.14, u);
		float hum = 0.5 + 0.5 * sin(6.2831853 * (t * 4.0 + cust.y));
		g = burst * (0.6 + 0.4 * hum);
	}
	vec3 rgb = COLOR.rgb * emit * g * cust.z;
	if (shape == 3 || shape == 2) {
		float yw = 1.0;
		if (yield_range.x > 0.0) {
			float d = length(VERTEX);
			float k = clamp((yield_range.x - d) / max(yield_range.x - yield_range.y, 0.001), 0.0, 1.0);
			yw = 1.0 - k * k * (3.0 - 2.0 * k);
		}
		vec3 sc = max(lscale, vec3(0.0001));
		float front = step(0.5, abs(lnrm.z));
		vec2 p = lpos.xy * sc.xy;
		vec2 fw = vec2(fwidth(p.x), fwidth(p.y));
		float core = front * sg_core(p, sc.xy, cust.x, fw);
		if (shape == 3) {
			float panel = panel_level * (1.0 - bright_var * sg_hash(vec2(3.0, 5.0), cust.x)) * mix(side_dim, 1.0, front);
			float lvl = min(max(panel, core * core_level) * cust.z, core_max);
			rgb = COLOR.rgb * lvl * yw;
		} else {
			rgb *= (1.0 - core) * yw;
		}
	}
	ALBEDO = rgb * emission_multiplier * look_blend;
	ALPHA = 1.0;
}
