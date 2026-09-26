class_name CityLayout
extends RefCounted
## Where the campaign's Grid sits in the city (view-only): Sites are laid out like the
## Grid data inside the corporation's territory, the boss end towards its HQ. Shared by
## the Grid, raid and netrun map overlays so a Site is the same building everywhere.

const RIGHT := Vector2(1, -1)
const DOWN := Vector2(1, 1)


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
		match CampaignRules.site_objective(c, sd):
			RC.SiteObjective.EXPLOIT:
				glyph = "◈"
			RC.SiteObjective.HEAT_REDUCTION:
				glyph = "❄"
			RC.SiteObjective.BOSS:
				glyph = "✦"
		var home := sd.id == c.grid.home_site_id
		var named := home or status != GridState.SiteStatus.CORPORATE or glyph.length() == 1 or sd.id == selected
		nodes.append({"id": sd.id, "at": points[sd.id], "color": col,
			"label": ("CORE" if home else sd.display_name) if named else "", "glyph": "⌂" if home else glyph, "big": home or glyph == "✦"})
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
