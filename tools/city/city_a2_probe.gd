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
		CityA2Builder.K_WATER: "~", CityA2Builder.K_PARK: ","}
	for j in range(R.position.y, R.end.y, 2):
		var row := ""
		for i in range(R.position.x, R.end.x, 2):
			var c: String = chars[kind[(j - R.position.y) * R.size.x + (i - R.position.x)]]
			if p.a2_sites.has(Vector2i(i, j)) or p.a2_sites.has(Vector2i(i + 1, j)) or p.a2_sites.has(Vector2i(i, j + 1)):
				c = "s"
			row += c
		print("M ", row)
	get_tree().quit()


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
				for q: Vector2 in CityGenerator.site_points_at(c, k * 15.0, mir, frame, frame["uvs"][id]):
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
