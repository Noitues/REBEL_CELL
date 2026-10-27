class_name TideFx
extends RefCounted
## Art-pass owns this file and tide_look.tres; build owns flow/layout/rules.
##
## Every drawing call, color, line width, glyph shape, StyleBox builder and font size of the Infected Tide raid screen lives here (static
## functions; the look numbers are in `content/config/tide_look.tres` through `TideLookData`). The screen, the map layer, the glyph view
## and the odds bar keep the flow, the layout positions, the rules calls and the signals, and draw through these functions.
## Phase 3 (Solace Infected Tide raid screen): the wordless glyph set, drawn on any CanvasItem. Ported from the raid lab
## (L14 to L17 UI): five tier shapes (HOLDS full shield, SITES LOST cracked shield, DAMAGED broken heart, BREACHED skull,
## EVADED open eye), the type shapes (D triangle, N square, E circle), the verb glyphs (GUARD shield, SHIFT curved arrow,
## JAM zigzag, a wound's crack), the response glyphs and the small HUD icons. Pure drawing: no state, no rules.

const TYPE_COLOR := {"D": Palette.TIDE_TYPE_D, "N": Palette.TIDE_TYPE_N, "E": Palette.TIDE_TYPE_E}
const TIER_COLOR := {"BREACHED": Palette.TIDE_BREACHED, "DAMAGED": Palette.TIDE_DAMAGED, "SITES LOST": Palette.TIDE_SITES_LOST,
	"HOLDS": Palette.TIDE_HOLDS, "EVADED": Palette.TIDE_EVADED, "CITY LOST": Palette.TIDE_RED}
## Best first: the one outcome ladder the legend pins, the odds bars, the tiles and the aftermath share. CITY LOST (the run ends) is the
## presentation tier above BREACHED; the rules' `tier_of` never returns it.
const TIER_LADDER: Array[String] = ["HOLDS", "SITES LOST", "DAMAGED", "BREACHED", "CITY LOST"]
const TIER_RANK := {"EVADED": 0, "HOLDS": 0, "SITES LOST": 1, "DAMAGED": 2, "BREACHED": 3, "CITY LOST": 4}
## The terminal presentation tier.
const TIER_CITY_LOST := "CITY LOST"

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
const OFF := Palette.TIDE_OFF
const ACID := Palette.TIDE_EVADED
## The font size of a card's title and Heat number.
const CARD_TITLE_PX := 11
const TILE_TEXT_PX := 13
## The screen's font sizes: body, small, headline, and the CITY LOST word.
const TXT := 14
const SMALL := 13
const BIG := 22
const CITY_LOST_PX := 72
## The map layer's tag sizes (a note, a beam label, a DOWN / TAKEN stamp) and the odds bar's count.
const SMALL_PX := 12
const LABEL_PX := 13
const STAMP_PX := 12
const COUNT_PX := 13
## The width of a beam on the map and the alpha of a beam already fired.
const LINE_W := 3.0
const DONE_ALPHA := 0.25
## The screen's panel fill.
const PANEL_BG := Palette.TIDE_PANEL_GLASS


## The shipped look numbers.
static func look() -> TideLookData:
	return TideLookData.shipped()


## The color of raid tier `tier`.
static func tier_color(tier: String) -> Color:
	return TIER_COLOR.get(SolaceTideTally.shown_tier(tier), INK)


## The player's word for raid tier `tier` (the rules' EVADED is read HOLDS).
static func tier_word(tier: String) -> String:
	return String(TranslationServer.translate(SolaceTideTally.shown_tier(tier)))


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
	match SolaceTideTally.shown_tier(tier_word):
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
		"CITY LOST":
			skull(cv, c, r, k, BLACK)
			var xw := maxf(1.5, r * 0.22)
			cv.draw_line(c + Vector2(-r * 0.95, -r * 0.95), c + Vector2(r * 0.95, r * 0.95), BLACK, xw + 2.0)
			cv.draw_line(c + Vector2(r * 0.95, -r * 0.95), c + Vector2(-r * 0.95, r * 0.95), BLACK, xw + 2.0)
			cv.draw_line(c + Vector2(-r * 0.95, -r * 0.95), c + Vector2(r * 0.95, r * 0.95), k, xw)
			cv.draw_line(c + Vector2(r * 0.95, -r * 0.95), c + Vector2(-r * 0.95, r * 0.95), k, xw)
		_:
			cv.draw_circle(c, r * 0.5, k)


