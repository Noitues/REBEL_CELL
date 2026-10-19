class_name NetrunHqOrbit
extends RefCounted
## NA-21 twin of `tools/netrun_art/hq/orbit.py`: the HQ orbit camera on generic slots (decision, hover, overview).


## The HQ rig numbers: config `hq_rig` without `dmin_kit`, plus `dmin = kit(dmin_kit)`.
static func hq_rig() -> Dictionary:
	var g: Dictionary = NetrunArtConfigData.shipped().hq_rig.duplicate(true)
	var dk: float = float(g["dmin_kit"])
	g.erase("dmin_kit")
	g["dmin"] = NetrunArtUnits.kit(dk)
	return g


## Outward plan normal of a room (back centre -> front centre, unit).
static func room_normal(room: Dictionary) -> Array:
	var f: Array = []
	var b: Array = []
	for k in 2:
		var sf: float = 0.0
		for q: Array in room["front"]:
			sf += float(q[k])
		f.append(sf / 4)
		var sb: float = 0.0
		for q: Array in room["back"]:
			sb += float(q[k])
		b.append(sb / 4)
	var n: Array = [f[0] - b[0], f[1] - b[1]]
	var length: float = NetrunArtUnits.hypot(n[0], n[1])
	if length == 0.0:
		length = 1.0
	return [n[0] / length, n[1] / length]


## Index into `FACES` of the face a room stands on (highest dot, ties to the lower index).
static func face_index(room: Dictionary) -> int:
	var n: Array = room_normal(room)
	var best: int = 0
	var best_dot: float = 0.0
	for i in 4:
		var fc: Array = NetrunHqSlots.FACES[i]
		var d: float = float(fc[0]) * n[0] + float(fc[1]) * n[1]
		if i == 0 or d > best_dot:
			best = i
			best_dot = d
	return best


static func _yaw(v: Array) -> float:
	return rad_to_deg(atan2(v[0], v[1]))


## Mean look vector (minus the outward normal) of the distinct faces of `ids`, as a rig yaw.
static func decision_yaw(rooms: Dictionary, ids: Array, look_ahead: float = 0.0) -> float:
	var set: Dictionary = {}
	for i: String in ids:
		set[face_index(rooms[i])] = true
	var faces: Array = set.keys()
	faces.sort()
	var vx: float = 0.0
	var vy: float = 0.0
	var ix: int = 0
	var iy: int = 0
	for f: int in faces:
		ix += -int(NetrunHqSlots.FACES[f][0])
		iy += -int(NetrunHqSlots.FACES[f][1])
	vx = float(ix)
	vy = float(iy)
	return _yaw([vx, vy]) + look_ahead


## DECISION pose on `current` ("" = none) plus `options`; `entry` ([] = none) is framed when there is no current.
static func hq_decision(rooms: Dictionary, current: String, options: Array, layer_idx: int, n_layers: int,
		rig_over: Dictionary = {}, entry: Array = []) -> NetrunPose:
	var g: Dictionary = NetrunArtUnits.merge(hq_rig(), rig_over)
	var ids: Array = []
	if current != "":
		ids.append(current)
	for o: String in options:
		if o != current:
			ids.append(o)
	var pts: Array = []
	for i: String in ids:
		for p: Array in NetrunCameraRig.room_corners(rooms[i]):
			pts.append(p)
	if current == "" and not entry.is_empty():
		pts.append(entry.duplicate())
	var t: float = NetrunArtUnits.clamp01(float(layer_idx) / float(maxi(1, n_layers - 1)))
	var pitch: float = NetrunArtUnits.lerp_f(g["pitch_lo"], g["pitch_hi"], t)
	return NetrunCameraRig.frame_points(pts, decision_yaw(rooms, ids, g["look_ahead"]), pitch, g["lens_d"], g["fill_w"],
		g["fill_h"], 0.0, [], g["dmin"])


