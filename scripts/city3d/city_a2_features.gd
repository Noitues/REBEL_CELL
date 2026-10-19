class_name CityA2Features
extends Node3D
## CITY-A2 step 2: the planner city's features over the 3D city's ground, as plain meshes in the ground material (vertex
## colour) and glow lines in the lane material (vertex colour = emission): A2's roads by class (decks lifted by class,
## with side faces when high: the ring, motorways and truck roads read as raised roads; interchange ramps), the rails by
## kind and their stations, the corporate walls (open at the gates) with a checkpoint on each gate, the port's terminal
## and piers, the drowned quarter's water sheet, and the undercity entrances. Tunnel stretches of roads and rails, and
## the undercity tunnels, lie below grade: not drawn. Every vertex stands on the terrain (CityPlan.terrain).
## `build` is pure (plan and config in, meshes out, no randomness); numbers: CityConfig's "A2 features" group.

## A built feature set: name -> {"mesh": ArrayMesh or null, "lane": bool (lane material), "quads": int}; "hidden": road
## and rail segments under ground (tunnels); "gates": wall segments left open.
var parts: Dictionary = {}
var hidden: int = 0
var gates: int = 0

const ORDER: Array[String] = ["roads", "road_glow", "ramps", "rails", "rail_glow", "stations", "walls", "checkpoints",
	"port", "piers", "entrances", "drowned"]


## The feature node of `plan` (its A2 raster and terrain) for config `cfg`: `ground_mat` for the solid parts, `lane_mat`
## for the glow lines, `water_mat` for the drowned quarter's sheet.
static func make(cfg: CityConfig, plan: CityPlan, ground_mat: Material, lane_mat: Material, water_mat: Material) -> CityA2Features:
	var f := CityA2Features.new()
	f.name = "A2Features"
	var b := build(cfg, plan)
	f.parts = b["parts"]
	f.hidden = b["hidden"]
	f.gates = b["gates"]
	for k: String in ORDER:
		var p: Dictionary = f.parts[k]
		if p["mesh"] == null:
			continue
		var mi := MeshInstance3D.new()
		mi.name = k.capitalize().replace(" ", "")
		mi.mesh = p["mesh"]
		mi.material_override = water_mat if k == "drowned" else (lane_mat if p["lane"] else ground_mat)
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		f.add_child(mi)
	return f


## The feature meshes of `plan`: {"parts": name -> {"mesh", "lane", "quads"}, "hidden": int, "gates": int}. Empty parts
## (no A2) when the plan has no raster.
static func build(cfg: CityConfig, plan: CityPlan) -> Dictionary:
	var acc := {}
	for k: String in ORDER:
		acc[k] = _Acc.new(k in ["road_glow", "rail_glow"])
	var out := {"parts": {}, "hidden": 0, "gates": 0}
	if plan.a2 != null and plan.terrain != null:
		var ctx := _Ctx.new(cfg, plan)
		_roads(ctx, acc)
		_rails(ctx, acc)
		_walls(ctx, acc)
		_port(ctx, acc)
		_undercity(ctx, acc)
		out["hidden"] = ctx.hidden
		out["gates"] = ctx.gates
	for k: String in ORDER:
		var a: _Acc = acc[k]
		out["parts"][k] = {"mesh": a.commit(), "lane": a.lane, "quads": a.quads}
	return out


class _Ctx:
	var cfg: CityConfig
	var ras: CityA2Raster
	var terrain: CityA2Terrain
	var a2: CityPlanA2
	var hidden: int = 0
	var gates: int = 0

	func _init(p_cfg: CityConfig, plan: CityPlan) -> void:
		cfg = p_cfg
		ras = plan.a2
		terrain = plan.terrain
		a2 = plan.a2.a2

	## The world point of A2 point `m` (metres) `lift` BU over the ground.
	func at(m: Vector2, lift: float) -> Vector3:
		var l := ras.lot_of(m)
		return CityIsoCamera.lot_to_world(cfg, l, terrain.height_at(l.x, l.y) + lift)

	## The world point of A2 point `m` on the ground.
	func ground(m: Vector2) -> Vector3:
		return at(m, 0.0)

	## Metres to BU.
	func bu(metres: float) -> float:
		return metres / ras.metres_per_lot * cfg.lot_bu

	## BU to metres.
	func metres(bu_v: float) -> float:
		return bu_v / cfg.lot_bu * ras.metres_per_lot