## A tier pip: the glyph in a framed square (BREACHED reads black and red).
static func tier_pip(cv: CanvasItem, c: Vector2, tier_word: String, r: float) -> void:
	var col := tier_color(tier_word)
	var rect := Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)
	if tier_word == "BREACHED" or tier_word == TIER_CITY_LOST:
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
	cv.draw_circle(c, 13.0 * s, Color(BLACK, look().disk_alpha))
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
	if tier_word == "BREACHED" or tier_word == TIER_CITY_LOST:
		cv.draw_rect(r, BLACK)
		cv.draw_rect(r, RED, false, 2.0)
	else:
		cv.draw_rect(r, Color(col, look().tile_fill_alpha))
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
	var gap := look().meter_gap
	var cw := minf(look().meter_cell_max, (r.size.x - gap * float(cells - 1)) / float(maxi(1, cells)))
	var top := r.position.y + 7.0
	var ch := r.size.y - 7.0
	for i in cells:
		var x := r.position.x + float(i) * (cw + gap)
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


# ================================================================================================ the map layer (TideRaidLayer)
## The front tint (the neighbours of INFECTED Sites), the TAKEN tint and the INFECTED disks, at their points (px).
static func tints(ci: CanvasItem, front_pts: PackedVector2Array, taken_pts: PackedVector2Array, infected_pts: PackedVector2Array) -> void:
	var lk := look()
	for p in front_pts:
		ci.draw_circle(p, lk.front_r, Palette.TIDE_FRONT_FILL)
	for p in taken_pts:
		ci.draw_circle(p, lk.front_r * 0.8, Palette.TIDE_TAKEN_FILL)
	for p in infected_pts:
		ci.draw_circle(p, lk.infect_r, Palette.TIDE_INFECT_FILL)
		ci.draw_arc(p, lk.infect_r, 0.0, TAU, 24, Palette.TIDE_INFECT_EDGE, 1.5)
		crack(ci, p, 9.0, Palette.TIDE_INFECT_CRACK, 1.5)


## One beam's line, its head shape at the start and its arrowhead (or, while `travelling`, the pulse) at the end of `dp`, in `col` (alpha folded in).
static func beam(ci: CanvasItem, dp: PackedVector2Array, type: String, col: Color, a: float, w: float, is_dashed: bool, travelling: bool) -> void:
	var ink := Color(BLACK, look().ink_alpha * a)
	if is_dashed:
		dashed_line(ci, dp, ink, w + 2.0)
		dashed_line(ci, dp, col, w)
	else:
		ci.draw_polyline(dp, ink, w + 2.0)
		ci.draw_polyline(dp, col, w)
	type_shape(ci, dp[0], type, 7.0, col)
	var d := (dp[dp.size() - 1] - dp[dp.size() - 2]).normalized()
	if travelling:
		pulse(ci, dp, col, a)
	else:
		var tip := dp[dp.size() - 1] - d * 14.0
		var n := Vector2(-d.y, d.x)
		ci.draw_colored_polygon(PackedVector2Array([tip + d * 9.0, tip - n * 5.0, tip + n * 5.0]), col)


## The pulse: a bright tail along the end of the drawn beam `dp` and a glowing head.
static func pulse(ci: CanvasItem, dp: PackedVector2Array, col: Color, a: float) -> void:
	var lk := look()
	var total := 0.0
	for i in dp.size() - 1:
		total += dp[i].distance_to(dp[i + 1])
	var head := dp[dp.size() - 1]
	var from := maxf(0.0, total * (1.0 - lk.pulse_tail))
	var tp := PackedVector2Array()
	var run := 0.0
	for i in dp.size() - 1:
		var seg := dp[i].distance_to(dp[i + 1])
		if run + seg >= from:
			tp.append(dp[i] if run >= from else dp[i].lerp(dp[i + 1], (from - run) / maxf(seg, 0.001)))
			tp.append(dp[i + 1])
		run += seg
	if tp.size() >= 2:
		ci.draw_polyline(tp, Color(INK, a), 3.0)
	ci.draw_circle(head, lk.pulse_r + 5.0, Color(col, 0.28 * a))
	ci.draw_circle(head, lk.pulse_r, Color(col, 0.75 * a))
	ci.draw_circle(head, lk.pulse_r * 0.5, Color(INK, a))


