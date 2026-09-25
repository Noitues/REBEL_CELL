extends GutTest
## M8 corporation selection and Meridian Freight Systems (GAP_ANALYSIS P0 3, P1 8):
## unlock gating, per-corporation raids, pools, boss hub, Tariff slice, voice, picker.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _meridian: CorporationData
var _solace: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_meridian = ContentRegistry.get_content(&"meridian") as CorporationData
	_solace = ContentRegistry.get_content(&"solace") as CorporationData


func _campaign(corp: CorporationData) -> CampaignState:
	return CampaignRules.new_campaign(corp, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())


func test_meridian_has_a_full_corporation() -> void:
	assert_not_null(_meridian)
	assert_eq(_meridian.city_grid.sites.size(), 32)
	assert_eq(_meridian.exploits.size(), 3)
	assert_eq(_meridian.story_paths.size(), 6)
	assert_eq(_meridian.enemies.size(), 6)
	assert_eq(_meridian.elites.size(), 2)
	assert_eq(_meridian.final_boss.id, &"the_manifest")
	assert_true(_meridian.final_boss.phases.size() >= 2)
	for e in _meridian.enemies + _meridian.elites:
		assert_eq(e.corporation_id, &"meridian", String(e.id))
	var foreshadows := []
	for p in _meridian.story_paths:
		foreshadows.append(p.foreshadows)
		assert_eq(p.beats.size(), 3, String(p.id))
		assert_not_null(p.finale)
	assert_true(foreshadows.has(&"dispatch") and foreshadows.has(&"halcyon"))


func test_corporations_are_gated_by_profile_unlocks() -> void:
	var profile := ProfileState.new()
	var ids := []
	for c in CampaignRules.available_corporations(profile, _lookup):
		ids.append(c.id)
	assert_eq(ids, [&"solace"], "only Solace starts open")
	var u := CampaignRules.unlock_for(_lookup, _meridian)
	assert_not_null(u)
	assert_eq(u.kind, RC.UnlockKind.CORPORATION)
	profile.add_unlock(u.id)
	assert_true(CampaignRules.corporation_available(profile, _lookup, _meridian))


func test_threshold_raids_resolve_to_the_corporations_own_raid() -> void:
	var m := _campaign(_meridian)
	m.corporation_id = &"meridian"
	HeatRules.add_heat(m, 26, _cfg, "test")
	assert_false(m.pending_raids.is_empty())
	var raid := CampaignRules.raid_data(m.pending_raids[0], _lookup)
	assert_eq(raid.id, &"raid_mer_heat_25", "Meridian's Delivery Exception replaces the shared raid")
	var s := _campaign(_solace)
	HeatRules.add_heat(s, 26, _cfg, "test")
	assert_eq(CampaignRules.raid_data(s.pending_raids[0], _lookup).id, &"raid_heat_25")
	assert_eq(CampaignRules.raid_data({"raid_id": "raid_heat_25"}, _lookup).id, &"raid_heat_25", "old saves keep the shared raid")


func test_meridian_netruns_use_meridian_pools() -> void:
	var c := _campaign(_meridian)
	assert_eq(c.corporation_id, &"meridian")
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"m1_a", 5, _meridian)
	var pools := s.pools()
	for id in pools["enemies"] + pools["elites"]:
		assert_eq((_lookup.get_content(id) as EnemyData).corporation_id, &"meridian", String(id))
	assert_eq(pools["mini_bosses"], [&"logistics_director"])
	assert_true(pools["events"].has(&"ev_mer_misdelivered"))
	assert_false(pools["events"].has(&"ev_wellness_kiosk"), "Solace-only events stay in Solace")
	assert_true(pools["events"].has(&"ev_rival_crew"), "corporation-neutral events are shared")


func test_the_manifest_shields_itself_unless_breached() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"the_manifest"], 4)
	CombatFixture.land(s.state.player, 5)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 5)
	var r := s.apply(CombatAction.end_turn())
	var shielded := false
	for e in CombatFixture.events_of(r, "shield"):
		if e["target"] == &"enemy_0":
			shielded = true
	assert_true(shielded, "Priority Routing: +4 shield at turn start")


func test_tariff_drains_ram() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"customs_scanner"], 4)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 1)  # Tariff
	CombatFixture.land(s.state.player, 5)
	var r := s.apply(CombatAction.end_turn())
	var drained := false
	for e in CombatFixture.events_of(r, "ram"):
		if int(e["amount"]) < 0:
			drained = true
	assert_true(drained, "Tariff drains RAM")


