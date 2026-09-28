extends Node
## SaveService autoload: versioned JSON save/load (TECH_SPEC §8). M0 skeleton: it
## writes and reads dictionaries with a top-level "version" and runs the migrations
## table on load. Profile/campaign layouts arrive with their state classes (M2–M3).
##
## JSON caveat: numbers come back as floats and only integers up to 2^53 survive.
## Store 64-bit values (RNG states) as strings; see RngService.to_dict().

const SAVE_VERSION: int = 1
const SAVE_DIR := "user://saves"
const PROFILE_FILE := "profile.json"
const CAMPAIGN_FILE_FORMAT := "campaign_%s.json"

## A GUT run's own save folder under SAVE_DIR (by process id), as Settings keeps its own
## file: parallel test shards and test runs by other people on the machine never share a
## save slot or a profile (Test suite optimization, docs/TEST_SUITE.md).
const TEST_DIR_FORMAT := "gut_%d"

## from_version (int) -> Callable(data: Dictionary) -> Dictionary at from_version + 1.
var _migrations: Dictionary = {}
## Where saves live: SAVE_DIR, or this test run's own folder in it.
var save_dir: String = SAVE_DIR.path_join(TEST_DIR_FORMAT % OS.get_process_id()) if is_test_run() else SAVE_DIR


## Whether this process runs the GUT test suite (as Settings.is_test_run; SaveService loads
## before the Settings autoload).
static func is_test_run() -> bool:
	for a in OS.get_cmdline_args():
		if a.ends_with("gut_cmdln.gd"):
			return true
	return false


## A test run removes its own save folder when it ends.
func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and save_dir != SAVE_DIR:
		_remove_tree(save_dir)


static func _remove_tree(dir_path: String) -> void:
	var dir := DirAccess.open(dir_path)
	if dir == null:
		return
	for f in dir.get_files():
		DirAccess.remove_absolute(dir_path.path_join(f))
	for d in dir.get_directories():
		_remove_tree(dir_path.path_join(d))
	DirAccess.remove_absolute(dir_path)


## Path of the profile save file.
func profile_path() -> String:
	return save_dir.path_join(PROFILE_FILE)


## Path of a campaign save file.
func campaign_path(campaign_id: String) -> String:
	return save_dir.path_join(CAMPAIGN_FILE_FORMAT % campaign_id)


## Registers a migration that upgrades data from `from_version` to `from_version + 1`.
func register_migration(from_version: int, migration: Callable) -> void:
	_migrations[from_version] = migration


## Writes `data` as JSON at `path`, stamping the current SAVE_VERSION. Creates the
## directory when needed. Returns OK or the file error.
func save_dict(path: String, data: Dictionary) -> Error:
	var stamped := data.duplicate(true)
	stamped["version"] = SAVE_VERSION
	var dir_error := DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	if dir_error != OK:
		SignalBus.save_failed.emit(path, dir_error)
		return dir_error
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		var err := FileAccess.get_open_error()
		SignalBus.save_failed.emit(path, err)
		return err
	file.store_string(JSON.stringify(stamped, "\t"))
	file.close()
	SignalBus.save_completed.emit(path)
	return OK


## Reads and migrates the JSON dictionary at `path`. Returns an empty dictionary
## (and pushes an error) when the file is missing, unparsable or newer than this build.
func load_dict(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		push_error("SaveService: no file at %s." % path)
		return {}
	var text := FileAccess.get_file_as_string(path)
	var parsed: Variant = JSON.parse_string(text)
	if not (parsed is Dictionary):
		push_error("SaveService: %s is not a JSON object." % path)
		return {}
	return migrate(parsed)


## Applies registered migrations until `data` reaches SAVE_VERSION. Data without a
## version is treated as version 1. Returns {} when a step is missing or too new.
func migrate(data: Dictionary) -> Dictionary:
	var current := data.duplicate(true)
	var version := int(current.get("version", 1))
	if version > SAVE_VERSION:
		push_error("SaveService: save version %d is newer than supported %d." % [version, SAVE_VERSION])
		return {}
	while version < SAVE_VERSION:
		if not _migrations.has(version):
			push_error("SaveService: no migration from version %d." % version)
			return {}
		var step: Callable = _migrations[version]
		current = step.call(current)
		version += 1
		current["version"] = version
	current["version"] = SAVE_VERSION
	return current


## Campaign slot names with a save file, sorted.
func list_campaign_slots() -> PackedStringArray:
	var out := PackedStringArray()
	var dir := DirAccess.open(save_dir)
	if dir == null:
		return out
	dir.list_dir_begin()
	var name := dir.get_next()
	while name != "":
		if not dir.current_is_dir() and name.begins_with("campaign_") and name.ends_with(".json"):
			out.append(name.trim_prefix("campaign_").trim_suffix(".json"))
		name = dir.get_next()
	dir.list_dir_end()
	out.sort()
	return out


## True when a save exists at `path`.
func has_save(path: String) -> bool:
	return FileAccess.file_exists(path)


## Deletes the save at `path`. Returns OK when it did not exist.
func delete_save(path: String) -> Error:
	if not FileAccess.file_exists(path):
		return OK
	return DirAccess.remove_absolute(path)
