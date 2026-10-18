extends GutTest
## Plan 2 N14 (ruling Q39) in a whole turn: a DETOUR slice gives SANDBOX charges by precision
## (1 at WEAK / GOOD, 2 at PERFECT, from the config); each charge negates one hit in
## resolution order (pointer index, then the target's pointers); the target's charge comes
## before its bodyguard; a status-only resolution is not negated. Preview equals the result
## in every case.

const SEED := 4242

var _null: SliceData
var _detour: SliceData


func before_all() -> void:
	_null = CombatFixture.slice(&"sbx_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	_detour = CombatFixture.slice(&"sbx_detour", RC.SliceType.DETOUR, 1, RC.TargetRule.SELF)


func _deck(id: StringName) -> Array[CardData]:
	return [CombatFixture.card(id, [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]


## The operative on `slices` (6) vs. an enemy whose six slices are SHIM `hit` with `pointers`.
func _session(slices: Array, hit: int, pointers: Array = [0]) -> CombatSession:
	var cls := CombatFixture.operative_class(&"sbx_class", 60, CombatFixture.wheel(slices), _deck(&"sbx_noop"))
	var foe := EnrageFixture.enemy(&"sbx_foe", RC.EnemyClass.NORMAL, hit, 999, null, pointers)
	return CombatSession.start(CombatFixture.resolver([cls, foe]), cls.id, [foe.id], SEED)


func _nulls() -> Array:
	return [_null, _null, _null, _null, _null, _null]


## [previewed HP lost, actual HP lost, the real result] for ending the turn now.
func _end(s: CombatSession) -> Array:
	var hp := s.state.player.hp
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	return [hp - pv.resolved_state.player.hp, hp - r.resolved_state.player.hp, r, pv]


func test_multi_hit_against_one_charge_negates_the_first_only() -> void:
	var s := _session(_nulls(), 2, [0, 5, 10, 15])
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	s.state.player.evade_charges = 1
	var out := _end(s)
	assert_eq(out[1], 6, "4 hits of 2 against 1 charge: the first is negated, 6 lands")
	assert_eq(out[0], out[1], "preview == result")
	var r: CombatResult = out[2]
	var hits := r.events.filter(func(e: Dictionary) -> bool: return e["type"] in ["evaded", "damage"])
	assert_eq(hits.size(), 4)
	assert_eq(String(hits[0]["type"]), "evaded", "resolution order: the first hit spends the charge")
	assert_true(bool(hits[0]["sandboxed"]))
	assert_eq(r.resolved_state.player.evade_charges, 0)


func test_one_charge_negates_a_30_hit() -> void:
	var s := _session(_nulls(), 30)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	s.state.player.evade_charges = 1
	var out := _end(s)
	assert_eq(out[1], 0)
	assert_eq(out[0], 0)


func test_detour_charges_by_precision() -> void:
	var cfg := CombatFixture.config()
	var want := {0: cfg.sandbox_charges_perfect, 1: cfg.sandbox_charges, 2: cfg.sandbox_charges}
	for offset: int in want:
		var s := _session([_detour, _detour, _detour, _detour, _detour, _detour], 0)
		CombatFixture.land(s.state.player, 0, offset)
		var pv := s.preview_end_turn()
		var r := s.apply(CombatAction.end_turn())
		assert_eq(r.resolved_state.player.evade_charges, want[offset], "offset %d" % offset)
		assert_eq(pv.resolved_state.player.evade_charges, r.resolved_state.player.evade_charges, "offset %d: preview == result" % offset)
		assert_eq(s.state.player.evade_charges, 0, "offset %d: the charges go at end of turn" % offset)


func test_perfect_detour_negates_two_hits_this_turn() -> void:
	var s := _session([_detour, _detour, _detour, _detour, _detour, _detour], 5, [0, 5, 10])
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	var out := _end(s)
	assert_eq(out[1], 5, "the defensive pass gives 2 charges before the enemy's 3 hits of 5")
	assert_eq(out[0], out[1])


func test_charge_comes_before_the_bodyguard() -> void:
	var atk := CombatFixture.slice(&"sbx_atk6", RC.SliceType.SHIM, 6)
	var cls := CombatFixture.operative_class(&"sbx_bg_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, atk]), _deck(&"sbx_noop2"))
	var drone := CombatFixture.enemy(&"sbx_drone", 5, CombatFixture.wheel([_null, _null]))
	var host := CombatFixture.enemy(&"sbx_host", 40, CombatFixture.wheel(_nulls()), [CombatFixture.spawn(drone, 2)])
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], SEED)
	var sat := s.state.satellites_of(&"enemy_0")[0]
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 2)
	s.state.get_combatant(&"enemy_0").evade_charges = 1
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "bodyguard").size(), 0, "the hit is negated before the redirect")
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 40)
	assert_eq(r.resolved_state.get_combatant(sat.id).hp, 5, "the drone is untouched")
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").evade_charges, 0)
	assert_eq(pv.resolved_state.state_hash(), r.resolved_state.state_hash(), "preview == result")


func test_bodyguard_still_guards_without_a_charge() -> void:
	var atk := CombatFixture.slice(&"sbx_atk6b", RC.SliceType.SHIM, 6)
	var cls := CombatFixture.operative_class(&"sbx_bg_class2", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, atk]), _deck(&"sbx_noop3"))
	var drone := CombatFixture.enemy(&"sbx_drone2", 5, CombatFixture.wheel([_null, _null]))
	var host := CombatFixture.enemy(&"sbx_host2", 40, CombatFixture.wheel(_nulls()), [CombatFixture.spawn(drone, 2)])
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], SEED)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 2)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "bodyguard").size(), 1)
	assert_eq(r.resolved_state.get_combatant(&"enemy_0").hp, 40)


func test_status_only_resolution_is_not_negated() -> void:
	var corrupt := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.POINTER_TARGET, 1, RC.RingScope.OUTER, 1.0, RC.Status.CORRUPTED)
	var te: Array[TriggeredEffectData] = [CombatFixture.triggered(RC.Trigger.ON_SLICE_TRIGGER, [corrupt])]
	var infect := CombatFixture.slice(&"sbx_infect", RC.SliceType.INFECT, 0, RC.TargetRule.POINTER, te)
	var s := _session([infect, infect, infect, infect, infect, infect], 0)
	CombatFixture.land(s.state.player, 0)
	var e := s.state.get_combatant(&"enemy_0")
	CombatFixture.land(e, 0)
	e.evade_charges = 1
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	var after := r.resolved_state.get_combatant(&"enemy_0")
	assert_eq(after.evade_charges, 1, "no charge spent on a status")
	assert_true(after.wheel.slice_statuses.has(RC.Status.CORRUPTED), "the status lands")
	assert_eq(pv.resolved_state.state_hash(), r.resolved_state.state_hash(), "preview == result")
