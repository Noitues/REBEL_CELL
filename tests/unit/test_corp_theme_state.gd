extends GutTest
## Plan 2 WH-02 (REPLAN 2026-10-19 A 2.4), fast tier: the additive corp_theme block. A v5 save
## written by the pre-WH-02 build (tests/fixtures/saves/v5/, recorded with
## tools/design_lab/wh02_v5_fixture.tscn on w1-close 0613a8c4) loads with every theme field at
## its default and hashes exactly as that build hashed it; the block joins the save and the
## hash only when a field is not default; every field round-trips the save (through JSON).

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")
const FIXTURE := "res://tests/fixtures/saves/v5/v5_pre_wh02.json"
const FIXTURE_HASHES := "res://tests/fixtures/saves/v5/v5_pre_wh02.hashes.json"

var _saves: Node


func before_each() -> void:
	_saves = autofree(SaveServiceScript.new())


func _fixture() -> Dictionary:
	var data: Dictionary = _saves.migrate(JSON.parse_string(FileAccess.get_file_as_string(FIXTURE)))
	assert_false(data.is_empty(), "the v5 fixture loads (%s)" % _saves.last_error)
	return data


func _hashes() -> Dictionary:
	return JSON.parse_string(FileAccess.get_file_as_string(FIXTURE_HASHES))


func test_the_save_version_stays_5() -> void:
	assert_eq(SaveServiceScript.SAVE_VERSION, 5, "WH-02 is additive: no version bump")


func test_an_old_v5_save_loads_every_theme_field_as_default() -> void:
	var data := _fixture()
	assert_false((data["campaign"] as Dictionary).has("corp_theme"), "written before WH-02")
	var c := CampaignState.from_dict(data["campaign"])
	var r := RunState.from_dict((data["run"] as Dictionary)["run"])
	assert_true(c.corp_theme.is_default())
	assert_true(r.corp_theme.is_default())
	assert_false(r.corp_theme.solace.enabled, "an old save loads the Bloom disabled (DORMANT)")
	assert_null(r.corp_theme.rebel_cell.hq_strike, "no HQ strike outside an HQ run")
	assert_eq(c.corp_theme.halcyon.eye_index, 0)
	assert_eq(c.corp_theme.raid.solace.infection_bp, 0)
	assert_eq(c.corp_theme.rebel_cell.lane_tag(&"any_site", &"STREET"), &"STREET")
	assert_eq(r.corp_theme.meridian.weigh_stations_passed.size(), 0)


func test_an_old_v5_save_hashes_as_the_pre_wh02_build_hashed_it() -> void:
	var data := _fixture()
	var h := _hashes()
	var c := CampaignState.from_dict(data["campaign"])
	var r := RunState.from_dict((data["run"] as Dictionary)["run"])
	assert_eq(c.state_hash(), int(h["campaign"]), "campaign hash unchanged at defaults")
	assert_eq(r.state_hash(), int(h["run"]), "run hash unchanged at defaults")
	assert_false(c.to_dict().has("corp_theme"))
	assert_false(r.to_dict().has("corp_theme"))


func test_a_non_default_field_changes_the_hash_and_joins_the_save() -> void:
	var data := _fixture()
	var cases: Array[Callable] = [
		func(c: CampaignState, _r: RunState) -> void: c.corp_theme.halcyon.eye_index = 3,
		func(c: CampaignState, _r: RunState) -> void: c.corp_theme.rebel_cell.lanes_scouted.append(&"ROOF"),
		func(c: CampaignState, _r: RunState) -> void: c.corp_theme.raid.solace.infection_bp = 500,
		func(_c: CampaignState, r: RunState) -> void: r.corp_theme.solace.front_milli = 1500,
		func(_c: CampaignState, r: RunState) -> void: r.corp_theme.orbital.lit_until_layer = 2,
		func(_c: CampaignState, r: RunState) -> void: r.corp_theme.meridian.capacity_bonus = -2,
		func(_c: CampaignState, r: RunState) -> void: r.corp_theme.rebel_cell.hq_strike = HqStrikeState.new(),
	]
	for i in cases.size():
		var c := CampaignState.from_dict(data["campaign"])
		var r := RunState.from_dict((data["run"] as Dictionary)["run"])
		var before := c.state_hash() + r.state_hash()
		cases[i].call(c, r)
		assert_ne(c.state_hash() + r.state_hash(), before, "case %d changes a hash" % i)
		assert_true(c.to_dict().has("corp_theme") or r.to_dict().has("corp_theme"), "case %d is saved" % i)


func test_setting_a_field_back_to_its_default_restores_the_hash() -> void:
	var r := RunState.new()
	var h := r.state_hash()
	r.corp_theme.halcyon.spotted_level = 2
	assert_ne(r.state_hash(), h)
	r.corp_theme.halcyon.spotted_level = 0
	assert_eq(r.state_hash(), h, "only non-default fields hash")


