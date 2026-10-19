class_name JackHubField
extends Control
## NA-25b r4 (ART_BIBLE 4.6, art-pass A-031 item 1): the covering hub as a flat class-colour field. Once the jack's wheel has swelled past
## its rest size, the hub core (a raster emblem blown up ~25x) is replaced by this: one flat disc in the class colour on the hub's own
## circle, the bezel's inner ring as its only edge (off screen when the hub covers), and the class emblem and its name at their own native
## size, centred and whole. It lives in the wheel's sub-viewport above the wheel, so the lens hole cuts through it. View only.

## The class accent's share mixed into the night sky for the flat field.
const FIELD_TINT := 0.16
## The inner ring's width (px, canvas units) and the arc's segment count.
const RING_PX := 4.0
const RING_SEGMENTS := 128
## The most the emblem's box grows to, as a share of the canvas height (it never passes the glyph's native size).
const EMBLEM_CAP := 0.30
## The name's size (px, canvas units) at most, its share of the canvas height, and the room it may take (share of the disc's diameter,
## and of the canvas width).
const NAME_CAP := 0.065
const NAME_FLOOR_PX := 9
const NAME_DISC_SHARE := 0.8
const NAME_CANVAS_SHARE := 0.8
## The name's gap under the emblem (share of the emblem's box).
const NAME_GAP := 0.14

## The disc's centre and radius (canvas px), the class accent, the emblem glyph id and the name to show.
var center: Vector2 = Vector2.ZERO
var radius: float = 0.0
var accent: Color = Palette.NO_TINT
var glyph: StringName = &""
var hub_name: String = ""
## The emblem's box (px) when it follows the hub (before the cap): the wheel's own emblem size at the current enlargement.
var natural_emblem_px: float = 0.0
## The field's opacity (0 shows the real hub), and the emblem's (it leaves while the CRT hold sits on the field).
var k: float = 0.0
var emblem_alpha: float = 1.0
var canvas: Vector2 = Vector2(1280.0, 720.0)


func _init() -> void:
	name = "HubField"
	mouse_filter = Control.MOUSE_FILTER_IGNORE


## The share of the field that shows at a wheel enlargement of `wheel_scale` (1 = at rest on the link): none at rest, whole once it has
## grown `span` more.
static func k_for_scale(wheel_scale: float, span: float) -> float:
	return clampf((wheel_scale - 1.0) / maxf(span, 0.001), 0.0, 1.0)


## The flat field's colour for a class accent.
static func field_color(p_accent: Color) -> Color:
	return Palette.NIGHT_SKY.lerp(p_accent, FIELD_TINT)


## The emblem's box (px): the hub's own enlargement, held to the glyph's native size and to a share of the canvas height.
static func emblem_px(natural: float, native: float, canvas_h: float) -> float:
	return minf(minf(natural, native), canvas_h * EMBLEM_CAP)


## True when the disc reaches every corner of the canvas (it is then the whole screen, its ring past every edge).
func covers_screen() -> bool:
	var far := 0.0
	for corner in [Vector2.ZERO, Vector2(canvas.x, 0.0), Vector2(0.0, canvas.y), canvas]:
		far = maxf(far, center.distance_to(corner))
	return radius >= far


func _draw() -> void:
	if k <= 0.0 or radius <= 0.0:
		return
	if covers_screen():
		# Covering: the flat field is the whole screen (its ring is past every edge), never a polygon of a huge circle.
		draw_rect(Rect2(Vector2.ZERO, canvas), Color(field_color(accent), k))
	else:
		draw_circle(center, radius, Color(field_color(accent), k))
		draw_arc(center, maxf(radius - RING_PX * 0.5, 0.0), 0.0, TAU, RING_SEGMENTS, Color(accent, k), RING_PX, true)
	if emblem_alpha <= 0.0:
		return
	var tex := WheelGlyphs.texture(glyph)
	var native := float(tex.get_width()) * WheelGlyphs.box_share(glyph) if tex != null else natural_emblem_px
	var box := emblem_px(natural_emblem_px, native, canvas.y)
	var a := k * emblem_alpha
	var font := Palette.body_medium()
	var fs := mini(roundi(canvas.y * NAME_CAP), roundi(box * 0.4))
	var room := minf(radius * 2.0 * NAME_DISC_SHARE, canvas.x * NAME_CANVAS_SHARE)
	while fs > NAME_FLOOR_PX and font.get_string_size(hub_name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	var show_name := hub_name != "" and fs >= NAME_FLOOR_PX
	var name_h := float(fs) * 1.2 if show_name else 0.0
	var block := box + (box * NAME_GAP + name_h if show_name else 0.0)
	var top := center.y - block * 0.5
	if tex != null and box > 1.0:
		WheelGlyphs.draw(self, glyph, Vector2(center.x, top + box * 0.5), box, Color(accent, a))
	if show_name:
		var w := font.get_string_size(hub_name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var at := Vector2(center.x - w * 0.5, top + box + box * NAME_GAP + float(fs))
		draw_string_outline(font, at, hub_name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(fs * 0.3)), Color(Palette.INK, a))
		draw_string(font, at, hub_name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.TEXT_HI, a))
