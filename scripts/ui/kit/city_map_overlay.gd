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
##            mark: "spray" (claimed: a spray-paint ring) | "cross" (Seized) | "",
##            kind: an icon (KIND_*; "" draws `glyph` in a hexagon), tip: hover text,
##            here: bool (you are here), next: bool (reachable now),
##            tier: int (a Site's tier 1-4: difficulty pips; 0 or missing = none)}]
##   edges: [{a, b, color, width, dashed: bool, flow: bool}]
## and optional `markers` (node id -> Array[String]) for threats standing on nodes.
## When any node carries `here` or `next` (a netrun route), nodes that can no longer be
## reached along the (directed) edges are dimmed.
##
## Drawing is layered so only the moving parts redraw every frame (H20): this control
## draws the static under-layer (looks, route keylines), `_anim` the flowing dashes and
## packets, `_top` the nodes, badges, tags and markers (redrawn only when something
## changes), `_hi` the pulsing selection ring.
##
## H21: node icons are drawn shapes (not font glyphs), sized in screen pixels (the city's
## zoom is undone) and shared with the MapLegend; labels follow Settings.text_scale and
## are placed so no two overlap (priority: selected / you are here, then reachable,
## claimed and landmark nodes, then the rest; ties by node id; a label with no free spot
## is left out and its node keeps its tooltip).
##
## H22: labels stay inside the visible map (`screen_rect`, else the overlay's own rect)
## and out of the screen areas the scene names (`avoid_controls`, `set_blocked_rects`: a
## side column); a focus label (selected, you are here, threats) or a landmark's (CORE,
## the boss) with no free spot near its node moves inward instead. Sites carry a tier
## difficulty cue: `draw_tier` pips under the icon, shared with the legend and mini-map.
##
## H23: a node off the visible map (outside it or under a blocked area) gets no label; a
## moved label stays within LABEL_REACH of its node and never lands on another label.
## Every kind has a word (`kind_word`) its tooltip leads with.

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
## Selection ring pulse round the selected icon (gap beyond the icon and amplitude, screen
## px; speed rad/s).
const SELECT_RING := 6.0
const PULSE_AMPLITUDE := 3.0
const PULSE_SPEED := 4.0

## Node icons (H21 #14): each kind has its own silhouette and symbol.
const KIND_FIGHT := "fight"
const KIND_ELITE := "elite"
const KIND_SHOP := "shop"
const KIND_EVENT := "event"
const KIND_RACK := "rack"
const KIND_BOSS := "boss"
const KIND_EXPLOIT := "exploit"
const KIND_HEAT := "heat"
const KIND_HOME := "home"
const KIND_TIER := "tier"
## Plain names of the kinds (tooltips built here when a node has no tip).
const KIND_NAMES := {KIND_FIGHT: "Router: a fight", KIND_ELITE: "Elite Router: a harder fight",
	KIND_SHOP: "Modem: the cyber shop", KIND_EVENT: "Terminal: an event with choices",
	KIND_RACK: "Server Rack: the Site's guardian", KIND_BOSS: "Boss Site: the corporation's core",
	KIND_EXPLOIT: "Exploit Site", KIND_HEAT: "Heat reduction Site", KIND_HOME: "Your home Site (CORE)",
	KIND_TIER: "Site"}
## H23 #6: the one word naming each kind (it leads every node tooltip).
const KIND_WORDS := {KIND_FIGHT: "Router", KIND_ELITE: "Elite Router", KIND_SHOP: "Modem", KIND_EVENT: "Terminal",
	KIND_RACK: "Server Rack", KIND_BOSS: "Boss", KIND_EXPLOIT: "Exploit", KIND_HEAT: "Heat reduction",
	KIND_HOME: "CORE", KIND_TIER: "Site"}
