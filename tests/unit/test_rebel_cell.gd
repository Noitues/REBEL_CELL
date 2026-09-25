extends GutTest
## M11 REBEL_CELL (GDD 8.5): built from the profile (usage snapshot -> mirrored elites,
## Daemon hub, Site names, mirrored threats), free unlock at ICE 10 everywhere, rebuilt
## identically on resume, "final final" achievement.

var _lookup: ContentLookup
var _template: CorporationData


func before_all() -> void:
	_lookup = GridFixture.lookup()
	_template = ContentRegistry.get_content(&"rebel_cell") as CorporationData


func _profile() -> ProfileState:
	var p := ProfileState.new()
	p.record_usage("class", &"ghost", 5)
	p.record_usage("class", &"breaker", 9)
	p.record_usage("class", &"botnet", 5)
	p.record_usage("daemon", &"adrenal_loop", 4)
	p.record_usage("daemon", &"kernel_sync", 4)
	p.record_usage("node", &"safehouse", 3)
	p.record_usage("asset", &"railgun", 2)
	p.record_usage("asset", &"turret", 6)
	return p


func test_profile_usage_ranks_most_used_first_then_by_id() -> void:
	var p := _profile()
	assert_eq(p.top_used("class", 3), [&"breaker", &"botnet", &"ghost"], "ties break by id")
	assert_eq(p.top_used("asset", 1), [&"turret"])
	assert_eq(p.top_used("node", 5), [&"safehouse"])


func test_snapshot_falls_back_when_nothing_was_used() -> void:
	var snap := RebelCellBuilder.snapshot(ProfileState.new(), &"breaker")
	assert_eq(snap["classes"], ["breaker"])
	assert_eq(snap["assets"], ["turret", "ice_lock", "decoy"])
	assert_eq(snap["daemons"], [])


func test_build_mirrors_classes_daemons_nodes_and_assets() -> void:
	var snap := RebelCellBuilder.snapshot(_profile(), &"breaker")
	var corp := RebelCellBuilder.build(_template, snap, _lookup)
	assert_ne(corp, _template, "a new resource, not the loaded template")
	assert_eq(corp.id, &"rebel_cell")
	assert_eq(corp.elites.size(), 2)
	var mirror := corp.elites[0]
	assert_eq(mirror.id, &"rc_mirror_breaker", "the most-used class is mirrored first")
	var breaker := ContentRegistry.get_content(&"breaker") as ClassData
	for i in mirror.wheel.slots.size():
		var theirs := mirror.wheel.slots[i].slice
		var ours := breaker.starting_wheel.slots[i].slice
		assert_eq(theirs.slice_type, ours.slice_type)
		if ours.slice_type != RC.SliceType.MISS:
			assert_true(theirs.base_output > ours.base_output, "%s -> %s is stronger" % [ours.id, theirs.id])
			assert_true(theirs.base_output <= ours.base_output * 2, "%s -> %s but not doubled" % [ours.id, theirs.id])
	assert_not_null(mirror.wheel.hub, "Adrenal Loop is a data Daemon: the hub runs it")
	assert_eq(mirror.wheel.hub.passive_effects.size(), 1, "Kernel Sync is a custom handler and is not copied")
	var renamed := false
	for s in corp.city_grid.sites:
		renamed = renamed or s.display_name.begins_with("Safehouse")
	assert_true(renamed, "Sites carry the most-used node type")
	var threat_ids := {}
	for r in corp.raids:
		for w in r.waves:
			for t in w.threats:
				threat_ids[t.id] = true
	assert_true(threat_ids.has(&"rc_threat_turret") and threat_ids.has(&"rc_threat_railgun"), "raids field mirrored assets: %s" % [threat_ids.keys()])
	for s in _template.city_grid.sites:
		assert_false(s.display_name.contains(":"), "the loaded template is untouched")


