extends GutTest
## Horizontal pass 24, combat (GAP_ANALYSIS H24): every drawn combat word translates (the
## slice and aim words, "YOU", SEND IT, RAM, the Heat poster); the status line and the aim
## hint fit at big text; what block soaked is shown beside a loss.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _text_scale_before: float = 1.0
var _translation: Translation = null
var _locale_before := ""


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_pass24"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if _translation != null:
		TranslationServer.remove_translation(_translation)
		_translation = null
		TranslationServer.set_locale(_locale_before)
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(false)
	Dialogue.clear()
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


## A throwaway catalogue in a locale of its own ("xx"): the English catalogue holds the
## same keys and would answer first.
func _translate(pairs: Dictionary) -> void:
	_locale_before = TranslationServer.get_locale()
	TranslationServer.set_locale("xx")
	_translation = Translation.new()
	_translation.locale = "xx"
	for k in pairs:
		_translation.add_message(String(k), String(pairs[k]))
	TranslationServer.add_translation(_translation)


func test_slice_and_aim_words_translate() -> void:
	var words := {}
	for w in Palette.SLICE_WORDS.values():
		words[w] = "XX_" + String(w)
	for w in Palette.TIER_WORDS.values():
		words[w] = "YY_" + String(w)
	words["YOU"] = "XX_YOU"
	_translate(words)
	var scene := await _combat()
	var s: CombatState = scene.engine.state()
	var title: String = scene._landing_title(s, s.player)["text"]
	assert_string_contains(title, "XX_", "slice word translated: %s" % title)
	assert_string_contains(title, "YY_", "aim word translated: %s" % title)
	for part in title.split(" "):
		assert_false(Palette.SLICE_WORDS.values().has(part), "no English slice word left: %s" % title)
	var res: CombatResult = scene.engine.preview_end_turn()
	var after: CombatState = res.resolved_state if res.resolved_state != null else res.state
	var o := CombatOutcome.between(s, after, res.events)
	for e in s.enemies:
		for chip in scene._chips_for(o, e.id, s):
			assert_false(String(chip["text"]).contains(" YOU "), "YOU goes through the translation: %s" % chip["text"])


func test_drawn_kit_words_translate() -> void:
	_translate({"SEND IT": "XX_SEND", "RAM %d/%d": "XX_RAM %d/%d", "HEAT": "XXHEAT", "WANTED": "XX_WANTED"})
	assert_eq(String(TranslationServer.translate("SEND IT")), "XX_SEND", "the drip text takes the translation")
	var scene := await _combat()
	# The RAM bar and the Heat poster draw from tr(): their node's tr() gives the key's text.
	assert_eq(scene.ram_note.tr("RAM %d/%d") % [3, 12], "XX_RAM 3/12")
	assert_eq(scene.heat_poster.tr("HEAT"), "XXHEAT")
	assert_true("XXHEAT".length() <= HeatPoster.RANSOM_LETTERS_MAX, "a short word keeps every strip")


