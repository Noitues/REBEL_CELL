extends GutTest
## Tooling 1 T2: the playtest HeuristicStrategist (tools/agent/heuristic_strategist.gd) answers
## every state decision with no LLM, from HeuristicStrategistConfigData; the same seed plays the
## same campaign.

const AgentSimulator := preload("res://tools/agent/agent_simulator.gd")
const HeuristicStrategist := preload("res://tools/agent/heuristic_strategist.gd")
const TurnPlanner := preload("res://tools/agent/turn_planner.gd")
const SOURCE := "res://tools/agent/heuristic_strategist.gd"
const KINDS: Array[String] = ["combat", "node", "reward", "event", "launch", "raid", "shop", "hq"]

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func _strategist(cfg: HeuristicStrategistConfigData = null) -> RefCounted:
	return HeuristicStrategist.new(cfg if cfg != null else HeuristicStrategistConfigData.shipped(), _resolver.lookup)


func _campaign(seed: int, runs: int) -> Dictionary:
	var sim = AgentSimulator.new(_resolver, "", [])
	sim.strategist = _strategist()
	var rep: Dictionary = sim.run_campaign(seed, 0, runs)
	rep["decisions"] = sim.decisions
	return rep


func test_same_seed_same_campaign() -> void:
	var a := _campaign(1000, 1)
	var b := _campaign(1000, 1)
	assert_eq(a["hash"], b["hash"], "same seed, same campaign state")
	var da: Array = a["decisions"]
	var db: Array = b["decisions"]
	assert_eq(da.size(), db.size())
	assert_gt(da.size(), 10, "a netrun asks many decisions")
	for i in mini(da.size(), db.size()):
		if da[i]["choice"] != db[i]["choice"] or da[i]["kind"] != db[i]["kind"]:
			fail_test("decision %d differs: %s vs %s" % [i, da[i], db[i]])
			return
	for d in da:
		assert_ne(String(d["reason"]), "timeout", "every decision answered in process")


func test_every_decision_kind_answered() -> void:
	var h := _strategist()
	var menus := {
		"node": [{"type": RC.InfilNodeType.ROUTER, "elite": false, "layer": 1, "heat": 0}, {"type": RC.InfilNodeType.MAINFRAME, "elite": false, "layer": 1, "heat": 0}],
		"reward": [{}, {"kind": "card", "id": "jolt", "slot": -1}, {"kind": "daemon", "id": "zero_day", "slot": -1}],
		"event": [{"index": 1}, {"index": 0}],
		"launch": [{"op_rank": 0, "tier": 1, "heat_change": 0, "objective": RC.SiteObjective.NONE, "patrol": false},
			{"op_rank": 2, "tier": 2, "heat_change": 0, "objective": RC.SiteObjective.EXPLOIT, "patrol": false}],
		"raid": [{"won": false, "campaign_lost": false, "home_after": 30, "threats_destroyed": 1, "down": 1, "taken": 0},
			{"won": true, "campaign_lost": false, "home_after": 50, "threats_destroyed": 2, "down": 0, "taken": 0}],
		"shop": [{"action": "leave"}, {"action": "remove", "id": "bug", "price": 50}],
		"hq": [{"action": "default"}, {"action": "done"}, {"action": "recruit", "price": 30}],
	}
	var ctx := {"hp": 60, "max_hp": 60, "cycles": 100, "campaign_heat": 0, "deck": [&"jolt"], "heat": 0, "exploits": 0,
		"schematics": 100, "living": 1, "rookie_price": 30, "claims": 0}
	for kind in menus:
		var r: Dictionary = h.choose(kind, ctx, menus[kind])
		assert_between(int(r["choice"]), 0, (menus[kind] as Array).size() - 1, kind)
		assert_false(String(r["reason"]).begins_with("unknown"), "%s has a rule: %s" % [kind, r["reason"]])
	# The expected picks: Exploit with the R2 operative, the raid plan that holds, the Bug removal, recruiting to two.
	assert_eq(int(h.choose("launch", ctx, menus["launch"])["choice"]), 1)
	assert_eq(int(h.choose("raid", ctx, menus["raid"])["choice"]), 1)
	assert_eq(int(h.choose("shop", ctx, menus["shop"])["choice"]), 1)
	assert_eq(int(h.choose("hq", ctx, menus["hq"])["choice"]), 2)
	# Combat, from a real turn's planner menu, with and without the 2-turn lookahead.
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 21, &"rank:1")
	var plans := TurnPlanner.plans(s)
	var meta: Array = []
	for p in plans:
		var o: Dictionary = p["outcome"]
		meta.append({"score": p["score"], "dealt": o["dealt"], "taken": o["taken"], "kills": o["kills"], "actions": p["actions"]})
	assert_eq(int(h.choose("combat", {"session": s}, meta)["choice"]), 0, "lookahead 1: the planner's best plan")
	h.lookahead_turns = 2
	var r2: Dictionary = h.choose("combat", {"session": s}, meta)
	assert_between(int(r2["choice"]), 0, meta.size() - 1)
	assert_string_contains(String(r2["reason"]), "lookahead")
	assert_eq(KINDS.size(), menus.size() + 1, "every kind the simulator asks is covered (combat above)")


