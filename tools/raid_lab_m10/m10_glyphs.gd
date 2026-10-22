class_name M10Glyphs
extends RefCounted
## Vector placeholder glyphs and palette for the M10 lab, matching the r10 mockups and the M9 glyph language:
## threats cobalt, the Cell yellow, red only marks loss, teal only the Cell's holds and spoof. All UI text goes through
## `text()`, so `scramble` (the --scramble capture flag) replaces every letter for the no-words test.

const BG := Color8(14, 16, 32)
const PANEL := Color8(26, 30, 54)
const PANEL_EDGE := Color8(70, 80, 130)
const INK := Color8(232, 236, 245)
const DIM := Color8(140, 148, 175)
const CELL := Color8(255, 210, 63)
const THREAT := Color8(61, 107, 255)
const THREAT_LIGHT := Color8(140, 170, 255)
const THREAT_FADE := Color8(50, 60, 110)
const DMG := Color8(255, 77, 77)
const HEAT := Color8(255, 110, 40)
const CLEAN := Color8(90, 220, 200)
const HOLD := Color8(255, 170, 40)
const EMPTY_NODE := Color8(40, 46, 80)

static var font: Font = ThemeDB.fallback_font
static var scramble: bool = false


## Replace every ASCII letter by another (bijective, keeps case); digits and punctuation stay.
static func scr(s: String) -> String:
	if not scramble:
		return s
	var out := ""
	for i in range(s.length()):
		var code := s.unicode_at(i)
		if code >= 65 and code <= 90:
			out += char(65 + ((code - 65) * 7 + 3) % 26)
		elif code >= 97 and code <= 122:
			out += char(97 + ((code - 97) * 7 + 3) % 26)
		else:
			out += s[i]
	return out


## Text with its top-left at `p`.
static func text(ci: CanvasItem, p: Vector2, s: String, size: int, col: Color = INK, align: int = HORIZONTAL_ALIGNMENT_LEFT, width: float = -1.0) -> void:
	ci.draw_string(font, p + Vector2(0, size * 0.95), scr(s), align, width, size, col)


## Text centered on `c`.
static func text_c(ci: CanvasItem, c: Vector2, s: String, size: int, col: Color = INK) -> void:
	var t := scr(s)
	var w := font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	ci.draw_string(font, c + Vector2(-w * 0.5, size * 0.36), t, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


## Text ending at x = right.
static func text_r(ci: CanvasItem, p: Vector2, s: String, size: int, col: Color = INK) -> void:
	var t := scr(s)
	var w := font.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	ci.draw_string(font, p + Vector2(-w, size * 0.95), t, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


static func text_w(s: String, size: int) -> float:
	return font.get_string_size(scr(s), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


static func panel(ci: CanvasItem, r: Rect2, edge: Color = PANEL_EDGE, fill: Color = PANEL, width: float = 2.0) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.set_corner_radius_all(6)
	sb.border_color = edge
	sb.set_border_width_all(int(width))
	ci.draw_style_box(sb, r)


static func button(ci: CanvasItem, r: Rect2, label: String, hot: bool = false, enabled: bool = true, size: int = 18) -> void:
	var edge := CELL if enabled else PANEL_EDGE
	panel(ci, r, edge, Color8(60, 52, 24) if (hot and enabled) else PANEL, 3.0)
	text_c(ci, r.get_center(), label, size, CELL if enabled else DIM)


static func line(ci: CanvasItem, a: Vector2, b: Vector2, col: Color, w: float = 2.0) -> void:
	ci.draw_line(a, b, col, w, true)


static func circle(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 2.0) -> void:
	ci.draw_arc(c, r, 0.0, TAU, 32, col, w, true)


static func disc(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	ci.draw_circle(c, r, col)


## Dashed ring (the ghost glyph).
static func dashed_ring(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 4.0) -> void:
	for k in range(12):
		var a := k * TAU / 12.0
		ci.draw_arc(c, r, a, a + TAU / 24.0, 5, col, w, true)


static func dashed_line(ci: CanvasItem, a: Vector2, b: Vector2, col: Color, on: float, off: float, w: float = 4.0) -> void:
	var length := a.distance_to(b)
	if length < 1.0:
		return
	var d := (b - a) / length
	var n := 0.0
	while n < length:
		var e := minf(length, n + on)
		ci.draw_line(a + d * n, a + d * e, col, w, true)
		n = e + off


static func hexagon(ci: CanvasItem, c: Vector2, r: float, fill: Color, edge: Color, w: float = 3.0) -> void:
	var pts := PackedVector2Array()
	for k in range(6):
		var a := PI / 6.0 + k * PI / 3.0
		pts.append(c + Vector2(cos(a), sin(a)) * r)
	ci.draw_colored_polygon(pts, fill)
	pts.append(pts[0])
	ci.draw_polyline(pts, edge, w, true)


static func coin(ci: CanvasItem, c: Vector2, r: float, col: Color = CELL) -> void:
	circle(ci, c, r, col, 3.0)
	ci.draw_line(c + Vector2(0, -r * 0.45), c + Vector2(0, r * 0.45), col, 3.0)


static func flame(ci: CanvasItem, c: Vector2, r: float, col: Color = HEAT) -> void:
	var pts := PackedVector2Array([c + Vector2(0, -r * 1.3), c + Vector2(r * 0.9, r * 0.2), c + Vector2(r * 0.5, r),
		c + Vector2(-r * 0.5, r), c + Vector2(-r * 0.9, r * 0.2), c + Vector2(-r * 0.2, -r * 0.4)])
	ci.draw_colored_polygon(pts, col)


static func check(ci: CanvasItem, c: Vector2, r: float, col: Color = CLEAN) -> void:
	ci.draw_polyline(PackedVector2Array([c + Vector2(-r, 0), c + Vector2(-r * 0.3, r * 0.7), c + Vector2(r, -r * 0.7)]), col, 3.0, true)


static func cross(ci: CanvasItem, c: Vector2, r: float, col: Color = DMG, w: float = 3.0) -> void:
	ci.draw_line(c + Vector2(-r, -r), c + Vector2(r, r), col, w, true)
	ci.draw_line(c + Vector2(-r, r), c + Vector2(r, -r), col, w, true)


## Cobalt shield (the Heat notch / contact threshold).
static func shield(ci: CanvasItem, c: Vector2, r: float, col: Color = THREAT) -> void:
	ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-r, -r), c + Vector2(r, -r), c + Vector2(r, r * 0.2),
		c + Vector2(0, r * 1.1), c + Vector2(-r, r * 0.2)]), col)


