extends GutTest
## Netrun rules (M2 acceptance): banking on Rack capture, death loses only unbanked
## loot and adds 10 + tier Heat, completion converts Cycles 10:1 and keeps the deck /
## Firmware / Daemons with Rank +1, quit mid-run (map or combat) and resume identically.

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


func _start(seed: int = 11, tier: int = 1, campaign: CampaignState = null) -> NetrunSession:
	if campaign == null:
		campaign = _campaign()
	return NetrunSession.start(_resolver, campaign, &"op_1", tier, &"t1_a", seed)


## Path of node ids from the current position to the first node matching `pred`.
func _path_to(s: NetrunSession, pred: Callable) -> Array[StringName]:
	var start := s.available_nodes()
	var prev := {}
	var queue: Array[StringName] = start.duplicate()
	for id in start:
		prev[id] = &""
	while not queue.is_empty():
		var id: StringName = queue.pop_front()
		var node := s.run.map.get_node(id)
		if pred.call(node):
			var path: Array[StringName] = []
			var cur := id
			while cur != &"":
				path.push_front(cur)
				cur = prev[cur]
			return path
		for n in node["next"]:
			if not prev.has(n):
				prev[n] = id
				queue.append(n)
	return []


## Fights the current combat to the end like a hurried player; lands the operative on
## its Crit slice each turn and (when `invincible`) keeps its HP topped up.
func _auto_fight(s: NetrunSession, invincible: bool = true) -> void:
	var turns := 0
	while s.in_combat() and turns < 80:
		if invincible:
			s.combat.state.player.hp = s.combat.state.player.max_hp
		CombatFixture.land(s.combat.state.player, 0)
		for i in range(s.combat.state.hand.size() - 1, -1, -1):
			if i < s.combat.state.hand.size():
				s.combat_action(CombatAction.play_card(i, s.combat.state.target_id))
		s.combat_action(CombatAction.end_turn())
		turns += 1
	assert_false(s.in_combat(), "fight finished within %d turns" % turns)


## Clears every pending reward (takes the first option, socketing Firmware in slot 1).
func _settle(s: NetrunSession) -> void:
	while s.run.phase == RunState.Phase.REWARD:
		var offer := s.current_reward()
		if offer["kind"] == "firmware":
			var ev := s.choose_reward(0, 1)
			if ev[ev.size() - 1]["type"] == "refused":
				s.skip_reward()
		else:
			s.choose_reward(0)
	if s.run.phase == RunState.Phase.EVENT:
		s.choose_event_option(s.current_event().choices.size() - 1)
		_settle(s)
	if s.run.phase == RunState.Phase.SHOP:
		s.leave_shop()


func _walk(s: NetrunSession, path: Array[StringName], invincible: bool = true) -> void:
	for id in path:
		s.enter_node(id)
		if s.in_combat():
			_auto_fight(s, invincible)
		_settle(s)
		if s.run.is_over():
			return


func _is_rack_l4(node: Dictionary) -> bool:
	return node["type"] == RC.InfilNodeType.SERVER_RACK and node["layer"] == 4


func _is_final(node: Dictionary) -> bool:
	return node["layer"] == _cfg.map_layers


# --- Start ---------------------------------------------------------------------------------

func test_run_starts_on_the_map_with_a_valid_map_and_a_working_copy() -> void:
	var s := _start()
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_eq(s.run.map.validate(_cfg).size(), 0)
	assert_eq(s.available_nodes().size(), s.run.map.nodes_in_layer(1).size())
	assert_eq(s.run.operative.id, &"op_1")
	assert_eq(s.campaign.runs_started, 1)
	s.run.operative.deck.append(&"twist")
	assert_false(s.campaign.get_operative(&"op_1").deck.has(&"twist"), "the run works on a copy")


func test_entering_a_router_starts_a_combat_against_a_solace_enemy() -> void:
	var s := _start()
	var first := s.available_nodes()[0]
	s.enter_node(first)
	assert_true(s.in_combat())
	assert_eq(s.run.phase, RunState.Phase.COMBAT)
	var enemy := s.combat.state.get_combatant(&"enemy_0")
	assert_true(s.pools()["enemies"].has(enemy.source_id), "%s is a normal Solace enemy" % enemy.source_id)
	assert_false(s.available_nodes().size() > 0, "cannot move during combat")


