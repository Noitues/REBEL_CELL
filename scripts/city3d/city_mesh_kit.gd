class_name CityMeshKit
extends RefCounted
## ART-1 1D: geometry of the real-time unified city (bible §1.2 Cv2, §6.1). Building
## families are unit prisms (square / hex / octagon footprints x facet-row classes) split
## into jittered triangles (concept `unified40.fgrid`: ~1.7 BU cells, interior points
## jittered, a tone value per triangle); each building extrusion is one MultiMesh instance
## (footprint basis, base, height; taper in INSTANCE_CUSTOM). Ground, street lots and lane
## glow are one mesh each. Deterministic: hashes of indices, no RNG.

## CUSTOM0 per vertex: x = tone 0-1 (per triangle), y = 1 on roofs, z = roof rim 0-1, w = 0.
## UV = the wall's start corner (unit footprint x/z), UV2 = the wall's edge vector.

const ROOF := 1.0


## Integer hash to 0-1 (the city's view hash; NeonCity._h style).
static func hash01(a: int, b: int, c: int = 0) -> float:
	var n := (a * 73856093) ^ (b * 19349663) ^ (c * 83492791)
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65535.0


## Unit footprint of a family with `sides` corners, centred on 0 (square: -0.5..0.5;
## n-gon: radius 1, corner k at angle 2 pi k / n).
static func unit_footprint(sides: int) -> PackedVector2Array:
	var out := PackedVector2Array()
	if sides == 4:
		out.append_array([Vector2(-0.5, -0.5), Vector2(0.5, -0.5), Vector2(0.5, 0.5), Vector2(-0.5, 0.5)])
		return out
	for k in sides:
		var t := TAU * k / sides
		out.append(Vector2(cos(t), sin(t)))
	return out


## The instance transform mapping the unit footprint of `poly.size()` sides onto `poly`
## (world X/Z), base `y0`, height `h`; Transform3D() when the footprint does not fit.
static func instance_transform(poly: PackedVector2Array, y0: float, h: float) -> Transform3D:
	var n := poly.size()
	if n == 4:
		var e1 := poly[1] - poly[0]
		var e3 := poly[3] - poly[0]
		var o := poly[0] + (e1 + e3) * 0.5
		if e1.cross(e3) < 0.0:
			# Mirrored order: swap the axes (the unit square maps onto itself).
			var t := e1
			e1 = e3
			e3 = t
		return Transform3D(Basis(Vector3(e1.x, 0, e1.y), Vector3(0, h, 0), Vector3(e3.x, 0, e3.y)), Vector3(o.x, y0, o.y))
	var c := Vector2.ZERO
	for p in poly:
		c += p
	c /= n
	var r := poly[0] - c
	var ax := Vector3(r.x, 0, r.y)
	# The next corner fixes the turning direction.
	var r1 := poly[1] - c
	var bz := Vector3(-r.y, 0, r.x)
	if r.cross(r1) < 0.0:
		bz = -bz
	return Transform3D(Basis(ax, Vector3(0, h, 0), bz), Vector3(c.x, y0, c.y))


