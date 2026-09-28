extends GutTest
## Animation pass ANIM-2 (ANIMATION_HANDOFF 4.2-4.4, 4.6-4.11; GDD 2.10, 9.2): spinners
## and the end-turn resolution. Headless and reduce effects show the end state at once;
## the SEND IT replay is built from the engine's own events (a beat for every HP and guard
## event, in event order, ending on the state's HP) and fits its budget; any press skips
## to the end state; spins end on the core's tick; the nudge queue never desyncs; numbers
## never cover the next resolving needle; the layout holds at the end state; motion never
## changes game state.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const ENEMIES: Array[StringName] = [&"collections_agent", &"compliance_officer", &"geostationary_guard", &"care_swarm"]
## Event types that change HP or guard and must each have a beat.
const BEAT_EVENTS := ["damage", "heal", "block", "shield", "corrupted", "evaded", "status", "died"]

var _text_scale_before: float = 1.0
var _reduce_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_reduce_before = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_anim2"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	if Settings.reduce_effects != _reduce_before:
		Settings.set_reduce_effects(_reduce_before)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
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


## Frees a fight a sweep is done with (Test suite optimization: a sweep kept every fight
## it opened alive, and each one's frames slowed the next).
func _close(scene: Control) -> void:
	scene.get_parent().queue_free()


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Motion.force_live = true


func _signature(scene: Control) -> Array:
	var s: CombatState = scene.engine.state()
	return [s.state_hash(), scene.engine.session.rng.state, s.hand.duplicate(), s.ram, s.turn]


func _assert_end_state(scene: Control, why: String) -> void:
	assert_null(scene._seq, "%s: no sequence runs" % why)
	assert_false(scene.fx_layer.busy(), "%s: no effect left" % why)
	for v in scene._views():
		var wv: WheelView = v
		assert_null(wv.shown_state, "%s: %s shows the state" % [why, wv.combatant.display_name])
		assert_true(is_nan(wv.anim_rotation), "%s: rotation is the state's" % why)
		assert_eq(wv.shown_rotation(), float(wv.combatant.wheel.rotation), "%s: shown on the core tick" % why)
		assert_eq(wv.shown_hp(), float(wv.combatant.hp), "%s: HP shown equals the state" % why)
		assert_false(wv.replaying, "%s: the tag is back" % why)
		assert_eq(wv.last_turn_shown, 1.0, "%s: LAST TURN in place" % why)
		assert_eq(wv.modulate.a, 1.0, "%s: the wheel is whole" % why)


# --- End state at once ---------------------------------------------------------------------

func test_headless_shows_the_end_state_at_once() -> void:
	var scene := await _combat()
	scene.end_turn()
	_assert_end_state(scene, "headless SEND IT")
	scene.nudge_wheel(&"player", 1)
	_assert_end_state(scene, "headless nudge")
	scene.rewind()
	_assert_end_state(scene, "headless rewind")


func test_reduce_effects_shows_the_end_state_at_once() -> void:
	var scene := await _combat()
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	scene.end_turn()
	_assert_end_state(scene, "reduce effects SEND IT")
	scene.nudge_wheel(&"player", 1)
	_assert_end_state(scene, "reduce effects nudge")


# --- The beats come from the engine's events -----------------------------------------------

func test_resolve_beats_match_the_engine_events() -> void:
	for enemy in ENEMIES:
		for combat_seed in [1, 5, 9]:
			var scene := await _combat(enemy, 1.0, combat_seed)
			for turn in 3:
				if scene.engine.state().is_over():
					break
				var before: CombatState = scene.engine.state().duplicate_state()
				scene.end_turn()
				var events: Array[Dictionary] = scene._last_events
				var after: CombatState = scene.engine.state()
				var beats := ResolveBeats.build(before, events, scene.engine.resolver.lookup)
				var by_event := {}
				var last := -1
				for b in beats:
					assert_true(int(b["event_index"]) > last, "%s: beats in event order" % enemy)
					last = int(b["event_index"])
					by_event[last] = b
				for i in events.size():
					if String(events[i].get("type", "")) in BEAT_EVENTS:
						assert_true(by_event.has(i), "%s seed %d: %s event %d has a beat" % [enemy, combat_seed, events[i]["type"], i])
				var hp := ResolveBeats.final_hp(before, beats)
				for c in [after.player] + after.enemies:
					assert_eq(int(hp.get(c.id, c.hp)), c.hp, "%s seed %d: the beats end on %s's HP" % [enemy, combat_seed, c.display_name])
				var sch := CombatScene_schedule(scene, beats)
				var times: PackedFloat32Array = sch["times"]
				for k in range(1, times.size()):
					assert_true(times[k] >= times[k - 1] - 0.0001, "the schedule never goes back")
				# ANIM-R2 (on purpose): projectiles one at a time and the HP settling are never squeezed.
				var allowed := _allowed(scene, beats)
				assert_true(float(sch["total"]) <= allowed, "%s: the sequence fits %.2f s (took %.2f)" % [enemy, allowed, sch["total"]])
			_close(scene)


