extends GutTest
## Solace tide, Phase 2a (SOLACE_RAID_SPEC.md section 10, item 1): golden parity. The port (SolaceTideBoard,
## SolaceTideRules, SolaceTideState) replays tools/raid_concepts/data/solace_raid_golden.json, written by the oracle
## (tools/raid_concepts/sweep_g1.py, variant H7C = H5 + R-I CITY LOST at raid end + R-J known beams aim at owned Sites
## (H6) + R-K retake TAKEN Sites + R-L a sentry shields its Site + R-M the tier SITES LOST (H7) + H7c: cadence 3, a one-beam
## shield, unguarded DOWN Sites fall at the close; the H7, H6 and H5 goldens are kept as solace_raid_golden_h7.json,
## solace_raid_golden_h6.json and solace_raid_golden_h5.json). Draws and hands are FED from the golden (Python's random streams differ
## from RngService), so only the rules are compared, never RNG output.

const GOLDEN := "res://tools/raid_concepts/data/solace_raid_golden.json"

var _g: Dictionary = {}
var _cfg: CampaignConfigData
var _board: SolaceTideBoard
var _home_max: int = 0
var _errs: Array[String] = []
## The naive player's placements come from its own rule (not the planner's list): not checked against `placements`.
var _naive: bool = false


func before_all() -> void:
	_cfg = load("res://content/config/campaign_config.tres")
	var f := FileAccess.open(GOLDEN, FileAccess.READ)
	_g = _norm(JSON.parse_string(f.get_as_text()))
	_board = SolaceTideBoard.from_dict(_g["graph"], _cfg.solace_tide_route_max_links)
	_home_max = int(_g["config"]["real"]["home_integrity"])


func before_each() -> void:
	_errs.clear()


## JSON numbers parse as floats: whole numbers become ints.
func _norm(v: Variant) -> Variant:
	if v is float and is_equal_approx(fposmod(v, 1.0), 0.0) and absf(v) < 1.0e12:
		return int(v)
	if v is Array:
		var a: Array = []
		for x in v:
			a.append(_norm(x))
		return a
	if v is Dictionary:
		var d := {}
		for k in v.keys():
			d[k] = _norm(v[k])
		return d
	return v


## StringNames to Strings, deeply, so ours compare with the golden's.
func _plain(v: Variant) -> Variant:
	if v is StringName:
		return String(v)
	if v is Array:
		var a: Array = []
		for x in v:
			a.append(_plain(x))
		return a
	return v


func _bad(msg: String) -> void:
	_errs.append(msg)


func _eq(label: String, got: Variant, want: Variant) -> void:
	if _plain(got) != want:
		_bad("%s: got %s want %s" % [label, str(_plain(got)).left(300), str(want).left(300)])


func _done() -> void:
	assert_eq(_errs.size(), 0, "\n".join(_errs.slice(0, 8)))


func _state(d: Dictionary) -> SolaceTideState:
	var s := SolaceTideState.from_dict(d)
	s.home_max = _home_max
	return s


func _state_eq(label: String, got: SolaceTideState, want: Dictionary) -> void:
	var gd := got.to_dict()
	for k in want.keys():
		if gd[k] != want[k]:
			_bad("%s: state.%s got %s want %s" % [label, k, str(gd[k]).left(200), str(want[k]).left(200)])


func _find_place(places: Array, want: Dictionary) -> bool:
	for p in places:
		if p["ghost"] == want["ghost"] and (p["sentries"] as Dictionary).size() == (want["sentries"] as Dictionary).size():
			var same := true
			for k in want["sentries"].keys():
				if not (p["sentries"] as Dictionary).has(k) or p["sentries"][k] != want["sentries"][k]:
					same = false
					break
			if same:
				return true
	return false


# ------------------------------------------------------------------------------------------------ board and tables
func test_route_pool_and_board() -> void:
	var pool: Array = _g["graph"]["route_pool"]
	_eq("route pool size", _board.route_pool.size(), pool.size())
	_eq("route pool", _board.route_pool, pool)
	assert_eq(_board.route_pool.size(), 29, "29 Solace routes")
	_done()


