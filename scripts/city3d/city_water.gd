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
const SMEAR_SHADER := preload("res://shaders/city/city_water_smear.gdshader")
## Smear sampling step along its path (BU) and the shortest smear kept (BU).
const SMEAR_STEP_BU := 0.5
const SMEAR_MIN_BU := 2.0
## Coping zoom scale is quantised to this step so the strip is rebuilt only when it visibly changes.
const COPING_STEP := 0.25
## Heights (BU) of the void and the sea above the ground plane (the void under the city's ground, the sea over it).
const VOID_Y := -0.04
const SEA_Y := 0.03

var water_mat: ShaderMaterial
var void_mat: ShaderMaterial
## The sea wall's face and the piers' decks (toon-lit; CityView3D's day ramp reaches them) and their lights (emission).
var wall_mat: ShaderMaterial
var light_mat: ShaderMaterial
var smear_mat: ShaderMaterial
var smears: int = 0
## The lot of each smear's light (probe / capture aid), in build order.
var smear_lots: Array[Vector2i] = []
var coping_scale: float = 1.0
var _cfg: CityConfig
var _plan: CityPlan
var _light_mi: MeshInstance3D
var piers: int = 0
var wall_edges: int = 0


## The sea of `plan` on `model`'s city (CityConfig `cfg`), the void spanning `outer_bu` BU round the origin.
static func make(cfg: CityConfig, plan: CityPlan, model: CityModel, outer_bu: float) -> CityWater:
	var w := CityWater.new()
	w.name = "Water"
	w._cfg = cfg
	w._plan = plan
	w.water_mat = _water_material(cfg, false)
	w.void_mat = _water_material(cfg, true)
	w.wall_mat = CityMaterials.ground(cfg, false)
	w.light_mat = CityMaterials.ground(cfg, true)
	w.light_mat.set_shader_parameter(&"lane_gain", cfg.seawall_light_gain)
	w.smear_mat = _smear_material(cfg)
	w._add(_void_mesh(outer_bu), w.void_mat, "Void")
	w._add(_sea_mesh(cfg, plan), w.water_mat, "Sea")
	var wall := _wall_meshes(cfg, plan, 1.0)
	w.wall_edges = int(wall["edges"])
	w._add(wall["face"], w.wall_mat, "SeaWall")
	w._light_mi = w._add(wall["light"], w.light_mat, "SeaWallLight")
	var pier := _pier_meshes(cfg, plan, model)
	w.piers = int(pier["count"])
	w._add(pier["deck"], w.wall_mat, "Piers")
	w._add(pier["lamp"], w.light_mat, "PierLamps")
	var sm := _smear_mesh(cfg, plan, pier["lamp_lots"])
	w.smears = int(sm["count"])
	w.smear_lots = sm["lots"]
	w._add(sm["mesh"], w.smear_mat, "ShoreReflections")
	return w


## The materials CityView3D's day ramp updates with the ground's (the sea wall and pier decks).
func lit_materials() -> Array[ShaderMaterial]:
	return [wall_mat]


## 1 = night tones .. 0 = day (the sea turns blue, its shore-light reflections go out).
func set_night(n: float) -> void:
	for m in [water_mat, void_mat, smear_mat]:
		m.set_shader_parameter(&"night", n)


## The netrun look's blend (NA-22): the sea and the void lifted by `water_look_gain` at 1.
func set_look_blend(lb: float) -> void:
	for m in [water_mat, void_mat, smear_mat]:
		m.set_shader_parameter(&"look_blend", lb)


## 0 freezes the ripple (reduce motion), 1 runs it.
func set_time_scale(s: float) -> void:
	water_mat.set_shader_parameter(&"time_scale", s)
	smear_mat.set_shader_parameter(&"time_scale", s)


## The coping's zoom scale at camera size `ortho` (BU): 1 at and nearer than `coping_ref_ortho`, growing in step with the
## zoom-out up to `coping_zoom_max`, quantised to COPING_STEP.
static func coping_scale_at(cfg: CityConfig, ortho: float) -> float:
	var raw := clampf(ortho / maxf(cfg.coping_ref_ortho, 0.001), 1.0, maxf(cfg.coping_zoom_max, 1.0))
	return snappedf(raw, COPING_STEP)


## The coping's top-strip width (BU) at `scale` (coping_scale_at).
static func coping_width_bu(cfg: CityConfig, scale: float) -> float:
	return cfg.seawall_coping_bu * scale