## The replay's time: `resolve_sequence` for the squeezable gaps, plus what ANIM-R2 never
## squeezes (each projectile's `hit_line` spacing and the last HP change settling).
func _allowed(scene: Control, beats: Array[Dictionary]) -> float:
	var timing: Dictionary = scene.beat_timing()
	var extra := 0.0
	var settle := 0.0
	for b in beats:
		if ResolveBeats.flies(b):
			extra += float(timing["hit_gap"])
		settle = maxf(settle, ResolveBeats.settle_after(b, timing))
	return Motion.seconds(&"resolve_sequence") + extra + settle + 0.001


func CombatScene_schedule(scene: Control, beats: Array[Dictionary]) -> Dictionary:
	return scene.sequence_schedule(beats)


func test_the_resolve_sequence_replays_from_before_and_skips_to_the_end() -> void:
	var scene := await _combat()
	_live()
	var before: CombatState = scene.engine.state().duplicate_state()
	scene.end_turn()
	var sig := _signature(scene)
	assert_not_null(scene._seq, "live: the sequence plays")
	var pv: WheelView = scene._player_view
	assert_true(pv.replaying, "the forecast hides while it replays")
	assert_eq(pv.shown_hp(), float(before.player.hp), "HP starts where SEND IT was pressed")
	assert_eq(pv.last_turn_shown, 0.0, "LAST TURN waits for the end")
	assert_true(scene.motion_seconds_left() > 0.0, "time left")
	# Any press skips to the end state and does nothing else.
	var key := InputEventKey.new()
	key.pressed = true
	key.keycode = KEY_SPACE
	scene._input(key)
	_assert_end_state(scene, "after the skip")
	assert_eq(_signature(scene), sig, "the skipping press changed nothing")
	await _frames(2)
	for v in scene._views():
		var wv: WheelView = v
		assert_false(wv.combatant.hp != wv.shown_hp(), "HP settles on the state")


func test_the_sequence_plays_out_by_itself() -> void:
	var scene := await _combat()
	_live()
	var settled := [false]
	scene.motion_settled.connect(func() -> void: settled[0] = true)
	scene.end_turn()
	var sig := _signature(scene)
	var limit: float = scene.motion_seconds_left() + BoundedWait.SLACK
	await BoundedWait.until(get_tree(), func() -> bool: return scene._seq == null, limit)
	assert_null(scene._seq, "the sequence ends within its budget")
	assert_true(settled[0], "motion_settled fires")
	# The after-effects (tag flips, floats, the HP settle) finish on their own clocks; wait
	# for the scene to say it is idle rather than a fixed time (it flaked under 4-shard load).
	await BoundedWait.until(get_tree(), func() -> bool: return not scene.motion_busy(), limit)
	_assert_end_state(scene, "played out")
	assert_eq(_signature(scene), sig, "the replay changed no game state")


# --- Spins and nudges ------------------------------------------------------------------------

func test_a_spin_ends_on_the_exact_core_tick() -> void:
	for dist in [1.0, -3.0, 9.0, 72.0, -61.0]:
		for trans in [Tween.TRANS_CUBIC, Tween.TRANS_QUART, Tween.TRANS_BACK]:
			assert_eq(WheelView.spin_curve(1.0, dist, 0.3, trans, Tween.EASE_OUT), dist, "p = 1 is the distance")
			assert_almost_eq(WheelView.spin_curve(0.0, dist, 0.3, trans, Tween.EASE_OUT), 0.0, 0.0001, "p = 0 is the start")
			assert_almost_eq(WheelView.spin_curve(0.9999, dist, 0.3, trans, Tween.EASE_OUT), dist, 0.01, "it settles onto the tick")
	for id in [&"wheel_spin", &"wheel_respin", &"enemy_turn_spin"]:
		var e := Motion.entry(id)
		assert_true(WheelView.spin_seconds(id, 1.0) >= e.duration * WheelView.SPIN_MIN_SHARE - 0.0001, "short spins keep a floor")
		assert_true(WheelView.spin_seconds(id, 90.0) <= e.duration * WheelView.SPIN_MAX_SHARE + 0.0001, "long spins keep a ceiling")
	var scene := await _combat()
	_live()
	var pv: WheelView = scene._player_view
	var core := float(pv.combatant.wheel.rotation)
	pv.play_turn(&"wheel_respin", core - 70.0, float(pv.combatant.wheel.inner_rotation) - 70.0)
	assert_true(pv.motion_busy(), "live: it turns")
	assert_eq(pv.shown_rotation(), core - 70.0, "from the old rotation")
	await BoundedWait.until(get_tree(), func() -> bool: return not pv.motion_busy(), WheelView.spin_seconds(&"wheel_respin", 70.0) + BoundedWait.SLACK)
	assert_false(pv.motion_busy(), "done")
	assert_eq(pv.shown_rotation(), core, "on the core's tick")
	assert_eq(pv.shown_inner_rotation(), float(pv.combatant.wheel.inner_rotation), "inner ring on its tick")