## Icon radius on screen (px, undoing the city's zoom), for normal and big nodes, and
## how far above the roof the icon floats (px, local).
const ICON_RADIUS := 13.0
const ICON_RADIUS_BIG := 17.0
const ICON_LIFT := 10.0
## Clearance between two icons (screen px), and how many steps an icon may float up to
## clear the icons in front of it.
const ICON_SPACING := 3.0
const ICON_STACK_MAX := 4
## Pillars look: how high the badge floats over normal and big nodes (px, local).
const PILLAR_HEIGHT := 46.0
const PILLAR_HEIGHT_BIG := 70.0
## Map labels: font size at text scale 1.0 (screen px), padding and gap to the icon (px).
const TAG_FONT := 13
const TAG_PAD := 3.0
const LABEL_GAP := 4.0
## Candidate rings a label may step out to when its first spots are taken.
const LABEL_RINGS := 3
## Label priorities (lower is placed first).
const PRIO_FOCUS := 0
const PRIO_KEY := 1
const PRIO_REST := 2
## The label of the "you are here" node when it has none of its own.
const HERE_LABEL := "YOU ARE HERE"
## Unreachable route nodes are drawn at this opacity.
const DIM_ALPHA := 0.3
## The "you are here" pin: size (screen px) and the ring around the icon (px beyond it).
const HERE_PIN := 9.0
const HERE_RING := 5.0
## Threat markers over a node: half-height and spacing (screen px).
const MARKER_SIZE := 9.0
const MARKER_STEP := 16.0
## Smallest city zoom the screen-size maths accepts.
const MIN_ZOOM := 0.1
## H22: labels keep this far inside the visible map area (screen px).
const EDGE_MARGIN := 4.0
## How far past a blocked area's edge a label moved out of it lands (local px).
const SHIFT_CLEARANCE := 1.0
## H23 #2: the furthest a label may sit from its node's centre (its nearest point, screen
## px); a label with no spot that near is left out (the node keeps its tooltip).
const LABEL_REACH := 110.0
## H22 tier difficulty cue: a row of TIER_PIPS_MAX pips under a Site's icon, `tier` of
## them lit (SiteData.tier is 1-4). Pip radius and spacing (screen px, at text scale
## 1.0 on the legend and mini-map; the map's pips follow the icon size) and the gap
## between the icon and the row.
const TIER_PIPS_MAX := 4
const TIER_PIP := 2.6
const TIER_PIP_STEP := 7.0
const TIER_PIP_GAP := 3.0

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
## Route graphs: node id -> true for nodes still reachable (empty = nothing dimmed).
var _reach: Dictionary = {}
## Icon positions (id -> local px) and the camera/look key they were placed for.
var _icon_cache: Dictionary = {}
var _icon_key: String = ""
var _anim: Control
var _top: Control
var _hi: Control
## The canvas item the helpers draw on (self, _anim, _top or _hi).
var _c: CanvasItem
## H22: the part of the viewport the map shows through (viewport px; a zero size means
## the overlay's own rect), and the screen areas labels keep out of: rects (viewport px)
## and controls read at each layout (a screen's side column).
var screen_rect: Rect2 = Rect2():
	set(v):
		screen_rect = v
		if _top != null:
			_top.queue_redraw()
## The tier pips of the last node draw (node id -> tier), for checks.
var drawn_tiers: Dictionary = {}
var _blocked_rects: Array[Rect2] = []
var _blocked_controls: Array[Control] = []


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
	# Labels follow the text size live (redrawn once per change, never per frame).
	Settings.changed.connect(_top.queue_redraw)


## The netrun route kind for an InfilNodeType (elite Routers are their own kind).
static func route_kind(node_type: int, elite: bool) -> String:
	match node_type:
		RC.InfilNodeType.ROUTER:
			return KIND_ELITE if elite else KIND_FIGHT
		RC.InfilNodeType.TERMINAL:
			return KIND_EVENT
		RC.InfilNodeType.MODEM:
			return KIND_SHOP
		RC.InfilNodeType.SERVER_RACK:
			return KIND_RACK
	return ""


## The word naming node kind `kind` (KIND_WORDS; "" for an unknown kind).
static func kind_word(kind: String) -> String:
	return String(KIND_WORDS.get(kind, ""))


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


## H22: screen areas the map labels keep out of, in viewport px (e.g. a panel over the
## map). Replaces the previous rects.
func set_blocked_rects(rects: Array[Rect2]) -> void:
	_blocked_rects = rects.duplicate()
	_top.queue_redraw()


## H22: controls over the map (a screen's side column) the labels keep out of; their
## on-screen rects are read at each layout, and the labels move when they do.
func avoid_controls(controls: Array[Control]) -> void:
	_blocked_controls = controls.duplicate()
	for c in _blocked_controls:
		if is_instance_valid(c) and not c.item_rect_changed.is_connected(_top.queue_redraw):
			c.item_rect_changed.connect(_top.queue_redraw)
	_top.queue_redraw()


## The area map labels may use (local px): the overlay's own rect (or `screen_rect` within
## it) less EDGE_MARGIN.
func label_area() -> Rect2:
	var area := Rect2(Vector2.ZERO, size)
	if screen_rect.has_area() and is_inside_tree():
		area = area.intersection(_to_local_rect(screen_rect))
	var m := EDGE_MARGIN * _k()
	return area.grow(-m) if area.size.x > m * 2.0 and area.size.y > m * 2.0 else area


## The screen areas labels keep out of (local px): the blocked rects and the visible
## blocked controls.
func label_blocks() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if not is_inside_tree():
		return out
	for r in _blocked_rects:
		out.append(_to_local_rect(r))
	for c in _blocked_controls:
		if is_instance_valid(c) and c.is_visible_in_tree() and c.size != Vector2.ZERO:
			out.append(_to_local_rect(c.get_global_transform_with_canvas() * Rect2(Vector2.ZERO, c.size)))
	return out


## A viewport-px rect in this overlay's local px.
func _to_local_rect(r: Rect2) -> Rect2:
	return get_global_transform_with_canvas().affine_inverse() * r


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


## The "you are here" node (&"" when the graph has none).
func here_id() -> StringName:
	for n in nodes:
		if n.get("here", false):
			return n["id"]
	return &""


## True when node `id` is on a route graph and can no longer be reached (drawn dimmed).
func is_dimmed(id: StringName) -> bool:
	return not _reach.is_empty() and not _reach.has(id)


## Route graphs: every node reachable from "you are here" and the nodes open now, along
## the directed edges (a -> b). Empty for graphs without route state (nothing dimmed).
func _reachable() -> Dictionary:
	var out := {}
	var queue: Array[StringName] = []
	var routed := false
	for n in nodes:
		if n.has("here") or n.has("next"):
			routed = true
		if n.get("here", false) or n.get("next", false):
			out[n["id"]] = true
			queue.append(n["id"])
	if not routed:
		return {}
	var head := 0
	while head < queue.size():
		var cur := queue[head]
		head += 1
		for e in edges:
			if e["a"] == cur and not out.has(e["b"]):
				out[e["b"]] = true
				queue.append(e["b"])
	return out


