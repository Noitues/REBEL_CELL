extends GutTest
## Change plan 1 V4: tools/agent/make_boss_save.gd writes the stopped campaign through the game's
## save path; the game's loader reads it back to the same campaign (round trip), on a one-run
## fixture (the 60-run play to the breach is not run here).

const BossStopSimulator := preload("res://tools/agent/boss_stop_simulator.gd")
const HeuristicStrategist := preload("res://tools/agent/heuristic_strategist.gd")

var _dir: String = "user://boss_save_test_%d" % OS.get_process_id()


func after_each() -> void:
	SaveService._remove_tree(_dir)


func test_written_save_loads_back_to_the_same_campaign() -> void:
	var resolver := CombatFixture.resolver()
	var sim = BossStopSimulator.new(resolver, "", [])
	sim.strategist = HeuristicStrategist.new(HeuristicStrategistConfigData.shipped(), resolver.lookup)
	sim.run_campaign(1000, 0, 1)
	assert_false(sim.reached_breach, "one run is far from the breach")
	assert_not_null(sim.final_campaign, "the campaign at the stop is kept")
	var c: CampaignState = sim.final_campaign
	assert_eq(BossSaveWriter.write(SaveService, RngService, c, _dir, "7"), OK)
	var path: String = _dir.path_join(SaveService.CAMPAIGN_FILE_FORMAT % "7")
	assert_true(SaveService.has_save(path))
	var data := SaveService.load_dict(path)
	assert_false(data.is_empty(), "the loader accepts the file (version stamp)")
	assert_eq(String(data["corporation_id"]), String(c.corporation_id))
	assert_true((data["run"] as Dictionary).is_empty(), "saved between runs")
	var back := CampaignState.from_dict(data["campaign"])
	assert_eq(back.state_hash(), c.state_hash(), "round trip: same campaign")
	var profile := SaveService.load_dict(_dir.path_join(SaveService.PROFILE_FILE))
	assert_eq(profile["slots"], ["7"], "the profile lists the slot")
	assert_string_contains(BossSaveWriter.summary(c), "seed 1000")
