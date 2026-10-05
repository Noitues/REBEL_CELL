extends GutTest
## Animation pass ANIM-R1, combat and input (DECISIONS "Animation pass — ANIM-R1 combat and
## input"): the Perfect landing with motion off (C1); one press predicate and one consume
## rule in every "a press completes the motion" helper (C2); a skip stops every wheel
## motion (C3); the replay's beats track every combatant's HP, satellites and drones too,
## with spawn and boss-phase beats (C4); the SEND IT replay's legibility: landing hold,
## hit lines to the HP ring, stamps for hits that deal nothing, numbers inside the hub off
## the name and never on each other, NO DAMAGE, the result held under THIS TURN before the
## NEXT TURN forecast, the TURN counter, the break's DEFEATED spot, a new enemy's entrance,
## the 2 s budget (C5); RAM refusals (C6); SEND IT's mark (C7); chip order (C8); inline
## numbers in the table (C9); menu typing keeps its words whole (C10).

const SCENE := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const ENEMIES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"geostationary_guard", &"care_swarm"]
## Off-screen: a click there reaches no control (only the helpers' _input sees it).
const OFF_SCREEN := Vector2(-200, -200)

var _scale: float = 1.0
var _reduce: bool = false
var _typing: bool = true
var _pad: bool


class Counter extends Node:
	## Counts the presses that reach it (it sits before the helper in the tree, so the
	## helper sees each event first).
	var got: int = 0

	func _input(event: InputEvent) -> void:
		if MotionSkip.is_press(event):
			got += 1


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing
	_pad = Settings.pad_active


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r1"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
	# A simulated pad press switches the hints to the pad; the next script's pages must not keep
	# the pad prompt row (it took the raid page's room in test_horizontal_pass22_screens).
	Settings.set_pad_active(_pad)
	Engine.time_scale = 1.0
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


func _combat(enemy: StringName = &"collections_agent", scale: float = 1.0, combat_seed: int = 5) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, combat_seed)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(1)


## The three kinds of press: a key, a mouse click (off screen) and a pad button.
func _presses() -> Array:
	var key := InputEventKey.new()
	key.keycode = KEY_SEMICOLON
	key.physical_keycode = KEY_SEMICOLON
	key.pressed = true
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = OFF_SCREEN
	click.global_position = OFF_SCREEN
	var pad := InputEventJoypadButton.new()
	pad.button_index = JOY_BUTTON_Y
	pad.pressed = true
	return [["key", key], ["click", click], ["pad", pad]]


## A holder with a press counter in front of whatever the test adds after it.
func _holder() -> Array:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var counter := Counter.new()
	holder.add_child(counter)
	return [holder, counter]


# --- C2: one press predicate, one consume rule -----------------------------------------------

func test_the_press_predicate() -> void:
	for p in _presses():
		assert_true(MotionSkip.is_press(p[1]), "%s is a press" % p[0])
	var echo := InputEventKey.new()
	echo.keycode = KEY_A
	echo.pressed = true
	echo.echo = true
	assert_false(MotionSkip.is_press(echo), "a key's auto-repeat is not")
	var up := InputEventKey.new()
	up.keycode = KEY_A
	assert_false(MotionSkip.is_press(up), "a key going up is not")
	for b in [MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_MIDDLE]:
		var m := InputEventMouseButton.new()
		m.button_index = b
		m.pressed = true
		assert_true(MotionSkip.is_press(m), "mouse button %d is" % b)
	for b in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN, MOUSE_BUTTON_WHEEL_LEFT, MOUSE_BUTTON_WHEEL_RIGHT]:
		var w := InputEventMouseButton.new()
		w.button_index = b
		w.pressed = true
		assert_false(MotionSkip.is_press(w), "the wheel (%d) scrolls, it is no press" % b)
	assert_false(MotionSkip.is_press(InputEventMouseMotion.new()), "motion is not")
	var axis := InputEventJoypadMotion.new()
	axis.axis_value = 1.0
	assert_false(MotionSkip.is_press(axis), "a stick is not")
	# Every helper uses it (no private press test left).
	for path in ["res://scripts/ui/combat_scene.gd", "res://scripts/ui/kit/drop_layer.gd", "res://scripts/ui/kit/flight_fx.gd",
			"res://scripts/ui/kit/menu_motion.gd", "res://scripts/ui/kit/typing.gd", "res://scripts/ui/kit/page_transition.gd",
			"res://scripts/autoload/dialogue.gd", "res://scripts/ui/netrun_scene.gd"]:
		var src := FileAccess.get_file_as_string(path)
		assert_true(src.contains("MotionSkip.is_press(event)") or src.contains("MotionSkip.verdict(event") or src.contains("MotionSkip.handle(event"), "%s uses the shared predicate (ANIM-R4 C2: or the verdict built on it; ANIM-R5: or handle)" % path)
		assert_true(src.contains("MotionSkip.consume(") or src.contains("MotionSkip.handle(event"), "%s applies the consume rule (ANIM-R5: handle consumes)" % path)
		assert_false(src.contains("InputEventJoypadButton and event.pressed"), "%s has no press test of its own" % path)


func test_the_combat_replay_skip_completes_and_consumes_every_press() -> void:
	var scene := await _combat()
	_live()
	for p in _presses():
		scene.end_turn()
		assert_not_null(scene._seq, "%s: the replay plays" % p[0])
		var turn: int = scene.engine.state().turn
		get_viewport().push_input(p[1])
		assert_null(scene._seq, "%s: it skips the replay" % p[0])
		assert_true(get_viewport().is_input_handled(), "%s: and is consumed" % p[0])
		assert_eq(scene.engine.state().turn, turn, "%s: and ends no second turn" % p[0])
	await _close(scene)


