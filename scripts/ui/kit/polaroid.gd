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
	var tints := [Palette.CELL_PINK, Palette.NET_CYAN, Palette.NEON_VIOLET, Palette.CRT_AMBER, Palette.CORP_SOLACE]
	return {"kind": PortraitArt.Kind.OPERATIVE, "key": key, "tint": tints[absi(hash(key)) % tints.size()], "name": caption}


## Placeholder portrait until final art lands: a neon duotone head-and-shoulders
## silhouette with a visor glint, tinted per operative (hash of the label).
static func draw_silhouette(ci: CanvasItem, image: Rect2, key: String) -> void:
	var tints := [Palette.CELL_PINK, Palette.NET_CYAN, Palette.NEON_VIOLET, Palette.CRT_AMBER, Palette.CORP_SOLACE]
	var tint: Color = tints[absi(hash(key)) % tints.size()]
	var top := Palette.NIGHT_SKY
	var bottom := tint.darkened(0.55)
	ci.draw_polygon(PackedVector2Array([image.position, Vector2(image.end.x, image.position.y), image.end, Vector2(image.position.x, image.end.y)]),
		PackedColorArray([top, top, bottom, bottom]))
	for k in 5:
		var y := image.position.y + image.size.y * (0.15 + k * 0.18)
		ci.draw_line(Vector2(image.position.x, y), Vector2(image.end.x, y), Color(tint, 0.08), 1.0)
	var c := image.position + Vector2(image.size.x * 0.5, image.size.y * 0.42)
	var r := image.size.x * 0.2
	var body := Color("#07080F")
	# Shoulders, neck, head; a rim light on the tint side.
	ci.draw_colored_polygon(PackedVector2Array([Vector2(image.position.x + image.size.x * 0.08, image.end.y), Vector2(c.x - r * 1.6, c.y + r * 1.5),
		Vector2(c.x + r * 1.6, c.y + r * 1.5), Vector2(image.end.x - image.size.x * 0.08, image.end.y)]), body)
	ci.draw_rect(Rect2(c.x - r * 0.45, c.y + r * 0.6, r * 0.9, r), body)
	ci.draw_circle(c, r, body)
	ci.draw_arc(c, r, -PI * 0.45, PI * 0.35, 16, Color(tint, 0.9), 1.5)
	ci.draw_line(Vector2(c.x + r * 1.6, c.y + r * 1.5), Vector2(image.end.x - image.size.x * 0.08, image.end.y), Color(tint, 0.7), 1.5)
	# Visor.
	ci.draw_rect(Rect2(c.x - r * 0.75, c.y - r * 0.2, r * 1.5, r * 0.32), Color(tint, 0.95))
	ci.draw_rect(Rect2(c.x - r * 0.75, c.y - r * 0.2, r * 1.5, r * 0.32).grow(2), Color(tint, 0.25))
