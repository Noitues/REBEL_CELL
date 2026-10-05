class_name CityMotionMeshes
extends RefCounted
## ART-5 5c: the meshes of the city's motion layers, sized from CityMotionConfigData. Car
## tiers (ART_BIBLE §4.1 car LOD; X = heading with the nose at 0, Y up, Z side; CUSTOM0 =
## (part, stretch) for `shaders/city/sky_car.gdshader`), the beam cone, the low-poly police
## chopper and drone (round 6 / round 24 silhouettes) for ToonInkMaterial. Builders only.

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
			var w := l * 0.22
			b.wedge(l, w, l * 0.08, Part.BODY)
			b.box(Vector3(-l * 0.62, l * 0.08, -w * 0.7), Vector3(-l * 0.2, l * 0.2, w * 0.7), Part.CABIN)
			b.box(Vector3(-l * 0.95, -l * 0.01, -w * 1.02), Vector3(-l * 0.1, l * 0.02, w * 1.02), Part.LANE)
			b.box(Vector3(-l * 0.85, -l * 0.07, -w * 0.8), Vector3(-l * 0.15, -l * 0.05, w * 0.8), Part.GLOW)
			b.box(Vector3(-0.04, -l * 0.02, -w * 0.85), Vector3(0.04, l * 0.04, -w * 0.4), Part.HEAD)
			b.box(Vector3(-0.04, -l * 0.02, w * 0.4), Vector3(0.04, l * 0.04, w * 0.85), Part.HEAD)
			b.box(Vector3(-l - 0.04, -l * 0.02, -w * 0.9), Vector3(-l + 0.04, l * 0.03, w * 0.9), Part.TAIL)
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


## A police chopper `length` BU long (round 6 `heli`: cabin, tail boom, fin, skids); X =
## heading. Its rotor is `rotor()`.
static func chopper(length: float) -> ArrayMesh:
	var b := _Builder.new()
	var s := length / 3.6
	b.box(Vector3(-1.0, -0.85, -0.45) * s, Vector3(1.0, 0.0, 0.45) * s, Part.BODY)
	b.box(Vector3(-0.2, 0.0, -0.32) * s, Vector3(0.75, 0.32, 0.32) * s, Part.BODY)
	b.box(Vector3(-2.6, -0.62, -0.12) * s, Vector3(-0.9, -0.38, 0.12) * s, Part.BODY)
	b.box(Vector3(-2.65, -0.62, -0.05) * s, Vector3(-2.35, 0.25, 0.05) * s, Part.BODY)
	b.box(Vector3(-0.8, -1.05, -0.55) * s, Vector3(0.9, -0.97, -0.45) * s, Part.BODY)
	b.box(Vector3(-0.8, -1.05, 0.45) * s, Vector3(0.9, -0.97, 0.55) * s, Part.BODY)
	return b.mesh(true)


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


## A quad drone `size` BU across: a flat body and four arms.
static func drone(size: float) -> ArrayMesh:
	var b := _Builder.new()
	var h := size * 0.5
	b.box(Vector3(-h * 0.45, -h * 0.18, -h * 0.45), Vector3(h * 0.45, h * 0.12, h * 0.45), Part.BODY)
	b.box(Vector3(-h, -h * 0.06, -h * 0.08), Vector3(h, h * 0.02, h * 0.08), Part.BODY)
	b.box(Vector3(-h * 0.08, -h * 0.06, -h), Vector3(h * 0.08, h * 0.02, h), Part.BODY)
	return b.mesh(true)


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

	## A wedge body `l` long (nose at 0), `w` half-wide, `h` high: low nose, raised tail.
	func wedge(l: float, w: float, h: float, part: int) -> void:
		box(Vector3(-l, -h, -w), Vector3(-l * 0.35, h * 1.4, w), part)
		box(Vector3(-l * 0.35, -h, -w * 0.85), Vector3(0.0, h * 0.6, w * 0.85), part)

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
