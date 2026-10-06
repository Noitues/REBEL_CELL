class_name CityMotionMeshes
extends RefCounted
## ART-5 5c: the meshes of the city's motion layers, sized from CityMotionConfigData. Car
## tiers (ART_BIBLE §4.1 car LOD; X = heading with the nose at 0, Y up, Z side; CUSTOM0 =
## (part, stretch) for `shaders/city/sky_car.gdshader`), the beam cone, the police chopper and
## drone for ToonInkMaterial. The CLOSE car, chopper and drone are the art pass's own models
## (exported from the concept round's builders, see the consts below); FAR and MEDIUM car
## tiers, the street car and the lane line are procedural, as in the concept (a dot, a box).
## Builders only.

## The art pass's vehicles (tools/art_pipeline/parity/blender_export_vehicles.py runs the concept
## round's own builders in Blender): the CLOSE car as triangles with part ids (a MultiMesh car
## needs per-vertex CUSTOM0, and an imported mesh cannot be read back headless; the same car is
## `flying_car.glb`), the chopper and the drone as glb models.
const CAR_TRIS := preload("res://assets/city/vehicles/flying_car_tris.json")
const CHOPPER_MODEL := preload("res://assets/city/vehicles/chopper.glb")
const DRONE_MODEL := preload("res://assets/city/vehicles/drone.glb")

## Car parts (CUSTOM0.x), as sky_car.gdshader reads them.
enum Part { BODY, LANE, HEAD, TAIL, CABIN, GLOW }


## Car tier `tier` (CitySkyTraffic.CarTier): FAR a head dot + a lane-colour line; MEDIUM a
## small box in the lane colour (translucent) + its line; CLOSE the low-poly flying car
## (wedge body, dark cabin, lane stripes, under-glow, head / tail lights) + a thick line.
## The line runs from behind the body to its stretch end (pushed back by each car's streak).
static func car(cfg: CityMotionConfigData, tier: int) -> ArrayMesh:
	var b := _Builder.new()
	match tier:
		CitySkyTraffic.CarTier.FAR:
			var w := cfg.far_line * 0.5
			b.line(0.0, w, Part.LANE)
			var d := cfg.far_dot * 0.5
			b.box(Vector3(-d, -d, -d), Vector3(d, d, d), Part.HEAD)
		CitySkyTraffic.CarTier.MEDIUM:
			var s := cfg.medium_box
			b.box(Vector3(-s.x, -s.y * 0.5, -s.z * 0.5), Vector3(0.0, s.y * 0.5, s.z * 0.5), Part.BODY)
			b.line(-s.x, cfg.medium_line * 0.5, Part.LANE)
			b.box(Vector3(-0.2, -0.15, -s.z * 0.4), Vector3(0.05, 0.1, s.z * 0.4), Part.HEAD)
		_:
			var l := cfg.close_length
			b.concept_car(CAR_TRIS.data as Dictionary, l)
			b.line(-l, cfg.close_line * 0.5, Part.LANE)
	return b.mesh()


## A street car: a head (or tail) light and its short streak.
static func street_car(cfg: CityMotionConfigData) -> ArrayMesh:
	var b := _Builder.new()
	var d := cfg.street_dot * 0.5
	b.box(Vector3(-d, -d * 0.6, -d), Vector3(d, d * 0.6, d), Part.HEAD)
	b.line(0.0, d * 0.5, Part.LANE)
	return b.mesh()


## The unit beam cone: apex at the origin, open along -Y to radius 1 at length 1; UV.y
## runs 0 (apex) .. 1 (open end).
static func cone(sides: int = 16) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for k in sides:
		var a0 := TAU * float(k) / float(sides)
		var a1 := TAU * float(k + 1) / float(sides)
		var p0 := Vector3(cos(a0), -1.0, sin(a0))
		var p1 := Vector3(cos(a1), -1.0, sin(a1))
		for p in [Vector3.ZERO, p0, p1]:
			var v: Vector3 = p
			st.set_normal(Vector3(v.x, 0.3, v.z).normalized() if v != Vector3.ZERO else Vector3(cos((a0 + a1) * 0.5), 0.3, sin((a0 + a1) * 0.5)).normalized())
			st.set_uv(Vector2(float(k) / float(sides), -v.y))
			st.add_vertex(v)
	return st.commit()


