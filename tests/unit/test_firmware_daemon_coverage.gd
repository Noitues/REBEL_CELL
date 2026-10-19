extends GutTest
## Per-id coverage (M2 acceptance "every card, Firmware and Daemon has at least one unit test"):
## every Firmware and Daemon id in the registry is named in COVERED with the unit test that exercises it,
## and that test must exist and mention the id. Ids that had no behaviour test get theirs below.

const SELF := "res://tests/unit/test_firmware_daemon_coverage.gd"
const FW := "res://tests/unit/test_firmware.gd"
const POOLS := "res://tests/unit/test_pools.gd"
const DAEMONS := "res://tests/unit/test_daemons.gd"
const DRONES := "res://tests/unit/test_drones.gd"
const NETRUN := "res://tests/integration/test_netrun.gd"

## id -> [script, test function].
const COVERED := {
	# Firmware
	&"barbed_wire": [SELF, "test_barbed_wire_defrag_also_hits_the_target_for_2"],
	&"bulkhead": [POOLS, "test_new_firmware_hooks"],
	&"burner": [FW, "test_burner_is_permanently_overclocked_and_adds_heat"],
	&"coolant_loop": [SELF, "test_coolant_loop_lowers_heat_on_a_perfect_once_per_combat"],
	&"counterstrike": [SELF, "test_counterstrike_detour_also_hits_the_target_for_4"],
	&"hardened": [FW, "test_hardened_is_permanent_encryption"],
	&"leech": [FW, "test_leech_restores_1_ram_on_good_or_better"],
	&"mirror": [FW, "test_mirror_copies_the_neighbour_on_the_side_you_landed"],
	&"nanite_mesh": [SELF, "test_nanite_mesh_hotfix_output_is_boosted_and_cleansed"],
	&"overvolt": [SELF, "test_overvolt_boosts_shim_and_overflow_by_25_percent"],
	&"patch_plus": [FW, "test_patch_plus_adds_50_percent_output"],
	&"power_cell": [SELF, "test_power_cell_sandbox_restores_1_ram"],
	&"recycler": [POOLS, "test_new_firmware_hooks"],
	&"shunt": [FW, "test_shunt_resolves_the_neighbour_instead_at_1_5x"],
	&"siphon": [POOLS, "test_new_firmware_hooks"],
	&"skimmer": [SELF, "test_skimmer_pays_3_cycles_on_a_perfect_twice_per_combat"],
	&"static_coat": [SELF, "test_static_coat_defrag_also_grants_2_shield"],
	&"tracer": [SELF, "test_tracer_strips_resistance_on_a_perfect_only"],
	# Daemons
	&"adrenal_loop": [SELF, "test_adrenal_loop_heals_2_on_each_perfect"],
	&"botnet_seed": [DRONES, "test_botnet_seed_sprouts_one_hp_drones_on_perfects_max_two"],
	&"bounty_code": [POOLS, "test_combat_end_daemons_pay_out_after_a_won_fight"],
	&"cascade": [SELF, "test_cascade_gives_1_ram_on_two_perfects_in_a_row"],
	&"clean_signal": [DAEMONS, "test_clean_signal_fires_on_the_third_consecutive_perfect"],
	&"cold_exit": [NETRUN, "test_cold_exit_and_scrubber_run_level_daemons"],
	&"fail_forward": [SELF, "test_fail_forward_null_slice_restores_2_ram"],
	&"fault_tolerance": [DAEMONS, "test_fault_tolerance_makes_the_null_slice_hit_for_3"],
	&"feedback_loop": [SELF, "test_feedback_loop_every_card_hits_every_enemy_for_1"],
	&"field_medic": [POOLS, "test_combat_end_daemons_pay_out_after_a_won_fight"],
	&"idle_armor": [SELF, "test_idle_armor_gives_2_block_each_turn_start"],
	&"kernel_sync": [DAEMONS, "test_kernel_sync_adds_1_damage_per_perfect"],
	&"linked_bus": [DRONES, "test_linked_bus_moves_your_wheel_with_enemy_nudges"],
	&"log_wiper": [POOLS, "test_rack_and_netrun_daemons"],
	&"rack_skimmer": [POOLS, "test_rack_and_netrun_daemons"],
	&"salvager": [POOLS, "test_combat_end_daemons_pay_out_after_a_won_fight"],
	&"scrubber": [NETRUN, "test_cold_exit_and_scrubber_run_level_daemons"],
	&"shield_cache": [POOLS, "test_new_combat_daemons"],
	&"static_field": [SELF, "test_static_field_hits_every_enemy_for_1_each_turn_start"],
	&"stolen_intent": [DRONES, "test_stolen_intent_swaps_a_null_for_the_enemys_slice_once"],
	&"tuning_fork": [SELF, "test_tuning_fork_every_nudge_gives_1_block"],
	&"twin_pointer": [DRONES, "test_twin_pointer_reads_the_wheel_at_the_bottom_and_halves_ram"],
	&"warm_boot": [POOLS, "test_new_combat_daemons"],
	&"zero_day": [DAEMONS, "test_zero_day_turns_a_perfect_null_into_a_3x_crit"],
}