func test_the_same_snapshot_builds_the_same_corporation() -> void:
	var snap := RebelCellBuilder.snapshot(_profile(), &"breaker")
	var a := RebelCellBuilder.build(_template, snap, _lookup)
	var b := RebelCellBuilder.build(_template, snap, _lookup)
	var names_a := []
	var names_b := []
	for s in a.city_grid.sites:
		names_a.append(s.display_name)
	for s in b.city_grid.sites:
		names_b.append(s.display_name)
	assert_eq(names_a, names_b)
	assert_eq(a.elites[1].id, b.elites[1].id)


func test_rebel_cell_opens_free_when_every_corporation_is_cleared_at_ice_10() -> void:
	var p := ProfileState.new()
	assert_false(CampaignRules.corporation_available(p, _lookup, _template))
	for id in [&"solace", &"meridian", &"halcyon", &"orbital"]:
		p.best_ice_by_corp[String(id)] = 10
	assert_true(CampaignRules.corporation_available(p, _lookup, _template), "no purchase needed")
	p.best_ice_by_corp["orbital"] = 9
	assert_false(CampaignRules.corporation_available(p, _lookup, _template))
	var u := CampaignRules.unlock_for(_lookup, _template)
	assert_eq(u.requires_all_corporations_at_ice, CombatFixture.config().rebel_cell_unlock_ice, "matches the config")


func test_a_rebel_cell_campaign_is_rebuilt_from_its_snapshot_on_resume() -> void:
	RunManager.save_slot = "gut_test_rc"
	RunManager.scene_switching_enabled = false
	var saved := RunManager.profile.best_ice_by_corp.duplicate()
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10
	RunManager.profile.record_usage("class", &"ghost", 1000)
	RunManager.new_campaign(1, &"rebel_cell")
	assert_eq(RunManager.campaign.corporation_id, &"rebel_cell")
	assert_eq(RunManager.corporation.elites[0].id, &"rc_mirror_ghost")
	assert_false(RunManager.campaign.generated.is_empty())
	RunManager.autosave()
	RunManager.profile.record_usage("class", &"rigger", 5000)  # the profile moves on...
	RunManager.reset()
	RunManager.profile.best_ice_by_corp = saved
	assert_true(RunManager.resume())
	assert_eq(RunManager.corporation.elites[0].id, &"rc_mirror_ghost", "...but the campaign keeps its snapshot")
	var s := RunManager.start_run()
	assert_not_null(s)
	assert_true(s.pools()["elites"].has(&"rc_mirror_ghost"), "netruns meet the mirrors")
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()  # reload the untouched default profile
	RunManager.scene_switching_enabled = true


func test_final_final_needs_every_corporation_and_rebel_cell_at_ice_20() -> void:
	var p := ProfileState.new()
	var corps := [&"solace", &"meridian", &"halcyon", &"orbital"]
	for id in corps:
		p.best_ice_by_corp[String(id)] = 20
	assert_false(Achievements.check(p, null, corps).has(&"final_final"), "REBEL_CELL too")
	p.best_ice_by_corp["rebel_cell"] = 20
	assert_true(Achievements.check(p, null, corps).has(&"final_final"))
	p.best_ice_by_corp["halcyon"] = 19
	assert_false(Achievements.check(p, null, corps).has(&"final_final"))


func test_mirror_elites_fight() -> void:
	var snap := RebelCellBuilder.snapshot(_profile(), &"breaker")
	var corp := RebelCellBuilder.build(_template, snap, _lookup)
	var lookup := GridFixture.lookup([corp])
	var resolver := CombatResolver.new(CombatFixture.config(), lookup)
	var s := CombatSession.start(resolver, &"breaker", [&"rc_mirror_breaker"], 4)
	var e := s.state.get_combatant(&"enemy_0")
	assert_eq(e.wheel.pointer_ticks.size(), 1, "one pointer, like your own wheel")
	CombatFixture.land(s.state.player, 5)
	var r := s.apply(CombatAction.end_turn())
	assert_true(r.ok(), r.error)
