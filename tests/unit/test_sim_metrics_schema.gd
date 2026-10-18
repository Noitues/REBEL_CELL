extends GutTest
## N19: the result row schema and the aggregation / pass-criteria math (tools/balance/phase_metrics.py).

const BalanceRunner := preload("res://tools/balance/balance_runner.gd")
const AGG := "res://tools/balance/phase_metrics.py"
const OLD := "res://tests/fixtures/sim_metrics/baseline_old.json"


func _aggregate(records: Array) -> Variant:
	var path := "user://n19_agg.json"
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify({"records": records}))
	f.close()
	var out: Array = []
	var rc := OS.execute("python", PackedStringArray([ProjectSettings.globalize_path(AGG), "aggregate", ProjectSettings.globalize_path(path)]), out, true)
	DirAccess.remove_absolute(path)
	if rc == -1:
		return "no python"
	assert_eq(rc, 0, "phase_metrics.py ran")
	return JSON.parse_string(String(out[0]))


func _rec(turns: Array, won: int = 1) -> Dictionary:
	var phases: Array = []
	for t in turns:
		phases.append({"turns": t, "parked": 2, "intake": 5, "heal_turns": 0, "resistance_absorbed": 1, "incomplete": false})
	return {"group": "g", "seed": 1, "scalars": {"won": won}, "metrics": {"phases": phases, "enrage_step": 1, "listener_fires": null,
		"turn_manipulation": {"own": 1, "enemy": 1, "both": 2, "none": 0}}}


func test_result_row_has_the_required_keys() -> void:
	var runner := BalanceRunner.new(ContentRegistry, {"skill": 0.6}, [])
	var rec := runner.run_fight(&"ground_control", 1, 1006)
	var m: Dictionary = rec["metrics"]
	for k in ["phases", "enrage_step", "listener_fires", "turn_manipulation"]:
		assert_true(m.has(k), k)
	for k in ["turns", "parked", "parked_by_path", "intake", "heal_turns", "resistance_absorbed", "incomplete"]:
		assert_true(m["phases"][0].has(k), k)
	assert_null(m["listener_fires"], "N6 absent")


func test_old_baseline_without_metrics_aggregates_to_null() -> void:
	var data = JSON.parse_string(FileAccess.get_file_as_string(OLD))
	assert_not_null(data)
	var agg = _aggregate(data["records"])
	if agg is String:
		pending("python is not on PATH here")
		return
	assert_null(agg)


func test_mean_p90_in_target_and_both_share() -> void:
	var recs: Array = []
	for t in [6, 7, 7, 8, 8, 8, 9, 9, 10, 12]:
		recs.append(_rec([t]))
	var agg = _aggregate(recs)
	if agg is String:
		pending("python is not on PATH here")
		return
	assert_almost_eq(float(agg["turns_mean"]), 8.4, 0.0001)
	assert_eq(int(agg["turns_p90"]), 10)  # nearest rank
	assert_eq(float(agg["in_target"]), 0.0)
	assert_almost_eq(float(agg["turns_with_both_share"]), 0.5, 0.0001)


func test_in_target_band_is_three_to_four() -> void:
	var agg = _aggregate([_rec([2, 3, 4, 5])])
	if agg is String:
		pending("python is not on PATH here")
		return
	assert_almost_eq(float(agg["in_target"]), 0.5, 0.0001)
	assert_eq(int(agg["phases_over_4"]), 1)


func test_empty_phase_list_does_not_divide_by_zero() -> void:
	var r := _rec([])
	var agg = _aggregate([r])
	if agg is String:
		pending("python is not on PATH here")
		return
	assert_not_null(agg)
	assert_null(agg["in_target"])
	assert_null(agg["phase_turns_mean"])


func test_incomplete_phase_is_left_out_of_the_phase_turn_stats() -> void:
	var r := _rec([4, 1])
	r["metrics"]["phases"][1]["incomplete"] = true
	var agg = _aggregate([r])
	if agg is String:
		pending("python is not on PATH here")
		return
	assert_almost_eq(float(agg["phase_turns_mean"]), 4.0, 0.0001)


func test_heal_over_limit_counts_phases_with_more_than_one_heal_turn() -> void:
	var r := _rec([4, 4])
	r["metrics"]["phases"][0]["heal_turns"] = 3
	var agg = _aggregate([r])
	if agg is String:
		pending("python is not on PATH here")
		return
	assert_eq(int(agg["heal_over_limit"]), 1)
	assert_eq(int(agg["heal_turns_per_phase_max"]), 3)
