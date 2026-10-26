extends GutTest
## Phase 2b (rules tier fast): the Solace Infected Tide inside a campaign. The per-corp switch (spec section 10 item 6), the
## CampaignState <-> SolaceTideState mapping, the raid queue (cadence + Heat levels), seeded replay through save and load,
## preview == result, the raid as one checkpoint (spec section 10 item 4), the breach retry, the Exploit re-take, the R-C card
## mapping, CLEAN, and R-F (the Genome Core grows with the INFECTED count).

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData
var _breaker: ClassData


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData
	_breaker = ContentRegistry.get_content(&"breaker") as ClassData


func _campaign(seed: int = 1) -> CampaignState:
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, seed, _breaker, GridFixture.home_node())
	c.schematics = 1000
	return c


func _run(site_id: StringName, kind: String = "netrun") -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	r.kind = kind
	return r


## The Sites linked to home, by id.
func _ring() -> Array[StringName]:
	var ids: Array[StringName] = []
	for l in _corp.city_grid.get_site(&"home").links:
		ids.append(l)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return ids


## Clears and claims the first `n` Sites around home (relays).
func _own(c: CampaignState, n: int) -> Array[StringName]:
	var owned: Array[StringName] = []
	for id in _ring().slice(0, n):
		CampaignRules.on_run_completed(c, _corp, _cfg, _run(id))
		CampaignRules.claim(c, _corp, _cfg, _lookup, id, &"relay")
		owned.append(id)
	return owned


func _pending(c: CampaignState) -> Dictionary:
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})
	return c.pending_raids[c.pending_raids.size() - 1]


func _fight(c: CampaignState) -> Array[Dictionary]:
	return CampaignRules.fight_raid(c, _corp, _cfg, _lookup, _pending(c))


# --------------------------------------------------------------------------------------- the per-corp switch (item 6)
func test_only_solace_ships_the_tide_and_the_others_keep_the_resolver() -> void:
	for id in [&"meridian", &"halcyon", &"orbital", &"rebel_cell"]:
		var corp := ContentRegistry.get_content(id) as CorporationData
		assert_eq(corp.raid_model, &"resolver", "%s" % id)
		assert_false(CampaignRules.uses_tide(corp))
	assert_true(CampaignRules.uses_tide(_corp))
	var c := _campaign()
	assert_not_null(c.corp_theme.solace.tide, "a Solace campaign starts the tide")
	assert_eq(c.corp_theme.solace.tide.deck.size(), 8)
	assert_eq(c.corp_theme.solace.tide.ghost, _cfg.solace_tide_ghost_start)
	var mer := ContentRegistry.get_content(&"meridian") as CorporationData
	var m := CampaignRules.new_campaign(mer, _cfg, _lookup, 1, _breaker, GridFixture.home_node())
	assert_null(m.corp_theme.solace.tide, "no tide for a resolver corporation")
	assert_true(m.corp_theme.is_default(), "its theme block stays default and out of the save")


func test_a_resolver_corporation_still_runs_the_raid_resolver() -> void:
	var mer := ContentRegistry.get_content(&"meridian") as CorporationData
	var c := CampaignRules.new_campaign(mer, _cfg, _lookup, 1, _breaker, GridFixture.home_node())
	c.schematics = 1000
	CampaignRules.on_run_completed(c, mer, _cfg, _run(&"m1_a"))
	CampaignRules.claim(c, mer, _cfg, _lookup, &"m1_a", &"relay")
	var pending := CampaignRules.pending_raid(c)
	assert_false(pending.is_empty(), "the claim queues the resolver's raid")
	var proj := CampaignRules.project_raid(c, mer, _cfg, _lookup, pending)
	assert_not_null(proj, "project_raid returns the resolver's result")
	assert_eq(CampaignRules.project_tide_raid(c, mer, _cfg, _lookup, pending), {}, "no tide preview for a resolver corporation")
	CampaignRules.fight_raid(c, mer, _cfg, _lookup, pending)
	assert_false(c.last_raid.has("model"), "the resolver's raid dictionary")
	assert_eq(c.last_raid["home_after"], proj.home_after, "preview == result on the resolver path")
	assert_eq(c.raids_won + c.raids_lost, 1)


