extends GutTest
## Animation pass ANIM-R6 (the sixth fix batch), combat (DECISIONS "Animation pass — ANIM-R6
## combat", items A1-A19 of fix agent A): one press only skips a fight-ending replay (A1); a
## skip keeps the bark and shows the DEFEAT stamp whole (A2); a turn-start kill lands at its
## beat (A3); every shown number is the applied one (A4); the top bar's HP follows the fight
## (A5); a lost fight waits for JACK OUT (A6); the replay's pace (A7); the portrait and the
## arrows follow the replay (A8); a fight left mid-replay lands its outcome (A9); the log's
## playback holds no lambda (A10); switched-off card motions don't play (A11); translated once
## (A12); the play marker on the tape (A13); the fight's background (A14); VICTORY holds (A15);
## the tutorial box (A16); the 1.6 layout and the glyphs (A17); the nudge is seen (A19).

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.3, 1.6]
## Fights tried for one that ends the way a test wants.
const SEEDS := 40

var _scale: float = 1.0
var _reduce: bool = false
var _landed: int = 0
var _continued: int = 0


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r6"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	_landed = 0
	_continued = 0


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	Engine.time_scale = 1.0
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
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


func _combat(scale: float = 1.0, enemy: StringName = &"collections_agent", combat_seed: int = 5) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, combat_seed)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene):
		scene.skip_motion()
		scene.get_parent().queue_free()
	await _frames(2)


## Sets `scene` up (fresh fights, lab-style HP of 1) so the next SEND IT ends the fight with
## `want`. True when found.
func _ending(scene: Control, want: int) -> bool:
	for s in SEEDS:
		scene.start_fight(&"collections_agent", 100 + s)
		scene.skip_motion()
		var st: CombatState = scene.engine.state()
		if want == CombatState.Outcome.VICTORY:
			st.enemies[0].hp = 1
		else:
			st.player.hp = 1
		if scene.engine.preview_end_turn().state.outcome == want:
			scene._refresh(st)
			return true
	return false


func _count_landed() -> void:
	_landed += 1


func _count_continue() -> void:
	_continued += 1


func _outcome_done(scene: Control) -> bool:
	return not scene.outcome_pending()


func _key(k: Key, pressed: bool = true) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = pressed
	return e


func _click(at: Vector2, pressed: bool = true) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.position = at
	e.global_position = at
	if pressed:
		e.button_mask = MOUSE_BUTTON_MASK_LEFT
	return e


## SEND IT's key (the first key bound to end_turn).
func _send_key() -> Key:
	for ev in InputMap.action_get_events(&"end_turn"):
		if ev is InputEventKey:
			var k := ev as InputEventKey
			return k.physical_keycode if k.physical_keycode != KEY_NONE else k.keycode
	return KEY_SPACE


## A lost fight's SEND IT replaying with its outcome held (JACK OUT waits).
func _held_defeat() -> Control:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.DEFEAT), "a fight that ends in DEFEAT was found")
	scene.show_continue(TextDb.mark("JACK OUT"))
	scene.continue_requested.connect(_count_continue)
	scene.outcome_landed.connect(_count_landed)
	_live()
	scene.end_turn()
	return scene


# --- A1: one press only skips a fight-ending replay ----------------------------------------------

## Delivers `ev` to `scene` as the viewport would (the replay's say first, then, unless
## consumed, its _unhandled_input; GUT's own panel holds the focus headless, so a pushed key
## never reaches the scene's unhandled input). True when the replay consumed it.
func _deliver(scene: Control, ev: InputEvent) -> bool:
	var consumed: bool = scene.replay_press(ev) == MotionSkip.Verdict.CONSUME
	if not consumed:
		scene._unhandled_input(ev)
	return consumed


