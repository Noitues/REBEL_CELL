class_name TideGlyphs
extends RefCounted
## Phase 3 (Solace Infected Tide raid screen): the wordless glyph set, drawn on any CanvasItem. Ported from the raid lab
## (L14 to L17 UI): five tier shapes (HOLDS full shield, SITES LOST cracked shield, DAMAGED broken heart, BREACHED skull,
## EVADED open eye), the type shapes (D triangle, N square, E circle), the verb glyphs (GUARD shield, SHIFT curved arrow,
## JAM zigzag, a wound's crack), the response glyphs and the small HUD icons. Pure drawing: no state, no rules.

const TYPE_COLOR := {"D": Palette.TIDE_TYPE_D, "N": Palette.TIDE_TYPE_N, "E": Palette.TIDE_TYPE_E}
const TIER_COLOR := {"BREACHED": Palette.TIDE_BREACHED, "DAMAGED": Palette.TIDE_DAMAGED, "SITES LOST": Palette.TIDE_SITES_LOST,
	"HOLDS": Palette.TIDE_HOLDS, "EVADED": Palette.TIDE_EVADED}
## Best first: the raid tier ladder the legend pins.
const TIER_LADDER: Array[String] = ["EVADED", "HOLDS", "SITES LOST", "DAMAGED", "BREACHED"]
const TIER_RANK := {"EVADED": 0, "HOLDS": 1, "SITES LOST": 2, "DAMAGED": 3, "BREACHED": 4}

const INK := Palette.TIDE_INK
const DIM := Palette.TIDE_DIM
const LATER := Palette.TIDE_LATER
const GOLD := Palette.TIDE_GOLD
const COBALT := Palette.TIDE_COBALT
const COBALT_HOT := Palette.TIDE_COBALT_HOT
const RED := Palette.TIDE_RED
const GREY := Palette.TIDE_GREY
const PANEL := Palette.TIDE_PANEL
const EDGE := Palette.TIDE_EDGE
const WOUND_FILL := Palette.TIDE_WOUND
const HEAT_COL := Palette.TIDE_HEAT
const YELLOW := Palette.TIDE_YELLOW
const BLACK := Palette.TIDE_BLACK
const NIGHT := Palette.TIDE_NIGHT
const ACID := Palette.TIDE_EVADED
## The shade of a sentry's disk and of a dimmed ring.
const DISK_ALPHA := 0.62
## The font size of a card's title and Heat number.
const CARD_TITLE_PX := 11
const TILE_FILL_ALPHA := 0.3
const TILE_TEXT_PX := 13
const METER_GAP := 2.0
const METER_CELL_MAX := 16.0


## The color of raid tier `tier`.
static func tier_color(tier: String) -> Color:
	return TIER_COLOR.get(tier, INK)


## The player's word for raid tier `tier` (the rules' EVADED is read UNTOUCHED).
static func tier_word(tier: String) -> String:
	return String(TranslationServer.translate("UNTOUCHED" if tier == "EVADED" else tier))


## 0 (best) to 4 (worst).
static func rank(tier: String) -> int:
	return int(TIER_RANK.get(tier, 0))


## The color of card or beam type `t` (D, N, E).
static func type_color(t: String) -> Color:
	return TYPE_COLOR.get(t, GREY)


## The type shape: triangle D, square N, circle E.
static func type_shape(cv: CanvasItem, c: Vector2, t: String, r: float, col: Color) -> void:
	match t:
		"D":
			cv.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -r), c + Vector2(r * 0.9, r * 0.65), c + Vector2(-r * 0.9, r * 0.65)]), col)
		"N":
			cv.draw_rect(Rect2(c - Vector2(r, r) * 0.75, Vector2(r, r) * 1.5), col)
		_:
			cv.draw_circle(c, r * 0.8, col)


