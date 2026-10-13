extends GutTest
## Change plan 1, W1 review R1 (R1-MISC): New Campaign shows one START (pinned at 2.0, inside the safe margin), the
## loot note of a refused Firmware take stays clear of the sheet / FIRMWARE DROP / CONTINUE and inside the safe margin,
## and the enemy precision tag's tooltip says it is the position after the hovered play.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w1r1_misc"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
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


func _holder() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	return holder


## Every visible "START" sticker under `root` (the campaign's verb, by its node name).
func _starts(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in root.find_children("StartCampaign", "", true, false):
		var c := n as Control
		if c != null and c.is_visible_in_tree():
			out.append(c)
	return out


func test_new_campaign_shows_one_start_and_the_pinned_one_keeps_the_safe_margin() -> void:
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
		var starts := _starts(hq)
		assert_eq(starts.size(), 1, "text %.1f: one START on New Campaign" % scale)
		if starts.size() == 1:
			var r := starts[0].get_global_rect()
			if scale >= 2.0:
				assert_eq(String(starts[0].get_parent().name), "StartBar", "2.0: START is the pinned one")
				assert_true(Fx.sticker_safe_rect(SCREEN).encloses(r), "2.0: the pinned START (%s) is inside the safe rect %s" % [r, Fx.sticker_safe_rect(SCREEN)])
			else:
				assert_eq(String(starts[0].get_parent().name), "PageHead", "%.1f: START stays in the head" % scale)
		holder.queue_free()
		await _frames(2)


func test_refused_firmware_note_is_one_named_message_clear_of_the_sheet_skip_and_continue() -> void:
	for scale in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(7)
		var holder := _holder()
		var scene: Control = load(NETRUN).instantiate()
		holder.add_child(scene)
		scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		scene.start_run(1)
		await _frames(2)
		var s := RunManager.netrun
		var options: Array = ["barbed_wire", "bulkhead", "burner"]
		s.run.pending_rewards.append({"kind": "firmware", "options": options})
		s.run.phase = RunState.Phase.REWARD
		scene._show_current()
		PageTransition.settle(scene)
		await _frames(6)
		var refused := false
		for k in s.run.operative.slot_slice_ids.size():
			for i in options.size():
				if not refused and s.firmware_slot_error(StringName(options[i]), k) != "":
					scene.choose_reward(i, k)
					refused = true
		assert_true(refused, "a chip that does not fit some slot exists to be refused")
		# the note stays well past a toast's hold (visible N frames later), nothing else says it
		await _frames(400)
		assert_null(scene._panel.find_child("LootNote", true, false), "%.1f: no second (pencil / red) line beside CONTINUE" % scale)
		assert_null(scene.find_child("Toast", true, false), "%.1f: no second (timed) toast" % scale)
		var toast := scene._panel.find_child("RefusalNote", true, false) as ToastNote
		assert_not_null(toast, "%.1f: the one message is the terminal note, still there" % scale)
		if toast == null:
			holder.queue_free()
			continue
		assert_true(toast.is_visible_in_tree(), "%.1f: visible 400 frames later" % scale)
		var text := toast.label.text
		assert_false(text.contains("_"), "%.1f: names, never ids: %s" % [scale, text])
		assert_true(text.contains("Slot ") and text.contains("It fits Slot"), "%.1f: says where it fits: %s" % [scale, text])
		assert_true(toast.whole(), "%.1f: every line shows" % scale)
		var ref := Label.new()
		scene._panel.add_child(ref)
		assert_eq(toast.label.get_theme_font_size("font_size"), ref.get_theme_font_size("font_size"), "%.1f: body text size, not shrunk" % scale)
		ref.queue_free()
		var nr := toast.get_global_rect()
		var safe := Fx.sticker_safe_rect(SCREEN)
		assert_true(safe.encloses(nr), "%.1f: the note %s is inside the safe rect %s" % [scale, nr, safe])
		for node_name in ["LootSheet", "FirmwareDrop", "Skip", "Continue"]:
			var other := scene._panel.find_child(node_name, true, false) as Control
			assert_not_null(other, "%s exists" % node_name)
			if other != null:
				assert_false(nr.intersects(other.get_global_rect()), "%.1f: the note %s does not cover %s %s" % [scale, nr, node_name, other.get_global_rect()])
		# choosing a slot is acting: the note goes
		var mini := _find_mini(scene._panel)
		if mini != null:
			mini.choose(mini.selected())
			assert_null(scene._panel.find_child("RefusalNote", true, false), "%.1f: the note clears once the player acts" % scale)
		holder.queue_free()
		await _frames(2)


func test_enemy_tag_tooltip_says_after_this_play() -> void:
	RunManager.new_campaign(1)
	var holder := _holder()
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames()
	var st: CombatState = scene.engine.state()
	var view: WheelView = scene._enemy_views[st.enemies[0].id]
	var tip := String(scene.hud_layer.row_for(view).tooltip_text)
	assert_true(tip.contains(tr(WheelView.TAG_AFTER_TIP)), "the tag's tooltip says it is the position after this play: %s" % tip)
	assert_true(tip.to_lower().contains("after this play"), "the tooltip carries 'after this play'")


func _find_mini(n: Node) -> SpinnerMini:
	if n is SpinnerMini:
		return n as SpinnerMini
	for c in n.get_children():
		var f := _find_mini(c)
		if f != null:
			return f
	return null
