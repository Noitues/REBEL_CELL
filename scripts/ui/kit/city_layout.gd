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
	GridState.SiteStatus.TAKEN: "TAKEN by a raid: run it again to take it back."}
## H23 #6: what each Site kind is and does (map and mini-map tooltips), led by its kind
## word (CityMapOverlay.kind_word) and the icon's shape, so a newcomer learns the icons
## without the legend.
## H24 K5: the Heat reduction Site is a drop with a flame and a down arrow (the snowflake
## is ICE's icon on the top bar).
const KIND_TIPS := {CityMapOverlay.KIND_TIER: "Site (hexagon, its tier inside): a corporate server on the Grid; clear it, then claim it for your network.", # TR
	CityMapOverlay.KIND_EXPLOIT: "Exploit Site (diamond): clearing it gives an Exploit for the Central Server breach.", # TR
	CityMapOverlay.KIND_HEAT: "Heat reduction Site (drop, flame and down arrow): clearing it lowers Heat.", # TR
	CityMapOverlay.KIND_CENTRAL_SERVER: "Central Server (star): the corporation's core.", # TR
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
		RC.SiteObjective.CENTRAL_SERVER:
			return CityMapOverlay.KIND_CENTRAL_SERVER
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
## ART-5 5e: the layout is spread by CityConfig.site_spread (x2: the Grid frames at ortho
## ~440 as round 39) and aimed into the corporation's own territory (site_aim_deg turns
## the layout round its HQ, site_mirror flips it across its run axis), the boss end staying
## next to the HQ. Presentation only: the Grid's rules never read it.
static func site_points(corp: CorporationData) -> Dictionary:
	var cfg: CityConfig = CityView3D.CONFIG
	return site_points_aimed(corp, float(cfg.site_aim_deg.get(corp.id, 0.0)), bool(cfg.site_mirror.get(corp.id, false)),
		spread_of(corp.id))


## Lots per unit of the layout's run (the Grid's left-right) and cross (up-down) axes at
## spread 1, the gap the boss end keeps from the HQ's centre, and the cross axis' offset.
const RUN_HALF := 7.5
const CROSS_HALF := 5.0
const BOSS_GAP := 3.5
const CROSS_OFFSET := 2.5


## ART-5 5e: the layout spread of corporation `id` (CityConfig.site_spread).
static func spread_of(_id: StringName) -> float:
	return maxf(CityView3D.CONFIG.site_spread, 0.1)


## ART-5 5e: the Site layout of `corp` turned `aim_deg` round its HQ (0: the boss end to the
## right of the Grid, as 5a laid it), mirrored across the run axis when `mirror`, spread by
## `spread`; the boss end (the Grid data's right edge) stays BOSS_GAP from the HQ's centre.
static func site_points_aimed(corp: CorporationData, aim_deg: float, mirror: bool, spread: float) -> Dictionary:
	var out := {}
	var min_p := Vector2(1e9, 1e9)
	var max_p := Vector2(-1e9, -1e9)
	for sd in corp.city_grid.sites:
		if sd != null:
			min_p = min_p.min(sd.map_position)
			max_p = max_p.max(sd.map_position)
	var span := (max_p - min_p).max(Vector2(1, 1))
	var a := RIGHT.rotated(deg_to_rad(aim_deg))
	var b := DOWN.rotated(deg_to_rad(aim_deg)) * (-1.0 if mirror else 1.0)
	var centre := NeonCity.hq_of(corp.id) + Vector2(NeonCity.HQ_LOTS * 0.5, NeonCity.HQ_LOTS * 0.5)
	var origin := centre - a * (BOSS_GAP + RUN_HALF * spread) + b * CROSS_OFFSET
	for sd in corp.city_grid.sites:
		if sd == null:
			continue
		var uv := (sd.map_position - min_p) / span * 2.0 - Vector2.ONE
		out[sd.id] = origin + a * uv.x * RUN_HALF * spread + b * uv.y * CROSS_HALF * spread
	return out


## ART-5 5e (the spread sweep): of layout `points` of `corp`, how many Sites stand in its own
## territory (`city.territory_at` of the Site's lot), which territories the others fall in,
## how many sit on an HQ plaza or off the city, and how many share a lot with another Site.
static func spread_report(city: NeonCity, corp: CorporationData, points: Dictionary) -> Dictionary:
	var cfg: CityConfig = CityView3D.CONFIG
	var r := {"sites": 0, "in": 0, "off": {}, "hq": 0, "out": 0, "dup": 0}
	var lots := {}
	var ids: Array = points.keys()
	ids.sort()
	for id in ids:
		var p: Vector2 = points[id]
		var l := Vector2i(floori(p.x), floori(p.y))
		r["sites"] = int(r["sites"]) + 1
		var t := city.territory_at(l.x, l.y)
		if t == corp.id:
			r["in"] = int(r["in"]) + 1
		else:
			var off: Dictionary = r["off"]
			off[t] = int(off.get(t, 0)) + 1
		for tr in NeonCity.TERRITORIES:
			if tr["id"] != &"" and Rect2(tr["at"], Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS)).has_point(Vector2(l) + Vector2(0.5, 0.5)):
				r["hq"] = int(r["hq"]) + 1
		if not Rect2(cfg.city_rect).has_point(Vector2(l)):
			r["out"] = int(r["out"]) + 1
		if lots.has(l):
			r["dup"] = int(r["dup"]) + 1
		lots[l] = true
	return r


