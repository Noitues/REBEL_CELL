extends GutTest
## Player-side drones (GDD 2.6, 5.2, 6.2): DEPLOY slices dock drones on the operative's
## wheel, a drone resolves when its slice does, it takes enemy hits aimed at that slice,
## Botnet Seed grows drones on Perfects, Twin Pointer reads the wheel twice, Linked Bus
## drags your wheel along, Stolen Intent swaps a Miss for the enemy's slice. Drones
## survive save/load and replay.

var _atk6: SliceData
var _deploy: SliceData
var _miss: SliceData
var _hub: HubCoreData


func before_each() -> void:
	_atk6 = CombatFixture.slice(&"dr_atk6", RC.SliceType.ATTACK, 6)
	_deploy = CombatFixture.slice(&"dr_deploy", RC.SliceType.DEPLOY, 1, RC.TargetRule.SELF)
	_miss = CombatFixture.slice(&"dr_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)
	_hub = CombatFixture.hub(&"dr_hub")
	_hub.max_drones = 2
	_hub.drone = ContentRegistry.get_content(&"botnet_drone") as EnemyData


## Wheel: Deploy, Atk, Atk, Atk, Atk, Miss. Enemy: 300 HP punching bag, or an attacker.
func _session(daemons: Array = [], enemy_wheel: WheelData = null, seed: int = 9) -> CombatSession:
	var deck: Array[CardData] = [CombatFixture.card(&"dr_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"dr_class", 60, CombatFixture.wheel([_deploy, _atk6, _atk6, _atk6, _atk6, _miss], _hub), deck)
	var enemy := CombatFixture.enemy(&"dr_dummy", 300, enemy_wheel if enemy_wheel != null else CombatFixture.miss_wheel())
	var ids := []
	for d in daemons:
		ids.append(String(d))
	return CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], seed, &"", 0, {"daemon_ids": ids})


func _end(s: CombatSession) -> CombatResult:
	return s.apply(CombatAction.end_turn())


func test_deploy_slice_docks_a_drone_up_to_the_hub_cap() -> void:
	var s := _session()
	CombatFixture.land(s.state.player, 0)
	var r := _end(s)
	assert_eq(CombatFixture.events_of(r, "deploy").size(), 1)
	assert_eq(s.state.living_drones().size(), 1)
	assert_eq(s.state.drones[0].dock_slot, 0, "docked on the Deploy slice itself")
	assert_eq(s.state.drones[0].hp, 5)
	assert_true(s.state.drones[0].is_player and s.state.drones[0].is_satellite)
	CombatFixture.land(s.state.player, 0)
	_end(s)
	assert_eq(s.state.living_drones().size(), 2)
	assert_eq(s.state.drones[1].dock_slot, 1, "next free slot clockwise")
	CombatFixture.land(s.state.player, 0)
	r = _end(s)
	assert_eq(CombatFixture.events_of(r, "drone_cap").size(), 1, "max_drones 2")
	assert_eq(s.state.living_drones().size(), 2)


func test_drone_resolves_only_when_its_slice_resolves() -> void:
	var s := _session()
	CombatFixture.land(s.state.player, 0)
	_end(s)
	var drone := s.state.drones[0]
	# Land on slot 3: the drone on slot 0 stays quiet.
	CombatFixture.land(s.state.player, 3)
	var r := _end(s)
	var drone_pointers := 0
	for e in CombatFixture.events_of(r, "pointer"):
		if e["owner"] == drone.id:
			drone_pointers += 1
	assert_eq(drone_pointers, 0, "slot 3 resolved, drone on slot 0 idle")
	# Land on slot 0 again: Deploy fires and so does the drone (Atk 3 or Def 3).
	CombatFixture.land(s.state.player, 0)
	r = _end(s)
	drone_pointers = 0
	var drone_acted := false
	for e in r.events:
		if e.get("type", "") == "pointer" and e["owner"] == drone.id:
			drone_pointers += 1
		if e.get("type", "") in ["attack", "block"] and e.get("attacker", e.get("target")) == drone.id:
			drone_acted = true
	assert_eq(drone_pointers, 1)
	assert_true(drone_acted, "the drone attacked or blocked")


func test_drone_on_the_resolved_slice_takes_the_enemy_hit() -> void:
	# Atk 10 so the drone dies even when its own mini-wheel lands on Def 3.
	var atk10 := CombatFixture.slice(&"dr_atk10", RC.SliceType.ATTACK, 10)
	var enemy_wheel := CombatFixture.wheel([atk10, atk10, atk10, atk10, atk10, _miss])
	var s := _session([], enemy_wheel)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 5)
	_end(s)
	var drone := s.state.drones[0]
	assert_eq(drone.dock_slot, 0)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 1)
	var hp := s.state.player.hp
	var r := _end(s)
	assert_eq(CombatFixture.events_of(r, "bodyguard").size(), 1)
	assert_eq(s.state.player.hp, hp, "the operative was not hit")
	# The drone dies (10 damage vs 5 HP + at most 3 block) and is reported.
	assert_eq(CombatFixture.events_of(r, "died").size(), 1)
	assert_false(s.state.drones[0].is_alive())
	assert_eq(s.state.living_drones().size(), 1, "the Deploy slice docked a replacement this turn")


