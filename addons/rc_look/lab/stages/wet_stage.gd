extends RcLookLabStage
## LOOK-TOOLBOX module 8 in the lab: the three wet F0 policies side by side for the designer (art-pass 2026-10-22: a
## look decision, not a refactor). One column per preset ("street": 0.16 x specular, "plinth": 0.08 x specular, "water":
## from the IOR). Top: the Fresnel curve, view cosine 0 (left, grazing) to 1 (right, overhead), the shader (rcl_fresnel)
## over the GDScript mirror (RcLookWet.fresnel) as chips. Below: a wet street reflecting a row of neon bars (the plates'
## wet street), the preset's puddle roughness (rcl_fbm3_n + rcl_puddle_rough) blurring each bar by roughness, the
## reflection weighted by rcl_fresnel (the water's boosted as the water plane's), over the dark ground. Seen twice: from
## eye height (grazing: Fresnel nears 1 whatever F0, so the policies converge) and from the city camera's height (about
## 45 degrees: F0 sets how much the street reflects). The street's SPECULAR_AMOUNT is taken as its specular (unverified).
## Schematic, not a renderer: the bars are an analytic environment. Static: no TIME. Day / night change the ground and
## the bars.

## Layout (px): margins, strip height, chips, label size, gap.
const MARGIN := Vector2(60.0, 70.0)
const STRIP_H := 30.0
const CHIPS := 16
const LABEL_SIZE := 15
const GAP := 40.0
## The two views (BU), street level then the city camera: eye height, the rays' slope range down the panel (down per
## unit forward), the bars' elevation (reflected ray's y: centre, half height) inside what the view reflects.
const VIEW_NAMES: Array[String] = ["street level", "city camera"]
const EYE_Y: Array[float] = [1.7, 40.0]
const SLOPE: Array[Vector2] = [Vector2(0.03, 0.5), Vector2(0.35, 1.2)]
const BAR_E: Array[Vector2] = [Vector2(0.12, 0.05), Vector2(0.55, 0.12)]
## The rays' spread across; the bars: their azimuths (rad), half width (rad), the blur per unit roughness (rad), gain.
const SPREAD := 0.9
const BAR_AZ: Array[float] = [-0.28, 0.0, 0.26]
const BAR_W := 0.035
const BAR_BLUR := 0.6
const BAR_GAIN := 1.6
const GROUND_DAY := Palette.DESK_METAL
const GROUND_NIGHT := Palette.DESK_DARK
const BARS_NIGHT: Array[Color] = [Palette.CELL_PINK, Palette.NET_CYAN, Palette.CELL_ACID]
const BARS_DAY: Array[Color] = [Palette.PAPER, Palette.PAPER, Palette.PAPER]
const WETS: Array[StringName] = [&"street", &"plinth", &"water"]

const STRIP_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_wet.gdshaderinc"
uniform float f0 = 0.04;
void fragment() {
	COLOR = vec4(vec3(rcl_fresnel(UV.x, f0)), 1.0);
}
"""

const STREET_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_wet.gdshaderinc"
uniform vec3 ground;
uniform vec3 bar_col[3];
uniform float bar_az[3];
uniform vec2 bar_e = vec2(0.1, 0.05);
uniform float bar_w = 0.035;
uniform float bar_blur = 0.6;
uniform float bar_gain = 1.0;
uniform float eye_y = 1.7;
uniform vec2 slope = vec2(0.03, 0.5);
uniform float spread = 0.9;
uniform float f0 = 0.04;
uniform float boost = 0.0;
uniform float noise_scale = 0.09;
uniform int octaves = 5;
uniform vec2 rough_noise = vec2(0.45, 0.6);
uniform vec2 rough_wet = vec2(0.3, 0.03);
uniform float aspect = 1.0;
void fragment() {
	vec3 eye = vec3(0.0, eye_y, 0.0);
	vec3 dir = normalize(vec3((UV.x - 0.5) * spread * aspect, -mix(slope.x, slope.y, UV.y), 1.0));
	vec3 p = eye + dir * (eye_y / -dir.y);
	float rough = rcl_puddle_rough(rcl_fbm3_n(vec3(p.x, 0.0, p.z) * noise_scale, octaves), rough_noise, rough_wet);
	vec3 r = reflect(dir, vec3(0.0, 1.0, 0.0));
	float az = atan(r.x, r.z);
	float b = rough * bar_blur;
	vec3 env = vec3(0.0);
	for (int i = 0; i < 3; i++) {
		float wx = bar_w + b;
		float wy = bar_e.y + b;
		// a blurred bar keeps its energy: it spreads and dims.
		float k = (bar_w / wx) * (bar_e.y / wy);
		env += bar_col[i] * k * exp(-pow((az - bar_az[i]) / wx, 2.0)) * exp(-pow((r.y - bar_e.x) / wy, 2.0));
	}
	float fr = min(rcl_fresnel(clamp(-dir.y, 0.0, 1.0), f0) * (1.0 + boost), 1.0);
	COLOR = vec4(ground * (1.0 - fr) + env * bar_gain * fr, 1.0);
}
"""

