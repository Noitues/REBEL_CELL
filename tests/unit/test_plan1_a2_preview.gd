extends GutTest
## Change plan 1, W2-A2: the planned outcome. Every number the new chips, the queue readout and the RAM
## bar forecast is read from the resolver's own after-state (preview = result): HP before -> after (a kill
## reads "-> 0", never the over-damage), a spin, a NULL landing, the RAM the next turn starts with, the
## queue's net, a satellite's row. F11: the enemy's nudge arrows preview like your own.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Vector2(1280, 720)

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = "gut_plan1_a2"
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Settings.restore(_settings)
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(combat_seed: int, enemy: StringName = &"collections_agent", scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, combat_seed)
	await _frames()
	return scene


func _chip(chips: Array, kind: StringName) -> Dictionary:
	for c in chips:
		if StringName(c["kind"]) == kind:
			return c
	return {}


func _is_random(scene: Control, i: int) -> bool:
	var card := scene.engine.content(scene.engine.state().hand[i]) as CardData
	return card == null or CardTargeting.is_random(card)


## Every deterministic play the hand and the nudge arrows offer now.
func _plays(scene: Control) -> Array[CombatAction]:
	var st: CombatState = scene.engine.state()
	var out: Array[CombatAction] = []
	for i in st.hand.size():
		if _is_random(scene, i):
			continue
		for a in CardTargeting.options(scene.engine.resolver, st, i):
			if scene.engine.validate(a) == "":
				out.append(a)
				break
	for wheel in [st.player.id, st.enemies[0].id]:
		for d in [-1, 1]:
			out.append(CombatAction.nudge(wheel, d, RC.RingScope.OUTER))
	return out


# --- HP before -> after ----------------------------------------------------------------------

func test_hp_line_is_the_resolvers_after_state_for_every_hovered_play() -> void:
	var checked := 0
	for combat_seed in [1, 5, 7, 9]:
		var scene: Control = await _combat(combat_seed)
		var st: CombatState = scene.engine.state()
		for a in _plays(scene):
			var turn: CombatResult = scene.engine.preview_turn_after(a)
			if turn == null:
				continue
			scene._preview_action(a)
			for id in [st.player.id, st.enemies[0].id]:
				var line := _chip(scene.result_chips(id), ResultChipModel.HP_LINE)
				var was := st.get_combatant(id).hp
				var now := maxi(0, turn.state.get_combatant(id).hp)
				if now == was:
					assert_true(line.is_empty(), "seed %d: no HP line when %s keeps its HP" % [combat_seed, id])
				else:
					assert_eq([int(line.get("before", -1)), int(line.get("after", -1))], [was, now], "seed %d %s: HP %d -> the resolver's %d" % [combat_seed, id, was, now])
					assert_eq(ResultChipModel.label(line), "%d→%d" % [was, now])
					checked += 1
	assert_gt(checked, 6, "HP lines were checked (%d)" % checked)


## Scans the wheel's rotation until `fatal` holds on the End Turn preview.
func _find_rotation(scene: Control, wheel: CombatantState, fatal: Callable) -> bool:
	for r in RC.TICKS:
		wheel.wheel.rotation = r
		if fatal.call(scene.engine.preview_end_turn().state):
			return true
	return false


