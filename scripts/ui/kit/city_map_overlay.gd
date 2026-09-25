class_name CityMapOverlay
extends Control
## Map overlays drawn ON the city (the Grid, raids, netrun routes): each node is a real
## building (highlighted by its roof outline: square, diamond, hexagon, octagon, the
## building's own cross-section) and each link follows the streets between them. The
## overlay is a child of the NeonCity so it pans and zooms with it, and it keeps the
## current (saturated) hues so it pops over a paler city. Pure view.
##
## Feed it a graph with `set_graph(nodes, edges)`:
##   nodes: [{id, at: Vector2 (grid target), color, label, glyph, big: bool}]
##   edges: [{a, b, color, width, dashed: bool, flow: bool}]
## and optional `markers` (node id -> Array[String]) for threats standing on nodes.

signal node_clicked(id: StringName)

## TRACE: roof outlines and solid street paths. PILLARS: light pillars and floating
## badges, flowing dashed paths. ISOLATE: the rest of the city greyed out.
## XRAY / BLUEPRINT / SPOTLIGHT: netrun looks (see `set_look`).
enum Look { TRACE, PILLARS, ISOLATE, XRAY, BLUEPRINT, SPOTLIGHT }

var city: NeonCity
var look: int = Look.TRACE
var nodes: Array[Dictionary] = []
var edges: Array[Dictionary] = []
var markers: Dictionary = {}
var selected_id: StringName = &""
## Spotlight target (node id) for the SPOTLIGHT look.
var focus_id: StringName = &""
var anim_t: float = 0.0

var _lots: Dictionary = {}  # node id -> Vector2i
var _routes: Array[PackedVector2Array] = []  # grid points per edge


func _init(p_city: NeonCity = null) -> void:
	city = p_city
	mouse_filter = Control.MOUSE_FILTER_PASS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	if city != null:
		city.rebuilt.connect(_relayout)


func _process(delta: float) -> void:
	if Settings.reduce_effects or not is_visible_in_tree():
		return
	anim_t += delta
	queue_redraw()


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


func _draw() -> void:
	if city == null or nodes.is_empty():
		return
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
		_edge(edges[k], _routes[k] if k < _routes.size() else PackedVector2Array())
	for n in nodes:
		_node(n)


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


func _edge(e: Dictionary, route: PackedVector2Array) -> void:
	if route.size() < 2:
		return
	var col: Color = e.get("color", Palette.NET_CYAN)
	var width: float = e.get("width", 3.0)
	var pts := PackedVector2Array()
	for p in route:
		pts.append(_to_local(p))
	var dashed: bool = e.get("dashed", false) or look == Look.PILLARS
	# Dark keyline under every path so it separates from the city's own ink.
	draw_polyline(pts, Color(0, 0, 0, 0.7), width + 5.0, true)
	draw_polyline(pts, Color(col, 0.16), width * 4.0, true)
	if dashed:
		var phase := fmod(anim_t * 30.0, 16.0) if e.get("flow", true) else 0.0
		for k in pts.size() - 1:
			var a := pts[k]
			var b := pts[k + 1]
			var length := a.distance_to(b)
			var dir := (b - a) / maxf(length, 0.001)
			var t := phase
			while t < length:
				draw_line(a + dir * t, a + dir * minf(t + 9.0, length), col, width)
				t += 16.0
	else:
		draw_polyline(pts, col, width, true)
	if e.get("flow", false) and not dashed:
		# A bright packet running along the route.
		var total := 0.0
		for k in pts.size() - 1:
			total += pts[k].distance_to(pts[k + 1])
		var d := fmod(anim_t * 90.0, maxf(total, 1.0))
		for k in pts.size() - 1:
			var seg := pts[k].distance_to(pts[k + 1])
			if d <= seg:
				draw_circle(pts[k].lerp(pts[k + 1], d / maxf(seg, 0.001)), width + 2.0, Palette.PAPER)
				break
			d -= seg


