extends GutTest
## Plan 2 EV-01 (Solace vertical): the event schema extension. Map edits (preview == result, never
## strand the run), pending combat modifiers (shape the next fight, spent per completed fight, the
## setup equals the fight), event fights (stake, payout, no normal-fight count), the event wheel
## (start tick from the `events` stream, nudges, commit == preview), the common-Firmware draw,
## next-raid modifiers (the roll comes from the `events` stream, a raid spends them), and the
## save round trip. The seven authored events validate and the Terminal pool draws only the
## Terminal venue.

const SOLACE_EVENTS: Array[StringName] = [&"ev_sol_courtesy_waiver", &"ev_solace_wellness_hold", &"ev_witness_statement",
	&"ev_sol_payment_plan", &"ev_service_hatch", &"ev_toll_ledger_debt", &"ev_rw_second_hand_rumor"]

var _resolver: CombatResolver
var _cfg: CampaignConfigData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config


func _campaign() -> CampaignState:
	var c := CampaignState.new()
	c.campaign_seed = 99
	c.schematics = _cfg.starting_schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	return c


func _session(seed: int = 11, tier: int = 1) -> NetrunSession:
	return NetrunSession.start(_resolver, _campaign(), &"op_1", tier, &"t1_a", seed)


func _event(id: StringName) -> TerminalEventData:
	return ContentRegistry.get_content(id) as TerminalEventData


## Puts the session on `node` with event `id` open (the Terminal draw is not what is tested here).
func _open(s: NetrunSession, id: StringName, node: StringName = &"L2N0") -> void:
	s.run.current_node_id = node
	s.run.event_id = id
	s.run.phase = RunState.Phase.EVENT


func _events_stream_copy(s: NetrunSession) -> RandomNumberGenerator:
	return RngStreams.from_dict(s.streams.to_dict()).get_stream(EventRules.STREAM)


func _texts(results: Array[Dictionary]) -> Array:
	var out := []
	for r in results:
		out.append(r["text"])
	return out


func _auto_fight(s: NetrunSession) -> void:
	var turns := 0
	while s.in_combat() and turns < 80:
		s.combat.state.player.hp = s.combat.state.player.max_hp
		CombatFixture.land(s.combat.state.player, 0)
		for i in range(s.combat.state.hand.size() - 1, -1, -1):
			if i < s.combat.state.hand.size():
				s.combat_action(CombatAction.play_card(i, s.combat.state.target_id))
		s.combat_action(CombatAction.end_turn())
		turns += 1
	assert_false(s.in_combat(), "fight finished within %d turns" % turns)


func _final_reachable(s: NetrunSession) -> bool:
	var seen := {}
	var queue: Array[StringName] = s.available_nodes()
	var final_id := s.run.map.final_node_id()
	while not queue.is_empty():
		var id: StringName = queue.pop_front()
		if seen.has(id):
			continue
		seen[id] = true
		if id == final_id:
			return true
		for n in s.run.map.get_node(id)["next"]:
			if not s.run.closed_nodes.has(n):
				queue.append(n)
	return false


# --- The authored events -------------------------------------------------------------------

func test_the_authored_events_validate() -> void:
	for id in SOLACE_EVENTS:
		var ev := _event(id)
		assert_not_null(ev, "%s is in the content" % id)
		if ev != null:
			assert_eq(ev.validate(), PackedStringArray(), "%s validates" % id)
			assert_ne(ev.title, "")


func test_the_terminal_pool_draws_only_the_terminal_venue() -> void:
	var pool: Array = _session().pools()["events"]
	for id in [&"ev_sol_courtesy_waiver", &"ev_solace_wellness_hold", &"ev_witness_statement", &"ev_sol_payment_plan", &"ev_service_hatch", &"ev_toll_ledger_debt"]:
		assert_true(pool.has(id), "%s can be rolled at a Terminal" % id)
	assert_false(pool.has(&"ev_rw_second_hand_rumor"), "a RAID_WIN event is not a Terminal event")
	assert_eq(_event(&"ev_rw_second_hand_rumor").venue, TerminalEventData.Venue.RAID_WIN)


