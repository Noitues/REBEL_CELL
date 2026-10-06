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
const SCALES: Array[float] = [1.0, 1.3, Settings.TEXT_SCALE_MAX]
## Fights tried for one that ends the way a test wants.
const SEEDS := 40

var _scale: float = 1.0
var _reduce: bool = false
var _landed: int = 0
var _continued: int = 0


## ANIM-R6 D9 (the suite guard): every Settings value as found (the tutorial test sets
## tutorial_done).
var _settings: Dictionary = {}


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


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
	Motion.use_config(null)  # the loaded table (a test may switch entries off in a copy)
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
		"source_slot": 0, "source_tier": RC.PrecisionTier.WEAK}
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
	# The demo steps on frame callbacks (ANIM-R6 B3): wait for its SEND IT.
	net._demo_combat_end("lose")
	await BoundedWait.until(get_tree(), _fight_over.bind(net), 5.0)
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


func _fight_over(net: Control) -> bool:
	return net.combat_scene != null and net.combat_scene.engine.state().is_over()


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


# --- A11: switched-off card motions don't play -------------------------------------------------------------

## The table in use with `ids` switched off (a duplicate: the loaded one is never changed).
func _table_with_off(ids: Array[StringName]) -> void:
	var dup := (load(Motion.CONFIG_PATH) as UiMotionData).duplicate(true)
	for id in ids:
		dup.find(id).enabled = false
	Motion.use_config(dup)


func _flown_card(scene: Control, exhaust: bool) -> Array:
	var card := ZineCard.new("TEST", 1, "test", 0)
	var fx: CombatFxLayer = scene.fx_layer
	var seconds := fx.play_card(card, Rect2(Vector2(100, 500), Vector2(80, 110)), 0.0, Vector2(400, 300), exhaust)
	var embers := fx.sprites.filter(func(s: Dictionary) -> bool: return String(s["kind"]) == "embers").size()
	return [seconds, embers]


func test_switched_off_card_stamp_and_burn_do_not_play() -> void:
	var scene := await _combat()
	_live()
	var fly := Motion.seconds(&"card_play")
	var stamp := Motion.seconds(&"card_stamp")
	var burn := Motion.seconds(&"card_exhaust")
	var burst := Motion.seconds(&"effect_burst")
	assert_almost_eq(float(_flown_card(scene, true)[0]), fly + stamp + burn, 0.001, "on: the flight, the stamp, the burn")
	scene.fx_layer.clear()
	_table_with_off([&"card_stamp", &"card_exhaust"])
	var off := _flown_card(scene, true)
	assert_almost_eq(float(off[0]), fly, 0.001, "switched off: no stamp and no burn take time")
	await _frames(1)
	var fx: CombatFxLayer = scene.fx_layer
	assert_eq(fx.sprites.filter(func(s: Dictionary) -> bool: return String(s["kind"]) == "embers").size(), 0, "no embers")
	fx.clear()
	_table_with_off([&"effect_burst"])
	assert_almost_eq(float(_flown_card(scene, false)[0]), fly + stamp, 0.001, "a switched-off dissolve takes no time")
	assert_eq(fx.sprites.filter(func(s: Dictionary) -> bool: return String(s["kind"]) == "burst").size(), 0, "and bursts nothing")
	fx.clear()
	Motion.use_config(null)
	assert_almost_eq(burst, Motion.seconds(&"effect_burst"), 0.001, "the table is back")
	await _close(scene)


func test_the_card_flight_has_no_inline_motion_numbers() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/combat_fx_layer.gd")
	var body := src.substr(src.find("func play_card("))
	body = body.substr(0, body.find("\nfunc ", 10))
	assert_false(body.contains("fly * 0.5"), "the grow share is a named drawing constant")
	assert_false(body.contains("set_ease(Tween.EASE_"), "no inline eases")



# --- A12: translated once ------------------------------------------------------------------------------------

func test_the_settings_button_stickers_and_notes_translate() -> void:
	PseudoLoc.on()
	var scene := await _combat()
	var settings: Button = scene._settings_button
	assert_true(settings.text.begins_with(tr("Settings")), "Settings is translated (%s)" % settings.text)
	assert_ne(tr("Settings"), "Settings", "(the scramble is on)")
	assert_eq(settings.auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "and shown as given")
	assert_eq(scene.preview_note.title, tr("WHAT WILL RESOLVE"))
	assert_eq(scene.log_note.title, tr("LOG"))
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	assert_true(src.contains("TerminalChip.new(tr(String(sp[1]))"), "the stickers are built translated")
	PseudoLoc.off()
	await _close(scene)