var _lookup: ContentLookup


func before_all() -> void:
	_lookup = GridFixture.lookup()


# --- the coverage check ------------------------------------------------------------------------------------------

func test_every_firmware_and_daemon_id_names_a_unit_test_that_exists() -> void:
	var ids: Array[StringName] = []
	ids.append_array(_lookup.ids_of_class(&"FirmwareData"))
	ids.append_array(_lookup.ids_of_class(&"DaemonData"))
	assert_gte(ids.size(), 42, "the registry has the 18 Firmware and 24 Daemons")
	for id in ids:
		assert_true(COVERED.has(id), "%s has no coverage entry: add a unit test and list it in COVERED" % id)
		if not COVERED.has(id):
			continue
		var entry: Array = COVERED[id]
		var src := FileAccess.get_file_as_string(entry[0])
		assert_ne(src, "", "%s: %s is readable" % [id, entry[0]])
		assert_true(src.contains("func %s(" % entry[1]), "%s: %s::%s exists" % [id, entry[0], entry[1]])
		var body := _function_body(src, entry[1])
		assert_true(body.contains(String(id)), "%s: %s::%s mentions the id" % [id, entry[0], entry[1]])
	for id in COVERED:
		assert_true(ids.has(id), "COVERED lists %s, which is not a Firmware or Daemon in the registry" % id)


## The text of `func name(` up to the next top-level `func`.
func _function_body(src: String, name: String) -> String:
	var start := src.find("func %s(" % name)
	if start < 0:
		return ""
	var end := src.find("\nfunc ", start + 1)
	return src.substr(start, (end if end >= 0 else src.length()) - start)


# --- Firmware ---------------------------------------------------------------------------------------------------

func _slice(id: String, type: int, output: int, rule: int = RC.TargetRule.POINTER) -> SliceData:
	return CombatFixture.slice(StringName(id), type, output, rule)


