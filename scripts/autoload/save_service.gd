extends Node
## SaveService autoload: versioned JSON save/load (TECH_SPEC §8). It writes and reads
## dictionaries with a top-level "version"; a file of another version is refused (the
## "can't load" path: an empty dictionary). There is no save or replay compatibility
## (DECISIONS 2026-10-05, ruling 5): the migrations table stays empty.
##
## Where saves live (ART-0 S0, DECISIONS "Art direction — ART-0 names pass, part 1 + saves
## folder"): a run from source writes to the project's own folder that git ignores
## (CampaignConfigData.save_dir_source, `res://saves`), with a `.gdignore` written when the
## folder is made so Godot never imports it; an exported build keeps
## CampaignConfigData.save_dir_export (`user://saves`). Finished combats are written as
## replays (CombatReplay) to the replay folder inside it, on source runs only.
##
## JSON caveat: numbers come back as floats and only integers up to 2^53 survive.
## Store 64-bit values (RNG states) as strings; see RngService.to_dict().

## ART-0 S0: bumped from 1 (names follow the display words; old saves are not read).
const SAVE_VERSION: int = 2
const PROFILE_FILE := "profile.json"
const CAMPAIGN_FILE_FORMAT := "campaign_%s.json"
## A replay's file name: the wall-clock time it was written (ms, zero-padded so the names
## sort oldest first; ART-0 audit B4) and its seed, so two fights never share one.
const REPLAY_FILE_FORMAT := "replay_%013d_%s.json"
const REPLAY_PREFIX := "replay_"
const REPLAY_EXT := ".json"
## Godot's marker that keeps a folder out of the import (a fixed engine file name).
const GDIGNORE_FILE := ".gdignore"
## The config the save locations come from.
const CONFIG_PATH := preload("res://scripts/autoload/content_registry.gd").CONFIG_PATH

## A GUT run's own save folder under the export folder (by process id), as Settings keeps
## its own file: parallel test shards and test runs by other people on the machine never
## share a save slot or a profile (Test suite optimization, docs/TEST_SUITE.md).
const TEST_DIR_FORMAT := "gut_%d"

## from_version (int) -> Callable(data: Dictionary) -> Dictionary at from_version + 1.
## Empty: no compatibility (ruling 5).
var _migrations: Dictionary = {}
## The save locations and the replay switch.
var config: CampaignConfigData = load(CONFIG_PATH)
## The folder this process saves under: the source folder or the export folder.
var root_dir: String = base_dir_for(config, is_source_run())
## Where saves live: root_dir, or this test run's own folder in the export folder.
var save_dir: String = config.save_dir_export.path_join(TEST_DIR_FORMAT % OS.get_process_id()) if is_test_run() else root_dir


## Whether this process runs the GUT test suite (as Settings.is_test_run; SaveService loads
## before the Settings autoload).
static func is_test_run() -> bool:
	for a in OS.get_cmdline_args():
		if a.ends_with("gut_cmdln.gd"):
			return true
	return false


## Whether this process runs from source (the editor, or a project run that is not an
## exported template build).
static func is_source_run() -> bool:
	return OS.has_feature("editor") or not OS.has_feature("template")


## The save folder for a run from source (`source` true) or an exported build.
static func base_dir_for(cfg: CampaignConfigData, source: bool) -> String:
	return cfg.save_dir_source if source else cfg.save_dir_export


## A test run removes its own save folder when it ends.
func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE and save_dir != root_dir:
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


## The folder replays are written to (inside the save folder).
func replay_dir() -> String:
	return save_dir.path_join(config.replay_subdir)


## Whether a finished combat writes its replay: the config's switch, on a run from source,
## never in a test run (a test that wants one calls write_replay with its own folder).
func replays_enabled() -> bool:
	return config.write_replays and is_source_run() and not is_test_run()


## Registers a migration that upgrades data from `from_version` to `from_version + 1`.
func register_migration(from_version: int, migration: Callable) -> void:
	_migrations[from_version] = migration


## Makes `dir_path` (and its parents). A folder made under the source save folder gets a
## `.gdignore` at that folder's root so Godot never imports what is saved there.
func ensure_dir(dir_path: String) -> Error:
	var err := DirAccess.make_dir_recursive_absolute(dir_path)
	if err != OK:
		return err
	var root := config.save_dir_source
	if dir_path == root or dir_path.begins_with(root + "/"):
		var marker := root.path_join(GDIGNORE_FILE)
		if not FileAccess.file_exists(marker):
			var f := FileAccess.open(marker, FileAccess.WRITE)
			if f == null:
				return FileAccess.get_open_error()
			f.close()
	return OK


## Writes `data` as JSON at `path`, stamping the current SAVE_VERSION. Creates the
## directory when needed. Returns OK or the file error.
func save_dict(path: String, data: Dictionary) -> Error:
	var stamped := data.duplicate(true)
	stamped["version"] = SAVE_VERSION
	var dir_error := ensure_dir(path.get_base_dir())
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
## (and pushes an error) when the file is missing, unparsable or of another version.
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


## Writes the replay of the finished `session` (CombatReplay) into `dir` (replay_dir() when
## empty). Returns the file's path, or "" when it could not be written.
func write_replay(session: CombatSession, dir: String = "") -> String:
	var folder := dir if dir != "" else replay_dir()
	var data := CombatReplay.record(session)
	var now_ms := int(Time.get_unix_time_from_system() * 1000.0)
	var path := folder.path_join(REPLAY_FILE_FORMAT % [now_ms, data["seed"]])
	var n := 1
	while FileAccess.file_exists(path):
		path = folder.path_join(REPLAY_FILE_FORMAT % [now_ms + n, data["seed"]])
		n += 1
	if save_dict(path, data) != OK:
		return ""
	prune_replays(folder)
	return path


## The replay files in `dir`, oldest first (their names sort by the time written).
func list_replays(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	for f in DirAccess.get_files_at(dir):
		if f.begins_with(REPLAY_PREFIX) and f.ends_with(REPLAY_EXT):
			out.append(dir.path_join(f))
	out.sort()
	return out


## ART-0 audit B4: deletes the oldest replays in `dir` until at most `config.max_replays`
## remain (0 = no cap). Returns how many were deleted.
func prune_replays(dir: String) -> int:
	if config.max_replays <= 0:
		return 0
	var files := list_replays(dir)
	var extra := files.size() - config.max_replays
	for i in maxi(0, extra):
		DirAccess.remove_absolute(files[i])
	return maxi(0, extra)


## Writes the replay of a combat that just ended, when replays are on (replays_enabled).
## Returns the path written, or "".
func record_replay(session: CombatSession) -> String:
	if session == null or session.state == null or not session.state.is_over() or not replays_enabled():
		return ""
	return write_replay(session)


## Reads a replay file (load_dict; {} when missing, of another version or not a replay).
func load_replay(path: String) -> Dictionary:
	var data := load_dict(path)
	if String(data.get("kind", "")) != CombatReplay.KIND:
		return {}
	return data


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