static func crack(cv: CanvasItem, c: Vector2, r: float, col: Color, w: float = 2.0) -> void:
	cv.draw_polyline(PackedVector2Array([c + Vector2(-r * 0.2, -r), c + Vector2(r * 0.25, -r * 0.35), c + Vector2(-r * 0.2, r * 0.1),
		c + Vector2(r * 0.2, r * 0.55), c + Vector2(0.0, r)]), col, w)


static func xmark(cv: CanvasItem, c: Vector2, r: float, col: Color, w: float = 2.0) -> void:
	cv.draw_line(c + Vector2(-r, -r), c + Vector2(r, r), col, w)
	cv.draw_line(c + Vector2(r, -r), c + Vector2(-r, r), col, w)


static func shield_pts(c: Vector2, r: float) -> PackedVector2Array:
	return PackedVector2Array([c + Vector2(-r * 0.8, -r * 0.85), c + Vector2(r * 0.8, -r * 0.85), c + Vector2(r * 0.8, -r * 0.05),
		c + Vector2(0.0, r * 0.95), c + Vector2(-r * 0.8, -r * 0.05)])


## The card verb: GUARD shield, SHIFT curved arrow, JAM zigzag, WOUND crack, DOSE a plus.
static func verb(cv: CanvasItem, c: Vector2, v: String, r: float, col: Color) -> void:
	var lw := maxf(1.5, r * 0.2)
	match v:
		"GUARD":
			cv.draw_colored_polygon(shield_pts(c, r), col)
		"SHIFT":
			var rr := r * 0.75
			cv.draw_arc(c + Vector2(0.0, r * 0.2), rr, PI, TAU, 14, col, lw)
			var e := c + Vector2(rr, r * 0.2)
			cv.draw_colored_polygon(PackedVector2Array([e + Vector2(-r * 0.4, -r * 0.05), e + Vector2(r * 0.4, -r * 0.05), e + Vector2(0.0, r * 0.55)]), col)
		"JAM":
			cv.draw_polyline(PackedVector2Array([c + Vector2(-r, r * 0.2), c + Vector2(-r * 0.5, -r * 0.6), c + Vector2(0.0, r * 0.6),
				c + Vector2(r * 0.5, -r * 0.6), c + Vector2(r, r * 0.2)]), col, lw)
		"WOUND":
			crack(cv, c, r, col, lw)
		"DOSE":
			cv.draw_line(c + Vector2(-r * 0.7, 0.0), c + Vector2(r * 0.7, 0.0), col, lw * 1.4)
			cv.draw_line(c + Vector2(0.0, -r * 0.7), c + Vector2(0.0, r * 0.7), col, lw * 1.4)


## A wordless card face in `r`: the verb glyph dominates, the type shape is a corner badge. A wound is a cracked gray card with a red
## X; `card` is [id, type, verb]. `gold` = the extra card a Heat level deals.
static func card_face(cv: CanvasItem, r: Rect2, card: Array, dim: bool = false, gold: bool = false, title: String = "", heat: int = -1) -> void:
	if card.size() < 3:
		return
	var s := minf(r.size.x, r.size.y)
	var verb_word := String(card[2])
	var edge := GOLD if gold else (EDGE.darkened(0.4) if dim else EDGE)
	var font := ThemeDB.fallback_font
	var ink := DIM if dim else INK
	if verb_word == "WOUND":
		cv.draw_rect(r, WOUND_FILL)
		cv.draw_rect(r, GREY, false, 1.5)
		var c := r.get_center() + Vector2(0.0, 6.0)
		crack(cv, c, s * 0.34, GREY.lightened(0.2), maxf(1.5, s * 0.06))
		xmark(cv, c, s * 0.24, RED.darkened(0.35) if dim else RED, maxf(1.5, s * 0.09))
		if title != "":
			cv.draw_string(font, r.position + Vector2(4.0, 13.0), title, HORIZONTAL_ALIGNMENT_LEFT, r.size.x - 8.0, CARD_TITLE_PX, GREY.lightened(0.35))
		return
	cv.draw_rect(r, PANEL)
	cv.draw_rect(r, edge, false, 2.0 if gold else 1.5)
	var t := String(card[1])
	if title != "":
		cv.draw_string(font, r.position + Vector2(4.0, 13.0), title, HORIZONTAL_ALIGNMENT_LEFT, r.size.x - 8.0, CARD_TITLE_PX, ink)
	verb(cv, r.get_center() + Vector2(0.0, 1.0), verb_word, s * 0.27, ink)
	# The foot: the target glyph (the beam type the card answers) at left, the Heat cost at right.
	var foot := r.end.y - 11.0
	if verb_word != "DOSE":
		type_shape(cv, Vector2(r.position.x + 12.0, foot), t, 6.5, type_color(t).darkened(0.45) if dim else type_color(t))
	if heat >= 0:
		var hc := HEAT_COL.darkened(0.45) if dim else HEAT_COL
		flame(cv, Vector2(r.end.x - 30.0, foot + 1.0), 4.4)
		cv.draw_string(font, Vector2(r.end.x - 23.0, foot + 4.5), "+%d" % heat if heat > 0 else "0", HORIZONTAL_ALIGNMENT_LEFT, 22.0, CARD_TITLE_PX, hc)


