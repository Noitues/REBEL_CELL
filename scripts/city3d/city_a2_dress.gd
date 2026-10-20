class_name CityA2Dress
extends RefCounted
## LOOK L5 (designer 2026-10-20, whole-city plate parity): the life of the whole-city pose: the port on the bay (lit piers,
## gantry cranes, moored freighters, a container yard on the terminal), ships under way in the bay and the sea, the bay
## islands' buildings (a fort, a lighthouse, a hamlet), police helicopters with searchlights on the city and police light
## bars on the ring road and motorways. Hulls and buildings carry 5b's landmark material names (CityA2Hqs._Build), so
## LandmarkMaterials styles them by day and night; the lights run police_light.gdshader and spot_light.gdshader.
## Numbers from CityConfig.a2_dress. View-side only; every draw from a fixed hash of the piece's index.

const TOON := CityA2Hqs.TOON
const WIN := CityA2Hqs.WIN
const NEON := CityA2Hqs.NEON
const POLICE_SHADER := preload("res://shaders/city/police_light.gdshader")
const SPOT_SHADER := preload("res://shaders/city/spot_light.gdshader")
const POOL_SHADER := preload("res://shaders/city/spot_pool.gdshader")
const SALT_PORT := 811
const SALT_SHIP := 823
const SALT_ISLE := 827
const SALT_HELI := 829
const SALT_COP := 839

var cfg: CityConfig
var ras: CityA2Raster
var terrain: CityA2Terrain
var look: Dictionary
var islands: Array[Dictionary] = []
var b := CityA2Hqs._Build.new()
var blink := SurfaceTool.new()
var spot := SurfaceTool.new()
var pool := SurfaceTool.new()
var _blinks: int = 0
var _spots: int = 0
## The lots the port's yard covers (its buildings give way): Vector2i -> true.
var mask: Dictionary = {}


## The dressing node of the whole-city pose of `plan`, on bay `islands` (CityWater.islands_of): {"node": Node3D,
## "fx": Array[ShaderMaterial] (police, spot), "mask": the cleared lots}; empty when the plan has no A2.
static func make(p_cfg: CityConfig, plan: CityPlan, p_islands: Array[Dictionary]) -> Dictionary:
	if plan.a2 == null or plan.terrain == null:
		return {}
	var d := CityA2Dress.new()
	d.cfg = p_cfg
	d.ras = plan.a2
	d.terrain = plan.terrain
	d.look = p_cfg.a2_dress
	d.islands = p_islands
	d.blink.begin(Mesh.PRIMITIVE_TRIANGLES)
	d.spot.begin(Mesh.PRIMITIVE_TRIANGLES)
	d.pool.begin(Mesh.PRIMITIVE_TRIANGLES)
	d._port()
	d._ships()
	d._islands()
	d._helis(plan.a2.a2)
	d._police(plan.a2.a2)
	var root := Node3D.new()
	root.name = "A2Dress"
	var body := MeshInstance3D.new()
	body.name = "Body"
	body.mesh = d.b.commit()
	root.add_child(body)
	var fx: Array[ShaderMaterial] = []
	if d._blinks > 0:
		fx.append(d._fx_node(root, "Blinks", d.blink, POLICE_SHADER, d.look.get("police", {})))
	if d._spots > 0:
		fx.append(d._fx_node(root, "Spots", d.spot, SPOT_SHADER, d.look.get("spot", {})))
		fx.append(d._fx_node(root, "Pools", d.pool, POOL_SHADER, d.look.get("pool", {})))
	return {"node": root, "fx": fx, "mask": d.mask}


func _fx_node(root: Node3D, nm: String, st: SurfaceTool, sh: Shader, params: Dictionary) -> ShaderMaterial:
	st.generate_normals()
	var mi := MeshInstance3D.new()
	mi.name = nm
	mi.mesh = st.commit()
	mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var m := ShaderMaterial.new()
	m.shader = sh
	for k: String in params:
		m.set_shader_parameter(StringName(k), params[k])
	mi.material_override = m
	root.add_child(mi)
	return m


