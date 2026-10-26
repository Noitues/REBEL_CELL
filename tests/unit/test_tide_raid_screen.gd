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


func _own_three(c: CampaignState, n: int = 3) -> void:
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var ring: Array[StringName] = []
	for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
		ring.append(l)
	ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ring.slice(0, n):
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


func _bar_agrees(hq: Control, flow: TideRaidFlow, tag: String) -> void:
	var h := flow.hud()
	assert_eq(hq.hud.heat_gauge.heat, int(h["heat"]), "the top bar's Heat is the screen's at " + tag)
	assert_eq(String(hq.hud.stats.items[0][1]), str(h["schematics"]), "the top bar's Schematics are the screen's at " + tag)
	assert_eq(String(hq.hud.stats.items[1][1]), str(h["home"]), "the top bar's HOME is the screen's at " + tag)


func test_the_top_bar_and_the_panels_agree_at_every_beat_and_the_hq_step_lists_every_action() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	_own_three(c)
	c.schematics = 300
	c.raids_won = 1
	var owned_ids: Array = []
	for s in c.grid.sites.keys():
		if c.grid.is_claimed(s) and s != c.grid.home_site_id:
			owned_ids.append(s)
	IdSort.sort_ids(owned_ids)
	c.grid.site(owned_ids[0])["condition"] = GridState.Condition.DOWN
	c.grid.home_integrity -= 4
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})
	var hq := _scene()
	await _frames()
	if hq.tide_screen == null:
		hq.show_raid()
		await _frames()
	var screen: TideRaidScreen = hq.tide_screen
	var flow: TideRaidFlow = screen.flow
	assert_eq(flow.raid_number(), 2)
	_bar_agrees(hq, flow, "DECAY")
	assert_not_null(screen.body.find_child("InfectedTally", true, false), "DECAY says where the INFECTED cards came from")
	screen.cont()
	screen.cont()
	_bar_agrees(hq, flow, "PLAN")
	assert_not_null(screen.hud_strip.find_child("InfectedMeter", true, false), "the HUD carries the INFECTED meter")
	screen.to_forecast()
	assert_not_null(screen.body.find_child("ForecastTable", true, false))
	screen.launch()
	if flow.phase == TideRaidFlow.Phase.FORECAST:
		screen.launch()
	if flow.phase == TideRaidFlow.Phase.REVEAL:
		flow.reveal_done()
		screen._rebuild()
	if flow.phase == TideRaidFlow.Phase.RESPONSE:
		screen.select_group(0)
		screen.commit()
		if flow.phase == TideRaidFlow.Phase.RESPONSE:
			screen.commit()
	await _frames()
	if flow.phase == TideRaidFlow.Phase.PLAYOUT:
		flow.playout_done()
		screen._rebuild()
	_bar_agrees(hq, flow, "AFTERMATH")
	assert_not_null(screen.body.find_child("InfectedTally", true, false), "the aftermath explains the INFECTED count")
	screen.cont()
	if flow.phase == TideRaidFlow.Phase.HQ_STEP:
		_bar_agrees(hq, flow, "HQ step")
		for k in ["Hq_patch", "Hq_clean", "Hq_cool", "Hq_install"]:
			assert_not_null(screen.body.find_child(k, true, false), "the HQ step lists " + k)
		screen.done_hq()
	assert_eq(flow.phase, TideRaidFlow.Phase.DONE)


func test_one_more_infected_card_shows_the_warning_at_plan() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	_own_three(c)
	var st := SolaceTideCampaign.load_state(c, RunManager.corporation, RunManager.config())
	var ids: Array = []
	for i in st.deck.size() - st.wound_count():
		ids.append(StringName("w_%02d" % i))
	SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})
	var hq := _scene()
	await _frames()
	hq.show_raid()
	await _frames()
	var screen: TideRaidScreen = hq.tide_screen
	screen.cont()
	screen.cont()
	assert_true(screen.flow.loss_warning())
	assert_not_null(screen.body.find_child("LossBanner", true, false), "PLAN warns: 1 more = CITY LOST")
	assert_not_null(screen.hud_strip.find_child("LossWarning", true, false), "and so does the HUD")