## A dashed polyline (dash lengths from the look).
static func dashed_line(ci: CanvasItem, pts: PackedVector2Array, col: Color, w: float) -> void:
	var lk := look()
	var on := true
	var left := lk.dash_on
	for i in pts.size() - 1:
		var a := pts[i]
		var b := pts[i + 1]
		var seg := a.distance_to(b)
		var dir := (b - a) / maxf(seg, 0.001)
		var t := 0.0
		while t < seg:
			var step := minf(left, seg - t)
			if on:
				ci.draw_line(a + dir * t, a + dir * (t + step), col, w)
			t += step
			left -= step
			if left <= 0.001:
				on = not on
				left = lk.dash_on if on else lk.dash_off


## The mark of a Site the beam has hit: a red cross.
static func hit_cross(ci: CanvasItem, p: Vector2) -> void:
	xmark(ci, p, 7.0, RED, 2.5)


## The route chip beside a beam's start, in the beam's type color `col` (alpha folded in).
static func beam_chip(ci: CanvasItem, start: Vector2, letter: String, col: Color) -> void:
	route_chip(ci, start + Vector2(14.0, -14.0), letter, look().chip_r, col)


## The ring on the beam the player is working on (`a` = its alpha).
static func beam_current(ci: CanvasItem, start: Vector2, a: float) -> void:
	ci.draw_arc(start, 12.0, 0.0, TAU, 20, Color(INK, a), 2.0)


## One tag plate of the map, in `box`: the leader line from `anchor` when the box stands off it, the black plate, the frame, the kind's icon
## ("stamp_taken", "stamp_down", "bad") and the text.
static func tag(ci: CanvasItem, font: Font, box: Rect2, anchor: Vector2, text: String, col: Color, a: float, px: int, kind: String) -> void:
	var pad := look().label_pad
	var edge := Vector2(clampf(anchor.x, box.position.x, box.end.x), clampf(anchor.y, box.position.y, box.end.y))
	if edge.distance_to(anchor) > 6.0:
		ci.draw_line(anchor, edge, Color(col, 0.9), 1.5)
		ci.draw_circle(anchor, 2.5, col)
	ci.draw_rect(box, Color(BLACK, 0.86))
	ci.draw_rect(box, Color(col, 0.95), false, 2.0 if kind != "label" else 1.5)
	var tx := box.position.x + pad
	var gc := Vector2(box.position.x + 9.0, box.get_center().y)
	match kind:
		"stamp_taken":
			crack(ci, gc, 5.0, col, 1.5)
			tx += 12.0
		"stamp_down":
			ci.draw_colored_polygon(PackedVector2Array([gc + Vector2(1.0, -6.0), gc + Vector2(-4.0, 1.0), gc + Vector2(-0.5, 1.0), gc + Vector2(-1.5, 6.0), gc + Vector2(4.0, -1.5), gc + Vector2(0.5, -1.5)]), INK)
			tx += 12.0
		"bad":
			xmark(ci, gc, 5.0, col, 2.0)
			tx += 12.0
	ci.draw_string(font, Vector2(tx, box.end.y - 5.0), text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(INK, a))


## A Site the raid hit: the infection's magenta disk with a cross.
static func site_hit(ci: CanvasItem, p: Vector2) -> void:
	var lk := look()
	ci.draw_circle(p, lk.infect_r, Palette.TIDE_INFECT_FILL)
	ci.draw_arc(p, lk.infect_r, 0.0, TAU, 24, Palette.TIDE_INFECT_EDGE, 2.0)
	xmark(ci, p, 7.0, RED, 2.5)