static func _h(i: int, salt: int) -> float:
	var x := (i * 374761393 + salt * 668265263) & 0x7fffffff
	x = ((x ^ (x >> 13)) * 1274126177) & 0x7fffffff
	return float(x ^ (x >> 16)) / float(0x7fffffff)


## World point of A2 point `m` (metres) at height `y` BU.
func w(m: Vector2, y: float) -> Vector3:
	return CityIsoCamera.lot_to_world(cfg, ras.lot_of(m), y)


func ground_y(m: Vector2) -> float:
	var l := ras.lot_of(m)
	return terrain.height_at(l.x, l.y)


func bu(metres: float) -> float:
	return metres / ras.metres_per_lot * cfg.lot_bu


func _col(key: String, fb: Color) -> Color:
	return look.get(key, fb)


## A flat-topped box on world point `c`, `along` its long axis (world, flat), size x (length) z (width), y0..y1.
func box(mat: String, c: Vector3, along: Vector3, size_x: float, size_z: float, y0: float, y1: float, col: Color) -> void:
	var d := Vector3(along.x, 0.0, along.z).normalized()
	var s := Vector3(-d.z, 0.0, d.x)
	b.box_between(c - d * size_x * 0.5, c + d * size_x * 0.5, s, size_z, y0, y1, mat, col)


## A blinking light (police_light.gdshader: white = red / blue bar, any other colour blinks itself) at `c`, phase `ph`.
func light(c: Vector3, along: Vector3, sx: float, sz: float, sy: float, col: Color, ph: float) -> void:
	var d := Vector3(along.x, 0.0, along.z).normalized() * sx * 0.5
	var s := Vector3(-d.z, 0.0, d.x).normalized() * sz * 0.5
	var up := Vector3(0.0, sy, 0.0)
	var q: Array[Vector3] = [c - d - s, c + d - s, c + d + s, c - d + s]
	var faces: Array = [[q[0] + up, q[1] + up, q[2] + up, q[3] + up]]
	for k in 4:
		faces.append([q[k], q[(k + 1) % 4], q[(k + 1) % 4] + up, q[k] + up])
	for f: Array in faces:
		for t: Array in [[0, 1, 2], [0, 2, 3]]:
			for i: int in t:
				blink.set_color(Color(col.r, col.g, col.b, ph))
				blink.add_vertex(f[i])
	_blinks += 1


# --- The port ------------------------------------------------------------------------------------------------------------

func _port() -> void:
	var port: Dictionary = ras.a2.port
	if port.is_empty():
		return
	var pl := float(look.get("pier_lift_bu", 0.8))
	var concrete := _col("concrete", Color(0.62, 0.62, 0.60))
	var lamp := _col("lamp", Color(1.0, 0.8, 0.5))
	var crane_cols: Array = look.get("crane_cols", [Color(0.85, 0.30, 0.18), Color(0.95, 0.70, 0.20)])
	var gap_m := float(look.get("crane_gap_m", 260.0))
	var crane_h := float(look.get("crane_h_bu", 4.5))
	var n := 0
	for p: Dictionary in port["piers"]:
		var br := deg_to_rad(float(p["bearing_deg"]))
		var dm := Vector2(sin(br), cos(br))
		var nm := Vector2(-dm.y, dm.x)
		var base: Vector2 = p["base"]
		var ln := float(p["length"])
		var wd := float(p["width"])
		var a := w(base, 0.0)
		var e := w(base + dm * ln, 0.0)
		var side := w(base + nm, 0.0) - a
		b.box_between(a, e, side, bu(wd), -1.5, pl, TOON, concrete)
		b.box_between(a, e, side, bu(wd) * 0.08, pl, pl + 0.12, NEON, lamp)
		# Gantry cranes along both edges, their booms over the water; freighters moored under them.
		var k := 0
		var t := gap_m * 0.6
		while t < ln - gap_m * 0.3:
			for sgn: float in [-1.0, 1.0]:
				var foot := base + dm * t + nm * sgn * wd * 0.32
				var col: Color = crane_cols[(n + k) % crane_cols.size()]
				_crane(foot, nm * sgn, dm, pl, crane_h, col)
				k += 1
			t += gap_m
		for sgn: float in [-1.0, 1.0]:
			if _h(n * 2 + int(sgn > 0.0), SALT_PORT) < float(look.get("moored_share", 0.8)):
				var off := wd * 0.5 + float(look.get("moor_gap_m", 40.0)) + 0.0
				var len_m := ln * lerpf(0.45, 0.75, _h(n * 7 + int(sgn > 0.0), SALT_PORT + 1))
				var c := base + dm * (ln * 0.5) + nm * sgn * (off + len_m * 0.08)
				_ship(c, dm, len_m, true, n * 13 + int(sgn > 0.0), false)
		n += 1
	_yard(port["terminal"])


