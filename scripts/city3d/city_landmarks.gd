class_name CityLandmarks
extends RefCounted
## ART-5 5e: where 5b's landmark glTFs stand on the one city, as data both the 3D view
## (CityView3D places the models) and the map layer (NeonCity lifts the roofs the Site
## markers float over, headless too) read: the HQ landmarks on their HQ lots, the Cell's
## district on its district, and one Site landmark per corporation (`<corp>_site.glb`, the
## Site named by CityConfig.site_landmarks) on that Site's lot block. Boxes come from the
## models themselves (their meshes' bounds), cached per file. Pure apart from loading the
## read-only glTF scenes.

const DIR := "res://assets/city/landmarks"

## Model file -> {"box": AABB (model space), "top": float (BU)}.
static var _boxes: Dictionary = {}


## The Site landmark glTF of corporation `corp` ("" when 5b made none).
static func site_path(corp: StringName) -> String:
	var p := "%s/%s/%s_site.glb" % [DIR, corp, corp]
	return p if ResourceLoader.exists(p) else ""


## The Site that carries `corp`'s Site landmark (&"" when none).
static func site_of(cfg: CityConfig, corp: StringName) -> StringName:
	if site_path(corp) == "":
		return &""
	return StringName(cfg.site_landmarks.get(corp, &""))


## The lot point the Site landmark of `corp` stands on (its block's centre), from the
## Site's layout point (`points`: CityLayout.site_points), or Vector2.INF.
static func site_lot(cfg: CityConfig, corp: StringName, points: Dictionary) -> Vector2:
	var id := site_of(cfg, corp)
	if id == &"" or not points.has(id):
		return Vector2.INF
	return (points[id] as Vector2).floor() + Vector2(0.5, 0.5)


## The model-space box of every mesh in glTF `path` (cached; AABB() when it will not load).
static func box_of(path: String) -> AABB:
	if not _boxes.has(path):
		var out := AABB()
		var scene := load(path) as PackedScene if ResourceLoader.exists(path) else null
		if scene != null:
			var root := scene.instantiate() as Node3D
			var first := true
			for mi in root.find_children("*", "MeshInstance3D", true, false):
				var m := mi as MeshInstance3D
				if m.mesh == null:
					continue
				var xf := Transform3D()
				var n: Node = m
				while n != null and n != root:
					xf = (n as Node3D).transform * xf
					n = n.get_parent()
				var b := xf * m.mesh.get_aabb()
				out = b if first else out.merge(b)
				first = false
			root.free()
		_boxes[path] = out
	return _boxes[path]


## The lots a model at lot point `centre` covers (`share` of its ground box, as CityView3D
## clears the procedural buildings), as a Rect2 in lots.
static func lot_rect(cfg: CityConfig, path: String, centre: Vector2, share: float) -> Rect2:
	var b := box_of(path)
	if b.size == Vector3.ZERO:
		return Rect2()
	var w := CityIsoCamera.lot_to_world(cfg, centre)
	var lo := Vector3(w.x + b.position.x, 0.0, w.z + b.position.z)
	var hi := Vector3(w.x + b.end.x, 0.0, w.z + b.end.z)
	var c := (lo + hi) * 0.5
	var h := (hi - lo) * share * 0.5
	var a := CityIsoCamera.world_to_lot(cfg, c - h)
	var d := CityIsoCamera.world_to_lot(cfg, c + h)
	return Rect2(a.min(d), (a - d).abs())


## The top (BU) of glTF `path` (0 when it will not load).
static func top_of(path: String) -> float:
	return box_of(path).end.y
