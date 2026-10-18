extends GutTest
## N13 (designer 2026-10-18, Q7/Q10): satellites and drones are fixed to their slice. Any
## player action that would move one (nudge, spin, flip, respin, freeze, snap) is refused
## with SATELLITE_FIXED unless the effect carries the Undock keyword; host spins, flips and
## respins carry them along on their slice. Preview equals the result.

const MOVES := {
	&"sf_nudge": RC.EffectType.NUDGE, &"sf_spin": RC.EffectType.SPIN, &"sf_flip": RC.EffectType.FLIP,
	&"sf_respin": RC.EffectType.RESPIN, &"sf_freeze": RC.EffectType.FREEZE, &"sf_snap": RC.EffectType.SNAP_TO_CENTER,
}


func _refused(s: CombatSession, a: CombatAction) -> void:
	var hash_before := s.state_hash()
	var resistance := s.state.get_combatant(&"enemy_0").resistance
	var preview := s.preview(a)
	var r := s.apply(a)
	assert_false(r.ok(), "refused")
	assert_eq(r.error, CombatResolver.SATELLITE_FIXED)
	assert_eq(preview.error, r.error, "preview names the same reason")
	assert_eq(s.state_hash(), hash_before, "a refusal leaves the state untouched")
	assert_eq(s.state.get_combatant(&"enemy_0").resistance, resistance, "host resistance untouched")


func test_nudge_action_on_a_satellite_is_refused() -> void:
	var s := SatelliteFixture.session([])
	_refused(s, CombatAction.nudge(SatelliteFixture.sat_of(s).id, 1))


func test_every_moving_card_effect_on_a_satellite_is_refused() -> void:
	for id in MOVES:
		var card := SatelliteFixture.move_card(id, MOVES[id], 7 if MOVES[id] == RC.EffectType.SPIN else 1)
		var s := SatelliteFixture.session([card])
		_refused(s, CombatAction.play_card(s.state.hand.find(id), SatelliteFixture.sat_of(s).id))


func test_undock_keyword_effect_moves_a_satellite_exactly_one_tick() -> void:
	var card := SatelliteFixture.move_card(&"sf_undock_nudge", RC.EffectType.NUDGE, 1, true)
	var s := SatelliteFixture.session([card])
	var sat := SatelliteFixture.sat_of(s)
	var before := sat.wheel.rotation
	var a := CombatAction.play_card(0, sat.id)
	var preview := s.preview(a)
	var r := s.apply(a)
	assert_true(r.ok(), r.error)
	assert_eq(absi(SatelliteFixture.sat_of(s).wheel.rotation - before), 1, "exactly 1 tick")
	assert_eq(preview.state.state_hash(), r.state.state_hash(), "preview == result")


func test_host_spin_flip_and_respin_keep_the_satellite_on_its_slice() -> void:
	for id in [&"sf_spin", &"sf_flip", &"sf_respin"]:
		var card := SatelliteFixture.move_card(id, MOVES[id], 7)
		var s := SatelliteFixture.session([card])
		var host := s.state.get_combatant(&"enemy_0")
		var sat := SatelliteFixture.sat_of(s)
		var slice_id := host.wheel.slot_slice_ids[sat.dock_slot]
		var sat_rotation := sat.wheel.rotation
		var r := SatelliteFixture.play(s, id, &"enemy_0")
		assert_true(r.ok(), "%s: %s" % [id, r.error])
		host = s.state.get_combatant(&"enemy_0")
		sat = SatelliteFixture.sat_of(s)
		assert_eq(host.wheel.slot_slice_ids[sat.dock_slot], slice_id, "%s: same slice" % id)
		assert_eq(sat.wheel.rotation, sat_rotation, "%s: mini-wheel unchanged" % id)


func test_host_respin_draws_for_the_host_wheel_only() -> void:
	var card := SatelliteFixture.move_card(&"sf_respin", RC.EffectType.RESPIN)
	var s := SatelliteFixture.session([card])
	var probe := CombatResolver.clone_rng(s.rng)
	probe.randi_range(0, RC.TICKS - 1)
	var r := SatelliteFixture.play(s, &"sf_respin", &"enemy_0")
	assert_true(r.ok(), r.error)
	assert_eq(s.rng.state, probe.state, "one draw: the host wheel, none per satellite")


func test_with_no_satellites_nothing_new_is_refused() -> void:
	var cards: Array[CardData] = []
	for id in [&"sf_nudge", &"sf_spin", &"sf_flip", &"sf_snap"]:
		cards.append(SatelliteFixture.move_card(id, MOVES[id]))
	var none: Array[SatelliteSpawnData] = [CombatFixture.spawn(SatelliteFixture.satellite(), 0, 0)]
	var s := SatelliteFixture.session(cards, none)
	assert_eq(s.state.satellites_of(&"enemy_0").size(), 0)
	assert_eq(s.resolver.validate_action(s.state, CombatAction.nudge(&"enemy_0", 1)), "")
	for id in [&"sf_nudge", &"sf_spin", &"sf_flip", &"sf_snap"]:
		assert_eq(s.resolver.validate_action(s.state, CombatAction.play_card(s.state.hand.find(id), &"enemy_0")), "", String(id))


func test_moving_effects_on_the_operative_own_wheel_are_not_refused_by_drones() -> void:
	var e := CombatFixture.effect(RC.EffectType.SPIN, RC.EffectTarget.OWN_WHEEL, 3, RC.RingScope.WHOLE_WHEEL)
	var card := CombatFixture.card(&"sf_self_spin", [e], 0, RC.WheelTarget.OWN)
	var s := SatelliteFixture.session([card])
	assert_true(SatelliteFixture.play(s, &"sf_self_spin", &"").ok())
