extends Node
## CITY-A2 step 1 probe: the A2 plan and model of a seed (default 1): timing, counts, HQ rects, Site headings, and an
## ASCII map (2 lots per char: ~ water, # building, = street, H plaza, s Site, . ground).
## Run: godot --headless --path . res://tools/city/city_a2_probe.tscn -- [seed] > log 2>&1


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var s := int(args[0]) if args.size() > 0 else 1
	var cfg := CityView3D.CONFIG
	if args.size() > 1 and args[1] == "--build":
		var bare := cfg.duplicate() as CityConfig
		bare.layout_rules_on = false
		for k in 3:
			var b0 := Time.get_ticks_usec()
			var bm := CityModel.build(bare, s + k)
			print("BUILD seed %d no-rules %.0f ms prisms %d" % [s + k, (Time.get_ticks_usec() - b0) / 1000.0, bm.prisms.size()])
		get_tree().quit()
		return
	if args.size() > 1 and args[1] == "--landmarks":
		_landmarks(s)
		get_tree().quit()
		return
	if args.size() > 1 and args[1] == "--terrain":
		_terrain()
		get_tree().quit()
		return
	if args.size() > 1 and args[1] == "--time":
		_time(s)
		get_tree().quit()
		return
	var t0 := Time.get_ticks_usec()
	var p := CityPlan.for_seed(s)
	var t1 := Time.get_ticks_usec()
	var m := CityModel.build(cfg, s)
	var t2 := Time.get_ticks_usec()
	print("A2 seed=%d source=%s fallback=%s failure=%s plan_ms=%.0f model_ms=%.0f" % [s, p.source(), p.fallback, p.failure,
		(t1 - t0) / 1000.0, (t2 - t1) / 1000.0])
	print("A2 prisms=%d buildings=%d streets=%d plazas=%d chunks=%d ruled=%d" % [m.prisms.size(), m.buildings, m.streets.size(),
		m.plazas.size(), m.chunks.size(), m.ruled_parts])
	for t in p.territories:
		print("A2 terr ", t["id"], " at ", t["at"])
	print("A2 aims ", p.site_aim, " mirror ", p.site_mirror, " sea side ", p.coast.get("side"))
	var top := 0.0
	for pr in m.prisms:
		top = maxf(top, float(pr["y0"]) + float(pr["h"]))
	print("A2 tallest top BU ", top)
	if p.a2 == null:
		_why(s)
		get_tree().quit()
		return
	var lots := CityA2Builder.lots_for(p, CityPlan.plan_config(), NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0 / cfg.height_px_bu)
	var R: Rect2i = lots["rect"]
	var kind: PackedByteArray = lots["kind"]
	var chars := {CityA2Builder.K_GROUND: ".", CityA2Builder.K_STREET: "=", CityA2Builder.K_PLAZA: "H", CityA2Builder.K_BUILDING: "#",
		CityA2Builder.K_WATER: "~", CityA2Builder.K_PARK: ",", CityA2Builder.K_BARE: " "}
	for j in range(R.position.y, R.end.y, 2):
		var row := ""
		for i in range(R.position.x, R.end.x, 2):
			var c: String = chars[kind[(j - R.position.y) * R.size.x + (i - R.position.x)]]
			if p.a2_sites.has(Vector2i(i, j)) or p.a2_sites.has(Vector2i(i + 1, j)) or p.a2_sites.has(Vector2i(i, j + 1)):
				c = "s"
			row += c
		print("M ", row)
	get_tree().quit()


## CITY-A2 step 2: our landmark glTFs (assets/city/landmarks) against art-pass ENTRIES.json @ 77cdfde9 (`ENTRIES`, the
## entry anchors: BU from the HQ lot centre, x east, y north, on the south face) and A2's HQ landmarks: each glb's ground
## box (world BU: x east, z south), its south face's distance from the centre against the entry's, and where the seed's
## HQ stands from A2's HQ position (lots).
const ENTRIES := {&"halcyon": Vector3(0.0, -29.0, 0.0), &"meridian": Vector3(0.0, -28.5, 0.0), &"orbital": Vector3(0.0, -13.7, 3.4),
	&"rebel_cell": Vector3(0.0, -6.0, 0.0), &"solace": Vector3(0.0, -12.0, 0.0)}