func test_config_matches_oracle() -> void:
	var r: Dictionary = _g["config"]["rules"]
	var real: Dictionary = _g["config"]["real"]
	var c := _cfg
	assert_eq(c.solace_tide_hand_base, 4)
	_eq("hand heat", Array(c.solace_tide_hand_heat), _norm(_csv(r["HAND_HEAT"])))
	_eq("beam heat", Array(c.solace_tide_beam_heat), _norm(_csv(r["BEAM_HEAT"])))
	_eq("max placed", c.solace_tide_max_placed, r["MAX_PLACED"])
	_eq("ghost start", c.solace_tide_ghost_start, _g["config"]["lab"]["GHOST_START"])
	_eq("ghost heat", c.solace_tide_ghost_heat, _g["config"]["lab"]["GHOST_HEAT"])
	_eq("response heat", c.solace_tide_card_response_heat, _g["config"]["lab"]["SPOOF_HEAT"])
	_eq("early raids", c.solace_tide_early_raids, r["EARLY_RAIDS"])
	_eq("early route", c.solace_tide_early_route_pct, int(round(float(r["EARLY_ROUTE"]) * 100.0)))
	_eq("known route", c.solace_tide_known_route_pct, int(round(float(r["KNOWN_ROUTE"]) * 100.0)))
	_eq("damage", Array(c.solace_tide_home_hit_damage_by_band), real["home_hit_damage_by_band"])
	_eq("spread", c.solace_tide_spread_min, r["SPREAD_MIN"])
	_eq("doses", c.solace_tide_doses_per_decay, r["DOSES_PER_DECAY"])
	_eq("dose every", c.solace_tide_dose_every, r["DOSE_EVERY"])
	_eq("sac gap", c.solace_tide_sacrifice_gap, r["SAC_GAP"])
	_eq("clean", c.solace_tide_clean_price, r["CLEAN"])
	_eq("raid every", c.solace_tide_raid_every, r["RAID_EVERY"])
	_eq("home infects", c.solace_tide_home_hit_infects, r["HOME_INF"] == 1)
	_eq("retries", c.solace_tide_breach_retries, r["BREACH_RETRY"])
	_eq("divert", c.solace_tide_divert, r["DIVERT"] == 1)
	_eq("city lost at raid end (R-I)", c.solace_tide_city_lost_at_raid_end, r["CITY_END"] == 1)
	_eq("known beams aim (R-J)", c.solace_tide_known_target, r["KNOWN_TARGET"] == 1)
	_eq("retake TAKEN (R-K)", c.solace_tide_retake_taken, r["RETAKE"] == 1)
	_eq("retake heat (R-K)", c.solace_tide_retake_heat, r["RETAKE_HEAT"])
	_eq("retake schematics (R-K)", c.solace_tide_retake_schematics, r["RETAKE_COST"])
	_eq("sentry shields (R-L)", c.solace_tide_sentry_shields, r["SHIELD"] == 1)
	_eq("shield beams (H7c)", c.solace_tide_sentry_shield_beams, int(r.get("SHIELD_BEAMS", 0)))
	_eq("unguarded fall (H7c)", c.solace_tide_unguarded_fall, int(r.get("DECAY_FAST", 0)) == 1)
	_eq("step pct", c.solace_tide_infected_front_step_pct, r["INF_STEP_PCT"])
	_eq("start deck", c.solace_tide_start_cards(), _g["config"]["lab"]["START_DECK"])
	# the existing keys the tide reads
	_eq("heat bands", Array(c.heat_band_levels()), [25, 50, 75, 100])
	_eq("clean heat", c.clean_defense_heat, real["clean_defense_heat"])
	_eq("raid schematics", Array(c.raid_schematics_by_tier), real["raid_schematics_by_tier"])
	_eq("rack heat", Array(c.rack_heat_by_tier), real["rack_heat_by_tier"])
	_eq("rack schematics", Array(c.rack_schematics_by_tier), real["rack_schematics_by_tier"])
	_eq("exploit heat", c.exploit_heat, real["exploit_heat"])
	_eq("death heat", c.death_heat_base, real["death_heat_base"])
	_eq("node cost", c.node_base_cost, real["node_base_cost"])
	_eq("heat purchase", [c.heat_purchase_amount, c.heat_purchase_cost, c.heat_purchase_increment],
		[real["heat_purchase_amount"], real["heat_purchase_cost"], real["heat_purchase_increment"]])
	_eq("heat max", c.heat_max, real["heat_max"])
	_done()


