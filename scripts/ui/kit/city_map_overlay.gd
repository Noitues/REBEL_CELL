class_name CityMapOverlay
extends Control
## Map overlays drawn ON the city (the Grid, raids, netrun routes): each node is a real
## building (highlighted by its roof outline: square, diamond, hexagon, octagon, the
## building's own cross-section) and each link follows the streets between them. The
## overlay is a child of the NeonCity so it pans and zooms with it, and it keeps the
## current (saturated) hues so it pops over a paler city. Pure view.
##
## Feed it a graph with `set_graph(nodes, edges)`:
##   nodes: [{id, at: Vector2 (grid target), color, label, glyph, big: bool,
##            mark: "spray" (claimed: a spray-paint ring) | "cross" (Seized) | ""}]
##   edges: [{a, b, color, width, dashed: bool, flow: bool}]
## and optional `markers` (node id -> Array[String]) for threats standing on nodes.
##
## Drawing is layered so only the moving parts redraw every frame (H20): this control
## draws the static under-layer (looks, route keylines), `_anim` the flowing dashes and
## packets, `_top` the nodes, badges, tags and markers (redrawn only when something
## changes), `_hi` the pulsing selection ring.

signal node_clicked(id: StringName)
## Threat markers moved (raid playout): the scene can follow them with the camera.
signal markers_changed

## TRACE: roof outlines and solid street paths. PILLARS: light pillars and floating
## badges, flowing dashed paths. ISOLATE: the rest of the city greyed out.
## XRAY / BLUEPRINT / SPOTLIGHT: netrun looks (see `set_look`).
enum Look { TRACE, PILLARS, ISOLATE, XRAY, BLUEPRINT, SPOTLIGHT }

## Non-colour Site marks (GDD 9.6: never colour alone): claimed Sites get a spray ring,
## Seized ones a cross.
const MARK_SPRAY := "spray"
const MARK_CROSS := "cross"
## Spray ring: radius around the roof (px), wobble, drips (count, length) and strokes.
const SPRAY_RADIUS := 26.0
const SPRAY_WOBBLE := 3.0
const SPRAY_SEGMENTS := 28
const SPRAY_DRIPS := 3
const SPRAY_DRIP_LEN := 9.0
const CROSS_SIZE := 13.0
## Dash pattern (px) and flow speeds (px per second).
const DASH_ON := 9.0
const DASH_PERIOD := 16.0
const DASH_SPEED := 30.0
const PACKET_SPEED := 90.0
## Selection ring pulse (radius px, amplitude px, speed rad/s).
const PULSE_RADIUS := 30.0
const PULSE_AMPLITUDE := 3.0
const PULSE_SPEED := 4.0

var city: NeonCity
var look: int = Look.TRACE
var nodes: Array[Dictionary] = []
var edges: Array[Dictionary] = []
var markers: Dictionary = {}
## Raid playout alias (RaidPlayoutPanel writes site id -> threat names here).
var threat_markers: Dictionary:
	get:
		return markers
	set(v):
		markers = v
		queue_redraw()
		markers_changed.emit()
var selected_id: StringName = &"":
	set(v):
		selected_id = v
		queue_redraw()
## Spotlight target (node id) for the SPOTLIGHT look.
var focus_id: StringName = &""
var anim_t: float = 0.0

var _lots: Dictionary = {}  # node id -> Vector2i
var _routes: Array[PackedVector2Array] = []  # grid points per edge
var _anim: Control
var _top: Control
var _hi: Control
## The canvas item the helpers draw on (self, _anim, _top or _hi).
var _c: CanvasItem


func _init(p_city: NeonCity = null) -> void:
	city = p_city
	_c = self
	mouse_filter = Control.MOUSE_FILTER_PASS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_anim = _layer("Flow", _draw_anim)
	_top = _layer("Nodes", _draw_top)
	_hi = _layer("Selection", _draw_hi)
	if city != null:
		city.rebuilt.connect(_relayout)


func _layer(layer_name: String, painter: Callable) -> Control:
	var c := Control.new()
	c.name = layer_name
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	c.draw.connect(painter)
	add_child(c)
	return c


