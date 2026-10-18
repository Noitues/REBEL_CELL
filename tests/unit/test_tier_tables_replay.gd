extends GutTest
## N2 (CLAUDE.md rule 6): the tier tables keep the core deterministic. Same seed + inputs
## = same hash; the End Turn preview equals the result at every tier; a save round trip
## keeps the table HP; the scale reads touch no RNG.

var _cfg: CampaignConfigData
var _hitter: EnemyData
var _resolver: CombatResolver


func before_all() -> void:
	_cfg = CombatFixture.config()
	var shim := CombatFixture.slice(&"n2r_shim", RC.SliceType.SHIM, 6)
	_hitter = CombatFixture.enemy(&"n2r_hitter", 30, CombatFixture.wheel([shim, shim, shim, shim, shim, shim]))
	_hitter.hp_by_tier = PackedInt32Array([32, 40, 50, 63])
	_resolver = CombatFixture.resolver([shim, _hitter])


func _overrides(tier: int) -> Dictionary:
	return {"tier": tier, "enemy_scale": _cfg.enemy_hp_scale(tier), "enemy_output_scale": _cfg.enemy_damage_factor(tier)}


func _session(tier: int, seed: int = 7) -> CombatSession:
	return CombatSession.start(_resolver, &"breaker", [&"n2r_hitter"], seed, &"rank:1", 0, _overrides(tier))


func _play(s: CombatSession, turns: int) -> void:
	for i in turns:
		if s.state.is_over():
			return
		s.apply(CombatAction.nudge(&"enemy_0", 1))
		s.apply(CombatAction.end_turn())


func test_same_seed_same_state_hash() -> void:
	for seed in [1, 7, 1000]:
		var a := _session(3, seed)
		var b := _session(3, seed)
		_play(a, 3)
		_play(b, 3)
		assert_eq(a.state_hash(), b.state_hash(), "seed %d" % seed)
		var r := CombatSession.replay(_resolver, a.setup, a.combat_seed, a.history)
		assert_eq(r.state_hash(), a.state_hash(), "seeded replay matches (seed %d)" % seed)


func test_preview_damage_equals_result_at_each_tier() -> void:
	for t in range(1, 5):
		var s := _session(t)
		assert_eq(s.state.get_combatant(&"enemy_0").max_hp, _hitter.hp_by_tier[t - 1])
		var before := s.state.player.hp
		var predicted := s.preview_end_turn()
		var actual := s.apply(CombatAction.end_turn())
		assert_eq(predicted.state.state_hash(), actual.resolved_state.state_hash(), "T%d preview == result" % t)
		assert_eq(predicted.state.player.hp, actual.resolved_state.player.hp)
		if t == 4:
			assert_true(before - actual.resolved_state.player.hp > 0, "the hitter hit")


func test_damage_grows_with_the_table() -> void:
	var losses := []
	for t in range(1, 5):
		var s := _session(t)
		var before := s.state.player.hp
		var actual := s.apply(CombatAction.end_turn())
		losses.append(before - actual.resolved_state.player.hp)
	for t in range(1, 4):
		assert_true(losses[t] >= losses[t - 1], "T%d hits at least as hard as T%d (%s)" % [t + 1, t, str(losses)])


func test_save_round_trip_preserves_scaled_hp() -> void:
	var s := _session(4)
	_play(s, 1)
	var back := CombatSession.from_dict(_resolver, JSON.parse_string(JSON.stringify(s.to_dict())))
	var e := back.state.get_combatant(&"enemy_0")
	assert_eq(e.max_hp, 63)
	assert_eq(e.hp, s.state.get_combatant(&"enemy_0").hp)
	assert_eq(back.state_hash(), s.state_hash())


func test_setup_without_tier_replays_as_t1() -> void:
	var setup := {"class_id": "breaker", "enemy_ids": ["n2r_hitter"], "ring_id": "rank:1", "heat_majors_crossed": 0, "overrides": {}}
	var r := CombatSession.replay(_resolver, setup, 5, [] as Array[CombatAction])
	assert_eq(r.state.get_combatant(&"enemy_0").max_hp, 32, "a pre-N2 setup has no tier: T1")


func test_scale_reads_touch_no_rng() -> void:
	var c := CampaignState.new()
	c.campaign_seed = 7
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	var s := NetrunSession.start_special(_resolver, c, &"op_1", "reclaim", &"t1_a", 3, 5, &"n2r_hitter", {})
	var streams_before := JSON.stringify(s.streams.to_dict())
	for i in 3:
		s.enemy_scale()
		s.enemy_output_scale()
	assert_eq(JSON.stringify(s.streams.to_dict()), streams_before, "no RNG stream read or advanced")


func test_no_global_random_in_scaling_sources() -> void:
	for path in ["res://scripts/core/hp_band_lint.gd", "res://scripts/data/enemy_data.gd", "res://scripts/data/campaign_config_data.gd"]:
		var src := FileAccess.get_file_as_string(path)
		for bad in ["randi(", "randf(", "randomize("]:
			assert_false(src.contains(bad), "%s calls %s" % [path, bad])


func test_lint_report_order_is_deterministic() -> void:
	var a := CombatFixture.enemy(&"n2r_b", 30, CombatFixture.null_wheel())
	var b := CombatFixture.enemy(&"n2r_a", 30, CombatFixture.null_wheel())
	var one := HpBandLint.lint([a, b] as Array[EnemyData], _cfg)
	var two := HpBandLint.lint([b, a] as Array[EnemyData], _cfg)
	assert_eq(one["warnings"], two["warnings"])
	assert_string_contains(one["warnings"][0], "n2r_a")
