extends RcLookLabStage
## LOOK-TOOLBOX module 9 in the lab: each grade preset on a grey ramp and on the neon tokens' ramps (black to the
## token), the shader (rcl_grade, a continuous strip) over the GDScript mirror (RcLookGrade, stepped chips). Strip
## and chips match when the mirror is exact; the shoulder shows as the top end rolling off instead of clipping.

## Layout (px): the rows' origin (the strips span the view between equal margins), a strip's height, the gap between rows and between presets, chip count.
const ORIGIN := Vector2(60.0, 70.0)
const STRIP_H := 34.0
const ROW_GAP := 10.0
const PRESET_GAP := 46.0
const CHIPS := 16
const LABEL_SIZE := 15
## The ramps' end colours: grey, then the neon tokens (Palette, as the views use them).
const RAMP_ENDS: Array[Color] = [Color(1, 1, 1), Palette.CELL_PINK, Palette.NET_CYAN, Palette.CELL_ACID]

const SHADER_CODE := """shader_type canvas_item;
#include "res://addons/rc_look/shaders/rc_grade.gdshaderinc"
uniform vec3 ramp_to = vec3(1.0);
uniform float grade_exposure = 1.0;
uniform float grade_white = 0.0;
uniform vec3 grade_tint = vec3(1.0);
uniform float grade_saturation = 1.0;
void fragment() {
	COLOR = vec4(rcl_grade(ramp_to * UV.x, grade_exposure, grade_white, grade_tint, grade_saturation), 1.0);
}
"""


func _ready() -> void:
	var shader := Shader.new()
	shader.code = SHADER_CODE
	var w := get_viewport_rect().size.x - ORIGIN.x * 2.0
	var y := ORIGIN.y
	for n: StringName in RcLookGrade.default_config().presets:
		var p := RcLookGrade.preset(n)
		var l := Label.new()
		l.text = "%s  (exposure %.2f, white %.2f, saturation %.2f)" % [n, p.exposure, p.white, p.saturation]
		l.position = Vector2(ORIGIN.x, y - LABEL_SIZE - 8.0)
		l.add_theme_font_size_override(&"font_size", LABEL_SIZE)
		add_child(l)
		for e in RAMP_ENDS:
			var strip := ColorRect.new()
			strip.position = Vector2(ORIGIN.x, y)
			strip.size = Vector2(w, STRIP_H * 0.5)
			var m := ShaderMaterial.new()
			m.shader = shader
			m.set_shader_parameter(&"ramp_to", Vector3(e.r, e.g, e.b))
			RcLookGrade.apply(m, p)
			strip.material = m
			add_child(strip)
			for k in CHIPS:
				var v := (float(k) + 0.5) / CHIPS
				var chip := ColorRect.new()
				var x0 := roundf(ORIGIN.x + w * float(k) / CHIPS)
				chip.position = Vector2(x0, y + STRIP_H * 0.5)
				chip.size = Vector2(roundf(ORIGIN.x + w * float(k + 1) / CHIPS) - x0, STRIP_H * 0.5)
				chip.color = RcLookGrade.grade_preset(Color(e.r * v, e.g * v, e.b * v), p)
				add_child(chip)
			y += STRIP_H + ROW_GAP
		y += PRESET_GAP