func test_schema_validation_catches_bad_data() -> void:
	var wheel := EventWheelData.new()
	var a := EventWheelSliceData.new(); a.label = "a"; a.size_ticks = 10
	var b := EventWheelSliceData.new(); b.label = "b"; b.size_ticks = 10
	wheel.slices = [a, b]
	assert_string_contains(",".join(wheel.validate()), "event_wheel_ticks", "slices that do not fill 30 ticks")
	b.size_ticks = 20
	assert_eq(wheel.validate(), PackedStringArray())
	wheel.max_extra_nudges = 2
	assert_string_contains(",".join(wheel.validate()), "event_wheel_extra_unpriced")
	assert_string_contains(",".join(EventCombatModsData.new().validate()), "combat_mods_empty")
	assert_string_contains(",".join(EventRaidModsData.new().validate()), "raid_mods_empty")
	var fight := EventFightData.new()
	assert_string_contains(",".join(fight.validate()), "event_fight_enemy_missing")
	fight.enemy_id = &"collections_agent"
	fight.stake_min_hp_pct = 40
	assert_string_contains(",".join(fight.validate()), "event_fight_stake_empty")
	var edit := MapEditData.new()
	edit.op = MapEditData.Op.ADD_LINK
	edit.layer_offset = 1
	assert_string_contains(",".join(edit.validate()), "map_edit_link_offset")
	var choice := EventChoiceData.new()
	choice.label = "x"
	choice.event_wheel = wheel
	choice.starts_combat = fight
	assert_string_contains(",".join(choice.validate()), "event_choice_fight_and_wheel")


# --- Map edits -----------------------------------------------------------------------------

func test_map_edit_preview_equals_result_and_changes_nothing() -> void:
	var specs := [[&"ev_solace_wellness_hold", 0], [&"ev_solace_wellness_hold", 1], [&"ev_solace_wellness_hold", 2],
		[&"ev_toll_ledger_debt", 0], [&"ev_toll_ledger_debt", 1], [&"ev_toll_ledger_debt", 2]]
	var succeeded := {}
	for seed in range(1, 7):
		for spec in specs:
			var s := _session(seed)
			_open(s, spec[0])
			s.run.cycles = 100
			var choice := s.current_event().choices[spec[1]]
			var before := s.run.map.graph_hash()
			var preview := s.map_edits_preview(choice.map_edits)
			assert_eq(s.run.map.graph_hash(), before, "a preview changes no node")
			assert_true(s.run.closed_nodes.is_empty() and s.run.revealed_nodes.is_empty(), "a preview closes and reveals nothing")
			s.choose_event_option(spec[1])
			var result: Array = []
			for e in s.last_events:
				if e["type"] == "map_edit":
					result.append(e["text"])
			assert_eq(result, _texts(preview), "%s choice %d seed %d: the log is the preview" % [spec[0], spec[1], seed])
			for r in preview:
				if r["ok"]:
					succeeded[MapEditData.Op.keys()[r["op"]]] = true
					if r["op"] == MapEditData.Op.ADD_LINK:
						assert_true((s.run.map.get_node(&"L2N0")["next"] as Array).has(r["to"]), "the link exists")
					elif r["op"] == MapEditData.Op.CLOSE_NODE:
						assert_true(s.node_closed(r["to"]))
					elif r["op"] == MapEditData.Op.REVEAL_TYPE:
						for id in r["nodes"]:
							assert_true(s.node_revealed(id))
	for op in ["ADD_LINK", "CLOSE_NODE", "CONVERT_NODE", "REVEAL_TYPE"]:
		assert_true(succeeded.has(op), "%s took effect on some seed" % op)


