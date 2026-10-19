extends GutTest
## Change plan 2, A-RULES (PB-PT-003b B1 / B5 / B6, D7). Seeded headless repros kept as regressions.
## B1: cards and nudges staged after the turn-start spin undo back to that spin (never past it), on
##     the core, the netrun and the screen; the words say "Nothing to undo" once nothing is left.
## B5: a preview read again with no input change reads the same, and equals the result.
## B6: a mid-turn save with staged cards resumes as the same fight and plays on identically.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SLOT := "gut_plan2_a_rules"
const SCREEN := Rect2(0, 0, 1280, 720)
const SEEDS := [3, 17, 41, 2024]
const ENEMIES := [&"collections_agent", &"dosage_dispenser", &"compliance_officer"]
const STAGED_PER_TURN := 4

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## A staged action from `choice`: a card that rolls nothing (no random pick, no reshuffle) or a
## nudge; null when the pick was a random card.
func _pick(s: CombatSession, choice: RandomNumberGenerator) -> CombatAction:
	var wheels: Array[StringName] = [&"player", s.state.target_id]
	if choice.randi_range(0, 2) > 0 and not s.state.hand.is_empty():
		var i := choice.randi_range(0, s.state.hand.size() - 1)
		var card := _resolver.lookup.get_content(s.state.hand[i]) as CardData
		if card == null or CardTargeting.is_random(card) or CardTargeting.may_reshuffle(s.state, card):
			return null
		var a := CombatAction.play_card(i, wheels[choice.randi_range(0, 1)])
		a.direction = [1, -1][choice.randi_range(0, 1)]
		return a
	return CombatAction.nudge(wheels[choice.randi_range(0, 1)], [1, -1][choice.randi_range(0, 1)])


## Stages up to `n` accepted actions through `act` (session.apply or netrun.combat_action).
func _stage(s: CombatSession, choice: RandomNumberGenerator, n: int, act: Callable) -> Array[CombatAction]:
	var done: Array[CombatAction] = []
	var tries := 0
	while done.size() < n and tries < 24 and not s.state.is_over():
		tries += 1
		var a := _pick(s, choice)
		if a == null:
			continue
		var rng_before := s.rng.state
		var r: CombatResult = act.call(a)
		if r.ok():
			assert_eq(s.rng.state, rng_before, "a staged card or nudge rolls nothing")
			done.append(a)
	return done


func _cards_played(actions: Array[CombatAction]) -> int:
	var n := 0
	for a in actions:
		if a.type == CombatAction.Type.PLAY_CARD:
			n += 1
	return n


# --- B1: UNDO after the turn-start spin ---------------------------------------------------------

func test_b1_staged_cards_undo_back_to_the_turn_start_spin_never_past_it() -> void:
	var cards := 0
	for enemy in ENEMIES:
		for seed in SEEDS:
			var s := CombatSession.start(_resolver, &"breaker", [enemy], seed, &"rank:1")
			var choice := CombatFixture.rng(seed + 1)
			for turn in 3:
				if s.state.is_over():
					break
				s.apply(CombatAction.end_turn())  # the new turn's random spin: the checkpoint
				if s.state.is_over():
					break
				var at_spin := s.state_hash()
				var ram := s.state.ram
				var hand := s.state.hand.duplicate()
				var rng_state := s.rng.state
				var history := s.history.size()
				assert_eq(String(s.checkpoint_cause["kind"]), "end_turn", "the turn began with its spin")
				assert_false(s.can_rewind(), "nothing staged yet")
				var staged := _stage(s, choice, STAGED_PER_TURN, s.apply)
				cards += _cards_played(staged)
				if staged.is_empty():
					continue
				assert_true(s.can_rewind(), "%s/%d: staged after the spin, so UNDO is live" % [enemy, seed])
				for k in staged.size():
					assert_true(s.rewind().ok(), "%s/%d: undo %d of %d" % [enemy, seed, k + 1, staged.size()])
				assert_eq(s.state_hash(), at_spin, "%s/%d: back exactly at the spin" % [enemy, seed])
				assert_eq(s.state.ram, ram, "the RAM is back")
				assert_eq(s.state.hand, hand, "the cards are back in the hand")
				assert_eq(s.rng.state, rng_state, "the next roll is the same")
				assert_eq(s.history.size(), history, "nothing staged is left in the log")
				var r := s.rewind()
				assert_false(r.ok(), "never past the spin")
				assert_eq(s.state_hash(), at_spin, "a refused UNDO changes nothing")
				# Stage again (a different plan) and leave it for SEND IT.
				_stage(s, choice, 2, s.apply)
	assert_gt(cards, 10, "the sweep staged real cards (%d), not only nudges" % cards)


