extends GutTest
## Plan 2 N14: SANDBOX charges are deterministic. A seeded fight that gains and spends
## charges replays to the same hash, draws no extra RNG, a staged card that grants charges
## undoes cleanly, and rewind never crosses a checkpoint.

const SEEDS: Array[int] = [4242, 4243]


func _cls(card: CardData) -> ClassData:
	var detour := CombatFixture.slice(&"dtr_detour", RC.SliceType.DETOUR, 1, RC.TargetRule.SELF)
	var shim := CombatFixture.slice(&"dtr_shim", RC.SliceType.SHIM, 3)
	var deck: Array[CardData] = [card, card, card, card, card]
	return CombatFixture.operative_class(&"dtr_class", 60, CombatFixture.wheel([detour, shim, detour, shim, detour, shim]), deck)


func _card() -> CardData:
	return CombatFixture.card(&"dtr_duck", [CombatFixture.effect(RC.EffectType.EVADE, RC.EffectTarget.SELF, 1)])


func _start(seed: int) -> CombatSession:
	var card := _card()
	var cls := _cls(card)
	var foe := EnrageFixture.enemy(&"dtr_foe", RC.EnemyClass.NORMAL, 4, 999, null, [0, 15])
	return CombatSession.start(CombatFixture.resolver([cls, foe, card]), cls.id, [foe.id], seed)


func _play(seed: int, turns: int = 5) -> CombatSession:
	var s := _start(seed)
	for t in turns:
		if s.state.is_over():
			break
		var i := s.state.hand.find(&"dtr_duck")
		if i >= 0 and t % 2 == 0:
			s.apply(CombatAction.play_card(i, s.state.player.id))
		s.apply(CombatAction.end_turn())
	return s


func test_seeded_replay_same_hash() -> void:
	for seed in SEEDS:
		var a := _play(seed)
		var b := CombatSession.replay(a.resolver, a.setup, seed, a.history)
		assert_eq(a.state_hash(), b.state_hash(), "seed %d" % seed)
		assert_eq(a.rng.state, b.rng.state, "seed %d: same draws" % seed)


func test_fight_actually_spends_charges() -> void:
	var s := _start(4242)
	var spent := 0
	for t in 5:
		var i := s.state.hand.find(&"dtr_duck")
		if i >= 0:
			s.apply(CombatAction.play_card(i, s.state.player.id))
		var r := s.apply(CombatAction.end_turn())
		spent += CombatFixture.events_of(r, "evaded").size()
	assert_gt(spent, 0, "the replay fixture exercises SANDBOX")


func test_hash_includes_charges() -> void:
	var s := _start(4242)
	var other := s.state.duplicate_state()
	other.player.evade_charges += 1
	assert_ne(other.state_hash(), s.state.state_hash())


func test_charges_draw_no_rng() -> void:
	var s := _start(4242)
	var before := s.rng.state
	var events: Array[Dictionary] = []
	s.state.player.evade_charges = 1
	s.resolver.fx.deal_hit(s.state, s.state.get_combatant(&"enemy_0"), s.state.player, 5, false, true, events)
	s.resolver.fx.gain_evade(s.state.player, 2, events)
	assert_eq(s.rng.state, before)
	for path in ["res://scripts/core/effect_interpreter.gd"]:
		var text := FileAccess.get_file_as_string(path)
		for word in ["randi(", "randf(", "randomize("]:
			assert_false(text.contains(word), "%s uses %s" % [path, word])


func test_staged_card_undoes_cleanly() -> void:
	var s := _start(4242)
	var before := s.state.state_hash()
	var i := s.state.hand.find(&"dtr_duck")
	assert_gt(i, -1)
	var pv := s.preview(CombatAction.play_card(i, s.state.player.id))
	var r := s.apply(CombatAction.play_card(i, s.state.player.id))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.player.evade_charges, 1)
	assert_eq(pv.state.state_hash(), s.state.state_hash(), "preview == result")
	assert_true(s.can_rewind())
	s.rewind()
	assert_eq(s.state.state_hash(), before, "undo restores the charge count")
	assert_eq(s.state.player.evade_charges, 0)


func test_rewind_never_crosses_the_end_turn_checkpoint() -> void:
	var s := _start(4242)
	var i := s.state.hand.find(&"dtr_duck")
	s.apply(CombatAction.play_card(i, s.state.player.id))
	s.apply(CombatAction.end_turn())
	assert_false(s.can_rewind(), "end turn is a checkpoint")
	assert_eq(s.state.player.evade_charges, 0)
