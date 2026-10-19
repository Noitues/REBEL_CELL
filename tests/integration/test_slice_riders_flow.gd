extends GutTest
## Plan 2 N20 flow: a several-turn fight against a Genome-Core-style rider foe (IV hits per
## CORRUPTED slice, Medicine x4 on a Perfect, Adrenaline pierce) through the session API.
## Every End Turn's preview equals its result, and the operative's HP after each turn is
## the sum of the rider hits the log reports.

const F := preload("res://tests/helpers/rider_fixture.gd")


func _foe_wheel(tag: StringName) -> Array:
	var iv := F.rider(StringName("%s_iv" % tag), 2, 1, 1.0, false, RC.Status.CORRUPTED, 1)
	var med := F.rider(StringName("%s_med" % tag), 10, 1, 4.0)
	var adr := F.rider(StringName("%s_adr" % tag), 10, 1, 4.0, true)
	return [iv, med, adr, iv, med, adr]


func test_full_fight_with_rider_foe_matches_preview_each_turn() -> void:
	var tag := &"rf_flow"
	var p := F.pad(&"rf_flow_pad")
	var noop: Array[CardData] = F._deck(tag)
	var cls := CombatFixture.operative_class(&"rf_flow_op", 400, CombatFixture.wheel([p, p, p, p, p, p]), noop)
	var foe := CombatFixture.enemy(&"rf_flow_foe", 999, CombatFixture.wheel(_foe_wheel(tag)))
	var s := CombatSession.start(CombatFixture.resolver([cls, foe]), cls.id, [foe.id], F.SEED)
	F.corrupt(s, [1, 2])
	var total := 0
	for turn in 4:
		s.state.player.block = 6
		var hp := s.state.player.hp
		var pv := s.preview_end_turn()
		var r := s.apply(CombatAction.end_turn())
		assert_true(r.ok(), r.error)
		var lost := hp - r.resolved_state.player.hp
		assert_eq(hp - pv.resolved_state.player.hp, lost, "turn %d: preview == result" % turn)
		assert_eq(pv.resolved_state.state_hash(), r.resolved_state.state_hash(), "turn %d: hashes" % turn)
		var hp_sum := 0
		for e in F.hits_of(r.events, s.state.player.id):
			hp_sum += int(e.get("hp_damage", 0))
		assert_eq(hp_sum, lost, "turn %d: the log's hits add up to the HP lost" % turn)
		total += lost
		if not s.state.player.is_alive():
			break
	assert_gt(total, 0, "the rider foe dealt damage")
	assert_eq(s.state.player.hp, 400 - total)
