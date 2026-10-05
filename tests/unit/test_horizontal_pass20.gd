extends GutTest
## Horizontal pass 20, combat (GAP_ANALYSIS H20 items 1-6, 8, 11, 12, 18-20 and the
## designer's list): cards are aimed by dragging or picking a target; every wheel has
## nudge arrows and a right nudge turns the wheel clockwise; the tags, HP arcs and RAM
## bar show the full outcome; refusals toast; the target is marked; hints follow the pad;
## the text scale reaches the tags, chips and cards; tooltips exist; the tutorial fits
## the new controls.

const SCENE := "res://scenes/combat/combat_scene.tscn"

## ANIM-R6 D9: every Settings value as found (the tutorial test sets tutorial_done).
var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_pass20"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	Settings.restore(_settings)
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


func _combat(enemy: StringName = &"compliance_officer", scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, 5)
	await _frames()
	return scene


## Puts `cards` in the hand with plenty of RAM and redraws.
func _hand(scene: Control, cards: Array[StringName]) -> void:
	var s: CombatState = scene.engine.state()
	s.hand = cards
	s.ram = s.max_ram
	var none: Array[Dictionary] = []
	scene.engine.state_changed.emit(s, none)


# --- Targeting ---------------------------------------------------------------------------

func test_a_nudge_card_offers_both_ways_on_every_wheel() -> void:
	var scene := await _combat()
	_hand(scene, [&"fine_tune"])
	var options := CardTargeting.options(scene.engine.resolver, scene.engine.state(), 0)
	var seen := {}
	for a in options:
		seen["%s:%d" % [a.wheel_id, a.direction]] = true
		assert_eq(scene.engine.validate(a), "", "every option is legal")
	assert_true(seen.has("player:1") and seen.has("player:-1"), "own wheel, both ways")
	assert_true(seen.has("%s:1" % scene.engine.state().target_id), "the enemy too")
	assert_eq(CardTargeting.options(scene.engine.resolver, scene.engine.state(), 0).size(), options.size(), "deterministic")


func test_a_chosen_slice_card_is_aimed_at_a_slice() -> void:
	var scene := await _combat()
	_hand(scene, [&"spawn_drone"])
	var options := CardTargeting.options(scene.engine.resolver, scene.engine.state(), 0)
	assert_true(options.size() > 1, "one option per slice")
	for a in options:
		assert_true(a.slot_index >= 0, "each names a slice")
	scene.select_card(0)
	assert_eq(scene.selecting, 0, "the card waits for its slice")
	assert_true(not scene._player_view.valid_zones.is_empty(), "slices light up as drop zones")
	assert_eq(String(scene._player_view.valid_zones[0]["kind"]), "slot")
	var hand: int = scene.engine.state().hand.size()
	scene._player_view.drag_dropped.emit({"kind": "slot", "slot": 2}, {"hand_index": 0})
	assert_eq(scene.engine.state().hand.size(), hand - 1, "dropping on a slice plays it there")


func test_click_then_target_and_keyboard_aim() -> void:
	var scene := await _combat()
	_hand(scene, [&"fine_tune", &"fine_tune"])
	scene.select_card(0)
	assert_eq(scene.selecting, 0)
	var first: CombatAction = scene.aimed_action()
	scene.step_selection(1)
	assert_ne(scene.aimed_action(), first, "arrows / Tab / D-pad walk the targets")
	var aimed: CombatAction = scene.aimed_action()
	var before: CombatState = scene.engine.state().duplicate_state()
	scene.confirm_selection()
	assert_eq(scene.selecting, -1)
	assert_eq(scene.engine.state().hand.size(), 1, "confirm plays the aimed option")
	var moved: CombatantState = scene.engine.state().get_combatant(aimed.wheel_id)
	var was := before.get_combatant(aimed.wheel_id)
	assert_true(moved.wheel.rotation != was.wheel.rotation or moved.wheel.inner_rotation != was.wheel.inner_rotation or moved.resistance < was.resistance, "the aimed wheel (or its inner ring) moved, or resistance absorbed it")
	scene.select_card(0)
	scene.cancel_selection()
	assert_eq(scene.engine.state().hand.size(), 1, "cancel plays nothing")


