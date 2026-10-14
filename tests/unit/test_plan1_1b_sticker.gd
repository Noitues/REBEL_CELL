extends GutTest
## Plan 1 wave 1b, 1B-STICKER (PT-002a F1, F2, F4, F5, F8), on the real netrun scene at text 1.0 / 1.6 / 2.0.
## Headless drops pushed mouse events, so hover is the handlers called directly (`grow_hover`, `mouse_entered`).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale := 1.0
var _system_log := false


func before_each() -> void:
	_scale = Settings.text_scale
	_system_log = Settings.system_log
	AudioDirector.muted = true
	Motion.force_live = false
	RunManager.save_slot = "gut_plan1_1b_sticker"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Settings.set_text_scale(_scale)
	Settings.set_system_log(_system_log)
	Motion.force_live = false
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true
	RunManager.reset()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _loot(kind: String, scale: float) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(2)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": kind, "options": ["twist", "jam", "cache"] if kind == "card" else ["barbed_wire", "bulkhead", "burner"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	scene.open_reward(0)  # ruling 3 (2026-10-14): a single pick shows the list first
	PageTransition.settle(scene)
	await _frames(8)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)
	RunManager.reset()


# --- F1: the focus fold has a corner to cut, beside the word ------------------------------------------------------

## The fold removes the corner where (distance in from the right edge) + (distance down from the top) is under
## `peel_px`. A word sticker's die-cut ran only round its letters, so its fold room was empty air and the fold cut
## nothing: the tab the room draws (`fold_room_rect`) stands inside that corner, and the flap covers it.
func test_f1_the_fold_cuts_a_drawn_corner_beside_the_word() -> void:
	for scale in TestScope.scales(SCALES):
		var scene := await _loot("card", scale)
		var go := scene._panel.find_child("Continue", true, false) as HoloSticker
		assert_not_null(go, "x%.1f: CONTINUE" % scale)
		var v := go.sticker
		var tab := v.fold_room_rect()
		assert_true(tab.has_area(), "x%.1f: the fold room is a drawn tab" % scale)
		assert_true(v.body_rect.encloses(tab), "x%.1f: the tab is inside the sticker body" % scale)
		var cut := tab.grow(v.edge())  # with its die-cut edge
		var in_x := v.body_rect.end.x - cut.end.x
		var in_y := cut.position.y - v.body_rect.position.y
		assert_lt(in_x + in_y, v.peel_px(), "x%.1f: the fold reaches the tab's corner (%.1f + %.1f < %.1f)" % [scale, in_x, in_y, v.peel_px()])
		assert_gt(tab.size.x + v.edge(), 0.0, "x%.1f: a tab with width" % scale)
		await _close(scene)


# --- F2: SKIP is a verb sticker like CONTINUE --------------------------------------------------------------------

func test_f2_skip_has_no_icon_over_its_letters_and_keeps_its_fold_room() -> void:
	for scale in TestScope.scales(SCALES):
		var scene := await _loot("card", scale)
		var skip := scene._panel.find_child("Skip", true, false) as HoloSticker
		assert_not_null(skip, "x%.1f: SKIP" % scale)
		assert_null(skip.get_node_or_null(^"IconMark"), "x%.1f: no '>>' mark over the S" % scale)
		assert_true(skip.sticker.fold_room_rect().has_area(), "x%.1f: SKIP has its fold room" % scale)
		assert_gte(skip.room_past_last_letter(), skip.sticker.peel_px(), "x%.1f: the fold stays past the last letter" % scale)
		await _close(scene)


# --- F4: a hovered reward card stays whole under the page's clip --------------------------------------------------