func _csv(s: String) -> Array:
	var out: Array = []
	for x in s.split(","):
		out.append(int(x))
	return out


func test_check_tables() -> void:
	var ch: Dictionary = _g["checks"]
	for row in ch["band"]:
		_eq("band %d" % row[0], SolaceTideRules.band(row[0], _cfg), row[1])
	for row in ch["hand_size"]:
		_eq("hand %d" % row[0], SolaceTideRules.hand_size(row[0], _cfg), row[1])
	for row in ch["known_fired"]:
		_eq("known %d" % row[0], SolaceTideRules.known_count(row[0], _cfg), row[1])
	for row in ch["home_damage"]:
		_eq("damage %s" % str(row), SolaceTideRules.home_damage(row[0], row[1], _cfg), row[2])
	var st := SolaceTideState.new()
	st.home_max = _home_max
	for row in ch["cool_price"]:
		st.cools = row[0]
		_eq("cool %d" % row[0], SolaceTideRules.cool_price(st, _cfg), row[1])
	for row in ch["patch"]:
		st.home = row[0]
		st.schematics = row[1]
		_eq("patch %s" % str(row), SolaceTideRules.patch_cost(st, _cfg), [row[2], row[3]])
	# R-D: the Bloom start gap with n INFECTED cards, from the golden's entry pace (BloomRules is Phase 2b)
	for row in ch["bloom_start_gap"]:
		var start: int = _cfg.bloom_start_gap_milli_by_tier[row[0] - 1]
		_eq("bloom gap %s" % str(row), SolaceTideRules.bloom_start_gap(start, row[4], row[3], _cfg), row[5])
	_done()


# ------------------------------------------------------------------------------------------------ campaigns
func test_campaign_phases() -> void:
	var rules: Dictionary = _g["config"]["rules"]
	var n_raid := 0
	var n_net := 0
	var n_breach := 0
	for camp in _g["campaigns"]:
		_naive = camp["player"] == "naive"
		for step in camp["steps"]:
			var label := "%s/%s/%d %s" % [camp["policy"], camp["player"], camp["seed"], step["phase"]]
			match String(step["phase"]):
				"NETRUN":
					_check_netrun(label + " n%d" % step["netrun"], step, rules)
					n_net += 1
				"BREACH":
					_check_breach(label + " n%d" % step["netrun"], step)
					n_breach += 1
				"RAID":
					_check_raid_step(label + " r%d" % step["raid"], step)
					n_raid += 1
	gut.p("campaign phases: %d netruns, %d breaches, %d raids" % [n_net, n_breach, n_raid])
	assert_gt(n_raid, 20)
	_done()