func test_meridian_voice_and_briefings() -> void:
	assert_ne(Dialogue.briefing(&"meridian", &"m1_a"), "")
	assert_ne(Dialogue.briefing(&"meridian", &"the_manifest_site"), "")
	var mer := Dialogue.raid_warning(&"meridian", &"raid_heat_25")
	var sol := Dialogue.raid_warning(&"solace", &"raid_heat_25")
	assert_true(mer.begins_with("MERIDIAN"), mer)
	assert_ne(mer, sol)
	for s in _meridian.city_grid.sites:
		if s.id != _meridian.city_grid.home_site_id:
			assert_ne(Dialogue.briefing(&"meridian", s.id), "", "briefing for %s" % s.id)


func test_run_manager_falls_back_to_solace_when_locked() -> void:
	RunManager.save_slot = "gut_test_corp"
	var had := RunManager.profile.has_unlock(&"unlock_meridian")
	RunManager.profile.unlocks.erase(&"unlock_meridian")
	RunManager.new_campaign(1, &"meridian")
	assert_eq(RunManager.campaign.corporation_id, &"solace", "locked corporation falls back")
	RunManager.profile.add_unlock(&"unlock_meridian")
	RunManager.new_campaign(1, &"meridian")
	assert_eq(RunManager.campaign.corporation_id, &"meridian")
	assert_eq(RunManager.corporation.id, &"meridian")
	if not had:
		RunManager.profile.unlocks.erase(&"unlock_meridian")
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT


func test_hq_start_panel_offers_a_corporation_picker() -> void:
	RunManager.save_slot = "gut_test_corp"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	var hq: Control = add_child_autofree(load("res://scenes/hq/hq_scene.tscn").instantiate())
	hq.show_start()
	var picker := hq.find_child("CorporationPicker", true, false) as OptionButton
	assert_not_null(picker)
	assert_true(picker.item_count >= 1)
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


## Every generated corporation (M8+) has the full shape, its own raids and briefings.
const GENERATED := [&"meridian", &"halcyon"]


func test_every_generated_corporation_is_complete() -> void:
	for id in GENERATED:
		var corp := ContentRegistry.get_content(id) as CorporationData
		assert_not_null(corp, String(id))
		assert_eq(corp.city_grid.sites.size(), 32, String(id))
		assert_eq(corp.exploits.size(), 3, String(id))
		assert_eq(corp.story_paths.size(), 6, String(id))
		assert_eq(corp.enemies.size(), 6, String(id))
		assert_eq(corp.elites.size(), 2, String(id))
		assert_true(corp.final_boss.is_boss and corp.final_boss.phases.size() >= 2, String(id))
		assert_not_null(CampaignRules.unlock_for(_lookup, corp), "%s is a Profile unlock" % id)
		var c := _campaign(corp)
		HeatRules.add_heat(c, 26, _cfg, "test")
		var raid := CampaignRules.raid_data(c.pending_raids[0], _lookup)
		assert_eq(raid.corporation_id, id, "%s threshold raid is its own" % id)
		for s in corp.city_grid.sites:
			if s.id != corp.city_grid.home_site_id:
				assert_ne(Dialogue.briefing(id, s.id), "", "%s briefing for %s" % [id, s.id])
		var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, corp.city_grid.get_site(corp.city_grid.home_site_id).links[0], 5, corp)
		assert_eq(s.pools()["mini_bosses"].size(), 1, "%s mini-boss" % id)


func test_citations_plant_a_parasite_on_your_wheel() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"parking_warden"], 4)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 1)  # Citation
	CombatFixture.land(s.state.player, 5)
	s.apply(CombatAction.end_turn())
	assert_true(s.state.player.wheel.slice_statuses.has(RC.Status.PARASITE), "a Citation halves one of your slices")


func test_the_civic_core_heals_and_blocks_unless_breached() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"civic_core"], 4)
	s.state.get_combatant(&"enemy_0").hp -= 50
	CombatFixture.land(s.state.player, 5)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 5)
	var r := s.apply(CombatAction.end_turn())
	var healed := false
	var blocked := false
	for e in CombatFixture.events_of(r, "heal"):
		healed = healed or e["target"] == &"enemy_0"
	for e in CombatFixture.events_of(r, "block"):
		blocked = blocked or e["target"] == &"enemy_0"
	assert_true(healed and blocked, "Emergency Powers: heal and block at turn start")