func test_botnet_seed_sprouts_one_hp_drones_on_perfects_max_two() -> void:
	var s := _session([&"botnet_seed"])
	for slot in [1, 2, 3]:
		CombatFixture.land(s.state.player, slot, 0)
		_end(s)
	var seeds := 0
	for d in s.state.living_drones():
		if d.source_id == &"seed_drone":
			seeds += 1
			assert_eq(d.hp, 1)
	assert_eq(seeds, 2, "third Perfect hits the cap")
	CombatFixture.land(s.state.player, 4, 1)
	var before := s.state.living_drones().size()
	_end(s)
	assert_eq(s.state.living_drones().size(), before, "Good landings do not seed")


func test_twin_pointer_reads_the_wheel_at_the_bottom_and_halves_ram() -> void:
	var s := _session([&"twin_pointer"])
	assert_eq(s.state.player.wheel.pointer_ticks, PackedInt32Array([0, 15]))
	assert_eq(s.state.max_ram, 6)
	assert_eq(s.state.ram, 6)
	CombatFixture.land(s.state.player, 1)  # pointer 0 on Atk 6 -> pointer 1 on slot 4 (Atk 6)
	var r := _end(s)
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 2, "both pointers trigger")
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 288)
	assert_eq(s.state.ram, 6, "regen is capped at the halved maximum")


func test_enemy_attacks_hit_both_twin_pointers() -> void:
	var enemy_wheel := CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _atk6])
	var s := _session([&"twin_pointer"], enemy_wheel)
	CombatFixture.land(s.state.player, 5)  # Miss under pointer 0, slot 2 under pointer 1
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	var r := _end(s)
	var on_me := 0
	for e in CombatFixture.events_of(r, "damage"):
		if e["target"] == &"player":
			on_me += 1
	assert_eq(on_me, 2, "one hit per operative pointer (GDD 2.7)")
	assert_eq(s.state.player.hp, 60 - 12)


func test_linked_bus_moves_your_wheel_with_enemy_nudges() -> void:
	var s := _session([&"linked_bus"])
	var mine := s.state.player.wheel.rotation
	var theirs := s.state.get_combatant(&"enemy_0").wheel.rotation
	var r := s.apply(CombatAction.nudge(&"enemy_0", -1))
	assert_eq(CombatFixture.events_of(r, "linked_bus").size(), 1)
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.rotation, theirs - 1)
	assert_eq(s.state.player.wheel.rotation, mine - 1, "same direction, free")
	assert_eq(s.state.free_nudges, 0)
	assert_eq(s.state.ram, 6, "no RAM spent on the echo")
	s.apply(CombatAction.nudge(&"player", 1))
	assert_eq(s.state.player.wheel.rotation, mine, "nudging your own wheel does not echo")


func test_stolen_intent_swaps_a_miss_for_the_enemys_slice_once() -> void:
	var enemy_wheel := CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _miss])
	var s := _session([&"stolen_intent"], enemy_wheel)
	CombatFixture.land(s.state.player, 5)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	var r := _end(s)
	assert_eq(CombatFixture.events_of(r, "stolen_intent").size(), 1)
	var hits := CombatFixture.events_of(r, "damage")
	assert_eq(hits.size(), 1)
	assert_eq(hits[0]["attacker"], &"player", "you attack with their Atk 6")
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 294)
	assert_eq(s.state.player.hp, 60, "they resolve your Miss")
	# Second time: no swap, you simply miss and get hit.
	CombatFixture.land(s.state.player, 5)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	r = _end(s)
	assert_eq(CombatFixture.events_of(r, "stolen_intent").size(), 0)
	assert_eq(s.state.player.hp, 54)
	# Preview equals the real result even with the swap.
	CombatFixture.land(s.state.player, 5)
	assert_eq(s.preview_end_turn().resolved_state.player.hp, _end(s).resolved_state.player.hp)


func test_drones_survive_save_load_and_replay() -> void:
	var s := _session([&"botnet_seed"])
	CombatFixture.land(s.state.player, 0)
	_end(s)
	CombatFixture.land(s.state.player, 1)
	_end(s)
	assert_eq(s.state.living_drones().size(), 3, "one Deploy drone and two seed drones")
	var reloaded := CombatSession.from_dict(s.resolver, s.to_dict())
	assert_eq(reloaded.state_hash(), s.state_hash())
	assert_eq(reloaded.state.drones.size(), s.state.drones.size())
	var d := s.state.duplicate_state()
	assert_eq(d.state_hash(), s.state_hash())
