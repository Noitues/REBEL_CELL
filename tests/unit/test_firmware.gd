extends GutTest
## Every Firmware in the slice has a unit test (M2 acceptance, GDD 6.1).

var _atk6: SliceData
var _def5: SliceData
var _crit12: SliceData
var _miss: SliceData


func before_each() -> void:
	_atk6 = CombatFixture.slice(&"fw_atk6", RC.SliceType.ATTACK, 6)
	_def5 = CombatFixture.slice(&"fw_def5", RC.SliceType.DEFEND, 5, RC.TargetRule.SELF)
	_crit12 = CombatFixture.slice(&"fw_crit12", RC.SliceType.CRIT, 12)
	_miss = CombatFixture.slice(&"fw_miss", RC.SliceType.MISS, 0, RC.TargetRule.SELF)


func _fw(id: StringName) -> FirmwareData:
	return ContentRegistry.get_content(id) as FirmwareData


## Wheel Crit, Atk, Def, Atk, Atk, Miss with `firmware_id` socketed in slot 1 (Atk 6).
func _session(firmware_id: StringName, slot: int = 1) -> CombatSession:
	var firmware := []
	firmware.resize(6)
	firmware[slot] = _fw(firmware_id)
	var deck: Array[CardData] = [CombatFixture.card(&"fw_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"fw_class", 60, CombatFixture.wheel([_crit12, _atk6, _def5, _atk6, _atk6, _miss], null, [0], 0, null, firmware), deck)
	var dummy := CombatFixture.enemy(&"fw_dummy", 200, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, dummy]), cls.id, [dummy.id], 2)
	CombatFixture.land(s.state.player, slot)
	return s


func _hits(r: CombatResult) -> Array[Dictionary]:
	return CombatFixture.events_of(r, "damage")


func test_patch_plus_adds_50_percent_output() -> void:
	var s := _session(&"patch_plus")
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_hits(r)[0]["amount"], 9)


func test_hardened_is_permanent_encryption() -> void:
	var s := _session(&"hardened")
	var events: Array[Dictionary] = []
	var absorbed := s.resolver.fx.apply_status(s.state.player, 1, RC.Status.CORRUPTED, events)
	assert_false(absorbed)
	assert_eq(s.state.player.wheel.slice_statuses[1], RC.Status.NONE)
	assert_eq(events[0]["type"], "status_absorbed")


func test_burner_is_permanently_overclocked_and_adds_heat() -> void:
	var s := _session(&"burner")
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_hits(r)[0]["amount"], 9, "1.5x every time")
	var heat := CombatFixture.events_of(r, "campaign_effect")
	assert_eq(heat.size(), 1)
	assert_eq(heat[0]["effect"], RC.EffectType.MODIFY_HEAT)
	assert_eq(heat[0]["amount"], 1)
	assert_eq(s.state.player.wheel.slice_statuses[1], RC.Status.NONE, "does not burn out into CORRUPTED")
	CombatFixture.land(s.state.player, 1)
	r = s.apply(CombatAction.end_turn())
	assert_eq(_hits(r)[0]["amount"], 9, "still overclocked next turn")


func test_leech_restores_1_ram_on_good_or_better() -> void:
	var s := _session(&"leech")
	CombatFixture.land(s.state.player, 1, 1)
	var ram := s.state.ram
	var r := s.apply(CombatAction.end_turn())
	assert_eq(s.state.ram, ram + 1 + 4, "+1 from Leech, +4 regen")
	s = _session(&"leech")
	CombatFixture.land(s.state.player, 1, 2)
	ram = s.state.ram
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.ram, ram + 4, "Partial: nothing from Leech")


func test_leech_only_fits_attack_slices() -> void:
	var fw := _fw(&"leech")
	assert_eq(fw.allowed_slice_types, [RC.SliceType.ATTACK])
	var w := CombatFixture.wheel([_crit12, _atk6, _def5, _atk6, _atk6, _miss], null, [0], 0, null, [null, null, fw])
	assert_eq(w.validate().size(), 1, "Leech on a DEF slot fails validation")


func test_mirror_copies_the_neighbour_on_the_side_you_landed() -> void:
	var s := _session(&"mirror")
	CombatFixture.land(s.state.player, 1, 1)  # clockwise of centre -> neighbour slot 2 (Def 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_hits(r).size(), 1, "own attack")
	assert_eq(_hits(r)[0]["amount"], 6)
	var blocks := CombatFixture.events_of(r, "block")
	assert_eq(blocks.size(), 1, "copied the DEF neighbour")
	assert_eq(blocks[0]["target"], &"player")
	s = _session(&"mirror")
	CombatFixture.land(s.state.player, 1, -1)  # counter-clockwise -> neighbour slot 0 (Crit 12)
	r = s.apply(CombatAction.end_turn())
	var amounts := []
	for h in _hits(r):
		amounts.append(h["amount"])
	assert_eq(amounts, [6, 12], "own attack, then the copied Crit")


func test_mirror_copies_both_neighbours_on_perfect() -> void:
	var s := _session(&"mirror")
	CombatFixture.land(s.state.player, 1, 0)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_hits(r).size(), 2, "own attack + Crit neighbour")
	assert_eq(CombatFixture.events_of(r, "block").size(), 1, "+ Def neighbour")


func test_shunt_resolves_the_neighbour_instead_at_1_5x() -> void:
	var s := _session(&"shunt")
	CombatFixture.land(s.state.player, 1, -1)  # toward slot 0 (Crit 12)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_hits(r).size(), 1)
	assert_eq(_hits(r)[0]["amount"], 18, "Crit 12 x 1.5, own Atk skipped")
	s = _session(&"shunt")
	CombatFixture.land(s.state.player, 1, 2)  # toward slot 2 (Def 5), Partial
	r = s.apply(CombatAction.end_turn())
	assert_eq(_hits(r).size(), 0)
	assert_eq(CombatFixture.events_of(r, "block")[0]["amount"], 4, "Def 5 x 1.5 x 0.5 partial = 3.75 -> 4")


func test_shunt_does_nothing_special_on_perfect() -> void:
	var s := _session(&"shunt")
	CombatFixture.land(s.state.player, 1, 0)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_hits(r).size(), 1)
	assert_eq(_hits(r)[0]["amount"], 6)
	assert_eq(CombatFixture.events_of(r, "block").size(), 0)


func test_all_six_firmware_exist_and_validate() -> void:
	for id in [&"patch_plus", &"hardened", &"burner", &"leech", &"mirror", &"shunt"]:
		assert_not_null(_fw(id), String(id))
