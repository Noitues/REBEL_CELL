extends GutTest
## Plan 2 N8: save v3 (×N status stacks) and the v2 -> v3 migration. The v2 fixtures
## (tests/fixtures/saves/v2/) were written by the v2 build before the change, with the HP
## every combatant had after one End Turn there; a migrated fixture must resolve to the same
## HP (PARASITE -> OUTPUT_DOWN x2 keeps the half output). A broken v3 is refused, not a crash.

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")

var _saves: Node
var _cfg: CampaignConfigData
var _dir: String = "user://test_n8_saves_%d" % OS.get_process_id()


func before_each() -> void:
	_saves = autofree(SaveServiceScript.new())
	_cfg = CombatFixture.config()


func after_each() -> void:
	if not DirAccess.dir_exists_absolute(_dir):
		return
	for f in DirAccess.get_files_at(_dir):
		DirAccess.remove_absolute(_dir.path_join(f))
	DirAccess.remove_absolute(_dir)


func _fixture(fixture_name: String) -> Dictionary:
	var text := FileAccess.get_file_as_string(StatusSaveFixture.FIXTURE_DIR + fixture_name + ".json")
	return JSON.parse_string(text)


func _migrated(fixture_name: String) -> Dictionary:
	var d: Dictionary = _saves.migrate(_fixture(fixture_name))
	assert_eq(_saves.last_error, "", "%s migrates" % fixture_name)
	return d


func _session(file: Dictionary) -> CombatSession:
	return CombatSession.from_dict(StatusSaveFixture.resolver(), StatusSaveFixture.session_dict(file))


## Every wheel dictionary in `v` (any depth).
func _wheels(v: Variant, out: Array = []) -> Array:
	if v is Dictionary:
		if (v as Dictionary).has("slot_slice_ids"):
			out.append(v)
		for k in v:
			_wheels(v[k], out)
	elif v is Array:
		for item in v:
			_wheels(item, out)
	return out


func test_v2_save_with_no_statuses_migrates_to_v3() -> void:
	var d := _migrated("v2_empty")
	assert_eq(int(d["version"]), SaveServiceScript.SAVE_VERSION, "v2 -> v3 -> v4 (N12 adds no v3 change)")
	for w in _wheels(d):
		assert_false(w.has("slice_statuses"))
		for slot in w["slice_stacks"]:
			assert_eq(slot, {}, "no stacks")


func test_v2_int_status_migrates_to_one_stack() -> void:
	var s := _session(_migrated("v2_corrupted_overclocked"))
	assert_eq(s.state.player.wheel.slice_stacks[1], {RC.Status.OVERCLOCKED: 1})
	assert_eq(s.state.player.wheel.slice_stacks[3], {RC.Status.CORRUPTED: 1})
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.slice_stacks[0], {RC.Status.CORRUPTED: 1})


func test_v2_parasite_migrates_to_output_down_two() -> void:
	assert_eq(RC.Status.PARASITE, 4, "the v2 int stays valid for the migration")
	var s := _session(_migrated("v2_parasite_slice"))
	var two := _cfg.parasite_output_down_stacks
	assert_eq(two, 2)
	assert_eq(s.state.player.wheel.slice_stacks[1], {RC.Status.OUTPUT_DOWN: two})
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.slice_stacks[0], {RC.Status.OUTPUT_DOWN: two})
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.slice_stacks[4], {RC.Status.ENCRYPTED: 1})


func test_v2_status_none_migrates_to_empty() -> void:
	var d: Dictionary = SaveMigration.v2_to_v3({"wheel": {"slot_slice_ids": ["a", "b"], "slice_statuses": [0, 1]}}, 2)
	assert_eq(d["wheel"]["slice_stacks"], [{}, {"1": 1}], "NONE is {} (never {NONE: 1})")


func test_migration_covers_player_enemy_and_satellite_wheels() -> void:
	var s := _session(_migrated("v2_satellite_status"))
	var sat: CombatantState = s.state.satellites_of(&"enemy_0")[0]
	assert_eq(sat.wheel.slice_stacks, [{RC.Status.OUTPUT_DOWN: 2}, {RC.Status.ENCRYPTED: 1}] as Array[Dictionary])
	assert_eq(s.state.player.wheel.slice_stacks.size(), 6)
	assert_eq(s.state.get_combatant(&"enemy_0").wheel.slice_stacks.size(), 6)


func test_migration_covers_mid_combat_checkpoint_stack() -> void:
	var s := _session(_migrated("v2_midfight_checkpoint"))
	assert_true(s.can_rewind(), "the saved fight had one action since the checkpoint")
	assert_eq(s.checkpoint_state.get_combatant(&"enemy_0").wheel.slice_stacks[0], {RC.Status.OUTPUT_DOWN: 2}, "the checkpoint is migrated too")
	assert_eq(s.state.player.wheel.slice_stacks[1], {RC.Status.OVERCLOCKED: 1})
	var r := s.rewind()
	assert_eq(r.error, "", "undo after load works")
	assert_eq(s.state.player.wheel.slice_stacks[1], {}, "the OVERCLOCKED play is undone")
	assert_eq(s.state.player.wheel.slice_stacks[2], {RC.Status.CORRUPTED: 1})