## The netrun path the screen uses (combat_action / combat_rewind), and its save after the undo.
func test_b1_netrun_undo_after_the_spin_and_the_save_agrees() -> void:
	var s := _netrun_fight(61)
	assert_not_null(s, "a netrun fight")
	if s == null:
		return
	s.combat_action(CombatAction.end_turn())
	var at_spin := s.combat.state_hash()
	var staged := _stage(s.combat, CombatFixture.rng(5), STAGED_PER_TURN, s.combat_action)
	assert_gt(staged.size(), 0, "staged something")
	for k in staged.size():
		assert_true(s.combat_rewind().ok(), "undo %d" % (k + 1))
	assert_eq(s.combat.state_hash(), at_spin, "back at the spin")
	assert_false(s.combat_rewind().ok(), "never past it")
	var saved := CombatSession.from_dict(_resolver, JSON.parse_string(JSON.stringify(s.run.combat)))
	assert_eq(saved.state_hash(), at_spin, "the run's saved fight is the undone one")


func test_b1_the_screen_undoes_a_card_played_after_the_spin_and_then_says_nothing_is_left() -> void:
	var scene := await _combat()
	scene.end_turn()
	scene.skip_motion()
	await _frames(2)
	var session: CombatSession = scene.engine.session
	var at_spin := session.state_hash()
	var ram := session.state.ram
	var hand_size := session.state.hand.size()
	var i := _plain_card(session)
	assert_gt(i, -1, "a card that rolls nothing in hand")
	scene.play_card(i)
	scene.skip_motion()
	await _frames(2)
	assert_lt(session.state.ram, ram, "the card spent RAM")
	assert_eq(session.state.hand.size(), hand_size - 1, "and left the hand")
	scene._rewind_button.pressed.emit()
	scene.skip_motion()
	await _frames(2)
	assert_eq(session.state_hash(), at_spin, "UNDO took the card back to the spin")
	assert_eq(session.state.ram, ram, "RAM back")
	assert_eq(session.state.hand.size(), hand_size, "card back")
	scene._rewind_button.pressed.emit()
	await _frames(1)
	assert_eq(session.state_hash(), at_spin, "nothing past the spin")
	assert_eq(scene.undo_block_text(), tr(scene.UNDO_BLOCKED_END_TURN))
	assert_true(scene.toast.label.text.begins_with("Nothing to undo"), "says nothing is left: %s" % scene.toast.label.text)
	for words in [scene.UNDO_BLOCKED, scene.UNDO_BLOCKED_OVER, scene.UNDO_BLOCKED_RESPIN, scene.UNDO_BLOCKED_CARD,
			scene.UNDO_BLOCKED_END_TURN, scene.UNDO_BLOCKED_TURN]:
		assert_true(String(words).begins_with("Nothing to undo"), "no block reads as a lock: %s" % words)
	scene.get_parent().queue_free()


