extends GutTest
## Plan 1 wave 3, W3-RAID (C9 raid setup, F17, R8 report pencil, D-UX6 smear notches, F18):
## the 0-crew warning shows exactly at 0 crew and START DEFENSE asks first (and still runs);
## the report's outcome word is the stamp's word (the resolver's outcome); one name for the home
## server; the intercept message is whole; the report pencil is CELL HOLDS only; the wax
## dropouts are a smear. Headless (the frames are checked windowed: DECISIONS "W3-RAID").

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const HQ_SCRIPT := preload("res://scripts/ui/hq_scene.gd")

var _scale: float


func before_each() -> void:
	RaidModelFixture.use_resolver()  # Phase 2b: Solace is the resolver's carrier here (raid views of the tide are Phase 3)
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w3_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	RaidModelFixture.restore()
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


# --- C9 + ruling 4 (2026-10-14): the warning fires on 0 STATIONED -----------------------------------

## Stations the living operative at `index` on the first free site (the count rule does not need a slot).
func _station(index: int = 0) -> void:
	var c := RunManager.campaign
	var ids: Array = c.grid.sites.keys()
	ids.sort()
	for id in ids:
		if c.grid.stationed_on(id) == &"":
			c.grid.site(id)["stationed"] = String(c.living_operatives()[index].id)
			return


func test_the_crew_warning_rule_is_true_exactly_at_zero_stationed_for_seeded_states() -> void:
	for seed_value in [1, 2, 3]:
		_raid_campaign(seed_value)
		var c := RunManager.campaign
		assert_gt(c.living_operatives().size(), 0, "a new campaign has crew")
		assert_eq(CampaignRules.stationed_count(c), 0)
		assert_true(CampaignRules.raid_crew_warning(c), "seed %d: crew alive but none stationed: the warning" % seed_value)
		_station()
		assert_eq(CampaignRules.stationed_count(c), 1)
		assert_false(CampaignRules.raid_crew_warning(c), "seed %d: one stationed: no warning" % seed_value)
		for o in c.living_operatives():
			o.alive = false
		assert_eq(CampaignRules.stationed_count(c), 0, "a dead operative does not count as stationed")
		assert_true(CampaignRules.raid_crew_warning(c))
	assert_false(CampaignRules.raid_crew_warning(null))


func test_the_raid_setup_reads_crew_stationed_and_warns_only_at_zero_stationed() -> void:
	_raid_campaign()
	_station()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var line := hq._panel.find_child("CrewCount", true, false) as Label
	assert_not_null(line)
	var alive := RunManager.campaign.living_operatives().size()
	assert_eq(line.text, "Crew: %d (Stationed: 1)" % alive)
	assert_null(hq._panel.find_child("NoCrewWarning", true, false), "stationed: no warning on the setup")
	hq.get_parent().queue_free()
	await _frames(1)
	_raid_campaign()
	hq = await _hq()
	hq.show_raid()
	await _frames(2)
	var warn := hq._panel.find_child("NoCrewWarning", true, false) as Label
	assert_not_null(warn, "0 stationed: the warning stands over START DEFENSE")
	assert_true(warn.text.contains("%d alive" % alive) and warn.text.contains("0 stationed"), "it names both numbers")
	assert_eq((hq._panel.find_child("CrewCount", true, false) as Label).text, "Crew: %d (Stationed: 0)" % alive)
	assert_not_null(hq._panel.find_child("RunRaid", true, false), "START DEFENSE stays")


func test_start_defense_with_nobody_stationed_asks_first_and_yes_runs_the_raid() -> void:
	_raid_campaign()
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


func test_start_defense_with_a_stationed_operative_starts_at_once() -> void:
	_raid_campaign()
	_station()
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	var pending_before := RunManager.campaign.pending_raids.size()
	hq.request_start_defense()
	await _frames(2)
	assert_null(hq._defense_confirm, "no confirm with crew stationed")
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
		assert_eq(holds != null, not bool(r.get("campaign_lost", false)), "seed %d: CELL HOLDS whenever Home survives" % seed_value)
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
	assert_string_contains(home.text, "HOME")
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
	RunManager.campaign.last_raid["campaign_lost"] = false  # D28: the sticker belongs to a CELL HOLDS report; this test is its layout
	hq.show_raid_summary()
	await _frames(4)
	var holds: Node = hq._panel.find_child("CellHolds", true, false)
	assert_null(hq._panel.find_child("ReportPencil", true, false), "ART-R1 3a: no pencil verdict layer")
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


