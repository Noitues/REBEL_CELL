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
## H24 K4: the pointer moved onto node `id` (&"" when it left every node), so a screen can
## light the matching row of its list.
signal node_hovered(id: StringName)

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
## ANIM-R1 M4: a placed defence's marker on its node (screen px radius), and the chevrons
## on threat routes (edges with "arrows"): their spacing and half-size (screen px).
const ASSET_ICON := 9.0
const ARROW_STEP := 34.0
const ARROW_SIZE := 6.0
## ANIM-R1 M15: the most dashes drawn along one route segment.
const DASHES_MAX := 400
## ANIM-5: dashes crawl at `route_crawl`'s amplitude px per its duration (toward the
## edge's b end: threat routes run entry -> home); packets run PACKET_SHARE times faster.
const CRAWL_MOTION := &"route_crawl"
const PACKET_SHARE := 3.0
## Selection ring round the selected icon: its gap beyond the icon (screen px); it breathes
## by `select_ring_pulse` (ANIM-R1: amplitude px over one period, from the motion table).
const SELECT_RING := 6.0
const PULSE_MOTION := &"select_ring_pulse"

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
## Plain names of the kinds (tooltips built here when a node has no tip; translated where
## the tip is built, ANIM-R4 H7).
const KIND_NAMES := {KIND_FIGHT: "Router: a fight", KIND_ELITE: "Elite Router: a harder fight", # TR
	KIND_SHOP: "Modem: the cyber shop", KIND_EVENT: "Terminal: an event with choices", # TR
	KIND_RACK: "Server Rack: the Site's guardian", KIND_BOSS: "Boss Site: the corporation's core", # TR
	KIND_EXPLOIT: "Exploit Site", KIND_HEAT: "Heat reduction Site", KIND_HOME: "Your home Site (CORE)", # TR
	KIND_TIER: "Site"} # TR
## ANIM-R4 H7: the hover text's own sentences, translated once where the tip is built (they
## showed in English in every language). Each takes the words noted.
const TIP_NAMED := "%s: %s." # TR
const TIP_ONE := "%s." # TR
const TIP_CLAIMED := "Claimed: part of your network." # TR
const TIP_SEIZED := "Seized by the corporation." # TR
const TIP_ELITE := "Elite: a harder fight." # TR
const TIP_HERE := "You are here." # TR
const TIP_NEXT := "You can move here now." # TR
const TIP_OUT := "Out of reach from here." # TR
const TIP_RAID := "Raid: %s." # TR
const TIP_THREATS := "Threats here: %s." # TR
## H24 K5: each kind's icon is a silhouette and a symbol, and no two kinds share either
## silhouette or both (the Modem shop was the Exploit's diamond, the Heat reduction Site
## ICE's snowflake). A symbol named like a StatIcon is drawn by StatIcon, so a map icon
## and the tag for the same thing match (the Exploit's diamond, the shop's bag).
const KIND_SHAPES := {KIND_FIGHT: "circle", KIND_ELITE: "star8", KIND_SHOP: "tag", KIND_EVENT: "square",
	KIND_RACK: "tower", KIND_BOSS: "star5", KIND_EXPLOIT: "diamond", KIND_HEAT: "drop", KIND_HOME: "house",
	KIND_TIER: "hexagon"}
const KIND_SYMBOLS := {KIND_FIGHT: "crossed_blades", KIND_ELITE: "crossed_blades", KIND_SHOP: "shop",
	KIND_EVENT: "question", KIND_RACK: "server_blades", KIND_BOSS: "star", KIND_EXPLOIT: "exploits",
	KIND_HEAT: "cooling", KIND_HOME: "door", KIND_TIER: "tier_number"}
## H23 #6: the one word naming each kind (it leads every node tooltip).
const KIND_WORDS := {KIND_FIGHT: "Router", KIND_ELITE: "Elite Router", KIND_SHOP: "Modem", KIND_EVENT: "Terminal", # TR
	KIND_RACK: "Server Rack", KIND_BOSS: "Boss", KIND_EXPLOIT: "Exploit", KIND_HEAT: "Heat reduction", # TR
	KIND_HOME: "CORE", KIND_TIER: "Site"} # TR
## Icon radius on screen (px, undoing the city's zoom), for normal and big nodes, and
## how far above the roof the icon floats (px, local).
const ICON_RADIUS := 13.0
const ICON_RADIUS_BIG := 17.0
const ICON_LIFT := 10.0
## Clearance between two icons (screen px), and how many steps an icon may float up to
## clear the icons in front of it (H24 K6: trying the columns beside its stalk at each).
const ICON_SPACING := 3.0
const ICON_STACK_MAX := 4
## H24 K6: the columns an icon may shift to at each height (in icon widths, in this
## order; sideways first keeps a crowd low, so a raid map still fits its frame), and how
## high it may float at the last (a free spot is always found well before).
const ICON_FAN: Array[int] = [0, 1, -1]
const ICON_STACK_LIMIT := 32
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
const HERE_LABEL := "YOU ARE HERE" # TR
## Unreachable route nodes are drawn at this opacity.
const DIM_ALPHA := 0.3
## The "you are here" pin: size (screen px) and the ring around the icon (px beyond it).
const HERE_PIN := 9.0
const HERE_RING := 5.0
## Threat markers over a node: half-height and spacing (screen px).
const MARKER_SIZE := 9.0
const MARKER_STEP := 16.0
## H24 K4: the lit node's ring, beyond the selection ring (screen px), and its ticks.
const HOVER_RING := 4.0
const HOVER_TICK := 6.0
## Smallest city zoom the screen-size maths accepts.
const MIN_ZOOM := 0.1
## H22: labels keep this far inside the visible map area (screen px).
const EDGE_MARGIN := 4.0
## How far past a blocked area's edge a label moved out of it lands (local px).
const SHIFT_CLEARANCE := 1.0
## H23 #2: the furthest a label may sit from its node's centre (its nearest point, screen
## px); a label with no spot that near is left out (the node keeps its tooltip).
const LABEL_REACH := 110.0
## ANIM-R1 M13: the close search round a node with no free spot on the rings: directions
## tried, and the step outwards (screen px) up to LABEL_REACH.
const SEARCH_ANGLES := 16
const SEARCH_STEP := 6.0
## ANIM-R1 M13: a focus label with no room goes one word a line, at most this many lines.
const WORD_LINES_MAX := 3
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
		var changed := v != selected_id
		selected_id = v
		if changed and v != &"":
			_draw_on_selection()
		queue_redraw()
## ANIM-5 (4.14): the selected node's roof outline drawn so far (0..1, `site_outline_draw`)
## and its ring's ease in (0..1, `select_ring_ease`; the "you are here" ring too).
var select_reveal: float:
	get:
		return _mv.value(&"select_reveal")
	set(v):
		_mv.put(&"select_reveal", v)
var ring_ease: float:
	get:
		return _mv.value(&"ring_ease")
	set(v):
		_mv.put(&"ring_ease", v)
## ANIM-R2 R9: the values this map's motion tweens (a tween step redraws only its layer).
var _mv := MotionValues.new({&"select_reveal": 1.0, &"ring_ease": 1.0, &"drop_t": 1.0, &"drop_stamp_t": 1.0, &"travel_t": 1.0, &"arrive_t": 1.0, &"dim_t": 1.0, &"change_t": 1.0, &"road_t": 1.0})
## ANIM-5: an asset landing on a node (`drop_asset`): {"site", "index"} and its fall (0..1).
var _drop: Dictionary = {}
var drop_t: float:
	get:
		return _mv.value(&"drop_t")
	set(v):
		_mv.put(&"drop_t", v)
## ANIM-5 (4.16): a netrun move playing (`travel`): {"from", "to"}, the light pulse along
## the link (0..1), the new node's pop (0..1) and the old node's dim (0..1).
var _travel: Dictionary = {}
var travel_t: float:
	get:
		return _mv.value(&"travel_t")
	set(v):
		_mv.put(&"travel_t", v)
var arrive_t: float:
	get:
		return _mv.value(&"arrive_t")
	set(v):
		_mv.put(&"arrive_t", v)
var dim_t: float:
	get:
		return _mv.value(&"dim_t")
	set(v):
		_mv.put(&"dim_t", v)
var _travel_tween: Tween = null
## The move's light trail: this many fading dots, each this share of the link behind.
const TRAVEL_TRAIL := 8
## ANIM-R2 R12: the trail's width (screen px).
const TRAVEL_WIDTH := 7.0
## ANIM-R1 M7: a visited route node's tick (screen px).
const TICK := 11.0
const TRAVEL_TRAIL_STEP := 0.04
## H24 K4: a node lit from outside the map (its row in a list is hovered or has the pad's
## focus): a paper ring with ticks round its icon, and its label shown first.
var hover_id: StringName = &"":
	set(v):
		if v == hover_id:
			return
		hover_id = v
		if _top != null:
			_queue_tags()
			_hi.queue_redraw()
## The node under the pointer (for `node_hovered`).
var _pointer_id: StringName = &""
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
var _tags: Control
var _hi: Control
## The canvas item the helpers draw on (self, _anim, _top or _hi).
var _c: CanvasItem
## H22: the part of the viewport the map shows through (viewport px; a zero size means
## the overlay's own rect), and the screen areas labels keep out of: rects (viewport px)
## and controls read at each layout (a screen's side column).
var screen_rect: Rect2 = Rect2():
	set(v):
		screen_rect = v
		if _tags != null:
			_queue_tags()