func test_drop_layer_and_flights_complete_and_consume_every_press() -> void:
	_live()
	for p in _presses():
		var h := _holder()
		var counter: Counter = h[1]
		var layer := DropLayer.new()
		h[0].add_child(layer)
		layer._stamp(Vector2(100, 100), 10.0)
		assert_true(layer.busy(), "%s: a stamp ring plays" % p[0])
		get_viewport().push_input(p[1])
		assert_false(layer.busy(), "%s: the press completes it" % p[0])
		assert_eq(counter.got, 0, "%s: and nothing behind sees it" % p[0])
		get_viewport().push_input(p[1])
		assert_eq(counter.got, 1, "%s: with nothing playing, a press passes" % p[0])
		# FlightFx: clicks complete flights too now.
		var screen: Control = h[0]
		var pic := ColorRect.new()
		FlightFx.fly_node(screen, pic, Rect2(10, 10, 40, 40), Vector2(600, 300), &"buy_fly")
		assert_eq(FlightFx.active_count(screen), 1, "%s: a flight plays" % p[0])
		get_viewport().push_input(p[1])
		assert_eq(FlightFx.active_count(screen), 0, "%s: the press lands it" % p[0])
		assert_eq(counter.got, 1, "%s: and is consumed" % p[0])
		screen.queue_free()
		await _frames(1)


func test_menus_typing_and_page_entrances_complete_and_consume_every_press() -> void:
	_live()
	Settings.set_subtitle_typing(true)
	for p in _presses():
		# MenuMotion: typing and the slide.
		var h := _holder()
		var counter: Counter = h[1]
		var box := VBoxContainer.new()
		h[0].add_child(box)
		for t in ["Continue", "Campaigns"]:
			var b := Button.new()
			b.text = t
			b.alignment = HORIZONTAL_ALIGNMENT_LEFT
			b.mouse_filter = Control.MOUSE_FILTER_IGNORE
			box.add_child(b)
		var mm := MenuMotion.attach(box)
		await _frames(2)
		(box.get_child(0) as Button).grab_focus()
		(box.get_child(1) as Button).grab_focus()
		assert_true(mm.typing(), "%s: the line types in" % p[0])
		get_viewport().push_input(p[1])
		assert_false(mm.typing() or mm.sliding(), "%s: the press completes the menu motion" % p[0])
		assert_eq(counter.got, 0, "%s: and is consumed" % p[0])
		# Typing (the Terminal event's words).
		var label := Label.new()
		label.text = "The grid is listening, and it keeps what it hears."
		h[0].add_child(label)
		assert_true(Typing.type_in(label) > 0.0, "%s: words type in" % p[0])
		get_viewport().push_input(p[1])
		assert_false(Typing.typing(label), "%s: the press shows them whole" % p[0])
		assert_eq(counter.got, 0, "%s: and is consumed" % p[0])
		# PageTransition.
		var page := Control.new()
		page.size = Vector2(300, 200)
		h[0].add_child(page)
		var done := [false]
		assert_not_null(PageTransition.enter(page, PageTransition.Look.GLASS, func() -> void: done[0] = true), "%s: the page enters" % p[0])
		get_viewport().push_input(p[1])
		assert_true(done[0], "%s: the press completes the entrance" % p[0])
		assert_eq(counter.got, 0, "%s: and is consumed" % p[0])
		h[0].queue_free()
		await _frames(1)
		# The Dialogue's subtitles (an autoload: checked through the viewport).
		Dialogue.clear()
		Dialogue.say(RC.Voice.DISPATCH, "Jacking you in. The rack is two hops out: keep your Heat down.")
		assert_true(Dialogue.typing(), "%s: the subtitle types in" % p[0])
		get_viewport().push_input(p[1])
		assert_false(Dialogue.typing(), "%s: the press shows it whole" % p[0])
		assert_true(get_viewport().is_input_handled(), "%s: and is consumed" % p[0])
		Dialogue.clear()


func test_a_focus_move_passes_through_a_menu_line_typing_in() -> void:
	_live()
	var h := _holder()
	var box := VBoxContainer.new()
	h[0].add_child(box)
	for t in ["Continue", "Campaigns", "Tutorial"]:
		var b := Button.new()
		b.text = t
		box.add_child(b)
	var mm := MenuMotion.attach(box)
	await _frames(2)
	(box.get_child(0) as Button).grab_focus()
	(box.get_child(1) as Button).grab_focus()
	assert_true(mm.typing())
	var down := InputEventKey.new()
	down.keycode = KEY_DOWN
	down.physical_keycode = KEY_DOWN
	down.pressed = true
	assert_true(down.is_action(&"ui_down"), "the down arrow moves focus")
	var counter: Counter = h[1]
	get_viewport().push_input(down)
	assert_false(mm.typing() and mm.line() == box.get_child(1), "the move ends the line's typing")
	assert_eq(counter.got, 1, "and is let through: a menu never drops a fast tap")


func test_the_route_move_completes_and_consumes_every_press() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames(3)
	for p in _presses():
		scene._travelling = true
		get_viewport().push_input(p[1])
		assert_false(scene._travelling, "%s: the press ends the move (pad buttons too)" % p[0])
		assert_true(get_viewport().is_input_handled(), "%s: and is consumed" % p[0])
	holder.queue_free()
	await _frames(2)