func test_add_link_picks_the_fewest_inbound_then_the_lowest_id() -> void:
	var s := _session(4)
	var map := s.run.map
	var edit := MapEditData.new()
	edit.op = MapEditData.Op.ADD_LINK
	edit.layer_offset = 2
	var cands: Array = []
	for node in map.nodes_in_layer(4):
		cands.append(node)
	cands.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var ia := MapEditRules.inbound(map, a["id"])
		var ib := MapEditRules.inbound(map, b["id"])
		return ia < ib or (ia == ib and String(a["id"]) < String(b["id"])))
	var r := MapEditRules.preview(map, &"L2N0", [] as Array[StringName], [] as Array[StringName], [edit] as Array[MapEditData])
	assert_eq(r[0]["to"], cands[0]["id"])
	var again := MapEditRules.preview(map, &"L2N0", [] as Array[StringName], [] as Array[StringName], [edit] as Array[MapEditData])
	assert_eq(again, r, "the same map gives the same pick")


func test_close_node_never_strands_the_run() -> void:
	for seed in range(1, 5):
		var s := _session(seed)
		s.run.current_node_id = &"L2N0"
		s.run.phase = RunState.Phase.MAP
		var edit := MapEditData.new()
		edit.op = MapEditData.Op.CLOSE_NODE
		edit.layer_offset = 1
		for i in 6:
			MapEditRules.apply(s.run.map, &"L2N0", s.run.closed_nodes, s.run.revealed_nodes, [edit] as Array[MapEditData])
			assert_false(s.available_nodes().is_empty(), "a node stays enterable (seed %d)" % seed)
			assert_true(_final_reachable(s), "the final node stays reachable (seed %d)" % seed)
		var open := 0
		for node in s.run.map.nodes_in_layer(3):
			if not s.run.closed_nodes.has(node["id"]):
				open += 1
		assert_true(open >= 1)
		for id in s.run.closed_nodes:
			assert_ne(s.run.map.get_node(id)["type"], RC.InfilNodeType.SERVER_RACK, "a Rack is never closed")
		assert_false(s.available_nodes().any(func(id: StringName) -> bool: return s.run.closed_nodes.has(id)), "a closed node is not offered")


func test_skip_layer_bypasses_the_next_layer_unless_it_holds_a_rack() -> void:
	var s := _session(2)
	var edit := MapEditData.new()
	edit.op = MapEditData.Op.SKIP_LAYER
	for layer in range(1, s.run.map.layer_count()):
		var cur := MapGraph.make_id(layer, 0)
		var has_rack := false
		for id in s.run.map.get_node(cur)["next"]:
			has_rack = has_rack or s.run.map.get_node(id)["type"] == RC.InfilNodeType.SERVER_RACK
		var r := MapEditRules.preview(s.run.map, cur, [] as Array[StringName], [] as Array[StringName], [edit] as Array[MapEditData])
		var expect_ok := not has_rack and layer + 1 < s.run.map.layer_count()
		assert_eq(r[0]["ok"], expect_ok, "layer %d: skip %s" % [layer, "allowed" if expect_ok else "refused"])
		if expect_ok:
			for id in r[0]["nodes"]:
				assert_eq(s.run.map.get_node(id)["layer"], layer + 2, "the successors are two layers on")


# --- Pending combat modifiers --------------------------------------------------------------

func _first_fight(s: NetrunSession) -> CombatState:
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat())
	return s.combat.state


func test_next_combat_overrides_shape_the_fight_and_the_setup_equals_it() -> void:
	var base_hp := _first_fight(_session(8)).enemies[0].max_hp
	var s := _session(8)
	var hp_mods := _event(&"ev_sol_courtesy_waiver").choices[1].next_combat_overrides
	s.run.combat_mods = [EventRules.mods_entry(hp_mods)] as Array[Dictionary]
	var copy := RngStreams.from_dict(s.streams.to_dict()).get_stream(&"combat")
	var setup := s._combat_setup(false, false, copy)
	var state := _first_fight(s)
	assert_eq(state.enemies[0].max_hp, maxi(1, roundi(base_hp * 0.85)), "HP -15%")
	assert_eq(state.enemies[0].hp, state.enemies[0].max_hp)
	assert_eq(String(s.combat.setup["enemy_ids"][0]), String(setup["enemy_id"]), "the previewed foe is the fought foe")
	assert_eq(int(s.combat.setup["overrides"]["event_hp_pct"]), -15)
	assert_eq(s.combat.setup["overrides"]["event_resistance_delta"], -1.0)


