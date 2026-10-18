extends GutTest
## Plan 2 N1 (R2, R5; ruling Q13 2026-10-18): the interpreter's amount arithmetic. FLAT enemy
## heal / block / shield x the tier damage factor; PERCENT reads the owner's max HP, rounds to
## nearest with a minimum of 1 and is never rescaled; the operative's FLAT stays at base;
## corruption PERCENT is a share of the target's non-NULL slices.

## Stub of N2's enemy_damage_by_tier (T1..T4) so N1 doesn't depend on N2.
const TIER_FACTORS: Array[float] = [1.0, 1.3, 1.69, 2.2]

var _null: SliceData
var _hit: SliceData


func before_all() -> void:
	_null = CombatFixture.slice(&"am_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	_hit = CombatFixture.slice(&"am_hit", RC.SliceType.SHIM, 4)


## A combat against one enemy on `enemy_slices`, its outputs at `factor`.
func _combat(factor: float, enemy_hp: int = 300, enemy_slices: Array = [], player_slices: Array = []) -> Array:
	if enemy_slices.is_empty():
		enemy_slices = [_hit, _hit, _hit, _hit, _hit, _null]
	if player_slices.is_empty():
		player_slices = [_hit, _hit, _hit, _hit, _hit, _null]
	var deck: Array[CardData] = [CombatFixture.card(&"am_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"am_class", 200, CombatFixture.wheel(player_slices), deck)
	var enemy := CombatFixture.enemy(&"am_enemy", enemy_hp, CombatFixture.wheel(enemy_slices))
	var resolver := CombatFixture.resolver([cls, enemy])
	var enemies: Array[EnemyData] = [enemy]
	var state := resolver.create_combat(cls, enemies, CombatFixture.rng(7), null, 0, {"enemy_output_scale": factor})
	return [resolver, state]


func _effect(type: int, amount: int, mode: int, mult: float = 1.0) -> EffectData:
	var e := CombatFixture.effect(type, RC.EffectTarget.SELF, amount, RC.RingScope.OUTER, mult)
	e.amount_mode = mode
	return e


## Applies `e` owned by `owner_id`; returns the events.
func _apply(pair: Array, e: EffectData, owner_id: StringName) -> Array[Dictionary]:
	var resolver: CombatResolver = pair[0]
	var state: CombatState = pair[1]
	var events: Array[Dictionary] = []
	var owner := state.get_combatant(owner_id)
	resolver.fx.apply_effect(state, e, {"owner": owner, "target": owner, "source_id": &"am"}, CombatFixture.rng(1), events)
	return events


func _enemy_heal(factor: float, e: EffectData, max_hp: int = 300) -> int:
	var pair := _combat(factor, max_hp)
	var enemy: CombatantState = (pair[1] as CombatState).get_combatant(&"enemy_0")
	enemy.hp = 1
	var before := enemy.hp
	var events := _apply(pair, e, &"enemy_0")
	assert_eq(int(events[0]["amount"]), enemy.hp - before, "the event reports the real delta")
	return enemy.hp - before


func test_flat_heal_tier1_equals_base() -> void:
	assert_eq(_enemy_heal(TIER_FACTORS[0], _effect(RC.EffectType.HEAL, 10, RC.AmountMode.FLAT)), 10)


func test_flat_heal_scaled_by_tier_factor() -> void:
	var got := []
	for f in TIER_FACTORS:
		got.append(_enemy_heal(f, _effect(RC.EffectType.HEAL, 10, RC.AmountMode.FLAT)))
	assert_eq(got, [10, 13, 17, 22], "round(10 x factor); 16.9 rounds to 17")


func test_percent_heal_reads_owner_max_hp_and_is_not_rescaled() -> void:
	for f in TIER_FACTORS:
		assert_eq(_enemy_heal(f, _effect(RC.EffectType.HEAL, 2, RC.AmountMode.PERCENT)), 6, "2 %% of 300 at factor %s" % f)


func test_percent_block_and_shield_use_max_hp() -> void:
	var pair := _combat(TIER_FACTORS[3], 200)
	var enemy: CombatantState = (pair[1] as CombatState).get_combatant(&"enemy_0")
	_apply(pair, _effect(RC.EffectType.GAIN_BLOCK, 5, RC.AmountMode.PERCENT), &"enemy_0")
	_apply(pair, _effect(RC.EffectType.GAIN_SHIELD, 5, RC.AmountMode.PERCENT), &"enemy_0")
	assert_eq(enemy.block, 10, "5 % of 200")
	assert_eq(enemy.shield, 10, "5 % of 200, never x2.2")


func test_percent_minimum_one_and_zero_edges() -> void:
	assert_eq(_enemy_heal(1.0, _effect(RC.EffectType.HEAL, 1, RC.AmountMode.PERCENT), 20), 1, "0.2 rises to the minimum 1")
	assert_eq(_enemy_heal(1.0, _effect(RC.EffectType.HEAL, 0, RC.AmountMode.PERCENT), 20), 0, "0 % gives 0")
	assert_eq(_enemy_heal(2.2, _effect(RC.EffectType.HEAL, 0, RC.AmountMode.FLAT)), 0, "FLAT 0 gives 0 at any tier")


func test_percent_of_rounds_half_up_in_integers() -> void:
	assert_eq(EffectInterpreter.percent_of(250, 1), 3, "2.5 rounds up")
	assert_eq(EffectInterpreter.percent_of(249, 1), 2, "2.49 rounds down")
	assert_eq(EffectInterpreter.percent_of(300, 2), 6)
	assert_eq(EffectInterpreter.percent_of(0, 40), 0, "nothing to take a share of")
	assert_eq(EffectInterpreter.percent_of(5, 40), 2)
	assert_eq(EffectInterpreter.percent_of(1, 10), 1, "minimum 1")


func test_heal_clamps_to_max_hp() -> void:
	var pair := _combat(1.0, 300)
	var enemy: CombatantState = (pair[1] as CombatState).get_combatant(&"enemy_0")
	enemy.hp = enemy.max_hp - 1
	var events := _apply(pair, _effect(RC.EffectType.HEAL, 50, RC.AmountMode.PERCENT), &"enemy_0")
	assert_eq(enemy.hp, enemy.max_hp)
	assert_eq(int(events[0]["amount"]), 1, "reports the real delta, not 150")


func test_shield_percent_respects_shield_cap_for_the_player() -> void:
	var pair := _combat(1.0)
	var state: CombatState = pair[1]
	state.player.max_hp = 200
	_apply(pair, _effect(RC.EffectType.GAIN_SHIELD, 10, RC.AmountMode.PERCENT), state.player.id)
	assert_eq(state.player.shield, (pair[0] as CombatResolver).config.shield_cap, "20 requested, capped at shield_cap")
	assert_eq(state.player.shield, 15)


func test_enemy_flat_block_scaled_player_flat_block_not() -> void:
	var pair := _combat(TIER_FACTORS[3])
	var state: CombatState = pair[1]
	var enemy := state.get_combatant(&"enemy_0")
	state.player.output_scale = TIER_FACTORS[3]  # even a scaled operative stays at base
	_apply(pair, _effect(RC.EffectType.GAIN_BLOCK, 10, RC.AmountMode.FLAT), &"enemy_0")
	_apply(pair, _effect(RC.EffectType.GAIN_BLOCK, 10, RC.AmountMode.FLAT), state.player.id)
	assert_eq(enemy.block, 22)
	assert_eq(state.player.block, 10, "operative FLAT amounts are never tier-scaled")


func test_buff_multiplier_independent_of_tier_on_percent() -> void:
	var at_t1 := _enemy_heal(TIER_FACTORS[0], _effect(RC.EffectType.HEAL, 4, RC.AmountMode.PERCENT, 1.25))
	var at_t4 := _enemy_heal(TIER_FACTORS[3], _effect(RC.EffectType.HEAL, 4, RC.AmountMode.PERCENT, 1.25))
	assert_eq(at_t1, 15, "4 % of 300 = 12, x1.25")
	assert_eq(at_t4, at_t1, "the buff multiplier does not depend on tier")


func test_amount_mode_large_values_no_overflow() -> void:
	var pair := _combat(TIER_FACTORS[3])
	var enemy: CombatantState = (pair[1] as CombatState).get_combatant(&"enemy_0")
	_apply(pair, _effect(RC.EffectType.GAIN_BLOCK, 1000000, RC.AmountMode.FLAT), &"enemy_0")
	assert_eq(enemy.block, 2200000)


# --- Corruption --------------------------------------------------------------------

func _corrupt(amount: int, mode: int) -> EffectData:
	var e := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.POINTER_TARGET, amount, RC.RingScope.OUTER, 1.0, RC.Status.CORRUPTED, RC.SlicePick.RANDOM_NON_NULL)
	e.amount_mode = mode
	return e


## Corrupted slots on the operative after the enemy applies `e` (player wheel `slices`).
func _corrupted_after(e: EffectData, slices: Array) -> int:
	var pair := _combat(1.0, 300, [], slices)
	var resolver: CombatResolver = pair[0]
	var state: CombatState = pair[1]
	var events: Array[Dictionary] = []
	resolver.fx.apply_effect(state, e, {"owner": state.get_combatant(&"enemy_0"), "target": state.player, "source_id": &"am"}, CombatFixture.rng(3), events)
	return state.player.wheel.slice_statuses.count(RC.Status.CORRUPTED)


func test_percent_corruption_counts_non_null_slices() -> void:
	assert_eq(_corrupted_after(_corrupt(40, RC.AmountMode.PERCENT), [_hit, _hit, _hit, _hit, _hit, _null]), 2, "5 non-NULL at 40 %")
	assert_eq(_corrupted_after(_corrupt(10, RC.AmountMode.PERCENT), [_hit, _null, _null, _null, _null, _null]), 1, "1 non-NULL at 10 %: minimum 1")
	assert_eq(_corrupted_after(_corrupt(40, RC.AmountMode.PERCENT), [_null, _null, _null, _null, _null, _null]), 0, "no non-NULL slice")


func test_flat_corruption_n_slices_capped_by_available() -> void:
	assert_eq(_corrupted_after(_corrupt(4, RC.AmountMode.FLAT), [_hit, _hit, _hit, _null, _null, _null]), 3)
	assert_eq(_corrupted_after(_corrupt(0, RC.AmountMode.FLAT), [_hit, _hit, _hit, _null, _null, _null]), 1, "legacy amount 0 corrupts one slice")


func test_corruption_count_one_draws_like_before() -> void:
	# The old path drew one randi_range over the eligible slots; FLAT 1 must draw the same.
	var pair := _combat(1.0)
	var resolver: CombatResolver = pair[0]
	var state: CombatState = pair[1]
	var rng := CombatFixture.rng(11)
	var expected := resolver.fx.pick_slot(state, state.player, RC.SlicePick.RANDOM_NON_NULL, {}, CombatFixture.rng(11))
	var events: Array[Dictionary] = []
	resolver.fx.apply_effect(state, _corrupt(1, RC.AmountMode.FLAT), {"owner": state.get_combatant(&"enemy_0"), "target": state.player}, rng, events)
	assert_eq(state.player.wheel.slice_statuses[expected], RC.Status.CORRUPTED)
	var ref := CombatFixture.rng(11)
	ref.randi_range(0, 4)
	assert_eq(rng.state, ref.state, "exactly one draw from the passed stream")
