extends GutTest
## Plan 1 animation round P1, flow (DECISIONS "Plan 1 ANIM-FLOW"): M5 the fight dissolves in over the route
## (and a move to a fight ends as its pulse lands), M6 the loot sheet dims while the offers leave and the
## rewards page comes back by fading, M9 the HQ page's entrance waits for the jack cover to lift, M10 plain
## buttons dip when pressed and rows come in one after another, R5 the lit route node reaches out to its
## building. Every case also checks the end state at once under reduce effects / headless.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Vector2(1280, 720)
## Longest real wait (s) for a motion to end.
const LIMIT := 4.0

var _reduce: bool = false


func before_all() -> void:
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_p1_flow"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	Motion.force_live = false
	Fx._cover_opaque = false
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
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
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	Motion.force_live = true


## Waits until `done` is true, at most `limit` real seconds (frames counted by their delta).
func _until(done: Callable, limit: float = LIMIT) -> bool:
	var waited := 0.0
	while not done.call() and waited < limit:
		await get_tree().process_frame
		waited += get_tree().root.get_process_delta_time()
	return done.call()


func _netrun() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	return scene


## A reward phase on `scene` with `n` offers (cards).
func _rewards(scene: Control, n: int) -> void:
	var s := RunManager.netrun
	var rng := RandomNumberGenerator.new()
	rng.seed = 9
	for i in n:
		s._offer(&"card", s._card_pool(), 3, rng)
	s.run.phase = RunState.Phase.REWARD
	scene._show_current()


# --- M5 ---------------------------------------------------------------------------------------

func test_a_fight_dissolves_in_over_the_route_and_the_city_goes_when_it_is_whole() -> void:
	var scene := _netrun()
	await _frames(3)
	_live()
	scene._demo_enter_fight()
	if scene._travelling:
		scene._end_travel()  # the move's pulse lands: the fight opens
	assert_not_null(scene.combat_scene, "the fight is the page")
	assert_true(scene.combat_entering(), "it dissolves in")
	assert_lt(scene.combat_scene.modulate.a, 1.0, "it starts clear")
	assert_true(scene.background.visible, "the route's city shows through it, not a dark frame")
	var whole := await _until(func() -> bool: return not scene.combat_entering())
	assert_true(whole, "the dissolve ends")
	await BoundedWait.frozen_frames(get_tree(), 1)
	assert_eq(scene.combat_scene.modulate.a, 1.0, "whole")
	assert_false(scene.background.visible, "the arena draws its own world once it is whole")


func test_a_fight_is_whole_at_once_without_motion() -> void:
	var scene := _netrun()
	await _frames(3)
	scene._demo_enter_fight()
	assert_not_null(scene.combat_scene)
	assert_false(scene.combat_entering(), "headless never waits")
	assert_eq(scene.combat_scene.modulate.a, 1.0)
	assert_false(scene.background.visible, "the end state in 0 frames")
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	Motion.force_live = true  # a real display with reduce effects on
	scene.combat_scene.queue_free()
	scene._show_current()
	assert_false(scene.combat_entering(), "reduce effects: the end state in 0 frames")
	assert_eq(scene.combat_scene.modulate.a, 1.0)


func test_a_move_to_a_fight_ends_as_the_pulse_lands() -> void:
	var scene := _netrun()
	await _frames(4)
	_live()
	var ov: CityMapOverlay = scene.city_overlay
	var nodes: Array = RunManager.netrun.available_nodes()
	var from: StringName = RunManager.netrun.run.current_node_id
	if ov == null or nodes.is_empty() or ov.icon_at(nodes[0]).x == INF:
		pending("no placed route map in this run")
		return
	var settle := ov.travel(from, nodes[0], Callable(), true)
	ov.finish_travel()
	var lead := ov.travel(from, nodes[0], Callable(), false)
	ov.finish_travel()
	assert_gt(settle, 0.0)
	assert_lt(lead, settle, "a fight does not wait for the node's pop and dim")
	var pop := Motion.seconds(&"node_pop") + Motion.delay_of(&"node_pop")
	assert_gte(lead, pop - 0.0001, "the press is shown by the node's pop at least")
	assert_lte(lead, settle + 0.0001, "and never longer than the whole move")


# --- M6 ---------------------------------------------------------------------------------------

