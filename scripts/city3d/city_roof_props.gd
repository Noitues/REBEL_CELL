class_name CityRoofProps
extends RefCounted
## ART-5 5e: the roof props of the one city (bible 4.1: from raid zoom; round 40 unified40.py
## city_building): AC units / vents, water tanks on legs, antennas with a red aircraft light
## and holo billboard panels standing on roofs. The models are the concept's own, exported
## by tools/art_pipeline/city/build_roof_props_v1.py (assets/city/roof_props/roof_props.glb,
## one node per prop, drawn at its middle size); this places them by the concept's rules
## (CityConfig.roof_*: flat roofs whose footprint is over 2 BU each way; 0-2 AC units, a
## tank on 18 %, an antenna on roofs over 22 BU at 45 %, a billboard on roofs over 14 BU at
## 16 %), with a per-building hash for every chance and spot (the concept's seeded random
## per building), the antenna and billboard scaled to the concept's size ranges. Pure apart
## from loading the read-only glTF.

const PATH := "res://assets/city/roof_props/roof_props.glb"
const AC := &"ac"
const TANK := &"tank"
const ANTENNA := &"antenna"
const BILLBOARDS: Array[StringName] = [&"billboard_0", &"billboard_1", &"billboard_2", &"billboard_3"]
## The concept's sizes: AC units keep this far inside the roof edge (BU, from the unit's
## centre: unified40 x0 + 0.4 .. x1 - 1.3 for a 0.9 x 0.7 unit), a tank 1 BU; the antenna's
## height and the billboard's width ranges, and the size the export drew each at (BU).
const AC_INSET := Vector2(0.85, 0.75)
const TANK_INSET := 1.0
const ANTENNA_H := Vector2(3.0, 7.0)
const ANTENNA_DRAWN := 5.0
const BILLBOARD_W := Vector2(4.0, 7.5)
const BILLBOARD_DRAWN := 5.75
## Hash salts (CityMeshKit.hash01) per choice.
const SALT := 5050

static var _meshes: Dictionary = {}


## Every prop name, in the export's order.
static func names() -> Array[StringName]:
	var out: Array[StringName] = [AC, TANK, ANTENNA]
	out.append_array(BILLBOARDS)
	return out


## The exported mesh of prop `prop_name` (null when the export is missing). Read-only: a
## caller that sets materials duplicates it first.
static func mesh_of(prop_name: StringName) -> Mesh:
	if _meshes.is_empty():
		var scene := load(PATH) as PackedScene if ResourceLoader.exists(PATH) else null
		if scene == null:
			return null
		var root := scene.instantiate()
		for mi in root.find_children("*", "MeshInstance3D", true, false):
			_meshes[StringName(mi.name)] = (mi as MeshInstance3D).mesh
		root.free()
	return _meshes.get(prop_name)


## The props on prisms `idx` of `prisms` (CityModel.prisms): prop name -> Array of
## Transform3D (world), in prism order. `skip` (prism index -> true) leaves prisms out.
static func place(cfg: CityConfig, prisms: Array[Dictionary], idx: PackedInt32Array, skip: Dictionary = {}) -> Dictionary:
	var out := {}
	for nm in names():
		var list: Array[Transform3D] = []
		out[nm] = list
	for n in idx:
		if skip.has(n):
			continue
		var pr: Dictionary = prisms[n]
		if float(pr.get("taper", 0.0)) < cfg.roof_prop_min_top_scale:
			continue
		var poly: PackedVector2Array = pr["poly"]
		var lo := Vector2(INF, INF)
		var hi := -lo
		for p in poly:
			lo = lo.min(p)
			hi = hi.max(p)
		if hi.x - lo.x <= cfg.roof_prop_min_side or hi.y - lo.y <= cfg.roof_prop_min_side:
			continue
		var top := float(pr["y0"]) + float(pr["h"])
		var h := float(pr["h"])
		var key := int(pr["key"])
		var mid := (lo + hi) * 0.5
		# The concept spots props in the roof's bounding box; on a turned or odd footprint a
		# spot off the roof itself is left out (ART-5 5e: no prop floats over the street).
		var mid_on := Geometry2D.is_point_in_polygon(mid, poly)
		var ac_n := mini(cfg.roof_ac_max, floori(CityMeshKit.hash01(key, SALT, 0) * float(cfg.roof_ac_max + 1)))
		for k in ac_n:
			var at := _spot(key, 1 + k * 2, lo + AC_INSET, hi - AC_INSET)
			if not Geometry2D.is_point_in_polygon(at, poly):
				continue
			(out[AC] as Array).append(Transform3D(Basis(), Vector3(at.x, top, at.y)))
		if CityMeshKit.hash01(key, SALT, 10) < cfg.roof_tank_share:
			var at := _spot(key, 11, lo + Vector2(TANK_INSET, TANK_INSET), hi - Vector2(TANK_INSET, TANK_INSET))
			if Geometry2D.is_point_in_polygon(at, poly):
				(out[TANK] as Array).append(Transform3D(Basis(), Vector3(at.x, top, at.y)))
		if mid_on and h > cfg.roof_antenna_above and CityMeshKit.hash01(key, SALT, 20) < cfg.roof_antenna_share:
			var hh := lerpf(ANTENNA_H.x, ANTENNA_H.y, CityMeshKit.hash01(key, SALT, 21))
			(out[ANTENNA] as Array).append(Transform3D(Basis().scaled(Vector3(1.0, hh / ANTENNA_DRAWN, 1.0)), Vector3(mid.x, top, mid.y)))
		if mid_on and h > cfg.roof_billboard_above and CityMeshKit.hash01(key, SALT, 30) < cfg.roof_billboard_share:
			var wv := lerpf(BILLBOARD_W.x, BILLBOARD_W.y, CityMeshKit.hash01(key, SALT, 31))
			var pick := mini(BILLBOARDS.size() - 1, floori(CityMeshKit.hash01(key, SALT, 32) * BILLBOARDS.size()))
			var s := wv / BILLBOARD_DRAWN
			(out[BILLBOARDS[pick]] as Array).append(Transform3D(Basis().scaled(Vector3(s, s, s)), Vector3(mid.x, top, mid.y)))
	return out


## A spot in the box lo..hi (world X/Z) from building `key`'s hash `salt` (the box's middle
## when it is empty).
static func _spot(key: int, salt: int, lo: Vector2, hi: Vector2) -> Vector2:
	if hi.x < lo.x or hi.y < lo.y:
		return (lo + hi) * 0.5
	return Vector2(lerpf(lo.x, hi.x, CityMeshKit.hash01(key, SALT, salt)), lerpf(lo.y, hi.y, CityMeshKit.hash01(key, SALT, salt + 1)))
