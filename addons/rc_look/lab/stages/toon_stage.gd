extends RcLookLabStage
## LOOK-TOOLBOX modules 4 / 5 in the lab. Two columns, one per toon preset ("props", "city"). Top of each: the band
## strip, n . l from -1 (left) to 1 (right) on one albedo (rcl_band_shade + rcl_band_tint), the shader over the
## GDScript mirror (RcLookToon) as chips; they match when the mirror is exact. Under it two overlapping spheres (the
## far one larger) lit from the upper left with a rim, inked twice: by the post pass (8 taps, rcl_ink_normal_edge +
## rcl_ink_depth_edge, ink preset "post") and by the hull (the silhouette grown rcl_hull_width px, ink preset "hull").
## Depth is in BU at the reference ortho size (ortho_ref BU over the view's height), as the city's. Day / night only
## change the wall.

## Layout (px): margins, the strip's height, the sphere panels' height, the gap, chips, label size.
const MARGIN := Vector2(60.0, 60.0)
const STRIP_H := 30.0
const PANEL_GAP := 30.0
const CHIPS := 16
const LABEL_SIZE := 15
## Spheres in a panel (share of the panel's height): centres from the panel's middle, radii; the near one overlaps the
## far one and sits NEAR_GAP of both radii in front of it.
const SPHERE_C: Array[Vector2] = [Vector2(-0.18, -0.02), Vector2(0.2, 0.06)]
const SPHERE_R: Array[float] = [0.34, 0.26]
const NEAR_GAP := 1.5
## The light (view space, toward the light), the rim's power and gain, the hull wobble's waves around the silhouette.
const LIGHT := Vector3(-0.55, 0.6, 0.58)
const RIM_P := 3.0
const RIM_GAIN := 0.25
const HULL_WAVES := 7.0
const ALBEDO: Array[Color] = [Palette.DESK_METAL, Palette.CELL_PINK]
const WALL_DAY := Palette.PAPER
const WALL_NIGHT := Palette.DESK_DARK
const TOONS: Array[StringName] = [&"props", &"city"]

const STRIP_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_toon.gdshaderinc"
uniform vec3 albedo;
uniform vec4 band;
uniform vec3 shadow_tint;
void fragment() {
	float s = rcl_band_shade(UV.x * 2.0 - 1.0, band.x, band.y, band.z, band.w);
	COLOR = vec4(albedo * s * rcl_band_tint(s, band.w, shadow_tint), 1.0);
}
"""

const SPHERE_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_toon.gdshaderinc"
#include "res://addons/rc_look/shaders/rc_ink.gdshaderinc"
uniform vec2 size = vec2(1.0);
uniform vec4 sphere[2];
uniform vec3 albedo[2];
uniform vec3 wall;
uniform vec4 band;
uniform vec3 shadow_tint;
uniform vec3 light_dir;
uniform vec2 rim = vec2(3.0, 0.25);
uniform bool hull = false;
uniform vec3 ink;
uniform vec4 ink_a;
uniform vec3 hull_a;
uniform float bu_px = 1.0;

// vec4(normal, material) and the depth (BU) at px: the nearer sphere, else the wall (material 0, far away).
vec4 at(vec2 px, out float z) {
	vec4 c = vec4(0.0, 0.0, 1.0, 0.0);
	z = 1e4;
	for (int i = 0; i < 2; i++) {
		vec2 d = (px - sphere[i].xy) / sphere[i].z;
		float rr = dot(d, d);
		if (rr < 1.0) {
			vec3 n = vec3(d.x, -d.y, sqrt(1.0 - rr));
			float zi = (sphere[i].w - n.z * sphere[i].z) * bu_px;
			if (zi < z) {
				z = zi;
				c = vec4(n, float(i + 1));
			}
		}
	}
	return c;
}

void fragment() {
	vec2 px = UV * size;
	float z;
	vec4 c0 = at(px, z);
	vec3 col = wall;
	if (c0.w > 0.0) {
		float s = rcl_band_shade(dot(c0.xyz, normalize(light_dir)), band.x, band.y, band.z, band.w);
		col = albedo[int(c0.w) - 1] * s * rcl_band_tint(s, band.w, shadow_tint);
		col += vec3(rcl_rim(c0.xyz, vec3(0.0, 0.0, 1.0), rim.x) * rim.y);
	}
	float e = 0.0;
	if (hull) {
		// The hull: outside every sphere, inside its silhouette grown by the wobbling width.
		for (int i = 0; i < 2; i++) {
			vec2 d = px - sphere[i].xy;
			float n01 = 0.5 + 0.5 * sin(atan(d.y, d.x) * hull_a.z);
			float w = rcl_hull_width(hull_a.x, hull_a.y, n01);
			if (c0.w == 0.0 && length(d) < sphere[i].z + w) {
				e = 1.0;
			}
		}
		col = mix(col, ink, e);
	} else {
		for (int k = 0; k < 8; k++) {
			float a = float(k) * 0.785398;
			float zn;
			vec4 cn = at(px + vec2(cos(a), sin(a)) * ink_a.x, zn);
			e = max(e, rcl_ink_normal_edge(c0, cn, ink_a.y));
			e = max(e, rcl_ink_depth_edge(z, zn, ink_a.z));
		}
		col = mix(col, ink, e * ink_a.w);
	}
	COLOR = vec4(col, 1.0);
}
"""

