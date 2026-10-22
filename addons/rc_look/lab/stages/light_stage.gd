extends RcLookLabStage
## LOOK-TOOLBOX module 6 in the lab. Top: each light preset as a strip from its source (left) over two units of reach,
## pink light added in linear light to a dark wall: the shader (rcl_fall + rcl_light_add) over the GDScript mirror
## (RcLookLight.at + light_add) as chips; they match when the mirror is exact. Bottom: a neon sign scene: three bars
## spill onto a dark facade (preset "spill_ui": a UI layer's spill, half the city's reach; in bar heights) beside a
## paper card, under the 2D bloom pass (rc_bloom.gdshader) at the capture's quality tier.

## Layout (px): margins, strip height and gaps, chip count, the scene's height share, bar size, the card's width share.
const MARGIN := Vector2(60.0, 60.0)
const STRIP_H := 30.0
const ROW_GAP := 24.0
const CHIPS := 16
const LABEL_SIZE := 15
const REACH_UNITS := 2.0
const SCENE_SHARE := 0.48
const BAR := Vector2(320.0, 26.0)
const BAR_GAP := 120.0
const CARD_SHARE := 0.22
## Colours: the wall, the light in the strips, the bars, the card.
const WALL := Palette.DESK_DARK
const STRIP_LIGHT := Palette.CELL_PINK
const BARS: Array[Color] = [Palette.CELL_PINK, Palette.NET_CYAN, Palette.CELL_ACID]
const CARD := Palette.PAPER

const STRIP_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_light.gdshaderinc"
uniform vec3 wall = vec3(0.1);
uniform vec3 light = vec3(1.0);
uniform float reach_units = 2.0;
uniform float reach = 1.0;
uniform float shape = 2.0;
uniform float gain = 1.0;
uniform int kind = 0;
void fragment() {
	float f = rcl_fall(UV.x * reach_units, reach, shape, kind) * gain;
	COLOR = vec4(rcl_light_add(wall, rcl_to_lin(light) * f), 1.0);
}
"""

const FACADE_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_light.gdshaderinc"
uniform vec3 wall = vec3(0.1);
uniform vec4 bar_rect[3];
uniform vec3 bar_color[3];
uniform float shape = 2.0;
uniform float gain = 1.0;
uniform int kind = 1;
uniform float reach_bars = 6.0;
uniform float reach = 1.0;
uniform vec2 size = vec2(1.0);
void fragment() {
	vec2 px = UV * size;
	vec3 add = vec3(0.0);
	for (int i = 0; i < 3; i++) {
		vec2 lo = bar_rect[i].xy;
		vec2 hi = bar_rect[i].xy + bar_rect[i].zw;
		float d = length(max(max(lo - px, px - hi), vec2(0.0)));
		add += rcl_to_lin(bar_color[i]) * rcl_fall(d / (bar_rect[i].w * reach_bars), reach, shape, kind) * gain;
	}
	COLOR = vec4(rcl_light_add(wall, add), 1.0);
}
"""

var _bloom: ColorRect


