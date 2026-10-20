class_name KeyLots
extends RefCounted
## Plan 2 EX-02 / EX-03 (REPLAN 2.3, 2.10): key placement. Each access key is one Exploit, and each corporation's three
## Exploit types (intel, breach, virus) stand in their own special building on a city lot (`lots_for`'s building cells).
## A key's building is the one under its Exploit Site's lot (the Grid layout, ruling O7), or the nearest free one:
## nearest by Chebyshev lot distance, ties by the cell's lot (i, then j). No lot is shared, and a key never stands on or
## beside an HQ. The footprint (config BU) must lie on land inside the city, clear of every HQ rect and of the other
## keys' footprints (each grown by the clearance), and the run's start is a street lot outside the footprint plus clearance.
##
## Derived data only: the plan's lots and the corporations' Site layouts decide it, so the same city seed gives the same
## placement and no RNG stream is read or advanced (no new stream; the order of corporations and Exploits is by id / type).
##
## A placement is {"keys": Array of key records (corp id, then Exploit order), "by_bid": bid -> record, "by_corp": corp id ->
## {exploit name -> record}, "problems": PackedStringArray (a key that found no building, empty when sound)}. A key record:
## {"corp", "exploit" (name), "exploit_type", "site", "bid" (the cell's top-left lot "i:j"), "cell" (Rect2i), "building"
## (the kind, the per-lot special-building hook), "footprint" (Rect2, lots), "start" (Vector2i street lot), "occlusion_host": true}.

## The Exploit types in key order, and their names (the contract's names).
const ORDER: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
const NAMES := {RC.ExploitType.INTEL: "intel", RC.ExploitType.BREACH: "breach", RC.ExploitType.VIRUS: "virus"}
## CityA2Builder's lot kinds this reads (the values of K_STREET and K_WATER).
const STREET := 1
const WATER := 4
const NO_START := Vector2i(1 << 30, 1 << 30)


## The placement for `corps` (CorporationData with a Grid) on a city whose building cells and lot kinds are `lots`
## (CityA2Builder.lots_for), `hq_rects` (corp id -> Rect2i) and Site layout points `points` (corp id -> {site id -> lot
## Vector2}). `lot_bu` is the BU per lot. Pure.
static func place(lots: Dictionary, hq_rects: Dictionary, corps: Array, points: Dictionary, cfg: CampaignConfigData, lot_bu: float) -> Dictionary:
	var out := {"keys": [], "by_bid": {}, "by_corp": {}, "problems": PackedStringArray()}
	var problems := PackedStringArray()
	var cells: Array = lots["cells"]
	var hqs: Array[Rect2] = []
	var hq_ids: Array = hq_rects.keys()
	IdSort.sort_ids(hq_ids)
	for id: Variant in hq_ids:
		hqs.append(Rect2(hq_rects[id]))
	var ordered: Array = corps.duplicate()
	ordered.sort_custom(func(a: CorporationData, b: CorporationData) -> bool: return String(a.id) < String(b.id))
	var taken: Array[Rect2] = []
	for corp: CorporationData in ordered:
		if corp == null or corp.city_grid == null:
			continue
		var pts: Dictionary = points.get(corp.id, {})
		for et in ORDER:
			var site := _site_of(corp, et)
			if site == null or not pts.has(site.id):
				continue
			var rec := _pick(lots, cells, hqs, taken, corp, et, site, pts[site.id], cfg, lot_bu)
			if rec.is_empty():
				problems.append("%s/%s: no building within %d lots of %s" % [corp.id, NAMES[et], cfg.exploit_building_reach_lots, site.id])
				continue
			var clear := cfg.exploit_building_clearance_bu / lot_bu
			taken.append((rec["footprint"] as Rect2).grow(clear))
			(out["keys"] as Array).append(rec)
			out["by_bid"][rec["bid"]] = rec
			if not (out["by_corp"] as Dictionary).has(String(corp.id)):
				out["by_corp"][String(corp.id)] = {}
			out["by_corp"][String(corp.id)][rec["exploit"]] = rec
	out["problems"] = problems
	return out


## The placement for city seed `city_seed`: its plan, lots and the corporations' Site layouts. `corps`: every corporation
## with a Grid.
static func for_seed(city_seed: int, corps: Array, lot_bu: float) -> Dictionary:
	var cfg := CityPlan.plan_config()
	var plan := CityPlan.for_seed(city_seed)
	var lots := CityA2Builder.lots_for(plan, cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0)
	var points := {}
	for corp: CorporationData in corps:
		if corp != null and corp.city_grid != null:
			points[corp.id] = CityLayout.site_points_in(corp, plan)
	return place(lots, plan.hq_rects(NeonCity.HQ_LOTS), corps, points, cfg, lot_bu)