func test_a_key_during_a_fight_ending_replay_only_skips_it() -> void:
	var scene := await _held_defeat()
	assert_true(scene.outcome_pending(), "the outcome waits for the replay")
	assert_false(scene.continue_shown(), "JACK OUT waits")
	assert_true(_deliver(scene, _key(_send_key())), "the press is consumed")
	assert_false(scene.outcome_pending(), "the press landed the outcome")
	assert_true(scene.continue_shown(), "JACK OUT shows")
	assert_eq(_continued, 0, "the press that skipped didn't also leave the fight")
	_deliver(scene, _key(_send_key()))
	assert_eq(_continued, 1, "the next press on SEND IT's key leaves")
	await _close(scene)


func test_a_click_on_the_next_step_spot_during_the_replay_only_skips_it() -> void:
	var scene := await _held_defeat()
	# The next step's spot, clear of GUT's own panel (headless it covers the bottom right).
	var at := Vector2(300, 300)
	scene._continue_button.global_position = at - scene._continue_button.size * 0.5
	assert_true(_deliver(scene, _click(at)), "the click is consumed (no button behind it sees it)")
	assert_true(scene.continue_shown(), "the press landed the outcome (the next step shows)")
	assert_eq(_continued, 0, "the click that skipped didn't also press JACK OUT")
	await _close(scene)


# --- A2: a skip keeps the bark and shows the stamp whole --------------------------------------------

func test_a_skipped_defeat_barks_and_its_stamp_shows_whole() -> void:
	var scene := await _held_defeat()
	var turn: int = scene.engine.state().turn
	scene.skip_motion()
	assert_eq(_landed, 1, "the outcome landed once")
	assert_true(scene._barked_turn.has("defeat:%d" % turn), "the DEFEAT bark the end beat would say is said")
	var pv: WheelView = scene._player_view
	assert_true(pv.flatlined, "the DEFEAT stamp is on")
	assert_eq(pv.flatline_pop, 1.0, "whole at once, no pop after the press")
	assert_false(pv.motion_busy(), "nothing left to complete")
	await _close(scene)