func _process(delta: float) -> void:
	if not Fx.effects_enabled() or not is_visible_in_tree():
		return
	anim_t += delta
	_anim.queue_redraw()
	if selected_id != &"":
		_hi.queue_redraw()


func set_graph(p_nodes: Array[Dictionary], p_edges: Array[Dictionary]) -> void:
	nodes = p_nodes
	edges = p_edges
	_relayout()


func set_look(value: int) -> void:
	look = value
	queue_redraw()


## Grid centre of the graph (for framing the camera on it).
func centre() -> Vector2:
	var c := Vector2.ZERO
	for n in nodes:
		c += n["at"]
	return c / maxf(1.0, nodes.size())


func lot_of(id: StringName) -> Vector2i:
	return _lots.get(id, Vector2i.ZERO)


## The non-colour mark drawn on node `id` ("spray", "cross" or "").
func mark_of(id: StringName) -> String:
	for n in nodes:
		if n["id"] == id:
			return String(n.get("mark", ""))
	return ""


func _relayout() -> void:
	_lots.clear()
	_routes.clear()
	if city == null:
		return
	var taken := {}
	for n in nodes:
		var at: Vector2 = n["at"]
		var lot := city.nearest_building(at.x, at.y, 4, taken)
		_lots[n["id"]] = lot
		var rec := city.roof_of(lot.x, lot.y)
		if rec.has("cell"):
			var cell: Rect2i = rec["cell"]
			for i in range(cell.position.x, cell.end.x):
				for j in range(cell.position.y, cell.end.y):
					taken[Vector2i(i, j)] = true
	for e in edges:
		if _lots.has(e["a"]) and _lots.has(e["b"]):
			_routes.append(_route(_lots[e["a"]], _lots[e["b"]]))
		else:
			_routes.append(PackedVector2Array())
	queue_redraw()


## Nearest street lot to a building lot (its "front door").
func _door(lot: Vector2i) -> Vector2i:
	for r in range(1, 6):
		for di in range(-r, r + 1):
			for dj in range(-r, r + 1):
				if absi(di) != r and absi(dj) != r:
					continue
				var l := lot + Vector2i(di, dj)
				if city.is_street(l.x, l.y):
					return l
	return lot


## Street route between two buildings: door -> BFS over street lots -> door, as grid
## points (lot centres). Falls back to an L-shaped path if the search fails.
func _route(a: Vector2i, b: Vector2i) -> PackedVector2Array:
	var da := _door(a)
	var db := _door(b)
	var box := Rect2i(Vector2i(mini(da.x, db.x) - 8, mini(da.y, db.y) - 8), Vector2i(absi(da.x - db.x) + 17, absi(da.y - db.y) + 17))
	var prev := {da: da}
	var queue: Array[Vector2i] = [da]
	var head := 0
	while head < queue.size():
		var cur := queue[head]
		head += 1
		if cur == db:
			break
		for step in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var nxt: Vector2i = cur + step
			if prev.has(nxt) or not box.has_point(nxt) or not city.is_street(nxt.x, nxt.y):
				continue
			prev[nxt] = cur
			queue.append(nxt)
	var pts := PackedVector2Array()
	pts.append(Vector2(a) + Vector2(0.5, 0.5))
	if prev.has(db):
		var chain: Array[Vector2i] = []
		var cur := db
		while cur != da:
			chain.append(cur)
			cur = prev[cur]
		chain.append(da)
		chain.reverse()
		# Keep only the corners so the path reads as clean street runs.
		for k in chain.size():
			if k == 0 or k == chain.size() - 1:
				pts.append(Vector2(chain[k]) + Vector2(0.5, 0.5))
				continue
			var d0 := chain[k] - chain[k - 1]
			var d1 := chain[k + 1] - chain[k]
			if d0 != d1:
				pts.append(Vector2(chain[k]) + Vector2(0.5, 0.5))
	else:
		pts.append(Vector2(b.x, a.y) + Vector2(0.5, 0.5))
	pts.append(Vector2(b) + Vector2(0.5, 0.5))
	return pts