func test_frozen_nudge_reveal_tier_and_escort_mods() -> void:
	var s := _session(8)
	s.run.combat_mods = [EventRules.mods_entry(_event(&"ev_sol_courtesy_waiver").choices[0].next_combat_overrides),
		EventRules.mods_entry(_event(&"ev_sol_courtesy_waiver").choices[2].next_combat_overrides),
		EventRules.mods_entry(_event(&"ev_witness_statement").choices[1].next_combat_overrides)] as Array[Dictionary]
	var state := _first_fight(s)
	assert_true(state.enemies[0].wheel.respin_skipped, "the enemy starts Frozen: turn 1 skips its respin")
	assert_eq(int(state.flags.get("extra_free_nudges", 0)), 1)
	assert_eq(int(state.flags.get("reveal_phases", 0)), 1)
	var foes := state.enemies.filter(func(e: CombatantState) -> bool: return not e.is_satellite)
	assert_eq(foes.size(), 2, "the escort joins")
	assert_eq(foes[1].source_id, &"collections_agent")
	# Tier delta clamps to the cap.
	var t4 := _session(8, 4)
	var up := EventCombatModsData.new()
	up.tier_delta = 1
	t4.run.combat_mods = [EventRules.mods_entry(up)] as Array[Dictionary]
	_first_fight(t4)
	assert_eq(int(t4.combat.setup["overrides"]["tier"]), _cfg.event_fight_tier_cap)


func test_a_completed_fight_spends_one_charge() -> void:
	var entries := [{"left": 3, "hp_pct": -15}, {"left": 1, "frozen": true}] as Array[Dictionary]
	var after := EventRules.spend(entries)
	assert_eq(after.size(), 1, "a spent entry goes")
	assert_eq(after[0]["left"], 2)
	var s := _session(9)
	var mods := EventCombatModsData.new()
	mods.enemy_hp_pct = -10
	mods.duration_combats = 2
	s.run.combat_mods = [EventRules.mods_entry(mods)] as Array[Dictionary]
	s.enter_node(s.available_nodes()[0])
	_auto_fight(s)
	assert_eq(s.run.combat_mods.size(), 1)
	assert_eq(int(s.run.combat_mods[0]["left"]), 1, "one fight done, one to go")


func test_pending_state_round_trips_through_a_save() -> void:
	var s := _session(5)
	_open(s, &"ev_sol_payment_plan")
	s.choose_event_option(0)
	s.run.combat_mods = [EventRules.mods_entry(_event(&"ev_sol_courtesy_waiver").choices[1].next_combat_overrides)] as Array[Dictionary]
	s.run.closed_nodes = [&"L3N1"] as Array[StringName]
	s.run.revealed_nodes = [&"L4N0"] as Array[StringName]
	var back := NetrunSession.from_dict(_resolver, s.campaign, JSON.parse_string(JSON.stringify(s.to_dict())))
	assert_eq(back.state_hash(), s.state_hash())
	assert_eq(int(back.run.event_wheel["tick"]), int(s.run.event_wheel["tick"]))
	assert_eq(back.run.closed_nodes, s.run.closed_nodes)
	assert_not_null(back.current_event_wheel(), "the wheel is still open after a reload")
	assert_eq(back.run.combat_mods.size(), 1)
	var plain := _session(5)
	assert_false(plain.run.to_dict().has("combat_mods") or plain.run.to_dict().has("event_wheel") or plain.run.to_dict().has("closed_nodes"), "defaults are absent from the save")


# --- Event fights --------------------------------------------------------------------------