# ------------------------------------------------------------------------------------------------ Phase 3c
func _pending(c: CampaignState) -> void:
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})


## Opens the tide screen on the first raid (`heat`), or with `lost` the second raid with INFECTED one card short of the line.
func _open_tide(heat: int, lost: bool = false) -> Array:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	c.schematics = 300
	_own_three(c, 4)
	c.heat = heat
	c.raids_lost = 0
	if lost:
		c.raids_won = 1
		c.raids_lost = 0
		var corp := RunManager.corporation
		var ring: Array[StringName] = []
		for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
			ring.append(l)
		ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
		c.grid.site(ring[0])["condition"] = GridState.Condition.DOWN
		var st := SolaceTideCampaign.load_state(c, corp, RunManager.config())
		var healthy := st.deck.size() - st.wound_count()
		var ids: Array = []
		for i in healthy - st.wound_count() - 1:
			ids.append(ring[1 + i % 3])
		SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	_pending(c)
	var hq := _scene()
	await _frames()
	if hq.tide_screen == null:
		hq.show_raid()
	await _frames()
	return [hq, hq.tide_screen]


func _to_response_screen(screen: TideRaidScreen, place: bool = false) -> void:
	var flow := screen.flow
	var p0 := flow.phase
	screen.cont()
	screen.cont()
	assert_eq(flow.phase, TideRaidFlow.Phase.PLAN, "start phase %d" % p0)
	var placed := 0
	for h in flow.hand_cards():
		var sites := flow.placeable_sites()
		if not place or placed >= 2 or sites.is_empty():
			break
		if h["verb"] == "GUARD":
			screen.card_pressed(h["id"])
			screen.site_clicked(sites[0])
			placed += 1
	screen.to_forecast()
	screen.launch()
	if flow.phase == TideRaidFlow.Phase.FORECAST:
		screen.launch()
	if flow.phase == TideRaidFlow.Phase.REVEAL:
		flow.reveal_done()
		screen._rebuild()


func test_the_header_shows_the_pending_heat_and_a_placed_card_keeps_its_cost() -> void:
	var o := await _open_tide(60)
	var screen: TideRaidScreen = o[1]
	var flow := screen.flow
	screen.cont()
	screen.cont()
	var cost := flow.cfg.solace_tide_card_response_heat
	var picked := ""
	for h in flow.hand_cards():
		if h["verb"] == "GUARD":
			picked = h["id"]
			break
	assert_ne(picked, "")
	var sites := flow.placeable_sites()
	screen.card_pressed(picked)
	screen.site_clicked(sites[0])
	var face := screen.hand_row.find_child("Card_%s" % picked, true, false) as TideGlyphView
	assert_eq(face.heat, cost, "a placed card keeps its Heat cost, it does not flip to 0")
	assert_true(flow.raid.st.ghost > 0)
	screen.ghost()
	var lab := screen.hud_strip.find_child("HeatLabel", true, false) as Label
	var p := flow.pending_heat()
	assert_true(lab.text.begins_with("HEAT 60 "), "the header leads with the Heat now: " + lab.text)
	assert_true(int(p["hi"]) != 60 and lab.text.contains("→"), "and shows where the plan leaves it: " + lab.text)
	assert_gte(int(p["lo"]), 60 + flow.cfg.solace_tide_ghost_heat, "the ghost's Heat is in it")


