class_name StreetRoomKit
extends RefCounted
## NA-23: the room interiors of the street netrun (PIPELINE_SPEC 9.3 rule 1: each node type has its own room dressing, read by
## shape, not by colour only). A room is the derive's front / back quads (`rooms[id]`); its interior is a lit shell (back wall
## glow, floor, ceiling, side walls, a bright frame) with a few near-black props whose front silhouette is distinct per kind.
## Seven kinds: the four run-graph types (router, terminal, mainframe, server_rack; a router with `elite` gains a crown) and the
## three D4 kinds (rest, workshop, cache; provisional art-pass shapes). Anything else is refused (`is_kind`). Pure geometry and
## data: the rig puts the meshes in the scene.

## The room kinds (DressReader.ROOM_KINDS).
## Vertex alpha of the frame bars (a marker; every other surface is 1).
const FRAME_ALPHA := 0.5
const KINDS: Array[String] = ["router", "terminal", "mainframe", "server_rack", "rest", "workshop", "cache"]

## Prop boxes per kind in the room's unit frame: [s0, s1, v0, v1, t0, t1, lit]. `s` -0.5..0.5 across the width, `v` 0..1 up
## the height, `t` 0 (the window) .. 1 (the back wall); `lit` 1 = glows in the kind colour (a screen, an indicator).
const PROPS: Dictionary = {
	"router": [
		[-0.40, -0.30, 0.0, 0.80, 0.55, 0.75, 0], [0.30, 0.40, 0.0, 0.80, 0.55, 0.75, 0], [-0.40, 0.40, 0.72, 0.82, 0.55, 0.75, 0],
		[-0.10, 0.10, 0.0, 0.30, 0.55, 0.75, 0],
	],
	"terminal": [
		[-0.42, 0.12, 0.0, 0.30, 0.45, 0.85, 0], [-0.22, -0.12, 0.30, 0.46, 0.55, 0.7, 0], [-0.40, 0.0, 0.46, 0.80, 0.55, 0.70, 0],
		[-0.36, -0.04, 0.50, 0.76, 0.52, 0.55, 1], [0.22, 0.40, 0.0, 0.40, 0.45, 0.8, 0], [0.34, 0.40, 0.40, 0.66, 0.45, 0.8, 0],
	],
	"mainframe": [
		[-0.44, -0.39, 0.0, 0.93, 0.6, 0.9, 0], [0.39, 0.44, 0.0, 0.93, 0.6, 0.9, 0], [-0.44, 0.44, 0.27, 0.32, 0.6, 0.9, 0],
		[-0.44, 0.44, 0.58, 0.63, 0.6, 0.9, 0], [-0.44, 0.44, 0.88, 0.93, 0.6, 0.9, 0], [-0.30, -0.12, 0.32, 0.50, 0.65, 0.85, 0],
		[0.08, 0.34, 0.63, 0.80, 0.65, 0.85, 0],
	],
	"server_rack": [
		[-0.42, -0.26, 0.0, 0.90, 0.5, 0.9, 0], [-0.20, -0.04, 0.0, 0.80, 0.5, 0.9, 0], [0.04, 0.20, 0.0, 0.92, 0.5, 0.9, 0],
		[0.26, 0.42, 0.0, 0.84, 0.5, 0.9, 0], [-0.38, -0.30, 0.22, 0.26, 0.48, 0.5, 1], [0.08, 0.16, 0.55, 0.59, 0.48, 0.5, 1],
	],
	"rest": [
		[-0.44, 0.22, 0.0, 0.20, 0.35, 0.9, 0], [-0.44, -0.30, 0.20, 0.32, 0.45, 0.8, 0], [0.30, 0.34, 0.0, 0.62, 0.6, 0.64, 0],
		[0.24, 0.40, 0.62, 0.72, 0.56, 0.68, 1],
	],
	"workshop": [
		[-0.42, -0.36, 0.0, 0.34, 0.5, 0.8, 0], [0.36, 0.42, 0.0, 0.34, 0.5, 0.8, 0], [-0.44, 0.44, 0.34, 0.41, 0.45, 0.85, 0],
		[0.18, 0.30, 0.41, 0.56, 0.55, 0.75, 0], [-0.42, -0.04, 0.58, 0.90, 0.78, 0.82, 0], [-0.30, -0.22, 0.62, 0.86, 0.7, 0.78, 1],
	],
	"cache": [
		[-0.36, 0.08, 0.0, 0.46, 0.45, 0.85, 0], [0.10, 0.40, 0.0, 0.30, 0.45, 0.85, 0], [-0.26, 0.02, 0.46, 0.66, 0.5, 0.8, 0],
		[-0.30, -0.22, 0.20, 0.30, 0.43, 0.45, 1],
	],
}
## Extra boxes of an elite router (the crown): three spikes over the lintel.
const ELITE_CROWN: Array = [
	[-0.34, -0.28, 0.82, 1.0, 0.55, 0.75, 0], [-0.03, 0.03, 0.82, 1.0, 0.55, 0.75, 0], [0.28, 0.34, 0.82, 1.0, 0.55, 0.75, 0],
]


