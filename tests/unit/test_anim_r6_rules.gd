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


## ANIM-R6 D4: the parallel runner's own unit tests (tools/test_run_tests.py: an empty or
## cut-short results.xml is that shard's problem, never a crash that loses every shard; a
## script that did not run is run alone; the free-disk check) pass. Needs Python on PATH,
## as the runner itself does.
func test_the_runners_own_tests_pass() -> void:
	var out: Array = []
	var code := OS.execute("python", [ProjectSettings.globalize_path("res://tools/test_run_tests.py")], out, true)
	if code == -1:
		pending("python is not on PATH here: run tools/test_run_tests.py by hand")
		return
	var text := "\n".join(out)
	assert_eq(code, 0, "tools/test_run_tests.py passes:\n%s" % text)
	assert_true(text.contains("OK"), "unittest says OK")


## ANIM-R6 D5: a schema change adds its check to tools/schema_smoke_checks.gd (the runner
## gains none since ANIM-R5 P17); the docs that say where send it there.
func test_the_docs_send_a_schema_check_to_the_checks_file() -> void:
	for path in ["res://CLAUDE.md", "res://docs/ANIMATION_HANDOFF.md"]:
		var src := FileAccess.get_file_as_string(path)
		assert_false(src.contains("update `tools/schema_smoke_test.gd`"), "%s no longer says to update the runner" % path)
		assert_true(src.contains("tools/schema_smoke_checks.gd"), "%s names the checks file" % path)


## ANIM-R6 D6: the docs say what the motion does now.
func test_the_docs_say_what_the_motion_does_now() -> void:
	var style := FileAccess.get_file_as_string("res://docs/STYLE_GUIDE.md")
	assert_false(style.contains("next step (LOOT / CONTINUE) at once"), "a won fight's next step waits for its outcome to land (ANIM-R5)")
	assert_true(style.contains("as its outcome lands"), "and the guide says so")
	var skip := FileAccess.get_file_as_string("res://scripts/ui/kit/motion_skip.gd")
	var list := skip.substr(skip.find("Every helper that ends its motion on a press"), 400)
	assert_true(list.contains("RaidPlayoutPanel"), "MotionSkip's helper list names the raid playout")


## ANIM-R6 D7: the game scripts that animate (a tween of their own or a Motion helper) and
## join no MotionSkip group, each with why a press does not complete its motion.
## STYLE_GUIDE 5.5 lists the same.
const NOT_SKIPPABLE := {
	"res://scripts/autoload/fx.gd": "the jack swallows every press itself; a flash and the Heat pulse are feedback of a tenth of a second",
	"res://scripts/ui/hq_scene.gd": "the raid's home number flying home and the SITES badge's bump: the raid verdict's reading moment",
	"res://scripts/ui/kit/buy_button.gd": "BUY's flap is a hover state (it holds while hovered)",
	"res://scripts/ui/kit/city_map_overlay.gd": "selection, outline and route pulses answer the pointer; the drop and the raid are DropLayer's and the playout's (both registered)",
	"res://scripts/ui/kit/combat_fx_layer.gd": "plays under the SEND IT replay, whose skip ends the layer",
	"res://scripts/ui/kit/crew_card.gd": "the Polaroid's tilt is a hover state",
	"res://scripts/ui/kit/focus_tip.gd": "a tip fades in on focus: the answer to the focus move itself",
	"res://scripts/ui/kit/forecast_stamp.gd": "the forecast stamp resolves inside the raid playout's step (registered)",
	"res://scripts/ui/kit/grid_map_view.gd": "the selection ring and the minimap pulse answer the pointer",
	"res://scripts/ui/kit/heat_poster.gd": "a threshold's stamp and roll are a reading moment (as RAID INCOMING holds)",
	"res://scripts/ui/kit/map_legend.gd": "the key folds on its own press: the answer to that press",
	"res://scripts/ui/kit/motion.gd": "the kit itself (its callers register)",
	"res://scripts/ui/kit/motion_values.gd": "the kit itself (its callers register)",
	"res://scripts/ui/kit/neon_city.gd": "ambient loops (traffic, signs, beacons): nothing to complete",
	"res://scripts/ui/kit/pad_prompts.gd": "the prompts fade in when a device is used: the answer to that press",
	"res://scripts/ui/kit/ram_bar.gd": "RAM ticks and refusals answer the card played or refused",
	"res://scripts/ui/kit/toast.gd": "a toast is a reading time",
	"res://scripts/ui/kit/wireframe_background.gd": "an ambient loop: nothing to complete",
	"res://scripts/ui/kit/zine_stamp.gd": "JACK IN's breathing is an ambient loop",
}


## The game scripts that animate and never join MotionSkip's group, as paths.
static func animating_unregistered() -> Array[String]:
	var out: Array[String] = []
	var anim := RegEx.create_from_string("create_tween\\(|Motion\\.(run|fade|pop|slide_in|shake|blink|loop_pulse|number_roll)\\(")
	var stack: Array[String] = ["res://scripts"]
	while not stack.is_empty():
		var dir: String = stack.pop_back()
		for f in DirAccess.get_files_at(dir):
			if not f.ends_with(".gd"):
				continue
			var path := dir.path_join(f)
			var src := FileAccess.get_file_as_string(path)
			if anim.search(src) != null and not src.contains("MotionSkip.register"):
				out.append(path)
		for d in DirAccess.get_directories_at(dir):
			stack.append(dir.path_join(d))
	out.sort()
	return out