## The "contact" glyph: a cobalt hex with an eye.
static func contact(ci: CanvasItem, c: Vector2, r: float) -> void:
	hexagon(ci, c, r, Color8(30, 44, 110), THREAT, 3.0)
	ci.draw_arc(c + Vector2(0, r * 0.35), r * 0.7, PI * 1.2, PI * 1.8, 12, INK, 2.0, true)
	ci.draw_arc(c + Vector2(0, -r * 0.35), r * 0.7, PI * 0.2, PI * 0.8, 12, INK, 2.0, true)
	ci.draw_circle(c, r * 0.2, INK)


static func arrow(ci: CanvasItem, a: Vector2, b: Vector2, col: Color, w: float = 3.0, head: float = 9.0) -> void:
	var d := (b - a).normalized()
	ci.draw_line(a, b - d * head * 0.5, col, w, true)
	var n := Vector2(-d.y, d.x)
	ci.draw_colored_polygon(PackedVector2Array([b, b - d * head + n * head * 0.55, b - d * head - n * head * 0.55]), col)


## Candidate end shapes: 0 triangle, 1 square, 2 diamond. Outline only (or filled).
static func cand_shape(ci: CanvasItem, c: Vector2, i: int, r: float, col: Color, fill: Color = Color(0, 0, 0, 0), w: float = 3.0) -> void:
	var pts: PackedVector2Array
	match i:
		0:
			pts = PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, r * 0.8), c + Vector2(-r, r * 0.8)])
		1:
			pts = PackedVector2Array([c + Vector2(-r, -r), c + Vector2(r, -r), c + Vector2(r, r), c + Vector2(-r, r)])
		_:
			pts = PackedVector2Array([c + Vector2(0, -r * 1.2), c + Vector2(r, 0), c + Vector2(0, r * 1.2), c + Vector2(-r, 0)])
	if fill.a > 0.0:
		ci.draw_colored_polygon(pts, fill)
	pts.append(pts[0])
	ci.draw_polyline(pts, col, w, true)


## Beam-order badge (1, 2, 3).
static func badge(ci: CanvasItem, c: Vector2, n: int, col: Color = THREAT) -> void:
	ci.draw_circle(c, 11.0, col)
	ci.draw_arc(c, 11.0, 0.0, TAU, 20, INK, 1.5, true)
	text_c(ci, c, str(n), 15, INK)


## Wrench (the DOWN mark): a handle with an open jaw.
static func wrench(ci: CanvasItem, c: Vector2, r: float, col: Color = DMG) -> void:
	ci.draw_line(c + Vector2(r * 0.9, r * 0.9), c + Vector2(-r * 0.2, -r * 0.2), col, 5.0, true)
	ci.draw_arc(c + Vector2(-r * 0.5, -r * 0.5), r * 0.62, PI * 0.9, PI * 2.55, 14, col, 4.0, true)


## Spoof (held press): a rounded key with a bar.
static func spoof_key(ci: CanvasItem, c: Vector2, col: Color) -> void:
	panel(ci, Rect2(c.x - 26, c.y - 14, 52, 28), col, Color(0, 0, 0, 0), 3.0)
	ci.draw_line(c + Vector2(-10, 0), c + Vector2(10, 0), col, 3.0)


## A stamp: a bordered word, tilted.
static func stamp(ci: CanvasItem, c: Vector2, word: String, col: Color, size: int, sub: String = "") -> void:
	ci.draw_set_transform(c, -0.12, Vector2.ONE)
	var w := text_w(word, size) + 36.0
	var h := size * 1.2 + (size * 0.7 if sub != "" else 0.0) + 18.0
	var r := Rect2(-w * 0.5, -h * 0.5, w, h)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0, 0, 0, 0.35)
	sb.set_corner_radius_all(6)
	sb.border_color = col
	sb.set_border_width_all(5)
	ci.draw_style_box(sb, r)
	text_c(ci, Vector2(0, -h * 0.5 + 9.0 + size * 0.6), word, size, col)
	if sub != "":
		text_c(ci, Vector2(0, h * 0.5 - 9.0 - size * 0.35), sub, int(size * 0.62), col)
	ci.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