## A wheel [Shim 6 x5] with slot 1 replaced by `middle` and `firmware_id` socketed there; the enemy has `resist` and 300 HP.
func _fw_session(firmware_id: StringName, middle: SliceData, resist: int = 0) -> CombatSession:
	var shim := _slice("cv_shim", RC.SliceType.SHIM, 6)
	var firmware := []
	firmware.resize(6)
	firmware[1] = ContentRegistry.get_content(firmware_id) as FirmwareData
	var deck: Array[CardData] = [CombatFixture.card(&"cv_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"cv_class", 60, CombatFixture.wheel([shim, middle, shim, shim, shim, shim], null, [0], 0, null, firmware), deck)
	var dummy := CombatFixture.enemy(&"cv_dummy", 300, CombatFixture.null_wheel(resist))
	var s := CombatSession.start(CombatFixture.resolver([cls, dummy]), cls.id, [dummy.id], 2)
	assert_eq(cls.starting_wheel.validate().size(), 0, "%s fits slot 1" % firmware_id)
	return s


func _land_and_end(s: CombatSession, offset: int = 0) -> CombatResult:
	CombatFixture.land(s.state.player, 1, offset)
	return s.apply(CombatAction.end_turn())


func _amounts(r: CombatResult, type: String) -> Array:
	var out := []
	for e in CombatFixture.events_of(r, type):
		out.append(e["amount"])
	return out


func test_barbed_wire_defrag_also_hits_the_target_for_2() -> void:
	var s := _fw_session(&"barbed_wire", _slice("cv_def", RC.SliceType.DEFRAG, 5, RC.TargetRule.SELF))
	var r := _land_and_end(s, 1)
	assert_eq(_amounts(r, "damage"), [2], "barbed_wire: 2 damage to the pointer target")
	assert_eq(_amounts(r, "block"), [5], "the Defrag itself still blocks")
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 298)


func test_static_coat_defrag_also_grants_2_shield() -> void:
	var s := _fw_session(&"static_coat", _slice("cv_def", RC.SliceType.DEFRAG, 5, RC.TargetRule.SELF))
	_land_and_end(s, 1)
	assert_eq(s.state.player.shield, 2, "static_coat: +2 shield")


func test_counterstrike_detour_also_hits_the_target_for_4() -> void:
	var s := _fw_session(&"counterstrike", _slice("cv_detour", RC.SliceType.DETOUR, 0, RC.TargetRule.SELF))
	var r := _land_and_end(s, 1)
	assert_true(_amounts(r, "damage").has(4), "counterstrike: 4 damage to the pointer target (%s)" % [_amounts(r, "damage")])


func test_power_cell_sandbox_restores_1_ram() -> void:
	var s := _fw_session(&"power_cell", _slice("cv_sandbox", RC.SliceType.SANDBOX, 0, RC.TargetRule.SELF))
	var plain := _fw_session(&"power_cell", _slice("cv_sandbox", RC.SliceType.SANDBOX, 0, RC.TargetRule.SELF))
	_land_and_end(s, 1)
	CombatFixture.land(plain.state.player, 4)  # the same turn on a plain Shim: no Power Cell
	plain.apply(CombatAction.end_turn())
	assert_eq(s.state.ram, plain.state.ram + 1, "power_cell: +1 RAM on a Sandbox slice")


func test_nanite_mesh_hotfix_output_is_boosted_and_cleansed() -> void:
	var s := _fw_session(&"nanite_mesh", _slice("cv_hotfix", RC.SliceType.HOTFIX, 4, RC.TargetRule.SELF))
	s.state.player.wheel.set_status(1, RC.Status.CORRUPTED)
	var r := _land_and_end(s, 1)
	assert_eq(s.state.player.wheel.status_at(1), RC.Status.NONE, "nanite_mesh: the slice cleanses itself")
	var plain := _fw_session(&"nanite_mesh", _slice("cv_hotfix", RC.SliceType.HOTFIX, 4, RC.TargetRule.SELF))
	assert_gte(r.events.size(), _land_and_end(plain, 1).events.size(), "nanite_mesh: the cleanse never loses events (N9: a corrupted slice no longer bites)")


func test_overvolt_boosts_shim_and_overflow_by_25_percent() -> void:
	var s := _fw_session(&"overvolt", _slice("cv_shim_mid", RC.SliceType.SHIM, 8))
	assert_eq(_amounts(_land_and_end(s, 1), "damage"), [10], "overvolt: Shim 8 x 1.25")
	s = _fw_session(&"overvolt", _slice("cv_over", RC.SliceType.OVERFLOW, 12))
	assert_eq(_amounts(_land_and_end(s, 1), "damage"), [15], "overvolt: Overflow 12 x 1.25")


func test_coolant_loop_lowers_heat_on_a_perfect_once_per_combat() -> void:
	var s := _fw_session(&"coolant_loop", _slice("cv_shim_mid", RC.SliceType.SHIM, 6))
	var heat := []
	var r := _land_and_end(s, 0)
	for e in CombatFixture.events_of(r, "campaign_effect"):
		heat.append(e["amount"])
	assert_eq(heat, [-1], "coolant_loop: -1 Heat on a Perfect")
	r = _land_and_end(s, 0)
	assert_eq(CombatFixture.events_of(r, "campaign_effect").size(), 0, "once per combat")
	s = _fw_session(&"coolant_loop", _slice("cv_shim_mid", RC.SliceType.SHIM, 6))
	assert_eq(CombatFixture.events_of(_land_and_end(s, 1), "campaign_effect").size(), 0, "a Good landing does nothing")


func test_skimmer_pays_3_cycles_on_a_perfect_twice_per_combat() -> void:
	var s := _fw_session(&"skimmer", _slice("cv_shim_mid", RC.SliceType.SHIM, 6))
	var paid := []
	for turn in 3:
		var r := _land_and_end(s, 0)
		for e in CombatFixture.events_of(r, "campaign_effect"):
			paid.append(e["amount"])
	assert_eq(paid, [3, 3], "skimmer: +3 Cycles on the first two Perfects only")
	s = _fw_session(&"skimmer", _slice("cv_shim_mid", RC.SliceType.SHIM, 6))
	assert_eq(CombatFixture.events_of(_land_and_end(s, 1), "campaign_effect").size(), 0, "not on a Good landing")


func test_tracer_strips_resistance_on_a_perfect_only() -> void:
	var s := _fw_session(&"tracer", _slice("cv_shim_mid", RC.SliceType.SHIM, 6), 3)
	assert_eq(_amounts(_land_and_end(s, 1), "resistance"), [], "tracer: nothing on a Good landing")
	assert_eq(_amounts(_land_and_end(s, 0), "resistance"), [-1], "tracer: -1 resistance on a Perfect")


# --- Daemons ----------------------------------------------------------------------------------------------------

func _daemon_session(daemon_id: StringName, enemies: int = 1) -> CombatSession:
	var shim := _slice("cd_shim", RC.SliceType.SHIM, 6)
	var nul := _slice("cd_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var deck: Array[CardData] = [CombatFixture.card(&"cd_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"cd_class", 60, CombatFixture.wheel([shim, shim, shim, shim, shim, nul]), deck)
	var dummy := CombatFixture.enemy(&"cd_dummy", 300, CombatFixture.null_wheel())
	var ids: Array[StringName] = []
	for i in enemies:
		ids.append(dummy.id)
	return CombatSession.start(CombatFixture.resolver([cls, dummy]), cls.id, ids, 6, &"", 0, {"daemon_ids": [String(daemon_id)]})


func test_adrenal_loop_heals_2_on_each_perfect() -> void:
	var s := _daemon_session(&"adrenal_loop")
	s.state.player.hp = 30
	CombatFixture.land(s.state.player, 1, 0)
	var r := s.apply(CombatAction.end_turn())
	assert_true(_amounts(r, "heal").has(2), "adrenal_loop: +2 on a Perfect")
	var after := s.state.player.hp
	CombatFixture.land(s.state.player, 1, 1)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.player.hp, after, "no heal on a Good landing")