func test_winning_a_router_gives_cycles_and_a_1_of_3_card_offer() -> void:
	var s := _start()
	s.enter_node(s.available_nodes()[0])
	_auto_fight(s)
	assert_eq(s.run.combats_won, 1)
	assert_true(s.run.cycles >= _cfg.cycles_router_range.x and s.run.cycles <= _cfg.cycles_router_range.y, "router Cycles %d" % s.run.cycles)
	assert_eq(s.run.phase, RunState.Phase.REWARD)
	var offer := s.current_reward()
	assert_eq(offer["kind"], "card")
	assert_eq(offer["options"].size(), 3)
	var deck_size := s.run.operative.deck.size()
	s.choose_reward(1)
	assert_eq(s.run.operative.deck.size(), deck_size + 1)
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_eq(s.run.operative.hp, s.combat.state.player.hp if s.combat != null else s.run.operative.hp)


func test_skipping_a_reward_leaves_the_deck_alone() -> void:
	var s := _start()
	s.enter_node(s.available_nodes()[0])
	_auto_fight(s)
	var deck_size := s.run.operative.deck.size()
	s.skip_reward()
	assert_eq(s.run.operative.deck.size(), deck_size)
	assert_eq(s.run.phase, RunState.Phase.MAP)


# --- Banking -----------------------------------------------------------------------------

func test_rack_capture_banks_schematics_and_assets() -> void:
	var s := _start()
	var path := _path_to(s, _is_rack_l4)
	assert_true(path.size() > 0, "a layer-4 Rack is reachable")
	s.run.unbanked_assets.append(&"turret")
	var heat_before := s.campaign.heat
	_walk(s, path)
	assert_false(s.run.is_over())
	assert_eq(s.run.banked_schematics, _cfg.rack_schematics_by_tier[0], "T1 Rack banks 10 Schematics")
	assert_true(s.run.banked_assets.has(&"turret"), "asset banked on capture")
	assert_false(s.run.unbanked_assets.has(&"turret"))
	assert_true(s.campaign.heat > heat_before, "Rack capture and elite nodes add Heat")
	assert_eq(s.campaign.schematics, _cfg.starting_schematics, "banked Schematics reach the campaign only when the run ends")


func test_rack_offers_1_of_3_daemons() -> void:
	var s := _start()
	var path := _path_to(s, _is_rack_l4)
	for id in path:
		s.enter_node(id)
		if s.in_combat():
			_auto_fight(s)
		if id == path[path.size() - 1]:
			break
		_settle(s)
	var kinds := []
	for offer in s.run.pending_rewards:
		kinds.append(offer["kind"])
	assert_true(kinds.has("daemon"), "Rack offers a Daemon: %s" % [kinds])
	for offer in s.run.pending_rewards:
		if offer["kind"] == "daemon":
			assert_eq(offer["options"].size(), 3)


func test_elite_nodes_add_heat_on_entry_and_offer_firmware() -> void:
	var s := _start()
	var path := _path_to(s, func(n: Dictionary) -> bool: return n["elite"] and n["type"] == RC.InfilNodeType.ROUTER)
	assert_true(path.size() > 0)
	var heat_before := s.campaign.heat
	for i in path.size() - 1:
		s.enter_node(path[i])
		if s.in_combat():
			_auto_fight(s)
		_settle(s)
	heat_before = s.campaign.heat
	s.enter_node(path[path.size() - 1])
	assert_eq(s.campaign.heat, heat_before + _cfg.elite_heat, "elite Heat on entry")
	assert_true(s.pools()["elites"].has(s.combat.state.get_combatant(&"enemy_0").source_id), "elite enemy")
	assert_eq(_campaign().elite_frequency_pct(_cfg), 0.0, "no elite modifier below Heat 25")
	var hot := _campaign()
	hot.heat = 25
	assert_eq(hot.elite_frequency_pct(_cfg), 25.0, "Heat 25 ongoing modifier")
	_auto_fight(s)
	var kinds := []
	for offer in s.run.pending_rewards:
		kinds.append(offer["kind"])
	assert_eq(kinds, ["card", "firmware"])
	assert_eq(s.run.pending_rewards[1]["options"].size(), 2, "Firmware 1-of-2")
	s.choose_reward(0)
	var fw := StringName(String(s.run.pending_rewards[0]["options"][0]))
	var ev := s.choose_reward(0, 1)
	if ev[ev.size() - 1]["type"] != "refused":
		assert_eq(s.run.operative.slot_firmware_ids[1], fw, "socketed into slot 1")


# --- Death -----------------------------------------------------------------------------

