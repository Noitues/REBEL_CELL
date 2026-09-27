extends GutTest
## Horizontal pass 23, combat (GAP_ANALYSIS H23): a subtitle on screen survives the dock
## moving; the status line names one nudge pair and says what the switches switch to; a
## respin says where it landed; RESPIN names its RAM; LAST TURN counts block, shield and
## statuses; a hit on your wheel reads as damage taken; the folded chip says MORE; the
## wheel centre moves up for the room below; satellite tokens keep off the HP block.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_pass23"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(false)
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(enemy: StringName = &"collections_agent", scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, 5)
	await _frames()
	return scene


func test_a_line_on_screen_survives_the_dock_moving() -> void:
	Dialogue.say(0, "Keep the Heat down and bank at the first Rack. The collectors are already on their way.")
	await _frames(2)
	Dialogue.dock_at(Rect2(900, 120, 300, 400), 3)
	await _frames(2)
	assert_gt(Dialogue.text_label.size.y, 0.0, "docked in a column: the words have height")
	Dialogue.dock_default()
	await _frames(2)
	assert_gt(Dialogue.text_label.size.y, 0.0, "back in the strip: still not an empty box")
	assert_ne(Dialogue.text_label.get_parsed_text(), "")


func test_the_status_line_names_one_nudge_pair() -> void:
	var scene := await _combat(&"compliance_officer")
	var text: String = scene._status.text
	var pair := "%s/%s NUDGE YOUR WHEEL" % [Settings.key_text(&"nudge_left"), Settings.key_text(&"nudge_right")]
	assert_string_contains(text, pair)
	assert_string_contains(text, "%s: NUDGE THE TARGET" % Settings.key_text(&"toggle_nudge_wheel"))
	assert_false(text.contains("YOURS"), "no bare toggle state: %s" % text)
	var own: CombatantState = scene.engine.state().player
	assert_eq(text.contains("RING"), own.wheel.has_inner_ring(), "the ring switch only where there is an inner ring: %s" % text)
	scene.toggle_nudge_wheel()
	assert_string_contains(scene._status.text, "NUDGE THE TARGET")
	assert_string_contains(scene._status.text, "%s: NUDGE YOUR WHEEL" % Settings.key_text(&"toggle_nudge_wheel"))


func test_a_respin_says_where_it_landed_and_what_it_cost() -> void:
	var scene := await _combat()
	var s: CombatState = scene.engine.state()
	s.ram = s.max_ram
	var none: Array[Dictionary] = []
	scene.engine.state_changed.emit(s, none)
	assert_string_contains((scene._respin_button as StickerButton).text, "RAM", "RESPIN names its cost's unit")
	var before: String = scene._landing_title(scene.engine.state(), scene.engine.state().player)["text"]
	scene.respin()
	var after: String = scene._landing_title(scene.engine.state(), scene.engine.state().player)["text"]
	var note: String = scene.toast.text()
	assert_string_contains(note, "RESPIN -")
	assert_string_contains(note, after, "it names the new landing")
	assert_eq(note.ends_with("AGAIN"), before == after, "AGAIN exactly when it landed the same: %s" % note)
	assert_false(scene.toast.refusal, "a note, not a refusal mark")


func test_last_turn_counts_block_shield_and_statuses() -> void:
	var before := CombatState.new()
	var p := CombatantState.new()
	p.id = &"player"
	p.is_player = true
	p.hp = 60
	p.max_hp = 60
	before.player = p
	var after := before.duplicate_state()
	var events: Array[Dictionary] = [
		{"type": "block", "target": &"player", "amount": 5},
		{"type": "shield", "target": &"player", "amount": 2},
		{"type": "status", "target": &"player", "slot": 1, "status": RC.Status.CORRUPTED},
		{"type": "status_absorbed", "target": &"player", "slot": 2, "status": RC.Status.CORRUPTED},
	]
	var line: String = load(SCENE).instantiate().get_script().last_turn_lines(before, after, events)[&"player"]
	assert_string_contains(line, "+5 BLOCK")
	assert_string_contains(line, "+2 SHIELD")
	assert_string_contains(line, "GOT CORRUPTED")
	assert_string_contains(line, "ENCRYPTED STOPPED 1")
	assert_false(line.contains("NO CHANGE"))