## PT-003 fix 7: CELL HOLDS clears every text row of the report (measured at 1.0): no label with words, and not the footer band.
func test_cell_holds_sticker_clears_every_text_row() -> void:
	var checked := 0
	for seed_value in [1, 2, 3, 4]:
		_raid_campaign(seed_value)
		var hq := await _hq()
		hq.show_raid()
		await _frames(2)
		RunManager.fight_raid()
		RunManager.campaign.last_raid["campaign_lost"] = false  # D28: the sticker belongs to a CELL HOLDS report; this test is its layout
		hq.show_raid_summary()
		await _frames(8)
		var holds := hq._panel.find_child("CellHolds", true, false) as Control
		if holds != null:
			checked += 1
			var box := holds.get_global_rect().grow(HQ_SCRIPT.HOLDS_CLEAR_PX - 0.5)  # the rule's own clearance (the tilt and die-cut border)
			for n in hq._panel.find_children("*", "Label", true, false):
				var l := n as Label
				if l.text.strip_edges() == "" or not l.is_visible_in_tree() or holds.is_ancestor_of(l):
					continue
				assert_false(box.intersects(l.get_global_rect()), "seed %d: CELL HOLDS covers '%s'" % [seed_value, l.text])
			var paper := hq._panel.find_child("RaidReport", true, false) as RaidPaper
			var foot := paper.get_global_rect()
			foot = Rect2(foot.position.x, foot.end.y - HQ_SCRIPT.HOLDS_FOOT_PX, foot.size.x, HQ_SCRIPT.HOLDS_FOOT_PX)
			assert_false(box.intersects(foot), "seed %d: CELL HOLDS %s clear of the footer meta line %s (paper %s)" % [seed_value, box, foot, paper.get_global_rect()])
		hq.get_parent().queue_free()
		await _frames(1)
	assert_gt(checked, 0, "at least one seed holds")


func test_holds_spot_clear_sits_under_the_rows_and_above_the_footer() -> void:
	var paper := Rect2(0, 0, 400, 600)
	var size := Vector2(120, 60)
	var want: Vector2 = HQ_SCRIPT.holds_spot(paper, size)
	var none: Array[Rect2] = []
	assert_eq(HQ_SCRIPT.holds_spot_clear(paper, size, none), want, "no rows: the plain spot")
	var rows: Array[Rect2] = [Rect2(0, 475, 400, 40)]
	var at: Vector2 = HQ_SCRIPT.holds_spot_clear(paper, size, rows, 600.0)
	assert_gte(at.y, rows[0].end.y, "under the row")
	assert_lte(at.y + size.y, 600.0, "above the footer line")
	assert_true(paper.encloses(Rect2(at, size)), "and still on the paper")
	var tight: Array[Rect2] = [Rect2(0, 0, 400, 570)]
	assert_eq(HQ_SCRIPT.holds_spot_clear(paper, size, tight, 590.0), want, "no room: the plain spot")


## PT-003 fix 4: the ring and the pip are readable at 1.0 (a stroke of at least 4 px and a pip disc of at least 5 px at a
## typical map icon radius), and a plain claimed node has no asset slot (GDD 3.2): the drop goes to a slotted node.
func test_the_defence_ring_and_pip_read_at_text_one() -> void:
	for r in [18.0, 24.0, 32.0]:
		assert_gte(RaidSocket.defence_ring_width(r), 4.0, "ring stroke at r=%s" % r)
		assert_gte(RaidSocket.defence_pip_radius(r), 4.5, "pip disc at r=%s" % r)
		assert_gte(RaidSocket.defence_ring_width(r), r * 0.2 - 0.001, "ring stroke scales with the node")


## ART-R2 M8: the raid result page has no SEND IT control (the one in the motion lab's M8 strip is the lab's chrome).
func test_art_r2_no_send_it_control_on_the_raid_result() -> void:
	_raid_campaign(2)
	var hq := await _hq()
	hq.show_raid()
	await _frames(2)
	RunManager.fight_raid()
	hq.show_raid_summary()
	await _frames(4)
	for c in hq._panel.find_children("*", "", true, false):
		var text := ""
		if c is BaseButton:
			text = (c as BaseButton).text
		elif c is Label:
			text = (c as Label).text
		assert_false(text.to_upper().contains("SEND IT"), "%s says SEND IT" % c.name)
		if c.has_method("get_text"):
			assert_false(String(c.get_text()).to_upper().contains("SEND IT"), "%s says SEND IT" % c.name)