func _crane(foot: Vector2, out: Vector2, along: Vector2, pl: float, h: float, col: Color) -> void:
	var span := bu(float(look.get("crane_span_m", 50.0)))
	var reach := bu(float(look.get("crane_reach_m", 70.0)))
	var leg := 0.35
	var f0 := w(foot - out * span * 0.0, 0.0)
	var o := (w(foot + out, 0.0) - f0).normalized()
	var a := (w(foot + along, 0.0) - f0).normalized()
	var back := f0 - o * span
	for p: Vector3 in [f0 - a * span * 0.35, f0 + a * span * 0.35, back - a * span * 0.35, back + a * span * 0.35]:
		b.box_between(p + Vector3(0.0, pl, 0.0), p + Vector3(0.0, pl + h, 0.0), a, leg, 0.0, 0.0, TOON, col, true)
	# The boom over the water and its back stay; a red light at its tip.
	var top := pl + h
	var tip := f0 + o * reach
	b.box_between(back - o * span * 0.4, tip, a, span * 0.7, top, top + 0.45, TOON, col)
	b.box_between(back, f0, a, span * 0.8, top - 0.9, top - 0.6, TOON, col * 0.8)
	light(tip + Vector3(0.0, top + 0.45, 0.0), o, 0.5, 0.5, 0.5, _col("tip_light", Color(1.0, 0.15, 0.1)), _h(int(tip.x * 7.0), SALT_PORT + 2))


func _yard(poly: PackedVector2Array) -> void:
	if poly.size() < 3:
		return
	var lo := Vector2(INF, INF)
	var hi := Vector2(-INF, -INF)
	for p in poly:
		lo = lo.min(p)
		hi = hi.max(p)
	var cols: Array = look.get("container_cols", [Color(0.70, 0.20, 0.14), Color(0.16, 0.35, 0.62)])
	var row_m := float(look.get("yard_row_m", 70.0))
	var bay_m := float(look.get("yard_bay_m", 140.0))
	var lift := cfg.a2_port_lift_bu
	var unit := float(look.get("container_h_bu", 0.45))
	var lamp := _col("lamp", Color(1.0, 0.8, 0.5))
	var i := 0
	var y := lo.y + row_m * 0.5
	while y < hi.y:
		var x := lo.x + bay_m * 0.5
		while x < hi.x:
			var m := Vector2(x, y)
			if Geometry2D.is_point_in_polygon(m, poly):
				var g := maxf(ground_y(m), 0.0) + lift
				var c := w(m, 0.0)
				var ax := w(m + Vector2(1.0, 0.0), 0.0) - c
				if _h(i, SALT_PORT + 3) < float(look.get("yard_fill", 0.85)):
					var stack := 1 + int(_h(i, SALT_PORT + 4) * 3.0)
					var col: Color = cols[int(_h(i, SALT_PORT + 5) * cols.size()) % cols.size()]
					box(TOON, c, ax, bu(bay_m * 0.86), bu(row_m * 0.7), g, g + unit * stack, col)
				elif _h(i, SALT_PORT + 6) < 0.35:
					# A yard lamp mast.
					b.box_between(c + Vector3(0.0, g, 0.0), c + Vector3(0.0, g + 3.0, 0.0), ax, 0.25, 0.0, 0.0, TOON, Color(0.4, 0.4, 0.42), true)
					b.box_between(c + Vector3(0.0, g + 3.0, 0.0), c + Vector3(0.0, g + 3.4, 0.0), ax, 0.8, 0.0, 0.0, NEON, lamp, true)
			i += 1
			x += bay_m
		y += row_m
	# The terminal's lots, wholly: buildings give way to the yard.
	var l0 := ras.lot_of(lo)
	var l1 := ras.lot_of(hi)
	for j in range(floori(minf(l0.y, l1.y)) - 1, ceili(maxf(l0.y, l1.y)) + 1):
		for ii in range(floori(minf(l0.x, l1.x)) - 1, ceili(maxf(l0.x, l1.x)) + 1):
			if Geometry2D.is_point_in_polygon(ras.metres_of(Vector2(ii + 0.5, j + 0.5)), poly):
				mask[Vector2i(ii, j)] = true


