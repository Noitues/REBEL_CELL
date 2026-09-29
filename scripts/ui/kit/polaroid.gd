class_name Polaroid
extends Control
## Polaroid portrait (STYLE_GUIDE 4, 7; ART_BIBLE 7.1): white frame, a square 1:1 image
## drawn by PortraitArt (the operative's own face once `set_operative` names them; the
## class's face from the `[CLASS PORTRAIT]` label otherwise) in one of four expressions
## (`set_expression`), and a marker caption. Final art swaps in behind this view without
## code changes (`portrait` texture).
##
## The caption is whatever the screen gives it; a dossier that prints the name below the
## Polaroid gives it something else (the rank), so the name is never said twice.

var caption: String = ""
var placeholder_label: String = "[PORTRAIT]"
var portrait: Texture2D = null
var glitch: bool = false
var tilt: float = -3.0
## Who is in the picture (PortraitArt subject); empty = an operative keyed by the label.
var subject: Dictionary = {}
## The face shown (PortraitArt.Expr); NEUTRAL unless a screen sets another.
var expression: int = PortraitArt.Expr.NEUTRAL

## The paper border round the photo (px).
const BORDER := 8.0
## Glitch bars over a low-HP photo: how many, and their height (px).
const GLITCH_BARS := 4
const GLITCH_BAR_H := 3.0
const GLITCH_ALPHA := 0.6


func _init(p_caption: String = "", p_label: String = "[PORTRAIT]", p_tilt: float = -3.0) -> void:
	caption = p_caption
	placeholder_label = p_label
	tilt = p_tilt
	custom_minimum_size = Vector2(110, 134)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = tilt


## The photo's square inside the frame.
func image_rect() -> Rect2:
	return Rect2(BORDER, BORDER, size.x - BORDER * 2.0, size.x - BORDER * 2.0)


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Palette.PAPER)
	draw_rect(Rect2(Vector2.ZERO, size), Color(Palette.INK, 0.4), false, 1.0)
	var image := image_rect()
	if portrait != null:
		draw_texture_rect(portrait, image, false)
	else:
		PortraitArt.draw(self, image, _subject())
	if glitch:
		for i in GLITCH_BARS:
			draw_rect(Rect2(image.position.x, image.position.y + i * image.size.y / GLITCH_BARS + GLITCH_BAR_H, image.size.x, GLITCH_BAR_H), Color(Palette.HARM, GLITCH_ALPHA))
	if caption != "":
		var fs := caption_font_size()
		var band := size.y - image.end.y
		draw_string(Palette.marker(), Vector2(BORDER, image.end.y + band * 0.5 + fs * 0.35), caption, HORIZONTAL_ALIGNMENT_LEFT, size.x - BORDER * 2.0, fs, Palette.INK)


## The caption's handwriting size: `label` at the text scale (ART_BIBLE 4.1: handwriting
## is never under 16 px), a step smaller while it doesn't fit the frame, never under
## `caption`.
func caption_font_size() -> int:
	var f := Palette.marker()
	var room := Vector2(size.x - BORDER * 2.0, size.y - image_rect().end.y)
	for step in [UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]:
		var fs := UiTheme.font_px(step)
		if f.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= room.x and f.get_height(fs) <= room.y:
			return fs
	return UiTheme.font_px(UiTheme.CAPTION)


## The drawn portrait's subject: `subject` if set, else an operative whose class is read
## from the placeholder label ("[BREAKER PORTRAIT]"), in `expression`.
func _subject() -> Dictionary:
	if not subject.is_empty():
		return PortraitArt.with_expression(subject, expression)
	var key := placeholder_label.trim_prefix("[").trim_suffix("]").replace(" PORTRAIT", "").to_lower()
	return PortraitArt.operative_subject(StringName(key), &"", caption, expression)


## Pictures one operative (PortraitArt.operative_subject): the class's silhouette, the
## operative's own face.
func set_operative(class_id: StringName, operative_id: StringName) -> void:
	subject = PortraitArt.operative_subject(class_id, operative_id, caption, expression)
	queue_redraw()


## Shows the face in expression `e` (PortraitArt.Expr: NEUTRAL, HURT, TRIUMPHANT,
## FLATLINED). Flatlined greys the photo and runs a flat line across it.
func set_expression(e: int) -> void:
	expression = e
	if not subject.is_empty():
		subject["expression"] = e
	queue_redraw()
