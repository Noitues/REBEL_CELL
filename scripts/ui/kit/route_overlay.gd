class_name RouteOverlay
extends CityMapOverlay
## ART-7 3B: the netrun route drawn in ART_BIBLE v2 §4.6 "hybrid D" on the current route view
## (wave 2 moves it onto the unified city). Pure view over CityMapOverlay's layout, labels,
## moves and hover (the route sweeps keep their rules):
## - **Node states, option A:** every node is a vinyl sticker in its kind's full colour (white
##   die-cut, ink keyline); one outline ring carries the state: lime walked, orange
##   selectable (numbered, with a soft glow), white not yet, dim grey cut off (the run never
##   goes back).
## - **Hidden nodes (D13):** only the walked nodes, the choices and the TARGET are drawn; the
##   rest show when `show_all` is on (the legend strip's hover, Options "Always show all
##   nodes") or one at a time under the pointer (~REVEAL_RADIUS px, `route_node_reveal`).
## - **TARGET:** the final Rack carries the red grease-pencil circle and the word.
## - **Transit v3 paths (ART-7 7w):** every link is a cable routed on the real city's streets
##   and blocks by RouteCableRouter (45° / 90° turns only, streets crossed rather than ridden,
##   crossings avoided, the rest bridged with a hop), from a sticker down to its lot, along
##   the run and up to the next sticker; the walked path is a solid lime line, the live
##   choices a crawling orange dash, the rest a white dash, cut-off links dim grey. Before
##   the lots are known a link falls back to `cable()` (one turn along the two axes). On the
##   3D city the links are these cables, not the Grid's network decal.
## - **Calm Heat (Heat B):** a choice Heat has made harder (`heat_chip`, from the rules) gets
##   a thin HEAT_B ring with a red and a blue light circling it and its effect as a label
##   line; with `heat_sweeps` two slow searchlights sweep the map.
## Node dictionaries read (besides CityMapOverlay's): target: bool (the final node),
## number: int (1-based choice number, 0 = none), heat_chip: String (translated, "" = none).
## Edge dictionaries read: state: "walked" | "live" | "later".

## The four states a ring can show.
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
const STICKER_RADIUS := 19.0
const STICKER_RADIUS_BIG := 23.0
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
const STICKER_ART := {KIND_FIGHT: "router", KIND_ELITE: "elite", KIND_EVENT: "terminal", KIND_SHOP: "shop", KIND_RACK: "rack"}
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
## The TARGET circle: its radius (share of the sticker's), squash, wobble (screen px), the
## pencil's stroke width (screen px), the second pass's turn offset (rad), and the word's
## lettering (screen px at text scale 1.0) and offset (shares of the circle's radius).
const TARGET_SHARE := 1.75
const TARGET_SQUASH := 0.86
const TARGET_WOBBLE := 2.6
const TARGET_STROKE := 3.6
const TARGET_SEGMENTS := 40
const TARGET_OVERRUN := 0.18
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

## D13: every node shown (the legend strip's hover or the Options setting): `show_all` is
## CityMapOverlay's (ART-5 5d); the route animates the reveal through its hook.
func _on_show_all_changed(v: bool) -> void:
	all_t = 0.0 if v else 1.0
	if v:
		if is_inside_tree():
			Motion.run(REVEAL_MOTION, self, ^"all_t", 1.0)
		else:
			all_t = 1.0
		queue_redraw()
## The show-all fade (0..1).
var all_t: float = 1.0:
	set(v):
		all_t = v
		_queue_top()
		queue_redraw()
## The node shown under the pointer (D13 hover reveal; &"" = none) and its fade (0..1).
var reveal_id: StringName = &""
var reveal_t: float = 1.0:
	set(v):
		reveal_t = v
		_queue_top()
		queue_redraw()
## Calm Heat: the two searchlights sweep (the scene sets it from the Heat band).
var heat_sweeps: bool = false:
	set(v):
		heat_sweeps = v
		if _anim != null:
			_anim.queue_redraw()


func _init(p_city: NeonCity = null) -> void:
	super(p_city)
	name = "RouteOverlay"


# --- State ------------------------------------------------------------------------------------