## The tier pips of the last node draw (node id -> tier), for checks.
var drawn_tiers: Dictionary = {}
## ANIM-5: false while a RaidFxLayer draws the threats itself (moving along the streets).
var draw_markers: bool = true
## ANIM-R5 P8: the radius (screen px at scale 1) of the raid's threat tokens standing on the
## marker rows (RaidFxLayer sets it; 0: the map's own small markers): labels keep off them.
var token_radius: float = 0.0
## ANIM-R5 P7: the bright packets running along the Cell's links; off once a raid's verdict
## is in (they kept running toward CORE after "Raid over" and on the report).
var packets: bool = true
var _blocked_rects: Array[Rect2] = []
var _blocked_controls: Array[Control] = []


func _init(p_city: NeonCity = null) -> void:
	# ANIM-R4 H7: the hover text is translated where it is built (tip_of); shown as given.
	tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	city = p_city
	_c = self
	mouse_filter = Control.MOUSE_FILTER_PASS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_anim = _layer("Flow", _draw_anim)
	_top = _layer("Nodes", _draw_top)
	# ANIM-R2 R9: the labels are a layer of their own (a column sliding in moves them every
	# frame; the nodes under them stay drawn).
	_tags = _layer("Labels", _draw_tags)
	_hi = _layer("Selection", _draw_hi)
	add_child(_mv)
	_mv.changed.connect(_on_motion_value)
	if city != null:
		city.rebuilt.connect(_relayout)
		city.marks_changed.connect(_on_marks_changed)
	# Labels follow the text size live (redrawn once per change, never per frame).
	Settings.changed.connect(_queue_top)


## ANIM-R3 B6: the city's territory marks changed: their rings (this layer) and their
## stamps (the top layer) redraw.
func _on_marks_changed() -> void:
	queue_redraw()
	if _hi != null:
		_hi.queue_redraw()


## ANIM-R2 R9: a motion value changed: only the layer that draws it redraws (the selection's
## draw-on and ring and the move's pulse on the selection layer; a landing asset, a node's
## pop and the node left dimming on the node layer).
func _on_motion_value(key: StringName) -> void:
	if _hi == null:
		return
	match key:
		&"drop_t", &"drop_stamp_t", &"arrive_t", &"dim_t":
			_queue_top()
		&"change_t":
			_hi.queue_redraw()
	_hi.queue_redraw()


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


## The word naming node kind `kind` (KIND_WORDS; "" for an unknown kind), translated
## (H24 K7).
static func kind_word(kind: String) -> String:
	var w := String(KIND_WORDS.get(kind, ""))
	return tr_word(w) if w != "" else ""


## H24 K7: `text` through the TranslationServer once (static code has no Node.tr). Words
## drawn with draw_string are never translated by a Label, so they come through here.
static func tr_word(text: String) -> String:
	return String(TranslationServer.translate(text))


## H24 K7: a Site's tier as the maps say it ("T2"): the letter translates, the number and
## the pips carry it for any reader.
static func tier_text(tier: int) -> String:
	return tr_word("T%d") % tier


## H24 K5: node kind `kind`'s icon identity, "<silhouette>/<symbol>" ("" when unknown).
static func icon_id(kind: String) -> String:
	if not KIND_SHAPES.has(kind):
		return ""
	return "%s/%s" % [KIND_SHAPES[kind], KIND_SYMBOLS[kind]]


func _layer(layer_name: String, painter: Callable) -> Control:
	var c := Control.new()
	c.name = layer_name
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	c.draw.connect(painter)
	add_child(c)
	return c


func _process(delta: float) -> void:
	if _drop.get("waiting", false):
		var ready: Callable = _drop.get("ready", Callable())
		if not ready.is_valid() or bool(ready.call()) or Time.get_ticks_msec() - int(_drop["since"]) > Motion.seconds(DROP_WAIT_MOTION) * 1000.0:
			_start_drop()
	if not Fx.effects_enabled() or not is_visible_in_tree():
		return
	# The map's own motion runs at the playout's speed (Motion.speed: 1x outside a raid).
	anim_t += delta * Motion.speed
	_anim.queue_redraw()
	if selected_id != &"" or not _travel.is_empty():
		_hi.queue_redraw()


func set_graph(p_nodes: Array[Dictionary], p_edges: Array[Dictionary]) -> void:
	nodes = p_nodes
	edges = p_edges
	_graph_serial += 1
	_relayout()


func set_look(value: int) -> void:
	look = value
	queue_redraw()


## H22: screen areas the map labels keep out of, in viewport px (e.g. a panel over the
## map). Replaces the previous rects.
func set_blocked_rects(rects: Array[Rect2]) -> void:
	_blocked_rects = rects.duplicate()
	_queue_tags()


## H22: controls over the map (a screen's side column) the labels keep out of; their
## on-screen rects are read at each layout, and the labels move when they do.
func avoid_controls(controls: Array[Control]) -> void:
	_blocked_controls = controls.duplicate()
	for c in _blocked_controls:
		if is_instance_valid(c) and not c.item_rect_changed.is_connected(_queue_tags):
			c.item_rect_changed.connect(_queue_tags)
	_queue_tags()


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


## ANIM-R6 C10: true when node `id` is on this map (it has a lot).
func has_site(id: StringName) -> bool:
	return _lots.has(id)


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


## ANIM-R3 B8: where the "you are here" marker stands when no node is "here" (grid lots:
## the street before a route's first node; INF: none). The marker is always drawn.
var here_at: Vector2 = Vector2.INF:
	set(v):
		here_at = v
		_queue_top()


## ANIM-R3 B8: the "you are here" marker's position (local px; INF when not shown): on the
## node that is "here", else at `here_at`.
func here_point() -> Vector2:
	var id := here_id()
	if id != &"":
		return icon_at(id)
	if here_at.x == INF or city == null:
		return Vector2(INF, INF)
	# ANIM-R6 C15: on the street itself (the nearest street lot to `here_at`: the marker stood
	# on a block beside the road).
	var lot := Vector2i(floori(here_at.x), floori(here_at.y))
	if not city.is_street(lot.x, lot.y):
		lot = _door(lot)
	return grid_point_local(Vector2(lot) + Vector2(0.5, 0.5))


## ANIM-R3 B8: the street marker's box (screen px, for fitting the route); [] when the
## marker is on a node.
func here_marker_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	if here_id() != &"" or here_at.x == INF or not is_inside_tree():
		return out
	var p := here_point()
	if p.x == INF:
		return out
	var xf := get_global_transform()
	var r := (ICON_RADIUS + HERE_RING + HERE_PIN * 2.0) * _k()
	out.append(Rect2(xf * (p - Vector2(r, r)), Vector2(r, r) * 2.0 * xf.get_scale()))
	return out


## True when node `id` is on a route graph and can no longer be reached (drawn dimmed).
func is_dimmed(id: StringName) -> bool:
	return not _reach.is_empty() and not _reach.has(id) and not is_visited(id)


## ANIM-R1 M7: a route node already passed through ("visited" on its node): drawn at the
## `visited_dim` share with a tick, apart from the nodes that can no longer be reached.
func is_visited(id: StringName) -> bool:
	return bool(_node_dict(id).get("visited", false))


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


## ANIM-R2 R1: the graph given last (a count) and what the last layout was worked out from
## (the graph and the city's placement): a redraw that changes neither (a camera move over
## a baked city, its image landing) keeps the lots and routes and only redraws.
var _graph_serial: int = 0
var _layout_sig: Array = []
var _drawn_stamp: Array = []


func _relayout() -> void:
	if city != null:
		var sig := [_graph_serial, city.placement_sig()]
		if sig == _layout_sig:
			# Only a new frame (the camera moved) needs a redraw; an image landing does not.
			var stamp := city.frame_stamp()
			if stamp != _drawn_stamp:
				_drawn_stamp = stamp
				queue_redraw()
			return
		_drawn_stamp = city.frame_stamp()
		_layout_sig = sig
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


## ANIM-R2 R1: street routes worked out so far, by the city's placement and the two lots
## (view memory; a baked city's routes never change with its camera). Emptied past
## ROUTE_MEMO_MAX.
static var _route_memo: Dictionary = {}
const ROUTE_MEMO_MAX := 4096


## Street route between two buildings: door -> BFS over street lots -> door, as grid
## points (lot centres). Falls back to an L-shaped path if the search fails.
func _route(a: Vector2i, b: Vector2i) -> PackedVector2Array:
	var key := [_layout_sig[1] if _layout_sig.size() > 1 else "", a, b]
	var known: Variant = _route_memo.get(key)
	if known != null:
		return known
	if _route_memo.size() >= ROUTE_MEMO_MAX:
		_route_memo.clear()
	var pts := _street_route(a, b)
	_route_memo[key] = pts
	return pts


func _street_route(a: Vector2i, b: Vector2i) -> PackedVector2Array:
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
	if event is InputEventMouseMotion:
		_point_at(node_at(event.position))
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var id := node_at(event.position)
		if id != &"":
			node_clicked.emit(id)
			accept_event()


func _notification(what: int) -> void:
	if what == NOTIFICATION_MOUSE_EXIT:
		_point_at(&"")


## H24 K4: the pointer is over node `id` now: tell the screen when that changes.
func _point_at(id: StringName) -> void:
	if id != _pointer_id:
		_pointer_id = id
		node_hovered.emit(id)


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
		var kind_key := String(KIND_NAMES.get(String(n.get("kind", "")), ""))
		var kind_text := tr_word(kind_key) if kind_key != "" else ""
		if name_text != "" and kind_text != "":
			tip = tr_word(TIP_NAMED) % [name_text, kind_text]
		elif name_text != "" or kind_text != "":
			tip = tr_word(TIP_ONE) % (name_text if name_text != "" else kind_text)
		else:
			tip = String(n.get("glyph", String(id)))
		match String(n.get("mark", "")):
			MARK_SPRAY:
				tip += " " + tr_word(TIP_CLAIMED)
			MARK_CROSS:
				tip += " " + tr_word(TIP_SEIZED)
	parts.append(tip)
	var elite := tr_word(TIP_ELITE)
	if String(n.get("kind", "")) == KIND_ELITE and not tip.contains(elite.get_slice(":", 0)):
		parts.append(elite)
	if n.get("here", false):
		parts.append(tr_word(TIP_HERE))
	elif n.get("next", false):
		parts.append(tr_word(TIP_NEXT))
	elif is_dimmed(id):
		parts.append(tr_word(TIP_OUT))
	if n.has("result"):
		parts.append(tr_word(TIP_RAID) % String(n["result"]))
	if markers.has(id):
		parts.append(tr_word(TIP_THREATS) % ", ".join(markers[id]))
	return "\n".join(parts)


