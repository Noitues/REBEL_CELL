class_name Polaroid
extends Control
## Polaroid portrait (STYLE_GUIDE 4, 7): white frame, square grey placeholder image at
## the final 1:1 aspect ratio labelled `[NAME PORTRAIT]`, marker caption. Final art
## swaps in behind this view without code changes (`portrait` texture).

var caption: String = ""
var placeholder_label: String = "[PORTRAIT]"
var portrait: Texture2D = null
var glitch: bool = false
var tilt: float = -3.0


func _init(p_caption: String = "", p_label: String = "[PORTRAIT]", p_tilt: float = -3.0) -> void:
	caption = p_caption
	placeholder_label = p_label
	tilt = p_tilt
	custom_minimum_size = Vector2(110, 134)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = tilt


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Palette.PAPER)
	draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.INK, 0.4), false, 1.0)
	var image := Rect2(8, 8, size.x - 16, size.x - 16)
	if portrait != null:
		draw_texture_rect(portrait, image, false)
	else:
		draw_rect(image, Color(0.45, 0.45, 0.47))
		draw_string(Palette.mono(), image.position + Vector2(4, image.size.y / 2.0), placeholder_label, HORIZONTAL_ALIGNMENT_LEFT, image.size.x - 8, 10, Palette.PAPER)
	if glitch:
		for i in 4:
			draw_rect(Rect2(image.position.x, image.position.y + i * image.size.y / 4.0 + 3, image.size.x, 3), Color(Palette.CELL_PINK, 0.6))
	draw_string(Palette.marker(), Vector2(8, size.y - 10), caption, HORIZONTAL_ALIGNMENT_LEFT, size.x - 16, 13, Palette.INK)