static func heart(cv: CanvasItem, c: Vector2, r: float, col: Color, broken: bool) -> void:
	cv.draw_circle(c + Vector2(-r * 0.45, -r * 0.2), r * 0.5, col)
	cv.draw_circle(c + Vector2(r * 0.45, -r * 0.2), r * 0.5, col)
	cv.draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.93, -r * 0.05), c + Vector2(r * 0.93, -r * 0.05), c + Vector2(0.0, r * 0.95)]), col)
	if broken:
		cv.draw_polyline(PackedVector2Array([c + Vector2(0.0, -r * 0.55), c + Vector2(r * 0.18, -r * 0.15), c + Vector2(-r * 0.15, r * 0.2),
			c + Vector2(r * 0.1, r * 0.55), c + Vector2(0.0, r * 0.9)]), NIGHT, maxf(1.5, r * 0.22))


static func skull(cv: CanvasItem, c: Vector2, r: float, col: Color, hole: Color) -> void:
	cv.draw_circle(c + Vector2(0.0, -r * 0.15), r * 0.8, col)
	cv.draw_rect(Rect2(c + Vector2(-r * 0.45, r * 0.3), Vector2(r * 0.9, r * 0.6)), col)
	cv.draw_circle(c + Vector2(-r * 0.32, -r * 0.15), r * 0.22, hole)
	cv.draw_circle(c + Vector2(r * 0.32, -r * 0.15), r * 0.22, hole)
	var tw := maxf(1.0, r * 0.12)
	cv.draw_line(c + Vector2(-r * 0.15, r * 0.5), c + Vector2(-r * 0.15, r * 0.9), hole, tw)
	cv.draw_line(c + Vector2(r * 0.15, r * 0.5), c + Vector2(r * 0.15, r * 0.9), hole, tw)


## The five tier shapes, used everywhere (forecast, rows, stamps, the record, the HOME glyphs).
static func tier(cv: CanvasItem, c: Vector2, tier_word: String, r: float, col: Color = Palette.CLEAR) -> void:
	var k := col if col.a > 0.0 else tier_color(tier_word)
	var w := maxf(2.0, r * 0.3)
	match tier_word:
		"EVADED":
			cv.draw_arc(c + Vector2(0.0, r * 0.55), r, PI * 1.2, PI * 1.8, 12, k, w * 0.6)
			cv.draw_arc(c - Vector2(0.0, r * 0.55), r, PI * 0.2, PI * 0.8, 12, k, w * 0.6)
			cv.draw_circle(c, r * 0.32, k)
		"HOLDS":
			cv.draw_colored_polygon(shield_pts(c, r), k)
		"SITES LOST":
			cv.draw_colored_polygon(shield_pts(c, r), k)
			cv.draw_polyline(PackedVector2Array([c + Vector2(-r * 0.1, -r * 0.9), c + Vector2(r * 0.25, -r * 0.35), c + Vector2(-r * 0.2, r * 0.1),
				c + Vector2(r * 0.15, r * 0.55), c + Vector2(0.0, r * 0.9)]), NIGHT, maxf(1.5, r * 0.22))
		"DAMAGED":
			heart(cv, c, r, k, true)
		"BREACHED":
			skull(cv, c, r, k, BLACK)
		_:
			cv.draw_circle(c, r * 0.5, k)


