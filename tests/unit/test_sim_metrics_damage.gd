extends GutTest
## N19: parked damage, intake, heal turns, resistance, enrage, wheel manipulation (fixture events).

const P := &"player"
const E := &"boss"


func _hit(target: StringName, parked: int, hp_damage: int = 0, extra: Dictionary = {}) -> Dictionary:
	var d := {"type": "damage", "attacker": P if target != P else E, "target": target, "amount": hp_damage + parked, "blocked": 0,
		"shielded": 0, "hp_damage": hp_damage, "parked": parked, "pierce": false}
	d.merge(extra, true)
	return d


func _end(m: SimMetrics, events: Array, enrage: int = 0) -> void:
	m.observe(true, events, enrage)


func test_parked_is_the_event_excess_and_sums_by_path() -> void:
	var m := SimMetrics.new(P)
	_end(m, [_hit(E, 16, 4), _hit(E, 3, 0, {"pierce": true}), {"type": "corrupted", "target": E, "amount": 0, "parked": 5},
		{"type": "parasite", "target": E, "parked": 2}, _hit(E, 1, 0, {"attacker": E})])
	var ph: Dictionary = m.to_dict(true)["phases"][0]
	assert_eq(ph["parked"], 27)
	var bp: Dictionary = ph["parked_by_path"]
	assert_eq([bp["hit"], bp["pierce"], bp["self"], bp["parasite"]], [16, 3, 6, 2])
	assert_eq(int(bp["hit"]) + int(bp["pierce"]) + int(bp["self"]) + int(bp["parasite"]), int(ph["parked"]))


func test_last_phase_has_zero_parked() -> void:
	var m := SimMetrics.new(P)
	_end(m, [_hit(E, 9), {"type": "boss_phase", "target": E}])
	_end(m, [_hit(E, 0, 30)])
	var d := m.to_dict(true)
	assert_eq([d["phases"][0]["parked"], d["phases"][1]["parked"]], [9, 0])


func test_intake_is_unblocked_damage_to_the_player() -> void:
	var m := SimMetrics.new(P)
	# BLOCK 12 against 5+5+5: the engine already splits it; only the last hit's 3 reaches HP
	_end(m, [_hit(P, 0, 0, {"blocked": 5}), _hit(P, 0, 0, {"blocked": 5}), _hit(P, 0, 3, {"blocked": 2})])
	assert_eq(m.to_dict(true)["phases"][0]["intake"], 3)


func test_sandboxed_hit_counts_as_zero_intake() -> void:
	var m := SimMetrics.new(P)
	_end(m, [_hit(P, 0, 7, {"sandboxed": true}), _hit(P, 0, 2)])
	assert_eq(m.to_dict(true)["phases"][0]["intake"], 2)


func test_intake_on_the_crossing_resolve_goes_to_the_old_phase() -> void:
	var m := SimMetrics.new(P)
	_end(m, [_hit(P, 0, 6), {"type": "boss_phase", "target": E}])
	_end(m, [_hit(P, 0, 4)])
	var d := m.to_dict(true)
	assert_eq([d["phases"][0]["intake"], d["phases"][1]["intake"]], [6, 4])


func test_enrage_step_is_the_highest_reached() -> void:
	var m := SimMetrics.new(P)
	_end(m, [], 0)
	_end(m, [], 2)
	_end(m, [], 1)
	assert_eq(m.to_dict(true)["enrage_step"], 2)


func test_heal_turns_count_turns_with_an_enemy_heal() -> void:
	var m := SimMetrics.new(P)
	_end(m, [{"type": "heal", "target": E, "amount": 6}, {"type": "heal", "target": E, "amount": 6}])
	_end(m, [{"type": "heal", "target": P, "amount": 6}])
	_end(m, [{"type": "heal", "target": E, "amount": 6}])
	assert_eq(m.to_dict(true)["phases"][0]["heal_turns"], 2)


func test_resistance_absorbed_counts_ticks_and_nudges() -> void:
	var m := SimMetrics.new(P)
	m.observe(false, [{"type": "spin", "target": E, "amount": 5, "moved": 2, "absorbed": 3}, {"type": "nudge_absorbed", "target": E}])
	_end(m, [])
	assert_eq(m.to_dict(true)["phases"][0]["resistance_absorbed"], 4)


func test_turn_manipulation_own_enemy_both_none() -> void:
	var m := SimMetrics.new(P)
	m.observe(false, [{"type": "nudge", "target": P}])
	_end(m, [])  # own
	m.observe(false, [{"type": "nudge", "target": E}])
	_end(m, [])  # enemy
	m.observe(false, [{"type": "nudge", "target": E}, {"type": "spin", "target": P, "absorbed": 0}])
	_end(m, [])  # both
	_end(m, [])  # none
	var tm: Dictionary = m.to_dict(true)["turn_manipulation"]
	assert_eq([tm["own"], tm["enemy"], tm["both"], tm["none"]], [1, 1, 1, 1])
