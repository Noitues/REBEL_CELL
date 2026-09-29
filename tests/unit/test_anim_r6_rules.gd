extends GutTest
## Animation pass ANIM-R6, motion rules and tests (DECISIONS "Animation pass — ANIM-R6
## rules"): the raid playout's own-controls exception holds whichever helper sees the
## press first (D1).

const SCREEN := Rect2(0, 0, 1280, 720)

var _reduce: bool = false
var _typing: bool = true


func before_all() -> void:
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing


func before_each() -> void:
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
	Dialogue.clear()


func _key(k: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = true
	return e


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


## A playout with steps to watch and, after it in the tree (so it sees each press first),
## a label typing in.
func _playout_with_typing() -> Dictionary:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	if not Settings.subtitle_typing:
		Settings.set_subtitle_typing(true)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var panel := RaidPlayoutPanel.new()
	holder.add_child(panel)
	var events: Array[Dictionary] = []
	for step in range(1, 6):
		events.append({"type": "move", "step": step, "threat": &"t0", "from": &"a", "to": &"b", "text": "A threat moves."})
	events.append({"type": "raid_end", "text": "Raid over."})
	panel.play(events, false)
	var label := Label.new()
	label.text = "The words of a long story typing in beside the raid, one letter at a time."
	holder.add_child(label)
	assert_gt(Typing.type_in(label), 0.0, "the label types in")
	return {"panel": panel, "label": label}


## Waits (bounded) until `panel` is inside a step with a length (its first group can be empty).
func _a_step_plays(panel: RaidPlayoutPanel) -> void:
	var ok := await BoundedWait.until(get_tree(), func() -> bool: return panel._next_at > 0.0, 2.0)
	assert_true(ok and panel.motion_running(), "a step with a length plays")


func test_a_speed_press_seen_first_by_another_helper_skips_no_step() -> void:
	var d := _playout_with_typing()
	var panel: RaidPlayoutPanel = d["panel"]
	var label: Label = d["label"]
	await _a_step_plays(panel)
	# The typing skip node sees the press first (it is later in the tree) and handles it.
	var skip := label.get_node(NodePath(Typing.NODE_NAME)) as Typing
	panel._clock = 0.0
	var focus := _key(KEY_RIGHT)
	assert_true(panel.motion_passes(focus), "a focus move drives the playout")
	skip._input(focus)
	assert_eq(panel._clock, 0.0, "a focus move handled by Typing leaves the watched step playing")
	assert_false(Typing.typing(label), "and completes the typing")
	# A press on 2x, handled by another helper first: the step plays on.
	var d2 := _playout_with_typing()
	var panel2: RaidPlayoutPanel = d2["panel"]
	var label2: Label = d2["label"]
	var two := panel2.find_child("Speed2x", true, false) as Button
	two.grab_focus()
	await _a_step_plays(panel2)
	panel2._clock = 0.0
	var accept := _key(KEY_ENTER)
	assert_true(panel2.motion_passes(accept), "accept on 2x drives the playout")
	(label2.get_node(NodePath(Typing.NODE_NAME)) as Typing)._input(accept)
	assert_eq(panel2._clock, 0.0, "accept on 2x seen first by Typing skips no step")
	assert_false(Typing.typing(label2), "the typing completes")


func test_a_press_that_does_not_drive_the_playout_still_ends_the_step_from_any_helper() -> void:
	var d := _playout_with_typing()
	var panel: RaidPlayoutPanel = d["panel"]
	var label: Label = d["label"]
	await _a_step_plays(panel)
	panel._clock = 0.0
	var key := _key(KEY_SEMICOLON)
	assert_false(panel.motion_passes(key), "a stray key drives nothing")
	(label.get_node(NodePath(Typing.NODE_NAME)) as Typing)._input(key)
	assert_almost_eq(panel._clock, panel._next_at, 0.0001, "the stray key handled by Typing ends the step (one press, every motion)")
	assert_false(Typing.typing(label), "and the typing")


func test_complete_all_without_a_press_completes_every_helper() -> void:
	var d := _playout_with_typing()
	var panel: RaidPlayoutPanel = d["panel"]
	await _a_step_plays(panel)
	panel._clock = 0.0
	MotionSkip.complete_all(panel)
	assert_almost_eq(panel._clock, panel._next_at, 0.0001, "a skip by hand (no press) ends the step: motion_passes asks only about a press")
	assert_false(MotionSkip.lets_pass(panel, null), "no event: nothing passes")