# --- A13: the play marker on the tape ------------------------------------------------------------------------

func test_a_hovered_card_names_itself_on_the_tape_not_as_a_chip() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		var seen := 0
		for i in scene.engine.state().hand.size():
			scene._preview_card(i)
			for v in scene._views():
				var wv := v as WheelView
				for c in wv.intent.get("chips", []):
					assert_false(bool((c as Dictionary).get("play", false)), "x%.1f: no play chip among the results" % scale)
				if wv.play_note == "":
					continue
				seen += 1
				assert_true(wv.was_shown(), "x%.1f: the tape names the card" % scale)
				var lay := wv.was_layout(wv._tag_geometry()["was"])
				assert_eq(String(lay["play"]), tr("YOUR %s") % wv.play_note, "x%.1f: YOUR <CARD>" % scale)
				assert_gte(int(lay["fs"]), roundi(WheelView.WAS_FONT_SIZE * scale), "x%.1f: at a readable size" % scale)
				# ART-2 2D (D15): no tape on screen; the chips' breakdown names the play first.
				assert_string_contains(scene.chip_row(wv.combatant.id).tooltip_text, tr("YOUR %s") % wv.play_note, "x%.1f: the breakdown names the card" % scale)
			assert_eq(scene.layout_violations(), [] as Array[String], "x%.1f card %d: no layout rule broken" % [scale, i])
			scene._show_end_turn_preview()
			for v in scene._views():
				assert_eq((v as WheelView).play_note, "", "the forecast itself names no card")
		assert_gt(seen, 0, "x%.1f: a card named itself" % scale)
		await _close(scene)
	assert_gt(WheelView.WAS_INK, 0.8, "the WAS words are readable, not a ghost")


# --- A15: VICTORY holds ---------------------------------------------------------------------------------------

func _settled(scene: Control) -> bool:
	return not scene.motion_busy()


func test_victory_stays_at_full_strength_until_the_fight_is_left() -> void:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.VICTORY), "a winning SEND IT was found")
	scene.show_continue(TextDb.mark("LOOT"))
	_live()
	scene.end_turn()
	await BoundedWait.until(get_tree(), _outcome_done.bind(scene), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	var fx: CombatFxLayer = scene.fx_layer
	assert_false(fx.held_word.is_empty(), "VICTORY stands")
	assert_eq(String(fx.held_word["text"]), tr("FIGHT WON"), "S-COMBAT-HUD CMB-14: FIGHT WON (round 32 reward_screen_v2)")
	await BoundedWait.until(get_tree(), _settled.bind(scene), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	assert_false(fx.held_word.is_empty(), "and stays once everything has settled (it faded after ~1 s)")
	assert_false(fx.busy(), "it is not an effect anything waits for")
	scene.start_fight(&"collections_agent", 3)
	assert_true(fx.held_word.is_empty(), "a new fight shows none")
	await _close(scene)


func test_a_skipped_win_still_shows_victory() -> void:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.VICTORY))
	_live()
	scene.end_turn()
	scene.skip_motion()
	var fx: CombatFxLayer = scene.fx_layer
	assert_false(fx.held_word.is_empty(), "VICTORY lands with the skip")
	assert_almost_eq(float(fx.held_word["age"]), float(fx.held_word["delay"]) + float(fx.held_word["land"]), 0.001, "landed at once")
	await _close(scene)


# --- A16: the tutorial box ---------------------------------------------------------------------------------------

