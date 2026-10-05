extends GutTest
## ART-2 2D (ART_BIBLE v2 §3.1, §1.3, §4.13; DECISIONS "Art direction — ART-2 2D HUD"): the
## combat HUD v4. D15: the result chips beside each HP are the preview, held to the real
## resolve for every enemy x seeds (GDD 2.10, the H23 / H24 sweeps moved onto the chip);
## their format; the replay holds, ticks and fades them; nudge buttons above the wheels; SEND
## IT a vinyl sticker over EXECUTE; RESPIN / UNDO terminal chips with the undo block on UNDO;
## the name sticker over the RAM panel; the layout at text sizes 1.0 / 1.6 / 2.0.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SEEDS: Array[int] = [1, 5, 9, 13]
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _settings: Dictionary = {}
var _events: Array[Dictionary] = []


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art2_hud"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Settings.restore(_settings)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


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


func _on_state(_state: CombatState, events: Array[Dictionary]) -> void:
	_events = events.duplicate(true)


## Every enemy in content the resolver knows.
func _enemy_ids(lookup: ContentLookup) -> Array[StringName]:
	var out: Array[StringName] = []
	for id in RunManager.lookup().ids_of_class(&"EnemyData"):
		if lookup.has(id):
			out.append(id)
	out.sort()
	return out


## The chips of every wheel now (id -> chips), from the scene's own rows.
func _rows(scene: Control) -> Dictionary:
	var out := {}
	var st: CombatState = scene.engine.state()
	for c in [st.player] + st.enemies:
		if not (c as CombatantState).is_satellite:
			out[c.id] = (scene.result_chips(c.id) as Array).duplicate(true)
	return out


## Holds a row shown before an action to what the action really did: the chips the real
## resolve gives (same model, the real events and states) and the HP, RAM, guard and status
## changes themselves. A random roll shows its odds, never the roll: it must still have landed.
func _check(label: String, shown: Dictionary, before: CombatState, after: CombatState, events: Array[Dictionary]) -> int:
	var checked := 0
	for id in shown:
		var chips: Array = shown[id]
		var random_status := -1
		for c in chips:
			if StringName(c["kind"]) == ResultChipModel.STATUS and bool(c.get("random", false)):
				random_status = int(c["status"])
		var heat := ResultChipModel.value_of(chips, ResultChipModel.HEAT)
		var real := ResultChipModel.build(before, after, events, id, random_status, heat)
		assert_eq(HudResultChips.signature(chips), HudResultChips.signature(real), "%s %s: chip == resolve" % [label, id])
		var b := before.get_combatant(id)
		var a := after.get_combatant(id)
		var hp_after := a.hp if a != null else 0
		assert_eq(b.hp + ResultChipModel.hp_change(chips), hp_after, "%s %s: the chips' HP change is the real one" % [label, id])
		var sums := ResultChipModel.sums_for(events, id, b.is_player)
		assert_eq(ResultChipModel.value_of(chips, ResultChipModel.ABSORBED), int(sums["absorbed"]), "%s %s: absorbed" % [label, id])
		assert_eq(ResultChipModel.value_of(chips, ResultChipModel.GAINED), int(sums["gained"]), "%s %s: gained" % [label, id])
		if b.is_player:
			assert_eq(ResultChipModel.value_of(chips, ResultChipModel.RAM), int(sums["ram_lost"]), "%s: RAM lost" % label)
		if random_status >= 0 and a != null:
			var landed := false
			for i in a.wheel.slice_statuses.size():
				if a.wheel.slice_statuses[i] == random_status and b.wheel.slice_statuses[i] != random_status:
					landed = true
			assert_true(landed, "%s %s: the random status the chip announced landed" % [label, id])
		checked += chips.size()
	return checked


## The real SEND IT (the session's own END_TURN): [the resolved state, the resolve's events].
## The chips preview the resolve (GDD 2.10: the next turn's start respins at random and is
## never previewed), so the result they are held to stops at the turn start.
func _real_end_turn(scene: Control) -> Array:
	var eng: CombatEngine = scene.engine
	var r: CombatResult = eng.session.apply(CombatAction.end_turn())
	assert_true(r.ok(), "SEND IT resolves")
	var events: Array[Dictionary] = []
	for e in r.events:
		if String(e.get("type", "")) == "turn_start":
			break
		events.append(e)
	scene._refresh(eng.state())
	return [r.resolved_state, events]


