extends GutTest
## Animation pass ANIM-R5 (the fifth fix batch), combat (DECISIONS "Animation pass — ANIM-R5
## combat"): the outcome waits for its beat (1); a lost fight looks lost and says JACK OUT (2);
## LETHAL by the HP instead of a cross over the hub, one DEFEAT chip (3); ticks at the chip's
## end (4); a doomed wheel acts before its HP reaches 0 (5); NO DAMAGE off the hub's name (6);
## a preview shows what the tag was (7); tags that say who gets what (8); every tooltip
## translated once (9); the next step's click by the one press rule (10); no await on a freed
## scene (11); STYLE_GUIDE's notation (12); reduce effects for the R4 motions (13).

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.3, 1.6]
## Fights tried for one that ends the way a test wants.
const SEEDS := 40

var _scale: float = 1.0
var _reduce: bool = false
var _landed: int = 0


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r5"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	_landed = 0


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	Engine.time_scale = 1.0
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	_pseudo(false)
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


func _reduced() -> void:
	if not Settings.reduce_effects:
		Settings.set_reduce_effects(true)
	Fx.apply_settings()
	Motion.force_live = false


## ANIM-R6 A18: on, then the project's own pseudolocalisation values back (PseudoLoc).
func _pseudo(on: bool) -> void:
	if on:
		PseudoLoc.on()
	else:
		PseudoLoc.off()


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


func _has_combat(net: Control) -> bool:
	return net.combat_scene != null


func _count_landed() -> void:
	_landed += 1


func _outcome_done(scene: Control) -> bool:
	return not scene.outcome_pending()


# --- 1: the outcome waits for its beat ------------------------------------------------------------