func _node_dict(id: StringName) -> Dictionary:
	for n in nodes:
		if n["id"] == id:
			return n
	return {}


func _roof(id: StringName) -> Dictionary:
	if city == null:
		return {}
	# ANIM-R2 R9: the roofs under the current frame are worked out once per frame change.
	_frame_cache()
	var rec: Variant = _roofs_now.get(id)
	if rec == null:
		var lot := lot_of(id)
		rec = city.roof_of(lot.x, lot.y)
		_roofs_now[id] = rec
	return rec


## ANIM-R2 R9: what the roofs, icons and labels on screen were worked out for (the look, the
## zoom, the city's frame and placement, the graph); the roofs under it (id -> the
## roof_of record, filled as asked) and the label layout's own key and result.
var _frame_key: Array = []
var _roofs_now: Dictionary = {}
var _labels_key: Array = []
var _labels_now: Array[Dictionary] = []


## Drops the roofs, icons and labels worked out for another frame (ANIM-R2 R9: they were
## worked out again on every call, ~15 ms a node pass and 100-300 ms a label pass).
func _frame_cache() -> void:
	var key := [look, city.scale.x, city.frame_stamp(), _layout_sig, nodes.size(), _lots.size()]
	if key != _frame_key:
		_frame_key = key
		_roofs_now = {}
		_icon_key = ""
		_labels_key = []


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


## The box node `n`'s icon covers round centre `p` (local px): its silhouette and, for a
## Site, its tier pips under it (H24 K6: the pips of one icon sat on the icon below).
func _icon_box(n: Dictionary, p: Vector2) -> Rect2:
	var r := icon_radius(n)
	var shape := icon_shape(String(n.get("kind", "")), p, r)
	var box := Rect2(p - Vector2(r, r), Vector2(r, r) * 2.0)
	for q in shape:
		box = box.expand(q)
	if tier_of(n) > 0:
		var s := _pip_scale(n)
		var pips := tier_pips_size(s)
		box = box.merge(Rect2(p + Vector2(-pips.x * 0.5, r + (TIER_PIP_GAP + TIER_PIP) * s - pips.y * 0.5), pips))
	return box


## H24 K6: the rect node `n`'s icon and tier pips cover as placed (local px).
func icon_rect(n: Dictionary) -> Rect2:
	var p := icon_pos(n)
	return _icon_box(n, p) if p.x != INF else Rect2()


## Every node's icon position (id -> local px), cached per camera and look. Icons are
## placed front to back (nearest roof first, ties by id); one whose box (icon and pips)
## would touch an icon already placed takes (H24 K6) the first free spot of the columns
## beside its stalk (ICON_FAN) at its height, then a step higher (its stalk grows), up to
## ICON_STACK_MAX steps, and at the last floats higher in its own column: no two icons
## ever overlap.
func _icon_positions() -> Dictionary:
	if city == null or nodes.is_empty():
		return {}
	_frame_cache()
	var key := "placed"
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
	var placed: Array[Rect2] = []
	var gap := ICON_SPACING * _k()
	for o in order:
		var n: Dictionary = o["n"]
		var r := icon_radius(n)
		var big: bool = n.get("big", false)
		var base: Vector2 = o["top"] + Vector2(0, -((PILLAR_HEIGHT_BIG if big else PILLAR_HEIGHT) if look == Look.PILLARS else ICON_LIFT + r))
		var own := _icon_box(n, base).size + Vector2(gap, gap)
		var p := base
		var found := false
		for level in ICON_STACK_MAX:
			for col in ICON_FAN:
				p = base + Vector2(col * own.x, -level * own.y)
				if _box_free(_icon_box(n, p), placed, gap):
					found = true
					break
			if found:
				break
		if not found:
			for level in range(ICON_STACK_MAX, ICON_STACK_LIMIT):
				p = base + Vector2(0, -level * own.y)
				if _box_free(_icon_box(n, p), placed, gap):
					break
		placed.append(_icon_box(n, p))
		out[n["id"]] = p
	_icon_key = key
	_icon_cache = out
	return out


static func _box_free(box: Rect2, placed: Array[Rect2], gap: float) -> bool:
	var grown := box.grow(gap * 0.5)
	for q in placed:
		if grown.intersects(q.grow(gap * 0.5)):
			return false
	return true


## Static under-layer: the look's veil and every route's keyline and glow. Any redraw of
## the overlay also refreshes the layers above it.
func _draw() -> void:
	_queue_top()
	_anim.queue_redraw()
	_hi.queue_redraw()
	if city == null or nodes.is_empty():
		return
	_c = self
	match look:
		Look.ISOLATE:
			draw_rect(Rect2(-size, size * 3.0), Color(0.02, 0.02, 0.04, 0.62))
		Look.XRAY:
			draw_rect(Rect2(-size, size * 3.0), Color(0.0, 0.03, 0.05, 0.72))
		Look.BLUEPRINT:
			draw_rect(Rect2(-size, size * 3.0), Color(0.02, 0.1, 0.32, 0.55))
		Look.SPOTLIGHT:
			_spotlight()
	for k in edges.size():
		_edge_static(edges[k], _route_px(k))
	# ANIM-R1 M5: a territory change's marks (outline, tint, CLAIMED / SEIZED stamp) show on
	# the map too, over its dimming and under its nodes. ANIM-R3 B6: their stamps draw on the
	# top layer, over the labels (a label hid CLAIMED).
	city.draw_marks_on(self, true, false)


## Flowing dashes and packets (redrawn every frame unless reduce-effects).
func _draw_anim() -> void:
	if city == null or nodes.is_empty():
		return
	_c = _anim
	for k in edges.size():
		_edge_flow(edges[k], _route_px(k))
	_c = self


## ANIM-R2 R1 / R9: the node layer draws at most once a process frame. A screen's first
## frame moved its column and key many times over (each container sort asked again), and
## each ask drew every node and label anew (8 draws, ~130 ms, in the Grid's first frame); a
## later ask in the same frame is drawn at the start of the next.
var _top_frame: int = -1
var _top_later: bool = false


func _queue_top() -> void:
	if _top == null:
		return
	_queue_tags()
	if _top_frame != Engine.get_process_frames() or not is_inside_tree():
		_top.queue_redraw()
		return
	if not _top_later:
		_top_later = true
		# A method, never a lambda: a lambda using self keeps a raw pointer to this overlay, and
		# a one-shot slot on the tree's process_frame is dropped before the emission calls it, so
		# an overlay freed earlier in that emission (a test's free(), a scene switch) had its
		# lambda run on freed memory (the bake crash, DECISIONS "Animation pass - bake crash").
		get_tree().process_frame.connect(_redraw_top_later, CONNECT_ONE_SHOT)


func _redraw_top_later() -> void:
	_top_later = false
	if is_instance_valid(_top):
		_top.queue_redraw()


## ANIM-R2 R9: the labels too draw at most once a process frame (a page's first frame
## moved the column and key several times, each a new layout).
var _tags_frame: int = -1
var _tags_later: bool = false


func _queue_tags() -> void:
	if _tags == null:
		return
	if _tags_frame != Engine.get_process_frames() or not is_inside_tree():
		_tags.queue_redraw()
		return
	if not _tags_later:
		_tags_later = true
		get_tree().process_frame.connect(_redraw_tags_later, CONNECT_ONE_SHOT)  # a method (see _queue_top)


func _redraw_tags_later() -> void:
	_tags_later = false
	if is_instance_valid(_tags):
		_tags.queue_redraw()


## Nodes, marks, badges, tags, assets and threat markers.
func _draw_top() -> void:
	_top_frame = Engine.get_process_frames()
	if city == null or nodes.is_empty():
		return
	_c = _top
	drawn_tiers.clear()
	for n in nodes:
		_node(n)
	# ANIM-R3 B8: before the route's first node the marker stands at the street, with its words.
	if here_id() == &"" and here_at.x != INF and _travel.is_empty():
		var p := here_point()
		if p.x != INF:
			_here(p, ICON_RADIUS * _k())
			var f := Palette.mono()
			var fs := label_font_size()
			var word := tr_word(HERE_LABEL)
			var w := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			var at := p + Vector2(-w * 0.5, (ICON_RADIUS + HERE_RING + LABEL_GAP) * _k() + f.get_ascent(fs))
			_c.draw_rect(Rect2(at - Vector2(TAG_PAD * _k(), f.get_ascent(fs) + TAG_PAD * _k()), Vector2(w, f.get_height(fs)) + Vector2(TAG_PAD, TAG_PAD) * 2.0 * _k()), Color(Palette.NIGHT_SKY, 0.86))
			_c.draw_string(f, at, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.CELL_PINK)
	_c = self


## The labels (ANIM-R2 R9: a layer of their own over the nodes).
func _draw_tags() -> void:
	if city == null or nodes.is_empty():
		return
	_tags_frame = Engine.get_process_frames()
	_c = _tags
	for l: Dictionary in _layout_labels():
		_tag_box(l)
	_c = self


