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


func test_infected_over_healthy_after_decay_plays_the_raid_then_city_lost() -> void:
	var env := _campaign(1)
	var c: CampaignState = env["c"]
	var tide := c.corp_theme.solace.tide
	# Many INFECTED cards: after DECAY they outnumber the healthy ones. R-I (2026-10-26): the raid is still played and
	# CITY LOST is checked when it resolves, after the response.
	var ids: Array = []
	for i in 12:
		ids.append(&"t1_a")
	SolaceTideRules.add_infected(tide, ids, false)
	var f := _open(env)
	assert_false(f.raid.over, "R-I: DECAY does not end the campaign")
	assert_false(c.is_over())
	assert_eq(SolaceTideRules.loss_margin(f.raid.st), 0, "the PLAN can warn: the city falls at the raid's end")
	f.advance()
	f.advance()
	assert_eq(f.phase, TideRaidFlow.Phase.PLAN, "the raid is played")
	assert_true(f.to_forecast())
	if f.launch() == "confirm":
		f.launch()
	f.reveal_done()
	assert_eq(f.commit([TideRaidFlow.HOLD], true), "committed")
	f.playout_done()
	assert_eq(f.phase, TideRaidFlow.Phase.AFTERMATH)
	assert_true(c.pending_raids.is_empty(), "the raid is consumed")
	assert_true(c.is_over())
	assert_eq(String(f.aftermath()["lost"]), SolaceTideState.LOST_CITY, "lost at the close (HOME stands)")
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
	var near := {"infected": 5, "healthy": 5, "margin": 1}
	assert_eq(f.loss_margin(near), 1, "the flow reads the margin from the HUD snapshot")


# ------------------------------------------------------------------------------------------------ Phase 3c
## A campaign for the 3c rules: `heat`, `downs` districts DOWN, and with `margin_one` the INFECTED count one card short of the line.
func _env(seed_: int, raids_done: int, heat: int = 80, downs: int = 1, margin_one: bool = false) -> Dictionary:
	RunManager.reset()
	RunManager.new_campaign(seed_)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	c.schematics = 300
	var ring: Array[StringName] = []
	for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
		ring.append(l)
	ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ring.slice(0, 4):
		var run := RunState.new()
		run.site_id = id
		CampaignRules.on_run_completed(c, corp, cfg, run)
		CampaignRules.claim(c, corp, cfg, RunManager.lookup(), id, &"relay")
	c.pending_raids.clear()
	c.heat = heat
	c.raids_won = raids_done
	c.raids_lost = 0
	for i in downs:
		c.grid.site(ring[i])["condition"] = GridState.Condition.DOWN
	if margin_one:
		var st := SolaceTideCampaign.load_state(c, corp, cfg)
		var healthy := st.deck.size() - st.wound_count()
		var ids: Array = []
		for i in healthy - st.wound_count() - downs:
			ids.append(ring[1 + i % 3])
		SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})
	return {"c": c, "corp": corp, "cfg": cfg}


## Plays the flow to the RESPONSE: up to two GUARD cards on the first free Sites, the ghost when asked, the launch (confirmed) and the reveal.
func _to_response(env: Dictionary, ghost: bool = false) -> TideRaidFlow:
	var f := _open(env)
	f.advance()
	f.advance()
	var placed := 0
	for h in f.hand_cards():
		var sites := f.placeable_sites()
		if placed >= 2 or sites.is_empty():
			break
		if h["verb"] == "GUARD":
			f.pick_card(h["id"])
			f.place_on(sites[0])
			placed += 1
	if ghost:
		f.toggle_ghost()
	f.to_forecast()
	if f.launch() == "confirm":
		f.launch()
	f.reveal_done()
	return f


