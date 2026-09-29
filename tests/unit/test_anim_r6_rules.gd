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


## ANIM-R6 D2: the lines of the game's scripts that write a tween's shape inline (a
## `Tween.EASE_*` / `Tween.TRANS_*` literal outside a named constant, an export default or a
## dictionary fallback), as "path:line: code". The dev-only demo drags are exempt (their
## path is a drawn stand-in for a hand, not a motion of the game).
static func inline_shapes(root: String = "res://scripts") -> Array[String]:
	var out: Array[String] = []
	var stack: Array[String] = [root]
	while not stack.is_empty():
		var dir: String = stack.pop_back()
		for f in DirAccess.get_files_at(dir):
			if not f.ends_with(".gd"):
				continue
			var path := dir.path_join(f)
			var lines := FileAccess.get_file_as_string(path).split("\n")
			for n in lines.size():
				var line := lines[n]
				var bare := line.strip_edges()
				if not (line.contains("Tween.EASE_") or line.contains("Tween.TRANS_")):
					continue
				if bare.begins_with("#") or bare.begins_with("const ") or bare.begins_with("@export") \
						or line.contains(".get(\"trans\", Tween.") or line.contains(".get(\"ease\", Tween.") \
						or line.contains("DEMO_DRAG_FRAMES"):
					continue
				out.append("%s:%d: %s" % [path, n + 1, bare])
		for d in DirAccess.get_directories_at(dir):
			stack.append(dir.path_join(d))
	return out


func test_no_tween_shape_is_written_inline() -> void:
	var found := inline_shapes()
	assert_eq(found, [] as Array[String], "every tween's ease and trans come from its entry or a named constant:\n%s" % "\n".join(found))


func test_the_reduced_jack_fade_runs_at_the_speed() -> void:
	Motion.set_speed(1.0)
	var at_1 := Fx.reduced_fade_times()
	Motion.set_speed(2.0)
	var at_2 := Fx.reduced_fade_times()
	var e := Motion.entry(&"jack_fade_reduced")
	assert_almost_eq(at_1.x + at_1.y, e.duration, 0.0001, "the whole fade is the entry's seconds at 1x")
	assert_almost_eq(at_1.x, e.duration * e.amplitude, 0.0001, "its amplitude's share goes dark")
	assert_almost_eq(at_2.x + at_2.y, e.duration / 2.0, 0.0001, "at 2x it takes half (it read the raw duration)")


func test_a_flight_and_a_stamp_take_their_shares_from_the_table() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var source := Button.new()
	source.text = "A card"
	source.position = Vector2(100, 100)
	source.size = Vector2(120, 160)
	holder.add_child(source)
	Motion.start_recording()
	FlightFx.fly(holder, source, Vector2(900, 40), &"buy_fly", "", 30.0)
	FlightFx.stamp_on(holder, source, "PICKED")
	var reads := Motion.stop_recording()
	for id: StringName in [&"flight_lift_share", &"flight_fade_share", &"choice_stamp_down_share", &"choice_stamp_hold_share"]:
		assert_true(reads.has(id) and (reads[id] as Dictionary).has("res://scripts/ui/kit/flight_fx.gd"), "FlightFx reads %s" % id)
		assert_true(UiMotionData.ALWAYS_ON.has(id), "%s tunes its flight or stamp (never switched off)" % id)
	FlightFx.finish_all(holder)


func _table_with_off(id: StringName) -> UiMotionData:
	var dup := (load(Motion.CONFIG_PATH) as UiMotionData).duplicate(true)
	dup.find(id).enabled = false
	Motion.use_config(dup)
	return dup


func test_a_view_asks_whether_its_motion_plays_through_the_kit() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	assert_almost_eq(Motion.seconds_live(&"drop_settle"), Motion.seconds(&"drop_settle"), 0.0001, "on: its seconds")
	assert_true(Motion.switched_on(&"jack_fade_reduced"), "on")
	_table_with_off(&"drop_settle")
	assert_eq(Motion.seconds_live(&"drop_settle"), 0.0, "off: no time (the end state at once)")
	assert_gt(Motion.seconds(&"drop_settle"), 0.0, "while its time stays for a hold (R5's kind rule)")
	Motion.use_config(null)
	Settings.set_reduce_effects(true)
	assert_eq(Motion.seconds_live(&"drop_settle"), 0.0, "reduce effects: no time")
	assert_true(Motion.switched_on(&"jack_fade_reduced"), "switched on whatever reduce effects say (the reduced jack plays)")
	_table_with_off(&"jack_fade_reduced")
	assert_false(Motion.switched_on(&"jack_fade_reduced"), "off")
	Motion.start_recording()
	Motion.seconds_live(&"drop_settle")
	Motion.switched_on(&"jack_fade_reduced")
	var asks := Motion.asks.duplicate(true)
	Motion.stop_recording()
	var me: String = (get_script() as Script).resource_path
	assert_true((asks.get(&"drop_settle", {}) as Dictionary).has(me), "seconds_live notes its caller's ask")
	assert_true((asks.get(&"jack_fade_reduced", {}) as Dictionary).has(me), "switched_on too")


func test_fx_pieces_honour_their_switch() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	var was := Fx.limiter.enabled
	Fx.limiter.enabled = false
	assert_true(Fx.flash(), "a flash with screen_flash's numbers")
	_table_with_off(&"screen_flash")
	assert_false(Fx.flash(), "screen_flash off: no flash on its numbers")
	assert_true(Fx.flash(Color.WHITE, 0.3, 0.1), "a caller's own numbers (its own entry gates it)")
	Motion.use_config(null)
	Settings.set_reduce_effects(true)
	assert_false(Fx.flash(Color.WHITE, 0.3, 0.1), "reduce effects: never a flash (D8)")
	Settings.set_reduce_effects(false)
	Fx.limiter.enabled = was
	Fx.flash_rect.color.a = 0.0
	# Two start times 100 ms apart (under one roll period) roll to different phases.
	assert_ne(Fx._roll(0), Fx._roll(100), "the scanlines roll")
	_table_with_off(&"jack_scanlines")
	assert_eq([Fx._roll(0), Fx._roll(100)], [0.0, 0.0], "jack_scanlines off: they hold still")