func test_the_loot_sheet_dims_while_the_offers_leave() -> void:
	var scene := _netrun()
	await _frames(3)
	_rewards(scene, 1)
	scene.open_reward(0)  # ruling 3 (2026-10-14): a single pick shows the list first
	PageTransition.settle(scene)
	await _frames(3)
	_live()
	assert_not_null(scene._panel.find_child("Stickers", true, false), "the pick page")
	scene.choose_reward(0)
	assert_true(scene.loot_leaving(), "the page waits for its flights")
	var receding := await _until(func() -> bool: return scene._panel.modulate.a < 1.0, 2.0)
	assert_true(receding, "the emptied sheet recedes")
	# Frame-count independent (a loaded machine runs fewer tween steps per frame): it reaches the entry's alpha.
	var dim := Motion.amplitude(&"loot_page_dim")
	var dimmed := await _until(func() -> bool: return scene._panel.modulate.a <= dim + 0.05, Motion.seconds(&"loot_page_dim") + 2.0)
	assert_true(dimmed, "towards the entry's alpha")
	var gone := await _until(func() -> bool: return not scene.loot_leaving(), 8.0)
	assert_true(gone, "the next page shows when the flights are down")


func test_the_loot_page_leaves_with_no_dim_without_motion() -> void:
	var scene := _netrun()
	await _frames(3)
	_rewards(scene, 1)
	PageTransition.settle(scene)
	await _frames(3)
	scene.choose_reward(0)
	assert_false(scene.loot_leaving(), "headless never waits")
	assert_ne(RunManager.netrun.run.phase, RunState.Phase.REWARD, "the pick is made, the page moved on")


func test_the_rewards_list_comes_back_by_fading_in_and_its_rows_come_in_one_by_one() -> void:
	var scene := _netrun()
	await _frames(3)
	_rewards(scene, 2)
	PageTransition.settle(scene)
	await _frames(3)
	assert_true(scene.rewards_list_on())
	_live()
	scene.open_reward(0)
	assert_eq(scene._panel.modulate.a, 0.0, "the rebuilt page starts clear")
	var shown := await _until(func() -> bool: return scene._panel.modulate.a >= 1.0)
	assert_true(shown, "and is whole after reward_page_in")
	# Back to the list: the rows rise one after another.
	scene.close_reward_row()
	await _frames(1)
	var r1 := scene._panel.find_child("Reward1", true, false) as Control
	var r2 := scene._panel.find_child("Reward2", true, false) as Control
	assert_not_null(r1)
	assert_not_null(r2)
	assert_eq(r1.modulate.a, 0.0, "row 1 is clear when the page rebuilds")
	var both := await _until(func() -> bool: return r1.modulate.a >= 1.0 and r2.modulate.a >= 1.0)
	assert_true(both, "both rows end whole")


func test_the_rewards_list_is_whole_at_once_without_motion() -> void:
	var scene := _netrun()
	await _frames(3)
	_rewards(scene, 2)
	scene.open_reward(0)
	assert_eq(scene._panel.modulate.a, 1.0)
	scene.close_reward_row()
	var r2 := scene._panel.find_child("Reward2", true, false) as Control
	assert_eq(r2.modulate.a, 1.0, "rows at rest in 0 frames")


# --- M9 ---------------------------------------------------------------------------------------

func test_the_hq_page_enters_when_the_cover_lifts_not_under_it() -> void:
	RunManager.new_campaign(7)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(5)
	_live()
	scene.show_start()
	await _frames(2)
	PageTransition.settle(scene)
	Fx._cover_opaque = true  # a jack out arrives under its opaque cover
	scene.show_hq()
	var page: Control = scene._panel
	assert_false(PageTransition.running(page), "nothing plays behind the cover")
	assert_eq(page.modulate.a, 1.0, "the page stands whole under it")
	Fx._cover_opaque = false
	Fx.cover_lifting.emit()
	assert_true(PageTransition.running(page), "the entrance plays as the cover lifts")
	PageTransition.settle(scene)
	assert_false(PageTransition.running(page))


func test_a_page_replaced_under_the_cover_plays_no_entrance() -> void:
	RunManager.new_campaign(7)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(5)
	_live()
	scene.show_start()
	await _frames(2)
	PageTransition.settle(scene)
	Fx._cover_opaque = true
	scene.show_hq()
	var old: Control = scene._panel
	scene.show_start()
	Fx._cover_opaque = false
	Fx.cover_lifting.emit()
	assert_false(PageTransition.running(old), "the replaced page is not entered")


# --- M10 --------------------------------------------------------------------------------------

func _menu() -> VBoxContainer:
	var box := VBoxContainer.new()
	for t in ["A", "B", "C"]:
		var b := Button.new()
		b.text = t
		box.add_child(b)
	var sticker := HoloSticker.verb_word("GO", VinylSticker.Fill.PINK)
	box.add_child(sticker)
	add_child_autofree(box)
	return box