var _mats: Array[ShaderMaterial] = []


func _ready() -> void:
	var view := get_viewport_rect().size
	var col_w := (view.x - MARGIN.x * 3.0) * 0.5
	var panel_h := (view.y - MARGIN.y * 2.0 - STRIP_H - LABEL_SIZE * 3.0 - PANEL_GAP * 3.0) * 0.5
	var post := RcLookInk.preset(&"post")
	var hull := RcLookInk.preset(&"hull")
	var ortho_ref := RcLookInk.default_config().ortho_ref
	for t in TOONS.size():
		var p := RcLookToon.preset(TOONS[t])
		var x := MARGIN.x + t * (col_w + MARGIN.x)
		var y := MARGIN.y + LABEL_SIZE + 6.0
		_label("%s: bands %.3f / %.3f, shades %.2f / %.2f (n . l -1..1: shader over mirror)" % [TOONS[t], p.lo, p.hi,
				p.shade_mid, p.shade_low], Vector2(x, MARGIN.y - 6.0))
		var strip := ColorRect.new()
		strip.position = Vector2(x, y)
		strip.size = Vector2(col_w, STRIP_H * 0.5)
		var sm := ShaderMaterial.new()
		sm.shader = _shader(STRIP_CODE)
		sm.set_shader_parameter(&"albedo", _v3(ALBEDO[0]))
		sm.set_shader_parameter(&"band", Vector4(p.lo, p.hi, p.shade_mid, p.shade_low))
		sm.set_shader_parameter(&"shadow_tint", _v3(p.shadow_tint))
		strip.material = sm
		add_child(strip)
		for k in CHIPS:
			var x0 := roundf(x + col_w * float(k) / CHIPS)
			var chip := ColorRect.new()
			chip.position = Vector2(x0, y + STRIP_H * 0.5)
			chip.size = Vector2(roundf(x + col_w * float(k + 1) / CHIPS) - x0, STRIP_H * 0.5)
			var s := RcLookToon.band_shade((float(k) + 0.5) / CHIPS * 2.0 - 1.0, p.lo, p.hi, p.shade_mid, p.shade_low)
			var tint := RcLookToon.band_tint(s, p.shade_low, p.shadow_tint)
			chip.color = Color(ALBEDO[0].r * s * tint.r, ALBEDO[0].g * s * tint.g, ALBEDO[0].b * s * tint.b)
			add_child(chip)
		y += STRIP_H + PANEL_GAP
		for h in 2:
			var ink := hull if h == 1 else post
			_label("ink %s: %.1f px%s" % [&"hull" if h == 1 else &"post", ink.width_px,
					", wobble %.2f" % ink.wobble if h == 1 else ", edges %.2f / %.2f" % [ink.normal_edge, ink.depth_edge]],
					Vector2(x, y - LABEL_SIZE - 6.0))
			var panel := ColorRect.new()
			panel.position = Vector2(x, y)
			panel.size = Vector2(col_w, panel_h)
			var m := ShaderMaterial.new()
			m.shader = _shader(SPHERE_CODE)
			var spheres: Array[Vector4] = []
			# The first sphere is the far one: its centre sits NEAR_GAP of both radii behind the second's.
			var far_z := (SPHERE_R[0] + SPHERE_R[1]) * panel_h * NEAR_GAP
			for i in 2:
				spheres.append(Vector4(col_w * 0.5 + SPHERE_C[i].x * panel_h, panel_h * (0.5 + SPHERE_C[i].y),SPHERE_R[i] * panel_h,
						far_z if i == 0 else 0.0))
			m.set_shader_parameter(&"size", panel.size)
			m.set_shader_parameter(&"bu_px", ortho_ref / view.y)
			m.set_shader_parameter(&"sphere", spheres)
			m.set_shader_parameter(&"albedo", [_v3(ALBEDO[0]), _v3(ALBEDO[1])] as Array[Vector3])
			m.set_shader_parameter(&"band", Vector4(p.lo, p.hi, p.shade_mid, p.shade_low))
			m.set_shader_parameter(&"shadow_tint", _v3(p.shadow_tint))
			m.set_shader_parameter(&"light_dir", LIGHT)
			m.set_shader_parameter(&"rim", Vector2(RIM_P, RIM_GAIN))
			m.set_shader_parameter(&"hull", h == 1)
			m.set_shader_parameter(&"ink", _v3(ink.color))
			m.set_shader_parameter(&"ink_a", Vector4(ink.width_px, ink.normal_edge,
					RcLookInk.depth_thr(ink.depth_edge, ortho_ref, ortho_ref), ink.alpha))
			m.set_shader_parameter(&"hull_a", Vector3(ink.width_px, ink.wobble, HULL_WAVES))
			panel.material = m
			_mats.append(m)
			add_child(panel)
			y += panel_h + PANEL_GAP + LABEL_SIZE
	apply(&"night", null)


func apply(time: StringName, _quality: RcLookQualityState) -> void:
	for m in _mats:
		m.set_shader_parameter(&"wall", _v3(WALL_DAY if time == &"day" else WALL_NIGHT))


func _label(text: String, at: Vector2) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
	add_child(l)


static func _shader(code: String) -> Shader:
	var s := Shader.new()
	s.code = code
	return s


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)
