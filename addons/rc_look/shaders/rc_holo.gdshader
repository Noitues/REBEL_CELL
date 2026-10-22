// LOOK-TOOLBOX module 15: the decrypted holo material (see rc_holo.gdshaderinc). Set up through RcLookHolo.apply,
// never by hand. mode 0 = glass under the words, mode 1 = scanlines and bands over them.
shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_look.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_holo.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, repeat_disable, filter_linear_mipmap;

uniform int mode = 0;
uniform vec4 panel = vec4(0.0, 0.0, 100.0, 100.0);
uniform vec4 tint : source_color = vec4(0.24, 1.0, 0.545, 1.0);
uniform vec4 deep : source_color = vec4(0.008, 0.012, 0.039, 1.0);
uniform float fill_share = 0.2;
uniform float fill_foot_share = 0.7;
uniform float glass_alpha = 0.6;
uniform float city_dim = 0.5;
uniform float blur_lod = 2.5;
uniform float scan_px = 4.0;
uniform float scan_strength = 0.16;
uniform float band_count = 3.0;
uniform float band_strength = 0.26;
uniform float band_trail = 2.5;
uniform float band_seconds = 6.0;
uniform float band_roll = 1.0;
uniform float band_pose = 0.35;
uniform float edge_px = 2.0;
uniform float edge_glow_px = 7.0;
uniform float edge_glow_strength = 0.45;
uniform float edge_lift = 0.45;
uniform float split_px = 2.5;

varying vec2 local_px;

void vertex() {
	local_px = VERTEX;
}

void fragment() {
	vec2 p = local_px;
	float sd = rcl_holo_sd(p, panel);
	vec4 col = vec4(0.0);
	float t = clamp((p.y - panel.y) / max(panel.w, 1.0), 0.0, 1.0);
	if (mode == 0) {
		if (sd <= 0.0) {
			vec3 g = rcl_holo_body(tint.rgb, deep.rgb, fill_share, fill_foot_share, t);
			if (blur_lod > 0.0) {
				// translucent glass: the blurred, dimmed city behind, the glass over it
				vec3 city = textureLod(screen_tex, SCREEN_UV, blur_lod).rgb * city_dim;
				col = vec4(mix(city, g, glass_alpha), 1.0);
			} else {
				col = vec4(g, glass_alpha);
			}
		}
		// the edge glow, then the edge in three offset channels (edge only)
		vec3 ink = rcl_holo_edge_ink(tint.rgb, edge_lift);
		float glow = rcl_holo_glow(p, panel, edge_glow_px) * edge_glow_strength;
		if (sd > 0.0) {
			col = vec4(tint.rgb, glow);
		} else {
			col.rgb = mix(col.rgb, tint.rgb, glow * 0.5);
		}
		vec4 e = rcl_holo_split_edge(p, panel, edge_px, split_px, ink);
		col = vec4(mix(col.rgb, e.rgb, e.a), max(col.a, e.a));
	} else if (sd <= 0.0) {
		float line = rcl_holo_scan(p.y - panel.y, scan_px);
		float phase = band_roll > 0.5 ? rc_time(TIME) / max(band_seconds, 0.1) : band_pose;
		float bands = rcl_holo_bands(t, band_count, phase, band_trail);
		vec3 ink = rcl_holo_edge_ink(tint.rgb, edge_lift * 0.6);
		col = vec4(tint.rgb, scan_strength * line);
		col = mix(col, vec4(ink, 1.0), bands * band_strength);
		col.a = max(col.a, bands * band_strength);
	}
	COLOR = col;
}