func test_a_tide_campaign_queues_no_resolver_raid() -> void:
	var c := _campaign()
	_own(c, 2)
	assert_true(c.pending_raids.is_empty(), "a claim queues no raid in a tide campaign")
	c.heat = 0
	HeatRules.add_heat(c, 30, _cfg, "test")  # crosses the 25 level
	assert_true(c.pending_raids.is_empty(), "a Heat level queues nothing itself: the netrun's close does")
	assert_true(c.corp_theme.solace.tide.heat_crossed)
	assert_eq(CampaignRules.queue_raid(c, _corp, RC.RaidTriggerSource.STORY, &"", "story").size(), 0)


# --------------------------------------------------------------------------------------- the mapping (item 2)
func test_campaign_state_maps_into_the_tide_and_back() -> void:
	var c := _campaign()
	var owned := _own(c, 3)
	c.grid.site(owned[1])["condition"] = GridState.Condition.DOWN
	c.grid.site(owned[2])["status"] = GridState.SiteStatus.TAKEN
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(&"t2_intel"))  # CLEARED
	var st := SolaceTideCampaign.load_state(c, _corp, _cfg)
	assert_eq(st.owned[owned[0]], SolaceTideState.Cond.OK)
	assert_eq(st.owned[owned[1]], SolaceTideState.Cond.DOWN)
	assert_eq(st.owned[owned[2]], SolaceTideState.Cond.TAKEN)
	assert_true(st.pending.has(&"t2_intel"), "CLEARED = pending")
	assert_false(st.owned.has(&"t2_intel"))
	assert_eq(st.heat, c.heat)
	assert_eq(st.home, c.grid.home_integrity)
	assert_eq(st.schematics, c.schematics)
	var before := c.state_hash()
	SolaceTideCampaign.store_state(c, st)
	assert_eq(c.state_hash(), before, "an untouched state stores back unchanged")


func test_exploits_held_map_to_exploit_sites() -> void:
	var c := _campaign()
	var exploit_site: SiteData = null
	for s in _corp.city_grid.sites:
		if s.objective == RC.SiteObjective.EXPLOIT:
			exploit_site = s
			break
	assert_not_null(exploit_site)
	assert_eq(SolaceTideCampaign.load_state(c, _corp, _cfg).held.size(), 0)
	c.exploits.append(exploit_site.exploit_type)
	assert_eq(SolaceTideCampaign.load_state(c, _corp, _cfg).held, [exploit_site.id] as Array[StringName])


func test_claims_use_territory_claimed_or_cleared() -> void:
	var c := _campaign()
	var ring := _ring()
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(ring[0]))  # CLEARED, not claimed
	var next: StringName = &""
	for n in c.grid.neighbors(ring[0], _corp.city_grid):
		if n != &"home" and c.grid.is_corporate(n):
			next = n
			break
	assert_ne(next, &"")
	assert_true(CampaignRules.touches_territory(c, _corp, next), "a cleared Site counts (spec section 2)")
	var ids: Array[StringName] = []
	for s in CampaignRules.launchable_sites(c, _corp, _cfg):
		ids.append(s.id)
	assert_true(ids.has(next), "and its neighbor is launchable")


# --------------------------------------------------------------------------------------- the raid
func test_a_tide_raid_applies_to_the_campaign_and_counts() -> void:
	var c := _campaign()
	_own(c, 3)
	c.heat = 40
	var events := _fight(c)
	assert_eq(c.pending_raids.size(), 0, "the pending raid is consumed")
	assert_eq(c.raids_won + c.raids_lost, 1)
	assert_eq(c.last_raid["model"], "tide")
	assert_eq(c.last_raid["home_after"], c.grid.home_integrity)
	assert_true(c.corp_theme.solace.tide.raid_n == 0 and not c.corp_theme.solace.tide.decayed)
	assert_true(events.size() > 0)
	var tier: String = c.last_raid["tier"]
	assert_true(["BREACHED", "DAMAGED", "EVADED", "BATTERED", "HOLDS"].has(tier), tier)


