extends GutTest
## N19: collecting metrics is observational: same state hash on and off, byte-equal repeats, no RNG in the collector.

const BalanceRunner := preload("res://tools/balance/balance_runner.gd")
const ENEMY := &"ground_control"


func _fight(collect: bool, fight_seed: int) -> Dictionary:
	var runner := BalanceRunner.new(ContentRegistry, {"skill": 0.6}, [])
	runner.collect_metrics = collect
	return runner.run_fight(ENEMY, 2, fight_seed)


func test_collection_does_not_change_the_state_hash_or_results() -> void:
	var on := _fight(true, 1003)
	var off := _fight(false, 1003)
	assert_eq(on["scalars"]["combat_hash"], off["scalars"]["combat_hash"])
	for k in off["scalars"]:
		assert_eq(on["scalars"][k], off["scalars"][k], "scalar %s is unchanged" % k)
	assert_true(on.has("metrics"))
	assert_false(off.has("metrics"))


func test_same_seed_gives_byte_equal_metrics() -> void:
	var a := JSON.stringify(_fight(true, 1004), "", true)
	var b := JSON.stringify(_fight(true, 1004), "", true)
	assert_eq(a, b)


func test_phase_turns_sum_to_the_fight_turns() -> void:
	var rec := _fight(true, 1005)
	var sum := 0
	for p in rec["metrics"]["phases"]:
		sum += int(p["turns"])
	assert_eq(sum, int(rec["scalars"]["turns"]))


func test_collector_source_has_no_rng_call() -> void:
	var text := FileAccess.get_file_as_string("res://tools/balance/sim_metrics.gd")
	assert_ne(text, "")
	for banned in ["randi", "randf", "randomize", "RandomNumberGenerator", "RngService", "shuffle", "pick_random"]:
		assert_eq(text.find(banned), -1, "no %s in the collector" % banned)