func test_a_rows_heat_and_infected_change_are_what_the_resolve_gives() -> void:
	for sd in [7, 11, 23]:
		for pick in [0, 1]:
			var f := _to_response(_env(sd, 1, 80, 1), sd == 11)
			var g: Dictionary = f.groups[mini(pick, f.groups.size() - 1)]
			var m: Dictionary = g["members"][0]
			var real := f.real_row(m["resp"])
			var ns: SolaceTideState = real["result"]["state"]
			var heat_before := f.raid.st.heat
			var inf_before := f.raid.st.wound_count()
			assert_true(int(m["heat_lo"]) <= ns.heat - heat_before and ns.heat - heat_before <= int(m["heat_hi"]), "the row's Heat range holds the real outcome (seed %d)" % sd)
			assert_true(int(m["inf_lo"]) <= ns.wound_count() - inf_before and ns.wound_count() - inf_before <= int(m["inf_hi"]), "and so does its INFECTED range")
			f.commit(m["resp"], true)
			assert_eq(int(f.last_raid["heat_delta"]), ns.heat - heat_before, "the real Heat change is the preview's (seed %d, row %d)" % [sd, pick])
			assert_eq(int(f.last_raid["infected"]) - inf_before, ns.wound_count() - inf_before, "the real INFECTED change is the preview's")


func test_the_pending_heat_in_plan_is_the_heat_a_hold_leaves() -> void:
	for ghost in [false, true]:
		var env := _env(7, 1, 80, 1)
		var f := _open(env)
		f.advance()
		f.advance()
		if ghost:
			assert_true(f.toggle_ghost())
		f.to_forecast()
		var p := f.pending_heat()
		assert_eq(int(p["now"]), 80)
		if ghost:
			assert_gte(int(p["lo"]), 80 + int(env["cfg"].solace_tide_ghost_heat), "the ghost's Heat is in the header's number")
		if f.launch() == "confirm":
			f.launch()
		f.reveal_done()
		f.commit([TideRaidFlow.HOLD], true)
		var heat: int = (env["c"] as CampaignState).heat
		assert_true(int(p["lo"]) <= heat and heat <= int(p["hi"]), "the Heat after the raid is inside the pending range (ghost %s)" % ghost)


func test_every_response_row_has_the_card_it_names() -> void:
	for sd in [7, 3, 11, 19, 31]:
		var f := _to_response(_env(sd, 1, 80, 2), sd == 3)
		var cards := f.hand_cards()
		for g in f.groups:
			for m in g["members"]:
				var r: Array = m["resp"]
				var need := f.resp_need(r)
				assert_true(bool(need["have"]), "%s has its card (seed %d)" % [f.resp_label_long(r), sd])
				var ok := false
				for c in cards:
					if c["site"] != "" or c["verb"] == "WOUND":
						continue
					match String(r[0]):
						"DEPLOY":
							ok = ok or c["type"] == String(r[1])
						"REDEPLOY", "DIVERT":
							ok = ok or c["verb"] == "SHIFT"
						"JAM", "JAM_B":
							ok = ok or c["verb"] == "JAM"
						_:
							ok = true
				assert_true(ok, "a card in hand backs %s (seed %d)" % [r[0], sd])


func test_response_rows_are_unique() -> void:
	var divert_seen := 0
	for sd in [7, 3, 11, 19, 31]:
		var f := _to_response(_env(sd, 1, 80, 2), true)
		var seen := {}
		for g in f.groups:
			var lab := String(g["label"])
			assert_false(seen.has(lab), "'%s' is listed once (seed %d)" % [lab, sd])
			seen[lab] = true
			if String(g["members"][0]["head"]) == "DIVERT":
				divert_seen += 1
	assert_gt(divert_seen, 0, "the sweep met DIVERT rows")


func test_the_infected_change_and_the_ends_run_mark_come_from_the_forecast_and_rank_last() -> void:
	var f := _to_response(_env(7, 1, 80, 1, true))
	var any_lethal := false
	var seen_lethal := false
	for g in f.groups:
		var m: Dictionary = g["members"][0]
		var rows := SolaceTideRules.forecast(f.ctx(), f.raid.st, f.raid.place, m["resp"])
		var dead := 0
		var hi := -99
		for r in rows:
			var ns: SolaceTideState = r["result"]["state"]
			hi = maxi(hi, ns.wound_count() - f.raid.st.wound_count())
			if ns.lost != SolaceTideState.LOST_NONE:
				dead += 1
		assert_eq(int(m["inf_hi"]), hi, "the row's INFECTED change is the forecast's")
		assert_eq(bool(m["lethal_any"]), dead > 0)
		assert_eq(bool(m["lethal_all"]), dead == rows.size())
		any_lethal = any_lethal or dead > 0
		if bool(g["lethal_any"]):
			seen_lethal = true
		else:
			assert_false(seen_lethal, "a row that ends the run never ranks above one that does not")
	assert_true(any_lethal, "the lost scenario has a response that ends the run")
	for a in 3:
		var n := 0
		for t in f.route_tiles(a):
			n += int(t["n"])
		assert_eq(n, 4, "the forecast column tiles hold all four outcomes of route %d" % a)


