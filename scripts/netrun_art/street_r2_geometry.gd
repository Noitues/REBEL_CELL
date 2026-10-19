class_name StreetR2Geometry
extends RefCounted
## Street r2 renderer, geometry half: the face records of `StreetR2Kits` (polygons `{pts, col}` in plan BU, z up) and the primitive records
## of the roof clutter turned into one `ArrayMesh` per building, one surface per material. Plan (x, y, z) is world (x, z, -y).

## Material ids in surface order.
const MATS: Array[String] = ["conc", "glass", "panel", "solid", "win", "neon"]


## The world point of a plan point `[x, y, z]`.
static func world(p: Array) -> Vector3:
	return Vector3(float(p[0]), float(p[2]), -float(p[1]))


## An empty bucket: material id -> Array of face records.
static func new_bucket() -> Dictionary:
	var b := {}
	for m: String in MATS:
		b[m] = []
	return b


## Appends the face records `faces` to material `mat` of `bucket`.
static func add(bucket: Dictionary, mat: String, faces: Array) -> void:
	(bucket[mat] as Array).append_array(faces)


## One face record.
static func face(pts: Array, col: Array) -> Dictionary:
	return {"pts": pts, "col": col}


## The face records of a primitive record of `StreetR2Faces.prims` (`cyl36`: a prism of `sides` sides and a cap, `box`, `beam`: a square
## tube of width w).
static func prim_faces(prim: Array, sides: int) -> Array:
	var out: Array = []
	match String(prim[0]):
		"cyl36":
			var cx := float(prim[1])
			var cy := float(prim[2])
			var z0 := float(prim[3])
			var z1 := float(prim[4])
			var rad := float(prim[5])
			var col: Array = prim[6]
			var ring: Array = []
			for k in sides:
				var ang := TAU * float(k) / float(sides)
				ring.append([cx + rad * cos(ang), cy + rad * sin(ang)])
			var cap: Array = []
			for k in sides:
				var p: Array = ring[k]
				var q: Array = ring[(k + 1) % sides]
				out.append(face([[p[0], p[1], z0], [q[0], q[1], z0], [q[0], q[1], z1], [p[0], p[1], z1]], col))
				cap.append([p[0], p[1], z1])
			out.append(face(cap, col))
		"box":
			var x0 := float(prim[1])
			var y0 := float(prim[2])
			var z0 := float(prim[3])
			var x1 := float(prim[4])
			var y1 := float(prim[5])
			var z1 := float(prim[6])
			var col: Array = prim[7]
			out.append(face([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], col))
			out.append(face([[x1, y1, z0], [x0, y1, z0], [x0, y1, z1], [x1, y1, z1]], col))
			out.append(face([[x0, y1, z0], [x0, y0, z0], [x0, y0, z1], [x0, y1, z1]], col))
			out.append(face([[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]], col))
			out.append(face([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], col))
			out.append(face([[x0, y1, z0], [x1, y1, z0], [x1, y0, z0], [x0, y0, z0]], col))
		"beam":
			out = beam_faces(prim[1], prim[2], float(prim[3]), prim[4])
	return out


## A square tube of width `w` between plan points `p0` and `p1` (four long faces).
static func beam_faces(p0: Array, p1: Array, w: float, col: Array) -> Array:
	var a := Vector3(float(p0[0]), float(p0[1]), float(p0[2]))
	var b := Vector3(float(p1[0]), float(p1[1]), float(p1[2]))
	var d := b - a
	if d.length() < 1e-6:
		return []
	var ref := Vector3(0, 0, 1) if absf(d.normalized().z) < 0.9 else Vector3(1, 0, 0)
	var u := d.cross(ref).normalized() * (w * 0.5)
	var v := d.cross(u).normalized() * (w * 0.5)
	var corners: Array[Vector3] = [u + v, u - v, -u - v, -u + v]
	var out: Array = []
	for k in 4:
		var c0: Vector3 = corners[k]
		var c1: Vector3 = corners[(k + 1) % 4]
		var q: Array = []
		for pt: Vector3 in [a + c0, a + c1, b + c1, b + c0]:
			q.append([pt.x, pt.y, pt.z])
		out.append(face(q, col))
	return out


## Number of triangles of the face records of `faces` (fan triangulation).
static func tri_count(faces: Array) -> int:
	var n := 0
	for f: Dictionary in faces:
		n += maxi(0, (f["pts"] as Array).size() - 2)
	return n


## One mesh from a bucket; `centre` (world) orients the normals away from the building. Empty surfaces are left out; `surface_of` maps a
## material id to its surface index. Returns null when the bucket holds no triangle.
static func mesh(bucket: Dictionary, centre: Vector3, surface_of: Dictionary) -> ArrayMesh:
	var m := ArrayMesh.new()
	for mat: String in MATS:
		var faces: Array = bucket[mat]
		if faces.is_empty():
			continue
		var verts := PackedVector3Array()
		var norms := PackedVector3Array()
		var cols := PackedColorArray()
		for f: Dictionary in faces:
			var pts: Array = f["pts"]
			if pts.size() < 3:
				continue
			var c := Color(float(f["col"][0]), float(f["col"][1]), float(f["col"][2]))
			var p0 := world(pts[0])
			var mid := Vector3.ZERO
			for p: Array in pts:
				mid += world(p)
			mid /= float(pts.size())
			for k in range(1, pts.size() - 1):
				var p1 := world(pts[k])
				var p2 := world(pts[k + 1])
				var n := (p1 - p0).cross(p2 - p0)
				if n.length_squared() < 1e-12:
					continue
				n = n.normalized()
				if n.dot(mid - centre) < 0.0:
					n = -n
				verts.append_array([p0, p1, p2])
				norms.append_array([n, n, n])
				cols.append_array([c, c, c])
		if verts.is_empty():
			continue
		var arr: Array = []
		arr.resize(Mesh.ARRAY_MAX)
		arr[Mesh.ARRAY_VERTEX] = verts
		arr[Mesh.ARRAY_NORMAL] = norms
		arr[Mesh.ARRAY_COLOR] = cols
		m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
		surface_of[mat] = m.get_surface_count() - 1
	if m.get_surface_count() == 0:
		return null
	return m
