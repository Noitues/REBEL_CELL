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
	var lay := caption_layout()
	var side: float = lay["image"]
	var image := Rect2((size.x - side) * 0.5, CAPTION_INSET, side, side)
	if portrait != null:
		draw_texture_rect(portrait, image, false)
	else:
		PortraitArt.draw(self, image, _subject())
	if glitch:
		for i in 4:
			draw_rect(Rect2(image.position.x, image.position.y + i * image.size.y / 4.0 + 3, image.size.x, 3), Color(Palette.CELL_PINK, 0.6))
	var lines: PackedStringArray = lay["lines"]
	var fs: int = lay["fs"]
	var f := Palette.marker()
	for i in lines.size():
		var y := size.y - CAPTION_BOTTOM - (lines.size() - 1 - i) * f.get_height(fs)
		draw_string(f, Vector2(CAPTION_INSET, y), lines[i], HORIZONTAL_ALIGNMENT_LEFT, size.x - CAPTION_INSET * 2.0, fs, Palette.INK)


## The caption's lettering (px) at rest, the least it shrinks to, its side inset and its
## baseline's height over the frame's foot (px).
const CAPTION_FONT := 13
const CAPTION_MIN := 8
const CAPTION_INSET := 8.0
const CAPTION_BOTTOM := 10.0


## ANIM-R5 P10: the caption as drawn, never cut (at 1.6 the dossier's smaller Polaroid cut
## "BREAKER 1" to "BREAK"): one line at CAPTION_FONT, stepped down while it does not fit;
## then two lines (split at the space that balances them), the picture made smaller (never
## under IMAGE_MIN_SHARE of its side) so both fit under it; the one line at CAPTION_MIN as
## the last resort. {"lines", "fs", "image" (the picture's side, px)}.
func caption_layout() -> Dictionary:
	var f := Palette.marker()
	var room := size.x - CAPTION_INSET * 2.0
	for fs in range(CAPTION_FONT, CAPTION_MIN - 1, -1):
		if f.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= room:
			return {"lines": PackedStringArray([caption]), "fs": fs, "image": room}
	var words := caption.split(" ", false)
	for fs in range(CAPTION_FONT, CAPTION_MIN - 1, -1):
		var side := minf(room, size.y - CAPTION_INSET - f.get_height(fs) * 2.0 - CAPTION_BOTTOM)
		if side < room * IMAGE_MIN_SHARE:
			continue
		var best := PackedStringArray()
		var best_w := INF
		for cut in range(1, words.size()):
			var a := " ".join(words.slice(0, cut))
			var b := " ".join(words.slice(cut))
			var w := maxf(f.get_string_size(a, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, f.get_string_size(b, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
			if w <= room and w < best_w:
				best_w = w
				best = PackedStringArray([a, b])
		if not best.is_empty():
			return {"lines": best, "fs": fs, "image": side}
	return {"lines": PackedStringArray([caption]), "fs": CAPTION_MIN, "image": room}


## The least share of its side the picture keeps to make room for a two-line caption.
const IMAGE_MIN_SHARE := 0.6


## The caption's lettering (px) as drawn.
func caption_size() -> int:
	return int(caption_layout()["fs"])


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

