extends Node
## Plan 2 WH-02 fixture writer (dev tool, headless): a v5 campaign save with a netrun in
## progress, written by the build it runs on, and its campaign and run state hashes beside it.
## Run on the pre-WH-02 build (campaign_state.gd / run_state.gd from w1-close 0613a8c4) to
## record tests/fixtures/saves/v5/v5_pre_wh02.json and .hashes.json, which
## test_corp_theme_state loads with the WH-02 build (defaults, same hashes).
##   godot --headless --path . res://tools/design_lab/wh02_v5_fixture.tscn -- --out=<abs dir>

const SEED := 7702


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = "wh02_fixture"
	RunManager.scene_switching_enabled = false
	RunManager.reset()
	RunManager.new_campaign(SEED)
	var s := RunManager.start_run()
	var err := RunManager.autosave()
	var text := FileAccess.get_file_as_string(RunManager.save_path())
	var f := FileAccess.open(out.path_join("v5_pre_wh02.json"), FileAccess.WRITE)
	f.store_string(text)
	f.close()
	var h := FileAccess.open(out.path_join("v5_pre_wh02.hashes.json"), FileAccess.WRITE)
	h.store_string(JSON.stringify({"campaign": RunManager.campaign.state_hash(), "run": s.state_hash() if s != null else 0}, "\t"))
	h.close()
	print("WH02 fixture: autosave=%d run=%s" % [err, s != null])
	RunManager.delete_save()
	get_tree().quit()