# --- Ships ---------------------------------------------------------------------------------------------------------------

## A ship centred on A2 point `c`, heading `dir` (metres), `len_m` long: hull, deck house with lit windows, deck cargo,
## nav lights, and a wake when `wake`.
func _ship(c: Vector2, dir: Vector2, len_m: float, cargo: bool, idx: int, wake: bool) -> void:
	var L := bu(len_m)
	var W := L * float(look.get("ship_beam_k", 0.16))
	var fb := float(look.get("ship_freeboard_bu", 0.6))
	var hulls: Array = look.get("hull_cols", [Color(0.18, 0.20, 0.24), Color(0.45, 0.14, 0.12)])
	var hull: Color = hulls[idx % hulls.size()]
	var cw := w(c, 0.0)
	var f := (w(c + dir.normalized(), 0.0) - cw).normalized()
	var s := Vector3(-f.z, 0.0, f.x)
	var stern := cw - f * L * 0.5
	var shoulder := cw + f * L * 0.32
	var bow := cw + f * L * 0.5
	# The hull: a box to the shoulder, a wedge to the bow.
	b.box_between(stern, shoulder, s, W, -0.3, fb, TOON, hull)
	for y: float in [fb]:
		b.tri(TOON, shoulder - s * W * 0.5 + Vector3(0, y, 0), bow + Vector3(0, y, 0), shoulder + s * W * 0.5 + Vector3(0, y, 0), hull * 1.1)
	b.quad(TOON, shoulder - s * W * 0.5 + Vector3(0, -0.3, 0), bow + Vector3(0, -0.3, 0), bow + Vector3(0, fb, 0), shoulder - s * W * 0.5 + Vector3(0, fb, 0), hull)
	b.quad(TOON, bow + Vector3(0, -0.3, 0), shoulder + s * W * 0.5 + Vector3(0, -0.3, 0), shoulder + s * W * 0.5 + Vector3(0, fb, 0), bow + Vector3(0, fb, 0), hull)
	# The deck house at the stern, windows round it.
	var house := stern + f * L * 0.1
	var hh := float(look.get("house_h_bu", 1.4))
	var white := _col("house", Color(0.90, 0.90, 0.88))
	box(TOON, house, f, L * 0.12, W * 0.8, fb, fb + hh, white)
	box(WIN, house, f, L * 0.122, W * 0.81, fb + hh * 0.55, fb + hh * 0.75, _col("ship_win", Color(1.0, 0.85, 0.55)))
	if cargo:
		var cols: Array = look.get("container_cols", [Color(0.70, 0.20, 0.14)])
		var rows := 4
		for r in rows:
			var t0 := 0.2 + 0.6 * float(r) / rows
			var t1 := 0.2 + 0.6 * float(r + 1) / rows - 0.02
			var stack := 1 + int(_h(idx * 5 + r, SALT_SHIP) * 3.0)
			var col: Color = cols[int(_h(idx * 5 + r, SALT_SHIP + 1) * cols.size()) % cols.size()]
			b.box_between(stern + f * L * t0, stern + f * L * t1, s, W * 0.82, fb, fb + 0.45 * stack, TOON, col)
	# Nav lights: red to port, green to starboard, a white masthead.
	light(shoulder - s * W * 0.5 + Vector3(0, fb, 0), f, 0.35, 0.35, 0.35, Color(1.0, 0.1, 0.1), 0.85)
	light(shoulder + s * W * 0.5 + Vector3(0, fb, 0), f, 0.35, 0.35, 0.35, Color(0.1, 1.0, 0.3), 0.85)
	light(house + Vector3(0, fb + hh + 0.4, 0), f, 0.4, 0.4, 0.4, Color(1.0, 0.95, 0.75), _h(idx, SALT_SHIP + 2))
	if wake:
		var wl := L * float(look.get("wake_k", 1.6))
		var ww := float(look.get("wake_w_k", 1.4))
		var foam := _col("wake", Color(0.80, 0.90, 0.92))
		var y := 0.06
		var tail := stern - f * wl
		b.tri(TOON, stern - s * W * 0.45 + Vector3(0, y, 0), stern + s * W * 0.45 + Vector3(0, y, 0), tail + s * W * ww + Vector3(0, y, 0), foam)
		b.tri(TOON, stern - s * W * 0.45 + Vector3(0, y, 0), tail + s * W * ww + Vector3(0, y, 0), tail - s * W * ww + Vector3(0, y, 0), foam * 0.9)


