class_name ColorblindLayer
extends CanvasLayer
## Colour-blind correction (ART_BIBLE §12, art pass W9): a full-screen daltonize pass
## (`shaders/colorblind.gdshader`) on the top canvas layer, above every layer the game
## draws (Fx at 100, flights at 80) and under the W10 review-pack filter (128), so a
## greyscale or deutan simulation capture sees the corrected frame. Settings keeps this layer
## as its own child only while `Settings.colorblind_mode` is not off, and frees it when it
## goes off: off costs nothing (ART-0 C: M13's ColorblindFilter autoload folded into
## Settings, ported from art-pass 44f14bb). View only: it reads Settings and never changes
## game state.
##
## "Remap corp and semantic hues" is realised as this global pass because Palette's colours
## are compile-time constants read by every view; the patterns and glyphs of §3.6 and §8
## stay the primary cue and this is an aid on top of them.

const SHADER := preload("res://shaders/colorblind.gdshader")
## Above every game layer, below the review-pack simulation filter (FILTER_LAYER 128).
const LAYER := 127
## Settings.colorblind_mode -> the shader's `mode` uniform.
const MODES := {&"deutan": 1, &"protan": 2, &"tritan": 3}
## How much of the daltonize shift is applied (the shader's `strength`).
const STRENGTH := 1.0

## The mode shown (&"deutan", &"protan" or &"tritan").
var mode: StringName = &"deutan"
var rect: ColorRect


func _init(p_mode: StringName = &"deutan") -> void:
	name = "ColorblindLayer"
	layer = LAYER
	rect = ColorRect.new()
	rect.name = "Correction"
	rect.color = Palette.NO_TINT
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var mat := ShaderMaterial.new()
	mat.shader = SHADER
	mat.set_shader_parameter(&"strength", STRENGTH)
	rect.material = mat
	add_child(rect)
	set_mode(p_mode)


## Shows the correction for `p_mode` (one of MODES' keys; anything else keeps the mode).
func set_mode(p_mode: StringName) -> void:
	if not MODES.has(p_mode):
		return
	mode = p_mode
	(rect.material as ShaderMaterial).set_shader_parameter(&"mode", MODES[p_mode])


## The shader's `mode` uniform as set (tests; the headless renderer keeps the value).
func shader_mode() -> int:
	return int((rect.material as ShaderMaterial).get_shader_parameter(&"mode"))


# --- Reference maths (the shader's, for tests and tools) -------------------------------
# Basis(x, y, z) takes columns, as GLSL mat3 does, so the columns match the shader's.

const _RGB2LMS := Basis(Vector3(17.8824, 3.45565, 0.0299566), Vector3(43.5161, 27.1554, 0.184309),
	Vector3(4.11935, 3.86714, 1.46709))
const _LMS2RGB := Basis(Vector3(0.0809444479, -0.0102485335, -0.000365296938),
	Vector3(-0.130504409, 0.0540193266, -0.00412161469), Vector3(0.116721066, -0.113614708, 0.693511405))
const _DEFICIENCY := {
	1: Basis(Vector3(1.0, 0.494207, 0.0), Vector3.ZERO, Vector3(0.0, 1.24827, 1.0)),
	2: Basis(Vector3.ZERO, Vector3(2.02344, 1.0, 0.0), Vector3(-2.52581, 0.0, 1.0)),
	3: Basis(Vector3(1.0, 0.0, -0.395913), Vector3(0.0, 1.0, 0.801109), Vector3.ZERO),
}
const _SHIFT_RED_GREEN := Basis(Vector3(0.0, 0.7, 0.7), Vector3(0.0, 1.0, 0.0), Vector3(0.0, 0.0, 1.0))
const _SHIFT_BLUE_YELLOW := Basis(Vector3(1.0, 0.0, 0.0), Vector3(0.0, 1.0, 0.0), Vector3(0.7, 0.7, 0.0))


## `c` as a viewer with `p_mode`'s full deficiency sees it (the shader's simulation step).
static func simulate(c: Color, p_mode: StringName) -> Color:
	var m: int = MODES.get(p_mode, 0)
	if m == 0:
		return c
	var lin := c.srgb_to_linear()
	var d: Basis = _DEFICIENCY[m]
	var v: Vector3 = _LMS2RGB * (d * (_RGB2LMS * Vector3(lin.r, lin.g, lin.b)))
	return _to_srgb(v, c.a)


## `c` after the daltonize correction for `p_mode`, at full strength (what the shader
## draws for a pixel of colour `c`).
static func correct(c: Color, p_mode: StringName) -> Color:
	var m: int = MODES.get(p_mode, 0)
	if m == 0:
		return c
	var lin := c.srgb_to_linear()
	var rgb := Vector3(lin.r, lin.g, lin.b)
	var d: Basis = _DEFICIENCY[m]
	var err: Vector3 = rgb - _LMS2RGB * (d * (_RGB2LMS * rgb))
	var shift: Basis = _SHIFT_BLUE_YELLOW if m == 3 else _SHIFT_RED_GREEN
	return _to_srgb(rgb + shift * err, c.a)


static func _to_srgb(v: Vector3, a: float) -> Color:
	var clamped := Color(clampf(v.x, 0.0, 1.0), clampf(v.y, 0.0, 1.0), clampf(v.z, 0.0, 1.0), a)
	return clamped.linear_to_srgb()