func test_cascade_gives_1_ram_on_two_perfects_in_a_row() -> void:
	var s := _daemon_session(&"cascade")
	var first := _perfect_turn_ram_events(s)
	assert_eq(first, 0, "cascade: nothing after one Perfect")
	assert_eq(_perfect_turn_ram_events(s), 1, "cascade: +1 RAM on the second Perfect in a row")


## Plays an end_turn on a Perfect and returns the +1 RAM events from the daemon (source cascade).
func _perfect_turn_ram_events(s: CombatSession) -> int:
	CombatFixture.land(s.state.player, 1, 0)
	var r := s.apply(CombatAction.end_turn())
	var n := 0
	for e in CombatFixture.events_of(r, "ram"):
		if int(e["amount"]) == 1:  # regen is 4 a turn; a lone +1 is the Daemon
			n += 1
	return n


func test_fail_forward_null_slice_restores_2_ram() -> void:
	var s := _daemon_session(&"fail_forward")
	CombatFixture.land(s.state.player, 5)
	var r := s.apply(CombatAction.end_turn())
	var got := 0
	for e in CombatFixture.events_of(r, "ram"):
		if int(e["amount"]) == 2:  # regen is 4 a turn; a lone +2 is the Daemon
			got += 2
	assert_eq(got, 2, "fail_forward: +2 RAM when the NULL slice resolves")
	s = _daemon_session(&"fail_forward")
	CombatFixture.land(s.state.player, 1)
	for e in CombatFixture.events_of(s.apply(CombatAction.end_turn()), "ram"):
		assert_ne(e["amount"], 2, "not on a plain slice")


func test_feedback_loop_every_card_hits_every_enemy_for_1() -> void:
	var s := _daemon_session(&"feedback_loop", 2)
	var r := s.apply(CombatAction.play_card(0))
	assert_eq(r.error, "")
	var hits := 0
	for e in CombatFixture.events_of(r, "damage"):
		assert_eq(e["amount"], 1)
		hits += 1
	assert_eq(hits, 2, "feedback_loop: one point to each of the 2 enemies")
	assert_eq(s.state.get_combatant(&"enemy_0").hp, 299)
	assert_eq(s.state.get_combatant(&"enemy_1").hp, 299)


func test_idle_armor_gives_2_block_each_turn_start() -> void:
	var s := _daemon_session(&"idle_armor")
	var r := s.apply(CombatAction.end_turn())
	assert_true(_amounts(r, "block").has(2), "idle_armor: +2 block at the start of the next turn")
	assert_eq(s.state.player.block, 2)


func test_static_field_hits_every_enemy_for_1_each_turn_start() -> void:
	var s := _daemon_session(&"static_field", 2)
	var r := s.apply(CombatAction.end_turn())
	var ones := 0
	for e in CombatFixture.events_of(r, "damage"):
		if e.get("source_id", &"") == &"static_field" and e["amount"] == 1:
			ones += 1
	assert_eq(ones, 2, "static_field: 1 damage to each enemy at turn start")


func test_tuning_fork_every_nudge_gives_1_block() -> void:
	var s := _daemon_session(&"tuning_fork")
	var r := s.apply(CombatAction.nudge(&"player", 1))
	assert_eq(r.error, "")
	assert_true(_amounts(r, "block").has(1), "tuning_fork: +1 block per nudge")
	assert_eq(s.state.player.block, 1)
	s.apply(CombatAction.nudge(&"player", -1))
	assert_eq(s.state.player.block, 2, "each nudge pays")
