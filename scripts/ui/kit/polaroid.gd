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
## Art pass WF: the least horizontal squeeze a caption takes before it shrinks as a whole
## (handwriting reads condensed; a clipped glyph never does).
const CONDENSE_MIN := 0.7
## The frame's ink edge alpha (opaque in high contrast).
const EDGE_ALPHA := 0.4


func _init(p_caption: String = "", p_label: String = "[PORTRAIT]", p_tilt: float = -3.0) -> void:
	caption = p_caption
	placeholder_label = p_label
	tilt = p_tilt
	custom_minimum_size = Vector2(110, 134)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func _ready() -> void:
	pivot_offset = size / 2.0
	rotation_degrees = tilt


## The photo's square inside the frame. Art pass W9F: a frame too short for its caption at
## the floor (`caption` at 1.0: the compact dossier's "R0" at 2.0 ran over the photo) gives the
## caption band that room and the photo shrinks, centred.
func image_rect() -> Rect2:
	var side := size.x - BORDER * 2.0
	if caption != "":
		var need := caption_floor_height()
		if size.y - BORDER - side < need:
			side = maxf(0.0, size.y - BORDER - need)
	return Rect2((size.x - side) * 0.5, BORDER, side, side)


## Art pass W9F: the least height the caption band keeps: the shortened caption's ink at the
## floor (`caption` at text scale 1.0).
func caption_floor_height() -> float:
	return _ink_size(short_caption(caption), UiTheme.CAPTION).y


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Palette.PAPER)
	draw_rect(Rect2(Vector2.ZERO, size), edge_color(), false, edge_width())
	var image := image_rect()
	if portrait != null:
		draw_texture_rect(portrait, image, false)
	else:
		PortraitArt.draw(self, image, _subject())
	if glitch:
		for i in GLITCH_BARS:
			draw_rect(Rect2(image.position.x, image.position.y + i * image.size.y / GLITCH_BARS + GLITCH_BAR_H, image.size.x, GLITCH_BAR_H), Color(Palette.HARM, GLITCH_ALPHA))
	if caption != "":
		# Art pass WF: the caption always fits its band whole (caption_layout): never a
		# clipped glyph.
		var cl := caption_layout()
		var f := Palette.marker()
		var fs: int = cl["px"]
		var k: Vector2 = cl["scale"]
		var band := Rect2(BORDER, image.end.y, size.x - BORDER * 2.0, size.y - image.end.y)
		var h := (f.get_ascent(fs) + f.get_descent(fs)) * k.y
		var base := Vector2(band.position.x, band.position.y + (band.size.y - h) * 0.5 + f.get_ascent(fs) * k.y)
		draw_set_transform(base, 0.0, k)
		draw_string(f, Vector2.ZERO, String(cl["text"]), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, caption_ink())
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


## The caption's handwriting size: `label` at the text scale (ART_BIBLE 4.1: handwriting
## is never under 16 px), a step smaller while it doesn't fit the frame, never under
## `caption`.
func caption_font_size() -> int:
	return int(caption_layout()["px"])


## The caption band's room (px): the frame under the photo, inside the border.
func caption_room() -> Vector2:
	return Vector2(size.x - BORDER * 2.0, size.y - image_rect().end.y)


## Art pass WF (ART_BIBLE 4.3, §7 W5's rank rule): how the caption is drawn so it always
## fits its band whole: {text, px, scale (x, y draw scale), size (drawn px)}.
## 1. `label`, then `body`, then `caption` at the text scale while it doesn't fit.
## 2. At caption: abbreviated (short_caption: "RANK n" to "R n", a name to its first word and
##    initials).
## 3. Still too wide: condensed sideways down to CONDENSE_MIN, then shrunk as a whole to the
##    band (never under `caption` at 1.0); too tall: shrunk to the band's height.
func caption_layout() -> Dictionary:
	var room := caption_room()
	for step in [UiTheme.LABEL, UiTheme.BODY, UiTheme.CAPTION]:
		var fs := UiTheme.font_px(step)
		var sz := _ink_size(caption, fs)
		if sz.x <= room.x and sz.y <= room.y:
			return {"text": caption, "px": fs, "scale": Vector2.ONE, "size": sz}
	var px := UiTheme.font_px(UiTheme.CAPTION)
	var text := short_caption(caption)
	var sz := _ink_size(text, px)
	var k := Vector2.ONE
	if sz.x > room.x:
		k.x = maxf(CONDENSE_MIN, room.x / sz.x)
	if sz.x * k.x > room.x:
		var u := room.x / (sz.x * k.x)
		k *= u
	if sz.y * k.y > room.y:
		var v := room.y / (sz.y * k.y)
		k *= v
	# The floor: never smaller than `caption` at text scale 1.0 (§4.3 rule 2).
	var floor_k := float(UiTheme.CAPTION) / px
	if k.y < floor_k:
		k *= floor_k / k.y
	return {"text": text, "px": px, "scale": k, "size": Vector2(sz.x * k.x, sz.y * k.y)}


## The drawn size of `text` at `px` in the handwriting (its advance and ascent + descent).
func _ink_size(text: String, px: int) -> Vector2:
	var f := Palette.marker()
	return Vector2(f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, f.get_ascent(px) + f.get_descent(px))


## Art pass WF: the caption shortened for a small frame: the rank "RANK n" as W5's compact "R n"
## (the translated forms), a name of several words as its first word and the initials of
## the rest ("Mara Voss-Okonkwo" -> "Mara V."); one word stays whole.
static func short_caption(text: String) -> String:
	var rank_word := String(TranslationServer.translate("RANK %d")).split("%d")[0].strip_edges()
	var t := text.strip_edges()
	if rank_word != "" and t.to_upper().begins_with(rank_word.to_upper() + " "):
		var n := t.substr(rank_word.length()).strip_edges()
		if n.is_valid_int():
			return String(TranslationServer.translate("R%d")) % int(n)
	var words := t.split(" ", false)
	if words.size() > 1:
		var out := words[0]
		for i in range(1, words.size()):
			out += " " + words[i].left(1) + "."
		return out
	return t


## The caption's ink: INK on the paper frame (high contrast too: PAPER keeps its stock, its
## ink is INK at well over 7:1, §12).
func caption_ink() -> Color:
	return PaperInk.text(Palette.INK)


## The frame's edge (§12: opaque INK, PaperInk.EDGE_PX, in high contrast).
func edge_color() -> Color:
	return PaperInk.edge(Color(Palette.INK, EDGE_ALPHA))


## The frame's edge width (px).
func edge_width() -> float:
	return PaperInk.edge_width(1.0)


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