## True for a room kind the view can draw.
static func is_kind(kind: String) -> bool:
	return KINDS.has(kind)


## The prop boxes of `kind` (an elite router adds the crown); empty for an unknown kind.
static func props(kind: String, elite: bool = false) -> Array:
	if not PROPS.has(kind):
		return []
	var out: Array = (PROPS[kind] as Array).duplicate()
	if elite and kind == "router":
		out.append_array(ELITE_CROWN)
	return out


## The front silhouette of `kind` rasterised to a `w` x `h` mask (1 = a prop covers the cell; row 0 on top). The shape tests
## compare these: every kind reads differently.
static func silhouette(kind: String, elite: bool = false, w: int = 14, h: int = 10) -> PackedByteArray:
	var out := PackedByteArray()
	out.resize(w * h)
	for b: Array in props(kind, elite):
		var x0: int = clampi(int(floorf((float(b[0]) + 0.5) * float(w))), 0, w - 1)
		var x1: int = clampi(int(ceilf((float(b[1]) + 0.5) * float(w))) - 1, 0, w - 1)
		var y0: int = clampi(int(floorf((1.0 - float(b[3])) * float(h))), 0, h - 1)
		var y1: int = clampi(int(ceilf((1.0 - float(b[2])) * float(h))) - 1, 0, h - 1)
		for y in range(y0, y1 + 1):
			for x in range(x0, x1 + 1):
				out[y * w + x] = 1
	return out


## The room's local frame from its derive quads: `{ok, origin (plan x, y), s (unit, along the window), t (unit, into the
## building), width, depth, z0, z1}` (z in plan units, `ground_z` added). Empty when the quads are degenerate.
static func frame_of(room: Dictionary) -> Dictionary:
	var gz: float = float(room.get("ground_z", 0.0))
	var f: Array = room["front"]
	var bk: Array = room["back"]
	var zmin := INF
	var zmax := -INF
	for p: Array in f:
		zmin = minf(zmin, float(p[2]))
		zmax = maxf(zmax, float(p[2]))
	var lo: Array = []
	for p: Array in f:
		if is_equal_approx(float(p[2]), zmin):
			lo.append(Vector2(float(p[0]), float(p[1])))
	if lo.size() < 2:
		return {}
	var a: Vector2 = lo[0]
	var b: Vector2 = lo[1]
	var width := a.distance_to(b)
	var mid := (a + b) * 0.5
	var bm := Vector2.ZERO
	for p: Array in bk:
		bm += Vector2(float(p[0]), float(p[1]))
	bm /= float(bk.size())
	var d := bm - mid
	var depth := d.length()
	if width < 0.01 or depth < 0.01 or zmax - zmin < 0.01:
		return {}
	var s := (b - a).normalized()
	var t := d / depth
	return {"origin": mid, "s": s, "t": t, "width": width, "depth": depth, "z0": zmin + gz, "z1": zmax + gz}


## The window volume the building shader cuts out of the route building's walls: `{box: Vector4(plan x0, y0, x1, y1), z: Vector2}`,
## the room grown `pad` BU toward the street (so the facade pixels are inside it).
static func volume(room: Dictionary, pad: float) -> Dictionary:
	var fr := frame_of(room)
	if fr.is_empty():
		return {}
	var o: Vector2 = fr["origin"]
	var s: Vector2 = fr["s"]
	var t: Vector2 = fr["t"]
	var hw: float = float(fr["width"]) * 0.5
	var dp: float = float(fr["depth"])
	var pts: Array[Vector2] = [o - s * hw - t * pad, o + s * hw - t * pad, o - s * hw + t * dp, o + s * hw + t * dp]
	var x0 := INF
	var y0 := INF
	var x1 := -INF
	var y1 := -INF
	for p in pts:
		x0 = minf(x0, p.x)
		y0 = minf(y0, p.y)
		x1 = maxf(x1, p.x)
		y1 = maxf(y1, p.y)
	return {"box": Vector4(x0, y0, x1, y1), "z": Vector2(float(fr["z0"]), float(fr["z1"]))}


