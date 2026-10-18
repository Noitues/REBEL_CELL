extends GutTest
## N13 (designer 2026-10-18, Q7): Undock is a global keyword (EffectData.undock). A satellite
## moves only through an effect that carries it; the shipped Undock card does.


func _undock_card() -> CardData:
	return ContentRegistry.get_content(&"undock") as CardData


func test_the_shipped_undock_card_carries_the_keyword() -> void:
	var card := _undock_card()
	assert_not_null(card)
	assert_true(card.effects[0].undock)


func test_undock_moves_only_the_chosen_satellite_one_slice() -> void:
	var a := SatelliteFixture.satellite(&"sf_a")
	var b := SatelliteFixture.satellite(&"sf_b")
	var spawns: Array[SatelliteSpawnData] = [CombatFixture.spawn(a, 2), CombatFixture.spawn(b, 4)]
	var s := SatelliteFixture.session([_undock_card()], spawns)
	var sats := s.state.satellites_of(&"enemy_0")
	var target := sats[0] if sats[0].dock_slot == 2 else sats[1]
	var other := sats[1] if target == sats[0] else sats[0]
	var action := CombatAction.play_card(0, target.id)
	var preview := s.preview(action)
	var r := s.apply(action)
	assert_true(r.ok(), r.error)
	assert_eq(absi(s.state.get_combatant(target.id).dock_slot - 2), 1, "one slice over")
	assert_eq(s.state.get_combatant(other.id).dock_slot, 4, "the other stays")
	assert_eq(preview.state.state_hash(), r.state.state_hash(), "preview == result")


func test_an_undock_effect_without_the_keyword_is_refused() -> void:
	var e := _undock_card().effects[0].duplicate() as EffectData
	e.undock = false
	var card := CombatFixture.card(&"sf_fake_undock", [e], 0, RC.WheelTarget.SATELLITE)
	var s := SatelliteFixture.session([card])
	var sat := SatelliteFixture.sat_of(s)
	var before := s.state_hash()
	var r := s.apply(CombatAction.play_card(0, sat.id))
	assert_eq(r.error, CombatResolver.SATELLITE_FIXED)
	assert_eq(s.state_hash(), before)


func test_the_handler_alone_refuses_without_the_keyword() -> void:
	var s := SatelliteFixture.session([])
	var sat := SatelliteFixture.sat_of(s)
	var e := EffectData.new()
	var events: Array[Dictionary] = _undock_card().effects[0].custom_handler.new().handle(
		{"target": sat, "effect": e, "action": null}, s.state, s.rng)
	assert_eq(String(events[0]["type"]), "undock_failed")
	assert_eq(sat.dock_slot, SatelliteFixture.DOCK_SLOT)


func test_undock_card_playability_matches_validate_action() -> void:
	var s := SatelliteFixture.session([_undock_card()])
	var options := CardTargeting.options(s.resolver, s.state, 0)
	assert_false(options.is_empty(), "Undock is offered on the satellite")
	for a in options:
		assert_eq(s.resolver.validate_action(s.state, a), "")
		assert_true(s.state.get_combatant(a.wheel_id).is_satellite)
	var nudge_card := SatelliteFixture.move_card(&"sf_nudge", RC.EffectType.NUDGE)
	var s2 := SatelliteFixture.session([nudge_card])
	for a in CardTargeting.options(s2.resolver, s2.state, 0):
		assert_false(s2.state.get_combatant(a.wheel_id).is_satellite, "a plain nudge is never offered on a satellite")
	assert_eq(s.resolver.validate_action(s.state, CombatAction.play_card(0, SatelliteFixture.sat_of(s).id)), "")
	assert_ne(s.resolver.validate_action(s.state, CombatAction.play_card(0, &"enemy_0")), "", "the host is no satellite")
