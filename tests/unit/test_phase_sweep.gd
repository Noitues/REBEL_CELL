extends GutTest
## Plan 2 N3 sweep (full tier): every shipped enemy with phases has legal phase data, its
## floors strictly descend, and an operative hitting hard reaches the last phase and the
## kill (no softlock at a floor).

const MAX_RESOLVES := 40
const HIT := 200


func _phased() -> Array[EnemyData]:
	var out: Array[EnemyData] = []
	var ids := ContentRegistry.all_ids()
	ids.sort()
	for id in ids:
		var data := ContentRegistry.get_content(id) as EnemyData
		if data != null and not data.phases.is_empty():
			out.append(data)
	return out


func test_every_enemy_every_tier_reaches_final_phase() -> void:
	var list := _phased()
	assert_gt(list.size(), 0)
	var cls := PhaseFixture.operative(&"sweep_op", HIT)
	for data in list:
		for tier in 4:
			var scale := CombatFixture.config().enemy_hp_scale(tier + 1)  # N2 removed enemy_scale_per_tier
			var s := CombatSession.start(CombatFixture.resolver([cls]), cls.id, [data.id], 1001 + tier, &"", 0,
				{"hp": 999999, "max_hp": 999999, "enemy_scale": scale})
			var resolves := 0
			while not s.state.is_over() and resolves < MAX_RESOLVES:
				CombatFixture.land(s.state.player, 0)
				s.apply(CombatAction.end_turn())
				resolves += 1
			var e := s.state.get_combatant(&"enemy_0")
			assert_eq(e.phase_index, data.phases.size(), "%s T%d reaches its last phase" % [data.id, tier + 1])
			assert_eq(s.state.outcome, CombatState.Outcome.VICTORY, "%s T%d dies within %d resolves" % [data.id, tier + 1, MAX_RESOLVES])


func test_floors_strictly_descending_per_enemy() -> void:
	for data in _phased():
		var last := data.hp + 1
		for p in data.phases:
			var f := BossPhaseData.floor_of(data.hp, p.threshold_bp())
			assert_lt(f, last, "%s floors strictly descend" % data.id)
			assert_gt(f, 0, "%s floor above 0" % data.id)
			last = f


func test_hp_by_tier_band_sanity() -> void:
	pending("needs N2 (hp_by_tier)")