## A guard that stopped a beam of `type`: its ring and the GUARD word-glyph above.
static func guard_block(ci: CanvasItem, p: Vector2, type: String) -> void:
	ci.draw_arc(p, 17.0, 0.0, TAU, 20, type_color(type), 3.0)
	verb(ci, p + Vector2(0, -24.0), "GUARD", 8.0, INK)


## The ring of a Site a sentry's shield covers.
static func shield_ring(ci: CanvasItem, p: Vector2) -> void:
	ci.draw_arc(p, 23.0, 0.0, TAU, 28, COBALT_HOT, 3.0)


## The faint ring of a Site whose shield just ended.
static func shield_gone_ring(ci: CanvasItem, p: Vector2) -> void:
	ci.draw_arc(p, 23.0, 0.0, TAU, 28, Color(COBALT_HOT, 0.35), 1.5)


## The forecast ring on a Site that would go DOWN or TAKEN.
static func forecast_ring(ci: CanvasItem, p: Vector2) -> void:
	ci.draw_arc(p, 21.0, 0.0, TAU, 28, RED, 3.0)


## The forecast rings of a Site that would fall with no sentry (two rings).
static func forecast_falls_ring(ci: CanvasItem, p: Vector2) -> void:
	ci.draw_arc(p, 21.0, 0.0, TAU, 28, RED, 3.0)
	ci.draw_arc(p, 26.0, 0.0, TAU, 28, Color(RED, 0.5), 1.5)


## The forecast ring on HOME, in `col` (see `forecast_home_color`).
static func forecast_home_ring(ci: CanvasItem, hp: Vector2, col: Color) -> void:
	ci.draw_arc(hp, 28.0, 0.0, TAU, 32, col, 3.5)


## The color of the forecast ring on HOME: red for damage, the SITES LOST color when Sites are hit, the HOLDS color when safe.
static func forecast_home_color(damage: int, sites_hit: bool) -> Color:
	return RED if damage > 0 else (Palette.TIDE_SITES_LOST if sites_hit else TIER_COLOR["HOLDS"])


## A sentry that does nothing: a red ring and cross over its post (the post stands 24 px above the Site).
static func bad_sentry(ci: CanvasItem, p: Vector2) -> void:
	ci.draw_arc(p + Vector2(0.0, -24.0), 17.0, 0.0, TAU, 24, RED, 3.0)
	xmark(ci, p + Vector2(0.0, -24.0), 14.0, RED, 3.0)


## The picked card tried on a Site: a red ring and cross (it would do nothing) or a clear ring (it would work).
static func ghost_site(ci: CanvasItem, p: Vector2, useless: bool) -> void:
	if useless:
		ci.draw_arc(p, 19.0, 0.0, TAU, 24, Color(RED, 0.9), 2.5)
		xmark(ci, p, 7.0, RED, 2.5)
	else:
		ci.draw_arc(p, 19.0, 0.0, TAU, 24, Color(TIER_COLOR["HOLDS"], 0.9), 2.5)


## A standing sentry above its Site at `p` (the post stands 24 px above the Site).
static func sentry_post(ci: CanvasItem, p: Vector2, type: String, verb_word: String) -> void:
	sentry(ci, p + Vector2(0.0, -24.0), type, verb_word, look().sentry_scale)
	ci.draw_line(p + Vector2(0.0, -9.0), p + Vector2(0.0, -9.0), INK, 1.0)


## HOME: the dashed ghost ring, the worst tier of each candidate route (glyph + chip) under it, and the ring on the core.
static func home_marks(ci: CanvasItem, hp: Vector2, has_home: bool, ghost_home: bool, tiers: Array, cols: Array[Color], letters: Array[String], cp: Vector2, has_core: bool) -> void:
	var lk := look()
	if has_home:
		if ghost_home:
			ghost(ci, hp, 24.0, COBALT_HOT)
		for i in tiers.size():
			var off := Vector2(-30.0 + 30.0 * i, 30.0)
			var c := hp + off
			ci.draw_circle(c, lk.home_glyph_r + 4.0, Color(BLACK, lk.ink_alpha))
			tier(ci, c, String(tiers[i]), lk.home_glyph_r)
			var chip_col: Color = cols[i] if i < cols.size() else DIM
			route_chip(ci, c + Vector2(0.0, lk.home_glyph_r + 13.0), letters[i], lk.chip_r, chip_col)
	if has_core:
		ci.draw_arc(cp, 26.0, 0.0, TAU, 28, COBALT_HOT, 2.0)