func _to_local(p: Vector2) -> Vector2:
	return city.grid_to_local(p.x, p.y)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		for n in nodes:
			var rec := city.roof_of(lot_of(n["id"]).x, lot_of(n["id"]).y)
			if rec.is_empty():
				continue
			var roof: PackedVector2Array = rec["roof"]
			if Geometry2D.is_point_in_polygon(event.position, roof) or event.position.distance_to(rec["base"]) < 18.0:
				node_clicked.emit(n["id"])
				accept_event()
				return


## Static under-layer: the look's veil and every route's keyline and glow. Any redraw of
## the overlay also refreshes the layers above it.
func _draw() -> void:
	_top.queue_redraw()
	_anim.queue_redraw()
	_hi.queue_redraw()
	if city == null or nodes.is_empty():
		return
	_c = self
	match look:
		Look.ISOLATE:
			draw_rect(Rect2(Vector2.ZERO, size), Color(0.02, 0.02, 0.04, 0.62))
		Look.XRAY:
			draw_rect(Rect2(Vector2.ZERO, size), Color(0.0, 0.03, 0.05, 0.72))
		Look.BLUEPRINT:
			draw_rect(Rect2(Vector2.ZERO, size), Color(0.02, 0.1, 0.32, 0.55))
		Look.SPOTLIGHT:
			_spotlight()
	for k in edges.size():
		_edge_static(edges[k], _route_px(k))


## Flowing dashes and packets (redrawn every frame unless reduce-effects).
func _draw_anim() -> void:
	if city == null or nodes.is_empty():
		return
	_c = _anim
	for k in edges.size():
		_edge_flow(edges[k], _route_px(k))
	_c = self


## Nodes, marks, badges, tags, assets and threat markers.
func _draw_top() -> void:
	if city == null or nodes.is_empty():
		return
	_c = _top
	for n in nodes:
		_node(n)
	_c = self


## The selected node's pulsing ring.
func _draw_hi() -> void:
	if city == null or selected_id == &"" or not _lots.has(selected_id):
		return
	var rec := city.roof_of(lot_of(selected_id).x, lot_of(selected_id).y)
	if rec.is_empty():
		return
	var top := _centroid(rec["roof"])
	_hi.draw_arc(top, PULSE_RADIUS + sin(anim_t * PULSE_SPEED) * PULSE_AMPLITUDE, 0, TAU, 32, Palette.CELL_ACID, 2.0)


func _route_px(k: int) -> PackedVector2Array:
	var pts := PackedVector2Array()
	if k >= _routes.size():
		return pts
	for p in _routes[k]:
		pts.append(_to_local(p))
	return pts


func _spotlight() -> void:
	var c := size * 0.5
	if focus_id != &"" and _lots.has(focus_id):
		c = _to_local(Vector2(_lots[focus_id]) + Vector2(0.5, 0.5))
	var r := 230.0
	var fog := Color(0.01, 0.01, 0.03, 0.8)
	var clear := Color(0.01, 0.01, 0.03, 0.0)
	var ring := PackedVector2Array()
	for k in 49:
		ring.append(c + Vector2(cos(TAU * k / 48.0), sin(TAU * k / 48.0) * 0.6) * r)
	# Fog outside an ellipse: a feathered band, then an opaque ring out past the screen.
	for k in 48:
		var a := ring[k]
		var b := ring[k + 1]
		var a2 := c + (a - c) * 1.35
		var b2 := c + (b - c) * 1.35
		var a3 := c + (a - c) * 12.0
		var b3 := c + (b - c) * 12.0
		draw_polygon(PackedVector2Array([a, b, b2, a2]), PackedColorArray([clear, clear, fog, fog]))
		draw_colored_polygon(PackedVector2Array([a2, b2, b3, a3]), fog)
	draw_arc(c, r * 1.02, 0, TAU, 64, Color(Palette.NET_CYAN, 0.25), 1.5)


func _is_dashed(e: Dictionary) -> bool:
	return e.get("dashed", false) or look == Look.PILLARS