func _relayout() -> void:
	_lots.clear()
	_routes.clear()
	_reach = _reachable()
	_icon_key = ""
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
		var id := node_at(event.position)
		if id != &"":
			node_clicked.emit(id)
			accept_event()


## The node under local point `p` (its icon first, then its roof or base), or &"". Icons
## are tested nearest first; roofs in graph order.
func node_at(p: Vector2) -> StringName:
	if city == null:
		return &""
	var best: StringName = &""
	var best_d := INF
	for n in nodes:
		var d := p.distance_to(icon_pos(n))
		if d <= icon_radius(n) and d < best_d:
			best_d = d
			best = n["id"]
	if best != &"":
		return best
	for n in nodes:
		var rec := _roof(n["id"])
		if rec.is_empty():
			continue
		if Geometry2D.is_point_in_polygon(p, rec["roof"]) or p.distance_to(rec["base"]) < ICON_RADIUS_BIG:
			return n["id"]
	return &""


## Hover text for the node under the pointer (H21 #14): its tip, where it stands on the
## route, the raid result and the threats on it; folded for the tooltip popup.
func _get_tooltip(at_position: Vector2) -> String:
	var id := node_at(at_position)
	return UiTip.fold(tip_of(id)) if id != &"" else ""


## The hover text of node `id`: its own "tip" or one built from what the node carries
## (label, kind, mark), plus its route state, raid result and threats.
func tip_of(id: StringName) -> String:
	var n := _node_dict(id)
	if n.is_empty():
		return ""
	var parts := PackedStringArray()
	var tip := String(n.get("tip", ""))
	if tip == "":
		var name_text := String(n.get("label", ""))
		var kind_text := String(KIND_NAMES.get(String(n.get("kind", "")), ""))
		if name_text != "" and kind_text != "":
			tip = "%s: %s." % [name_text, kind_text]
		elif name_text != "" or kind_text != "":
			tip = "%s." % (name_text if name_text != "" else kind_text)
		else:
			tip = String(n.get("glyph", String(id)))
		match String(n.get("mark", "")):
			MARK_SPRAY:
				tip += " Claimed: part of your network."
			MARK_CROSS:
				tip += " Seized by the corporation."
	parts.append(tip)
	if String(n.get("kind", "")) == KIND_ELITE and not tip.contains("Elite"):
		parts.append("Elite: a harder fight.")
	if n.get("here", false):
		parts.append("You are here.")
	elif n.get("next", false):
		parts.append("You can move here now.")
	elif is_dimmed(id):
		parts.append("Out of reach from here.")
	if n.has("result"):
		parts.append("Raid: %s." % String(n["result"]))
	if markers.has(id):
		parts.append("Threats here: %s." % ", ".join(markers[id]))
	return "\n".join(parts)


func _node_dict(id: StringName) -> Dictionary:
	for n in nodes:
		if n["id"] == id:
			return n
	return {}


func _roof(id: StringName) -> Dictionary:
	var lot := lot_of(id)
	return city.roof_of(lot.x, lot.y) if city != null else {}


## Screen-size factor: local px per screen px (the city's zoom undone).
func _k() -> float:
	return 1.0 / maxf(MIN_ZOOM, city.scale.x) if city != null else 1.0


## Icon radius of node `n` (local px).
func icon_radius(n: Dictionary) -> float:
	return (ICON_RADIUS_BIG if n.get("big", false) else ICON_RADIUS) * _k()


## Where node `n`'s icon sits (local px): floating over its roof, or atop its pillar;
## lifted higher when it would sit on a nearer node's icon (see `_icon_positions`).
func icon_pos(n: Dictionary) -> Vector2:
	return _icon_positions().get(n["id"], Vector2(INF, INF))


## Every node's icon position (id -> local px), cached per camera and look. Icons are
## placed front to back (nearest roof first, ties by id); one that would overlap an icon
## already placed floats up a step at a time (its stalk grows), at most ICON_STACK_MAX.
func _icon_positions() -> Dictionary:
	if city == null or nodes.is_empty():
		return {}
	var first := _roof(nodes[0]["id"])
	var key := str([look, city.scale.x, first.get("base", Vector2.INF), nodes.size(), _lots.size()])
	if key == _icon_key:
		return _icon_cache
	var order: Array[Dictionary] = []
	for n in nodes:
		var rec := _roof(n["id"])
		if not rec.is_empty():
			order.append({"n": n, "top": _centroid(rec["roof"])})
	order.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if not is_equal_approx(a["top"].y, b["top"].y):
			return a["top"].y > b["top"].y
		return String(a["n"]["id"]) < String(b["n"]["id"]))
	var out := {}
	var placed: Array[Vector3] = []  # x, y, radius
	var gap := ICON_SPACING * _k()
	for o in order:
		var n: Dictionary = o["n"]
		var r := icon_radius(n)
		var big: bool = n.get("big", false)
		var p: Vector2 = o["top"] + Vector2(0, -((PILLAR_HEIGHT_BIG if big else PILLAR_HEIGHT) if look == Look.PILLARS else ICON_LIFT + r))
		for step in ICON_STACK_MAX:
			var hit := false
			for q in placed:
				if p.distance_to(Vector2(q.x, q.y)) < r + q.z + gap:
					hit = true
					break
			if not hit:
				break
			p.y -= r * 2.0 + gap
		placed.append(Vector3(p.x, p.y, r))
		out[n["id"]] = p
	_icon_key = key
	_icon_cache = out
	return out


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
	drawn_tiers.clear()
	for n in nodes:
		_node(n)
	for l: Dictionary in _layout_labels():
		_tag_box(l)
	_c = self