## The coping's emission gain at `scale`: seawall_light_gain at 1, `coping_gain_far` times that at coping_zoom_max.
static func coping_gain(cfg: CityConfig, scale: float) -> float:
	var span := maxf(cfg.coping_zoom_max - 1.0, 0.001)
	var k := clampf((scale - 1.0) / span, 0.0, 1.0)
	return cfg.seawall_light_gain * lerpf(1.0, cfg.coping_gain_far, k)


## The camera size changed: the coping strip is rebuilt wider (and brighter) when the zoom-out scale moved a step.
func set_zoom(ortho: float) -> void:
	var sc := coping_scale_at(_cfg, ortho)
	if is_equal_approx(sc, coping_scale) and _light_mi != null:
		return
	coping_scale = sc
	light_mat.set_shader_parameter(&"lane_gain", coping_gain(_cfg, sc))
	if _light_mi != null:
		_light_mi.mesh = _wall_meshes(_cfg, _plan, sc)["light"]


func _add(mesh: Mesh, mat: Material, node_name: String) -> MeshInstance3D:
	if mesh == null:
		return null
	var mi := MeshInstance3D.new()
	mi.name = node_name
	mi.mesh = mesh
	mi.material_override = mat
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(mi)
	return mi


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
	m.set_shader_parameter(&"shallow_lots", cfg.water_shallow_lots)
	m.set_shader_parameter(&"caustic_bu", cfg.water_caustic_bu)
	m.set_shader_parameter(&"caustic_speed", cfg.water_caustic_speed)
	m.set_shader_parameter(&"caustic_gain", cfg.water_caustic_gain)
	m.set_shader_parameter(&"caustic_night", Vector3(cfg.water_caustic_night.r, cfg.water_caustic_night.g, cfg.water_caustic_night.b))
	m.set_shader_parameter(&"caustic_day", Vector3(cfg.water_caustic_day.r, cfg.water_caustic_day.g, cfg.water_caustic_day.b))
	m.set_shader_parameter(&"foam_lots", cfg.water_foam_lots)
	m.set_shader_parameter(&"foam_gain", cfg.water_foam_gain)
	m.set_shader_parameter(&"look_gain", cfg.water_look_gain)
	return m


static func _smear_material(cfg: CityConfig) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = SMEAR_SHADER
	m.set_shader_parameter(&"gain", cfg.water_reflect_gain)
	m.set_shader_parameter(&"length_bu", cfg.water_reflect_reach_lots * cfg.lot_bu)
	m.set_shader_parameter(&"ripple_bu", cfg.water_ripple_bu)
	m.set_shader_parameter(&"ripple_speed", cfg.water_ripple_speed)
	m.set_shader_parameter(&"look_gain", cfg.water_look_gain)
	return m


## Screen-down on the ground (the horizontal direction toward the camera, world XZ) for the config's yaw.
static func screen_down(cfg: CityConfig) -> Vector2:
	var yw := deg_to_rad(cfg.yaw_deg)
	return Vector2(-cos(yw), sin(yw))


## A stable 0..1 hash of a shore edge (lot, direction) and a salt, no randomness service needed (pure function of the plan).
static func edge_hash(l: Vector2i, d: Vector2i, salt: int) -> float:
	var h: int = (l.x * 73856093) ^ (l.y * 19349663) ^ (d.x * 83492791) ^ (d.y * 2654435761) ^ (salt * 40503)
	h = (h ^ (h >> 13)) * 1274126177
	h = h ^ (h >> 16)
	return float(h & 0xFFFF) / 65535.0


## The shore lights' reflections: on `water_reflect_share` of the sea-wall edges a light sits at a hashed point along the
## edge, and a smear hangs straight down the screen from its foot, as long as it stays over water, at most
## `water_reflect_reach_lots`. Edges whose sea lies up the screen (the near shore) get none: the wall hides it.
static func _smear_mesh(cfg: CityConfig, plan: CityPlan, lamps: Array[Vector2]) -> Dictionary:
	var a := MeshArrays.new()
	var count := 0
	var lots: Array[Vector2i] = []
	for l in plan.shoreline():
		for d in DIRS:
			if not plan.is_water(l.x + d.x, l.y + d.y):
				continue
			if edge_hash(l, d, 1) >= cfg.water_reflect_share:
				continue
			var e := _edge(l, d)
			var f := 0.15 + 0.7 * edge_hash(l, d, 2)
			var start := CityIsoCamera.lot_to_world(cfg, e[0].lerp(e[1], f), SEA_Y + 0.02)
			start += Vector3(d.x, 0.0, d.y) * 0.15
			if _add_smear(a, cfg, plan, start, edge_hash(l, d, 3), edge_hash(l, d, 4)):
				count += 1
				lots.append(l)
	# Each pier's end lamp stands over the water: its reflection hangs right under it.
	for lc: Vector2 in lamps:
		var start := CityIsoCamera.lot_to_world(cfg, lc, SEA_Y + 0.02)
		var pick := edge_hash(Vector2i(lc.floor()), Vector2i.ZERO, 5)
		if _add_smear(a, cfg, plan, start, pick, edge_hash(Vector2i(lc.floor()), Vector2i.ZERO, 6)):
			count += 1
	return {"mesh": a.mesh(), "count": count, "lots": lots}


