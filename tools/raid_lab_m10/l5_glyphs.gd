class_name L5Glyphs
extends RefCounted
## Vector placeholder glyphs and palette for the L3 lab, matching the r10 mockups and the M9 glyph language:
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


static var _word_cache: Dictionary = {}

const HOLD_OK := Color8(206, 214, 236)


## The no-words test: every word (a run of ASCII letters) becomes random letters of the same length, seeded by the
## word itself (the same word always gives the same noise, different words do not share a letter mapping, so nothing
## can be decoded by substitution). Case pattern, digits and punctuation stay.
static func scr(s: String) -> String:
	if not scramble:
		return s
	var out := ""
	var i := 0
	while i < s.length():
		var code := s.unicode_at(i)
		if (code >= 65 and code <= 90) or (code >= 97 and code <= 122):
			var j := i
			while j < s.length() and ((s.unicode_at(j) >= 65 and s.unicode_at(j) <= 90) or (s.unicode_at(j) >= 97 and s.unicode_at(j) <= 122)):
				j += 1
			out += _noise_word(s.substr(i, j - i))
			i = j
		else:
			out += s[i]
			i += 1
	return out


static func _noise_word(w: String) -> String:
	if _word_cache.has(w):
		return _word_cache[w]
	var rng := RandomNumberGenerator.new()
	rng.seed = w.to_lower().hash()
	var out := ""
	for k in range(w.length()):
		var base := 65 if w.unicode_at(k) <= 90 else 97
		out += char(base + rng.randi_range(0, 25))
	_word_cache[w] = out
	return out


const BATTERED := Color8(250, 176, 40)
const DAMAGED_C := Color8(255, 100, 56)


## The color of an outcome tier: EVADED teal, HOLDS neutral, BATTERED amber, DAMAGED orange, BREACHED red.
static func tier_color(tier: String) -> Color:
	match tier:
		"EVADED":
			return CLEAN
		"HOLDS":
			return HOLD_OK
		"BATTERED":
			return BATTERED
		"DAMAGED":
			return DAMAGED_C
	return DMG


## The tier's word on the stamp and the record.
static func tier_word(tier: String) -> String:
	match tier:
		"EVADED":
			return "EVADED"
		"HOLDS":
			return "CELL HOLDS"
		"BATTERED":
			return "CELL BATTERED"
		"DAMAGED":
			return "CELL DAMAGED"
	return "BREACHED"


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


## Candidate end shapes: 0 triangle, 1 square, 2 circle. Outline only (or filled).
static func cand_shape(ci: CanvasItem, c: Vector2, i: int, r: float, col: Color, fill: Color = Color(0, 0, 0, 0), w: float = 3.0) -> void:
	var pts: PackedVector2Array
	match i:
		0:
			pts = PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, r * 0.8), c + Vector2(-r, r * 0.8)])
		1:
			pts = PackedVector2Array([c + Vector2(-r, -r), c + Vector2(r, -r), c + Vector2(r, r), c + Vector2(-r, r)])
		_:
			pts = PackedVector2Array()
			for k in range(16):
				pts.append(c + Vector2(cos(k * TAU / 16.0), sin(k * TAU / 16.0)) * r * 1.05)
	if fill.a > 0.0:
		ci.draw_colored_polygon(pts, fill)
	pts.append(pts[0])
	ci.draw_polyline(pts, col, w, true)


## Beam-order badge (1, 2, 3).
static func badge(ci: CanvasItem, c: Vector2, n: Variant, col: Color = THREAT) -> void:
	var s := str(n)
	var r := 11.0 if s.length() < 2 else 15.0
	ci.draw_circle(c, r, col)
	ci.draw_arc(c, r, 0.0, TAU, 20, INK, 1.5, true)
	text_c(ci, c, s, 15, INK)


## Wrench (the DOWN mark): a handle with an open jaw.
static func wrench(ci: CanvasItem, c: Vector2, r: float, col: Color = DMG) -> void:
	ci.draw_line(c + Vector2(r * 0.9, r * 0.9), c + Vector2(-r * 0.2, -r * 0.2), col, 5.0, true)
	ci.draw_arc(c + Vector2(-r * 0.5, -r * 0.5), r * 0.62, PI * 0.9, PI * 2.55, 14, col, 4.0, true)


## Spoof key: the teal skip-chevron in a rounded key (the spoof's own mark; no other thing uses a chevron).
static func spoof_key(ci: CanvasItem, c: Vector2, col: Color) -> void:
	panel(ci, Rect2(c.x - 26, c.y - 14, 52, 28), col, Color(0, 0, 0, 0), 3.0)
	skip_chevron(ci, c, 8.0, col, 3.0)