func test_the_nudge_queue_never_desyncs_under_rapid_input() -> void:
	var scene := await _combat()
	_live()
	var pv: WheelView = scene._player_view
	var sig_ram: int = scene.engine.state().ram
	for d in [1, 1, -1, 1, 1, 1, -1, -1]:
		scene.nudge_wheel(&"player", d)
		var core := float(scene.engine.state().player.wheel.rotation)
		if not is_nan(pv.queue_target(RC.RingScope.OUTER)):
			assert_eq(pv.queue_target(RC.RingScope.OUTER), core, "the queue ends on the core's tick")
		var shown := pv.shown_rotation()
		assert_true(absf(shown - core) <= pv.queued_steps() + 1.0, "the shown wheel is at most the queue behind")
	assert_true(sig_ram >= scene.engine.state().ram, "nudges went through the engine")
	await BoundedWait.until(get_tree(), func() -> bool: return not pv.motion_busy(), 2.0 + BoundedWait.SLACK)
	assert_false(pv.motion_busy(), "the queue drains")
	assert_eq(pv.shown_rotation(), float(scene.engine.state().player.wheel.rotation), "and ends on the core")
	assert_true(is_nan(pv.anim_rotation), "no override left")


func test_rewind_scrub_never_crosses_the_checkpoint() -> void:
	for pair in [[10.0, 4.0], [-3.0, 6.0], [70.0, 70.0]]:
		var lo := minf(pair[0], pair[1])
		var hi := maxf(pair[0], pair[1])
		var last: float = pair[0]
		for k in 101:
			var v := WheelView.scrub_value(pair[0], pair[1], k / 100.0)
			assert_true(v >= lo - 0.0001 and v <= hi + 0.0001, "between the two states")
			assert_true(absf(v - pair[1]) <= absf(last - pair[1]) + 0.0001, "only ever toward the checkpoint side")
			last = v
		assert_eq(WheelView.scrub_value(pair[0], pair[1], 1.0), pair[1], "ends on the restored state")
	var scene := await _combat()
	_live()
	scene.nudge_wheel(&"player", 1)
	scene.skip_motion()
	var pv: WheelView = scene._player_view
	var from := float(scene.engine.state().player.wheel.rotation)
	scene.rewind()
	var to := float(scene.engine.state().player.wheel.rotation)
	assert_eq(scene.engine.state().player.wheel.rotation, int(from) - 1, "rewound one nudge")
	assert_true(scene.fx_layer.busy(), "VHS lines play")
	for i in 6:
		var v := pv.shown_rotation()
		assert_true(v >= minf(from, to) and v <= maxf(from, to), "the scrub stays between (%.2f)" % v)
		await get_tree().process_frame


# --- Readability ------------------------------------------------------------------------------

func test_numbers_never_cover_the_next_resolving_needle() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		for enemy in ENEMIES:
			var scene := await _combat(enemy, scale)
			var before: CombatState = scene.engine.state().duplicate_state()
			scene.end_turn()
			var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
			var counts := {}
			for k in beats.size():
				var n: Dictionary = scene.number_for(beats[k], before, int(counts.get(beats[k]["target"], 0)))
				if n.is_empty():
					continue
				counts[beats[k]["target"]] = int(counts.get(beats[k]["target"], 0)) + 1
				var v: WheelView = n["view"]
				var rect := CombatFxLayer.number_rect(n["at"], n["text"], n["crit"], Vector2.UP * float(n["rise"]))
				# Every needle hub and satellite token of every wheel: the next one to resolve
				# is among them.
				for w in scene._views():
					var wv: WheelView = w
					for p in wv.shown_pointers().size():
						var spot := wv.pointer_spot(p)
						assert_false(rect.grow(WheelView.SATELLITE_TOKEN).has_point(spot), "%s %.1f: %s clear of %s's needle %d" % [enemy, scale, n["text"], wv.combatant.display_name, p])
					for sat in wv.satellites:
						assert_false(rect.has_point(wv.satellite_spot(sat.id)), "%s %.1f: clear of %s" % [enemy, scale, sat.display_name])
				assert_true(v.global_center().distance_to(n["at"]) <= v.hub_radius(), "starts inside the hub")
			_close(scene)


