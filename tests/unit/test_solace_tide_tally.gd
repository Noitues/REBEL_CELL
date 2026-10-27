extends GutTest
## Phase 3b (tier fast): the INFECTED tally the raid screen shows (SolaceTideTally). DECAY's tally adds up to the real DECAY on every mix of DOWN
## Sites, spread and DOSE cards; the raid's tally splits the added cards into Sites lost and HOME hits; the loss margin counts the INFECTED cards
## that still fit before the city is lost.

var _cfg: CampaignConfigData


const GOLDEN := "res://tools/raid_concepts/data/solace_raid_golden.json"
var _board: SolaceTideBoard


func before_all() -> void:
	_cfg = load("res://content/config/campaign_config.tres")
	var golden: Dictionary = JSON.parse_string(FileAccess.open(GOLDEN, FileAccess.READ).get_as_text())
	_board = SolaceTideBoard.from_dict(golden["graph"], _cfg.solace_tide_route_max_links)


func _line(cells: Array, kind: String, t: String) -> Dictionary:
	var c: Array = []
	for x in cells:
		c.append(StringName(x))
	return {"kind": kind, "cells": c, "type": t, "home": kind == "ROUTE"}


## A raid on a hand-built board: route A is an N route over t3_f, t2_f, t1_f; B an E route; C a D route; no known beam.
func _ctx(st: SolaceTideState) -> SolaceTideRules.Ctx:
	var wounds: Array = []
	for c in st.deck:
		if c[2] == SolaceTideState.VERB_WOUND:
			wounds.append(c)
	st.deck = [["s0", "D", "GUARD"], ["s1", "N", "GUARD"], ["s2", "E", "SHIFT"], ["s3", "D", "GUARD"], ["x0", "-", "DOSE"]]
	st.deck.append_array(wounds)
	st.sort_deck()
	for s in ["t3_f", "t2_f", "t1_f", "t3_g", "t2_g", "t1_g", "t3_d", "t2_d", "t1_d", "t3_h", "t1_h"]:
		st.owned[StringName(s)] = SolaceTideState.Cond.OK
	# Four known beams (more than any Heat fires) over their own Sites, so the number that fire never runs the list dry.
	var known: Array = []
	for s in ["t3_k1", "t3_k2", "t3_k3", "t3_k4"]:
		known.append(_line([s], "STREET", "E"))
	var draw := {"known": known, "cands": [_line(["t3_f", "t2_f", "t1_f"], "ROUTE", "N"), _line(["t3_g", "t2_g", "t1_g"], "ROUTE", "E"),
		_line(["t3_d", "t2_d", "t1_d"], "ROUTE", "D")], "real_a": 0, "real_b_drawn": 1, "hunter_type": "D",
		"hunters": [_line(["t3_h"], "STREET", "D"), _line(["t1_h"], "STREET", "D")], "hunter_real": 0, "n_paths": 29}
	return SolaceTideRules.make_ctx(_board, st, _cfg, draw, ["s0", "s1", "s2", "s3"], 1)


func test_the_odds_count_every_row_worst_tier_first() -> void:
	var rows: Array = []
	for t in ["HOLDS", "HOLDS", "SITES LOST", "BREACHED", "HOLDS", "EVADED"]:
		rows.append({"tier": t})
	var odds := SolaceTideTally.tier_odds(rows)
	assert_eq(odds.map(func(o: Dictionary) -> String: return String(o["tier"])), ["BREACHED", "SITES LOST", "HOLDS"], "EVADED folds into HOLDS")
	assert_eq(int(odds[2]["n"]), 4)
	var sum := 0
	for o in odds:
		sum += int(o["n"])
	assert_eq(sum, rows.size())