## One smear quad from world point `start` straight down the screen, clipped where the water ends; false when it would
## be shorter than SMEAR_MIN_BU.
static func _add_smear(a: MeshArrays, cfg: CityConfig, plan: CityPlan, start: Vector3, pick: float, seed_: float) -> bool:
	var down := screen_down(cfg)
	var reach := cfg.water_reflect_reach_lots * cfg.lot_bu
	var dir := Vector3(down.x, 0.0, down.y)
	var length := 0.0
	while length < reach:
		var lot := CityIsoCamera.world_to_lot(cfg, start + dir * (length + SMEAR_STEP_BU))
		if not plan.is_water(floori(lot.x), floori(lot.y)):
			break
		length += SMEAR_STEP_BU
	if length < SMEAR_MIN_BU:
		return false
	var palette := cfg.water_reflect_colors
	var col := Color.BLACK
	if not palette.is_empty():
		col = palette[int(pick * 0.999 * palette.size())]
	col.a = seed_
	var side := Vector3(-down.y, 0.0, down.x) * cfg.water_smear_w_bu * 0.5
	var end := start + dir * length
	a.quad([start - side, start + side, end + side, end - side], Vector3.UP, col,
		[Vector2(0, -1), Vector2(0, 1), Vector2(length / reach, 1), Vector2(length / reach, -1)])
	return true


static func _void_mesh(outer_bu: float) -> ArrayMesh:
	var a := MeshArrays.new()
	var h := outer_bu * 0.5
	var far := Vector2(1000.0, 0.0)  # deep water when the whole-city look draws the void as sea
	a.quad([Vector3(-h, VOID_Y, -h), Vector3(h, VOID_Y, -h), Vector3(h, VOID_Y, h), Vector3(-h, VOID_Y, h)], Vector3.UP, Color.BLACK,
			[far, far, far, far])
	return a.mesh()


## The sea lots of the city rect grown by `water_extend_lots`, as runs along the inland axis (rows for a west / east sea,
## columns for a north / south one): UV.x the lots from the shore (exact: the shore distance is linear along a run),
## UV.y the lots along the shore. CITY-A2 r2: with terrain, over the terrain's whole land (its coarse rect), wet where the
## terrain says (A2's coastline out to the extent, the land wrapping round it).
static func _sea_mesh(cfg: CityConfig, plan: CityPlan) -> ArrayMesh:
	var a := MeshArrays.new()
	var t := plan.terrain
	var r := t.coarse_rect if t != null else plan.rect.grow(cfg.water_extend_lots)
	var wet := PackedByteArray()
	wet.resize(r.size.x * r.size.y)
	for j in r.size.y:
		for i in r.size.x:
			var l := r.position + Vector2i(i, j)
			var w := t.is_water_at(l.x + 0.5, l.y + 0.5) if t != null else plan.is_water(l.x, l.y)
			wet[j * r.size.x + i] = 1 if w else 0
	var is_wet := func(l: Vector2i) -> bool: return wet[(l.y - r.position.y) * r.size.x + (l.x - r.position.x)] != 0
	if t != null:
		return _sea_field_mesh(cfg, r, wet)
	var side := int(plan.coast["side"])
	var rows := side < 2  # runs along i, one per j
	var outer_n := r.size.y if rows else r.size.x
	var inner_n := r.size.x if rows else r.size.y
	for o in outer_n:
		var k := 0
		while k < inner_n:
			var lot := _lot_of(r, rows, o, k)
			if not is_wet.call(lot):
				k += 1
				continue
			var start := k
			while k < inner_n and is_wet.call(_lot_of(r, rows, o, k)):
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