func test_thresholds_come_from_the_config() -> void:
	var cfg := HeuristicStrategistConfigData.new()
	var elite_vs_router := [{"type": RC.InfilNodeType.ROUTER, "elite": true, "layer": 4, "heat": 0},
		{"type": RC.InfilNodeType.TERMINAL, "elite": false, "layer": 4, "heat": 0}]
	var ctx := {"hp": 33, "max_hp": 60, "cycles": 0, "campaign_heat": 0}
	cfg.elite_min_hp_share = 0.5
	assert_eq(int(_strategist(cfg).choose("node", ctx, elite_vs_router)["choice"]), 0, "55% HP: the Elite is fine")
	cfg.elite_min_hp_share = 0.6
	assert_eq(int(_strategist(cfg).choose("node", ctx, elite_vs_router)["choice"]), 1, "under the config's share: avoided")
	var breach := [{"op_rank": 5, "tier": 1, "heat_change": -5, "objective": RC.SiteObjective.NONE, "patrol": true},
		{"op_rank": 5, "tier": 4, "heat_change": 0, "objective": RC.SiteObjective.CENTRAL_SERVER, "patrol": false}]
	cfg.breach_max_heat = 20
	assert_eq(int(_strategist(cfg).choose("launch", {"heat": 15}, breach)["choice"]), 1)
	cfg.breach_max_heat = 10
	assert_eq(int(_strategist(cfg).choose("launch", {"heat": 15}, breach)["choice"]), 0, "too hot to breach: scrub")
	# Every threshold is read, and the source holds no tuning literal (rule 5).
	var src := FileAccess.get_file_as_string(SOURCE)
	for p in cfg.get_property_list():
		if int(p["usage"]) & PROPERTY_USAGE_SCRIPT_VARIABLE:
			assert_string_contains(src, "config." + String(p["name"]), "the strategist reads %s" % p["name"])
	var code := PackedStringArray()
	for line in src.split("\n"):
		var l := line.strip_edges()
		if l.begins_with("#"):
			continue
		var q := RegEx.create_from_string("\"[^\"]*\"").sub(l, "", true)
		code.append(q.split("#")[0])
	var literals := RegEx.create_from_string("(?<![A-Za-z_0-9.])\\d+\\.?\\d*").search_all("\n".join(code))
	for m in literals:
		assert_true(m.get_string() in ["0", "1", "2", "0.0", "1.0", "100.0"], "tuning literal %s belongs in the config" % m.get_string())


func test_shipped_config_validates() -> void:
	var cfg := HeuristicStrategistConfigData.shipped()
	assert_not_null(cfg)
	assert_eq(cfg.validate().size(), 0, str(cfg.validate()))