## A unit prism family: `sides` corners, `rows` facet rows, `cols` facet columns per wall,
## interior points jittered by `jitter` of a cell and `njitter` along the wall normal
## (unit space); `salt` varies the family's pattern.
static func unit_prism(sides: int, rows: int, cols: int, jitter: float, njitter: float, salt: int) -> ArrayMesh:
	var fp := unit_footprint(sides)
	var verts := PackedVector3Array()
	var uvs := PackedVector2Array()
	var uv2s := PackedVector2Array()
	var cust := PackedFloat32Array()
	var tri := 0
	for k in sides:
		var a := fp[k]
		var b := fp[(k + 1) % sides]
		var e := b - a
		var nrm := Vector2(e.y, -e.x).normalized()
		if nrm.dot((a + b) * 0.5) < 0.0:
			nrm = -nrm
		var grid: Array[PackedVector3Array] = []
		for j in rows + 1:
			var row := PackedVector3Array()
			for i in cols + 1:
				var u := float(i) / cols
				var v := float(j) / rows
				var p := a.lerp(b, u)
				var y := v
				if i > 0 and i < cols and j > 0 and j < rows:
					var ju := (hash01(k * 131 + i, j, salt) - 0.5) * 2.0 * jitter / cols
					var jv := (hash01(k * 131 + i, j, salt + 1) - 0.5) * 2.0 * jitter / rows
					var jn := (hash01(k * 131 + i, j, salt + 2) - 0.5) * 2.0 * njitter
					p += e * ju + nrm * jn
					y += jv
				row.append(Vector3(p.x, y, p.y))
			grid.append(row)
		for j in rows:
			for i in cols:
				var p00 := grid[j][i]
				var p10 := grid[j][i + 1]
				var p11 := grid[j + 1][i + 1]
				var p01 := grid[j + 1][i]
				var quads: Array = [[p00, p11, p10], [p00, p01, p11]] if (i + j) % 2 == 0 else [[p00, p01, p10], [p10, p01, p11]]
				for t3: Array in quads:
					var tone := hash01(tri, salt, 7)
					tri += 1
					for q: Vector3 in t3:
						verts.append(q)
						uvs.append(a)
						uv2s.append(e)
						cust.append_array([tone, 0.0, 0.0, 0.0])
	# Roof: a fan from a slightly pushed centre (facet_quad with jit 0.01).
	var top_c := Vector3(0, 1.0, 0)
	for k in sides:
		var a := fp[k]
		var b := fp[(k + 1) % sides]
		var tone := hash01(tri, salt, 9)
		tri += 1
		for q in [[top_c, 0.0], [Vector3(b.x, 1.0, b.y), 1.0], [Vector3(a.x, 1.0, a.y), 1.0]]:
			verts.append(q[0])
			uvs.append(Vector2.ZERO)
			uv2s.append(Vector2.ZERO)
			cust.append_array([tone, ROOF, float(q[1]), 0.0])
	return _mesh(verts, uvs, uv2s, cust)


static func _mesh(verts: PackedVector3Array, uvs: PackedVector2Array, uv2s: PackedVector2Array, cust: PackedFloat32Array) -> ArrayMesh:
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = verts
	arr[Mesh.ARRAY_TEX_UV] = uvs
	arr[Mesh.ARRAY_TEX_UV2] = uv2s
	arr[Mesh.ARRAY_CUSTOM0] = cust
	var normals := PackedVector3Array()
	normals.resize(verts.size())
	normals.fill(Vector3.UP)
	arr[Mesh.ARRAY_NORMAL] = normals
	var m := ArrayMesh.new()
	var fmt := Mesh.ARRAY_CUSTOM_RGBA_FLOAT << Mesh.ARRAY_FORMAT_CUSTOM0_SHIFT
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr, [], {}, fmt)
	return m


## The facet-row class of height `h` (BU).
static func height_class(cfg: CityConfig, h: float) -> int:
	for k in cfg.height_classes.size():
		if h <= cfg.height_classes[k]:
			return k
	return cfg.height_classes.size() - 1


## Family key of a prism: sides * 16 + height class.
static func family_of(cfg: CityConfig, pr: Dictionary) -> int:
	return (pr["poly"] as PackedVector2Array).size() * 16 + height_class(cfg, float(pr["h"]))


## Groups the district's prisms by family: key -> Array of prism indices (prism order).
static func families(cfg: CityConfig, d: CityDistrict) -> Dictionary:
	var out := {}
	for n in d.prisms.size():
		var key := family_of(cfg, d.prisms[n])
		if not out.has(key):
			out[key] = []
		(out[key] as Array).append(n)
	return out


## The base colour of a building (family mix + territory tint, unified40.city_building).
static func base_color(cfg: CityConfig, pr: Dictionary) -> Color:
	var fam := cfg.families[absi(int(pr["key"])) % cfg.families.size()]
	var terr: StringName = pr["terr"]
	if terr == &"":
		return fam
	return fam.lerp(Palette.corp_color(terr), cfg.territory_tint)


## The ground mesh: asphalt, plazas, street lots (lot quads at height 0).
static func ground_mesh(cfg: CityConfig, d: CityDistrict) -> ArrayMesh:
	var r := cfg.district_radius * cfg.lot_bu * 1.6
	return ground_mesh_of(cfg, Rect2(-r, -r, r * 2.0, r * 2.0), d.plazas, d.streets)