func test_a_response_that_ends_the_run_needs_a_second_press() -> void:
	var f := _to_response(_env(7, 1, 80, 1, true))
	var lethal := -1
	var safe := -1
	for gi in f.groups.size():
		if bool(f.groups[gi]["lethal_any"]) and lethal < 0:
			lethal = gi
		if not bool(f.groups[gi]["lethal_any"]) and String(f.groups[gi]["members"][0]["head"]) != TideRaidFlow.HOLD and safe < 0:
			safe = gi
	assert_gte(lethal, 0)
	var resp: Array = f.select_group(lethal)
	assert_eq(f.commit(resp), "confirm", "the first press only arms")
	assert_true(f.lethal_armed)
	assert_eq(f.phase, TideRaidFlow.Phase.RESPONSE)
	assert_eq(f.commit(resp), "committed", "the second press commits")
	if safe >= 0:
		var g := _to_response(_env(7, 1, 80, 1, true))
		var r2: Array = g.select_group(safe)
		assert_ne(g.commit(r2), "confirm", "a response that cannot end the run commits at once")


func test_the_raids_count_holds_until_the_aftermath() -> void:
	var env := _env(7, 1, 80, 1)
	var f := _to_response(env)
	assert_eq(f.raids_shown(), -1)
	f.commit([TideRaidFlow.HOLD], true)
	assert_eq(f.phase, TideRaidFlow.Phase.PLAYOUT)
	assert_eq((env["c"] as CampaignState).pending_raids.size(), 0, "the campaign has dealt with the raid")
	assert_eq(f.raids_shown(), 1, "the top bar still counts it while the playout runs")
	f.playout_done()
	assert_eq(f.raids_shown(), -1, "and drops it at the aftermath")


func test_the_aftermath_always_has_the_raids_tier_and_keeps_decay_apart() -> void:
	var env := _env(7, 1, 80, 2, true)
	var f := _to_response(env)
	f.commit([TideRaidFlow.HOLD], true)
	f.playout_done()
	var a := f.aftermath()
	assert_true(bool(a["raided"]))
	assert_eq(String(a["tier"]), String((env["c"] as CampaignState).last_raid["tier"]), "the tier shown is the resolve's")
	assert_ne(String(a["tier"]), "CITY LOST", "the tier is the raid's, the loss is the banner")
	assert_eq(int(a["home_after"]), (env["c"] as CampaignState).grid.home_integrity, "HOME shown is HOME")
	var t: Dictionary = a["tally"]
	assert_eq(int(t["mid"]), int(t["decay"]["after"]), "DECAY's rows end where the raid's begin")
	assert_eq(int(t["raid"]["before"]), int(t["mid"]))
	assert_eq(int(t["mid"]) + int(t["raid"]["added"]), int(t["after"]), "the raid's rows add up to the final count")