func test_b_during_a_shred_landing_only_ends_the_landing() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	RunManager.netrun.run.cycles = 999
	RunManager.netrun._open_shop()
	scene._show_current()
	await _frames(4)
	_live()
	scene.open_remove()
	await _frames(2)
	var view := scene.get_node("DeckView") as DeckView
	var layer: DropLayer = scene.modal_drops
	var data: Variant = layer.begin_drag(view.card(0), view.card(0).get_meta(DropLayer.SOURCE_META))
	assert_not_null(data)
	assert_eq(layer.drop_on("shred"), "dropped")
	assert_true(layer.busy(), "the card feeds into the shredder")
	var b := InputEventJoypadButton.new()
	b.button_index = JOY_BUTTON_B
	b.pressed = true
	get_viewport().push_input(b)
	assert_false(is_instance_valid(layer) and layer.busy(), "B ends the landing")
	await _frames(2)
	assert_null(scene.get_node_or_null("DeckView"), "the viewer closes as REMOVE closes it")
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.SHOP, "and the Mainframe stays: B did nothing else")
	holder.queue_free()
	await _frames(2)


# --- C1 / C3 ------------------------------------------------------------------------------------

func test_a_perfect_landing_with_motion_off_shows_the_end_state_at_once() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	# Headless: no inversion, no flash, no freeze.
	var flashes := Fx.flashes_shown.size()
	scene._perfect_feedback(pv)
	assert_false(pv.inverted, "headless: no inversion")
	assert_eq(Engine.time_scale, 1.0, "headless: no freeze")
	assert_eq(Fx.flashes_shown.size(), flashes, "headless: no flash")
	# Reduce effects wins over a forced live run.
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	scene._perfect_feedback(pv)
	assert_false(pv.inverted, "reduce effects: no inversion")
	assert_eq(Engine.time_scale, 1.0, "reduce effects: no freeze")
	assert_eq(Fx.flashes_shown.size(), flashes, "reduce effects: no flash")
	await _close(scene)


func test_a_skip_stops_every_wheel_motion_and_lands_without_a_flip() -> void:
	var scene := await _combat()
	_live()
	scene.end_turn()
	var pv: WheelView = scene._player_view
	scene._stutter_view(pv)  # the Weak shake (a kit helper, not the view's own tween)
	assert_true(pv.motion_busy(), "the stutter counts as motion")
	scene.skip_motion()
	assert_false(scene.motion_busy(), "nothing plays right after a skip")
	assert_eq(pv.shake, Vector2.ZERO, "the shake is back at rest")
	await _frames(3)
	for v in scene._views():
		assert_false((v as WheelView).tag_flipping(), "%s: the skip lands without a tag flip" % v.combatant.display_name)
	assert_false(scene.motion_busy(), "and nothing starts after it")
	await _close(scene)


# --- C4: beats for every combatant ------------------------------------------------------------

## Every enemy in content (a campaign's generated REBEL_CELL Mirrors, which another test may
## have left in the run's lookup, are not content: the combat resolver doesn't know them).
func _enemy_ids(lookup: ContentLookup) -> Array[StringName]:
	var out: Array[StringName] = []
	for id in RunManager.lookup().ids_of_class(&"EnemyData"):
		if lookup.has(id):
			out.append(id)
	out.sort()
	return out


func test_the_beats_end_on_every_combatants_hp() -> void:
	var resolver := CombatEngine.make_resolver()
	var kinds := {}
	for enemy in _enemy_ids(resolver.lookup):
		for combat_seed in [1, 7]:
			var session := CombatSession.start(resolver, &"breaker", [enemy], combat_seed, &"rank:1")
			for turn in 6:
				if session.state.is_over():
					break
				# Play what can be played (hits bring bosses to their phases), then SEND IT.
				var actions: Array[CombatAction] = []
				for i in session.state.hand.size():
					var opts := CardTargeting.options(resolver, session.state, 0)
					if not opts.is_empty():
						actions.append(opts[0])
						break
				actions.append(CombatAction.end_turn())
				for action in actions:
					if session.state.is_over():
						break
					var before := session.state.duplicate_state()
					var res := session.apply(action)
					if not res.ok():
						continue
					var beats := ResolveBeats.build(before, res.events, resolver.lookup)
					for b in beats:
						kinds[b["kind"]] = true
					var hp := ResolveBeats.final_hp(before, beats)
					var after := session.state
					var everyone: Array[CombatantState] = [after.player]
					everyone.append_array(after.enemies)
					everyone.append_array(after.drones)
					for c in everyone:
						assert_true(hp.has(c.id), "%s seed %d: %s has a shown HP" % [enemy, combat_seed, c.id])
						assert_eq(int(hp.get(c.id, -1)), maxi(0, c.hp), "%s seed %d: the beats end on %s's HP" % [enemy, combat_seed, c.id])
	for k in ["spawn", "died"]:
		assert_true(kinds.has(k), "the sweep met a %s beat" % k)


