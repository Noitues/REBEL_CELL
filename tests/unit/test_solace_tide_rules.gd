extends GutTest
## Solace tide, Phase 2a (SOLACE_RAID_SPEC.md section 10, items 2, 3 and 5): preview equals result, seeded replay, and
## the rule tests. Scenarios are built by hand on the Solace graph of the golden.

const GOLDEN := "res://tools/raid_concepts/data/solace_raid_golden.json"

var _cfg: CampaignConfigData
var _board: SolaceTideBoard
var _golden: Dictionary


func before_all() -> void:
	_cfg = load("res://content/config/campaign_config.tres")
	_golden = JSON.parse_string(FileAccess.open(GOLDEN, FileAccess.READ).get_as_text())
	_board = SolaceTideBoard.from_dict(_golden["graph"], _cfg.solace_tide_route_max_links)


# ------------------------------------------------------------------------------------------------ helpers
func _st(owned: Dictionary = {}) -> SolaceTideState:
	var s := SolaceTideState.start(_cfg, 50)
	for k in owned.keys():
		s.owned[StringName(k)] = owned[k]
	return s


func _line(cells: Array, kind: String = "ROUTE", t: String = "D") -> Dictionary:
	var c: Array = []
	for x in cells:
		c.append(StringName(x))
	return {"kind": kind, "cells": c, "type": t, "home": kind == "ROUTE"}


## A draw with the given known routes; the candidates are pool paths 0..2, hunters two streets away from everything.
func _draw(known: Array, cands: Array = []) -> Dictionary:
	var cs: Array = cands
	if cs.is_empty():
		cs = [_line(["t3_f", "t2_f", "t1_f"], "ROUTE", "N"), _line(["t3_g", "t2_g", "t1_g"], "ROUTE", "E"),
			_line(["t3_d", "t2_d", "t1_d"], "ROUTE", "D")]
	return {"known": known, "cands": cs, "real_a": 0, "real_b_drawn": 1, "hunter_type": "D",
		"hunters": [_line(["t3_h"], "STREET"), _line(["t1_h"], "STREET")], "hunter_real": 0, "n_paths": 29}


func _ctx(st: SolaceTideState, draw: Dictionary, hand: Array = ["s0", "s1", "s2", "s5"], idx: int = 1) -> SolaceTideRules.Ctx:
	return SolaceTideRules.make_ctx(_board, st, _cfg, draw, hand, idx)


func _place(sent: Dictionary = {}, ghost: StringName = &"") -> Dictionary:
	var m := {}
	for k in sent.keys():
		m[StringName(k)] = sent[k]
	return {"sentries": m, "ghost": ghost}


func _wounds(st: SolaceTideState, tied: String = "") -> int:
	var n := 0
	for c in st.deck:
		if c[2] == "WOUND" and (tied == "" or c[1] == tied):
			n += 1
	return n


# ------------------------------------------------------------------------------------------------ item 2: preview == result
func test_forecast_equals_play_on_the_golden_raids() -> void:
	var bad := 0
	var rows_checked := 0
	var divert_seen := 0
	for rec in _golden["random_raids"]:
		var st := SolaceTideState.from_dict(rec["before"])
		var draw := SolaceTideRules.draw_from_json(rec["draw"])
		var ctx := SolaceTideRules.make_ctx(_board, st, _cfg, draw, rec["hand"], int(rec["raid"]))
		var place := SolaceTideRules.place_from_json(rec["place"])
		var opts := SolaceTideRules.response_options(ctx, SolaceTideRules.launch(ctx, st, place))
		var pick: Array = []
		for i in opts.size():
			if opts[i][0] == "DIVERT" or i % 7 == 0 or i == opts.size() - 1:
				pick.append(opts[i])
		for resp in pick:
			if resp[0] == "DIVERT":
				divert_seen += 1
			var rows := SolaceTideRules.forecast(ctx, st, place, resp)
			for row in rows:
				var res := SolaceTideRules.play(ctx, st, place, resp, row["a"], row["hunter"])
				var f: Dictionary = row["result"]
				rows_checked += 1
				if res["tier"] != row["tier"] or res["trace"] != f["trace"] or res["b_pick"] != f["b_pick"] \
						or res["lean"] != f["lean"] or res["state"].to_dict() != f["state"].to_dict():
					bad += 1
	gut.p("forecast rows compared: %d (DIVERT responses %d)" % [rows_checked, divert_seen])
	assert_eq(bad, 0, "forecast rows that differ from play")
	assert_gt(rows_checked, 1000)
	assert_gt(divert_seen, 0)


