extends GutTest
## BAL-01: the named reference policy (heuristic bot at lookahead 2) is deterministic: the same seeds give the same
## JSON, and `--policy reference` equals `--policy heuristic --lookahead 2` except for the policy name.

const BalanceRunner := preload("res://tools/balance/balance_runner.gd")
const ENEMY := &"ground_control"
const SEEDS: Array = [1000, 1001]


func _report(opts: Dictionary) -> Dictionary:
	var runner := BalanceRunner.new(ContentRegistry, opts, [])
	assert_eq(runner.errors.size(), 0)
	var rep := runner.run("fight", SEEDS)
	return JSON.parse_string(JSON.stringify(rep, "", true))


func test_reference_rerun_is_identical_and_equals_heuristic_lookahead_2() -> void:
	var base := {"enemy": [String(ENEMY)], "tiers": [1]}
	var a := _report(base.merged({"policy": "reference"}))
	var b := _report(base.merged({"policy": "reference"}))
	assert_eq(JSON.stringify(a), JSON.stringify(b), "same seeds, same JSON")
	assert_eq(int(a["opts"]["lookahead"]), int(BalanceRunner.defaults()["reference_lookahead"]), "lookahead comes from config")
	var h := _report(base.merged({"policy": "heuristic", "lookahead": int(BalanceRunner.defaults()["reference_lookahead"])}))
	a["opts"]["policy"] = "x"
	h["opts"]["policy"] = "x"
	assert_eq(JSON.stringify(a), JSON.stringify(h), "reference == heuristic at the reference lookahead")
	assert_gt(a["records"].size(), 0)