func test_the_outcome_marks_are_what_the_forecast_rows_do_to_the_board() -> void:
	var st := SolaceTideState.start(_cfg, 50)
	var ctx := _ctx(st)
	var rows := SolaceTideRules.forecast(ctx, st, {"sentries": {}, "ghost": &""}, ["HOLD"])
	assert_eq(rows.size(), 12)
	var all := SolaceTideTally.outcome_marks(rows, st)
	# H7c: with no sentry anywhere every Site a beam leaves DOWN falls at the close: the marks say "falls", not DOWN
	assert_true((all["down"] as Array).is_empty(), "no unguarded Site stays DOWN")
	assert_false((all["falls"] as Array).is_empty(), "an unguarded raid's hit Sites fall")
	for r in rows:
		for s in (r["result"]["sweep"] as SolaceTideRules.Sweep).fell:
			assert_true((all["falls"] as Array).has(s) or (all["taken"] as Array).has(s), "every fallen Site is marked")
	var worst_home := 0
	for r in rows:
		worst_home = maxi(worst_home, st.home - (r["result"]["state"] as SolaceTideState).home)
	assert_eq(int(all["home"]), worst_home)
	var one := SolaceTideTally.outcome_marks([rows[0]], st)
	for s in one["down"]:
		assert_true((all["down"] as Array).has(s), "a row's marks are within the union")
		assert_eq(int((rows[0]["result"]["state"] as SolaceTideState).owned[s]), SolaceTideState.Cond.DOWN)


func test_a_sentry_of_the_wrong_type_is_useless_and_one_of_the_right_type_is_not() -> void:
	var st := SolaceTideState.start(_cfg, 50)
	var ctx := _ctx(st)
	var place := {"sentries": {}, "ghost": &""}
	var wrong := SolaceTideTally.sentry_check(ctx, st, place, &"t3_f", "s0")  # a D card on an N route
	assert_true(wrong["useless"])
	assert_eq(wrong["why"], "type")
	assert_eq(wrong["beam_types"], ["N"])
	var right := SolaceTideTally.sentry_check(ctx, st, place, &"t3_f", "s1")  # the N card
	assert_false(right["useless"])
	var none := SolaceTideTally.sentry_check(ctx, st, place, &"t2_zz", "s1")
	assert_true(none["useless"])
	assert_eq(none["why"], "none", "no beam reaches that Site")
	# The same answer once the card is placed.
	var placed := {"sentries": {&"t3_f": "s0"}, "ghost": &""}
	assert_true(SolaceTideTally.sentry_check(ctx, st, placed, &"t3_f", "s0")["useless"])


func test_a_second_guard_behind_the_first_changes_no_outcome() -> void:
	var st := SolaceTideState.start(_cfg, 50)
	var ctx := _ctx(st)
	var place := {"sentries": {&"t3_f": "s1"}, "ghost": &""}
	# The N card on t2_f stands behind the one on t3_f that already blocks the N route: the type fits, the outcome is the same.
	var behind := SolaceTideTally.sentry_check(ctx, st, place, &"t2_f", "s1")
	assert_true(behind["useless"] or behind["why"] == "")
	if behind["useless"]:
		assert_eq(behind["why"], "same")


func test_the_check_agrees_with_the_forecast_it_is_built_on() -> void:
	var st := SolaceTideState.start(_cfg, 50)
	var ctx := _ctx(st)
	var place := {"sentries": {}, "ghost": &""}
	var base := SolaceTideRules.forecast(ctx, st, place, ["HOLD"])
	var guarded := SolaceTideRules.forecast(ctx, st, {"sentries": {&"t3_f": "s1"}, "ghost": &""}, ["HOLD"])
	var useful := SolaceTideTally.outcome_signature(base) != SolaceTideTally.outcome_signature(guarded)
	assert_eq(not SolaceTideTally.sentry_check(ctx, st, place, &"t3_f", "s1")["useless"], useful)


