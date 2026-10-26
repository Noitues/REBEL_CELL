extends GutTest
## Phase 3b (tier fast): the INFECTED tally the raid screen shows (SolaceTideTally). DECAY's tally adds up to the real DECAY on every mix of DOWN
## Sites, spread and DOSE cards; the raid's tally splits the added cards into Sites lost and HOME hits; the loss margin counts the INFECTED cards
## that still fit before the city is lost.

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = load("res://content/config/campaign_config.tres")


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