## The beat's impact on a Site: a solid ring, a pulse ring swelling out of it (`k` 0..1), spokes and a cross.
static func impact(ci: CanvasItem, p: Vector2, col: Color, k: float) -> void:
	var lk := look()
	ci.draw_circle(p, lk.impact_r + 4.0, Color(BLACK, 0.45))
	ci.draw_arc(p, lk.impact_r, 0.0, TAU, 28, col, 3.5)
	ci.draw_arc(p, lk.impact_r + 22.0 * k, 0.0, TAU, 28, Color(col, 1.0 - k), 2.5)
	for s in lk.impact_spokes:
		var d := Vector2.from_angle(TAU * float(s) / float(lk.impact_spokes) + 0.2)
		ci.draw_line(p + d * (lk.impact_r + 5.0), p + d * (lk.impact_r + 13.0 + 6.0 * k), col, 2.0)
	xmark(ci, p, 7.0, RED, 3.0)


## One effect of the beat at `p`, `k` (0..1) through it, over a layer of `layer_size`: "shield", "slam", "home" or "bloom".
static func burst(ci: CanvasItem, kind: String, p: Vector2, col: Color, k: float, layer_size: Vector2) -> void:
	var lk := look()
	match kind:
		"shield":
			# The guard holds: a shield swells over the Site and a ring runs out of it.
			var r := 16.0 + 8.0 * k
			ci.draw_circle(p, 26.0, Color(INK, 0.45 * (1.0 - k)))
			ci.draw_colored_polygon(shield_pts(p, r), Color(col, 0.55))
			ci.draw_polyline(closed(shield_pts(p, r)), INK, 2.5)
			ci.draw_arc(p, 20.0 + 38.0 * k, 0.0, TAU, 32, Color(col, 1.0 - k), 3.0)
			ci.draw_arc(p, 20.0 + 22.0 * k, 0.0, TAU, 32, Color(INK, 0.8 * (1.0 - k)), 2.0)
		"slam":
			# A Site is hit: a heavy magenta impact, a hard ring and spokes, the whole map flashing.
			var r := lerpf(10.0, lk.slam_r, 1.0 - pow(1.0 - k, 3.0))
			ci.draw_rect(Rect2(Vector2.ZERO, layer_size), Color(Palette.TIDE_INFECT_EDGE, lk.slam_flash_alpha * (1.0 - k)))
			ci.draw_circle(p, r, Color(Palette.TIDE_INFECT_FILL, 0.75))
			ci.draw_arc(p, r, 0.0, TAU, 40, Color(INK, 1.0 - 0.6 * k), 5.0)
			ci.draw_arc(p, r * 0.6, 0.0, TAU, 32, Palette.TIDE_INFECT_EDGE, 3.5)
			for s in lk.burst_spokes:
				var d := Vector2.from_angle(TAU * float(s) / float(lk.burst_spokes) + 0.15)
				ci.draw_line(p + d * (r * 0.7), p + d * (r + 14.0 * (1.0 - k)), Color(Palette.TIDE_INFECT_CRACK, 1.0 - k), 3.0)
			crack(ci, p, 14.0 + 8.0 * k, Palette.TIDE_INFECT_CRACK, 3.0)
		"home":
			# The beam lands on HOME: a hot flash, a ring and spokes.
			ci.draw_rect(Rect2(Vector2.ZERO, layer_size), Color(RED, lk.home_flash_alpha * (1.0 - k)))
			ci.draw_circle(p, 22.0 + 30.0 * k, Color(RED, 0.5 * (1.0 - k)))
			ci.draw_arc(p, 26.0 + 46.0 * k, 0.0, TAU, 36, Color(INK, 1.0 - k), 4.0)
			for s in lk.burst_spokes:
				var d := Vector2.from_angle(TAU * float(s) / float(lk.burst_spokes))
				ci.draw_line(p + d * (26.0 + 8.0 * k), p + d * (34.0 + 40.0 * k), Color(RED, 1.0 - 0.5 * k), 3.0)
			xmark(ci, p, 12.0, RED, 4.0)
		"bloom":
			# The infection takes the Site: a dark bloom swells over the district and cracks.
			var r := lerpf(6.0, lk.bloom_r, 1.0 - pow(1.0 - k, 2.0))
			ci.draw_circle(p, r, Color(Palette.TIDE_INFECT_FILL, 0.8))
			ci.draw_arc(p, r, 0.0, TAU, 32, Palette.TIDE_INFECT_EDGE, 2.5)
			ci.draw_arc(p, r * 0.6, 0.0, TAU, 28, Color(Palette.TIDE_INFECT_EDGE, 0.7), 1.5)
			crack(ci, p, 12.0 + 6.0 * k, Palette.TIDE_INFECT_CRACK, 2.5)


