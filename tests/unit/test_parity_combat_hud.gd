extends GutTest
## S-COMBAT-HUD (parity CMB-05..08, CMB-10..18; designer rulings 2026-10-05; DECISIONS "Parity fix —
## card aiming and combat HUD (designer ruling)"): card aiming in grease pencil, the aimed play's
## result on the wheel it changes (held to the real resolve for every card in content: spins,
## nudges, block, damage, evade, drones, statuses, multi-target), the hovered card over the result
## chips, the TURN strip's address line, the CELL-n name sticker, the tutorial between the wheels,
## FIGHT WON / DELETED / FLATLINED, and the layout at text 1.0 / 1.6 / 2.0.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
## Enemies the play sweep fights (a plain one, one with drones / guards, a boss-like one).
const ENEMIES: Array[StringName] = [&"collections_agent", &"care_swarm", &"geostationary_guard"]
## RAM the sweep gives the hand so every card can be aimed.
const SWEEP_RAM := 12

var _settings: Dictionary = {}
var _events: Array[Dictionary] = []


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_combat_hud"
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
	_events.append_array(events)


## Aims card `hand_index` at its option `k` the way a drag over that zone does.
func _aim(scene: Control, hand_index: int, k: int) -> CombatAction:
	var eng: CombatEngine = scene.engine
	var options := CardTargeting.options(eng.resolver, eng.state(), hand_index)
	scene._dragging = true
	scene._begin_targeting(hand_index, options)
	scene._dragging = false
	var sorted: Array[CombatAction] = scene.selection_options()
	scene._option_index = posmod(k, sorted.size())
	scene._show_selection()
	return scene.aimed_action()


# --- The aimed play's result on the wheel (preview == result) ----------------------------------

func test_the_result_on_the_aimed_wheel_is_the_real_play_for_every_card() -> void:
	var scene := await _combat()
	var eng: CombatEngine = scene.engine
	eng.state_changed.connect(_on_state)
	var cards: Array[StringName] = []
	for id in RunManager.lookup().ids_of_class(&"CardData"):
		if eng.resolver.lookup.has(id):
			cards.append(id)
	cards.sort()
	assert_gt(cards.size(), 20, "cards to sweep")
	var checked := 0
	var plays := 0
	var kinds := {}
	for card_id in cards:
		for enemy in ENEMIES:
			scene.start_fight(enemy, 3)
			scene.skip_motion()
			var st: CombatState = eng.state()
			if st.is_over():
				continue
			st.hand[0] = card_id
			st.ram = maxi(st.ram, SWEEP_RAM)
			scene._refresh(st)
			var card := eng.content(card_id) as CardData
			var options := CardTargeting.options(eng.resolver, st, 0)
			if options.is_empty() or card.ram_cost > st.ram:
				continue
			for k in ([0, options.size() - 1] if options.size() > 1 else [0]):
				scene.start_fight(enemy, 3)
				scene.skip_motion()
				st = eng.state()
				st.hand[0] = card_id
				st.ram = maxi(st.ram, SWEEP_RAM)
				scene._refresh(st)
				var action := _aim(scene, 0, k)
				if action == null or eng.validate(action) != "":
					scene.cancel_selection()
					continue
				var plates: Dictionary = scene.play_plates()
				var aimed_c := st.get_combatant(action.wheel_id)
				var aimed_v: WheelView = scene._view_of(aimed_c.host_id if aimed_c != null and aimed_c.is_satellite else action.wheel_id)
				if CardTargeting.is_random(card):
					assert_eq(plates.size(), 0, "%s: a random play shows its odds on the chips, no plate" % card_id)
					scene.cancel_selection()
					continue
				assert_true(plates.has(aimed_v), "%s on %s: the aimed wheel shows the play's result" % [card_id, enemy])
				var shown := {}
				for v in plates:
					shown[(v as WheelView).combatant.id] = ((plates[v] as PlayResultPlate).result as Dictionary).duplicate(true)
				var before: CombatState = st.duplicate_state()
				scene.cancel_selection()
				_events = []
				assert_true(eng.submit(action), "%s: the card plays" % card_id)
				scene.skip_motion()
				var r: CombatResult = eng.session.apply(CombatAction.end_turn())
				assert_true(r.ok(), "SEND IT resolves")
				var events: Array[Dictionary] = _events.duplicate()
				for e in r.events:
					if String(e.get("type", "")) == "turn_start":
						break
					events.append(e)
				var after: CombatState = r.resolved_state
				for id in shown:
					var plate: Dictionary = shown[id]
					var chips: Array = plate["chips"]
					var random_status := -1
					for c in chips:
						if StringName(c["kind"]) == ResultChipModel.STATUS and bool(c.get("random", false)):
							random_status = int(c["status"])
					var real := ResultChipModel.build(before, after, events, id, random_status, ResultChipModel.value_of(chips, ResultChipModel.HEAT))
					assert_eq(HudResultChips.signature(chips), HudResultChips.signature(real), "%s on %s (%s): the plate's chips == the real play" % [card_id, enemy, id])
					var a := after.get_combatant(id)
					assert_eq(int(plate["hp_to"]), a.hp if a != null else 0, "%s on %s (%s): HP after == the real play" % [card_id, enemy, id])
					assert_eq(int(plate["hp_from"]), before.get_combatant(id).hp, "%s: HP before" % card_id)
					checked += 1
				plays += 1
				for e in card.effects:
					if e != null:
						kinds[e.type] = true
	eng.state_changed.disconnect(_on_state)
	for kind in [RC.EffectType.SPIN, RC.EffectType.NUDGE, RC.EffectType.GAIN_BLOCK, RC.EffectType.DEAL_DAMAGE, RC.EffectType.EVADE,
			RC.EffectType.DEPLOY_DRONE, RC.EffectType.APPLY_STATUS]:
		assert_true(kinds.has(kind), "the sweep aimed a %s card" % RC.EffectType.keys()[kind])
	assert_gt(plays, cards.size(), "plays swept (%d)" % plays)
	assert_gt(checked, plays, "plates checked (%d)" % checked)
	await _close(scene)


