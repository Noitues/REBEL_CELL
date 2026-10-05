// ART-9 4B (ART_BIBLE v2 §4.12, round 38 NOTES "The feed"): the operative's CRT comm feed.
// One shader for every state and context: a pre-rendered cel bust (an atlas cell of
// assets/portraits/busts_<class>.png) over the feed's own backdrop, with
//   mode     0 idle, 1 talk, 2 hurt, 3 stationed, 4 dead, 5 recruit, 6 print, 7 voice;
//   tint     the class colour (rim haze; the stationed monochrome; the voice trace);
//   split    RGB split (px); tear: torn scan bands (share of the feed's height);
//   noise    static (0..1); fps_hold: the frame rate the stationed feed steps at.
// `feed_time` is the script's clock (PortraitFeed advances it only while its motion
// entries play); under reduce effects rc_live() also stops it here, so the feed is a still.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D bust : filter_linear, repeat_disable;
// The bust's cell in the atlas (uv x, y, w, h) and where it sits in the feed (feed uv).
uniform vec4 bust_uv = vec4(0.0, 0.0, 1.0, 1.0);
uniform vec4 bust_box = vec4(0.0, 0.0, 1.0, 1.0);
uniform bool has_bust = true;
uniform int mode = 0;
uniform vec4 tint : source_color = vec4(0.36, 0.88, 1.0, 1.0);
uniform vec4 backdrop : source_color = vec4(0.03, 0.04, 0.07, 1.0);
uniform vec4 paper : source_color = vec4(0.83, 0.78, 0.68, 1.0);
uniform vec4 alarm : source_color = vec4(0.91, 0.08, 0.12, 1.0);
uniform float split = 1.5;
uniform float tear = 0.0;
uniform float noise = 0.04;
uniform float fps_hold = 0.0;
uniform float feed_time = 0.0;
uniform float roll_period = 4.0;
uniform float dim = 0.0;
uniform vec2 rect_size = vec2(240.0, 266.0);

float hash12(vec2 p) {
	vec3 p3 = fract(vec3(p.xyx) * 0.1031);
	p3 += dot(p3, p3.yzx + 33.33);
	return fract((p3.x + p3.y) * p3.z);
}

float luma(vec3 c) {
	return dot(c, vec3(0.299, 0.587, 0.114));
}

vec4 bust_at(vec2 uv) {
	if (!has_bust) {
		return vec4(0.0);
	}
	vec2 b = (uv - bust_box.xy) / bust_box.zw;
	if (b.x < 0.0 || b.x > 1.0 || b.y < 0.0 || b.y > 1.0) {
		return vec4(0.0);
	}
	// Half a texel inside the cell so the neighbours never bleed in.
	vec2 px = 0.5 / vec2(textureSize(bust, 0));
	vec2 a = clamp(bust_uv.xy + b * bust_uv.zw, bust_uv.xy + px, bust_uv.xy + bust_uv.zw - px);
	return texture(bust, a);
}

// The feed's backdrop: dark glass, a soft haze of the class colour behind the head, a faint
// grid (the comm feed's "room").
vec3 feed_back(vec2 uv) {
	vec3 c = backdrop.rgb * (1.15 - uv.y * 0.35);
	float haze = smoothstep(0.75, 0.0, distance(uv, vec2(0.48, 0.38)));
	c += tint.rgb * haze * 0.10;
	c += vec3(0.5, 0.55, 0.65) * smoothstep(0.55, 0.0, abs(uv.x - 0.3)) * smoothstep(0.0, 0.6, uv.y) * 0.035;
	vec2 g = fract(uv * rect_size / 14.0);
	float grid = max(step(g.x, 1.0 / 14.0), step(g.y, 1.0 / 14.0));
	c += tint.rgb * grid * 0.025;
	return c;
}

vec3 composite(vec2 uv, float t) {
	vec4 b = bust_at(uv);
	return mix(feed_back(uv), b.rgb, b.a);
}