func test_an_event_fight_pays_its_payload_and_not_the_normal_rewards() -> void:
	var s := _session(6)
	_open(s, &"ev_witness_statement")
	s.campaign.heat = 10
	var normal_started := s.run.normal_fights_started
	var cycles := s.run.cycles
	s.choose_event_option(0)
	assert_true(s.in_combat())
	assert_eq(String(s.combat.setup["enemy_ids"][0]), "collections_agent")
	assert_eq(int(s.combat.setup["overrides"]["tier"]), 2, "tier +1")
	assert_eq(s.run.normal_fights_started, normal_started, "an event fight is not a normal fight")
	assert_eq(s.run.event_id, &"")
	_auto_fight(s)
	assert_eq(s.run.cycles, cycles + 35, "the payload replaces the Router Cycles")
	assert_eq(s.campaign.heat, 10 + HeatRules.scaled_delta(s.campaign, -2, _cfg), "-2 Heat")
	assert_eq(s.run.pending_rewards.size(), 1, "one Firmware chip and no card offer")
	assert_eq(s.run.pending_rewards[0]["kind"], "firmware")
	assert_eq(s.run.phase, RunState.Phase.REWARD)
	assert_true(s.run.event_fight.is_empty())


func test_the_stake_withholds_the_payload_below_the_line() -> void:
	assert_true(EventRules.stake_held(24, 60, 40), "exactly 40% holds")
	assert_false(EventRules.stake_held(23, 60, 40))
	assert_true(EventRules.stake_held(1, 60, 0), "no stake always holds")
	var s := _session(6)
	s.run.event_fight = {"normal": false, "stake": 40, "win_cycles": 35, "win_heat": -2, "win_firmware": true}
	s.run.operative.hp = 10
	s.run.operative.max_hp = 60
	var cycles := s.run.cycles
	s.last_events = []
	s._event_fight_payout()
	assert_eq(s.run.cycles, cycles, "stake lost: nothing paid")
	assert_true(s.run.pending_rewards.is_empty())
	assert_eq(s.last_events[0]["type"], "event_stake_lost")
	assert_true(s.run.event_fight.is_empty())
	s.run.event_fight = {"normal": false, "stake": 40, "win_cycles": 35, "win_heat": 0, "win_firmware": false}
	s.run.operative.hp = 24
	s._event_fight_payout()
	assert_eq(s.run.cycles, cycles + 35, "stake held: paid")


# --- Event wheel ---------------------------------------------------------------------------

func test_slice_index_covers_all_thirty_ticks_and_wraps() -> void:
	var wheel: EventWheelData = _event(&"ev_sol_payment_plan").choices[0].event_wheel
	var counts := {}
	for t in RC.TICKS:
		var i := EventRules.slice_index(wheel, t)
		counts[i] = int(counts.get(i, 0)) + 1
	for i in wheel.slices.size():
		assert_eq(counts[i], wheel.slices[i].size_ticks, "slice %d holds its ticks" % i)
	assert_eq(EventRules.slice_index(wheel, -1), wheel.slices.size() - 1, "tick -1 wraps to the last slice")
	assert_eq(EventRules.slice_index(wheel, RC.TICKS), 0)


func test_the_wheel_start_tick_comes_from_the_events_stream_once() -> void:
	var ticks := {}
	for seed in range(1, 21):
		var s := _session(seed)
		_open(s, &"ev_sol_payment_plan")
		var expect := _events_stream_copy(s).randi_range(0, RC.TICKS - 1)
		s.choose_event_option(0)
		assert_eq(int(s.run.event_wheel["tick"]), expect, "seed %d: the start tick is the next events draw" % seed)
		assert_eq(s.run.phase, RunState.Phase.EVENT, "the event stays open on the wheel")
		assert_eq(s.run.event_id, &"ev_sol_payment_plan")
		ticks[expect] = true
	assert_true(ticks.size() > 3, "the start varies with the seed")
	var s2 := _session(3)
	_open(s2, &"ev_sol_payment_plan")
	s2.choose_event_option(0)
	var refused := s2.choose_event_option(0)
	assert_eq(refused[refused.size() - 1]["type"], "refused", "the wheel must be resolved first")