func test_the_shown_lean_is_the_hold_pick() -> void:
	var n := 0
	for rec in _golden["random_raids"]:
		var st := SolaceTideState.from_dict(rec["before"])
		var draw := SolaceTideRules.draw_from_json(rec["draw"])
		var ctx := SolaceTideRules.make_ctx(_board, st, _cfg, draw, rec["hand"], int(rec["raid"]))
		var place := SolaceTideRules.place_from_json(rec["place"])
		for a in 3:
			var res := SolaceTideRules.play(ctx, st, place, ["HOLD"], a, 0)
			assert_eq(res["lean"], res["b_pick"], "HOLD keeps the lean")
			n += 1
	assert_eq(n, 360)


# ------------------------------------------------------------------------------------------------ item 3: seeded replay
func _owned_start() -> SolaceTideState:
	return _st({"t1_a": SolaceTideState.Cond.OK, "t1_b": SolaceTideState.Cond.OK, "t2_intel": SolaceTideState.Cond.OK,
		"t1_c": SolaceTideState.Cond.OK})


func test_the_same_seed_draws_the_same_raid() -> void:
	var st := _owned_start()
	var r1 := RandomNumberGenerator.new()
	r1.seed = 4242
	var r2 := RandomNumberGenerator.new()
	r2.seed = 4242
	var d1 := SolaceTideRules.draw_lines(_board, st, _cfg, r1)
	var h1 := SolaceTideRules.draw_hand(st, _cfg, r1)
	var d2 := SolaceTideRules.draw_lines(_board, st, _cfg, r2)
	var h2 := SolaceTideRules.draw_hand(st, _cfg, r2)
	assert_eq(d1, d2)
	assert_eq(h1, h2)
	assert_eq(h1.size(), 4)
	var differs := false
	for seed_i in range(1, 12):
		var r3 := RandomNumberGenerator.new()
		r3.seed = seed_i
		if SolaceTideRules.draw_lines(_board, st, _cfg, r3) != d1:
			differs = true
	assert_true(differs, "other seeds draw other raids")


func test_the_drawn_lines_are_legal() -> void:
	var st := _owned_start()
	for seed_i in 40:
		var rng := RandomNumberGenerator.new()
		rng.seed = seed_i
		st.raid_n = seed_i % 8
		var d := SolaceTideRules.draw_lines(_board, st, _cfg, rng)
		var cands: Array = d["cands"]
		assert_eq(cands.size(), 3)
		var types := {}
		var live_counts: Array[int] = []
		var chosen := {}
		for ln in cands:
			types[ln["type"]] = true
			chosen[str(ln["cells"])] = true
			var n := 0
			for s in ln["cells"]:
				if st.is_live(s):
					n += 1
			live_counts.append(n)
		assert_eq(types.size(), 3, "distinct types")
		assert_eq(chosen.size(), 3, "distinct paths")
		var worst: int = live_counts.min()
		for p in _board.route_pool:
			if not chosen.has(str(p)):
				var n := 0
				for s in p:
					if st.is_live(s):
						n += 1
				assert_true(n <= worst, "candidates are the routes through the most live Sites")
		assert_true(d["real_a"] >= 0 and d["real_a"] < 3 and d["real_b_drawn"] != d["real_a"])
		assert_eq((d["known"] as Array).size(), 3)
		assert_eq((d["hunters"] as Array).size(), 2)
		if st.raid_n < _cfg.solace_tide_early_raids:
			for ln in d["known"]:
				assert_eq(ln["kind"], "ROUTE", "early raids draw known routes")
		else:
			for ln in d["known"]:
				assert_eq(ln["kind"], "STREET", "later raids draw known streets")
		for ln in d["hunters"]:
			assert_eq(ln["home"], false)


