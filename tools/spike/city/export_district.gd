extends Node
## ART-1 1D spike (b): exports the same district (CityDistrict, the game's own layout) for
## the Blender bake: every prism with its base colour, ink and roof-trim pick (the same
## picks the real-time path makes), the ground and lane-glow triangles (CityMeshKit, so
## both paths draw identical streets), the traffic lanes and the view cameras.
## Headless: godot --headless --path . res://tools/spike/city/export_district.tscn -- --out=<abs.json>

const CONFIG := preload("res://tools/spike/city/city_spike_config.tres")


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
	var cfg: CityConfig = CONFIG
	var d := CityDistrict.from_layout(cfg)
	var prisms := []
	for pr in d.prisms:
		var poly := []
		for q: Vector2 in pr["poly"]:
			poly.append([q.x, q.y])
		var key := int(pr["key"])
		var trim := float(pr["taper"]) > 0.05 and CityMeshKit.hash01(key, 42, 1) < cfg.roof_trim_share
		prisms.append({"poly": poly, "y0": pr["y0"], "h": pr["h"], "taper": pr["taper"], "key": key,
			"col": _c(CityMeshKit.base_color(cfg, pr)), "ink": _c(pr["ink"]), "trim": trim, "hq": pr.get("hq", false)})
	var views := {}
	for v: String in cfg.views:
		var cam := CityIsoCamera.for_view(cfg, v, Vector2(1920, 1080))
		views[v] = {"target": [cam.target.x, cam.target.y, cam.target.z], "ortho": cam.ortho,
			"lod": CityIsoCamera.lod_of(cfg, cam.ortho), "opacity": CityLod.opacity(cfg, CityIsoCamera.lod_of(cfg, cam.ortho)),
			"city": CityLod.city_share(cfg, CityIsoCamera.lod_of(cfg, cam.ortho)), "detail": CityLod.detail(cfg, cam.ortho)}
	var data := {"yaw": cfg.yaw_deg, "pitch": cfg.pitch_deg, "distance": cfg.camera_distance, "prisms": prisms,
		"ground": _tris(CityMeshKit.ground_mesh(cfg, d)), "lanes": _tris(CityMeshKit.lane_mesh(cfg, d)), "views": views,
		"ramp": [_c(cfg.ramp[0]), _c(cfg.ramp[1]), _c(cfg.ramp[2])], "sky": _c(cfg.sky),
		"window_colors": cfg.window_colors.map(func(c: Color) -> Array: return _c(c)), "window_share": cfg.window_share}
	var f := FileAccess.open(out, FileAccess.WRITE)
	f.store_string(JSON.stringify(data))
	f.close()
	print("EXPORT %s prisms=%d" % [out, prisms.size()])
	get_tree().quit()


static func _c(c: Color) -> Array:
	return [snappedf(c.r, 0.0001), snappedf(c.g, 0.0001), snappedf(c.b, 0.0001)]


## Triangles of mesh surface 0 as [[x, y, z] x3, [r, g, b]] (Godot world).
static func _tris(m: ArrayMesh) -> Array:
	var arr := m.surface_get_arrays(0)
	var v: PackedVector3Array = arr[Mesh.ARRAY_VERTEX]
	var c: PackedColorArray = arr[Mesh.ARRAY_COLOR]
	var idx: PackedInt32Array = arr[Mesh.ARRAY_INDEX] if arr[Mesh.ARRAY_INDEX] != null else PackedInt32Array()
	var out := []
	var n := idx.size() if idx.size() > 0 else v.size()
	for k in range(0, n, 3):
		var ia := idx[k] if idx.size() > 0 else k
		var ib := idx[k + 1] if idx.size() > 0 else k + 1
		var ic := idx[k + 2] if idx.size() > 0 else k + 2
		var col := c[ia]
		out.append([snappedf(v[ia].x, 0.01), snappedf(v[ia].y, 0.01), snappedf(v[ia].z, 0.01),
			snappedf(v[ib].x, 0.01), snappedf(v[ib].y, 0.01), snappedf(v[ib].z, 0.01),
			snappedf(v[ic].x, 0.01), snappedf(v[ic].y, 0.01), snappedf(v[ic].z, 0.01),
			snappedf(col.r, 0.001), snappedf(col.g, 0.001), snappedf(col.b, 0.001)])
	return out
