extends GutTest
## Six written Solace story paths (GDD 8.4) and the text externalisation pipeline
## (GDD 10): every content string has a stable key, the export collects them, and
## TextDb prefers a loaded translation over the content's own text.

var _corp: CorporationData
var _lookup: ContentLookup


func before_all() -> void:
	_corp = ContentRegistry.get_content(&"solace") as CorporationData
	_lookup = GridFixture.lookup()


func test_six_written_paths_with_bonus_beats_and_finales() -> void:
	assert_eq(_corp.story_paths.size(), 6)
	var titles := {}
	for p in _corp.story_paths:
		titles[p.title] = true
		assert_eq(p.beats.size(), 3, p.title)
		assert_eq(p.bonus_beats.size(), 2, p.title)
		assert_not_null(p.finale, p.title)
		assert_false(p.premise.contains("Placeholder"), p.title)
		for b in p.beats + p.bonus_beats + [p.finale]:
			assert_false(b.text.contains("Placeholder"), b.id)
			assert_true(b.text.length() > 60, "%s is written" % b.id)
	for t in ["Recall Notice", "Clinical Trial", "Terms of Service", "The Cure", "Ghost Patient", "Hostile Takeover"]:
		assert_true(titles.has(t), t)
	var ghost: StoryPathData = null
	var takeover: StoryPathData = null
	for p in _corp.story_paths:
		if p.id == &"sp_ghost_patient":
			ghost = p
		if p.id == &"sp_hostile_takeover":
			takeover = p
	assert_eq(ghost.foreshadows, &"dispatch")
	assert_true(ghost.beats[1].triggers_raid, "Ghost Patient II triggers the story raid")
	for b in ghost.beats:
		assert_true(b.dispatch_clue)
	assert_eq(takeover.foreshadows, &"meridian", "Hostile Takeover foreshadows the second corporation")
	# Bonus beats reveal with extra Exploits; the finale on the win.
	var cfg := CombatFixture.config()
	var c := CampaignRules.new_campaign(_corp, cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	c.story_path_id = &"sp_the_cure"
	c.story_beats_revealed = 4
	assert_eq(CampaignRules.revealed_beats(c, _corp).size(), 4)
	assert_eq(CampaignRules.revealed_beats(c, _corp)[3].id, &"the_cure_bonus_1")
	c.outcome = CampaignState.Outcome.WON
	assert_eq(CampaignRules.revealed_beats(c, _corp)[4].id, &"the_cure_f")


func test_text_keys_are_stable_and_the_export_collects_every_string() -> void:
	var jolt := _lookup.get_content(&"jolt") as CardData
	assert_eq(TextDb.key_for(jolt, "description"), "CardData.jolt.description")
	assert_eq(TextDb.t(jolt, "description"), jolt.description, "no translation: the content's own text")
	var rows := TextDb.collect(_lookup)
	assert_true(rows.size() > 300, "%d strings collected" % rows.size())
	var keys := {}
	for r in rows:
		assert_false(keys.has(r[0]), "duplicate key %s" % r[0])
		keys[r[0]] = true
	assert_true(keys.has("CardData.jolt.description"))
	assert_true(keys.has("SiteData.t1_a.display_name"))
	assert_true(keys.has("VoiceLineData." + "dispatch_solace" + ".id") == false, "voice lines key by their set")
	assert_true(FileAccess.file_exists("res://assets/text/strings.csv"), "the export ran (tools/export_text.gd)")


func test_a_loaded_translation_wins_over_the_content_text() -> void:
	var jolt := _lookup.get_content(&"jolt") as CardData
	var tr := Translation.new()
	tr.locale = "xx"
	tr.add_message("CardData.jolt.description", "Faire tourner la roue de 3 crans.")
	TranslationServer.add_translation(tr)
	var before := TranslationServer.get_locale()
	TranslationServer.set_locale("xx")
	assert_eq(TextDb.t(jolt, "description"), "Faire tourner la roue de 3 crans.")
	assert_eq(TextDb.ui("ui.nothing", "fallback"), "fallback")
	TranslationServer.set_locale(before)
	TranslationServer.remove_translation(tr)
	assert_eq(TextDb.t(jolt, "description"), jolt.description)
	assert_true(Settings.available_languages().has("en"))