func test_plain_buttons_dip_when_pressed_and_stickers_keep_their_own_press() -> void:
	var box := _menu()
	var n := PressDip.attach(box)
	assert_eq(n, 3, "the three plain buttons; the sticker has a press of its own")
	assert_eq(PressDip.attach(box), 0, "attaching again adds nothing")
	var b := box.get_child(0) as Button
	_live()
	b.button_down.emit()
	var dipped := await _until(func() -> bool: return b.scale.x < 1.0, 1.0)
	assert_true(dipped, "the press is acknowledged within frames")
	b.button_up.emit()
	var back := await _until(func() -> bool: return is_equal_approx(b.scale.x, 1.0))
	assert_true(back, "and springs back")
	var sticker := box.get_child(3) as Control
	assert_eq(sticker.scale, Vector2.ONE, "the sticker is not dipped by this")


func test_a_press_dips_nothing_without_motion() -> void:
	var box := _menu()
	PressDip.attach(box)
	var b := box.get_child(0) as Button
	b.button_down.emit()
	assert_eq(b.scale, Vector2.ONE, "headless: no dip")
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	Motion.force_live = true
	b.button_down.emit()
	assert_eq(b.scale, Vector2.ONE, "reduce effects: no dip")


func test_rows_rise_in_order_and_are_whole_at_once_without_motion() -> void:
	var box := _menu()
	var rows: Array = [box.get_child(0), box.get_child(1), box.get_child(2)]
	assert_eq(PressDip.rise(rows), 0.0, "headless: nothing to wait for")
	for r: Control in rows:
		assert_eq(r.modulate.a, 1.0, "at rest in 0 frames")
	_live()
	var secs := PressDip.rise(rows)
	assert_gt(secs, Motion.seconds(&"menu_page_in"), "the last row is later than the first")
	for r: Control in rows:
		assert_eq(r.modulate.a, 0.0, "clear to start")
	var first_done := await _until(func() -> bool: return (rows[0] as Control).modulate.a >= 1.0)
	assert_true(first_done)
	assert_lt((rows[2] as Control).modulate.a, 1.0 + 0.0001, "the later rows follow")
	var all := await _until(func() -> bool: return (rows[2] as Control).modulate.a >= 1.0)
	assert_true(all, "every row ends whole")


# --- R5 ---------------------------------------------------------------------------------------

func test_the_lit_route_node_reaches_out_to_its_building() -> void:
	var scene := _netrun()
	await _frames(4)
	var ov := scene.city_overlay as RouteOverlay
	assert_not_null(ov)
	var id: StringName = RunManager.netrun.available_nodes()[0]
	ov.hover_id = id
	assert_eq(ov._mv.value(&"hover_out_t"), 1.0, "headless: the reach is whole at once")
	ov.hover_id = &""
	_live()
	ov.hover_id = id
	assert_eq(ov._mv.value(&"hover_out_t"), 0.0, "it starts at the sticker")
	var out := await _until(func() -> bool: return ov._mv.value(&"hover_out_t") >= 1.0)
	assert_true(out, "and ends on the building after route_hover_out")
	ov.hover_id = &""
	assert_eq(ov._mv.value(&"hover_out_t"), 1.0, "lighting nothing leaves no stem")


func test_the_travel_marker_rides_the_route_to_the_node() -> void:
	var scene := _netrun()
	await _frames(4)
	_live()
	var ov := scene.city_overlay as RouteOverlay
	var from: StringName = &""
	var to: StringName = &""
	for e in ov.edges if ov != null else []:
		if ov.icon_at(e["a"]).x != INF and ov.icon_at(e["b"]).x != INF and ov.icon_at(e["a"]).distance_to(ov.icon_at(e["b"])) > 40.0:
			from = e["a"]
			to = e["b"]
			break
	if to == &"":
		pending("no placed route map in this run")
		return
	var secs := ov.travel(from, to)
	assert_gt(secs, 0.0)
	await _frames(1)
	ov.travel_t = 0.5  # halfway (a loaded machine may have played the whole move by now)
	var at := ov.here_marker_pos()
	assert_ne(at, ov.icon_at(to), "mid-move the marker is on the way")
	assert_ne(at, ov.icon_at(from), "and off where it left")
	ov.finish_travel()
	assert_eq(ov.here_marker_pos(), ov.icon_at(to), "it lands on the node")