## The state ring node `n` shows (STATE_*).
func state_of(n: Dictionary) -> String:
	if n.get("here", false) or n.get("visited", false):
		return STATE_WALKED
	if n.get("next", false):
		return STATE_NEXT
	if is_dimmed(n["id"]):
		return STATE_CUT
	return STATE_LATER


## True when node `n` is always drawn (D13): walked, a choice or the TARGET.
static func pinned(n: Dictionary) -> bool:
	return bool(n.get("here", false)) or bool(n.get("visited", false)) or bool(n.get("next", false)) or bool(n.get("target", false))


## How much of node `n` shows (0 hidden .. 1 drawn).
func shown(n: Dictionary) -> float:
	if pinned(n):
		return 1.0
	var a := 0.0
	if show_all:
		a = all_t
	if n["id"] == reveal_id:
		a = maxf(a, reveal_t)
	return a


## The ids drawn now (shown at all), in graph order (tests and captures).
func drawn_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for n in nodes:
		if shown(n) > 0.0:
			out.append(n["id"])
	return out


func icon_radius(n: Dictionary) -> float:
	return (STICKER_RADIUS_BIG if n.get("big", false) else STICKER_RADIUS) * _k()


## Labels: a hidden node has none; a choice Heat has made harder carries its effect as a
## second line (placed with the label, so it never covers another).
func label_lines(id: StringName) -> PackedStringArray:
	var n := _node_dict(id)
	if n.is_empty() or shown(n) <= 0.0:
		return PackedStringArray()
	var lines := super(id)
	var chip := String(n.get("heat_chip", ""))
	if chip != "" and not lines.is_empty():
		lines.append(chip)
	return lines


# --- Hover reveal (D13) ----------------------------------------------------------------------

func _gui_input(event: InputEvent) -> void:
	super(event)
	if event is InputEventMouseMotion:
		_reveal_near(event.position)


func _notification(what: int) -> void:
	super(what)
	if what == NOTIFICATION_MOUSE_EXIT:
		_reveal(&"")


## The hidden node within REVEAL_RADIUS of local point `p` (nearest; ties by id), or &"".
func hidden_near(p: Vector2) -> StringName:
	var best: StringName = &""
	var best_d := REVEAL_RADIUS * _k()
	for n in nodes:
		if pinned(n):
			continue
		var at := icon_pos(n)
		if at.x == INF:
			continue
		var d := p.distance_to(at)
		if d < best_d or (is_equal_approx(d, best_d) and best != &"" and String(n["id"]) < String(best)):
			best_d = d
			best = n["id"]
	return best


func _reveal_near(p: Vector2) -> void:
	_reveal(hidden_near(p))


func _reveal(id: StringName) -> void:
	if id == reveal_id:
		return
	reveal_id = id
	if id == &"":
		_queue_top()
		queue_redraw()
		return
	reveal_t = 0.0
	if is_inside_tree():
		Motion.run(REVEAL_MOTION, self, ^"reveal_t", 1.0)
	else:
		reveal_t = 1.0


# --- Paths ------------------------------------------------------------------------------------

## ART-7 7w: a cable's bridge over another (screen px radius) and its arc's segments.
const HOP_RADIUS := 5.0
const HOP_SEGMENTS := 8
## Routed cable sets kept per process (a route's cables never change while its lots stand).
const CABLE_MEMO_MAX := 64
static var _cable_memo: Dictionary = {}
## ART-7 7w: the transit v3 cables on the real city (RouteCableRouter, lot points): one per
## edge in graph order, then one per entry run (the street to each first choice); and what
## they were routed for (the map's layout signature and the street marker's spot).
var _cables: Array[Dictionary] = []
var _entry_cables: Dictionary = {}
var _cables_sig: Array = []
var _cables_here: Vector2 = Vector2.INF


## ART-7 7w: on the 3D city the route's links are its own cables, not the Grid's network
## decal: the decal is cleared.
func _feed_decal() -> void:
	if city != null and city.view3d != null:
		city.view3d.set_network(null)


## ART-7 7w: the walked cables draw on the 3D city too (the Grid's decal path draws no
## static links).
func _draw() -> void:
	super()
	if on_ground_decal() and city != null and not nodes.is_empty():
		_c = self
		for k in edges.size():
			_edge_static(edges[k], _route_px(k))