func test_the_tide_raid_is_seeded_and_the_preview_equals_the_result() -> void:
	var a := _campaign(7)
	_own(a, 4)
	a.heat = 60
	var b := a.duplicate_state()
	var pending := _pending(a)
	var pv := CampaignRules.project_tide_raid(a, _corp, _cfg, _lookup, pending)
	assert_false(pv.is_empty())
	var hash_before := a.state_hash()
	CampaignRules.project_tide_raid(a, _corp, _cfg, _lookup, pending)
	assert_eq(a.state_hash(), hash_before, "a projection changes nothing")
	CampaignRules.fight_raid(a, _corp, _cfg, _lookup, pending)
	var res := a.last_raid.duplicate(true)
	pv.erase("events")
	assert_eq(pv, res, "preview == result")
	_fight(b)
	assert_eq(a.state_hash(), b.state_hash(), "same seed and inputs, same campaign")
	assert_eq(SolaceTideCampaign.raid_streams(7, 3).randi(), SolaceTideCampaign.raid_streams(7, 3).randi(), "the raids stream is a pure function of seed and index")
	assert_ne(SolaceTideCampaign.raid_streams(7, 3).randi(), SolaceTideCampaign.raid_streams(7, 4).randi())


func test_a_campaign_resumes_identically_through_save_and_load() -> void:
	var a := _campaign(11)
	_own(a, 4)
	a.heat = 55
	_fight(a)
	var json := JSON.stringify(a.to_dict())
	var b := CampaignState.from_dict(JSON.parse_string(json))
	assert_eq(b.state_hash(), a.state_hash(), "the loaded campaign hashes the same")
	for i in 3:
		a.heat = 55
		b.heat = 55
		_fight(a)
		_fight(b)
		assert_eq(b.state_hash(), a.state_hash(), "raid %d after the load" % (i + 2))
		assert_eq(b.last_raid, a.last_raid)
	assert_eq(b.corp_theme.solace.tide.block_dict(), a.corp_theme.solace.tide.block_dict())


func test_a_saved_tide_block_has_the_spec_fields() -> void:
	var c := _campaign()
	var d: Dictionary = c.to_dict()["corp_theme"]["solace"]["tide"]
	for k in ["deck", "inf_n", "dose_n", "asset_n", "ghost", "lost_since_raid", "last_lost", "last_sac", "raid_n", "netruns_since_raid",
			"purge_queued", "dose_spent", "breach_fails"]:
		assert_true(d.has(k), k)
	assert_false(c.to_dict()["corp_theme"]["solace"].has("infection_bp"), "R-G: infection_bp is gone")
	assert_eq(SaveServiceScript.SAVE_VERSION, 5)


# --------------------------------------------------------------------------------------- spec section 10 item 4: the checkpoint
func test_the_raid_is_one_checkpoint_rewind_never_crosses_it_and_decay_is_never_undone() -> void:
	var c := _campaign(5)
	_own(c, 4)
	c.heat = 50
	_fight(c)  # raid 0 (no DECAY)
	var down: StringName = _ring()[0]
	c.grid.site(down)["condition"] = GridState.Condition.DOWN  # a Site left DOWN: the next raid's DECAY takes it
	var pending := _pending(c)
	var raid := SolaceTideRaid.open(c, _corp, _cfg, pending)
	assert_false(raid.over)
	assert_true(c.grid.is_taken(down), "DECAY ran when the raid opened")
	var infected := SolaceTideCampaign.infected_count(c)
	assert_gt(infected, 0, "and added its INFECTED card")
	var campaign_hash := c.state_hash()
	assert_false(raid.can_rewind(), "nothing to undo at the start of the raid")
	assert_false(raid.rewind())
	var places := raid.placements()
	assert_gt(places.size(), 1)
	assert_true(raid.set_place(places[1]))
	assert_true(raid.can_rewind())
	var opts := raid.response_options()
	assert_true(raid.set_response(opts[opts.size() - 1]))
	assert_true(raid.rewind(), "the RESPONSE is undone")
	assert_eq(raid.resp, ["HOLD"].duplicate())
	assert_true(raid.rewind(), "and the PLAN")
	assert_eq(raid.place, {"sentries": {}, "ghost": &""})
	assert_false(raid.can_rewind(), "back at the checkpoint, not past it")
	assert_eq(c.state_hash(), campaign_hash, "PLAN and RESPONSE changed nothing in the campaign")
	assert_true(c.grid.is_taken(down), "DECAY stays done through every rewind")
	var rows := raid.preview()
	assert_eq(rows.size(), 12)
	raid.set_place(places[1])
	raid.resolve()
	assert_false(raid.can_rewind(), "after the resolve nothing rewinds")
	assert_false(raid.rewind())
	assert_false(raid.set_place(places[0]), "and nothing is planned")
	var after := c.state_hash()
	raid.resolve()
	assert_eq(c.state_hash(), after, "a second resolve does nothing")
	assert_true(c.grid.is_taken(down))


