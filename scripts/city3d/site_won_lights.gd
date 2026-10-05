class_name SiteWonLights
extends MultiMeshInstance3D
## ART-5 5d, D17 (fight won: the building's lights turn Cell colours): the lit windows of
## every Site building the Cell has won (cleared or claimed, not DOWN: no power) as one
## MultiMesh of small unshaded window quads in Cell pink and lime on the building's walls,
## for 5a's CityView3D `fx` layer (`add_to_layer(&"fx", lights)`). Window placement is a
## pure function of the CityModel and the Site lots (`windows_for`), so it is tested
## headless; colours come from SiteMarker.won_light (deterministic by Site id). A view.

## Window rows per wall and their span of the wall's height, the step along a wall, the
## window's size and how far it stands off the wall (BU).
const ROWS := 4
const ROW_SPAN := 0.8
const STEP_BU := 2.2
const WINDOW_BU := Vector2(0.9, 0.6)
const OFFSET_BU := 0.05


func _init() -> void:
	name = "SiteWonLights"
	cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


## The windows of Site lots `won` (id -> lot point) on `model`: [{site, pos: Vector3,
## normal: Vector3, color}] in Site id order, each wall's windows in row order.
static func windows_for(model: CityModel, won: Dictionary) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var ids := won.keys()
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ids:
		var lot := Vector2i((won[id] as Vector2).floor())
		var key := Vector2i(floori(float(lot.x) / model.cfg.chunk_lots), floori(float(lot.y) / model.cfg.chunk_lots))
		if not model.chunks.has(key):
			continue
		var i := 0
		for n: int in model.chunks[key]["prisms"]:
			var pr := model.prisms[n]
			if not (pr["cell"] as Rect2i).has_point(lot):
				continue
			var poly: PackedVector2Array = pr["poly"]
			var y0 := float(pr["y0"])
			var h := float(pr["h"])
			var c: Vector2 = pr["centre"]
			for e in poly.size():
				var a := poly[e]
				var b := poly[(e + 1) % poly.size()]
				var mid := (a + b) * 0.5
				var nrm := (mid - c).normalized()
				var steps := maxi(1, floori(a.distance_to(b) / STEP_BU))
				for r in ROWS:
					var y := y0 + h * ROW_SPAN * (float(r) + 1.0) / float(ROWS + 1)
					for s in steps:
						var q := a.lerp(b, (float(s) + 0.5) / float(steps)) + nrm * OFFSET_BU
						out.append({"site": id, "pos": Vector3(q.x, y, q.y), "normal": Vector3(nrm.x, 0.0, nrm.y), "color": SiteMarker.won_light(id, i)})
						i += 1
	return out


## Builds the lights of Site lots `won` (id -> lot point) on `model`.
func build(model: CityModel, won: Dictionary) -> void:
	var wins := windows_for(model, won)
	var quad := QuadMesh.new()
	quad.size = WINDOW_BU
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.vertex_color_use_as_albedo = true
	mat.cull_mode = BaseMaterial3D.CULL_DISABLED
	quad.material = mat
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.mesh = quad
	mm.instance_count = wins.size()
	for k in wins.size():
		var w: Dictionary = wins[k]
		var nrm: Vector3 = w["normal"]
		var basis := Basis.looking_at(-nrm if nrm.length() > 0.0 else Vector3.FORWARD, Vector3.UP)
		mm.set_instance_transform(k, Transform3D(basis, w["pos"]))
		mm.set_instance_color(k, w["color"])
	multimesh = mm
