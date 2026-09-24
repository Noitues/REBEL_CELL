class_name GridFixture
extends RefCounted
## Builders for campaign and raid tests: tiny in-memory City Grids, campaigns with
## claimed nodes and deployed assets, over the real node/asset/threat content.


static func site(id: StringName, tier: int, links: Array, objective: int = RC.SiteObjective.NONE, exploit: int = RC.ExploitType.NONE) -> SiteData:
	var s := SiteData.new()
	s.id = id
	s.display_name = String(id)
	s.tier = tier
	var l: Array[StringName] = []
	for x in links:
		l.append(x)
	s.links = l
	s.objective = objective
	s.exploit_type = exploit
	return s


## A chain: home - c1 - c2 - ... - entry (corporate). `extra` adds more sites/links.
static func chain_grid(middle: Array[StringName], entry: StringName = &"entry") -> CityGridData:
	var g := CityGridData.new()
	var ids: Array[StringName] = [&"home"]
	ids.append_array(middle)
	ids.append(entry)
	var sites: Array[SiteData] = []
	for i in ids.size():
		var links := []
		if i + 1 < ids.size():
			links.append(ids[i + 1])
		sites.append(site(ids[i], 1, links))
	g.sites = sites
	g.home_site_id = &"home"
	g.boss_site_id = entry
	return g


static func home_node() -> NetworkNodeData:
	return (ContentRegistry.get_content(&"home_standard") as HomeServerVariantData).core


## Campaign over `grid` with `claims` = {site_id: node_type_id} already installed.
static func campaign(grid: CityGridData, claims: Dictionary = {}, config: CampaignConfigData = null) -> CampaignState:
	var c := CampaignState.new()
	c.schematics = 100
	c.grid = GridState.from_grid(grid, home_node())
	c.grid.sites[c.grid.home_site_id]["node_type"] = "home_server"
	for site_id in claims:
		var node := ContentRegistry.get_content(claims[site_id]) as NetworkNodeData
		var s := c.grid.site(site_id)
		s["status"] = GridState.SiteStatus.CLAIMED
		s["node_type"] = String(claims[site_id])
		s["integrity"] = node.integrity
		s["max_integrity"] = node.integrity
	return c


static func deploy(c: CampaignState, site_id: StringName, asset_id: StringName) -> void:
	c.grid.site(site_id)["assets"].append(String(asset_id))


static func raid(id: StringName, threat_ids: Array, reward: int = 8, waves: int = 1) -> RaidData:
	var r := RaidData.new()
	r.id = id
	r.display_name = String(id)
	r.schematic_reward = reward
	var ws: Array[RaidWaveData] = []
	for w in waves:
		var wave := RaidWaveData.new()
		var ts: Array[ThreatData] = []
		for t in threat_ids:
			ts.append(ContentRegistry.get_content(t) as ThreatData)
		wave.threats = ts
		ws.append(wave)
	r.waves = ws
	return r


static func lookup(extra: Array = []) -> ContentLookup:
	var l := ContentLookup.new().add_registry(ContentRegistry)
	for r in extra:
		l.add(r)
	return l


static func config_with_cap(cap: int) -> CampaignConfigData:
	var cfg: CampaignConfigData = CombatFixture.config().duplicate()
	cfg.raid_step_cap = cap
	return cfg