func test_response_rows_carry_their_numbers_the_commit_is_pinned_and_a_lethal_pick_asks_twice() -> void:
	var o := await _open_tide(80, true)
	var screen: TideRaidScreen = o[1]
	var flow := screen.flow
	_to_response_screen(screen)
	assert_eq(flow.phase, TideRaidFlow.Phase.RESPONSE, "phase=%d fast=%s groups=%d" % [flow.phase, flow.fast, flow.groups.size()])
	assert_not_null(screen.foot.find_child("Commit", true, false), "COMMIT is pinned under the scrolling list")
	assert_null(screen.body.find_child("Commit", true, false))
	var lethal := -1
	for gi in flow.groups.size():
		var m: Dictionary = flow.groups[gi]["members"][0]
		var row := screen.body.find_child("Resp_%d" % gi, true, false)
		assert_not_null(row)
		var heat := row.find_child("HeatChip", true, false).find_child("Val", true, false) as Label
		var inf := row.find_child("InfChip", true, false).find_child("Val", true, false) as Label
		assert_eq(heat.text, ("%+d" % int(m["heat_lo"])) if int(m["heat_lo"]) == int(m["heat_hi"]) else "%+d..%+d" % [m["heat_lo"], m["heat_hi"]], "the Heat chip is the forecast's")
		assert_eq(inf.text, ("%+d" % int(m["inf_lo"])) if int(m["inf_lo"]) == int(m["inf_hi"]) else "%+d..%+d" % [m["inf_lo"], m["inf_hi"]], "the INFECTED chip is the forecast's")
		if bool(flow.groups[gi]["lethal_any"]) and lethal < 0:
			lethal = gi
	assert_gte(lethal, 0)
	screen.select_group(lethal)
	screen.commit()
	assert_eq(flow.phase, TideRaidFlow.Phase.RESPONSE, "the first press only arms")
	assert_not_null(screen.foot.find_child("LethalConfirm", true, false), "the foot says the pick can end the run")
	assert_string_contains((screen.foot.find_child("Commit", true, false) as Button).text, "END THE RUN")
	screen.commit()
	await _frames()
	assert_true(flow.phase in [TideRaidFlow.Phase.PLAYOUT, TideRaidFlow.Phase.AFTERMATH])


func test_the_top_bar_keeps_the_raid_count_through_the_playout_and_the_stops_follow_the_trace() -> void:
	var o := await _open_tide(80, true)
	var hq: Control = o[0]
	var screen: TideRaidScreen = o[1]
	var flow := screen.flow
	_to_response_screen(screen)
	flow.commit([TideRaidFlow.HOLD], true)
	screen._rebuild()
	var raids := ""
	for it in hq.hud.stats.items:
		if String(it[0]) == "RAIDS":
			raids = String(it[1])
	assert_eq(raids, "1", "RAIDS still counts the raid while it plays")
	for b in flow.beats():
		var want := ""
		for e in b["trace"]:
			if e[2] == "block":
				want = String(e[1])
				break
			if e[2] == "home" or e[2] == "shield":
				want = "HOME"
		assert_eq(screen._stop_of(b), want, "a beam stops at its guard or at HOME")
	flow.playout_done()
	screen._rebuild()
	for it in hq.hud.stats.items:
		if String(it[0]) == "RAIDS":
			raids = String(it[1])
	assert_eq(raids, "0", "and drops it at the aftermath")


func test_city_lost_is_a_full_screen_moment_over_the_raids_own_tier() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	_own_three(c)
	c.raids_won = 1
	var ids: Array = []
	for i in 12:
		ids.append(&"t1_a")
	SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	_pending(c)
	var hq := _scene()
	await _frames()
	if hq.tide_screen == null:
		hq.show_raid()
	await _frames()
	var screen: TideRaidScreen = hq.tide_screen
	var flow := screen.flow
	_to_response_screen(screen)
	if flow.phase == TideRaidFlow.Phase.RESPONSE:
		screen.select_group(0)
		screen.commit()
		if flow.phase == TideRaidFlow.Phase.RESPONSE:
			screen.commit()
	await _frames()
	if flow.phase == TideRaidFlow.Phase.PLAYOUT:
		flow.playout_done()
		screen._rebuild()
	assert_eq(flow.phase, TideRaidFlow.Phase.AFTERMATH)
	assert_true(screen.city_lost_showing(), "CITY LOST covers the screen")
	var banner := screen.body.find_child("Banner", true, false) as Label
	assert_eq(banner.text, "CITY LOST")
	var stamp := screen.body.find_child("AftermathStamp", true, false)
	var words := ""
	for ch in stamp.get_children():
		if ch is Label:
			words = (ch as Label).text
	assert_ne(words, "CITY LOST", "the stamp is the raid's own tier")
	assert_eq(words, screen._tierw(String(flow.aftermath()["tier"])))
	screen.cont()
	assert_false(screen.city_lost_showing(), "CONTINUE lets the aftermath go on")


