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
## Stroke width and the entry circle's radii (screen px x the overlay's screen_k), the
## arrow's stop short of the target node (x its icon radius), the letter's size.
const WIDTH := 4.5
const ENTRY_R := Vector2(30, 20)
const ARROW_STOP := 1.9
const LETTER_PX := 24
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
	if is_visible_in_tree() and not routes.is_empty():
		queue_redraw()


## Route `path`'s points on the map (local px): node to node along the streets, ending short
## of the last node (its arrow stops outside the node's circle); empty when off the map.
func path_points(path: Array) -> PackedVector2Array:
	var pts := PackedVector2Array()
	if overlay == null or path.size() < 2:
		return pts
	var first := overlay.icon_at(StringName(String(path[0])))
	if first.x == INF:
		return pts
	pts.append(first)
	for i in path.size() - 1:
		var a := StringName(String(path[i]))
		var b := StringName(String(path[i + 1]))
		for p in overlay.route_between(a, b):
			pts.append(overlay.grid_point_local(p))
		var end := overlay.icon_at(b)
		if end.x == INF:
			return PackedVector2Array()
		pts.append(end)
	# Stop short of the target's circle.
	var stop := CityMapOverlay.ICON_RADIUS_BIG * overlay.screen_k() * ARROW_STOP
	var total := RaidPencil.length_of(pts)
	if total > stop * 1.5:
		pts = RaidPencil.trimmed(pts, 0.0, 1.0 - stop / total)
	return pts


func _draw() -> void:
	if overlay == null or overlay.city == null:
		return
	var k := overlay.screen_k()
	var red := RaidSkin.pencil_threat()
	var w := WIDTH * k
	for i in routes.size():
		var pts := path_points(routes[i])
		if pts.size() < 2:
			continue
		if wipe_u <= 0.0:
			RaidPencil.arrow(self, pts, red, w, write_u, 31 + i * 17)
		else:
			RaidPencil.stroke(self, pts, red, w, wipe_u, write_u, 31 + i * 17)
	for i in what_if.size():
		var pts := path_points(what_if[i])
		if pts.size() >= 2:
			RaidPencil.arrow(self, pts, red, w, 1.0, 71 + i * 13, true)
	var ids := letters.keys()
	ids.sort()
	for id in ids:
		var c := overlay.icon_at(id)
		if c.x == INF:
			continue
		var u := clampf(write_u * 1.5, 0.0, 1.0)
		RaidPencil.circle(self, c, ENTRY_R.x * k, ENTRY_R.y * k, red, w, wipe_u, u, String(id).hash())
		if wipe_u < 1.0 and u > 0.0:
			var px := maxi(1, roundi(LETTER_PX * k * Settings.text_scale))
			RaidPencil.word(self, String(letters[id]), c + LETTER_OFF * k, px, red, u, wipe_u, -0.08)


## The entry letters drawn (Site id -> letter; tests).
func letter_of(site: StringName) -> String:
	return String(letters.get(site, ""))