func test_spawn_phase_and_death_beats_seed_hp_from_the_events() -> void:
	var s := CombatState.new()
	s.player = CombatantState.new()
	s.player.id = &"player"
	s.player.is_player = true
	s.player.hp = 40
	s.player.wheel = WheelState.new()
	var boss := CombatantState.new()
	boss.id = &"enemy_0"
	boss.hp = 30
	boss.wheel = WheelState.new()
	var sat := CombatantState.new()
	sat.id = &"enemy_0_sat_0"
	sat.is_satellite = true
	sat.host_id = boss.id
	sat.hp = 8
	sat.wheel = WheelState.new()
	s.enemies = [boss, sat]
	var events: Array[Dictionary] = [
		{"type": "resolve_start"},
		{"type": "satellite_spawn", "target": "enemy_0", "satellite": "enemy_0_sat_1", "slot": 2, "hp": 12},
		{"type": "deploy", "owner": "player", "drone": "player_drone_2", "slot": 1, "hp": 6},
		{"type": "boss_phase", "target": "enemy_0", "phase": 1, "behavior": RC.PointerBehavior.MULTIPLY, "ticks": [0, 10, 20],
			"spawned": [{"id": "enemy_0_sat_3", "hp": 9, "slot": 4}]},
		{"type": "damage", "attacker": "player", "target": "enemy_0_sat_1", "amount": 5, "hp_damage": 5, "blocked": 0, "shielded": 0},
		{"type": "damage", "attacker": "player", "target": "enemy_0", "amount": 30, "hp_damage": 30, "blocked": 0, "shielded": 0},
		{"type": "died", "target": "enemy_0_sat_0"},
		{"type": "died", "target": "enemy_0"},
	]
	var beats := ResolveBeats.build(s, events)
	var by_kind := {}
	for b in beats:
		by_kind[b["kind"]] = int(by_kind.get(b["kind"], 0)) + 1
	assert_eq(int(by_kind.get("spawn", 0)), 2, "a satellite launch and a drone deploy each get a beat")
	assert_eq(int(by_kind.get("phase", 0)), 1, "the boss phase gets a beat")
	var hp := ResolveBeats.final_hp(s, beats)
	assert_eq(int(hp[&"enemy_0_sat_1"]), 7, "a launched satellite starts on its event's HP (12 - 5), not 0")
	assert_eq(int(hp[&"player_drone_2"]), 6, "a deployed drone starts on its event's HP")
	assert_eq(int(hp[&"enemy_0_sat_3"]), 9, "a phase's satellite starts on its HP")
	assert_eq(int(hp[&"enemy_0_sat_0"]), 0, "a satellite going down with its host ends at 0 (no damage event)")
	assert_eq(int(hp[&"enemy_0"]), 0)
	for b in beats:
		if b["kind"] == "died":
			assert_eq(bool(b["wheel"]), b["target"] == &"enemy_0", "only the host is a whole wheel")
		if b["kind"] == "phase":
			assert_eq(b["ticks"], [0, 10, 20], "the phase carries its needles")


func test_satellite_tokens_go_on_their_death_beat_and_newcomers_dock() -> void:
	var scene := await _combat(&"geostationary_guard")
	_live()
	var state: CombatState = scene.engine.state()
	var before := state.duplicate_state()
	var sats := before.enemies.filter(func(c: CombatantState) -> bool: return c.is_satellite)
	if sats.is_empty():
		pending("geostationary_guard starts with no satellite")
		await _close(scene)
		return
	var sat: CombatantState = sats[0]
	var v: WheelView = scene._view_of(sat.host_id)
	v.shown_state = before.get_combatant(sat.host_id)
	v.shown_satellites = before.satellites_of(sat.host_id)
	v.replaying = true
	scene._death_beat(sat.id, before, state)
	for s in v.shown_satellites:
		assert_ne(s.id, sat.id, "the dead satellite's token is gone")
	scene._spawn_beat(sat.id, 3, state)
	var back := false
	for s in v.shown_satellites:
		if s.id == sat.id:
			back = true
			assert_eq(s.hp, 3, "a newcomer docks with the HP its event gave")
	assert_true(back, "and a spawned one docks")
	scene.skip_motion()
	await _close(scene)


# --- C5: the SEND IT replay -------------------------------------------------------------------

func test_the_schedule_holds_the_landing_and_the_result_within_budget() -> void:
	assert_lte(Motion.seconds(&"resolve_sequence"), 2.0 + 0.0001, "the budget is about 2 s at 1x")
	for enemy in ENEMIES:
		for combat_seed in [1, 5, 9]:
			var scene := await _combat(enemy, 1.0, combat_seed)
			for turn in 3:
				if scene.engine.state().is_over():
					break
				var before: CombatState = scene.engine.state().duplicate_state()
				scene.end_turn()
				var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
				var sch: Dictionary = scene.sequence_schedule(beats)
				var times: PackedFloat32Array = sch["times"]
				var first := INF
				var last_hit := 0.0
				for k in beats.size():
					if beats[k]["kind"] != "land" and beats[k]["phase"] != "turn_start":
						first = minf(first, times[k])
						# ANIM-R2 E5 (on purpose): a fight that ends on a break shows its result just
						# before the break (the break and VICTORY come after it).
						if not (beats[k]["kind"] in ["died", "end"]):
							last_hit = maxf(last_hit, times[k])
					if beats[k]["kind"] == "died" and bool(beats[k].get("wheel", false)):
						# Its HP is seen at 0 first.
						for j in k:
							if beats[j]["kind"] == "damage" and beats[j]["target"] == beats[k]["target"]:
								assert_true(times[k] - times[j] >= scene.death_lead() - 0.0001, "%s: the break waits for HP 0" % enemy)
				if first < INF:
					assert_true(first >= Motion.seconds(&"resolve_landing_hold") - 0.0001, "%s: the landing holds before anything resolves" % enemy)
					var dbg := PackedStringArray()
					for k in beats.size():
						dbg.append("%s/%s@%.2f" % [beats[k]["kind"], beats[k]["phase"], times[k]])
					assert_true(float(sch["result_at"]) >= last_hit - 0.0001, "%s: the result comes after the last hit (%.2f < %.2f: %s)" % [enemy, float(sch["result_at"]), last_hit, " ".join(dbg)])
				if float(sch["spin_at"]) >= 0.0:
					assert_true(float(sch["spin_at"]) - float(sch["result_at"]) >= Motion.seconds(&"resolve_result_hold") - 0.0001,
						"%s: the result holds before the wheels turn on" % enemy)
				# ANIM-R2 (on purpose): hits one at a time and the HP settling before the result are
				# never squeezed; the budget holds the rest.
				assert_lte(float(sch["total"]), _allowed(scene, beats), "%s: fits the budget" % enemy)
			await _close(scene)


