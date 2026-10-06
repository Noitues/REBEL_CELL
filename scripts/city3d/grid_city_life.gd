class_name GridCityLife
extends RefCounted
## ART-5 5e: what the live City Grid's 3D city shows of the campaign (bible 4.3 Heat on
## maps, 4.4 landmarks), read from the state and never written: the Heat band (its rig of
## police, searchlights and choppers), the hardened Sites (the Sites a run launches at now
## while ENEMY_RESISTANCE is on: fights there are harder, so the rig centres on them), the
## Cell's home lot (where suspicion gathers), whether the Cell's district shows DISPATCH's
## fist (the REBEL_CELL campaign: DISPATCH is that corporation's own crew), and the Site
## landmark (5b's `<corp>_site.glb`) on its Site's lot. Night only: the game has no day rule
## (DECISIONS "ART-5 5e", open question). Pure: same campaign, same answer.


## The Grid's city life for campaign `c` against `corp` under config `cfg`: {"heat_band"
## (CityHeatRig.Band), "hardened" (Site ids, sorted), "home_lot" (Vector2 or INF),
## "dispatch" (bool), "site_corp" (StringName, &"" when none), "site_lot" (Vector2 or INF),
## "points" (CityLayout.site_points: Site id -> lot point)}.
static func of(c: CampaignState, corp: CorporationData, cfg: CampaignConfigData) -> Dictionary:
	var points := CityLayout.site_points(corp)
	var hardened: Array[StringName] = []
	if c.rule_modifier(cfg, RC.RuleModifierType.ENEMY_RESISTANCE) > 0.0:
		for s in CampaignRules.launchable_sites(c, corp, cfg):
			hardened.append(s.id)
	hardened.sort()
	var home: Vector2 = points.get(c.grid.home_site_id, Vector2.INF)
	var ccfg: CityConfig = CityView3D.CONFIG
	var site_lot := CityLandmarks.site_lot(ccfg, corp.id, points)
	return {"heat_band": Palette.heat_band(c.heat, HeatRules.band_levels(c, cfg)), "hardened": hardened,
		"home_lot": home, "dispatch": corp.id == CityView3D.CELL,
		"site_corp": corp.id if site_lot != Vector2.INF else &"", "site_lot": site_lot, "points": points}
