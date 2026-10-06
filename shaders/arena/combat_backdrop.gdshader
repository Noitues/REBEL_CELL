// Combat backdrop (ART_BIBLE v2 3.1, 3.14): the target building's close-up still, softened in a pool
// behind each wheel (B1a: the pools' darkening and the bands under the top bar and the hand are the
// shared UiScrimPools layer's, drawn over this backdrop and its Heat lights). Fight won
// (D17): the district dims and the target's own lights turn Cell colours (lime, pink hazard stripes).
// Static: nothing here animates on its own (`won` is tweened by the view, its end state under reduce
// effects); rc_common is included so the convention holds if a part ever moves.
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

// R = the target's silhouette, G = the target's own lights (same framing as the still).
uniform sampler2D won_mask : filter_linear, hint_default_black;
uniform float won : hint_range(0.0, 1.0) = 0.0;
uniform float district_dim : hint_range(0.0, 1.0) = 0.62;
uniform vec4 lime : source_color = vec4(0.83, 1.0, 0.0, 1.0);
uniform vec4 pink : source_color = vec4(1.0, 0.24, 0.66, 1.0);
// Hazard stripes: period (share of the still's width) and the pink share of each period.
uniform float stripe_period = 0.022;
uniform float stripe_share : hint_range(0.0, 1.0) = 0.4;
// The lights mask's ramp (G) and the outline's reach (mask texels).
uniform float light_from = 0.08;
uniform float light_to = 0.45;
uniform float outline_px = 1.5;
// ART-8 8w (D17 on the city): no won mask (the live city close-up): the target is the ellipse of
// radius keep_radius (share of the width) round keep_at (UV); the district outside it dims, and the
// target's own lights come from the city (SiteWonLights), not from this shader.
uniform bool use_mask = true;
uniform vec2 keep_at = vec2(0.5, 0.5);
uniform float keep_radius = 0.16;
// Up to four wheel pools: xy = centre (still UV), z = radius (share of the still's width).
uniform vec3 pool_a = vec3(0.0, 0.0, 0.0);
uniform vec3 pool_b = vec3(0.0, 0.0, 0.0);
uniform vec3 pool_c = vec3(0.0, 0.0, 0.0);
uniform vec3 pool_d = vec3(0.0, 0.0, 0.0);
// The blur radius inside a pool (still texels).
uniform float pool_blur = 2.5;
// Pool edge: exp(-(d / r) ^ pool_falloff).
uniform float pool_falloff = 4.0;
// The still's aspect (width / height), to keep pools round.
uniform float aspect = 1.7777778;

// Parity fix S-ARENA: the city close-up's canvas grade (CityConfig backdrop_exposure /
// backdrop_tint), city only (the stills are the concept already), before the pools: the
// value V (brightest channel) goes to 1 - (1 - V)^exposure, hue kept (no neon clips), then the
// tint and the saturation (toward its grey; the concept's calmer rainy city). CombatBackdrop.graded
// mirrors it for the tests.
uniform bool city_grade = false;
uniform float city_exposure = 1.0;
uniform vec3 city_tint = vec3(1.0);
uniform float city_saturation = 1.0;
// S-ARENA round 2: the subject's focus (UV), its ellipse radius (share of the width), the blur
// (texels) and the dim (share taken off) outside it (CityConfig backdrop_focus_*).
uniform vec2 focus_at = vec2(0.5, 0.5);
uniform float focus_radius = 0.24;
uniform float focus_blur = 2.0;
uniform float focus_dim = 0.0;
uniform float focus_lift = 1.0;
// B2 (art director): the focus ellipse's axes (x = 1: focus_radius across; y: its height over
// its width), so a tall Site block is lit as itself.
uniform vec2 focus_axes = vec2(1.0, 1.0);
// B2 b (art director): a Site's subject block is lit by its own neon, not a flat lift: inside the
// focus its windows (the bright, lit pixels from window_from up) x window_gain, a rim of `neon` (the
// district / corp colour) on its edges (the luminance edge, rim_gain), and the street in front of
// it (under subject_rect's foot, street_reach of the view's height down) catching that colour.
uniform bool subject_on = false;
uniform vec4 subject_rect = vec4(0.0);
uniform vec4 neon : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform float window_from = 0.45;
uniform float window_gain = 2.0;
// The block's unlit facades inside the focus (the neon, not a lift, lights it).
uniform float subject_base = 0.72;
uniform float rim_gain = 0.55;
uniform float rim_edge = 0.09;
uniform float street_gain = 0.35;
uniform float street_reach = 0.12;

vec3 graded(vec3 c) {
	if (!city_grade) {
		return c;
	}
	float v = max(max(c.r, c.g), c.b);
	float k = (1.0 - pow(1.0 - clamp(v, 0.0, 1.0), city_exposure)) / max(v, 0.0001);
	vec3 g = clamp(c * k * city_tint, 0.0, 1.0);
	return mix(vec3(dot(g, vec3(0.2126, 0.7152, 0.0722))), g, city_saturation);
}

