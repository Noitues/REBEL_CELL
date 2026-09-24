extends GutTest
## Inner Ring segments beyond the Breaker ring (GDD 6.4): Corrupt, Anchor, Accelerator,
## Echo, and the Rank 3 segment swap flow (CampaignRules + the netrun's working copy).

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


## A Breaker (real content) whose Rank 1 ring has `segment_id` in every segment.
func _session(segment_id: StringName, enemy: StringName = &"triage_unit", seed: int = 4) -> CombatSession:
	var ids := [String(segment_id), String(segment_id), String(segment_id)]
	var s := CombatSession.start(_resolver, &"breaker", [enemy], seed, &"rank:1", 0, {"ring_segment_ids": ids})
	assert_eq(s.state.player.wheel.ring_segment_ids, [segment_id, segment_id, segment_id])
	return s


func test_corrupt_corrupts_the_targets_resolved_slice() -> void:
	var s := _session(&"seg_corrupt")
	var e := s.state.get_combatant(&"enemy_0")
	CombatFixture.land(e, 2)
	CombatFixture.land(s.state.player, 1)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.slice_statuses[2], RC.Status.CORRUPTED)


func test_anchor_skips_the_next_respin_after_a_perfect() -> void:
	var s := _session(&"seg_anchor")
	CombatFixture.land(s.state.player, 1, 0)
	var rotation := s.state.player.wheel.rotation
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "frozen_skip").size(), 1)
	assert_eq(s.state.player.wheel.rotation, rotation, "no respin: the Perfect holds")
	# The anchored turn lands the same Perfect again, but a wheel that just skipped its
	# respin cannot be frozen twice in a row: no perpetual lock.
	rotation = s.state.player.wheel.rotation
	r = s.apply(CombatAction.end_turn())
	assert_true(CombatFixture.events_of(r, "freeze_blocked").size() >= 1)
	assert_eq(CombatFixture.events_of(r, "frozen_skip").size(), 0, "it respins this time")
	CombatFixture.land(s.state.player, 1, 1)
	rotation = s.state.player.wheel.rotation
	s.apply(CombatAction.end_turn())
	assert_ne(s.state.player.wheel.rotation, rotation, "a Good landing does not anchor")


func test_accelerator_makes_nudge_cards_trigger_twice_next_turn() -> void:
	var s := _session(&"seg_accelerator")
	CombatFixture.land(s.state.player, 1)
	s.apply(CombatAction.end_turn())
	assert_true(s.state.double_nudge_cards, "armed for this turn")
	# Put a Fine Tune in hand (two nudges) and play it on our own outer ring.
	s.state.hand[0] = &"fine_tune"
	var before := s.state.player.wheel.rotation
	var a := CombatAction.play_card(0, &"player")
	a.ring = RC.RingScope.OUTER
	a.direction = 1
	var r := s.apply(a)
	assert_true(r.ok(), r.error)
	assert_eq(CombatFixture.events_of(r, "accelerator").size(), 1)
	assert_eq(s.state.player.wheel.rotation, before + 4, "two nudges resolved twice")
	CombatFixture.land(s.state.player, 5)  # Miss (no accelerator this time: ring resolves anyway)
	s.state.player.wheel.inner_rotation = 0
	s.apply(CombatAction.end_turn())


func test_echo_resolves_the_outer_slice_again_at_half() -> void:
	var s := _session(&"seg_echo")
	CombatFixture.land(s.state.player, 1, 1)  # Atk 6, Good (no Breaker Perfect hook)
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 2)
	assert_eq(hits[0]["amount"], 6)
	assert_eq(hits[1]["amount"], 3)


func test_rank_3_swap_flow_reaches_the_combat_wheel() -> void:
	var cfg := CombatFixture.config()
	var lookup := GridFixture.lookup()
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var breaker := ContentRegistry.get_content(&"breaker") as ClassData
	var c := CampaignRules.new_campaign(corp, cfg, lookup, 1, breaker, GridFixture.home_node())
	var op := c.roster[0]
	assert_eq(CampaignRules.swap_ring_segment(c, lookup, op.id, 2, &"seg_echo")[0]["type"], "refused", "Rank 0 has no swaps")
	op.rank = 3
	assert_eq(CampaignRules.ring_segment_options(op, breaker), [&"seg_corrupt", &"seg_anchor", &"seg_accelerator", &"seg_echo"])
	assert_eq(CampaignRules.swap_ring_segment(c, lookup, op.id, 2, &"seg_x2")[0]["type"], "refused", "not an option")
	assert_eq(CampaignRules.swap_ring_segment(c, lookup, op.id, 2, &"seg_echo")[0]["type"], "segment_swapped")
	assert_eq(op.ring_segment_ids, [&"", &"", &"seg_echo"])
	var s := NetrunSession.start(_resolver, c, op.id, 1, &"t1_a", 5)
	s.enter_node(s.available_nodes()[0])
	assert_true(s.in_combat())
	assert_eq(s.combat.state.player.wheel.ring_segment_ids, [&"seg_x2", &"seg_pierce", &"seg_echo"])
	# Back to the default.
	CampaignRules.swap_ring_segment(c, lookup, op.id, 2, &"")
	assert_eq(op.ring_segment_ids, [&"", &"", &""])
	var again := CampaignState.from_dict(c.to_dict())
	assert_eq(again.get_operative(op.id).ring_segment_ids.size(), 3, "swaps survive save/load")