func test_death_loses_unbanked_loot_keeps_banked_and_adds_heat() -> void:
	var s := _start()
	var path := _path_to(s, _is_rack_l4)
	s.run.unbanked_assets.append(&"turret")
	_walk(s, path)
	assert_eq(s.run.banked_schematics, 10)
	s.run.unbanked_assets.append(&"decoy")
	var cycles := s.run.cycles
	var schematics_before := s.campaign.schematics
	# Next combat: make the operative fragile, the enemy always hits, the operative never does.
	var next := _path_to(s, func(n: Dictionary) -> bool: return n["type"] == RC.InfilNodeType.ROUTER)
	assert_true(next.size() > 0)
	for i in next.size() - 1:
		s.enter_node(next[i])
		if s.in_combat():
			_auto_fight(s)
		_settle(s)
	s.enter_node(next[next.size() - 1])
	assert_true(s.in_combat())
	var heat_before := s.campaign.heat  # after any elite-entry Heat
	var turns := 0
	while s.in_combat() and turns < 30:
		s.combat.state.player.hp = 1
		s.combat.state.player.block = 0
		CombatFixture.land(s.combat.state.player, 5)
		var enemy := s.combat.state.get_combatant(&"enemy_0")
		var attack_slot := 0
		for i in enemy.wheel.slot_slice_ids.size():
			var slice := _resolver.lookup.get_content(enemy.wheel.slot_slice_ids[i]) as SliceData
			if slice.slice_type in [RC.SliceType.ATTACK, RC.SliceType.CRIT]:
				attack_slot = i
				break
		CombatFixture.land(enemy, attack_slot)
		s.combat_action(CombatAction.end_turn())
		turns += 1
	assert_true(s.run.is_over())
	assert_eq(s.run.outcome, RunState.Outcome.DIED)
	assert_false(s.campaign.get_operative(&"op_1").alive, "permadeath")
	assert_eq(s.campaign.schematics, schematics_before + 10, "banked Schematics kept")
	assert_true(s.campaign.armory.has(&"turret"), "banked asset kept")
	assert_false(s.campaign.armory.has(&"decoy"), "unbanked asset lost")
	assert_eq(s.campaign.heat, heat_before + _cfg.death_heat_base + 1, "10 + tier Heat")
	assert_eq(s.campaign.deaths, 1)
	assert_true(cycles >= 0)


# --- Completion ----------------------------------------------------------------------------

func test_completion_converts_cycles_keeps_everything_and_ranks_up() -> void:
	var s := _start(21)
	var path := _path_to(s, _is_final)
	assert_eq(path.size(), _cfg.map_layers, "one node per layer")
	s.run.operative.daemon_ids.append(&"kernel_sync")
	_walk(s, path)
	assert_eq(s.run.outcome, RunState.Outcome.COMPLETED, "completed (last events: %s)" % [s.last_events])
	var op := s.campaign.get_operative(&"op_1")
	assert_eq(op.rank, 1, "Rank +1")
	assert_eq(op.hp, op.max_hp, "healed at HQ")
	assert_true(op.deck.size() >= 10, "keeps the deck (%d cards)" % op.deck.size())
	assert_true(op.daemon_ids.has(&"kernel_sync"), "keeps Daemons")
	assert_eq(op.slot_firmware_ids.size(), 6, "keeps Firmware sockets")
	var expected := _cfg.starting_schematics + s.run.banked_schematics + int(s.run.cycles / _cfg.cycles_per_schematic)
	assert_eq(s.campaign.schematics, expected, "banked + Cycles 10:1")
	assert_true(s.run.banked_schematics >= 2 * _cfg.rack_schematics_by_tier[0] or s.run.banked_schematics >= _cfg.rack_schematics_by_tier[0], "final Rack banked")
	assert_eq(s.campaign.runs_completed, 1)


func test_cold_exit_and_scrubber_run_level_daemons() -> void:
	var s := _start(21)
	s.run.operative.daemon_ids.append(&"scrubber")
	s.run.operative.daemon_ids.append(&"cold_exit")
	var path := _path_to(s, _is_final)
	var last: StringName = path.pop_back()
	_walk(s, path)
	s.enter_node(last)
	_auto_fight(s)
	var fight_events := s.last_events.duplicate()  # the Rack capture (rewards come next)
	_settle(s)
	assert_eq(s.run.outcome, RunState.Outcome.COMPLETED)
	var heat_events := []
	for e in fight_events:
		if e.get("type", "") == "heat":
			heat_events.append(e)
	var scrubbed := false
	for e in heat_events:
		if e["reason"] == "Server Rack" and e["amount"] == -1:
			scrubbed = true
	assert_true(scrubbed, "Scrubber turned the final Rack Heat into -1: %s" % [heat_events])
	var cold := false
	for e in s.last_events:
		if e.get("type", "") == "heat" and e["reason"] == "cold_exit":
			cold = true
	assert_eq(cold, not s.run.miss_resolved, "Cold Exit -3 iff the Miss slice never resolved")