func _run_campaign(roundtrip: bool) -> String:
	var st := _owned_start()
	st.schematics = 60
	var rng := RandomNumberGenerator.new()
	rng.seed = 777
	for idx in 5:
		var ctx := SolaceTideRules.begin_raid(_board, st, _cfg, rng, idx)
		if ctx == null:
			break
		var places := SolaceTideRules.placements(ctx, st)
		var place: Dictionary = places[(idx * 5) % places.size()]
		var sw := SolaceTideRules.launch(ctx, st, place)
		var opts := SolaceTideRules.response_options(ctx, sw)
		var resp: Array = opts[idx % opts.size()]
		var res := SolaceTideRules.play(ctx, st, place, resp, ctx.draw["real_a"], ctx.draw["hunter_real"])
		st = res["state"]
		SolaceTideRules.finish_raid(st, resp, idx)
		if st.lost != "":
			break
		var bo := SolaceTideRules.between_options(st, _cfg)
		st = SolaceTideRules.between(st, bo[bo.size() - 1], _cfg)
		if roundtrip:
			st = SolaceTideState.from_dict(JSON.parse_string(JSON.stringify(st.to_dict())))
	return JSON.stringify(st.to_dict())


func test_a_seeded_campaign_replays_and_survives_a_save() -> void:
	var a := _run_campaign(false)
	assert_eq(_run_campaign(false), a, "same seed, same inputs, same state")
	assert_eq(_run_campaign(true), a, "a save and load between raids changes nothing")


# ------------------------------------------------------------------------------------------------ item 5: rules
func test_a_home_hit_adds_one_infected_card_tied_to_home() -> void:
	var st := _st({"t1_b": SolaceTideState.Cond.OK})
	var ctx := _ctx(st, _draw([_line(["t3_b", "t2_breach", "t1_b"]), _line(["t3_c", "t2_virus", "t1_c"]),
		_line(["t3_c", "t2_virus", "t1_c"], "ROUTE", "N")]))
	var res := SolaceTideRules.play(ctx, st, _place(), ["HOLD"], 0, 0)
	var ns: SolaceTideState = res["state"]
	assert_eq(ns.home, 50 - 5, "HOME is hit once per raid even when several routes arrive")
	assert_eq(_wounds(ns, "HOME"), 1, "one INFECTED card tied to HOME")
	assert_eq(ns.lost_since_raid, 0, "a HOME card is not a lost Site: no spread count")
	assert_eq(ns.last_lost, &"", "and not last_lost")
	assert_eq(ns.infected_total, 1)


func test_a_shield_or_a_ghost_stops_the_home_infection() -> void:
	var st := _st({"t1_b": SolaceTideState.Cond.OK, "t1_c": SolaceTideState.Cond.OK})
	var ctx := _ctx(st, _draw([_line(["t3_b", "t2_breach", "t1_b"]), _line(["t3_c", "t2_virus", "t1_c"]),
		_line(["t3_c", "t2_virus", "t1_c"], "ROUTE", "N")]))
	var shielded := SolaceTideRules.play(ctx, st, _place(), ["SACRIFICE", &"t1_b"], 0, 0)
	assert_eq((shielded["state"] as SolaceTideState).home, 50)
	assert_eq(_wounds(shielded["state"], "HOME"), 0, "SACRIFICE shields HOME")
	assert_eq(_wounds(shielded["state"], "t1_b"), 1, "the sacrificed Site is TAKEN and infected")
	var ghosted := SolaceTideRules.play(ctx, st, _place({}, &"HOME"), ["HOLD"], 0, 0)
	assert_eq((ghosted["state"] as SolaceTideState).home, 50)
	assert_eq(_wounds(ghosted["state"], "HOME"), 0, "the ghost on HOME takes no hit")


