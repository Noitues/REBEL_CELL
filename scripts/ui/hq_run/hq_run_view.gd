class_name HqRunView
extends Control
## ART-8 8w: the HQ run's page on the city (bible 4.6 / 4.7, wave 2b): its own CityView3D
## framed on the corporation's compound (HqCompoundStage: the manifest's camera; DISPATCH's
## run in the round 43 Tokyo canyon), with the run drawn over it in the route's ink: the
## entry and "you are here", the links (walked a solid lime line, the live ones a crawling
## orange dash, the rest a white dash), the nodes as the route's vinyl stickers with their
## state rings, and the Central Server: the rack sticker, the red grease-pencil TARGET circle
## and the yellow `CENTRAL SERVER // <name>` chip clear of the pencil.
## Headless (no renderer) it draws the marks only, projected by the same camera, so the
## page's maths are testable. A view: it emits `node_pressed` and never changes game state.

## A selectable node was clicked (or pressed by its number).
signal node_pressed(id: StringName)

const CHIP_WORDS := "CENTRAL SERVER // %s" # TR
## The chip: gap above the pencil circle, padding, lettering (screen px at text scale 1.0)
## and its glass alpha.
const CHIP_GAP := 8.0
const CHIP_PAD := 6.0
const CHIP_FONT := 15
const CHIP_GLASS_ALPHA := 0.9
## The entry's mark: a small lime ring on the ground where the run comes in.
const ENTRY_RADIUS := 7.0
const ENTRY_WIDTH := 2.4
## A click reaches a node within its sticker plus this (screen px).
const PICK_SLACK := 6.0
## The page keeps every node and the entry this far inside its edges (screen px), widening
## the compound's reference framing up to FIT_MAX_SHARE times when it must.
const FIT_MARGIN_PX := 64.0
const FIT_MAX_SHARE := 2.0

var corp: StringName = &""
## The Central Server's name, translated and upper case (the Site's display name).
var server_label: String = ""
var graph: MapGraph = null
var current_id: StringName = &""
var visited: Array[StringName] = []
var available: Array[StringName] = []
## The city (null headless or before mount).
var city: CityView3D = null
## The camera the marks are projected with (the city's own when there is one).
var iso: CityIsoCamera = null
var anim_t: float = 0.0

var _layout: HqCompoundLayoutData = null
var _manifest: Dictionary = {}
var _at: Transform3D = Transform3D()
var _points: Dictionary = {}
var _entry: Vector3 = Vector3.ZERO
var _city_rect: TextureRect = null
var _marks: Control = null


func _init() -> void:
	name = "HqRunView"
	mouse_filter = Control.MOUSE_FILTER_STOP
	_city_rect = TextureRect.new()
	_city_rect.name = "City"
	_city_rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_city_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_city_rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	_city_rect.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_city_rect)
	_marks = Control.new()
	_marks.name = "Marks"
	_marks.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_marks.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_marks.draw.connect(_draw_marks)
	add_child(_marks)
	resized.connect(_on_resized)


## Shows run `graph` on `p_corp`'s compound: the walked, current and selectable nodes, and
## the Central Server named `p_server_label`.
func show_run(p_corp: StringName, p_graph: MapGraph, p_current: StringName, p_visited: Array[StringName],
		p_available: Array[StringName], p_server_label: String) -> void:
	corp = p_corp
	graph = p_graph
	current_id = p_current
	visited = p_visited.duplicate()
	available = p_available.duplicate()
	server_label = p_server_label
	_manifest = HqCompoundStage.manifest(corp)
	_layout = HqCompoundStage.layout(corp)
	_at = HqCompoundStage.place(CityView3D.CONFIG, corp, _manifest)
	_points = HqCompoundStage.node_points(_layout, graph, _at)
	_entry = HqCompoundStage.entry_point(_layout, _at)
	_frame()
	if CityView3D.can_render() and city == null:
		_mount_city()
	_marks.queue_redraw()


## The world point of node `id` (Vector3.INF when it has no slot).
func world_of(id: StringName) -> Vector3:
	return _points.get(id, Vector3.INF)


## The screen point (local) of node `id` (Vector2.INF when it has none).
func screen_of(id: StringName) -> Vector2:
	var w := world_of(id)
	return iso.project(w) if iso != null and w != Vector3.INF else Vector2.INF


## The entry's screen point (local).
func entry_screen() -> Vector2:
	return iso.project(_entry) if iso != null else Vector2.INF


