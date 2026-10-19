class_name NetrunPoseBuilder
extends RefCounted
## NA-21 twin of `tools/netrun_art/poses.py`: assembles the `poses_<run>.json` v1 dictionary from a derive v2 result.

## Poses file version.
const VERSION := 1
## The dive sample parameters.
const DIVE_SAMPLES: Array = [0.0, 0.25, 0.5, 0.75, 1.0]
## The fixture walk names.
const FIXTURE_WALKS: Array = ["first", "mid", "last"]


## Option ids after `node` (edge targets sorted by id), or the layer-1 nodes before the first step (`node` "" = None).
static func successors(run_graph: Dictionary, node: String) -> Array:
	var out: Array = []
	if node == "":
		var ln: Array = NetrunStreetDeriver.layer_nodes(run_graph)
		for n: Dictionary in ln[0][1]:
			out.append(n["id"])
		return out
	for e: Dictionary in run_graph["edges"]:
		if e["a"] == node:
			out.append(e["b"])
	IdSort.sort_ids(out)
	return out


## Three deterministic walks: none, half way, and up to the last layer (first successor at every step).
static func fixture_walks(run_graph: Dictionary) -> Dictionary:
	var n: int = run_graph["layers"]
	var walks: Dictionary = {"first": [], "mid": [], "last": []}
	var cur: String = ""
	var path: Array = []
	for step in range(1, n):
		var opts: Array = successors(run_graph, cur)
		cur = opts[0]
		path.append(cur)
		if step == maxi(1, n / 2):
			walks["mid"] = path.duplicate()
	walks["last"] = path.duplicate()
	return walks


static func _layer_of(run_graph: Dictionary, node: String) -> int:
	if node == "":
		return 0
	for n: Dictionary in run_graph["nodes"]:
		if n["id"] == node:
			return int(n["layer"])
	return 0


static func _make_ctx(derive: Dictionary, city: Dictionary, run_graph: Dictionary, net: Dictionary) -> Dictionary:
	var cx: Dictionary = {}
	cx["d"] = derive
	cx["city"] = city
	cx["g"] = run_graph
	cx["kind"] = derive["kind"]
	cx["rooms"] = derive["rooms"]
	cx["layers"] = run_graph["layers"]
	var ov: NetrunPose = NetrunPose.from_json(derive["overview"])
	var dec: NetrunPose = NetrunPose.from_json(derive["decision"])
	cx["ov"] = ov
	cx["dec"] = dec
	var skip: Dictionary = {}
	for r: Dictionary in derive["rooms"].values():
		skip[r["bld"]] = true
	cx["boxes"] = OcclusionHelper.building_boxes(city, skip)
	if cx["kind"] == "hq":
		var corp: String = String(derive["route_keys"][0]).split(":", true, 1)[1]
		var n_tiers: int = NetrunStreetDeriver.layer_nodes(run_graph).size()
		var comp: Dictionary = NetrunHqSlots.plan_compound(NetrunHqSlots.hq_lot_rect(city, corp), n_tiers)
		if comp.has("error"):
			return comp
		cx["comp"] = NetrunHqSlots.set_entrance(comp, ov, corp)
		var outlines: Dictionary = NetrunArtConfigData.shipped().face_outlines
		cx["outline"] = outlines.get(corp, [])
	cx["has_d0"] = false
	cx["d0"] = NAN
	if cx["kind"] == "street" and not net.is_empty():
		var cam: Array = NetrunCameraRig.hq_page_camera(net)
		var hq: NetrunPose = NetrunCameraRig.hq_page_pose(cam[0], cam[1])
		cx["hq"] = hq
		cx["d0"] = NetrunCameraRig.dive_distance(hq, ov)
		cx["has_d0"] = true
	cx["d1"] = ov.dist
	cx["d_ov"] = ov.dist
	cx["d_dec"] = dec.dist
	return cx


static func _decision(cx: Dictionary, current: String, options: Array) -> NetrunPose:
	var layer: int = _layer_of(cx["g"], current)
	if cx["kind"] == "hq":
		var li: int = maxi(0, layer - 1) if current != "" else 0
		return NetrunHqOrbit.hq_decision(cx["rooms"], current, options, li, cx["layers"], {}, cx["comp"]["entrance"])
	var u: float = NetrunCameraRig.street_u(cx["layers"], layer)
	var a: Array = cx["d"]["street"]["a"]
	return NetrunCameraRig.street_decision(cx["rooms"], current, options, u, cx["d"]["nrm"], cx["d"]["start_left"], {},
		[a[0], a[1], 0.0])


static func _hover(cx: Dictionary, dec: NetrunPose, node: String) -> NetrunPose:
	if cx["kind"] == "hq":
		return NetrunHqOrbit.hq_hover(dec, cx["rooms"][node])
	return NetrunCameraRig.street_hover(dec, cx["rooms"][node], cx["d"]["nrm"])


