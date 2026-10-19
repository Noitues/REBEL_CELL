class_name RouteOverlay
extends RefCounted
## The route stickers' drawing kit (ART_BIBLE v2 4.6 "hybrid D"): the node sticker (a vinyl die-cut in its kind's colour,
## one outline ring carrying the state: lime walked, orange selectable, white not yet, dim grey cut off), the state ring, the
## node-type shape badge, the TARGET loop and the operative token. NA-26 retired the 2D route page that mounted it as a
## CityMapOverlay (the run's route is the street view now, `StreetRouteView`); what stays is the static drawing the HQ run's
## compound (`HqRunView`) and the route key (`RouteLegend`) share. The three motion ids below stay declared for
## `ui_motion.tres` and the motion lab (their route page is gone; a motion-pass item).

const STATE_WALKED := "walked"
const STATE_NEXT := "next"
const STATE_LATER := "later"
const STATE_CUT := "cut"
## Each state's second cue besides its colour (§5.1 never colour alone; the greyscale audit):
## walked a double ring, selectable a thick solid ring with the glow and its number, not yet a
## dashed ring, cut off a dotted ring struck through.
const RING_STYLES := {STATE_WALKED: "double", STATE_NEXT: "solid", STATE_LATER: "dashed", STATE_CUT: "dotted_struck"}
## Dashes round a dashed ring, dots round a dotted one.
const RING_DASHES := 12
const RING_DOTS := 16
## A sticker's outer reach, ring included, at text scale 1.0 (screen px); the TARGET's.
## B3 (review D14: node stickers at least 44 px at 1080p): the die-cut is about 34 px at 720p.
const STICKER_RADIUS := 22.0
const STICKER_RADIUS_BIG := 26.0
## The state ring's width, the ink keyline's extra width, the die-cut border's width and
## the gap the ring keeps off the die-cut (screen px).
const RING_WIDTH := 3.2
const KEYLINE_EXTRA := 3.0
const DIE_CUT_WIDTH := 2.4
const RING_GAP := 2.0
## A selectable node's soft glow: width (screen px) and alpha.
const NEXT_GLOW_WIDTH := 9.0
const NEXT_GLOW_ALPHA := 0.28
## M14 asset parity: the node stickers and the operative token are round 37's own drawings
## (`tools/art_pipeline/parity/export_route_stickers.py`, manifest in ROUTE_ART_DIR); the
## concept kind each route kind shows.
const ROUTE_ART_DIR := "res://assets/netrun/route/"
const STICKER_ART := {CityMapOverlay.KIND_FIGHT: "router", CityMapOverlay.KIND_ELITE: "elite", CityMapOverlay.KIND_EVENT: "terminal", CityMapOverlay.KIND_SHOP: "shop", CityMapOverlay.KIND_RACK: "rack"}
## A cut-off sticker's alpha (its art is the concept's grey `past` sticker).
const CUT_ALPHA := 0.75
## The choice number's chip: side and lettering (screen px at text scale 1.0).
const NUMBER_SIDE := 15.0
const NUMBER_FONT := 13
## The operative pin over "you are here": its side (share of the sticker radius), tilt (rad)
## and offset (shares of the radius, right and up).
const PIN_SHARE := 1.05
const PIN_TILT := -0.3
const PIN_OFFSET := Vector2(0.75, -1.45)
## The TARGET circle: its radius (share of the sticker's) and squash (B1b, D3: one hand loop
## with its 20 degree tail in the kit's wax, PencilShapes.hand_circle), and the word's
## lettering (screen px at text scale 1.0) and offset (shares of the circle's radius).
const TARGET_SHARE := 1.75
const TARGET_SQUASH := 0.86
const TARGET_FONT := 20
const ROUTE_TARGET_WORD_AT := Vector2(0.7, -0.95)
const TARGET_WORD_TILT := -0.12
## Cable paths (screen px): widths of the walked line, the live dash and the later dash.
const CABLE_WALKED := 3.6
const CABLE_LIVE := 3.0
const CABLE_LATER := 1.6
## The walked line's glow (width share, alpha).
const CABLE_GLOW_SHARE := 3.0
const CABLE_GLOW_ALPHA := 0.18
## The later and cut dashes' alpha.
const LATER_ALPHA := 0.7
const CUT_EDGE_ALPHA := 0.5
## B3 (designer Q4, round 44 `route_page_hover_all.png`): every run link the route does not
## use, while the legend strip is hovered: a white hairline (width share of CABLE_LATER) at
## this alpha.
const LINK_HINT_SHARE := 0.6
const LINK_HINT_ALPHA := 0.25
## Hover reveal (D13): radius round the pointer (screen px), and the motion that fades a
## hidden node in.
const REVEAL_RADIUS := 40.0
const REVEAL_MOTION := &"route_node_reveal"
## Calm Heat: the ring's gap off the sticker and width (screen px), the lights' radius (screen
## px), the orbit motion (one turn per its duration).
const HEAT_RING_GAP := 5.0
const HEAT_RING_WIDTH := 1.6
const HEAT_LIGHT := 3.4
const HEAT_LIGHT_GLOW := 2.4
const HEAT_ORBIT_MOTION := &"route_heat_orbit"
## F14: the ring that marks every node of the kind the key's hovered row names: its gap off
## the sticker and width (screen px).
const KIND_RING_GAP := 10.0
const KIND_RING_WIDTH := 3.2
## Searchlights: their motion (one sweep per duration; amplitude = the sweep's half angle in
## degrees), the cone's half width (rad), reach (share of the map's diagonal), alpha, and the
## two lights' phase offset (share of a period) and base angles (rad from straight down).
const SEARCHLIGHT_MOTION := &"route_searchlight"
const SEARCH_HALF_WIDTH := 0.11
const SEARCH_REACH := 1.1
const SEARCH_ALPHA := 0.07
const SEARCH_PHASE := 0.37
const SEARCH_BASES: Array[float] = [0.35, -0.45]
const SEARCH_ORIGINS: Array[float] = [0.18, 0.82]


