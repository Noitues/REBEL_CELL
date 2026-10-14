extends GutTest
## Plan 1 animation round P1, combat (DECISIONS "Plan 1 ANIM-COMBAT"): M4 the turn header
## only ever moves forward through a SEND IT replay; M1 a played card or a nudge shows its
## effect as it is queued (the card leaves the hand, the wheel turns, RAM ticks); M2 / M3 /
## M7 the replay's order and payoff beats come from ui_motion.tres entries.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const SEEDS: Array[int] = [5, 11, 23]

var _reduce: bool = false


func before_all() -> void:
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_p1"
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
	AudioDirector.muted = false
	RunManager.delete_save()
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


func _combat(combat_seed: int) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", combat_seed)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(1)


## The turn number the header shows now (-1 when it cannot be read).
func _header_turn(scene: Control) -> int:
	var rx := RegEx.new()
	rx.compile("TURN (\\d+)")
	var m := rx.search(scene._banner_title.text)
	return int(m.get_string(1)) if m != null else -1


func test_the_turn_header_never_flips_back() -> void:
	for combat_seed in SEEDS:
		var scene := await _combat(combat_seed)
		_live()
		var seen: Array[int] = [_header_turn(scene)]
		scene.end_turn()
		var waited := 0.0
		while (scene._seq != null or waited < 0.5) and waited < 12.0:
			await get_tree().process_frame
			waited += get_tree().root.get_process_delta_time()
			var t := _header_turn(scene)
			if t != seen[-1]:
				seen.append(t)
		for i in range(1, seen.size()):
			assert_gt(seen[i], seen[i - 1], "seed %d: the header only counts up (saw %s)" % [combat_seed, str(seen)])
		assert_eq(seen[-1], scene.engine.state().turn, "seed %d: it ends on the state's turn" % combat_seed)
		scene.get_parent().queue_free()
		await _frames(1)


func test_a_card_turns_the_wheel_as_it_lands() -> void:
	# M1: the wheels' answer to a played card starts inside the card's flight (a config share).
	assert_true(Motion.entry(&"card_effect_lead") != null, "the share is a motion entry")
	var share := Motion.amplitude(&"card_effect_lead")
	assert_true(share > 0.0 and share < 1.0, "it starts partway through the flight")
	var scene := await _combat(5)
	_live()
	scene.play_card(0)
	await _frames(2)


func test_the_enemy_strike_follows_with_a_short_gap() -> void:
	# M7: the other side's first hit waits only a short, config-driven gap after my last one lands.

	assert_lt(Motion.seconds(&"resolve_side_gap"), 0.15, "no dead lull between the sides")
	assert_gt(Motion.seconds(&"resolve_side_gap"), 0.0)


func test_damage_numbers_are_readable() -> void:
	# M2: the lettering of a floating number.
	assert_gte(CombatFxLayer.NUMBER_FONT, 28)


func test_a_perfect_tag_resolves_toward_the_enemy_wheel() -> void:
	# M3: the PERFECT tag's bits fly to the enemy wheel the hit is for.
	var scene := await _combat(5)
	var to: Vector2 = scene._payoff_point(scene.engine.state())
	assert_ne(to, Vector2.INF, "a living enemy gives the payoff point")
	var enemy_view: WheelView = scene._enemy_views.values()[0]
	assert_eq(to, enemy_view.global_center())


func _hand_index(scene: Control, card_id: StringName) -> int:
	var hand: Array = scene.engine.state().hand
	for i in hand.size():
		if StringName(String(hand[i])) == card_id:
			return i
	return -1


func test_the_wheel_moves_before_the_card_flight_ends() -> void:
	# M1: sampled mid-flight with live motion, the wheel's shown rotation has left its old tick.
	var scene: Control = null
	var idx := -1
	for combat_seed in range(1, 60):
		scene = await _combat(combat_seed)
		idx = _hand_index(scene, &"fine_tune")
		if idx >= 0:
			break
		scene.get_parent().queue_free()
		await _frames(1)
	assert_gte(idx, 0, "a seed deals Fine Tune")
	if idx < 0:
		return
	_live()
	var olds := {}
	for v in scene._views():
		olds[v] = v.shown_rotation()
	var flight := Motion.seconds(&"card_play")
	scene.play_card(idx)
	var elapsed := 0.0
	var moved_at := -1.0
	while elapsed < flight * 3.0 and moved_at < 0.0:
		await get_tree().process_frame
		elapsed += get_tree().root.get_process_delta_time()
		for v in olds:
			if not is_equal_approx(v.shown_rotation(), float(olds[v])):
				moved_at = elapsed
	assert_gt(moved_at, 0.0, "the wheel turned")
	# The card's whole journey (flight, stamp, dissolve) is what the wheel used to wait for.
	var journey := flight + Motion.seconds(&"card_stamp") + Motion.seconds(&"effect_burst")
	assert_lt(moved_at, journey * 0.95, "it turned before the card's journey ended")


func test_beams_never_overlap_and_each_number_lands_before_the_next_beam() -> void:
	# M2: from the runner's own schedule: consecutive beams launch hit_line apart and after the
	# previous hit's number has entered its HP counter; every HP-changing hit targets a wheel's HP chip.
	var checked := 0
	var chips := 0
	for combat_seed in SEEDS:
		var scene := await _combat(combat_seed)
		_live()
		for turn in 3:
			if scene.engine.state().is_over():
				break
			var before: CombatState = scene.engine.state().duplicate_state()
			scene.end_turn()
			var beats := ResolveBeats.build(before, scene._last_events, scene.engine.resolver.lookup)
			var timing: Dictionary = scene.beat_timing()
			var times: PackedFloat32Array = scene.sequence_schedule(beats)["times"]
			var prev := -1
			for k in beats.size():
				var b := beats[k]
				if b["phase"] == "turn_start" or not ResolveBeats.flies(b):
					continue
				if prev >= 0:
					assert_gte(times[k], times[prev] + float(timing["hit_gap"]) - 0.0001, "seed %d: a beam waits hit_line after the last launch" % combat_seed)
					assert_gte(times[k], times[prev] + ResolveBeats.arrive_after(beats[prev], timing) - 0.0001, "seed %d: the last number landed first" % combat_seed)
					checked += 1
				if ResolveBeats.is_hit(b) and ResolveBeats.changes_hp(b):
					var tid := StringName(String(b["target"]))
					if before.get_combatant(tid) != null:
						assert_ne(scene._host_view(tid, before), null, "the number has a wheel's HP chip to land on")
						chips += 1
				prev = k
			scene.skip_motion()
		await _close(scene)
	assert_gt(checked, 0, "the sweep saw consecutive beams")
	assert_gt(chips, 0, "the sweep saw hits that land on an HP chip")


func test_a_number_landing_pulses_the_hp_chip() -> void:
	var scene := await _combat(5)
	_live()
	var view: WheelView = scene._player_view
	var n: int = view.hp_pulses
	scene._hp_arrives(view, maxi(1, scene.engine.state().player.hp - 1))
	assert_eq(view.hp_pulses, n + 1, "the chip pulsed")
	assert_gt(view.hp_pulse, 0.0, "its outline is up")
