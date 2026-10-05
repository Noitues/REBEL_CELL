// ART-0 audit B1: the Heat glitch Options extra (ART_BIBLE v2 §3.15, §5.5, Appendix B;
// round 18-22 heat_glitch). One post pass over the combat world (the city backdrop and its
// Heat lights), drawn under the wheels, the FX and the HUD, so no value is ever touched.
// HeatGlitchLayer drives every uniform: a burst's envelope `env`, its progress `q` and the
// glitch state `seed` (stepped, so a state holds a couple of frames), and the band's layers
// (each band adds to the one before):
//   COOL     a luminance dip (`dip`) and two thin lines jittering sideways;
//   NOTICED  + chromatic tears: bands slip sideways with an RGB split;
//   FLAGGED  + a scanline roll (a bright band, `roll_gain`, runs top to bottom) + macroblocks
//            copied, posterised and pulled to the corp colour;
//   HUNTED   + a vertical hold slip, a whole-screen RGB split, ambient scanlines.
// The static corp edge tint (`edge`) is what remains when the glitch is off (HUNTED only).
// The flash limiter zeroes `dip` and `roll_gain` (the glitch then adds no light). Animated
// strengths go through rc_live(): nothing moves under reduce effects.
shader_type canvas_item;
render_mode unshaded;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_nearest;
uniform float env = 0.0;
uniform float q = 0.0;
uniform float seed = 0.0;
uniform float dip = 0.0;
uniform float jitter_px = 2.0;
uniform float tears = 0.0;
uniform float tear_px = 0.0;
uniform float tear_split_px = 0.0;
uniform float roll = 0.0;
uniform float roll_gain = 0.0;
uniform float roll_dark = 0.28;
uniform float roll_px = 70.0;
uniform float blocks = 0.0;
uniform vec4 block_color : source_color = vec4(1.0, 0.47, 0.19, 1.0);
uniform float slip_px = 0.0;
uniform float split_px = 0.0;
uniform float scan = 0.0;
uniform float edge = 0.0;
uniform vec4 edge_color : source_color = vec4(1.0, 0.47, 0.19, 1.0);

float h1(float n) {
	return fract(sin(n * 127.1 + 311.7) * 43758.5453);
}

void fragment() {
	vec2 px = SCREEN_PIXEL_SIZE;
	vec2 size = 1.0 / px;
	vec2 p = SCREEN_UV * size;
	float e = clamp(env, 0.0, 1.0) * rc_live();
	float s = floor(seed);
	vec2 sp = p;
	float split = 0.0;
	float w = 0.0;
	if (e > 0.0) {
		// COOL: two thin lines jitter 1-2 px.
		for (int i = 0; i < 2; i++) {
			float y = h1(s * 7.0 + float(i)) * size.y;
			if (abs(p.y - y) < jitter_px * 0.5) {
				sp.x -= 1.0 + floor(h1(s + float(i) * 3.1) * jitter_px);
			}
		}
		// NOTICED+: chromatic tears.
		int n = int(tears * e);
		for (int i = 0; i < 24; i++) {
			if (i >= n) {
				break;
			}
			float fi = float(i);
			float hgt = 4.0 + floor(h1(s * 13.0 + fi * 1.7) * 40.0);
			float y0 = h1(s * 5.0 + fi * 2.3) * (size.y - hgt);
			if (p.y >= y0 && p.y < y0 + hgt) {
				sp.x -= (h1(s * 3.0 + fi * 4.1) * 2.0 - 1.0) * (tear_px * e + 2.0);
				split = max(split, max(1.0, tear_split_px * e));
			}
		}
		// HUNTED: the vertical hold slips mid-burst; the whole frame splits early on.
		if (q > 0.3 && q < 0.5) {
			sp.y -= slip_px;
		}
		if (q < 0.45 && split_px > 0.0) {
			split = max(split, split_px * e + 1.0);
		}
		// FLAGGED+: the roll, a band running top to bottom across the burst.
		if (roll > 0.0) {
			float cy = q * (size.y + 2.0 * roll_px) - roll_px;
			w = exp(-pow((p.y - cy) / roll_px, 2.0));
			sp.x += sin(p.y / 7.0) * 6.0 * w;
		}
	}
	vec2 uv = sp * px;
	vec3 col;
	col.r = texture(screen_tex, uv + vec2(split * px.x, 0.0)).r;
	col.g = texture(screen_tex, uv).g;
	col.b = texture(screen_tex, uv - vec2(split * px.x, 0.0)).b;
	// FLAGGED+: macroblocks mid-burst.
	if (blocks > 0.0 && e > 0.0 && q > 0.15 && q < 0.85) {
		vec2 cell = vec2(32.0, 16.0);
		vec2 c = floor(p / cell);
		// Counted against a 1920 x 1080 frame (the concept's), whatever the window.
		float total = (1920.0 / cell.x) * (1080.0 / cell.y);
		float pick = h1(c.x * 17.0 + c.y * 131.0 + s * 7.3);
		if (pick < blocks * e / total) {
			vec2 off = vec2(floor((h1(pick * 91.0) * 2.0 - 1.0) * 120.0), floor((h1(pick * 37.0) * 2.0 - 1.0) * 40.0));
			vec3 b = texture(screen_tex, (p + off) * px).rgb;
			b = clamp(floor(b * 4.0) / 4.0 + 0.24, 0.0, 1.0);
			col = mix(b, block_color.rgb, 0.5);
		}
	}
	if (w > 0.0) {
		float line = 1.0 - step(1.0, mod(floor(p.y), 3.0));
		col *= (1.0 + roll_gain * w) * (1.0 - roll_dark * line * w);
	}
	col *= 1.0 - dip * e;
	if (scan > 0.0) {
		col *= 1.0 - scan * rc_live() * (1.0 - step(1.0, mod(floor(p.y), 3.0)));
	}
	if (edge > 0.0) {
		vec2 d = abs(p - size * 0.5) / (size * 0.5);
		float k = pow(clamp((max(d.x, d.y) - 0.78) / 0.22, 0.0, 1.0), 1.6) * edge;
		col = mix(col, edge_color.rgb, k);
	}
	COLOR = vec4(col, 1.0);
}