## Draws a route node sticker of `kind` at `p` (outer reach `r`, ring included) in state
## `state` (STATE_*) on `ci`: soft glow when selectable, ink keyline, the state ring, the
## white die-cut, the kind's colour and its symbol. `k` = local px per screen px. Shared with
## the legend strip so the key shows what the map draws.
static func draw_sticker(ci: CanvasItem, kind: String, p: Vector2, r: float, state: String, k: float, alpha: float = 1.0) -> void:
	var ring_col := RouteInk.ring_of(state)
	var ring_r := r - RING_WIDTH * 0.5 * k
	var disc_r := r - (RING_WIDTH + RING_GAP + DIE_CUT_WIDTH) * k
	var a := alpha
	if state == STATE_CUT:
		a *= CUT_ALPHA
	if state == STATE_NEXT:
		ci.draw_arc(p, ring_r, 0, TAU, 40, Color(ring_col, NEXT_GLOW_ALPHA * a), NEXT_GLOW_WIDTH * k)
	# M14 asset parity: the concept's own node sticker (round 37 r32ui.node_sd: the round 31
	# icon on a die-cut vinyl sticker; its grey `past` look when cut off), sized to the die-cut.
	var t := sticker_art(kind, state == STATE_CUT)
	var cut := disc_r + DIE_CUT_WIDTH * k
	var sz := Vector2(t.get_width(), t.get_height()) * (cut * 2.0 / maxf(1.0, t.get_width()))
	ci.draw_texture_rect(t, Rect2(p - sz * 0.5, sz), false, Color(Palette.NO_TINT, a))
	if CityMapOverlay.KIND_SHAPES.has(kind):
		ci.set_meta(&"icon_id", CityMapOverlay.icon_id(kind))
	draw_state_ring(ci, p, ring_r, state, k, a)
	draw_shape_badge(ci, kind, p, r, k, a)


## W3-ROUTE (C7): the badge's centre (share of the sticker's reach, right and down), its reach
## (share of the sticker's reach) and the share of it the kind's colour fills.
const BADGE_AT := Vector2(0.72, 0.72)
const BADGE_SHARE := 0.4
const BADGE_FILL := 0.62
## The star badge's points and its inner radius share.
const BADGE_STAR_POINTS := 8
const BADGE_STAR_INNER := 0.62
const BADGE_ROUND_SEGMENTS := 16