# --- Modem and Terminal ------------------------------------------------------------------

func test_modem_shop_sells_cards_firmware_daemons_removal_and_overwrites() -> void:
	var s := _start(5)
	var path := _path_to(s, func(n: Dictionary) -> bool: return n["type"] == RC.InfilNodeType.MODEM)
	assert_true(path.size() > 0)
	for i in path.size() - 1:
		s.enter_node(path[i])
		if s.in_combat():
			_auto_fight(s)
		_settle(s)
	s.enter_node(path[path.size() - 1])
	assert_eq(s.run.phase, RunState.Phase.SHOP)
	var shop := s.run.shop
	assert_eq(shop["cards"].size(), 3)
	assert_eq(shop["firmware"].size(), 2)
	assert_eq(shop["daemons"].size(), 1)
	assert_eq(shop["slices"].size(), _cfg.shop_slice_choices, "overwrite offers from the catalogue")
	for sid in shop["slices"]:
		var in_catalogue := false
		for slice in _cfg.shop_slices:
			if slice.id == StringName(String(sid)):
				in_catalogue = true
		assert_true(in_catalogue, "%s is in the shop slice catalogue" % sid)
	for p in shop["card_prices"]:
		assert_true(p >= _cfg.card_price_range.x and p <= _cfg.card_price_range.y, "card price %d" % p)
	s.run.cycles = 1000
	var deck := s.run.operative.deck.size()
	var card := StringName(String(shop["cards"][0]))
	s.buy("cards", 0)
	assert_eq(s.run.operative.deck.size(), deck + 1)
	assert_true(s.run.operative.deck.has(card))
	assert_eq(s.run.shop["cards"].size(), 2)
	assert_eq(s.card_removal_price(), _cfg.card_removal_price)
	s.remove_card(0)
	assert_eq(s.run.operative.deck.size(), deck)
	assert_eq(s.card_removal_price(), _cfg.card_removal_price + _cfg.card_removal_increment, "+25 each time")
	assert_eq(s.slice_overwrite_price(5), _cfg.miss_slice_overwrite_price, "Miss slot costs 150")
	assert_eq(s.slice_overwrite_price(1), _cfg.slice_overwrite_price)
	var cycles := s.run.cycles
	s.overwrite_slice(5, 0)
	assert_ne(s.run.operative.slot_slice_ids[5], &"miss", "Miss slice overwritten")
	assert_eq(s.run.cycles, cycles - _cfg.miss_slice_overwrite_price)
	var daemon := StringName(String(shop["daemons"][0]))
	s.buy("daemons", 0)
	assert_true(s.run.operative.daemon_ids.has(daemon))
	s.run.cycles = 0
	var ev := s.buy("firmware", 0, 1)
	assert_eq(ev[ev.size() - 1]["type"], "refused", "cannot afford")
	s.leave_shop()
	assert_eq(s.run.phase, RunState.Phase.MAP)


func test_terminal_event_choices_apply_their_costs_and_effects() -> void:
	var s := _start(7)
	var path := _path_to(s, func(n: Dictionary) -> bool: return n["type"] == RC.InfilNodeType.TERMINAL)
	if path.is_empty():
		pass_test("no Terminal on this map")
		return
	for i in path.size() - 1:
		s.enter_node(path[i])
		if s.in_combat():
			_auto_fight(s)
		_settle(s)
	s.enter_node(path[path.size() - 1])
	assert_eq(s.run.phase, RunState.Phase.EVENT)
	var ev := s.current_event()
	assert_not_null(ev)
	s.run.cycles = 100
	var hp := s.run.operative.hp
	var cycles := s.run.cycles
	var choice := ev.choices[0]
	s.choose_event_option(0)
	assert_eq(s.run.cycles, cycles - choice.cycle_cost + _sum_cycles(choice))
	assert_true(s.run.operative.hp <= hp - choice.hp_cost + _sum_heal(choice))
	assert_true(s.run.phase in [RunState.Phase.MAP, RunState.Phase.REWARD])
	assert_eq(s.run.event_id, &"")


func _sum_cycles(choice: EventChoiceData) -> int:
	var n := 0
	for e in choice.effects:
		if e != null and e.type == RC.EffectType.GAIN_CYCLES:
			n += e.amount
	return n


