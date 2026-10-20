class_name HqPlateExport
extends RefCounted
## HQ-EXPORT (art-pass A-042): the data an HQ plate is rendered from, written from the game's own objects: the staged
## compound (HqCompoundStage), the city around its lot (the street export's building records), the run page's rooms
## (HqRunView) and the camera the page frames (HqCompoundStage.run_camera, read from the view). Canonical text as
## NetrunArtExport.canonical. Pure data out; reads, never changes game state. Schema: docs/handoff/netrun_art/plate_inputs/HQ_EXPORT.md.

## Contract version written in every file.
const VERSION: int = 1


## The files of `corp`'s HQ view `view_name` ("overview") for the page `view` (an HqRunView already shown with `show_run`),
## the city `model` and the page size `px`: {file name: canonical text}. `reach_lots` is how far (lots) round the HQ lot the
## ring city runs. `run_id` names the run in the files.
static func files(corp: StringName, view: HqRunView, model: CityModel, cfg: CityConfig, px: Vector2i, reach_lots: int,
		view_name: String, run_id: String) -> Dictionary:
	var out := {}
	out["hq_compound.json"] = NetrunArtExport.canonical(compound_json(corp, view, model, cfg, reach_lots))
	out["run_graph.json"] = NetrunArtExport.canonical(rooms_json(view, run_id))
	out["hq_%s_capture.json" % view_name] = NetrunArtExport.canonical(capture_json(corp, view, model, px, view_name, run_id))
	return out


## `hq_compound.json`: the landmark id, the site lot, the compound's parts as placed and the ring city round the lot.
static func compound_json(corp: StringName, view: HqRunView, model: CityModel, cfg: CityConfig, reach_lots: int) -> Dictionary:
	var m := HqCompoundStage.manifest(corp)
	var at := view.compound_at()
	var hq_rect: Rect2i = model.hqs.get(corp, Rect2i())
	var lot := HqCompoundStage.place_lot(corp, m, hq_rect)
	var fp := HqCompoundStage.footprint_rect(m, at)
	var path := HqCompoundStage.model_path(corp, m)
	var fp_max: Array = (m.get("footprint", {}) as Dictionary).get("max", [0, 0, 0])
	return {"version": VERSION, "corp": String(corp), "landmark": String(corp), "units": "BU",
		"layout_seed": ArtSeed.u64_str(model.city_seed), "lot_bu": cfg.lot_bu,
		"site": {"hq_rect": _rect(hq_rect), "place_lot": [lot.x, lot.y], "place_lot_source": "manifest" if m.get("place_lot") is Array else "hq_rect",
			"origin_lot": [cfg.district_centre.x, cfg.district_centre.y]},
		"compound": {"glb": path, "manifest": "%s/%s/manifest.json" % [HqCompoundStage.ASSETS_DIR, corp],
			"transform": xf(at), "plan_origin": plan(at.origin),
			"footprint": {"world_rect": [fp.position.x, fp.position.y, fp.size.x, fp.size.y],
				"plan_corners": _plan_corners(fp), "height": float(fp_max[1])}},
		"parts": parts(path, at),
		"ring": ring(model, cfg, hq_rect, reach_lots)}


## The mesh parts of the compound's glTF at `path` placed at `at`: [{name, tris, aabb, local, world}] sorted by node path.
## `local` is the part's transform in the compound frame, `world` is `at * local`.
static func parts(path: String, at: Transform3D) -> Array:
	var out := []
	if path == "" or not ResourceLoader.exists(path):
		return out
	var scene := load(path) as PackedScene
	if scene == null:
		return out
	var root := scene.instantiate() as Node3D
	for n: Node in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		var local := _local(mi, root)
		var bb := mi.mesh.get_aabb() if mi.mesh != null else AABB()
		out.append({"name": String(root.get_path_to(mi)), "tris": mi.mesh.get_faces().size() / 3 if mi.mesh != null else 0,
			"aabb": [bb.position.x, bb.position.y, bb.position.z, bb.size.x, bb.size.y, bb.size.z],
			"local": xf(local), "world": xf(at * local)})
	root.free()
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return String(a["name"]) < String(b["name"]))
	return out


## The buildings, streets and plazas of the city within `reach_lots` of the HQ lot, in city.json's records (all HQ rects too).
static func ring(model: CityModel, cfg: CityConfig, hq_rect: Rect2i, reach_lots: int) -> Dictionary:
	var cj := NetrunArtExport.city_json(model.city_seed, cfg.lot_bu, cfg.district_centre, model.prisms, model.streets, model.plazas,
		model.hqs, model.city_sections())
	var box := hq_rect.grow(reach_lots)
	var buildings := []
	for b: Dictionary in cj["buildings"]:
		var c: Array = b["cell"]
		if bool(b["hq"]) or box.intersects(Rect2i(c[0], c[1], c[2], c[3])):
			buildings.append(b)
	var streets := []
	for s: Dictionary in cj["streets"]:
		if box.has_point(Vector2i(s["lot"][0], s["lot"][1])):
			streets.append(s)
	var plazas := []
	for p: Dictionary in cj["plazas"]:
		if box.has_point(Vector2i(p["lot"][0], p["lot"][1])):
			plazas.append(p)
	return {"reach_lots": reach_lots, "window": _rect(box), "buildings": buildings, "streets": streets, "plazas": plazas, "hqs": cj["hqs"],
		"origin_lot": cj["origin_lot"]}