## ART-7 7w: the ground point (lots) a node's cable starts from: its building lot's centre.
func cable_end(id: StringName) -> Vector2:
	if not _lots.has(id):
		return Vector2.INF
	return Vector2(_lots[id]) + Vector2(0.5, 0.5)


## ART-7 7w: the cables routed for the current layout (lot points), routing them when the
## graph, its lots or the street marker changed. Returns the edge cables in edge order.
func cables() -> Array[Dictionary]:
	if city == null:
		var none: Array[Dictionary] = []
		return none
	if _cables_sig == _layout_sig and _cables_here == here_at and _cables.size() == edges.size():
		return _cables
	_cables_sig = _layout_sig.duplicate()
	_cables_here = here_at
	var pairs: Array = []
	for e in edges:
		pairs.append({"a": cable_end(e["a"]), "b": cable_end(e["b"])})
	var entry_ids: Array[StringName] = []
	if here_at.x != INF and here_id() == &"":
		var from := Vector2(here_lot()) + Vector2(0.5, 0.5)
		for n in nodes:
			if bool(n.get("next", false)) and _lots.has(n["id"]):
				entry_ids.append(n["id"])
				pairs.append({"a": from, "b": cable_end(n["id"])})
	var routable: Array = []
	for p: Dictionary in pairs:
		if Vector2(p["a"]).x != INF and Vector2(p["b"]).x != INF:
			routable.append(p)
	var key := [city.city3d, city.city_seed, routable]
	var routed: Array = _cable_memo.get(key, [])
	if routed.is_empty() and not routable.is_empty():
		if _cable_memo.size() >= CABLE_MEMO_MAX:
			_cable_memo.clear()
		routed = RouteCableRouter.route_all(routable, func(i: int, j: int) -> bool: return city.is_street(i, j))
		_cable_memo[key] = routed
	_cables.clear()
	_entry_cables.clear()
	var r := 0
	for k in pairs.size():
		var c: Dictionary = {}
		if Vector2(pairs[k]["a"]).x != INF and Vector2(pairs[k]["b"]).x != INF and r < routed.size():
			c = routed[r]
			r += 1
		if k < edges.size():
			_cables.append(c)
		else:
			_entry_cables[entry_ids[k - edges.size()]] = c
	return _cables


## ART-7 7w: cable `c` on screen (local px): from `top_a` (a node's sticker, or the street
## marker) down to its ground point, along its run with a bridge at each hop, up to
## `top_b`. Every ground point goes through the city's own projection (`_to_local`: the 3D
## camera on the 3D city).
func cable_px(c: Dictionary, top_a: Vector2, top_b: Vector2) -> PackedVector2Array:
	var out := PackedVector2Array()
	var lots: PackedVector2Array = c.get("points", PackedVector2Array())
	if lots.size() < 2:
		return out
	if top_a.x != INF:
		out.append(top_a)
	var hops: Array = c.get("hops", [])
	var r := HOP_RADIUS * _k()
	for q in lots.size():
		var p := _to_local(lots[q])
		if q > 0:
			var p0 := _to_local(lots[q - 1])
			var seg := p - p0
			var length := seg.length()
			if length > 0.0:
				var dir := seg / length
				var up := Vector2(-dir.y, dir.x)
				if up.y > 0.0 or (is_zero_approx(up.y) and up.x < 0.0):
					up = -up
				for h: Dictionary in hops:
					if int(h["seg"]) != q - 1:
						continue
					var at := _to_local(h["at"])
					var t := (at - p0).dot(dir)
					if t - r <= 0.0 or t + r >= length:
						continue
					for s in HOP_SEGMENTS + 1:
						var u := -1.0 + 2.0 * s / HOP_SEGMENTS
						out.append(at + dir * (u * r) + up * (sqrt(maxf(0.0, 1.0 - u * u)) * r))
		out.append(p)
	if top_b.x != INF:
		out.append(top_b)
	return out


## The city's two ground axes on screen (local px per grid step).
func _axes() -> Array[Vector2]:
	var o := _to_local(Vector2.ZERO)
	return [_to_local(Vector2(1, 0)) - o, _to_local(Vector2(0, 1)) - o]


