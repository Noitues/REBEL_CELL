extends GutTest
## Plan 2 N1b (R2 "tier scales enemy hits"): an enemy's DEAL_DAMAGE *effects* (Hub
## listeners, slice extra effects, satellites) scale by the tier damage factor exactly as
## its slice hits do since N1/N2; the operative's effects never do; a slice hit is scaled
## once, not twice; preview == result; a seeded replay matches.

const TIER_FACTORS: Array[float] = [1.0, 1.3, 1.69, 2.2]
const EXPECTED: Array[int] = [10, 13, 17, 22]

var _cfg: CampaignConfigData
var _hub_enemy: EnemyData
var _slice_enemy: EnemyData
var _host: EnemyData
var _resolver: CombatResolver


func before_all() -> void:
	_cfg = CombatFixture.config()
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.POINTER_TARGET, 10)
	var hub := CombatFixture.hub(&"n1b_hub", 0, [CombatFixture.triggered(RC.Trigger.ON_TURN_START, [dmg])])
	_hub_enemy = CombatFixture.enemy(&"n1b_hub_enemy", 300, CombatFixture.null_wheel(0, hub))
	var extra := CombatFixture.triggered(RC.Trigger.ON_SLICE_TRIGGER, [dmg])
	var shim := CombatFixture.slice(&"n1b_shim", RC.SliceType.SHIM, 10, RC.TargetRule.POINTER, [extra])
	_slice_enemy = CombatFixture.enemy(&"n1b_slice_enemy", 300, CombatFixture.wheel([shim, shim, shim, shim, shim, shim]))
	var sat := CombatFixture.enemy(&"n1b_sat", 5, CombatFixture.null_wheel())
	_host = CombatFixture.enemy(&"n1b_host", 300, CombatFixture.null_wheel(), [CombatFixture.spawn(sat, 2)])
	_resolver = CombatFixture.resolver([hub, _hub_enemy, shim, _slice_enemy, sat, _host])


## `park`: a roomy operative parked on slot 5 and the enemy on a centred slot 0 (Perfect,
## no Weak multiplier). Replays start unparked, since setup carries no hand edits.
func _session(enemy: EnemyData, tier: int, seed: int = 7, park: bool = true) -> CombatSession:
	var o := {"tier": tier, "enemy_scale": 1.0, "enemy_output_scale": _cfg.enemy_damage_factor(tier)}
	var s := CombatSession.start(_resolver, &"breaker", [enemy.id], seed, &"", 0, o)
	if park:
		s.state.player.max_hp = 500
		s.state.player.hp = 500
		CombatFixture.land(s.state.player, 5)
		CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	return s


## Damage events from `attacker` in `r` (the pre-absorb hit amount, after enrage).
func _hits(r: CombatResult, attacker: StringName) -> Array:
	var out := []
	for e in CombatFixture.events_of(r, "damage"):
		if e["attacker"] == attacker:
			out.append(int(e["amount"]))
	return out


func _end_turn_checked(s: CombatSession) -> CombatResult:
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	assert_eq(pv.state.state_hash(), r.resolved_state.state_hash(), "End Turn preview == resolved state")
	assert_eq(pv.state.player.hp, r.resolved_state.player.hp, "preview HP == result HP")
	return r


func test_config_factors_are_the_brief_table() -> void:
	for t in range(1, 5):
		assert_almost_eq(_cfg.enemy_damage_factor(t), TIER_FACTORS[t - 1], 0.0001, "T%d factor" % t)


func test_hub_damage_effect_scales_by_tier() -> void:
	var got := []
	for t in range(1, 5):
		var s := _session(_hub_enemy, t)
		var r := _end_turn_checked(s)
		var hits := _hits(r, &"enemy_0")
		assert_eq(hits.size(), 1, "T%d: one Hub hit" % t)
		got.append(hits[0] if not hits.is_empty() else -1)
	assert_eq(got, EXPECTED, "round(10 x factor) at T1-T4")


func test_slice_extra_effect_scales_and_slice_hit_is_not_scaled_twice() -> void:
	for t in range(1, 5):
		var s := _session(_slice_enemy, t)
		var r := _end_turn_checked(s)
		var hits := _hits(r, &"enemy_0")
		# One slice hit plus its extra DEAL_DAMAGE effect, both at round(10 x factor);
		# a double-scaled hit would read round(10 x factor^2) (48 at T4).
		assert_eq(hits.size(), 2, "T%d: slice hit + extra effect" % t)
		for h in hits:
			assert_eq(h, EXPECTED[t - 1], "T%d: every enemy hit is round(10 x factor) once" % t)
		for a in CombatFixture.events_of(r, "attack"):
			if a["attacker"] == &"enemy_0":
				assert_eq(int(a["amount"]), EXPECTED[t - 1], "T%d: attack line equals the hit" % t)


func test_satellite_effect_inherits_the_host_factor() -> void:
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.POINTER_TARGET, 10)
	for t in range(1, 5):
		var s := _session(_host, t)
		var sat: CombatantState = null
		for e in s.state.enemies:
			if e.host_id == &"enemy_0":
				sat = e
		assert_not_null(sat, "satellite docked")
		if sat != null:
			assert_eq(s.resolver.fx.damage_amount(dmg, sat), EXPECTED[t - 1], "T%d satellite effect" % t)


func test_player_effect_unscaled() -> void:
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.POINTER_TARGET, 10)
	var s := _session(_hub_enemy, 4)
	var p := s.state.player
	p.output_scale = TIER_FACTORS[3]  # even a stray factor on the operative is ignored
	assert_eq(s.resolver.fx.damage_amount(dmg, p), 10, "operative effect unscaled")
	var events: Array[Dictionary] = []
	var enemy := s.state.get_combatant(&"enemy_0")
	var before := enemy.hp
	s.resolver.fx.apply_effect(s.state, dmg, {"owner": p, "target": enemy}, CombatFixture.rng(1), events)
	assert_eq(before - enemy.hp, 10, "the operative's DEAL_DAMAGE 10 lands as 10 at T4")


func test_percent_amount_never_rescaled() -> void:
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.POINTER_TARGET, 10)
	dmg.amount_mode = RC.AmountMode.PERCENT
	var s := _session(_hub_enemy, 4)
	assert_eq(s.resolver.fx.damage_amount(dmg, s.state.get_combatant(&"enemy_0")), 10, "PERCENT skips the tier factor")


func test_seeded_replay_matches() -> void:
	for enemy in [_hub_enemy, _slice_enemy]:
		for seed in [1, 7, 1000]:
			var a := _session(enemy, 3, seed, false)
			var b := _session(enemy, 3, seed, false)
			for s in [a, b]:
				for i in 2:
					s.apply(CombatAction.nudge(&"enemy_0", 1))
					s.apply(CombatAction.end_turn())
			assert_eq(a.state_hash(), b.state_hash(), "%s seed %d" % [enemy.id, seed])
			var r := CombatSession.replay(_resolver, a.setup, a.combat_seed, a.history)
			assert_eq(r.state_hash(), a.state_hash(), "seeded replay matches (%s seed %d)" % [enemy.id, seed])
