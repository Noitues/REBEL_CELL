class_name CityWater
extends Node3D
## NA-12 r2 (art-pass item 17): a generated city's sea on the 3D city (CityView3D adds it to its ground layer when the
## model's plan has a coast; the fixed city has none). Four meshes, all from the plan and the model (no randomness):
## the sea (every sea lot of the city rect grown by `water_extend_lots`, in runs along the inland axis so the shore
## distance in UV.x is exact; `city_water.gdshader`), the void past the city (the same shader, `void_mode`, darker than
## the sea), the sea wall (a face on every land lot's edge that meets the sea, toon-lit like the ground, with a lit
## coping strip), and a pier where a street runs into the water (a deck and a lamp at its end). Numbers and colours:
## CityConfig's "Water" group. `set_night` / `set_look_blend` / `set_time_scale` follow the view's day look, the
## netrun look and reduce motion.

const SHADER := preload("res://shaders/city/city_water.gdshader")
## Heights (BU) of the void and the sea above the ground plane (the void under the city's ground, the sea over it).
const VOID_Y := -0.04
const SEA_Y := 0.03

var water_mat: ShaderMaterial
var void_mat: ShaderMaterial
## The sea wall's face and the piers' decks (toon-lit; CityView3D's day ramp reaches them) and their lights (emission).
var wall_mat: ShaderMaterial
var light_mat: ShaderMaterial
var piers: int = 0
var wall_edges: int = 0


## The sea of `plan` on `model`'s city (CityConfig `cfg`), the void spanning `outer_bu` BU round the origin.
static func make(cfg: CityConfig, plan: CityPlan, model: CityModel, outer_bu: float) -> CityWater:
	var w := CityWater.new()
	w.name = "Water"
	w.water_mat = _water_material(cfg, false)
	w.void_mat = _water_material(cfg, true)
	w.wall_mat = CityMaterials.ground(cfg, false)
	w.light_mat = CityMaterials.ground(cfg, true)
	w.light_mat.set_shader_parameter(&"lane_gain", cfg.seawall_light_gain)
	w._add(_void_mesh(outer_bu), w.void_mat, "Void")
	w._add(_sea_mesh(cfg, plan), w.water_mat, "Sea")
	var wall := _wall_meshes(cfg, plan)
	w.wall_edges = int(wall["edges"])
	w._add(wall["face"], w.wall_mat, "SeaWall")
	w._add(wall["light"], w.light_mat, "SeaWallLight")
	var pier := _pier_meshes(cfg, plan, model)
	w.piers = int(pier["count"])
	w._add(pier["deck"], w.wall_mat, "Piers")
	w._add(pier["lamp"], w.light_mat, "PierLamps")
	return w


## The materials CityView3D's day ramp updates with the ground's (the sea wall and pier decks).
func lit_materials() -> Array[ShaderMaterial]:
	return [wall_mat]


## 1 = night tones .. 0 = day (the sea turns blue, its shore-light reflections go out).
func set_night(n: float) -> void:
	for m in [water_mat, void_mat]:
		m.set_shader_parameter(&"night", n)


## The netrun look's blend (NA-22): the sea and the void lifted by `water_look_gain` at 1.
func set_look_blend(lb: float) -> void:
	for m in [water_mat, void_mat]:
		m.set_shader_parameter(&"look_blend", lb)


## 0 freezes the ripple (reduce motion), 1 runs it.
func set_time_scale(s: float) -> void:
	water_mat.set_shader_parameter(&"time_scale", s)


func _add(mesh: Mesh, mat: Material, node_name: String) -> void:
	if mesh == null:
		return
	var mi := MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = mesh
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)


static func _water_material(cfg: CityConfig, is_void: bool) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SHADER
	m.set_shader_parameter(&"void_mode", is_void)
	var cols := {&"deep_night": cfg.water_deep_night, &"deep_day": cfg.water_deep_day, &"shore_night": cfg.water_shore_night,
		&"shore_day": cfg.water_shore_day, &"void_night": cfg.water_void_night, &"void_day": cfg.water_void_day}
	for k: StringName in cols:
		var c: Color = cols[k]
		m.set_shader_parameter(k, Vector3(c.r, c.g, c.b))
	m.set_shader_parameter(&"ripple_bu", cfg.water_ripple_bu)
	m.set_shader_parameter(&"ripple_speed", cfg.water_ripple_speed)
	m.set_shader_parameter(&"ripple_gain", cfg.water_ripple_gain)
	m.set_shader_parameter(&"reflect_reach", cfg.water_reflect_reach_lots)
	m.set_shader_parameter(&"reflect_gain", cfg.water_reflect_gain)
	m.set_shader_parameter(&"reflect_streak", cfg.water_reflect_streak_lots)
	m.set_shader_parameter(&"reflect_width", cfg.water_reflect_width)
	m.set_shader_parameter(&"reflect_share", cfg.water_reflect_share)
	var names: Array[StringName] = [&"reflect_a", &"reflect_b", &"reflect_c", &"reflect_d"]
	for k in names.size():
		var rc: Color = cfg.water_reflect_colors[k % cfg.water_reflect_colors.size()] if not cfg.water_reflect_colors.is_empty() else Color.BLACK
		m.set_shader_parameter(names[k], Vector3(rc.r, rc.g, rc.b))
	m.set_shader_parameter(&"look_gain", cfg.water_look_gain)
	return m


