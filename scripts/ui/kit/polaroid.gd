class_name Polaroid
extends Control
## Polaroid portrait (STYLE_GUIDE 4, 7): white frame, a square 1:1 image drawn by
## PortraitArt (the operative's own face once `set_operative` names them; the class's
## face from the `[CLASS PORTRAIT]` label otherwise), marker caption. Final art swaps in
## behind this view without code changes (`portrait` texture).

var caption: String = ""
var placeholder_label: String = "[PORTRAIT]"
var portrait: Texture2D = null
var glitch: bool = false
var tilt: float = -3.0
## Who is in the picture (PortraitArt subject); empty = an operative keyed by the label.
var subject: Dictionary = {}


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
		PortraitArt.draw(self, image, _subject())
	if glitch:
		for i in 4:
			draw_rect(Rect2(image.position.x, image.position.y + i * image.size.y / 4.0 + 3, image.size.x, 3), Color(Palette.CELL_PINK, 0.6))
	draw_string(Palette.marker(), Vector2(8, size.y - 10), caption, HORIZONTAL_ALIGNMENT_LEFT, size.x - 16, 13, Palette.INK)


## The drawn portrait's subject: `subject` if set, else an operative whose class is read
## from the placeholder label ("[BREAKER PORTRAIT]").
func _subject() -> Dictionary:
	if not subject.is_empty():
		return subject
	var key := placeholder_label.trim_prefix("[").trim_suffix("]").replace(" PORTRAIT", "").to_lower()
	return PortraitArt.operative_subject(StringName(key), &"", caption)


## Pictures one operative (PortraitArt.operative_subject): the class's kind, the
## operative's own face.
func set_operative(class_id: StringName, operative_id: StringName) -> void:
	subject = PortraitArt.operative_subject(class_id, operative_id, caption)
	queue_redraw()

