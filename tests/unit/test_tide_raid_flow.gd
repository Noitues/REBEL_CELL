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


func _action(acts: Array, kind: String, site: StringName = &"") -> Dictionary:
	for a in acts:
		if a["kind"] == kind and (site == &"" or a["site"] == site):
			return a
	return {}


func test_the_hq_step_lists_every_action_with_a_price_and_a_reason_when_it_cannot_be_taken() -> void:
	var env := _campaign()
	var c: CampaignState = env["c"]
	var f := _open(env)
	var acts := f.hq_actions([&"", "", false])
	for k in ["patch", "repair", "clean", "cool", "install"]:
		assert_false(_action(acts, k).is_empty(), "the %s action is listed" % k)
	assert_false(bool(_action(acts, "patch")["enabled"]), "HOME is full: no patch")
	assert_ne(String(_action(acts, "patch")["why"]), "", "and it says why")
	assert_false(bool(_action(acts, "repair")["enabled"]), "no district is DOWN")
	assert_ne(String(_action(acts, "repair")["why"]), "")
	assert_false(bool(_action(acts, "install")["enabled"]), "installing happens at the HQ map")
	# Damage HOME, take a district DOWN, cool the Cell down: now every action but install can be taken.
	var ring: Array = []
	for s in c.grid.sites.keys():
		if c.grid.is_claimed(s) and s != c.grid.home_site_id:
			ring.append(s)
	IdSort.sort_ids(ring)
	c.grid.site(ring[0])["condition"] = GridState.Condition.DOWN
	c.grid.home_integrity -= 6
	c.heat = 40
	c.schematics = 300
	acts = f.hq_actions([&"", "", false])
	assert_true(bool(_action(acts, "patch")["enabled"]))
	assert_eq(int(_action(acts, "patch")["points"]), 6)
	assert_true(bool(_action(acts, "repair", ring[0])["enabled"]))
	assert_eq(int(_action(acts, "repair", ring[0])["cost"]), SolaceTideRules.repair_cost(env["cfg"]))
	assert_true(bool(_action(acts, "cool")["enabled"]))
	assert_eq(int(_action(acts, "cool")["cost"]), SolaceTideRules.cool_price(SolaceTideCampaign.load_state(c, env["corp"], env["cfg"]), env["cfg"]))
	# Too few Schematics: the price is shown, the action is off and the reason names the need.
	c.schematics = SolaceTideRules.repair_cost(env["cfg"]) + 1
	acts = f.hq_actions([ring[0], "", false])
	assert_true(bool(_action(acts, "repair", ring[0])["picked"]))
	assert_false(bool(_action(acts, "cool")["enabled"]), "a repair and a cool do not both fit")
	assert_string_contains(String(_action(acts, "cool")["why"]), "Needs")
	assert_eq(f.hq_total([ring[0], "", false]), SolaceTideRules.repair_cost(env["cfg"]))
	# Every pick the screen can make is one the rules list as legal.
	c.schematics = 300
	var legal := f.hq_options()
	assert_true(legal.size() > 1)
	for o in legal:
		assert_true(f.hq_total(o) <= 300, "a legal option costs no more than the Cell holds")


func test_a_card_response_that_changes_nothing_folds_into_the_hold_row() -> void:
	var env := _campaign()
	var f := _open(env)
	f.advance()
	f.advance()
	f.to_forecast()
	if f.launch() == "confirm":
		f.launch()
	var opts := f.raid.response_options()
	var members := 0
	var hold_same := -1
	for g in f.groups:
		assert_false(bool(g["changes_nothing"]), "no row says 'changes nothing': it folds into HOLD")
		members += (g["members"] as Array).size()
		if g["members"][0]["head"] == TideRaidFlow.HOLD:
			hold_same = int(g["same"])
	assert_gte(hold_same, 0, "the HOLD row carries the count")
	assert_eq(members + hold_same, opts.size(), "every response is either a row or counted as the same as HOLD")


func test_the_raid_is_counted_from_one_and_decay_explains_the_infected_jump() -> void:
	var env := _campaign(0)
	var first := _open(env)
	assert_eq(first.raid_number(), 1, "the first raid is raid 1")
	assert_true(first.decay_tally.is_empty(), "nothing decays before the first raid")
	RunManager.reset()
	var env2 := _campaign(1)
	var c: CampaignState = env2["c"]
	var down: StringName = &""
	for s in c.grid.sites.keys():
		if c.grid.is_claimed(s) and s != c.grid.home_site_id:
			down = s
			break
	c.grid.site(down)["condition"] = GridState.Condition.DOWN
	var f := _open(env2)
	assert_eq(f.raid_number(), 2)
	assert_eq(int(f.decay_tally["taken"]), 1, "the DOWN district was TAKEN")
	assert_eq(f.decay_sites().size(), 1)
	assert_eq(f.decay_sites()[0], down)
	var t := f.infected_tally()
	assert_eq(int(t["after"]), int(f.hud_pre["infected"]))
	assert_eq(int(t["before"]) + int(f.decay_tally["taken"]) + (1 if bool(f.decay_tally["spread"]) else 0) - int(f.decay_tally["cured"]), int(t["after"]), "the tally adds up to the count the HUD shows")


func test_site_names_are_display_names_never_ids() -> void:
	var env := _campaign()
	var f := _open(env)
	var corp: CorporationData = env["corp"]
	for sd in corp.city_grid.sites:
		if sd == null or sd.id == corp.city_grid.home_site_id:
			continue
		var nm := f.site_name(sd.id)
		assert_ne(nm, String(sd.id), "%s is shown by its name" % sd.id)
		assert_false(nm.begins_with("T1 ") or nm.begins_with("T2 ") or nm.begins_with("T3 "), "never 'T1 Site': %s" % nm)


func test_the_loss_warning_shows_at_a_margin_of_one() -> void:
	var env := _campaign()
	var f := _open(env)
	var h := f.hud()
	assert_eq(f.loss_margin(h), int(h["healthy"]) - int(h["infected"]) + 1)
	assert_false(f.loss_warning() and int(h["infected"]) < int(h["healthy"]), "no warning while the city has room")
	var near := {"infected": 5, "healthy": 5}
	assert_eq(f.loss_margin(near), 1)
