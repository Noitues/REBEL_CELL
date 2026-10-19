extends GutTest
## Plan 2 N8: slot statuses are ×N stacks, {status: stacks} on every wheel (operative, enemy,
## satellite, drone). Storage, apply (cap, ENCRYPTED absorb), cleanse (all / one stack),
## OVERCLOCKED burn-out, and stacks travelling with their slice (flip, spin, satellites).

var _cfg: CampaignConfigData
var _fx: EffectInterpreter


func before_each() -> void:
	_cfg = CombatFixture.config()
	_fx = CombatFixture.resolver().fx


func _wheel() -> WheelState:
	var w := WheelState.new()
	for i in RC.SLICES:
		w.slot_slice_ids.append(&"")
		w.slot_firmware_ids.append(&"")
		w.slice_stacks.append({})
	return w


func _combatant() -> CombatantState:
	var c := CombatantState.new()
	c.id = &"t"
	c.display_name = "T"
	c.wheel = _wheel()
	return c


func _apply(c: CombatantState, slot: int, status: int, stacks: int = 1) -> bool:
	var events: Array[Dictionary] = []
	return _fx.apply_status(c, slot, status, events, stacks)


func test_apply_status_on_empty_slice_sets_one_stack() -> void:
	var c := _combatant()
	assert_true(_apply(c, 2, RC.Status.OUTPUT_DOWN))
	assert_eq(c.wheel.stacks_of(2, RC.Status.OUTPUT_DOWN), 1)
	assert_eq(c.wheel.slice_stacks[2], {RC.Status.OUTPUT_DOWN: 1})


func test_apply_status_twice_adds_stacks() -> void:
	var c := _combatant()
	_apply(c, 2, RC.Status.OUTPUT_DOWN)
	_apply(c, 2, RC.Status.OUTPUT_DOWN)
	assert_eq(c.wheel.stacks_of(2, RC.Status.OUTPUT_DOWN), 2)


func test_apply_status_amount_three_sets_three() -> void:
	var c := _combatant()
	_apply(c, 0, RC.Status.OUTPUT_DOWN, 3)
	assert_eq(c.wheel.stacks_of(0, RC.Status.OUTPUT_DOWN), 3)


func test_stacks_cap_at_config_max() -> void:
	var cap := _cfg.status_stack_cap
	for amount in [cap - 1, cap, cap + 1, 10]:
		var c := _combatant()
		_apply(c, 1, RC.Status.OUTPUT_DOWN, amount)
		assert_eq(c.wheel.stacks_of(1, RC.Status.OUTPUT_DOWN), mini(amount, cap), "amount %d" % amount)
	var full := _combatant()
	_apply(full, 1, RC.Status.OVERCLOCKED, cap)
	_apply(full, 1, RC.Status.OVERCLOCKED, 1)
	assert_eq(full.wheel.stacks_of(1, RC.Status.OVERCLOCKED), cap, "a full slot stays at the cap")


func test_corrupted_and_encrypted_ignore_the_cap() -> void:
	var cap := _cfg.status_stack_cap
	var c := _combatant()
	_apply(c, 1, RC.Status.CORRUPTED, cap + 3)
	assert_eq(c.wheel.stacks_of(1, RC.Status.CORRUPTED), cap + 3, "no corruption cap (Q36)")
	_apply(c, 2, RC.Status.ENCRYPTED, cap + 1)
	assert_eq(c.wheel.stacks_of(2, RC.Status.ENCRYPTED), cap + 1, "ENCRYPTED is not capped (designer 2026-10-18)")


func test_zero_stacks_are_never_stored() -> void:
	var w := _wheel()
	assert_eq(w.add_stacks(3, RC.Status.OUTPUT_DOWN, 0, _cfg.status_stack_cap), 0)
	assert_false(w.slice_stacks[3].has(RC.Status.OUTPUT_DOWN), "the key is absent, not {S: 0}")
	w.set_status(3, RC.Status.CORRUPTED, 0)
	assert_eq(w.slice_stacks[3], {})
	w.add_stacks(3, RC.Status.OUTPUT_DOWN, 1, _cfg.status_stack_cap)
	w.remove_stacks(3, RC.Status.OUTPUT_DOWN, 1)
	assert_eq(w.slice_stacks[3], {}, "the last stack removed takes the key")