# --- D15: the chip is the preview -------------------------------------------------------

func test_d15_chips_equal_the_resolve_for_every_enemy_and_seed() -> void:
	var scene := await _combat()
	var eng: CombatEngine = scene.engine
	eng.state_changed.connect(_on_state)
	var enemies := _enemy_ids(eng.resolver.lookup)
	assert_gt(enemies.size(), 3, "enemies to sweep")
	var checked := 0
	var fights := 0
	for enemy in enemies:
		for combat_seed in SEEDS:
			scene.start_fight(enemy, combat_seed)
			scene.skip_motion()
			if eng.state().is_over():
				continue
			fights += 1
			# SEND IT now: the rows, then the real resolve.
			scene._show_end_turn_preview()
			var shown := _rows(scene)
			var before: CombatState = eng.state().duplicate_state()
			var real := _real_end_turn(scene)
			checked += _check("%s seed %d send" % [enemy, combat_seed], shown, before, real[0], real[1])
			# A card's hover then its play and SEND IT, on the next turn.
			if eng.state().is_over():
				continue
			var st: CombatState = eng.state()
			for i in st.hand.size():
				var card := eng.content(st.hand[i]) as CardData
				if card == null or card.ram_cost > st.ram or CardTargeting.is_random(card):
					continue
				var options := CardTargeting.options(eng.resolver, st, i)
				if options.is_empty():
					continue
				var action: CombatAction = options[0]
				for o in options:
					if o.wheel_id == st.target_id and o.direction == 1:
						action = o
						break
				if eng.validate(action) != "":
					continue
				scene._preview_action(action)
				var hovered := _rows(scene)
				var before_card: CombatState = st.duplicate_state()
				var all: Array[Dictionary] = []
				_events = []
				assert_true(eng.submit(action), "%s seed %d: the card plays" % [enemy, combat_seed])
				all.append_array(_events)
				scene.skip_motion()
				var real_card := _real_end_turn(scene)
				all.append_array(real_card[1])
				checked += _check("%s seed %d card %d" % [enemy, combat_seed, i], hovered, before_card, real_card[0], all)
				break
	eng.state_changed.disconnect(_on_state)
	assert_gt(fights, enemies.size(), "fights swept")
	assert_gt(checked, fights, "chips checked (%d)" % checked)
	await _close(scene)


func test_d15_chip_format_and_order() -> void:
	var before := CombatState.new()
	var p := CombatantState.new()
	p.id = &"player"
	p.is_player = true
	p.hp = 40
	p.max_hp = 60
	p.wheel = WheelState.new()
	p.wheel.slice_statuses.assign([RC.Status.NONE, RC.Status.NONE, RC.Status.NONE])
	before.player = p
	var after := before.duplicate_state()
	after.player.hp = 34
	after.player.wheel.slice_statuses.assign([RC.Status.CORRUPTED, RC.Status.CORRUPTED, RC.Status.NONE])
	var events: Array[Dictionary] = [
		{"type": "damage", "attacker": &"e0", "target": &"player", "amount": 10, "blocked": 4, "shielded": 0, "hp_damage": 6},
		{"type": "shield", "target": &"player", "amount": 4},
		{"type": "ram", "amount": -1},
		{"type": "ram", "amount": 4},
	]
	var chips := ResultChipModel.build(before, after, events, &"player")
	var labels: Array = chips.map(func(c: Dictionary) -> String: return ResultChipModel.label(c))
	assert_eq(labels, ["-6", "(4", "+4", "-1", "%s×2" % Palette.STATUS_GLYPHS[RC.Status.CORRUPTED]], "D15: [final damage] (N shield) +N shield -N RAM status×N")
	assert_eq(StringName(chips[0]["kind"]), ResultChipModel.DAMAGE)
	assert_eq(StringName(chips[3]["kind"]), ResultChipModel.RAM, "only RAM lost shows (the refill comes from the TURN banner)")
	assert_eq(ResultChipModel.hp_change(chips), -6)
	assert_eq(HudResultChips.chip_color(chips[0]), HudSkin.CHIP_DAMAGE, "red")
	assert_eq(HudResultChips.chip_color(chips[1]), HudSkin.CHIP_ABSORBED, "blue")
	assert_eq(HudResultChips.chip_color(chips[2]), HudSkin.CHIP_GAIN, "green")
	for c in chips:
		assert_ne(ResultChipModel.words(c), "", "every chip says itself in words")
	# A lethal hit: the damage chip says so.
	var dead := before.duplicate_state()
	dead.player.hp = 0
	var lethal := ResultChipModel.build(before, dead, [{"type": "damage", "attacker": &"e0", "target": &"player", "amount": 50, "blocked": 0, "shielded": 0, "hp_damage": 40}] as Array[Dictionary], &"player")
	assert_true(bool(lethal[0]["lethal"]), "LETHAL")