func test_a_lost_fight_keeps_its_outcome_until_the_beat() -> void:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.DEFEAT), "a fight that ends in DEFEAT was found")
	scene.show_continue(TextDb.mark("JACK OUT"))
	_live()
	var heat_before: int = scene.heat_poster.heat
	scene.outcome_landed.connect(_count_landed)
	scene.end_turn()
	assert_true(scene.engine.state().is_over(), "the state is final at once")
	assert_true(scene.outcome_pending(), "the outcome waits for the replay")
	assert_false(scene._status.text.contains(tr("DEFEAT")), "the status line doesn't say DEFEAT before the hit")
	assert_false(scene.continue_shown(), "JACK OUT waits too")
	assert_true(scene._end_turn_button.visible, "SEND IT stays (spent) until DEFEAT lands")
	assert_eq(scene.heat_poster.heat, heat_before, "Heat doesn't move before the outcome")
	assert_false(scene._player_view.flatlined, "no DEFEAT stamp before the hit")
	var done := await BoundedWait.until(get_tree(), _outcome_done.bind(scene), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	assert_true(done, "the replay lands the outcome")
	assert_string_contains(scene._status.text, tr("DEFEAT"))
	assert_true(scene.continue_shown(), "JACK OUT shows once DEFEAT lands")
	assert_true(scene._player_view.flatlined, "the DEFEAT stamp is on the operative's wheel")
	assert_eq(_landed, 1, "outcome_landed once")
	# DEFEAT lands with the HP already at 0: never before an HP roll has ended.
	assert_eq(roundi(scene._player_view.shown_hp()), 0, "the HP reads 0 when DEFEAT lands")
	await _close(scene)


func test_the_outcome_lands_after_every_hp_roll() -> void:
	var timing: Dictionary = load("res://scripts/ui/combat_scene.gd").beat_timing()
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var hit := {"kind": "damage", "phase": "resolve", "pass": "offensive", "source": &"e0", "target": &"player", "amount": 5, "hp_after": 0,
		"soaked": 0, "side": "enemy"}
	var end := {"kind": "end", "phase": "resolve", "pass": "", "source": &"", "target": &"", "amount": 0, "hp_after": -1, "soaked": 0}
	var beats: Array[Dictionary] = [hit, end]
	var times := PackedFloat32Array([0.2, 0.3])
	var at: float = script.outcome_time(beats, times)
	assert_gte(at, 0.2 + ResolveBeats.settle_after(hit, timing) - 0.0001, "the outcome waits for the HP roll")
	assert_eq(script.outcome_time([hit] as Array[Dictionary], PackedFloat32Array([0.2])), -1.0, "no end, no outcome")


func test_a_win_keeps_victory_and_loot_until_the_beat() -> void:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.VICTORY), "a winning SEND IT was found")
	scene.show_continue(TextDb.mark("LOOT"))
	_live()
	scene.end_turn()
	assert_false(scene._status.text.contains(tr("VICTORY")), "no VICTORY before the killing hit")
	assert_false(scene.continue_shown(), "LOOT waits")
	var ev: WheelView = scene._enemy_views.values()[0]
	assert_gt(roundi(ev.shown_hp()), 0, "the enemy's HP isn't 0 before the hit flies")
	await BoundedWait.until(get_tree(), _outcome_done.bind(scene), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	assert_string_contains(scene._status.text, tr("VICTORY"))
	assert_true(scene.continue_shown())
	await _close(scene)


func test_the_netrun_top_bar_and_report_wait_for_the_outcome() -> void:
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
	assert_not_null(net.combat_scene, "a fight shows")
	_live()
	await net._demo_combat_end("lose")
	var combat: Control = net.combat_scene
	assert_eq(combat.engine.state().outcome, CombatState.Outcome.DEFEAT, "the fight is lost")
	assert_true(combat.outcome_pending(), "its outcome waits")
	assert_string_contains(net._status.text, "|| Run", "the top bar still shows the run (HP, Cycles...)")
	assert_true(net.hud.loadout_button.visible, "VIEW LOADOUT stays until DEFEAT lands")
	await BoundedWait.until(get_tree(), _outcome_done.bind(combat), BoundedWait.motion_limit([&"resolve_sequence"], 6.0))
	assert_false(net._status.text.contains("|| Run"), "then the top bar shows the run ended")
	assert_eq(combat._continue_label, TextDb.mark("JACK OUT"), "the next step says JACK OUT")
	var b := combat._continue_button as DripButton
	assert_ne(b.paint, DripButton.DRIP_PINK, "JACK OUT doesn't wear SEND IT's pink")
	assert_true(b.drips.is_empty(), "nor its drips")
	combat.skip_motion()
	holder.queue_free()
	await _frames(2)


# --- 2: a lost fight looks lost -------------------------------------------------------------------

func test_a_lethal_hit_never_barks_hurt() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var st := CombatState.new()
	st.player = CombatantState.new()
	st.player.id = &"player"
	st.player.max_hp = 60
	st.player.hp = 10
	var e := {"type": "damage", "target": &"player", "hp_damage": 6}
	assert_true(script.hurt_bark_due(e, st), "hurt at a sixth of its HP: it barks")
	st.player.hp = 0
	st.outcome = CombatState.Outcome.DEFEAT
	assert_false(script.hurt_bark_due(e, st), "the hit that flatlines doesn't bark 'keep going'")


func test_the_defeat_stamp_stays_and_shows_at_once_under_reduce_effects() -> void:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.DEFEAT))
	scene.show_continue(TextDb.mark("JACK OUT"))
	_reduced()
	scene.end_turn()
	assert_false(scene.outcome_pending(), "reduce effects: the end state at once")
	assert_null(scene._seq, "no replay")
	assert_string_contains(scene._status.text, tr("DEFEAT"))
	assert_true(scene.continue_shown())
	assert_true(scene._player_view.flatlined, "the DEFEAT stamp shows")
	assert_eq(scene._player_view.flatline_pop, 1.0, "at once")
	await _frames(5)
	assert_true(scene._player_view.flatlined, "and stays")
	await _close(scene)


# --- 3: LETHAL by the HP --------------------------------------------------------------------------