func test_purge_damage_only_for_the_queued_purge_raid() -> void:
	var st := _st({"t1_b": SolaceTideState.Cond.OK})
	st.heat = 100
	var draw := _draw([_line(["t3_b", "t2_breach", "t1_b"]), _line(["t3_c"], "STREET"), _line(["t3_c"], "STREET")])
	var normal := SolaceTideRules.play(_ctx(st, draw), st, _place(), ["HOLD"], 0, 0)
	assert_eq((normal["state"] as SolaceTideState).home, 50 - _cfg.solace_tide_home_hit_damage_by_band[3])
	st.purge_queued = true
	var purge := SolaceTideRules.play(_ctx(st, draw), st, _place(), ["HOLD"], 0, 0)
	assert_eq((purge["state"] as SolaceTideState).home, 50 - _cfg.solace_tide_home_hit_damage_by_band[4])
	SolaceTideRules.finish_raid(purge["state"], ["HOLD"], 1)
	assert_false((purge["state"] as SolaceTideState).purge_queued)


func test_add_heat_queues_purge_on_first_crossing_only() -> void:
	var st := _st()
	st.heat = 95
	assert_true(SolaceTideRules.add_heat(st, 5, _cfg))
	assert_true(st.purge_queued)
	st.purge_queued = false
	assert_false(SolaceTideRules.add_heat(st, 3, _cfg), "100 is already crossed")
	assert_false(st.purge_queued)
	assert_eq(st.heat, 100, "clamped to heat_max")


func test_divert_targets_and_the_bent_beam() -> void:
	var known := _line(["t3_b", "t2_breach", "t1_b"])
	var st := _st({"t1_a": SolaceTideState.Cond.OK, "t1_b": SolaceTideState.Cond.OK})
	var draw := _draw([known, _line(["t3_c", "t2_virus", "t1_c"]), _line(["t3_c", "t2_virus", "t1_c"])])
	var nbrs := SolaceTideRules.divert_neighbors(_board, draw, st)
	for p in nbrs[0]:
		assert_ne(p, known["cells"])
		assert_true(p[0] == &"t3_b" or p[p.size() - 1] == &"t1_b", "starts or ends at the same Site")
	assert_gt((nbrs[0] as Array).size(), 0)
	# pool order
	var idx := -1
	for p in nbrs[0]:
		var at := _board.route_pool.find(p)
		assert_gt(at, idx, "pool order")
		idx = at
	# a SHIFT card bends the beam: it scans its new cells
	var target: Array = nbrs[0][0]
	var ctx := _ctx(st, draw, ["s0", "s5", "s1", "s2"])
	var sw := SolaceTideRules.launch(ctx, st, _place())
	var found := false
	for o in SolaceTideRules.response_options(ctx, sw):
		if o[0] == "DIVERT" and o[1] == 0 and o[2] == target:
			found = true
	assert_true(found, "DIVERT is offered with a SHIFT card in hand")
	var plain := SolaceTideRules.play(ctx, st, _place(), ["HOLD"], 0, 0)
	var bent := SolaceTideRules.play(ctx, st, _place(), ["DIVERT", 0, target], 0, 0)
	var hit_plain: Array = []
	for t in plain["trace"]:
		if t[0] == "known0":
			hit_plain.append(t[1])
	assert_true(hit_plain.has("t1_b"), "the plain beam hits t1_b")
	var hit_bent: Array = []
	for t in bent["trace"]:
		if t[0] == "known0":
			hit_bent.append(t[1])
	if not target.has(&"t1_b"):
		assert_false(hit_bent.has("t1_b"), "the bent beam left the old cells")
	assert_eq(plain["b_pick"], plain["lean"])
	assert_eq((bent["state"] as SolaceTideState).heat, _cfg.solace_tide_card_response_heat + st.heat, "a card response costs Heat")
	# the B pick does not depend on the known beams
	var quiet := _draw([_line(["t3_h"], "STREET"), _line(["t3_h"], "STREET"), _line(["t3_h"], "STREET")])
	var q := SolaceTideRules.play(_ctx(st, quiet, ["s0", "s5", "s1", "s2"]), st, _place(), ["HOLD"], 0, 0)
	assert_eq(q["b_pick"], plain["b_pick"], "the known beams do not change B")