## HOVER pose at ease `k`: pull toward the room, turn toward it (side by camera right), dolly.
static func hq_hover(decision: NetrunPose, room: Dictionary, k: float = 1.0, rig_over: Dictionary = {}) -> NetrunPose:
	var g: Dictionary = NetrunArtUnits.merge(hq_rig(), rig_over)
	var c: Array = NetrunCameraRig.room_center(room)
	var focus: Array = []
	for i in 3:
		focus.append(decision.F[i] + (c[i] - decision.F[i]) * g["hover_pull"])
	var d: Array = decision.dir()
	var rx: float = d[1]
	var ry: float = -d[0]
	var s: float = -1.0
	if (c[0] - decision.F[0]) * rx + (c[1] - decision.F[1]) * ry > 0:
		s = 1.0
	var h: NetrunPose = NetrunPose.make(focus, decision.yaw + g["hover_yaw"] * s, decision.pitch,
		decision.dist * g["hover_dolly"], decision.lens, decision.sx, decision.sy)
	return decision.mix(h, k)


## Yaw on the corner whose two faces hold the most live rooms; tie to the current face, then the lower face.
static func overview_yaw(rooms: Dictionary, live: Array, current: String) -> float:
	var fc: int = -1
	if current != "":
		fc = face_index(rooms[current])
	var have: bool = false
	var bn: int = 0
	var bc: int = 0
	var bf: int = 0
	var bg: int = 0
	for f in 4:
		var g: int = (f + 1) % 4
		var n: int = 0
		for i: String in live:
			var fi: int = face_index(rooms[i])
			if fi == f or fi == g:
				n += 1
		var c: int = 1 if f == fc else 0
		var better: bool = false
		if not have:
			better = true
		elif n != bn:
			better = n > bn
		elif c != bc:
			better = c > bc
		else:
			better = -f > -bf
		if better:
			have = true
			bn = n
			bc = c
			bf = f
			bg = g
	var ff: Array = NetrunHqSlots.FACES[bf]
	var fg: Array = NetrunHqSlots.FACES[bg]
	return _yaw([float(-int(ff[0]) - int(fg[0])), float(-int(ff[1]) - int(fg[1]))])


## Corner points of every tier base, the crown, and the lot rectangle on the ground.
static func overview_points(comp: Dictionary) -> Array:
	var cx: float = comp["centre"][0]
	var cy: float = comp["centre"][1]
	var pts: Array = []
	var halves: Array = comp["half"]
	var z0s: Array = comp["z0"]
	for n in mini(halves.size(), z0s.size()):
		var hs: float = halves[n]
		var z0: float = z0s[n]
		for sx: int in [-1, 1]:
			for sy: int in [-1, 1]:
				pts.append([cx + float(sx) * hs, cy + float(sy) * hs, z0])
	var top: float = float(z0s[z0s.size() - 1]) + float(comp["tier_h"])
	pts.append([cx, cy, top])
	var r: Array = comp["rect"]
	pts.append([r[0], r[2], 0.0])
	pts.append([r[1], r[2], 0.0])
	pts.append([r[1], r[3], 0.0])
	pts.append([r[0], r[3], 0.0])
	return pts


## OVERVIEW pose framed on the whole landmark, centred on its mid height.
static func hq_overview(rooms: Dictionary, comp: Dictionary, live: Array, current: String,
		rig_over: Dictionary = {}) -> NetrunPose:
	var g: Dictionary = NetrunArtUnits.merge(hq_rig(), rig_over)
	var z0s: Array = comp["z0"]
	var mid: float = (float(z0s[z0s.size() - 1]) + float(comp["tier_h"])) / 2.0
	return NetrunCameraRig.frame_points(overview_points(comp), overview_yaw(rooms, live, current), g["pitch_o"],
		g["lens_o"], g["fill_ow"], g["fill_oh"], 0.0, [float(comp["centre"][0]), float(comp["centre"][1]), mid])


## A room is drawn when `dot(face normal, direction to the camera) > vis_margin` (margin NAN = config value).
static func visible_room(room: Dictionary, pose: NetrunPose, margin: float = NAN) -> bool:
	var m: float = margin
	if is_nan(margin):
		m = float(hq_rig()["vis_margin"])
	var loc: Array = pose.loc()
	var c: Array = NetrunCameraRig.room_center(room)
	var dx: float = loc[0] - c[0]
	var dy: float = loc[1] - c[1]
	var length: float = NetrunArtUnits.hypot(dx, dy)
	if length == 0.0:
		length = 1.0
	var n: Array = room_normal(room)
	return (n[0] * dx + n[1] * dy) / length > m
