extends GutTest
## SOLACE_BAL_r1 (BAL-05, Q29): the Genome Core keeps its three phases and its phase HP; only the HP and
## enrage numbers are tuned. Enrage steps are additive, never a countdown.

const BOSS_HP: int = 400
const PHASE_THRESHOLDS: Array[float] = [0.66, 0.33]


func _boss() -> EnemyData:
	return ContentRegistry.get_content(&"renewal_engine") as EnemyData


func test_phase_count_stays_three() -> void:
	# Base phase + two thresholds. Q29: phases are never shortened; the minimum stays 3.
	assert_eq(_boss().phases.size() + 1, 3, "the Genome Core has three phases")
	assert_gte(_boss().phases.size() + 1, 3, "phase minimum 3")


func test_phase_hp_is_pinned() -> void:
	assert_eq(_boss().hp, BOSS_HP, "boss HP at T1")
	assert_eq(_boss().phases.size(), PHASE_THRESHOLDS.size())
	for i in PHASE_THRESHOLDS.size():
		assert_almost_eq(_boss().phases[i].hp_threshold_pct, PHASE_THRESHOLDS[i], 0.0001, "phase %d threshold" % (i + 2))


func test_boss_enrage_is_additive_not_a_countdown() -> void:
	var e := CombatFixture.config().enrage_for(_boss())
	assert_not_null(e, "the boss enrages")
	assert_gt(e.start_turn, 0)
	assert_gt(e.every_n_turns, 0, "a step every N turns")
	assert_gt(e.damage_pct_step, 0, "each step adds damage")
