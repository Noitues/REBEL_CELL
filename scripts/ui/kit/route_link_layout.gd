class_name RouteLinkLayout
extends RefCounted
## S-MAPVIEW (designer ruling 2026-10-05, "city as a map in raid and netrun views"): a netrun's
## route nodes sit along the link between two raid nodes (the Grid's Sites), not scattered on
## the city. The link is the one the run jacks along (RunManager.jack_link, bible 4.6): from
## the Cell's end (home or a claimed Site linked to the target, lowest content id first) to the
## run's Site. Layer k of L sits k / L of the way along it (the last layer, the final Rack, on
## the target Site); the entry (the Cell before its first node) at the Cell's end; a layer's
## nodes side by side across the link, `route_link_lateral` lots apart, in index order (node
## ids are L<layer>N<index>: content order). Pure presentation from the run's map and the
## Grid's layout: no rule reads it, the route's generation is unchanged.


## The Site a run on `site_id` jacks in from: home or a claimed Site linked to it (the target's
## own links, lowest id first; else an owned Site whose links name it, lowest id first); &""
## when none (RunManager.jack_link's choice, shared so the jack and the route ride one link).
static func from_site(corp: CorporationData, campaign: CampaignState, site_id: StringName) -> StringName:
	if corp == null or campaign == null or site_id == &"":
		return &""
	var to_site := CampaignRules.site_data(corp, site_id)
	if to_site == null:
		return &""
	var owned: Array[StringName] = []
	if corp.city_grid != null:
		owned.append(corp.city_grid.home_site_id)
	if campaign.grid != null:
		owned.append_array(campaign.grid.claimed_ids())
	var links: Array = to_site.links.duplicate()
	links.sort()
	for l in links:
		if owned.has(l) and l != site_id:
			return l
	var mine := owned.duplicate()
	mine.sort()
	for o in mine:
		if o == site_id:
			continue
		var od := CampaignRules.site_data(corp, o)
		if od != null and od.links.has(site_id):
			return o
	return &""


## The link (lot points [a, b]) a run on `site_id` lies along, on the layout `points`
## (CityLayout.site_points): from its jack-in Site to the run's Site; with no owned end, from
## home. A link shorter than `min_lots` keeps its target end and reaches back that far along
## its own heading (or the layout's run axis when the ends meet).
static func link_of(cfg: CityConfig, corp: CorporationData, campaign: CampaignState, site_id: StringName,
		points: Dictionary) -> PackedVector2Array:
	var b: Vector2 = points.get(site_id, Vector2.ZERO)
	var from := from_site(corp, campaign, site_id)
	if from == &"" and corp != null and corp.city_grid != null:
		from = corp.city_grid.home_site_id
	var a: Vector2 = points.get(from, b)
	var d := b - a
	if d.length() < cfg.route_link_min_lots:
		var dir := d.normalized() if d.length() > 0.001 else CityLayout.RIGHT.normalized()
		a = b - dir * cfg.route_link_min_lots
	return PackedVector2Array([a, b])


## {"nodes": node id -> lot point for every node of `map` along `link` ([a, b], lots),
## "entry": the Cell's point before the first layer (the link's start)}.
static func place(cfg: CityConfig, map: MapGraph, link: PackedVector2Array) -> Dictionary:
	var out := {}
	if map == null or link.size() < 2:
		return {"nodes": out, "entry": Vector2.INF}
	var a := link[0]
	var b := link[1]
	var d := b - a
	var across := Vector2(-d.y, d.x).normalized() if d.length() > 0.001 else CityLayout.DOWN.normalized()
	var layers := map.layer_count()
	for li in range(1, layers + 1):
		var row: Array = map.nodes_in_layer(li).duplicate()
		row.sort_custom(func(p: Dictionary, q: Dictionary) -> bool:
			return int(p["index"]) < int(q["index"]) if int(p["index"]) != int(q["index"]) else String(p["id"]) < String(q["id"]))
		var at := a + d * (float(li) / float(layers))
		for k in row.size():
			out[row[k]["id"]] = at + across * (float(k) - (row.size() - 1) * 0.5) * cfg.route_link_lateral
	return {"nodes": out, "entry": a}


## The distance (lots) from point `p` to the segment `link` ([a, b]).
static func off_link(p: Vector2, link: PackedVector2Array) -> float:
	var a := link[0]
	var ab := link[1] - a
	var h := clampf((p - a).dot(ab) / maxf(ab.length_squared(), 1e-6), 0.0, 1.0)
	return p.distance_to(a + ab * h)