func test_slices_a_play_changes_are_circled_in_pencil_true_to_the_preview() -> void:
	var scene := await _combat()
	var eng: CombatEngine = scene.engine
	var st: CombatState = eng.state()
	st.hand[0] = &"corrupt_packet"
	st.ram = SWEEP_RAM
	scene._refresh(st)
	var action := _aim(scene, 0, 0)
	assert_not_null(action, "the status card aims")
	var marks: Array[Dictionary] = scene.slice_marks()
	var want := 0
	for v in scene._views():
		if scene.play_plates().has(v):
			want += (v.outcome.get("statuses", []) as Array).size()
	assert_eq(marks.size(), want, "one pencil circle per slice whose status the play changes")
	await _frames(2)
	scene.cancel_selection()
	assert_eq(scene.slice_marks().size(), 0, "the circles go with the aim")
	assert_eq(scene.play_plates().size(), 0, "and the plates")
	await _close(scene)


func test_hover_without_aim_shows_no_plate_and_pad_aiming_does() -> void:
	var scene := await _combat()
	scene._preview_card(0)
	assert_eq(scene.play_plates().size(), 0, "a hovered card (not aimed) keeps the chips only")
	var picked := -1
	for i in scene.engine.state().hand.size():
		if CardTargeting.options(scene.engine.resolver, scene.engine.state(), i).size() > 1:
			picked = i
			break
	assert_true(picked >= 0, "a card with several targets")
	Settings.pad_active = true
	scene.select_card(picked)
	assert_gt(scene.play_plates().size(), 0, "pad aiming shows the result on the wheel")
	scene.step_selection(1)
	assert_gt(scene.play_plates().size(), 0, "and keeps it as the aim steps")
	scene.cancel_selection()
	await _close(scene)


# --- The aim in grease pencil --------------------------------------------------------------------

func test_the_aim_arrow_ends_at_the_hub_edge_and_loops_the_target() -> void:
	var scene := await _combat()
	var eng: CombatEngine = scene.engine
	var st: CombatState = eng.state()
	st.hand[0] = &"jolt"
	scene._refresh(st)
	var options := CardTargeting.options(eng.resolver, st, 0)
	assert_gt(options.size(), 0)
	var action := _aim(scene, 0, 0)
	var spec: Dictionary = scene.aim_spec()
	assert_false(spec.is_empty(), "an aim to draw")
	var loop: Dictionary = spec["loop"]
	assert_false(loop.is_empty(), "on a target the loop goes round it")
	var shapes := AimLinePencil.shapes(spec)
	assert_false((shapes["arrow"] as Array).is_empty(), "an arrow")
	assert_eq((shapes["arrow"] as Array).size(), 3, "a shaft and its two head flicks (PencilShapes.arrow)")
	var shaft: PackedVector2Array = (shapes["arrow"] as Array)[0]
	var to: Vector2 = spec["to"]
	assert_almost_eq(shaft[shaft.size() - 1].distance_to(to), float(spec["stop"]), 1.0, "it stops that far short of its zone")
	var card: Rect2 = scene._card_node(0).get_global_rect()
	assert_almost_eq(shaft[0].distance_to(Vector2(card.get_center().x, card.position.y)), 0.0, 1.0, "from the card's top edge")
	assert_not_null(action)
	scene.cancel_selection()
	assert_true(scene.aim_spec().is_empty(), "no aim once it ends")
	await _close(scene)