func test_a_lethal_forecast_says_so_by_the_hp_and_once_on_the_tag() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		assert_true(_ending(scene, CombatState.Outcome.DEFEAT))
		await _frames(1)
		var pv: WheelView = scene._player_view
		assert_true(pv.lethal_forecast(), "x%.1f: the operative's wheel knows this turn takes it to 0" % scale)
		var lay := pv.hp_layout()
		assert_string_contains(String(lay["next_text"]), tr("LETHAL"), "x%.1f: the plate says LETHAL" % scale)
		var nr: Rect2 = lay["next"]
		assert_true(Rect2(Vector2.ZERO, pv.size).encloses(nr), "x%.1f: the plate stays in the view (%s in %s)" % [scale, nr, pv.size])
		assert_false(nr.intersects(lay["hp"]), "x%.1f: off the HP number" % scale)
		assert_string_contains(pv._get_tooltip(nr.get_center()), tr("LETHAL: this turn takes you to 0 HP."), "x%.1f: its tooltip says it" % scale)
		var words: Array = []
		for c in pv.intent.get("chips", []):
			words.append(String(c["text"]))
		assert_false(words.has(tr("DOWN")), "x%.1f: no DOWN beside DEFEAT" % scale)
		assert_eq(words.count(tr("DEFEAT")), 1, "x%.1f: one DEFEAT chip" % scale)
		await _close(scene)
	var src := FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd")
	assert_false(src.contains("a red cross over the hub"), "the cross over the hub is gone")


func test_an_enemy_taken_to_zero_shows_lethal_too() -> void:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.VICTORY))
	await _frames(1)
	var ev: WheelView = scene._enemy_views.values()[0]
	assert_true(ev.lethal_forecast())
	assert_string_contains(String(ev.hp_layout()["next_text"]), tr("LETHAL"))
	assert_string_contains(ev._get_tooltip(Rect2(ev.hp_layout()["next"]).get_center()), tr("LETHAL: this turn takes it to 0 HP."))
	await _close(scene)


# --- 4: ticks at the chip's end -------------------------------------------------------------------

func test_ticks_sit_at_the_chip_end_off_its_words() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		for v in scene._views():
			var wv := v as WheelView
			if wv.intent.is_empty():
				continue
			wv.hold_forecast_tag(wv.intent)
			wv.replaying = true
			var r := wv._intent_rect_local()
			var boxes := wv.chip_layout(r)
			assert_gt(boxes.size(), 0, "x%.1f: chips to check" % scale)
			for bx in boxes:
				var tick: Rect2 = bx["tick"]
				assert_true(tick.has_area(), "x%.1f: every chip keeps room for its tick" % scale)
				assert_false(tick.intersects(bx["text"]), "x%.1f: the tick is off '%s'" % [scale, bx["chip"]["text"]])
				assert_true(Rect2(bx["rect"]).grow(0.5).encloses(tick), "x%.1f: at the chip's end, inside it" % scale)
			wv.stop_motion()
		await _close(scene)


# --- 5: a doomed wheel acts before its HP reaches 0 -----------------------------------------------

func _beat(kind: String, src: StringName, tgt: StringName, amount: int, hp_after: int, pass_name: String = "offensive") -> Dictionary:
	return {"kind": kind, "event_index": 0, "phase": "resolve", "pass": pass_name, "source": src, "pointer_index": 0, "target": tgt,
		"amount": amount, "crit": false, "hp_after": hp_after, "slot": 1, "status": RC.Status.CORRUPTED, "tier": -1, "soaked": 0,
		"host": &"", "source_slot": 0, "source_tier": -1, "raw": amount, "blocked": 0, "shielded": 0, "side": "", "wheel_source": true}


func test_a_doomed_wheel_acts_before_its_hp_reaches_zero() -> void:
	var st := CombatState.new()
	st.player = CombatantState.new()
	st.player.id = &"player"
	st.player.is_player = true
	st.player.hp = 60
	st.player.max_hp = 60
	var e0 := CombatantState.new()
	e0.id = &"e0"
	e0.hp = 5
	e0.max_hp = 40
	st.enemies.append(e0)
	var died := _beat("died", &"", &"e0", 0, 0, "")
	died["wheel"] = true
	var beats: Array[Dictionary] = [_beat("damage", &"player", &"e0", 5, 0), _beat("damage", &"e0", &"player", 6, 54),
		_beat("status", &"e0", &"player", 0, -1, "statuses"), died]
	var out := ResolveBeats.doomed_first(st, beats)
	assert_eq(out.size(), beats.size())
	var fatal := -1
	for k in out.size():
		if String(out[k]["kind"]) == "damage" and StringName(String(out[k]["target"])) == &"e0":
			fatal = k
	for k in out.size():
		if StringName(String(out[k]["source"])) == &"e0":
			assert_lt(k, fatal, "the enemy's %s plays before its HP reaches 0" % out[k]["kind"])
			assert_true(bool(out[k].get("same_moment", false)), "marked as the same moment")
	assert_eq(ResolveBeats.final_hp(st, out), ResolveBeats.final_hp(st, beats), "the result is the engine's")
	assert_eq(int(out[fatal]["hp_after"]), 0, "its HP still reaches 0 on the killing hit")


