extends GutTest
## Plan 2 N14 (rulings Q39, Q31): the defense trio on one hit. deal_hit runs enrage, then a
## SANDBOX charge (negates the whole hit, any source but self, Pierce never touches it), then
## BLOCK, then SHIELD (both skipped by Pierce), then HP. BLOCK and charges go at the turn
## boundary; SHIELD stays and caps at the config's shield_cap.


func _session() -> CombatSession:
	return EnrageFixture.session(EnrageFixture.enemy(&"dt_foe", RC.EnemyClass.NORMAL, 0), 0)


func _hit(s: CombatSession, attacker: CombatantState, victim: CombatantState, amount: int, pierce: bool = false, is_attack: bool = true) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	s.resolver.fx.deal_hit(s.state, attacker, victim, amount, pierce, is_attack, events, &"dt")
	return events


func test_block_absorbs_then_hp() -> void:
	var s := _session()
	var p := s.state.player
	var hp := p.hp
	p.block = 5
	_hit(s, s.state.get_combatant(&"enemy_0"), p, 8)
	assert_eq(p.block, 0)
	assert_eq(hp - p.hp, 3)


func test_block_consumed_before_shield() -> void:
	var s := _session()
	var p := s.state.player
	var hp := p.hp
	p.block = 4
	p.shield = 4
	_hit(s, s.state.get_combatant(&"enemy_0"), p, 6)
	assert_eq([p.block, p.shield, hp - p.hp], [0, 2, 0], "block 4, shield 4, hit 6 -> block 0, shield 2, HP full")


func test_pierce_bypasses_block_and_shield() -> void:
	var s := _session()
	var p := s.state.player
	var hp := p.hp
	p.block = 5
	p.shield = 5
	_hit(s, s.state.get_combatant(&"enemy_0"), p, 6, true)
	assert_eq([p.block, p.shield, hp - p.hp], [5, 5, 6])


func test_one_charge_negates_one_big_hit() -> void:
	var s := _session()
	var p := s.state.player
	var hp := p.hp
	p.evade_charges = 1
	p.block = 3
	var events := _hit(s, s.state.get_combatant(&"enemy_0"), p, 30)
	assert_eq(hp - p.hp, 0, "a 30 hit against 1 charge deals 0")
	assert_eq(p.evade_charges, 0, "the charge is spent")
	assert_eq(p.block, 3, "SANDBOX comes before BLOCK: block untouched")
	var ev := events.filter(func(e: Dictionary) -> bool: return e["type"] == "evaded")
	assert_eq(ev.size(), 1)
	assert_true(bool(ev[0]["sandboxed"]), "the negated hit carries the sandboxed flag (sim intake 0)")
	assert_eq(int(ev[0]["hp_damage"]), 0)


func test_pierce_does_not_bypass_sandbox() -> void:
	var s := _session()
	var p := s.state.player
	var hp := p.hp
	p.evade_charges = 1
	_hit(s, s.state.get_combatant(&"enemy_0"), p, 10, true)
	assert_eq(hp - p.hp, 0)
	assert_eq(p.evade_charges, 0)


func test_listener_hit_spends_a_charge() -> void:
	var s := _session()
	var p := s.state.player
	var hp := p.hp
	p.evade_charges = 1
	_hit(s, s.state.get_combatant(&"enemy_0"), p, 7, false, false)
	assert_eq(hp - p.hp, 0, "a counter or listener hit (not a slice attack) is negated too")
	assert_eq(p.evade_charges, 0)


func test_deal_damage_effect_spends_a_charge() -> void:
	var s := _session()
	var e := s.state.get_combatant(&"enemy_0")
	var p := s.state.player
	var hp := p.hp
	p.evade_charges = 1
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.POINTER_TARGET, 9)
	var events: Array[Dictionary] = []
	s.resolver.fx.apply_effect(s.state, dmg, {"owner": e, "target": p, "pointer_index": 0, "source_id": &"dt"}, s.rng, events)
	assert_eq(hp - p.hp, 0)
	assert_eq(p.evade_charges, 0)


func test_self_damage_is_not_negated() -> void:
	var s := _session()
	var p := s.state.player
	var hp := p.hp
	p.evade_charges = 1
	_hit(s, p, p, 4, false, false)
	assert_eq(hp - p.hp, 4)
	assert_eq(p.evade_charges, 1, "self-damage keeps the charge")


func test_zero_hit_spends_nothing() -> void:
	var s := _session()
	var p := s.state.player
	p.evade_charges = 1
	var events := _hit(s, s.state.get_combatant(&"enemy_0"), p, 0)
	assert_eq(p.evade_charges, 1)
	assert_eq(events.size(), 0)


func test_charges_stack_additively() -> void:
	var s := _session()
	var p := s.state.player
	var events: Array[Dictionary] = []
	s.resolver.fx.gain_evade(p, 1, events)
	s.resolver.fx.gain_evade(p, 2, events)
	assert_eq(p.evade_charges, 3)
	var hp := p.hp
	var e := s.state.get_combatant(&"enemy_0")
	for i in 4:
		_hit(s, e, p, 5)
	assert_eq(hp - p.hp, 5, "three hits negated, the fourth lands")


func test_shield_cap_edges() -> void:
	var s := _session()
	var p := s.state.player
	var cap := CombatFixture.config().shield_cap
	var events: Array[Dictionary] = []
	p.shield = cap - 1
	s.resolver.fx.gain_shield(p, 1, events)
	assert_eq(p.shield, cap)
	s.resolver.fx.gain_shield(p, 1, events)
	assert_eq(p.shield, cap)
	assert_eq(int(events[-1]["amount"]), 0, "0 gained at the cap")


func test_turn_boundary_clears_block_and_charges_keeps_shield() -> void:
	var s := _session()
	for c in s.state.combatants_in_order():
		c.block = 4
		c.shield = 6
		c.evade_charges = 2
	var events: Array[Dictionary] = []
	s.resolver.start_turn(s.state, s.rng, events)
	for c in s.state.combatants_in_order():
		assert_eq(c.block, 0, "%s block expires" % c.id)
		assert_eq(c.evade_charges, 0, "%s charges expire" % c.id)
		assert_eq(c.shield, 6, "%s shield persists" % c.id)


func test_end_turn_leaves_block_and_charges_for_the_resolve_only() -> void:
	var s := _session()
	var p := s.state.player
	p.block = 4
	p.evade_charges = 1
	p.shield = 3
	var r := s.apply(CombatAction.end_turn())
	assert_true(r.ok(), r.error)
	p = s.state.player
	assert_eq([p.block, p.evade_charges, p.shield], [0, 0, 3], "end of turn: BLOCK and SANDBOX gone, SHIELD kept")


func test_enum_ints_unchanged() -> void:
	assert_eq([RC.SliceType.DEFRAG, RC.SliceType.DETOUR, RC.SliceType.SANDBOX], [2, 3, 4])


func test_config_charges_validate() -> void:
	var cfg := CampaignConfigData.new()
	assert_eq([cfg.sandbox_charges, cfg.sandbox_charges_perfect], [1, 2])
	assert_eq([CombatFixture.config().sandbox_charges, CombatFixture.config().sandbox_charges_perfect], [1, 2])
	cfg.sandbox_charges = 0
	assert_true(",".join(cfg.validate()).contains("sandbox_charges"))