func test_a_defeat_played_out_barks_once() -> void:
	var scene := await _held_defeat()
	var turn: int = scene.engine.state().turn
	var done := await BoundedWait.until(get_tree(), _outcome_done.bind(scene), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	assert_true(done, "the replay lands the outcome")
	assert_true(scene._barked_turn.has("defeat:%d" % turn), "it barks at the beat")
	await _close(scene)


# --- A3: a turn-start kill lands at its beat -----------------------------------------------------------

func _b(kind: String, phase: String, target: StringName, amount: int, hp_after: int, source: StringName = &"") -> Dictionary:
	return {"kind": kind, "phase": phase, "pass": "", "source": source, "target": target, "amount": amount, "hp_after": hp_after,
		"soaked": 0, "side": "", "pointer_index": -1, "slot": -1}


func test_a_turn_start_kill_lands_its_outcome_after_the_hp_roll() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var timing: Dictionary = script.beat_timing()
	var hit := _b("damage", "resolve", &"e0", 4, 3, &"player")
	var spin := _b("spin", "turn_start", &"e0", 0, -1)
	var bite := _b("corrupted", "turn_start", &"e0", 3, 0, &"e0")
	var died := _b("died", "turn_start", &"e0", 0, 0)
	var end := _b("end", "turn_start", &"", 0, -1)
	var beats: Array[Dictionary] = [hit, spin, bite, died, end]
	var sch: Dictionary = ResolveBeats.schedule(beats, 2.0, 0.18, 1.0, 0.3, 0.5, 0.5, timing)
	var times: PackedFloat32Array = sch["times"]
	var at: float = script.outcome_time(beats, times)
	assert_gt(at, 0.0, "a turn-start end lands at its beat, not at 0 s")
	assert_gte(at, times[2] + ResolveBeats.settle_after(bite, timing) - 0.0001, "after the bite's HP roll")
	for k in beats.size():
		assert_gte(script.beat_delay(beats, times, k, at), 0.0, "beat %d: never a negative delay" % k)
	assert_eq(script.beat_delay(beats, times, 4, at), at, "the end beat plays at the outcome's time")
	var no_end: Array[Dictionary] = [hit]
	assert_almost_eq(float(script.beat_delay(no_end, PackedFloat32Array([0.2]), 0, -1.0)), 0.2, 0.0001, "a fight that goes on: the beat's own time")


# --- A4: every shown number is the applied one ------------------------------------------------------

## The (through, applied) pairs the wheel-own hit chips of `chips` say: "HITS X 8" = (8, 8),
## "HITS X 8 → 1 LEFT" = (8, 1). Sorted.
static func _chip_hits(chips: Array) -> Array:
	var re := RegEx.create_from_string("^HITS .* (\\d+)(?: → (\\d+) LEFT)?$")
	var out: Array = []
	for c in chips:
		var m := re.search(String(c["text"]))
		if m == null:
			continue
		var through := m.get_string(1).to_int()
		out.append([through, m.get_string(2).to_int() if m.get_string(2) != "" else through])
	out.sort()
	return out


## The same pairs from the resolve's own events for attacker `id`.
static func _event_hits(events: Array[Dictionary], id: StringName) -> Array:
	var per := {}
	for e in events:
		if String(e.get("type", "")) != "damage" or StringName(String(e.get("attacker", ""))) != id:
			continue
		var t := String(e.get("target", ""))
		var p: Array = per.get(t, [0, 0])
		p[0] += maxi(0, int(e["amount"]) - int(e.get("blocked", 0)) - int(e.get("shielded", 0)))
		p[1] += int(e.get("hp_damage", 0))
		per[t] = p
	var out: Array = per.values()
	out.sort()
	return out


## Checks every number the forecast now shows on `scene` against `events` / `resolved` (the
## preview the forecast came from). Returns how many hit chips it checked.
func _check_forecast(scene: Control, events: Array[Dictionary], resolved: CombatState, label: String) -> int:
	var checked := 0
	for v in scene._views():
		var wv := v as WheelView
		if wv.combatant == null or wv.intent.is_empty():
			continue
		var chips: Array = wv.intent.get("chips", [])
		for c in chips:
			var t := String(c["text"])
			assert_false(t.contains("½"), "%s: no fraction on a chip (%s)" % [label, t])
			assert_false(t.begins_with(tr("YOU TAKE")) or t.begins_with(tr("TAKES")), "%s: no second sum of the loss on a tag (%s)" % [label, t])
		var shown := _chip_hits(chips)
		assert_eq(shown, _event_hits(events, wv.combatant.id), "%s: %s's hit numbers are the applied ones (%s)" % [label, wv.combatant.id, chips.map(func(c: Dictionary) -> String: return String(c["text"]))])
		checked += shown.size()
		var rc := resolved.get_combatant(wv.combatant.id)
		if rc != null and rc.hp != wv.combatant.hp:
			var lay := wv.hp_layout()
			assert_string_contains(String(lay["next_text"]), tr("NEXT %d (%s)") % [rc.hp, TextDb.signed(rc.hp - wv.combatant.hp)],
				"%s: the NEXT plate carries the total (%s)" % [label, wv.combatant.id])
	return checked


func test_every_number_on_the_forecast_is_the_applied_one() -> void:
	var checked := 0
	for combat_seed in [1, 5, 9, 13]:
		for enemy in [&"collections_agent", &"compliance_officer", &"dosage_dispenser"]:
			var scene := await _combat(1.0, enemy, combat_seed)
			var eng: CombatEngine = scene.engine
			var st: CombatState = eng.state()
			# The End Turn forecast.
			var res: CombatResult = eng.preview_end_turn()
			checked += _check_forecast(scene, res.events, res.state, "seed %d %s send" % [combat_seed, enemy])
			# Each card's hover.
			for i in st.hand.size():
				scene._preview_card(i)
				var action: CombatAction = null
				for a in CardTargeting.options(eng.resolver, st, i):
					if a.wheel_id == st.target_id and a.direction == 1:
						action = a
						break
				if action == null:
					var opts := CardTargeting.options(eng.resolver, st, i)
					if opts.is_empty():
						continue
					action = opts[0]
				var pr: CombatResult = eng.preview(action)
				var turn: CombatResult = eng.preview_turn_after(action)
				if pr == null or not pr.ok() or turn == null:
					continue
				var card := eng.content(st.hand[i]) as CardData
				if card != null and CardTargeting.is_random(card):
					continue
				var all: Array[Dictionary] = pr.events.duplicate()
				all.append_array(turn.events)
				checked += _check_forecast(scene, all, turn.state, "seed %d %s card %d" % [combat_seed, enemy, i])
			# A lethal turn: the clamped hit says what it really takes.
			if _ending(scene, CombatState.Outcome.DEFEAT):
				var lr: CombatResult = eng.preview_end_turn()
				checked += _check_forecast(scene, lr.events, lr.state, "seed %d %s lethal" % [combat_seed, enemy])
			await _close(scene)
	assert_gt(checked, 10, "hit chips were checked (%d)" % checked)


func test_a_clamped_hit_says_so_and_the_ride_is_whole() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	assert_eq(script.hit_chip_text("YOU", 8, 8), tr("HITS %s %d") % ["YOU", 8])
	assert_eq(script.hit_chip_text("YOU", 8, 1), tr("HITS %s %d → %d LEFT") % ["YOU", 8, 1], "8 → 1 left")
	var events: Array[Dictionary] = [{"type": "damage", "attacker": &"e0", "target": &"player", "amount": 10, "blocked": 2, "shielded": 0, "hp_damage": 1}]
	var totals: Dictionary = script.hit_totals(events)
	assert_eq(totals[&"e0"][&"player"], {"through": 8, "applied": 1}, "after the guard, and what it really took")
	# The equation where it struck: sword 10 − shield 2 = 8 → 1 LEFT.
	var b := {"kind": "damage", "source": &"e0", "target": &"player", "amount": 1, "raw": 10, "soaked": 2}
	var eq: Array = script.hit_equation(b)
	assert_eq(eq.map(func(it: Dictionary) -> String: return String(it["text"])), ["10", "2", "8", tr("%d LEFT") % 1])
	# The icon row: no guard = one "-N HP"; a guard keeps the equation and its clamp.
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	pv.last_turn = "LAST TURN: -1 HP"
	pv.last_turn_icons = {"hit": 8, "soaked": 0, "evaded": 0, "hp": -1, "dealt": 1}
	assert_eq(pv.icon_row_items().map(func(it: Dictionary) -> String: return String(it["text"])), ["-1 " + tr("HP")], "'↓8 = 8' is now '-1 HP'")
	pv.last_turn_icons = {"hit": 10, "soaked": 2, "evaded": 0, "hp": -1, "dealt": 1}
	assert_eq(pv.icon_row_items().map(func(it: Dictionary) -> String: return String(it["text"])), ["10", "2", "8", tr("%d LEFT") % 1])
	# A hit at half power rides a whole number.
	var st: CombatState = scene.engine.state()
	var hit := {"kind": "damage", "source": st.player.id, "target": st.enemies[0].id, "amount": 3, "raw": 3, "soaked": 0,
		"source_slot": 0, "source_tier": RC.PrecisionTier.PARTIAL}
	var ride: Dictionary = scene.ride_for(hit, st)
	assert_eq(String(ride["label"]), "3", "no '3 ½'")
	await _close(scene)


# --- A5: the top bar's HP follows the fight -----------------------------------------------------------

func _has_combat(net: Control) -> bool:
	return net.combat_scene != null


func _replay_done(scene: Control) -> bool:
	return not scene.motion_busy() and scene._replay_start_hp < 0


func test_the_top_bar_hp_is_the_fights_as_each_replay_lands() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var net: Control = load(NETRUN).instantiate()
	holder.add_child(net)
	net.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	net.new_campaign(1)
	net.start_run(1)
	await _frames()
	net.enter_node(RunManager.netrun.available_nodes()[0])
	await BoundedWait.until(get_tree(), _has_combat.bind(net), 5.0)
	var combat: Control = net.combat_scene
	assert_not_null(combat, "a fight shows")
	var st: CombatState = combat.engine.state()
	var start_hp := st.player.hp
	# A hurt operative (a turn played earlier): the run's HP is written only at the fight's end.
	st.player.hp = start_hp - 7
	combat._refresh(st)
	net._refresh_status()
	assert_string_contains(net._status.text, "HP %d/" % st.player.hp, "the top bar shows the fight's HP, not the run's")
	assert_eq(RunManager.netrun.run.operative.hp, start_hp, "the run's own HP is untouched until the fight ends")
	_live()
	var before := st.player.hp
	combat.end_turn()
	var now: int = combat.engine.state().player.hp
	assert_string_contains(net._status.text, "HP %d/" % before, "during the replay the top bar keeps the turn's start HP")
	await BoundedWait.until(get_tree(), _replay_done.bind(combat), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	if combat.engine.state().is_over():
		await BoundedWait.until(get_tree(), _outcome_done.bind(combat), 6.0)
	else:
		assert_string_contains(net._status.text, "HP %d/" % now, "once the replay lands, its HP")
	combat.skip_motion()
	holder.queue_free()
	await _frames(2)


# --- A6: a lost fight waits for JACK OUT -----------------------------------------------------------------

func test_a_lost_fight_waits_for_jack_out() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var net: Control = load(NETRUN).instantiate()
	holder.add_child(net)
	net.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	net.new_campaign(1)
	net.start_run(1)
	await _frames()
	net.enter_node(RunManager.netrun.available_nodes()[0])
	await BoundedWait.until(get_tree(), _has_combat.bind(net), 5.0)
	_live()
	await net._demo_combat_end("lose")
	var combat: Control = net.combat_scene
	assert_eq(combat.engine.state().outcome, CombatState.Outcome.DEFEAT, "the fight is lost")
	combat.skip_motion()
	# Well past the old hold (combat_end_hold) the fight still shows, JACK OUT on it.
	var left := await BoundedWait.until(get_tree(), _left.bind(net), Motion.seconds(&"combat_end_hold") * 3.0, 30)
	assert_false(left, "the fight stays after DEFEAT")
	assert_true(combat.continue_shown(), "JACK OUT shows")
	combat._continue_pressed()
	assert_null(net.combat_scene, "JACK OUT leaves")
	holder.queue_free()
	await _frames(2)


func _left(net: Control) -> bool:
	return net.combat_scene == null


# --- A8: the portrait and the arrows follow the replay ---------------------------------------------------

func test_the_portrait_and_arrows_follow_the_replay() -> void:
	var scene := await _held_defeat()
	var before: int = scene._replay_hp
	assert_gt(before, 0, "the replay starts from the HP before SEND IT")
	assert_string_contains(scene.portrait.tooltip_text, "%d/%d HP" % [before, scene.engine.state().player.max_hp], "the portrait's tooltip says the replay's HP, not the end's")
	for v in scene._views():
		assert_true((v as WheelView).show_arrows, "the arrows stay while the outcome waits")
	scene.skip_motion()
	assert_string_contains(scene.portrait.tooltip_text, "0/%d HP" % scene.engine.state().player.max_hp, "then the fight's")
	assert_true(scene.portrait.glitch, "the portrait glitches at 0 HP")
	for v in scene._views():
		assert_false((v as WheelView).show_arrows, "and the arrows go with the outcome")
	await _close(scene)


# --- A9: a fight left mid-replay lands its outcome -------------------------------------------------------

func test_a_fight_left_mid_replay_lands_its_outcome() -> void:
	var scene := await _held_defeat()
	assert_true(scene.outcome_pending())
	assert_eq(_landed, 0)
	var holder := scene.get_parent()
	holder.remove_child(scene)
	assert_eq(_landed, 1, "leaving the tree lands the outcome (the DISPATCH line is never dropped)")
	scene.free()
	holder.queue_free()
	await _frames(2)


# --- A10: the log's playback holds no lambda --------------------------------------------------------------

func test_the_log_playback_binds_a_method() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	var body := src.substr(src.find("func _play_log("))
	body = body.substr(0, body.find("\nfunc ", 10))
	assert_false(body.contains("func()"), "no lambda in the log playback")
	assert_true(body.contains("_append_log.bind("), "a bound method instead")
