shader_type canvas_item;
// Reduce effects (rc_common): nothing here runs on TIME; the spread is driven by the view,
// which shows its end state at once under reduce effects.
#include "res://shaders/lib/rc_common.gdshaderinc"
// Territory colour change (Animation pass ANIM-5): NeonCity draws the NEW baked city as
// usual and the OLD image on a layer above it with this shader, which masks the old one
// away as the new tint spreads from the Sites that changed owner (the same formula as
// InfluenceSpread.reveal_at: Manhattan street distance in grid lots, plus a per-block
// jitter so whole blocks turn at once). mode 0: the old image, masked; mode 1: the
// spreading front's glow only (a light band in the new owner's colour).

uniform int mode = 0;
// Local px of grid point (0, 0) under the city's camera, and the iso tile size (px).
uniform vec2 cam = vec2(0.0);
uniform vec2 tile = vec2(34.0, 17.0);
uniform vec2 origins[4];
uniform int origin_count = 0;
// The front's radius (lots), its soft edge (lots) and the cross-fade of the rest (0..1).
uniform float radius = 0.0;
uniform float feather = 1.5;
uniform float fade = 0.0;
uniform vec4 front_color : source_color = vec4(1.0, 0.24, 0.66, 1.0);
uniform float front_alpha = 0.5;
// ANIM-R2 R7: the lasting tint over the district the front has crossed (mode 1), in the new
// owner's colour; it stays after the spread (the front's band fades, the wash does not).
uniform float wash = 0.0;
// Art pass W7 (ART_BIBLE 9.3, critique gifs/16): the lasting wash is a CELL_TURF hatch, not a
// flat fill (acid over a green district read as muddy khaki): 45-degree lines `hatch_px`
// apart (screen px), `hatch_width` px wide. 0 spacing draws the old flat wash.
uniform float hatch_px = 7.0;
uniform float hatch_width = 1.6;
// How strong the lasting wash is (W7 turns it down: the claimed buildings carry their own hatch).
uniform float wash_gain = 1.0;

varying vec2 local_pos;

void vertex() {
	local_pos = VERTEX;
}

float jitter(vec2 lot) {
	return fract(sin(lot.x * 12.9898 + lot.y * 78.233) * 43758.5453);
}

void fragment() {
	float dd = (local_pos.x - cam.x) / tile.x;
	float ss = (local_pos.y - cam.y) / tile.y;
	vec2 g = vec2((ss + dd) * 0.5, (ss - dd) * 0.5);
	float d = 1e6;
	for (int k = 0; k < 4; k++) {
		if (k < origin_count) {
			vec2 q = abs(g - origins[k]);
			d = min(d, q.x + q.y);
		}
	}
	d += jitter(floor(g)) * feather;
	float spread = radius > 0.0 ? 1.0 - smoothstep(radius - feather, radius, d) : 0.0;
	float reveal = max(spread, fade);
	if (mode == 0) {
		COLOR.a *= 1.0 - reveal;
	} else {
		float band = radius > 0.0 ? 1.0 - smoothstep(0.0, feather, abs(d - radius)) : 0.0;
		float lines = 1.0;
		if (hatch_px > 0.0) {
			float u = fract((FRAGCOORD.x + FRAGCOORD.y) / hatch_px) * hatch_px;
			lines = 1.0 - smoothstep(hatch_width * 0.5, hatch_width * 0.5 + 1.0, abs(u - hatch_px * 0.5));
		}
		COLOR = vec4(front_color.rgb, clamp(band * front_alpha * (1.0 - fade) + spread * wash * lines * wash_gain, 0.0, 1.0));
	}
}
