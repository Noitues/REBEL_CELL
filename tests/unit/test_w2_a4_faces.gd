extends GutTest
## Plan 1 W2-A4: card and chip faces say what they do and when they cannot (6A), every card says its
## direction and tick distance, and an event that rewards a Daemon shows the Daemon's icon and tooltip
## (R4). Offers and rules are unchanged: only the words and the chips.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale: float
var _pad: bool


func before_each() -> void:
	_scale = Settings.text_scale
	_pad = Settings.pad_active
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w2_a4"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.pad_active != _pad:
		Settings.set_pad_active(_pad)
	Motion.force_live = false
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _content(klass: StringName) -> Array:
	var lookup := RunManager.lookup()
	var out: Array = []
	for id in lookup.ids_of_class(klass):
		out.append(lookup.get_content(id))
	return out


func test_a_card_that_needs_the_inner_ring_says_so() -> void:
	var needing := 0
	for c: CardData in _content(&"CardData"):
		var says := FaceText.card_text(c).contains(TranslationServer.translate(FaceText.NEEDS_INNER))
		assert_eq(says, FaceText.needs_inner_ring(c), "%s: the condition is on its face exactly when it needs the inner ring" % c.id)
		needing += 1 if says else 0
	assert_gt(needing, 0, "some cards need the inner ring")
	assert_true(FaceText.card_text(RunManager.lookup().get_content(&"ring_tap") as CardData).contains("inner ring"), "Ring Tap")
	# a card with no such effect keeps its own words
	var jolt := RunManager.lookup().get_content(&"jolt") as CardData
	assert_eq(FaceText.card_text(jolt), TextDb.t(jolt, "description"))


func test_a_chip_limited_to_slice_types_names_them() -> void:
	var lookup := RunManager.lookup()
	assert_true(FaceText.offer_text(lookup.get_content(&"static_coat")).ends_with("Fits DEFRAG slices only."), "Static Coat")
	assert_true(FaceText.offer_text(lookup.get_content(&"siphon")).ends_with("Fits SHIM slices only."), "Siphon")
	assert_true(FaceText.offer_text(lookup.get_content(&"overvolt")).ends_with("Fits SHIM or OVERFLOW slices only."), "Overvolt")
	assert_eq(FaceText.fits_text(lookup.get_content(&"patch_plus")), "", "a chip that fits any slice says nothing")
	for fw: FirmwareData in _content(&"FirmwareData"):
		assert_eq(FaceText.offer_text(fw).contains("Fits"), not fw.allowed_slice_types.is_empty(), "%s: the limit is stated exactly when there is one" % fw.id)


func test_every_spin_and_move_says_its_direction_and_distance() -> void:
	for c: CardData in _content(&"CardData"):
		var d := TextDb.t(c, "description")
		assert_false(d.contains("+-"), "%s: no ASCII plus-minus" % c.id)
		for e in c.effects:
			if e != null and e.type == RC.EffectType.SPIN and e.amount != 0 and d.contains("tick"):
				assert_true(d.contains("clockwise"), "%s: a spin of fixed direction says it" % c.id)
				assert_eq(d.contains("counter-clockwise"), e.amount < 0, "%s: and says the right one" % c.id)
				assert_true(d.contains(str(absi(e.amount))), "%s: and the distance" % c.id)


func test_the_plus_minus_sign_is_in_the_face_font() -> void:
	assert_true(Palette.body().has_char(0xB1), "the card body type draws the plus-minus sign")


func test_faces_hold_the_whole_text_at_every_text_size() -> void:
	# the loot card, with the condition on it, at 1.0 / 1.6 / 2.0 (the A4 words must not overflow)
	var loot: Vector2 = load("res://scripts/ui/netrun_scene.gd").LOOT_CARD
	var lookup := RunManager.lookup()
	for scale in TestScope.scales(SCALES):
		for c: CardData in _content(&"CardData"):
			var z := ZineCard.new(TextDb.t(c, "display_name"), c.ram_cost, FaceText.card_text(c), 0).with_card(c)
			z.size = loot * scale
			z.fit_whole = true
			z.body_floor = ZineCard.FIT_MIN_TEXT
			autofree(z)
			assert_true(z.text_whole(), "loot x%.1f %s: every word on the face" % [scale, c.id])
		for fw: FirmwareData in _content(&"FirmwareData"):
			var z := ZineCard.new(TextDb.t(fw, "display_name"), -1, FaceText.offer_text(fw), 0).as_offer("firmware", "chip_%s" % fw.id)
			z.size = loot * scale
			z.fit_whole = true
			z.body_floor = ZineCard.FIT_MIN_TEXT
			autofree(z)
			assert_true(z.text_whole(), "loot x%.1f %s: every word on the chip's face" % [scale, fw.id])
	assert_not_null(lookup)


func _daemon_event() -> TerminalEventData:
	return RunManager.lookup().get_content(&"ev_daemon_broker") as TerminalEventData


func test_an_event_daemon_reward_shows_its_icon_and_tooltip() -> void:
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		RunManager.reset()
		var holder: Control = add_child_autofree(Control.new())
		holder.size = SCREEN.size
		var scene: Control = load(NETRUN).instantiate()
		holder.add_child(scene)
		scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		scene.new_campaign(1)
		scene.start_run(1)
		await _frames(2)
		var run := RunManager.netrun.run
		run.cycles = 999
		run.event_id = &"ev_daemon_broker"
		run.phase = RunState.Phase.EVENT
		scene._show_current()
		await _frames(4)
		var ev := _daemon_event()
		var daemon: DaemonData = ev.choices[0].reward as DaemonData
		var choice := scene._panel.find_child("Choice1", true, false) as Button
		var row := choice.get_node(^"OutcomeRow") as OutcomeRow
		var reward: Dictionary = {}
		for it in row.items:
			if StringName(it["kind"]) == StatIcon.DAEMON:
				reward = it
		assert_false(reward.is_empty(), "x%.1f: the Daemon is a chip on the choice" % scale)
		assert_eq(String(reward.get("art", "")), "daemon_%s" % daemon.id, "x%.1f: the chip wears that Daemon's own icon" % scale)
		# (the tooltip is folded to a width: compare the words)
		var words := " ".join(choice.tooltip_text.split("\n", false))
		assert_true(words.contains(TextDb.t(daemon, "description")),"x%.1f: the sticker's tooltip says what the Daemon does" % scale)
		assert_eq(row.tooltip_text, choice.tooltip_text, "x%.1f: the icons give the sticker's tooltip" % scale)
		assert_ne(row.mouse_filter, Control.MOUSE_FILTER_IGNORE, "x%.1f: and can be hovered" % scale)
		var rect := row.get_global_rect()
		assert_true(SCREEN.grow(1.0).encloses(rect), "x%.1f: the chips stay on the screen (%s)" % [scale, rect])
		holder.queue_free()
		await _frames(2)
		RunManager.reset()