func test_a_forced_loss_is_the_city_already_over_the_line_and_it_holds_on_every_setup() -> void:
	var st := SolaceTideState.start(_cfg, 50)
	assert_false(SolaceTideTally.forced_loss(st))
	var healthy := st.deck.size()
	var ids: Array = []
	for i in healthy + 1:
		ids.append(StringName("w_%02d" % i))
	SolaceTideRules.add_infected(st, ids, false)
	assert_eq(SolaceTideRules.loss_margin(st), 0)
	assert_true(SolaceTideTally.forced_loss(st))
	# Every placement and every response ends the run on every outcome.
	var ctx := _ctx(st)
	var checked := 0
	for p in SolaceTideRules.placements(ctx, st):
		var sw := SolaceTideRules.launch(ctx, st, p)
		for resp in SolaceTideRules.response_options(ctx, sw):
			for r in SolaceTideRules.forecast(ctx, st, p, resp):
				assert_ne((r["result"]["state"] as SolaceTideState).lost, SolaceTideState.LOST_NONE)
				checked += 1
	assert_gt(checked, 0)


func test_the_next_decay_warns_when_the_downs_would_end_the_city() -> void:
	var st := _state(0, 0, 0)
	var calm := SolaceTideTally.next_decay(st, _cfg)
	assert_false(calm["fatal"])
	assert_false(calm["near"])
	# Fill the deck with INFECTED up to one short of the line, then leave Sites DOWN.
	var healthy := st.deck.size()
	var ids: Array = []
	for i in healthy - 1:
		ids.append(StringName("w_%02d" % i))
	SolaceTideRules.add_infected(st, ids, false)
	st.owned[&"d1"] = SolaceTideState.Cond.DOWN
	var t := SolaceTideTally.next_decay(st, _cfg)
	var run := st.duplicate_state()
	SolaceTideRules.decay(run, _cfg)
	assert_eq(int(t["added"]), run.wound_count() - st.wound_count(), "it is the real DECAY")
	assert_eq(int(t["margin"]), SolaceTideRules.loss_margin(run))
	assert_eq(bool(t["fatal"]), SolaceTideRules.loss_margin(run) == 0)
	assert_eq(t["downs"], [&"d1"])
	# Repairing the DOWN Site (what the HQ step does) lifts the threat.
	st.owned[&"d1"] = SolaceTideState.Cond.OK
	var fixed := SolaceTideTally.next_decay(st, _cfg)
	assert_true(int(fixed["margin"]) > int(t["margin"]) or not bool(t["fatal"]))


func _state(downs: int, wounds: int, doses: int, lost_since: int = 0) -> SolaceTideState:
	var st := SolaceTideState.start(_cfg, 50)
	for i in downs:
		st.owned[StringName("s%02d" % i)] = SolaceTideState.Cond.DOWN
	var ids: Array = []
	for i in wounds:
		ids.append(StringName("w_%02d" % i))
	SolaceTideRules.add_infected(st, ids, false)
	for i in doses:
		SolaceTideRules.add_dose(st)
	st.lost_since_raid = lost_since
	return st


func test_the_decay_tally_adds_up_to_the_real_decay() -> void:
	for downs in [0, 1, 2, 3]:
		for wounds in [0, 1, 4]:
			for doses in [0, 1, 2, 3]:
				for lost_since in [0, 1]:
					var pre := _state(downs, wounds, doses, lost_since)
					var t := SolaceTideTally.decay_tally(pre, _cfg)
					var run := pre.duplicate_state()
					SolaceTideRules.decay(run, _cfg)
					var tag := "downs %d wounds %d doses %d lost %d" % [downs, wounds, doses, lost_since]
					assert_eq(int(t["before"]), pre.wound_count(), tag)
					assert_eq(int(t["after"]), run.wound_count(), "after is the real DECAY's count: " + tag)
					var sum := int(t["before"]) + int(t["taken"]) + (1 if bool(t["spread"]) else 0) - int(t["cured"])
					assert_eq(sum, int(t["after"]), "the parts add up: " + tag)
					assert_eq(int(t["taken"]), downs, tag)