func test_migration_covers_drones_and_parasite_drone_docks() -> void:
	var s := _session(_migrated("v2_botnet_drones"))
	assert_eq(s.state.drones.size(), 1)
	assert_eq(s.state.drones[0].wheel.slice_stacks[0], {RC.Status.OUTPUT_DOWN: 2})
	assert_eq(s.state.drones[0].wheel.slice_stacks[1], {RC.Status.CORRUPTED: 1})
	assert_eq(s.state.player.wheel.slice_stacks[1], {RC.Status.OUTPUT_DOWN: 2})


func test_migrated_state_hash_equals_fresh_equivalent() -> void:
	var loaded := _session(_migrated("v2_parasite_slice"))
	var fresh := StatusSaveFixture.start()
	fresh.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 2)
	var e := fresh.state.get_combatant(&"enemy_0")
	e.wheel.set_status(0, RC.Status.OUTPUT_DOWN, 2)
	e.wheel.set_status(4, RC.Status.ENCRYPTED, 1)
	assert_eq(loaded.state.state_hash(), fresh.state.state_hash())


func test_migration_is_idempotent() -> void:
	for f in StatusSaveFixture.FIXTURES:
		var once := SaveMigration.v2_to_v3(_fixture(f), 2)
		assert_eq(SaveMigration.v2_to_v3(once, 2), once, f)
	var v3: Dictionary = _migrated("v2_parasite_slice")
	var text := JSON.stringify(v3, "\t")
	var again: Dictionary = _saves.migrate(JSON.parse_string(text))
	assert_eq(JSON.parse_string(JSON.stringify(again)), JSON.parse_string(text), "a v3 save comes back unchanged")


func test_v3_roundtrip_save_load_equality() -> void:
	var s := StatusSaveFixture.start()
	s.state.player.wheel.set_status(1, RC.Status.OUTPUT_DOWN, 3)
	s.state.player.wheel.add_stacks(1, RC.Status.CORRUPTED, 2, _cfg.status_stack_cap)
	var path := _dir.path_join("v3.json")
	assert_eq(_saves.save_dict(path, s.to_dict()), OK)
	var back := CombatSession.from_dict(StatusSaveFixture.resolver(), _saves.load_dict(path))
	assert_eq(back.state.state_hash(), s.state.state_hash())
	assert_eq(back.state.player.wheel.slice_stacks[1], {RC.Status.CORRUPTED: 2, RC.Status.OUTPUT_DOWN: 3})


func test_v3_json_keys_are_strings_and_reload_as_ints() -> void:
	var w := StatusSaveFixture.start().state.player.wheel
	w.set_status(2, RC.Status.OUTPUT_DOWN, 2)
	var d := w.to_dict()
	assert_eq(d["slice_stacks"][2], {str(RC.Status.OUTPUT_DOWN): 2}, "String keys in the file")
	var back := WheelState.from_dict(JSON.parse_string(JSON.stringify(d)))
	assert_eq(back.slice_stacks[2], {RC.Status.OUTPUT_DOWN: 2})
	assert_true(back.slice_stacks[2].keys()[0] is int, "int keys at run time")


func test_future_version_5_is_rejected_with_named_reason() -> void:
	assert_eq(_saves.migrate({"version": 5}), {})
	assert_eq(_saves.last_error, "save_version_too_new")
	assert_push_error("save_version_too_new")


func _v3_with(slot: Dictionary) -> Dictionary:
	return {"version": 3, "run": {"combat": {"state": {"player": {"wheel": {"slot_slice_ids": ["a"], "slice_stacks": [slot]}}}}}}


func test_corrupt_v3_negative_stacks_rejected() -> void:
	assert_eq(_saves.migrate(_v3_with({"5": -1})), {})
	assert_eq(_saves.last_error, "invalid_stack_count")
	assert_eq(_saves.migrate(_v3_with({"5": 0})), {})
	assert_eq(_saves.migrate(_v3_with({"5": 1.5})), {})
	assert_eq(_saves.last_error, "invalid_stack_count")
	assert_push_error_count(3, "three refusals, each named")


func test_corrupt_v3_unknown_status_id_rejected() -> void:
	for bad in ["99", "0", "4", "x"]:
		assert_eq(_saves.migrate(_v3_with({bad: 1})), {}, bad)
		assert_eq(_saves.last_error, "unknown_status", bad)
	assert_eq(_saves.migrate({"version": 3, "w": {"slice_stacks": [3]}}), {})
	assert_eq(_saves.last_error, "invalid_stacks_shape")
	assert_push_error_count(5, "five refusals, each named")


func test_failed_migration_leaves_original_file_untouched() -> void:
	assert_eq(DirAccess.make_dir_recursive_absolute(_dir), OK)
	var path := _dir.path_join("broken.json")
	var text := JSON.stringify(_v3_with({"5": -3}))
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(text)
	f.close()
	assert_eq(_saves.load_dict(path), {}, "refused")
	assert_eq(FileAccess.get_file_as_string(path), text, "the file is never rewritten by a load")
	assert_push_error("invalid_stack_count")


func test_resume_after_migration_replays_remaining_inputs_equal() -> void:
	for f in StatusSaveFixture.FIXTURES:
		var file := _migrated(f)
		var s := _session(file)
		var r := s.apply(CombatAction.end_turn())
		assert_true(r.ok(), "%s: %s" % [f, r.error])
		var want: Dictionary = file["expect_end_turn"]
		var got := StatusSaveFixture.hp_by_id(s.state)
		for id in want:
			assert_eq(int(got.get(id, -1)), int(want[id]), "%s: %s HP after End Turn equals the v2 build's" % [f, id])