func test_a_held_shift_card_gets_a_row_or_a_reason_and_the_infected_land_live() -> void:
	var found := false
	for sd in [7, 3, 11, 19, 31, 5, 13, 17, 29, 37, 41, 43]:
		var f := _to_response(_env(sd, 1, 80, 2))
		var sw := SolaceTideRules.launch(f.ctx(), f.raid.st, f.raid.place)
		if not SolaceTideRules._has_verb(sw.rhand, SolaceTideState.VERB_SHIFT):
			continue
		found = true
		var named := false
		for g in f.groups:
			named = named or String(g["members"][0]["head"]) in ["REDEPLOY", "DIVERT"]
		for gh in f.ghosts:
			named = named or String(gh[0]) in ["REDEPLOY", "DIVERT"]
		assert_true(named, "the held SHIFT card has a row or a ghost row (seed %d)" % sd)
	assert_true(found, "the sweep met a held SHIFT card")
	# The INFECTED cards land one by one during the playout and end at the campaign's count.
	var f2 := _to_response(_env(7, 1, 80, 1, true))
	var sac := -1
	for gi in f2.groups.size():
		if String(f2.groups[gi]["members"][0]["head"]) == "SACRIFICE":
			sac = gi
			break
	if sac >= 0:
		var pre := int(f2.hud()["infected"])
		f2.commit(f2.select_group(sac), true)
		assert_eq(int(f2.hud()["infected"]), pre, "nothing has landed when the playout starts")
		var added := f2.new_wounds().size()
		assert_gt(added, 0, "a sacrificed Site adds an INFECTED card")
		for i in added:
			f2.land_infected()
		assert_eq(int(f2.hud()["infected"]), pre + added)
		f2.playout_done()
		assert_eq(int(f2.hud()["infected"]), int(f2.last_raid["infected"]))


# ------------------------------------------------------------------------------------------------ Phase 3d
func _over_the_line(env: Dictionary) -> void:
	var ids: Array = []
	for i in 12:
		ids.append(&"t1_a")
	SolaceTideRules.add_infected(env["c"].corp_theme.solace.tide, ids, false)


func test_a_forced_loss_skips_the_menu_and_plays_the_raid_to_city_lost() -> void:
	var env := _campaign(1)
	_over_the_line(env)
	var f := _open(env)
	assert_true(f.forced(), "DECAY alone put INFECTED over the line: no response can save the city")
	assert_eq(f.phase, TideRaidFlow.Phase.DECAY)
	assert_eq(f.commit_forced(), "committed", "THE CITY FALLS plays from the DECAY beat: no PLAN, no RESPONSE, no confirm")
	assert_true(f.forced_run)
	assert_eq(f.phase, TideRaidFlow.Phase.PLAYOUT)
	assert_false(f.beats().is_empty(), "the raid plays straight through")
	var camp: CampaignState = env["c"]
	assert_true(camp.is_over(), "the campaign is lost")
	assert_eq(String(f.last_raid["lost"]), SolaceTideState.LOST_CITY)
	f.playout_done()
	assert_eq(String(f.aftermath()["banner"]), "CITY LOST")
	# A healthy city is never forced.
	var ok := _open(_campaign(1))
	assert_false(ok.forced())
	assert_eq(ok.commit_forced(), "no")


func test_home_shows_the_raids_damage_from_the_beat_that_hits_it() -> void:
	for sd in [7, 11, 23, 31]:
		var f := _to_response(_env(sd, 1, 80, 2))
		f.commit([TideRaidFlow.HOLD], true)
		var pre := int(f.hud()["home"])
		assert_eq(f.home_live, -1, "HOME has not dropped when the playout starts")
		f.land_home()
		var after := (f.result["state"] as SolaceTideState).home
		assert_eq(int(f.hud()["home"]), after, "from the HOME beat on the HUD shows what the raid leaves")
		assert_true(after <= pre)
		f.playout_done()


func test_a_deployed_card_is_marked_where_it_is_played() -> void:
	for sd in [7, 11, 23, 31, 41, 53]:
		var f := _to_response(_env(sd, 1, 80, 2))
		for gi in f.groups.size():
			var r: Array = f.groups[gi]["members"][0]["resp"]
			if String(r[0]) == "DEPLOY":
				var marked := 0
				for c in f.hand_cards(r):
					if String(c["played"]) != "":
						marked += 1
						assert_eq(String(c["played"]), String(r[2]))
				assert_eq(marked, 1, "exactly the card the DEPLOY spends carries the Site it goes to")
				return
	pending("no DEPLOY row on these seeds")


