extends GutTest
## Resolution order (GDD 2.2 step 3, M1 acceptance): defensive -> offensive -> statuses,
## simultaneous on both sides.

var _atk8: SliceData
var _def5: SliceData
var _crit12: SliceData
var _dose: SliceData


func before_each() -> void:
	_atk8 = CombatFixture.slice(&"o_atk8", RC.SliceType.ATTACK, 8)
	_def5 = CombatFixture.slice(&"o_def5", RC.SliceType.DEFEND, 5, RC.TargetRule.SELF)
	_crit12 = CombatFixture.slice(&"o_crit12", RC.SliceType.CRIT, 12)
	var corrupt := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.POINTER_TARGET, 0, RC.RingScope.OUTER, 1.0, RC.Status.CORRUPTED, RC.SlicePick.RANDOM_NON_MISS)
	var te: Array[TriggeredEffectData] = [CombatFixture.triggered(RC.Trigger.ON_SLICE_TRIGGER, [corrupt])]
	_dose = CombatFixture.slice(&"o_dose", RC.SliceType.AFFLICT, 0, RC.TargetRule.POINTER, te)


func _fight(player_slices: Array, enemy_slices: Array, enemy_hp: int = 50) -> CombatSession:
	var deck: Array[CardData] = [CombatFixture.card(&"o_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"o_class", 60, CombatFixture.wheel(player_slices), deck)
	var enemy := CombatFixture.enemy(&"o_enemy", enemy_hp, CombatFixture.wheel(enemy_slices))
	var resolver := CombatFixture.resolver([cls, enemy])
	var s := CombatSession.start(resolver, cls.id, [enemy.id], 3)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	return s


func test_block_gained_this_turn_absorbs_this_turns_attack() -> void:
	var s := _fight([_def5, _def5, _def5, _def5, _def5, _def5], [_atk8, _atk8, _atk8, _atk8, _atk8, _atk8])
	var r := s.apply(CombatAction.end_turn())
	var block_index := CombatFixture.index_of_event(r, "block")
	var damage_index := CombatFixture.index_of_event(r, "damage")
	assert_true(block_index >= 0 and damage_index > block_index, "block resolves before the hit")
	var hit := CombatFixture.events_of(r, "damage")[0]
	assert_eq(hit["blocked"], 5)
	assert_eq(hit["hp_damage"], 3)
	assert_eq(s.state.player.hp, 57)


func test_passes_run_defensive_then_offensive_then_statuses() -> void:
	var s := _fight([_def5, _def5, _def5, _def5, _def5, _def5], [_dose, _dose, _dose, _dose, _dose, _dose])
	var r := s.apply(CombatAction.end_turn())
	var d := CombatFixture.index_of_event(r, "pass", "pass", "defensive")
	var o := CombatFixture.index_of_event(r, "pass", "pass", "offensive")
	var st := CombatFixture.index_of_event(r, "pass", "pass", "statuses")
	assert_true(d < o and o < st, "pass markers in order")
	assert_true(CombatFixture.index_of_event(r, "block") < o, "DEF resolves in the defensive pass")
	assert_true(CombatFixture.index_of_event(r, "status") > st, "DOSE applies its status in the status pass")
	assert_eq(s.state.player.wheel.slice_statuses.count(RC.Status.CORRUPTED), 1, "one player slice corrupted")


func test_both_sides_resolve_even_when_one_dies() -> void:
	var s := _fight([_crit12, _crit12, _crit12, _crit12, _crit12, _crit12], [_atk8, _atk8, _atk8, _atk8, _atk8, _atk8], 10)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 0, "enemy killed this turn")
	assert_eq(s.state.player.hp, 52, "the dying enemy's attack still landed (simultaneous)")
	assert_eq(s.state.outcome, CombatState.Outcome.VICTORY)
	assert_eq(CombatFixture.events_of(r, "died").size(), 1)


func test_enemy_block_from_its_defensive_slice_absorbs_the_players_attack() -> void:
	var s := _fight([_atk8, _atk8, _atk8, _atk8, _atk8, _atk8], [_def5, _def5, _def5, _def5, _def5, _def5])
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 47, "8 - 5 block = 3")


func test_hand_is_discarded_and_redrawn_each_turn() -> void:
	var s := _fight([_def5, _def5, _def5, _def5, _def5, _def5], [_atk8, _atk8, _atk8, _atk8, _atk8, _atk8])
	assert_eq(s.state.hand.size(), 1, "one-card deck draws one")
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.turn, 2)
	assert_eq(s.state.hand.size(), 1, "redrawn after the reshuffle")
	assert_eq(s.state.discard_pile.size(), 0)
