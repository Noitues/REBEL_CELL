class_name BloomRibbons
extends RefCounted
## LOOK Solace THE BLOOM A "Necrosis": the pink vein ribbons that crawl ahead of the front on the walk and the road and climb the facade,
## forking now and then. A port of art-pass bloom/scripts/street3d/bloom3d_ribbons.py: thin tapered quad strips from random walks, never
## inside a keep-out box (route rooms, links) and only on the ground band and the lowest facade metres. View side: deterministic (a
## seeded generator of its own, no global randomness, no game stream), the same look gives the same mesh.
## The mesh is in the STREET FRAME (BloomLook.frame_to_world places it); the ribbon material is `bloom_ribbon.gdshader`.

const MATERIAL_SHADER := preload("res://shaders/city/bloom_ribbon.gdshader")
const MESH_NAME := "BloomRibbons"
const TWO_PI := TAU

var _s: int = 0
var _boxes: Array = []
var _r: Dictionary = {}
var _verts := PackedVector3Array()
var _idx := PackedInt32Array()
var _made: int = 0


## The ribbon mesh of a street look's `ribbons` block, its vertices put through `xf` (the street frame -> world; null when it has none or
## the strength is 0).
static func build(rb: Dictionary, xf: Transform3D = Transform3D.IDENTITY) -> ArrayMesh:
	if rb.is_empty() or float(rb.get("strength", 0.0)) <= 0.0:
		return null
	var b := BloomRibbons.new()
	b._run(rb)
	if b._verts.is_empty():
		return null
	var arr: Array = []
	arr.resize(Mesh.ARRAY_MAX)
	var vs := PackedVector3Array()
	vs.resize(b._verts.size())
	for i in b._verts.size():
		vs[i] = xf * b._verts[i]  # baked into the world: the frame can be a mirror
	arr[Mesh.ARRAY_VERTEX] = vs
	arr[Mesh.ARRAY_INDEX] = b._idx
	var m := ArrayMesh.new()
	m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
	return m


## Ribbons made for `rb` (the count, for tests).
static func count(rb: Dictionary) -> int:
	var b := BloomRibbons.new()
	b._run(rb)
	return b._made


## The ribbon material at emission `strength` (pink = linear colour).
static func make_material(pink: Vector3, strength: float) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = MATERIAL_SHADER
	m.set_shader_parameter(&"pink", pink)
	m.set_shader_parameter(&"strength", strength)
	return m


func _run(rb: Dictionary) -> void:
	_r = rb
	_boxes = rb["boxes"]
	_s = int(rb["seed"]) * 2654435761 + 1013904223
	var fx := float(rb["front"])
	for i in int(rb["n_ground"]):  # on the walk / road, from just behind the front out ahead of it
		var x0 := fx + _uni(-1.0, 6.0)
		var y0 := _uni(float(rb["y0"]), float(rb["y1"]))
		_walk(Vector3(x0, y0, float(rb["z_ground"])), _gauss(0.0, 0.25), _uni(float(rb["len_min"]), float(rb["reach"])), 0, false)
	for i in int(rb["n_facade"]):  # up the facade face, rooted at the kerb
		var x0 := fx + _uni(-2.0, 8.0)
		_walk(Vector3(x0, float(rb["facade_y"]), 0.3), _gauss(0.5, 0.3), _uni(2.0, float(rb["facade_h"])), 0, true)


# splitmix64: a seeded 64-bit generator of our own (GDScript ints wrap)
func _next() -> int:
	_s += -7046029254386353131
	var z := _s
	z = (z ^ (z >> 30)) * -4658895280553007687
	z = (z ^ (z >> 27)) * -7723592293110705685
	return z ^ (z >> 31)


func _f() -> float:
	return float((_next() >> 11) & 0x1FFFFFFFFFFFFF) / 9007199254740992.0


func _uni(a: float, b: float) -> float:
	return a + (b - a) * _f()


func _gauss(mu: float, sigma: float) -> float:
	var u := maxf(_f(), 1e-12)
	var v := _f()
	return mu + sigma * sqrt(-2.0 * log(u)) * cos(TWO_PI * v)


func _inside(q: Vector3) -> bool:
	for bx: Array in _boxes:
		var lo := bx[0] as Vector3
		var hi := bx[1] as Vector3
		if q.x > lo.x and q.x < hi.x and q.y > lo.y and q.y < hi.y and q.z > lo.z and q.z < hi.z:
			return true
	return false


func _walk(p: Vector3, d: float, length: float, depth: int, facade: bool) -> void:
	var pts: Array[Vector3] = [p]
	var step := float(_r["step"])
	var ang := d
	for _i in int(length / step):
		ang += _gauss(0.0, 0.22)
		ang *= 0.93
		var last := pts[pts.size() - 1]
		var q: Vector3
		if not facade:
			q = Vector3(last.x - cos(ang) * step, last.y + sin(ang) * step, last.z)
		else:  # x along the street (toward -x), z up
			q = Vector3(last.x - cos(ang) * step * 0.7, last.y, last.z + absf(sin(ang)) * step * 0.9)
		if _inside(q) or q.z > float(_r["facade_h"]):
			break
		pts.append(q)
		if depth < 2 and _f() < float(_r["fork"]):
			_walk(q, ang + (-1.0 if _f() < 0.5 else 1.0) * 0.7, length * 0.5, depth + 1, facade)
	if pts.size() < 3:
		return
	var w := float(_r["width"]) * (1.0 if depth == 0 else 0.65)
	for i in range(pts.size() - 1):
		var a := pts[i]
		var b := pts[i + 1]
		var t := 1.0 - float(i) / float(pts.size())  # taper toward the tip
		var base := _verts.size()
		if not facade:
			var nx := -(b.y - a.y)
			var ny := b.x - a.x
			var l := maxf(sqrt(nx * nx + ny * ny), 1e-6)
			nx = nx / l * w * t * 0.5
			ny = ny / l * w * t * 0.5
			_verts.append(Vector3(a.x - nx, a.y - ny, a.z))
			_verts.append(Vector3(a.x + nx, a.y + ny, a.z))
			_verts.append(Vector3(b.x + nx, b.y + ny, b.z))
			_verts.append(Vector3(b.x - nx, b.y - ny, b.z))
		else:
			var nz := w * t * 0.5
			_verts.append(Vector3(a.x, a.y, a.z - nz))
			_verts.append(Vector3(a.x, a.y, a.z + nz))
			_verts.append(Vector3(b.x, b.y, b.z + nz))
			_verts.append(Vector3(b.x, b.y, b.z - nz))
		_idx.append_array(PackedInt32Array([base, base + 1, base + 2, base, base + 2, base + 3]))
	_made += 1