static func _void_mesh(outer_bu: float) -> ArrayMesh:
	var a := MeshArrays.new()
	var h := outer_bu * 0.5
	a.quad([Vector3(-h, VOID_Y, -h), Vector3(h, VOID_Y, -h), Vector3(h, VOID_Y, h), Vector3(-h, VOID_Y, h)], Vector3.UP, Color.BLACK)
	return a.mesh()


## The sea lots of the city rect grown by `water_extend_lots`, as runs along the inland axis (rows for a west / east sea,
## columns for a north / south one): UV.x the lots from the shore (exact: the shore distance is linear along a run),
## UV.y the lots along the shore.
static func _sea_mesh(cfg: CityConfig, plan: CityPlan) -> ArrayMesh:
	var a := MeshArrays.new()
	var r := plan.rect.grow(cfg.water_extend_lots)
	var side := int(plan.coast["side"])
	var rows := side < 2  # runs along i, one per j
	var outer_n := r.size.y if rows else r.size.x
	var inner_n := r.size.x if rows else r.size.y
	for o in outer_n:
		var k := 0
		while k < inner_n:
			var lot := _lot_of(r, rows, o, k)
			if not plan.is_water(lot.x, lot.y):
				k += 1
				continue
			var start := k
			while k < inner_n and plan.is_water(_lot_of(r, rows, o, k).x, _lot_of(r, rows, o, k).y):
				k += 1
			var p0 := Vector2(_lot_of(r, rows, o, start))
			var p1 := Vector2(_lot_of(r, rows, o, k - 1)) + Vector2.ONE
			var corners := [Vector2(p0.x, p0.y), Vector2(p1.x, p0.y), Vector2(p1.x, p1.y), Vector2(p0.x, p1.y)]
			var vs: Array[Vector3] = []
			var uvs: Array[Vector2] = []
			for c: Vector2 in corners:
				vs.append(CityIsoCamera.lot_to_world(cfg, c, SEA_Y))
				uvs.append(Vector2(maxf(-plan.land_depth(c.x, c.y), 0.0), c.y if side < 2 else c.x))
			a.quad(vs, Vector3.UP, Color.BLACK, uvs)
	return a.mesh()


static func _lot_of(r: Rect2i, rows: bool, o: int, k: int) -> Vector2i:
	return Vector2i(r.position.x + k, r.position.y + o) if rows else Vector2i(r.position.x + o, r.position.y + k)


const DIRS: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]


## The sea wall: on each shoreline lot (CityPlan.shoreline) a face on every edge that meets a sea lot, from
## `seawall_drop` under the water to `seawall_h` over it, and a lit coping strip (`seawall_light_h`) on its sea side.
static func _wall_meshes(cfg: CityConfig, plan: CityPlan) -> Dictionary:
	var face := MeshArrays.new()
	var light := MeshArrays.new()
	var edges := 0
	for l in plan.shoreline():
		for d in DIRS:
			if not plan.is_water(l.x + d.x, l.y + d.y):
				continue
			edges += 1
			var e := _edge(l, d)
			var a := CityIsoCamera.lot_to_world(cfg, e[0])
			var b := CityIsoCamera.lot_to_world(cfg, e[1])
			var n := Vector3(d.x, 0.0, d.y)
			face.quad([a + Vector3(0, -cfg.seawall_drop, 0), b + Vector3(0, -cfg.seawall_drop, 0), b + Vector3(0, cfg.seawall_h, 0),
				a + Vector3(0, cfg.seawall_h, 0)], n, cfg.seawall_color)
			var o := n * 0.02
			light.quad([a + o + Vector3(0, cfg.seawall_h - cfg.seawall_light_h, 0), b + o + Vector3(0, cfg.seawall_h - cfg.seawall_light_h, 0),
				b + o + Vector3(0, cfg.seawall_h + 0.01, 0), a + o + Vector3(0, cfg.seawall_h + 0.01, 0)], n, cfg.seawall_light_color)
	return {"face": face.mesh(), "light": light.mesh(), "edges": edges}