## The selected node's pulsing ring, and (H24 K4) the lit node's ticked ring; (ANIM-5) a
## netrun move's light pulse and the travelling "you are here" marker.
func _draw_hi() -> void:
	if not _travel.is_empty() and travel_t < 1.0:
		_draw_travel()
	if road_t < 1.0 and drop_stamp_t > 0.0:
		_draw_road()
	elif change_t < 1.0 and drop_stamp_t > 0.0:
		_draw_changes()
	if city != null:
		# ANIM-R4 H11d: the stamps keep off the labels and icons (the Site's name stays read).
		if not city.marks.is_empty():
			city.stamp_avoid = stamp_avoid_rects()
		city.draw_marks_on(_hi, false, true)
	# The selected node's roof outline, drawing on (ANIM-5; ANIM-R2 R9: on this layer).
	if city != null and selected_id != &"" and _lots.has(selected_id):
		var rec := _roof(selected_id)
		if not rec.is_empty():
			var closed: PackedVector2Array = (rec["roof"] as PackedVector2Array).duplicate()
			closed.append(closed[0])
			var c0 := _c
			_c = _hi
			_stroke_on(closed, select_reveal, Palette.CELL_ACID, 1.5)
			_c = c0
	var hc := hover_centre()
	if hc.x != INF:
		var k := _k()
		var hn := _node_dict(hover_id)
		var hr := (icon_radius(hn) if not hn.is_empty() else ICON_RADIUS * k) + (SELECT_RING + pulse_amplitude() + HOVER_RING) * k
		_hi.draw_arc(hc, hr, 0, TAU, 32, Color(0, 0, 0, 0.85), 5.0 * k)
		_hi.draw_arc(hc, hr, 0, TAU, 32, Palette.PAPER, 2.0 * k)
		for q in 4:
			var d := Vector2.from_angle(PI * 0.25 + q * PI * 0.5)
			_hi.draw_line(hc + d * hr, hc + d * (hr + HOVER_TICK * k), Palette.PAPER, 2.0 * k)
	var at := ring_centre()
	if at.x == INF:
		return
	var grow := lerpf(Motion.amplitude(&"select_ring_ease"), 1.0, ring_ease)
	_hi.draw_arc(at, ring_radius() * grow + (sin(anim_t * TAU / maxf(Motion.entry(PULSE_MOTION).duration, 0.001)) - 1.0) * pulse_amplitude() * _k(), 0, TAU, 32, Color(Palette.CELL_ACID, ring_ease), 2.0 * _k())


## ANIM-R3 B5: the forecast numbers a drop changed rise off their nodes ("25 > 30": green
## when it got better, pink when worse), over the labels, fading over their last third.
func _draw_changes() -> void:
	var k := _k()
	var f := Palette.display()
	var fs := maxi(1, roundi(CHANGE_FONT * Settings.text_scale * k))
	var u := change_t
	var e := Motion.entry(CHANGE_MOTION)
	var rise := Motion.amplitude(CHANGE_MOTION) * k * (float(Tween.interpolate_value(0.0, 1.0, u, 1.0, e.trans, e.ease)) if e != null else u)
	var a := clampf((1.0 - u) / change_fade_share(), 0.0, 1.0)
	# ANIM-R5 P8: a caption over the numbers says they are the raid forecast changing ("45 →
	# 50 ▲" over CORE read as its HP).
	var cf := Palette.mono()
	var cfs := maxi(1, roundi(CHANGE_CAPTION_FONT * Settings.text_scale * k))
	var caption := tr_word(CHANGE_CAPTION)
	for ch: Dictionary in _drop.get("changes", []):
		var p := icon_at(StringName(ch["site"]))
		if p.x == INF:
			continue
		var better := int(ch["to"]) >= int(ch["from"])
		var col := Palette.CELL_ACID if better else Palette.CELL_PINK
		var text := change_text(int(ch["from"]), int(ch["to"]))
		var tw := f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs)
		var cw := cf.get_string_size(caption, HORIZONTAL_ALIGNMENT_LEFT, -1, cfs)
		var size := Vector2(maxf(tw.x, cw.x), tw.y + cf.get_height(cfs)) + Vector2(TAG_PAD, TAG_PAD) * 2.0 * k
		var at := p + Vector2(-size.x * 0.5, -ICON_RADIUS_BIG * k - LABEL_GAP * k - size.y - rise)
		var box := Rect2(at, size)
		_hi.draw_rect(box.grow(2.0 * k), Color(0, 0, 0, 0.85 * a))
		_hi.draw_rect(box, Color(Palette.NIGHT_SKY, 0.95 * a))
		_hi.draw_rect(box, Color(col, a), false, 2.0 * k)
		_hi.draw_string(cf, at + Vector2(TAG_PAD * k, TAG_PAD * k + cf.get_ascent(cfs)), caption, HORIZONTAL_ALIGNMENT_LEFT, -1, cfs, Color(Palette.PAPER, 0.85 * a))
		_hi.draw_string(f, at + Vector2(TAG_PAD * k, TAG_PAD * k + cf.get_height(cfs) + f.get_ascent(fs)), text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(col, a))


## ANIM-R5 P8: the forecast change's caption and its lettering (px at text scale 1.0).
const CHANGE_CAPTION := "RAID FORECAST" # TR
const CHANGE_CAPTION_FONT := 11


## ANIM-R5 P8: the forecast change's caption as drawn (translated; tests).
func change_caption() -> String:
	return tr_word(CHANGE_CAPTION)


## The selection ring's breathing (screen px): `select_ring_pulse`'s amplitude, 0 when that
## entry is off (ANIM-R1 M3: the end state, a still ring).
func pulse_amplitude() -> float:
	var e := Motion.entry(PULSE_MOTION)
	return e.amplitude if e != null and e.enabled else 0.0


## Centre of the lit node's ring (H24 K4), or INF when no node is lit.
func hover_centre() -> Vector2:
	if city == null or hover_id == &"" or not _lots.has(hover_id):
		return Vector2(INF, INF)
	return _icon_positions().get(hover_id, Vector2(INF, INF))


## Centre of the selection ring (the selected node's icon), or INF when none shows.
func ring_centre() -> Vector2:
	if city == null or selected_id == &"" or not _lots.has(selected_id):
		return Vector2(INF, INF)
	return _icon_positions().get(selected_id, Vector2(INF, INF))


## Outer radius of the pulsing selection ring (local px): round the icon, clear of it.
func ring_radius() -> float:
	var n := _node_dict(selected_id)
	return (icon_radius(n) if not n.is_empty() else ICON_RADIUS * _k()) + (SELECT_RING + pulse_amplitude()) * _k()


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
		var phase := fmod(anim_t * crawl_speed(), DASH_PERIOD) if e.get("flow", true) else 0.0
		for k in pts.size() - 1:
			var a := pts[k]
			var b := pts[k + 1]
			var length := a.distance_to(b)
			var dir := (b - a) / maxf(length, 0.001)
			# ANIM-R1 M15: a bounded count of dashes (a segment measured mid-layout can be
			# huge or not finite).
			if not is_finite(length):
				continue
			for q in mini(DASHES_MAX, ceili(maxf(0.0, length - phase) / DASH_PERIOD)):
				var t := phase + q * DASH_PERIOD
				_c.draw_line(a + dir * t, a + dir * minf(t + DASH_ON, length), col, width)
	if e.get("arrows", false):
		_chevrons(e, pts)
	if _is_dashed(e):
		return
	elif e.get("flow", false) and packets and crawl_speed() > 0.0:
		# A bright packet running along the route.
		var total := 0.0
		for k in pts.size() - 1:
			total += pts[k].distance_to(pts[k + 1])
		var d := fmod(anim_t * crawl_speed() * PACKET_SHARE, maxf(total, 1.0))
		for k in pts.size() - 1:
			var seg := pts[k].distance_to(pts[k + 1])
			if d <= seg:
				_c.draw_circle(pts[k].lerp(pts[k + 1], d / maxf(seg, 0.001)), width + 2.0, Palette.PAPER)
				break
			d -= seg


