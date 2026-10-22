class_name SolSiteCheck
extends RefCounted
## Solace district layout, Site lots (A-069 / A-070 follow-up): every Solace Site lot clears the plinth circle by at least
## one lot, and no stair landing or stair path touches a Site lot.


## Problems found for city `plan` and its `lots` (CityA2Builder lots, Solace pass on); [] when none.
static func problems(plan: CityPlan, lots: Dictionary, tag: String) -> PackedStringArray:
	var out := PackedStringArray()
	var park: Dictionary = lots.get("solace", {})
	var corp := ContentRegistry.get_content(CitySolaceDistrict.TERR) as CorporationData
	if park.is_empty() or corp == null or corp.city_grid == null:
		out.append("%s: no Solace park or corporation" % tag)
		return out
	var pl: Dictionary = park["plinth"]
	var centre: Vector2 = pl["centre"]
	var r_l := float(pl["radius_bu"]) / CityView3D.CONFIG.lot_bu
	var pts := CityLayout.site_points_in(corp, plan)
	var site_lots := {}
	var ids: Array = pts.keys()
	IdSort.sort_ids(ids)
	for id: StringName in ids:
		var l := Vector2i((pts[id] as Vector2).floor())
		if site_lots.has(l):
			out.append("%s: Sites share lot %s" % [tag, l])
		site_lots[l] = id
		if not plan.a2_sites.has(l):
			out.append("%s: Site %s lot %s is not a plan Site lot" % [tag, id, l])
		var gap := CitySolaceDistrict._gap(l, centre)
		if gap < r_l + 1.0 - 0.0001:
			out.append("%s: Site %s at %s is %.2f lots from the circle" % [tag, id, l, gap - r_l])
	var paths := {}
	for p: Dictionary in park["paths"]:
		paths[p["id"]] = p
	for st: Dictionary in pl["stairs"]:
		var pts_l: Array = [st["landing"]]
		if paths.has(st["path"]):
			pts_l.append_array(Array((paths[st["path"]] as Dictionary)["points"]))
		for q: Vector2 in pts_l:
			for l: Vector2i in site_lots:
				if q.x >= l.x and q.x <= l.x + 1 and q.y >= l.y and q.y <= l.y + 1:
					out.append("%s: stair %s touches Site lot %s" % [tag, st["dir"], l])
	return out
