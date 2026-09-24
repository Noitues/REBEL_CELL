extends GutTest
## SaveService skeleton: versioned JSON round trip, migrations, and RNG stream state
## surviving a save (SaveService + RngService together).

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")
const RngServiceScript := preload("res://scripts/autoload/rng_service.gd")
const PATH := "user://test_saves/roundtrip.json"

var _saves: Node


func before_each() -> void:
	_saves = autofree(SaveServiceScript.new())


func after_each() -> void:
	_saves.delete_save(PATH)


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
	_saves.register_migration(0, func(d: Dictionary) -> Dictionary:
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
	assert_true(_saves.profile_path().begins_with(SaveServiceScript.SAVE_DIR))
	assert_true(_saves.campaign_path("solace").begins_with(SaveServiceScript.SAVE_DIR))
	assert_string_contains(_saves.campaign_path("solace"), "solace")


func test_delete_missing_save_is_ok() -> void:
	assert_eq(_saves.delete_save("user://test_saves/nope.json"), OK)


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