## `run_graph.json` of the HQ page: the rooms as the page lays them out (kind, state, number, the box on the compound) and the edges.
static func rooms_json(view: HqRunView, run_id: String) -> Dictionary:
	var g := view.graph
	var rooms := []
	var ids: Array = []
	for n in g.all_nodes():
		ids.append(String(n["id"]))
	IdSort.sort_ids(ids)
	var bu_px := view.iso.bu_per_px()
	for sid: String in ids:
		var id := StringName(sid)
		var n := g.get_node(id)
		var w := view.world_of(id)
		var slot := w != Vector3.INF
		var r := view.node_radius(id) * bu_px
		var kind := view.kind_of(id)
		rooms.append({"id": sid, "layer": int(n["layer"]), "index": int(n["index"]), "kind": kind, "state": view.state_of(id),
			"number": view.number_of(id), "server": kind == CityMapOverlay.KIND_RACK, "has_slot": slot,
			"point": _v3(w) if slot else [], "plan": plan(w) if slot else [],
			"box": [w.x - r, w.y, w.z - r, w.x + r, w.y + r, w.z + r] if slot else []})
	var edges := []
	for l: Dictionary in view.links():
		edges.append({"a": String(l["from"]), "b": String(l["to"]), "state": String(l["state"])})
	var entry := view.entry_world()
	return {"version": VERSION, "run": run_id, "corp": String(view.corp), "layers": g.layer_count(), "rooms": rooms, "edges": edges,
		"slots": slots(view.corp, view.compound_at()),
		"entry": _v3(entry), "entry_plan": plan(entry),
		"box_note": "[min x, y, z, max x, y, z] in world BU: the sticker radius at the page's scale round the room point, one radius up"}


## Every slot of `corp`'s compound layout in the world (placed at `at`): the layered rows (1-based layer, 0-based slot) and the
## Central Server, whether or not today's run map uses them: [{layer, slot, point, plan}] (the server has slot -1, layer 0).
static func slots(corp: StringName, at: Transform3D) -> Array:
	var out := []
	var l := HqCompoundStage.layout(corp)
	if l == null:
		return out
	for layer in range(1, l.layer_rows() + 1):
		for s in l.slots_per_layer:
			var w := at * l.slot_position(layer, s)
			out.append({"layer": layer, "slot": s, "point": _v3(w), "plan": plan(w)})
	var sw := at * l.central_server
	out.append({"layer": 0, "slot": -1, "point": _v3(sw), "plan": plan(sw)})
	return out


## `hq_<view>_capture.json`: the camera the page framed (the street capture's keys: loc, tgt, lens, shift, yaw, pitch, resolution).
static func capture_json(corp: StringName, view: HqRunView, model: CityModel, px: Vector2i, view_name: String, run_id: String) -> Dictionary:
	var c := view.iso
	var eye := c.eye()
	return {"version": VERSION, "kind": "hq", "view": view_name, "corp": String(corp), "run": run_id, "look": "mainline",
		"layout_seed": ArtSeed.u64_str(model.city_seed), "time": "night", "resolution": [px.x, px.y],
		"camera": {"projection": "perspective" if c.perspective() else "orthogonal", "loc": _v3(eye), "tgt": _v3(c.target),
			"plan_loc": plan(eye), "plan_tgt": plan(c.target), "yaw": c.yaw_deg, "pitch": c.pitch_deg, "dist": c.eye_distance(),
			"ortho_scale": c.ortho, "fov": c.fov_deg, "lens": 0.0, "shift_x": 0.0, "shift_y": 0.0,
			"note": "yaw / pitch are CityIsoCamera degrees (view direction cos(yaw)cos(pitch), -sin(pitch), -sin(yaw)cos(pitch) in world); lens 0 = orthographic, shift 0 = the frame is centered on tgt"}}


## A transform as 12 floats: basis x, y, z columns, then the origin.
static func xf(t: Transform3D) -> Array:
	return [t.basis.x.x, t.basis.x.y, t.basis.x.z, t.basis.y.x, t.basis.y.y, t.basis.y.z, t.basis.z.x, t.basis.z.y, t.basis.z.z,
		t.origin.x, t.origin.y, t.origin.z]


## The transform of `a` (12 floats from `xf`).
static func from_xf(a: Array) -> Transform3D:
	return Transform3D(Basis(Vector3(a[0], a[1], a[2]), Vector3(a[3], a[4], a[5]), Vector3(a[6], a[7], a[8])), Vector3(a[9], a[10], a[11]))


## A world point in the plan frame of city.json: [x, -z, height].
static func plan(w: Vector3) -> Array:
	return [w.x, -w.z, w.y]


static func _local(n: Node3D, root: Node3D) -> Transform3D:
	var t := Transform3D()
	var cur: Node = n
	while cur != root and cur is Node3D:
		t = (cur as Node3D).transform * t
		cur = cur.get_parent()
	return t


static func _plan_corners(r: Rect2) -> Array:
	return [[r.position.x, -r.position.y], [r.end.x, -r.position.y], [r.end.x, -r.end.y], [r.position.x, -r.end.y]]


static func _v3(v: Vector3) -> Array:
	return [v.x, v.y, v.z]


static func _rect(r: Rect2i) -> Array:
	return [r.position.x, r.position.y, r.size.x, r.size.y]