## `pts` as a closed outline.
static func closed(pts: PackedVector2Array) -> PackedVector2Array:
	var out := pts.duplicate()
	if not out.is_empty():
		out.append(out[0])
	return out


## An INFECTED card in flight at `pos`, `s` times its size.
static func flight_card(ci: CanvasItem, pos: Vector2, s: float) -> void:
	var lk := look()
	var r := Rect2(pos - Vector2(lk.flight_w, lk.flight_h) * 0.5 * s, Vector2(lk.flight_w, lk.flight_h) * s)
	ci.draw_rect(r.grow(3.0), Color(RED, 0.35))
	ci.draw_rect(r, WOUND_FILL)
	ci.draw_rect(r, RED, false, 2.0)
	crack(ci, r.get_center(), 6.0 * s, RED, 2.0)


## The ghost of a picked response on the map. `head` is the response's head; `p` / `q` are the Site points it names (the first and the second
## where it has two), `hp` HOME's point, `hunter_pts` the first point of each HUNTER lane. Absent points are Vector2.INF.
static func preview_ghost(ci: CanvasItem, head: String, type: String, sent_type: String, p: Vector2, q: Vector2, hp: Vector2, hunter_pts: PackedVector2Array) -> void:
	var lk := look()
	var ghost_col := Color(GOLD, lk.ghost_alpha)
	match head:
		"DEPLOY":
			if p.x != INF:
				sentry(ci, p + Vector2(0.0, -24.0), type, "GUARD", lk.sentry_scale)
				ci.draw_arc(p, 20.0, 0.0, TAU, 20, ghost_col, 2.0)
		"REDEPLOY":
			if p.x != INF and q.x != INF:
				ci.draw_line(p + Vector2(0.0, -24.0), q + Vector2(0.0, -24.0), ghost_col, 3.0)
				sentry(ci, q + Vector2(0.0, -24.0), sent_type, "SHIFT", lk.sentry_scale)
				ci.draw_arc(q, 20.0, 0.0, TAU, 20, ghost_col, 2.0)
		"SACRIFICE":
			if p.x != INF:
				ci.draw_circle(p, lk.front_r, Palette.TIDE_TAKEN_FILL)
				ci.draw_arc(p, 20.0, 0.0, TAU, 20, COBALT_HOT, 3.0)
			if hp.x != INF:
				ci.draw_arc(hp + Vector2(0.0, 6.0), 30.0, PI, TAU, 20, COBALT_HOT, 3.0)
		"JAM", "JAM_B":
			for hpt in hunter_pts:
				ci.draw_line(hpt + Vector2(-12, -12), hpt + Vector2(12, 12), RED, 4.0)


# ================================================================================================ the screen (TideRaidScreen)
## The raid panel's frame.
static func style_panel(c: Control) -> void:
	c.add_theme_stylebox_override("panel", UiTheme.box(PANEL_BG, EDGE, 2, 10, 8))


## The HUD strip's frame.
static func style_hud(c: Control) -> void:
	c.add_theme_stylebox_override("panel", UiTheme.box(PANEL_BG, EDGE, 1, 8, 4))


