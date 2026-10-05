extends GutTest
## ART-11 4D (ART_BIBLE v2 §4.8; DECISIONS "Art direction — ART-11 4D campaign end"): the
## campaign lost ransomware lock (option A), the corporation's audit dossier (lost and won) and
## the run end's verdict sticker. Their words and facts, MotionSkip on one press, reduce effects
## = end state, headless never waits, views never change state, layouts at 1.0 / 1.6 / 2.0, the
## buttons reachable by pad, and the motion entries with their lab demos.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const LAB_SCRIPT := "res://tools/design_lab/motion_lab.gd"
const SCREEN := Rect2(0, 0, 1280, 720)
const IDS: Array[StringName] = [&"ransom_glitch", &"ransom_wipe", &"ransom_padlock", &"ransom_notice_in", &"ransom_verb_stamp",
	&"ransom_sticker_curl", &"ransom_sticker_drop", &"ransom_sticker_stagger", &"ransom_countdown", &"ransom_wipe_hold", &"ransom_cut",
	&"dossier_open", &"dossier_stamp", &"dossier_note", &"dossier_note_stagger", &"run_end_slap"]
## Frames a forced-live lock gets to cut and finish (bounded; its cut is half a second).
const CUT_FRAMES := 240

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art11_end"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
		Fx.apply_settings()
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