## ART-5 5a: the ground of world rect `area` (X/Z): asphalt, then plazas and street lots.
static func ground_mesh_of(cfg: CityConfig, area: Rect2, plazas: Array, streets: Array) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var a := area.position
	var b := area.end
	_quad(st, Vector3(a.x, -0.02, a.y), Vector3(b.x, -0.02, a.y), Vector3(b.x, -0.02, b.y), Vector3(a.x, -0.02, b.y), cfg.ground)
	for p: Dictionary in plazas:
		var l: Vector2i = p["lot"]
		var col := cfg.plaza.lerp(Palette.corp_color(p["terr"]), 0.12)
		_lot_quad(st, cfg, l, 0.005, col)
	for s: Dictionary in streets:
		_lot_quad(st, cfg, s["lot"], 0.01, cfg.street)
	st.generate_normals()
	return st.commit()


## Lane glow strips (unified40 GLANE): a soft bed and 3-12 bright strokes per street lot
## in its lane colour (vertex colour = emission).
static func lane_mesh(cfg: CityConfig, d: CityDistrict) -> ArrayMesh:
	return lane_mesh_of(cfg, d.streets)


## ART-5 5a: lane glow strips of street lots `streets` (one chunk's).
static func lane_mesh_of(cfg: CityConfig, streets: Array) -> ArrayMesh:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var u := cfg.lot_bu
	var any := false
	for s: Dictionary in streets:
		if s["along_i"] and s["along_j"]:
			continue
		var l: Vector2i = s["lot"]
		var ai: bool = s["along_i"]
		var a := Vector2(l.x + 0.5, l.y) if ai else Vector2(l.x, l.y + 0.5)
		var b := Vector2(l.x + 0.5, l.y + 1) if ai else Vector2(l.x + 1, l.y + 0.5)
		var wa := CityIsoCamera.lot_to_world(cfg, a)
		var wb := CityIsoCamera.lot_to_world(cfg, b)
		var col: Color = s["col"]
		var tr: float = s["traffic"]
		var strokes := 7 + int(tr * 23.0)
		var half := (1.5 + strokes * 0.42) / cfg.lane_bed_px * u
		var dir := (wb - wa).normalized()
		var nrm := Vector3(-dir.z, 0, dir.x)
		var bed := col * (cfg.lane_glow_base + tr * cfg.lane_glow_traffic)
		_strip(st, wa - dir * 0.3, wb + dir * 0.3, nrm, half + 0.5, 0.02, bed)
		any = true
		var nl := mini(strokes, 3 + int(tr * 9.0))
		for k in nl:
			var t := (k + 0.5) / nl * 2.0 - 1.0
			var lane := t * half * 0.8 + (hash01(l.x * 7919 + l.y, k, 3) - 0.5) * 0.25
			var al := 0.55 + 0.35 * hash01(l.x, l.y * 31 + k, 4) + tr * 0.15
			var c2 := Color(minf(1.0, col.r * al), minf(1.0, col.g * al), minf(1.0, col.b * al))
			_strip(st, wa + nrm * lane - dir * 0.35, wb + nrm * lane + dir * 0.35, nrm, cfg.lane_stroke_bu * 0.5, 0.04, c2)
	return st.commit() if any else null


## Car part ids (CUSTOM0.x): body, lane-colour light, headlight, tail light.
enum Part { BODY, LANE, HEAD, TAIL }