## True when A2 point `m` is open water: in the ocean, deep enough, off the islands and the port.
func _open(m: Vector2, poly: PackedVector2Array) -> bool:
	if not Geometry2D.is_point_in_polygon(m, poly):
		return false
	var l := ras.lot_of(m)
	if not ras.is_water(floori(l.x), floori(l.y)):
		return false
	for it: Dictionary in islands:
		if CityWater.island_rho(cfg, it, l) < float(look.get("ship_isle_rho", 2.4)):
			return false
	return true


func _ships() -> void:
	var poly: PackedVector2Array = ras.a2.ocean
	if poly.size() < 3:
		return
	var box_m: Rect2 = look.get("ship_rect_m", Rect2(-12000.0, -12000.0, 24000.0, 21000.0))
	var want := int(look.get("ships", 14))
	var placed: Array[Vector2] = []
	var tries := 0
	var i := 0
	while placed.size() < want and tries < want * 40:
		var m := box_m.position + Vector2(_h(tries, SALT_SHIP + 3), _h(tries, SALT_SHIP + 4)) * box_m.size
		tries += 1
		if not _open(m, poly):
			continue
		var ok := true
		for q in placed:
			if q.distance_to(m) < float(look.get("ship_gap_m", 900.0)):
				ok = false
				break
		if not ok:
			continue
		var an := _h(i, SALT_SHIP + 5) * TAU
		var len_m := lerpf(float(look.get("ship_len_m", Vector2(120.0, 320.0)).x), float(look.get("ship_len_m", Vector2(120.0, 320.0)).y), _h(i, SALT_SHIP + 6))
		_ship(m, Vector2(cos(an), sin(an)), len_m, _h(i, SALT_SHIP + 7) < 0.6, 100 + i, true)
		placed.append(m)
		i += 1


# --- Islands -------------------------------------------------------------------------------------------------------------

func _isle_y(at: Vector2) -> float:
	return CitySeabedKit.bed_z(cfg, terrain, at, cfg.sea_field_cap_lots, true, islands)