func test_no_layout_violation_at_the_end_state() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		var scene := await _combat(&"collections_agent", scale)
		_live()
		scene.end_turn()
		scene.skip_motion()
		await _frames(2)
		assert_eq(scene.layout_violations(), [] as Array[String], "scale %.1f after SEND IT" % scale)
		scene.nudge_wheel(&"player", 1)
		scene.skip_motion()
		await _frames(2)
		assert_eq(scene.layout_violations(), [] as Array[String], "scale %.1f after a nudge" % scale)
		Motion.force_live = false
		_close(scene)


func test_intent_tags_flip_only_when_their_content_changes() -> void:
	var scene := await _combat()
	_live()
	var ev: WheelView = scene._enemy_views.values()[0]
	scene.skip_motion()
	await _frames(3)
	ev._tweens.erase(&"tag")
	var flips := ev.tag_flips
	var same := ev.intent.duplicate(true)
	ev.intent = same
	ev.queue_redraw()
	await _frames(2)
	assert_false(ev.tag_flipping(), "the same chips re-set on hover: no flip, no jitter")
	assert_eq(ev.tag_flips, flips, "no flip started")
	var changed := ev.intent.duplicate(true)
	changed["text"] = String(changed.get("text", "")) + " X"
	ev.intent = changed
	ev.queue_redraw()
	# Count the flips instead of catching one mid-way: a slow frame can finish the whole
	# flip before a fixed frame count is up (Test suite: bounded waits).
	if Motion.live(&"intent_flip"):
		await BoundedWait.until(get_tree(), func() -> bool: return ev.tag_flips > flips, BoundedWait.motion_limit([&"intent_flip"]))
	assert_true(ev.tag_flips > flips or not Motion.live(&"intent_flip"), "new content flips the tag")


func test_precision_landings_are_distinct_marks() -> void:
	var scene := await _combat()
	_live()
	var pv: WheelView = scene._player_view
	pv.play_good_ring()
	assert_true(pv.ring_pulse > 0.0, "Good: a ring off the rim")
	pv.play_miss_static(2)
	assert_eq(pv.miss_slot, 2, "Miss: static over that slice only")
	assert_true(pv.miss_static > 0.0, "static on")
	pv.play_pulse(0)
	assert_eq(pv.pulse_pointer, 0, "the resolving needle pulses")
	pv.stop_motion()
	assert_eq(pv.ring_pulse, 0.0, "a skip clears the ring")
	assert_eq(pv.miss_slot, -1, "and the static")


func test_death_breaks_the_wheel_and_the_skip_mends_the_view() -> void:
	var scene := await _combat()
	_live()
	var ev: WheelView = scene._enemy_views.values()[0]
	scene._seq = create_tween()  # a sequence is running (the break is part of one)
	scene._seq.tween_interval(5.0)
	scene.demo_break(ev.combatant.id)
	assert_eq(ev.modulate.a, 0.0, "the wheel falls apart")
	assert_true(scene.fx_layer.busy(), "its pieces fall")
	assert_false(ev.slice_pieces().is_empty(), "one piece per slice")
	scene.skip_motion()
	assert_eq(ev.modulate.a, 1.0, "the skip shows the end state")
	assert_false(scene.fx_layer.busy(), "no piece left")


func test_motion_never_changes_game_state() -> void:
	var scene := await _combat()
	var sig := _signature(scene)
	_live()
	var pv: WheelView = scene._player_view
	pv.play_turn(&"wheel_spin", float(pv.combatant.wheel.rotation) - 9.0)
	pv.play_hp(1.0)
	pv.play_pointers([3], &"pointer_orbit", true)
	pv.play_flip()
	scene.fx_layer.number(pv.global_center(), "-9", Color.RED, &"number_float")
	scene.demo_break(scene._enemy_views.keys()[0])
	await get_tree().create_timer(0.3).timeout  # fixed-wait-ok: any point mid-motion; the skip then shows the end state
	scene.skip_motion()
	assert_eq(_signature(scene), sig, "motion left the state as it was")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/resolve_beats.gd") + FileAccess.get_file_as_string("res://scripts/ui/kit/combat_fx_layer.gd")
	for bad in ["randi(", "randf(", "randomize(", "RandomNumberGenerator"]:
		assert_false(src.contains(bad), "no RNG in the replay (%s)" % bad)