func test_an_opened_raid_does_not_decay_twice_after_a_save() -> void:
	var c := _campaign(9)
	_own(c, 3)
	_fight(c)
	c.grid.site(_ring()[0])["condition"] = GridState.Condition.DOWN
	var pending := _pending(c)
	SolaceTideRaid.open(c, _corp, _cfg, pending)
	var tide := c.corp_theme.solace.tide
	assert_true(tide.decayed)
	var n := tide.inf_n
	var loaded := CampaignState.from_dict(JSON.parse_string(JSON.stringify(c.to_dict())))
	var again := SolaceTideRaid.open(loaded, _corp, _cfg, loaded.pending_raids[0])
	assert_eq(loaded.corp_theme.solace.tide.inf_n, n, "no second DECAY")
	var first := SolaceTideRaid.open(c, _corp, _cfg, pending)
	assert_eq(again.ctx.hand, first.ctx.hand, "the same hand")
	assert_eq(again.ctx.draw["real_a"], first.ctx.draw["real_a"], "and the same lines")


# --------------------------------------------------------------------------------------- the raid queue (cadence + Heat)
func test_the_cadence_queues_a_raid_every_third_netrun_and_a_raid_resets_it() -> void:
	var c := _campaign()
	for i in 2:
		c.runs_completed += 1
		CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, false)
		assert_true(c.pending_raids.is_empty(), "netrun %d" % (i + 1))
	c.runs_completed += 1
	CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, false)
	assert_eq(c.pending_raids.size(), 1, "the third netrun queues a raid (solace_tide_raid_every)")
	assert_eq(c.pending_raids[0]["model"], "tide")
	c.runs_completed += 1
	CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, false)
	assert_eq(c.pending_raids.size(), 1, "at most one raid waits")
	_fight(c)
	assert_eq(c.corp_theme.solace.tide.netruns_since_raid, 0, "a raid resets the cadence")


func test_a_heat_level_queues_a_raid_at_once_and_resets_the_cadence() -> void:
	var c := _campaign()
	c.runs_completed += 1
	HeatRules.add_heat(c, 30, _cfg, "test")
	var events := CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, false)
	assert_eq(c.pending_raids.size(), 1, "crossing 25 queues a raid after the first netrun")
	assert_eq(c.pending_raids[0]["source"], RC.RaidTriggerSource.HEAT_THRESHOLD)
	assert_false(c.corp_theme.solace.tide.heat_crossed, "the flag is spent")
	assert_gt(events.size(), 0)
	c.pending_raids.clear()
	_fight(c)
	assert_eq(c.corp_theme.solace.tide.netruns_since_raid, 0, "a Heat raid resets the cadence too (Phase 1 rule)")
	c.runs_completed += 1
	CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, false)
	assert_true(c.pending_raids.is_empty(), "no second raid from the same level")


func test_a_level_reached_during_a_raid_fires_at_the_next_netruns_close() -> void:
	var c := _campaign()
	c.heat = 26  # a raid's clean-defense Heat put the Heat past 25 without a threshold firing
	assert_false(c.thresholds_fired.has(25))
	c.runs_completed += 1
	CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, false)
	assert_true(c.thresholds_fired.has(25))
	assert_eq(c.pending_raids.size(), 1)


func test_a_dose_arrives_every_fourth_netrun_deaths_included() -> void:
	var c := _campaign()
	var tide := c.corp_theme.solace.tide
	for i in 4:
		if i == 2:
			c.deaths += 1
		else:
			c.runs_completed += 1
		CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, false)
	assert_eq(tide.dose_n, 1, "one DOSE after four netruns")
	assert_eq(tide.dose_cards().size(), 1)