func test_the_tutorial_box_fits_its_text_and_moves_on() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		scene.start_tutorial()
		await _frames(3)
		var t: TutorialOverlay = scene.tutorial
		assert_not_null(t)
		# Every page of every step fits the box (no scrolling).
		for i in TutorialOverlay.STEPS.size():
			t.step = i
			t.page = 0
			t.fit(t.size)
			var r: Dictionary = t._room(t.size)
			for p in t.pages():
				var lines := TutorialOverlay.wrap_words(p, r["font"], int(r["fs"]), float(r["w"]))
				assert_lte(lines.size(), int(r["lines"]), "x%.1f step %d: a page fits the box" % [scale, i])
		t.step = 0
		t.page = 0
		t.fit(t.size)
		# A new turn moves the wheel's step on.
		var events: Array[Dictionary] = [{"type": "turn_start"}]
		t.on_events(events)
		assert_eq(t.current_title(), "NUDGE", "x%.1f: the turn moves THE WHEEL on" % scale)
		await _frames(2)
		assert_eq(scene.layout_violations(), [] as Array[String], "x%.1f: the box breaks no layout rule" % scale)
		t.skip()
		Settings.set_tutorial_done(true)
		await _close(scene)


func test_next_pulses_when_it_moves_the_tutorial_on() -> void:
	_live()
	var t := TutorialOverlay.new(Vector2(300, 400))
	add_child_autofree(t)
	t.step = 1  # NUDGE: a nudge ends it
	t.page = 0
	t.fit(Vector2(300, 400))
	assert_false(t.next_pulsing(), "a step a play ends: Next stays still")
	t.step = 2  # RESISTANCE: only Next (or the turn) ends it
	t.fit(Vector2(300, 400))
	assert_true(t.next_pulsing(), "Next pulses")
	assert_true(Motion.has(&"tutorial_next_pulse") and UiMotionData.REQUIRED_IDS.has(&"tutorial_next_pulse"), "its timing is in the table")


# --- A17: the arrows clear of the tag, the inner ring's mark, the play mark ------------------------------------

func test_the_tags_never_cover_the_nudge_arrows() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		for i in [-1] + range(scene.engine.state().hand.size()):
			if i >= 0:
				scene._preview_card(i)
			for v in scene._views():
				var wv := v as WheelView
				var tag := wv.intent_rect()
				if not tag.has_area():
					continue
				for ar in wv.arrows():
					var c := wv.arrow_center(int(ar["ring"]), int(ar["direction"]))
					var disc := WheelView.ARROW_HIT * 0.9
					assert_false(tag.intersects(Rect2(c - Vector2(disc, disc), Vector2(disc, disc) * 2.0)),
						"x%.1f preview %d: %s's tag covers its %s arrow" % [scale, i, wv.combatant.id, ar])
		await _close(scene)
	var src := FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd")
	assert_false(src.contains("\"IN\", HORIZONTAL_ALIGNMENT_CENTER"), "the inner ring's arrows carry a mark, not \"IN\"")


func test_send_it_carries_a_play_mark() -> void:
	var scene := await _combat()
	var b := scene._end_turn_button as DripButton
	assert_true(b.glyph, "SEND IT draws its mark")
	var h := roundi(DripButton.HINT_SIZE * Settings.text_scale)
	var r := b.play_mark_rect(Vector2(b.size.x * 0.5, b.size.y * 0.5), h)
	assert_gte(r.size.y, h * 1.2, "a play button's mark, bigger than the key hint")
	await _close(scene)


# --- A18: the lab's lost fight, the scramble's settings ----------------------------------------------------------

func test_pseudolocalisation_restores_the_project_values() -> void:
	var before := {}
	for k in PseudoLoc.KEYS:
		before[k] = ProjectSettings.get_setting(k)
	var was := TranslationServer.pseudolocalization_enabled
	PseudoLoc.on()
	assert_true(TranslationServer.pseudolocalization_enabled)
	PseudoLoc.off()
	for k in PseudoLoc.KEYS:
		assert_eq(ProjectSettings.get_setting(k), before[k], "%s is back to its own value" % k)
	assert_eq(TranslationServer.pseudolocalization_enabled, was)
	for f in ["test_anim_r4_combat.gd", "test_anim_r5_combat.gd"]:
		var src := FileAccess.get_file_as_string("res://tests/unit/" + f)
		assert_false(src.contains("set_setting(\"internationalization/pseudolocalization/replace_with_accents\", on)"), "%s restores the prior values" % f)
	assert_false(FileAccess.get_file_as_string("res://tests/unit/test_anim_r5_combat.gd").contains("assert_true(true"), "no empty assert")


func _lab_lost(lab: Control) -> bool:
	var sc: Variant = lab.get("_scene")
	if sc == null or not is_instance_valid(sc):
		return false
	var eng := (sc as Control).get(&"engine") as CombatEngine
	return eng != null and eng.has_fight() and eng.state().outcome == CombatState.Outcome.DEFEAT