## ANIM-R1 M4: chevrons along a threat route pointing the way the threats go (a -> b), in
## a dark keyline, crawling with the dashes: an enemy path reads apart from the Cell's
## solid links at any zoom.
func _chevrons(e: Dictionary, pts: PackedVector2Array) -> void:
	var k := _k()
	var col: Color = e.get("color", Palette.NET_CYAN)
	var step := ARROW_STEP * k
	var s := ARROW_SIZE * k
	var phase := fmod(anim_t * crawl_speed(), step) if e.get("flow", true) else 0.0
	var carry := phase
	for q in pts.size() - 1:
		var a := pts[q]
		var b := pts[q + 1]
		var length := a.distance_to(b)
		if not is_finite(length) or length <= 0.0:
			continue
		var dir := (b - a) / length
		var side := dir.orthogonal()
		var n := mini(DASHES_MAX, ceili(maxf(0.0, length - carry) / step))
		for i in n:
			var p := a + dir * (carry + i * step)
			var tip := p + dir * s
			var wing := PackedVector2Array([p - dir * s + side * s, tip, p - dir * s - side * s])
			_c.draw_polyline(wing, Color(0, 0, 0, 0.8), 4.5 * k)
			_c.draw_polyline(wing, col, 2.2 * k)
		# Where the next chevron falls on the next segment (the spacing runs on round corners).
		carry = maxf(0.0, carry + n * step - length)


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
	var visited := is_visited(n["id"])
	if not _travel.is_empty() and n["id"] == _travel["from"]:
		# ANIM-5 (4.16): the node left behind dims as a visited one.
		col = Color(col, col.a * lerpf(1.0, Motion.amplitude(&"visited_dim"), dim_t))
	elif visited:
		col = Color(col, col.a * Motion.amplitude(&"visited_dim"))
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
	if _travel.is_empty():
		if n.get("here", false):
			_here(at, r)
	elif n["id"] == _travel["to"] and travel_t >= 1.0:
		# ANIM-5 (4.16): the new node pops up with the marker on it.
		r *= lerpf(Motion.amplitude(&"node_pop"), 1.0, arrive_t)
		_here(at, r)
	draw_icon(_c, String(n.get("kind", "")), at, r, col, String(n.get("glyph", "")), DIM_ALPHA if dim else 1.0)
	if visited or (not _travel.is_empty() and n["id"] == _travel["from"] and dim_t > 0.0):
		# ANIM-R1 M7: a tick on a node passed through (it fades in as the node dims).
		var ta := 1.0 if visited else dim_t
		var tk := _k()
		var t0 := at + Vector2(r * 0.55, r * 0.35)
		var tick := PackedVector2Array([t0, t0 + Vector2(TICK * 0.35, TICK * 0.4) * tk, t0 + Vector2(TICK, -TICK * 0.55) * tk])
		_c.draw_polyline(tick, Color(0, 0, 0, 0.9 * ta), 5.0 * tk)
		_c.draw_polyline(tick, Color(Palette.PAPER, ta), 2.5 * tk)
	if tier_of(n) > 0:
		draw_tier(_c, tier_pips_centre(n), tier_of(n), col, _pip_scale(n), DIM_ALPHA if dim else 1.0)
		drawn_tiers[n["id"]] = tier_of(n)
	var assets: Array = n.get("assets", [])
	for k in assets.size():
		var slot := asset_slot(n, k, assets.size())
		var ar := ASSET_ICON * _k()
		var landing: bool = not _drop.is_empty() and _drop["site"] == n["id"] and int(_drop["index"]) == k
		if landing and _drop.get("waiting", false):
			continue  # ANIM-R2 R6: it drops once the camera has panned there
		if landing and drop_t < 1.0:
			# ANIM-5: falling onto its node. ANIM-R2 R6: a bigger stamp ring as it lands.
			# ANIM-R3 B5: a longer fall, from `asset_drop_grow` x its size (it was nearly
			# invisible).
			slot.y -= (1.0 - drop_t) * Motion.amplitude(&"asset_drop") * _k()
			ar *= lerpf(maxf(1.0, Motion.amplitude(GROW_MOTION)), 1.0, drop_t)
		if landing and drop_stamp_t < 1.0 and drop_t >= 1.0:
			var grow := lerpf(1.0, Motion.amplitude(&"asset_drop_stamp"), drop_stamp_t)
			var fade := 1.0 - drop_stamp_t
			_c.draw_circle(slot, ar * 1.25 * grow, Color(Palette.CELL_PINK, 0.35 * fade))
			_c.draw_arc(slot, ar * 1.25 * grow, 0, TAU, 28, Color(0, 0, 0, 0.8 * fade), 7.0 * _k())
			_c.draw_arc(slot, ar * 1.25 * grow, 0, TAU, 28, Color(Palette.PAPER, fade), 4.0 * _k())
		# ANIM-R1 M4: the placed defence stays on its node as a marker the size of a map
		# icon (a dark plate, a pink ring, the asset's own icon), readable at any zoom.
		_c.draw_circle(slot, ar * 1.25, Color(0, 0, 0, 0.85))
		_c.draw_arc(slot, ar * 1.25, 0, TAU, 20, Palette.CELL_PINK, 2.0 * _k())
		AssetIcon.draw_icon(_c, slot, ar, assets[k])
		if landing and String(_drop.get("label", "")) != "":
			# ANIM-R2 R6: the defence that just landed keeps its name under it.
			var f := Palette.mono()
			var fs := label_font_size()
			var word: String = str(_drop["label"])
			var w := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			var lab_at := slot + Vector2(-w * 0.5, ar * 1.25 + LABEL_GAP * _k() + f.get_ascent(fs))
			_c.draw_rect(Rect2(lab_at - Vector2(TAG_PAD * _k(), f.get_ascent(fs) + TAG_PAD * _k()), Vector2(w, f.get_height(fs)) + Vector2(TAG_PAD, TAG_PAD) * 2.0 * _k()), Color(Palette.NIGHT_SKY, 0.86))
			_c.draw_string(f, lab_at, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, AssetIcon.color_of(assets[k]))
	if draw_markers and markers.has(n["id"]):
		var names: Array = markers[n["id"]]
		var row := _marker_row(n)
		for k in names.size():
			var mp := row + Vector2((k - (names.size() - 1) * 0.5) * MARKER_STEP * _k(), 0)
			var s := MARKER_SIZE * _k()
			var dia := PackedVector2Array([mp + Vector2(0, -s), mp + Vector2(s * 0.9, 0), mp + Vector2(0, s), mp + Vector2(-s * 0.9, 0)])
			_c.draw_colored_polygon(dia, Palette.corp_color(StringName(n.get("threat_corp", "solace"))) if n.has("threat_corp") else Palette.CORP_SOLACE)
			_c.draw_polyline(dia + PackedVector2Array([dia[0]]), Palette.PAPER, 1.2)


## ANIM-R1 M4: where placed asset `k` of `count` on node `n` sits (local px): a row
## beside the icon, on its right, screen-sized.
func asset_slot(n: Dictionary, k: int, count: int) -> Vector2:
	var step := ASSET_ICON * 2.8 * _k()
	var at := icon_pos(n) + Vector2(icon_radius(n) + ASSET_ICON * 1.6 * _k(), 0)
	return at + Vector2(step * k, 0)


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


# --- Motion hooks (Animation pass ANIM-5) -----------------------------------------------------

## Where node `id`'s icon sits now (local px; INF when the node is not on this map).
func icon_at(id: StringName) -> Vector2:
	return _icon_positions().get(id, Vector2(INF, INF))


## Where threat `k` of `count` standing on node `id` is drawn (local px): the marker row
## over its icon (INF when the node is not on this map).
func marker_slot(id: StringName, k: int, count: int) -> Vector2:
	var n := _node_dict(id)
	if n.is_empty() or icon_at(id).x == INF:
		return Vector2(INF, INF)
	return _marker_row(n) + Vector2((k - (count - 1) * 0.5) * MARKER_STEP * _k(), 0)


## The street route from node `a` to node `b` (grid points): the map's own edge route
## when the two are linked (reversed when it runs b -> a), else a street route between
## their buildings; empty when either is not on this map.
func route_between(a: StringName, b: StringName) -> PackedVector2Array:
	for k in edges.size():
		if k >= _routes.size():
			break
		if edges[k]["a"] == a and edges[k]["b"] == b:
			return _routes[k]
		if edges[k]["a"] == b and edges[k]["b"] == a:
			var back := _routes[k].duplicate()
			back.reverse()
			return back
	if city == null or not _lots.has(a) or not _lots.has(b):
		return PackedVector2Array()
	return _route(_lots[a], _lots[b])


## Grid point `p` in this overlay's local px (under the city's current camera).
func grid_point_local(p: Vector2) -> Vector2:
	return _to_local(p) if city != null else p


## Local px per screen px (the city's zoom undone): motion sizes are screen px x this.
func screen_k() -> float:
	return _k()


## ANIM-5: dash crawl speed (local px per second): `route_crawl`'s amplitude per duration.
## ANIM-R6 C4: 0 when the crawl doesn't play (switched off, reduce effects): the dashes and
## chevrons stand still and no packet runs.
func crawl_speed() -> float:
	var e := Motion.entry(CRAWL_MOTION)
	if e == null or not Motion.live(CRAWL_MOTION):
		return 0.0
	return e.amplitude / maxf(e.duration, 0.001)


## ANIM-5 (4.14): the selected node's roof outline draws on and its ring eases in (the
## end state at once when motion doesn't play).
func _draw_on_selection() -> void:
	if not is_inside_tree():
		select_reveal = 1.0
		ring_ease = 1.0
		return
	select_reveal = 0.0
	ring_ease = 0.0
	Motion.run(&"site_outline_draw", _mv, ^"select_reveal", 1.0)
	Motion.run(&"select_ring_ease", _mv, ^"ring_ease", 1.0)


## ANIM-5: eases the selection / "you are here" ring in again (a screen that just opened).
func ease_rings() -> void:
	if not is_inside_tree():
		return
	ring_ease = 0.0
	Motion.run(&"select_ring_ease", _mv, ^"ring_ease", 1.0)


## ANIM-5 (4.14): a raid asset lands on node `site_id` (the last asset in its list) with a
## stamp. The hook drag-and-drop deploying calls once the asset is placed.
## ANIM-R2 R6: `ready` (optional) says when the screen's camera has settled: the drop waits
## for it (a camera pan at the same time hid it), at most `asset_drop_wait`; `label`
## names the defence under its marker once it has landed (it stays).
## ANIM-R3 B5: `changes` ([{"site", "from", "to"}]) are the forecast numbers the drop
## changed: once it has landed each shows "25 > 30" rising off its node (`forecast_change`).
## ANIM-R4 H11b: `road` (Site ids from the defence's node to CORE, the way threats come)
## carries a pulse from the node to CORE once the defence lands; the forecast numbers it
## changed rise when the pulse arrives (the drop and the forecast read as cause and effect).
func drop_asset(site_id: StringName, ready: Callable = Callable(), label: String = "", changes: Array = [], road: Array = []) -> void:
	var n := _node_dict(site_id)
	var count := (n.get("assets", []) as Array).size()
	if n.is_empty() or count == 0:
		return
	_drop = {"site": site_id, "index": count - 1, "label": label, "changes": changes, "road": road}
	drop_t = 0.0
	drop_stamp_t = 0.0
	change_t = 1.0
	road_t = 1.0
	if not is_inside_tree() or not Motion.live(&"asset_drop"):
		drop_t = 1.0
		drop_stamp_t = 1.0
		_queue_top()
		return
	if not changes.is_empty() and Motion.live(CHANGE_MOTION):
		change_t = 0.0
		if road.size() > 1 and Motion.live(ROAD_MOTION):
			road_t = 0.0
	if ready.is_valid() and not bool(ready.call()):
		_drop["waiting"] = true
		_drop["ready"] = ready
		_drop["since"] = Time.get_ticks_msec()
		_queue_top()
		return
	_start_drop()


