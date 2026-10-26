extends GutTest
## Phase 3 (tier fast): the Solace tide raid screen in the real HQ scene, headless. A seeded Solace campaign with a raid pending
## opens the tide screen (not the resolver's pages); the screen goes DECAY, DRAW, PLAN, FORECAST, SEALED A, RESPONSE, the playout, the
## AFTERMATH and the HQ step by the player's presses, ending with the state the rules give; a resolver corporation still opens the
## resolver's raid setup. One flow test per screen (rule 6); the look is checked in the windowed captures.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _saved_slot: String
var _focus: StringName


func before_each() -> void:
	AudioDirector.muted = true
	_saved_slot = RunManager.save_slot
	_focus = RunManager.focus_corp_override
	RunManager.save_slot = "gut_tide_screen"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RaidModelFixture.restore()
	RunManager.focus_corp_override = _focus
	Dialogue.clear()
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = _saved_slot
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _own_three(c: CampaignState) -> void:
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var ring: Array[StringName] = []
	for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
		ring.append(l)
	ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ring.slice(0, 3):
		var run := RunState.new()
		run.site_id = id
		CampaignRules.on_run_completed(c, corp, cfg, run)
		CampaignRules.claim(c, corp, cfg, RunManager.lookup(), id, &"relay")
	c.pending_raids.clear()


func test_a_solace_raid_plays_on_the_tide_screen_to_the_hq_step() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	assert_true(CampaignRules.uses_tide(RunManager.corporation))
	_own_three(c)
	c.schematics = 300
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})
	var hq := _scene()
	await _frames()
	hq.show_raid()
	await _frames()
	assert_eq(hq.panel_name, "raid_tide", "a Solace raid opens the tide screen")
	var screen: TideRaidScreen = hq.tide_screen
	assert_not_null(screen)
	var flow: TideRaidFlow = screen.flow
	assert_not_null(screen.layer, "the raid lines are drawn on the city")
	assert_eq(flow.phase, TideRaidFlow.Phase.DECAY)
	screen.cont()
	assert_eq(flow.phase, TideRaidFlow.Phase.DRAW)
	screen.cont()
	assert_eq(flow.phase, TideRaidFlow.Phase.PLAN)
	assert_gt(screen.hand_row.get_child_count(), 0, "the hand row shows the cards")
	# Pick a card by the press the player makes, then a Site on a line.
	var sites := flow.placeable_sites()
	var picked := ""
	for h in flow.hand_cards():
		if SolaceTideRules.PLACEABLE.has(h["verb"]):
			picked = h["id"]
			break
	if picked != "" and not sites.is_empty():
		screen.card_pressed(picked)
		assert_eq(flow.sel_card, picked)
		screen.site_clicked(sites[0])
		assert_true((flow.raid.place["sentries"] as Dictionary).has(sites[0]), "the card stands on the Site")
		assert_true(flow.place_is_legal())
		assert_true(screen.layer.sentries.has(sites[0]), "the sentry is drawn on the city")
	screen.to_forecast()
	assert_eq(flow.phase, TideRaidFlow.Phase.FORECAST)
	assert_eq(flow.forecast().size(), 12)
	screen.launch()
	if flow.phase == TideRaidFlow.Phase.FORECAST:
		screen.launch()
	assert_true(flow.phase in [TideRaidFlow.Phase.REVEAL, TideRaidFlow.Phase.RESPONSE, TideRaidFlow.Phase.PLAYOUT, TideRaidFlow.Phase.AFTERMATH])
	if flow.phase == TideRaidFlow.Phase.REVEAL:
		flow.reveal_done()
		screen._rebuild()
	if flow.phase == TideRaidFlow.Phase.RESPONSE:
		assert_gt(flow.groups.size(), 0, "the response rows are listed")
		screen.select_group(0)
		screen.commit()
		if flow.phase == TideRaidFlow.Phase.RESPONSE:
			screen.commit()  # the HOLD confirm
	await _frames()
	assert_true(flow.phase in [TideRaidFlow.Phase.AFTERMATH, TideRaidFlow.Phase.PLAYOUT])
	assert_true(c.pending_raids.is_empty(), "the raid resolved")
	assert_false(flow.raid.rewind(), "no undo after the resolve")
	assert_eq(String(flow.aftermath()["tier"]), String(c.last_raid["tier"]))
	if flow.phase == TideRaidFlow.Phase.PLAYOUT:
		flow.playout_done()
		screen._rebuild()
	screen.cont()
	if flow.phase == TideRaidFlow.Phase.HQ_STEP:
		screen.done_hq()
	assert_eq(flow.phase, TideRaidFlow.Phase.DONE)


func test_a_resolver_corporation_still_opens_the_resolver_raid_setup() -> void:
	RaidModelFixture.use_resolver()  # Solace as the resolver's carrier: the other corporations are locked on a fresh profile
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	assert_false(CampaignRules.uses_tide(RunManager.corporation))
	c.schematics = 300
	var open := CampaignRules.launchable_sites(c, RunManager.corporation, RunManager.config())
	var run := RunState.new()
	run.site_id = open[0].id
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), run)
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), open[0].id, &"relay")
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
	var hq := _scene()
	await _frames()
	hq.show_raid()
	await _frames()
	assert_ne(hq.panel_name, "raid_tide", "the resolver raid keeps its screens")
	assert_false(hq.tide_raid_pending())
	RaidModelFixture.restore()
