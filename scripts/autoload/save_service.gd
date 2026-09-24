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

## from_version (int) -> Callable(data: Dictionary) -> Dictionary at from_version + 1.
var _migrations: Dictionary = {}


## Path of the profile save file.
func profile_path() -> String:
	return SAVE_DIR.path_join(PROFILE_FILE)


## Path of a campaign save file.
func campaign_path(campaign_id: String) -> String:
	return SAVE_DIR.path_join(CAMPAIGN_FILE_FORMAT % campaign_id)


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


## True when a save exists at `path`.
func has_save(path: String) -> bool:
	return FileAccess.file_exists(path)


## Deletes the save at `path`. Returns OK when it did not exist.
func delete_save(path: String) -> Error:
	if not FileAccess.file_exists(path):
		return OK
	return DirAccess.remove_absolute(path)