## The selected node's pulsing ring.
func _draw_hi() -> void:
	var at := ring_centre()
	if at.x == INF:
		return
	_hi.draw_arc(at, ring_radius() + (sin(anim_t * PULSE_SPEED) - 1.0) * PULSE_AMPLITUDE * _k(), 0, TAU, 32, Palette.CELL_ACID, 2.0 * _k())


## Centre of the selection ring (the selected node's icon), or INF when none shows.
func ring_centre() -> Vector2:
	if city == null or selected_id == &"" or not _lots.has(selected_id):
		return Vector2(INF, INF)
	return _icon_positions().get(selected_id, Vector2(INF, INF))


## Outer radius of the pulsing selection ring (local px): round the icon, clear of it.
func ring_radius() -> float:
	var n := _node_dict(selected_id)
	return (icon_radius(n) if not n.is_empty() else ICON_RADIUS * _k()) + (SELECT_RING + PULSE_AMPLITUDE) * _k()


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
	var rec := _roof(n["id"])
	if rec.is_empty():
		return
	var dim := is_dimmed(n["id"])
	var col: Color = n.get("color", Palette.CELL_PINK)
	if dim:
		col = Color(col, col.a * DIM_ALPHA)
	var roof: PackedVector2Array = rec["roof"]
	var base: Vector2 = rec["base"]
	var top := _centroid(roof)
	var closed := roof.duplicate()
	closed.append(roof[0])
	var ink := Color(0, 0, 0, 0.85 * (DIM_ALPHA if dim else 1.0))
	var at := icon_pos(n)
	var r := icon_radius(n)
	match look:
		Look.PILLARS:
			_c.draw_colored_polygon(PackedVector2Array([base + Vector2(-7, 0), base + Vector2(7, 0), at + Vector2(3, 0), at + Vector2(-3, 0)]), Color(col, col.a * 0.16))
			_c.draw_line(base, at, Color(col, col.a * 0.8), 1.5)
			_c.draw_colored_polygon(roof, Color(col, col.a * 0.3))
			_c.draw_polyline(closed, ink, 6.0, true)
			_c.draw_polyline(closed, col, 2.0, true)
		_:
			var fill_a := 0.45 if look == Look.ISOLATE or look == Look.XRAY or look == Look.BLUEPRINT else 0.28
			_c.draw_colored_polygon(roof, Color(col, col.a * fill_a))
			_c.draw_polyline(closed, ink, 7.0, true)
			_c.draw_polyline(closed, Color(col, col.a * 0.3), 11.0, true)
			_c.draw_polyline(closed, col, 2.6, true)
			if look == Look.ISOLATE or look == Look.XRAY:
				_c.draw_line(base, top, Color(col, col.a * 0.6), 1.5)
			# A short stalk ties the floating icon to its roof.
			_c.draw_line(top, at + Vector2(0, r), Color(col, col.a * 0.7), 1.5)
	_mark(n, top, col)
	if n.get("here", false):
		_here(at, r)
	draw_icon(_c, String(n.get("kind", "")), at, r, col, String(n.get("glyph", "")), DIM_ALPHA if dim else 1.0)
	if tier_of(n) > 0:
		draw_tier(_c, tier_pips_centre(n), tier_of(n), col, _pip_scale(n), DIM_ALPHA if dim else 1.0)
		drawn_tiers[n["id"]] = tier_of(n)
	var assets: Array = n.get("assets", [])
	for k in assets.size():
		var a := TAU * k / maxf(1.0, assets.size()) - PI * 0.5
		AssetIcon.draw_icon(_c, top + Vector2(cos(a) * 26.0, sin(a) * 14.0 - 6.0), 8.0, assets[k])
	if n["id"] == selected_id:
		_c.draw_polyline(closed, Palette.CELL_ACID, 1.5, true)
	if markers.has(n["id"]):
		var names: Array = markers[n["id"]]
		var row := _marker_row(n)
		for k in names.size():
			var mp := row + Vector2((k - (names.size() - 1) * 0.5) * MARKER_STEP * _k(), 0)
			var s := MARKER_SIZE * _k()
			var dia := PackedVector2Array([mp + Vector2(0, -s), mp + Vector2(s * 0.9, 0), mp + Vector2(0, s), mp + Vector2(-s * 0.9, 0)])
			_c.draw_colored_polygon(dia, Palette.corp_color(StringName(n.get("threat_corp", "solace"))) if n.has("threat_corp") else Palette.CORP_SOLACE)
			_c.draw_polyline(dia + PackedVector2Array([dia[0]]), Palette.PAPER, 1.2)


