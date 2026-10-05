// REBEL_CELL material kit (ART-1 1B): light spill, 2D (ART_BIBLE v2 §1.2 "World": bloom and
// light spill from glowing elements onto walls and streets; round 3 combined_v2 `kit.py`
// light_spill: the blurred emitter colour multiplies the base (it lights the facets) plus a
// little fill, through a soft tonemap shoulder, and the emitter itself is not re-lit).
// Drawn as a rect round its source over what is already on screen (the screen texture):
// the source is a rounded rect `src_size` at the rect's centre, the light falls off over
// `reach` px. `gain` is the per-screen tuning (round 3: combat 1.15, city 0.38, shop 1.2).
// The breathe (light_spill_breathe) rides TIME and stops under reduce effects.
shader_type canvas_item;
render_mode blend_mix;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear_mipmap;
uniform vec4 color : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform vec2 src_size = vec2(60.0, 300.0);
uniform float src_corner = 12.0;
uniform float reach = 140.0;
uniform float gain = 1.0;
// Shares of the light that multiply the base (lights the facets) and that add as haze.
uniform float multiply_k = 1.9;
uniform float haze_k = 0.28;
uniform float breathe_amp = 0.0;
uniform float breathe_period = 3.2;
// The rect's size (px): drawn centred on the source.
uniform vec2 rect_size = vec2(400.0, 600.0);

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

float sd_box(vec2 p, vec2 b, float r) {
	vec2 q = abs(p) - b + vec2(r);
	return length(max(q, vec2(0.0))) + min(max(q.x, q.y), 0.0) - r;
}

void fragment() {
	vec2 p = local_px;  // the rect is drawn centred on the source (node origin)
	float d = sd_box(p, src_size * 0.5, src_corner);
	// two falloffs (a tight one and a wide one), like the concept's two blurs
	float near_l = exp(-max(d, 0.0) / max(reach * 0.25, 1.0)) * 1.2;
	float far_l = exp(-max(d, 0.0) / max(reach * 0.75, 1.0)) * 1.5;
	// fades out before the drawn rect's edge (no seam)
	float light = (near_l + far_l) * 0.6 * (1.0 - smoothstep(reach * 0.6, reach, d));
	float br = 1.0 + breathe_amp * sin(rc_time(TIME) * 6.2832 / max(breathe_period, 0.1)) * rc_live();
	light *= gain * br;
	vec3 base = texture(screen_tex, SCREEN_UV).rgb;
	// the emitter itself (bright, saturated pixels) is not re-lit; the facets between its
	// tubes are
	float mx = max(max(base.r, base.g), base.b);
	float mn = min(min(base.r, base.g), base.b);
	float emit = clamp((mx - 0.55) / 0.30, 0.0, 1.0) * clamp(((mx - mn) / max(mx, 0.0001) - 0.2) / 0.3, 0.0, 1.0);
	float keep = 1.0 - clamp(emit * 1.5, 0.0, 1.0);
	vec3 add = (base * color.rgb * light * multiply_k + color.rgb * light * haze_k) * keep;
	// tonemap shoulder on the added light only
	add = add / (1.0 + add);
	vec3 lit = base + add * (vec3(1.0) - base);
	COLOR = vec4(lit, smoothstep(0.0, 0.02, light));
}