func test_every_script_that_animates_registers_or_says_why_not() -> void:
	var found := animating_unregistered()
	for p in found:
		assert_true(NOT_SKIPPABLE.has(p), "%s animates and joins no MotionSkip group: register it (register_passive for a short motion) or list it with why" % p)
	for p: String in NOT_SKIPPABLE:
		assert_true(found.has(p), "%s is listed as not skippable but registers or no longer animates: take it off the list" % p)
	var style := FileAccess.get_file_as_string("res://docs/STYLE_GUIDE.md")
	for p: String in NOT_SKIPPABLE:
		if not p.contains("/motion"):
			assert_true(style.contains("`%s`" % p.get_file().get_basename()), "STYLE_GUIDE 5.5 names %s" % p.get_file())
	for p in ["res://scripts/ui/kit/modem_sign.gd", "res://scripts/ui/kit/hud_stats.gd", "res://scripts/ui/kit/drip_button.gd",
			"res://scripts/ui/kit/zine_card.gd", "res://scripts/ui/wheel_view.gd"]:
		assert_true(FileAccess.get_file_as_string(p).contains("MotionSkip.register_passive("), "%s's short motion joins the group" % p)


func test_a_short_motion_completes_with_a_press_another_helper_takes_and_takes_none_itself() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	if not Settings.subtitle_typing:
		Settings.set_subtitle_typing(true)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var stats := HudStats.new()
	holder.add_child(stats)
	stats.items = [["CYCLES", "10", ""]]
	stats.items = [["CYCLES", "25", ""]]
	var sign := ModemSign.new()
	holder.add_child(sign)
	sign.warm_up()
	var drips := DripButton.new("SEND IT")
	holder.add_child(drips)
	drips.press_motion()
	assert_true(stats.motion_running(), "a tag bumps")
	assert_true(sign.motion_running(), "the sign warms up")
	assert_true(drips.motion_running(), "SEND IT squashes")
	# Alone, a press is no one's: it passes on untouched and the short motions play on.
	assert_eq(MotionSkip.running(holder).size(), 3, "all three joined the group")
	var key := _key(KEY_SEMICOLON)
	for n: Node in [stats, sign, drips]:
		var script := n.get_script() as Script
		assert_false(script.source_code.contains("func _input("), "%s takes no press of its own" % script.resource_path.get_file())
	get_viewport().push_input(key)
	assert_true(stats.motion_running() and sign.motion_running() and drips.motion_running(), "a press no helper takes leaves them playing")
	# A press another helper takes completes them too.
	var label := Label.new()
	label.text = "Words typing in beside the short motions."
	holder.add_child(label)
	Typing.type_in(label)
	(label.get_node(NodePath(Typing.NODE_NAME)) as Typing)._input(key)
	assert_false(stats.motion_running(), "the bump ends with the press the typing took")
	assert_false(sign.motion_running(), "the sign is lit")
	assert_false(drips.motion_running(), "SEND IT at rest")
	assert_eq(sign.warm, 1.0, "whole")
	assert_eq(drips.squash, 1.0, "unsquashed")


## ANIM-R6 D9: Settings' snapshot covers every value it holds (a new field must join it,
## or the suite guard would miss a test that leaves it changed), and restore puts back what
## to_dict / from_dict missed (the session's pad_active, the InputMap's keys).
func test_a_settings_snapshot_covers_every_field_and_restores_it() -> void:
	var snap := Settings.snapshot()
	for prop in (Settings.get_script() as Script).get_script_property_list():
		var name := String(prop["name"])
		if int(prop["usage"]) & PROPERTY_USAGE_SCRIPT_VARIABLE == 0 or name == "path" or name.begins_with("_"):
			continue
		assert_true(snap.has(name), "the snapshot holds Settings.%s" % name)
	var nudge := Settings.key_for(&"nudge_left")
	Settings.set_pad_active(not Settings.pad_active)
	Settings.rebind(&"nudge_left", KEY_J)
	Settings.set_tutorial_done(not Settings.tutorial_done)
	var guard: GDScript = load("res://tests/helpers/suite_guard.gd")
	assert_eq(guard.changed_keys(snap, Settings.snapshot()), PackedStringArray(["keybinds", "pad_active", "tutorial_done"]), "the guard names what changed")
	Settings.restore(snap)
	assert_eq(guard.changed_keys(snap, Settings.snapshot()), PackedStringArray(), "restored whole")
	assert_eq(Settings.key_for(&"nudge_left"), nudge, "the InputMap's key too")


## ANIM-R6 D9 / D10: the suite guard runs in both ways of running the suite.
func test_the_suite_guard_is_wired_into_every_run() -> void:
	var cfg := JSON.parse_string(FileAccess.get_file_as_string("res://.gutconfig.json")) as Dictionary
	assert_eq(String(cfg.get("pre_run_script", "")), "res://tests/helpers/suite_guard.gd", "the single-process run's pre-run hook")
	assert_eq(String(cfg.get("post_run_script", "")), "res://tests/helpers/suite_guard.gd", "and its post-run hook")
	var runner := FileAccess.get_file_as_string("res://tools/run_tests.py")
	assert_true(runner.contains("-gpre_run_script=") and runner.contains("-gpost_run_script=") and runner.contains("tests/helpers/suite_guard.gd"), "the parallel runner's shards")