func _node(n: Dictionary) -> void:
	var lot: Vector2i = _lots.get(n["id"], Vector2i.ZERO)
	var rec := city.roof_of(lot.x, lot.y)
	if rec.is_empty():
		return
	var col: Color = n.get("color", Palette.CELL_PINK)
	var roof: PackedVector2Array = rec["roof"]
	var base: Vector2 = rec["base"]
	var top := Vector2.ZERO
	for q in roof:
		top += q
	top /= maxf(1.0, roof.size())
	var closed := roof.duplicate()
	closed.append(roof[0])
	var big: bool = n.get("big", false)
	match look:
		Look.PILLARS:
			var tip := top + Vector2(0, -70 if big else -46)
			draw_colored_polygon(PackedVector2Array([base + Vector2(-7, 0), base + Vector2(7, 0), tip + Vector2(3, 0), tip + Vector2(-3, 0)]), Color(col, 0.16))
			draw_line(base, tip, Color(col, 0.8), 1.5)
			draw_colored_polygon(roof, Color(col, 0.3))
			draw_polyline(closed, Color(0, 0, 0, 0.85), 6.0, true)
			draw_polyline(closed, col, 2.0, true)
			_badge(tip, 13.0 if big else 10.0, col, n.get("glyph", ""))
			_tag(tip + Vector2(16, 4), n.get("label", ""), col)
		_:
			var fill_a := 0.45 if look == Look.ISOLATE or look == Look.XRAY or look == Look.BLUEPRINT else 0.28
			draw_colored_polygon(roof, Color(col, fill_a))
			draw_polyline(closed, Color(0, 0, 0, 0.85), 7.0, true)
			draw_polyline(closed, Color(col, 0.3), 11.0, true)
			draw_polyline(closed, col, 2.6, true)
			if look == Look.ISOLATE or look == Look.XRAY:
				draw_line(base, top, Color(col, 0.6), 1.5)
			_badge(top + Vector2(0, -20), 10.0 if big else 8.0, col, n.get("glyph", ""))
			_tag(top + Vector2(14, -16), n.get("label", ""), col)
	var assets: Array = n.get("assets", [])
	for k in assets.size():
		var a := TAU * k / maxf(1.0, assets.size()) - PI * 0.5
		AssetIcon.draw_icon(self, top + Vector2(cos(a) * 26.0, sin(a) * 14.0 - 6.0), 8.0, assets[k])
	if n.has("result"):
		_tag(top + Vector2(14, 2), String(n["result"]), col)
	if n["id"] == selected_id:
		draw_polyline(closed, Palette.CELL_ACID, 1.5, true)
		draw_arc(top, 30.0 + sin(anim_t * 4.0) * 3.0, 0, TAU, 32, Palette.CELL_ACID, 2.0)
	if markers.has(n["id"]):
		var names: Array = markers[n["id"]]
		for k in names.size():
			var mp := top + Vector2(-16 + k * 16, -44)
			var dia := PackedVector2Array([mp + Vector2(0, -9), mp + Vector2(8, 0), mp + Vector2(0, 9), mp + Vector2(-8, 0)])
			draw_colored_polygon(dia, Palette.corp_color(StringName(n.get("threat_corp", "solace"))) if n.has("threat_corp") else Palette.CORP_SOLACE)
			draw_polyline(dia + PackedVector2Array([dia[0]]), Palette.PAPER, 1.2)
		_tag(top + Vector2(-40, -60), ", ".join(names), Palette.PAPER)


func _badge(p: Vector2, r: float, col: Color, glyph: String) -> void:
	var pts := PackedVector2Array()
	for k in 7:
		var t := PI / 6.0 + TAU * k / 6.0
		pts.append(p + Vector2(cos(t), sin(t)) * r)
	draw_colored_polygon(pts, Color(Palette.NIGHT_SKY, 0.92))
	draw_polyline(pts, col, 1.6)
	if glyph != "":
		draw_string(Palette.mono(), p + Vector2(-r, r * 0.45), glyph, HORIZONTAL_ALIGNMENT_CENTER, r * 2.0, int(r * 1.15), col)


func _tag(at: Vector2, text: String, col: Color) -> void:
	if text == "":
		return
	var f := Palette.mono()
	var w := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x
	draw_rect(Rect2(at.x - 3, at.y - 11, w + 6, 15), Color(Palette.NIGHT_SKY, 0.82))
	draw_rect(Rect2(at.x - 3, at.y - 11, 2, 15), col)
	draw_string(f, at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Palette.PAPER)