func test_dropping_a_nudge_card_on_an_arrow_sets_its_way() -> void:
	var scene := await _combat()
	_hand(scene, [&"fine_tune"])
	var rot: int = scene.engine.state().player.wheel.rotation
	scene._notification(Control.NOTIFICATION_DRAG_BEGIN)  # no drag data: ignored
	scene.select_card(0)
	scene._player_view.drag_dropped.emit({"kind": "arrow", "ring": RC.RingScope.OUTER, "direction": -1}, {"hand_index": 0})
	assert_true(scene.engine.state().player.wheel.rotation < rot, "the anticlockwise arrow turns it back")


func test_a_right_nudge_turns_the_wheel_clockwise() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var c: CombatantState = scene.engine.state().player
	# The slice one slice-width anticlockwise of the top arrives under the needle after a
	# +1 slice of rotation: the top of the wheel moves right, as a right nudge reads.
	var a := deg_to_rad(-90.0 - 60.0)
	var r := v._radius() - v._band() * 0.5
	var left_slot := v.slot_at_global(v.global_center() + Vector2(cos(a), sin(a)) * r)
	for i in c.wheel.ticks_per_slice():
		scene.nudge_wheel(&"player", 1)
	c = scene.engine.state().player
	assert_eq(WheelMath.slice_at(c.wheel.tick_at(0), c.wheel.slice_count), left_slot, "clockwise on screen")


func test_every_wheel_has_arrows_and_an_arrow_nudges() -> void:
	var scene := await _combat()
	var enemy: WheelView = scene._enemy_views.values()[0]
	assert_true(enemy.arrows().size() >= 2)
	assert_true(scene._player_view.arrows().size() >= 2)
	var rot: int = scene.engine.state().player.wheel.rotation
	scene._player_view.arrow_pressed.emit(RC.RingScope.OUTER, 1)
	assert_eq(scene.engine.state().player.wheel.rotation, rot + 1)
	var z: Dictionary = scene._player_view.zone_at(scene._player_view.arrow_center(RC.RingScope.OUTER, -1))
	assert_eq(String(z.get("kind", "")), "arrow", "the arrow is where it is drawn")
	assert_ne(scene._player_view._get_tooltip(scene._player_view.arrow_center(RC.RingScope.OUTER, -1) - scene._player_view.global_position), "", "arrows have tooltips")


# --- The outcome on screen -----------------------------------------------------------------

func test_the_tags_show_every_change_the_turn_brings() -> void:
	for enemy in [&"compliance_officer", &"collections_agent", &"dosage_dispenser"]:
		var scene := await _combat(enemy)
		for turn in 3:
			var state: CombatState = scene.engine.state()
			var preview: CombatResult = scene.engine.preview_end_turn()
			var o := CombatOutcome.between(state, preview.state, preview.events)
			for id in o.combatants:
				var d: Dictionary = o.combatants[id]
				var c := state.get_combatant(id)
				if c == null or not c.is_alive():
					continue
				var host: StringName = c.host_id if c.is_satellite else c.id
				var view: WheelView = scene._view_of(host)
				if view == null:
					continue
				var texts := PackedStringArray()
				for chip in view.intent.get("chips", []):
					texts.append(String(chip["text"]))
				var all := " ".join(texts)
				if not c.is_satellite and int(d["hp_after"]) != int(d["hp_before"]):
					# ANIM-R6 A4: a wheel's own HP change shows on its NEXT plate (the total), the
					# hits that cause it on the attacker's tag.
					assert_string_contains(all + " " + String(view.hp_layout()["next_text"]), "NEXT", "%s HP change shown" % c.display_name)
				if not c.is_satellite and int(d["block_after"]) != int(d["block_before"]):
					assert_string_contains(all, "BLOCK")
				if not (d["statuses"] as Array).is_empty():
					assert_true((view.outcome.get("statuses", []) as Array).size() > 0 or all.contains("RANDOM"), "status ghosts (or odds for a random pick) on %s" % c.display_name)
				if int(d["dealt"]) > 0:
					assert_string_contains(all, "HITS", "%s damage dealt shown" % c.display_name)
			scene.end_turn()
			if scene.engine.state().is_over():
				break