## The campaign's Grid as a graph for the city overlay: every Site on a real building
## in the corporation's territory (laid out like the Grid data, the boss end near the
## corporation's HQ), links along the streets, pending threat routes in its colour.
##
## ART-5 5d: `v4` (the Grid page) gives each node its Site marker v4 (`marker`:
## SiteMarker.spec_for; `pinned`; an Exploit Site's `exploit_tag` for its hover file), the
## links to a TAKEN or DOWN node de-powered, and the locked cross-links (grey dashes and a
## padlock). Selectable = a run launches there now (`cfg`: the campaign config, else the
## running one).
static func grid_graph(c: CampaignState, corp: CorporationData, paths: Array[Array], selected: StringName = &"", v4: bool = false,
		cfg: CampaignConfigData = null) -> Dictionary:
	var points := site_points(corp)
	var corp_col := Palette.corp_color(corp.id)
	var nodes: Array[Dictionary] = []
	var selectable := {}
	var dead := {}
	if v4:
		if cfg == null and RunManager != null:
			cfg = RunManager.config()
		if cfg != null:
			for s in CampaignRules.launchable_sites(c, corp, cfg):
				selectable[s.id] = true
	for sd in corp.city_grid.sites:
		if sd == null:
			continue
		var status := c.grid.status_of(sd.id)
		var col := corp_col
		match status:
			GridState.SiteStatus.CLAIMED:
				col = Palette.CELL_TURF  # ANIM-R3 B6: territory, not the damage pink
			GridState.SiteStatus.CLEARED:
				col = Palette.NET_CYAN
			GridState.SiteStatus.TAKEN:
				col = Palette.RESIST_GOLD
		# H24 K5 / K7: the kind is the drawn icon (no font glyph); a plain Site's hexagon
		# carries its tier, translated.
		var objective := CampaignRules.site_objective(c, sd)
		var kind := site_kind(c, sd)
		var home := kind == CityMapOverlay.KIND_HOME
		var glyph := CityMapOverlay.tier_text(sd.tier) if kind == CityMapOverlay.KIND_TIER else ""
		var named := home or status != GridState.SiteStatus.CORPORATE or kind != CityMapOverlay.KIND_TIER or sd.id == selected
		# Never colour alone (GDD 9.6): claimed Sites carry a spray ring, TAKEN a cross.
		var mark := ""
		if status == GridState.SiteStatus.CLAIMED:
			mark = CityMapOverlay.MARK_SPRAY
		elif status == GridState.SiteStatus.TAKEN:
			mark = CityMapOverlay.MARK_CROSS
		# H22: the translated name (TextDb), as on every other screen.
		var site_label := home_label() if home else TextDb.t(sd, "display_name")
		var node := {"id": sd.id, "at": points[sd.id], "color": col, "mark": mark, "kind": kind,
			"label": site_label if named else "", "name": site_label, "glyph": glyph, "big": home or objective == RC.SiteObjective.CENTRAL_SERVER,
			"tier": 0 if home else sd.tier,
			"tip": site_tip(site_label, sd.tier, status, kind)}
		if v4:
			var spec := SiteMarker.spec_for(c, corp.id, sd, selectable.has(sd.id))
			node["marker"] = spec
			node["pinned"] = spec["pinned"]
			var lines := PackedStringArray([node["tip"]])
			var key := SiteMarker.meaning_key(spec)
			if key == "down" or key == "taken":
				lines.append(SiteMarker.meaning(key))
			if spec["status"] == SiteMarker.ST_CLEARED:
				lines.append(CityMapOverlay.tr_word(SiteMarker.PATROL_TIP))
			if spec["kind"] == SiteMarker.KIND_EXPLOIT:
				var tag := SiteMarker.exploit_tag(corp, int(spec["exploit"]))
				if not tag.is_empty():
					tag["site"] = "%s  %s" % [CityMapOverlay.tier_text(sd.tier), site_label]
					node["exploit_tag"] = tag
					lines.insert(0, "%s // %s: %s" % [tag["category"], tag["name"], tag["effect"]])
			node["tip"] = "\n".join(lines)
			if spec["status"] == SiteMarker.ST_TAKEN or spec["status"] == SiteMarker.ST_DOWN:
				dead[sd.id] = true
		nodes.append(node)
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
			var e := {"a": sd.id, "b": l, "color": Palette.CELL_TURF if ours else Color(Palette.NET_CYAN, 0.6), "width": 3.5 if ours else 2.0, "flow": ours}
			if dead.has(sd.id) or dead.has(l):
				e["depowered"] = true  # ART-5 5d: no power flows to a TAKEN or DOWN node
				e["flow"] = false
			edges.append(e)
		if v4:
			# ART-5 5d: the locked cross-links still shut (an opened one is a link like any).
			for l in sd.locked_links:
				var key := [String(sd.id), String(l)]
				key.sort()
				if seen.has(str(key)):
					continue
				seen[str(key)] = true
				if c.grid.is_link_open(sd.id, l):
					edges.append({"a": sd.id, "b": l, "color": Color(Palette.NET_CYAN, 0.6), "width": 2.0, "flow": false})
				else:
					edges.append({"a": sd.id, "b": l, "color": Palette.TEXT_LO, "width": 2.0, "flow": false, "locked": true})
	for path in paths:
		for i in path.size() - 1:
			edges.append({"a": path[i], "b": path[i + 1], "color": corp_col, "width": 4.0, "dashed": true, "flow": true, "arrows": true})
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
