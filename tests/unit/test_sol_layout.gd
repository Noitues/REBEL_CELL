extends GutTest
## Solace district layout (A-069 / A-070), fast tier: L1 blocks of 2-3 lots, lower, never under 3 storeys; L2 one park (no
## interior street, an organic outline, paths and lanes that run out to the city streets, ponds on open lawn); L3 the 70 BU
## plinth circle holds no block and its cardinal stairs land on park paths; every other territory's lots are exactly what
## the A2 pass made (layout off == on outside Solace); the park section is deterministic. The seed sweep: test_sol_layout_sweep.gd.

const SEEDS: Array[int] = [1, 2, 7]
const TERR := &"solace"

var _on: CampaignConfigData
var _off: CampaignConfigData
var _cache: Dictionary = {}


func before_all() -> void:
	_on = load(CityPlan.FIXED_CONFIG_PATH)
	_off = _on.duplicate()
	_off.city_sol_layout = false


func _lots(s: int, cfg: CampaignConfigData) -> Dictionary:
	var key := "%d|%s" % [s, cfg.city_sol_layout]
	if not _cache.has(key):
		var plan := CityPlan.for_seed(s)
		_cache[key] = CityA2Builder._subdivide(plan, cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	return _cache[key]


func _kind(lots: Dictionary, l: Vector2i) -> int:
	var R: Rect2i = lots["rect"]
	return int((lots["kind"] as PackedByteArray)[(l.y - R.position.y) * R.size.x + (l.x - R.position.x)])


func _top_bu(c: Dictionary) -> float:
	var t := 0.0
	for e: Dictionary in c["extrusions"]:
		t = maxf(t, float(e["z0"]) + float(e["h"]))
	return t  # px_per_bu 1.0: height px == BU


func _sol_cells(plan: CityPlan, lots: Dictionary) -> Array:
	var out: Array = []
	for c: Dictionary in lots["cells"]:
		var cell: Rect2i = c["cell"]
		if plan.a2.territory(cell.end.x - 1, cell.end.y - 1) == TERR:
			out.append(c)
	return out


func test_other_territories_are_untouched() -> void:
	for s in SEEDS:
		var plan := CityPlan.for_seed(s)
		var a := _lots(s, _on)
		var b := _lots(s, _off)
		var R: Rect2i = a["rect"]
		for j in range(R.position.y, R.end.y):
			for i in range(R.position.x, R.end.x):
				if plan.a2.territory(i, j) != TERR:
					assert_eq(_kind(a, Vector2i(i, j)), _kind(b, Vector2i(i, j)), "seed %d kind at %d,%d" % [s, i, j])
		var by_cell := {}
		for c: Dictionary in b["cells"]:
			by_cell[c["cell"]] = c
		var n := 0
		for c: Dictionary in a["cells"]:
			var cell: Rect2i = c["cell"]
			if plan.a2.territory(cell.end.x - 1, cell.end.y - 1) == TERR:
				continue
			n += 1
			assert_true(by_cell.has(cell), "seed %d: the cell %s is in the A2 layout" % [s, cell])
			assert_eq(var_to_str(c["extrusions"]), var_to_str(by_cell[cell]["extrusions"]), "seed %d cell %s identical" % [s, cell])
		var m := 0
		for c: Dictionary in b["cells"]:
			var cell2: Rect2i = c["cell"]
			if plan.a2.territory(cell2.end.x - 1, cell2.end.y - 1) != TERR:
				m += 1
		assert_eq(n, m, "seed %d: no other cell lost" % s)
		var sa: Dictionary = a["streets"]
		var sb: Dictionary = b["streets"]
		for k: int in sb:
			var l := Vector2i(R.position.x + k % R.size.x, R.position.y + k / R.size.x)
			if plan.a2.territory(l.x, l.y) != TERR:
				assert_eq(var_to_str(sa.get(k)), var_to_str(sb[k]), "seed %d street %s identical" % [s, l])
		assert_eq(var_to_str(a["plazas"]), var_to_str(b["plazas"]), "the HQ plazas are identical")


func test_blocks_are_two_to_three_lots_and_low() -> void:
	var fl := NetrunArtUnits.floor_bu()
	for s in SEEDS:
		var plan := CityPlan.for_seed(s)
		var a := _lots(s, _on)
		var b := _lots(s, _off)
		var cells := _sol_cells(plan, a)
		assert_gt(cells.size(), 10, "seed %d has Solace blocks" % s)
		var bl := _on.city_sol_block_lots
		var sum_on := 0.0
		for c: Dictionary in cells:
			var cell: Rect2i = c["cell"]
			if plan.a2_sites.has(cell.position):
				assert_eq(cell.size, Vector2i.ONE, "a Site lot keeps its one-lot building")
			else:
				assert_true(cell.size.x >= bl.x and cell.size.x <= bl.y and cell.size.y >= bl.x and cell.size.y <= bl.y,
					"seed %d block %s is %d..%d lots a side" % [s, cell, bl.x, bl.y])
			assert_gte(_top_bu(c), float(_on.city_sol_min_floors) * fl - 0.001, "seed %d: %s stands at least %d storeys" % [s, cell, _on.city_sol_min_floors])
			sum_on += _top_bu(c)
		var sum_off := 0.0
		var cells_off := _sol_cells(plan, b)
		for c: Dictionary in cells_off:
			sum_off += _top_bu(c)
		assert_lt(sum_on / cells.size(), 0.62 * sum_off / cells_off.size(), "seed %d: about half the A2 Solace height" % s)
		# two blocks never touch (a lawn gap), Site cells included
		for x in cells.size():
			for y in range(x + 1, cells.size()):
				var p: Rect2i = cells[x]["cell"]
				var q: Rect2i = cells[y]["cell"]
				assert_false(p.grow(_on.city_sol_gap_lots - 1).intersects(q), "seed %d: %s and %s are a lot apart" % [s, p, q])


func test_one_park_no_interior_street() -> void:
	for s in SEEDS:
		var plan := CityPlan.for_seed(s)
		var a := _lots(s, _on)
		var R: Rect2i = a["rect"]
		var streets := 0
		var park := 0
		for j in range(R.position.y, R.end.y):
			for i in range(R.position.x, R.end.x):
				if plan.a2.territory(i, j) != TERR:
					continue
				var k := _kind(a, Vector2i(i, j))
				if k == CityA2Builder.K_PARK:
					park += 1
				if k == CityA2Builder.K_STREET and plan.a2.road_rank(i, j) == 0:
					var edge := false
					for d: Vector2i in CityA2Builder.DIRS:
						if plan.a2.territory(i + d.x, j + d.y) != TERR:
							edge = true
					assert_true(edge, "seed %d: street %d,%d is on the district's edge" % [s, i, j])
					streets += 1
		assert_gt(park, 100, "seed %d: a park" % s)
		assert_gt(streets, 0, "seed %d: the edge streets stay" % s)


func test_park_data() -> void:
	for s in SEEDS:
		var plan := CityPlan.for_seed(s)
		var a := _lots(s, _on)
		var park: Dictionary = a["solace"]
		assert_false(park.is_empty(), "seed %d: a park" % s)
		var outline: Array = park["outline"]
		assert_gt(outline.size(), 0)
		assert_false(bool(outline[0]["hole"]), "the largest loop is the outer boundary")
		# the outline stays off other territories' buildings
		for lp: Dictionary in outline:
			for p: Vector2 in lp["points"]:
				var l := Vector2i(p.floor())
				if (a["rect"] as Rect2i).has_point(l) and plan.a2.territory(l.x, l.y) != TERR:
					assert_ne(_kind(a, l), CityA2Builder.K_BUILDING, "seed %d: the outline reaches no other territory's building (%s)" % [s, l])
		var paths: Array = park["paths"]
		var lanes := 0
		for p: Dictionary in paths:
			if p["kind"] == "lane":
				lanes += 1
			var pts: PackedVector2Array = p["points"]
			assert_gte(pts.size(), 2)
			for q in pts:
				var l2 := Vector2i(q.floor())
				var kd := _kind(a, l2)
				assert_true(kd == CityA2Builder.K_PARK or kd == CityA2Builder.K_STREET, "seed %d: %s runs on lawn and streets (%s kind %d)" % [s, p["id"], l2, kd])
			if p["kind"] != "stair":
				# both ends are on a city street
				assert_eq(_kind(a, Vector2i(pts[0].floor())), CityA2Builder.K_STREET, "%s starts on a street" % p["id"])
		assert_gt(lanes, 0, "seed %d: service lanes" % s)
		for po: Dictionary in park["ponds"]:
			for q: Vector2 in po["points"]:
				assert_eq(_kind(a, Vector2i(q.floor())), CityA2Builder.K_PARK, "seed %d: a pond is on lawn" % s)


func test_sites_clear_the_plinth_and_stairs() -> void:
	for s in SEEDS:
		var plan := CityPlan.for_seed(s)
		assert_eq(SolSiteCheck.problems(plan, _lots(s, _on), "seed %d" % s), PackedStringArray())


func test_shift_sites_moves_the_least() -> void:
	var c := Vector2(10, 10)
	var r := 5.0
	# stands 0.5 lot south of the circle: moves south by whole lots until the gap is 1 lot
	var out := CitySolaceDistrict.shift_sites(PackedVector2Array([Vector2(11.3, 15.5), Vector2(11.3, 30.5), Vector2(11.3, 15.6)]), c, r)
	assert_eq(out[0], Vector2(11.3, 16.5), "one lot further")
	assert_eq(out[1], Vector2(11.3, 30.5), "a far Site stays")
	assert_eq(out[2], Vector2(11.3, 17.6), "never onto a lot an earlier Site holds")
	assert_eq(CitySolaceDistrict.shift_sites(PackedVector2Array([Vector2(11.3, 15.5)]), c, 0.0)[0], Vector2(11.3, 15.5), "off = unchanged")


func test_plinth_circle_is_clear_and_stairs_land_on_paths() -> void:
	var lot_bu := CityView3D.CONFIG.lot_bu
	for s in SEEDS:
		var plan := CityPlan.for_seed(s)
		var a := _lots(s, _on)
		var hq: Rect2i = plan.hq_rects(NeonCity.HQ_LOTS)[TERR]
		var centre := Vector2(hq.position) + Vector2(hq.size) * 0.5
		var pl: Dictionary = (a["solace"] as Dictionary)["plinth"]
		assert_almost_eq(float(pl["radius_bu"]), _on.city_sol_plinth_r_bu, 0.001)
		var r_l := float(pl["radius_bu"]) / lot_bu
		# the circle fits the HQ rect grown by the NA-11c zone (2 lots)
		assert_lte(r_l, float(hq.size.x) * 0.5 + 2.0, "the plinth fits the HQ zone")
		for c: Dictionary in _sol_cells(plan, a):
			var cell: Rect2i = c["cell"]
			if plan.a2_sites.has(cell.position):
				pass  # Solace's own Sites: test_sites_clear_the_plinth_and_stairs
			else:
				assert_true(not CitySolaceDistrict._in_circle_rect(cell, centre, r_l), "seed %d: block %s clears the plinth" % [s, cell])
		var stairs: Array = pl["stairs"]
		assert_eq(stairs.size(), 4)
		var ids := {}
		for p: Dictionary in a["solace"]["paths"]:
			ids[p["id"]] = p
		var linked := 0
		for st: Dictionary in stairs:
			assert_almost_eq((st["landing"] as Vector2).distance_to(centre), r_l, 0.001, "the landing is on the circle")
			if st["path"] != "":
				linked += 1
				var pts: PackedVector2Array = (ids[st["path"]] as Dictionary)["points"]
				assert_eq(pts[0], st["landing"], "the stair path starts at its landing")
		assert_eq(linked, 4, "seed %d: all four stairs land on a path" % s)


func test_section_is_deterministic_and_plan_bu() -> void:
	var plan := CityPlan.for_seed(1)
	var a := plan.solace_park_section(6.0, CityView3D.CONFIG.district_centre)
	CityPlan.forget_all()
	var b := CityPlan.for_seed(1).solace_park_section(6.0, CityView3D.CONFIG.district_centre)
	assert_eq(JSON.stringify(a), JSON.stringify(b), "same seed, same section")
	for k in ["outline", "paths", "ponds", "lots", "plinth"]:
		assert_true(a.has(k), k)
	assert_eq(float(a["plinth"]["radius"]), _on.city_sol_plinth_r_bu)
	assert_eq(plan.city_sections(6.0, CityView3D.CONFIG.district_centre).has("solace_park"), true)


func test_layout_off_leaves_the_a2_grid() -> void:
	var plan := CityPlan.for_seed(1)
	var b := _lots(1, _off)
	assert_false(b.has("solace"), "layout off: no park")
	var street := 0
	for c: Dictionary in _sol_cells(plan, b):
		street += 1
	assert_gt(street, 0)
