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
## The entry circle's radii (screen px; the stroke is the kit's one wax width, B1b), the
## arrow's stop short of the target node (x its icon radius), the letter's size.
const ENTRY_R := Vector2(30, 20)
const ARROW_STOP := 1.9
const LETTER_STEP := UiTheme.TITLE
const LETTER_OFF := Vector2(34, -22)
## RAID-FIX D1: the white-hot core is a thin 0.18 of the width (the cobalt stays saturated either side of it), and a dark
## ink edge 1.3 x the width sits under the route so it reads as a drawn threat path, not a network link.
## RAID-FIX C2: the white-hot core's share of the stroke width; the count tick ("x2") on a segment several threats
## share, and where it sits off the segment's middle (px).
const CORE_SHARE := 0.18
const EDGE_SHARE := 1.3
const COUNT_FORMAT := "x%d"
const COUNT_OFF := Vector2(0, -18)

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
## M14 12Q-HQ: where the pencil is laid (null: the scene's raid pencil layer, over every UI). A
## page that keeps its map marks under its own panels (the HQ: its terminals over the routes)
## gives a Control in its draw order; the pool maps the global points into it.
var pool_host: Control = null
## The signature the pencil was last laid for (0: lay at the next frame).
var _laid_sig: int = 0


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
func path_points(path: Array, stop_short: bool = true) -> PackedVector2Array:
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
	if not stop_short:
		return pts
	# Stop short of the target's circle.
	var stop := CityMapOverlay.ICON_RADIUS_BIG * ARROW_STOP
	var total := PencilShapes.length_of(pts)
	if total > stop * 1.5:
		pts = PencilShapes.trim(pts, 0.0, total - stop)
	return pts


## RAID-FIX C2: the routes with their shared segments drawn once. Returns {"runs": Array of
## {"nodes": Array (Site ids), "arrow": bool (the run ends on its route's last node: it carries
## the head)}, "ticks": Array of {"a", "b" (the stretch's first segment), "count"}}: a stretch of
## segments that `count` >= 2 routes share gets one "xN" tick. Pure; ties follow the routes' order.
static func merge_routes(paths: Array) -> Dictionary:
	var counts := {}
	for p in paths:
		var seen := {}
		for i in (p as Array).size() - 1:
			var k := _seg_key(p[i], p[i + 1])
			if not seen.has(k):
				seen[k] = true
				counts[k] = int(counts.get(k, 0)) + 1
	var drawn := {}
	var runs: Array[Dictionary] = []
	var ticks: Array[Dictionary] = []
	var tick_done := {}
	for p in paths:
		var arr: Array = p
		var cur: Array = []
		var prev_n := 0
		for i in arr.size() - 1:
			var k := _seg_key(arr[i], arr[i + 1])
			var n := int(counts[k])
			if n >= 2 and n != prev_n and not tick_done.has(k):
				tick_done[k] = true
				ticks.append({"a": arr[i], "b": arr[i + 1], "count": n})
			prev_n = n if n >= 2 else 0
			if drawn.has(k):
				if not cur.is_empty():
					runs.append({"nodes": cur, "arrow": false})
					cur = []
				continue
			drawn[k] = true
			if cur.is_empty():
				cur = [arr[i]]
			cur.append(arr[i + 1])
		if not cur.is_empty():
			runs.append({"nodes": cur, "arrow": cur[cur.size() - 1] == arr[arr.size() - 1]})
	return {"runs": runs, "ticks": ticks}


static func _seg_key(a: Variant, b: Variant) -> String:
	var x := String(a)
	var y := String(b)
	return "%s>%s" % [x, y] if x <= y else "%s>%s" % [y, x]