func _check_netrun(label: String, step: Dictionary, rules: Dictionary) -> void:
	var st := _state(step["before"])
	var site: StringName = &"" if step["site"] == null else StringName(String(step["site"]))
	var tier := 1 if site == &"" else int(_board.tier[site])
	var crossed: bool
	if step["died"]:
		crossed = SolaceTideRules.netrun_death(st, _cfg, tier)
	else:
		# the oracle's abstractions: ELITE_RUN elites per netrun, CYCLE_SCHEM Schematics from unspent Cycles
		crossed = SolaceTideRules.netrun_complete(st, _board, _cfg, site, int(rules["ELITE_RUN"]) * _cfg.elite_heat,
			int(rules["CYCLE_SCHEM"]))
		var want_asset: int = int(step["after"]["asset_n"])
		if want_asset > st.asset_n:
			for c in step["after"]["deck"]:
				if String(c[0]) == "a%02d" % st.asset_n:
					SolaceTideRules.add_asset(st, String(c[1]))
	SolaceTideRules.end_netrun(st, _cfg, int(step["netrun"]))
	_state_eq(label, st, step["after"])
	_eq(label + " raid queued", crossed, step["raid_queued"])


func _check_breach(label: String, step: Dictionary) -> void:
	var st := _state(step["before"])
	if step["success"]:
		st.won = true
	else:
		SolaceTideRules.breach_failed(st, _cfg, int(step["netrun"]))
	_state_eq(label, st, step["after"])


func _check_raid_step(label: String, step: Dictionary) -> void:
	var st := _state(step["before"])
	var idx: int = int(step["raid"])
	if idx > 0:
		SolaceTideRules.decay(st, _cfg)
		_state_eq(label + " decay", st, step["after_decay"])
		if st.lost != "":
			return
	st.raid_n = idx
	_state_eq(label + " at draw", st, step["after_discard"])
	_check_raid(label, st, idx, step, true)
	if not _errs.is_empty():
		return
	if step.has("between"):
		var ns := _after_raid(st, step)
		_check_between(label, ns, step)


func _after_raid(st: SolaceTideState, step: Dictionary) -> SolaceTideState:
	var draw := SolaceTideRules.draw_from_json(step["draw"])
	var hand: Array = step["hand"]
	var ctx := SolaceTideRules.make_ctx(_board, st, _cfg, draw, hand, int(step["raid"]))
	var res := SolaceTideRules.play(ctx, st, SolaceTideRules.place_from_json(step["place"]),
		SolaceTideRules.response_from_json(step["response"]), int(draw["real_a"]), int(draw["hunter_real"]))
	var ns: SolaceTideState = res["state"]
	SolaceTideRules.finish_raid(ns, SolaceTideRules.response_from_json(step["response"]), int(step["raid"]))
	return ns


func _check_between(label: String, ns: SolaceTideState, step: Dictionary) -> void:
	if ns.lost != "":
		return
	var opts := SolaceTideRules.between_options(ns, _cfg)
	_eq(label + " between options", opts, step["between_options"].map(func(o: Array) -> Array: return [o[0] if o[0] != null else "", o[1] if o[1] != null else "", o[2]]))
	var b: Dictionary = step["between"]
	var opt: Array = [&"" if b["repair"] == null else StringName(String(b["repair"])), "" if b["build"] == null else String(b["build"]), b["patch"]]
	var out := SolaceTideRules.between(ns, opt, _cfg)
	_state_eq(label + " between", out, step["after"])