## With nothing hovered or aimed, the plain forecast is not "THIS PLAY" (nullpoint read it as a
## staged card holding RAM). N9: CORRUPTED no longer drains RAM at SEND IT, so it forecasts none.
func test_b1_the_plain_forecast_ram_change_is_not_called_this_play() -> void:
	var scene := await _combat()
	var st: CombatState = scene.engine.state()
	for k in st.player.wheel.slice_stacks.size():
		st.player.wheel.set_status(k, RC.Status.CORRUPTED)
	scene._refresh(st)
	await _frames(1)
	assert_eq(scene.ram_note.pending, 0, "CORRUPTED no longer drains RAM at SEND IT")
	assert_false(scene.ram_note.pending_from_play, "nothing is played")
	assert_false(scene.ram_note._label().contains("THIS PLAY"), scene.ram_note._label())
	var i := _plain_card(scene.engine.session)
	scene._preview_action(CombatAction.play_card(i, &"enemy_0"))
	assert_true(scene.ram_note.pending_from_play, "a hovered card's RAM is this play's")
	scene._show_end_turn_preview()
	assert_false(scene.ram_note.pending_from_play, "and the plain forecast's is not again")
	scene.get_parent().queue_free()


# --- B5: the preview holds while nothing changes, and equals the result ---------------------------

func test_b5_previews_read_the_same_until_an_input_changes_and_equal_the_result() -> void:
	var engine := CombatEngine.new()
	engine.resolver = _resolver
	add_child_autofree(engine)
	var checked := 0
	for enemy in ENEMIES:
		for seed in SEEDS:
			var s := CombatSession.start(_resolver, &"breaker", [enemy], seed, &"rank:1")
			engine.session = s
			var choice := CombatFixture.rng(seed + 7)
			for turn in 4:
				if s.state.is_over():
					break
				_stage(s, choice, 2, s.apply)
				var end := s.preview_end_turn().state.state_hash()
				for a in _candidates(s):
					var p1 := s.preview(a)
					if not p1.ok():
						continue
					var turn1 := engine.preview_turn_after(a)
					# Read again, with other reads and a save between (a hover cycle, an autosave).
					s.preview_end_turn()
					s.to_dict()
					var p2 := s.preview(a)
					var turn2 := engine.preview_turn_after(a)
					assert_eq(p2.state.state_hash(), p1.state.state_hash(), "%s/%d t%d: the same preview twice" % [enemy, seed, s.state.turn])
					assert_eq(turn2.resolved_state.state_hash(), turn1.resolved_state.state_hash(), "the same SEND IT forecast twice")
					assert_eq(s.preview_end_turn().state.state_hash(), end, "the plain forecast holds")
					var rng_before := s.rng.state
					var r := s.apply(a)
					assert_eq(r.state.state_hash(), p1.state.state_hash(), "preview == result")
					if s.rng.state != rng_before or s.state.is_over():
						break  # a random card: its checkpoint is new, not undoable
					var sent := _resolver.apply(s.state, CombatAction.end_turn(), CombatResolver.clone_rng(s.rng))
					assert_eq(sent.resolved_state.state_hash(), turn1.resolved_state.state_hash(), "the SEND IT forecast == its resolve")
					assert_true(s.rewind().ok())
					assert_eq(s.preview(a).state.state_hash(), p1.state.state_hash(), "an undo leaves no residue in the preview")
					assert_eq(s.preview_end_turn().state.state_hash(), end, "nor in the plain forecast")
					checked += 1
				s.apply(CombatAction.end_turn())
	engine.session = null
	assert_gt(checked, 100, "checked %d previews" % checked)


func test_b5_the_screen_readouts_hold_across_hover_cycles() -> void:
	var scene := await _combat()
	var session: CombatSession = scene.engine.session
	_stage(session, CombatFixture.rng(11), 2, scene.engine.session.apply)
	scene._refresh(session.state)
	await _frames(1)
	var rest := _readouts(scene)
	for round in 3:
		for a in _candidates(session):
			scene._preview_action(a)
			scene._show_end_turn_preview()
		scene._show_end_turn_preview()
		assert_eq(_readouts(scene), rest, "round %d: the forecast reads as before the hovers" % round)
	scene.get_parent().queue_free()


# --- B6: a mid-turn save resumes as the same fight -------------------------------------------------