func test_the_breach_has_one_retry_then_the_exploits_are_spent_and_retaken() -> void:
	var st := _st({"t2_intel": SolaceTideState.Cond.OK, "t2_breach": SolaceTideState.Cond.OK, "t2_virus": SolaceTideState.Cond.OK})
	st.held = [&"t2_breach", &"t2_intel", &"t2_virus"]
	SolaceTideRules.breach_failed(st, _cfg, 5)
	assert_eq(st.breach_fails, 1)
	assert_eq(st.held.size(), 3, "the first failure keeps the Exploits")
	assert_eq(st.deaths, 1)
	assert_eq(st.heat, _cfg.death_heat_base + 4, "death Heat at tier 4")
	SolaceTideRules.breach_failed(st, _cfg, 6)
	assert_eq(st.held.size(), 0, "the second failure spends them")
	assert_eq(st.breach_fails, 0)
	var sites := SolaceTideRules.retake_sites(st, _board)
	assert_eq(sites.size(), 3, "the Exploit Sites are launchable again")
	var h0 := st.heat
	SolaceTideRules.netrun_complete(st, _board, _cfg, &"t2_intel", 0, 0)
	assert_eq(st.held, [&"t2_intel"] as Array[StringName], "a re-take restores one")
	assert_eq(st.heat - h0, _cfg.rack_heat_by_tier[1] + _cfg.exploit_heat, "the Exploit Heat is paid again")
	assert_eq(SolaceTideRules.retake_sites(st, _board).size(), 2)


func test_decay_takes_down_sites_and_infects() -> void:
	var st := _st({"t1_a": SolaceTideState.Cond.DOWN, "t1_c": SolaceTideState.Cond.OK})
	SolaceTideRules.decay(st, _cfg)
	assert_eq(st.owned[&"t1_a"], SolaceTideState.Cond.TAKEN)
	assert_eq(st.owned[&"t1_c"], SolaceTideState.Cond.OK)
	assert_eq(_wounds(st, "t1_a"), 1)
	assert_eq(st.lost_since_raid, 0, "reset after the spread check")
	assert_eq(st.sites_lost, 1)


func test_spread_and_dose_order() -> void:
	# two Sites lost: the spread adds a third card tied to the lowest-id lost Site
	var st := _st({"t1_a": SolaceTideState.Cond.DOWN, "t1_b": SolaceTideState.Cond.DOWN})
	SolaceTideRules.decay(st, _cfg)
	assert_eq(_wounds(st), 3)
	assert_eq(_wounds(st, "t1_a"), 2, "the spread card is tied to last_lost, the lowest id")
	# a DOSE cancels the spread
	st = _st({"t1_a": SolaceTideState.Cond.DOWN, "t1_b": SolaceTideState.Cond.DOWN})
	SolaceTideRules.add_dose(st)
	SolaceTideRules.decay(st, _cfg)
	assert_eq(_wounds(st), 2)
	assert_eq(st.dose_spent, 1)
	assert_eq(st.dose_cards().size(), 0)
	# a second DOSE then cures the highest-id INFECTED card
	st = _st({"t1_a": SolaceTideState.Cond.DOWN, "t1_b": SolaceTideState.Cond.DOWN})
	SolaceTideRules.add_dose(st)
	SolaceTideRules.add_dose(st)
	SolaceTideRules.decay(st, _cfg)
	assert_eq(_wounds(st), 1)
	assert_eq(st.dose_spent, 2)
	var left := ""
	for c in st.deck:
		if c[2] == "WOUND":
			left = c[0]
	assert_eq(left, "w000", "the highest id was cured")
	# one Site lost: no spread; a DOSE cures one card
	st = _st({"t1_a": SolaceTideState.Cond.DOWN})
	SolaceTideRules.add_dose(st)
	SolaceTideRules.decay(st, _cfg)
	assert_eq(_wounds(st), 0)


func test_city_lost_when_infected_outnumber_healthy_and_a_dose_counts_healthy() -> void:
	var st := _st()
	st.deck = [["s0", "D", "GUARD"], ["s1", "D", "GUARD"], ["x0", "-", "DOSE"]]
	for i in 3:
		st.deck.append(["w%03d" % i, "t1_a", "WOUND"])
	SolaceTideRules.check_loss(st)
	assert_eq(st.lost, "", "3 INFECTED against 3 healthy (the DOSE counts) is not lost")
	st.deck.append(["w003", "t1_a", "WOUND"])
	SolaceTideRules.check_loss(st)
	assert_eq(st.lost, "CITY_LOST")
	assert_eq(RaidOutcome.verdict_of_tide(st.lost), RaidOutcome.Verdict.CITY_LOST)
	st.lost = ""
	st.home = 0
	SolaceTideRules.check_loss(st)
	assert_eq(RaidOutcome.verdict_of_tide(st.lost), RaidOutcome.Verdict.BREACHED)