## A tier pip: the glyph in a framed square (BREACHED reads black and red).
static func tier_pip(cv: CanvasItem, c: Vector2, tier_word: String, r: float) -> void:
	var col := tier_color(tier_word)
	var rect := Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)
	if tier_word == "BREACHED":
		cv.draw_rect(rect, BLACK)
		cv.draw_rect(rect, RED, false, 2.0)
	else:
		cv.draw_rect(rect, PANEL)
		cv.draw_rect(rect, col, false, 2.0)
	tier(cv, c, tier_word, r * 0.75, col)


static func flame(cv: CanvasItem, c: Vector2, r: float) -> void:
	cv.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -r * 1.35), c + Vector2(r * 0.5, -r * 0.45), c + Vector2(r * 0.75, r * 0.3),
		c + Vector2(r * 0.4, r * 0.85), c + Vector2(-r * 0.4, r * 0.85), c + Vector2(-r * 0.75, r * 0.3), c + Vector2(-r * 0.35, -r * 0.5)]), HEAT_COL)
	cv.draw_circle(c + Vector2(0.0, r * 0.35), r * 0.38, YELLOW)


## The "+1 beam" tick icon (a short beam with a head).
static func beam_tick(cv: CanvasItem, c: Vector2, col: Color) -> void:
	cv.draw_line(c + Vector2(-6.0, 0.0), c + Vector2(2.0, 0.0), col, 2.0)
	cv.draw_colored_polygon(PackedVector2Array([c + Vector2(1.0, -4.0), c + Vector2(6.0, 0.0), c + Vector2(1.0, 4.0)]), col)


## The "+1 card" tick icon (a small card with a plus).
static func card_tick(cv: CanvasItem, c: Vector2, col: Color) -> void:
	var r := Rect2(c - Vector2(4.5, 6.0), Vector2(9.0, 12.0))
	cv.draw_rect(r, PANEL)
	cv.draw_rect(r, col, false, 1.5)
	cv.draw_line(c + Vector2(-2.0, 0.0), c + Vector2(2.0, 0.0), col, 1.5)
	cv.draw_line(c + Vector2(0.0, -2.0), c + Vector2(0.0, 2.0), col, 1.5)


static func hound(cv: CanvasItem, c: Vector2, col: Color = COBALT_HOT) -> void:
	cv.draw_rect(Rect2(c + Vector2(-7.0, -3.0), Vector2(11.0, 5.0)), col)
	cv.draw_rect(Rect2(c + Vector2(3.0, -7.0), Vector2(6.0, 5.0)), col)
	for lx: float in [-6.0, -3.0, 0.0, 3.0]:
		cv.draw_line(c + Vector2(lx, 2.0), c + Vector2(lx, 7.0), col, 1.5)


static func ghost(cv: CanvasItem, c: Vector2, r: float, col: Color) -> void:
	for k in 8:
		var a := TAU * float(k) / 8.0
		cv.draw_arc(c, r, a, a + TAU / 16.0, 4, col, 2.0)


static func arrow(cv: CanvasItem, x: float, cy: float, col: Color) -> void:
	cv.draw_line(Vector2(x, cy), Vector2(x + 9.0, cy), col, 2.0)
	cv.draw_colored_polygon(PackedVector2Array([Vector2(x + 8.0, cy - 4.0), Vector2(x + 13.0, cy), Vector2(x + 8.0, cy + 4.0)]), col)


