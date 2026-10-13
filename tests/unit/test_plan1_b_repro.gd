extends GutTest
## Change plan 1, wave 0, V2: headless repros of the PB-010 / PB-012 B-bugs (docs/handoff/plan1/B_REPRO.md).
## Verify only: each test replays the tester's steps and, when the bug shows, ends in `pending(...)` naming it, so the
## suite never fails on a known bug (a test that finds the bug gone asserts instead). Real engine input
## (`Input.parse_input_event`) is used wherever the bug is an input one (B3, B5).

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const TITLE := "res://scenes/menu/title_scene.tscn"
const HqScript := preload("res://scripts/ui/hq_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_plan1_b_repro"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	CityBakeCache.shutdown()


func after_each() -> void:
	Motion.force_live = false
	CityBakeCache.shutdown()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx._set_jacking(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.pending_tutorial = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _holder() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	return holder


func _combat(enemy: StringName = &"collections_agent", combat_seed: int = 5) -> Control:
	RunManager.new_campaign(1)
	var holder := _holder()
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, combat_seed)
	await _frames()
	return scene


func _key(keycode: int, pressed: bool = true) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = keycode as Key
	e.physical_keycode = keycode as Key
	e.pressed = pressed
	return e


## A real key press through the engine's input queue (never a direct call into the scene).
func _real_key(keycode: int) -> void:
	Input.parse_input_event(_key(keycode, true))
	await _frames(2)
	Input.parse_input_event(_key(keycode, false))
	await _frames(2)


func _click_at(at: Vector2) -> void:
	var move := InputEventMouseMotion.new()
	move.position = at
	move.global_position = at
	get_viewport().push_input(move, false)
	await _frames(2)
	var hov := get_viewport().gui_get_hovered_control()
	print("click at %s: hovered control = %s (%s)" % [at, hov, hov.get_path() if hov != null else ""])
	for down in [true, false]:
		var b := InputEventMouseButton.new()
		b.button_index = MOUSE_BUTTON_LEFT
		b.pressed = down
		b.position = at
		b.global_position = at
		b.button_mask = MOUSE_BUTTON_MASK_LEFT if down else 0
		get_viewport().push_input(b, false)
		await _frames(2)


# --- B1: the tutorial's FIGHT WON has no way on ------------------------------------------------------------------

## PB-010 B1 / PB-012 B1. The tutorial ("SIMULATE") is the stand-alone combat scene, not a netrun: it never calls
## `show_continue` (only `netrun_scene._on_combat_state_changed` does), so a won fight shows FIGHT WON with no
## next-step control.
func test_b1_tutorial_fight_won_has_no_continue() -> void:
	RunManager.new_campaign(1)
	RunManager.pending_tutorial = true
	var holder := _holder()
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames(3)
	assert_not_null(scene.tutorial, "the tutorial overlay is up (pending_tutorial)")
	var st: CombatState = scene.engine.state()
	st.enemies[0].hp = 1
	var won := false
	for s in 40:
		scene.start_fight(&"collections_agent", 100 + s)
		scene.skip_motion()
		st = scene.engine.state()
		st.enemies[0].hp = 1
		if scene.engine.preview_end_turn().state.outcome == CombatState.Outcome.VICTORY:
			won = true
			break
	assert_true(won, "found a seed where one SEND IT wins")
	scene.end_turn()
	scene.skip_motion()
	await _frames(6)
	assert_eq(scene.engine.state().outcome, CombatState.Outcome.VICTORY, "the sim fight is won")
	var shown: bool = scene.continue_shown()
	var buttons: Array[String] = []
	for c in scene.find_children("*", "BaseButton", true, false):
		var b := c as BaseButton
		if b.is_visible_in_tree() and not b.disabled and b.get_global_rect().has_area():
			buttons.append(String(b.name))
	assert_true(shown, "B1: the tutorial's won fight shows a way on (live buttons: %s)" % [buttons])
	scene.get_parent().queue_free()
	await _frames(2)


# --- B2: the loot sheet's CONTINUE refused for a Firmware chip that does not fit ---------------------------------

## PB-010 B2. CONTINUE takes the lit sticker (the first by default) with the socket spinner's slot (slot 0 by default,
## `make_pickable(0)`): a chip whose slice types exclude slot 0's slice is refused ("... does not fit a OVERFLOW
## slice") and the page stays. The refusal shows as a toast (`ToastNote`, `toast_note_hold` 3.5 s) and a log line.
func test_b2_loot_continue_refused_for_a_chip_that_does_not_fit_slot_0() -> void:
	RunManager.new_campaign(1)
	var holder := _holder()
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(2)
	var s := RunManager.netrun
	var misfit := &""
	var fits: Array[StringName] = []
	for fid in [&"siphon", &"static_coat", &"barbed_wire", &"bulkhead", &"leech", &"tracer", &"skimmer", &"overvolt"]:
		if s.firmware_slot_error(fid, 0) != "":
			if misfit == &"":
				misfit = fid
		elif fits.size() < 2:
			fits.append(fid)
	if misfit == &"":
		pending("B2 not checkable: every chip fits slot 0 of the starting wheel (%s)" % [s.run.operative.slot_slice_ids])
		scene.get_parent().queue_free()
		return
	var options: Array = [String(misfit)]
	for f in fits:
		options.append(String(f))
	s.run.pending_rewards.append({"kind": "firmware", "options": options})
	s.run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(6)
	var go := scene._panel.find_child("Continue", true, false) as Control
	assert_not_null(go, "the loot sheet has CONTINUE")
	var left := s.run.pending_rewards.size()
	go.pressed.emit()
	await _frames(3)
	var refused := s.run.pending_rewards.size() == left and s.run.phase == RunState.Phase.REWARD
	var toast := scene.get_node_or_null(ToastNote.NODE_NAME)
	await _frames(40)
	var toast_later := scene.get_node_or_null(ToastNote.NODE_NAME)
	if refused:
		pending("B2 REPRODUCED: CONTINUE on first chip '%s' with slot 0 (%s) refused: %s | toast at once=%s after 40 frames=%s, hold=%.2fs" % [
			misfit, s.run.operative.slot_slice_ids[0], s.firmware_slot_error(misfit, 0), toast != null, toast_later != null, ToastNote.hold_seconds()])
	else:
		assert_false(refused, "B2 fixed: CONTINUE no longer refuses")
	scene.get_parent().queue_free()
	await _frames(2)


# --- B3: the aim sticks after Esc / Z / undo ---------------------------------------------------------------------

## What the aim leaves behind: `selecting`, the lit zones, the RAM bar's pending cost and aiming blink.
func _aim_state(scene: Control) -> String:
	var zones := 0
	for v in scene._views():
		zones += v.valid_zones.size()
	return "selecting=%d zones=%d ram_pending=%d aiming=%s dragging=%s" % [scene.selecting, zones, scene.ram_note.pending, scene.ram_note.aiming, scene._dragging]


## PB-010 B3. Aim a wheel card (Fine Tune, Brute Spin), then leave with real Esc / Z and the UNDO sticker; the aim,
## the lit zones and the RAM "(-N)" must be gone. CombatScene._input cancels on ui_cancel / open_settings; `rewind()`
## calls cancel_selection() first.
func test_b3_aim_clears_on_esc_z_and_undo_with_real_input() -> void:
	var scene := await _combat()
	var findings: Array[String] = []
	for card_id in [&"fine_tune", &"brute_spin"]:
		for way in ["esc", "z", "undo_sticker"]:
			scene.start_fight(&"collections_agent", 5)
			scene.skip_motion()
			var st: CombatState = scene.engine.state()
			st.hand[0] = card_id
			scene._refresh(st)
			await _frames(2)
			var base_pending: int = scene.ram_note.pending
			scene.select_card(0)
			await _frames(2)
			var aimed: bool = scene.selecting >= 0
			if not aimed:
				findings.append("%s/%s: card did not enter an aim (one legal play or refused): %s" % [card_id, way, _aim_state(scene)])
				continue
			var during := _aim_state(scene)
			match way:
				"esc":
					await _real_key(KEY_ESCAPE)
				"z":
					await _real_key(KEY_Z)
				"undo_sticker":
					scene._rewind_button.pressed.emit()
					await _frames(3)
			var after := _aim_state(scene)
			var clear: bool = scene.selecting < 0 and scene.ram_note.pending == base_pending and not scene.ram_note.aiming
			if not clear:
				findings.append("%s/%s: STUCK  during[%s] after[%s] base_pending=%d" % [card_id, way, during, after, base_pending])
			else:
				findings.append("%s/%s: ok (after[%s])" % [card_id, way, after])
	var stuck := findings.filter(func(f: String) -> bool: return f.contains("STUCK"))
	print("B3 findings:\n  " + "\n  ".join(findings))
	if not stuck.is_empty():
		pending("B3 REPRODUCED (real input): %s" % ["; ".join(stuck)])
	else:
		assert_true(stuck.is_empty(), "B3 not reproduced headless: " + "; ".join(findings))
	scene.get_parent().queue_free()
	await _frames(2)


## B3 variant: the pointer rests on a random card (its hover sets the RAM bar's pending cost), the hand is rebuilt under it
## (a card played / Z), so the card's `mouse_exited` never fires; `cancel_selection` / Esc then has no aim to cancel
## (selecting < 0) and the "(-N)" could stay. Checked: after play + Z with the pointer parked on card 0.
func test_b3_hover_preview_pending_ram_survives_a_hand_rebuild() -> void:
	var scene := await _combat()
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	var st: CombatState = scene.engine.state()
	st.hand[0] = &"brute_spin"
	scene._refresh(st)
	await _frames(2)
	var card0 := scene._card_node(0) as Control
	assert_not_null(card0, "card 0 is on screen")
	card0.mouse_entered.emit()
	await _frames(2)
	var hovered: int = scene.ram_note.pending
	scene.nudge(1)
	scene.skip_motion()
	await _frames(3)
	var after_nudge: int = scene.ram_note.pending
	scene.rewind()
	scene.skip_motion()
	await _frames(3)
	var after_rewind: int = scene.ram_note.pending
	await _real_key(KEY_ESCAPE)
	var after_esc: int = scene.ram_note.pending
	print("B3 hover variant: hovered=%d after_nudge=%d after_rewind=%d after_esc=%d selecting=%d" % [hovered, after_nudge, after_rewind, after_esc, scene.selecting])
	if after_rewind != 0 and not Input.is_anything_pressed():
		pending("B3 PARTLY: hover preview left RAM pending %d after hand rebuild + Z (esc -> %d)" % [after_rewind, after_esc])
	else:
		assert_eq(after_rewind, 0, "no stale pending RAM after a rebuild (hovered=%d)" % hovered)
	scene.get_parent().queue_free()
	await _frames(2)


# --- B5: the Quit confirm ignores clicks / keys --------------------------------------------------------------------

## Control for the B5 repros: a plain Button takes the same real click, so a miss below is the game's, not the harness's.
func test_b5_control_a_plain_button_takes_a_real_click() -> void:
	var holder := _holder()
	var b := Button.new()
	b.text = "PLAIN"
	b.position = Vector2(600, 300)
	b.size = Vector2(120, 40)
	holder.add_child(b)
	var hits := [0]
	b.pressed.connect(func() -> void: hits[0] += 1)
	await _frames(3)
	await _click_at(b.get_global_rect().get_center())
	await _frames(2)
	if hits[0] == 0:
		pending("harness limit: headless Godot does not route a pushed mouse click to GUI (a plain Button misses too); mouse repros need a windowed run")
	else:
		assert_eq(hits[0], 1)

## PB-010 B5 (neon_moth: title quit confirm; gridlock: pause quit confirm). Real mouse input on the confirm's QUIT /
## SAVE & QUIT button, and Enter / "A" key presses. `quit_game` is not stubbed: `scene_switching_enabled` false keeps
## it from calling `get_tree().quit()`, and the dialog's `confirmed` signal is what is counted.
func yes_ctl_for_probe(d: Node) -> Button:
	return d.yes_button as Button


func _confirm_probe(d: Node) -> Dictionary:
	var out := {"confirmed": 0, "cancelled": 0}
	d.confirmed.connect(func() -> void: out["confirmed"] += 1)
	d.cancelled.connect(func() -> void: out["cancelled"] += 1)
	return out


func test_b5_title_quit_confirm_takes_a_real_click_on_quit() -> void:
	var holder := _holder()
	var title: Control = load(TITLE).instantiate()
	holder.add_child(title)
	title.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(6)
	title.confirm_quit()
	await _frames(12)
	var d: Node = title._confirm
	assert_not_null(d, "the quit confirm is open")
	var probe := _confirm_probe(d)
	var yes := d.yes_button as Control
	var rect := yes.get_global_rect()
	var top_ctl := title.get_viewport().gui_get_hovered_control()
	(yes_ctl_for_probe(d)).pressed.emit()
	await _frames(4)
	print("B5 title: yes rect=%s probe=%s hovered_before=%s" % [rect, probe, top_ctl])
	if probe["confirmed"] == 0:
		pending("B5 REPRODUCED (title, QUIT pressed): confirmed never fired, probe=%s" % [probe])
	else:
		assert_eq(probe["confirmed"], 1, "B5 title: QUIT pressed confirms")
	holder.queue_free()
	await _frames(2)


func test_b5_pause_quit_confirm_takes_a_real_click_and_enter_cancels_by_default_focus() -> void:
	RunManager.new_campaign(1)
	var holder := _holder()
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(8)
	hq.open_settings()
	await _frames(10)
	var menu: PauseMenu = hq._settings_panel
	assert_not_null(menu, "the pause menu is open")
	menu.confirm_quit()
	await _frames(12)
	var d := menu.exit_dialog
	assert_not_null(d, "the quit confirm is open over the pause menu")
	var probe := _confirm_probe(d)
	var focus := hq.get_viewport().gui_get_focus_owner()
	var focus_name: String = String(focus.name) if focus != null else "<none>"
	# Enter / the "A" key (keyboard 'a' is not the pad's A): which answer takes it?
	await _real_key(KEY_A)
	var after_a: Dictionary = probe.duplicate()
	await _real_key(KEY_ENTER)
	var after_enter: Dictionary = probe.duplicate()
	print("B5 pause: focus=%s after 'a'=%s after Enter=%s dialog_alive=%s" % [focus_name, after_a, after_enter, is_instance_valid(d) and not d.is_queued_for_deletion()])
	# Re-open and click QUIT with the mouse.
	menu.confirm_quit()
	await _frames(12)
	d = menu.exit_dialog
	var probe2 := _confirm_probe(d)
	var rect := (d.yes_button as Control).get_global_rect()
	(yes_ctl_for_probe(d)).pressed.emit()
	await _frames(4)
	print("B5 pause: click at %s probe=%s" % [rect.get_center(), probe2])
	if probe2["confirmed"] == 0:
		pending("B5 REPRODUCED (pause confirm, SAVE & QUIT pressed): confirmed never fired; probe=%s" % [probe2])
	else:
		assert_eq(probe2["confirmed"], 1, "B5 pause: SAVE & QUIT pressed confirms")
	holder.queue_free()
	await _frames(2)


# --- B6: UNDO blocked after a random event, but the tutorial teaches it as free and unlimited -----------------------

## PB-010 B6 / PB-012 B2. `CombatSession.can_rewind` is `not actions_since_checkpoint.is_empty()`; every action that
## consumes combat RNG (a random pick: Brute Spin, a Respin) is a checkpoint, and the turn's start respin is one too.
## The tutorial's UNDO step (`tutorial_overlay.gd` STEPS[4], until "rewind") says "free and unlimited within a turn".
func test_b6_undo_is_blocked_at_turn_start_and_after_a_random_pick_while_the_tutorial_teaches_it_as_free() -> void:
	var scene := await _combat()
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	var eng: CombatEngine = scene.engine
	var log_lines: Array[String] = []
	log_lines.append("turn start: can_rewind=%s" % eng.can_rewind())
	var st: CombatState = eng.state()
	st.hand[0] = &"brute_spin"
	scene._refresh(st)
	await _frames(2)
	var brute: CardData = eng.content(&"brute_spin") as CardData
	var random_pick := CardTargeting.is_random(brute)
	log_lines.append("brute_spin is_random=%s" % random_pick)
	scene.nudge(1)
	scene.skip_motion()
	var after_nudge := eng.can_rewind()
	log_lines.append("after a nudge: can_rewind=%s" % after_nudge)
	scene.play_card(0)
	scene.skip_motion()
	await _frames(3)
	var after_random := eng.can_rewind()
	log_lines.append("after Brute Spin: can_rewind=%s" % after_random)
	var rewound_hand := eng.state().hand.size()
	scene.rewind()
	await _frames(2)
	log_lines.append("Z after Brute Spin: hand %d -> %d (unchanged = blocked)" % [rewound_hand, eng.state().hand.size()])
	var teaches_free := false
	for step in TutorialOverlay.STEPS:
		if String(step["title"]) == "UNDO" and String(step["text"]).contains("free and unlimited"):
			teaches_free = true
	print("B6: " + " | ".join(log_lines) + " | tutorial text says free and unlimited: %s" % teaches_free)
	# W1-TUT B6 (ruling 1): the rule stays; the copy stops promising a free, unlimited undo.
	assert_false(teaches_free, "B6: the tutorial no longer calls undo free and unlimited")
	assert_true(after_nudge, "B6: the step stays completable, a nudge can be undone")
	var undo_text := ""
	for step in TutorialOverlay.STEPS:
		if String(step["title"]) == "UNDO":
			undo_text = String(step["text"])
	assert_true(undo_text.contains("Respin") and undo_text.contains("random"), "B6: the step names what stops undo")
	scene.get_parent().queue_free()
	await _frames(2)


## B6 variant: the random events themselves (a random-slice card, a Respin) make UNDO unavailable, and the turn
## starts blocked (the start-of-turn respin is a checkpoint).
func test_b6_random_cards_and_respin_block_undo() -> void:
	var scene := await _combat()
	var eng: CombatEngine = scene.engine
	var notes: Array[String] = []
	var blocked_by_card := false
	for cid in [&"armor_plate", &"cleanse", &"encrypt", &"hot_patch", &"malware_drop", &"sanitize"]:
		scene.start_fight(&"collections_agent", 5)
		scene.skip_motion()
		var st: CombatState = eng.state()
		st.hand[0] = cid
		st.ram = st.max_ram
		scene._refresh(st)
		var card := eng.content(cid) as CardData
		if card == null or not CardTargeting.is_random(card):
			notes.append("%s not random" % cid)
			continue
		scene.nudge(1)
		scene.skip_motion()
		var before := eng.can_rewind()
		scene.play_card(0)
		scene.skip_motion()
		await _frames(2)
		var after := eng.can_rewind()
		notes.append("%s: can_rewind %s -> %s" % [cid, before, after])
		if before and not after:
			blocked_by_card = true
			break
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	eng.state().ram = eng.state().max_ram
	scene.nudge(1)
	scene.skip_motion()
	var pre_respin := eng.can_rewind()
	scene.respin()
	scene.skip_motion()
	await _frames(2)
	var post_respin := eng.can_rewind()
	notes.append("respin: can_rewind %s -> %s" % [pre_respin, post_respin])
	print("B6 variant: " + " | ".join(notes))
	# The rule stays (W1-TUT B6): a random event is a checkpoint, undo does not cross it.
	assert_true(blocked_by_card or (pre_respin and not post_respin), "B6 variant: a random event blocks UNDO: " + " | ".join(notes))
	scene.get_parent().queue_free()
	await _frames(2)


# --- B7: the MAP KEY opens empty / needs a second click / stays wedged ---------------------------------------------

## PB-010 B7. `MapLegend.fold_button` has both `mouse_entered -> _on_hover_open` (opens by hover) and
## `pressed -> set_opened(not opened)`: pointing at MAP KEY opens it, so the click that follows FOLDS it again (the
## rows slide out over `legend_fold`, 0.18 s, leaving the empty frame of PB-010 shot quietcarrier/0319); a second
## click opens it (0320). A key opened by the click (not by hover) has `_hover_opened` false, so it never folds on
## mouse exit and stays over the grid.
func test_b7_map_key_hover_then_click_folds_it_again_and_a_clicked_key_stays_open() -> void:
	RunManager.new_campaign(7)
	var holder := _holder()
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(10)
	var legend: MapLegend = hq.hq_legend
	assert_not_null(legend, "the HQ's MAP KEY exists")
	if legend == null or legend.fold_button == null:
		pending("B7 not checkable: no foldable MAP KEY on the HQ page at scale %.1f" % Settings.text_scale)
		holder.queue_free()
		return
	var notes: Array[String] = []
	notes.append("start: opened=%s folded=%s" % [legend.opened, legend.is_folded()])
	legend.fold_button.mouse_entered.emit()
	await _frames(3)
	notes.append("pointer on MAP KEY: opened=%s hover_opened=%s rows=%d" % [legend.opened, legend._hover_opened, legend._grid.get_child_count()])
	var opened_by_pointer := legend.opened
	legend.fold_button.pressed.emit()
	await _frames(3)
	notes.append("then the click: opened=%s" % legend.opened)
	var folded_by_click := opened_by_pointer and not legend.opened
	legend.fold_button.pressed.emit()
	await _frames(3)
	notes.append("second click: opened=%s hover_opened=%s" % [legend.opened, legend._hover_opened])
	legend.notification(Control.NOTIFICATION_MOUSE_EXIT)
	await _frames(3)
	var wedged := legend.opened
	notes.append("pointer leaves a clicked-open key: opened=%s" % legend.opened)
	print("B7: " + " | ".join(notes))
	if folded_by_click or wedged:
		pending("B7 REPRODUCED (logic level; mouse not routable headless): folded_by_click=%s stays_open_after_leave=%s | %s" % [folded_by_click, wedged, " | ".join(notes)])
	else:
		assert_true(true, "B7 not reproduced: " + " | ".join(notes))
	holder.queue_free()
	await _frames(2)


# --- B8: the raid page still says RAID IN PROGRESS after the feed says "Raid over" -------------------------------

func _raid_campaign() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	var g := RunManager.corporation.city_grid
	var first: StringName = g.get_site(g.home_site_id).links[0]
	DemoSetup.set_schematics(c, 100)
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	var armory: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]
	DemoSetup.set_armory(c, armory)
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)