# --- 6: NO DAMAGE off the hub's name --------------------------------------------------------------

func test_no_damage_never_sits_on_the_hub_name() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		for guard in [[0, 0], [5, 0], [5, 4]]:
			for v in scene._views():
				var wv := v as WheelView
				wv.combatant.block = int(guard[0])
				wv.combatant.shield = int(guard[1])
				wv.queue_redraw()
				for word in [tr("NO DAMAGE"), tr("ALL BLOCKED")]:
					var spot := wv.stamp_slot(word, CombatFxLayer.GUARD_NULL)
					var box := WheelView.stamp_bounds(spot, word, CombatFxLayer.GUARD_NULL)
					var ext := wv.hub_text_extent()
					var hub_r := wv.hub_radius()
					var words := Rect2(wv.global_center() + Vector2(-hub_r, ext.x), Vector2(hub_r * 2.0, ext.y - ext.x))
					assert_false(box.intersects(words), "x%.1f guard %s: %s stays off the hub's name and lines (%s vs %s)" % [scale, guard, word, box, words])
					assert_true(wv.get_global_rect().grow(1.0).encloses(box), "x%.1f guard %s: %s stays in its view" % [scale, guard, word])
		await _close(scene)


# --- 7: a preview shows what the tag was ------------------------------------------------------------

func test_a_card_preview_shows_what_the_tag_was() -> void:
	var seen := 0
	for scale in SCALES:
		var scene := await _combat(scale)
		for i in scene.engine.state().hand.size():
			scene._preview_card(i)
			for v in scene._views():
				var wv := v as WheelView
				if wv.was_tag.is_empty():
					continue
				seen += 1
				assert_true(scene.tag_changed(wv.was_tag, wv.intent), "x%.1f: only a changed tag has a before" % scale)
				assert_string_contains(wv.was_text(), String(wv.was_tag["text"]), "x%.1f: the before names its title" % scale)
				var tip := wv._get_tooltip(wv._intent_rect_local().get_center())
				assert_string_contains(tip, tr("Before this play: %s") % wv.was_text(), "x%.1f: the tooltip says it always" % scale)
			assert_eq(scene.layout_violations(), [] as Array[String], "x%.1f card %d: the WAS row breaks no layout rule" % [scale, i])
			scene._show_end_turn_preview()
			for v in scene._views():
				assert_true((v as WheelView).was_tag.is_empty(), "the forecast itself has no before")
		await _close(scene)
	assert_gt(seen, 0, "some preview changed a tag")


func test_the_play_chip_is_not_a_change() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var old := {"text": "ATTACK · GOOD", "chips": [{"text": "HITS YOU 6"}]}
	var same := {"text": "ATTACK · GOOD", "chips": [{"text": "YOU PLAY JOLT", "play": true}, {"text": "HITS YOU 6"}]}
	assert_false(script.tag_changed(old, same))
	assert_true(script.tag_changed(old, {"text": "CRITICAL · GOOD", "chips": [{"text": "HITS YOU 14"}]}))


# --- 8: tags that say who gets what -----------------------------------------------------------------

