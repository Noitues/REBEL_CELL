class_name NetrunCameraRig
extends RefCounted
## NA-21 twin of `tools/netrun_art/rig.py`: easing, framing solver, street rig poses and the dive path.


## Smoothstep easing.
static func ease(t: float) -> float:
	var x: float = NetrunArtUnits.clamp01(t)
	return x * x * (3.0 - 2.0 * x)


## Cubic ease-out.
static func ease_out(t: float) -> float:
	var x: float = NetrunArtUnits.clamp01(t)
	return 1.0 - pow(1.0 - x, 3.0)


## `SB/sb_ocjobs.py` smoother (smootherstep).
static func smootherstep(t: float) -> float:
	var x: float = NetrunArtUnits.clamp01(t)
	return x * x * x * (x * (6.0 * x - 15.0) + 10.0)


## layout36 concept yaw (0 = +x, ccw) to rig yaw (0 = +y, cw).
static func yaw_to_rig(yaw_l36: float) -> float:
	return 90.0 - yaw_l36


## Rig yaw looking along a plan vector: `atan2(x, y)` in degrees.
static func yaw_of_nrm(nrm: Array) -> float:
	return rad_to_deg(atan2(float(nrm[0]), float(nrm[1])))


## `y` shifted by multiples of 360 to lie within 180 of `ref` (shortest arc).
static func unwrap_yaw(y: float, ref: float) -> float:
	var r: float = y
	while r - ref > 180.0:
		r -= 360.0
	while r - ref < -180.0:
		r += 360.0
	return r


## Pixel box `[x0, y0, x1, y1]` of the unshifted projections; empty Array when no point is in front of the camera.
static func bbox_px(pose: NetrunPose, pts: Array) -> Array:
	var xs: Array = []
	var ys: Array = []
	for p: Array in pts:
		var q: Array = pose.proj(p, false)
		if not q.is_empty():
			xs.append(q[0])
			ys.append(q[1])
	if xs.is_empty():
		return []
	return [xs.min(), ys.min(), xs.max(), ys.max()]