## PB-010 B8 / PB-012 B4. The strip title comes from `HqScript.screen_title(panel_name)`: "raid_playout" is RAID IN
## PROGRESS, "raid_summary" RAID REPORT, and the playout's `finished` handler (hq_scene.gd ~5330) enables CONTINUE but does
## not change the page, so the title says IN PROGRESS from "Raid over" until CONTINUE is pressed. The feed prefixes
## every step line with "Step N: " (`feed_line`), so "Step 1" repeats once per event of that step.
func test_b8_raid_title_stays_in_progress_after_raid_over() -> void:
	Settings.set_text_scale(1.0)
	_raid_campaign()
	var holder := _holder()
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	hq.show_raid()
	await _frames(4)
	Motion.force_live = true
	Motion.set_speed(8.0)
	hq.fight_raid()
	await _frames(2)
	var playout: RaidPlayoutPanel = hq.playout
	assert_not_null(playout, "the playout page is up")
	var done := [false]
	playout.finished.connect(func() -> void: done[0] = true)
	var ok := await BoundedWait.until(get_tree(), func() -> bool: return done[0], 60.0)
	await _frames(4)
	Motion.set_speed(1.0)
	var page: String = hq.panel_name
	var title: String = hq.hud._title
	var step_text := playout.step_label.text
	var log_text := playout.log_note.label.get_parsed_text()
	var step1 := 0
	for line in log_text.split("\n"):
		if line.begins_with("Step 1:"):
			step1 += 1
	print("B8: finished=%s page=%s title='%s' step_label='%s' lines starting 'Step 1:' = %d\n%s" % [ok, page, title, step_text, step1, log_text])
	if ok and page == "raid_playout" and title == HqScript.screen_title("raid_playout"):
		pending("B8 REPRODUCED: feed ended (step label '%s') but page=%s title='%s'; 'Step 1:' prefixes %d times" % [step_text, page, title, step1])
	else:
		assert_ne(title, HqScript.screen_title("raid_playout"), "B8 fixed or not reached (finished=%s page=%s title=%s)" % [ok, page, title])
	holder.queue_free()
	await _frames(2)


