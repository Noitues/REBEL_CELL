extends GutTest
## B5c (art director, after B5b): every sticker on a page stays inside the safe margin (Fx.STICKER_SAFE_MARGIN, 24 px
## x text scale) from the screen's edges: on loot FIGHT WON touched the left edge and CONTINUE ran off the right one.
## Checked on the loot, event, title, pause, campaign slots and raid setup pages at text 1.0 / 1.6 / 2.0
## (Fx.stickers_outside_safe: the shared rule next to the SAVED stamp's clearance).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const TITLE := "res://scenes/menu/title_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const SLOTS: Array[String] = ["1", "2", "3"]

var _scale := 1.0


func before_each() -> void:
	_scale = Settings.text_scale
	Motion.force_live = false


func after_each() -> void:
	Settings.set_text_scale(_scale)
	for s in SLOTS:
		RunManager.save_slot = s
		RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _holder() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	return holder


func _assert_safe(root: Node, what: String, scale: float) -> void:
	var out := Fx.stickers_outside_safe(root, SCREEN)
	assert_eq(out, [], "%s at %.1f: every sticker %d px or more inside the screen's edges" % [what, scale, roundi(Fx.STICKER_SAFE_MARGIN * scale)])


func test_the_safe_margin_is_24_px_times_the_text_scale() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		assert_almost_eq(Fx.sticker_margin(), 24.0 * scale, 0.001)
		assert_eq(Fx.sticker_safe_rect(SCREEN), SCREEN.grow(-24.0 * scale))
	var edge := VerbSticker.new("EDGE", VerbSticker.Fill.PINK, 30)
	var h := _holder()
	h.add_child(edge)
	edge.position = Vector2(2, 300)
	await _frames(2)
	assert_eq(Fx.stickers_outside_safe(h, SCREEN).size(), 1, "a sticker on the edge is found")


func _netrun() -> Control:
	var scene: Control = load(NETRUN).instantiate()
	_holder().add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	return scene


func test_loot_and_event_stickers_keep_the_safe_margin() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		for kind in ["card", "firmware"]:
			var scene := _netrun()
			await _frames(2)
			var run := RunManager.netrun.run
			run.pending_rewards.append({"kind": kind, "options": ["twist", "jam", "cache"] if kind == "card" else ["barbed_wire", "bulkhead", "burner"]})
			run.phase = RunState.Phase.REWARD
			scene._show_current()
			PageTransition.settle(scene)
			await _frames(4)
			_assert_safe(scene, "loot (%s)" % kind, scale)
			scene.get_parent().queue_free()
			await _frames(1)
		var ev := _netrun()
		await _frames(2)
		DemoSetup.open_event(RunManager.netrun, &"ev_leash_on_the_floor")
		ev._show_current()
		PageTransition.settle(ev)
		await _frames(4)
		_assert_safe(ev, "event", scale)
		ev.get_parent().queue_free()
		await _frames(1)


func test_title_and_slots_stickers_keep_the_safe_margin() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		for s in SLOTS:
			RunManager.save_slot = s
			RunManager.new_campaign(int(s))
			RunManager.autosave()
		RunManager.save_slot = "gut_b5c"
		RunManager.campaign = null
		var t: Control = load(TITLE).instantiate()
		_holder().add_child(t)
		await _frames(4)
		_assert_safe(t, "title", scale)
		t.show_slots()
		await _frames(4)
		_assert_safe(t, "campaign slots", scale)
		t.get_parent().queue_free()
		await _frames(1)


func test_pause_stickers_keep_the_safe_margin() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		# As the game opens it: over the HQ, centred under the subtitle band.
		RunManager.new_campaign(1)
		var hq: Control = load(HQ).instantiate()
		_holder().add_child(hq)
		hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		await _frames(4)
		hq.open_settings()
		await _frames(4)
		assert_not_null(hq._settings_panel, "the pause menu is open")
		_assert_safe(hq._settings_panel, "pause", scale)
		hq.get_parent().queue_free()
		await _frames(1)
		RunManager.reset()


func test_raid_setup_stickers_keep_the_safe_margin() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var c := RunManager.campaign
		CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
		var hq: Control = load(HQ).instantiate()
		_holder().add_child(hq)
		hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		await _frames(4)
		hq.show_raid()
		await _frames(6)
		_assert_safe(hq, "raid setup", scale)
		hq.get_parent().queue_free()
		await _frames(1)
		RunManager.reset()