## The replay's time: `resolve_sequence` for the squeezable gaps, plus what ANIM-R2 never
## squeezes (each projectile's `hit_line` spacing and the last HP change settling).
func _allowed(scene: Control, beats: Array[Dictionary]) -> float:
	var timing: Dictionary = scene.beat_timing()
	var extra := 0.0
	var settle := 0.0
	for b in beats:
		settle = maxf(settle, ResolveBeats.settle_after(b, timing))
	# ANIM-R4 C6a (on purpose): each projectile waits for the last one's arrival, and the other
	# side's first one for every roll plus `resolve_side_gap` (another attacker on the same
	# side: `resolve_attacker_gap`); none of it is squeezed.
	var last_side := ""
	var last_source := ""
	for b in beats:
		if not ResolveBeats.flies(b):
			continue
		extra += maxf(float(timing["hit_gap"]), ResolveBeats.arrive_after(b, timing))
		var side := String(b.get("side", ""))
		if last_side != "" and side != "" and side != last_side:
			extra += settle + float(timing["side_gap"])
		elif last_source != "" and String(b["source"]) != last_source:
			extra += float(timing["attacker_gap"])
		if side != "":
			last_side = side
		last_source = String(b["source"])
	return Motion.seconds(&"resolve_sequence") + extra + settle + 0.001


func test_the_forecast_and_the_turn_wait_for_the_replay() -> void:
	var scene := await _combat()
	_live()
	var turn: int = scene.engine.state().turn
	var flips_before := 0
	for v in scene._views():
		flips_before += (v as WheelView).tag_flips
	scene.end_turn()
	assert_not_null(scene._seq)
	assert_true(scene.banner_text().contains(str(turn)), "the status line still shows the turn played")
	for v in scene._views():
		var wv: WheelView = v
		assert_true(wv.intent.is_empty(), "%s: no forecast during the replay" % wv.combatant.display_name)
		assert_true(wv.outcome.is_empty(), "%s: no NEXT plate either" % wv.combatant.display_name)
	# Played out: the forecast flips in, the turn counter moves on.
	await BoundedWait.until(get_tree(), func() -> bool: return scene._seq == null, scene.motion_seconds_left() + BoundedWait.SLACK)
	assert_null(scene._seq, "the replay ends by itself")
	assert_true(scene.banner_text().contains(str(scene.engine.state().turn)), "the TURN counter changes when the replay ends")
	# Counted, not caught mid-flip: under load one frame can outlast the whole flip. The
	# flips start on a redraw, so wait for them (bounded) rather than two frames.
	# ART-2 2D (D15): the forecast flips in on the result chips.
	var flips := func() -> int:
		var n := 0
		for v in scene._views():
			n += scene.chip_row((v as WheelView).combatant.id).flips
		return n
	await BoundedWait.until(get_tree(), func() -> bool: return flips.call() > flips_before, BoundedWait.motion_limit([&"intent_flip"]))
	for v in scene._views():
		var wv: WheelView = v
		if not wv.intent.is_empty():
			assert_false(wv.replaying)
	assert_gt(flips.call(), flips_before, "the forecast tags flip in")
	await _close(scene)


func test_the_result_holds_under_this_turn() -> void:
	var scene := await _combat()
	_live()
	var before: CombatState = scene.engine.state().duplicate_state()
	scene.end_turn()
	var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
	var sch: Dictionary = scene.sequence_schedule(beats)
	# Wait for the hold itself (bounded), not a fixed result_at + caption time that a slow
	# frame could carry past it (Test suite: bounded waits).
	var pv: WheelView = scene._player_view
	await BoundedWait.until(get_tree(), func() -> bool: return scene._seq == null or (pv.caption == tr("THIS TURN") and pv.last_turn_shown > 0.0),
		float(sch["result_at"]) + Motion.seconds(&"result_caption") + BoundedWait.SLACK)
	if scene._seq == null:
		pending("the machine was too slow to catch the hold")
		await _close(scene)
		return
	assert_eq(pv.caption, tr("THIS TURN"), "THIS TURN over the wheel")
	assert_not_null(pv.shown_state, "the wheel has not turned on yet (the result stays in view)")
	assert_true(pv.last_turn_shown > 0.0, "LAST TURN slides up with the result")
	scene.skip_motion()
	assert_eq(pv.caption, "", "a skip clears the caption")
	await _close(scene)