func _live() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _key(k: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = true
	return e


## A lock on its own over a host, Halcyon's, with five nodes and four stickers.
func _lock() -> RansomLock:
	var host: Control = add_child_autofree(Control.new())
	host.size = SCREEN.size
	var lock := RansomLock.new()
	host.add_child(lock)
	lock.nodes_provider = func() -> Array:
		var pts: Array = []
		for i in 5:
			pts.append({"at": Vector2(200 + i * 200, 150 + (i % 2) * 300), "home": i == 0})
		return pts
	var specs: Array[Dictionary] = [{"text": "CELL DEFENSE"}, {"asset": &"turret", "text": "TURRET"}, {"asset": &"decoy", "text": "DECOY"},
		{"text": "REBEL_CELL", "fill": Palette.END_VINYL_PINK}]
	lock.setup(&"halcyon", "Halcyon Civic", 0, 50, specs)
	return lock


func _facts(won: bool) -> DossierFacts:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	c.outcome = CampaignState.Outcome.WON if won else CampaignState.Outcome.LOST
	return DossierFacts.build(c, RunManager.corporation, RunManager.profile, RunManager.config(), func(id: StringName) -> String: return String(id),
		func(id: StringName) -> String: return String(id), [] as Array[Dictionary], 3)


# --- House styles -----------------------------------------------------------------------------

func test_every_corporation_has_its_house_style_and_verb() -> void:
	var verbs := {&"halcyon": "PROCESSED", &"meridian": "RECLAIMED", &"solace": "TREATED", &"orbital": "DE-ORBITED", &"rebel_cell": "OVERWRITTEN"}
	assert_eq(CorpHouseStyle.known_ids().size(), verbs.size(), "the five corporations of the bible's §2.4")
	for id: StringName in verbs:
		var s := CorpHouseStyle.of(id)
		assert_eq(s.verb, verbs[id], "%s's verb (bible §4.8)" % id)
		assert_ne(s.head, "", "%s has a head line" % id)
		assert_ne(s.sub, "", "%s has its sub line" % id)
		assert_eq(s.color(), Palette.corp_color(id), "%s: the house hue is the corporation's own" % id)
		assert_eq(s.accent(), Palette.corp_secondary(id), "%s: its accent the round 18 secondary" % id)
	assert_eq(CorpHouseStyle.of(&"rebel_cell").name_shown("Rebel Cell"), tr("DISPATCH"), "DISPATCH signs its own lock")
	assert_eq(CorpHouseStyle.of(&"rebel_cell").head_font(), Palette.mono(), "DISPATCH stays Share Tech Mono (bible §2.9)")
	assert_eq(CorpHouseStyle.of(&"nobody").verb, CorpHouseStyle.of(CorpHouseStyle.FALLBACK).verb, "an unknown house wears the fallback's words")


# --- The audit dossier's facts ----------------------------------------------------------------

func test_the_dossier_reads_the_campaign_and_never_changes_it() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var cls := RunManager.lookup().get_content(&"ghost") as ClassData
	c.recruit(cls)
	c.roster[1].alive = false
	c.roster[0].runs_completed = 4
	c.thresholds_fired.assign([50, 25])
	c.heat = 61
	c.outcome = CampaignState.Outcome.LOST
	var before := c.state_hash()
	var f := DossierFacts.build(c, RunManager.corporation, RunManager.profile, RunManager.config(), func(id: StringName) -> String: return String(id),
		func(id: StringName) -> String: return String(id), [] as Array[Dictionary], 2)
	assert_false(f.won)
	assert_eq(f.heat_marks, [25, 50] as Array[int], "the thresholds crossed, ascending")
	assert_eq(f.heat_levels, RunManager.config().major_heat_levels(), "the trace's rules are the config's levels")
	assert_eq(f.crew.size(), c.roster.size(), "the whole crew")
	assert_eq(f.at_large(), c.living_operatives().size(), "the dead are not at large")
	assert_false(f.crew[1]["alive"], "the lost operative is DECEASED")
	assert_eq(String(f.most_troublesome["name"]), c.roster[0].name, "the most runs")
	assert_eq(f.home_max, c.grid.home_max_integrity)
	assert_eq(c.state_hash(), before, "reading the file changes nothing")


func test_the_dossier_shows_at_once_headless_with_its_words() -> void:
	for won in [false, true]:
		var d: AuditDossier = add_child_autofree(AuditDossier.new(_facts(won)))
		d.size = SCREEN.size
		await _frames(2)
		assert_false(d.motion_running(), "headless: the open file at once")
		assert_true(d.case_stamp.visible)
		assert_eq(d.case_stamp.text, tr("AT LARGE") if won else tr("CASE CLOSED"))
		assert_eq(d.notes.size(), 4, "four auditor's notes")
		for n in d.notes:
			assert_true(n.visible, "each note has landed")
		var lines := "\n".join(d.report_lines())
		assert_string_contains(lines, tr("SUBJECT"))
		if won:
			assert_string_contains(lines, tr("AT LARGE"))
		else:
			assert_string_contains(lines, tr(CorpHouseStyle.of(d.facts.corporation_id).verb), "the house's verb is the STATUS")
		assert_false(d.cover.visible, "the cover is open")
		d.queue_free()


func test_the_dossiers_buttons_emit_and_are_stickers_the_pad_reaches() -> void:
	var d: AuditDossier = add_child_autofree(AuditDossier.new(_facts(false)))
	d.size = SCREEN.size
	await _frames(2)
	assert_true(d.main_menu_button is VinylButton and d.new_campaign_button is VinylButton)
	assert_eq(d.main_menu_button.focus_mode, Control.FOCUS_ALL)
	assert_eq(d.new_campaign_button.focus_mode, Control.FOCUS_ALL)
	assert_eq(UiFocus.first_focusable(d), d.main_menu_button, "the yellow safe choice has the first focus (bible §2.10)")
	assert_eq(d.main_menu_button.sticker.fill, Palette.END_VINYL_YELLOW)
	assert_eq(d.new_campaign_button.sticker.fill, Palette.END_VINYL_PINK, "the pink verb")
	var got := []
	d.main_menu_pressed.connect(func() -> void: got.append("menu"))
	d.new_campaign_pressed.connect(func() -> void: got.append("new"))
	d.main_menu_button.pressed.emit()
	d.new_campaign_button.pressed.emit()
	assert_eq(got, ["menu", "new"], "Signal Up: the view only asks")


func test_the_dossier_fits_at_every_text_size() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var d: AuditDossier = add_child_autofree(AuditDossier.new(_facts(false)))
		d.size = SCREEN.size
		await _frames(3)
		for sheet in d.find_children("*", "PaperSheet", true, false):
			var r := (sheet as Control).get_global_rect()
			assert_true(r.end.x <= SCREEN.size.x + 1.0 and r.position.x >= -1.0, "%.1f: %s on the screen's width: %s" % [scale, sheet.name, r])
		for b: Control in [d.main_menu_button, d.new_campaign_button]:
			assert_true(b.get_global_rect().end.x <= SCREEN.size.x + 1.0, "%.1f: %s on the screen" % [scale, b.name])
		if scale >= Settings.TEXT_SCALE_MAX:
			assert_true(d.spread.vertical, "at the largest text the pages stack")
		d.queue_free()
		await _frames(1)


func test_the_dossier_completes_on_one_press_when_live() -> void:
	_live()
	var d: AuditDossier = add_child_autofree(AuditDossier.new(_facts(false)))
	d.size = SCREEN.size
	assert_true(d.motion_running(), "the cover swings open, the stamp and notes land")
	assert_true(d.is_in_group(MotionSkip.GROUP))
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(d.motion_running(), "one press: the open file")
	assert_true(d.case_stamp.visible)
	assert_eq(d.case_stamp.scale, Vector2.ONE)


# --- The ransomware lock ----------------------------------------------------------------------

func test_the_lock_completes_on_one_press_then_cuts_on_the_next() -> void:
	_live()
	var lock := _lock()
	var ended := [0]
	lock.finished.connect(func() -> void: ended[0] += 1)
	await BoundedWait.until(get_tree(), func() -> bool: return lock.started, 5.0)
	assert_true(lock.started and lock.visible, "it starts once the screen behind is ready")
	assert_true(lock.motion_running())
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(lock.motion_running(), "one press completes the takeover")
	assert_eq(lock.countdown_label.text, RansomLock.COUNTDOWN_FORMAT % 0.0, "the countdown at zero")
	assert_eq(lock._locks_landed, 5, "every node padlocked")
	for v in lock.stickers:
		assert_false(v.visible, "the Cell's stickers have dropped off")
	assert_true(lock.verb_stamp.visible and lock.notice.modulate.a >= 1.0, "the notice and its verb")
	get_viewport().push_input(_key(KEY_SEMICOLON))
	await BoundedWait.until(get_tree(), func() -> bool: return ended[0] > 0, 5.0, CUT_FRAMES)
	assert_eq(ended[0], 1, "a press in the hold cuts to the dossier, once")


func test_reduce_effects_shows_the_locks_end_state_at_once() -> void:
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	var lock := _lock()
	await _frames(3)
	assert_false(lock.motion_running(), "reduce effects: no motion")
	assert_eq(lock.countdown_label.text, RansomLock.COUNTDOWN_FORMAT % 0.0)
	assert_eq(lock._locks_landed, 5)
	assert_eq(lock.phase(RansomLock.WIPE), 1.0, "the takeover covers the screen")
	assert_eq(lock.hold_seconds(), 0.0, "headless never waits (no hold)")
	assert_true(lock.done, "headless: it cuts at once")


func test_headless_campaign_loss_goes_straight_to_the_dossier_and_state_holds() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	DemoSetup.end_campaign(c, CampaignState.Outcome.LOST)
	var before := c.state_hash()
	var hq := _scene(HQ)
	await _frames(2)
	assert_false(RansomLock.plays_now(), "headless: no lock")
	hq.show_end()
	await _frames(2)
	assert_eq(hq.panel_name, "end")
	assert_true(hq._panel is AuditDossier)
	assert_null(hq.end_lock)
	assert_eq(c.state_hash(), before, "the end screens change nothing")


func test_a_live_loss_plays_the_lock_over_the_network_then_the_dossier() -> void:
	_live()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	DemoSetup.end_campaign(c, CampaignState.Outcome.LOST)
	var before := c.state_hash()
	var hq := _scene(HQ)
	await _frames(2)
	hq.show_end()
	await _frames(2)
	assert_eq(hq.panel_name, "end_lock")
	var lock: RansomLock = hq.end_lock
	assert_not_null(lock)
	assert_eq(lock.style.corp_id, c.corporation_id, "the winning corporation's house")
	assert_false(hq._end_lock_nodes().is_empty(), "the network's nodes to padlock")
	lock.complete_motion()
	lock.cut()
	await BoundedWait.until(get_tree(), func() -> bool: return hq.panel_name == "end", 5.0, CUT_FRAMES)
	assert_eq(hq.panel_name, "end", "the cut shows the audit dossier")
	assert_false(is_instance_valid(lock) and lock.is_inside_tree(), "the lock is gone")
	assert_eq(c.state_hash(), before, "the end screens change nothing")


# --- The run end ------------------------------------------------------------------------------

func test_the_run_ends_verdicts_are_stickers_and_home_fell_is_red() -> void:
	RunManager.new_campaign(1)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	await _frames(2)
	for outcome in [RunState.Outcome.COMPLETED, RunState.Outcome.DIED, RunState.Outcome.ABORTED]:
		RunManager.netrun.run.outcome = outcome
		RunManager.netrun.run.phase = RunState.Phase.ENDED
		scene._show_end()
		await _frames(2)
		var stamp := scene._panel.find_child("ResultStamp", true, false) as VinylWord
		assert_not_null(stamp)
		assert_eq(stamp.verdict, scene.end_verdict(outcome))
		assert_eq(stamp.fill, Palette.END_VINYL_YELLOW if outcome == RunState.Outcome.COMPLETED else Palette.END_VINYL_RED)
		assert_eq(stamp.focus_mode, Control.FOCUS_NONE)
		assert_true(stamp.get_parent() is TiltBox, "tilted on the glass")
		var back := scene._panel.find_child("BackToHq", true, false) as VinylButton
		assert_eq(back.text, "Back to HQ")
		assert_eq(back.sticker.fill, Palette.END_VINYL_PINK, "the screen's one pink verb")
	assert_eq(scene.end_verdict(RunState.Outcome.ABORTED), "HOME FELL")


func test_the_verdict_slap_completes_with_a_press() -> void:
	_live()
	var v: VinylWord = add_child_autofree(VinylWord.new("FLATLINED", Palette.END_VINYL_RED, UiTheme.DISPLAY))
	await _frames(1)
	v.slap(&"run_end_slap")
	assert_true(v.motion_running())
	MotionSkip.complete_all(v)
	assert_false(v.motion_running())
	assert_eq(v.scale, Vector2.ONE)


# --- Motion table -----------------------------------------------------------------------------

func test_the_end_motions_are_required_and_have_lab_demos() -> void:
	var demos: Dictionary = (load(LAB_SCRIPT) as GDScript).get_script_constant_map()["DEMOS"]
	for id in IDS:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in ui_motion.tres" % id)
		assert_true(demos.has(id) and String((demos[id] as Array)[0]) == "screen", "%s has a demo on its real piece" % id)
	assert_true(UiMotionData.OFF_PARTS.has(&"ransom_sticker_stagger") and UiMotionData.OFF_PARTS.has(&"dossier_note_stagger"), "the staggers are parts")