func test_campaign_effects_and_ram_are_chips() -> void:
	var scene := await _combat()
	var s: CombatState = scene.engine.state()
	var after := s.duplicate_state()
	after.ram += 2
	var events: Array[Dictionary] = [{"type": "campaign_effect", "effect": RC.EffectType.MODIFY_HEAT, "amount": 1}]
	var o := CombatOutcome.between(s, after, events)
	assert_eq(o.heat, 1)
	assert_eq(o.ram_delta, 2)
	var chips: Array = scene._chips_for(o, s.player.id, s)
	var texts := PackedStringArray()
	for c in chips:
		texts.append(String(c["text"]))
	var heat := HeatRules.scaled_delta(RunManager.campaign, 1, RunManager.config())
	assert_true(texts.has("HEAT %+d" % heat), "Heat as the campaign will apply it (%s)" % [texts])
	assert_true(texts.has("RAM +2"))


func test_card_hover_and_respin_show_on_screen() -> void:
	var scene := await _combat()
	_hand(scene, [&"jolt", &"reroll"])
	scene._preview_card(0)
	var chips: Array = scene._player_view.intent.get("chips", [])
	var ram_chip := false
	for c in chips:
		ram_chip = ram_chip or String(c["text"]).begins_with("RAM")
	assert_true(ram_chip or scene.ram_note.pending != 0, "the card's RAM cost is shown")
	scene._show_respin_odds()
	var texts := PackedStringArray()
	for c in scene._player_view.intent.get("chips", []):
		texts.append(String(c["text"]))
	assert_true(texts.has("RESPIN: ODDS"), "respin odds on the player's tag")
	scene._preview_card(1)
	var odds := false
	for v in scene._views():
		for c in v.intent.get("chips", []):
			odds = odds or String(c["text"]) == "RANDOM: ODDS"
	assert_true(odds, "a random card shows odds, not a roll")


func test_refusals_toast() -> void:
	var scene := await _combat()
	scene.engine.state().ram = 0
	scene.respin()
	assert_string_contains(scene.toast.text(), "RAM", "the refusal is on screen")
	assert_false(scene.toast.get_global_rect().intersects(scene._player_view.wheel_rect()), "over the hand, not a wheel")


func test_the_target_is_marked() -> void:
	var scene := await _combat(&"collections_agent")
	var s: CombatState = scene.engine.state()
	var host: WheelView = scene._enemy_views[s.target_id]
	assert_true(host.highlighted, "the target wears the crosshair")
	scene.cycle_target()
	s = scene.engine.state()
	var t := s.get_combatant(s.target_id)
	if t.is_satellite:
		assert_eq(scene._enemy_views[t.host_id].targeted_satellite, t.id, "a targeted satellite is marked on its host")


# --- Hints, text scale, tooltips, tutorial ---------------------------------------------------

func test_pad_players_see_pad_buttons() -> void:
	var scene := await _combat()
	Settings.set_pad_active(true)
	await _frames()
	assert_eq(scene._end_turn_button.key_hint, "[X]", "SEND IT names the pad button")
	assert_string_contains(scene._stickers["respin"].text, "[R3]")
	assert_string_contains(TutorialOverlay.step_text(3), "D-pad", "the tutorial speaks pad")
	Settings.set_pad_active(false)
	await _frames()
	assert_eq(scene._end_turn_button.key_hint, "[%s]" % Settings.key_text(&"end_turn"))