## The two lot-space corners of lot `l`'s edge facing `d`.
static func _edge(l: Vector2i, d: Vector2i) -> Array[Vector2]:
	var p := Vector2(l)
	if d == Vector2i(1, 0):
		return [p + Vector2(1, 0), p + Vector2(1, 1)]
	if d == Vector2i(-1, 0):
		return [p, p + Vector2(0, 1)]
	if d == Vector2i(0, 1):
		return [p + Vector2(0, 1), p + Vector2(1, 1)]
	return [p, p + Vector2(1, 0)]


## A pier where a street lot's own direction runs into the sea (along_i streets run along j, along_j along i): a deck
## `pier_len_lots` long, `pier_w_lots` wide, `pier_h` high, and a lamp cube at its end. Sorted by lot, so stable.
static func _pier_meshes(cfg: CityConfig, plan: CityPlan, model: CityModel) -> Dictionary:
	var deck := MeshArrays.new()
	var lamp := MeshArrays.new()
	var count := 0
	var lots: Array = []
	for s: Dictionary in model.streets:
		var ai := bool(s["along_i"])
		var aj := bool(s["along_j"])
		if ai == aj:
			continue  # a crossing (or no direction)
		var l: Vector2i = s["lot"]
		for d: Vector2i in ([Vector2i(0, 1), Vector2i(0, -1)] if ai else [Vector2i(1, 0), Vector2i(-1, 0)]):
			if plan.is_water(l.x + d.x, l.y + d.y):
				lots.append([l, d])
	lots.sort_custom(func(x: Array, y: Array) -> bool:
		var a: Vector2i = x[0]
		var b: Vector2i = y[0]
		if a != b:
			return a.y < b.y if a.y != b.y else a.x < b.x
		var da: Vector2i = x[1]
		var db: Vector2i = y[1]
		return da.y < db.y if da.y != db.y else da.x < db.x)
	for e: Array in lots:
		var l: Vector2i = e[0]
		var d: Vector2i = e[1]
		var c := Vector2(l) + Vector2(0.5, 0.5) + Vector2(d) * 0.5
		var side := Vector2(-d.y, d.x) * cfg.pier_w_lots * 0.5
		var tip := c + Vector2(d) * cfg.pier_len_lots
		_box(deck, cfg, [c - side, c + side, tip + side, tip - side], 0.0, cfg.pier_h, cfg.pier_color)
		var lh := cfg.pier_lamp_bu / cfg.lot_bu * 0.5
		var lc := tip - Vector2(d) * lh * 2.0
		_box(lamp, cfg, [lc + Vector2(-lh, -lh), lc + Vector2(lh, -lh), lc + Vector2(lh, lh), lc + Vector2(-lh, lh)], cfg.pier_h,
			cfg.pier_h + cfg.pier_lamp_bu, cfg.pier_lamp_color)
		count += 1
	return {"deck": deck.mesh(), "lamp": lamp.mesh(), "count": count}


## A prism on lot-space quad `q` (4 corners) from y0 to y1 (BU): its top and four sides.
static func _box(a: MeshArrays, cfg: CityConfig, q: Array, y0: float, y1: float, col: Color) -> void:
	var lo: Array[Vector3] = []
	var hi: Array[Vector3] = []
	for c: Vector2 in q:
		lo.append(CityIsoCamera.lot_to_world(cfg, c, y0))
		hi.append(CityIsoCamera.lot_to_world(cfg, c, y1))
	a.quad([hi[0], hi[1], hi[2], hi[3]], Vector3.UP, col)
	for k in 4:
		var n := (hi[(k + 1) % 4] - hi[k]).cross(Vector3.UP).normalized()
		a.quad([lo[k], lo[(k + 1) % 4], hi[(k + 1) % 4], hi[k]], n, col)


## Growing mesh arrays (two triangles per quad).
class MeshArrays:
	var v := PackedVector3Array()
	var n := PackedVector3Array()
	var c := PackedColorArray()
	var uv := PackedVector2Array()

	func quad(q: Array, nrm: Vector3, col: Color, uvs: Array = []) -> void:
		for k: int in [0, 1, 2, 0, 2, 3]:
			v.append(q[k])
			n.append(nrm)
			c.append(col)
			uv.append(uvs[k] if not uvs.is_empty() else Vector2.ZERO)

	func mesh() -> ArrayMesh:
		if v.is_empty():
			return null
		var arr := []
		arr.resize(Mesh.ARRAY_MAX)
		arr[Mesh.ARRAY_VERTEX] = v
		arr[Mesh.ARRAY_NORMAL] = n
		arr[Mesh.ARRAY_COLOR] = c
		arr[Mesh.ARRAY_TEX_UV] = uv
		var m := ArrayMesh.new()
		m.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arr)
		return m
