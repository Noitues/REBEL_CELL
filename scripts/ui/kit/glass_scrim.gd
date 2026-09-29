class_name GlassScrim
extends ColorRect
## The SCRIM behind glass (ART_BIBLE §3.3, §5.3, §13): what sits behind a glass panel or a
## modal over the city is blurred by `Palette.SCRIM_BLUR_PX` and dimmed by `Palette.SCRIM`
## (W6's `glass_blur` shader: #02030A at 55% over a 6 px blur). One shared material. Under
## high contrast (§12: opaque panels, no blur) it is opaque `HighContrast.BG` instead. It
## never takes input or focus. A panel puts one behind itself (`show_behind_parent`, sized
## to the panel by the panel); a modal puts a `full_screen` one behind itself. View only.

const SHADER := preload("res://shaders/glass_blur.gdshader")
const NODE_NAME := "GlassScrim"

static var _material: ShaderMaterial = null


func _init() -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	sync()


func _ready() -> void:
	if not Settings.changed.is_connected(sync):
		Settings.changed.connect(sync)


## The blur-and-dim material every scrim shares (§3.3 values from Palette).
static func shared_material() -> ShaderMaterial:
	if _material == null:
		_material = ShaderMaterial.new()
		_material.shader = SHADER
		_material.set_shader_parameter(&"blur_px", float(Palette.SCRIM_BLUR_PX))
		_material.set_shader_parameter(&"tint", Color(Palette.SCRIM, 1.0))
		_material.set_shader_parameter(&"tint_alpha", Palette.SCRIM.a)
	return _material


## True when the scrim is opaque (high contrast) rather than a blur.
func opaque() -> bool:
	return material == null


## Follows the high-contrast setting: opaque black, or the shared blur.
func sync() -> void:
	if Settings.high_contrast:
		material = null
		color = HighContrast.BG
	else:
		material = shared_material()
		# The shader keeps this colour's alpha (a fade on the scrim still fades it).
		color = Color(Palette.SCRIM, 1.0)


## A scrim over the whole viewport (a modal's backdrop; it eats no clicks itself).
static func full_screen() -> GlassScrim:
	var s := GlassScrim.new()
	s.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return s