## The building kind of key (`corp`, exploit type `et`): the config table, else "key_<exploit>".
static func kind_of(cfg: CampaignConfigData, corp: StringName, et: int) -> StringName:
	var k := "%s/%s" % [corp, NAMES[et]]
	return StringName(String(cfg.exploit_building_kinds[k])) if cfg.exploit_building_kinds.has(k) else StringName("key_" + String(NAMES[et]))


## The per-lot special-building hook: the kind of the building on cell `bid`, or &"" for an ordinary lot.
static func special_building_at(placement: Dictionary, bid: String) -> StringName:
	var r: Dictionary = (placement["by_bid"] as Dictionary).get(bid, {})
	return r["building"] if not r.is_empty() else &""


## Building ids excluded from the view's flatten / ghost set (the hosts), sorted.
static func occlusion_exempt(placement: Dictionary) -> PackedStringArray:
	var ids: Array = []
	for r: Dictionary in placement["keys"]:
		if bool(r["occlusion_host"]):
			ids.append(String(r["bid"]))
	IdSort.sort_ids(ids)
	return PackedStringArray(ids)


## `all_bids` less the hosts: the buildings the view still flattens or ghosts (order kept).
static func flatten_set(all_bids: Array, placement: Dictionary) -> Array:
	var exempt := occlusion_exempt(placement)
	var out := []
	for b: Variant in all_bids:
		if not exempt.has(String(b)):
			out.append(b)
	return out


## The key records of `corp` for key_locations.json: exploit name -> {"bid", "building", "start" [i, j]}.
static func export_keys(placement: Dictionary, corp: StringName) -> Dictionary:
	var out := {}
	var by: Dictionary = (placement["by_corp"] as Dictionary).get(String(corp), {})
	for name: String in by:
		var r: Dictionary = by[name]
		out[name] = {"bid": r["bid"], "building": String(r["building"]), "start": [(r["start"] as Vector2i).x, (r["start"] as Vector2i).y]}
	return out


## Problems of `placement` against the rules (empty = sound): distinct lots, no HQ lot, footprint on land and clear of the
## HQs and each other, the start a street lot outside the footprint plus clearance and outside every building cell.
static func validate(placement: Dictionary, lots: Dictionary, hq_rects: Dictionary, cfg: CampaignConfigData, lot_bu: float) -> PackedStringArray:
	var errors := PackedStringArray(placement["problems"])
	var clear := cfg.exploit_building_clearance_bu / lot_bu
	var seen := {}
	var keys: Array = placement["keys"]
	var cells: Array = lots["cells"]
	var R: Rect2i = lots["rect"]
	var kind: PackedByteArray = lots["kind"]
	for i in keys.size():
		var r: Dictionary = keys[i]
		var tag := "%s/%s" % [r["corp"], r["exploit"]]
		if seen.has(r["bid"]):
			errors.append("%s shares lot %s with %s." % [tag, r["bid"], seen[r["bid"]]])
		seen[r["bid"]] = tag
		var cell: Rect2i = r["cell"]
		var fp: Rect2 = r["footprint"]
		for id: Variant in hq_rects:
			if Rect2(hq_rects[id]).intersects(Rect2(cell)):
				errors.append("%s stands on the HQ of %s." % [tag, id])
			if Rect2(hq_rects[id]).intersects(fp.grow(clear)):
				errors.append("%s footprint reaches the HQ of %s." % [tag, id])
		if _wet(kind, R, fp):
			errors.append("%s footprint is over water or off the city." % tag)
		for j in range(i + 1, keys.size()):
			if fp.grow(clear).intersects((keys[j]["footprint"] as Rect2).grow(clear)):
				errors.append("%s footprint meets %s/%s." % [tag, keys[j]["corp"], keys[j]["exploit"]])
		var s: Vector2i = r["start"]
		var c := Vector2(s) + Vector2(0.5, 0.5)
		if fp.grow(clear).has_point(c):
			errors.append("%s start %s is inside the footprint plus clearance." % [tag, s])
		for cc: Dictionary in cells:
			if (cc["cell"] as Rect2i).has_point(s):
				errors.append("%s start %s is inside a building." % [tag, s])
				break
		if not R.has_point(s) or kind[(s.y - R.position.y) * R.size.x + (s.x - R.position.x)] != STREET:
			errors.append("%s start %s is not a street lot." % [tag, s])
	return errors