func test_a_kill_reads_zero_never_the_over_damage_and_your_lethal_turn_warns() -> void:
	var scene: Control = await _combat(7)
	var st: CombatState = scene.engine.state()
	st.enemies[0].hp = 1
	assert_true(_find_rotation(scene, st.player, func(s: CombatState) -> bool: return not s.enemies[0].is_alive()), "a rotation that kills the Agent")
	scene._show_end_turn_preview()
	var kill := _chip(scene.result_chips(st.enemies[0].id), ResultChipModel.HP_LINE)
	assert_eq([int(kill["before"]), int(kill["after"])], [1, 0], "1 -> 0")
	assert_eq(ResultChipModel.label(kill), "1→0")
	for v in scene._views():
		for c in v.intent.get("chips", []):
			assert_false(String(c["text"]).contains("LEFT"), "no 'N LEFT' wording left (%s)" % c["text"])
	# Your own lethal turn: HP 1, the Agent's needle where it hurts.
	var scene2: Control = await _combat(7)
	var st2: CombatState = scene2.engine.state()
	st2.player.hp = 1
	st2.player.block = 0
	var found := false
	for rot in RC.TICKS:
		st2.enemies[0].wheel.rotation = rot
		if not scene2.engine.preview_end_turn().state.player.is_alive():
			found = true
			break
	assert_true(found, "a needle that kills the operative")
	scene2._show_end_turn_preview()
	var row: Array = scene2.result_chips(st2.player.id)
	assert_false(_chip(row, ResultChipModel.LETHAL).is_empty(), "a lethal turn is flagged on your row")
	var line := _chip(row, ResultChipModel.HP_LINE)
	assert_eq([int(line["before"]), int(line["after"])], [1, 0], "your HP 1 -> 0, whatever the hit was")
	assert_string_contains(ResultChipModel.words(_chip(row, ResultChipModel.LETHAL)), "LETHAL")


func test_the_hit_chip_text_clamps_to_zero() -> void:
	var script: Script = load("res://scripts/ui/combat_scene.gd")
	assert_eq(script.hit_chip_text("YOU", 11, 5), tr("HITS %s → 0") % "YOU")
	assert_eq(script.hit_chip_text("YOU", 11, 11), tr("HITS %s %d") % ["YOU", 11])


# --- the spin, the NULL, F11 -----------------------------------------------------------------

func test_a_spin_chip_is_the_rotation_the_play_really_makes_on_either_wheel() -> void:
	var checked := 0
	for combat_seed in [3, 7]:
		for who in [&"player", &"enemy"]:
			for d in [-1, 1]:
				var scene: Control = await _combat(combat_seed)
				var st: CombatState = scene.engine.state()
				var id: StringName = st.player.id if who == &"player" else st.enemies[0].id
				var before := st.get_combatant(id).wheel.rotation
				scene._preview_nudge(id, {"kind": "arrow", "ring": RC.RingScope.OUTER, "direction": d})
				var chip := _chip(scene.result_chips(id), ResultChipModel.SPIN)
				assert_false(chip.is_empty(), "seed %d: hovering the %s's nudge shows its spin (F11)" % [combat_seed, who])
				assert_ne(String(chip.get("tip", "")), "", "the spin says where the needle goes")
				var v: WheelView = scene._view_of(id)
				assert_ne(v.play_note, "", "the %s's tag names the hovered nudge, like your own" % who)
				scene.nudge_wheel(id, d, RC.RingScope.OUTER)
				scene.skip_motion()
				var real := ResultChipModel.spin_ticks(before, scene.engine.state().get_combatant(id).wheel.rotation)
				assert_eq(int(chip["value"]), real, "seed %d %s %+d: the chip is the real spin" % [combat_seed, who, d])
				checked += 1
	assert_eq(checked, 8)


func test_a_null_landing_says_null_only_when_a_needle_is_on_it() -> void:
	var scene: Control = await _combat(7)
	var st: CombatState = scene.engine.state()
	var nulls := 0
	for r in RC.TICKS:
		st.player.wheel.rotation = r
		scene._show_end_turn_preview()
		var on_null := false
		for rd in scene.engine.resolver.pointer_readouts(st, st.player):
			if (rd["slice"] as SliceData).slice_type == RC.SliceType.NULL:
				on_null = true
		var chip := _chip(scene.result_chips(st.player.id), ResultChipModel.NULL_LAND)
		assert_eq(not chip.is_empty(), on_null, "rotation %d: the NULL chip appears iff a needle lands on NULL" % r)
		if on_null:
			nulls += 1
			assert_string_contains(String(chip.get("tip", "")), "NULL")
	assert_gt(nulls, 0, "some rotation lands on NULL")