func test_status_chips_say_who_gets_what() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	var chip: Dictionary = script.random_status_chip(RC.Status.CORRUPTED, true)
	assert_string_contains(String(chip["text"]), tr("YOU GET %s") % tr("CORRUPTED"), "on your tag: you get it")
	var lead: Dictionary = script.odds_lead_chip()
	assert_eq(String(lead["text"]), tr("ON A RANDOM SLICE:"), "the odds say what they are")
	var scene := await _combat()
	var st: CombatState = scene.engine.state()
	var e0: StringName = st.enemies[0].id
	var events: Array[Dictionary] = [{"type": "resolve_start"}, {"type": "pass", "pass": "statuses"}, {"type": "afflict", "attacker": e0},
		{"type": "status", "target": st.player.id, "slot": 1, "status": RC.Status.CORRUPTED, "random": true}]
	var chips: Dictionary = scene.afflict_chips(st, events)
	assert_true(chips.has(e0), "the enemy's tag gets a chip")
	var text := String(chips[e0][0]["text"])
	assert_eq(text, tr("PUTS %s ON YOU") % ("%s %s" % [Palette.STATUS_GLYPHS[RC.Status.CORRUPTED], tr("CORRUPTED")]), "AFFLICT names the status and the victim")
	assert_eq(chips[e0][0]["color"], script.CHIP_LOSS, "bad for you: red")
	await _close(scene)


# --- 9: every tooltip translated once ---------------------------------------------------------------

## A line's string literals: [start, end, body, prefixed by & or ^].
static func _literals(line: String) -> Array:
	var out: Array = []
	var i := 0
	while i < line.length():
		var ch := line[i]
		if ch == "#":
			break
		if ch == "\"":
			var j := i + 1
			while j < line.length() and line[j] != "\"":
				j += 2 if line[j] == "\\" else 1
			out.append([i, j + 1, line.substr(i + 1, j - i - 1), i > 0 and line[i - 1] in ["&", "^"]])
			i = j + 1
			continue
		i += 1
	return out


## Literals on `line` a player would read that are not translated there.
static func _untranslated(line: String) -> Array:
	if line.strip_edges(false, true).ends_with(TextDb.CODE_MARK):
		return []
	var ph := RegEx.create_from_string("%[-+0-9.]*[sdif]|\\\\.")
	var word := RegEx.create_from_string("[A-Za-z]{2,}")
	var ident := RegEx.create_from_string("^[a-z0-9_]*$")
	var out: Array = []
	for l in _literals(line):
		var body: String = l[2]
		if bool(l[3]) or ident.search(body) != null:
			continue
		if word.search(ph.sub(body, "", true)) == null:
			continue
		var pre := line.substr(0, int(l[0])).strip_edges(false, true)
		var post := line.substr(int(l[1])).strip_edges(true, false)
		var translated := false
		for f in ["tr(", "atr(", "TranslationServer.translate(", "TextDb.mark(", "tr_word("]:
			if pre.ends_with(f):
				translated = true
		if translated or post.begins_with(":") or post.begins_with("]") or pre.ends_with("[") or pre.ends_with("==") or pre.ends_with("!="):
			continue
		out.append(body)
	return out


static func _gd_files(dir: String) -> PackedStringArray:
	var out := PackedStringArray()
	var d := DirAccess.open(dir)
	if d == null:
		return out
	for f in d.get_files():
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for sub in d.get_directories():
		out.append_array(_gd_files(dir.path_join(sub)))
	return out


func test_no_tooltip_shows_an_untranslated_literal() -> void:
	var offenders: Array[String] = []
	for path in _gd_files("res://scripts/ui"):
		var lines := FileAccess.get_file_as_string(path).split("\n")
		var in_tip := false
		for i in lines.size():
			var line := lines[i]
			var st := line.strip_edges()
			if st.begins_with("#"):
				continue
			if st.begins_with("func _get_tooltip("):
				in_tip = true
				continue
			if in_tip and st != "" and not line.begins_with("\t"):
				in_tip = false
			if line.contains("tooltip_text = ") or (in_tip and st.begins_with("return")):
				for body in _untranslated(line):
					offenders.append("%s:%d: \"%s\"" % [path, i + 1, body])
	assert_eq(offenders, [] as Array[String], "every tooltip literal is translated (tr / # TR)")