## The sticker radius of node `id` (the Central Server's is the big one).
func node_radius(id: StringName) -> float:
	var big := graph != null and int(graph.get_node(id).get("layer", 0)) == graph.layer_count()
	return (RouteOverlay.STICKER_RADIUS_BIG if big else RouteOverlay.STICKER_RADIUS) * Settings.text_scale


## The state ring node `id` shows (RouteOverlay.STATE_*).
func state_of(id: StringName) -> String:
	if visited.has(id):
		return RouteOverlay.STATE_WALKED
	if available.has(id):
		return RouteOverlay.STATE_NEXT
	if current_id != &"" and graph != null and int(graph.get_node(id).get("layer", 0)) <= int(graph.get_node(current_id).get("layer", 0)):
		return RouteOverlay.STATE_CUT
	return RouteOverlay.STATE_LATER


## The links drawn: [{from, to, state}] where from/to are node ids (&"" = the entry) and state
## is "walked", "live" or "later"; in node-id order.
func links() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if graph == null:
		return out
	for id: StringName in graph.first_layer_ids():
		out.append({"from": &"", "to": id, "state": _link_state(&"", id)})
	var ids: Array[StringName] = []
	for n in graph.all_nodes():
		ids.append(n["id"])
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ids:
		var nexts: Array = graph.get_node(id).get("next", [])
		for to: StringName in nexts:
			out.append({"from": id, "to": to, "state": _link_state(id, to)})
	return out


func _link_state(from: StringName, to: StringName) -> String:
	var from_walked := from == &"" or visited.has(from)
	if from_walked and visited.has(to):
		return "walked"
	if from == current_id and available.has(to):
		return "live"
	return "later"


## The selectable node under local point `p` (&"" = none).
func node_at(p: Vector2) -> StringName:
	var best := &""
	var best_d := INF
	for id: StringName in available:
		var s := screen_of(id)
		if s == Vector2.INF:
			continue
		var d := s.distance_to(p)
		if d <= node_radius(id) + PICK_SLACK and d < best_d:
			best = id
			best_d = d
	return best


## The chip's rect (local) over the Central Server (Rect2() when there is none).
func chip_rect() -> Rect2:
	var id := _server_id()
	var at := screen_of(id) if id != &"" else Vector2.INF
	if at == Vector2.INF:
		return Rect2()
	var f := Palette.mono()
	var fs := maxi(1, roundi(CHIP_FONT * Settings.text_scale))
	var w := f.get_string_size(_chip_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	var box := Vector2(w, f.get_height(fs)) + Vector2(CHIP_PAD, CHIP_PAD) * 2.0
	var rr := node_radius(id) * RouteOverlay.TARGET_SHARE
	var r := Rect2(Vector2(at.x - box.x * 0.5, at.y - rr * RouteOverlay.TARGET_SQUASH - CHIP_GAP - box.y), box)
	r.position.x = clampf(r.position.x, 0.0, maxf(0.0, size.x - box.x))
	if r.position.y < 0.0:
		# No room above (the server near the top edge): under the circle, still clear of it.
		r.position.y = at.y + rr * RouteOverlay.TARGET_SQUASH + CHIP_GAP
	return r


func _chip_text() -> String:
	return tr(CHIP_WORDS) % server_label


func _server_id() -> StringName:
	if graph == null or graph.layer_count() < 1:
		return &""
	var last: Array = graph.nodes_in_layer(graph.layer_count())
	return StringName(last[0]["id"]) if not last.is_empty() else &""


func _frame() -> void:
	var sz := size if size.x > 1.0 and size.y > 1.0 else Vector2(1920, 1080)
	var pts: Array[Vector3] = [_entry]
	for id: StringName in _points:
		pts.append(_points[id])
	iso = HqCompoundStage.run_camera(CityView3D.CONFIG, _manifest, _at, sz, pts, FIT_MARGIN_PX, FIT_MAX_SHARE)
	if city != null:
		city.set_view_size(Vector2i(sz))
		city.set_iso(iso)


func _mount_city() -> void:
	city = CityView3D.new()
	city.name = "HqCity"
	city.set_iso(iso)
	city.stage_compound(corp)
	add_child(city)
	city.set_view_size(Vector2i(size.max(Vector2(2, 2))))
	_city_rect.texture = city.get_texture()
	move_child(city, 0)


func _on_resized() -> void:
	if not _manifest.is_empty():
		_frame()
	_marks.queue_redraw()


func _process(delta: float) -> void:
	if not is_visible_in_tree() or not Fx.effects_enabled():
		return
	anim_t += delta
	_marks.queue_redraw()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and (event as InputEventMouseButton).pressed \
			and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		var id := node_at((event as InputEventMouseButton).position)
		if id != &"":
			accept_event()
			node_pressed.emit(id)


func _get_tooltip(at_position: Vector2) -> String:
	var id := node_at(at_position)
	if id == &"":
		return ""
	return tr(CityMapOverlay.KIND_NAMES[CityMapOverlay.KIND_CENTRAL_SERVER]) if id == _server_id() else ""


# --- Drawing ----------------------------------------------------------------------------------

func _draw_marks() -> void:
	if iso == null or graph == null:
		return
	var k := Settings.text_scale
	var e := entry_screen()
	for l in links():
		var a := e if l["from"] == &"" else screen_of(l["from"])
		var b := screen_of(l["to"])
		if a == Vector2.INF or b == Vector2.INF:
			continue
		_link(a, b, String(l["state"]), k)
	_marks.draw_arc(e, ENTRY_RADIUS * k, 0.0, TAU, 24, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA), (ENTRY_WIDTH + RouteOverlay.KEYLINE_EXTRA) * k)
	_marks.draw_arc(e, ENTRY_RADIUS * k, 0.0, TAU, 24, RouteInk.RING_WALKED, ENTRY_WIDTH * k)
	var server := _server_id()
	for n in graph.all_nodes():
		var id: StringName = n["id"]
		var at := screen_of(id)
		if at == Vector2.INF:
			continue
		var kind := CityMapOverlay.KIND_RACK if id == server else CityMapOverlay.route_kind(int(n["type"]), bool(n["elite"]))
		RouteOverlay.draw_sticker(_marks, kind, at, node_radius(id), state_of(id), k)
	if server != &"" and screen_of(server) != Vector2.INF:
		_target(server, screen_of(server), node_radius(server), k)
		_chip(k)
	var here := screen_of(current_id) if current_id != &"" else e
	if here != Vector2.INF:
		_here(here, node_radius(current_id) if current_id != &"" else ENTRY_RADIUS * 2.0 * k, k)


