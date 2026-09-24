extends GutTest
## Pointer rule and satellite bodyguard (GDD 2.7, M1 acceptance); Pierce ignores
## satellites and block.

var _atk6: SliceData
var _def10: SliceData
var _miss: SliceData


func before_each() -> void:
	_atk6 = CombatFixture.slice(&"g_atk6", RC.SliceType.ATTACK, 6)
	_def10 = CombatFixture.slice(&"g_def10", RC.SliceType.DEFEND, 10, RC.TargetRule.SELF)
	_miss = CombatFixture.slice(&"g_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)


func _player_class(with_ring: bool) -> ClassData:
	var deck: Array[CardData] = [CombatFixture.card(&"g_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var ring: InnerRingData = null
	if with_ring:
		ring = CombatFixture.ring([CombatFixture.segment(&"g_plain"), CombatFixture.segment(&"g_pierce", 1.0, true), CombatFixture.segment(&"g_plain2")])
	var w := CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _atk6], null, [0], 0, ring)
	return CombatFixture.operative_class(&"g_class", 60, w, deck)


func test_pointer_rule_hits_every_pointer_of_the_target_wheel() -> void:
	var cls := _player_class(false)
	var boss := CombatFixture.enemy(&"g_two_pointers", 100, CombatFixture.wheel([_miss, _miss, _miss, _miss, _miss, _miss], null, [0, 15]))
	var s := CombatSession.start(CombatFixture.resolver([cls, boss]), cls.id, [boss.id], 5)
	CombatFixture.land(s.state.player, 0)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage").size(), 2, "one attack lands at each of the two pointers")
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 88)


func test_enemy_with_several_pointers_attacks_from_each() -> void:
	var cls := _player_class(false)
	var boss := CombatFixture.enemy(&"g_two_atk", 100, CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _atk6], null, [0, 15]))
	var s := CombatSession.start(CombatFixture.resolver([cls, boss]), cls.id, [boss.id], 5)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)  # pointers 0 and 15 both land Perfect
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.player.hp, 48, "two enemy pointers, 6 each")


func test_satellite_docked_on_the_resolved_slice_takes_the_hit() -> void:
	var cls := _player_class(false)
	var drone := CombatFixture.enemy(&"g_drone", 5, CombatFixture.wheel([_miss, _miss]))
	var host := CombatFixture.enemy(&"g_host", 40, CombatFixture.wheel([_miss, _miss, _miss, _miss, _miss, _miss]), [CombatFixture.spawn(drone, 2)])
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], 5)
	var sat := s.state.satellites_of(&"enemy_0")[0]
	assert_eq(sat.dock_slot, 2)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 2)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "bodyguard").size(), 1)
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 40, "host untouched")
	assert_eq(s.state.get_combatant(sat.id).hp, 0, "drone absorbed 6 and died")
	assert_eq(s.state.satellites_of(&"enemy_0").size(), 0)


func test_satellite_on_another_slice_does_not_guard() -> void:
	var cls := _player_class(false)
	var drone := CombatFixture.enemy(&"g_drone", 5, CombatFixture.wheel([_miss, _miss]))
	var host := CombatFixture.enemy(&"g_host", 40, CombatFixture.wheel([_miss, _miss, _miss, _miss, _miss, _miss]), [CombatFixture.spawn(drone, 2)])
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], 5)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 3)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 34)


func test_satellite_attacks_the_player_after_its_host() -> void:
	var cls := _player_class(false)
	var drone := CombatFixture.enemy(&"g_drone", 5, CombatFixture.wheel([_atk6, _atk6]))
	var host := CombatFixture.enemy(&"g_host", 40, CombatFixture.wheel([_atk6, _miss, _miss, _miss, _miss, _miss]), [CombatFixture.spawn(drone, 4)])
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], 5)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 0)
	var r := s.apply(CombatAction.end_turn())
	var hits := CombatFixture.events_of(r, "damage")
	var on_player: Array[String] = []
	for h in hits:
		if h["target"] == &"player":
			on_player.append(String(h["attacker"]))
	assert_eq(on_player, ["enemy_0", "enemy_0_sat_0"], "host first, then its satellite")
	assert_eq(s.state.player.hp, 48)


func test_pierce_ignores_satellites_and_block() -> void:
	var cls := _player_class(true)
	var drone := CombatFixture.enemy(&"g_drone", 5, CombatFixture.wheel([_miss, _miss]))
	var host := CombatFixture.enemy(&"g_host", 40, CombatFixture.wheel([_def10, _def10, _def10, _def10, _def10, _def10]), [CombatFixture.spawn(drone, 1)])
	var s := CombatSession.start(CombatFixture.resolver([cls, drone, host]), cls.id, [host.id], 5)
	assert_true(s.state.player.wheel.has_inner_ring())
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land_inner(s.state.player, 1)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 1)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "bodyguard").size(), 0, "satellite ignored")
	var hit := CombatFixture.events_of(r, "damage")[0]
	assert_true(hit["pierce"])
	assert_eq(hit["blocked"], 0, "block ignored")
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 34)
	assert_eq(s.state.satellites_of(&"enemy_0")[0].hp, 5, "drone untouched")


func test_without_pierce_block_and_satellite_apply() -> void:
	var cls := _player_class(true)
	var host := CombatFixture.enemy(&"g_host", 40, CombatFixture.wheel([_def10, _def10, _def10, _def10, _def10, _def10]))
	var s := CombatSession.start(CombatFixture.resolver([cls, host]), cls.id, [host.id], 5)
	CombatFixture.land(s.state.player, 0)
	CombatFixture.land_inner(s.state.player, 0)
	CombatFixture.land(s.state.get_combatant(&"enemy_0"), 1)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 40, "10 block soaks the 6")
