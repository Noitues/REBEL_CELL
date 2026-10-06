// ART-9 4A (ART_BIBLE v2 4.11 events, 1.2 "World ... event CAM feeds"): a security CAM feed of
// the city behind the event: the screen copy (the city, copied by the event's BackBufferCopy
// before the page draws) magnified from `src` (screen UV rect), graded toward the corp `tint`,
// with scanlines, grain and a slow roll bar. Under reduce effects the roll and grain stop (the
// static picture and its scanlines stay).
shader_type canvas_item;
#include "res://shaders/lib/rc_common.gdshaderinc"

uniform sampler2D screen_tex : hint_screen_texture, filter_linear;
uniform vec4 src = vec4(0.3, 0.3, 0.3, 0.3);
uniform vec4 tint : source_color = vec4(0.24, 1.0, 0.55, 1.0);
uniform float tint_mix : hint_range(0.0, 1.0) = 0.35;
uniform float speed = 0.08;
uniform float scan_strength : hint_range(0.0, 1.0) = 0.25;
uniform float grain : hint_range(0.0, 0.5) = 0.08;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	float t = rc_time(TIME);
	vec2 uv = src.xy + UV * src.zw;
	vec3 c = texture(screen_tex, uv).rgb;
	float lum = dot(c, vec3(0.299, 0.587, 0.114));
	c = mix(c, tint.rgb * (lum * 1.6 + 0.08), tint_mix);
	c *= 1.0 - scan_strength * step(0.5, fract(FRAGCOORD.y / 3.0));
	float roll = fract(t * speed);
	c += vec3(0.06) * smoothstep(0.06, 0.0, abs(UV.y - roll)) * rc_live();
	c += (hash(FRAGCOORD.xy + floor(t * 24.0)) - 0.5) * grain * rc_live();
	vec2 v = UV - 0.5;
	c *= 1.0 - dot(v, v) * 0.9;
	COLOR = vec4(c, 1.0);
}