func test_hits_fly_to_the_hp_ring_and_hits_that_deal_nothing_stamp() -> void:
	var scene := await _combat()
	_live()
	var state: CombatState = scene.engine.state()
	var before := state.duplicate_state()
	var enemy: CombatantState = state.enemies[0]
	var ev: WheelView = scene._view_of(enemy.id)
	var pv: WheelView = scene._player_view
	var base := {"event_index": 0, "phase": "resolve", "pass": "offensive", "source": enemy.id, "pointer_index": 0,
		"target": state.player.id, "crit": false, "slot": -1, "status": 0, "tier": -1, "host": &"", "source_slot": 0}
	var hit := base.duplicate()
	hit.merge({"kind": "damage", "amount": 5, "soaked": 0, "hp_after": state.player.hp - 5})
	scene._play_beat(hit, before, state)
	var lines: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "line")
	assert_eq(lines.size(), 1, "a hit that deals damage draws its line")
	assert_eq(lines[0]["to"], pv.hp_ring_spot(), "to the victim's HP ring")
	assert_eq(lines[0]["from"], ev.slot_spot(0), "from the attacker's landed slice")
	assert_eq(lines[0]["color"], scene.hit_color(enemy.id, before), "in the attacker's side's colour (ANIM-R2: not the wheel's)")
	assert_eq(float(lines[0]["width"]), Motion.amplitude(&"hit_line"), "thick (the table's width)")
	assert_eq(scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "travel").size(), 1, "its number travels into the HP counter")
	scene.skip_motion()
	var blocked := base.duplicate()
	blocked.merge({"kind": "damage", "amount": 0, "soaked": 4, "hp_after": state.player.hp})
	scene._play_beat(blocked, before, state)
	assert_eq(scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "line").size(), 1, "ANIM-R2: a fully blocked hit still flies (who hit whom)")
	# ANIM-R3 A6a (expectation changed): "0" with a shield where it struck, not a word stamp.
	var marks: Array = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "impact")
	assert_eq(marks.size(), 1)
	if not marks.is_empty():
		assert_eq(String(marks[0]["text"]), "0", "it shows 0 at the victim")
		assert_eq(marks[0]["at"], pv.hp_ring_spot(), "where the hit struck")
	scene.skip_motion()
	var evaded := base.duplicate()
	evaded.merge({"kind": "evaded", "amount": 7, "soaked": 0, "hp_after": -1})
	scene._play_beat(evaded, before, state)
	assert_eq(scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "line").size(), 1, "ANIM-R2: an evaded hit still flies")
	marks = scene.fx_layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "impact")
	assert_eq(marks.size(), 1)
	if not marks.is_empty():
		assert_eq(int(marks[0]["icon"]), RC.SliceType.DETOUR, "an evaded hit shows 0 with the evade mark")
	scene.skip_motion()
	await _close(scene)


func test_a_number_travels_into_the_hp_counter_which_rolls_down() -> void:
	var scene := await _combat()
	_live()
	var pv: WheelView = scene._player_view
	var hp := float(pv.combatant.hp)
	pv.anim_hp = hp
	var slot := pv.number_slot("hp", "-6", false)
	scene.fx_layer.travel_number(slot["at"], pv.hp_counter_spot(), "-6", WheelView.LOSS_COLOR, false, int(slot["fs"]), "t", scene._hp_arrives.bind(pv, int(hp) - 6))
	assert_eq(pv.shown_hp(), hp, "the HP waits for the number")
	# Bounded wait for the arrival (a fixed delay + 0.1 s missed it under loaded parallel shards;
	# DECISIONS "Animation pass - bake crash").
	# Test suite: bounded waits: the bound is game time and a frame floor, not the wall clock.
	await BoundedWait.until(get_tree(), func() -> bool: return pv.shown_hp() < hp, BoundedWait.motion_limit([&"number_to_hp"]))
	assert_true(pv.shown_hp() < hp, "it rolls down once the number arrives")
	assert_false(is_nan(pv.lag_hp), "with the white lag bar")
	scene.skip_motion()
	await _close(scene)