## Solve `dist` and the lens shift so `pts` fill `fw` of the usable width or `fh` of its height (bisection); `centre` [] = none.
static func frame_points(pts: Array, yaw: float, pitch: float, lens: float, fw: float, fh: float, bias: float = 0.0,
		centre: Array = [], dmin: float = 0.0) -> NetrunPose:
	var rg: Dictionary = NetrunArtConfigData.shipped().rig
	var use: Array = rg["use"]
	var ref_w: float = rg["ref_w"]
	var ucx: float = (float(use[0]) + float(use[2])) / 2
	var ucy: float = (float(use[1]) + float(use[3])) / 2
	var uw: float = float(use[2]) - float(use[0])
	var uh: float = float(use[3]) - float(use[1])
	var focus: Array = []
	if not centre.is_empty():
		focus = centre
	else:
		var mn: Array = [INF, INF, INF]
		var mx: Array = [-INF, -INF, -INF]
		for p: Array in pts:
			for i in 3:
				mn[i] = minf(mn[i], float(p[i]))
				mx[i] = maxf(mx[i], float(p[i]))
		focus = [(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, (mn[2] + mx[2]) / 2]
	var br: Array = rg["solver_bracket"]
	var lo: float = br[0]
	var hi: float = br[1]
	var iters: int = int(rg["solver_iters"])
	for _n in iters:
		var d: float = sqrt(lo * hi)
		var bb: Array = bbox_px(NetrunPose.make(focus, yaw, pitch, d, lens), pts)
		var k: float = 9.0
		if not bb.is_empty():
			k = maxf((bb[2] - bb[0]) / (fw * uw), (bb[3] - bb[1]) / (fh * uh))
		if k > 1.0:
			lo = d
		else:
			hi = d
	var pose: NetrunPose = NetrunPose.make(focus, yaw, pitch, maxf(hi, dmin), lens)
	var b: Array = bbox_px(pose, pts)
	if b.is_empty():
		return pose
	pose.sx = ((b[0] + b[2]) / 2 - (ucx + bias * uw)) / ref_w
	pose.sy = (ucy - (b[1] + b[3]) / 2) / ref_w
	return pose


## The 8 world corners of a derive room (front then back quad), z above `ground_z` added.
static func room_corners(room: Dictionary) -> Array:
	var gz: float = float(room.get("ground_z", 0.0))
	var out: Array = []
	for p: Array in room["front"]:
		out.append([float(p[0]), float(p[1]), float(p[2]) + gz])
	for p: Array in room["back"]:
		out.append([float(p[0]), float(p[1]), float(p[2]) + gz])
	return out


## Centroid of the 8 corners.
static func room_center(room: Dictionary) -> Array:
	var c: Array = room_corners(room)
	var n: float = float(c.size())
	var out: Array = []
	for k in 3:
		var s: float = 0.0
		for p: Array in c:
			s += float(p[k])
		out.append(s / n)
	return out


## `yaw0` of the street rig: the camera looks along the street face normal.
static func street_yaw0(nrm: Array) -> float:
	return yaw_of_nrm(nrm)


## The plate camera rule (art-pass A-025 / A-026): focus on the box centre of `pts`, the plate's fixed `dist` and lens shift
## (`ov_*` / `dec_*` in the rig config), the yaw along the street face normal. Twin of `rig.plate_pose`.
static func plate_pose(pts: Array, yaw: float, pitch: float, lens: float, dist: float, shift: Array) -> NetrunPose:
	var mn: Array = [INF, INF, INF]
	var mx: Array = [-INF, -INF, -INF]
	for p: Array in pts:
		for i in 3:
			mn[i] = minf(mn[i], float(p[i]))
			mx[i] = maxf(mx[i], float(p[i]))
	var pose: NetrunPose = NetrunPose.make([(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, (mn[2] + mx[2]) / 2], yaw, pitch, dist, lens)
	pose.sx = float(shift[0])
	pose.sy = float(shift[1])
	return pose


## The street OVERVIEW pose (one-city overrides, rig convention); `rig_over` {} = none.
static func street_overview(rooms: Dictionary, nrm: Array, start_left: bool, rig_over: Dictionary = {}) -> NetrunPose:
	var g: Dictionary = NetrunArtUnits.merge(NetrunArtConfigData.shipped().rig, rig_over)
	var sgn: float = 1.0 if start_left else -1.0
	var pts: Array = []
	for r: Dictionary in rooms.values():
		pts.append_array(room_corners(r))
	return plate_pose(pts, street_yaw0(nrm) + sgn * float(g["ov_yaw_k"]) * float(g["yaw_max"]), g["pitch_o"], g["lens_o"],
		float(g["ov_dist"]), g["ov_shift"])


## `u = layer / (layers - 1)` clamped 0..1.
static func street_u(layers: int, current_layer: int) -> float:
	return NetrunArtUnits.clamp01(float(current_layer) / float(maxi(1, layers - 1)))


## The street DECISION pose on `current` ("" = none) plus `options`; `entry` [] = none.
static func street_decision(rooms: Dictionary, current: String, options: Array, u: float, nrm: Array,
		start_left: bool, rig_over: Dictionary = {}, entry: Array = []) -> NetrunPose:
	var g: Dictionary = NetrunArtUnits.merge(NetrunArtConfigData.shipped().rig, rig_over)
	var sgn: float = 1.0 if start_left else -1.0
	var ids: Array = []
	if current != "":
		ids.append(current)
	for o: String in options:
		if o != current:
			ids.append(o)
	var pts: Array = []
	for i: String in ids:
		pts.append_array(room_corners(rooms[i]))
	if current == "" and not entry.is_empty():
		pts.append(entry.duplicate())
	var off: float = sgn * float(g["yaw_max"]) * (1.0 - 2.0 * NetrunArtUnits.clamp01(u))
	return plate_pose(pts, street_yaw0(nrm) + off, g["pitch_d"], g["lens_d"], float(g["dec_dist"]), g["dec_shift"])


## The street HOVER pose at ease `k` (1 = fully hovered): pull toward the room, turn toward it, dolly in.
static func street_hover(decision: NetrunPose, target_room: Dictionary, nrm: Array, k: float = 1.0,
		rig_over: Dictionary = {}) -> NetrunPose:
	var g: Dictionary = NetrunArtUnits.merge(NetrunArtConfigData.shipped().rig, rig_over)
	var c: Array = room_center(target_room)
	var p: NetrunPose = decision
	var focus: Array = []
	for i in 3:
		focus.append(p.F[i] + (c[i] - p.F[i]) * float(g["hover_pull"]))
	var rx: float = nrm[1]
	var ry: float = -float(nrm[0])
	var s: float = 1.0 if (c[0] - p.F[0]) * rx + (c[1] - p.F[1]) * ry > 0.0 else -1.0
	var h: NetrunPose = NetrunPose.make(focus, p.yaw + float(g["hover_yaw"]) * s, p.pitch,
		p.dist * float(g["hover_dolly"]), p.lens, p.sx, p.sy)
	return p.mix(h, k)


## Mainline HQ page camera `[target, width]` fitted to the launchable Sites of `net`.
static func hq_page_camera(net: Dictionary) -> Array:
	var cfg: NetrunArtConfigData = NetrunArtConfigData.shipped()
	var c: Dictionary = cfg.hq_page
	var dv: Dictionary = cfg.dive
	var ref_w: float = cfg.rig["ref_w"]
	var ref_h: float = cfg.rig["ref_h"]
	var yw: float = deg_to_rad(float(dv["hq_yaw_l36"]))
	var pt: float = deg_to_rad(float(dv["hq_pitch"]))
	var fwd: Array = [cos(yw) * cos(pt), sin(yw) * cos(pt), -sin(pt)]
	var right: Array = [sin(yw), -cos(yw), 0.0]
	var up: Array = NetrunArtUnits.cross3(right, fwd)
	var pts: Array = []
	for n: Dictionary in net["nodes"]:
		var st: String = n["state"]
		if st == "core" or st == "owned" or st == "corporate":
			pts.append(n["lot"])
	if pts.is_empty():
		for n: Dictionary in net["nodes"]:
			pts.append(n["lot"])
	var xs: Array = []
	var ys: Array = []
	for p: Array in pts:
		xs.append(p[0] * right[0] + p[1] * right[1])
		ys.append(p[0] * up[0] + p[1] * up[1])
	var margin: float = c["fit_margin"]
	var share: float = c["fit_share"]
	var bw: float = float(xs.max()) - float(xs.min()) + 2.0 * margin
	var bh: float = float(ys.max()) - float(ys.min()) + 2.0 * margin
	var fr: Array = c["free"]
	var fw: float = (float(fr[2]) - float(fr[0])) / ref_w
	var fh: float = (float(fr[3]) - float(fr[1])) / ref_h
	var ortho: float = maxf(bw / (share * fw), (bh * ref_w / ref_h) / (share * fh))
	var clamp_r: Array = c["ortho_clamp"]
	ortho = minf(float(clamp_r[1]), maxf(float(clamp_r[0]), ortho))
	ortho = minf(ortho, float(c["grid_ortho"]))
	var cx: float = (float(xs.max()) + float(xs.min())) / 2
	var cy: float = (float(ys.max()) + float(ys.min())) / 2
	var vw: float = ortho
	var vh: float = ortho * ref_h / ref_w
	var anchor: Array = c["anchor"]
	var tx: float = cx + (0.5 - float(anchor[0])) * vw
	var ty: float = cy - (0.5 - float(anchor[1])) * vh
	var a11: float = right[0]
	var a12: float = right[1]
	var a21: float = up[0]
	var a22: float = up[1]
	var det: float = a11 * a22 - a12 * a21
	return [[(tx * a22 - a12 * ty) / det, (a11 * ty - tx * a21) / det, 0.0], ortho]


## The HQ page camera as a perspective pose (orthographic emulated by a long lens).
static func hq_page_pose(target: Array, width: float) -> NetrunPose:
	var cfg: NetrunArtConfigData = NetrunArtConfigData.shipped()
	var dv: Dictionary = cfg.dive
	var sensor: float = cfg.rig["sensor_mm"]
	return NetrunPose.make(target, yaw_to_rig(float(dv["hq_yaw_l36"])), dv["hq_pitch"],
		width * float(dv["hq_lens"]) / sensor, dv["hq_lens"])


## The dive camera at `u` (0 = HQ page, 1 = street OVERVIEW), pitch lagging.
static func dive_pose(u: float, hq: NetrunPose, ov: NetrunPose) -> NetrunPose:
	var cfg: NetrunArtConfigData = NetrunArtConfigData.shipped()
	var dv: Dictionary = cfg.dive
	var sensor: float = cfg.rig["sensor_mm"]
	var s: float = smootherstep(u)
	var sp: float = smootherstep(pow(minf(1.0, u * float(dv["lag_k"])), float(dv["lag_pow"])))
	var w0: float = hq.dist * sensor / hq.lens
	var w1: float = ov.dist * sensor / ov.lens
	var tg: Array = []
	for i in 3:
		tg.append(NetrunArtUnits.lerp_f(hq.F[i], ov.F[i], s))
	var yaw: float = NetrunArtUnits.lerp_f(hq.yaw, unwrap_yaw(ov.yaw, hq.yaw), s)
	var pit: float = NetrunArtUnits.lerp_f(hq.pitch, ov.pitch, sp)
	var w: float = exp(NetrunArtUnits.lerp_f(log(w0), log(w1), s))
	var lens: float = exp(NetrunArtUnits.lerp_f(log(hq.lens), log(ov.lens), s))
	return NetrunPose.make(tg, yaw, pit, w * lens / sensor, lens, NetrunArtUnits.lerp_f(0.0, ov.sx, s),
		NetrunArtUnits.lerp_f(0.0, ov.sy, s))


## Distance from the camera to the OVERVIEW target.
static func dive_distance(p: NetrunPose, ov: NetrunPose) -> float:
	var loc: Array = p.loc()
	var s: float = 0.0
	for i in 3:
		var d: float = loc[i] - ov.F[i]
		s += d * d
	return sqrt(s)


## The street rig constants plus `look_bias_sign` (stored in poses json `rig`).
static func street_rig_json() -> Dictionary:
	var cfg: NetrunArtConfigData = NetrunArtConfigData.shipped()
	return NetrunArtUnits.merge(cfg.rig, {"look_bias_sign": cfg.look_bias_sign})


## A copy of the dive constants.
static func dive_constants() -> Dictionary:
	return NetrunArtConfigData.shipped().dive.duplicate(true)