## Transit v3: a cable run from local point `a` to `b` along the city's two axes (a, corner,
## b): straight segments, one turn, along the blocks' edges like a cable run between them.
func cable(a: Vector2, b: Vector2) -> PackedVector2Array:
	var pts := PackedVector2Array([a])
	if a.x == INF or b.x == INF or city == null:
		return PackedVector2Array()
	var ax := _axes()
	var u := ax[0]
	var v := ax[1]
	var det := u.x * v.y - u.y * v.x
	var d := b - a
	if absf(det) < 0.0001:
		pts.append(b)
		return pts
	var s := (d.x * v.y - d.y * v.x) / det
	var t := (u.x * d.y - u.y * d.x) / det
	pts.append(a + u * s)
	pts.append(b)
	return pts


## Edge `k`'s cable on screen: its routed run (7w), else the one-turn run between its
## stickers (no lots yet).
func _route_px(k: int) -> PackedVector2Array:
	if k >= edges.size():
		return PackedVector2Array()
	var a := icon_at(edges[k]["a"])
	var b := icon_at(edges[k]["b"])
	var cs := cables()
	if k < cs.size() and not cs[k].is_empty():
		if a.x == INF or b.x == INF:
			return PackedVector2Array()
		return cable_px(cs[k], a, b)
	return cable(a, b)


## The move rides its link's own cable (either way round).
func _travel_route() -> PackedVector2Array:
	var from: StringName = _travel["from"]
	var to: StringName = _travel["to"]
	for k in edges.size():
		if edges[k]["a"] == from and edges[k]["b"] == to:
			return _route_px(k)
		if edges[k]["a"] == to and edges[k]["b"] == from:
			var back := _route_px(k)
			back.reverse()
			return back
	return cable(icon_at(from), icon_at(to))


## How much of edge `e` shows (its ends' share).
func edge_shown(e: Dictionary) -> float:
	return minf(shown(_node_dict(e["a"])), shown(_node_dict(e["b"])))


func _edge_state(e: Dictionary) -> String:
	var st := String(e.get("state", ""))
	if st != "":
		if st == STATE_LATER and (is_dimmed(e["a"]) or is_dimmed(e["b"])):
			return STATE_CUT
		return st
	return STATE_LATER


func _edge_static(e: Dictionary, pts: PackedVector2Array) -> void:
	if pts.size() < 2:
		return
	var a := edge_shown(e)
	if a <= 0.0 or _edge_state(e) != STATE_WALKED:
		return
	var k := _k()
	var w := CABLE_WALKED * k
	draw_polyline(pts, Color(RouteInk.RING_WALKED, CABLE_GLOW_ALPHA * a), w * CABLE_GLOW_SHARE, true)
	draw_polyline(pts, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * a), w + KEYLINE_EXTRA * k, true)
	draw_polyline(pts, Color(RouteInk.RING_WALKED, a), w, true)


func _edge_flow(e: Dictionary, pts: PackedVector2Array) -> void:
	if pts.size() < 2:
		return
	var a := edge_shown(e)
	if a <= 0.0:
		return
	var k := _k()
	match _edge_state(e):
		STATE_WALKED:
			return
		"live":
			_dashes(pts, RouteInk.RING_AVAILABLE, CABLE_LIVE * k, a, fmod(anim_t * crawl_speed(), DASH_PERIOD * k), true)
		STATE_CUT:
			_dashes(pts, RouteInk.RING_CUT, CABLE_LATER * k, a * CUT_EDGE_ALPHA, 0.0, false)
		_:
			_dashes(pts, RouteInk.RING_UNAVAILABLE, CABLE_LATER * k, a * LATER_ALPHA, 0.0, false)


## Dashes along `pts` (screen-sized), `phase` px in, with an ink keyline when `keyline`.
func _dashes(pts: PackedVector2Array, col: Color, width: float, alpha: float, phase: float, keyline: bool) -> void:
	var k := _k()
	var on := DASH_ON * k
	var period := DASH_PERIOD * k
	var carry := phase
	for q in pts.size() - 1:
		var p0 := pts[q]
		var p1 := pts[q + 1]
		var length := p0.distance_to(p1)
		if not is_finite(length) or length <= 0.0:
			continue
		var dir := (p1 - p0) / length
		var t := carry
		var n := 0
		while t < length and n < DASHES_MAX:
			var t1 := minf(t + on, length)
			if t1 > maxf(t, 0.0):
				var s0 := p0 + dir * maxf(t, 0.0)
				var s1 := p0 + dir * t1
				if keyline:
					_c.draw_line(s0, s1, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * alpha), width + KEYLINE_EXTRA * k)
				_c.draw_line(s0, s1, Color(col, alpha), width)
			t += period
			n += 1
		carry = t - length


