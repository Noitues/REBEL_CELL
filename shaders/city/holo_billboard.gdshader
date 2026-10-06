// ART-5 5c: holo billboards (ART_BIBLE §4.2 layer: "illegible panels cycling with a wipe,
// dropout, jitter"; round 24 make_boards). A unit quad turned about Y to face the camera,
// `size` BU, drawing a panel of illegible glyph blocks in its colour with scanlines and a
// bright frame. Each `hold` seconds the next panel wipes in over `wipe` seconds; now and
// then a frame drops out (`dropout` share) and the panel jitters sideways. `steady` (reduce
// motion / reduce effects) holds one panel, no dropout or jitter. INSTANCE_CUSTOM = (phase,
// first panel, 0, 0); COLOR = the panel colour. Additive, depth-tested.
shader_type spatial;
render_mode unshaded, blend_add, cull_disabled, depth_draw_never, specular_disabled, fog_disabled;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform float clock = 0.0;
uniform float hold = 3.2;
uniform float wipe = 0.24;
uniform float dropout = 0.06;
uniform bool steady = false;
uniform vec2 size = vec2(6.0, 3.6);
uniform float gain = 1.6;
uniform float scanlines = 22.0;
uniform int panels = 4;
uniform float jitter = 0.04;
uniform sampler2D panel_tex : filter_linear, repeat_disable;

varying float v_panel;
varying float v_next;
varying float v_wipe;
varying float v_drop;

float h11(float p) {
	return fract(sin(p * 127.1) * 43758.5453);
}

float h21(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void vertex() {
	vec3 o = MODEL_MATRIX[3].xyz;
	vec3 back = INV_VIEW_MATRIX[2].xyz;
	vec3 fwd = normalize(vec3(back.x, 0.0, back.z) + vec3(1e-5, 0.0, 0.0));
	vec3 right = vec3(fwd.z, 0.0, -fwd.x);
	float t = steady ? 0.0 : clock / max(hold, 0.01) + INSTANCE_CUSTOM.x;
	float k = floor(t);
	float within = (t - k) * hold;
	v_panel = mod(INSTANCE_CUSTOM.y + k, float(panels));
	v_next = mod(v_panel + 1.0, float(panels));
	v_wipe = steady ? 0.0 : clamp((within - (hold - wipe)) / max(wipe, 0.001), 0.0, 1.0);
	float tick = floor(clock * 12.0) + INSTANCE_CUSTOM.x * 97.0;
	v_drop = (!steady && h11(tick) < dropout) ? 0.25 : 1.0;
	float jx = steady ? 0.0 : (h11(tick + 3.0) < dropout * 2.0 ? (h11(tick + 7.0) - 0.5) * jitter : 0.0);
	vec3 wp = o + right * (VERTEX.x + jx) * size.x + vec3(0.0, 1.0, 0.0) * VERTEX.y * size.y;
	POSITION = PROJECTION_MATRIX * VIEW_MATRIX * vec4(wp, 1.0);
}

// Round 26's own billboard panels (assets/city/billboards/panels.png, from cm._billboard_tex): one
// atlas cell per panel id. R = the lightened-colour mask (c2 = col * 0.5 + 0.5), A = the panel alpha
// (pictogram, glyph rows, frame and the concept's half-alpha scanline rows are all in the texture).
vec4 panel(vec2 uv, float id) {
	vec2 auv = vec2((clamp(uv.x, 0.0, 1.0) + id) / float(panels), clamp(uv.y, 0.0, 1.0));
	return texture(panel_tex, auv);
}

void fragment() {
	vec2 uv = UV;
	uv.y = 1.0 - uv.y;
	float id = uv.x < v_wipe ? v_next : v_panel;
	vec4 t = panel(uv, id);
	float wipe_line = (v_wipe > 0.0 && v_wipe < 1.0) ? smoothstep(0.03, 0.0, abs(uv.x - v_wipe)) : 0.0;
	float scan = 0.85 + 0.15 * sin(uv.y * scanlines * PI * 2.0);
	vec3 col = mix(COLOR.rgb, COLOR.rgb * 0.5 + 0.5, t.r);
	float a = (t.a * scan + wipe_line) * v_drop;
	ALBEDO = col * gain;
	ALPHA = clamp(a, 0.0, 1.0);
}