## A sky-lane car tier mesh (bible §4.1 car LOD; X = heading, Y up, Z side), its speed
## line `streak` BU long behind the nose. 0 FAR: head dot + lane line; 1 MEDIUM: small box
## + line; 2 CLOSE: wedge body, dark cabin, lane stripes, under-glow, head and tail lights
## + a thick line.
static func car_mesh(tier: int, streak: float) -> ArrayMesh:
	var v := PackedVector3Array()
	var c := PackedFloat32Array()
	match tier:
		0:
			_box(v, c, Vector3(-streak, -0.1, -0.12), Vector3(0, 0.1, 0.12), Part.LANE)
			_box(v, c, Vector3(-0.3, -0.3, -0.3), Vector3(0.3, 0.3, 0.3), Part.HEAD)
		1:
			_box(v, c, Vector3(-streak, -0.08, -0.1), Vector3(-1.2, 0.08, 0.1), Part.LANE)
			_box(v, c, Vector3(-1.2, -0.3, -0.6), Vector3(1.2, 0.3, 0.6), Part.BODY)
		_:
			_box(v, c, Vector3(-streak, -0.15, -0.3), Vector3(-1.5, 0.15, 0.3), Part.LANE)
			_box(v, c, Vector3(-1.5, -0.25, -0.7), Vector3(1.4, 0.2, 0.7), Part.BODY)
			_box(v, c, Vector3(-0.9, 0.2, -0.5), Vector3(0.6, 0.6, 0.5), Part.BODY)
			_box(v, c, Vector3(-1.5, -0.05, -0.74), Vector3(1.2, 0.05, 0.74), Part.LANE)
			_box(v, c, Vector3(-1.2, -0.35, -0.5), Vector3(1.0, -0.27, 0.5), Part.LANE)
			_box(v, c, Vector3(1.4, -0.15, -0.6), Vector3(1.5, 0.05, -0.3), Part.HEAD)
			_box(v, c, Vector3(1.4, -0.15, 0.3), Vector3(1.5, 0.05, 0.6), Part.HEAD)
			_box(v, c, Vector3(-1.6, -0.1, -0.6), Vector3(-1.5, 0.1, 0.6), Part.TAIL)
	var arr := []
	arr.resize(Mesh.ARRAY_MAX)
	arr[Mesh.ARRAY_VERTEX] = v
	arr[Mesh.ARRAY_CUSTOM0] = c
	var cols := PackedColorArray()
	cols.resize(v.size())
	cols.fill(Color.WHITE)
	arr[Mesh.ARRAY_COLOR] = cols
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr, [], {}, Mesh.ARRAY_CUSTOM_RGBA_FLOAT << Mesh.ARRAY_FORMAT_CUSTOM0_SHIFT)
	return m


static func _box(v: PackedVector3Array, c: PackedFloat32Array, lo: Vector3, hi: Vector3, part: int) -> void:
	var p := [Vector3(lo.x, lo.y, lo.z), Vector3(hi.x, lo.y, lo.z), Vector3(hi.x, lo.y, hi.z), Vector3(lo.x, lo.y, hi.z),
		Vector3(lo.x, hi.y, lo.z), Vector3(hi.x, hi.y, lo.z), Vector3(hi.x, hi.y, hi.z), Vector3(lo.x, hi.y, hi.z)]
	for f in [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]:
		for k in [0, 1, 2, 0, 2, 3]:
			v.append(p[f[k]])
			c.append_array([float(part), 0.0, 0.0, 0.0])


static func _strip(st: SurfaceTool, a: Vector3, b: Vector3, nrm: Vector3, half: float, y: float, col: Color) -> void:
	var up := Vector3(0, y, 0)
	_quad(st, a + nrm * half + up, b + nrm * half + up, b - nrm * half + up, a - nrm * half + up, col)


static func _lot_quad(st: SurfaceTool, cfg: CityConfig, l: Vector2i, y: float, col: Color) -> void:
	var p0 := CityIsoCamera.lot_to_world(cfg, Vector2(l.x, l.y), y)
	var p1 := CityIsoCamera.lot_to_world(cfg, Vector2(l.x + 1, l.y), y)
	var p2 := CityIsoCamera.lot_to_world(cfg, Vector2(l.x + 1, l.y + 1), y)
	var p3 := CityIsoCamera.lot_to_world(cfg, Vector2(l.x, l.y + 1), y)
	_quad(st, p0, p1, p2, p3, col)


## Quad a-b-c-d, wound to face up (+Y).
static func _quad(st: SurfaceTool, a: Vector3, b: Vector3, c: Vector3, d: Vector3, col: Color) -> void:
	var up := (b - a).cross(d - a).y > 0.0
	var order := PackedVector3Array([a, b, c, a, c, d]) if not up else PackedVector3Array([a, c, b, a, d, c])
	for p in order:
		st.set_color(col)
		st.set_normal(Vector3.UP)
		st.add_vertex(p)


# --- ART-5 5a: the whole city's chunked building families and LODs --------------------------

## Floats per MultiMesh instance: transform (3x4), colour, custom.
const INSTANCE_FLOATS := 20
## Unit meshes made so far: "key|lod|rows|cols" -> ArrayMesh (pure functions of their key).
static var _unit_cache: Dictionary = {}