func _edge_static(e: Dictionary, pts: PackedVector2Array) -> void:
	if pts.size() < 2:
		return
	var col: Color = e.get("color", Palette.NET_CYAN)
	var width: float = e.get("width", 3.0)
	# Dark keyline under every path so it separates from the city's own ink.
	draw_polyline(pts, Color(0, 0, 0, 0.7), width + 5.0, true)
	draw_polyline(pts, Color(col, 0.16), width * 4.0, true)
	if not _is_dashed(e):
		draw_polyline(pts, col, width, true)


func _edge_flow(e: Dictionary, pts: PackedVector2Array) -> void:
	if pts.size() < 2:
		return
	var col: Color = e.get("color", Palette.NET_CYAN)
	var width: float = e.get("width", 3.0)
	if _is_dashed(e):
		var phase := fmod(anim_t * DASH_SPEED, DASH_PERIOD) if e.get("flow", true) else 0.0
		for k in pts.size() - 1:
			var a := pts[k]
			var b := pts[k + 1]
			var length := a.distance_to(b)
			var dir := (b - a) / maxf(length, 0.001)
			var t := phase
			while t < length:
				_c.draw_line(a + dir * t, a + dir * minf(t + DASH_ON, length), col, width)
				t += DASH_PERIOD
	elif e.get("flow", false):
		# A bright packet running along the route.
		var total := 0.0
		for k in pts.size() - 1:
			total += pts[k].distance_to(pts[k + 1])
		var d := fmod(anim_t * PACKET_SPEED, maxf(total, 1.0))
		for k in pts.size() - 1:
			var seg := pts[k].distance_to(pts[k + 1])
			if d <= seg:
				_c.draw_circle(pts[k].lerp(pts[k + 1], d / maxf(seg, 0.001)), width + 2.0, Palette.PAPER)
				break
			d -= seg


static func _centroid(pts: PackedVector2Array) -> Vector2:
	var c := Vector2.ZERO
	for q in pts:
		c += q
	return c / maxf(1.0, pts.size())


func _node(n: Dictionary) -> void:
	var lot: Vector2i = _lots.get(n["id"], Vector2i.ZERO)
	var rec := city.roof_of(lot.x, lot.y)
	if rec.is_empty():
		return
	var col: Color = n.get("color", Palette.CELL_PINK)
	var roof: PackedVector2Array = rec["roof"]
	var base: Vector2 = rec["base"]
	var top := _centroid(roof)
	var closed := roof.duplicate()
	closed.append(roof[0])
	var big: bool = n.get("big", false)
	match look:
		Look.PILLARS:
			var tip := top + Vector2(0, -70 if big else -46)
			_c.draw_colored_polygon(PackedVector2Array([base + Vector2(-7, 0), base + Vector2(7, 0), tip + Vector2(3, 0), tip + Vector2(-3, 0)]), Color(col, 0.16))
			_c.draw_line(base, tip, Color(col, 0.8), 1.5)
			_c.draw_colored_polygon(roof, Color(col, 0.3))
			_c.draw_polyline(closed, Color(0, 0, 0, 0.85), 6.0, true)
			_c.draw_polyline(closed, col, 2.0, true)
			_mark(n, top, col)
			_badge(tip, 13.0 if big else 10.0, col, n.get("glyph", ""))
			_tag(tip + Vector2(16, 4), n.get("label", ""), col)
		_:
			var fill_a := 0.45 if look == Look.ISOLATE or look == Look.XRAY or look == Look.BLUEPRINT else 0.28
			_c.draw_colored_polygon(roof, Color(col, fill_a))
			_c.draw_polyline(closed, Color(0, 0, 0, 0.85), 7.0, true)
			_c.draw_polyline(closed, Color(col, 0.3), 11.0, true)
			_c.draw_polyline(closed, col, 2.6, true)
			if look == Look.ISOLATE or look == Look.XRAY:
				_c.draw_line(base, top, Color(col, 0.6), 1.5)
			_mark(n, top, col)
			_badge(top + Vector2(0, -20), 10.0 if big else 8.0, col, n.get("glyph", ""))
			_tag(top + Vector2(14, -16), n.get("label", ""), col)
	var assets: Array = n.get("assets", [])
	for k in assets.size():
		var a := TAU * k / maxf(1.0, assets.size()) - PI * 0.5
		AssetIcon.draw_icon(_c, top + Vector2(cos(a) * 26.0, sin(a) * 14.0 - 6.0), 8.0, assets[k])
	if n.has("result"):
		_tag(top + Vector2(14, 2), String(n["result"]), col)
	if n["id"] == selected_id:
		_c.draw_polyline(closed, Palette.CELL_ACID, 1.5, true)
	if markers.has(n["id"]):
		var names: Array = markers[n["id"]]
		for k in names.size():
			var mp := top + Vector2(-16 + k * 16, -44)
			var dia := PackedVector2Array([mp + Vector2(0, -9), mp + Vector2(8, 0), mp + Vector2(0, 9), mp + Vector2(-8, 0)])
			_c.draw_colored_polygon(dia, Palette.corp_color(StringName(n.get("threat_corp", "solace"))) if n.has("threat_corp") else Palette.CORP_SOLACE)
			_c.draw_polyline(dia + PackedVector2Array([dia[0]]), Palette.PAPER, 1.2)
		_tag(top + Vector2(-40, -60), ", ".join(names), Palette.PAPER)