float pool_at(vec2 uv, vec3 p) {
	if (p.z <= 0.0) {
		return 0.0;
	}
	vec2 d = (uv - p.xy) * vec2(1.0, 1.0 / aspect);
	return exp(-pow(length(d) / p.z, pool_falloff));
}

void fragment() {
	vec2 texel = TEXTURE_PIXEL_SIZE;
	vec4 base = texture(TEXTURE, UV);
	vec3 raw = base.rgb;
	if (city_grade) {
		base.rgb = graded(base.rgb);
	}
	float pool = max(max(pool_at(UV, pool_a), pool_at(UV, pool_b)), max(pool_at(UV, pool_c), pool_at(UV, pool_d)));
	// S-ARENA round 2: outside the subject's ellipse the close-up softens and dims (focus_dim 0: off).
	float away = 0.0;
	if (focus_dim > 0.0) {
		vec2 df = (UV - focus_at) * vec2(1.0, 1.0 / aspect) / max(focus_axes, vec2(0.001));
		away = 1.0 - exp(-pow(length(df) / max(focus_radius, 0.001), pool_falloff));
	}
	vec3 col = base.rgb;
	float soften = max(pool, away);
	if (soften > 0.01) {
		float br = max(pool > 0.01 ? pool_blur : 0.0, focus_blur * away);
		vec3 soft = base.rgb;
		for (int k = 0; k < 8; k++) {
			float a = float(k) * 0.785398;
			soft += graded(texture(TEXTURE, UV + vec2(cos(a), sin(a)) * texel * br).rgb);
		}
		soft /= 9.0;
		col = mix(col, soft, soften);
		col *= 1.0 - focus_dim * away;
	}
	if (focus_dim > 0.0 && !subject_on) {
		col = min(col * mix(focus_lift, 1.0, away), vec3(1.0));
	}
	if (subject_on) {
		float inside = 1.0 - away;
		float v = max(max(raw.r, raw.g), raw.b);
		float win = smoothstep(window_from, 1.0, v);
		col = min(col * mix(mix(1.0, subject_base, inside), window_gain, win * inside), vec3(1.0));
		// The rim: the luminance edges of the block, in its neon.
		vec2 o = texel * 1.5;
		float lx = dot(texture(TEXTURE, UV + vec2(o.x, 0.0)).rgb - texture(TEXTURE, UV - vec2(o.x, 0.0)).rgb, vec3(0.333));
		float ly = dot(texture(TEXTURE, UV + vec2(0.0, o.y)).rgb - texture(TEXTURE, UV - vec2(0.0, o.y)).rgb, vec3(0.333));
		float edge = smoothstep(rim_edge * 0.5, rim_edge, length(vec2(lx, ly)));
		vec2 lo = subject_rect.xy;
		vec2 hi = subject_rect.xy + subject_rect.zw;
		float in_box = step(lo.x, UV.x) * step(UV.x, hi.x) * step(lo.y, UV.y) * step(UV.y, hi.y);
		col += neon.rgb * rim_gain * edge * in_box * inside;
		// The street in front catches it: under the block's foot, fading down and to the sides.
		float below = (UV.y - hi.y) / max(street_reach, 0.001);
		float across = abs(UV.x - (lo.x + hi.x) * 0.5) / max((hi.x - lo.x) * 0.5, 0.001);
		float street = step(0.0, below) * (1.0 - clamp(below, 0.0, 1.0)) * (1.0 - smoothstep(0.7, 1.3, across));
		col += neon.rgb * street_gain * street;
		col = min(col, vec3(1.0));
	}
	vec4 m = texture(won_mask, UV);
	if (won > 0.0 && !use_mask) {
		vec2 dk = (UV - keep_at) * vec2(1.0, 1.0 / aspect);
		float keep = exp(-pow(length(dk) / max(keep_radius, 0.001), pool_falloff));
		col = mix(col, col * district_dim, won * (1.0 - keep));
	} else if (won > 0.0) {
		float sil = clamp(m.r, 0.0, 1.0);
		col = mix(col, col * district_dim, won * (1.0 - sil));
		float lum = max(max(base.r, base.g), base.b);
		// The target's own lights: lime, with pink hazard stripes across them.
		float stripe = step(1.0 - stripe_share, fract((UV.x * aspect + UV.y) / (stripe_period * aspect)));
		vec3 cell = mix(lime.rgb, pink.rgb, stripe) * (0.7 + 0.6 * lum);
		col = mix(col, cell, won * smoothstep(light_from, light_to, m.g));
		// Lime outlines: the silhouette's edge.
		vec2 mt = 1.0 / vec2(textureSize(won_mask, 0)) * outline_px;
		float e = 0.0;
		e = max(e, abs(texture(won_mask, UV + vec2(mt.x, 0.0)).r - sil));
		e = max(e, abs(texture(won_mask, UV - vec2(mt.x, 0.0)).r - sil));
		e = max(e, abs(texture(won_mask, UV + vec2(0.0, mt.y)).r - sil));
		e = max(e, abs(texture(won_mask, UV - vec2(0.0, mt.y)).r - sil));
		col = mix(col, lime.rgb, won * smoothstep(0.25, 0.6, e));
	}
	COLOR = vec4(col, base.a) * COLOR;
}