func test_the_status_line_fits_its_width_at_big_text() -> void:
	Settings.set_pad_active(true)
	var scene := await _combat(&"compliance_officer", Settings.TEXT_SCALE_MAX)
	scene._refresh_status()
	await _frames(2)
	var st: Label = scene._status
	var fs := st.get_theme_font_size("font_size")
	var w := st.get_theme_font("font").get_string_size(st.text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
	assert_true(w <= st.size.x + 0.5 or fs <= scene.STATUS_MIN_FONT, "the line fits: %.0f in %.0f at %d px" % [w, st.size.x, fs])
	assert_eq(st.auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "built from translated parts, not translated twice")


func test_the_aim_hint_sits_above_the_ram_row_and_on_screen() -> void:
	for pad in [false, true]:
		Settings.set_pad_active(pad)
		var scene := await _combat(&"collections_agent", Settings.TEXT_SCALE_MAX)
		var s: CombatState = scene.engine.state()
		s.hand = [&"jolt", &"jolt"]
		s.ram = s.max_ram
		var none: Array[Dictionary] = []
		scene.engine.state_changed.emit(s, none)
		await _frames(2)  # the rebuilt hand settles, as it has before any player input
		scene.select_card(0)
		await _frames(1)
		if not scene._aim_hint.visible:
			continue
		var hint: Rect2 = scene._aim_hint.get_global_rect()
		var screen: Rect2 = scene.get_global_rect()
		assert_true(hint.end.x <= screen.end.x + 0.5 and hint.position.x >= screen.position.x - 0.5, "on screen (pad %s): %s" % [pad, hint])
		assert_true(hint.end.y <= scene.ram_note.get_global_rect().position.y + 0.5, "above the RAM row (pad %s): hint %s ram %s hand %s" % [pad, hint, scene.ram_note.get_global_rect(), scene._hand_box.get_global_rect()])
		scene.cancel_selection()


func test_soaked_damage_is_counted_and_shown() -> void:
	var scene := await _combat(&"compliance_officer")
	var s: CombatState = scene.engine.state()
	s.player.block = 50
	var res: CombatResult = scene.engine.preview_end_turn()
	var after: CombatState = res.resolved_state if res.resolved_state != null else res.state
	var o := CombatOutcome.between(s, after, res.events)
	var soaked := 0
	for e in res.events:
		if String(e.get("type", "")) == "damage" and StringName(String(e.get("target", ""))) == s.player.id:
			soaked += int(e.get("blocked", 0)) + int(e.get("shielded", 0))
	assert_eq(int(o.of(s.player.id)["soaked"]), soaked, "the outcome sums block and shield soak")
	var texts: Array = scene._chips_for(o, s.player.id, s).map(func(c: Dictionary) -> String: return String(c["text"]))
	if soaked > 0:
		assert_true(texts.has("%d BLOCKED" % soaked), "shown beside the loss: %s" % [texts])
	else:
		assert_false(texts.any(func(t: String) -> bool: return t.ends_with(" BLOCKED")), "nothing soaked, nothing shown")


func test_toasts_sit_in_the_right_column_off_the_cards() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		var s: CombatState = scene.engine.state()
		s.ram = 0
		var none: Array[Dictionary] = []
		scene.engine.state_changed.emit(s, none)
		await _frames(2)
		scene.respin()  # refused: not enough RAM
		await _frames(1)
		assert_true(scene.toast.visible, "a refusal shows")
		var t: Rect2 = scene.toast.get_global_rect()
		assert_true(scene._notes_area.get_global_rect().grow(1.0).encloses(t), "inside the right column at %.1f: %s vs %s" % [scale, t, scene._notes_area.get_global_rect()])
		for card in scene._hand_box.get_children():
			assert_false(t.intersects((card as Control).get_global_rect()), "off the cards at %.1f" % scale)
		assert_eq(scene.layout_violations(), [], "and off the wheels")


func test_the_aim_line_draws_under_the_wheels() -> void:
	var scene := await _combat()
	var root_index := -1
	for child in scene.get_children():
		if child is VBoxContainer:
			root_index = child.get_index()
			break
	assert_true(scene._aim_line.get_index() < root_index, "under the UI root (the wheels' HP and NEXT stay on top)")


func test_the_nearest_arrow_or_satellite_takes_the_click() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		for v in scene._views():
			var wv: WheelView = v
			for rot in 30:
				wv.combatant.wheel.rotation = rot
				for ar in wv.arrows():
					var z := wv.zone_at(wv.arrow_center(int(ar["ring"]), int(ar["direction"])))
					assert_eq(String(z.get("kind", "")), "arrow", "an arrow's centre is its arrow (%s rot %d %.1f)" % [wv.combatant.display_name, rot, scale])
					assert_eq(int(z.get("ring", -1)), int(ar["ring"]), "and its own ring")
					assert_eq(int(z.get("direction", 0)), int(ar["direction"]), "and its own way")
				for sat in wv.satellites:
					assert_eq(String(wv.zone_at(wv._satellite_pos(sat)).get("kind", "")), "satellite", "a token's centre is the token")


func test_satellite_tokens_and_plates_keep_off_hp_next_and_last_turn() -> void:
	for enemy in [&"collections_agent", &"geostationary_guard", &"care_swarm"]:
		for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
			var scene := await _combat(enemy, scale)
			scene.end_turn()  # a LAST TURN line and (with a preview) a NEXT plate
			await _frames(1)
			for v in scene._enemy_views.values():
				var host: WheelView = v
				host.outcome = {"hp_after": maxi(0, host.combatant.hp - 7)}
				for rot in 30:
					host.combatant.wheel.rotation = rot
					var blocks: Array[Rect2] = host._hp_block_rects()
					for sat in host.satellites:
						var tr_ := _token_rect(host, sat)
						var plate := host.satellite_plate_rect(sat, "%d >%d" % [sat.hp, sat.hp])
						for b in blocks:
							assert_false(tr_.intersects(b), "%s rot %d %.1f: token off %s" % [enemy, rot, scale, b])
							assert_false(plate.intersects(b), "%s rot %d %.1f: plate off %s" % [enemy, rot, scale, b])


func _token_rect(host: WheelView, sat: CombatantState) -> Rect2:
	var r := WheelView.SATELLITE_TOKEN * WheelView._ts()
	var c := host._satellite_pos(sat) - host.global_position
	return Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)


func test_last_turn_never_draws_smaller_than_at_normal_text() -> void:
	var scene := await _combat(&"compliance_officer", Settings.TEXT_SCALE_MAX)
	var v: WheelView = scene._player_view
	# A usual line keeps at least the 1.0 size; the longest possible one stays in its view.
	v.last_turn = "LAST TURN: -11 HP · 3 BLOCKED · +5 BLOCK · GOT CORRUPTED"
	var lay := v.hp_layout()
	assert_true(int(lay["last_fs"]) >= WheelView.HUB_FONT_SIZE, "a usual line keeps the 1.0 size: %d" % int(lay["last_fs"]))
	v.last_turn = "LAST TURN: -11 HP · +3 AT TURN START · 5 BLOCKED · +5 BLOCK · +2 SHIELD · GOT CORRUPTED · GUARD +3 BLOCK · ENCRYPTED STOPPED 1"
	lay = v.hp_layout()
	assert_true((lay["last_lines"] as PackedStringArray).size() <= WheelView.LAST_TURN_LINES, "on at most two lines")
	assert_true((lay["last"] as Rect2).end.y <= v.size.y + 0.5, "inside its view")