## The node's non-colour mark: a spray-paint ring (claimed) or a cross (Seized). The
## wobble and drips come from a hash of the node id (no game RNG).
func _mark(n: Dictionary, at: Vector2, col: Color) -> void:
	match String(n.get("mark", "")):
		MARK_SPRAY:
			var seed_v := absi(hash(String(n["id"])))
			var ring := PackedVector2Array()
			for k in SPRAY_SEGMENTS + 1:
				var t := TAU * k / SPRAY_SEGMENTS
				var wob := sin(t * 3.0 + float(seed_v % 97)) * SPRAY_WOBBLE
				ring.append(at + Vector2(cos(t), sin(t) * 0.55) * (SPRAY_RADIUS + wob))
			_c.draw_polyline(ring, Color(0, 0, 0, 0.8), 6.0, true)
			_c.draw_polyline(ring, Color(Palette.CELL_PINK, 0.95), 3.0, true)
			for d in SPRAY_DRIPS:
				var t := TAU * (0.15 + 0.2 * d) + float((seed_v >> (d * 4)) % 7) * 0.05
				var p := at + Vector2(cos(t), sin(t) * 0.55) * SPRAY_RADIUS
				var drip := SPRAY_DRIP_LEN * (0.6 + 0.4 * float((seed_v >> (d * 3)) % 5) / 4.0)
				_c.draw_line(p, p + Vector2(0, drip), Color(Palette.CELL_PINK, 0.85), 2.0)
				_c.draw_circle(p + Vector2(0, drip), 1.6, Color(Palette.CELL_PINK, 0.85))
		MARK_CROSS:
			var s := CROSS_SIZE
			for pair in [[Vector2(-s, -s * 0.6), Vector2(s, s * 0.6)], [Vector2(-s, s * 0.6), Vector2(s, -s * 0.6)]]:
				_c.draw_line(at + pair[0], at + pair[1], Color(0, 0, 0, 0.85), 6.0)
				_c.draw_line(at + pair[0], at + pair[1], col, 3.0)


func _badge(p: Vector2, r: float, col: Color, glyph: String) -> void:
	var pts := PackedVector2Array()
	for k in 7:
		var t := PI / 6.0 + TAU * k / 6.0
		pts.append(p + Vector2(cos(t), sin(t)) * r)
	_c.draw_colored_polygon(pts, Color(Palette.NIGHT_SKY, 0.92))
	_c.draw_polyline(pts, col, 1.6)
	if glyph != "":
		_c.draw_string(Palette.mono(), p + Vector2(-r, r * 0.45), glyph, HORIZONTAL_ALIGNMENT_CENTER, r * 2.0, int(r * 1.15), col)


func _tag(at: Vector2, text: String, col: Color) -> void:
	if text == "":
		return
	var f := Palette.mono()
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x
	_c.draw_rect(Rect2(at.x - 3, at.y - 11, w + 6, 15), Color(Palette.NIGHT_SKY, 0.82))
	_c.draw_rect(Rect2(at.x - 3, at.y - 11, 2, 15), col)
	_c.draw_string(f, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Palette.PAPER)
