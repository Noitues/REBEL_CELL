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
## H23 #6: what each Site kind is and does (map and mini-map tooltips), led by its kind
## word (CityMapOverlay.kind_word) and the icon's shape, so a newcomer learns the icons
## without the legend.
## H24 K5: the Heat reduction Site is a drop with a flame and a down arrow (the snowflake
## is ICE's icon on the top bar).
const KIND_TIPS := {CityMapOverlay.KIND_TIER: "Site (hexagon, its tier inside): a corporate server on the Grid; clear it, then claim it for your network.", # TR
	CityMapOverlay.KIND_EXPLOIT: "Exploit Site (diamond): clearing it gives an Exploit for the boss breach.", # TR
	CityMapOverlay.KIND_HEAT: "Heat reduction Site (drop, flame and down arrow): clearing it lowers Heat.", # TR
	CityMapOverlay.KIND_BOSS: "Boss Site (star): the corporation's core.", # TR
	CityMapOverlay.KIND_HOME: "CORE (house): your home server; if its integrity reaches 0 the campaign is lost."} # TR


## The map kind (CityMapOverlay.KIND_*) of Site `sd` in campaign `c`: home, objective or
## a plain tier Site.
static func site_kind(c: CampaignState, sd: SiteData) -> String:
	if sd.id == c.grid.home_site_id:
		return CityMapOverlay.KIND_HOME
	match CampaignRules.site_objective(c, sd):
		RC.SiteObjective.EXPLOIT:
			return CityMapOverlay.KIND_EXPLOIT
		RC.SiteObjective.HEAT_REDUCTION:
			return CityMapOverlay.KIND_HEAT
		RC.SiteObjective.BOSS:
			return CityMapOverlay.KIND_BOSS
	return CityMapOverlay.KIND_TIER


## A Site's hover text on the city maps (H21 #14): name and tier (with its difficulty,
## H22: the tier pips' meaning in words), then (H23 #6) its kind and what it does, then
## its status.
static func site_tip(site_label: String, tier: int, status: int, kind: String) -> String:
	var home := kind == CityMapOverlay.KIND_HOME
	var parts := PackedStringArray()
	parts.append("%s." % site_label if home else "%s (%s: %s)." % [site_label, CityMapOverlay.tier_text(tier),
		CityMapOverlay.tr_word("difficulty %d of %d") % [tier, CityMapOverlay.TIER_PIPS_MAX]])
	parts.append(CityMapOverlay.tr_word(String(KIND_TIPS.get(kind, KIND_TIPS[CityMapOverlay.KIND_TIER]))))
	if not home:
		parts.append(CityMapOverlay.tr_word(String(STATUS_TIPS.get(status, ""))))
	return " ".join(parts)


## H24 K7: the home Site's map name, translated ("CORE").
static func home_label() -> String:
	return CityMapOverlay.tr_word(HOME_LABEL)


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
		# H24 K5 / K7: the kind is the drawn icon (no font glyph); a plain Site's hexagon
		# carries its tier, translated.
		var objective := CampaignRules.site_objective(c, sd)
		var kind := site_kind(c, sd)
		var home := kind == CityMapOverlay.KIND_HOME
		var glyph := CityMapOverlay.tier_text(sd.tier) if kind == CityMapOverlay.KIND_TIER else ""
		var named := home or status != GridState.SiteStatus.CORPORATE or kind != CityMapOverlay.KIND_TIER or sd.id == selected
		# Never colour alone (GDD 9.6): claimed Sites carry a spray ring, Seized a cross.
		var mark := ""
		if status == GridState.SiteStatus.CLAIMED:
			mark = CityMapOverlay.MARK_SPRAY
		elif status == GridState.SiteStatus.SEIZED:
			mark = CityMapOverlay.MARK_CROSS
		# H22: the translated name (TextDb), as on every other screen.
		var site_label := home_label() if home else TextDb.t(sd, "display_name")
		nodes.append({"id": sd.id, "at": points[sd.id], "color": col, "mark": mark, "kind": kind,
			"label": site_label if named else "", "name": site_label, "glyph": glyph, "big": home or objective == RC.SiteObjective.BOSS,
			"tier": 0 if home else sd.tier,
			"tip": site_tip(site_label, sd.tier, status, kind)})
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