func _entry_roads() -> void:
	var p := here_point()
	if p.x == INF:
		return
	var k := _k()
	cables()
	for n in nodes:
		if not bool(n.get("next", false)):
			continue
		var c: Dictionary = _entry_cables.get(n["id"], {})
		var pts := cable_px(c, p, icon_pos(n)) if not c.is_empty() else cable(p, icon_pos(n))
		_dashes(pts, RouteInk.RING_AVAILABLE, CABLE_LIVE * k, 1.0, 0.0, true)


# --- Nodes ------------------------------------------------------------------------------------

func _node(n: Dictionary) -> void:
	var a := shown(n)
	if a <= 0.0:
		return
	var at := icon_pos(n)
	if at.x == INF:
		return
	var k := _k()
	var r := icon_radius(n)
	var state := state_of(n)
	if not _travel.is_empty() and n["id"] == _travel["to"] and travel_t >= 1.0:
		# ANIM-5 (4.16): the new node pops up with the marker on it.
		r *= lerpf(Motion.amplitude(&"node_pop"), 1.0, arrive_t)
	draw_sticker(_c, String(n.get("kind", "")), at, r, state, k, a)
	if int(n.get("number", 0)) > 0:
		_number(at, r, int(n["number"]), a)
	var chip := String(n.get("heat_chip", ""))
	if chip != "":
		var hr := r + HEAT_RING_GAP * k
		_c.draw_arc(at, hr, 0, TAU, 40, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * a), (HEAT_RING_WIDTH + KEYLINE_EXTRA) * k)
		_c.draw_arc(at, hr, 0, TAU, 40, Color(RouteInk.heat_b(), a), HEAT_RING_WIDTH * k)
	if n.get("target", false):
		_target(n, at, r, a)
	if _travel.is_empty():
		if n.get("here", false):
			_here(at, r)
	elif n["id"] == _travel["to"] and travel_t >= 1.0:
		_here(at, r)


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
	if KIND_SHAPES.has(kind):
		ci.set_meta(&"icon_id", icon_id(kind))
	draw_state_ring(ci, p, ring_r, state, k, a)


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


## The choice number's orange chip at the sticker's upper left (§4.6: the next options are
## numbered).
func _number(at: Vector2, r: float, number: int, a: float) -> void:
	var k := _k()
	var side := NUMBER_SIDE * Settings.text_scale * k
	var c := at + Vector2(-r, -r) * 0.78
	var box := Rect2(c - Vector2(side, side) * 0.5, Vector2(side, side))
	_c.draw_rect(box.grow(k), Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * a))
	_c.draw_rect(box, Color(RouteInk.RING_AVAILABLE, a))
	var f := Palette.mono()
	var fs := maxi(1, roundi(NUMBER_FONT * Settings.text_scale * k))
	var text := str(number)
	var y := c.y + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	_c.draw_string(f, Vector2(box.position.x, y), text, HORIZONTAL_ALIGNMENT_CENTER, side, fs, Color(RouteInk.KEYLINE, a))