# --- RAM after SEND IT -----------------------------------------------------------------------

func test_ram_next_turn_is_the_ram_the_next_turn_really_starts_with() -> void:
	var checked := 0
	for combat_seed in [1, 4, 7, 11]:
		for played in [0, 1, 2]:
			var scene: Control = await _combat(combat_seed)
			for k in played:
				for a in _plays(scene):
					if a.type == CombatAction.Type.PLAY_CARD and scene.engine.state().ram >= (scene.engine.content(scene.engine.state().hand[a.hand_index]) as CardData).ram_cost:
						scene.engine.submit(a)
						break
			var eng: CombatEngine = scene.engine
			var forecast := eng.resolver.ram_next_turn(eng.preview_end_turn().state)
			scene._show_end_turn_preview()
			assert_eq(scene.ram_note.next_turn, forecast, "the RAM bar carries the forecast")
			assert_true(eng.submit(CombatAction.end_turn()))
			assert_eq(eng.state().ram, forecast, "seed %d after %d plays: RAM the next turn starts with" % [combat_seed, played])
			checked += 1
	assert_eq(checked, 12)


# --- the queue readout -----------------------------------------------------------------------

func _play_cards(scene: Control, n: int) -> int:
	var done := 0
	for k in n:
		var st: CombatState = scene.engine.state()
		for i in st.hand.size():
			var card := scene.engine.content(st.hand[i]) as CardData
			var opts := CardTargeting.options(scene.engine.resolver, st, i)
			if card == null or opts.is_empty() or CardTargeting.is_random(card) or card.ram_cost > st.ram or scene.engine.validate(opts[0]) != "":
				continue
			scene.play_card(i)
			scene.skip_motion()
			done += 1
			break
	return done


func test_the_queue_lists_the_plays_the_running_ram_and_the_net_of_the_plan() -> void:
	var scene: Control = await _combat(7)
	assert_true(scene.queue_rows().is_empty(), "nothing queued, no readout")
	var ram0: int = scene.engine.state().ram
	assert_eq(_play_cards(scene, 2), 2)
	var st: CombatState = scene.engine.state()
	scene._show_end_turn_preview()
	var rows: Array[Dictionary] = scene.queue_rows()
	assert_eq(String(rows[0]["left"]), "THIS TURN")
	assert_eq(String(rows[0]["right"]), "RAM -%d" % (ram0 - st.ram), "the total RAM cost of the chain")
	var steps := 0
	for r in rows:
		if String(r["left"]).begins_with("1 ") or String(r["left"]).begins_with("2 "):
			steps += 1
	assert_eq(steps, 2, "each played action is listed")
	# The net of the plan = the End Turn resolve's own after-state.
	var resolved: CombatState = scene.engine.preview_end_turn().state
	var you := ""
	for r in rows:
		if String(r["left"]) == "YOU":
			you = String(r["right"])
	assert_eq(you, "%d→%d" % [scene._turn_queue.base_state().player.hp, maxi(0, resolved.player.hp)], "your HP, turn start -> after SEND IT")
	var ram_row: Dictionary = rows[rows.size() - 1]
	assert_eq(String(ram_row["right"]), "%d→%d  NEXT %d" % [ram0, resolved.ram, scene.engine.resolver.ram_next_turn(resolved)])
	# A third play hovered joins the list with its cost.
	var pending := false
	for a in _plays(scene):
		if a.type == CombatAction.Type.PLAY_CARD and scene.engine.validate(a) == "":
			scene._preview_action(a)
			for r in scene.queue_rows():
				if String(r["left"]).begins_with("> "):
					pending = true
			break
	assert_true(pending, "the hovered play shows as '> NAME' after the played ones")
	# UNDO drops the last step; SEND IT starts the list over.
	scene._show_end_turn_preview()
	scene.rewind()
	scene.skip_motion()
	scene._show_end_turn_preview()
	var after_undo := 0
	for r in scene.queue_rows():
		if String(r["left"]).begins_with("1 ") or String(r["left"]).begins_with("2 "):
			after_undo += 1
	assert_eq(after_undo, 1, "UNDO takes the last step off")
	scene.end_turn()
	scene.skip_motion()
	await _frames()
	assert_true(scene.queue_rows().is_empty(), "a new turn starts an empty list")


