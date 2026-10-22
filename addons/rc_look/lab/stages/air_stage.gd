extends RcLookLabStage
## LOOK-TOOLBOX module 7 in the lab: the capture's time of day (preset `day` / `night`). The sky (rcl_sky by elevation)
## fills the stage; five skyline rows stand at growing distance, each block coloured by the air between the eye and its
## middle (RcLookAir.amount and mix, the GDScript mirror). Under it a strip: one facade colour seen through the air from
## 0 to MAX_D, the shader (rcl_air + rcl_air_mix) over the mirror as chips; they match when the mirror is exact.

## Layout (px share of the view): the horizon's height, the elevation at the top and bottom edges, the strip.
const HORIZON := 0.62
const E_TOP := 0.6
const E_BOTTOM := -0.25
const MARGIN := 60.0
const STRIP_H := 30.0
const CHIPS := 16
const LABEL_SIZE := 15
## Skyline rows: distance (BU), block width and the heights cycled along the row (px; fixed, no randomness).
const ROW_D: Array[float] = [480.0, 240.0, 120.0, 60.0, 20.0]
const ROW_W: Array[float] = [26.0, 38.0, 56.0, 80.0, 120.0]
const HEIGHTS: Array[float] = [0.55, 0.8, 0.4, 1.0, 0.65, 0.9, 0.5, 0.75]
const ROW_H: Array[float] = [330.0, 270.0, 210.0, 150.0, 90.0]
## The facade colour every block shares, the neutral ground under the skyline (the sheet judges the air alone), the
## strip's reach (BU).
const FACADE := Palette.DESK_METAL
const GROUND := Palette.DESK_DARK
const MAX_D := 500.0

const SKY_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_air.gdshaderinc"
uniform vec3 sky_top;
uniform vec3 sky_horizon;
uniform vec3 sky_ground;
uniform float glow_k = 12.0;
uniform float ground_k = 8.0;
uniform float e_top = 0.6;
uniform float e_bottom = -0.25;
void fragment() {
	COLOR = vec4(rcl_sky(mix(e_top, e_bottom, UV.y), sky_top, sky_horizon, sky_ground, glow_k, ground_k), 1.0);
}
"""

const STRIP_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_air.gdshaderinc"
uniform vec3 air;
uniform vec4 air_a;
uniform vec3 facade;
uniform float max_d = 500.0;
void fragment() {
	COLOR = vec4(rcl_air_mix(facade, air, rcl_air(UV.x * max_d, 0.0, air_a)), 1.0);
}
"""

var _sky: ColorRect
var _strip: ColorRect
var _dyn: Control


func _ready() -> void:
	_sky = ColorRect.new()
	_sky.set_anchors_preset(Control.PRESET_FULL_RECT)
	var sm := ShaderMaterial.new()
	sm.shader = _shader(SKY_CODE)
	sm.set_shader_parameter(&"e_top", E_TOP)
	sm.set_shader_parameter(&"e_bottom", E_BOTTOM)
	_sky.material = sm
	add_child(_sky)
	_dyn = Control.new()
	_dyn.set_anchors_preset(Control.PRESET_FULL_RECT)
	add_child(_dyn)
	_strip = ColorRect.new()
	var stm := ShaderMaterial.new()
	stm.shader = _shader(STRIP_CODE)
	stm.set_shader_parameter(&"facade", Vector3(FACADE.r, FACADE.g, FACADE.b))
	stm.set_shader_parameter(&"max_d", MAX_D)
	_strip.material = stm
	add_child(_strip)
	apply(&"night", null)


func apply(time: StringName, _quality: RcLookQualityState) -> void:
	var p := RcLookAir.preset(&"day" if time == &"day" else &"night")
	RcLookAir.apply(_sky.material as ShaderMaterial, p)
	RcLookAir.apply(_strip.material as ShaderMaterial, p)
	for c in _dyn.get_children():
		c.queue_free()
	var view := get_viewport_rect().size
	var ground := view.y * HORIZON
	var floor_rect := ColorRect.new()
	floor_rect.position = Vector2(0.0, ground)
	floor_rect.size = Vector2(view.x, view.y - ground)
	floor_rect.color = GROUND
	_dyn.add_child(floor_rect)
	for r in ROW_D.size():
		var x := 0.0
		var k := r * 3
		while x < view.x:
			var h := ROW_H[r] * HEIGHTS[k % HEIGHTS.size()]
			var b := ColorRect.new()
			b.position = Vector2(x, ground - h + r * 14.0)
			b.size = Vector2(ROW_W[r] - 4.0, h)
			b.color = RcLookAir.mix(FACADE, p.air_color(), RcLookAir.amount(p, ROW_D[r], 0.0))
			_dyn.add_child(b)
			x += ROW_W[r]
			k += 1
	var w := view.x - MARGIN * 2.0
	var y := view.y - MARGIN - STRIP_H
	_strip.position = Vector2(MARGIN, y)
	_strip.size = Vector2(w, STRIP_H * 0.5)
	for i in CHIPS:
		var x0 := roundf(MARGIN + w * float(i) / CHIPS)
		var chip := ColorRect.new()
		chip.position = Vector2(x0, y + STRIP_H * 0.5)
		chip.size = Vector2(roundf(MARGIN + w * float(i + 1) / CHIPS) - x0, STRIP_H * 0.5)
		chip.color = RcLookAir.mix(FACADE, p.air_color(), RcLookAir.amount(p, (float(i) + 0.5) / CHIPS * MAX_D, 0.0))
		_dyn.add_child(chip)
	var l := Label.new()
	l.text = "%s air: density %.3f / BU, facade through 0..%.0f BU (shader over mirror)" % [time, p.density, MAX_D]
	l.position = Vector2(MARGIN, y - LABEL_SIZE - 8.0)
	l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
	_dyn.add_child(l)


static func _shader(code: String) -> Shader:
	var s := Shader.new()
	s.code = code
	return s