func test_the_scan_catches_what_it_should() -> void:
	assert_eq(_untranslated("\tb.tooltip_text = \"Pause: options.\""), ["Pause: options."])
	assert_eq(_untranslated("\tb.tooltip_text = tr(\"Pause: options.\")"), [])
	assert_eq(_untranslated("\tb.tooltip_text = \"Pause: options.\"  # TR"), [])
	assert_eq(_untranslated("\t\treturn \"%s (%d HP): guards.\" % [a, b]"), ["%s (%d HP): guards."])
	assert_eq(_untranslated("\t\treturn String(intent.get(\"tooltip\", \"\"))"), [])
	assert_eq(_untranslated("\t\treturn TextDb.t(d, \"description\")"), [])


func test_the_tutorial_and_combat_tooltips_translate_under_pseudolocalisation() -> void:
	_pseudo(true)
	for i in TutorialOverlay.STEPS.size():
		var t := TutorialOverlay.step_text(i)
		assert_false(t.contains("{"), "step %d: its keys are filled in" % i)
		assert_ne(t, String(TutorialOverlay.STEPS[i]["text"]), "step %d: translated (scrambled)" % i)
	var tut := TutorialOverlay.new()
	assert_ne(tut.next_button.text, "Next", "Next is translated")
	assert_ne(tut.skip_button.text, "Skip tutorial", "Skip tutorial is translated")
	assert_eq(tut.next_button.auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "and not translated again")
	tut.free()
	var scene := await _combat()
	for c in [scene._status, scene._settings_button, scene.heat_poster, scene._end_turn_button, scene._rewind_button, scene._respin_button, scene.ram_note, scene.portrait]:
		var ctl := c as Control
		assert_eq(ctl.tooltip_auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "%s: shown as given (translated once)" % ctl.name)
	assert_string_contains(scene._end_turn_button.tooltip_text, tr("End the turn: every needle resolves at once (defensive, then offensive, then statuses). The tags show the outcome."))
	assert_eq(scene._player_view.tooltip_auto_translate_mode, Node.AUTO_TRANSLATE_MODE_DISABLED, "the wheel's tooltips translate once")
	var hub: String = scene._player_view._get_tooltip(scene._player_view.global_center() - scene._player_view.global_position)
	assert_false(hub.contains("At 0 HP you lose"), "the hub's tooltip is translated")
	_pseudo(false)
	await _close(scene)


func test_new_words_are_exported_once() -> void:
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for key in ["JACK OUT", "LETHAL", "LETHAL: this turn takes you to 0 HP.", "WAS", "Before this play: %s", "YOU GET %s", "GETS %s",
			"ON A RANDOM SLICE:", "PUTS %s ON YOU", "PUTS %s ON %s", "Skip tutorial", "Next", "THE WHEEL",
			"Pause: options, codex, save and quit.", "RAM %d/%d: pays for cards, respins and extra nudges. Refills each turn.",
			"Nudge %s one tick clockwise.", "Guarded by %s (%d HP): it takes hits aimed at this slice."]:
		assert_true(csv.contains(key), "%s is exported for translation" % key)


# --- 10: the next step's click by the one press rule ------------------------------------------------

func test_only_a_real_click_on_the_next_step_counts() -> void:
	var scene := await _combat()
	assert_true(_ending(scene, CombatState.Outcome.DEFEAT))
	scene.show_continue(TextDb.mark("JACK OUT"))
	scene.end_turn()
	await _frames(2)
	assert_true(scene.continue_shown())
	# Headless, GUT's own panel sits over the screen's bottom-right corner: the button is
	# moved clear of it for each check (no frame passes, so its row doesn't lay it out again).
	var at := CLEAR_SPOT
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.position = at
	click.global_position = at
	_place(scene._continue_button, at)
	assert_true(scene._for_continue(click), "a left click on it counts")
	var right := click.duplicate() as InputEventMouseButton
	right.button_index = MOUSE_BUTTON_RIGHT
	assert_false(scene._for_continue(right), "a right-click works no left-click button")
	var cover := ColorRect.new()
	cover.mouse_filter = Control.MOUSE_FILTER_STOP
	cover.size = SCREEN.size
	scene.get_parent().add_child(cover)
	await _frames(1)
	_place(scene._continue_button, at)
	assert_false(scene._for_continue(click), "a button under a panel is not clicked")
	cover.free()
	_place(scene._continue_button, at)
	scene._continue_button.visible = false
	assert_false(scene._for_continue(click), "a hidden button is not clicked")
	await _close(scene)