## The art pass's police chopper (district20 `heli_geo`) `length` BU long, X = heading; see
## `aircraft()`. Its rotor is `rotor()`, sized and lifted by the model's blades.
static func chopper(length: float) -> Dictionary:
	return aircraft(CHOPPER_MODEL, length)


## An aircraft of the art pass (district20 `heli_geo` / `drone_geo` through Blender, the glb in
## assets/city/vehicles) fitted to `size` BU along X (its body, blades excluded). Returns
## {body: Mesh, neon: Mesh, scale: float, offset: Vector3, rotor_y: float, rotor_r: float}: the
## meshes are in the glb's own units, so a view scales them by `scale` and moves them by `offset`
## (the body's centre onto the node origin); the rotor values (where the concept's blades sat and
## their radius) are already scaled, 0 when the model has no blades. The body's vertex colours are
## tones relative to the concept's body colour (the material albedo stays the tuned body tone);
## `neon` carries the concept's lit parts in their own colours.
static func aircraft(model: PackedScene, size: float) -> Dictionary:
	var out := {"body": null, "neon": null, "scale": 1.0, "offset": Vector3.ZERO, "rotor_y": 0.0, "rotor_r": 0.0}
	var root := model.instantiate()
	var meshes := {}
	for n in root.find_children("*", "MeshInstance3D", true, false):
		var mi := n as MeshInstance3D
		meshes[String(mi.name)] = mi.mesh
	root.free()
	var body: Mesh = meshes.get("body")
	var box := body.get_aabb()
	var k := size / maxf(box.size.x, 0.001)
	out["body"] = body
	out["neon"] = meshes.get("neon")
	out["scale"] = k
	out["offset"] = -box.get_center() * k
	if meshes.has("blades"):
		var blades := (meshes["blades"] as Mesh).get_aabb()
		out["rotor_y"] = (blades.get_center().y - box.get_center().y) * k
		out["rotor_r"] = blades.size.x * 0.5 * k
	return out


## A rotor disc of radius `r` (flat, for the blur material).
static func rotor(r: float) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var n := 20
	for k in n:
		var a0 := TAU * float(k) / float(n)
		var a1 := TAU * float(k + 1) / float(n)
		for v in [Vector3.ZERO, Vector3(cos(a0), 0.0, sin(a0)) * r, Vector3(cos(a1), 0.0, sin(a1)) * r]:
			st.set_normal(Vector3.UP)
			st.set_uv(Vector2(float(k) / float(n), (v as Vector3).length() / r))
			st.add_vertex(v)
	return st.commit()


## The art pass's quad drone (district20 `drone_geo`) `size` BU across; see `aircraft()`.
static func drone(size: float) -> Dictionary:
	return aircraft(DRONE_MODEL, size)


