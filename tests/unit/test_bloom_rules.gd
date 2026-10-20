extends GutTest
## Plan 2 WH-11 (Solace THE BLOOM), fast tier: the virus front is integer milli, moves on node
## entry and when a fight ends (frozen inside fights), CAUGHT is the Q24.1 operative loss (the
## raid is untouched), the preview is the result with nothing random, numbers only from config,
## and the block round-trips the (v5, additive) save.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _solace: CorporationData
var _meridian: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_solace = ContentRegistry.get_content(&"solace") as CorporationData
	_meridian = ContentRegistry.get_content(&"meridian") as CorporationData


func _session(tier: int = 3, seed: int = 5, corp: CorporationData = null) -> NetrunSession:
	if corp == null:
		corp = _solace
	var c := CampaignRules.new_campaign(corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	return NetrunSession.start(_resolver, c, c.roster[0].id, tier, &"t1_a", seed, corp)


func _bloom(s: NetrunSession) -> BloomState:
	return s.run.corp_theme.solace


func _first_of_type(s: NetrunSession, type: int) -> StringName:
	for id in s.available_nodes():
		if int(s.run.map.get_node(id)["type"]) == type:
			return id
	return &""


func _win_fight(s: NetrunSession) -> int:
	for e in s.combat.state.living_enemies():
		e.hp = 1
	s.combat.state.player.hp = 20
	var turns := 0
	while s.in_combat() and turns < 10:
		turns += 1
		CombatFixture.land(s.combat.state.player, 0, 0)
		s.combat_action(CombatAction.end_turn())
	return turns


# --- Start, bands, entry ------------------------------------------------------------

func test_start_values_come_from_config_per_tier_and_no_tier_gets_a_free_dose() -> void:
	for tier in [1, 2, 3, 4]:
		var s := _session(tier)
		var b := _bloom(s)
		assert_true(b.enabled)
		assert_eq(b.front_milli, -int(_cfg.bloom_start_gap_milli_by_tier[tier - 1]), "tier %d" % tier)
		assert_eq(b.doses_held, 0, "S5: no free dose at any tier")
		assert_eq(s.bloom_band(), BloomRules.Band.DORMANT, "DORMANT until a node is entered")


func test_disabled_on_other_corporations() -> void:
	var s := _session(3, 5, _meridian)
	assert_false(_bloom(s).enabled)
	assert_true(_bloom(s).is_default(), "no block, no hash change")
	assert_eq(s.theme_chip(), {})
	var id := s.available_nodes()[0]
	s.enter_node(id)
	assert_eq(_bloom(s).front_milli, 0, "the front never moves off Solace")


func test_node_entry_moves_the_operative_and_the_front() -> void:
	var s := _session(3)
	var b := _bloom(s)
	var id := s.available_nodes()[0]
	var predicted := int(s.bloom_preview()[id]["gap_milli"])
	s.enter_node(id)
	assert_eq(b.layer_milli, 1000)
	assert_eq(b.front_milli, -int(_cfg.bloom_start_gap_milli_by_tier[2]) + int(_cfg.bloom_pace_node_milli_by_tier[2]))
	assert_eq(BloomRules.gap_milli(b), predicted, "preview == result")


func test_state_bands_are_exact_at_each_boundary() -> void:
	var c := _cfg
	assert_eq(BloomRules.band_for_gap(c.bloom_close_gap_milli + 1, c), BloomRules.Band.CREEPING)
	assert_eq(BloomRules.band_for_gap(c.bloom_close_gap_milli, c), BloomRules.Band.CLOSE)
	assert_eq(BloomRules.band_for_gap(c.bloom_catch_gap_milli + 1, c), BloomRules.Band.CLOSE)
	assert_eq(BloomRules.band_for_gap(c.bloom_catch_gap_milli, c), BloomRules.Band.CATCHING)
	assert_eq(BloomRules.band_for_gap(1, c), BloomRules.Band.CATCHING)
	assert_eq(BloomRules.band_for_gap(0, c), BloomRules.Band.CAUGHT)
	assert_eq(BloomRules.band_for_gap(-300, c), BloomRules.Band.CAUGHT)


# --- Fights ------------------------------------------------------------------------

func test_front_is_frozen_in_a_fight_and_advances_turns_times_pace_at_its_end() -> void:
	var s := _session(3)
	var b := _bloom(s)
	var router := _first_of_type(s, RC.InfilNodeType.ROUTER)
	if router == &"":
		pending("no Router on the first layer for this seed")
		return
	s.enter_node(router)
	assert_true(s.in_combat())
	var at_entry := b.front_milli
	s.combat_action(CombatAction.end_turn())
	assert_eq(b.front_milli, at_entry, "frozen inside the fight")
	assert_false(b.caught, "a fight never latches CAUGHT")
	s.combat.state.turn = 4  # the fight's turn count at its end
	_win_fight(s)

	assert_false(s.in_combat())
	assert_false(b.caught)
	assert_gt(b.front_milli, at_entry, "the fight's turns advanced the front")
	assert_eq((b.front_milli - at_entry) % _cfg.bloom_pace_turn_milli, 0, "whole turns of pace_turn")


func test_end_fight_pace_is_turns_times_config() -> void:
	var b := BloomState.new()
	b.enabled = true
	assert_eq(BloomRules.fight_pace(b, _cfg, 7), 7 * _cfg.bloom_pace_turn_milli)
	BloomRules.end_fight(b, _cfg, 3)
	assert_eq(b.front_milli, 3 * _cfg.bloom_pace_turn_milli)


func test_virus_scales_pace_once_rounded_down_minimum_one() -> void:
	var b := BloomState.new()
	b.key_virus = true
	assert_eq(BloomRules.scaled(b, _cfg, 650), 650 * _cfg.bloom_virus_pace_pct / 100)
	assert_eq(BloomRules.scaled(b, _cfg, 100), 75)
	assert_eq(BloomRules.scaled(b, _cfg, 1), 1, "minimum 1")
	b.key_virus = false
	assert_eq(BloomRules.scaled(b, _cfg, 650), 650)


# --- Caught (Q24.1) ----------------------------------------------------------------

func test_caught_on_entry_loses_the_operative_and_abandons_the_netrun_raid_unchanged() -> void:
	var s := _session(3)
	var b := _bloom(s)
	b.front_milli = 0  # the front is on the start; entering layer 1 with pace 650 leaves gap 350: set tighter
	b.front_milli = 1000 - 100  # gap after entry <= 0
	var raid_theme_before := s.campaign.corp_theme.raid.to_dict()
	var id := s.available_nodes()[0]
	assert_true(bool(s.bloom_preview()[id]["caught"]), "the preview warns CAUGHT before commit")
	var op_id := s.run.operative.id
	s.enter_node(id)
	assert_true(b.caught)
	assert_true(s.run.is_over())
	assert_eq(s.run.outcome, RunState.Outcome.DIED, "the Q24.1 path")
	assert_false(s.campaign.get_operative(op_id).alive, "operative lost")
	assert_eq(s.campaign.corp_theme.raid.to_dict(), raid_theme_before, "raid state unchanged")


func test_caught_after_a_fight_uses_the_same_path() -> void:
	var s := _session(3)
	var b := _bloom(s)
	var router := _first_of_type(s, RC.InfilNodeType.ROUTER)
	if router == &"":
		pending("no Router on the first layer for this seed")
		return
	s.enter_node(router)
	b.front_milli = b.layer_milli - 50  # one more turn of pace catches it
	_win_fight(s)
	assert_true(b.caught)
	assert_eq(s.run.outcome, RunState.Outcome.DIED)


# --- Doses -------------------------------------------------------------------------

func test_dose_pushes_the_front_back_and_clamps_the_gap_at_max() -> void:
	var b := BloomState.new()
	b.enabled = true
	b.layer_milli = 3000
	b.front_milli = 0
	BloomRules.push(b, _cfg)
	assert_eq(b.front_milli, -_cfg.bloom_dose_push_milli)
	b.front_milli = 3000 - _cfg.bloom_max_gap_milli + 200
	BloomRules.push(b, _cfg)
	assert_eq(BloomRules.gap_milli(b), _cfg.bloom_max_gap_milli, "clamped at max_gap")


func test_t1_starts_with_zero_doses_and_a_bought_dose_is_used_and_counted() -> void:
	var s := _session(1)
	var b := _bloom(s)
	assert_eq(b.doses_held, 0)
	assert_eq(b.front_milli, -int(_cfg.bloom_start_gap_milli_by_tier[0]), "the wide T1 gap")
	b.doses_held = 1
	s.enter_node(s.available_nodes()[0])
	if s.run.phase != RunState.Phase.MAP:
		s.run.phase = RunState.Phase.MAP
		s.combat = null
	var preview := s.dose_preview()
	var gap := BloomRules.gap_milli(b)
	s.use_dose()
	assert_eq(b.doses_held, 0)
	assert_eq(b.doses_taken, 1)
	assert_eq(BloomRules.gap_milli(b), preview, "dose preview == result")
	assert_eq(BloomRules.gap_milli(b), mini(gap + _cfg.bloom_dose_push_milli, _cfg.bloom_max_gap_milli))
	s.run.phase = RunState.Phase.SHOP
	s.run.cycles = _cfg.bloom_dose_price
	s.buy_dose()
	assert_eq(s.run.cycles, 0)
	assert_eq(b.doses_held, 1)


# --- HQ ----------------------------------------------------------------------------

func test_hq_across_costs_pace_cross_and_the_preview_equals_the_result() -> void:
	var b := BloomState.new()
	BloomRules.begin(b, _cfg, _solace, 3, true)
	assert_true(b.enabled)
	assert_eq(b.front_milli, -_cfg.bloom_hq_start_gap_milli)
	var plain := BloomRules.gap_after_entry(b, _cfg, 3, 2)
	var across := BloomRules.gap_after_entry(b, _cfg, 3, 2, true)
	assert_eq(plain - across, _cfg.bloom_pace_cross_milli)
	BloomRules.enter(b, _cfg, 3, 2, true)
	assert_eq(BloomRules.gap_milli(b), across)
	assert_eq(b.front_milli, -_cfg.bloom_hq_start_gap_milli + _cfg.bloom_hq_pace_node_milli + _cfg.bloom_pace_cross_milli)


func test_ward_rest_calls_dose_push_without_a_dose() -> void:
	var b := BloomState.new()
	BloomRules.begin(b, _cfg, _solace, 3, true)
	BloomRules.enter(b, _cfg, 3, 3)
	var gap := BloomRules.gap_milli(b)
	BloomRules.ward_rest(b, _cfg)
	assert_eq(BloomRules.gap_milli(b), mini(gap + _cfg.bloom_dose_push_milli, _cfg.bloom_max_gap_milli))
	assert_eq(b.doses_held, 0)


func test_infected_rooms_are_the_same_layers_on_both_towers() -> void:
	var b := BloomState.new()
	b.enabled = true
	b.front_milli = 2500
	assert_true(BloomRules.room_infected(b, 1))
	assert_true(BloomRules.room_infected(b, 2))
	assert_false(BloomRules.room_infected(b, 3), "layer <= floor(front)")
	b.front_milli = -3000
	assert_false(BloomRules.room_infected(b, 1), "a front still behind the start infects nothing")


func test_intel_reveals_the_whole_ladder_gap_exactly() -> void:
	var b := BloomState.new()
	BloomRules.begin(b, _cfg, _solace, 3, true)
	var gaps := BloomRules.ladder_gaps(b, _cfg, 3, [1, 4, 8])
	for l in [1, 4, 8]:
		var c := b.copy() as BloomState
		for step in l:
			BloomRules.enter(c, _cfg, 3, step + 1)
		assert_eq(int(gaps[l]), BloomRules.gap_milli(c), "layer %d" % l)


func test_session_preview_with_intel_lists_every_unvisited_node_in_id_order() -> void:
	var s := _session(3)
	s.bloom_set_keys(true, false)
	var p := s.bloom_preview()
	assert_eq(p.size(), s.run.map.node_count())
	for id in s.available_nodes():
		assert_true(p.has(id))
	for v in p.values():
		assert_true(v is Dictionary and (v as Dictionary).has("gap_milli"))
		assert_false(str(v).contains("?"), "nothing random: no ? in the preview")


# --- Chip, determinism, save, config -------------------------------------------------

func test_theme_chip_value_is_the_gap() -> void:
	var s := _session(3)
	assert_eq(s.theme_chip()["value"], "3.0", "gap 3000 at the T3 start")
	assert_eq(NetrunSession.bloom_gap_text(1850), "1.8")
	assert_eq(NetrunSession.bloom_gap_text(-50), "0.0")
	s.enter_node(s.available_nodes()[0])
	var chip := s.theme_chip()
	assert_eq(chip["key"], "FRONT")
	assert_eq(chip["value"], NetrunSession.bloom_gap_text(BloomRules.gap_milli(_bloom(s))))


func test_same_seed_and_inputs_give_the_same_front_and_hash() -> void:
	var out: Array = []
	for i in 2:
		var s := _session(3, 77)
		s.enter_node(s.available_nodes()[0])
		if s.in_combat():
			_win_fight(s)
		out.append([_bloom(s).front_milli, _bloom(s).layer_milli, s.state_hash()])
	assert_eq(out[0], out[1])


func test_block_round_trips_the_save_through_json() -> void:
	var s := _session(1)
	s.enter_node(s.available_nodes()[0])
	_bloom(s).key_virus = true
	var d: Dictionary = JSON.parse_string(JSON.stringify(s.run.to_dict()))
	var r := RunState.from_dict(d)
	assert_eq(r.corp_theme.solace.to_dict(), _bloom(s).to_dict())
	assert_eq(r.state_hash(), s.run.state_hash(), "the hash includes the block")
	assert_true(r.corp_theme.solace.enabled)


func test_an_inactive_bloom_leaves_the_hash_as_before() -> void:
	var s := _session(3, 5, _meridian)
	assert_false(s.run.to_dict().has("corp_theme"))


func test_retired_tolls_and_debts_have_no_config_keys() -> void:
	var banned := ["copay", "co_pay", "referral", "audit", "quarantine", "toll", "debt"]
	var cfg_script := _cfg.get_script() as Script
	for p in cfg_script.get_script_property_list():
		var n := String(p["name"]).to_lower()
		for w in banned:
			assert_false(n.contains(w), "config key %s names the retired %s mechanic" % [n, w])


func test_bloom_code_has_no_inline_pace_numbers() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/core/bloom_rules.gd")
	for bad in ["650", "500", "700", "1000 *", "75", "5000", "2000"]:
		assert_false(src.contains(bad), "bloom_rules.gd holds only config reads (found %s)" % bad)


# --- Solace v2: Heat pace, Exploit forms ---------------------------------------------

func _heat_to_band(s: NetrunSession, band: int) -> void:
	var levels := HeatRules.band_levels(s.campaign, _cfg)
	s.campaign.heat = 0 if band == 0 else int(levels[band - 1])


func test_every_fight_class_pays_the_turn_cost_bosses_included() -> void:
	# S3: there is no class exemption. The same fight (4 turns) costs the same front for a normal,
	# an elite, a mini-boss and a boss node.
	var cost := {}
	for cls in ["normal", "elite", "mini_boss", "boss"]:
		var s := _session(3)
		var router := _first_of_type(s, RC.InfilNodeType.ROUTER)
		if router == &"":
			pending("no Router on the first layer for this seed")
			return
		s.enter_node(router)
		var node := s.run.map.get_node(router)
		node["elite"] = cls == "elite"
		node["mini_boss"] = cls == "mini_boss"
		node["boss"] = cls == "boss"
		var b := _bloom(s)
		var at := b.front_milli
		s.combat.state.turn = 4
		_win_fight(s)
		cost[cls] = b.front_milli - at
	for cls in cost:
		assert_eq(cost[cls], cost["normal"], "%s pays like a normal fight" % cls)
	assert_gt(int(cost["normal"]), 0)


func test_heat_band_speeds_the_pace_floored_minimum_one() -> void:
	for band in 5:
		var s := _session(3)
		_heat_to_band(s, band)
		assert_eq(SolaceRaidRules.heat_band_index(s.campaign, _cfg), band)
		var id := s.available_nodes()[0]
		var predicted := int(s.bloom_preview()[id]["gap_milli"])
		var b := _bloom(s)
		var before := b.front_milli
		s.enter_node(id)
		var pct := int(_cfg.bloom_pace_heat_pct_by_band[band])
		assert_eq(b.front_milli - before, maxi(1, int(_cfg.bloom_pace_node_milli_by_tier[2]) * pct / 100), "band %d" % band)
		assert_eq(BloomRules.gap_milli(b), predicted, "preview == result at band %d" % band)
	var tiny := BloomState.new()
	assert_eq(BloomRules.scaled(tiny, _cfg, 1), 1)
	assert_eq(_cfg.bloom_pace_heat_pct_by_band[4], 160, "SO4: 160 percent at PURGE")


func test_heat_also_scales_the_turn_cost() -> void:
	var b := BloomState.new()
	b.heat_pct = 160
	assert_eq(BloomRules.fight_pace(b, _cfg, 3), 3 * (_cfg.bloom_pace_turn_milli * 160 / 100))


func test_virus_scales_pace_once_with_heat_no_drift() -> void:
	var b := BloomState.new()
	b.key_virus = true
	b.heat_pct = 110
	var one := BloomRules.scaled(b, _cfg, 650)
	assert_eq(one, 650 * 110 * 75 / 10000, "one floor over the product")
	assert_eq(BloomRules.scaled(b, _cfg, 650), one, "the same every call")


func test_breach_setback_fires_once_and_across_is_free() -> void:
	var b := BloomState.new()
	BloomRules.begin(b, _cfg, _solace, 3, true)
	b.key_breach = true
	var gap_breach := BloomRules.gap_after_entry(b, _cfg, 3, 2, true)
	var no_key := b.copy() as BloomState
	no_key.key_breach = false
	assert_eq(gap_breach - BloomRules.gap_after_entry(no_key, _cfg, 3, 2, true), _cfg.bloom_breach_setback_milli + _cfg.bloom_pace_cross_milli, "setback plus the free ACROSS")
	var front0 := b.front_milli
	BloomRules.enter(b, _cfg, 3, 2, true)
	assert_eq(BloomRules.gap_milli(b), gap_breach, "preview == result")
	assert_true(b.breach_applied)
	assert_eq(b.front_milli, front0 + _cfg.bloom_hq_pace_node_milli - _cfg.bloom_breach_setback_milli, "no ACROSS toll")
	var front1 := b.front_milli
	BloomRules.enter(b, _cfg, 3, 3, true)
	assert_eq(b.front_milli, front1 + _cfg.bloom_hq_pace_node_milli, "the second entry has no setback")


func test_intel_cuts_the_turn_cost() -> void:
	var b := BloomState.new()
	b.key_intel = true
	assert_eq(BloomRules.fight_pace(b, _cfg, 4), 4 * (_cfg.bloom_pace_turn_milli * _cfg.bloom_intel_turn_pct / 100))
	assert_eq(BloomRules.scaled(b, _cfg, 650), 650, "Intel does not slow node pace")


func test_all_three_exploits_stack_to_the_product_formula() -> void:
	var b := BloomState.new()
	BloomRules.begin(b, _cfg, _solace, 3, true)
	b.key_intel = true
	b.key_virus = true
	b.key_breach = true
	b.heat_pct = 110
	var node := _cfg.bloom_hq_pace_node_milli * 110 * 75 / 10000
	var turn := _cfg.bloom_pace_turn_milli * 110 * 75 * _cfg.bloom_intel_turn_pct / 1000000
	assert_eq(BloomRules.entry_pace(b, _cfg, 3, true), node, "ACROSS is free")
	assert_eq(BloomRules.fight_pace(b, _cfg, 4), 4 * turn)
	var front0 := b.front_milli
	BloomRules.enter(b, _cfg, 3, 1)
	assert_eq(b.front_milli, front0 + node - _cfg.bloom_breach_setback_milli)
	BloomRules.end_fight(b, _cfg, 4)
	assert_eq(b.front_milli, front0 + node - _cfg.bloom_breach_setback_milli + 4 * turn, "no cap on the stack (SO3)")


func test_a_session_loads_its_keys_from_the_exploits_held() -> void:
	var c := CampaignRules.new_campaign(_solace, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var none := NetrunSession.start(_resolver, c, c.roster[0].id, 3, &"t1_a", 5, _solace)
	assert_false(_bloom(none).key_virus or _bloom(none).key_breach or _bloom(none).key_intel)
	var c2 := CampaignRules.new_campaign(_solace, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	c2.exploits.assign([RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS])
	var all := NetrunSession.start(_resolver, c2, c2.roster[0].id, 3, &"t1_a", 5, _solace)
	assert_true(_bloom(all).key_virus and _bloom(all).key_breach and _bloom(all).key_intel)


func test_the_breach_fields_round_trip_and_an_old_save_loads_them_off() -> void:
	var b := BloomState.new()
	b.enabled = true
	b.key_breach = true
	b.breach_applied = true
	b.heat_pct = 125
	var back := BloomState.new()
	back.load_dict(JSON.parse_string(JSON.stringify(b.to_dict())))
	assert_eq(back.to_dict(), b.to_dict())
	var old := BloomState.new()
	old.load_dict({"front_milli": -3000, "enabled": true})
	assert_false(old.breach_applied)
	assert_eq(old.heat_pct, 100)