func test_the_text_scale_reaches_tags_chips_and_cards() -> void:
	var small := await _combat(&"compliance_officer", 1.0)
	var tag_small: float = small._player_view.intent_rect().size.y
	var big := await _combat(&"compliance_officer", Settings.TEXT_SCALE_MAX)
	assert_true(big._player_view.intent_rect().size.y > tag_small, "the tag grows with the text scale")
	var card: ZineCard = big._hand_box.get_child(0)
	assert_true(card.text_scale > 1.0, "hand cards scale their lettering")
	assert_eq(big.layout_violations(), [], "still nothing over a wheel at TEXT_SCALE_MAX")


func test_combat_controls_have_tooltips() -> void:
	var scene := await _combat()
	for c in [scene._end_turn_button, scene._stickers["respin"], scene._stickers["undo"], scene.heat_poster, scene.ram_note]:
		assert_ne((c as Control).tooltip_text, "", "%s has a tooltip" % c.name)
	assert_ne(scene._player_view._get_tooltip(scene._player_view.intent_rect().get_center() - scene._player_view.global_position), "", "the tag explains its chips")
	assert_eq(scene.ram_note.mouse_filter, Control.MOUSE_FILTER_PASS, "the RAM bar receives the mouse (tooltips need it)")


func test_the_tutorial_and_subtitles_share_the_right_column() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"compliance_officer", scale)
		scene.start_tutorial()
		Dialogue.say(RC.Voice.DISPATCH, "Runner, keep the needle off the Miss slice and bank the Rack before the audit lands.")
		await _frames()
		assert_eq(scene.layout_violations(), [], "tutorial and subtitles clear of every wheel and tag at %.1f" % scale)
		assert_false(scene.tutorial.get_global_rect().intersects(Rect2(Dialogue.bar.global_position, Dialogue.bar.size)), "the tutorial sits under the subtitles")
		assert_true(scene.tutorial.get_global_rect().end.x <= scene.get_global_rect().end.x + 0.5, "the tutorial stays on screen")
		assert_false(TutorialOverlay.step_text(4).contains("preview strip"), "no mention of the old preview strip")
		scene.tutorial.skip()
		Settings.set_tutorial_done(true)
		Dialogue.clear()


func test_pad_inspect_on_a_card_says_what_it_does() -> void:
	var scene := await _combat()
	var card: Control = scene._hand_box.get_child(0)
	var text: String = scene.inspect_at(card.get_global_rect().get_center())
	assert_ne(text, "", "the card is described")
	assert_true(scene.inspect_popup.visible, "beside the card")


func test_a_netrun_fight_shows_the_whole_hand_and_send_it_at_1_6() -> void:
	# Pass-20 P1 (a height test): at the largest text scale the fight inside a netrun keeps
	# every card and SEND IT on the 720-px canvas.
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load("res://scenes/netrun_map/netrun_scene.tscn").instantiate()
	holder.add_child(scene)
	scene.start_run(1)
	scene.enter_node(RunManager.netrun.available_nodes()[0])
	await _frames(6)
	var combat: Control = scene.combat_scene
	assert_not_null(combat, "the first node is a fight")
	if combat == null:
		return
	var bottom: float = holder.get_global_rect().end.y
	assert_true(combat._end_turn_button.get_global_rect().end.y <= bottom + 0.5, "SEND IT ends at %.0f" % combat._end_turn_button.get_global_rect().end.y)
	for c in combat._hand_box.get_children():
		assert_true((c as Control).get_global_rect().end.y <= bottom + 0.5, "a card ends at %.0f" % (c as Control).get_global_rect().end.y)
	assert_eq(combat.layout_violations(), [], "nothing over a wheel in the netrun at TEXT_SCALE_MAX")