func test_numbers_stay_inside_the_hub_off_the_name_and_never_rest_on_each_other() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		for enemy in ENEMIES:
			var scene := await _combat(enemy, scale)
			var before: CombatState = scene.engine.state().duplicate_state()
			scene.end_turn()
			var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
			for b in beats:
				for n in scene.numbers_for(b, before):
					if not bool(n.get("hub", true)):
						continue  # ANIM-R2 E4b / R3 A6e: a satellite's numbers sit at its token
					var v: WheelView = n["view"]
					var rect := CombatFxLayer.number_rect(n["at"], n["text"], n["crit"], Vector2.UP * float(n["rise"]), int(n["fs"]), int(n.get("icon", -1)))
					var c := v.global_center()
					for corner in [rect.position, Vector2(rect.end.x, rect.position.y), rect.end, Vector2(rect.position.x, rect.end.y)]:
						assert_true(corner.distance_to(c) <= v.hub_radius() + 0.5, "%s %.1f: %s stays inside the hub" % [enemy, scale, n["text"]])
					var ext := v.hub_text_extent()
					var name_band := Rect2(c.x - v.hub_radius(), c.y + ext.x, v.hub_radius() * 2.0, ext.y - ext.x)
					if float(n["fs"]) > WheelView.NUMBER_MIN_FONT:
						assert_false(rect.grow(-0.5).intersects(name_band), "%s %.1f: %s keeps off the hub's words" % [enemy, scale, n["text"]])
			await _close(scene)
	# Two numbers in one band never rest on each other.
	var sc := await _combat()
	_live()
	var pv: WheelView = sc._player_view
	var s1 := pv.number_slot("hp", "-3", false)
	sc.fx_layer.travel_number(s1["at"], pv.hp_counter_spot(), "-3", WheelView.LOSS_COLOR, false, int(s1["fs"]), "p:hp")
	sc.fx_layer.travel_number(s1["at"], pv.hp_counter_spot(), "-4", WheelView.LOSS_COLOR, false, int(s1["fs"]), "p:hp")
	var g := pv.number_slot("guard", "+5 BLOCK", false)
	sc.fx_layer.number(g["at"], "+5 BLOCK", Palette.NET_CYAN, &"block_number", Vector2.UP, false, 0.0, int(g["fs"]), "p:guard")
	sc.fx_layer.number(g["at"], "+2 SHIELD", Palette.NET_CYAN, &"block_number", Vector2.UP, false, 0.0, int(g["fs"]), "p:guard")
	var bands := {}
	for r in sc.fx_layer.resting_numbers():
		bands[r["band"]] = int(bands.get(r["band"], 0)) + 1
	assert_eq(int(bands.get("p:hp", 0)), 1, "a new damage number sends the resting one on")
	assert_eq(int(bands.get("p:guard", 0)), 1, "a new guard number replaces the resting one")
	sc.skip_motion()
	await _close(sc)


func test_a_turn_without_hp_change_stamps_no_damage_or_all_blocked() -> void:
	var scene := await _combat()
	var state: CombatState = scene.engine.state()
	var enemy: CombatantState = state.enemies[0]
	var beats: Array[Dictionary] = [
		{"kind": "damage", "phase": "resolve", "target": state.player.id, "amount": 0, "soaked": 6, "hp_after": state.player.hp},
		{"kind": "block", "phase": "resolve", "target": enemy.id, "amount": 3, "soaked": 0, "hp_after": -1},
	]
	var stamps: Dictionary = scene.result_stamps(beats, state)
	assert_eq(stamps.get(state.player.id), tr("ALL BLOCKED"), "hit but nothing got through")
	assert_eq(stamps.get(enemy.id), tr("NO DAMAGE"), "not hit at all")
	beats.append({"kind": "damage", "phase": "resolve", "target": enemy.id, "amount": 4, "soaked": 0, "hp_after": enemy.hp - 4})
	stamps = scene.result_stamps(beats, state)
	assert_false(stamps.has(enemy.id), "a wheel that lost HP stamps nothing")
	await _close(scene)


func test_a_beaten_enemy_leaves_a_defeated_spot_and_a_new_one_enters() -> void:
	var scene := await _combat()
	_live()
	var ev: WheelView = scene._enemy_views.values()[0]
	scene._seq = create_tween()
	scene._seq.tween_interval(5.0)
	scene.demo_break(ev.combatant.id)
	assert_true(ev.defeated(), "after the break the view shows the empty spot")
	scene.skip_motion()
	assert_false(ev.defeated(), "a skip shows the state (still alive here)")
	# A real death: the dead enemy keeps its DEFEATED spot.
	scene.engine.state().enemies[0].hp = 0
	assert_true(ev.defeated(), "a dead enemy's view is its DEFEATED spot")
	# A new fight on the same scene: its enemy enters from the edge with its name.
	scene.start_fight(&"compliance_officer", 3)
	var nv: WheelView = scene._enemy_views.values()[0]
	assert_true(nv.enter_slide > 0.0, "the new enemy enters from the edge")
	assert_false(nv.defeated(), "it never reads as the beaten one coming back")
	scene.skip_motion()
	assert_eq(nv.enter_slide, 0.0, "a skip puts it in place")
	await _close(scene)


# --- C6 / C7 / C8 ------------------------------------------------------------------------------

func test_a_ram_refusal_flashes_the_chips_and_pulses_the_cost() -> void:
	var scene := await _combat()
	var state: CombatState = scene.engine.state()
	state.ram = 0
	scene._refresh(state)
	var cost := 0
	var i := 0
	for k in state.hand.size():
		var card := scene.engine.content(state.hand[k]) as CardData
		if card != null and card.ram_cost > 0:
			cost = card.ram_cost
			i = k
			break
	scene.select_card(i)
	assert_true(scene.ram_note.flashing(), "the RAM chips flash")
	assert_eq(scene.ram_note.refusal_text(), tr("NEED %d · HAVE %d") % [cost, 0], "NEED COST · HAVE RAM beside them (ANIM-R3 A6j)")
	assert_true((scene._card_node(i) as ZineCard).cost_alarm > 0.0, "the card's cost shows the refusal (static headless)")
	assert_true(scene.toast.visible, "the toast stays")
	scene.respin()
	assert_eq(scene.ram_note.refusal_text(), tr("NEED %d · HAVE %d") % [scene.engine.resolver.config.respin_ram_cost, 0], "a respin says its cost")
	await _close(scene)