func test_a_dose_stops_the_spread_instead_of_curing_a_card() -> void:
	var t := SolaceTideTally.decay_tally(_state(2, 3, 1), _cfg)
	assert_true(bool(t["cancelled"]), "two Sites lost spread the Tide and the DOSE stops it")
	assert_false(bool(t["spread"]))
	assert_eq(int(t["cured"]), 0)
	var t2 := SolaceTideTally.decay_tally(_state(1, 3, 1), _cfg)
	assert_false(bool(t2["cancelled"]), "one Site lost does not spread")
	assert_eq(int(t2["cured"]), 1, "the DOSE cures a card")


func test_the_raid_tally_splits_sites_from_home_hits() -> void:
	var t := SolaceTideTally.raid_tally(4, 7, 2)
	assert_eq(int(t["added"]), 3)
	assert_eq(int(t["sites"]), 2)
	assert_eq(int(t["home"]), 1)
	var none := SolaceTideTally.raid_tally(4, 4, 0)
	assert_eq(int(none["added"]) + int(none["home"]), 0)
	var capped := SolaceTideTally.raid_tally(4, 5, 3)
	assert_eq(int(capped["sites"]), 1, "never more Sites than cards added")


func test_the_loss_margin_counts_the_cards_that_end_the_city() -> void:
	# The rule itself: at equal counts the margin is 1, and one more INFECTED card loses the city.
	var st := SolaceTideState.start(_cfg, 50)
	var healthy := st.deck.size()
	var ids: Array = []
	for i in healthy:
		ids.append(StringName("w_%02d" % i))
	SolaceTideRules.add_infected(st, ids, false)
	assert_eq(SolaceTideRules.loss_margin(st), 1)
	SolaceTideRules.check_loss(st)
	assert_eq(st.lost, SolaceTideState.LOST_NONE, "equal counts are not lost")
	SolaceTideRules.add_infected(st, [&"w_x"], false)
	SolaceTideRules.check_loss(st)
	assert_eq(st.lost, SolaceTideState.LOST_CITY, "one more INFECTED card ends the city")


func test_the_ladder_puts_a_run_ending_row_on_the_city_lost_tier_and_leaves_tier_of_alone() -> void:
	var live := SolaceTideState.start(_cfg, 50)
	var dead := live.duplicate_state()
	dead.lost = SolaceTideState.LOST_CITY
	var rows: Array = [{"tier": "DAMAGED", "result": {"state": dead}}, {"tier": "HOLDS", "result": {"state": live}}]
	SolaceTideTally.ladder(rows)
	assert_eq(rows[0]["tier"], "CITY LOST", "a row that ends the run is CITY LOST, not the raid's own tier")
	assert_eq(rows[0]["raid_tier"], "DAMAGED", "the raid's tier stays as the subline")
	assert_eq(rows[1]["tier"], "HOLDS")
	var odds := SolaceTideTally.tier_odds(rows)
	assert_eq(odds[0]["tier"], "CITY LOST", "the odds bar draws the worst tier first")
	assert_eq(TideFx.TIER_LADDER[TideFx.TIER_LADDER.size() - 1], "CITY LOST", "the legend ends on CITY LOST")
	assert_gt(TideFx.rank("CITY LOST"), TideFx.rank("BREACHED"))


func test_the_next_decay_forecast_lists_every_card_it_adds() -> void:
	for downs in [1, 2, 3]:
		var st := _state(downs, 2, 0, 1)
		var t := SolaceTideTally.next_decay(st, _cfg)
		var d: Dictionary = t["tally"]
		var sum := int(d["taken"]) + (1 if bool(d["spread"]) else 0) - int(d["cured"])
		assert_eq(sum, int(t["added"]), "the warning's lines (DOWN to TAKEN, spread, DOSE) add up to its +N: downs %d" % downs)