void fragment() {
	vec2 uv = UV;
	float live = rc_live();
	float t = feed_time * live;
	if (mode == 3 && fps_hold > 0.0) {
		t = floor(t * fps_hold) / fps_hold;
	}
	vec2 px = 1.0 / rect_size;
	vec3 col;
	if (mode == 7) {
		// DISPATCH: no face. A red voice trace on black (round 38 contexts), its layers
		// drifting with the clock; the waveform's envelope peaks at the centre.
		col = vec3(0.012, 0.004, 0.006);
		vec2 g = fract(uv * rect_size / 16.0);
		col += alarm.rgb * max(step(g.x, 1.0 / 16.0), step(g.y, 1.0 / 16.0)) * 0.05;
		float env = exp(-pow((uv.x - 0.5) * 3.2, 2.0));
		for (int k = 0; k < 4; k++) {
			float fk = float(k);
			float ph = t * (2.2 + fk * 0.5) + fk * 0.9;
			float w = sin(uv.x * (22.0 + fk * 3.0) + ph) * 0.6 + sin(uv.x * (47.0 - fk * 4.0) - ph * 1.3) * 0.22;
			float y = 0.5 - w * env * (0.36 - fk * 0.05);
			float d = abs(uv.y - y) * rect_size.y;
			// The voice itself bright and glowing; its echoes thin and faint.
			float core = (k == 0) ? 1.0 : 0.22;
			float width = (k == 0) ? 1.8 : 1.1;
			col += alarm.rgb * core * (smoothstep(width, 0.0, d) + smoothstep(10.0, 0.0, d) * (k == 0 ? 0.35 : 0.0));
		}
		col += alarm.rgb * smoothstep(1.0, 0.0, abs(uv.y - 0.5) * rect_size.y) * 0.25;
	} else {
		// Torn scan bands: a few rows slide sideways (hurt, and a little for dead).
		float shift = 0.0;
		if (tear > 0.0) {
			float row = floor(uv.y * rect_size.y / 6.0);
			float r = hash12(vec2(row, floor(t * 9.0)));
			shift = (r > 1.0 - tear * 3.0) ? (hash12(vec2(row, 7.0 + floor(t * 9.0))) - 0.5) * 0.09 : 0.0;
		}
		vec2 suv = uv + vec2(shift, 0.0);
		float s = split * px.x;
		vec3 c = composite(suv, t);
		col = vec3(composite(suv + vec2(s, 0.0), t).r, c.g, composite(suv - vec2(s, 0.0), t).b);
		if (mode == 6) {
			// Print (corp paper): a flat photo backdrop, desaturated and warmed, grain.
			vec4 b = bust_at(uv);
			vec3 p = mix(paper.rgb * 0.62, b.rgb, b.a);
			float l = luma(p);
			col = mix(vec3(l), p, 0.42) * vec3(1.05, 0.98, 0.86);
			col *= 0.92 + hash12(floor(uv * rect_size)) * 0.12;
			col = mix(col, paper.rgb * 0.5, smoothstep(0.35, 0.9, distance(uv, vec2(0.5))) * 0.35);
		} else {
			if (mode == 2) {
				// Hurt: a red wash.
				col = mix(col, vec3(luma(col) * 1.6, luma(col) * 0.32, luma(col) * 0.26) + alarm.rgb * 0.08, 0.62);
			} else if (mode == 3) {
				// Stationed: class-colour monochrome.
				col = tint.rgb * (luma(col) * 1.7 + 0.04);
			} else if (mode == 4 || mode == 5) {
				col = vec3(luma(col)) * (mode == 4 ? 0.6 : 0.95);
			}
			// The feed's gain (the busts read lit on the glass, as on the round 39 sheet).
			col *= 1.12;
			// Scanlines (3 px) and a slow rolling bar.
			float line = step(0.5, fract(FRAGCOORD.y / 3.0));
			col *= 1.0 - 0.16 * line;
			float roll = fract(t / max(roll_period, 0.01));
			col += vec3(0.06) * smoothstep(0.06, 0.0, abs(uv.y - roll)) * (mode == 4 ? 0.0 : 1.0);
			// Static.
			float n = 0.22 + 0.5 * hash12(floor(uv * rect_size * 0.5) + floor(t * 24.0) * 13.0);
			col = mix(col, vec3(n), clamp(noise, 0.0, 1.0));
			// Vignette, the glass edge.
			col *= 1.0 - smoothstep(0.5, 0.8, distance(uv, vec2(0.5))) * 0.3;
		}
	}
	col = mix(col, vec3(luma(col)) * 0.45, clamp(dim, 0.0, 1.0));
	COLOR = vec4(col, 1.0) * COLOR;
}
