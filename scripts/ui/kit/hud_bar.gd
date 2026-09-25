class_name HudBar
extends HBoxContainer
## The top strip of a screen (STYLE_GUIDE 4, "Neon city"): the screen title on a black
## band with a pink underline ("01. CYBERDECK HQ"), then the status line. `label` is the
## status Label the scene writes to.

var header: ScreenHeader
var label: Label


func _init() -> void:
	add_theme_constant_override("separation", 0)
	header = ScreenHeader.new()
	add_child(header)
	label = Label.new()
	label.theme_type_variation = &"HudLabel"
	label.material = UiTheme.crt_material()
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART  # large text scales (H14)
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	label.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	add_child(label)


## Names the current screen ("01", "CYBERDECK HQ"); an empty title hides the header.
func set_screen(number: String, title: String) -> void:
	header.number = number
	header.title = title
	header.visible = title != ""
	header.custom_minimum_size = Vector2(header._text_width() + 42, 38)
	header.queue_redraw()