func _islands() -> void:
	var stone := _col("isle_stone", Color(0.66, 0.62, 0.55))
	var roof := _col("isle_roof", Color(0.55, 0.30, 0.22))
	var win := _col("isle_win", Color(1.0, 0.82, 0.5))
	for n in islands.size():
		var it: Dictionary = islands[n]
		var c: Vector2 = it["c"]
		var r := float(it["r"])
		var asp := float(it.get("a", 1.0))
		var rot := float(it.get("rot", 0.0))
		var ax := Vector2(cos(rot), sin(rot)) * sqrt(asp)
		var ay := Vector2(-sin(rot), cos(rot)) / sqrt(asp)
		var pick := n % 3
		if pick == 0:
			# A star fort: a low wall round the crown, bastions, a keep with lit slits.
			var fr := r * 0.42
			var cy := _isle_y(c)
			var cw := CityIsoCamera.lot_to_world(cfg, c, 0.0)
			var nb := 5
			for k in nb:
				var a0 := TAU * k / nb
				var a1 := TAU * (k + 1) / nb
				var p0 := c + (ax * cos(a0) + ay * sin(a0)) * fr
				var p1 := c + (ax * cos(a1) + ay * sin(a1)) * fr
				var w0 := CityIsoCamera.lot_to_world(cfg, p0, 0.0)
				var w1 := CityIsoCamera.lot_to_world(cfg, p1, 0.0)
				var y := minf(_isle_y(p0), _isle_y(p1))
				b.box_between(w0, w1, Vector3(-(w1 - w0).z, 0.0, (w1 - w0).x), 0.7, y - 0.5, y + 1.2, TOON, stone)
				box(TOON, w0, w1 - w0, 2.0, 2.0, y - 0.5, y + 1.5, stone * 0.92)
			box(TOON, cw, Vector3.RIGHT, 3.0, 3.0, cy - 0.3, cy + 3.2, stone)
			box(WIN, cw, Vector3.RIGHT, 3.05, 3.05, cy + 2.0, cy + 2.4, win)
		elif pick == 1:
			# A lighthouse on the far end, red and white bands, its lamp blinking.
			var p := c + ax * r * 0.55
			var y := _isle_y(p)
			var lw := CityIsoCamera.lot_to_world(cfg, p, 0.0)
			var bands := 5
			for k in bands:
				var col := Color(0.92, 0.92, 0.9) if k % 2 == 0 else Color(0.75, 0.15, 0.12)
				b.box_between(lw + Vector3(0, y + 1.2 * k, 0), lw + Vector3(0, y + 1.2 * (k + 1), 0), Vector3.RIGHT, 1.1 - 0.08 * k, 0.0, 0.0, TOON, col, true)
			b.box_between(lw + Vector3(0, y + 1.2 * bands, 0), lw + Vector3(0, y + 1.2 * bands + 0.8, 0), Vector3.RIGHT, 1.0, 0.0, 0.0, NEON, Color(1.0, 0.9, 0.6), true)
			light(lw + Vector3(0, y + 1.2 * bands + 0.8, 0), Vector3.RIGHT, 0.9, 0.9, 0.5, Color(1.0, 0.95, 0.7), 0.1 * n)
			_hamlet(c - ax * r * 0.2, ax, ay, r * 0.3, n, stone, roof, win, 5)
		else:
			_hamlet(c, ax, ay, r * 0.4, n, stone, roof, win, 9)


