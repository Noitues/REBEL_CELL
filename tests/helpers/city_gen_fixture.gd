class_name CityGenFixture
extends RefCounted
## Plan 2 NA-12: the city generator's checks shared by test_city_generator (fast) and
## test_city_generator_sweep (full): seeds, the corporations, plan-level and full-city problems.

const CITY_CONFIG := preload("res://content/config/city_config.tres")
## A Site's street lies within this many lots of it.
const STREET_REACH := 4.0

static func seed_of(k: int) -> int:
	return k * 104729 - 3000017


static func corps() -> Array[CorporationData]:
	var out: Array[CorporationData] = []
	var ids: Array = ContentRegistry.all_ids()
	IdSort.sort_ids(ids)
	for cid: StringName in ids:
		var c := ContentRegistry.get_content(cid) as CorporationData
		if c != null and c.city_grid != null:
			out.append(c)
	return out


## Problems of `plan` at plan level (empty = fine): HQ rects overlapping, outside the city or
## on the water; Sites off the city, in the water or on another corporation's HQ rect.
static func plan_problems(plan: CityPlan, corp_list: Array[CorporationData]) -> PackedStringArray:
	var out := PackedStringArray()
	var city := CITY_CONFIG.city_rect as Rect2i
	var rects := plan.hq_rects(NeonCity.HQ_LOTS)
	var ids: Array = rects.keys()
	IdSort.sort_ids(ids)
	for a in ids.size():
		var ra: Rect2i = rects[ids[a]]
		if not city.encloses(ra):
			out.append("%s HQ off the city" % ids[a])
		for di in ra.size.x:
			for dj in ra.size.y:
				if plan.is_water(ra.position.x + di, ra.position.y + dj):
					out.append("%s HQ on the water" % ids[a])
		for b in range(a + 1, ids.size()):
			if ra.intersects(rects[ids[b]]):
				out.append("%s HQ overlaps %s" % [ids[a], ids[b]])
	for corp in corp_list:
		var pts := CityLayout.site_points_in(corp, plan)
		var sids: Array = pts.keys()
		IdSort.sort_ids(sids)
		for sid: StringName in sids:
			var p: Vector2 = pts[sid]
			var lot := Vector2i(p.floor())
			if not city.has_point(lot):
				out.append("%s %s off the city" % [corp.id, sid])
			if plan.is_water(lot.x, lot.y) or plan.land_depth(p.x, p.y) < 1.0:
				out.append("%s %s in the water" % [corp.id, sid])
			for other: StringName in ids:
				if other != corp.id and other != NeonCity.FIST_TERRITORY and (rects[other] as Rect2i).has_point(lot):
					out.append("%s %s on %s's HQ" % [corp.id, sid, other])
	return out


## Problems of a full city of `p_seed` (empty = fine): `hq_overlaps`, a Site without a building
## (`site_bid`), a Grid link without a street route between its ends.
static func full_city_problems(m: CityModel, corp_list: Array[CorporationData]) -> PackedStringArray:
	var out := PackedStringArray()
	var cfg: CityConfig = CITY_CONFIG
	var p_seed := m.city_seed
	var city := NetrunArtExport.city_json(m.city_seed, cfg.lot_bu, cfg.district_centre, m.prisms, m.streets, m.plazas, m.hqs)
	for o: Dictionary in city["hq_overlaps"]:
		out.append("hq overlap %s" % str(o))
	var index := NetrunArtExport.lot_index(city["buildings"])
	var plan := CityPlan.for_seed(p_seed)
	for corp in corp_list:
		var pts := CityLayout.site_points_in(corp, plan)
		var sids: Array = pts.keys()
		IdSort.sort_ids(sids)
		for sid: StringName in sids:
			if NetrunArtExport.site_bid(pts[sid], index, cfg.art_site_bid_reach_lots) == "":
				out.append("%s %s has no building" % [corp.id, sid])
	var net := CityLayoutRuler.fixed_net(p_seed, cfg, corp_list, func(c: CorporationData) -> Dictionary: return CityLayout.site_points_in(c, plan))
	var cells: Dictionary = NetrunArtLayout.street_cells(city)
	var ctx := {}
	for link: Dictionary in net["links"]:
		var a: Array = link["pts"][0]
		var b: Array = link["pts"][1]
		for end: Array in [a, b]:
			var l: Array = NetrunArtLayout.plan_to_lot(end, city["origin_lot"], float(city["lot_bu"]))
			var near := INF
			for di in range(-4, 5):
				for dj in range(-4, 5):
					var c := Vector2i(floori(float(l[0])) + di, floori(float(l[1])) + dj)
					if cells.has(c):
						near = minf(near, Vector2(c).distance_to(Vector2(float(l[0]), float(l[1])).floor()))
			if near > STREET_REACH:
				out.append("%s-%s: no street within %d lots of an end" % [link["a"], link["b"], int(STREET_REACH)])
		# Both ends on one street lot need no route; otherwise the street derive must find one (not its L fallback).
		var r: Array = NetrunArtLayout.route_on_streets(city, a, b, ctx)
		var ca := NetrunArtLayout._nearest_cell(NetrunArtLayout.plan_to_lot(a, city["origin_lot"], float(city["lot_bu"])), ctx["cells"])
		var cb := NetrunArtLayout._nearest_cell(NetrunArtLayout.plan_to_lot(b, city["origin_lot"], float(city["lot_bu"])), ctx["cells"])
		if ca != cb and r == [a, [b[0], a[1]], b]:
			out.append("%s-%s: no street route" % [link["a"], link["b"]])
	return out
