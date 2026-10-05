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
## ART-9 4B: killed in action (the campaign audit): the print dimmed and crossed out.
var kia: bool = false
## KIA: the dim over the print (alpha), the X's inset and width (shares of the picture's
## side) and the grease pencil's opacity (ART_BIBLE §1.2: 0.96).
const KIA_GREY := 0.45
const KIA_INSET := 0.08
const KIA_WIDTH := 0.05
const PENCIL_ALPHA := 0.96


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
	draw_rect(Rect2(Vector2.ZERO, size), edge_color(), false, edge_width())
	var lay := caption_layout()
	var side: float = lay["image"]
	var image := Rect2((size.x - side) * 0.5, CAPTION_INSET, side, side)
	if portrait != null:
		draw_texture_rect(portrait, image, false)
	else:
		PortraitArt.draw(self, image, _subject())
	if kia:
		# ART-9 4B (round 38 contexts, campaign audit): KIA, the print greyed and crossed out
		# in red pencil.
		draw_rect(image, Color(Palette.INK, KIA_GREY))
		var m := image.size.x * KIA_INSET
		var w := maxf(2.0, image.size.x * KIA_WIDTH)
		var red := Color(PortraitFeed.pencil_red(), PENCIL_ALPHA)
		draw_line(image.position + Vector2(m, m), image.end - Vector2(m, m), red, w, true)
		draw_line(Vector2(image.end.x - m, image.position.y + m), Vector2(image.position.x + m, image.end.y - m), red, w, true)
	if glitch:
		for i in 4:
			draw_rect(Rect2(image.position.x, image.position.y + i * image.size.y / 4.0 + 3, image.size.x, 3), PaperInk.opaque(Color(Palette.CELL_PINK, GLITCH_ALPHA)))
	var lines: PackedStringArray = lay["lines"]
	var fs: int = lay["fs"]
	var f := Palette.marker()
	for i in lines.size():
		var y := size.y - CAPTION_BOTTOM - (lines.size() - 1 - i) * f.get_height(fs)
		draw_string(f, Vector2(CAPTION_INSET, y), lines[i], HORIZONTAL_ALIGNMENT_LEFT, size.x - CAPTION_INSET * 2.0, fs, caption_ink())


## The caption's lettering (px at text scale 1.0) at rest, the least it shrinks to (ANIM-R6
## C6: 12 px x the text size, the kit's floor for words; it was 8 px whatever the text size),
## its side inset and its baseline's height over the frame's foot (px).
const CAPTION_FONT := 13
const CAPTION_MIN := 12
const CAPTION_INSET := 8.0
const CAPTION_BOTTOM := 10.0


## ANIM-R6 C6: the caption's lettering at rest and its floor at the text size now (px).
static func caption_top() -> int:
	return roundi(CAPTION_FONT * Settings.text_scale)


static func caption_floor() -> int:
	return roundi(CAPTION_MIN * Settings.text_scale)


## ANIM-R5 P10 / ANIM-R6 C6: the caption as drawn, never cut and never under its floor, both
## at the text size: one line from `caption_top` stepped down to `caption_floor` while it does
## not fit; then two lines and more (split at spaces, a word too long for a line between its
## letters), the picture made smaller (never under IMAGE_MIN_SHARE of its side) so they fit
## under it; the last resort is the lines at the floor over a picture as small as they need.
## {"lines", "fs", "image" (the picture's side, px)}.
func caption_layout() -> Dictionary:
	var f := Palette.marker()
	var room := maxf(1.0, size.x - CAPTION_INSET * 2.0)
	var top := caption_top()
	var low := mini(top, caption_floor())
	for fs in range(top, low - 1, -1):
		if f.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= room:
			return {"lines": PackedStringArray([caption]), "fs": fs, "image": minf(room, _image_room(1, fs))}
	for fs in range(top, low - 1, -1):
		var lines := HeatPoster.wrap_words(f, caption, fs, room)
		var side := minf(room, _image_room(lines.size(), fs))
		if side >= room * IMAGE_MIN_SHARE:
			return {"lines": lines, "fs": fs, "image": side}
	var last := HeatPoster.wrap_words(f, caption, low, room)
	return {"lines": last, "fs": low, "image": maxf(0.0, minf(room, _image_room(last.size(), low)))}


## ANIM-R6 C6: never narrower than the caption's longest word at its floor (plus the insets),
## as tall in proportion: a word is never broken between letters (the dossier's compact
## Polaroid at 1.6 is 60 px wide and "Breaker" at 19 px needs about 70).
func _get_minimum_size() -> Vector2:
	var f := Palette.marker()
	var widest := 0.0
	for word in caption.split(" ", false):
		widest = maxf(widest, f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, caption_floor()).x)
	var w := ceilf(widest + CAPTION_INSET * 2.0)
	var base := custom_minimum_size if custom_minimum_size.x > 0.0 else Vector2(110, 134)
	return Vector2(w, ceilf(w * base.y / base.x)) if w > base.x else Vector2.ZERO


## The picture's side that leaves room under it for `count` caption lines at `fs` (px).
func _image_room(count: int, fs: int) -> float:
	return size.y - CAPTION_INSET - Palette.marker().get_height(fs) * count - CAPTION_BOTTOM


## The least share of its side the picture keeps to make room for a caption of more lines
## (the last resort goes under it rather than cut a word or letter under the floor).
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


# --- High contrast on paper (ART-0 F (ported from art-pass WF b9af7e3, ART_BIBLE v2 §5.6)) -------------------------
## The frame's soft ink edge (alpha) and the glitch bars' alpha out of high contrast.
const EDGE_ALPHA := 0.4
const GLITCH_ALPHA := 0.6


## The caption's ink: INK (7:1 on PAPER in high contrast too).
func caption_ink() -> Color:
	return PaperInk.text(Palette.INK)


## The frame's edge: soft INK, or opaque INK under high contrast.
func edge_color() -> Color:
	return PaperInk.edge(Color(Palette.INK, EDGE_ALPHA))


## The frame's edge width (px): 1, or PaperInk.EDGE_PX under high contrast.
func edge_width() -> float:
	return PaperInk.edge_width(1.0)
