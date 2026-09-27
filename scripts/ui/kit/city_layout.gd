class_name CityLayout
extends RefCounted
## Where the campaign's Grid sits in the city (view-only): Sites are laid out like the
## Grid data inside the corporation's territory, the boss end towards its HQ. Shared by
## the Grid, raid and netrun map overlays so a Site is the same building everywhere.

const RIGHT := Vector2(1, -1)
const DOWN := Vector2(1, 1)
## The home Site's name on the maps (never its id).
const HOME_LABEL := "CORE"
## What a Site's status means (map tooltips).
const STATUS_TIPS := {GridState.SiteStatus.CORPORATE: "Corporate: run it to clear it.",
	GridState.SiteStatus.CLEARED: "Cleared: claim it to build a node of your network.",
	GridState.SiteStatus.CLAIMED: "Claimed: part of your network; it defends in raids.",
	GridState.SiteStatus.SEIZED: "Seized by a raid: run it again to take it back."}
## What a Site's objective adds (map tooltips).
const OBJECTIVE_TIPS := {RC.SiteObjective.EXPLOIT: "Exploit Site: clearing it gives an Exploit for the boss breach.",
	RC.SiteObjective.HEAT_REDUCTION: "Heat reduction: clearing it lowers Heat.",
	RC.SiteObjective.BOSS: "Boss Site: the corporation's core."}


## A Site's hover text on the city maps (H21 #14): name and tier, status, objective.
static func site_tip(site_label: String, tier: int, status: int, objective: int, home: bool) -> String:
	var parts := PackedStringArray(["%s (T%d)." % [site_label, tier]])
	if home:
		parts.append("Your home server: if its integrity reaches 0 the campaign is lost.")
	else:
		parts.append(String(STATUS_TIPS.get(status, "")))
	if OBJECTIVE_TIPS.has(objective):
		parts.append(String(OBJECTIVE_TIPS[objective]))
	return " ".join(parts)


## Grid point (lots) for every Site id of `corp`'s City Grid.
static func site_points(corp: CorporationData) -> Dictionary:
	var out := {}
	var min_p := Vector2(1e9, 1e9)
	var max_p := Vector2(-1e9, -1e9)
	for sd in corp.city_grid.sites:
		if sd != null:
			min_p = min_p.min(sd.map_position)
			max_p = max_p.max(sd.map_position)
	var span := (max_p - min_p).max(Vector2(1, 1))
	var origin := NeonCity.hq_of(corp.id) + Vector2(NeonCity.HQ_LOTS * 0.5, NeonCity.HQ_LOTS * 0.5) - RIGHT * 11.0 + DOWN * 2.5
	for sd in corp.city_grid.sites:
		if sd == null:
			continue
		var uv := (sd.map_position - min_p) / span * 2.0 - Vector2.ONE
		out[sd.id] = origin + RIGHT * uv.x * 7.5 + DOWN * uv.y * 5.0
	return out


## The campaign's Grid as a graph for the city overlay: every Site on a real building
## in the corporation's territory (laid out like the Grid data, the boss end near the
## corporation's HQ), links along the streets, pending threat routes in its colour.
static func grid_graph(c: CampaignState, corp: CorporationData, paths: Array[Array], selected: StringName = &"") -> Dictionary:
	var points := site_points(corp)
	var corp_col := Palette.corp_color(corp.id)
	var nodes: Array[Dictionary] = []
	for sd in corp.city_grid.sites:
		if sd == null:
			continue
		var status := c.grid.status_of(sd.id)
		var col := corp_col
		match status:
			GridState.SiteStatus.CLAIMED:
				col = Palette.CELL_PINK
			GridState.SiteStatus.CLEARED:
				col = Palette.NET_CYAN
			GridState.SiteStatus.SEIZED:
				col = Palette.RESIST_GOLD
		var glyph := "T%d" % sd.tier
		var kind := CityMapOverlay.KIND_TIER
		var objective := CampaignRules.site_objective(c, sd)
		match objective:
			RC.SiteObjective.EXPLOIT:
				glyph = "◈"
				kind = CityMapOverlay.KIND_EXPLOIT
			RC.SiteObjective.HEAT_REDUCTION:
				glyph = "❄"
				kind = CityMapOverlay.KIND_HEAT
			RC.SiteObjective.BOSS:
				glyph = "✦"
				kind = CityMapOverlay.KIND_BOSS
		var home := sd.id == c.grid.home_site_id
		if home:
			kind = CityMapOverlay.KIND_HOME
		var named := home or status != GridState.SiteStatus.CORPORATE or glyph.length() == 1 or sd.id == selected
		# Never colour alone (GDD 9.6): claimed Sites carry a spray ring, Seized a cross.
		var mark := ""
		if status == GridState.SiteStatus.CLAIMED:
			mark = CityMapOverlay.MARK_SPRAY
		elif status == GridState.SiteStatus.SEIZED:
			mark = CityMapOverlay.MARK_CROSS
		var site_label := HOME_LABEL if home else sd.display_name
		nodes.append({"id": sd.id, "at": points[sd.id], "color": col, "mark": mark, "kind": kind,
			"label": site_label if named else "", "glyph": "⌂" if home else glyph, "big": home or objective == RC.SiteObjective.BOSS,
			"tip": site_tip(site_label, sd.tier, status, objective, home)})
	var edges: Array[Dictionary] = []
	var seen := {}
	for sd in corp.city_grid.sites:
		if sd == null:
			continue
		for l in sd.links:
			var key := [String(sd.id), String(l)]
			key.sort()
			if seen.has(str(key)):
				continue
			seen[str(key)] = true
			var ours := c.grid.is_claimed(sd.id) and c.grid.is_claimed(l)
			edges.append({"a": sd.id, "b": l, "color": Palette.CELL_PINK if ours else Color(Palette.NET_CYAN, 0.6), "width": 3.5 if ours else 2.0, "flow": ours})
	for path in paths:
		for i in path.size() - 1:
			edges.append({"a": path[i], "b": path[i + 1], "color": corp_col, "width": 4.0, "dashed": true, "flow": true})
	return {"nodes": nodes, "edges": edges}


## Pending raids' routes, entry -> home (Site ids).
static func threat_paths(c: CampaignState, corp: CorporationData) -> Array[Array]:
	var paths: Array[Array] = []
	for pending in c.pending_raids:
		for entry in CampaignRules.raid_entries(c, corp, pending):
			var path: Array = [entry]
			var cur := entry
			var guard := 0
			while cur != c.grid.home_site_id and guard < 12:
				guard += 1
				cur = c.grid.next_hop(cur, c.grid.home_site_id, corp.city_grid)
				path.append(cur)
			paths.append(path)
	return paths
