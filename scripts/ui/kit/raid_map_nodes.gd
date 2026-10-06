class_name RaidMapNodes
extends RefCounted
## S-MAPVIEW (designer ruling 2026-10-05): the city raid view shows the major (raid) nodes only:
## the Cell's network (home and the claimed Sites) and the Sites the raid's threats really enter
## at and cross (the routes its resolution takes, round 40 raid_view_v3: the network and the
## lettered entries), never a netrun's route nodes (sub-nodes) or every Site a raid could enter
## at (RaidResolver.default_entry_sites lists the whole frontier: main drew a hexagon on each).
## Pure presentation over the rules' own projection (CampaignRules.project_raid): what the map
## shows is what the raid does (preview == result).


## The threat routes in raid events `events` (Site ids, entry first), one per threat in the
## order they entered, repeats dropped (a threat's route is where it entered, then each move).
static func route_paths(events: Array) -> Array[Array]:
	var by_threat := {}
	var order: Array[String] = []
	for e in events:
		var t := String(e.get("threat", ""))
		match String(e.get("type", "")):
			"threat_enters":
				if not by_threat.has(t):
					order.append(t)
				by_threat[t] = [StringName(String(e.get("site", "")))]
			"move":
				if by_threat.has(t):
					var p: Array = by_threat[t]
					var to := StringName(String(e.get("to", "")))
					if p.is_empty() or p[p.size() - 1] != to:
						p.append(to)
	var out: Array[Array] = []
	var seen := {}
	for t in order:
		var p: Array = by_threat[t]
		if p.size() < 2:
			continue
		var key := str(p)
		if seen.has(key):
			continue
		seen[key] = true
		out.append(p)
	return out


## The routes of the raid a raid page shows, as its resolution takes them: `results` a
## projection (RaidResult: the setup, its own events); empty (the playout's start) the next
## raid pending on `c` (CampaignRules.pending_raid) projected now; a played raid's nodes
## (Dictionary, the report) none (`major_ids` keeps the Sites it reached).
static func shown_routes(results: Variant, c: CampaignState, corp: CorporationData, cfg: CampaignConfigData,
		lookup: ContentLookup) -> Array[Array]:
	if results is RaidResolver.RaidResult:
		return route_paths((results as RaidResolver.RaidResult).events)
	var out: Array[Array] = []
	if c == null or corp == null or cfg == null or lookup == null or not (results as Dictionary).is_empty():
		return out
	var pending := CampaignRules.pending_raid(c)
	if pending.is_empty():
		return out
	return route_paths(CampaignRules.project_raid(c, corp, cfg, lookup, pending).events)


## The raid view's nodes (id -> true): the Cell's network on `c`, every Site on `routes`, and
## the Sites named in `touched` (a raid result's nodes: the report keeps what the raid reached).
static func major_ids(c: CampaignState, routes: Array[Array], touched: Dictionary = {}) -> Dictionary:
	var out := {}
	if c == null:
		return out
	for id in c.grid.claimed_ids():
		out[id] = true
	for p in routes:
		for id in p:
			out[StringName(String(id))] = true
	for id in touched:
		out[StringName(String(id))] = true
	return out