## The hand's frame.
static func style_hand(c: Control) -> void:
	c.add_theme_stylebox_override("panel", UiTheme.box(PANEL_BG, EDGE, 1, 8, 6))


## A banner / warning chip's frame: the raised panel color with an `edge` outline.
static func style_chip(c: Control, edge: Color, margin_h: float = 8.0, margin_v: float = 4.0) -> void:
	c.add_theme_stylebox_override("panel", UiTheme.box(Palette.TIDE_PANEL_HI, edge, 2, margin_h, margin_v))


## A legend row's frame: lit (gold outline) while pinned, clear otherwise.
static func style_legend_row(c: Control, pinned: bool) -> void:
	c.add_theme_stylebox_override("panel", UiTheme.box(Palette.TIDE_PANEL_HI if pinned else Palette.CLEAR, GOLD if pinned else Palette.CLEAR, 1, 3, 1))


## A label's font, size and color.
static func style_label(l: Label, px: int, col: Color) -> void:
	l.add_theme_font_size_override("font_size", px)
	l.add_theme_color_override("font_color", col)
	l.add_theme_font_override("font", Palette.mono())


## A button's four boxes, font and colors; `accent` is its outline.
static func style_button(b: Button, accent: Color) -> void:
	b.add_theme_font_size_override("font_size", TXT)
	b.add_theme_font_override("font", Palette.mono())
	b.add_theme_stylebox_override("normal", UiTheme.box(Palette.TIDE_BUTTON, accent, 2, 10, 6))
	b.add_theme_stylebox_override("hover", UiTheme.box(Palette.TIDE_BUTTON_HOT, accent.lightened(0.3), 2, 10, 6))
	b.add_theme_stylebox_override("pressed", UiTheme.box(accent.darkened(0.4), accent, 2, 10, 6))
	b.add_theme_stylebox_override("disabled", UiTheme.box(Palette.TIDE_BUTTON_OFF, Palette.TIDE_EDGE_OFF, 1, 10, 6))
	b.add_theme_color_override("font_color", INK)
	b.add_theme_color_override("font_disabled_color", OFF)


## A response row's boxes: the picked row (`sel`) lifts, `edge` is its outline.
static func style_row(b: Button, sel: bool, edge: Color) -> void:
	b.add_theme_stylebox_override("normal", UiTheme.box(Palette.TIDE_PANEL_HI if sel else Palette.TIDE_ROW, edge, 2, 6, 3))
	b.add_theme_stylebox_override("hover", UiTheme.box(Palette.TIDE_ROW_HOT, edge.lightened(0.3), 2, 6, 3))
	b.add_theme_stylebox_override("pressed", UiTheme.box(Palette.TIDE_ROW_PRESSED, GOLD, 2, 6, 3))


## A small button's font size (the response variants).
static func style_button_small(b: Button) -> void:
	b.add_theme_font_size_override("font_size", SMALL)


## The tint of a card that does nothing where it stands.
static func useless_tint() -> Color:
	return RED.lightened(0.55)


## The gold outline of the selected card, drawn over `cv` (never a tint: the type glyph keeps its color).
static func select_frame(cv: CanvasItem, size: Vector2) -> void:
	var w := look().select_edge_w
	cv.draw_rect(Rect2(Vector2.ZERO, size), Palette.TIDE_GOLD, false, w)
	cv.draw_rect(Rect2(Vector2.ONE * w, size - Vector2.ONE * w * 2.0), Color(Palette.TIDE_GOLD, 0.45), false, 1.0)


## The deck strip: its frame, the DECK word and one cell per card (`cards` = the card arrays [id, type, verb]; `cell_pos` their top-left points).
static func deck_strip(cv: CanvasItem, size: Vector2, cards: Array, cell_pos: PackedVector2Array, cell: Vector2) -> void:
	cv.draw_rect(Rect2(Vector2.ZERO, size), PANEL_BG)
	cv.draw_rect(Rect2(Vector2.ZERO, size), EDGE, false, 1.0)
	cv.draw_string(ThemeDB.fallback_font, Vector2(6, 16), "DECK", HORIZONTAL_ALIGNMENT_LEFT, -1, SMALL, DIM)
	for i in cards.size():
		var c: Array = cards[i]
		var p := cell_pos[i]
		var r := Rect2(p, cell)
		if String(c[2]) == "WOUND":
			cv.draw_rect(r, WOUND_FILL)
			crack(cv, p + Vector2(5.5, 6.5), 5.0, RED, 1.2)
		elif String(c[2]) == "DOSE":
			cv.draw_rect(r, PANEL)
			cv.draw_rect(r, ACID, false, 1.0)
		else:
			cv.draw_rect(r, type_color(String(c[1])).darkened(0.5))
			cv.draw_rect(r, type_color(String(c[1])), false, 1.0)