func test_the_sacrifice_gap() -> void:
	var st := _st({"t1_b": SolaceTideState.Cond.OK})
	st.last_sac = 3
	var draw := _draw([_line(["t3_b", "t2_breach", "t1_b"]), _line(["t3_c"], "STREET"), _line(["t3_c"], "STREET")])
	for case in [[4, false], [5, true]]:
		var ctx := _ctx(st, draw, ["s0", "s1", "s2", "s5"], case[0])
		var any := false
		for o in SolaceTideRules.response_options(ctx, SolaceTideRules.launch(ctx, st, _place())):
			if o[0] == "SACRIFICE":
				any = true
		assert_eq(any, case[1], "raid %d" % case[0])
	var ctx2 := _ctx(st, draw)
	var res := SolaceTideRules.play(ctx2, st, _place(), ["SACRIFICE", &"t1_b"], 0, 0)
	SolaceTideRules.finish_raid(res["state"], ["SACRIFICE", &"t1_b"], 5)
	assert_eq((res["state"] as SolaceTideState).last_sac, 5)


func test_clean_defense_pays_heat_and_schematics() -> void:
	# nothing owned on any line and the ghost on HOME: no damage at all
	var st := _st({"t1_j": SolaceTideState.Cond.OK})
	var res := SolaceTideRules.play(_ctx(st, _draw([_line(["t3_c"], "STREET"), _line(["t3_c"], "STREET"), _line(["t3_c"], "STREET")])),
		st, _place({}, &"HOME"), ["HOLD"], 0, 0)
	var ns: SolaceTideState = res["state"]
	assert_eq(ns.heat, _cfg.solace_tide_ghost_heat + _cfg.clean_defense_heat)
	assert_eq(ns.schematics, st.schematics + _cfg.raid_schematics_by_tier[0])
	assert_eq(ns.ghost, st.ghost - 1)
	# any damage pays nothing
	var st2 := _st({"t1_b": SolaceTideState.Cond.OK})
	var hit := SolaceTideRules.play(_ctx(st2, _draw([_line(["t3_b", "t2_breach", "t1_b"]), _line(["t3_c"], "STREET"), _line(["t3_c"], "STREET")])),
		st2, _place(), ["HOLD"], 0, 0)
	assert_eq((hit["state"] as SolaceTideState).schematics, st2.schematics)
	assert_eq((hit["state"] as SolaceTideState).heat, 0)


func test_cadence_a_heat_raid_resets_the_count() -> void:
	var st := _st()
	assert_false(SolaceTideRules.note_netrun(st, _cfg, false))
	assert_false(SolaceTideRules.note_netrun(st, _cfg, false))
	assert_true(SolaceTideRules.note_netrun(st, _cfg, false), "the third netrun fires a raid")
	var rng := RandomNumberGenerator.new()
	rng.seed = 1
	st.owned[&"t1_a"] = SolaceTideState.Cond.OK
	SolaceTideRules.begin_raid(_board, st, _cfg, rng, 0)
	assert_eq(st.netruns_since_raid, 0)
	assert_true(SolaceTideRules.note_netrun(st, _cfg, true), "a Heat crossing fires a raid at once")
	SolaceTideRules.begin_raid(_board, st, _cfg, rng, 1)
	assert_eq(st.netruns_since_raid, 0, "a Heat raid resets the cadence too")


func test_a_netrun_death_and_the_dose_cadence() -> void:
	var st := _st()
	SolaceTideRules.netrun_death(st, _cfg, 2)
	assert_eq(st.heat, _cfg.death_heat_base + 2)
	assert_eq(st.deaths, 1)
	for n in range(1, 9):
		SolaceTideRules.end_netrun(st, _cfg, n)
	assert_eq(st.dose_cards().size(), 2, "a DOSE card every 4th netrun")