## A sentry marker on a Site: a post with the type shape; a held tool (SHIFT or JAM) draws its verb glyph larger than a plain
## GUARD does, so a tool reads differently from a guard.
static func sentry(cv: CanvasItem, c: Vector2, t: String, v: String, scale: float = 1.0) -> void:
	var col := type_color(t)
	var s := scale
	cv.draw_circle(c, 13.0 * s, Color(BLACK, DISK_ALPHA))
	cv.draw_arc(c, 13.0 * s, 0.0, TAU, 20, col, 2.0)
	if v == "SHIFT" or v == "JAM":
		verb(cv, c + Vector2(0.0, 1.0 * s), v, 9.5 * s, INK)
		type_shape(cv, c + Vector2(9.0, -9.0) * s, t, 4.5 * s, col)
	else:
		verb(cv, c + Vector2(0.0, 1.0 * s), "GUARD", 6.5 * s, INK)
		type_shape(cv, c + Vector2(9.0, -9.0) * s, t, 4.5 * s, col)


## A response's large verb glyph: HOLD (two bars), REDEPLOY (curved arrow), DEPLOY (an arrow dropping on a pad), SACRIFICE (a dome over
## a cracked base), JAM and JAM_B (a struck-out hound), DIVERT (a bent arrow). `r` is the response array (its head and arguments).
static func response(cv: CanvasItem, c: Vector2, r: Array, rad: float, dim: bool, sent_type: String = "") -> void:
	var head := "HOLD" if r.is_empty() else String(r[0])
	var col := INK
	match head:
		"REDEPLOY":
			col = type_color(sent_type) if sent_type != "" else ACID
		"DEPLOY":
			col = type_color(String(r[1])) if r.size() > 1 else ACID
		"SACRIFICE":
			col = COBALT_HOT
		"JAM", "JAM_B":
			col = RED
		"DIVERT":
			col = ACID
	if dim:
		col = LATER
	var lw := maxf(2.0, rad * 0.22)
	match head:
		"HOLD":
			cv.draw_rect(Rect2(c + Vector2(-rad * 0.6, -rad * 0.75), Vector2(rad * 0.4, rad * 1.5)), col)
			cv.draw_rect(Rect2(c + Vector2(rad * 0.2, -rad * 0.75), Vector2(rad * 0.4, rad * 1.5)), col)
		"REDEPLOY":
			verb(cv, c, "SHIFT", rad, col)
		"DIVERT":
			verb(cv, c, "SHIFT", rad, col)
			cv.draw_line(c + Vector2(-rad, rad * 0.9), c + Vector2(rad, rad * 0.9), col, lw)
		"DEPLOY":
			cv.draw_line(c + Vector2(0.0, -rad), c + Vector2(0.0, rad * 0.15), col, lw)
			cv.draw_colored_polygon(PackedVector2Array([c + Vector2(-rad * 0.45, rad * 0.05), c + Vector2(rad * 0.45, rad * 0.05), c + Vector2(0.0, rad * 0.6)]), col)
			cv.draw_line(c + Vector2(-rad * 0.8, rad * 0.85), c + Vector2(rad * 0.8, rad * 0.85), col, lw)
		"SACRIFICE":
			cv.draw_arc(c + Vector2(0.0, rad * 0.45), rad * 0.9, PI, TAU, 16, col, lw)
			cv.draw_line(c + Vector2(-rad, rad * 0.5), c + Vector2(rad, rad * 0.5), col, lw)
			crack(cv, c + Vector2(0.0, rad * 0.1), rad * 0.4, col, maxf(1.5, lw * 0.6))
		"JAM", "JAM_B":
			hound(cv, c, COBALT_HOT.darkened(0.3) if not dim else LATER)
			cv.draw_line(c + Vector2(-rad, rad * 0.8), c + Vector2(rad, -rad * 0.8), col, lw)