## Checks one raid record (a campaign step or a random raid) against the port. `st` is the state at the draw.
func _check_raid(label: String, st: SolaceTideState, idx: int, rec: Dictionary, in_campaign: bool) -> void:
	var draw := SolaceTideRules.draw_from_json(rec["draw"])
	var hand: Array = rec["hand"]
	var ctx := SolaceTideRules.make_ctx(_board, st, _cfg, draw, hand, idx)
	var place := SolaceTideRules.place_from_json(rec["place"])
	var places := SolaceTideRules.placements(ctx, st)
	if rec.has("n_placements"):
		_eq(label + " n placements", places.size(), rec["n_placements"])
	if not _naive and not _find_place(places, place):
		_bad(label + " place not in placements")
	if rec.has("divert_neighbors"):
		_eq(label + " divert neighbors", ctx.nbrs, rec["divert_neighbors"])
	var resp := SolaceTideRules.response_from_json(rec["response"])
	var sw := SolaceTideRules.launch(ctx, st, place)
	var opts := SolaceTideRules.response_options(ctx, sw)
	if rec.has("response_options"):
		_eq(label + " response options", opts, rec["response_options"])
	else:
		var found := false
		for o in opts:
			if _plain(o) == _plain(resp):
				found = true
		if not found:
			_bad(label + " response %s not in options" % str(rec["response"]))
	var a: int = int(rec["a"]) if rec.has("a") else int(draw["real_a"])
	var h: int = int(rec["hunter"]) if rec.has("hunter") else int(draw["hunter_real"])
	var res := SolaceTideRules.play(ctx, st, place, resp, a, h)
	_eq(label + " lean", res["lean"], rec["lean"])
	_eq(label + " b pick", res["b_pick"], rec["b_pick"])
	_eq(label + " home dmg", res["home_dmg"], rec["home_dmg"])
	_eq(label + " trace", res["trace"], rec["trace"])
	_eq(label + " tier", res["tier"], rec["tier"])
	var want_after: Dictionary = rec["after_raid"] if rec.has("after_raid") else rec["after"]
	_state_eq(label + " after raid", res["state"], want_after)
	if rec.has("forecast_hold"):
		var rows := SolaceTideRules.forecast(ctx, st, place, ["HOLD"])
		var tiers: Array = []
		for r in rows:
			tiers.append(r["tier"])
		_eq(label + " forecast hold", tiers, rec["forecast_hold"])
	if rec.has("divert"):
		var d: Array = res["sweep"].divert
		_eq(label + " divert", d, rec["divert"] if rec["divert"] != null else [])


# ------------------------------------------------------------------------------------------------ random raids
func test_random_raids() -> void:
	_naive = false
	var n := 0
	for rec in _g["random_raids"]:
		var st := _state(rec["before"])
		_check_raid("random raid %d" % n, st, int(rec["raid"]), rec, false)
		n += 1
	assert_eq(n, 120)
	_done()


## R-J: every known beam the oracle drew (campaign raids and random raids) is a path of its pool that `most_owned` keeps:
## the port's candidate rule and the oracle's agree on the golden's states.
func test_golden_known_beams_are_most_owned_paths() -> void:
	var recs: Array = []
	for camp in _g["campaigns"]:
		for step in camp["steps"]:
			if step["phase"] == "RAID" and step.has("draw"):
				recs.append([step["after_discard"], step["draw"]])
	for rec in _g["random_raids"]:
		recs.append([rec["before"], rec["draw"]])
	var n := 0
	for r in recs:
		var st := _state(r[0])
		var cand_cells: Array = []
		for ln in r[1]["cands"]:
			cand_cells.append((ln["cells"] as Array).map(func(x: String) -> StringName: return StringName(x)))
		var spool := _board.street_pool(cand_cells, st.owned)
		for ln in r[1]["known"]:
			var pool: Array = _board.route_pool if ln["kind"] == "ROUTE" else spool
			var ok := false
			for p in SolaceTideRules.most_owned(pool, st):
				if _plain(p) == ln["cells"]:
					ok = true
			if not ok:
				_bad("known beam %s is not a most-owned path of its pool" % str(ln["cells"]))
			n += 1
	assert_gt(n, 300)
	_done()


func test_random_betweens() -> void:
	var n := 0
	for rec in _g["random_betweens"]:
		var st := _state(rec["before"])
		var opts := SolaceTideRules.between_options(st, _cfg)
		_eq("between %d options" % n, opts, rec["options"].map(func(o: Array) -> Array: return [o[0] if o[0] != null else "", o[1] if o[1] != null else "", o[2]]))
		var c: Dictionary = rec["choice"]
		var opt: Array = [&"" if c["repair"] == null else StringName(String(c["repair"])), "" if c["build"] == null else String(c["build"]), c["patch"]]
		_state_eq("between %d" % n, SolaceTideRules.between(st, opt, _cfg), rec["after"])
		n += 1
	assert_eq(n, 80)
	_done()