func test_guard_block_counts_on_the_host_line() -> void:
	var scene := await _combat(&"collections_agent")
	var s: CombatState = scene.engine.state()
	var host: CombatantState = null
	var guard: CombatantState = null
	for e in s.enemies:
		if e.is_satellite:
			guard = e
		elif host == null:
			host = e
	assert_not_null(guard, "the drone")
	var events: Array[Dictionary] = [{"type": "block", "target": guard.id, "amount": 3}]
	var lines: Dictionary = load(SCENE).instantiate().get_script().last_turn_lines(s, s.duplicate_state(), events)
	assert_string_contains(String(lines[guard.host_id if guard.host_id != &"" else host.id]), "GUARD +3 BLOCK")


func test_signed_numbers_avoid_the_plus_format() -> void:
	var script: Script = load(SCENE).instantiate().get_script()
	assert_eq(script.signed(3), "+3")
	assert_eq(script.signed(-2), "-2")
	assert_eq(script.signed(0), "0")
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	var rx := RegEx.create_from_string("(tr|translate)\\(\"[^\"]*%\\+d")
	assert_null(rx.search(src), "no translated key uses %+d")


func test_long_hub_names_take_two_lines_before_shrinking() -> void:
	var scene := await _combat(&"compliance_officer", Settings.TEXT_SCALE_MAX)
	var v: WheelView = scene._player_view
	var lines: Array = v.hub_name_lines(60.0)
	assert_true(int(lines[0]) >= WheelView.NAME_FONT_SIZE or lines.size() == 3 or not v.shown_name().contains(" "), "two lines before going under the 1.0 size: %s" % [lines])


func test_a_capped_shield_event_reports_the_shield_gained() -> void:
	var scene := await _combat()
	var s: CombatState = scene.engine.state()
	var fx: EffectInterpreter = scene.engine.resolver.fx
	var cap: int = fx.config.shield_cap
	s.player.shield = cap - 2
	var events: Array[Dictionary] = []
	fx.gain_shield(s.player, 5, events)
	assert_eq(s.player.shield, cap)
	assert_eq(int(events[0]["amount"]), 2, "the event says what was gained")
	var before := s.duplicate_state()
	before.player.shield = cap - 2
	var line: String = load(SCENE).instantiate().get_script().last_turn_lines(before, s, events)[s.player.id]
	assert_string_contains(line, "+2 SHIELD")


func test_toasts_and_stickers_translate_exactly_once() -> void:
	_translate({"UNDO": "XX_UNDO", "RESPIN %d RAM": "XX_RESPIN %d"})
	var scene := await _combat()
	scene._refresh_key_hints()
	var undo: StickerButton = scene._stickers["undo"]
	assert_true(undo.shown_text().begins_with("XX_UNDO"), "sticker label translated: %s" % undo.shown_text())
	assert_true(undo.pre_translated, "and not again by the sticker")
	assert_eq(scene.toast.label.auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "toast text arrives translated")


func test_a_hovered_card_names_itself_on_the_wheel_it_acts_on() -> void:
	var scene := await _combat()
	var s: CombatState = scene.engine.state()
	s.hand = [&"jolt"]
	s.ram = s.max_ram
	var none: Array[Dictionary] = []
	scene.engine.state_changed.emit(s, none)
	await _frames(1)
	scene._preview_card(0)
	var found := false
	for v in scene._views():
		var chips: Array = (v as WheelView).intent.get("chips", [])
		if not chips.is_empty() and String(chips[0]["text"]).begins_with("IF "):
			found = true
			assert_string_contains(String(chips[0]["text"]), "JOLT")
	assert_true(found, "one wheel's tag starts with IF JOLT")


func test_last_turn_shows_the_ram_a_turn_brings_back() -> void:
	var before := CombatState.new()
	var p := CombatantState.new()
	p.id = &"player"
	p.is_player = true
	before.player = p
	before.ram = 6
	var after := before.duplicate_state()
	after.ram = 10
	var none: Array[Dictionary] = []
	var line: String = load(SCENE).instantiate().get_script().last_turn_lines(before, after, none)[&"player"]
	assert_string_contains(line, "RAM +4")


func test_the_hub_says_how_the_fight_is_won_and_the_tag_explains_the_dots() -> void:
	var scene := await _combat()
	var enemy: WheelView = scene._enemy_views.values()[0]
	var tip := enemy._get_tooltip(enemy._center())
	assert_string_contains(tip, "to 0 to win")
	assert_string_contains(scene._chips_tooltip([{"text": "X"}]), "perfect aim")


func test_a_test_run_never_touches_the_players_settings_file() -> void:
	assert_true(Settings.is_test_run(), "this is a GUT run")
	assert_ne(Settings.path, Settings.PATH, "settings live in this run's own file")
	assert_string_contains(Settings.path, str(OS.get_process_id()))