## Collects boxes into one triangle mesh with flat normals and CUSTOM0 = (part, stretch).
class _Builder:
	var v := PackedVector3Array()
	var n := PackedVector3Array()
	var c := PackedFloat32Array()

	func box(lo: Vector3, hi: Vector3, part: int) -> void:
		var p := [Vector3(lo.x, lo.y, lo.z), Vector3(hi.x, lo.y, lo.z), Vector3(hi.x, lo.y, hi.z), Vector3(lo.x, lo.y, hi.z),
			Vector3(lo.x, hi.y, lo.z), Vector3(hi.x, hi.y, lo.z), Vector3(hi.x, hi.y, hi.z), Vector3(lo.x, hi.y, hi.z)]
		var faces := [[0, 3, 2, 1, Vector3.DOWN], [4, 5, 6, 7, Vector3.UP], [0, 1, 5, 4, Vector3.FORWARD],
			[1, 2, 6, 5, Vector3.RIGHT], [2, 3, 7, 6, Vector3.BACK], [3, 0, 4, 7, Vector3.LEFT]]
		for f in faces:
			var nrm: Vector3 = f[4]
			_tri(p[f[0]], p[f[1]], p[f[2]], nrm, part, 0.0, 0.0, 0.0)
			_tri(p[f[0]], p[f[2]], p[f[3]], nrm, part, 0.0, 0.0, 0.0)

	## One triangle facing `nrm` (Godot's front faces wind clockwise: the right-hand normal
	## points away from the viewer), with each corner's stretch.
	func _tri(a: Vector3, b: Vector3, d: Vector3, nrm: Vector3, part: int, sa: float, sb: float, sd: float) -> void:
		var pts := [a, b, d]
		var st := [sa, sb, sd]
		if (b - a).cross(d - a).dot(nrm) > 0.0:
			pts = [a, d, b]
			st = [sa, sd, sb]
		for k in 3:
			v.append(pts[k])
			n.append(nrm)
			c.append_array([float(part), float(st[k]), 0.0, 0.0])

	## A line from x = `x0` back to its stretch end (x0, stretch 1), `w` half-width.
	func line(x0: float, w: float, part: int) -> void:
		var p := [Vector3(x0, -w, -w), Vector3(x0, -w, w), Vector3(x0, w, w), Vector3(x0, w, -w)]
		# Four long faces between the head ring (stretch 0) and the tail ring (stretch 1); the
		# tail ring sits a hair behind so the faces are never degenerate before stretching.
		var back := Vector3(-0.01, 0.0, 0.0)
		for k in 4:
			var a: Vector3 = p[k]
			var b: Vector3 = p[(k + 1) % 4]
			var nrm := ((a + b) * 0.5 - Vector3(x0, 0.0, 0.0)).normalized()
			_tri(a, b, b + back, nrm, part, 0.0, 0.0, 1.0)
			_tri(a, b + back, a + back, nrm, part, 0.0, 1.0, 1.0)

	## The art pass's flying car (`flying_car_tris.json`, unified38.flying_car through Blender) `l` long:
	## concept axes (nose +X, up +Z, side Y) become the game's (nose at X = 0, tail at -l, Y up, Z side;
	## a proper rotation, so the winding holds), centred vertically on the body; each triangle keeps
	## the part id the export classified.
	func concept_car(data: Dictionary, l: float) -> void:
		var tris: Array = data["tris"]
		var xmin := INF
		var xmax := -INF
		var zmin := INF
		var zmax := -INF
		for t in tris:
			for p in t:
				xmin = minf(xmin, float(p[0]))
				xmax = maxf(xmax, float(p[0]))
				zmin = minf(zmin, float(p[2]))
				zmax = maxf(zmax, float(p[2]))
		var k := l / maxf(xmax - xmin, 0.001)
		var zmid := (zmin + zmax) * 0.5
		for t in tris:
			var pts: Array[Vector3] = []
			for p in t:
				pts.append(Vector3((float(p[0]) - xmax) * k, (float(p[2]) - zmid) * k, -float(p[1]) * k))
			var nrm := (pts[1] - pts[0]).cross(pts[2] - pts[0])
			if nrm.length() < 1e-9:
				continue
			_tri(pts[0], pts[1], pts[2], nrm.normalized(), int(t[0][3]), 0.0, 0.0, 0.0)

	func mesh(normals_only: bool = false) -> ArrayMesh:
		var arr := []
		arr.resize(Mesh.ARRAY_MAX)
		arr[Mesh.ARRAY_VERTEX] = v
		arr[Mesh.ARRAY_NORMAL] = n
		var flags := 0
		if not normals_only:
			arr[Mesh.ARRAY_CUSTOM0] = c
			flags = Mesh.ARRAY_CUSTOM_RGBA_FLOAT << Mesh.ARRAY_FORMAT_CUSTOM0_SHIFT
		var cols := PackedColorArray()
		cols.resize(v.size())
		cols.fill(Color.WHITE)
		arr[Mesh.ARRAY_COLOR] = cols
		var m := ArrayMesh.new()
		m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr, [], {}, flags)
		return m