func test_the_hq_step_warns_a_raid_early_and_names_what_lifts_it() -> void:
	var env := _campaign(0)
	var c: CampaignState = env["c"]
	var corp: CorporationData = env["corp"]
	var cfg: CampaignConfigData = env["cfg"]
	var ring: Array[StringName] = []
	for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
		ring.append(l)
	ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	c.grid.site(ring[0])["condition"] = GridState.Condition.DOWN
	# INFECTED equal to the healthy cards: the DOWN Site that falls at the next DECAY is the card that ends the city.
	var st := SolaceTideCampaign.load_state(c, corp, cfg)
	var ids: Array = []
	for i in (st.deck.size() - st.wound_count()) - st.wound_count():
		ids.append(&"t1_a")
	SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	var f := _open(env)
	var none: Array = [&"", "", false]
	var base := f.hq_threat(none)
	var real := SolaceTideTally.next_decay(SolaceTideCampaign.load_state(c, corp, cfg), cfg)
	assert_eq(base, real, "the flow reads the core's query on the campaign's state")
	assert_true(bool(base["fatal"]) or bool(base["near"]), "a DOWN Site at the line is a threat")
	var fixes := f.hq_fixes(none)
	var repair := f.hq_threat([ring[0], "", false])
	assert_true(int(repair["added"]) < int(base["added"]), "repairing the DOWN Site stops its card")
	assert_true(fixes.has("repair:%s" % ring[0]), "REPAIR is named as a way out: %s" % [fixes])


## H7c: the playout shows a block's shield on the next beat only, then "shield gone"; a new block renews it.
func test_shield_spans_show_a_one_beam_shield_then_its_end() -> void:
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	var beats: Array = []
	for t in [[["known0", "t1_a", "block"]], [], [["sealed_b", "t1_b", "block"]], [["hunter", "t1_b", "block"]], []]:
		beats.append({"trace": t})
	TideRaidFlow.shield_spans(beats, cfg)
	var on: Array = []
	var gone: Array = []
	for b in beats:
		on.append(b["shielded"])
		gone.append(b["shield_gone"])
	assert_eq(on, [[], [&"t1_a"], [], [&"t1_b"], [&"t1_b"]], "shielded on the beat after each block")
	assert_eq(gone, [[], [], [&"t1_a"], [], []], "then gone; a renewed shield runs on")


func test_the_aftermath_counts_and_the_maps_stamps_come_from_one_event_list() -> void:
	for sd in [7, 11, 23, 31]:
		var f := _to_response(_env(sd, 1, 80, 2))
		f.commit([TideRaidFlow.HOLD], true)
		f.playout_done()
		var a := f.aftermath()
		var owned := f.aftermath_owned()
		var map_down := 0
		var map_taken := 0
		for s in owned:
			if int(owned[s]) == SolaceTideState.Cond.DOWN:
				map_down += 1
			elif int(owned[s]) == SolaceTideState.Cond.TAKEN:
				map_taken += 1
		var c: Dictionary = a["counts"]
		assert_eq(int(c["down"]), map_down, "seed %d: the DOWN count is the DOWN stamps on the map" % sd)
		assert_eq(int(c["taken"]), map_taken, "seed %d: the TAKEN count is the TAKEN stamps on the map" % sd)
		assert_eq((a["events"] as Array).size(), map_down + map_taken, "seed %d: one event per stamp" % sd)
		assert_eq(int(c["decay_taken"]), f.decay_sites().size(), "seed %d: DECAY's takings are kept apart" % sd)
		assert_eq(int(c["raid_taken"]) + int(c["unguarded_taken"]), (f.last_raid["taken"] as Array).size(), "seed %d: and so are the raid's own" % sd)
		assert_eq(int(c["unguarded_taken"]), (f.last_raid["fell"] as Array).size(), "seed %d: H7c: the fallen Sites are 'unguarded'" % sd)
		assert_eq(int(c["raid_down"]), (f.last_raid["down"] as Array).size())
		assert_eq(int(c["decay_taken"]) + int(c["raid_taken"]) + int(c["unguarded_taken"]) + int(c["earlier_taken"]), int(c["taken"]), "the parts add up")
		assert_gt(int(c["decay_taken"]), 0, "DECAY took the DOWN Sites, so the raid's own count alone would contradict the map")
