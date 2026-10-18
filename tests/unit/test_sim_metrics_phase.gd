extends GutTest
## N19: SimMetrics turn and phase accounting (fixture events; observational, no combat needed).

const P := &"player"
const E := &"boss"


func _turn(m: SimMetrics, events: Array = [], enrage: int = 0) -> void:
	m.observe(true, events, enrage)


func _phase_ev() -> Dictionary:
	return {"type": "boss_phase", "target": E, "phase": 1}


func test_normal_reports_one_phase_with_total_turns() -> void:
	var m := SimMetrics.new(P)
	for i in 4:
		_turn(m)
	var d := m.to_dict(true)
	assert_eq(d["phases"].size(), 1)
	assert_eq(d["phases"][0]["turns"], 4)
	assert_false(d["phases"][0]["incomplete"])


func test_phase_change_turn_belongs_to_outgoing_phase() -> void:
	var m := SimMetrics.new(P)
	for i in 2:
		_turn(m)
	_turn(m, [_phase_ev()])  # turn 3 crosses: counts in phase 1
	for i in 4:
		_turn(m)
	var d := m.to_dict(true)
	assert_eq([d["phases"][0]["turns"], d["phases"][1]["turns"]], [3, 4])


func test_five_phase_boss_sum_equals_fight_turns() -> void:
	var m := SimMetrics.new(P)
	var total := 0
	for n in [3, 4, 2, 5, 4]:
		for i in n - 1:
			_turn(m)
		_turn(m, [_phase_ev()])
		total += n
	_turn(m)  # the last phase needs a turn to exist
	total += 1
	var d := m.to_dict(true)
	var sum := 0
	for p in d["phases"]:
		sum += int(p["turns"])
	assert_eq(sum, total)
	assert_eq(d["phases"].size(), 6)


func test_player_death_flags_last_phase_incomplete() -> void:
	var m := SimMetrics.new(P)
	_turn(m, [_phase_ev()])
	_turn(m)
	var d := m.to_dict(false)
	assert_false(d["phases"][0]["incomplete"])
	assert_true(d["phases"][1]["incomplete"])


func test_zero_turn_fight_reports_empty_phases() -> void:
	var d := SimMetrics.new(P).to_dict(true)
	assert_eq(d["phases"], [])
	assert_eq(d["enrage_step"], 0)


func test_card_finishing_mid_turn_counts_the_turn() -> void:
	var m := SimMetrics.new(P)
	_turn(m)
	m.observe(false, [])
	m.finish_mid_turn()
	assert_eq(m.to_dict(true)["phases"][0]["turns"], 2)


func test_phases_keep_their_order() -> void:
	var m := SimMetrics.new(P)
	_turn(m, [_phase_ev()])
	for i in 3:
		_turn(m)
	var d := m.to_dict(true)
	assert_eq([d["phases"][0]["turns"], d["phases"][1]["turns"]], [1, 3])