func test_the_aim_writes_on_and_wipes_and_one_press_completes_it() -> void:
	var scene := await _combat()
	Motion.force_live = true
	var picked := -1
	for i in scene.engine.state().hand.size():
		if CardTargeting.options(scene.engine.resolver, scene.engine.state(), i).size() > 1:
			picked = i
			break
	scene.select_card(picked)
	await BoundedWait.frozen_frames(get_tree(), 1)
	assert_true(scene.aim_pencil.motion_running(), "the loop writes on (target_snap)")
	scene.aim_pencil.complete_motion()
	assert_false(scene.aim_pencil.motion_running(), "MotionSkip: written whole")
	scene.cancel_selection()
	await BoundedWait.frozen_frames(get_tree(), 1)
	assert_true(scene.aim_pencil.motion_running(), "it wipes off (pencil_wipe), never fades")
	scene.aim_pencil.complete_motion()
	await BoundedWait.frozen_frames(get_tree(), 1)
	assert_eq(scene.aim_pencil.shown(), [], "gone")
	Motion.force_live = false
	await _close(scene)


# --- The hovered card over the result chips (S-CARDFACE's defect) -------------------------------

func test_the_hovered_card_draws_over_the_result_chips() -> void:
	var scene := await _combat()
	scene._spread_hand(0)
	var card: ZineCard = scene._card_node(0)
	assert_gt(card.z_index, scene.hud_layer.z_index, "the hovered card over the chips' layer")
	for over in [scene.fx_layer, scene.toast, scene.inspect_popup]:
		assert_gt((over as CanvasItem).z_index, card.z_index, "%s stays above it" % (over as Node).name)
	scene._spread_hand(-1)
	assert_eq(card.z_index, 0, "back in the row")
	await _close(scene)


# --- TURN strip, name sticker, tutorial, end states ------------------------------------------------

func test_the_turn_strip_says_where_the_fight_is_and_fits() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		var line: String = scene.address_line()
		assert_string_contains(line, tr("TRAINING SIM").to_upper(), "a fight with no run")
		assert_string_contains(line, scene._name_of(scene.engine.state().enemies[0]).to_upper(), "names the enemy")
		assert_true(line.ends_with(scene._address.text), "x%.1f: the line, or its end when the strip is short" % scale)
		assert_string_contains(scene._address.text, scene._name_of(scene.engine.state().enemies[0]).to_upper(), "x%.1f: the enemy stays on it" % scale)
		var fs: int = scene._address.get_theme_font_size("font_size")
		var w := HudSkin.mono().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var min_fs := int((scene.get_script() as Script).get_script_constant_map()["ADDRESS_MIN_FONT"])
		assert_true(w <= scene._address.size.x + 1.0 or fs == min_fs, "x%.1f: the address fits its strip (%.0f in %.0f)" % [scale, w, scene._address.size.x])
		assert_false(scene._status.visible, "the key hints are the strip's tooltip, not a line")
		assert_string_contains(scene._banner.tooltip_text, Settings.key_text(&"toggle_nudge_wheel"))
		assert_true(SCREEN.encloses(scene._banner.get_global_rect()), "x%.1f: on screen" % scale)
		await _close(scene)


func test_the_name_sticker_reads_as_a_cell_designation() -> void:
	assert_eq(HudNameSticker.cell_name("Breaker 1", "Breaker", "CELL"), "CELL-1")
	assert_eq(HudNameSticker.cell_name("Ghost", "Breaker", "CELL"), "Ghost", "a name of its own stays")
	assert_eq(HudNameSticker.cell_name("Breaker Bob", "Breaker", "CELL"), "Breaker Bob")
	var s := HudNameSticker.new()
	s.set_names("Breaker 9", "Breaker", "CELL")
	assert_eq(s.words, "CELL-9 // BREAKER", "combat_typical_v4's CELL-9 // BREAKER (no class word twice)")
	s.free()


