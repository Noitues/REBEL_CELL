shader_type spatial;
render_mode cull_back;
#include "res://shaders/lib/rc_common.gdshaderinc"
// LOOK Solace HQ: interior mapping of the Solace helix windows (art-pass hq NOTES v4, "Godot port"): one flat oval patch per window
// raycast into a box room. Vertex data: NORMAL = the window's outward normal, UV = (u, dz) in the window frame (u along the level
// axis tw = normal x up, dz up from the window's middle), UV2 = (atlas variant row, blind 0..1), COLOR = (tint rgb, lit).
// The atlas: 3240 x (420 x variants), five tiles per row (back 800 x 336, left 420 x 336, right 420 x 336, floor 800 x 420,
// ceiling 800 x 420 at x = 0 / 800 / 1220 / 1640 / 2440).

uniform sampler2D atlas : source_color, filter_linear_mipmap, repeat_disable;
uniform float variants = 6.0;
uniform float imap_k = 0.55;
uniform float emit_gain = 1.0;
uniform float room_hu = 10.0;      // half width (BU)
uniform float room_d = 10.5;       // depth
uniform float room_zb = -3.15;     // floor, relative to the window's middle
uniform float room_h = 8.4;
uniform float plane_dp = 1.45;
uniform float frost = 0.10;
uniform float unit_k = 1.0;        // city BU per plate (kit) unit: the patch's UV and the room constants are in plate units

varying vec3 w_nrm;
varying vec3 w_pos;

vec2 tile_uv(float x0, float w, float h, float s, float ty, float row) {
	float px = x0 + clamp(s, 0.0, 1.0) * w;
	float py = row * 420.0 + h - clamp(ty, 0.0, 1.0) * h;
	return vec2(px / 3240.0, py / (420.0 * variants));
}

void vertex() {
	w_nrm = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	w_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	bool ortho = PROJECTION_MATRIX[3][3] == 1.0;
	vec3 cam = INV_VIEW_MATRIX[3].xyz;
	vec3 V = ortho ? -normalize(INV_VIEW_MATRIX[2].xyz) : normalize(w_pos - cam);
	vec3 nw = normalize(w_nrm);
	vec3 tw = normalize(cross(nw, vec3(0.0, 1.0, 0.0)));
	float u = UV.x / unit_k;
	float dz = UV.y / unit_k;
	float Vu = dot(V, tw);
	float a = max(-dot(V, nw), 0.03);
	float Vz = V.y;
	Vu = abs(Vu) < 1e-4 ? 1e-4 : Vu;
	Vz = abs(Vz) < 1e-4 ? 1e-4 : Vz;
	float tb = room_d / a;
	float tu = ((Vu > 0.0 ? room_hu : -room_hu) - u) / Vu;
	float tz = ((Vz >= 0.0 ? room_zb + room_h : room_zb) - dz) / Vz;
	float t = min(tb, min(tu, tz));
	float hu = u + Vu * t;
	float hz = dz + Vz * t;
	float hd = a * t;
	float row = clamp(UV2.x, 0.0, variants - 1.0);
	vec2 uv;
	if (t == tb) {
		uv = tile_uv(0.0, 800.0, 336.0, (room_hu - hu) / (2.0 * room_hu), (hz - room_zb) / room_h, row);
	} else if (t == tu) {
		float ty = (hz - room_zb) / room_h;
		if (Vu > 0.0) {
			uv = tile_uv(1220.0, 420.0, 336.0, hd / room_d, ty, row);
		} else {
			uv = tile_uv(800.0, 420.0, 336.0, (room_d - hd) / room_d, ty, row);
		}
	} else if (Vz >= 0.0) {
		uv = tile_uv(2440.0, 800.0, 420.0, (hu + room_hu) / (2.0 * room_hu), hd / room_d, row);
	} else {
		uv = tile_uv(1640.0, 800.0, 420.0, (hu + room_hu) / (2.0 * room_hu), 1.0 - hd / room_d, row);
	}
	vec3 col = texture(atlas, uv).rgb;
	col = mix(col, vec3(0.8, 0.85, 0.82), frost);
	float blind = UV2.y;
	if (blind > 0.0 && dz > 4.2 - 7.0 * blind) {
		float slat = smoothstep(0.30, 0.62, fract(dz * 2.5));
		col *= mix(0.15, 0.7, slat);
	}
	col *= COLOR.rgb;
	float lit = COLOR.a;
	ALBEDO = col * 0.15;
	ROUGHNESS = 0.4;
	SPECULAR = 0.6;
	CLEARCOAT = 0.4;
	CLEARCOAT_ROUGHNESS = 0.1;
	EMISSION = col * (0.10 + 0.90 * lit) * imap_k * emit_gain;
}
