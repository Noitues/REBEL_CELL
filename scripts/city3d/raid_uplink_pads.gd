class_name RaidUplinkPads
extends RefCounted
## ART-3 6w (bible v2 §4.8 raid language B, §4.1 "uplink pads and risers" from raid zoom): the
## raid's building nodes as uplink pads. Each of the Cell's nodes stands on a building (the map
## overlay's lot, CityMapOverlay.lot_of); its roof carries the concept's pad (a dark slab with a
## lime trim and a lime-capped mast) and three lime riser traces run up the building's corner
## that faces the node's street. The models are the concept's own, exported by
## tools/art_pipeline/raid/build_uplink_pads_v1.py (assets/raid/uplink/uplink_pads.glb: the pad
## drawn at half-size 1 BU on roof height 0, the riser at RISER_DRAWN BU tall); this places them
## by the concept's rule (half-size = `uplink_pad_share` x the roof's shorter side; roofs under
## `uplink_min_top` carry none). Pure apart from loading the read-only glTF.

const PATH := "res://assets/raid/uplink/uplink_pads.glb"
const PAD := &"uplink_pad"
const RISER := &"uplink_riser"
## The riser's drawn height (BU; the manifest's settings.riser_h).
const RISER_DRAWN := 10.0

static var _meshes: Dictionary = {}


## The exported mesh of piece `piece` (PAD or RISER; null when the export is missing).
## Read-only: a caller that sets materials duplicates it first.
static func mesh_of(piece: StringName) -> Mesh:
	if _meshes.is_empty():
		var scene := load(PATH) as PackedScene if ResourceLoader.exists(PATH) else null
		if scene == null:
			return null
		var root := scene.instantiate()
		for mi in root.find_children("*", "MeshInstance3D", true, false):
			_meshes[StringName(mi.name)] = (mi as MeshInstance3D).mesh
		root.free()
	return _meshes.get(piece)


## The pads of `nodes` ({"id", "lot": Vector2i (the node's building lot), "door": Vector2 (a
## lot point on its street)}) on `model`: {"id", "lot", "top" (BU), "half" (BU), "centre":
## Vector3 (the roof's middle, at the top), "corner": Vector3 (the footprint corner nearest the
## door, on the ground)}, in the nodes' order. A lot with no building, or a roof under
## `uplink_min_top`, gets none. The building is the tallest prism over the lot (ties by prism
## index); a tapered top shrinks the pad with the roof.
static func of(model: CityModel, cfg: CityConfig, nodes: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if model == null:
		return out
	for n in nodes:
		var lot: Vector2i = n["lot"]
		var pr := top_prism(model, lot)
		if pr.is_empty():
			continue
		var top := float(pr["y0"]) + float(pr["h"])
		if top < cfg.uplink_min_top:
			continue
		var poly: PackedVector2Array = pr["poly"]
		var lo := poly[0]
		var hi := poly[0]
		for q in poly:
			lo = lo.min(q)
			hi = hi.max(q)
		var c: Vector2 = pr["centre"]
		var ext := hi - lo
		var half := minf(ext.x, ext.y) * cfg.uplink_pad_share * clampf(float(pr["taper"]), 0.0, 1.0)
		var door := CityIsoCamera.lot_to_world(cfg, n.get("door", Vector2(lot) + Vector2(0.5, 0.5)))
		var best := 0
		for k in poly.size():
			if poly[k].distance_squared_to(Vector2(door.x, door.z)) < poly[best].distance_squared_to(Vector2(door.x, door.z)) - 0.0001:
				best = k
		out.append({"id": n["id"], "lot": lot, "top": top, "half": half, "centre": Vector3(c.x, top, c.y),
			"corner": Vector3(poly[best].x, 0.0, poly[best].y)})
	return out


## The tallest prism standing on lot `lot` ({} when none), ties by prism index.
static func top_prism(model: CityModel, lot: Vector2i) -> Dictionary:
	var cfg := model.cfg
	var key := Vector2i(floori(float(lot.x) / cfg.chunk_lots), floori(float(lot.y) / cfg.chunk_lots))
	if not model.chunks.has(key):
		return {}
	var best: Dictionary = {}
	var best_top := -INF
	for n: int in model.chunks[key]["prisms"]:
		var pr := model.prisms[n]
		if not (pr["cell"] as Rect2i).has_point(lot):
			continue
		var t := float(pr["y0"]) + float(pr["h"])
		if t > best_top:
			best_top = t
			best = pr
	return best


## Where the pad and riser of `pad` (an `of` record) stand: {PAD: Transform3D, RISER: Transform3D}
## (world; the pad scaled in X / Z to its half-size, the riser in Y to the roof).
static func transforms(pad: Dictionary) -> Dictionary:
	var h := float(pad["half"])
	var t := float(pad["top"])
	return {PAD: Transform3D(Basis.from_scale(Vector3(h, 1.0, h)), pad["centre"]),
		RISER: Transform3D(Basis.from_scale(Vector3(1.0, t / RISER_DRAWN, 1.0)), pad["corner"])}
