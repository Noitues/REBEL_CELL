extends GutTest
## M1 content matches GDD A.1 / A.3: Breaker deck, the three enemies, satellite dock.


func _enemy(id: StringName) -> EnemyData:
	return ContentRegistry.get_content(id) as EnemyData


func _slice_ids(w: WheelData) -> Array[StringName]:
	var out: Array[StringName] = []
	for slot in w.slots:
		out.append(slot.slice.id)
	return out


func test_breaker_starting_deck_is_the_a1_list() -> void:
	var breaker := ContentRegistry.get_content(&"breaker") as ClassData
	var counts := {}
	for c in breaker.starting_deck:
		counts[c.id] = int(counts.get(c.id, 0)) + 1
	assert_eq(counts, {&"jolt": 4, &"brute_spin": 2, &"fine_tune": 2, &"mirror_flip": 1, &"overdrive": 1})
	assert_eq(breaker.starting_deck.size(), 10)
	assert_eq((ContentRegistry.get_content(&"overdrive") as CardData).class_id, &"breaker")
	assert_eq(breaker.base_hp, 60)
	assert_eq(breaker.rank_rewards[0].inner_ring.segments[0].output_multiplier, 2.0)
	assert_true(breaker.rank_rewards[0].inner_ring.segments[1].pierce)


func test_card_costs_match_a1() -> void:
	var costs := {&"jolt": 1, &"brute_spin": 2, &"fine_tune": 1, &"mirror_flip": 3, &"overdrive": 1}
	for id in costs:
		assert_eq((ContentRegistry.get_content(id) as CardData).ram_cost, costs[id], String(id))


func test_collections_agent_matches_a3() -> void:
	var e := _enemy(&"collections_agent")
	assert_eq(e.hp, 40)
	assert_eq(_slice_ids(e.wheel), [&"atk_8", &"atk_8", &"def_6", &"dose", &"crit_14", &"miss"])
	assert_eq(e.spawns.size(), 1)
	assert_eq(e.spawns[0].satellite.id, &"collections_drone")
	assert_eq(e.spawns[0].dock_slot, 1)
	var drone := e.spawns[0].satellite
	assert_eq(drone.hp, 5)
	assert_eq(drone.wheel.slice_count, 2)
	assert_eq(_slice_ids(drone.wheel), [&"atk_3", &"def_3"])


func test_compliance_officer_matches_a3() -> void:
	var e := _enemy(&"compliance_officer")
	assert_eq(e.hp, 50)
	assert_eq(_slice_ids(e.wheel), [&"atk_7", &"atk_7", &"def_6", &"crit_12", &"atk_7", &"miss"])
	assert_eq(e.wheel.hub.id, &"compliance_lock")
	assert_eq(e.wheel.hub.hub_resistance, 3)


func test_dosage_dispenser_matches_a3() -> void:
	var e := _enemy(&"dosage_dispenser")
	assert_eq(e.hp, 38)
	assert_eq(_slice_ids(e.wheel), [&"dose", &"atk_6", &"dose", &"def_5", &"atk_6", &"miss"])
	var dose := ContentRegistry.get_content(&"dose") as SliceData
	assert_eq(dose.slice_type, RC.SliceType.AFFLICT)
	assert_eq(dose.extra_effects[0].effects[0].status, RC.Status.CORRUPTED)
	assert_eq(dose.extra_effects[0].effects[0].slice_pick, RC.SlicePick.RANDOM_NON_MISS)


func test_session_against_collections_agent_docks_the_drone_on_slot_1() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"collections_agent"], 1)
	var sats := s.state.satellites_of(&"enemy_0")
	assert_eq(sats.size(), 1)
	assert_eq(sats[0].dock_slot, 1)
	assert_eq(sats[0].hp, 5)
	assert_eq(sats[0].source_id, &"collections_drone")
	assert_eq(s.state.hand.size(), 5)
	assert_eq(s.state.draw_pile.size(), 5)
	assert_eq(s.state.turn, 1)
	assert_eq(s.state.phase, CombatState.Phase.PLAYER_PHASE)