func test_the_tutorial_sits_between_the_wheels_clear_of_both() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		scene.start_tutorial()
		await _frames(3)
		var t: Rect2 = scene.tutorial.get_global_rect()
		for v in scene._views():
			assert_false(t.intersects((v as WheelView).wheel_rect()), "x%.1f: the tutorial clear of %s's wheel (%s vs %s)" % [scale, (v as WheelView).combatant.id, t, (v as WheelView).wheel_rect()])
		var left: Rect2 = scene._player_view.wheel_rect()
		var right: Rect2 = (scene._enemy_views.values()[0] as WheelView).wheel_rect()
		assert_true(t.get_center().x > left.get_center().x and t.get_center().x < right.get_center().x, "x%.1f: between the wheels" % scale)
		await _close(scene)


func test_the_beaten_enemy_wears_deleted_and_flatlined_sits_on_the_hub() -> void:
	var scene := await _combat()
	var ev: WheelView = scene._enemy_views.values()[0]
	var d: Dictionary = ev.deleted_sticker()
	assert_eq(String(d["word"]), tr("DELETED"), "round 23 fx_enemy_defeated_v2: DELETED")
	assert_true(ev.wheel_rect().encloses(Rect2(ev.global_position + (d["box"] as Rect2).position, (d["box"] as Rect2).size)), "in the wheel's spot")
	var pv: WheelView = scene._player_view
	var fb: Dictionary = pv.flatline_box()
	var hub := pv.hub_radius()
	assert_true((fb["box"] as Rect2).size.x <= hub * WheelView.FLATLINE_HUB_SHARE + 1.0, "FLATLINED fits the hub (round 40 player_defeat_v2)")
	await _close(scene)


# --- Fit at 1.0 / 1.6 / 2.0 -------------------------------------------------------------------------

func test_the_result_plate_fits_on_screen_at_every_text_scale() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		var picked := -1
		for i in scene.engine.state().hand.size():
			if CardTargeting.options(scene.engine.resolver, scene.engine.state(), i).size() > 1:
				picked = i
				break
		scene.select_card(picked)
		var plates: Dictionary = scene.play_plates()
		assert_gt(plates.size(), 0, "x%.1f: a plate" % scale)
		for v in plates:
			var r: Rect2 = (plates[v] as Control).get_global_rect()
			assert_true(SCREEN.encloses(r), "x%.1f: the plate on screen (%s)" % [scale, r])
			assert_true(r.has_point((v as WheelView).global_center()), "x%.1f: on its wheel's hub" % scale)
			assert_false(r.intersects(scene._hand_box.get_global_rect()), "x%.1f: never on the hand" % scale)
		scene.cancel_selection()
		await _close(scene)


func test_preview_labels_keep_off_the_send_it_block_and_the_aim_hint() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		var ev: WheelView = scene._enemy_views.values()[0]
		var overlay := ev.find_child("CardPreview", true, false) as CardPreviewOverlay
		if overlay == null:
			overlay = scene.find_child("CardPreview", true, false) as CardPreviewOverlay
		assert_not_null(overlay, "the card preview overlay")
		var blockers: Array[Rect2] = overlay.label_blockers()
		for c in [scene._end_turn_button, scene._sticker_box]:
			var r: Rect2 = (c as Control).get_global_rect()
			var local := Rect2(r.position - overlay.global_position, r.size).grow(CardPreviewOverlay.BLOCK_PAD)
			assert_true(blockers.has(local), "x%.1f: %s blocks the preview's labels" % [scale, (c as Node).name])
		# a label aimed straight at the SEND IT block turns round the wheel off it
		var send: Rect2 = scene._end_turn_button.get_global_rect()
		var hub: Vector2 = ev.global_center() - overlay.global_position
		var at: Vector2 = send.get_center() - overlay.global_position
		var dists: Array[float] = [hub.distance_to(at)]
		var box: Rect2 = overlay.label_box(hub, (at - hub).angle(), dists, tr("DRONE ENDS HERE"))
		assert_false(Rect2(box.position + overlay.global_position, box.size).intersects(send), "x%.1f: DRONE ENDS HERE never sits on SEND IT / EXECUTE" % scale)
		await _close(scene)