func test_send_it_carries_its_mark_and_pulses_when_ram_is_spent() -> void:
	var scene := await _combat()
	var send: DripButton = scene._end_turn_button
	assert_true(send.glyph, "SEND IT carries the drawn end-turn mark")
	_live()
	var state: CombatState = scene.engine.state()
	state.ram = 0
	scene._refresh(state)
	assert_true(send.ready_pulsing(), "no RAM left: the mark pulses")
	state.ram = 3
	scene._refresh(state)
	assert_false(send.ready_pulsing(), "RAM to spend: it holds still")
	Settings.set_reduce_effects(true)
	state.ram = 0
	scene._refresh(state)
	assert_false(send.ready_pulsing(), "reduce effects: no pulse")
	await _close(scene)


func test_chips_come_in_order_of_importance_and_the_fold_keeps_damage() -> void:
	var chips := [
		{"text": "+3 BLOCK", "color": Color.CYAN},
		{"text": "HITS YOU 14", "color": Color.RED, "rank": 0},
		{"text": "RESIST 2→3", "color": Color.YELLOW},
		{"text": "TAKES 5 HP", "color": Color.RED, "rank": 2},
		{"text": "HITS DRONE 3", "color": Color.RED, "rank": 1},
	]
	var ranked: Array = CombatScene_ranked(chips)
	assert_eq(ranked.map(func(c: Dictionary) -> String: return c["text"]), ["HITS YOU 14", "HITS DRONE 3", "TAKES 5 HP", "+3 BLOCK", "RESIST 2→3"],
		"damage to you, damage dealt, HP, then the rest (in their order)")
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	var v := WheelView.new()
	v.size = Vector2(360, 330)
	add_child_autofree(v)
	var many: Array = ranked.duplicate()
	for k in 8:
		many.append({"text": "STATUS %d" % k, "color": Color.GREEN})
	v.intent = {"text": "SHIM", "chips": many}
	var rows: Array = v._chip_rows()
	var shown: Array = []
	for row in rows:
		for c in row:
			shown.append(String(c["text"]))
	assert_true(shown.has("HITS YOU 14"), "the fold never hides HITS YOU (shown: %s)" % [shown])
	assert_true(shown.back().contains(tr("+%d MORE").replace("%d", "")) or shown.back().ends_with("MORE"), "the rest folds into +N MORE")


func CombatScene_ranked(chips: Array) -> Array:
	return (load("res://scripts/ui/combat_scene.gd") as GDScript).ranked_chips(chips)


# --- C9 / C10 ----------------------------------------------------------------------------------

func test_inline_motion_numbers_moved_to_the_table() -> void:
	var checks := {
		"res://scripts/ui/combat_scene.gd": ["Fx.flash(Palette.CELL_ACID, 0.3)", ", 0.3)\n"],
		"res://scripts/ui/kit/drag_ghost.gd": ["1200"],
		"res://scripts/ui/kit/ram_bar.gd": ["FLASH_SECONDS"],
		"res://scripts/ui/kit/toast_note.gd": ["3.5"],
		"res://scripts/ui/kit/flight_fx.gd": ["STAMP_DOWN_SHARE * 0.5"],
		"res://scripts/ui/kit/drip_button.gd": ["dd * 0.5"],
	}
	for path in checks:
		var src := FileAccess.get_file_as_string(path)
		for bad in checks[path]:
			assert_false(src.contains(bad), "%s no longer has %s inline" % [path, bad.strip_edges()])
	for id in [&"victory_flash", &"boss_phase_flash", &"drag_ghost_tilt_speed", &"ram_refusal", &"toast_note_hold",
			&"stamp_fade_in", &"send_it_drips_share"]:
		assert_true(Motion.has(id), "%s is in the table" % id)
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)


func test_menu_typing_keeps_the_words_whole() -> void:
	_live()
	var h := _holder()
	var box := VBoxContainer.new()
	h[0].add_child(box)
	for t in ["Continue", "Campaigns"]:
		var b := Button.new()
		b.text = t
		box.add_child(b)
	var mm := MenuMotion.attach(box)
	await _frames(2)
	(box.get_child(0) as Button).grab_focus()
	var line := box.get_child(1) as Button
	line.grab_focus()
	assert_true(mm.typing())
	assert_eq(line.text, "Campaigns", "the line's text stays whole while it types in")
	assert_true(mm.typed_count() < line.text.length(), "the typing is drawn")
	assert_eq(line.get_theme_color(&"font_focus_color").a, 0.0, "the line's own lettering is clear meanwhile")
	mm.finish()
	assert_ne(line.get_theme_color(&"font_focus_color").a, 0.0, "and back when it ends")


func test_a_longer_translation_of_send_it_shrinks_to_its_room() -> void:
	var before := TranslationServer.get_locale()
	var t := Translation.new()
	t.locale = "xx"
	t.add_message("SEND IT", "SEND IT RIGHT NOW PLEASE")
	TranslationServer.add_translation(t)
	TranslationServer.set_locale("xx")
	var b := DripButton.new("SEND IT")
	var lettering := b.shown_lettering()
	var room := Palette.marker().get_string_size("SEND IT", HORIZONTAL_ALIGNMENT_LEFT, -1, b.font_size).x
	var width := Palette.marker().get_string_size(String(lettering[0]), HORIZONTAL_ALIGNMENT_LEFT, -1, int(lettering[1])).x
	TranslationServer.remove_translation(t)
	TranslationServer.set_locale(before)
	b.free()
	assert_eq(String(lettering[0]), "SEND IT RIGHT NOW PLEASE", "the translated word")
	assert_true(width <= room + 0.5 or int(lettering[1]) <= roundi(44 * DripButton.FIT_MIN_SHARE), "fits the source word's room: %.0f in %.0f" % [width, room])