func _link(a: Vector2, b: Vector2, state: String, k: float) -> void:
	match state:
		"walked":
			var w := RouteOverlay.CABLE_WALKED * k
			_marks.draw_line(a, b, Color(RouteInk.RING_WALKED, RouteOverlay.CABLE_GLOW_ALPHA), w * RouteOverlay.CABLE_GLOW_SHARE, true)
			_marks.draw_line(a, b, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA), w + RouteOverlay.KEYLINE_EXTRA * k, true)
			_marks.draw_line(a, b, RouteInk.RING_WALKED, w, true)
		"live":
			var speed := 0.0
			var me := Motion.entry(CityMapOverlay.CRAWL_MOTION)
			if me != null and Motion.live(CityMapOverlay.CRAWL_MOTION):
				speed = me.amplitude / maxf(me.duration, 0.001)
			_dashes(a, b, RouteInk.RING_AVAILABLE, RouteOverlay.CABLE_LIVE * k, 1.0, fmod(anim_t * speed, CityMapOverlay.DASH_PERIOD * k), true, k)
		_:
			_dashes(a, b, RouteInk.RING_UNAVAILABLE, RouteOverlay.CABLE_LATER * k, RouteOverlay.LATER_ALPHA, 0.0, false, k)


func _dashes(a: Vector2, b: Vector2, col: Color, width: float, alpha: float, phase: float, keyline: bool, k: float) -> void:
	var length := a.distance_to(b)
	if length <= 0.0:
		return
	var dir := (b - a) / length
	var on := CityMapOverlay.DASH_ON * k
	var period := CityMapOverlay.DASH_PERIOD * k
	var t := phase - period
	var n := 0
	while t < length and n < CityMapOverlay.DASHES_MAX:
		var t0 := maxf(t, 0.0)
		var t1 := minf(t + on, length)
		if t1 > t0:
			if keyline:
				_marks.draw_line(a + dir * t0, a + dir * t1, Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA * alpha), width + RouteOverlay.KEYLINE_EXTRA * k)
			_marks.draw_line(a + dir * t0, a + dir * t1, Color(col, alpha), width)
		t += period
		n += 1


