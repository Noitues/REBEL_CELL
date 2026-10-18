extends GutTest
## W0 SITENAMES: a Site is shown by its type; only the Central Server Site (the HQ building
## and the boss) keeps its name (designer 2026-10-16). SiteData.display_name stays as data.

const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_site_text"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RunManager.reset()


func test_every_shipped_site_shows_its_type_and_only_the_central_server_its_name() -> void:
	for corp_id in CORPS:
		var corp := RunManager.lookup().get_content(corp_id) as CorporationData
		assert_not_null(corp, str(corp_id))
		var named := 0
		for sd in corp.city_grid.sites:
			var text := SiteText.label(sd, corp.city_grid.home_site_id)
			assert_ne(text, "", "%s/%s has a label" % [corp_id, sd.id])
			if sd.objective == RC.SiteObjective.CENTRAL_SERVER:
				named += 1
				assert_eq(text, TextDb.t(sd, "display_name"), "%s: the Central Server keeps its name" % corp_id)
				assert_true(SiteText.is_named(sd))
			else:
				assert_ne(text, TextDb.t(sd, "display_name"), "%s/%s: no Site name" % [corp_id, sd.id])
				assert_false(SiteText.is_named(sd))
				assert_false(SiteText.tiered(sd, corp.city_grid.home_site_id).contains(sd.display_name), "%s/%s tiered" % [corp_id, sd.id])
		assert_eq(named, 1, "%s: one named Site (the boss's)" % corp_id)


func test_type_words_follow_the_objective() -> void:
	var s := SiteData.new()
	s.id = &"x"
	s.display_name = "Secret Name"
	assert_eq(SiteText.label(s), CityMapOverlay.kind_word(CityMapOverlay.KIND_TIER))
	s.objective = RC.SiteObjective.EXPLOIT
	s.exploit_type = RC.ExploitType.INTEL
	assert_eq(SiteText.label(s), CityMapOverlay.kind_word(CityMapOverlay.KIND_EXPLOIT))
	s.objective = RC.SiteObjective.HEAT_REDUCTION
	assert_eq(SiteText.label(s), CityMapOverlay.kind_word(CityMapOverlay.KIND_HEAT))
	assert_eq(SiteText.label(s, &"x"), CityMapOverlay.kind_word(CityMapOverlay.KIND_HOME), "the home Site")
	assert_eq(SiteText.label(null), "")


func test_grid_view_shows_no_site_name() -> void:
	RunManager.new_campaign(1)
	var corp := RunManager.corporation
	var c := RunManager.campaign
	var g := CityLayout.grid_graph(c, corp, [], &"")
	var mini: GridMapView = add_child_autofree(GridMapView.new())
	mini.size = Vector2(760, 380)
	mini.show_grid(c, corp)
	for n in g["nodes"]:
		var sd := CampaignRules.site_data(corp, n["id"])
		if sd == null or sd.objective == RC.SiteObjective.CENTRAL_SERVER:
			continue
		assert_false(String(n["tip"]).contains(sd.display_name), "%s: no name in the tip" % sd.id)
		assert_false(String(n["label"]).contains(sd.display_name), "%s: no name in the label" % sd.id)
		assert_false(mini.site_label(sd, false).contains(sd.display_name), "%s: no name in the mini-map" % sd.id)


func test_loot_header_names_tier_and_type_and_the_hq_building() -> void:
	RunManager.new_campaign(1)
	var corp := RunManager.corporation
	var plain := 0
	for sd in corp.city_grid.sites:
		if sd.id == corp.city_grid.home_site_id:
			continue  # the home Site is never run
		var word: String = load("res://scripts/ui/netrun_scene.gd").loot_site_word(sd.id)
		if SiteText.is_named(sd):
			assert_eq(word, SiteText.objective_word(sd).to_upper(), "the HQ run keeps the building's name")
		else:
			plain += 1
			assert_true(word.begins_with("T%d " % sd.tier), "%s: tier first (%s)" % [sd.id, word])
			assert_true(word.ends_with(SiteText.objective_word(sd, corp.city_grid.home_site_id).to_upper()), "%s: then the objective word (%s)" % [sd.id, word])
			assert_ne(word, "SITE", "never the bare SITE")
	assert_gt(plain, 0)


func test_objective_word_names_the_objective_with_the_tier() -> void:
	var s := SiteData.new()
	s.id = &"x"
	s.tier = 1
	s.display_name = "Secret Name"
	assert_eq(SiteText.tiered_objective(s), "T1 %s" % CityMapOverlay.kind_word(CityMapOverlay.KIND_TIER), "no objective: the Site word")
	s.objective = RC.SiteObjective.EXPLOIT
	assert_eq(SiteText.objective_word(s), CityMapOverlay.kind_word(CityMapOverlay.KIND_EXPLOIT))
	s.objective = RC.SiteObjective.HEAT_REDUCTION
	assert_eq(SiteText.tiered_objective(s).to_upper(), "T1 HEAT SINK", "a Heat Site is a heat sink, never its type word")
	assert_eq(SiteText.objective_word(s, &"x"), CityMapOverlay.kind_word(CityMapOverlay.KIND_HOME), "the home Site keeps its name")
	s.objective = RC.SiteObjective.CENTRAL_SERVER
	assert_eq(SiteText.tiered_objective(s), SiteText.label(s), "the named Site keeps its name")
	assert_eq(SiteText.objective_word(null), "")
