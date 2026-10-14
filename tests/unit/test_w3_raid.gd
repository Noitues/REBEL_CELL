extends GutTest
## Plan 1 wave 3, W3-RAID (C9 raid setup, F17, R8 report pencil, D-UX6 smear notches, F18):
## the 0-crew warning shows exactly at 0 crew and START DEFENSE asks first (and still runs);
## the report's outcome word is the stamp's word (the resolver's outcome); one name for the home
## server; the intercept message is whole; the report pencil is CELL HOLDS only; the wax
## dropouts are a smear. Headless (the frames are checked windowed: DECISIONS "W3-RAID").

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w3_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _raid_campaign(seed_value: int = 1) -> void:
	RunManager.new_campaign(seed_value)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"safehouse"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	c.armory = [&"turret", &"ice_lock", &"honeypot_node"]
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


func _hq() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	return scene


func _kill_crew() -> void:
	for o in RunManager.campaign.roster:
		o.alive = false


# --- C9: the 0-crew warning ----------------------------------------------------------------------

func test_the_crew_warning_rule_is_true_exactly_at_zero_living_crew() -> void:
	_raid_campaign()
	var c := RunManager.campaign
	assert_gt(c.living_operatives().size(), 0, "a new campaign has crew")
	assert_false(CampaignRules.raid_crew_warning(c), "crew: no warning")
	var living := c.living_operatives()
	for i in living.size() - 1:
		living[i].alive = false
	assert_eq(c.living_operatives().size(), 1)
	assert_false(CampaignRules.raid_crew_warning(c), "one left: no warning")
	living[living.size() - 1].alive = false
	assert_true(CampaignRules.raid_crew_warning(c), "0 crew: the warning")
	assert_false(CampaignRules.raid_crew_warning(null))


func test_the_raid_setup_shows_the_warning_only_at_zero_crew() -> void:
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	assert_null(hq._panel.find_child("NoCrewWarning", true, false), "crew: no warning on the setup")
	hq.get_parent().queue_free()
	await _frames(1)
	_raid_campaign()
	_kill_crew()
	hq = await _hq()
	hq.show_raid()
	await _frames(2)
	var warn := hq._panel.find_child("NoCrewWarning", true, false) as Label
	assert_not_null(warn, "0 crew: the warning stands over START DEFENSE")
	assert_not_null(hq._panel.find_child("RunRaid", true, false), "START DEFENSE stays")


func test_start_defense_at_zero_crew_asks_first_and_yes_runs_the_raid() -> void:
	_raid_campaign()
	_kill_crew()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var pending_before := RunManager.campaign.pending_raids.size()
	hq.request_start_defense()
	await _frames(2)
	var d := hq._defense_confirm as ConfirmDialog
	assert_not_null(d, "a confirm opens")
	assert_eq(RunManager.campaign.pending_raids.size(), pending_before, "the raid has not started")
	d.confirmed.emit()
	await _frames(2)
	assert_lt(RunManager.campaign.pending_raids.size(), pending_before, "YES runs the raid")


func test_start_defense_with_crew_starts_at_once() -> void:
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var pending_before := RunManager.campaign.pending_raids.size()
	hq.request_start_defense()
	await _frames(2)
	assert_null(hq._defense_confirm, "no confirm with crew")
	assert_lt(RunManager.campaign.pending_raids.size(), pending_before, "the raid ran")


# --- C9: one name, one outcome word ---------------------------------------------------------------

