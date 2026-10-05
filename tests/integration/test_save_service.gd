extends GutTest
## SaveService skeleton: versioned JSON round trip, migrations, and RNG stream state
## surviving a save (SaveService + RngService together).

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")
const RngServiceScript := preload("res://scripts/autoload/rng_service.gd")
## This run's own file (by process id): test runs in parallel never share it.
var PATH: String = "user://test_saves_%d/roundtrip.json" % OS.get_process_id()

var _saves: Node


func before_each() -> void:
	_saves = autofree(SaveServiceScript.new())


func after_each() -> void:
	_saves.delete_save(PATH)
	DirAccess.remove_absolute(PATH.get_base_dir())


func _draw(rng: RandomNumberGenerator, count: int) -> PackedInt64Array:
	var out := PackedInt64Array()
	for i in count:
		out.append(rng.randi())
	return out


func test_round_trip_preserves_data_and_stamps_version() -> void:
	var data := {"name": "cell", "heat": 42, "tags": ["a", "b"], "nested": {"x": 1.5}}
	assert_eq(_saves.save_dict(PATH, data), OK)
	assert_true(_saves.has_save(PATH))
	var loaded: Dictionary = _saves.load_dict(PATH)
	assert_eq(int(loaded["version"]), SaveServiceScript.SAVE_VERSION)
	assert_eq(loaded["name"], "cell")
	assert_eq(int(loaded["heat"]), 42)
	assert_eq(loaded["tags"], ["a", "b"])
	assert_eq(loaded["nested"]["x"], 1.5)


func test_save_does_not_mutate_the_input() -> void:
	var data := {"k": 1}
	_saves.save_dict(PATH, data)
	assert_false(data.has("version"))


func test_migration_runs_for_older_versions() -> void:
	# The table ships empty (ART-0, no compatibility); the mechanism still runs registered steps.
	for v in SaveServiceScript.SAVE_VERSION:
		_saves.register_migration(v, func(d: Dictionary) -> Dictionary:
			d["migrated"] = true
			return d)
	var out: Dictionary = _saves.migrate({"version": 0, "k": 1})
	assert_true(out.get("migrated", false))
	assert_eq(int(out["version"]), SaveServiceScript.SAVE_VERSION)
	assert_eq(int(out["k"]), 1)


func test_current_version_needs_no_migration() -> void:
	var out: Dictionary = _saves.migrate({"version": SaveServiceScript.SAVE_VERSION, "k": 1})
	assert_eq(int(out["k"]), 1)


func test_paths_live_under_the_save_dir() -> void:
	assert_true(_saves.profile_path().begins_with(_saves.save_dir))
	assert_true(_saves.campaign_path("solace").begins_with(_saves.save_dir))
	assert_string_contains(_saves.campaign_path("solace"), "solace")


func test_delete_missing_save_is_ok() -> void:
	assert_eq(_saves.delete_save(PATH.get_base_dir().path_join("nope.json")), OK)


func test_a_test_run_keeps_its_saves_in_its_own_folder() -> void:
	assert_true(SaveServiceScript.is_test_run(), "this is a GUT run")
	var own := _export_root().path_join(SaveServiceScript.TEST_DIR_FORMAT % OS.get_process_id())
	assert_eq(_saves.save_dir, own, "saves live in this run's own folder")
	assert_eq(SaveService.save_dir, own, "the autoload too")
	assert_true(_saves.profile_path().begins_with(own + "/"))
	assert_true(_saves.campaign_path("gut_test").begins_with(own + "/"), "a test slot is this run's alone")
	RunManager.save_slot = "gut_isolation"
	assert_true(RunManager.save_path().begins_with(own + "/"))
	assert_true(RunManager.profile_path().begins_with(own + "/"), "and so is its private profile")
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	# Another process's slot (a file straight in the export folder or in another run's folder) is not
	# listed, and this run's own is.
	var stranger := _export_root().path_join("campaign_gut_stranger_%d.json" % OS.get_process_id())
	assert_eq(_saves.save_dict(stranger, {"campaign": {}}), OK)
	assert_eq(_saves.save_dict(_saves.campaign_path("gut_mine"), {"campaign": {}}), OK)
	var slots: PackedStringArray = _saves.list_campaign_slots()
	assert_false(slots.has("gut_stranger_%d" % OS.get_process_id()), "another run's slot is not listed")
	assert_true(slots.has("gut_mine"), "this run's slot is")
	_saves.delete_save(stranger)
	_saves.delete_save(_saves.campaign_path("gut_mine"))


func test_a_test_runs_folder_is_removed_when_its_save_service_ends() -> void:
	var service: Node = SaveServiceScript.new()
	service.save_dir = _export_root().path_join("gut_%d_cleanup" % OS.get_process_id())
	assert_eq(service.save_dict(service.campaign_path("gut_x"), {"campaign": {}}), OK)
	var dir: String = service.save_dir
	assert_true(DirAccess.dir_exists_absolute(dir))
	service.free()
	assert_false(DirAccess.dir_exists_absolute(dir), "the folder went with the run")


func test_rng_stream_state_survives_save_and_load() -> void:
	var rng: Node = autofree(RngServiceScript.new())
	rng.seed_campaign(777)
	for stream_name in RngServiceScript.STREAM_NAMES:
		_draw(rng.get_stream(stream_name), 5)
	assert_eq(_saves.save_dict(PATH, {"rng": rng.to_dict()}), OK)
	var restored: Node = autofree(RngServiceScript.new())
	restored.from_dict(_saves.load_dict(PATH)["rng"])
	for stream_name in RngServiceScript.STREAM_NAMES:
		assert_eq(_draw(restored.get_stream(stream_name), 32), _draw(rng.get_stream(stream_name), 32),
			"stream %s" % stream_name)


## The export save folder (a test run's own folder sits in it).
func _export_root() -> String:
	return CombatFixture.config().save_dir_export