# --- Internals -------------------------------------------------------------------------------

## The Exploit Site of `corp` for type `et` (lowest id when several).
static func _site_of(corp: CorporationData, et: int) -> SiteData:
	var best: SiteData = null
	for sd in corp.city_grid.sites:
		if sd != null and sd.exploit_type == et and (best == null or String(sd.id) < String(best.id)):
			best = sd
	return best


static func _pick(lots: Dictionary, cells: Array, hqs: Array[Rect2], taken: Array[Rect2], corp: CorporationData, et: int, site: SiteData,
		point: Vector2, cfg: CampaignConfigData, lot_bu: float) -> Dictionary:
	var R: Rect2i = lots["rect"]
	var kind: PackedByteArray = lots["kind"]
	var p := Vector2i(point.floor())
	var cands: Array = []
	for ci in cells.size():
		var cell: Rect2i = cells[ci]["cell"]
		var d := maxi(maxi(cell.position.x - p.x, p.x - (cell.end.x - 1)), maxi(cell.position.y - p.y, p.y - (cell.end.y - 1)))
		d = maxi(d, 0)
		if d <= cfg.exploit_building_reach_lots:
			cands.append([d, cell.position.x, cell.position.y, ci])
	cands.sort_custom(func(a: Array, b: Array) -> bool:
		for k in 3:
			if a[k] != b[k]:
				return a[k] < b[k]
		return false)
	var clear := cfg.exploit_building_clearance_bu / lot_bu
	var size := Vector2(cfg.exploit_building_lot_w_bu, cfg.exploit_building_lot_d_bu) / lot_bu
	for c: Array in cands:
		var cell: Rect2i = cells[c[3]]["cell"]
		if _hits(hqs, Rect2(cell)):
			continue
		var fp := Rect2(Vector2(cell.position) + Vector2(cell.size) * 0.5 - size * 0.5, size)
		var grown := fp.grow(clear)
		if _hits(hqs, grown) or _hits(taken, grown) or _wet(kind, R, fp):
			continue
		var start := _start(kind, R, fp, clear, cfg.exploit_building_start_reach_lots)
		if start == NO_START:
			continue
		return {"corp": String(corp.id), "exploit": NAMES[et], "exploit_type": et, "site": String(site.id),
			"bid": "%d:%d" % [cell.position.x, cell.position.y], "cell": cell, "building": kind_of(cfg, corp.id, et),
			"footprint": fp, "start": start, "occlusion_host": true}
	return {}


static func _hits(rects: Array[Rect2], r: Rect2) -> bool:
	for o in rects:
		if o.intersects(r):
			return true
	return false


## True when footprint `fp` leaves the city rect `R` or covers a water lot.
static func _wet(kind: PackedByteArray, R: Rect2i, fp: Rect2) -> bool:
	if not Rect2(R).encloses(fp):
		return true
	for j in range(int(floorf(fp.position.y)), int(ceilf(fp.end.y))):
		for i in range(int(floorf(fp.position.x)), int(ceilf(fp.end.x))):
			if kind[(j - R.position.y) * R.size.x + (i - R.position.x)] == WATER:
				return true
	return false


## The border street's start: the street lot nearest the footprint whose centre lies outside the footprint grown by `clear`
## (within `reach` lots beyond it); ties by lot row, then column. NO_START when none.
static func _start(kind: PackedByteArray, R: Rect2i, fp: Rect2, clear: float, reach: int) -> Vector2i:
	var grown := fp.grow(clear)
	var win := fp.grow(clear + reach)
	var best := NO_START
	var best_d := INF
	for j in range(maxi(int(floorf(win.position.y)), R.position.y), mini(int(ceilf(win.end.y)), R.end.y)):
		for i in range(maxi(int(floorf(win.position.x)), R.position.x), mini(int(ceilf(win.end.x)), R.end.x)):
			if kind[(j - R.position.y) * R.size.x + (i - R.position.x)] != STREET:
				continue
			var c := Vector2(i, j) + Vector2(0.5, 0.5)
			if grown.has_point(c):
				continue
			var dx := maxf(maxf(fp.position.x - c.x, c.x - fp.end.x), 0.0)
			var dy := maxf(maxf(fp.position.y - c.y, c.y - fp.end.y), 0.0)
			var d := dx * dx + dy * dy
			if d < best_d:
				best_d = d
				best = Vector2i(i, j)
	return best
