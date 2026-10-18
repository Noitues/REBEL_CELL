extends GutTest
## N13 (designer 2026-10-18, Q7/Q10): max 1 satellite per slice. A spawn on an occupied
## slice destroys the one there (it counts as destroyed) and docks the new one. Every
## destroyed satellite fires ON_SATELLITE_DESTROYED: killed, replaced or cleared.


## A host that docks `first` on slot 2 at combat start and launches `second` on slot 2 at
## turn 2 start; the operative's Hub gains 3 block per destroyed satellite.
func _replace_session(cards: Array[CardData] = []) -> CombatSession:
	var first := SatelliteFixture.satellite(&"sf_first")
	var second := SatelliteFixture.satellite(&"sf_second", 7)
	var later := CombatFixture.spawn(second, SatelliteFixture.DOCK_SLOT)
	later.trigger = RC.Trigger.ON_TURN_START
	later.every_n = 2  # turn 1 start skips it; turn 2 start replaces
	var spawns: Array[SatelliteSpawnData] = [CombatFixture.spawn(first, SatelliteFixture.DOCK_SLOT), later]
	return SatelliteFixture.session(cards, spawns, _hub())


func _hub() -> HubCoreData:
	var block := CombatFixture.effect(RC.EffectType.GAIN_BLOCK, RC.EffectTarget.SELF, 3)
	var hook := CombatFixture.triggered(RC.Trigger.ON_SATELLITE_DESTROYED, [block])
	return CombatFixture.hub(&"sf_hub", 0, [hook])


func _destroyed_triggers(r: CombatResult) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for ev in CombatFixture.events_of(r, "trigger"):
		if int(ev["trigger"]) == RC.Trigger.ON_SATELLITE_DESTROYED:
			out.append(ev)
	return out


func test_spawn_on_an_occupied_slice_replaces_and_fires_the_trigger() -> void:
	var s := _replace_session()
	var first := SatelliteFixture.sat_of(s)
	assert_eq(first.source_id, &"sf_first")
	var preview := s.preview(CombatAction.end_turn())
	var r := s.apply(CombatAction.end_turn())
	assert_true(r.ok(), r.error)
	var sats := s.state.satellites_of(&"enemy_0")
	assert_eq(sats.size(), 1, "max 1 per slice")
	assert_eq(sats[0].source_id, &"sf_second")
	assert_eq(sats[0].dock_slot, SatelliteFixture.DOCK_SLOT)
	assert_eq(sats[0].hp, sats[0].max_hp, "the new one starts at full HP")
	assert_false(s.state.get_combatant(first.id).is_alive(), "the old one is destroyed")
	var died := CombatFixture.events_of(r, "died").filter(func(ev: Dictionary) -> bool: return ev["target"] == first.id)
	assert_eq(died.size(), 1, "reported once")
	assert_eq(String(died[0].get("cause", "")), "replaced")
	assert_eq(_destroyed_triggers(r).size(), 1, "ON_SATELLITE_DESTROYED fired once")
	assert_eq(preview.state.state_hash(), r.state.state_hash(), "preview == result")


func test_a_killed_satellite_fires_the_trigger_once() -> void:
	var hit := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.TARGET_WHEEL, 50)
	var card := CombatFixture.card(&"sf_zap", [hit])
	var s := SatelliteFixture.session([card], [], _hub())
	var sat := SatelliteFixture.sat_of(s)
	var block := s.state.player.block
	var r := SatelliteFixture.play(s, &"sf_zap", sat.id)
	assert_true(r.ok(), r.error)
	assert_false(s.state.get_combatant(sat.id).is_alive())
	assert_eq(_destroyed_triggers(r).size(), 1)
	assert_eq(s.state.player.block, block + 3, "the Hub hook ran")


func test_satellites_cleared_with_their_host_fire_the_trigger() -> void:
	var hit := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.TARGET_WHEEL, 500)
	var card := CombatFixture.card(&"sf_nuke", [hit])
	var s := SatelliteFixture.session([card], [], _hub())
	var r := SatelliteFixture.play(s, &"sf_nuke", &"enemy_0")
	assert_true(r.ok(), r.error)
	assert_eq(_destroyed_triggers(r).size(), 1, "the docked satellite went down with its host")


func test_a_spawn_on_a_free_slice_replaces_nothing() -> void:
	var s := SatelliteFixture.session([], [], _hub())
	var r := s.apply(CombatAction.end_turn())
	assert_true(r.ok(), r.error)
	assert_eq(_destroyed_triggers(r).size(), 0)
	assert_eq(s.state.satellites_of(&"enemy_0").size(), 1)


func test_replace_is_deterministic_across_runs() -> void:
	var hashes: Array[int] = []
	for i in 3:
		var s := _replace_session()
		s.apply(CombatAction.end_turn())
		s.apply(CombatAction.end_turn())
		hashes.append(s.state_hash())
	assert_eq(hashes[0], hashes[1])
	assert_eq(hashes[1], hashes[2])