## Facet rows of height class `hc` at building LOD `lod` (CityLod.building_lod).
static func lod_rows(cfg: CityConfig, hc: int, lod: int) -> int:
	var share: float = cfg.lod_rows_share[clampi(lod, 0, cfg.lod_rows_share.size() - 1)]
	if share <= 0.0:
		return 1
	return maxi(1, roundi(cfg.height_class_rows[hc] * share))


## The unit prism of family `key` (sides * 16 + height class) at building LOD `lod`
## (cached: the same mesh for every chunk).
static func family_mesh(cfg: CityConfig, key: int, lod: int) -> ArrayMesh:
	var sides := key / 16
	var hc := key % 16
	var rows := lod_rows(cfg, hc, lod)
	var cols: int = cfg.lod_cols[clampi(lod, 0, cfg.lod_cols.size() - 1)]
	var k := "%d|%d|%d|%d|%s" % [key, lod, rows, cols, cfg.resource_path]
	if not _unit_cache.has(k):
		var jit := cfg.facet_jitter if rows > 1 else 0.0
		_unit_cache[k] = unit_prism(sides, rows, cols, jit, cfg.facet_normal_jitter * 0.1 if rows > 1 else 0.0, key)
	return _unit_cache[k]


## Groups prisms `idx` (indices into `prisms`) by family: key -> PackedInt32Array, in
## index order.
static func families_of(cfg: CityConfig, prisms: Array[Dictionary], idx: PackedInt32Array) -> Dictionary:
	var out := {}
	for n in idx:
		var key := family_of(cfg, prisms[n])
		# Packed arrays are values: append through the dictionary, never a cast copy.
		if not out.has(key):
			out[key] = PackedInt32Array()
		out[key].append(n)
	return out


## The roof-trim ink palette of `prisms` (distinct inks by RGBA, sorted, at most 16: the
## building shader's `ink_colors`).
static func ink_palette(prisms: Array[Dictionary]) -> Array[Color]:
	var seen := {}
	for pr in prisms:
		seen[(pr["ink"] as Color).to_rgba32()] = pr["ink"]
	var keys: Array = seen.keys()
	keys.sort()
	var out: Array[Color] = []
	for k in keys:
		if out.size() >= 16:
			break
		out.append(seen[k])
	return out


## The ink palette slot of `c` (1-based; the nearest when the palette is full).
static func ink_slot(inks: Array[Color], c: Color) -> int:
	var best := 0
	var best_d := INF
	for k in inks.size():
		var d := Vector3(inks[k].r - c.r, inks[k].g - c.g, inks[k].b - c.b).length_squared()
		if d < best_d:
			best_d = d
			best = k + 1
	return best


## The MultiMesh buffer of prisms `idx` (TRANSFORM_3D + colours + custom data):
## transform rows, COLOR = base colour, INSTANCE_CUSTOM = (taper, trim ink slot or 0,
## seed, crest).
static func instance_buffer(cfg: CityConfig, prisms: Array[Dictionary], idx: PackedInt32Array, inks: Array[Color]) -> PackedFloat32Array:
	var buf := PackedFloat32Array()
	buf.resize(idx.size() * INSTANCE_FLOATS)
	var o := 0
	for n in idx:
		var pr := prisms[n]
		var t := instance_transform(pr["poly"], pr["y0"], pr["h"])
		var b := t.basis
		var vals := [b.x.x, b.y.x, b.z.x, t.origin.x, b.x.y, b.y.y, b.z.y, t.origin.y, b.x.z, b.y.z, b.z.z, t.origin.z]
		for v: float in vals:
			buf[o] = v
			o += 1
		var col := base_color(cfg, pr)
		buf[o] = col.r
		buf[o + 1] = col.g
		buf[o + 2] = col.b
		buf[o + 3] = 1.0
		o += 4
		var key_i := int(pr["key"])
		var trim := 0.0
		if float(pr["taper"]) > 0.05 and hash01(key_i, 42, 1) < cfg.roof_trim_share:
			trim = float(ink_slot(inks, pr["ink"]))
		buf[o] = float(pr["taper"])
		buf[o + 1] = trim
		buf[o + 2] = hash01(key_i, 43, 2)
		buf[o + 3] = 0.0
		o += 4
	return buf