func test_the_queue_panel_holds_the_layout_at_every_text_size() -> void:
	for ts in [1.0, 1.6, 2.0]:
		var scene: Control = await _combat(7, &"collections_agent", ts)
		_play_cards(scene, 2)
		scene._show_end_turn_preview()
		scene._relayout()
		await _frames()
		var panel: Control = scene._queue_panel
		assert_true(panel.visible, "x%.1f: the readout shows after two plays" % ts)
		var rect := panel.get_global_rect()
		assert_true(scene.get_global_rect().grow(0.5).encloses(rect), "x%.1f: on screen (%s)" % [ts, rect])
		for v in scene._views():
			if (v as WheelView).combatant != null:
				assert_false((v as WheelView).covers(rect), "x%.1f: off %s's wheel" % [ts, v.combatant.display_name])
		assert_false(rect.intersects(scene._banner.get_global_rect()), "x%.1f: clear of the turn banner" % ts)
		assert_true(scene.layout_violations().is_empty(), "x%.1f: %s" % [ts, scene.layout_violations()])


# --- a satellite's row, a random status's odds -----------------------------------------------

func test_a_satellite_has_a_row_of_its_own_read_from_the_resolve() -> void:
	var found := 0
	for combat_seed in range(1, 16):
		var scene: Control = await _combat(combat_seed)
		var st: CombatState = scene.engine.state()
		var sats := st.satellites_of(st.enemies[0].id)
		if sats.is_empty():
			scene.get_parent().queue_free()
			continue
		scene._show_end_turn_preview()
		var resolved: CombatState = scene.engine.preview_end_turn().state
		var host: WheelView = scene._view_of(st.enemies[0].id)
		var rows: Dictionary = scene.hud_layer.sat_rows.get(host, {})
		for sat in sats:
			var rs := resolved.get_combatant(sat.id)
			var changed := rs == null or rs.hp != sat.hp or rs.block != sat.block
			var row: HudResultChips = rows.get(sat.id)
			if changed:
				assert_not_null(row, "seed %d: %s changes, so it has a row" % [combat_seed, sat.display_name])
				if row != null:
					var line := _chip(row.chips, ResultChipModel.HP_LINE)
					if rs != null and rs.hp != sat.hp:
						assert_eq(int(line.get("after", -1)), maxi(0, rs.hp), "the satellite's HP line is the resolver's")
					found += 1
			elif row != null:
				assert_true(row.chips.is_empty(), "seed %d: an unchanged satellite shows no chips" % combat_seed)
		scene.get_parent().queue_free()
		if found > 0:
			break
	assert_gt(found, 0, "some seed docks a satellite that changes")


func test_a_random_status_chip_says_its_odds_and_its_source() -> void:
	var found := 0
	for combat_seed in range(1, 12):
		var scene: Control = await _combat(combat_seed)
		var st: CombatState = scene.engine.state()
		scene._show_end_turn_preview()
		var chip := _chip(scene.result_chips(st.player.id), ResultChipModel.STATUS)
		if chip.is_empty() or not bool(chip.get("random", false)):
			scene.get_parent().queue_free()
			continue
		var tip := String(chip.get("tip", ""))
		assert_string_contains(tip, "%", "the odds are on the chip")
		assert_string_contains(tip, st.enemies[0].display_name.to_upper(), "and who puts it there")
		found += 1
		break
	assert_gt(found, 0, "some seed's enemy puts a random status on you")