## A cluster of `count` small houses round lot point `c` within `rr` lots on the island's axes.
func _hamlet(c: Vector2, ax: Vector2, ay: Vector2, rr: float, n: int, wall: Color, roof: Color, win: Color, count: int) -> void:
	for k in count:
		var u := (_h(n * 31 + k, SALT_ISLE) * 2.0 - 1.0) * rr
		var v := (_h(n * 31 + k, SALT_ISLE + 1) * 2.0 - 1.0) * rr * 0.6
		var p := c + ax * u + ay * v
		var y := _isle_y(p)
		if y < 0.4:
			continue
		var pw := CityIsoCamera.lot_to_world(cfg, p, 0.0)
		var dir := Vector3(ax.x, 0.0, ax.y)
		var hgt := 1.0 + _h(n * 31 + k, SALT_ISLE + 2) * 1.6
		box(TOON, pw, dir, 2.2, 1.6, y - 0.4, y + hgt, wall)
		box(TOON, pw, dir, 2.4, 1.8, y + hgt, y + hgt + 0.35, roof)
		if _h(n * 31 + k, SALT_ISLE + 3) < 0.7:
			box(WIN, pw, dir, 2.22, 1.62, y + hgt * 0.45, y + hgt * 0.7, win)


# --- Helicopters ---------------------------------------------------------------------------------------------------------

func _helis(a2: CityPlanA2) -> void:
	var count := int(look.get("helis", 6))
	if count <= 0 or a2.districts.is_empty():
		return
	var alt := float(look.get("heli_alt_bu", 38.0))
	var reach := float(look.get("heli_reach_m", 900.0))
	var body := _col("heli_body", Color(0.12, 0.13, 0.16))
	var beam := _col("spot_col", Color(0.85, 0.92, 1.0))
	var pool_r := float(look.get("pool_r_bu", 5.0))
	var ids: Array = []
	for di: Dictionary in a2.districts:
		ids.append(di)
	ids.sort_custom(func(p: Dictionary, q: Dictionary) -> bool: return String(p["id"]) < String(q["id"]))
	for i in count:
		var di: Dictionary = ids[i % ids.size()]
		var c: Vector2 = di["centre"]
		var an := _h(i, SALT_HELI) * TAU
		var hm := c + Vector2(cos(an), sin(an)) * reach * (0.4 + 0.6 * _h(i, SALT_HELI + 1))
		var gy := maxf(ground_y(hm), 0.0)
		var hp := w(hm, gy + alt + _h(i, SALT_HELI + 2) * 8.0)
		var sc := float(look.get("heli_scale", 1.0))
		var head := w(hm + Vector2(cos(an + 1.3), sin(an + 1.3)), 0.0) - w(hm, 0.0)
		# The body, its tail boom and the rotor's blur.
		box(TOON, hp, head, 2.4 * sc, 1.0 * sc, -0.5 * sc, 0.5 * sc, body)
		var hf := Vector3(head.x, 0.0, head.z).normalized()
		b.box_between(hp - hf * 1.2 * sc, hp - hf * 3.4 * sc, Vector3(-hf.z, 0.0, hf.x), 0.3 * sc, 0.0, 0.3 * sc, TOON, body)
		box(TOON, hp + Vector3(0, 0.7 * sc, 0), head, 4.6 * sc, 0.25 * sc, 0.0, 0.05 * sc, body * 1.4)
		box(TOON, hp + Vector3(0, 0.7 * sc, 0), Vector3(-hf.z, 0.0, hf.x), 4.6 * sc, 0.25 * sc, 0.0, 0.05 * sc, body * 1.4)
		light(hp - hf * 3.4 * sc + Vector3(0, 0.3 * sc, 0), hf, 0.45 * sc, 0.45 * sc, 0.45 * sc, Color(1.0, 0.12, 0.1), _h(i, SALT_HELI + 3))
		light(hp + Vector3(0, -0.6 * sc, 0), hf, 0.7 * sc, 0.4 * sc, 0.25 * sc, Color(1.0, 1.0, 1.0), _h(i, SALT_HELI + 4))
		# The searchlight: a soft cone to a pool on the city, a little ahead.
		var tm := hm + Vector2(cos(an + 2.4), sin(an + 2.4)) * float(look.get("spot_lead_m", 220.0))
		var ty := maxf(ground_y(tm), 0.0) + 0.4
		var tp := w(tm, ty)
		_cone(hp + Vector3(0, -0.6, 0), tp, 0.3, pool_r, beam)
		_pool(tp, pool_r, beam)