var _streets: Array[ShaderMaterial] = []


func _ready() -> void:
	var view := get_viewport_rect().size
	var col_w := (view.x - MARGIN.x * 2.0 - GAP * 2.0) / 3.0
	var panel_h := (view.y - MARGIN.y * 2.0 - STRIP_H - GAP * 2.0 - LABEL_SIZE * 2.0) * 0.5
	for c in WETS.size():
		var p := RcLookWet.preset(WETS[c])
		var f0 := p.f0()
		var x := MARGIN.x + c * (col_w + GAP)
		var y := MARGIN.y
		_label("%s: F0 %.3f (%s)%s" % [WETS[c], f0, RcLookWetPreset.F0Policy.keys()[p.f0_policy].to_lower(),
				", boost %.2f" % p.fresnel_boost if p.fresnel_boost > 0.0 else ""], Vector2(x, y - LABEL_SIZE - 8.0))
		var strip := ColorRect.new()
		strip.position = Vector2(x, y)
		strip.size = Vector2(col_w, STRIP_H * 0.5)
		var sm := ShaderMaterial.new()
		sm.shader = _shader(STRIP_CODE)
		sm.set_shader_parameter(&"f0", f0)
		strip.material = sm
		add_child(strip)
		for k in CHIPS:
			var x0 := roundf(x + col_w * float(k) / CHIPS)
			var chip := ColorRect.new()
			chip.position = Vector2(x0, y + STRIP_H * 0.5)
			chip.size = Vector2(roundf(x + col_w * float(k + 1) / CHIPS) - x0, STRIP_H * 0.5)
			var g := RcLookWet.fresnel((float(k) + 0.5) / CHIPS, f0)
			chip.color = Color(g, g, g)
			add_child(chip)
		y += STRIP_H + GAP
		for r in VIEW_NAMES.size():
			_label(VIEW_NAMES[r], Vector2(x, y - LABEL_SIZE - 8.0))
			_street(p, f0, r, Rect2(x, y, col_w, panel_h))
			y += panel_h + GAP + LABEL_SIZE
	apply(&"night", null)


## One street panel: preset `p` (F0 `f0`) seen from view `r` in `area`.
func _street(p: RcLookWetPreset, f0: float, r: int, area: Rect2) -> void:
	var street := ColorRect.new()
	street.position = area.position
	street.size = area.size
	var m := ShaderMaterial.new()
	m.shader = _shader(STREET_CODE)
	m.set_shader_parameter(&"bar_az", BAR_AZ)
	m.set_shader_parameter(&"bar_e", BAR_E[r])
	m.set_shader_parameter(&"bar_w", BAR_W)
	m.set_shader_parameter(&"bar_blur", BAR_BLUR)
	m.set_shader_parameter(&"bar_gain", BAR_GAIN)
	m.set_shader_parameter(&"eye_y", EYE_Y[r])
	m.set_shader_parameter(&"slope", SLOPE[r])
	m.set_shader_parameter(&"spread", SPREAD)
	m.set_shader_parameter(&"f0", f0)
	m.set_shader_parameter(&"boost", p.fresnel_boost)
	m.set_shader_parameter(&"noise_scale", p.noise_scale)
	m.set_shader_parameter(&"octaves", p.octaves)
	m.set_shader_parameter(&"rough_noise", p.rough_noise)
	m.set_shader_parameter(&"rough_wet", p.rough_wet)
	m.set_shader_parameter(&"aspect", area.size.x / area.size.y)
	street.material = m
	_streets.append(m)
	add_child(street)


func apply(time: StringName, _quality: RcLookQualityState) -> void:
	var day := time == &"day"
	var cols: Array[Vector3] = []
	for c in (BARS_DAY if day else BARS_NIGHT):
		cols.append(_v3(c))
	for m in _streets:
		m.set_shader_parameter(&"ground", _v3(GROUND_DAY if day else GROUND_NIGHT))
		m.set_shader_parameter(&"bar_col", cols)


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