func test_b6_a_mid_turn_save_with_staged_cards_resumes_the_same_fight() -> void:
	var s := _netrun_fight(73)
	assert_not_null(s, "a netrun fight")
	if s == null:
		return
	s.combat_action(CombatAction.end_turn())
	var staged := _stage(s.combat, CombatFixture.rng(9), 3, s.combat_action)
	assert_gt(staged.size(), 0, "staged before quitting")
	var before := _canon(s.combat.to_dict())
	var preview_before := s.combat.preview_end_turn().state.state_hash()
	RunManager.after_step()
	RunManager.quit_game()
	RunManager.reset()
	assert_true(RunManager.resume(), "CONTINUE finds the save")
	var back := RunManager.netrun
	assert_not_null(back.combat, "in the fight")
	assert_eq(_canon(back.combat.to_dict()), before, "the same fight: state, checkpoint, staged actions, RNG, UNDO reason")
	assert_eq(back.combat.can_rewind(), s.combat.can_rewind(), "UNDO as live as before")
	assert_eq(back.combat.preview_end_turn().state.state_hash(), preview_before, "the same forecast")
	# Both play on identically: one undo, then whole turns.
	assert_true(back.combat_rewind().ok())
	assert_true(s.combat_rewind().ok())
	assert_eq(back.combat.state_hash(), s.combat.state_hash(), "the same undo")
	for turn in 3:
		if s.combat.state.is_over():
			break
		var c1 := CombatFixture.rng(100 + turn)
		var c2 := CombatFixture.rng(100 + turn)
		_stage(s.combat, c1, 2, s.combat_action)
		_stage(back.combat, c2, 2, back.combat_action)
		s.combat_action(CombatAction.end_turn())
		back.combat_action(CombatAction.end_turn())
		assert_eq(back.combat.state_hash(), s.combat.state_hash(), "turn %d: the same" % turn)


# --- Helpers ----------------------------------------------------------------------------------------

## Every card (each wheel, both directions) and nudge open now.
func _candidates(s: CombatSession) -> Array[CombatAction]:
	var out: Array[CombatAction] = []
	var wheels: Array[StringName] = [&"player", s.state.target_id]
	for w in wheels:
		for d in [1, -1]:
			out.append(CombatAction.nudge(w, d))
			for i in s.state.hand.size():
				var a := CombatAction.play_card(i, w)
				a.direction = d
				out.append(a)
	return out


## The index of a hand card that rolls nothing, or -1.
func _plain_card(s: CombatSession) -> int:
	for i in s.state.hand.size():
		var card := _resolver.lookup.get_content(s.state.hand[i]) as CardData
		if card != null and not CardTargeting.is_random(card) and not CardTargeting.may_reshuffle(s.state, card) \
				and card.ram_cost > 0 and _resolver.validate_action(s.state, CombatAction.play_card(i, s.state.target_id)) == "":
			return i
	return -1


## What the forecast shows on every wheel and the RAM bar.
func _readouts(scene: Control) -> Array:
	var out := []
	for v in scene._views():
		out.append([v.name, JSON.stringify(v.intent, "", true), JSON.stringify(v.outcome, "", true)])
	out.append([scene.ram_note.pending, scene.ram_note.pending_from_play, scene.ram_note.next_turn])
	return out


func _canon(d: Dictionary) -> String:
	return JSON.stringify(JSON.parse_string(JSON.stringify(d)), "", true)


func _combat() -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	scene.skip_motion()
	await _frames(2)
	return scene


## A campaign's first netrun, walked to its first fight (the saved slot is this test's own).
func _netrun_fight(campaign_seed: int) -> NetrunSession:
	RunManager.new_campaign(campaign_seed)
	RunManager.start_run()
	var steps := 0
	while RunManager.has_active_run() and steps < 50:
		steps += 1
		var s := RunManager.netrun
		match s.run.phase:
			RunState.Phase.COMBAT:
				return s
			RunState.Phase.MAP:
				s.enter_node(s.available_nodes()[0])
			RunState.Phase.REWARD:
				s.skip_reward()
			RunState.Phase.EVENT:
				s.choose_event_option(s.current_event().choices.size() - 1)
			RunState.Phase.SHOP:
				s.leave_shop()
			_:
				return null
	return null
