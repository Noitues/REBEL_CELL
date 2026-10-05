extends GutTest
## ART-0 S0 (DECISIONS "Art direction — ART-0 names pass, part 1 + saves folder", ruling 5):
## a run from source saves under the project's git-ignored `saves/` folder (with a
## `.gdignore`), an exported build under `user://saves`; finished combats write replays
## that reload and replay to the same result hash; a save of another version is refused
## through the "can't load" path. GUT runs keep their own per-process folders.

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")

var _saves: Node
var _cfg: CampaignConfigData
## This run's own scratch folders (by process id).
var _src: String = "user://gut_saves_src_%d" % OS.get_process_id()
var _replays: String = "user://gut_replays_%d" % OS.get_process_id()


func before_each() -> void:
	_cfg = CombatFixture.config()
	_saves = autofree(SaveServiceScript.new())


func after_each() -> void:
	SaveServiceScript._remove_tree(_src)
	SaveServiceScript._remove_tree(_replays)


func test_a_run_from_source_saves_in_the_project_folder_and_an_export_in_user() -> void:
	assert_eq(_cfg.save_dir_source, "res://saves", "the project's own folder (git ignores /saves/)")
	assert_eq(_cfg.save_dir_export, "user://saves")
	assert_eq(SaveServiceScript.base_dir_for(_cfg, true), _cfg.save_dir_source, "source run")
	assert_eq(SaveServiceScript.base_dir_for(_cfg, false), _cfg.save_dir_export, "exported build")
	assert_true(SaveServiceScript.is_source_run(), "the suite runs from source")
	assert_eq(_saves.root_dir, _cfg.save_dir_source, "so its root is the project folder")
	assert_eq(_saves.replay_dir(), _saves.save_dir.path_join(_cfg.replay_subdir), "replays sit in the save folder")
	# A GUT run keeps its per-process folder (outside the project).
	assert_true(String(_saves.save_dir).begins_with(_cfg.save_dir_export), "a test run never writes into the project")
	assert_true(FileAccess.get_file_as_string("res://.gitignore").contains("/saves/"), "git ignores the folder")


func test_the_source_folder_gets_a_gdignore_when_it_is_made() -> void:
	var svc: Node = autofree(SaveServiceScript.new())
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.save_dir_source = _src
	svc.config = cfg
	assert_eq(svc.save_dict(_src.path_join(_cfg.replay_subdir).path_join("x.json"), {"k": 1}), OK)
	assert_true(FileAccess.file_exists(_src.path_join(SaveServiceScript.GDIGNORE_FILE)), "Godot never imports the saves")
	assert_false(FileAccess.file_exists(_replays.path_join(SaveServiceScript.GDIGNORE_FILE)), "only under the source folder")


func test_a_test_run_writes_no_replay_unless_it_asks() -> void:
	assert_false(_saves.replays_enabled(), "replays are off in a test run")
	var s := _finished_session()
	assert_eq(_saves.record_replay(s), "", "a finished combat in a test writes nothing")
	assert_false(DirAccess.dir_exists_absolute(_saves.replay_dir()), "no replay folder appears")
	assert_true(_cfg.write_replays, "the switch is on in the shipped config")


func test_a_replay_file_reloads_and_replays_to_the_same_result_hash() -> void:
	var s := _finished_session()
	var path: String = _saves.write_replay(s, _replays)
	assert_ne(path, "", "written")
	assert_true(path.begins_with(_replays + "/"))
	var data: Dictionary = _saves.load_replay(path)
	assert_false(data.is_empty(), "it reloads")
	assert_eq(String(data["seed"]), str(s.combat_seed))
	assert_eq((data["actions"] as Array).size(), s.history.size(), "every action")
	assert_eq(String(data["result_hash"]), str(s.state.state_hash()))
	var again := CombatReplay.run(CombatFixture.resolver(), data)
	assert_eq(again.state.state_hash(), s.state.state_hash(), "same result hash")
	assert_true(CombatReplay.matches(CombatFixture.resolver(), data))
	# A tampered action list no longer matches.
	var bent := data.duplicate(true)
	(bent["actions"] as Array).pop_back()
	assert_false(CombatReplay.matches(CombatFixture.resolver(), bent), "the hash pins the actions")


func test_a_save_of_an_older_version_is_refused_without_a_crash() -> void:
	assert_eq(SaveServiceScript.SAVE_VERSION, 2, "bumped for ART-0 (no compatibility)")
	assert_true(_saves._migrations.is_empty(), "no migrations")
	var slot := "gut_old_%d" % OS.get_process_id()
	var path := SaveService.campaign_path(slot)
	assert_eq(SaveService.ensure_dir(path.get_base_dir()), OK)
	var f := FileAccess.open(path, FileAccess.WRITE)
	f.store_string(JSON.stringify({"version": 1, "corporation_id": "solace", "campaign": {"heat": 5}}))
	f.close()
	assert_eq(SaveService.load_dict(path), {}, "refused")
	assert_push_error("no migration from version 1")
	assert_eq(RunManager.slot_summary(slot), {}, "the title screen shows it as empty")
	assert_push_error("no migration from version 1")
	var before := RunManager.save_slot
	RunManager.save_slot = slot
	assert_false(RunManager.resume(), "and CONTINUE can't load it")
	assert_push_error("no migration from version 1")
	RunManager.save_slot = before
	SaveService.delete_save(path)


## A short standalone fight played to its end (or a turn cap), as the engine records it.
func _finished_session() -> CombatSession:
	var s := CombatSession.start(CombatFixture.resolver(), &"breaker", [&"claims_adjuster"], 7, &"rank:1")
	var turns := 0
	while not s.state.is_over() and turns < 60:
		s.apply(CombatAction.nudge(&"player", 1))
		s.apply(CombatAction.end_turn())
		turns += 1
	return s