## ANIM-R3 B9: the most a drop waits for the camera (its duration, seconds).
const DROP_WAIT_MOTION := &"asset_drop_wait"
## ANIM-R3 B5: the forecast change after a drop, and the landing's size.
const CHANGE_MOTION := &"forecast_change"
const GROW_MOTION := &"asset_drop_grow"
## The forecast change's lettering at text scale 1.0 (px).
const CHANGE_FONT := 20
## ANIM-R4 H9: the share of its time the forecast change spends fading out, from the motion
## table (`forecast_change_fade`'s amplitude; it was CHANGE_FADE_SHARE, 1/3 inline).
const CHANGE_FADE_MOTION := &"forecast_change_fade"
## ANIM-R4 H11b: the pulse along the threat road from the new defence to CORE, and its
## lettering-free look: the dot's radius and the lit road's width (px x screen_k).
const ROAD_MOTION := &"forecast_road_pulse"
const ROAD_DOT := 7.0
const ROAD_WIDTH := 4.0
var road_t: float:
	get:
		return _mv.value(&"road_t")
	set(v):
		_mv.put(&"road_t", v)


## ANIM-R4 H9: the share of the forecast change's time spent fading (0..1).
static func change_fade_share() -> float:
	return clampf(Motion.amplitude(CHANGE_FADE_MOTION), 0.01, 1.0)


## ANIM-R4 H11b: a forecast change as the screens write it: "45 → 50 ▲" (a gain), "50 → 45 ▼"
## (a loss), "45 → 45" (none).
static func change_text(from: int, to: int) -> String:
	return "%d → %d%s" % [from, to, " ▲" if to > from else (" ▼" if to < from else "")]


## ANIM-R4 H11b: the drop's road to CORE in local px (the streets between its Sites).
func road_points() -> PackedVector2Array:
	var road: Array = _drop.get("road", [])
	var pts := PackedVector2Array()
	for i in road.size():
		var at := icon_at(StringName(road[i]))
		if at.x == INF:
			return PackedVector2Array()
		if i > 0:
			for p in route_between(StringName(road[i - 1]), StringName(road[i])):
				pts.append(_to_local(p))
		pts.append(at)
	return pts


## ANIM-R4 H11b: the pulse on its way to CORE: the road lit behind it, the dot at its head.
func _draw_road() -> void:
	var pts := road_points()
	if pts.size() < 2:
		return
	var k := _k()
	var e := Motion.entry(ROAD_MOTION)
	var u: float = float(Tween.interpolate_value(0.0, 1.0, clampf(road_t, 0.0, 1.0), 1.0, e.trans, e.ease)) if e != null else road_t
	var tail := maxf(0.0, u - Motion.amplitude(ROAD_MOTION))
	var lit := PackedVector2Array()
	var steps := 16
	for i in steps + 1:
		lit.append(_along(pts, lerpf(tail, u, float(i) / steps)))
	_hi.draw_polyline(lit, Color(0, 0, 0, 0.7), (ROAD_WIDTH + 3.0) * k, true)
	_hi.draw_polyline(lit, Color(Palette.CELL_ACID, 0.9), ROAD_WIDTH * k, true)
	var head := _along(pts, u)
	_hi.draw_circle(head, (ROAD_DOT + 2.0) * k, Color(0, 0, 0, 0.8))
	_hi.draw_circle(head, ROAD_DOT * k, Palette.CELL_ACID)
	_hi.draw_circle(head, ROAD_DOT * 0.45 * k, Palette.PAPER)


var change_t: float:
	get:
		return _mv.value(&"change_t")
	set(v):
		_mv.put(&"change_t", v)


## ANIM-R3 B5: the forecast changes the last drop shows ([{"site", "from", "to"}]; tests).
func drop_changes() -> Array:
	return _drop.get("changes", [])
var drop_stamp_t: float:
	get:
		return _mv.value(&"drop_stamp_t")
	set(v):
		_mv.put(&"drop_stamp_t", v)


func _start_drop() -> void:
	_drop.erase("waiting")
	_drop.erase("ready")
	var tw := Motion.run(&"asset_drop", _mv, ^"drop_t", 1.0)
	if tw == null:
		drop_stamp_t = 1.0
		return
	tw.finished.connect(_on_dropped_down)


## The drop has landed: the stamp rings out and the forecast numbers it changed rise.
func _on_dropped_down() -> void:
	if not is_instance_valid(_mv):
		return
	if Motion.run(&"asset_drop_stamp", _mv, ^"drop_stamp_t", 1.0) == null:
		drop_stamp_t = 1.0
	if road_t < 1.0:
		# ANIM-R4 H11b: the pulse runs the road to CORE first, then the numbers rise.
		var tw := Motion.run(ROAD_MOTION, _mv, ^"road_t", 1.0)
		if tw != null:
			tw.finished.connect(_start_change)
			return
		road_t = 1.0
	_start_change()


func _start_change() -> void:
	if not is_instance_valid(_mv):
		return
	if change_t < 1.0 and Motion.run(CHANGE_MOTION, _mv, ^"change_t", 1.0) == null:
		change_t = 1.0


## True while a dropped defence waits for the camera (tests).
func drop_waiting() -> bool:
	return bool(_drop.get("waiting", false))


## ANIM-5 (4.16): the netrun moves from node `from` to node `to`: a light pulse runs the
## link with the "you are here" marker, the new node pops up, the old one dims. Returns
## the seconds it takes (0 when motion doesn't play: the end state at once).
func travel(from: StringName, to: StringName, on_land: Callable = Callable()) -> float:
	_travel = {"from": from, "to": to}
	_on_land = on_land
	travel_t = 1.0
	arrive_t = 1.0
	dim_t = 1.0
	if not is_inside_tree() or not Motion.live(&"route_pulse") or icon_at(to).x == INF:
		_land()
		queue_redraw()
		return 0.0
	travel_t = 0.0 if icon_at(from).x != INF else 1.0
	arrive_t = 0.0
	dim_t = 0.0
	var pulse := Motion.run(&"route_pulse", _mv, ^"travel_t", 1.0) if travel_t < 1.0 else null
	var lead := Motion.seconds(&"route_pulse") + Motion.delay_of(&"route_pulse") if pulse != null else 0.0
	var pop := create_tween()
	pop.tween_interval(lead)
	pop.tween_callback(func() -> void:
		_land()
		Motion.run(&"node_pop", _mv, ^"arrive_t", 1.0)
		Motion.run(&"visited_dim", _mv, ^"dim_t", 1.0))
	_travel_tween = pop
	queue_redraw()
	return lead + maxf(Motion.seconds(&"node_pop") + Motion.delay_of(&"node_pop"), Motion.seconds(&"visited_dim") + Motion.delay_of(&"visited_dim"))


## ANIM-R1 M7: what the screen does when the pulse lands (the route's new state: the choice
## labels move to the new next nodes); once per move.
var _on_land: Callable = Callable()


func _land() -> void:
	var cb := _on_land
	_on_land = Callable()
	if cb.is_valid():
		cb.call()


## Jumps a running move to its end (input skips it).
func finish_travel() -> void:
	_land()
	if _travel_tween != null and _travel_tween.is_valid():
		_travel_tween.kill()
	Motion.stop(self)
	Motion.stop(_mv)
	travel_t = 1.0
	arrive_t = 1.0
	dim_t = 1.0
	queue_redraw()


## Where the "you are here" marker is now (local px): on its way along the link while a
## move plays, else over the node it stands on (INF when none).
func here_marker_pos() -> Vector2:
	if not _travel.is_empty():
		if travel_t < 1.0:
			return _travel_point(travel_t)
		return icon_at(_travel["to"])
	return icon_at(here_id()) if here_id() != &"" else Vector2(INF, INF)


## The point `u` (0..1, eased by route_pulse) along the move's street route (local px).
func _travel_point(u: float) -> Vector2:
	var pts := _travel_route()
	if pts.size() < 2 or pts[0].x == INF:
		return icon_at(_travel["to"])
	var e := Motion.entry(&"route_pulse")
	var k: float = float(Tween.interpolate_value(0.0, 1.0, clampf(u, 0.0, 1.0), 1.0, e.trans, e.ease)) if e != null else u
	return _along(pts, k)


func _travel_route() -> PackedVector2Array:
	var pts := PackedVector2Array([icon_at(_travel["from"])])
	for p in route_between(_travel["from"], _travel["to"]):
		pts.append(_to_local(p))
	pts.append(icon_at(_travel["to"]))
	return pts


static func _along(pts: PackedVector2Array, u: float) -> Vector2:
	var total := 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	var d := u * total
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if d <= seg:
			return pts[i].lerp(pts[i + 1], d / maxf(seg, 0.001))
		d -= seg
	return pts[pts.size() - 1]