## W3-ROUTE (C7): the outline of kind `kind`'s shape badge centred at `c`, reach `rr`
## (CityMapOverlay.KIND_SHAPES: fight circle, elite star, shop tag, event square, rack tower).
## Every kind has its own silhouette, so node types differ by shape and not by colour only.
static func shape_polygon(kind: String, c: Vector2, rr: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	match String(CityMapOverlay.KIND_SHAPES.get(kind, "circle")):
		"star8":
			for i in BADGE_STAR_POINTS * 2:
				var ang := TAU * i / (BADGE_STAR_POINTS * 2) - PI * 0.5
				pts.append(c + Vector2.from_angle(ang) * rr * (1.0 if i % 2 == 0 else BADGE_STAR_INNER))
		"tag":
			var h := rr * 0.8
			pts = PackedVector2Array([c + Vector2(-rr, -h), c + Vector2(rr * 0.35, -h), c + Vector2(rr, 0.0),
				c + Vector2(rr * 0.35, h), c + Vector2(-rr, h)])
		"square":
			var q := rr * 0.85
			pts = PackedVector2Array([c + Vector2(-q, -q), c + Vector2(q, -q), c + Vector2(q, q), c + Vector2(-q, q)])
		"tower":
			var w := rr * 0.6
			pts = PackedVector2Array([c + Vector2(-w, rr), c + Vector2(-w, -rr * 0.35), c + Vector2(-w * 0.45, -rr * 0.35),
				c + Vector2(-w * 0.45, -rr), c + Vector2(w * 0.45, -rr), c + Vector2(w * 0.45, -rr * 0.35),
				c + Vector2(w, -rr * 0.35), c + Vector2(w, rr)])
		_:
			for i in BADGE_ROUND_SEGMENTS:
				pts.append(c + Vector2.from_angle(TAU * i / BADGE_ROUND_SEGMENTS) * rr)
	return pts


## W3-ROUTE (C7): the shape badge of `kind` at the sticker's lower right: ink keyline, paper
## rim, the kind's colour inside.
static func draw_shape_badge(ci: CanvasItem, kind: String, p: Vector2, r: float, k: float, a: float = 1.0) -> void:
	if not CityMapOverlay.KIND_SHAPES.has(kind):
		return
	var c := p + BADGE_AT * r
	var rr := r * BADGE_SHARE
	var outer := shape_polygon(kind, c, rr + k * 1.5)
	ci.draw_colored_polygon(outer, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * a))
	ci.draw_colored_polygon(shape_polygon(kind, c, rr), Color(RouteInk.DIE_CUT, a))
	ci.draw_colored_polygon(shape_polygon(kind, c, rr * BADGE_FILL), Color(RouteInk.sticker_of(kind), a))


## The state ring at radius `ring_r` round `p` in state `state`'s colour AND style
## (RING_STYLES), over an ink keyline. Shared with the legend strip's swatches.
static func draw_state_ring(ci: CanvasItem, p: Vector2, ring_r: float, state: String, k: float, a: float = 1.0) -> void:
	var col := Color(RouteInk.ring_of(state), a)
	var ink := Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * a)
	var w := RING_WIDTH * k
	match String(RING_STYLES.get(state, "solid")):
		"double":
			for rr in [ring_r - w * 0.55, ring_r + w * 0.55]:
				ci.draw_arc(p, rr, 0, TAU, 40, ink, w * 0.6 + KEYLINE_EXTRA * k * 0.6)
			for rr in [ring_r - w * 0.55, ring_r + w * 0.55]:
				ci.draw_arc(p, rr, 0, TAU, 40, col, w * 0.55)
		"dashed":
			for q in RING_DASHES:
				var a0 := TAU * q / RING_DASHES
				var a1 := a0 + TAU / RING_DASHES * 0.55
				ci.draw_arc(p, ring_r, a0, a1, 6, ink, w + KEYLINE_EXTRA * k)
				ci.draw_arc(p, ring_r, a0, a1, 6, col, w)
		"dotted_struck":
			for q in RING_DOTS:
				var d := p + Vector2.from_angle(TAU * q / RING_DOTS) * ring_r
				ci.draw_circle(d, w * 0.75 + k, ink)
				ci.draw_circle(d, w * 0.6, col)
			var s := Vector2(ring_r, -ring_r) * 0.72
			ci.draw_line(p - s, p + s, ink, w + KEYLINE_EXTRA * k)
			ci.draw_line(p - s, p + s, col, w)
		_:
			ci.draw_arc(p, ring_r, 0, TAU, 40, ink, w * 1.4 + KEYLINE_EXTRA * k)
			ci.draw_arc(p, ring_r, 0, TAU, 40, col, w * 1.4)


## The concept sticker a route kind shows (STICKER_ART names, round 37's kinds; `past` = the
## grey cut-off look), loaded once.
static func sticker_art(kind: String, past: bool = false) -> Texture2D:
	var name := "node_%s%s" % [STICKER_ART.get(kind, "router"), "_past" if past else ""]
	if not _art_cache.has(name):
		_art_cache[name] = load(ROUTE_ART_DIR + name + ".png") as Texture2D
	return _art_cache[name]


## The operative token (round 37 r32ui.token_sd), loaded once.
static func token_art() -> Texture2D:
	if not _art_cache.has("token"):
		_art_cache["token"] = load(ROUTE_ART_DIR + "token_operative.png") as Texture2D
	return _art_cache["token"]


static var _art_cache: Dictionary = {}


## The TARGET's red grease-pencil loop round `at` (radius `rr`): one hand ellipse with its 20
## degree tail (B1b, D3), its wobble from `seed`.
static func target_loop(at: Vector2, rr: float, seed: int) -> Array[PackedVector2Array]:
	return [PencilShapes.hand_circle(at, Vector2(rr, rr * TARGET_SQUASH), seed)] as Array[PackedVector2Array]


## The TARGET's word.
const TARGET_WORD := "TARGET" # TR