# --------------------------------------------------------------------------------------- breach and re-take
func _exploit_sites() -> Array[SiteData]:
	var out: Array[SiteData] = []
	for s in _corp.city_grid.sites:
		if s != null and s.objective == RC.SiteObjective.EXPLOIT:
			out.append(s)
	out.sort_custom(func(a: SiteData, b: SiteData) -> bool: return String(a.id) < String(b.id))
	return out


func test_the_breach_has_one_retry_then_the_exploits_are_spent() -> void:
	var c := _campaign()
	for s in _exploit_sites():
		c.exploits.append(s.exploit_type)
	assert_eq(c.exploits.size(), 3)
	c.deaths += 1
	CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, true)
	assert_eq(c.corp_theme.solace.tide.breach_fails, 1)
	assert_eq(c.exploits.size(), 3, "the first failure keeps the Exploits")
	c.deaths += 1
	CampaignRules.on_run_closed(c, _corp, _cfg, _lookup, true)
	assert_eq(c.exploits.size(), 0, "the second failure spends them")
	assert_eq(c.corp_theme.solace.tide.breach_fails, 0)
	# the same counters as the core rule
	var st := SolaceTideState.new()
	st.held = [&"x"]
	assert_false(SolaceTideRules.breach_retry(st, _cfg))
	assert_true(SolaceTideRules.breach_retry(st, _cfg))
	assert_eq(st.held.size(), 0)


func test_a_retake_run_restores_one_exploit_and_pays_its_heat_again() -> void:
	var c := _campaign()
	var sites := _exploit_sites()
	var first := sites[0]
	# own the Exploit Site: clear and claim it through the grid directly
	c.grid.sites[first.id]["status"] = GridState.SiteStatus.CLAIMED
	c.grid.sites[first.id]["node_type"] = "relay"
	assert_true(CampaignRules.is_retake(c, first))
	var st := SolaceTideCampaign.load_state(c, _corp, _cfg)
	var board := SolaceTideCampaign.board_for(_corp, _cfg)
	assert_true(SolaceTideRules.retake_sites(st, board).has(first.id), "the core rule agrees")
	var ids: Array[StringName] = []
	for s in CampaignRules.launchable_sites(c, _corp, _cfg):
		ids.append(s.id)
	assert_true(ids.has(first.id), "launchable while live and its Exploit is not held")
	assert_eq(CampaignRules.run_kind_for(c, first), "netrun")
	var beats := c.story_beats_revealed
	var heat := c.heat
	var events := CampaignRules.on_run_completed(c, _corp, _cfg, _run(first.id), _lookup)
	assert_true(c.has_exploit(first.exploit_type))
	assert_true(c.grid.is_claimed(first.id), "the Site stays the Cell's")
	assert_eq(c.heat - heat, _cfg.exploit_heat, "the Exploit Heat is paid again")
	assert_eq(c.story_beats_revealed, beats, "no second story beat")
	assert_false(CampaignRules.is_retake(c, first), "held again: no longer a re-take")
	assert_gt(events.size(), 0)
	st = SolaceTideCampaign.load_state(c, _corp, _cfg)
	assert_false(SolaceTideRules.retake_sites(st, board).has(first.id))


# --------------------------------------------------------------------------------------- R-C, CLEAN, R-F
func test_armory_assets_and_stationed_operatives_become_cards() -> void:
	var c := _campaign()
	var tide := c.corp_theme.solace.tide
	var n := tide.deck.size()
	for pair in [[&"turret", "D", "GUARD"], [&"ice_lock", "N", "JAM"], [&"decoy", "E", "SHIFT"]]:
		var card := SolaceTideCampaign.asset_banked(c, _cfg, _lookup, pair[0])
		assert_eq([card[1], card[2]], [pair[1], pair[2]], "%s" % pair[0])
	assert_eq(tide.deck.size(), n + 3)
	assert_eq(tide.asset_n, 3)
	# a stationed operative adds its class card for the raid, never to the saved deck
	var site: StringName = _ring()[0]
	CampaignRules.on_run_completed(c, _corp, _cfg, _run(site))
	CampaignRules.claim(c, _corp, _cfg, _lookup, site, &"safehouse")  # a Safehouse has a station slot
	var op := c.living_operatives()[0]
	CampaignRules.station(c, _lookup, op.id, site)
	assert_eq(CampaignRules.stationed_site(c, op.id), site)
	var st := SolaceTideCampaign.load_state(c, _corp, _cfg)
	var want := _cfg.solace_tide_class_card(op.class_id)
	var found := false
	for card in st.deck:
		if card[0] == SolaceTideCampaign.CLASS_CARD_PREFIX + String(op.id):
			found = true
			assert_eq([card[1], card[2]], [want[1], want[2]])
	assert_true(found, "the class card joins the raid deck")
	SolaceTideCampaign.store_state(c, st)
	for card in c.corp_theme.solace.tide.deck:
		assert_false(String(card[0]).begins_with(SolaceTideCampaign.CLASS_CARD_PREFIX), "never saved")
	assert_eq(_cfg.validate().size(), 0, "the mapping validates")


