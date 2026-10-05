class_name GlassScrim
extends ColorRect
## The SCRIM behind glass and modals (ART_BIBLE v2 §2 `SCRIM`: #02030A at 55% over a 6 px
## blur): what sits behind a modal over the city is blurred by `Palette.SCRIM_BLUR_PX` and
## dimmed by `Palette.SCRIM` (`shaders/glass_blur.gdshader`). One shared material. Under
## high contrast (§5.6: opaque panels, no blur) it is opaque `HighContrast.BG` instead. It
## takes no focus; a modal's backdrop stops the clicks meant for the page behind it
## (`full_screen`). View only. ART-0 F: ported from art-pass (W8a).

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


## The blur-and-dim material every scrim shares (the SCRIM token's values from Palette).
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


## A modal's backdrop over the whole viewport, drawn behind its modal (`show_behind_parent`,
## top level so no container lays it out), `view_size` (the host's viewport) big: it stops
## the clicks meant for the page.
static func backdrop_for(modal: Control, view_size: Vector2) -> GlassScrim:
	var s := GlassScrim.new()
	s.name = "ModalScrim"
	s.top_level = true
	s.show_behind_parent = true
	s.mouse_filter = Control.MOUSE_FILTER_STOP
	s.position = Vector2.ZERO
	s.size = view_size
	modal.add_child(s)
	return s


## A scrim over the whole of its parent (anchored full rect; it eats no clicks itself).
static func full_screen() -> GlassScrim:
	var s := GlassScrim.new()
	s.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return s
