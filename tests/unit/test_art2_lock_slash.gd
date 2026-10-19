extends GutTest
## Plan 2 N7 (18.1) / Q19 (3.17): the nudge lock is a wax circle-slash on the button, shown exactly
## when the lock state says so, with no lock words anywhere; the respin ghost is nine 46 px
## chevrons that light one at a time and loop. Input gating itself stays in test_lock_validation.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _scene: Control


func before_each() -> void:
	_scene = add_child_autofree(load(SCENE).instantiate())
	_scene.start_fight(&"collections_agent", 21)
	await get_tree().process_frame
	await get_tree().process_frame


func _keys_of(marks: Array) -> Array[String]:
	var out: Array[String] = []
	for m: Dictionary in marks:
		out.append(String(m["key"]))
	IdSort.sort_ids(out)
	return out


func test_no_slash_without_a_lock() -> void:
	assert_true(_scene.nudge_lock_marks().is_empty())
	assert_true(_scene.nudge_lock_pencil.shown_keys().is_empty())


func test_the_slash_shows_exactly_while_the_nudge_lock_holds() -> void:
	var player: CombatantState = _scene.engine.state().player
	player.wheel.add_lock(WheelState.LOCK_NUDGE, &"lk_enemy", 1)
	var marks: Array = _scene.nudge_lock_marks()
	var expect := 4 if player.wheel.has_inner_ring() else 2
	var mine := 0
	for m: Dictionary in marks:
		if String(m["group"]) == String(player.id):
			mine += 1
	assert_eq(mine, expect, "one slash per nudge button of the locked wheel")
	await get_tree().process_frame
	await get_tree().process_frame
	assert_eq(_scene.nudge_lock_pencil.shown_keys(), _keys_of(_scene.nudge_lock_marks()), "the pencil shows what the lock state says")
	player.wheel.clear_locks()
	assert_true(_scene.nudge_lock_marks().is_empty(), "lock over: no marks")
	await get_tree().process_frame
	await get_tree().process_frame
	assert_true(_scene.nudge_lock_pencil.shown_keys().is_empty(), "wiped off with it")


func test_a_respin_lock_slashes_the_respin_chip_and_not_the_nudges() -> void:
	var player: CombatantState = _scene.engine.state().player
	player.wheel.add_lock(WheelState.LOCK_RESPIN, &"lk_enemy", 1)
	assert_eq(_keys_of(_scene.nudge_lock_marks()), ["respin"])


func test_no_lock_word_is_drawn_and_a_refusal_has_no_toast() -> void:
	var player: CombatantState = _scene.engine.state().player
	player.wheel.add_lock(WheelState.LOCK_NUDGE, &"lk_enemy", 1)
	player.wheel.add_lock(WheelState.LOCK_RESPIN, &"lk_enemy", 1)
	for c in _scene._player_view.standing_chips():
		assert_false(String(c["text"]).contains("LOCKED"), "no chip says LOCKED")
	assert_false(_scene._player_view.tooltip_text.contains("LOCKED"), "nor the tooltip")
	_scene._on_action_refused(CombatResolver.NUDGE_LOCKED)
	assert_eq(_scene.toast.text(), "", "no refusal toast for a lock")
	assert_eq(_scene._locked_group(CombatResolver.NUDGE_LOCKED), String(player.id))
	assert_eq(_scene._locked_group(CombatResolver.RESPIN_LOCKED), "respin")


func test_the_slash_shape_is_a_circle_then_a_diagonal_and_is_deterministic() -> void:
	var a := NudgeLockPencil.shapes(Vector2(100, 100), Vector2(17, 17), 7)
	var b := NudgeLockPencil.shapes(Vector2(100, 100), Vector2(17, 17), 7)
	assert_eq(a.size(), 2)
	assert_eq(a[0], b[0])
	assert_eq(a[1], b[1])
	var slash: PackedVector2Array = a[1]
	var reach := 17.0 * NudgeLockPencil.CIRCLE_SHARE
	assert_gt(slash[0].distance_to(Vector2(100, 100)), reach, "the slash runs past the ring")
	assert_gt(a[0].size(), 100, "the ring is one long hand stroke")
	assert_gt(a[0][0].distance_to(a[0][a[0].size() - 1]), 0.0, "the ring does not close on itself")
	var low := NudgeLockPencil.shapes(Vector2(100, 100), Vector2(17, 17), 7, 100.0 + 17.0 + 3.0)
	for p in low[0]:
		assert_lt(p.y, 100.0 + 17.0 + 3.0, "the ring's foot stays above the key label")
	assert_lt(slash[0].x, 100.0, "starts upper left")
	assert_lt(slash[0].y, 100.0)
	assert_gt(slash[slash.size() - 1].x, 100.0, "ends lower right")


func test_the_respin_ghost_lights_one_chevron_at_a_time_all_the_way_round() -> void:
	var n := WheelView.UNKNOWN_CHEVRONS
	assert_eq(n, 9)
	assert_eq(WheelView.UNKNOWN_CHEVRON_PX, 46.0)
	var seen := {}
	for step in 90:
		var chase := float(step) / 90.0
		var head := -1
		var best := 0.0
		for k in n:
			var lit := WheelView.unknown_chevron_light(k, chase)
			if lit > best:
				best = lit
				head = k
		assert_gt(best, 0.99, "a head is always full")
		seen[head] = true
	assert_eq(seen.size(), n, "the chase visits every chevron: all the way round")
	var at := 4.5 / n
	assert_almost_eq(WheelView.unknown_chevron_light(4, at), 1.0, 0.001)
	assert_almost_eq(WheelView.unknown_chevron_light(3, at), 1.0 - 1.0 / WheelView.UNKNOWN_CHASE_TAIL, 0.001, "the trail is behind the head")
	assert_eq(WheelView.unknown_chevron_light(5, at), 0.0, "nothing ahead of the head is lit")