func test_the_lab_lost_fight_always_loses() -> void:
	_live()
	var lab: Control = load("res://tools/design_lab/motion_lab.tscn").instantiate()
	lab.set("_loop", false)
	add_child_autofree(lab)
	await get_tree().process_frame
	lab.set("_id", &"defeat_stamp")
	lab.call("_play")
	var lost := await BoundedWait.until(get_tree(), _lab_lost.bind(lab), 10.0)
	assert_true(lost, "send_lose ends in DEFEAT")


# --- A19: the nudge is seen ----------------------------------------------------------------------------------------

func _still(v: WheelView) -> bool:
	return not v.motion_busy()


func test_a_nudge_step_is_long_enough_to_see() -> void:
	assert_gte(Motion.seconds(&"wheel_nudge"), NUDGE_SEEN, "a nudge step lasts long enough to watch the wheel turn")
	var scene := await _combat()
	_live()
	scene.nudge_wheel(&"player", 1)
	var pv: WheelView = scene._player_view
	assert_true(pv.motion_busy(), "the step plays")
	assert_true(await BoundedWait.until(get_tree(), _still.bind(pv), BoundedWait.motion_limit([&"wheel_nudge"])), "and ends on the tick")
	assert_eq(pv.shown_rotation(), float(pv.combatant.wheel.rotation), "on the state's tick")
	await _close(scene)


## The shortest nudge step the eye follows (s).
const NUDGE_SEEN := 0.15


# --- A7: the replay's pace ---------------------------------------------------------------------------------------------

func test_a_plain_turn_replays_in_about_two_and_a_half_seconds() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var p := &"player"
	var e := &"e0"
	var beats: Array[Dictionary] = [
		_b("land", "resolve", p, 0, -1, p), _b("land", "resolve", e, 0, -1, e),
		_b("damage", "resolve", e, 6, 34, p), _b("damage", "resolve", p, 5, 55, e),
		_b("spin", "turn_start", p, 0, -1), _b("spin", "turn_start", e, 0, -1),
	]
	beats[2]["side"] = "player"
	beats[2]["pass"] = "offensive"
	beats[3]["side"] = "enemy"
	beats[3]["pass"] = "offensive"
	var total := float(script.sequence_schedule(beats)["total"])
	gut.p("A7: a plain turn (one hit each way) replays in %.2f s" % total)
	assert_lte(total, PLAIN_TURN_MAX, "a turn with one hit each way replays in about 2.5 s (%.2f)" % total)


## The longest a plain SEND IT (one hit each way, the spin to the next landing) may replay at
## 1x (s): STYLE_GUIDE 5.2's measured pace.
const PLAIN_TURN_MAX := 2.6


# --- A14: the city lands between turns ---------------------------------------------------------------------------------

func test_the_city_waits_to_land_until_the_replay_ends() -> void:
	var scene := await _combat()
	_live()
	assert_false(scene.city_held(), "before SEND IT the city may land")
	scene.end_turn()
	assert_true(scene.city_held(), "during the replay a bake waits (the silhouette stays)")
	scene.skip_motion()
	assert_false(scene.city_held(), "it lands once the turn has")
	scene.end_turn()
	await BoundedWait.until(get_tree(), _settled.bind(scene), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	assert_false(scene.city_held(), "and when the replay plays out")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/neon_city.gd")
	assert_true(src.contains("if key != \"\" and hold_landing and _sky_shown and key != _baked_key:"), "the city keeps its silhouette while held")
	await _close(scene)


func test_a_card_dealt_in_starts_whole_on_screen() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		var half: float = ZineCard.STICKER_SIZE.x * scene._hand_scale * 0.5
		var spot: Vector2 = scene._deck_spot()
		assert_gte(spot.x - half, scene.get_global_rect().position.x, "x%.1f: the dealt card's left edge is on screen" % scale)
		await _close(scene)


func test_victory_reads_before_the_loot_opens() -> void:
	assert_gte(Motion.seconds(&"combat_end_hold"), VICTORY_READ, "the netrun holds a won fight long enough to read VICTORY")


## The shortest hold on a won fight before its loot (s): VICTORY reads (it read ~1 s before).
const VICTORY_READ := 1.2