func _sum_heal(choice: EventChoiceData) -> int:
	var n := 0
	for e in choice.effects:
		if e != null and e.type == RC.EffectType.HEAL:
			n += e.amount
	return n


# --- Save / resume -------------------------------------------------------------------------

func test_quit_and_resume_on_the_map_is_identical() -> void:
	var s := _start(13)
	s.enter_node(s.available_nodes()[0])
	_auto_fight(s)
	_settle(s)
	var json := JSON.stringify(s.to_dict())
	var campaign_copy := CampaignState.from_dict(JSON.parse_string(JSON.stringify(s.campaign.to_dict())))
	var loaded := NetrunSession.from_dict(_resolver, campaign_copy, JSON.parse_string(json))
	assert_eq(loaded.state_hash(), s.state_hash(), "run state identical after reload")
	assert_eq(loaded.available_nodes(), s.available_nodes())
	# Both continue identically: same node, same fight, same rewards.
	var next := s.available_nodes()[0]
	s.enter_node(next)
	loaded.enter_node(next)
	assert_eq(loaded.state_hash(), s.state_hash(), "same combat started from the same streams")
	_auto_fight(s)
	_auto_fight(loaded)
	assert_eq(loaded.state_hash(), s.state_hash(), "same outcome and offers")
	assert_eq(loaded.campaign.heat, s.campaign.heat)


func test_quit_and_resume_mid_combat_is_identical() -> void:
	var s := _start(17)
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat())
	s.combat_action(CombatAction.nudge(&"enemy_0", 1))
	s.combat_action(CombatAction.play_card(0, s.combat.state.target_id))
	var json := JSON.stringify(s.to_dict())
	var campaign_copy := CampaignState.from_dict(JSON.parse_string(JSON.stringify(s.campaign.to_dict())))
	var loaded := NetrunSession.from_dict(_resolver, campaign_copy, JSON.parse_string(json))
	assert_true(loaded.in_combat())
	assert_eq(loaded.combat.state_hash(), s.combat.state_hash())
	assert_eq(loaded.state_hash(), s.state_hash())
	assert_true(loaded.combat.can_rewind(), "checkpoint and actions survived")
	loaded.combat_rewind()
	s.combat_rewind()
	assert_eq(loaded.combat.state_hash(), s.combat.state_hash(), "rewind identical after reload")
	loaded.combat_action(CombatAction.end_turn())
	s.combat_action(CombatAction.end_turn())
	assert_eq(loaded.state_hash(), s.state_hash(), "same random respins after reload")


func test_tier_2_scales_enemies_and_rewards() -> void:
	var s := _start(3, 2)
	assert_eq(s.enemy_scale(), 1.6)
	s.enter_node(s.available_nodes()[0])
	var enemy := s.combat.state.get_combatant(&"enemy_0")
	var base := (ContentRegistry.get_content(enemy.source_id) as EnemyData).hp
	assert_eq(enemy.max_hp, roundi(base * 1.6))
	_auto_fight(s)
	assert_true(s.run.cycles >= roundi(_cfg.cycles_router_range.x * 1.7), "rewards x1.7 (%d)" % s.run.cycles)


## Horizontal pass 12: the final Rack's card offer is chosen before the run completes
## (it used to be dropped), and the final Rack offers no Daemon (the layer-4 Rack does).
func test_the_final_rack_rewards_can_be_claimed() -> void:
	var s := _start()
	var path := _path_to(s, _is_final)
	for id in path:
		s.enter_node(id)
		if s.in_combat():
			_auto_fight(s)
		if id == path[path.size() - 1]:
			break
		_settle(s)
	assert_eq(s.run.phase, RunState.Phase.REWARD, "the final Rack waits for its offers")
	assert_false(s.run.is_over())
	var card := &""
	while s.run.phase == RunState.Phase.REWARD:
		var offer := s.current_reward()
		assert_ne(offer["kind"], "daemon", "no Daemon at the final Rack")
		if offer["kind"] == "card":
			card = StringName(String(offer["options"][0]))
		if offer["kind"] == "firmware":
			s.skip_reward()
		else:
			s.choose_reward(0)
	assert_ne(card, &"", "a card was offered")
	assert_true(s.run.is_over())
	assert_eq(s.run.outcome, RunState.Outcome.COMPLETED)
	assert_true(s.campaign.get_operative(&"op_1").deck.has(card), "the card goes home")
	var racks := s.run.visited.filter(func(n: StringName) -> bool: return s.run.map.get_node(n)["type"] == RC.InfilNodeType.SERVER_RACK)
	assert_eq(s.run.racks_captured, racks.size(), "every Rack on the path is counted")