## The move's light pulse (a bright head with a fading trail along the link) and the
## marker riding it.
func _draw_travel() -> void:
	var pts := _travel_route()
	if pts.size() < 2 or pts[0].x == INF:
		return
	var k := _k()
	var head := _travel_point(travel_t)
	# ANIM-R2 R12: the node it heads for pulses (`route_target_pulse`) while it travels.
	var to := icon_at(_travel["to"])
	if to.x != INF:
		var period := maxf(Motion.seconds(&"route_target_pulse"), 0.001)
		var swell := (0.5 + 0.5 * sin(anim_t * TAU / period)) * Motion.amplitude(&"route_target_pulse")
		var tr_r := icon_radius(_node_dict(_travel["to"])) + (SELECT_RING + swell) * k
		_hi.draw_arc(to, tr_r, 0, TAU, 32, Color(0, 0, 0, 0.8), 6.0 * k)
		_hi.draw_arc(to, tr_r, 0, TAU, 32, Palette.CELL_ACID, 3.0 * k)
	# ANIM-R2 R12: a thick, bright trail along the street behind the head (it was a row of
	# small dots), a dark keyline under it.
	var trail := PackedVector2Array()
	for q in TRAVEL_TRAIL + 1:
		trail.append(_travel_point(maxf(0.0, travel_t - (TRAVEL_TRAIL - q) * TRAVEL_TRAIL_STEP)))
	_hi.draw_polyline(trail, Color(0, 0, 0, 0.8), TRAVEL_WIDTH * 2.0 * k, true)
	_hi.draw_polyline(trail, Color(Palette.CELL_ACID, 0.9), TRAVEL_WIDTH * k, true)
	_hi.draw_polyline(trail, Palette.PAPER, TRAVEL_WIDTH * 0.35 * k, true)
	_hi.draw_circle(head, TRAVEL_WIDTH * 1.1 * k, Palette.CELL_ACID)
	_hi.draw_circle(head, TRAVEL_WIDTH * 0.6 * k, Palette.PAPER)
	var c0 := _c
	_c = _hi
	_here(head, ICON_RADIUS * k)
	_c = c0


## Draws closed polyline `pts` from its start up to `share` (0..1) of its length, with a
## bright head while it is drawing (the stroke reveal).
func _stroke_on(pts: PackedVector2Array, share: float, col: Color, width: float) -> void:
	if share >= 1.0:
		_c.draw_polyline(pts, col, width, true)
		return
	var total := 0.0
	for i in pts.size() - 1:
		total += pts[i].distance_to(pts[i + 1])
	var left := clampf(share, 0.0, 1.0) * total
	var drawn := PackedVector2Array([pts[0]])
	for i in pts.size() - 1:
		var seg := pts[i].distance_to(pts[i + 1])
		if left <= seg:
			drawn.append(pts[i].lerp(pts[i + 1], left / maxf(seg, 0.001)))
			break
		drawn.append(pts[i + 1])
		left -= seg
	if drawn.size() >= 2:
		_c.draw_polyline(drawn, Color(col, 0.35), width * 4.0, true)
		_c.draw_polyline(drawn, col, width * 1.6, true)
		_c.draw_circle(drawn[drawn.size() - 1], width * 2.5, Palette.PAPER)


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


## H24 K1 (checks): the nodes with a label to show, on the visible map, that were left
## out although a spot near them (on one line or two) is free of every placed label, icon,
## pip row and the rings. The layout never does that; a Site with no label had no room.
func unplaced_with_room() -> Array[StringName]:
	var out: Array[StringName] = []
	if city == null or nodes.is_empty():
		return out
	var placed := _layout_labels()
	var got := {}
	for l: Dictionary in placed:
		got[l["key"]] = true
	var f := Palette.mono()
	var fs := label_font_size()
	var pad := TAG_PAD * _k()
	var line_h := f.get_height(fs)
	var icons: Array[Dictionary] = []
	var marks: Array[Rect2] = []
	for n in nodes:
		if not _roof(n["id"]).is_empty():
			icons.append({"id": n["id"], "at": icon_pos(n), "r": icon_radius(n)})
			if tier_of(n) > 0:
				marks.append(tier_pips_rect(n))
	var obstacles := {"icons": icons, "marks": marks, "placed": placed, "ring_c": ring_centre(), "ring_r": ring_radius(),
		"area": label_area(), "blocks": label_blocks()}
	for n in nodes:
		var lines := label_lines(n["id"])
		if lines.is_empty() or got.has(String(n["id"])) or _roof(n["id"]).is_empty():
			continue
		var t := {"at": icon_pos(n), "r": icon_radius(n)}
		if not _visible_at(t["at"], obstacles["area"], obstacles["blocks"]):
			continue
		for v: PackedStringArray in [lines, wrap_lines(lines)]:
			if _free_spot(t, _label_box(v, f, fs, pad, line_h), obstacles).size != Vector2.ZERO:
				out.append(n["id"])
				break
	return out


## The labels drawn now: node id -> Rect2 (local px). Threat tags are keyed "<id>#threats".
## ANIM-R4 H11d: the rects a territory stamp keeps clear of, in the city's local px: every
## node label and icon body.
func stamp_avoid_rects() -> Array[Rect2]:
	var out: Array[Rect2] = []
	var xf := get_transform()
	for r: Rect2 in label_rects().values():
		out.append(xf * r)
	var at := _icon_positions()
	for n in nodes:
		if at.has(n["id"]):
			var r := icon_radius(n)
			out.append(xf * Rect2(Vector2(at[n["id"]]) - Vector2(r, r), Vector2(r, r) * 2.0))
	return out


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
		# ANIM-R5 P12: translated once here (the lines are drawn as given).
		text = tr_word(HERE_LABEL)
	# H24 K4: a node lit from its list row shows its name even where the map shows none.
	if text == "" and id == hover_id:
		text = String(n.get("name", ""))
	if text != "":
		lines.append(text)
	if n.has("result"):
		lines.append(String(n["result"]))
	return lines


func _prio(n: Dictionary) -> int:
	if n["id"] == selected_id or n.get("here", false) or n["id"] == hover_id:
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
	if city == null or nodes.is_empty():
		return [] as Array[Dictionary]
	# ANIM-R2 R9: the layout is worked out again only when something it reads changed: the
	# frame (roofs and icons), the text size, the focus, the labels' words and priorities, the
	# threats, the area and the blocked rects, the ring.
	_frame_cache()
	var sig := []
	for n in nodes:
		sig.append([n["id"], label_lines(n["id"]), _prio(n)])
	var key := [Settings.text_scale, selected_id, hover_id, hash(sig), var_to_str(markers), label_area(), label_blocks(), ring_radius(), token_radius]
	if key == _labels_key:
		return _labels_now
	_labels_now = _place_labels()
	_labels_key = key
	return _labels_now


func _place_labels() -> Array[Dictionary]:
	var placed: Array[Dictionary] = []
	var f := Palette.mono()
	var fs := label_font_size()
	var k := _k()
	var pad := TAG_PAD * k
	var line_h := f.get_height(fs)
	var icons: Array[Dictionary] = []
	var marks: Array[Rect2] = []
	var tok := token_radius * k
	for n in nodes:
		if not _roof(n["id"]).is_empty():
			icons.append({"id": n["id"], "at": icon_pos(n), "r": icon_radius(n)})
			if tier_of(n) > 0:
				marks.append(tier_pips_rect(n))
			# ANIM-R5 P8: a raid's threat tokens (RaidFxLayer: much bigger than the map's
			# markers) are obstacles too: no label (CORE's included) is placed under one.
			if tok > 0.0 and markers.has(n["id"]):
				var count := (markers[n["id"]] as Array).size()
				for i in count:
					var slot := marker_slot(n["id"], i, count)
					if slot.x != INF:
						marks.append(Rect2(slot - Vector2(tok, tok), Vector2(tok, tok) * 2.0))
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
			var half := maxf(MARKER_SIZE * k, tok)
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
		var obstacles := {"icons": icons, "marks": marks, "placed": placed, "ring_c": ring_c, "ring_r": ring_r, "area": area, "blocks": blocks}
		# H24 K1: a long name with no room on one line tries two (narrower) lines.
		var variants: Array[PackedStringArray] = [t["lines"]]
		var wrapped := wrap_lines(t["lines"])
		if wrapped != t["lines"]:
			variants.append(wrapped)
		var spot := Rect2()
		var box := Vector2.ZERO
		for lines: PackedStringArray in variants:
			box = _label_box(lines, f, fs, pad, line_h)
			spot = _free_spot(t, box, obstacles)
			if spot.size != Vector2.ZERO:
				t["lines"] = lines
				break
		if spot.size == Vector2.ZERO:
			# H22: focus labels (and the landmarks: CORE, the boss) move inward onto the
			# screen rather than off it or under a side column (H23 #2: never further than
			# LABEL_REACH from their node; H23 #4: never onto another label).
			if t["prio"] != PRIO_FOCUS and not _node_dict(t["id"]).get("big", false):
				continue
			for lines: PackedStringArray in variants:
				box = _label_box(lines, f, fs, pad, line_h)
				spot = _inward_spot(t, box, obstacles, false)
				if spot.size == Vector2.ZERO:
					# ANIM-R1 M13: a closer look all round the node, within reach.
					spot = _search_spot(t, box, obstacles)
				if spot.size != Vector2.ZERO:
					t["lines"] = lines
					break
			if spot.size == Vector2.ZERO and t["prio"] == PRIO_FOCUS:
				# The last resort for a focus label: a spot clear of every label and every
				# other node's icon (ANIM-R1 M13: the selected Site's long name lay over other
				# nodes' icons in a late campaign at big text); only "you are here" may then
				# cover an icon (the route's marker label always shows). Else the label is
				# left out: the selected Site's card names it and its tooltip stays.
				# Narrower first: one word a line, then the name cut short ("Warehouse…").
				var tight: Array[PackedStringArray] = variants.duplicate()
				for v in [word_lines(t["lines"]), short_lines(t["lines"])]:
					if not tight.has(v):
						tight.append(v)
				for may_cover in [false, true]:
					if may_cover and not (bool(_node_dict(t["id"]).get("here", false)) or String(t["key"]).ends_with("#threats")):
						break
					for lines: PackedStringArray in tight:
						box = _label_box(lines, f, fs, pad, line_h)
						spot = _loose_spot(t, box, obstacles, may_cover)
						if spot.size != Vector2.ZERO:
							t["lines"] = lines
							break
					if spot.size != Vector2.ZERO:
						break
			if spot.size == Vector2.ZERO:
				continue
		t["rect"] = spot
		t["fs"] = fs
		t["pad"] = pad
		placed.append(t)
	return placed