## Lays the routes on 1B's grease pencil (RaidPencilPool): red arrows along the streets
## (snapped onto them: the mark says what the rules will do), the entries circled and lettered.
func _lay() -> void:
	if overlay == null or overlay.city == null or not is_visible_in_tree():
		_laid_sig = 0
		if _pool != null:
			_pool.begin()
			_pool.end()
		return
	if _pool == null:
		if pool_host != null and is_instance_valid(pool_host):
			_pool = RaidPencilPool.new()
			pool_host.add_child(_pool)
		else:
			_pool = RaidPencilPool.make(self)
	if pool_host != null and is_instance_valid(pool_host) and _pool.get_parent() == pool_host:
		# The points are global px: the pool undoes its host's canvas transform (a page that slides).
		var undo := pool_host.get_global_transform_with_canvas().affine_inverse()
		if _pool.transform != undo:
			_pool.transform = undo
	# M14 perf slice: the pencil is laid again only when something it shows changed (the routes,
	# the progress, the map's camera, the text size); at rest the marks stay as laid.
	var sig := lay_signature()
	if sig == _laid_sig:
		return
	_laid_sig = sig
	_pool.begin()
	var threat := GreasePencilMark.Ink.THREAT_ROUTE
	var cues := RaidPencil.hostile_cues()
	var merged := merge_routes(routes)
	var runs: Array = merged["runs"]
	for i in runs.size():
		var run: Dictionary = runs[i]
		var arrow := bool(run["arrow"])
		var street := path_points(run["nodes"], arrow)
		if street.size() < 2:
			continue
		var hand := PencilShapes.snap_to(RaidPencil.roughen(street, 31 + i, GreasePencilMark.stroke_width() * 0.4, GreasePencilMark.stroke_width() * 3.0), street)
		var strokes: Array[PackedVector2Array] = [hand]
		if arrow:
			strokes = PencilShapes.arrow(hand, GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 31 + i)
		var edge := _pool.stroke("edge_%d" % i, strokes, GreasePencilMark.Ink.THREAT_EDGE, write_u, wipe_u, false, 31 + i)
		edge.width_share = EDGE_SHARE
		_pool.stroke("route_%d" % i, strokes, threat, write_u, wipe_u, false, 31 + i)
		# C2: the white-hot core, a thin sliver of the width, centred on the cobalt stroke.
		var core := _pool.stroke("core_%d" % i, strokes, GreasePencilMark.Ink.THREAT_CORE, write_u, wipe_u, false, 31 + i)
		core.width_share = CORE_SHARE
		if cues:
			# M14 12Q-RAID: the colour-blind setting's barbed line (hostile by shape, RaidPencil).
			var w := GreasePencilMark.stroke_width()
			_pool.stroke("ticks_%d" % i, RaidPencil.hazard_ticks(hand, w * RaidPencil.TICK_STEP, w * RaidPencil.TICK_HALF), threat, write_u, wipe_u, false, 131 + i)
	var ticks: Array = merged["ticks"]
	for i in ticks.size():
		var seg := path_points([ticks[i]["a"], ticks[i]["b"]], false)
		if seg.size() < 2:
			continue
		_pool.word("count_%d" % i, COUNT_FORMAT % int(ticks[i]["count"]), seg[seg.size() / 2] + COUNT_OFF, LETTER_STEP, threat, 1.0, clampf(write_u * 1.5, 0.0, 1.0), wipe_u, -0.08)
	for i in what_if.size():
		var street := path_points(what_if[i])
		if street.size() >= 2:
			_pool.stroke("whatif_%d" % i, PencilShapes.arrow(street, GreasePencilMark.stroke_width() * RaidPencil.HEAD_LEN, 71 + i), threat, 1.0, 0.0, true, 71 + i)
			if cues:
				# M14 12Q-ACCESS (L79): the HQ's what-if route carries the barbed line too (the Grid's
				# pending raid read red-on-lime alone with the colour-blind setting on).
				var w := GreasePencilMark.stroke_width()
				_pool.stroke("whatif_ticks_%d" % i, RaidPencil.hazard_ticks(street, w * RaidPencil.TICK_STEP, w * RaidPencil.TICK_HALF), threat, 1.0, 0.0, false, 171 + i)
	var ids := letters.keys()
	IdSort.sort_ids(ids)
	for id in ids:
		var c := RaidMapAnchor.site(overlay, id)
		if c.x == INF:
			continue
		var u := clampf(write_u * 1.5, 0.0, 1.0)
		var seed := String(id).hash()
		_pool.stroke("entry_%s" % id, [PencilShapes.hand_circle(c, ENTRY_R, seed)], threat, u, wipe_u, false, seed)
		_pool.word("letter_%s" % id, String(letters[id]), c + LETTER_OFF, LETTER_STEP, threat, 1.0, u, wipe_u, -0.08)
		if cues:
			_pool.stroke("reticle_%s" % id, RaidPencil.reticle_ticks(c, ENTRY_R), threat, u, wipe_u, false, seed + 1)
	_pool.end()


## The signature of what the pencil shows (M14 perf slice): the routes, what-ifs and letters,
## the write and wipe progress, the text size, and where the map puts each route's ends and
## each entry (the map's camera: with a fixed yaw and pitch, two points pin down a pan and a zoom).
func lay_signature() -> int:
	var anchors: Array[Vector2] = []
	for r: Array in routes + what_if:
		if r.is_empty():
			continue
		anchors.append(RaidMapAnchor.site(overlay, StringName(String(r[0]))))
		anchors.append(RaidMapAnchor.site(overlay, StringName(String(r[r.size() - 1]))))
	var ids := letters.keys()
	IdSort.sort_ids(ids)
	for id in ids:
		anchors.append(RaidMapAnchor.site(overlay, id))
	return hash([routes, what_if, ids, letters.values(), write_u, wipe_u, anchors, Settings.text_scale, size, RaidPencil.hostile_cues()])


## The entry letters drawn (Site id -> letter; tests).
func letter_of(site: StringName) -> String:
	return String(letters.get(site, ""))


## The pencil marks laid now (tests).
func shown() -> Array[Node2D]:
	return _pool.shown() if _pool != null else []