## The TARGET's red grease-pencil circle (two rough passes, a dark under-shadow, wax
## opacity) and the word beside it. The wobble comes from a hash of the node id.
func _target(n: Dictionary, at: Vector2, r: float, a: float) -> void:
	var k := _k()
	var seed_v := absi(hash(String(n["id"])))
	var rr := r * TARGET_SHARE
	for pass_i in 2:
		var ring := PackedVector2Array()
		var turn := TAU * (1.0 + TARGET_OVERRUN)
		var start := float(seed_v % 628) * 0.01 + pass_i * 0.9
		for q in TARGET_SEGMENTS + 1:
			var t := start + turn * q / TARGET_SEGMENTS
			var wob := (sin(t * 3.0 + float(seed_v % 31) + pass_i) + 0.5 * sin(t * 7.0 + pass_i * 2.0)) * TARGET_WOBBLE * k
			var grow := 1.0 + pass_i * 0.06
			ring.append(at + Vector2(cos(t), sin(t) * TARGET_SQUASH) * (rr * grow + wob))
		_c.draw_polyline(ring, Color(RouteInk.PENCIL_SHADOW, RouteInk.PENCIL_SHADOW_ALPHA * a), (TARGET_STROKE + KEYLINE_EXTRA) * k, true)
		_c.draw_polyline(ring, Color(RouteInk.PENCIL_THREAT, RouteInk.PENCIL_ALPHA * a), TARGET_STROKE * k * (1.0 - pass_i * 0.35), true)
	# The word: on its label's spot when the layout placed one (a label never covers another),
	# else beside the circle.
	if label_rects().has(String(n["id"])):
		return
	_pencil_word(at + Vector2(rr * ROUTE_TARGET_WORD_AT.x, rr * ROUTE_TARGET_WORD_AT.y), tr_word(TARGET_WORD), a)


## The TARGET's word in red grease pencil at `wp` (its baseline's start), tilted.
func _pencil_word(wp: Vector2, word: String, a: float, size_px: float = 0.0) -> void:
	var k := _k()
	var f := RouteInk.pencil_font()
	var fs := maxi(1, roundi(TARGET_FONT * Settings.text_scale * k))
	if size_px > 0.0:
		# Inside a placed label's box: the lettering that fills its height.
		fs = maxi(1, roundi(size_px / maxf(0.01, f.get_height(1))))
	_c.draw_set_transform(wp, TARGET_WORD_TILT)
	_c.draw_string_outline(f, Vector2.ZERO, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, roundi(KEYLINE_EXTRA * 2.0 * k), Color(RouteInk.PENCIL_SHADOW, RouteInk.PENCIL_SHADOW_ALPHA * a))
	_c.draw_string(f, Vector2.ZERO, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(RouteInk.PENCIL_THREAT, RouteInk.PENCIL_ALPHA * a))
	_c.draw_set_transform(Vector2.ZERO, 0.0)


## The TARGET's word (a key).
const TARGET_WORD := "TARGET" # TR


## "You are here": the operative's pink sticker pinned over the node (a tilted die-cut
## square with the operative glyph), the node's own ring already lime.
func _here(at: Vector2, r: float) -> void:
	var k := _k()
	var side := r * PIN_SHARE
	var c := at + Vector2(r * PIN_OFFSET.x, r * PIN_OFFSET.y)
	_c.draw_set_transform(c, PIN_TILT)
	# M14 asset parity: the concept's operative token (round 37 token_sd, the Breaker emblem in
	# Cell pink on a die-cut sticker), its die-cut as wide as the old pin's.
	var t := token_art()
	var w := side + (DIE_CUT_WIDTH * k + k) * 2.0
	var sz := Vector2(t.get_width(), t.get_height()) * (w / maxf(1.0, t.get_width()))
	_c.draw_texture_rect(t, Rect2(-sz * 0.5, sz), false)
	_c.draw_set_transform(Vector2.ZERO, 0.0)
	# The pin's point down onto the sticker.
	var tip := at + Vector2(r * 0.35, -r * 0.7)
	_c.draw_line(c + Vector2(-side * 0.2, side * 0.45), tip, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA), 2.0 * k)


# --- Labels -----------------------------------------------------------------------------------