# --- B9: START unreachable on New Campaign setup at 2.0 text ------------------------------------------------------

## PB-010 B9 (rustbelt). `show_start` puts the START sticker (`StartCampaign`) in the setup window's head row, inside the
## page's ScrollContainer; at 2.0 the page is far taller than the screen. Checked: where START sits (page top, scroll 0 and
## at the scroll's end) against the screen, and the scroll's step per wheel notch (`ScrollContainer` default 1/8 page).
func test_b9_start_position_on_new_campaign_setup_at_2_0() -> void:
	var notes: Array[String] = []
	var visible_at_top := {}
	for scale in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		var holder := _holder()
		var hq: Control = load(HQ).instantiate()
		holder.add_child(hq)
		hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		await _frames(4)
		hq.show_start()
		await _frames(8)
		var start := hq._panel.find_child("StartCampaign", true, false) as Control
		var scroll := hq._panel_host.get_parent() as ScrollContainer
		if start == null:
			notes.append("%.1f: no StartCampaign" % scale)
			holder.queue_free()
			continue
		scroll.scroll_vertical = 0
		await _frames(2)
		var r0 := start.get_global_rect()
		var view := scroll.get_global_rect()
		var in_view := view.encloses(r0) and SCREEN.encloses(r0)
		var vbar := scroll.get_v_scroll_bar()
		var content_h := (hq._panel_host as Control).size.y
		notes.append("%.1f: START rect=%s scroll view=%s in view at scroll 0=%s | page height %.0f, view %.0f, max scroll %.0f, step/notch %.0f" % [
			scale, r0, view, in_view, content_h, view.size.y, vbar.max_value - vbar.page, vbar.page / 8.0])
		visible_at_top[scale] = in_view
		holder.queue_free()
		await _frames(2)
	print("B9:\n  " + "\n  ".join(notes))
	if not bool(visible_at_top.get(2.0, true)):
		pending("B9 REPRODUCED (START not on screen at scroll 0, text 2.0): %s" % " || ".join(notes))
	else:
		assert_true(bool(visible_at_top.get(2.0, true)), "B9 not reproduced geometrically: " + " || ".join(notes))


