extends GutTest
## LOOK Solace Bloom A (A-096), build's two calls: the street netrun page and the Solace HQ run page put `BloomLook.from_state` of the run's
## Bloom on their city view. Solace (Bloom enabled) gives a non-off look, another corporation an off look; look only (headless: the
## looks the views hold, nothing renders).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCRIPT := preload("res://scripts/ui/netrun_scene.gd")
const HQ_TIER := 4

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _breach(corp_id: StringName) -> NetrunSession:
	var corp := ContentRegistry.get_content(corp_id) as CorporationData
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	return NetrunSession.start_special(_resolver, c, c.roster[0].id, "boss", &"the_genome_core", HQ_TIER, 7,
		corp.final_boss.id, CampaignRules.boss_overrides(c, corp), corp)


func _hq_look(corp_id: StringName, decision: bool) -> Dictionary:
	var s := _breach(corp_id)
	var v := HqRunView.new()
	v.size = Vector2(1920, 1080)
	add_child_autofree(v)
	v.show_run(corp_id, s.run.map, s.run.current_node_id, s.run.visited, s.available_nodes(), "THE CORE")
	return v.set_bloom(s.run.corp_theme.solace, s.config, decision)


func test_the_solace_hq_page_carries_the_bloom_and_another_corp_does_not() -> void:
	var on := _hq_look(&"solace", true)
	assert_eq(on["kind"], BloomLook.KIND_HQ)
	assert_gt(float(on["strength"]), 0.0, "Solace: the Bloom look is on")
	var over := _hq_look(&"solace", false)
	assert_gt(float(over["strength"]), 0.0, "Solace overview: on")
	assert_gt(float(on["front"]), float(over["front"]), "the decision shot lifts the front above the overview")
	var off := _hq_look(&"meridian", true)
	assert_eq(float(off["strength"]), 0.0, "another corporation: off")


func _scene_for(corp_id: StringName) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.focus_corp_override = corp_id
	var u := CampaignRules.unlock_for(RunManager.lookup(), ContentRegistry.get_content(corp_id))
	if u != null:
		RunManager.profile.add_unlock(u.id)
	RunManager.new_campaign(1, corp_id)
	scene.start_run(1)
	await get_tree().process_frame
	await get_tree().process_frame
	return scene


func before_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_bloom_wiring"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()
	SCRIPT.force_street_error = ""


func after_each() -> void:
	SCRIPT.force_street_error = ""
	CityBakeCache.shutdown()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.focus_corp_override = &""
	RunManager.scene_switching_enabled = true


func test_the_solace_street_page_carries_the_bloom() -> void:
	var scene := await _scene_for(&"solace")
	var v: StreetRouteView = scene.street_view
	assert_not_null(v, "the street page is mounted")
	var b: BloomState = RunManager.netrun.run.corp_theme.solace
	assert_true(b.enabled, "a Solace netrun runs the Bloom")
	assert_eq(v.bloom["kind"], BloomLook.KIND_STREET)
	assert_gt(float(v.bloom["strength"]), 0.0, "Solace: the Bloom look is on the street")
	assert_eq(v.rig.view.bloom_look(), v.bloom, "the city view holds the look the page set")


func test_another_corp_street_page_is_off() -> void:
	var scene := await _scene_for(&"meridian")
	var v: StreetRouteView = scene.street_view
	assert_not_null(v, "the street page is mounted")
	assert_false(RunManager.netrun.run.corp_theme.solace.enabled)
	assert_eq(float(v.bloom["strength"]), 0.0, "another corporation: off")