## Node `n`'s Site tier for the difficulty pips (0: no pips, e.g. route nodes, CORE).
static func tier_of(n: Dictionary) -> int:
	return clampi(int(n.get("tier", 0)), 0, TIER_PIPS_MAX)


## Map pips' scale for node `n`: they follow its icon's size (local px per legend px).
func _pip_scale(n: Dictionary) -> float:
	return icon_radius(n) / ICON_RADIUS


## Centre of node `n`'s tier pip row, under its icon (local px).
func tier_pips_centre(n: Dictionary) -> Vector2:
	var s := _pip_scale(n)
	return icon_pos(n) + Vector2(0, icon_radius(n) + (TIER_PIP_GAP + TIER_PIP) * s)


## The rect node `n`'s tier pips cover (local px; zero size when it has none).
func tier_pips_rect(n: Dictionary) -> Rect2:
	if tier_of(n) <= 0:
		return Rect2()
	var box := tier_pips_size(_pip_scale(n))
	return Rect2(tier_pips_centre(n) - box * 0.5, box)


## Size of a tier pip row drawn at `scale` (px).
static func tier_pips_size(scale: float = 1.0) -> Vector2:
	return Vector2(TIER_PIP_STEP * (TIER_PIPS_MAX - 1) + TIER_PIP * 2.0 + 2.0, TIER_PIP * 2.0 + 2.0) * scale


## Draws the tier difficulty cue (H22 #14) centred at `at`: TIER_PIPS_MAX pips in a row,
## the first `tier` lit in `col`, the rest hollow, so harder Sites read at a glance
## without the word "tier". Shared by the map, the MapLegend and the HQ mini-map (and
## any Site list) so the cue is the same everywhere. `scale` sizes it (1.0 = legend px).
static func draw_tier(ci: CanvasItem, at: Vector2, tier: int, col: Color, scale: float = 1.0, alpha: float = 1.0) -> void:
	var r := TIER_PIP * scale
	var step := TIER_PIP_STEP * scale
	var x0 := at.x - step * (TIER_PIPS_MAX - 1) * 0.5
	var ink := Color(0, 0, 0, 0.85 * alpha)
	var lit := Color(col, col.a * alpha)
	for k in TIER_PIPS_MAX:
		var p := Vector2(x0 + step * k, at.y)
		ci.draw_circle(p, r + maxf(1.0, scale), ink)
		if k < tier:
			ci.draw_circle(p, r, lit)
		else:
			ci.draw_arc(p, r * 0.8, 0, TAU, 12, Color(col, col.a * 0.55 * alpha), maxf(1.0, scale * 0.8))


## Centre of the threat markers' row over node `n` (local px).
func _marker_row(n: Dictionary) -> Vector2:
	return icon_pos(n) - Vector2(0, icon_radius(n) + (LABEL_GAP + MARKER_SIZE) * _k())


## The "you are here" mark: a pink ring round the icon and a pin pointing down at it.
func _here(at: Vector2, r: float) -> void:
	var k := _k()
	var ring := r + HERE_RING * k
	_c.draw_arc(at, ring, 0, TAU, 32, Color(0, 0, 0, 0.85), 5.0 * k)
	_c.draw_arc(at, ring, 0, TAU, 32, Palette.CELL_PINK, 2.5 * k)
	var tip := at - Vector2(0, ring + 2.0 * k)
	var s := HERE_PIN * k
	var pin := PackedVector2Array([tip, tip + Vector2(-s, -s * 1.4), tip + Vector2(s, -s * 1.4)])
	_c.draw_colored_polygon(pin, Palette.CELL_PINK)
	_c.draw_polyline(pin + PackedVector2Array([pin[0]]), Color(0, 0, 0, 0.85), 1.5 * k)


# --- Labels -----------------------------------------------------------------------------

## Font size of the map labels (local px): TAG_FONT screen px at the current text scale.
func label_font_size() -> int:
	return maxi(1, roundi(TAG_FONT * Settings.text_scale * _k()))


## The labels drawn now: node id -> Rect2 (local px). Threat tags are keyed "<id>#threats".
func label_rects() -> Dictionary:
	var out := {}
	for l: Dictionary in _layout_labels():
		out[l["key"]] = l["rect"]
	return out


## The text lines of node `id`'s label ([] when it has none).
func label_lines(id: StringName) -> PackedStringArray:
	var n := _node_dict(id)
	var lines := PackedStringArray()
	if n.is_empty() or is_dimmed(id):
		return lines
	var text := String(n.get("label", ""))
	if text == "" and n.get("here", false):
		text = HERE_LABEL
	if text != "":
		lines.append(text)
	if n.has("result"):
		lines.append(String(n["result"]))
	return lines


func _prio(n: Dictionary) -> int:
	if n["id"] == selected_id or n.get("here", false):
		return PRIO_FOCUS
	if n.get("next", false) or String(n.get("mark", "")) == MARK_SPRAY or n.get("big", false):
		return PRIO_KEY
	return PRIO_REST