## Where the next-step button is put for the click checks (clear of GUT's panel).
const CLEAR_SPOT := Vector2(300, 300)


func _place(c: Control, at: Vector2) -> void:
	c.global_position = at - c.size * 0.5


func _hover(at: Vector2) -> void:
	var m := InputEventMouseMotion.new()
	m.position = at
	m.global_position = at
	get_viewport().push_input(m)


# --- 11: no await on a freed scene --------------------------------------------------------------------

func test_the_perfect_inversion_never_resumes_on_a_freed_scene() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	var body := src.substr(src.find("func _perfect_feedback("), 1200)
	assert_false(RegEx.create_from_string("\\n\\s*await ").search(body.substr(0, body.find("\nfunc ", 10))) != null, "no await in the Perfect feedback")
	var scene := await _combat()
	_live()
	var v: WheelView = scene._player_view
	scene._perfect_feedback(v)
	assert_true(v.inverted, "the inversion shows")
	await _frames(PERFECT_WAIT)
	assert_false(v.inverted, "and ends after its frames")
	scene._perfect_feedback(v)
	assert_true(_perfect_waiting(), "the next inversion frame waits on the tree's frame")
	scene.get_parent().remove_child(scene)
	scene.free()
	# ANIM-R6 A18: a real check (it asserted nothing): the freed scene's frame step is
	# dropped with it, so nothing is left to resume on it.
	assert_false(_perfect_waiting(), "a scene freed mid-inversion leaves nothing to resume")
	await _frames(PERFECT_WAIT)
	assert_false(_perfect_waiting(), "and nothing comes back")


## True while a combat scene's Perfect inversion frame step is connected to the tree's frame.
func _perfect_waiting() -> bool:
	for c in get_tree().process_frame.get_connections():
		var cb: Callable = c["callable"]
		if cb.get_method() == &"_perfect_frame":
			return true
	return false


const PERFECT_WAIT := 4


# --- 12: STYLE_GUIDE's notation ------------------------------------------------------------------------

func test_the_style_guide_uses_the_one_notation() -> void:
	var guide := FileAccess.get_file_as_string("res://docs/STYLE_GUIDE.md")
	assert_false(guide.contains("sword 6 -> shield 5 = -1"), "the arrow formula is gone")
	assert_true(guide.contains("ANIM-R5"), "the R5 combat rules are written down")


# --- 13: reduce effects for the R4 combat motions ------------------------------------------------------

func test_reduce_effects_shows_the_r4_combat_motions_end_state_at_once() -> void:
	var scene := await _combat()
	_reduced()
	scene.end_turn()
	assert_null(scene._seq, "SEND IT: no replay, so no side or attacker gaps")
	assert_false(scene.motion_busy(), "nothing waits")
	assert_eq(scene.motion_seconds_left(), 0.0)
	for v in scene._views():
		assert_false((v as WheelView).replaying, "the wheels show the state")
	# A card that spins a wheel: the forecast never hides.
	for i in scene.engine.state().hand.size():
		scene.select_card(i)
		if scene.selecting >= 0:
			scene.confirm_selection()
		if not scene.card_forecast_held():
			continue
		fail_test("card %d: the forecast is held under reduce effects" % i)
	assert_false(scene.card_forecast_held(), "the forecast shows at once after a card")
	# The RAM refill: the chips show the RAM, no float.
	var bar: RamBar = scene.ram_note
	bar.hold(0)
	bar.play_refill()
	assert_eq(bar.spend_text, "", "no +N RAM float")
	assert_eq(bar.shown_ram, bar.ram, "the chips are full at once")
	await _close(scene)


func test_reduce_effects_takes_loot_at_once() -> void:
	_reduced()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var net: Control = load(NETRUN).instantiate()
	holder.add_child(net)
	net.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	net.new_campaign(1)
	net.start_run(1)
	await _frames()
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	net._show_current()
	PageTransition.settle(net)
	net.choose_reward(0)
	assert_null(net._loot_hold, "the loot page doesn't wait for falling offers")
	assert_eq(FlightFx.active_count(net), 0, "no flight plays")
	holder.queue_free()
	await _frames(2)