class _Acc:
	var st := SurfaceTool.new()
	var lane: bool = false
	var quads: int = 0

	func _init(p_lane: bool) -> void:
		lane = p_lane
		st.begin(Mesh.PRIMITIVE_TRIANGLES)

	func quad(a: Vector3, b: Vector3, c: Vector3, d: Vector3, col: Color) -> void:
		for p: Vector3 in [a, b, c, a, c, d]:
			st.set_color(col)
			st.set_normal(Vector3.UP)
			st.add_vertex(p)
		quads += 1

	func tri(a: Vector3, b: Vector3, c: Vector3, col: Color) -> void:
		for p: Vector3 in [a, b, c]:
			st.set_color(col)
			st.set_normal(Vector3.UP)
			st.add_vertex(p)
		quads += 1

	func commit() -> ArrayMesh:
		if quads == 0:
			return null
		if not lane:
			st.generate_normals()
		return st.commit()


## True when segment a-b (metres) runs inside one of `tunnels` (its midpoint within `tol` metres of a tunnel polyline).
static func _in_tunnel(a: Vector2, b: Vector2, tunnels: Array[PackedVector2Array], tol: float) -> bool:
	var mid := (a + b) * 0.5
	for t in tunnels:
		for k in t.size() - 1:
			if Geometry2D.get_closest_point_to_segment(mid, t[k], t[k + 1]).distance_to(mid) <= tol:
				return true
	return false


## A deck along polyline `pl` (metres): `half` BU each side, `lift` BU over the ground, colour `col`; side faces down to the
## ground when `lift` reaches `cfg.a2_deck_skirt_from`; a glow line (`glow_half` BU, colour `glow`) into `glow_acc`
## (skipped when null). Segments in `tunnels` are not drawn (counted in ctx.hidden).
static func _deck(ctx: _Ctx, acc: _Acc, glow_acc: _Acc, pl: PackedVector2Array, half: float, lift: float, col: Color,
		glow: Color, glow_half: float, tunnels: Array[PackedVector2Array]) -> void:
	var hm := ctx.metres(half)
	var gm := ctx.metres(glow_half)
	var skirt := lift >= ctx.cfg.a2_deck_skirt_from
	for k in pl.size() - 1:
		var a := pl[k]
		var b := pl[k + 1]
		if a.is_equal_approx(b):
			continue
		if not tunnels.is_empty() and _in_tunnel(a, b, tunnels, ctx.cfg.a2_tunnel_tol_m):
			ctx.hidden += 1
			continue
		var d := (b - a).normalized()
		var n := Vector2(-d.y, d.x)
		var ea := a - d * hm * 0.5
		var eb := b + d * hm * 0.5  # overlap the joints a little (no gaps at bends)
		acc.quad(ctx.at(ea + n * hm, lift), ctx.at(eb + n * hm, lift), ctx.at(eb - n * hm, lift), ctx.at(ea - n * hm, lift), col)
		if skirt:
			for s: float in [1.0, -1.0]:
				acc.quad(ctx.at(ea + n * hm * s, lift), ctx.at(eb + n * hm * s, lift), ctx.ground(eb + n * hm * s), ctx.ground(ea + n * hm * s), col)
		if glow_acc != null:
			var gl := lift + ctx.cfg.lane_stroke_bu
			glow_acc.quad(ctx.at(a + n * gm, gl), ctx.at(b + n * gm, gl), ctx.at(b - n * gm, gl), ctx.at(a - n * gm, gl), glow)


## A box centred on A2 point `m` (metres) on the ground: `size` (x along `dir`, y across, z high; BU).
static func _box(ctx: _Ctx, acc: _Acc, m: Vector2, dir: Vector2, size: Vector3, lift: float, col: Color) -> void:
	var d := dir.normalized() if dir.length() > 0.0 else Vector2.RIGHT
	var n := Vector2(-d.y, d.x)
	var hx := ctx.metres(size.x * 0.5)
	var hy := ctx.metres(size.y * 0.5)
	var c: Array[Vector2] = [m - d * hx - n * hy, m + d * hx - n * hy, m + d * hx + n * hy, m - d * hx + n * hy]
	var base := INF
	for q in c:
		base = minf(base, ctx.ground(q).y)
	var top := base + lift + size.z
	var tops: Array[Vector3] = []
	var bots: Array[Vector3] = []
	for q in c:
		var w := ctx.ground(q)
		tops.append(Vector3(w.x, top, w.z))
		bots.append(Vector3(w.x, base, w.z))
	acc.quad(tops[0], tops[1], tops[2], tops[3], col)
	for k in 4:
		var k2 := (k + 1) % 4
		acc.quad(tops[k], tops[k2], bots[k2], bots[k], col)