func test_the_report_outcome_is_the_stamps_word_for_seeded_raids() -> void:
	for seed_value in [1, 2, 3, 4]:
		_raid_campaign(seed_value)
		var hq := await _hq()
		hq.show_raid()
		await _frames(2)
		RunManager.fight_raid()
		hq.show_raid_summary()
		await _frames(3)
		var r: Dictionary = RunManager.campaign.last_raid
		var word: String = hq.report_outcome_words(r)
		assert_eq(word, RaidVerdict.of_result(r).replace("\n", ", "), "seed %d: the report says the stamp's verdict" % seed_value)
		var report := hq._panel.find_child("RaidReport", true, false) as RaidPaper
		assert_not_null(report)
		var sub: String = report.sub_label.text
		assert_string_contains(sub, word, "seed %d: the order line carries it" % seed_value)
		assert_false(sub.contains("FAILED") or sub.contains("SUCCESS"), "seed %d: no corp FAILED / SUCCESS beside the stamp" % seed_value)
		if bool(r.get("campaign_lost", false)):
			assert_string_contains(word, "BREACHED")
		var holds: Node = hq._panel.find_child("CellHolds", true, false)
		assert_eq(holds != null, not bool(r.get("campaign_lost", false)), "seed %d: CELL HOLDS only when the Cell survived" % seed_value)
		hq.get_parent().queue_free()
		await _frames(1)


func test_the_home_server_has_one_name_on_the_raid_pages() -> void:
	var hq_script: GDScript = load("res://scripts/ui/hq_scene.gd")
	assert_eq(hq_script.get("HOME_LABEL"), "HOME SERVER")
	assert_eq(CityLayout.HOME_LABEL, "HOME SERVER")
	assert_eq(hq_script.get("RAID_TARGETS")[RC.ThreatRouting.SHORTEST_TO_HOME], "HOME SERVER")
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var home := hq._panel.find_child("HomeForecast", true, false) as Label
	assert_not_null(home)
	assert_string_contains(home.text, "HOME SERVER")
	assert_false(home.text.contains("CORE"))
	var stopped := hq._panel.find_child("ThreatsStopped", true, false) as Label
	assert_not_null(stopped)
	assert_false(stopped.text.to_upper().contains("STOPPED"), "the row label says THREATS STOPPED; its value is the count")


func test_the_intercept_message_is_not_truncated() -> void:
	var toast := CorpNewsToast.new(&"halcyon")
	add_child_autofree(toast)
	assert_eq(toast.label.max_lines_visible, -1, "no line cap")
	assert_eq(toast.label.text_overrun_behavior, TextServer.OVERRUN_NO_TRIMMING, "no ellipsis")


# --- R8: the report pencil -----------------------------------------------------------------------

func test_the_report_verdict_is_a_sticker_and_no_pencil_layer() -> void:
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	RunManager.fight_raid()
	hq.show_raid_summary()
	await _frames(4)
	var r: Dictionary = RunManager.campaign.last_raid
	var holds: Node = hq._panel.find_child("CellHolds", true, false)
	assert_null(hq._panel.find_child("ReportPencil", true, false), "ART-R1 3a: no pencil verdict layer")
	if bool(r.get("campaign_lost", false)):
		assert_null(holds)
		return
	assert_true(holds is RaidSticker, "ART-R1 3a: CELL HOLDS is a sticker on the paper (Q7)")
	assert_eq((holds as RaidSticker).mouse_filter, Control.MOUSE_FILTER_IGNORE, "CELL HOLDS takes no input")
	assert_eq((holds as RaidSticker).text, tr(RaidVerdict.CELL_HOLDS))


# --- D-UX6: the notches are a smear --------------------------------------------------------------

func test_wax_dropouts_are_a_soft_streaky_smear_not_a_flat_square() -> void:
	var src := FileAccess.get_file_as_string("res://shaders/kit/marker_stroke.gdshader")
	assert_true(src.contains("SMEAR_SOFT"), "a wide soft edge")
	assert_true(src.contains("SMEAR_STREAK_MIN"), "a streaky alpha")
	assert_true(src.contains("h.x * soft * streak"), "the bite is the soft edge times the streak")


# --- F17: a placed defence shows on the node itself ----------------------------------------------

func test_dropping_a_defence_on_a_node_changes_the_node_itself() -> void:
	_raid_campaign()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var c := RunManager.campaign
	var target: StringName = c.grid.claimed_ids()[0]
	var before := int(RaidMapNodes.socket_spec(target, {}, true, c)["defence"])
	hq.deploy_asset(0, target)
	await _frames(3)
	var after := int(RaidMapNodes.socket_spec(target, {}, true, c)["defence"])
	assert_eq(after, before + 1, "the node's socket counts the placed defence")