## The interior mesh of `room` (derive dict) as a kind `kind` room of colour `col` in world space (x, z up, -y), or null when
## the kind is unknown or the quads are degenerate. `cfg` is `StreetRouteConfigData.rooms`.
static func build_mesh(room: Dictionary, kind: String, elite: bool, col: Color, cfg: Dictionary) -> ArrayMesh:
	if not is_kind(kind):
		return null
	var fr := frame_of(room)
	if fr.is_empty():
		return null
	var o: Vector2 = fr["origin"]
	var s: Vector2 = fr["s"]
	var t: Vector2 = fr["t"]
	var w: float = fr["width"]
	var d: float = fr["depth"]
	var z0: float = fr["z0"]
	var h: float = float(fr["z1"]) - z0
	var v := {"p": PackedVector3Array(), "c": PackedColorArray()}
	var wall := col * float(cfg["wall_gain"])
	wall.a = 1.0
	var floor_c := col * float(cfg["floor_gain"])
	floor_c.a = 1.0
	var ceil_c := col * float(cfg["ceil_gain"])
	ceil_c.a = 1.0
	var side_c := col * float(cfg["side_gain"])
	side_c.a = 1.0
	var prop := _rgb(cfg["prop"])
	var frame_c := _rgb(cfg["frame"]) * float(cfg["frame_gain"])
	frame_c.a = FRAME_ALPHA  # the marker the room shader scales with the zoom (`frame_k`)
	var at := func(ss: float, tt: float, vv: float) -> Vector3:
		var q: Vector2 = o + s * (ss * w) + t * (tt * d)
		return Vector3(q.x, z0 + vv * h, -q.y)
	# Back wall (glow fades toward the top), floor, ceiling, the two side walls.
	_quad(v, at.call(-0.5, 1.0, 0.0), at.call(0.5, 1.0, 0.0), at.call(0.5, 1.0, 1.0), at.call(-0.5, 1.0, 1.0), wall, wall, wall * 0.55, wall * 0.55)
	_quad(v, at.call(-0.5, 0.0, 0.0), at.call(0.5, 0.0, 0.0), at.call(0.5, 1.0, 0.0), at.call(-0.5, 1.0, 0.0), floor_c * 1.6, floor_c * 1.6, floor_c * 0.7, floor_c * 0.7)
	_quad(v, at.call(-0.5, 0.0, 1.0), at.call(0.5, 0.0, 1.0), at.call(0.5, 1.0, 1.0), at.call(-0.5, 1.0, 1.0), ceil_c, ceil_c, ceil_c, ceil_c)
	for sx: float in [-0.5, 0.5]:
		_quad(v, at.call(sx, 0.0, 0.0), at.call(sx, 1.0, 0.0), at.call(sx, 1.0, 1.0), at.call(sx, 0.0, 1.0), side_c * 0.8, side_c * 0.6, side_c * 0.45, side_c * 0.6)
	for b: Array in props(kind, elite):
		var c := col * 1.1 if int(b[6]) == 1 else prop
		c.a = 1.0
		_box(v, at, float(b[0]), float(b[1]), float(b[2]), float(b[3]), float(b[4]), float(b[5]), c)
	# The frame round the window: four bars in the opening plane, flush with the room edges.
	var fb: float = float(cfg["frame_bu"])
	var fs: float = fb / w
	var fv: float = fb / h
	var ft: float = 0.04 / d
	_box(v, at, -0.5, 0.5, 1.0 - fv, 1.0, -ft, ft, frame_c)
	_box(v, at, -0.5, 0.5, 0.0, fv, -ft, ft, frame_c)
	_box(v, at, -0.5, -0.5 + fs, 0.0, 1.0, -ft, ft, frame_c)
	_box(v, at, 0.5 - fs, 0.5, 0.0, 1.0, -ft, ft, frame_c)
	var arrays: Array = []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = v["p"]
	arrays[Mesh.ARRAY_COLOR] = v["c"]
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh


static func _rgb(a: Array) -> Color:
	return Color(float(a[0]), float(a[1]), float(a[2]), 1.0)


static func _quad(v: Dictionary, a: Vector3, b: Vector3, c: Vector3, d: Vector3, ca: Color, cb: Color, cc: Color, cd: Color) -> void:
	var p: PackedVector3Array = v["p"]
	var col: PackedColorArray = v["c"]
	p.append_array(PackedVector3Array([a, b, c, a, c, d]))
	col.append_array(PackedColorArray([ca, cb, cc, ca, cc, cd]))
	v["p"] = p
	v["c"] = col


## A box in the unit frame (`s0..s1`, `v0..v1`, `t0..t1`), all six faces one colour.
static func _box(v: Dictionary, at: Callable, s0: float, s1: float, v0: float, v1: float, t0: float, t1: float, c: Color) -> void:
	var p000: Vector3 = at.call(s0, t0, v0)
	var p100: Vector3 = at.call(s1, t0, v0)
	var p110: Vector3 = at.call(s1, t1, v0)
	var p010: Vector3 = at.call(s0, t1, v0)
	var p001: Vector3 = at.call(s0, t0, v1)
	var p101: Vector3 = at.call(s1, t0, v1)
	var p111: Vector3 = at.call(s1, t1, v1)
	var p011: Vector3 = at.call(s0, t1, v1)
	_quad(v, p000, p100, p101, p001, c, c, c, c)
	_quad(v, p010, p110, p111, p011, c, c, c, c)
	_quad(v, p000, p010, p011, p001, c, c, c, c)
	_quad(v, p100, p110, p111, p101, c, c, c, c)
	_quad(v, p000, p100, p110, p010, c, c, c, c)
	_quad(v, p001, p101, p111, p011, c, c, c, c)