func test_f4_a_grown_reward_card_stays_inside_the_page() -> void:
	for scale in TestScope.scales(SCALES):
		var scene := await _loot("card", scale)
		var top: float = scene._page_top()
		for c in scene._panel.find_children("*", "ZineCard", true, false):
			var card := c as ZineCard
			card.grow_hover(true)
			await _frames(3)
			await BoundedWait.until(get_tree(), func() -> bool: return is_equal_approx(card.hover_scale, card.hover_target()), BoundedWait.motion_limit([&"card_hover"]))
			var xf := card.get_global_transform()
			var foot_y := (xf * Vector2(0.0, card.size.y)).y
			var drawn_top := foot_y - card.size.y * card.hover_scale * absf(xf.get_scale().y) - card.lift
			assert_gte(drawn_top + 0.5, top, "x%.1f: the grown card's top (%.1f) is under the page's clip (%.1f)" % [scale, drawn_top, top])
			assert_gt(card.hover_scale, 1.0, "x%.1f: it still grows" % scale)
			card.grow_hover(false)
		await _close(scene)


# --- F5: the loot page keeps SKIP / CONTINUE / DECK on the screen --------------------------------------------------

func _inside_room(scene: Control, what: String) -> void:
	var host := scene._panel_host.get_parent() as Control
	var room := host.get_global_rect()
	for n in ["Skip", "Continue", "DeckCount"]:
		var c := scene._panel.find_child(n, true, false) as Control
		if c == null:
			continue
		var r := c.get_global_rect()
		assert_lte(r.end.y, minf(room.end.y, SCREEN.end.y) + 0.5, "%s: %s is not cut off (bottom %.1f, room %.1f)" % [what, n, r.end.y, room.end.y])


func test_f5_the_loot_foot_is_on_screen_and_stays_after_the_room_shrinks() -> void:
	for scale in TestScope.scales(SCALES):
		for kind in ["card", "firmware"]:
			var scene := await _loot(kind, scale)
			_inside_room(scene, "%s x%.1f" % [kind, scale])
			# the room under the bar shrinks (the system log's 110 px, a taller subtitle band): the page fits again
			Settings.set_system_log(true)
			await _frames(8)
			_inside_room(scene, "%s x%.1f, system log on" % [kind, scale])
			Settings.set_system_log(false)
			await _frames(8)
			scene.subtitle_strip.set_lines(2)
			await _frames(8)
			_inside_room(scene, "%s x%.1f, 2-line subtitle band" % [kind, scale])
			await _close(scene)


# --- F8: a won fight leaves by the player's press, never by the clock --------------------------------------------

func test_f8_a_won_fight_waits_for_the_loot_press() -> void:
	Settings.set_text_scale(1.0)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(2)
	var s := RunManager.netrun
	scene.enter_node(s.available_nodes()[0])
	await _frames(3)
	var guard := 0
	while s.run.phase == RunState.Phase.COMBAT and guard < 60 and scene.combat_scene != null:
		s.combat.state.player.hp = s.combat.state.player.max_hp
		CombatFixture.land(s.combat.state.player, 0)
		for i in range(s.combat.state.hand.size() - 1, -1, -1):
			if i < s.combat.state.hand.size():
				scene.combat_scene.play_card(i)
		scene.combat_scene.end_turn()
		guard += 1
	assert_ne(s.run.phase, RunState.Phase.COMBAT, "the fight is won")
	assert_true(scene.combat_scene != null and scene.combat_scene.continue_shown(), "LOOT / CONTINUE shows")
	var gone := await BoundedWait.until(get_tree(), func() -> bool: return scene.combat_scene == null, Motion.seconds(&"combat_end_hold") * 2.0 + BoundedWait.SLACK)
	assert_false(gone, "F8: past the hold the fight still shows (nothing opened the loot sheet)")
	assert_not_null(scene._panel.find_child("Continue", true, false), "the fight's step is still on screen")
	scene.combat_scene.call(&"_continue_pressed")
	var moved := await BoundedWait.until(get_tree(), func() -> bool: return scene.combat_scene == null, BoundedWait.motion_limit([&"combat_end_hold"]))
	assert_true(moved, "F8: the press moves on")
	await _close(scene)