## A forecast tile: the outcome tier tinted with its color, its glyph and, when `n` outcomes share it, "x N". Pairs the five tier shapes with color.
## `inf` is the INFECTED cards that outcome adds ("+1" in the INFECTED red, "+0" dim) and `lethal` marks an outcome that ends the campaign (a skull
## on the right and a red frame).
static func tier_tile(cv: CanvasItem, r: Rect2, tier_word: String, n: int = 1, inf: int = 0, lethal: bool = false) -> void:
	if tier_word == "":
		return
	var col := tier_color(tier_word)
	if tier_word == "BREACHED":
		cv.draw_rect(r, BLACK)
		cv.draw_rect(r, RED, false, 2.0)
	else:
		cv.draw_rect(r, Color(col, TILE_FILL_ALPHA))
		cv.draw_rect(r, col, false, 2.0)
	if lethal:
		cv.draw_rect(r.grow(-1.0), RED, false, 2.0)
	var gr := minf(r.size.y * 0.5, 13.0) * 0.8
	tier(cv, Vector2(r.position.x + gr + 5.0, r.get_center().y), tier_word, gr, col)
	var x := r.position.x + gr * 2.0 + 10.0
	var f := ThemeDB.fallback_font
	if n > 1:
		var t := "x%d" % n
		cv.draw_string(f, Vector2(x, r.get_center().y + 5.0), t, HORIZONTAL_ALIGNMENT_LEFT, -1, TILE_TEXT_PX, INK)
		x += f.get_string_size(t, HORIZONTAL_ALIGNMENT_LEFT, -1, TILE_TEXT_PX).x + 6.0
	# The INFECTED change: the wound pip and its count.
	var pip := Rect2(Vector2(x, r.get_center().y - 5.5), Vector2(8.0, 11.0))
	cv.draw_rect(pip, WOUND_FILL)
	crack(cv, pip.get_center(), 3.5, RED if inf > 0 else DIM, 1.2)
	cv.draw_string(f, Vector2(x + 11.0, r.get_center().y + 5.0), "+%d" % inf, HORIZONTAL_ALIGNMENT_LEFT, -1, TILE_TEXT_PX, RED if inf > 0 else DIM)
	if lethal:
		skull(cv, Vector2(r.end.x - 11.0, r.get_center().y), 7.0, INK, BLACK)


## A route chip: a disk in the beam's type color with the route letter in it (the forecast column and the map's beam carry the same one).
static func route_chip(cv: CanvasItem, c: Vector2, letter: String, r: float, col: Color) -> void:
	cv.draw_circle(c, r * 0.95, BLACK)
	cv.draw_circle(c, r * 0.8, col)
	var px := int(maxf(9.0, r * 1.15))
	cv.draw_string(ThemeDB.fallback_font, c + Vector2(-px * 0.3, px * 0.36), letter, HORIZONTAL_ALIGNMENT_LEFT, -1, px, BLACK)


## The INFECTED vs healthy meter: one cell per INFECTED card the city can bear plus the cell that ends it. INFECTED cells fill red from the left;
## the last cell is the CITY LOST line, marked with a flag above it, and shows a cross when the city is lost.
static func infected_meter(cv: CanvasItem, r: Rect2, infected: int, healthy: int) -> void:
	var cells := healthy + 1
	var cw := minf(METER_CELL_MAX, (r.size.x - METER_GAP * float(cells - 1)) / float(maxi(1, cells)))
	var top := r.position.y + 7.0
	var ch := r.size.y - 7.0
	for i in cells:
		var x := r.position.x + float(i) * (cw + METER_GAP)
		var cell := Rect2(x, top, cw, ch)
		if i < infected:
			cv.draw_rect(cell, RED.darkened(0.15))
		else:
			cv.draw_rect(cell, WOUND_FILL)
			cv.draw_rect(cell, GREY.darkened(0.2), false, 1.0)
		if i == cells - 1:
			cv.draw_rect(cell.grow(1.0), RED, false, 2.0)
			var fx := cell.get_center().x
			cv.draw_colored_polygon(PackedVector2Array([Vector2(fx - 4.0, r.position.y), Vector2(fx + 4.0, r.position.y), Vector2(fx, r.position.y + 6.0)]), RED)
			if infected > healthy:
				xmark(cv, cell.get_center(), minf(cw, ch) * 0.3, INK, 1.5)