func test_multiple_status_types_coexist_on_slice() -> void:
	var c := _combatant()
	_apply(c, 4, RC.Status.CORRUPTED)
	_apply(c, 4, RC.Status.OUTPUT_DOWN, 2)
	assert_eq(c.wheel.stacks_of(4, RC.Status.CORRUPTED), 1)
	assert_eq(c.wheel.stacks_of(4, RC.Status.OUTPUT_DOWN), 2)
	assert_eq(c.wheel.statuses_at(4), [RC.Status.CORRUPTED, RC.Status.OUTPUT_DOWN] as Array[int])


func test_cleanse_removes_all_stacks_by_default() -> void:
	var c := _combatant()
	_apply(c, 1, RC.Status.OUTPUT_DOWN, 3)
	_apply(c, 1, RC.Status.CORRUPTED)
	var events: Array[Dictionary] = []
	_fx.cleanse(c, 1, events)
	assert_eq(c.wheel.slice_stacks[1], {})
	assert_eq(events.size(), 1)


func test_cleanse_one_stack_mode_decrements() -> void:
	var c := _combatant()
	_apply(c, 1, RC.Status.OUTPUT_DOWN, 3)
	_apply(c, 1, RC.Status.CORRUPTED)
	var events: Array[Dictionary] = []
	_fx.cleanse(c, 1, events, RC.CleanseMode.ONE_STACK)
	assert_eq(c.wheel.slice_stacks[1], {RC.Status.OUTPUT_DOWN: 2}, "x3 -> x2; x1 -> gone")


func test_cleanse_effect_reads_its_mode() -> void:
	var c := _combatant()
	var s := CombatState.new()
	s.player = c
	_apply(c, 0, RC.Status.OUTPUT_DOWN, 3)
	var e := CombatFixture.effect(RC.EffectType.CLEANSE, RC.EffectTarget.SELF)
	e.cleanse_mode = RC.CleanseMode.ONE_STACK
	var events: Array[Dictionary] = []
	_fx.apply_effect(s, e, {"owner": c, "pointer_index": 0}, CombatFixture.rng(1), events)
	assert_eq(c.wheel.stacks_of(0, RC.Status.OUTPUT_DOWN), 2)


func test_encrypted_absorbs_one_apply_regardless_of_amount() -> void:
	var c := _combatant()
	_apply(c, 2, RC.Status.ENCRYPTED)
	assert_false(_apply(c, 2, RC.Status.OUTPUT_DOWN, 3))
	assert_eq(c.wheel.stacks_of(2, RC.Status.OUTPUT_DOWN), 0)
	assert_eq(c.wheel.slice_stacks[2], {}, "ENCRYPTED consumed")


func test_encrypted_stacks_absorb_that_many_applies() -> void:
	var c := _combatant()
	_apply(c, 2, RC.Status.ENCRYPTED)
	_apply(c, 2, RC.Status.ENCRYPTED)
	assert_eq(c.wheel.stacks_of(2, RC.Status.ENCRYPTED), 2, "ENCRYPTED on ENCRYPTED adds a stack")
	assert_false(_apply(c, 2, RC.Status.CORRUPTED))
	assert_false(_apply(c, 2, RC.Status.CORRUPTED))
	assert_true(_apply(c, 2, RC.Status.CORRUPTED), "the third lands")
	assert_eq(c.wheel.slice_stacks[2], {RC.Status.CORRUPTED: 1})


func test_parasite_applies_as_output_down_two() -> void:
	var c := _combatant()
	_apply(c, 3, RC.Status.PARASITE)
	assert_eq(c.wheel.slice_stacks[3], {RC.Status.OUTPUT_DOWN: _cfg.parasite_output_down_stacks}, "R8: no PARASITE is stored")


func test_has_status_true_for_any_stacks_ge_one() -> void:
	var w := _wheel()
	assert_false(w.has_status(0, RC.Status.CORRUPTED))
	w.add_stacks(0, RC.Status.CORRUPTED, 1, _cfg.status_stack_cap)
	assert_true(w.has_status(0, RC.Status.CORRUPTED))
	assert_true(w.has_any_status(0))
	assert_eq(w.count_status(RC.Status.CORRUPTED), 1)
	assert_eq(w.status_at(0), RC.Status.CORRUPTED)
	assert_eq(w.status_at(1), RC.Status.NONE)