func test_the_aftermath_tally_keeps_decay_and_the_raid_apart_and_the_hq_pick_shows() -> void:
	var o := await _open_tide(80, true)
	var screen: TideRaidScreen = o[1]
	var flow := screen.flow
	_to_response_screen(screen)
	flow.commit([TideRaidFlow.HOLD], true)
	flow.playout_done()
	screen._rebuild()
	var tally := screen.body.find_child("InfectedTally", true, false)
	assert_not_null(tally.find_child("TallyDecay", true, false), "DECAY rows are their own section: %s" % [flow.decay_tally])
	assert_not_null(tally.find_child("TallyRaid", true, false), "and so are the raid's")
	screen.cont()
	if flow.phase == TideRaidFlow.Phase.HQ_STEP:
		var acts := flow.hq_actions([&"", "", false])
		for a in acts:
			if bool(a["enabled"]):
				screen._hq_pick(a)
				assert_gt(flow.hq_total([screen._hq_repair, screen._hq_build, screen._hq_patch]), 0, "the pick counts")
				var name_ := "Hq_%s" % a["kind"] if StringName(a["site"]) == &"" else "Hq_%s_%s" % [a["kind"], a["site"]]
				var btn := screen.body.find_child(name_, true, false).find_child("Pick", true, false) as Button
				assert_true(btn.text.begins_with("> "), "the picked row is marked")
				break


# ------------------------------------------------------------------------------------------------ Phase 3d
func test_a_forced_loss_shows_the_city_falls_not_the_menu() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	_own_three(c)
	c.raids_won = 1
	var ids: Array = []
	for i in 12:
		ids.append(&"t1_a")
	SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	_pending(c)
	var hq := _scene()
	await _frames()
	if hq.tide_screen == null:
		hq.show_raid()
	await _frames()
	var screen: TideRaidScreen = hq.tide_screen
	var flow := screen.flow
	assert_not_null(screen.body.find_child("CityFallsButton", true, false), "the DECAY beat offers THE CITY FALLS")
	assert_not_null(screen.body.find_child("CityFalls", true, false))
	screen.city_falls()
	await _frames()
	assert_true(flow.forced_run)
	assert_false(flow.phase == TideRaidFlow.Phase.RESPONSE, "no response menu, no confirm")
	if flow.phase == TideRaidFlow.Phase.PLAYOUT:
		flow.playout_done()
		screen._rebuild()
	assert_eq(flow.phase, TideRaidFlow.Phase.AFTERMATH)
	assert_true(screen.city_lost_showing(), "the sequence ends on CITY LOST")


func test_the_forecast_odds_and_a_pointed_outcome_draw_on_the_map() -> void:
	var o := await _open_tide(80)
	var screen: TideRaidScreen = o[1]
	var flow := screen.flow
	screen.cont()
	screen.cont()
	screen.to_forecast()
	var odds := flow.plan_odds()
	var total := 0
	for t in odds:
		total += int(t["n"])
	assert_eq(total, 12, "the bar counts all twelve outcomes")
	var bar := screen.body.find_child("OddsBar", true, false) as TideOddsBar
	assert_not_null(bar)
	assert_eq(bar.total, 12)
	assert_eq(odds.map(func(t: Dictionary) -> String: return String(t["tier"])), SolaceTideTally.tier_odds(flow.forecast()).map(func(t: Dictionary) -> String: return String(t["tier"])))
	var worst := String(odds[0]["tier"])
	screen._set_fc_hover({"a": -1, "tier": worst, "inf": -1})
	var want := flow.marks_of(flow.rows_of(-1, worst))
	assert_eq(screen.layer.fc_marks, want, "the map shows what that tier does: the Sites that go DOWN and HOME's damage")
	screen._set_fc_hover({})
	assert_true(screen.layer.fc_marks.is_empty())