static func _record(cx: Dictionary, pose: NetrunPose, ids: Array, decision: bool = false) -> Dictionary:
	var loc: Array = pose.loc()
	var rooms: Dictionary = cx["rooms"]
	var pts: Array = _front_points(rooms, ids)
	var occ_pts: Array = pts
	if decision:
		# a DECISION cone targets EVERY route room in frame, the `ids` rooms included (art-pass 6d214ce9, NA-04c)
		var rcfg: Dictionary = NetrunArtConfigData.shipped().rig
		var is_hq: bool = cx["kind"] == "hq"
		var occ_ids: Array = OcclusionHelper.rooms_in_frame(rooms, pose, rcfg["ref_w"], rcfg["ref_h"], is_hq, not is_hq)
		for i: String in ids:
			if not occ_ids.has(i):
				occ_ids.append(i)
		IdSort.sort_ids(occ_ids)
		occ_pts = _front_points(rooms, occ_ids)
		occ_pts.append_array(_band(cx, pose, ids))
	var rec: Dictionary = {"pose": pose.to_json()}
	if cx["has_d0"]:
		rec["zoom_dive"] = RevealTiers.zoom_dive(NetrunCameraRig.dive_distance(pose, cx["ov"]), cx["d0"], cx["d1"])
	rec["zoom_detail"] = RevealTiers.zoom_detail(pose.dist, cx["d_ov"], cx["d_dec"])
	rec["lod_weights"] = RevealTiers.weights(pose.dist)
	rec["occlusion"] = OcclusionHelper.occlusion_block(OcclusionHelper.occlusion_params(loc, occ_pts), cx["boxes"])
	if cx["kind"] == "hq":
		var hs: float = cx["comp"]["half"][0]
		var sec_pts: Array = pts if ids != rooms.keys() else []
		rec["section"] = NetrunSection.section_params(loc, ["rect", hs, hs], sec_pts)
	return rec


## `poses_<run>.json` v1 for a street or HQ derive; `net` ({} = none) feeds the street dive's HQ page camera.
## Returns `{"error": ...}` if the HQ compound cannot be planned.
static func build_poses(derive: Dictionary, city: Dictionary, run_graph: Dictionary, net: Dictionary = {}) -> Dictionary:
	var cx: Dictionary = _make_ctx(derive, city, run_graph, net)
	if cx.has("error"):
		return cx
	var ov: NetrunPose = cx["ov"]
	var dec: NetrunPose = cx["dec"]
	var rooms: Dictionary = cx["rooms"]
	var first: Array = successors(run_graph, "")
	var room_ids: Array = rooms.keys()
	IdSort.sort_ids(room_ids)
	var out: Dictionary = {}
	out["version"] = VERSION
	out["run"] = derive["run"]
	out["layout_seed"] = derive["layout_seed"]
	out["kind"] = derive["kind"]
	out["overview"] = _record(cx, ov, room_ids)
	out["decision"] = _record(cx, dec, first, true)
	out["rig"] = NetrunCameraRig.street_rig_json() if cx["kind"] == "street" else NetrunHqOrbit.hq_rig()
	out["zoom"] = {"d_ov": cx["d_ov"], "d_dec": cx["d_dec"]}
	out["lod"] = RevealTiers.lod_block()
	out["section"] = NetrunSection.section_block()
	if cx["has_d0"]:
		var hq: NetrunPose = cx["hq"]
		out["zoom"]["d0"] = cx["d0"]
		out["zoom"]["d1"] = cx["d1"]
		var dv: Dictionary = NetrunCameraRig.dive_constants()
		var samples: Array = []
		for u: float in DIVE_SAMPLES:
			var dp: NetrunPose = NetrunCameraRig.dive_pose(u, hq, ov)
			samples.append({"u": u, "pose": dp.to_json(),
				"zoom_dive": RevealTiers.zoom_dive(NetrunCameraRig.dive_distance(dp, ov), cx["d0"], cx["d1"])})
		out["dive"] = {"hq_pose": hq.to_json(), "overview_pose": ov.to_json(), "duration_s": dv["duration_s"],
			"lag_k": dv["lag_k"], "lag_pow": dv["lag_pow"], "hq_lens": dv["hq_lens"], "samples": samples}
	var fixtures: Array = []
	var walks: Dictionary = fixture_walks(run_graph)
	for wname: String in walks:
		var walked: Array = walks[wname]
		var cur: String = walked[-1] if not walked.is_empty() else ""
		var opts: Array = successors(run_graph, cur)
		var d: NetrunPose = _decision(cx, cur, opts)
		var hov: NetrunPose = _hover(cx, d, opts[0])
		var ids: Array = []
		if cur != "":
			ids.append(cur)
		ids.append_array(opts)
		var current_v: Variant = cur if cur != "" else null
		fixtures.append({"name": wname, "walked": walked.duplicate(), "current": current_v, "options": opts,
			"hover": opts[0], "decision": _record(cx, d, ids, true), "hover_pose": hov.to_json()})
	out["fixtures"] = fixtures
	return out


## Face band of the current level (DECISION / HOVER only; spec 7.1 rule 1): the landmark's tier face on an HQ, the route
## building's face on a street.
static func _band(cx: Dictionary, pose: NetrunPose, ids: Array) -> Array:
	if ids.is_empty():
		return []
	var rcfg: Dictionary = NetrunArtConfigData.shipped().rig
	if cx["kind"] == "hq":
		return OcclusionHelper.hq_band_points(cx["rooms"], ids, cx["comp"]["centre"], pose, rcfg["ref_w"], rcfg["ref_h"],
			0.0, cx["outline"])
	var ext: Dictionary = {}
	for i: String in ids:
		var bid: String = cx["rooms"][i]["bld"]
		ext[bid] = OcclusionHelper.building_extent(cx["city"], bid)
	return OcclusionHelper.street_band_points(cx["rooms"], ids, ext, pose, rcfg["ref_w"], rcfg["ref_h"])


## The front-quad corner points (ground_z added to z) of the rooms `ids`, in the order given.
static func _front_points(rooms: Dictionary, ids: Array) -> Array:
	var pts: Array = []
	for i: String in ids:
		var gz: float = rooms[i].get("ground_z", 0.0)
		for q: Array in rooms[i]["front"]:
			pts.append([q[0], q[1], q[2] + gz])
	return pts