## A full-rect wash of `col` over `host` (a Control that fills the screen). Returns it. The CITY LOST overlay is its first user; the art pass may
## add a wash to any beat. Child order is draw order.
static func wash(host: Control, col: Color) -> ColorRect:
	var w := ColorRect.new()
	w.color = col
	w.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	w.mouse_filter = Control.MOUSE_FILTER_IGNORE
	host.add_child(w)
	return w


## The CITY LOST wash color.
static func lost_wash_color() -> Color:
	var lk := look()
	return Color(Palette.TIDE_RED.darkened(lk.lost_wash_darken), lk.lost_wash_alpha)


## The HQ step's DECAY warning panel: a chip with a red outline.
static func decay_warning_panel() -> PanelContainer:
	var chip := PanelContainer.new()
	chip.name = "DecayWarning"
	style_chip(chip, RED)
	return chip


## The color of a DECAY line's count: red for cards added, the HOLDS color for cards cured, dim for none.
static func decay_count_color(n: int) -> Color:
	return RED if n > 0 else (TIER_COLOR["HOLDS"] if n < 0 else DIM)


## The hound glyph centred in a small control (the HUNTER legend row).
static func hunter_glyph(c: Control) -> void:
	hound(c, c.size * 0.5)


## A small right arrow in a control (the guard line).
static func arrow_glyph(c: Control, col: Color) -> void:
	arrow(c, 1.0, 8.0, col)


## The deck-pip icon of a WOUND (a cracked card) or a card of `word`'s type, centred at `c` with radius scale `r`.
static func deck_pip(ci: CanvasItem, c: Vector2, r: float, word: String) -> void:
	var rr := Rect2(c - Vector2(r, r) * 0.7, Vector2(r, r) * 1.4)
	if word == "WOUND":
		ci.draw_rect(rr, WOUND_FILL)
		crack(ci, c, r * 0.6, RED, 1.5)
	else:
		ci.draw_rect(rr, type_color(word).darkened(0.45))
		ci.draw_rect(rr, type_color(word), false, 1.0)


# ================================================================================================ the odds bar (TideOddsBar)
## The odds bar's segments `segs` (one per tier of `odds` [{tier, n}]); `lit` is the tier the pointer is on ("" = none).
static func odds_bar(ci: CanvasItem, odds: Array, segs: Array[Rect2], lit: String) -> void:
	var f := ThemeDB.fallback_font
	var gmin := look().odds_glyph_min_w
	for i in segs.size():
		var t := String(odds[i]["tier"])
		var r := segs[i].grow_individual(-1.0, 0.0, -1.0, 0.0)
		var col := tier_color(t)
		if t == "BREACHED" or t == TIER_CITY_LOST:
			ci.draw_rect(r, BLACK)
			ci.draw_rect(r, RED, false, 2.0)
		else:
			ci.draw_rect(r, Color(col, 0.55 if lit == "" or lit == t else 0.25))
			ci.draw_rect(r, col, false, 2.0 if lit == t else 1.0)
		var x := r.position.x + 3.0
		if r.size.x >= gmin + 14.0:
			tier(ci, Vector2(x + 8.0, r.get_center().y), t, minf(8.0, r.size.y * 0.4), col)
			x += 19.0
		if r.size.x >= 14.0:
			ci.draw_string(f, Vector2(x, r.get_center().y + 5.0), "%d" % int(odds[i]["n"]), HORIZONTAL_ALIGNMENT_LEFT, r.end.x - x, COUNT_PX, INK)