func test_clean_removes_the_highest_infected_card_for_its_price() -> void:
	var c := _campaign()
	assert_ne(SolaceTideCampaign.clean_error(c, _cfg), "", "nothing to clean")
	var tide := c.corp_theme.solace.tide
	SolaceTideRules.add_infected(tide, [&"t1_a"])
	SolaceTideRules.add_infected(tide, [&"t1_b"])
	c.schematics = _cfg.solace_tide_clean_price - 1
	assert_ne(SolaceTideCampaign.clean_error(c, _cfg), "", "too few Schematics")
	c.schematics = 50
	CampaignRules.tide_hq_step(c, _cfg, _lookup, [&"", "CLEAN", false])
	assert_eq(SolaceTideCampaign.infected_count(c), 1)
	assert_eq(c.schematics, 50 - _cfg.solace_tide_clean_price)
	for card in tide.deck:
		assert_ne(card[0], "w001", "the highest id went")
	assert_eq(tide.deck.filter(func(card: Array) -> bool: return card[0] == "w000").size(), 1)


func test_the_hq_step_follows_the_campaigns_own_repair_rules() -> void:
	var c := _campaign()
	var owned := _own(c, 1)
	c.grid.site(owned[0])["condition"] = GridState.Condition.DOWN
	c.grid.home_integrity = c.grid.home_max_integrity - 5
	var cost := CampaignRules.repair_cost(c, _cfg, _lookup, owned[0])
	var home_cost := CampaignRules.home_repair_price(c, _cfg)
	var schem := c.schematics
	CampaignRules.tide_hq_step(c, _cfg, _lookup, [owned[0], "", true])
	assert_eq(c.grid.home_integrity, c.grid.home_max_integrity, "PATCH")
	assert_eq(int(c.grid.site(owned[0])["condition"]), GridState.Condition.OK, "REPAIR")
	assert_eq(c.schematics, schem - cost - home_cost, "by the campaign's own prices")


func test_the_boss_grows_with_the_infected_count() -> void:
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.solace_tide_boss_hp_pct_per_infected = 5
	var c := _campaign()
	assert_false(CampaignRules.breach_overrides(c, _corp, cfg).has("boss_hp_pct"), "0 INFECTED: unchanged")
	assert_eq(CampaignRules.breach_overrides(c, _corp, cfg), CampaignRules.boss_overrides(c, _corp))
	var tide := c.corp_theme.solace.tide
	SolaceTideRules.add_infected(tide, [&"t1_a", &"t1_b", &"t1_c"])
	var o := CampaignRules.breach_overrides(c, _corp, cfg)
	assert_eq(o["boss_hp_pct"], 15)
	var plain := CombatSession.start(CombatFixture.resolver(), &"breaker", [_corp.final_boss.id], 3, &"", 0, CampaignRules.boss_overrides(c, _corp))
	var big := CombatSession.start(CombatFixture.resolver(), &"breaker", [_corp.final_boss.id], 3, &"", 0, o)
	var hp0: int = plain.state.enemies[0].max_hp
	assert_eq(big.state.enemies[0].max_hp, roundi(hp0 * 1.15), "the Genome Core has 15 % more HP")
	cfg.solace_tide_boss_hp_pct_per_infected = 0
	assert_false(CampaignRules.breach_overrides(c, _corp, cfg).has("boss_hp_pct"), "0 = off")
	var other := ContentRegistry.get_content(&"meridian") as CorporationData
	var m := CampaignRules.new_campaign(other, cfg, _lookup, 1, _breaker, GridFixture.home_node())
	assert_eq(SolaceTideCampaign.infected_count(m), 0)