## A map label as the Cell's terminal tag: navy glass, a hairline in the node's ring colour,
## the words in TEXT_HI; a Heat line in HEAT_B. The TARGET's word alone is pencil (no box).
func _tag_box(l: Dictionary) -> void:
	var rect: Rect2 = l["rect"]
	var n := _node_dict(l["id"])
	var lines: PackedStringArray = l["lines"]
	if not n.is_empty() and n.get("target", false) and lines.size() == 1 and lines[0] == tr_word(TARGET_WORD):
		# The TARGET's own word is pencil, not a terminal tag.
		var pf := RouteInk.pencil_font()
		var pfs := maxi(1, roundi(rect.size.y / maxf(0.01, pf.get_height(1))))
		var pw := pf.get_string_size(lines[0], HORIZONTAL_ALIGNMENT_LEFT, -1, pfs).x
		pfs = maxi(1, roundi(pfs * minf(1.0, rect.size.x / maxf(1.0, pw))))
		_pencil_word(Vector2(rect.position.x, rect.end.y - pf.get_descent(pfs)), lines[0], 1.0, pf.get_height(pfs))
		return
	var fs: int = l["fs"]
	var pad: float = l["pad"]
	var k := _k()
	var f := Palette.mono()
	var col := RouteInk.ring_of(state_of(n)) if not n.is_empty() else Palette.NET_CYAN
	if not n.is_empty() and n.get("here", false):
		col = Palette.CELL_PINK
	var near := Vector2(clampf(l["at"].x, rect.position.x, rect.end.x), clampf(l["at"].y, rect.position.y, rect.end.y))
	if near.distance_to(l["at"]) > float(l["r"]) + LABEL_GAP * k * 2.0:
		_c.draw_line(l["at"] + (near - l["at"]).normalized() * float(l["r"]), near, Color(col, 0.7), k)
	_c.draw_rect(rect, Palette.TERMINAL_BG)
	_c.draw_rect(rect, Color(col, 0.85), false, k)
	_c.draw_rect(Rect2(rect.position, Vector2(2.0 * k, rect.size.y)), col)
	var y := rect.position.y + pad + f.get_ascent(fs)
	var chip := String(n.get("heat_chip", "")) if not n.is_empty() else ""
	for line in lines:
		var lc := RouteInk.heat_b().lightened(0.25) if chip != "" and line == chip else Palette.TEXT_HI
		_c.draw_string(Palette.mono_for(line), Vector2(rect.position.x + pad, y), line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, lc)
		y += f.get_height(fs)


# --- Animated layer: calm Heat ---------------------------------------------------------------

func _draw_anim() -> void:
	super()
	if city == null or nodes.is_empty():
		return
	if heat_sweeps:
		_searchlights()
	var k := _k()
	var period := maxf(Motion.seconds(HEAT_ORBIT_MOTION), 0.001)
	var turn := anim_t * TAU / period if Motion.live(HEAT_ORBIT_MOTION) else 0.0
	for n in nodes:
		if String(n.get("heat_chip", "")) == "" or shown(n) <= 0.0:
			continue
		var at := icon_pos(n)
		if at.x == INF:
			continue
		var hr := icon_radius(n) + HEAT_RING_GAP * k
		for q in 2:
			var p := at + Vector2.from_angle(turn + PI * q) * hr
			var lc := RouteInk.HEAT_LIGHT_RED if q == 0 else RouteInk.HEAT_LIGHT_BLUE
			_anim.draw_circle(p, (HEAT_LIGHT + HEAT_LIGHT_GLOW) * k, Color(lc, 0.3))
			_anim.draw_circle(p, HEAT_LIGHT * k, lc)


## Two slow searchlight cones sweeping the visible map from its top edge.
func _searchlights() -> void:
	var area := label_area()
	if not area.has_area():
		return
	var e := Motion.entry(SEARCHLIGHT_MOTION)
	var period := maxf(Motion.seconds(SEARCHLIGHT_MOTION), 0.001)
	var swing := deg_to_rad(e.amplitude if e != null else 0.0)
	var live := Motion.live(SEARCHLIGHT_MOTION)
	var reach := area.size.length() * SEARCH_REACH
	for q in SEARCH_BASES.size():
		var phase := (anim_t / period + q * SEARCH_PHASE) * TAU if live else 0.0
		var ang := SEARCH_BASES[q] + sin(phase) * swing
		var o := Vector2(area.position.x + area.size.x * SEARCH_ORIGINS[q], area.position.y)
		var d0 := Vector2(0, 1).rotated(ang - SEARCH_HALF_WIDTH) * reach
		var d1 := Vector2(0, 1).rotated(ang + SEARCH_HALF_WIDTH) * reach
		var glow := Color(Palette.TEXT_HI, SEARCH_ALPHA)
		var clear := Color(Palette.TEXT_HI, 0.0)
		_anim.draw_polygon(PackedVector2Array([o, o + d0, o + d1]), PackedColorArray([glow, clear, clear]))