func test_nudges_free_then_paid_and_the_preview_names_the_landing_slice() -> void:
	var s := _session(3)
	_open(s, &"ev_sol_payment_plan")
	s.run.cycles = 100
	s.choose_event_option(0)
	s.run.event_wheel["tick"] = 29
	var wheel := s.current_event_wheel()
	var up := s.event_wheel_preview(1)
	assert_true(up["ok"] and up["free"])
	assert_eq(up["tick"], 0, "the pointer wraps")
	assert_eq(up["slice"], 0)
	s.event_wheel_nudge(1)
	assert_eq(int(s.run.event_wheel["tick"]), 0)
	assert_eq(EventRules.slice_index(wheel, 0), up["slice"], "preview == result")
	s.event_wheel_nudge(1)
	assert_eq(EventRules.free_left(wheel, s.run.event_wheel), 0)
	var no_pay := s.event_wheel_preview(1)
	assert_false(no_pay["free"])
	assert_eq(no_pay["pay"], {"hp": 3, "heat": 1})
	var refused := s.event_wheel_nudge(1)
	assert_eq(refused[0]["type"], "refused", "a paid nudge names its currency")
	var hp := s.run.operative.hp
	s.event_wheel_nudge(1, &"hp")
	assert_eq(s.run.operative.hp, hp - 3)
	var heat := s.campaign.heat
	s.event_wheel_nudge(-1, &"heat")
	assert_true(s.campaign.heat > heat)
	assert_eq(EventRules.extra_left(wheel, s.run.event_wheel), 2)
	var bad_currency := s.event_wheel_nudge(1, &"cycles")
	assert_eq(bad_currency[0]["type"], "refused", "this wheel does not take Cycles")
	s.run.operative.hp = 3
	assert_eq(s.event_wheel_nudge(1, &"hp")[0]["type"], "refused", "a nudge cannot flatline the operative")
	s.event_wheel_nudge(1, &"heat")
	s.event_wheel_nudge(1, &"heat")
	assert_false(s.event_wheel_preview(1)["ok"], "no nudges left")
	assert_eq(s.event_wheel_nudge(1, &"heat")[0]["type"], "refused")


func test_committing_the_wheel_resolves_the_slice_under_the_pointer() -> void:
	var s := _session(3)
	_open(s, &"ev_sol_payment_plan")
	s.campaign.heat = 10
	s.choose_event_option(0)
	s.run.event_wheel["tick"] = 1  # Debt Forgiven: +45 Cycles, -1 Heat
	var cycles := s.run.cycles
	s.event_wheel_commit()
	assert_eq(s.run.cycles, cycles + 45)
	assert_true(s.campaign.heat < 10)
	assert_eq(s.run.event_id, &"")
	assert_true(s.run.event_wheel.is_empty())
	assert_eq(s.run.phase, RunState.Phase.MAP)
	# The clamped fee: Processing Fee never takes the Cycles below zero.
	var f := _session(3)
	_open(f, &"ev_sol_payment_plan")
	f.choose_event_option(0)
	f.run.event_wheel["tick"] = 16  # Processing Fee (ticks 14..20)
	f.run.cycles = 5
	f.event_wheel_commit()
	assert_eq(f.run.cycles, 0)
	# Referral: a fight with +1 Heat on entry and the normal rewards.
	var r := _session(3)
	_open(r, &"ev_sol_payment_plan")
	r.campaign.heat = 10
	r.choose_event_option(0)
	r.run.event_wheel["tick"] = 28
	r.event_wheel_commit()
	assert_true(r.in_combat())
	assert_eq(r.campaign.heat, 10 + HeatRules.scaled_delta(r.campaign, 1, _cfg), "+1 Heat on entry")
	assert_true(bool(r.run.event_fight["normal"]), "the Referral pays the normal rewards")
	assert_eq(String(r.combat.setup["enemy_ids"][0]), "collections_agent")


