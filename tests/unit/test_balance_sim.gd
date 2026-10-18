extends GutTest
## BalanceSim (docs/handoff/plan2/BALANCE_SIM.md): data overrides never touch a loaded Resource, a seed plus
## overrides always gives the same report, a fight-mode result equals a CombatResolver replay of its seed, and the
## `balance` branch path guard rejects anything but data and balance tooling.

const BalanceContent := preload("res://tools/balance/balance_content.gd")
const BalanceRunner := preload("res://tools/balance/balance_runner.gd")
const ENEMY := &"ground_control"


func _enemy(reg: Object) -> EnemyData:
	return reg.get_content(ENEMY) as EnemyData


func test_overrides_never_mutate_a_loaded_resource() -> void:
	var cfg: CampaignConfigData = ContentRegistry.config
	var enemy := _enemy(ContentRegistry)
	var before_heat := cfg.heat_max
	var before_hp := enemy.hp
	var before_rack := cfg.rack_heat_by_tier.duplicate()
	var before_cycles := cfg.cycles_combat_range
	var before_slice0 := enemy.wheel.slice_count
	var bc := BalanceContent.new(ContentRegistry)
	var errors := bc.apply_all([
		"config.heat_max=%d" % (before_heat + 50), "%s.hp=999" % ENEMY, "config.rack_heat_by_tier.0=77",
		"config.cycles_combat_range*=2", "config.target_turns_per_phase+=1"])
	assert_eq(errors.size(), 0, "all overrides apply: %s" % str(errors))
	# the loaded Resources are untouched
	assert_eq(cfg.heat_max, before_heat)
	assert_eq(enemy.hp, before_hp)
	assert_eq(cfg.rack_heat_by_tier, before_rack)
	assert_eq(cfg.cycles_combat_range, before_cycles)
	assert_eq(enemy.wheel.slice_count, before_slice0)
	# the copies carry them, and are copies
	var copy := bc.content(ENEMY) as EnemyData
	assert_ne(copy, enemy, "the sim holds a duplicate")
	assert_true(bc.is_copy(copy))
	assert_false(bc.is_copy(enemy))
	assert_eq(copy.hp, 999)
	assert_eq(bc.config.heat_max, before_heat + 50)
	assert_eq(bc.config.rack_heat_by_tier[0], 77)
	assert_eq(bc.config.cycles_combat_range, Vector2i(before_cycles.x * 2, before_cycles.y * 2))
	assert_ne(bc.config, cfg)
	assert_eq(bc.lookup.get_content(ENEMY), copy, "the lookup resolves to the copy")
	assert_ne(copy.wheel, enemy.wheel, "nested resources are copied too")
	assert_ne(bc.apply("config.no_such_property=1"), "", "a bad path is an error, not a silent no-op")
	assert_ne(bc.apply("no_such_id.hp=1"), "")


func _report(specs: Array, mode: String, opts: Dictionary, seeds: Array) -> String:
	var runner := BalanceRunner.new(ContentRegistry, opts, specs)
	assert_eq(runner.errors.size(), 0)
	return JSON.stringify(runner.run(mode, seeds), "", true)


func test_same_seed_and_overrides_give_the_same_report() -> void:
	var opts := {"enemy": [String(ENEMY)], "tiers": [1, 2], "skill": 0.5}
	var specs := ["%s.hp*=1.5" % ENEMY]
	var a := _report(specs, "fight", opts, [1000, 1001, 1002])
	var b := _report(specs, "fight", opts, [1000, 1001, 1002])
	assert_eq(a, b, "fight reports are identical for the same seeds and overrides")
	var other := _report(["%s.hp*=3" % ENEMY], "fight", opts, [1000, 1001, 1002])
	assert_ne(a, other, "a different override changes the report")
	var n1 := _report([], "netrun", {"tier": 1, "skill": 0.7}, [1000, 1001])
	var n2 := _report([], "netrun", {"tier": 1, "skill": 0.7}, [1000, 1001])
	assert_eq(n1, n2, "netrun reports (the skill dice included) are identical")


func test_fight_mode_equals_a_resolver_replay() -> void:
	var runner := BalanceRunner.new(ContentRegistry, {"skill": 0.6}, [])
	var rec := runner.run_fight(ENEMY, 2, 1003)
	var played := runner.last_combat
	assert_not_null(played)
	assert_true(played.state.is_over(), "the fight was played to its end")
	# replay the recorded actions from the same seed on a resolver built straight from the loaded content
	var plain := CombatResolver.new(ContentRegistry.config, ContentLookup.new().add_registry(ContentRegistry))
	var replay := CombatSession.replay(plain, played.setup, played.combat_seed, played.history)
	assert_eq(replay.state.state_hash(), played.state.state_hash(), "replay reaches the same state")
	assert_eq(replay.state.state_hash(), int(rec["scalars"]["combat_hash"]), "the record carries that state's hash")
	assert_eq(replay.state.outcome == CombatState.Outcome.VICTORY, int(rec["scalars"]["won"]) == 1)
	assert_eq(replay.state.player.hp, int(rec["scalars"]["hp_end"]))


func test_quiet_events_change_nothing_but_the_text() -> void:
	# S4b: the simulation switch skips event texts only: states, hashes and every metric stay identical.
	var opts := {"enemy": [String(ENEMY), "port_authority"], "tiers": [1, 3], "skill": 0.8}
	var loud := _report([], "fight", opts.merged({"quiet": false}), [1000, 1001])
	var quiet := _report([], "fight", opts.merged({"quiet": true}), [1000, 1001])
	var a: Dictionary = JSON.parse_string(loud)
	var b: Dictionary = JSON.parse_string(quiet)
	assert_eq(a["records"], b["records"], "quiet and loud runs give the same records")


func _guard(branch: String, paths: Array) -> int:
	var script := ProjectSettings.globalize_path("res://tools/balance/path_guard.py")
	var args := PackedStringArray([script, "--branch", branch])
	args.append_array(PackedStringArray(paths))
	var out: Array = []
	return OS.execute("python", args, out, true)


func test_path_guard_rejects_non_data_files_on_the_balance_branch() -> void:
	var probe := _guard("main", ["scripts/core/x.gd"])
	if probe == -1:
		pending("python is not on PATH here")
		return
	assert_eq(probe, 0, "other branches are not guarded")
	assert_eq(_guard("balance", ["scripts/core/x.gd"]), 1, "a code file is rejected")
	assert_eq(_guard("balance", ["content/enemies/ground_control.tres", "scripts/core/x.gd"]), 1, "one bad path fails the commit")
	assert_eq(_guard("balance", ["tests/unit/test_x.gd"]), 1)
	assert_eq(_guard("balance", ["content/config/campaign_config.tres", "docs/balance/BASELINE_x.md", "tools/balance/balance.py"]), 0,
		"content, docs/balance and tools/balance pass")