## LOOK L5 (A2 plate): the sea over the terrain's wet lots `wet` (row order over `r`) with UV.x the lots to the nearest
## land (a chamfer distance field, capped at `sea_field_cap_lots`), so the shallows and foam hug every shore (the bay,
## the lagoon, the coast past the raster), not the old straight coast. Lots whose corners all sit at the cap merge into
## runs; the rest are one quad each. UV.y = lot row.
static func _sea_field_mesh(cfg: CityConfig, r: Rect2i, wet: PackedByteArray) -> ArrayMesh:
	var a := MeshArrays.new()
	var w := r.size.x
	var h := r.size.y
	var cap := cfg.sea_field_cap_lots
	var d := PackedFloat32Array()
	d.resize(w * h)
	for k in w * h:
		d[k] = cap if wet[k] != 0 else 0.0
	for pass_ in 2:
		var j0 := 0 if pass_ == 0 else h - 1
		var j1 := h if pass_ == 0 else -1
		var sj := 1 if pass_ == 0 else -1
		var j := j0
		while j != j1:
			var i := 0 if pass_ == 0 else w - 1
			while i >= 0 and i < w:
				var k := j * w + i
				if d[k] > 0.0:
					var best := d[k]
					for o: Vector3 in [Vector3(-sj, 0, 1.0), Vector3(0, -sj, 1.0), Vector3(-sj, -sj, DIAG), Vector3(sj, -sj, DIAG)]:
						var ii := i + int(o.x)
						var jj := j + int(o.y)
						if ii >= 0 and ii < w and jj >= 0 and jj < h:
							best = minf(best, d[jj * w + ii] + o.z)
					d[k] = best
				i += sj
			j += sj
	# Corner value: the least of its (up to) four lots, land lots 0, so a corner on the shore is 0.
	var cd := func(ci: int, cj: int) -> float:
		var m := cap
		for o: Vector2i in [Vector2i(-1, -1), Vector2i(0, -1), Vector2i(-1, 0), Vector2i(0, 0)]:
			var ii := ci + o.x
			var jj := cj + o.y
			if ii >= 0 and ii < w and jj >= 0 and jj < h:
				m = minf(m, d[jj * w + ii])
		return m
	for j in h:
		var i := 0
		while i < w:
			if wet[j * w + i] == 0:
				i += 1
				continue
			var e := [cd.call(i, j), cd.call(i + 1, j), cd.call(i + 1, j + 1), cd.call(i, j + 1)]
			var i1 := i + 1
			if e[0] >= cap and e[1] >= cap and e[2] >= cap and e[3] >= cap:
				while i1 < w and wet[j * w + i1] != 0 and cd.call(i1 + 1, j) >= cap and cd.call(i1 + 1, j + 1) >= cap:
					i1 += 1
			var p0 := Vector2(r.position.x + i, r.position.y + j)
			var p1 := Vector2(r.position.x + i1, r.position.y + j + 1)
			var corners := [p0, Vector2(p1.x, p0.y), p1, Vector2(p0.x, p1.y)]
			var ev := [e[0], cd.call(i1, j), cd.call(i1, j + 1), e[3]]
			var vs: Array[Vector3] = []
			var uvs: Array[Vector2] = []
			for c in 4:
				vs.append(CityIsoCamera.lot_to_world(cfg, corners[c], SEA_Y))
				uvs.append(Vector2(ev[c], corners[c].y))
			a.quad(vs, Vector3.UP, Color.BLACK, uvs)
			i = i1
	return a.mesh()


static func _lot_of(r: Rect2i, rows: bool, o: int, k: int) -> Vector2i:
	return Vector2i(r.position.x + k, r.position.y + o) if rows else Vector2i(r.position.x + o, r.position.y + k)


const DIRS: Array[Vector2i] = [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]


## The sea wall: on each shoreline lot (CityPlan.shoreline) a face on every edge that meets a sea lot, from
## `seawall_drop` under the water to `seawall_h` over it, and a lit coping strip (`seawall_light_h`) on its sea side.
static func _wall_meshes(cfg: CityConfig, plan: CityPlan, scale: float) -> Dictionary:
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
			# The coping's top strip, reaching out over the water by its zoom-scaled width.
			var wd := coping_width_bu(cfg, scale)
			var top := cfg.seawall_h + 0.02
			light.quad([a + n * -wd * 0.25 + Vector3(0, top, 0), b + n * -wd * 0.25 + Vector3(0, top, 0),
				b + n * wd * 0.75 + Vector3(0, top, 0), a + n * wd * 0.75 + Vector3(0, top, 0)], Vector3.UP, cfg.seawall_light_color)
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
	var lamp_lots: Array[Vector2] = []
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
		lamp_lots.append(lc)
		count += 1
	return {"deck": deck.mesh(), "lamp": lamp.mesh(), "count": count, "lamp_lots": lamp_lots}


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