func _landmarks(s: int) -> void:
	var plan := CityPlan.for_seed(s)
	var m := CityModel.build(CityView3D.CONFIG, s)
	var ids: Array = ENTRIES.keys()
	IdSort.sort_ids(ids)
	for corp: StringName in ids:
		var path := "res://assets/city/landmarks/%s/%s_hq.glb" % [corp, corp]
		if corp == NeonCity.FIST_TERRITORY:
			path = "res://assets/city/landmarks/%s/%s_district.glb" % [corp, corp]
		var box := AABB()
		if ResourceLoader.exists(path):
			var n := (load(path) as PackedScene).instantiate() as Node3D
			box = _box_of(n, Transform3D())
			n.free()
		var e: Vector3 = ENTRIES[corp]
		var a2_hq := Vector2.INF
		for lm: Dictionary in plan.a2.a2.landmarks:
			var want := &"centre" if corp == NeonCity.FIST_TERRITORY else corp
			if lm["kind"] == &"hq" and lm["district"] == want:
				a2_hq = plan.a2.lot_of(lm["pos"])
		var hq: Vector2 = plan.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
		print("LANDMARK %s glb=%s box=%s south_face=%.1f entry_south=%.1f match=%s hq_lot=%s a2_hq_lot=%s off_lots=%.1f ground=%.2f" % [
			corp, ResourceLoader.exists(path), box, box.end.z, -e.y, absf(box.end.z + e.y) <= ENTRY_TOL_BU, hq, a2_hq,
			hq.distance_to(a2_hq) if a2_hq != Vector2.INF else -1.0, m.ground_at(hq)])


## Entries within this many BU of a glb's south face match it.
const ENTRY_TOL_BU := 2.0


static func _box_of(n: Node, xf: Transform3D) -> AABB:
	var out := AABB()
	var first := true
	var t := xf * ((n as Node3D).transform if n is Node3D else Transform3D())
	if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
		out = t * (n as MeshInstance3D).mesh.get_aabb()
		first = false
	for c in n.get_children():
		var b := _box_of(c, t)
		if b.size != Vector3.ZERO:
			out = b if first else out.merge(b)
			first = false
	return out


## CITY-A2 step 2: the terrain's build time, its highest ground in the city and past it, and an ASCII height map of the
## coarse grid (~ water, then " .:-=+*#%@" by `TERRAIN_CHAR_BU` BU bands).
const TERRAIN_CHAR_BU := 6.0


func _terrain() -> void:
	var cfg := CityPlan.plan_config()
	var cc := CityView3D.CONFIG
	var t0 := Time.get_ticks_usec()
	var ras := CityA2Builder.raster(cfg, cc.city_rect, NeonCity.BORDER_BLEND)
	var t1 := Time.get_ticks_usec()
	var t := CityA2Builder.terrain(cfg, cc.city_rect, NeonCity.BORDER_BLEND, cc.lot_bu)
	var t2 := Time.get_ticks_usec()
	print("TERRAIN raster_ms=%.0f terrain_ms=%.0f fine=%s coarse=%s step=%d" % [(t1 - t0) / 1000.0, (t2 - t1) / 1000.0, t.fine_rect,
		t.coarse_rect, t.step])
	var hi := -INF
	var at := Vector2i.ZERO
	for j in range(cc.city_rect.position.y, cc.city_rect.end.y):
		for i in range(cc.city_rect.position.x, cc.city_rect.end.x):
			if t.lot_height(i, j) > hi:
				hi = t.lot_height(i, j)
				at = Vector2i(i, j)
	var hal := ras.lot_of(Vector2(700, 5900))
	var mx := -INF
	for k in t.coarse.size():
		mx = maxf(mx, t.coarse[k])
	print("TERRAIN city_max=%.2f at %s halcyon_hill=%.2f beyond_max=%.2f" % [hi, at, t.height_at(hal.x, hal.y), mx])
	# Seams: the largest step between the two grids just inside / outside the fine rect's edge.
	var fr := t.fine_rect
	var seam := 0.0
	for i in range(fr.position.x, fr.end.x + 1):
		for y: int in [fr.position.y, fr.end.y]:
			var o := 1 if y == fr.end.y else -1
			seam = maxf(seam, absf(t.height_at(i, y) - t.height_at(i, y + o * 0.01)))
	for j in range(fr.position.y, fr.end.y + 1):
		for x: int in [fr.position.x, fr.end.x]:
			var o := 1 if x == fr.end.x else -1
			seam = maxf(seam, absf(t.height_at(x, j) - t.height_at(x + o * 0.01, j)))
	var ring: PackedVector2Array = ras.a2.road(cfg.city_a2_outer_ring)["polyline"]
	var rb := Rect2(ras.lot_of(ring[0]), Vector2.ZERO)
	for q in ring:
		rb = rb.expand(ras.lot_of(q))
	var ob := Rect2(ras.lot_of(ras.a2.ocean[0]), Vector2.ZERO)
	for q in ras.a2.ocean:
		ob = ob.expand(ras.lot_of(q))
	print("TERRAIN city_rect=%s ring_lots=%s ocean_lots=%s fine_edge_seam=%.3f mpl=%.2f" % [cc.city_rect, rb, ob, seam, ras.metres_per_lot])
	var w := t.coarse_rect.size.x / t.step + 1
	for j in range(0, t.coarse.size() / w, 3):
		var line := ""
		for i in range(0, w, 2):
			var k := j * w + i
			line += "~" if t.coarse_water[k] != 0 else " .:-=+*#%@"[clampi(int(t.coarse[k] / TERRAIN_CHAR_BU), 0, 9)]
		print("T ", line)