## The size of a label of `lines` (local px).
static func _label_box(lines: PackedStringArray, f: Font, fs: int, pad: float, line_h: float) -> Vector2:
	var w := 0.0
	for line in lines:
		w = maxf(w, Palette.mono_for(line).get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x)
	return Vector2(w + pad * 2.0, line_h * lines.size() + pad * 2.0)


## H24 K1: `lines` with its first line broken in two at the space nearest its middle
## (unchanged when it has no space).
static func wrap_lines(lines: PackedStringArray) -> PackedStringArray:
	if lines.is_empty():
		return lines
	var text := lines[0]
	var best := -1
	for i in text.length():
		if text[i] == " " and (best < 0 or absi(i * 2 - text.length()) < absi(best * 2 - text.length())):
			best = i
	if best < 0:
		return lines
	var out := PackedStringArray([text.substr(0, best), text.substr(best + 1)])
	for k in range(1, lines.size()):
		out.append(lines[k])
	return out


## ANIM-R1 M13: `lines` with its first line one word a line (at most WORD_LINES_MAX lines
## for it; the rest stays on the last).
static func word_lines(lines: PackedStringArray) -> PackedStringArray:
	if lines.is_empty():
		return lines
	var words := lines[0].split(" ", false)
	var out := PackedStringArray()
	for i in words.size():
		if out.size() < WORD_LINES_MAX:
			out.append(words[i])
		else:
			out[out.size() - 1] += " " + words[i]
	for k in range(1, lines.size()):
		out.append(lines[k])
	return out


## ANIM-R1 M13: `lines` with its first line cut to its first word and an ellipsis (the
## whole name stays in the node's tooltip).
static func short_lines(lines: PackedStringArray) -> PackedStringArray:
	if lines.is_empty():
		return lines
	var words := lines[0].split(" ", false)
	if words.size() <= 1:
		return lines
	var out := PackedStringArray([words[0] + "…"])
	for k in range(1, lines.size()):
		out.append(lines[k])
	return out


## Candidate top-left corners for a `box` label around a centre `c` at distance `d`.
static func _spots(c: Vector2, d: float, box: Vector2) -> Array[Vector2]:
	return [Vector2(c.x + d, c.y - box.y * 0.5), Vector2(c.x - d - box.x, c.y - box.y * 0.5),
		Vector2(c.x - box.x * 0.5, c.y - d - box.y), Vector2(c.x - box.x * 0.5, c.y + d),
		Vector2(c.x + d * 0.7, c.y - d * 0.7 - box.y), Vector2(c.x - d * 0.7 - box.x, c.y - d * 0.7 - box.y),
		Vector2(c.x + d * 0.7, c.y + d * 0.7), Vector2(c.x - d * 0.7 - box.x, c.y + d * 0.7)]


## The first free spot for label `t` (Rect2 with a zero size when there is none): inside
## the label area, out of the blocked screen areas, clear of the obstacles.
func _free_spot(t: Dictionary, box: Vector2, obstacles: Dictionary) -> Rect2:
	var reach := LABEL_REACH * _k()
	for rect in _candidates(t, box):
		# H24 K1: no spot further than LABEL_REACH either (a two-line label's outer rings).
		if reach_of(rect, t["at"]) > reach:
			continue
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


## ANIM-R1 M13: a closer search for label `t`: SEARCH_ANGLES directions round its node at
## every SEARCH_STEP of distance out to LABEL_REACH, each spot moved inside the label area;
## the first clear of every obstacle (Rect2 with a zero size when none is).
func _search_spot(t: Dictionary, box: Vector2, obstacles: Dictionary) -> Rect2:
	var k := _k()
	var reach := LABEL_REACH * k
	var at: Vector2 = t["at"]
	var d: float = t["r"] + LABEL_GAP * k
	while d <= reach:
		for q in SEARCH_ANGLES:
			var dir := Vector2.from_angle(TAU * q / SEARCH_ANGLES)
			# The box's corner so its nearest edge faces the node at distance d.
			var c := at + dir * (d + (absf(dir.x) * box.x + absf(dir.y) * box.y) * 0.5)
			var rect := _shift_inside(Rect2(c - box * 0.5, box), obstacles["area"], obstacles["blocks"])
			if reach_of(rect, at) > reach or not _on_screen(rect, obstacles):
				continue
			if not _blocked(rect, obstacles):
				return rect
		d += SEARCH_STEP * k
	return Rect2()


## ANIM-R1 M13: a focus label's last resort: the first candidate (the near rings, then the
## close search) clear of every placed label and of every other node's icon; with
## `may_cover_icons`, clear of the labels only (H23 #4: never onto another label).
func _loose_spot(t: Dictionary, box: Vector2, obstacles: Dictionary, may_cover_icons: bool) -> Rect2:
	var k := _k()
	var reach := LABEL_REACH * k
	var at: Vector2 = t["at"]
	var tries: Array[Rect2] = []
	for rect in _candidates(t, box):
		tries.append(_shift_inside(rect, obstacles["area"], obstacles["blocks"]))
	var d: float = t["r"] + LABEL_GAP * k
	while d <= reach:
		for q in SEARCH_ANGLES:
			var dir := Vector2.from_angle(TAU * q / SEARCH_ANGLES)
			var c := at + dir * (d + (absf(dir.x) * box.x + absf(dir.y) * box.y) * 0.5)
			tries.append(_shift_inside(Rect2(c - box * 0.5, box), obstacles["area"], obstacles["blocks"]))
		d += SEARCH_STEP * k
	for rect in tries:
		if reach_of(rect, at) > reach or not _on_screen(rect, obstacles) or _hits_label(rect, obstacles):
			continue
		if may_cover_icons or not _hits_icon(rect, obstacles, t["id"]):
			return rect
	return Rect2()


## True when `rect` covers the icon of a node other than `own`.
static func _hits_icon(rect: Rect2, obstacles: Dictionary, own: StringName) -> bool:
	for ic: Dictionary in obstacles["icons"]:
		if ic["id"] != own and _rect_hits_disc(rect, ic["at"], ic["r"]):
			return true
	return false


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
		# ANIM-R4 H11b: a result line "50 → 40 HOLDS" draws its arrow from the fallback face.
		_c.draw_string(Palette.mono_for(line), Vector2(rect.position.x + pad, y), line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.PAPER)
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
			_c.draw_polyline(ring, Color(Palette.CELL_TURF, 0.95), 3.0, true)
			for d in SPRAY_DRIPS:
				var t := TAU * (0.15 + 0.2 * d) + float((seed_v >> (d * 4)) % 7) * 0.05
				var p := at + Vector2(cos(t), sin(t) * 0.55) * SPRAY_RADIUS
				var drip := SPRAY_DRIP_LEN * (0.6 + 0.4 * float((seed_v >> (d * 3)) % 5) / 4.0)
				_c.draw_line(p, p + Vector2(0, drip), Color(Palette.CELL_TURF, 0.85), 2.0)
				_c.draw_circle(p + Vector2(0, drip), 1.6, Color(Palette.CELL_TURF, 0.85))
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
		KIND_FIGHT:
			return _ngon(p, r, 20, 0.0)
		KIND_HEAT:
			# A drop (cooling), its point up (H24 K5).
			var d := PackedVector2Array([p + Vector2(0, -r * 1.25)])
			for k in 15:
				var t := -PI / 6.0 + (PI + PI / 3.0) * k / 14.0
				d.append(p + Vector2(0, r * 0.18) + Vector2(cos(t), sin(t)) * r * 0.92)
			d.append(p + Vector2(0, -r * 1.25))
			return d
		KIND_ELITE:
			return _star(p, r * 1.1, r * 0.8, 8)
		KIND_SHOP:
			# A price tag, its point left (H24 K5: the shop was the Exploit's diamond).
			return PackedVector2Array([p + Vector2(-r * 1.2, 0), p + Vector2(-r * 0.55, -r * 0.8), p + Vector2(r * 1.05, -r * 0.8),
				p + Vector2(r * 1.05, r * 0.8), p + Vector2(-r * 0.55, r * 0.8), p + Vector2(-r * 1.2, 0)])
		KIND_EXPLOIT:
			return _ngon(p, r * 1.15, 4, -PI * 0.5)
		KIND_RACK:
			# A server tower (H24 K5: it was the plain Site's hexagon).
			return PackedVector2Array([p + Vector2(-r * 0.75, -r * 1.1), p + Vector2(r * 0.75, -r * 1.1), p + Vector2(r * 0.75, r * 1.1),
				p + Vector2(-r * 0.75, r * 1.1), p + Vector2(-r * 0.75, -r * 1.1)])
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
	if KIND_SHAPES.has(kind):
		ci.set_meta(&"icon_id", icon_id(kind))  # the last map icon drawn on `ci` (checks)
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
			StatIcon.draw(ci, p + Vector2(r * 0.12, 0), r * 0.58, StatIcon.SHOP, edge)
			ci.draw_circle(p + Vector2(-r * 0.72, 0), maxf(1.0, r * 0.1), edge)  # the tag's hole
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
			StatIcon.draw(ci, p, r * 0.62, StatIcon.EXPLOITS, edge)
		KIND_HEAT:
			# Heat going down (H24 K5: the snowflake is ICE's icon on the top bar).
			StatIcon.draw(ci, p + Vector2(0, r * 0.2), r * 0.6, StatIcon.COOLING, edge)
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