func _ready() -> void:
	var cfg := RcLookLight.default_config()
	var w := get_viewport_rect().size.x - MARGIN.x * 2.0
	var vh := get_viewport_rect().size.y
	var strip := Shader.new()
	strip.code = STRIP_CODE
	var y := MARGIN.y
	var names: Array = cfg.presets.keys()
	names.sort()
	for n: StringName in names:
		var p := RcLookLight.preset(n)
		_label("%s  (%s, shape %.2f, gain %.2f; %.0f units of reach)" % [n, "exp" if p.kind == RcLookLightPreset.Kind.EXP else "pow",
				p.shape, p.gain, REACH_UNITS], Vector2(MARGIN.x, y - LABEL_SIZE - 6.0))
		var r := ColorRect.new()
		r.position = Vector2(MARGIN.x, y)
		r.size = Vector2(w, STRIP_H * 0.5)
		var m := ShaderMaterial.new()
		m.shader = strip
		m.set_shader_parameter(&"wall", _v3(WALL))
		m.set_shader_parameter(&"light", _v3(STRIP_LIGHT))
		m.set_shader_parameter(&"reach_units", REACH_UNITS)
		m.set_shader_parameter(&"shape", p.shape)
		m.set_shader_parameter(&"reach", p.reach)
		m.set_shader_parameter(&"gain", p.gain)
		m.set_shader_parameter(&"kind", int(p.kind))
		r.material = m
		add_child(r)
		var lin := STRIP_LIGHT.srgb_to_linear()
		for k in CHIPS:
			var x0 := roundf(MARGIN.x + w * float(k) / CHIPS)
			var chip := ColorRect.new()
			chip.position = Vector2(x0, y + STRIP_H * 0.5)
			chip.size = Vector2(roundf(MARGIN.x + w * float(k + 1) / CHIPS) - x0, STRIP_H * 0.5)
			var f := RcLookLight.at(p, (float(k) + 0.5) / CHIPS * REACH_UNITS)
			chip.color = RcLookLight.light_add(WALL, Color(lin.r * f, lin.g * f, lin.b * f))
			add_child(chip)
		y += STRIP_H + ROW_GAP
	_scene(Rect2(MARGIN.x, vh * (1.0 - SCENE_SHARE), w, vh * SCENE_SHARE - MARGIN.y))


## The neon sign scene in `area`, with the bloom pass over it.
func _scene(area: Rect2) -> void:
	var p := RcLookLight.preset(&"spill_ui")
	var facade_w := area.size.x * (1.0 - CARD_SHARE)
	var facade := ColorRect.new()
	facade.position = area.position
	facade.size = Vector2(facade_w, area.size.y)
	var sh := Shader.new()
	sh.code = FACADE_CODE
	var m := ShaderMaterial.new()
	m.shader = sh
	var rects: Array[Vector4] = []
	var cols: Array[Vector3] = []
	for i in BARS.size():
		var at := Vector2((facade_w - BAR.x) * 0.5 + (float(i) - 1.0) * BAR_GAP, area.size.y * (0.25 + 0.25 * i))
		rects.append(Vector4(at.x, at.y, BAR.x, BAR.y))
		cols.append(_v3(BARS[i]))
		var bar := ColorRect.new()
		bar.position = at
		bar.size = BAR
		bar.color = BARS[i]
		facade.add_child(bar)
	m.set_shader_parameter(&"wall", _v3(WALL))
	m.set_shader_parameter(&"bar_rect", rects)
	m.set_shader_parameter(&"bar_color", cols)
	m.set_shader_parameter(&"shape", p.shape)
	m.set_shader_parameter(&"reach", p.reach)
	m.set_shader_parameter(&"gain", p.gain)
	m.set_shader_parameter(&"kind", int(p.kind))
	m.set_shader_parameter(&"size", facade.size)
	facade.material = m
	add_child(facade)
	var card := ColorRect.new()
	card.position = area.position + Vector2(facade_w + 24.0, area.size.y * 0.15)
	card.size = Vector2(area.size.x * CARD_SHARE - 24.0, area.size.y * 0.7)
	card.color = CARD
	add_child(card)
	_label("paper (UI): no bloom", card.position + Vector2(0.0, card.size.y + 6.0))
	_bloom = ColorRect.new()
	_bloom.position = area.position
	_bloom.size = area.size
	_bloom.material = RcLookLight.bloom_material()
	add_child(_bloom)


func apply(_time: StringName, quality: RcLookQualityState) -> void:
	if _bloom != null:
		RcLookLight.apply_bloom(_bloom.material as ShaderMaterial, quality)


func _label(text: String, at: Vector2) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
	add_child(l)


static func _v3(c: Color) -> Vector3:
	return Vector3(c.r, c.g, c.b)