## Plan and subdivision times (ms) of `n` seeds from `s`: max and mean of each.
func _time(n: int) -> void:
	var gcfg := CityPlan.plan_config()
	var frame := CityPlan.site_frame()
	CityA2Builder.raster(gcfg, CityView3D.CONFIG.city_rect, NeonCity.BORDER_BLEND)
	var ids: Array = [&"halcyon", &"meridian", &"orbital", &"rebel_cell", &"solace"]
	var tp := PackedFloat64Array()
	var ts := PackedFloat64Array()
	for k in n:
		var t0 := Time.get_ticks_usec()
		var p := CityA2Builder.make_plan(k * 104729 - 3000017, gcfg, CityView3D.CONFIG.city_rect, ids, NeonCity.FIST_TERRITORY,
			NeonCity.HQ_LOTS, frame, NeonCity.BORDER_BLEND, CityView3D.CONFIG.lot_bu)
		var t1 := Time.get_ticks_usec()
		CityA2Builder._subdivide(p, gcfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
		var t2 := Time.get_ticks_usec()
		tp.append((t1 - t0) / 1000.0)
		ts.append((t2 - t1) / 1000.0)
	tp.sort()
	ts.sort()
	print("TIME plan median %.0f max %.0f | lots median %.0f max %.0f ms" % [tp[n / 2], tp[n - 1], ts[n / 2], ts[n - 1]])


## Why a fallen-back seed found no Site heading: per corporation, the fewest blocked Site lots by reason over every
## heading (edge, coast, road, park, HQ).
func _why(s: int) -> void:
	var gcfg := CityPlan.plan_config()
	var ras := CityA2Builder.raster(gcfg, CityView3D.CONFIG.city_rect, NeonCity.BORDER_BLEND)
	var frame := CityPlan.site_frame()
	var ids: Array = [&"halcyon", &"meridian", &"orbital", &"solace", &"rebel_cell"]
	for id: StringName in ids:
		var d := CityA2Builder._district_of(ras, gcfg, id)
		var m: Vector2 = ras.a2.old_city_centre if id == &"rebel_cell" else d["hq"]
		var c := ras.lot_of(m)
		if not frame["uvs"].has(id):
			continue
		var best := [999, 999, 999, 999, 999, 999]
		for mir in [false, true]:
			for k in 24:
				var why := [0, 0, 0, 0, 0, 0]
				var tot := 0
				for q: Vector2 in CityA2Builder.site_points_at(c, k * 15.0, mir, frame, frame["uvs"][id]):
					var l := Vector2i(q.floor())
					if not CityView3D.CONFIG.city_rect.grow(-gcfg.city_gen_edge_lots).has_point(l):
						why[0] += 1
					if ras.depth_at(q.x, q.y) < gcfg.city_gen_coast_clear:
						why[1] += 1
					if ras.road_rank(l.x, l.y) > 0:
						why[2] += 1
					if ras.is_park(l.x, l.y):
						why[3] += 1
					if ras.territory(l.x, l.y) != id:
						why[4] += 1
					tot += 1
				why[5] = tot
				if why[0] + why[1] + why[2] + why[3] < best[0] + best[1] + best[2] + best[3]:
					best = why
		print("WHY %s edge/coast/road/park/notown/total %s" % [id, best])