func test_a_hit_on_your_wheel_reads_as_damage_taken() -> void:
	for enemy in [&"collections_agent", &"claims_adjuster", &"compliance_officer"]:
		var scene := await _combat(enemy)
		var res: CombatResult = scene.engine.preview_end_turn()
		var after: CombatState = res.resolved_state if res.resolved_state != null else res.state
		var o := CombatOutcome.between(scene.engine.state(), after, res.events)
		var chips: Array = scene._chips_for(o, &"player", scene.engine.state())
		for chip in chips:
			var t := String(chip["text"])
			assert_false(RegEx.create_from_string("^-\\d+ HP$").search(t) != null, "no bare '-N HP' chip: %s" % t)
		var d := o.of(&"player")
		if not d.is_empty() and int(d["hp_after"]) < int(d["hp_before"]):
			var texts: Array = chips.map(func(c: Dictionary) -> String: return String(c["text"]))
			assert_true(texts.has("YOU TAKE %d HP" % (int(d["hp_before"]) - int(d["hp_after"]))), "%s: %s" % [enemy, texts])


func test_the_folded_chip_says_more() -> void:
	var scene := await _combat(&"collections_agent", Settings.TEXT_SCALE_MAX)
	var v: WheelView = scene._player_view
	var many: Array = []
	for i in 12:
		many.append({"text": "CHIP NUMBER %d" % i, "color": Palette.INK, "ink": Palette.PAPER})
	v.intent = {"type": -1, "text": "TEST", "chips": many, "tooltip": "all of them"}
	var rows: Array = v._chip_rows()
	var last: Array = rows[rows.size() - 1]
	assert_true(String(last[last.size() - 1]["text"]).ends_with(" MORE"), "folded chip: %s" % last[last.size() - 1]["text"])


func test_the_wheel_centre_leaves_room_for_the_hp_block() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"compliance_officer", scale)
		for v in [scene._player_view] + scene._enemy_views.values():
			var wv: WheelView = v
			assert_true(wv._center().y + wv._radius() + WheelView._bottom_need() <= wv.size.y + 0.5,
				"%.1f: the HP number and LAST TURN fit under %s" % [scale, wv.combatant.display_name])


func test_satellite_tokens_keep_off_the_hp_block() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		var host: WheelView = scene._enemy_views.values()[0]
		for rot in 30:
			host.combatant.wheel.rotation = rot
			for sat in host.satellites:
				var sp := host._satellite_pos(sat)
				var below := sp.y > host.global_center().y + host._radius()
				if below:
					assert_true(absf(sp.x - host.global_center().x) >= WheelView.HP_BLOCK_HALF * WheelView._ts(),
						"rot %d at %.1f: the token sits beside the HP block" % [rot, scale])


func test_satellite_hp_plates_keep_clear_of_the_tag() -> void:
	for enemy in [&"collections_agent", &"geostationary_guard", &"care_swarm"]:
		for scale in [1.3, Settings.TEXT_SCALE_MAX]:
			var scene := await _combat(enemy, scale)
			for v in scene._enemy_views.values():
				var host: WheelView = v
				var tag := host._intent_rect_local()
				for rot in 30:
					host.combatant.wheel.rotation = rot
					for sat in host.satellites:
						var plate := host.satellite_plate_rect(sat, "%d >%d" % [sat.hp, sat.hp])
						assert_false(tag.has_area() and plate.intersects(tag), "%s rot %d at %.1f: the HP plate is clear of the tag" % [enemy, rot, scale])


func test_combat_words_go_through_the_translation() -> void:
	var t := Translation.new()
	# A locale of its own (H24 S1: the English catalogue now carries these keys too and
	# would answer first for "en").
	var locale_before := TranslationServer.get_locale()
	t.locale = "xx"
	TranslationServer.set_locale("xx")
	t.add_message("NO CHANGE", "XX_NO_CHANGE")
	t.add_message("LAST TURN: ", "XX_LAST: ")
	t.add_message("TURN %d · FREE NUDGE %d", "XX_TURN %d XX_FREE %d")
	t.add_message("YOUR WHEEL", "XX_YOURS")
	TranslationServer.add_translation(t)
	var before := CombatState.new()
	var p := CombatantState.new()
	p.id = &"player"
	p.is_player = true
	before.player = p
	var none: Array[Dictionary] = []
	var line: String = load(SCENE).instantiate().get_script().last_turn_lines(before, before.duplicate_state(), none)[&"player"]
	var scene := await _combat(&"compliance_officer")
	scene._refresh_status()
	var status: String = scene._status.text
	TranslationServer.remove_translation(t)
	TranslationServer.set_locale(locale_before)
	assert_eq(line, "XX_LAST: XX_NO_CHANGE")
	assert_string_contains(status, "XX_TURN 1 XX_FREE")
	assert_string_contains(status, "XX_YOURS")