func test_every_theme_field_round_trips_the_save() -> void:
	var c := CampaignState.new()
	c.corp_theme.halcyon.eye_index = 5
	c.corp_theme.halcyon.eye_fixed_left = 2
	c.corp_theme.rebel_cell.lane_tags[&"site_b"] = &"SEWER"
	c.corp_theme.rebel_cell.lanes_scouted.assign([&"ROOF", &"SEWER"])
	c.corp_theme.raid.solace.infection_bp = 1250
	c.corp_theme.raid.rebel_cell.raid_arrival_step = 4
	c.corp_theme.raid.orbital.dark_nodes.assign([&"home", &"site_a"])
	var r := RunState.new()
	var b := r.corp_theme.solace
	b.front_milli = 2300
	b.layer_milli = 4000
	b.doses_taken = 1
	b.caught = true
	b.enabled = true
	b.doses_held = 2
	r.corp_theme.halcyon.spotted_level = 1
	r.corp_theme.halcyon.eye_phase = 6
	r.corp_theme.halcyon.eye_step = 9
	var hs := HqStrikeState.new()
	hs.lanes.append({"lane_id": "ROOF", "operative_id": "op_1", "layer": 3, "node_id": "n_3_1", "status": HqStrikeState.LaneStatus.ARMED})
	hs.graphs.append({"layers": 7})
	hs.phase = HqStrikeState.Phase.FINALE
	hs.focus_lane = 1
	r.corp_theme.rebel_cell.hq_strike = hs
	r.corp_theme.orbital.dark_nodes.assign([&"n_4_0"])
	r.corp_theme.orbital.lit_until_layer = 3
	r.corp_theme.meridian.capacity_bonus = -4
	r.corp_theme.meridian.weigh_stations_passed = PackedInt32Array([4, 7])
	var text := JSON.stringify({"version": SaveServiceScript.SAVE_VERSION, "campaign": c.to_dict(), "run": {"run": r.to_dict()}})
	var data: Dictionary = _saves.migrate(JSON.parse_string(text))
	var c2 := CampaignState.from_dict(data["campaign"])
	var r2 := RunState.from_dict((data["run"] as Dictionary)["run"])
	assert_eq(c2.state_hash(), c.state_hash())
	assert_eq(r2.state_hash(), r.state_hash())
	assert_eq(c2.corp_theme.halcyon.eye_index, 5)
	assert_eq(c2.corp_theme.rebel_cell.lane_tag(&"site_b", &"STREET"), &"SEWER")
	assert_eq(c2.corp_theme.rebel_cell.lane_tag(&"site_c", &"STREET"), &"STREET")
	assert_eq(c2.corp_theme.rebel_cell.lanes_scouted, [&"ROOF", &"SEWER"] as Array[StringName])
	assert_eq(c2.corp_theme.raid.orbital.dark_nodes, [&"home", &"site_a"] as Array[StringName])
	assert_eq(c2.corp_theme.raid.rebel_cell.raid_arrival_step, 4)
	var b2 := r2.corp_theme.solace
	assert_eq([b2.front_milli, b2.layer_milli, b2.doses_taken, b2.caught, b2.enabled, b2.doses_held], [2300, 4000, 1, true, true, 2])
	assert_eq(r2.corp_theme.halcyon.eye_step, 9)
	var hs2 := r2.corp_theme.rebel_cell.hq_strike
	assert_not_null(hs2)
	assert_eq(hs2.phase, HqStrikeState.Phase.FINALE)
	assert_eq(hs2.focus_lane, 1)
	assert_eq(hs2.lanes[0]["layer"], 3, "whole numbers read back as ints")
	assert_typeof(hs2.lanes[0]["layer"], TYPE_INT)
	assert_eq(r2.corp_theme.orbital.dark_nodes, [&"n_4_0"] as Array[StringName])
	assert_eq(r2.corp_theme.meridian.weigh_stations_passed, PackedInt32Array([4, 7]))
	assert_eq(r2.corp_theme.meridian.capacity_bonus, -4)


func test_an_empty_hq_strike_still_saves_as_present() -> void:
	var r := RunState.new()
	r.corp_theme.rebel_cell.hq_strike = HqStrikeState.new()
	var r2 := RunState.from_dict(JSON.parse_string(JSON.stringify(r.to_dict())))
	assert_not_null(r2.corp_theme.rebel_cell.hq_strike, "an HQ run's strike at its defaults survives the save")
	assert_eq(r2.corp_theme.rebel_cell.hq_strike.focus_lane, HqStrikeState.NO_FOCUS)


func test_a_resumed_netrun_keeps_its_theme_block() -> void:
	RunManager.save_slot = "gut_wh02"
	RunManager.scene_switching_enabled = false
	RunManager.reset()
	RunManager.new_campaign(7702)
	var s := RunManager.start_run()
	assert_not_null(s)
	s.run.corp_theme.solace.front_milli = 700
	RunManager.campaign.corp_theme.halcyon.eye_fixed_left = 1
	var run_hash := s.state_hash()
	var camp_hash := RunManager.campaign.state_hash()
	assert_eq(RunManager.autosave(), OK)
	RunManager.reset()
	assert_true(RunManager.resume())
	assert_eq(RunManager.netrun.run.corp_theme.solace.front_milli, 700)
	assert_eq(RunManager.campaign.corp_theme.halcyon.eye_fixed_left, 1)
	assert_eq(RunManager.netrun.state_hash(), run_hash)
	assert_eq(RunManager.campaign.state_hash(), camp_hash)
	assert_eq(RunManager.netrun.theme_chip(), {}, "no theme rule fills the chip yet")
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func test_the_config_section_carries_the_tables_defaults() -> void:
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	assert_eq(cfg.bloom_start_gap_milli_by_tier, PackedInt32Array([4000, 3500, 3000, 2500]))
	assert_eq(cfg.raid_infection_lost_bp, 10000)
	assert_eq(cfg.eye_step_deg, 45)
	assert_eq(cfg.blade_classes_l1, [&"ELITE", &"MINI_BOSS", &"RACK"] as Array[StringName])
	assert_eq(cfg.hq_lane_ids, [&"ROOF", &"STREET", &"SEWER"] as Array[StringName])
	assert_eq(cfg.lane_tag_default, &"STREET")
	assert_eq(int(cfg.hq_lane_node_weights[&"SEWER"][&"event"]), 40)
	assert_eq(cfg.street_dark_every, 3)
	assert_eq(cfg.meridian_capacity_tier_bonus, PackedInt32Array([2, 1, 1, 0]))
	assert_eq(cfg.meridian_jettison_value_daemon, 60)
