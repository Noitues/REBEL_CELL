extends GutTest
## Plan 2 NA-12 (D3), fast tier: the campaign's city seed. A new campaign stores a city seed
## drawn from its campaign seed's own stream (no saved stream advances); the save carries it as
## a u64 decimal string (save v5) and a resumed campaign regenerates the identical city (plan,
## map look); a v4 campaign save is refused cleanly while a v4 profile still reads; the bake
## cache key changes with the city seed and is stable otherwise.

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")

var _saves: Node


func before_each() -> void:
	_saves = autofree(SaveServiceScript.new())
	RunManager.save_slot = "gut_city_seed"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func test_city_seed_is_a_pure_64_bit_draw_of_the_campaign_seed() -> void:
	assert_eq(CampaignRules.city_seed_for(31), CampaignRules.city_seed_for(31), "deterministic")
	assert_ne(CampaignRules.city_seed_for(31), CampaignRules.city_seed_for(32), "per campaign")
	var wide := false
	for s in 20:
		var c := CampaignRules.city_seed_for(s)
		assert_ne(c, 0, "0 is the fixed city, never drawn")
		if c > 0xFFFFFFFF or c < 0:
			wide = true
	assert_true(wide, "64 bits, not 32")


func test_a_new_campaign_stores_its_city_seed_and_advances_no_stream() -> void:
	RngService.seed_campaign(4401)
	var fresh := JSON.stringify(RngService.to_dict(), "", true)
	var c := RunManager.new_campaign(4401)
	assert_eq(c.city_seed, CampaignRules.city_seed_for(4401))
	assert_eq(JSON.stringify(RngService.to_dict(), "", true), fresh, "the saved streams are as freshly seeded")
	assert_eq(CityPlan.current_seed(), c.city_seed, "the maps read the campaign's city")
	assert_eq(CityPlan.current().city_seed, c.city_seed, "the campaign's own city")
	assert_eq(NeonCity.hq_of(&"halcyon"), CityPlan.current().hq_of(&"halcyon"), "HQs come from the campaign's city")


func test_the_save_round_trips_the_city_seed_as_a_u64_string() -> void:
	var c := CampaignState.new()
	c.city_seed = -6917529027641081856  # the u64 0xA000000000000000
	var d := c.to_dict()
	assert_eq(d["city_seed"], "11529215046068469760")
	var text := JSON.stringify({"version": SaveServiceScript.SAVE_VERSION, "campaign": d})
	var back := CampaignState.from_dict((JSON.parse_string(text) as Dictionary)["campaign"])
	assert_eq(back.city_seed, c.city_seed)


func test_a_resumed_campaign_regenerates_the_identical_city() -> void:
	var c := RunManager.new_campaign(4402)
	var seed_v := c.city_seed
	var plan := JSON.stringify(CityPlan.current().to_dict(), "", true)
	var cfg: CampaignConfigData = load(CityPlan.FIXED_CONFIG_PATH)
	var city: NeonCity = autofree(NeonCity.new())
	var key := city.look_key()
	assert_eq(RunManager.autosave(), OK)
	RunManager.reset()
	assert_eq(CityPlan.current_seed(), CityPlan.default_seed(), "no campaign: the default city")
	assert_true(RunManager.resume(), "resumed")
	assert_eq(RunManager.campaign.city_seed, seed_v)
	assert_eq(JSON.stringify(CityPlan.current().to_dict(), "", true), plan, "the same city")
	assert_eq(JSON.stringify(CityPlan.generate(seed_v, cfg).to_dict(), "", true), plan, "regenerated from the seed alone")
	var again: NeonCity = autofree(NeonCity.new())
	assert_eq(again.look_key(), key, "the same baked look")


func test_a_v4_campaign_save_is_refused_and_a_v4_profile_still_reads() -> void:
	assert_eq(SaveServiceScript.SAVE_VERSION, 5)
	var old := {"version": 4, "corporation_id": "solace", "campaign": {"heat": 5, "campaign_seed": "7"}}
	assert_eq(_saves.migrate(old), {})
	assert_eq(_saves.last_error, SaveMigration.ERR_NO_CITY_SEED)
	assert_push_error(SaveMigration.ERR_NO_CITY_SEED)
	var prof: Dictionary = _saves.migrate({"version": 4, "profile": {"campaigns_started": 3}})
	assert_eq(int(prof["version"]), 5, "a profile reads on")
	assert_eq(int(prof["profile"]["campaigns_started"]), 3)
	var ok: Dictionary = _saves.migrate({"version": 5, "campaign": {"city_seed": "12"}})
	assert_false(ok.is_empty(), "a v5 campaign loads")
	assert_eq(_saves.migrate({"version": 5, "campaign": {"city_seed": 12}}), {}, "the seed is a string")
	assert_push_error(SaveMigration.ERR_NO_CITY_SEED)


func test_the_bake_key_changes_with_the_city_seed_only() -> void:
	var a: NeonCity = autofree(NeonCity.new())
	var b: NeonCity = autofree(NeonCity.new())
	assert_eq(a.look_key(), b.look_key(), "one seed, one key")
	b.city_seed = CampaignRules.city_seed_for(5)
	assert_ne(a.look_key(), b.look_key(), "another city, another key")
	a.city_seed = b.city_seed
	assert_eq(a.look_key(), b.look_key(), "stable for the seed")