func test_a_card_that_stops_nothing_turns_red_and_is_flagged_before_it_is_placed() -> void:
	var o := await _open_tide(80)
	var screen: TideRaidScreen = o[1]
	var flow := screen.flow
	screen.cont()
	screen.cont()
	# Pick each placeable card in turn and find a Site where the rule says it does nothing.
	var hit := false
	for h in flow.hand_cards():
		if hit or not SolaceTideRules.PLACEABLE.has(h["verb"]):
			continue
		screen.card_pressed(h["id"])
		for s in flow.placeable_sites():
			var chk: Dictionary = SolaceTideTally.sentry_check(flow.raid.ctx, flow.raid.st, flow.raid.place, s, h["id"])
			if bool(chk["useless"]):
				assert_true(screen.layer.ghost_sites.has(s), "the ghost is flagged before the card is placed")
				assert_true(bool(screen.layer.ghost_sites[s]["useless"]))
				screen.site_clicked(s)
				assert_true(screen.layer.bad_sentries.has(s), "the placed card turns red with its reason")
				assert_ne(String(screen.layer.bad_sentries[s]), "")
				assert_not_null(screen.body.find_child("Mismatch_%s" % s, true, false), "and the page says why")
				hit = true
				break
		if not hit:
			screen.card_pressed(h["id"])  # let go
	assert_true(hit, "the sweep met a card that stops nothing")


func test_blocked_beams_merge_into_one_sweep_and_hits_stand_alone() -> void:
	var o := await _open_tide(80)
	var screen: TideRaidScreen = o[1]
	var flow := screen.flow
	_to_response_screen(screen, true)
	flow.commit([TideRaidFlow.HOLD], true)
	var beats := flow.beats()
	var steps := screen._make_steps(beats)
	var n := 0
	var prev_quiet := false
	for s in steps:
		n += (s["idx"] as Array).size()
		if bool(s["quiet"]):
			assert_false(prev_quiet, "two quiet steps never follow each other")
		else:
			assert_eq((s["idx"] as Array).size(), 1, "a hit is its own step")
		prev_quiet = bool(s["quiet"])
	assert_eq(n, beats.size(), "every beam is in a step")
	assert_true(steps.size() <= beats.size())
	flow.playout_done()


func test_the_hq_step_shows_the_decay_warning_and_the_fix() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	_own_three(c)
	c.schematics = 300
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var ring: Array[StringName] = []
	for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
		ring.append(l)
	ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	c.grid.site(ring[0])["condition"] = GridState.Condition.DOWN
	var st := SolaceTideCampaign.load_state(c, corp, cfg)
	var ids: Array = []
	for i in (st.deck.size() - st.wound_count()) - st.wound_count():
		ids.append(&"t1_a")
	SolaceTideRules.add_infected(c.corp_theme.solace.tide, ids, false)
	_pending(c)
	var hq := _scene()
	await _frames()
	if hq.tide_screen == null:
		hq.show_raid()
	await _frames()
	var screen: TideRaidScreen = hq.tide_screen
	screen.flow.phase = TideRaidFlow.Phase.HQ_STEP
	screen._rebuild()
	assert_not_null(screen.body.find_child("DecayWarning", true, false), "the HQ step warns that the next DECAY threatens the city")
	assert_not_null(screen.body.find_child("Fix", true, false), "and marks the way out")
	screen._hq_repair = ring[0]
	screen._rebuild()
	var still := screen.flow.hq_threat([ring[0], "", false])
	assert_eq(screen.body.find_child("DecayWarning", true, false) != null, bool(still["fatal"]) or bool(still["near"]), "the warning follows the picks")