func test_the_chip_row_shows_beside_each_hp_with_its_breakdown() -> void:
	var scene := await _combat(1.0, &"compliance_officer", 5)
	scene._show_end_turn_preview()
	await _frames()
	var st: CombatState = scene.engine.state()
	for c in [st.player, st.enemies[0]]:
		var row: HudResultChips = scene.chip_row(c.id)
		var view: WheelView = scene._view_of(c.id)
		assert_true(view.hud_results, "%s: the view draws no tag and no NEXT plate" % c.id)
		assert_false(view.intent_rect().has_area(), "%s: no forecast tag" % c.id)
		var hp: Rect2 = view.hp_layout()["hp"]
		var hpg := Rect2(view.global_position + hp.position, hp.size)
		if row.chips.is_empty():
			continue
		var rr := row.get_global_rect()
		assert_true(rr.position.x >= hpg.end.x or rr.position.y >= hpg.end.y, "%s: beside (or under) the HP number" % c.id)
		assert_true(absf(rr.get_center().y - hpg.get_center().y) < hpg.size.y + rr.size.y, "%s: on the HP's line" % c.id)
		assert_string_contains(row.tooltip_text, "->", "%s: the breakdown names the HP it ends on" % c.id)
		assert_ne(row.tip_title, "", "%s: the breakdown's title" % c.id)
	await _close(scene)


func test_the_replay_holds_ticks_and_fades_the_chips() -> void:
	var scene := await _combat(1.0, &"collections_agent", 5)
	Motion.force_live = true
	scene._show_end_turn_preview()
	var shown: Array = (scene.result_chips(&"player") as Array).duplicate(true)
	scene.end_turn()
	var row: HudResultChips = scene.chip_row(&"player")
	if not shown.is_empty():
		assert_true(row.holding, "the row holds what it showed when SEND IT was pressed")
		assert_eq(HudResultChips.signature(row.held), HudResultChips.signature(shown), "the same chips")
	# One press ends it all (MotionSkip): the row is live again, no tween left.
	scene.skip_motion()
	assert_false(row.holding, "a skip releases the row")
	assert_false(row.motion_running(), "nothing left playing")
	Motion.force_live = false
	await _close(scene)


func test_chip_motion_shows_the_end_state_without_motion() -> void:
	# Headless (or reduce effects): a tick is whole at once and a fade gone, nothing waits.
	var row := HudResultChips.new()
	add_child_autofree(row)
	var chips: Array = [{"kind": ResultChipModel.DAMAGE, "value": 3, "icon": "", "good": false, "lethal": false}]
	row.set_result(chips, "T", "B")
	row.hold(chips)
	row.tick(0)
	assert_eq(float(row.ticks[0]), 1.0, "the tick at its end state")
	row.fade()
	assert_eq(row.held_alpha, 0.0, "faded at once")
	assert_false(row.motion_running())
	assert_true(UiMotionData.REQUIRED_IDS.has(&"forecast_tick") and UiMotionData.REQUIRED_IDS.has(&"forecast_fade") and UiMotionData.REQUIRED_IDS.has(&"intent_flip"),
		"the chips run on the tag's motion entries")