## The red grease-pencil TARGET circle (two rough passes over a dark under-shadow) and the
## word beside it, as the route's TARGET.
func _target(id: StringName, at: Vector2, r: float, k: float) -> void:
	var seed_v := absi(hash(String(corp) + String(id)))
	var rr := r * RouteOverlay.TARGET_SHARE
	for pass_i in 2:
		var ring := PackedVector2Array()
		var turn := TAU * (1.0 + RouteOverlay.TARGET_OVERRUN)
		var start := float(seed_v % 628) * 0.01 + pass_i * 0.9
		for q in RouteOverlay.TARGET_SEGMENTS + 1:
			var t := start + turn * q / RouteOverlay.TARGET_SEGMENTS
			var wob := (sin(t * 3.0 + float(seed_v % 31) + pass_i) + 0.5 * sin(t * 7.0 + pass_i * 2.0)) * RouteOverlay.TARGET_WOBBLE * k
			ring.append(at + Vector2(cos(t), sin(t) * RouteOverlay.TARGET_SQUASH) * (rr * (1.0 + pass_i * 0.06) + wob))
		_marks.draw_polyline(ring, Color(RouteInk.PENCIL_SHADOW, RouteInk.PENCIL_SHADOW_ALPHA), (RouteOverlay.TARGET_STROKE + RouteOverlay.KEYLINE_EXTRA) * k, true)
		_marks.draw_polyline(ring, Color(RouteInk.PENCIL_THREAT, RouteInk.PENCIL_ALPHA), RouteOverlay.TARGET_STROKE * k * (1.0 - pass_i * 0.35), true)
	var f := RouteInk.pencil_font()
	var fs := maxi(1, roundi(RouteOverlay.TARGET_FONT * k))
	var wp := at + Vector2(rr * RouteOverlay.ROUTE_TARGET_WORD_AT.x, -rr * RouteOverlay.ROUTE_TARGET_WORD_AT.y * 0.2)
	_marks.draw_set_transform(wp, RouteOverlay.TARGET_WORD_TILT)
	var word := tr(RouteOverlay.TARGET_WORD)
	_marks.draw_string_outline(f, Vector2.ZERO, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, maxi(1, roundi(RouteOverlay.KEYLINE_EXTRA * k)), Color(RouteInk.PENCIL_SHADOW, RouteInk.PENCIL_SHADOW_ALPHA))
	_marks.draw_string(f, Vector2.ZERO, word, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(RouteInk.PENCIL_THREAT, RouteInk.PENCIL_ALPHA))
	_marks.draw_set_transform(Vector2.ZERO, 0.0)


func _chip(k: float) -> void:
	var r := chip_rect()
	if not r.has_area():
		return
	var f := Palette.mono()
	var fs := maxi(1, roundi(CHIP_FONT * k))
	_marks.draw_rect(r, Color(Palette.NIGHT_SKY, CHIP_GLASS_ALPHA))
	_marks.draw_rect(r, Palette.RESIST_GOLD, false, maxf(1.0, k))
	_marks.draw_string(f, r.position + Vector2(CHIP_PAD, CHIP_PAD + f.get_ascent(fs)), _chip_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Palette.RESIST_GOLD)


## The operative pin over "you are here" (the route's pin).
func _here(at: Vector2, r: float, k: float) -> void:
	var side := r * RouteOverlay.PIN_SHARE
	var c := at + Vector2(r * RouteOverlay.PIN_OFFSET.x, r * RouteOverlay.PIN_OFFSET.y)
	_marks.draw_set_transform(c, RouteOverlay.PIN_TILT)
	var box := Rect2(-Vector2(side, side) * 0.5, Vector2(side, side))
	_marks.draw_rect(box.grow(RouteOverlay.DIE_CUT_WIDTH * k + k), Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA))
	_marks.draw_rect(box.grow(RouteOverlay.DIE_CUT_WIDTH * k), RouteInk.DIE_CUT)
	_marks.draw_rect(box, Palette.CELL_PINK)
	StatIcon.draw(_marks, Vector2.ZERO, side * RouteOverlay.PIN_ICON_SHARE * 0.5, StatIcon.OPERATIVE, Palette.PAPER)
	_marks.draw_set_transform(Vector2.ZERO, 0.0)
	_marks.draw_line(c + Vector2(-side * 0.2, side * 0.45), at + Vector2(r * 0.35, -r * 0.7), Color(RouteInk.KEYLINE, RouteInk.KEYLINE_ALPHA), 2.0 * k)