func test_the_hatch_wheel_skip_and_firmware_slices() -> void:
	var sk := _session(2)
	_open(sk, &"ev_service_hatch", &"L2N0")
	sk.choose_event_option(0)
	sk.run.event_wheel["tick"] = 12  # Skip (ticks 11..15)
	var preview := sk.map_edits_preview(sk.event_wheel_slice().map_edits)
	sk.event_wheel_commit()
	assert_eq(sk.last_events.filter(func(e: Dictionary) -> bool: return e["type"] == "map_edit").map(func(e: Dictionary) -> String: return e["text"]), _texts(preview))
	var fw := _session(2)
	_open(fw, &"ev_service_hatch")
	fw.choose_event_option(0)
	fw.run.event_wheel["tick"] = 27  # Loose cable (ticks 26..29)
	var pool: Array = fw.pools()["common_firmware"]
	var expect: StringName = pool[_events_stream_copy(fw).randi_range(0, pool.size() - 1)]
	fw.event_wheel_commit()
	assert_eq(fw.run.pending_rewards.size(), 1)
	assert_eq(fw.run.pending_rewards[0]["options"], [String(expect)], "the chip is the next events draw")
	assert_eq(fw.run.phase, RunState.Phase.REWARD)
	var gp := _session(2)
	_open(gp, &"ev_service_hatch")
	gp.choose_event_option(0)
	gp.run.event_wheel["tick"] = 22  # Guard post (ticks 20..25)
	gp.event_wheel_commit()
	assert_true(gp.in_combat())
	assert_eq(String(gp.combat.setup["enemy_ids"][0]), "patrol_unit")
	assert_false(bool(gp.run.event_fight["normal"]))


# --- Next-raid modifiers -------------------------------------------------------------------

func test_next_raid_overrides_roll_from_the_events_stream_and_a_raid_spends_them() -> void:
	var hits := 0
	for seed in range(1, 31):
		var s := _session(seed)
		_open(s, &"ev_rw_second_hand_rumor")
		var predicted := _events_stream_copy(s).randi_range(1, 100) <= 30
		s.choose_event_option(2)
		assert_eq(int(s.campaign.next_raid_mods.get("extra_waves", 0)), 1 if predicted else 0, "seed %d: the 30%% roll is the next events draw" % seed)
		hits += 1 if predicted else 0
	assert_true(hits > 0 and hits < 30, "the rumor is sometimes true")
	var s := _session(7)
	_open(s, &"ev_rw_second_hand_rumor")
	s.run.cycles = 50
	assert_eq(s.choice_costs(s.current_event().choices[2]), "+25 Cycles, next raid +1 wave ?", "the preview shows ? where the stream is read")
	s.choose_event_option(1)
	assert_eq(s.campaign.next_raid_mods["strength_pct"], 10)
	assert_eq(s.campaign.next_raid_mods["extra_waves"], 0)
	var c := _session(7)
	_open(c, &"ev_rw_second_hand_rumor")
	c.run.cycles = 50
	c.choose_event_option(0)
	assert_eq(c.run.cycles, 30)
	assert_true(bool(c.campaign.next_raid_mods["scout"]))


func test_a_raid_reads_and_spends_the_event_modifier() -> void:
	var lookup := GridFixture.lookup()
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var breaker := ContentRegistry.get_content(&"breaker") as ClassData
	var c := CampaignRules.new_campaign(corp, _cfg, lookup, 1, breaker, GridFixture.home_node())
	var base_pct := CampaignRules.raid_strength_pct(c, _cfg)
	var base_waves := CampaignRules.raid_extra_waves(c, _cfg)
	c.next_raid_mods = EventRules.raid_merge({}, EventRules.raid_entry(_event(&"ev_rw_second_hand_rumor").choices[2].next_raid_overrides, true))
	c.next_raid_mods = EventRules.raid_merge(c.next_raid_mods, {"strength_pct": 10})
	assert_eq(CampaignRules.raid_strength_pct(c, _cfg), base_pct + 10.0)
	assert_eq(CampaignRules.raid_extra_waves(c, _cfg), base_waves + 1)
	var back := CampaignState.from_dict(c.to_dict())
	assert_eq(back.next_raid_mods, c.next_raid_mods, "the campaign save keeps it")
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	CampaignRules.fight_raid(c, corp, _cfg, lookup, c.pending_raids[0])
	assert_true(c.next_raid_mods.is_empty(), "the raid spent it")
	assert_eq(CampaignRules.raid_strength_pct(c, _cfg), base_pct)
	assert_false(CampaignState.new().to_dict().has("next_raid_mods"), "absent at default")