# --- Controls ---------------------------------------------------------------------------

func test_send_it_is_a_vinyl_sticker_and_respin_undo_are_terminal_chips() -> void:
	var scene := await _combat()
	var send: Control = scene._end_turn_button
	assert_true(send is SendItSticker, "SEND IT is the vinyl sticker")
	assert_eq((send as SendItSticker).system_word, "EXECUTE", "over the system word EXECUTE")
	assert_true(scene._respin_button is TerminalChip and scene._rewind_button is TerminalChip, "RESPIN / UNDO are terminal chips")
	var undo: TerminalChip = scene._rewind_button
	assert_eq(undo.disabled, not scene.engine.can_rewind(), "UNDO is off while blocked")
	if undo.disabled:
		assert_eq(undo.state(), KitState.DISABLED, "the undo block shows on UNDO (grey, lock tick), never as a word")
	assert_eq(undo.parts()[0], tr("UNDO"), "the verb first")
	assert_true(scene.name_sticker.words.contains("//"), "the CELL // CLASS sticker: %s" % scene.name_sticker.words)
	var ns: Rect2 = scene.name_sticker.get_global_rect()
	var ram: Rect2 = scene.ram_note.get_global_rect()
	assert_true(ns.position.y < ram.position.y and ns.end.y > ram.position.y - 1.0, "the name sticker sits just over the RAM panel")
	await _close(scene)


func test_nudges_sit_on_one_line_above_each_wheel() -> void:
	var scene := await _combat(1.0, &"compliance_officer", 5)
	await _frames()
	for v in scene._views():
		var wv := v as WheelView
		var ars := wv.arrows()
		assert_gt(ars.size(), 1, "nudges on every wheel")
		var top := wv.global_center().y - wv.disc_radius()
		var ys := {}
		for ar in ars:
			var c := wv.arrow_center(int(ar["ring"]), int(ar["direction"]))
			assert_lt(c.y, top, "%s: above the wheel" % wv.combatant.id)
			ys[roundi(c.y)] = true
			assert_eq(wv.zone_at(c).get("kind", ""), "arrow", "the button is still the view's nudge zone")
			if int(ar["direction"]) < 0:
				assert_lt(c.x, wv.global_center().x, "counter-clockwise on the left")
			else:
				assert_gt(c.x, wv.global_center().x, "clockwise on the right")
		assert_eq(ys.size(), 1, "%s: one line" % wv.combatant.id)
	await _close(scene)


func test_the_hud_fits_at_every_text_size() -> void:
	for scale in SCALES:
		var scene := await _combat(scale, &"compliance_officer", 5)
		scene._show_end_turn_preview()
		await _frames(4)
		assert_eq(scene.layout_violations(), [] as Array[String], "x%.1f: layout rules" % scale)
		gut.p("x%.1f: send %s stickers %s cell %s banner %s card scale %.2f radius %.0f" % [scale, scene._end_turn_button.size, scene._sticker_box.size,
			scene._cell_panel.size, scene._banner.size, scene._hand_scale, scene._player_view._radius()])
		var parts: Array[Control] = [scene._end_turn_button, scene._respin_button, scene._rewind_button, scene.name_sticker, scene.ram_note, scene._banner]
		parts = parts.filter(func(c: Control) -> bool: return c.is_visible_in_tree())  # the name sticker stands down above 1.3
		for c in parts:
			assert_true(SCREEN.grow(0.5).encloses(c.get_global_rect()), "x%.1f: %s on screen %s" % [scale, c.name, c.get_global_rect()])
		for i in parts.size():
			for j in range(i + 1, parts.size()):
				if parts[i] == scene.name_sticker and parts[j] == scene.ram_note:
					continue  # the sticker overlaps the panel's top edge on purpose
				assert_false(parts[i].get_global_rect().intersects(parts[j].get_global_rect()), "x%.1f: %s and %s apart" % [scale, parts[i].name, parts[j].name])
		await _close(scene)