func _cone(top: Vector3, bot: Vector3, r0: float, r1: float, col: Color) -> void:
	var ax := (bot - top).normalized()
	var u := ax.cross(Vector3.RIGHT if absf(ax.x) < 0.9 else Vector3.FORWARD).normalized()
	var v := ax.cross(u)
	var n := 16
	var a0 := float(look.get("spot_cone_a", Vector2(0.9, 0.25)).x)
	var a1 := float(look.get("spot_cone_a", Vector2(0.9, 0.25)).y)
	for k in n:
		var t0 := TAU * k / n
		var t1 := TAU * (k + 1) / n
		var p0 := top + (u * cos(t0) + v * sin(t0)) * r0
		var p1 := top + (u * cos(t1) + v * sin(t1)) * r0
		var q0 := bot + (u * cos(t0) + v * sin(t0)) * r1
		var q1 := bot + (u * cos(t1) + v * sin(t1)) * r1
		for e: Array in [[p0, a0], [q0, a1], [q1, a1], [p0, a0], [q1, a1], [p1, a0]]:
			spot.set_color(Color(col.r, col.g, col.b, e[1]))
			spot.add_vertex(e[0])
	_spots += 1


func _pool(c: Vector3, r: float, col: Color) -> void:
	var n := 20
	var a := float(look.get("pool_a", 0.8))
	for k in n:
		var t0 := TAU * k / n
		var t1 := TAU * (k + 1) / n
		for e: Array in [[c, a], [c + Vector3(cos(t0), 0, sin(t0)) * r, 0.0], [c + Vector3(cos(t1), 0, sin(t1)) * r, 0.0]]:
			pool.set_color(Color(col.r, col.g, col.b, e[1]))
			pool.add_vertex(e[0])


# --- Police on the highways ----------------------------------------------------------------------------------------------

func _police(a2: CityPlanA2) -> void:
	var per := int(look.get("cops_per_road", 3))
	var classes: Array = look.get("cop_classes", [&"ring", &"motorway"])
	var seen := {}
	var i := 0
	for r: Dictionary in a2.roads:
		var cls: StringName = r["class"]
		var k: int = seen.get(cls, 0)
		seen[cls] = k + 1
		if not classes.has(cls):
			continue
		var id: StringName = r["id"]
		var lift: float = float(cfg.a2_road_lift_ids[id]) if cfg.a2_road_lift_ids.has(id) else CityA2Features._lift_of(cfg.a2_road_lift, cls, k)
		var pl: PackedVector2Array = r["polyline"]
		if pl.size() < 2:
			continue
		var total := 0.0
		for j in pl.size() - 1:
			total += pl[j].distance_to(pl[j + 1])
		for c in per:
			var at := total * (float(c) + 0.2 + 0.6 * _h(i, SALT_COP)) / per
			var j := 0
			var run := 0.0
			while j < pl.size() - 2 and run + pl[j].distance_to(pl[j + 1]) < at:
				run += pl[j].distance_to(pl[j + 1])
				j += 1
			var seg := pl[j].distance_to(pl[j + 1])
			var m := pl[j].lerp(pl[j + 1], clampf((at - run) / maxf(seg, 0.001), 0.0, 1.0))
			var y := ground_y(m) + lift + 0.25
			var p := w(m, y)
			var dir := w(pl[j + 1], 0.0) - w(pl[j], 0.0)
			var sz: Vector3 = look.get("cop_bar_bu", Vector3(2.2, 0.9, 0.5))
			# Two bars a car apart: the second a half beat later.
			light(p, dir, sz.x, sz.y, sz.z, Color.WHITE, _h(i, SALT_COP + 1))
			light(p + Vector3(dir.x, 0.0, dir.z).normalized() * sz.x * 2.2, dir, sz.x, sz.y, sz.z, Color.WHITE, _h(i, SALT_COP + 1) + 0.5)
			i += 1