## Skip-chevron: a double chevron pointing right with a bar after it ("jump over this node").
static func skip_chevron(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 3.0) -> void:
	for k in range(2):
		var x := c.x + (k - 1) * r * 0.9 - r * 0.35
		ci.draw_polyline(PackedVector2Array([Vector2(x - r * 0.45, c.y - r), Vector2(x + r * 0.45, c.y), Vector2(x - r * 0.45, c.y + r)]), col, w, true)
	ci.draw_line(Vector2(c.x + r * 0.95, c.y - r), Vector2(c.x + r * 0.95, c.y + r), col, w, true)


## A decoy diamond outline.
static func diamond(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 3.0) -> void:
	ci.draw_polyline(PackedVector2Array([c + Vector2(0, -r), c + Vector2(r, 0), c + Vector2(0, r), c + Vector2(-r, 0), c + Vector2(0, -r)]), col, w, true)


## A stamp: a bordered word, tilted.
static func stamp(ci: CanvasItem, c: Vector2, word: String, col: Color, size: int, sub: String = "") -> void:
	ci.draw_set_transform(c, -0.12, Vector2.ONE)
	var w := maxf(text_w(word, size), text_w(sub, int(size * 0.62)) if sub != "" else 0.0) + 36.0
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


## DOWN mark (GDD): a white lightning bolt.
static func bolt(ci: CanvasItem, c: Vector2, r: float, col: Color = INK) -> void:
	ci.draw_colored_polygon(PackedVector2Array([c + Vector2(r * 0.35, -r), c + Vector2(-r * 0.55, r * 0.15), c + Vector2(-r * 0.02, r * 0.15),
		c + Vector2(-r * 0.35, r), c + Vector2(r * 0.55, -r * 0.2), c + Vector2(r * 0.02, -r * 0.2)]), col)


## TAKEN: a cobalt corp marker (hexagon with a flag).
static func corp(ci: CanvasItem, c: Vector2, r: float) -> void:
	hexagon(ci, c, r, Color8(30, 44, 110), THREAT_LIGHT, maxf(2.0, r * 0.14))
	ci.draw_line(c + Vector2(-r * 0.25, r * 0.55), c + Vector2(-r * 0.25, -r * 0.55), INK, maxf(1.5, r * 0.12), true)
	ci.draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.25, -r * 0.55), c + Vector2(r * 0.5, -r * 0.3), c + Vector2(-r * 0.25, -r * 0.05)]), INK)


## HOME server: a rounded square with two stacked bars.
static func home_server(ci: CanvasItem, c: Vector2, r: float, edge: Color, fill: Color = PANEL) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.set_corner_radius_all(maxi(2, int(r * 0.15)))
	sb.border_color = edge
	sb.set_border_width_all(maxi(2, int(r * 0.1)))
	ci.draw_style_box(sb, Rect2(c.x - r, c.y - r, r * 2.0, r * 2.0))
	for k in range(2):
		var y := c.y - r * 0.38 + k * r * 0.76
		ci.draw_rect(Rect2(c.x - r * 0.6, y - r * 0.2, r * 1.2, r * 0.4), edge, false, maxf(1.0, r * 0.08))
		ci.draw_circle(Vector2(c.x + r * 0.35, y), r * 0.09, edge)


## A pip: filled (integrity left), hollow red cross (lost), hatched (projected loss), saved (spoof keeps it).
static func pip(ci: CanvasItem, c: Vector2, s: float, mode: String) -> void:
	var r := Rect2(c.x - s * 0.5, c.y - s * 0.5, s, s)
	match mode:
		"full":
			ci.draw_rect(r, CELL)
		"lost":
			ci.draw_rect(r, DMG, false, 2.0)
			cross(ci, c, s * 0.28, DMG, 2.0)
		"proj":
			ci.draw_rect(r, Color(DMG.r, DMG.g, DMG.b, 0.3))
			ci.draw_rect(r, DMG, false, 2.0)
			ci.draw_line(r.position + Vector2(0, s), r.position + Vector2(s, 0), DMG, 2.0, true)
		"saved":
			ci.draw_rect(r, CELL)
			ci.draw_rect(r.grow(3.0), CLEAN, false, 2.0)
		_:
			ci.draw_rect(r, PANEL_EDGE, false, 2.0)


