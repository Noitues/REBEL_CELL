extends GutTest
## CORRUPTED, OVERCLOCKED and ENCRYPTED behave per GDD 2.9 (M1 acceptance).

var _cfg: CampaignConfigData
var _atk6: SliceData
var _null: SliceData
var _cls: ClassData
var _dummy: EnemyData
var _overdrive: CardData
var _encrypt: CardData


func before_each() -> void:
	_cfg = CombatFixture.config()
	_atk6 = CombatFixture.slice(&"s_atk6", RC.SliceType.SHIM, 6)
	_null = CombatFixture.slice(&"s_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	_overdrive = CombatFixture.card(&"s_overdrive", [CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.OWN_WHEEL, 0, RC.RingScope.OUTER, 1.0, RC.Status.OVERCLOCKED)], 1, RC.WheelTarget.OWN)
	_encrypt = CombatFixture.card(&"s_encrypt", [CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.OWN_WHEEL, 0, RC.RingScope.OUTER, 1.0, RC.Status.ENCRYPTED)], 1, RC.WheelTarget.OWN)
	var deck: Array[CardData] = [_overdrive, _encrypt]
	_cls = CombatFixture.operative_class(&"s_class", 60, CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _null]), deck)
	_dummy = CombatFixture.enemy(&"s_dummy", 200, CombatFixture.null_wheel())


func _session(enemy: EnemyData = null, heat_majors: int = 0) -> CombatSession:
	if enemy == null:
		enemy = _dummy
	var s := CombatSession.start(CombatFixture.resolver([_cls, enemy]), _cls.id, [enemy.id], 21, &"", heat_majors)
	CombatFixture.land(s.state.player, 1)
	return s


func test_corrupted_slice_no_longer_damages_or_drains_when_it_resolves() -> void:
	var s := _session(_dummy, 2)
	s.state.player.wheel.set_status(1, RC.Status.CORRUPTED)
	var ram := s.state.ram
	var r := s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "corrupted").size(), 0, "N9: no bite at any Heat")
	assert_eq(s.state.player.hp, 60)
	assert_eq(s.state.ram, ram + 4, "no RAM drain, then +4 at the next turn start")
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], 6, "the slice still attacks normally")
	assert_eq(s.state.player.wheel.status_at(1), RC.Status.CORRUPTED, "lasts until cleansed")


func test_corrupted_enemy_slice_does_not_hurt_the_enemy() -> void:
	var enemy := CombatFixture.enemy(&"s_corrupt_enemy", 50, CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _atk6]))
	var s := _session(enemy)
	var e := s.state.get_combatant(&"enemy_0")
	CombatFixture.land(e, 0)
	e.wheel.set_status(0, RC.Status.CORRUPTED)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 50 - 6, "only the player's 6")


func test_overclocked_gives_1_5x_once_then_becomes_corrupted() -> void:
	var s := _session()
	var idx := s.state.hand.find(&"s_overdrive")
	var r := s.apply(CombatAction.play_card(idx))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.player.wheel.status_at(1), RC.Status.OVERCLOCKED, "slice under the pointer overclocked")
	r = s.apply(CombatAction.end_turn())
	assert_eq(CombatFixture.events_of(r, "damage")[0]["amount"], roundi(6 * _cfg.overclock_multiplier))
	assert_eq(s.state.player.wheel.status_at(1), RC.Status.CORRUPTED, "burned out")


func test_encrypted_absorbs_the_next_status_then_clears() -> void:
	var s := _session()
	var r := s.apply(CombatAction.play_card(s.state.hand.find(&"s_encrypt")))
	assert_true(r.ok(), r.error)
	assert_eq(s.state.player.wheel.status_at(1), RC.Status.ENCRYPTED)
	r = s.apply(CombatAction.play_card(s.state.hand.find(&"s_overdrive")))
	assert_eq(CombatFixture.events_of(r, "status_absorbed").size(), 1)
	assert_eq(s.state.player.wheel.status_at(1), RC.Status.NONE, "encryption consumed, no overclock")


func test_hardened_firmware_is_permanent_encryption() -> void:
	var hardened := FirmwareData.new()
	hardened.id = &"s_hardened"
	hardened.permanent_status = RC.Status.ENCRYPTED
	var w := CombatFixture.wheel([_atk6, _atk6, _atk6, _atk6, _atk6, _null], null, [0], 0, null, [null, hardened])
	var deck: Array[CardData] = [_overdrive, _overdrive]
	var cls := CombatFixture.operative_class(&"s_hard_class", 60, w, deck)
	var s := CombatSession.start(CombatFixture.resolver([cls, _dummy, hardened]), cls.id, [_dummy.id], 4)
	CombatFixture.land(s.state.player, 1)
	for i in 2:
		var r := s.apply(CombatAction.play_card(0))
		assert_eq(CombatFixture.events_of(r, "status_absorbed").size(), 1, "absorbed every time")
	assert_eq(s.state.player.wheel.status_at(1), RC.Status.NONE)


func test_dose_corrupts_a_random_non_null_player_slice() -> void:
	var s := CombatSession.start(CombatFixture.resolver([_cls]), _cls.id, [&"dosage_dispenser"], 9)
	var dispenser := s.state.get_combatant(&"enemy_0")
	CombatFixture.land(dispenser, 0)  # Dose
	CombatFixture.land(s.state.player, 5)  # NULL: no attack, keeps the numbers clean
	var r := s.apply(CombatAction.end_turn())
	var statuses := CombatFixture.events_of(r, "status")
	assert_eq(statuses.size(), 1)
	assert_eq(statuses[0]["target"], &"player")
	assert_ne(statuses[0]["slot"], 5, "never the NULL slice")
	assert_eq(s.state.player.wheel.count_status(RC.Status.CORRUPTED), 1)
