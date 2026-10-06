// Combat backdrop (ART_BIBLE v2 3.1, 3.14): the target building's close-up still, softened and
// darkened in a pool behind each wheel, with darker bands under the top bar and the hand. Fight won
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
// Pool darkening (0.45 leaves 55 %) and the blur radius inside a pool (still texels).
uniform float pool_dark : hint_range(0.0, 1.0) = 0.45;
uniform float pool_blur = 2.5;
// Pool edge: exp(-(d / r) ^ pool_falloff).
uniform float pool_falloff = 4.0;
// The still's aspect (width / height), to keep pools round.
uniform float aspect = 1.7777778;
// Darker bands: the top bar (top share of the height) and the hand (bottom share), and how dark.
uniform float top_band = 0.1;
uniform float bottom_band = 0.24;
uniform float band_dark : hint_range(0.0, 1.0) = 0.4;

// Parity fix S-ARENA: the city close-up's canvas grade (CityConfig backdrop_exposure /
// backdrop_tint), city only (the stills are the concept already), before pools and bands: the
// value V (brightest channel) goes to 1 - (1 - V)^exposure, hue kept (no neon clips), then the
// tint and the saturation (toward its grey; the concept's calmer rainy city). CombatBackdrop.graded
// mirrors it for the tests.
uniform bool city_grade = false;
uniform float city_exposure = 1.0;
uniform vec3 city_tint = vec3(1.0);
uniform float city_saturation = 1.0;

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
	if (city_grade) {
		base.rgb = graded(base.rgb);
	}
	float pool = max(max(pool_at(UV, pool_a), pool_at(UV, pool_b)), max(pool_at(UV, pool_c), pool_at(UV, pool_d)));
	vec3 col = base.rgb;
	if (pool > 0.01) {
		vec3 soft = base.rgb;
		for (int k = 0; k < 8; k++) {
			float a = float(k) * 0.785398;
			soft += graded(texture(TEXTURE, UV + vec2(cos(a), sin(a)) * texel * pool_blur).rgb);
		}
		soft /= 9.0;
		col = mix(col, soft, pool);
		col *= 1.0 - pool_dark * pool;
	}
	float top = 1.0 - smoothstep(0.0, top_band, UV.y);
	float bottom = smoothstep(1.0 - bottom_band, 1.0, UV.y);
	col *= 1.0 - band_dark * max(top, bottom);
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