## The hunter's rule: an arrow that comes in from the upper right of the first touch, turns and ends ON its column, just
## above the node, heading down (a quarter turn of radius `r`). `dx` is the column's offset from the node's x (a column
## drawn shifted to stay clear of another line). `prog` 0..1 draws it growing. Returns the tip.
static func turn_arrow(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 4.0, prog: float = 1.0, dx: float = 0.0) -> Vector2:
	var end := Vector2(c.x + dx, c.y - 36.0)
	var k := end + Vector2(r, 0.0)
	var pts := PackedVector2Array()
	var n_seg := 16
	var upto := clampf(prog, 0.0, 1.0)
	var th := -PI * 0.5
	for i in range(int(ceil(n_seg * upto)) + 1):
		var f := minf(float(i) / n_seg, upto)
		th = -PI * 0.5 - PI * 0.5 * f
		pts.append(k + Vector2(cos(th), sin(th)) * r)
	if pts.size() >= 2:
		ci.draw_polyline(pts, col, w, true)
	var tip: Vector2 = pts[pts.size() - 1]
	var d := Vector2(sin(th), -cos(th))
	var nn := Vector2(-d.y, d.x)
	ci.draw_colored_polygon(PackedVector2Array([tip + d * 11.0, tip - d * 3.0 + nn * 8.0, tip - d * 3.0 - nn * 8.0]), col)
	return tip


## JAM: the hunter's down chevrons inside a ring, struck by a slash ("the hunter does not run").
static func jam_mark(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 2.5) -> void:
	chevron_down(ci, c + Vector2(0, -r * 0.35), r * 0.55, col, w)
	chevron_down(ci, c + Vector2(0, r * 0.3), r * 0.55, col, w)
	ci.draw_line(c + Vector2(-r * 0.95, r * 0.95), c + Vector2(r * 0.95, -r * 0.95), DMG, w + 0.5, true)


## The hunter's own line when nothing was touched: a ring-topped pin on the column (it has no target, it runs its fixed
## line), drawn at c.
static func own_line(ci: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	circle(ci, c, r, col, 3.0)
	ci.draw_circle(c, r * 0.4, col)
	ci.draw_line(c + Vector2(0, r), c + Vector2(0, r * 2.2), col, 3.0, true)
	ci.draw_line(c + Vector2(-r * 0.7, r * 2.2), c + Vector2(r * 0.7, r * 2.2), col, 3.0, true)


## A small chevron pointing down (the hunter runs this way).
static func chevron_down(ci: CanvasItem, c: Vector2, r: float, col: Color, w: float = 3.0) -> void:
	ci.draw_polyline(PackedVector2Array([c + Vector2(-r, -r * 0.5), c + Vector2(0, r * 0.5), c + Vector2(r, -r * 0.5)]), col, w, true)


## A beam's stop: a bar across the beam with a short tick behind it. `d` is the beam's direction.
static func stop_bar(ci: CanvasItem, c: Vector2, d: Vector2, col: Color) -> void:
	var n := Vector2(-d.y, d.x)
	ci.draw_line(c - n * 17.0, c + n * 17.0, col, 6.0, true)
	ci.draw_line(c - n * 11.0 - d * 7.0, c + n * 11.0 - d * 7.0, col, 2.0, true)


## The go-dark glyph: a black disc with a grey ring.
static func dark_disc(ci: CanvasItem, c: Vector2, r: float, col: Color = DIM) -> void:
	ci.draw_circle(c, r, Color8(10, 10, 16))
	circle(ci, c, r, col, maxf(2.0, r * 0.18))


## The ghost's detour: a half ring round a node on one side of the beam (`d` is the beam's direction, `side` +1 / -1).
static func detour(ci: CanvasItem, c: Vector2, r: float, d: Vector2, side: float, col: Color, w: float = 3.0) -> void:
	var n := Vector2(-d.y, d.x) * side
	var pts := PackedVector2Array()
	for k in range(13):
		var th := PI * k / 12.0
		pts.append(c - d * (r * cos(th)) + n * (r * sin(th)))
	ci.draw_polyline(pts, col, w, true)
	var last := pts[pts.size() - 1]
	var prev := pts[pts.size() - 2]
	var dd := (last - prev).normalized()
	var nn := Vector2(-dd.y, dd.x)
	ci.draw_colored_polygon(PackedVector2Array([last + dd * 8.0, last - dd * 2.0 + nn * 6.0, last - dd * 2.0 - nn * 6.0]), col)