## Places every label (H21 #15): by priority, then node id, each at the first free spot
## around its icon (right, left, above, below, then the corners, stepping further out);
## a spot is free when it overlaps no placed label, no node icon and not the selection
## ring. Focus labels (selected, you are here, threats) always show; others with no
## free spot are left out. Deterministic: the same graph and camera give the same layout.
func _layout_labels() -> Array[Dictionary]:
	var placed: Array[Dictionary] = []
	if city == null or nodes.is_empty():
		return placed
	var f := Palette.mono()
	var fs := label_font_size()
	var k := _k()
	var pad := TAG_PAD * k
	var line_h := f.get_height(fs)
	var icons: Array[Dictionary] = []
	var marks: Array[Rect2] = []
	for n in nodes:
		if not _roof(n["id"]).is_empty():
			icons.append({"id": n["id"], "at": icon_pos(n), "r": icon_radius(n)})
			if tier_of(n) > 0:
				marks.append(tier_pips_rect(n))
	var area := label_area()
	var blocks := label_blocks()
	var ring_c := ring_centre()
	var ring_r := ring_radius()
	var todo: Array[Dictionary] = []
	for n in nodes:
		if _roof(n["id"]).is_empty():
			continue
		var lines := label_lines(n["id"])
		if not lines.is_empty():
			todo.append({"key": String(n["id"]), "id": n["id"], "lines": lines, "col": n.get("color", Palette.CELL_PINK), "prio": _prio(n), "at": icon_pos(n), "r": icon_radius(n)})
		if markers.has(n["id"]) and not (markers[n["id"]] as Array).is_empty():
			var names := PackedStringArray()
			for m in markers[n["id"]]:
				names.append(String(m))
			var half := MARKER_SIZE * k
			todo.append({"key": "%s#threats" % n["id"], "id": n["id"], "lines": PackedStringArray([", ".join(names)]), "col": Palette.PAPER, "prio": PRIO_FOCUS,
				"at": _marker_row(n), "r": half + MARKER_STEP * k * 0.5 * (names.size() - 1)})
	todo.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if a["prio"] != b["prio"]:
			return a["prio"] < b["prio"]
		return String(a["key"]) < String(b["key"]))
	for t in todo:
		# H23 #2: a node off the visible map (outside it, or under a panel) has no label: a
		# label moved in for it would float with nothing to point at.
		if not _visible_at(t["at"], area, blocks):
			continue
		var w := 0.0
		for line in t["lines"]:
			w = maxf(w, f.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
		var box := Vector2(w + pad * 2.0, line_h * (t["lines"] as PackedStringArray).size() + pad * 2.0)
		var obstacles := {"icons": icons, "marks": marks, "placed": placed, "ring_c": ring_c, "ring_r": ring_r, "area": area, "blocks": blocks}
		var spot := _free_spot(t, box, obstacles)
		if spot.size == Vector2.ZERO:
			# H22: focus labels (and the landmarks: CORE, the boss) move inward onto the
			# screen rather than off it or under a side column (H23 #2: never further than
			# LABEL_REACH from their node; H23 #4: never onto another label).
			if t["prio"] != PRIO_FOCUS and not _node_dict(t["id"]).get("big", false):
				continue
			spot = _inward_spot(t, box, obstacles, t["prio"] == PRIO_FOCUS)
			if spot.size == Vector2.ZERO:
				continue
		t["rect"] = spot
		t["fs"] = fs
		t["pad"] = pad
		placed.append(t)
	return placed


## Candidate top-left corners for a `box` label around a centre `c` at distance `d`.
static func _spots(c: Vector2, d: float, box: Vector2) -> Array[Vector2]:
	return [Vector2(c.x + d, c.y - box.y * 0.5), Vector2(c.x - d - box.x, c.y - box.y * 0.5),
		Vector2(c.x - box.x * 0.5, c.y - d - box.y), Vector2(c.x - box.x * 0.5, c.y + d),
		Vector2(c.x + d * 0.7, c.y - d * 0.7 - box.y), Vector2(c.x - d * 0.7 - box.x, c.y - d * 0.7 - box.y),
		Vector2(c.x + d * 0.7, c.y + d * 0.7), Vector2(c.x - d * 0.7 - box.x, c.y + d * 0.7)]


## The first free spot for label `t` (Rect2 with a zero size when there is none): inside
## the label area, out of the blocked screen areas, clear of the obstacles.
func _free_spot(t: Dictionary, box: Vector2, obstacles: Dictionary) -> Rect2:
	for rect in _candidates(t, box):
		if _on_screen(rect, obstacles) and not _blocked(rect, obstacles):
			return rect
	return Rect2()


## Label `t`'s candidate rects, nearest ring first (see `_spots`).
func _candidates(t: Dictionary, box: Vector2) -> Array[Rect2]:
	var k := _k()
	var out: Array[Rect2] = []
	for ring in LABEL_RINGS:
		var d: float = t["r"] + LABEL_GAP * k + ring * (box.y + LABEL_GAP * k)
		for p in _spots(t["at"], d, box):
			out.append(Rect2(p, box))
	return out


## H22: a spot for a label that has no free one near its node: each candidate moved into
## the label area and out of the blocked screen areas, the first clear of the obstacles.
## With `always` (a focus label), the first moved candidate that is clear of the other
## labels when none is clear of everything (it may cover an icon, never a label: H23 #4).
## H23 #2: a moved spot must stay within LABEL_REACH of its node.
func _inward_spot(t: Dictionary, box: Vector2, obstacles: Dictionary, always: bool) -> Rect2:
	var loose := Rect2()
	var reach := LABEL_REACH * _k()
	for rect in _candidates(t, box):
		var moved := _shift_inside(rect, obstacles["area"], obstacles["blocks"])
		if not _on_screen(moved, obstacles) or reach_of(moved, t["at"]) > reach:
			continue
		if not _blocked(moved, obstacles):
			return moved
		if always and loose.size == Vector2.ZERO and not _hits_label(moved, obstacles):
			loose = moved
	return loose


## How far label `rect` lies from its node's centre `at` (its nearest point; local px).
static func reach_of(rect: Rect2, at: Vector2) -> float:
	var q := Vector2(clampf(at.x, rect.position.x, rect.end.x), clampf(at.y, rect.position.y, rect.end.y))
	return q.distance_to(at)


## True when node point `at` shows on the map: inside the label area and under no
## blocked screen area.
static func _visible_at(at: Vector2, area: Rect2, blocks: Array[Rect2]) -> bool:
	if not area.has_point(at):
		return false
	for b in blocks:
		if b.has_point(at):
			return false
	return true


## True when `rect` overlaps a label placed before it.
static func _hits_label(rect: Rect2, obstacles: Dictionary) -> bool:
	for other: Dictionary in obstacles["placed"]:
		if rect.intersects(other["rect"]):
			return true
	return false


## True when `rect` lies inside the label area and off every blocked screen area.
static func _on_screen(rect: Rect2, obstacles: Dictionary) -> bool:
	if not (obstacles["area"] as Rect2).encloses(rect):
		return false
	for b: Rect2 in obstacles["blocks"]:
		if rect.intersects(b):
			return false
	return true


## `rect` moved the least way into `area` and out of the `blocks` it overlaps (sideways
## first, the way that stays inside; else up or down), then clamped into `area` again.
static func _shift_inside(rect: Rect2, area: Rect2, blocks: Array[Rect2]) -> Rect2:
	var r := _clamp_into(rect, area)
	for b in blocks:
		if not r.intersects(b):
			continue
		# A pixel past the edge, so rounding never leaves the label touching the block.
		var e := SHIFT_CLEARANCE
		var moves: Array[Vector2] = [Vector2(b.position.x - r.end.x - e, 0), Vector2(b.end.x - r.position.x + e, 0),
			Vector2(0, b.position.y - r.end.y - e), Vector2(0, b.end.y - r.position.y + e)]
		var best := Vector2.INF
		for m in moves:
			if area.encloses(Rect2(r.position + m, r.size)) and m.length() < best.length():
				best = m
		if best != Vector2.INF:
			r.position += best
	return _clamp_into(r, area)


static func _clamp_into(rect: Rect2, area: Rect2) -> Rect2:
	var p := Vector2(clampf(rect.position.x, area.position.x, maxf(area.position.x, area.end.x - rect.size.x)),
		clampf(rect.position.y, area.position.y, maxf(area.position.y, area.end.y - rect.size.y)))
	return Rect2(p, rect.size)


## True when `rect` overlaps a placed label, a node icon, a tier pip row or the
## selection ring.
static func _blocked(rect: Rect2, obstacles: Dictionary) -> bool:
	for other: Dictionary in obstacles["placed"]:
		if rect.intersects(other["rect"]):
			return true
	for ic: Dictionary in obstacles["icons"]:
		if _rect_hits_disc(rect, ic["at"], ic["r"]):
			return true
	for m: Rect2 in obstacles["marks"]:
		if rect.intersects(m):
			return true
	var ring_c: Vector2 = obstacles["ring_c"]
	return ring_c.x != INF and _rect_hits_disc(rect, ring_c, obstacles["ring_r"])


static func _rect_hits_disc(rect: Rect2, c: Vector2, r: float) -> bool:
	var q := Vector2(clampf(c.x, rect.position.x, rect.end.x), clampf(c.y, rect.position.y, rect.end.y))
	return q.distance_to(c) < r


## Draws a placed label: a dark box with a colour edge, one line per row, and a thin
## leader back to its node when it had to step away.
func _tag_box(l: Dictionary) -> void:
	var rect: Rect2 = l["rect"]
	var col: Color = l["col"]
	var f := Palette.mono()
	var fs: int = l["fs"]
	var pad: float = l["pad"]
	var near := Vector2(clampf(l["at"].x, rect.position.x, rect.end.x), clampf(l["at"].y, rect.position.y, rect.end.y))
	if near.distance_to(l["at"]) > float(l["r"]) + LABEL_GAP * _k() * 2.0:
		_c.draw_line(l["at"] + (near - l["at"]).normalized() * float(l["r"]), near, Color(col, 0.7), 1.0)
	_c.draw_rect(rect, Color(Palette.NIGHT_SKY, 0.86))
	_c.draw_rect(Rect2(rect.position, Vector2(2.0 * _k(), rect.size.y)), col)
	var y := rect.position.y + pad + f.get_ascent(fs)
	for line in l["lines"]:
		_c.draw_string(f, Vector2(rect.position.x + pad, y), line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.PAPER)
		y += f.get_height(fs)


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


# --- Icons ------------------------------------------------------------------------------

## Regular polygon (closed) of `sides` round `p`, radius `r`, first corner at `rot`.
static func _ngon(p: Vector2, r: float, sides: int, rot: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in sides + 1:
		var t := rot + TAU * k / sides
		pts.append(p + Vector2(cos(t), sin(t)) * r)
	return pts


## Star (closed) with `points` tips between radii `r_out` and `r_in`, a tip pointing up.
static func _star(p: Vector2, r_out: float, r_in: float, points: int) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in points * 2 + 1:
		var t := -PI * 0.5 + PI * k / points
		pts.append(p + Vector2(cos(t), sin(t)) * (r_out if k % 2 == 0 else r_in))
	return pts


## The silhouette of a node icon of `kind` (closed outline) round `p`, radius `r`. Each
## kind on a map has its own shape, so icons differ by more than their symbol.
static func icon_shape(kind: String, p: Vector2, r: float) -> PackedVector2Array:
	match kind:
		KIND_FIGHT, KIND_HEAT:
			return _ngon(p, r, 20, 0.0)
		KIND_ELITE:
			return _star(p, r * 1.1, r * 0.8, 8)
		KIND_SHOP, KIND_EXPLOIT:
			return _ngon(p, r * 1.15, 4, -PI * 0.5)
		KIND_EVENT:
			return _ngon(p, r * 1.2, 4, PI * 0.25)
		KIND_BOSS:
			return _star(p, r * 1.3, r * 0.72, 5)
		KIND_HOME:
			var s := r * 0.85
			return PackedVector2Array([p + Vector2(-s, s), p + Vector2(-s, -s * 0.2), p + Vector2(0, -s * 1.25),
				p + Vector2(s, -s * 0.2), p + Vector2(s, s), p + Vector2(-s, s)])
	return _ngon(p, r, 6, PI / 6.0)


## Draws a node icon (H21 #14): a dark silhouette of the kind's shape edged in `col`, and
## the kind's symbol; unknown kinds show `text` (the node's glyph) in a hexagon. Shared
## with MapLegend so the key shows exactly what the map draws. `alpha` dims it.
static func draw_icon(ci: CanvasItem, kind: String, p: Vector2, r: float, col: Color, text: String = "", alpha: float = 1.0) -> void:
	var shape := icon_shape(kind, p, r)
	var ink := Color(0, 0, 0, 0.85 * alpha)
	var edge := Color(col, alpha)
	var w := maxf(1.5, r * 0.13)
	ci.draw_colored_polygon(shape, Color(Palette.NIGHT_SKY, 0.94 * alpha))
	ci.draw_polyline(shape, ink, w + 3.0, true)
	ci.draw_polyline(shape, edge, w, true)
	var f := Palette.mono()
	match kind:
		KIND_FIGHT, KIND_ELITE:
			# Crossed blades with their guards.
			var s := r * 0.5
			for dir: Vector2 in [Vector2(1, 1), Vector2(-1, 1)]:
				ci.draw_line(p - dir * s, p + dir * s, edge, w)
				var g := p + dir * s * 0.55
				var perp := Vector2(-dir.y, dir.x) * s * 0.35
				ci.draw_line(g - perp, g + perp, edge, w)
		KIND_SHOP:
			_icon_text(ci, f, "$", p, r, edge)
		KIND_EVENT:
			_icon_text(ci, f, "?", p, r, edge)
		KIND_RACK:
			# Three server blades with a status light each.
			var bw := r * 1.0
			var bh := r * 0.26
			for k in 3:
				var y := p.y + (k - 1) * bh * 1.5 - bh * 0.5
				ci.draw_rect(Rect2(p.x - bw * 0.5, y, bw, bh), edge, false, maxf(1.0, w * 0.7))
				ci.draw_circle(Vector2(p.x + bw * 0.3, y + bh * 0.5), bh * 0.3, edge)
		KIND_BOSS:
			ci.draw_colored_polygon(_star(p, r * 0.55, r * 0.25, 5), edge)
		KIND_EXPLOIT:
			ci.draw_colored_polygon(_ngon(p, r * 0.5, 4, -PI * 0.5), edge)
		KIND_HEAT:
			# A snowflake: three bars with a tick at each end.
			for a in 3:
				var dir := Vector2.from_angle(PI * 0.5 + PI * a / 3.0) * r * 0.62
				ci.draw_line(p - dir, p + dir, edge, w)
				for end_p: Vector2 in [p - dir, p + dir]:
					var back := (p - end_p).normalized() * r * 0.22
					var side := Vector2(-back.y, back.x)
					ci.draw_line(end_p + back, end_p + back * 0.2 + side, edge, maxf(1.0, w * 0.7))
					ci.draw_line(end_p + back, end_p + back * 0.2 - side, edge, maxf(1.0, w * 0.7))
		KIND_HOME:
			var s := r * 0.3
			ci.draw_rect(Rect2(p.x - s * 0.6, p.y + r * 0.85 - s * 2.0, s * 1.2, s * 2.0), edge)
		_:
			if text != "":
				_icon_text(ci, f, text, p, r, edge)


static func _icon_text(ci: CanvasItem, f: Font, text: String, p: Vector2, r: float, col: Color) -> void:
	var fs := maxi(1, roundi(r * (1.25 if text.length() == 1 else 0.95)))
	var y := p.y + (f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	ci.draw_string(f, Vector2(p.x - r, y), text, HORIZONTAL_ALIGNMENT_CENTER, r * 2.0, fs, col)