func test_status_iteration_order_is_enum_sorted() -> void:
	var w := _wheel()
	for st in [RC.Status.OUTPUT_DOWN, RC.Status.ENCRYPTED, RC.Status.OVERCLOCKED, RC.Status.CORRUPTED]:
		w.add_stacks(5, st, 1, _cfg.status_stack_cap)
	assert_eq(w.statuses_at(5), [RC.Status.CORRUPTED, RC.Status.OVERCLOCKED, RC.Status.ENCRYPTED, RC.Status.OUTPUT_DOWN] as Array[int])
	assert_eq(w.status_at(5), RC.Status.CORRUPTED, "the one-badge view shows the first in enum order")


func _session_with(cards: Array[CardData]) -> CombatSession:
	var atk := CombatFixture.slice(&"st_atk6", RC.SliceType.SHIM, 6)
	var cls := CombatFixture.operative_class(&"st_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, atk]), cards)
	var dummy := CombatFixture.enemy(&"st_dummy", 300, CombatFixture.null_wheel())
	var custom: Array = [cls, dummy]
	custom.append_array(cards)
	var s := CombatSession.start(CombatFixture.resolver(custom), cls.id, [dummy.id], 31)
	CombatFixture.land(s.state.player, 1)
	return s


func test_overclocked_burnout_converts_to_corrupted_one_stack() -> void:
	var s := _session_with([])
	s.state.player.wheel.set_status(1, RC.Status.OVERCLOCKED, 3)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.player.wheel.slice_stacks[1], {RC.Status.CORRUPTED: 1}, "every OVERCLOCKED stack burns out into CORRUPTED x1")


func test_overclocked_stacks_do_not_multiply_beyond_one_point_five() -> void:
	for n in [1, 2, _cfg.status_stack_cap]:
		var s := _session_with([])
		s.state.player.wheel.set_status(1, RC.Status.OVERCLOCKED, n)
		var r := s.apply(CombatAction.end_turn())
		assert_eq(int(CombatFixture.events_of(r, "damage")[0]["amount"]), roundi(6 * _cfg.overclock_multiplier), "x%d still 1.5x" % n)


func test_flip_and_spin_carry_stacks_with_slice() -> void:
	var w := _wheel()
	w.slot_slice_ids[1] = &"a"
	w.add_stacks(1, RC.Status.OUTPUT_DOWN, 3, _cfg.status_stack_cap)
	w.add_stacks(1, RC.Status.CORRUPTED, 1, _cfg.status_stack_cap)
	w.flip()
	var j := WheelMath.mirrored_slot(1, w.slice_count)
	assert_eq(w.slot_slice_ids[j], &"a")
	assert_eq(w.slice_stacks[j], {RC.Status.OUTPUT_DOWN: 3, RC.Status.CORRUPTED: 1}, "the stacks travel with their slice")
	w.flip()
	assert_eq(w.slice_stacks[1], {RC.Status.OUTPUT_DOWN: 3, RC.Status.CORRUPTED: 1}, "flipping twice restores")
	w.rotation += 7  # a spin moves the wheel, never the stacks off their slot
	assert_eq(w.stacks_of(1, RC.Status.OUTPUT_DOWN), 3)


func test_satellite_slice_statuses_use_stack_form() -> void:
	var s := StatusSaveFixture.start()
	var sat: CombatantState = s.state.satellites_of(&"enemy_0")[0]
	var events: Array[Dictionary] = []
	s.resolver.fx.apply_status(sat, 0, RC.Status.OUTPUT_DOWN, events, 2)
	s.resolver.fx.apply_status(sat, 0, RC.Status.OUTPUT_DOWN, events, 1)
	assert_eq(sat.wheel.slice_stacks[0], {RC.Status.OUTPUT_DOWN: 3})
	var drone := StatusSaveFixture.dock_drone(s)
	s.resolver.fx.apply_status(drone, 1, RC.Status.CORRUPTED, events, 2)
	assert_eq(drone.wheel.slice_stacks[1], {RC.Status.CORRUPTED: 2}, "drones too")


func test_status_event_names_the_stack_count() -> void:
	var c := _combatant()
	var events: Array[Dictionary] = []
	_fx.apply_status(c, 0, RC.Status.OUTPUT_DOWN, events, 2)
	assert_eq(int(events[0]["stacks"]), 2)