static func _roads(ctx: _Ctx, acc: Dictionary) -> void:
	var cfg := ctx.cfg
	for r: Dictionary in ctx.a2.roads:
		var cls: StringName = r["class"]
		var half := maxf(ctx.bu(float(r["width"])) * 0.5, cfg.a2_road_min_half_bu)
		var glow: Color = cfg.a2_road_glow.get(cls, cfg.street)
		_deck(ctx, acc["roads"], acc["road_glow"], r["polyline"], half, float(cfg.a2_road_lift.get(cls, 0.0)), cfg.street, glow,
			half * cfg.a2_road_glow_share, r["tunnels"])
	var ramp_lift := float(cfg.a2_road_lift.get(&"truck", 0.0))
	for ix: Dictionary in ctx.a2.interchanges:
		for pl: PackedVector2Array in ix["ramps"]:
			_deck(ctx, acc["ramps"], null, pl, cfg.a2_road_min_half_bu, ramp_lift, cfg.street, Color.BLACK, 0.0, [] as Array[PackedVector2Array])


static func _rails(ctx: _Ctx, acc: Dictionary) -> void:
	var cfg := ctx.cfg
	for r: Dictionary in ctx.a2.rails:
		var kind: StringName = r["kind"]
		var half := maxf(ctx.bu(float(r["gauge"])) * 0.5, cfg.a2_rail_min_half_bu)
		var glow: Color = cfg.a2_rail_glow.get(kind, cfg.a2_rail_color)
		_deck(ctx, acc["rails"], acc["rail_glow"], r["polyline"], half, float(cfg.a2_rail_lift.get(kind, 0.0)), cfg.a2_rail_color, glow,
			half * cfg.a2_road_glow_share, r["tunnels"])
	for s: Dictionary in ctx.a2.stations:
		var box: Vector3 = cfg.a2_station_box.get(s["kind"], cfg.a2_station_box[&"rail"])
		_box(ctx, acc["stations"], s["position"], Vector2.RIGHT, box, 0.0, cfg.plaza)


static func _walls(ctx: _Ctx, acc: Dictionary) -> void:
	var cfg := ctx.cfg
	var ids: Array = ctx.a2.walls.keys()
	IdSort.sort_ids(ids)
	for id: StringName in ids:
		var w: Dictionary = ctx.a2.walls[id]
		var pl: PackedVector2Array = w["wall"]
		var gate_pts: PackedVector2Array = w["gates"]
		for k in pl.size():
			var a := pl[k]
			var b := pl[(k + 1) % pl.size()]
			var mid := (a + b) * 0.5
			var open := false
			for g in gate_pts:
				if g.distance_to(mid) <= cfg.a2_gate_gap_m:
					open = true
					break
			if open:
				ctx.gates += 1
				continue
			_deck(ctx, acc["walls"], null, PackedVector2Array([a, b]), cfg.a2_wall_half_bu, cfg.a2_wall_h_bu, cfg.a2_wall_color,
				Color.BLACK, 0.0, [] as Array[PackedVector2Array])
	for c: Dictionary in ctx.a2.checkpoints:
		var col := cfg.plaza.lerp(Palette.corp_color(c["district"]), cfg.territory_tint)
		_box(ctx, acc["checkpoints"], c["position"], Vector2.RIGHT, cfg.a2_checkpoint_box, 0.0, col)


static func _port(ctx: _Ctx, acc: Dictionary) -> void:
	var cfg := ctx.cfg
	if not ctx.a2.port.is_empty():
		_fill(ctx, acc["port"], ctx.a2.port["terminal"], cfg.a2_port_lift_bu, cfg.plaza)
		for p: Dictionary in ctx.a2.port["piers"]:
			var br := deg_to_rad(float(p["bearing_deg"]))
			var d := Vector2(sin(br), cos(br))  # compass bearing: clockwise from north
			var base: Vector2 = p["base"]
			var mid := base + d * float(p["length"]) * 0.5
			_box(ctx, acc["piers"], mid, d, Vector3(ctx.bu(float(p["length"])), ctx.bu(float(p["width"])), cfg.a2_pier_lift_bu), 0.0, cfg.plaza)
	if not ctx.a2.drowned.is_empty():
		_fill(ctx, acc["drowned"], ctx.a2.drowned, cfg.a2_drowned_lift_bu, Color.BLACK)


static func _undercity(ctx: _Ctx, acc: Dictionary) -> void:
	for e: Vector2 in ctx.a2.undercity_entrances:
		_box(ctx, acc["entrances"], e, Vector2.RIGHT, ctx.cfg.a2_entrance_box, 0.0, ctx.cfg.a2_rail_color)
	ctx.hidden += ctx.a2.undercity_tunnels.size()


## Polygon `poly` (metres) filled `lift` BU over the ground (triangulated).
static func _fill(ctx: _Ctx, acc: _Acc, poly: PackedVector2Array, lift: float, col: Color) -> void:
	var tri := Geometry2D.triangulate_polygon(poly)
	for k in range(0, tri.size(), 3):
		acc.tri(ctx.at(poly[tri[k]], lift), ctx.at(poly[tri[k + 1]], lift), ctx.at(poly[tri[k + 2]], lift), col)
