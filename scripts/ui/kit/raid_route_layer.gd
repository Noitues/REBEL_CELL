class_name RaidRouteLayer
extends Control
## ART-6 3A: the raid's grease-pencil routes on the map (ART_BIBLE v2 §4.8 "Pencil rules",
## round 21 `path_rules`): red pencil along the real streets, solid = the route a threat
## will take (the resolver's own projection, so the plan is true to the rules: preview equals
## result), dashed = a what-if (a defence carried over a node, before it is placed), with
## the entry Sites circled and lettered A, B, C. The routes write on along their length
## (`raid_route_write`) and wipe off with a cloth wipe from their start (`raid_route_wipe`,
## at the verdict), never an alpha fade. A child of a CityMapOverlay (it pans and zooms with
## the city); view only: it draws the site paths it is given.

const WRITE_MOTION := &"raid_route_write"
const WIPE_MOTION := &"raid_route_wipe"
## Stroke width and the entry circle's radii (screen px), the
## arrow's stop short of the target node (x its icon radius), the letter's size.
const WIDTH := 7.0
const ENTRY_R := Vector2(30, 20)
const ARROW_STOP := 1.9
const LETTER_STEP := UiTheme.TITLE
const LETTER_OFF := Vector2(34, -22)

var overlay: CityMapOverlay
## Solid routes: Arrays of Site ids (entry first).
var routes: Array[Array] = []
## Dashed what-if routes.
var what_if: Array[Array] = []
## Entry Site id -> its letter ("A").
var letters: Dictionary = {}
## Write-on and wipe progress (0..1); MotionValues keep them on the Motion clock.
var write_u: float:
	get:
		return _mv.value(&"write_u")
	set(v):
		_mv.put(&"write_u", v)
var wipe_u: float:
	get:
		return _mv.value(&"wipe_u", 0.0)
	set(v):
		_mv.put(&"wipe_u", v)
var _mv := MotionValues.new({&"write_u": 1.0, &"wipe_u": 0.0})
var _pool: RaidPencilPool = null


func _init(p_overlay: CityMapOverlay = null) -> void:
	overlay = p_overlay
	name = "RaidRoutes"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_mv)
	_mv.changed.connect(_on_value)
	MotionSkip.register_passive(self)


## Sets the solid routes (`paths`: Site id sequences) and letters their entries in order
## (A first); `write` draws them on (`raid_route_write`; at once when motion doesn't play).
func set_routes(paths: Array[Array], write: bool = true) -> void:
	routes = paths
	letters.clear()
	for p in paths:
		if p.is_empty():
			continue
		var entry := StringName(String(p[0]))
		if not letters.has(entry):
			letters[entry] = RaidRouteMark.letter_of(letters.size())
	wipe_u = 0.0
	if write and is_inside_tree():
		write_u = 0.0
		Motion.run(WRITE_MOTION, _mv, ^"write_u", 1.0)
	else:
		write_u = 1.0
	queue_redraw()


## Sets the dashed what-if routes (empty: none).
func set_what_if(paths: Array[Array]) -> void:
	what_if = paths
	queue_redraw()


## Cloth-wipes every route off (the verdict is in).
func wipe() -> void:
	if is_inside_tree():
		Motion.run(WIPE_MOTION, _mv, ^"wipe_u", 1.0)
	else:
		wipe_u = 1.0


func _on_value(_key: StringName) -> void:
	queue_redraw()


## MotionSkip (ANIM-R6 D7): the write-on or wipe is running.
func motion_running() -> bool:
	return Motion.held(_mv, ^"write_u") or Motion.held(_mv, ^"wipe_u")


## MotionSkip: the routes at their end state.
func complete_motion() -> void:
	Motion.settle(_mv, ^"write_u")
	Motion.settle(_mv, ^"wipe_u")


func _process(_delta: float) -> void:
	_lay()


func _exit_tree() -> void:
	if _pool != null and is_instance_valid(_pool):
		_pool.release()
	_pool = null


## Route `path`'s points (global px, through RaidMapAnchor): node to node along the streets,
## ending short of the last node (its arrow stops outside the node's circle); empty when off
## the map.
func path_points(path: Array) -> PackedVector2Array:
	var pts := PackedVector2Array()
	if overlay == null or path.size() < 2:
		return pts
	var first := RaidMapAnchor.site(overlay, StringName(String(path[0])))
	if first.x == INF:
		return pts
	pts.append(first)
	for i in path.size() - 1:
		var a := StringName(String(path[i]))
		var b := StringName(String(path[i + 1]))
		pts.append_array(RaidMapAnchor.street(overlay, a, b))
		var end := RaidMapAnchor.site(overlay, b)
		if end.x == INF:
			return PackedVector2Array()
		pts.append(end)
	# Stop short of the target's circle.
	var stop := CityMapOverlay.ICON_RADIUS_BIG * ARROW_STOP
	var total := PencilShapes.length_of(pts)
	if total > stop * 1.5:
		pts = PencilShapes.trim(pts, 0.0, total - stop)
	return pts


## Lays the routes on 1B's grease pencil (RaidPencilPool): red arrows along the streets
## (snapped onto them: the mark says what the rules will do), the entries circled and lettered.
func _lay() -> void:
	if overlay == null or overlay.city == null or not is_visible_in_tree():
		if _pool != null:
			_pool.begin()
			_pool.end()
		return
	if _pool == null:
		_pool = RaidPencilPool.make(self)
	_pool.begin()
	var threat := GreasePencilMark.Ink.THREAT
	for i in routes.size():
		var street := path_points(routes[i])
		if street.size() < 2:
			continue
		var hand := PencilShapes.snap_to(RaidPencil.roughen(street, 31 + i, WIDTH * 0.4, WIDTH * 3.0), street)
		var strokes := PencilShapes.arrow(hand, WIDTH * RaidPencil.HEAD_LEN, 31 + i)
		_pool.stroke("route_%d" % i, strokes, threat, WIDTH, write_u, wipe_u, false, 31 + i)
	for i in what_if.size():
		var street := path_points(what_if[i])
		if street.size() >= 2:
			_pool.stroke("whatif_%d" % i, PencilShapes.arrow(street, WIDTH * RaidPencil.HEAD_LEN, 71 + i), threat, WIDTH, 1.0, 0.0, true, 71 + i)
	var ids := letters.keys()
	ids.sort()
	for id in ids:
		var c := RaidMapAnchor.site(overlay, id)
		if c.x == INF:
			continue
		var u := clampf(write_u * 1.5, 0.0, 1.0)
		var seed := String(id).hash()
		_pool.stroke("entry_%s" % id, [PencilShapes.hand_circle(c, ENTRY_R, seed)], threat, WIDTH, u, wipe_u, false, seed)
		_pool.word("letter_%s" % id, String(letters[id]), c + LETTER_OFF, LETTER_STEP, threat, 1.0, u, wipe_u, -0.08)
	_pool.end()


## The entry letters drawn (Site id -> letter; tests).
func letter_of(site: StringName) -> String:
	return String(letters.get(site, ""))


## The pencil marks laid now (tests).
func shown() -> Array[Node2D]:
	return _pool.shown() if _pool != null else []
