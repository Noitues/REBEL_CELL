extends GutTest
## Phase 3 (tier fast): the Solace Infected Tide raid flow (TideRaidFlow) over SolaceTideRaid. A seeded Solace campaign opens a
## raid, places a card, picks a response, resolves, reaches the aftermath and the HQ step, with the state equal to what
## SolaceTideRaid.resolve gives on a copy; the checkpoint (no undo after the resolve); a resolver corporation never opens it.

var _saved_slot: String


func before_each() -> void:
	AudioDirector.muted = true
	_saved_slot = RunManager.save_slot
	RunManager.save_slot = "gut_tide_flow"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RaidModelFixture.restore()
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = _saved_slot
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false


func _campaign(raids_done: int = 0) -> Dictionary:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	c.schematics = 300
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
	c.raids_won = raids_done
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})
	return {"c": c, "corp": corp, "cfg": cfg}


func _open(env: Dictionary) -> TideRaidFlow:
	return TideRaidFlow.open(env["c"], env["corp"], env["cfg"], RunManager.pending_raid())


func test_a_resolver_corporation_does_not_open_the_tide_flow() -> void:
	RaidModelFixture.use_resolver()  # Solace as the resolver's carrier
	RunManager.new_campaign(3)
	assert_null(TideRaidFlow.open(RunManager.campaign, RunManager.corporation, RunManager.config(), {}))
	RaidModelFixture.restore()


func test_a_full_raid_reaches_the_aftermath_and_the_state_equals_the_rules() -> void:
	var env := _campaign()
	var c: CampaignState = env["c"]
	var f := _open(env)
	assert_not_null(f)
	assert_eq(f.phase, TideRaidFlow.Phase.DECAY)
	f.advance()
	assert_eq(f.phase, TideRaidFlow.Phase.DRAW)
	assert_false(f.hand_cards().is_empty(), "the hand is dealt")
	f.advance()
	assert_eq(f.phase, TideRaidFlow.Phase.PLAN)
	var sites := f.placeable_sites()
	if not sites.is_empty():
		for h in f.hand_cards():
			if SolaceTideRules.PLACEABLE.has(h["verb"]):
				assert_true(f.pick_card(h["id"]))
				assert_eq(f.place_on(sites[0]), "")
				break
		assert_true(f.place_is_legal(), "the placement is one the rules list")
		assert_true(f.can_undo())
	assert_true(f.to_forecast())
	assert_eq(f.forecast().size(), 12)
	assert_true(f.guard().has("hold"))
	var go := f.launch()
	if go == "confirm":
		go = f.launch()
	assert_eq(go, "launched")
	f.reveal_done()
	# The reference: the same setup resolved by the rules on a copy of the campaign.
	var copy := c.duplicate_state()
	var ref := SolaceTideRaid.open(copy, env["corp"], env["cfg"], copy.pending_raids[0])
	ref.place = f.raid.place
	ref.resp = [TideRaidFlow.HOLD]
	ref.resolve()
	assert_eq(f.commit([TideRaidFlow.HOLD], true), "committed")
	assert_eq(f.phase, TideRaidFlow.Phase.PLAYOUT)
	assert_true(c.pending_raids.is_empty(), "the pending raid is consumed")
	assert_eq(c.heat, copy.heat, "Heat equals the rules' result")
	assert_eq(c.grid.home_integrity, copy.grid.home_integrity, "HOME equals the rules' result")
	assert_eq(String(c.last_raid["tier"]), String(copy.last_raid["tier"]))
	assert_eq(c.corp_theme.solace.tide.deck.size(), copy.corp_theme.solace.tide.deck.size())
	assert_false(f.raid.rewind(), "nothing rewinds after the resolve")
	assert_false(f.beats().is_empty())
	f.playout_done()
	assert_eq(f.phase, TideRaidFlow.Phase.AFTERMATH)
	assert_eq(String(f.aftermath()["tier"]), String(copy.last_raid["tier"]))
	f.advance()
	if f.phase == TideRaidFlow.Phase.HQ_STEP:
		var opts := f.hq_options()
		assert_false(opts.is_empty())
		f.apply_hq_step(opts[0])
		assert_eq(f.phase, TideRaidFlow.Phase.DONE)


func test_undo_works_before_the_launch_and_the_forecast_equals_the_resolve() -> void:
	var env := _campaign()
	var f := _open(env)
	f.advance()
	f.advance()
	var before: Dictionary = f.raid.place.duplicate(true)
	assert_true(f.toggle_ghost(), "the kit has a ghost")
	assert_ne(f.raid.place["ghost"], &"")
	assert_true(f.undo())
	assert_eq(f.raid.place, before)
	assert_false(f.undo(), "nothing left to undo at the start")
	f.to_forecast()
	var hunter := int(f.ctx().draw["hunter_real"])
	var real_tier := ""
	for r in f.forecast():
		if r["a"] == f.real_a() and r["hunter"] == hunter:
			real_tier = String(r["tier"])
	if f.launch() == "confirm":
		f.launch()
	f.reveal_done()
	f.commit([TideRaidFlow.HOLD], true)
	assert_eq(String(RunManager.campaign.last_raid["tier"]), real_tier, "the forecast row of the real outcome is the result")


func test_decay_that_ends_the_campaign_closes_the_raid_as_city_lost() -> void:
	var env := _campaign(1)
	var c: CampaignState = env["c"]
	var tide := c.corp_theme.solace.tide
	# Many INFECTED cards: after DECAY they outnumber the healthy ones.
	var ids: Array = []
	for i in 12:
		ids.append(&"t1_a")
	SolaceTideRules.add_infected(tide, ids, false)
	var f := _open(env)
	assert_true(f.raid.over, "DECAY ended the campaign")
	f.advance()
	assert_eq(f.phase, TideRaidFlow.Phase.AFTERMATH)
	assert_true(c.pending_raids.is_empty(), "the raid is consumed")
	assert_true(c.is_over())
	assert_eq(String(f.aftermath()["tier"]), "CITY LOST")
	assert_eq(String(f.aftermath()["banner"]), "CITY LOST")
	f.advance()
	assert_eq(f.phase, TideRaidFlow.Phase.DONE, "a lost campaign has no HQ step")


func test_the_guard_the_hold_confirm_and_the_fast_resolve_follow_the_forecast() -> void:
	var env := _campaign()
	var f := _open(env)
	f.advance()
	f.advance()
	f.to_forecast()
	var hold_rows := f.forecast()
	assert_eq(String(f.guard()["hold"]), String(f.tier_range(hold_rows)[0]), "the guard's HOLD tier is the forecast's worst")
	if f.launch() == "confirm":
		f.launch()
	var tiers := {}
	for g in f.groups:
		for m in g["members"]:
			for r in SolaceTideRules.forecast(f.ctx(), f.raid.st, f.raid.place, m["resp"]):
				tiers[r["tier"]] = true
	assert_eq(f.fast, tiers.size() <= 1, "fast resolve only when every row gives one tier everywhere")
	var worse := f.hold_worse_group()
	f.reveal_done()
	if not f.fast and worse >= 0:
		assert_eq(f.commit([TideRaidFlow.HOLD]), "confirm", "HOLD that loses HOME some row saves asks first")
		assert_eq(f.commit([TideRaidFlow.HOLD]), "committed")
	else:
		assert_eq(f.commit([TideRaidFlow.HOLD]), "committed")
	assert_eq(f.commit([TideRaidFlow.HOLD], true), "no", "a second commit after the resolve is refused")
