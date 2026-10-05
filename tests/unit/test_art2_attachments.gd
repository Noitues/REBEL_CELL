extends GutTest
## ART-2 2B (ART_BIBLE v2 §3.9, §3.11, §3.13, §3.14, §3.17, §3.21; DECISIONS D17): the wheel
## attachments (firmware sockets, drones and satellites with the collapsed band and the bloom, the
## animated card-play preview, the Daemon rack) and the combat backdrop. The preview shows the
## result (it reads the forecast's ghost); motion never waits headless; views never change state.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
const SPIN_CARDS: Array[StringName] = [&"heavy_spin", &"brute_spin", &"backspin", &"flick"]

var _text_scale_before: float = 1.0
var _reduce_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_reduce_before = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_art2_2b"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	if Settings.reduce_effects != _reduce_before:
		Settings.set_reduce_effects(_reduce_before)
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


func _combat(enemy: StringName = &"collections_agent", scale: float = 1.0, seed_value: int = 5) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, seed_value)
	await _frames()
	return scene


## Docks a drone of `template` on `owner`'s slot `slot` (a fixture: the lab and these tests only).
func _dock(st: CombatState, owner: CombatantState, lookup: ContentLookup, template: StringName, slot: int) -> CombatantState:
	var d := EffectInterpreter.make_combatant(lookup.get_content(template) as EnemyData, StringName("%s_t%d" % [owner.id, slot]), true)
	d.is_player = owner.is_player
	d.host_id = owner.id
	d.dock_slot = slot
	if owner.is_player:
		st.drones.append(d)
	else:
		st.enemies.append(d)
	return d


# --- The backdrop (§3.14, D17) ---------------------------------------------------------------------

func test_every_corporation_has_a_boss_and_a_site_backdrop_day_and_night() -> void:
	for corp in CORPS:
		for boss in [true, false]:
			for day in [true, false]:
				var p := BackdropCatalog.place(corp, boss, day)
				var path := BackdropCatalog.still_path(p)
				assert_ne(path, "", "%s has a still" % BackdropCatalog.stem(p))
				assert_true(path.contains(String(corp)), "%s shows its own corporation (%s)" % [BackdropCatalog.stem(p), path])
				assert_true(path.contains("_hq_" if boss else "_site_"), "%s: a boss fight at the HQ, a regular one at the Site" % path)
				if corp != &"rebel_cell":
					assert_true(path.ends_with(("_day" if day else "_night") + ".jpg"), "%s: day is the cool day, night the reference" % path)
					assert_ne(BackdropCatalog.won_mask_path(p), "", "%s has its won lights mask" % path)
	# The REBEL_CELL canyon is a night street; its won look is the Cell's own street.
	var rebel := BackdropCatalog.place(&"rebel_cell", true, true)
	assert_false(bool(rebel["day"]), "the canyon has no day")
	assert_ne(BackdropCatalog.won_still_path(rebel), "", "DISPATCH's canyon gives way to HOME once won")


func test_the_place_follows_the_fight_and_the_run() -> void:
	var camp := CampaignState.new()
	camp.corporation_id = &"halcyon"
	var boss := EnemyData.new()
	boss.is_boss = true
	var grunt := EnemyData.new()
	grunt.corporation_id = &"orbital"
	var foes: Array[EnemyData] = [grunt, boss]
	var p := BackdropCatalog.place_for(camp, foes)
	assert_eq(p["corp"], &"halcyon", "the campaign's corporation")
	assert_eq(p["kind"], BackdropCatalog.KIND_HQ, "a boss among the foes: its HQ")
	var only: Array[EnemyData] = [grunt]
	assert_eq(BackdropCatalog.place_for(null, only)["corp"], &"orbital", "no campaign: the enemy's corporation")
	assert_eq(BackdropCatalog.place_for(camp, only)["kind"], BackdropCatalog.KIND_SITE, "a regular fight: the Site")
	camp.runs_started = 0
	var night := bool(BackdropCatalog.place_for(camp, only)["day"])
	camp.runs_started = 1
	assert_ne(bool(BackdropCatalog.place_for(camp, only)["day"]), night, "runs alternate night and day")


func test_the_combat_scene_stands_in_front_of_the_target_and_lights_it_when_won() -> void:
	var scene := await _combat(&"the_manifest")
	var bd: CombatBackdrop = scene.arena_backdrop
	assert_not_null(bd, "the combat scene has the backdrop")
	assert_eq(bd.place.get("kind"), BackdropCatalog.KIND_HQ, "The Manifest is a boss: its HQ")
	assert_eq(bd.won, 0.0, "a fight going on is not won")
	assert_false(scene.background.visible, "the net city under it is hidden")
	bd.play_won()
	assert_eq(bd.won, 1.0, "headless never waits: the won look lands at once")
	assert_false(bd.motion_running(), "nothing left running")
	scene.start_fight(&"collections_agent", 3)
	await _frames()
	assert_eq(bd.place.get("kind"), BackdropCatalog.KIND_SITE, "a new regular fight: the Site")
	assert_eq(bd.won, 0.0, "a new fight starts un-won")


func test_a_won_fight_lights_the_backdrop_with_victory() -> void:
	var scene := await _combat(&"collections_agent")
	var st: CombatState = scene.engine.state()
	for e in st.enemies:
		e.hp = 0
	st.outcome = CombatState.Outcome.VICTORY
	scene._refresh(st)  # a fight shown won (as on loading one): VICTORY stands at once
	var bd: CombatBackdrop = scene.arena_backdrop
	var done := await BoundedWait.until(get_tree(), func() -> bool: return bd.won >= 1.0, 10.0)
	assert_true(done, "VICTORY lights the target's windows in Cell colours")


func test_the_won_look_under_reduce_effects_is_its_end_state_and_one_press_completes_it() -> void:
	var bd := CombatBackdrop.new()
	add_child_autofree(bd)
	bd.show_place(BackdropCatalog.place(&"solace", true, false))
	Settings.set_reduce_effects(true)
	bd.play_won()
	assert_eq(bd.won, 1.0, "reduce effects: the end state at once")
	Settings.set_reduce_effects(false)
	bd.show_place(BackdropCatalog.place(&"orbital", false, false))
	Motion.force_live = true
	bd.play_won()
	var was_running := bd.motion_running()
	bd.complete_motion()
	Motion.force_live = false
	assert_true(was_running, "animated when live")
	assert_eq(bd.won, 1.0, "a press lands it")
	assert_true(bd.is_in_group(MotionSkip.GROUP), "it joins the one-press skip")


func test_wheel_pools_follow_the_wheels() -> void:
	var scene := await _combat(&"the_manifest")
	await _frames(2)
	var bd: CombatBackdrop = scene.arena_backdrop
	var mat: ShaderMaterial = bd.get_node("Still").material
	var a: Vector3 = mat.get_shader_parameter(&"pool_a")
	var b: Vector3 = mat.get_shader_parameter(&"pool_b")
	assert_gt(a.z, 0.0, "the operative's wheel has a pool")
	assert_gt(b.z, 0.0, "the enemy's wheel has a pool")
	assert_lt(a.x, b.x, "the operative's pool on the left, the boss's on the right")


# --- Attachments ------------------------------------------------------------------------------------

func test_every_wheel_carries_its_attachments_and_leaves_their_drawing_to_them() -> void:
	var scene := await _combat(&"collections_agent")
	for v in scene._views():
		var a: WheelAttachments = v.attachments
		assert_not_null(a, "the wheel has its attachments")
		assert_eq(a.get_parent(), v, "docked on the wheel")
		assert_not_null(a.sockets)
		assert_not_null(a.dock)
		assert_not_null(a.preview)


func test_drones_collapse_dock_on_their_slice_and_are_aimed_at_their_spot() -> void:
	for scale in [1.0, 1.6, 2.0]:
		var scene := await _combat(&"collections_agent", scale)
		var st: CombatState = scene.engine.state()
		var lookup: ContentLookup = scene.engine.resolver.lookup
		for i in st.player.wheel.slice_count:
			_dock(st, st.player, lookup, &"botnet_drone", i)
		scene._refresh(st)
		await _frames(2)
		var v: WheelView = scene._player_view
		var a: WheelAttachments = v.attachments
		for e in a.dock.entries():
			var sat: CombatantState = e["sat"]
			var mid := float(e["mid"])
			var tile: Vector2 = e["tile"]
			var off := tile - a.center()
			assert_gt(off.length(), a.rim(), "a band stands outside the rim (scale %.1f)" % scale)
			assert_lt(absf(wrapf(off.angle() - mid, -PI, PI)), TAU / st.player.wheel.slice_count * 0.5, "on its own slice")
			assert_eq(String(v.zone_at(v._satellite_pos(sat)).get("kind", "")), "satellite", "its spot aims at it (scale %.1f)" % scale)
			assert_eq(v.zone_at(v._satellite_pos(sat)).get("id"), sat.id, "at that drone")


func test_aiming_at_a_drone_blooms_its_band_into_a_mini_wheel_inside_the_screen() -> void:
	for scale in [1.0, 1.6, 2.0]:
		var scene := await _combat(&"collections_agent", scale)
		var st: CombatState = scene.engine.state()
		var lookup: ContentLookup = scene.engine.resolver.lookup
		for i in st.player.wheel.slice_count:
			_dock(st, st.player, lookup, &"botnet_drone", i)
		scene._refresh(st)
		var v: WheelView = scene._player_view
		var dock: DroneDock = v.attachments.dock
		for e in dock.entries():
			v.valid_zones.append({"kind": "satellite", "id": (e["sat"] as CombatantState).id})
		await _frames(2)
		var vr := Rect2(Vector2.ZERO, v.size)
		for e in dock.entries():
			assert_eq(float(dock.bloom.get(int(e["slot"]), 0.0)), 1.0, "aimed: bloomed (headless: at once)")
			var sat: CombatantState = e["sat"]
			assert_true((v._satellite_pos(sat) - v.global_position).is_equal_approx(e["mini"]), "it is aimed at its mini-wheel")
			var r := float(e["mini_r"])
			var m: Vector2 = e["mini"]
			assert_true(vr.grow(1.0).encloses(Rect2(m - Vector2(r, r), Vector2(r, r) * 2.0)), "bloomed mini-wheels stay on screen (scale %.1f)" % scale)
		v.valid_zones.clear()
		await _frames(2)
		for e in dock.entries():
			assert_eq(float(dock.bloom.get(int(e["slot"]), 0.0)), 0.0, "not aimed, not hovered: collapsed again")


func test_a_satellite_never_moves_the_fight() -> void:
	var scene := await _combat(&"the_manifest")
	var st: CombatState = scene.engine.state()
	var lookup: ContentLookup = scene.engine.resolver.lookup
	_dock(st, st.player, lookup, &"botnet_drone", 0)
	scene._refresh(st)
	var before := st.state_hash()
	for v in scene._views():
		v.attachments.dock.force_bloom = true
		v.attachments.preview.queue_redraw()
	await _frames(3)
	assert_eq(st.state_hash(), before, "views never change state")


func test_firmware_sockets_sit_in_the_hub_side_band_pins_to_the_core() -> void:
	var scene := await _combat(&"collections_agent")
	var st: CombatState = scene.engine.state()
	st.player.wheel.slot_firmware_ids[0] = &"leech"
	st.player.wheel.slot_firmware_ids[3] = &"overvolt"
	scene._refresh(st)
	await _frames(2)
	var a: WheelAttachments = scene._player_view.attachments
	var u := a.unit()
	for slot in st.player.wheel.slice_count:
		var s := a.sockets.socket(slot)
		if st.player.wheel.slot_firmware_ids[slot] == &"":
			assert_true(s.is_empty(), "no firmware, no socket")
			continue
		var d := (Vector2(s["at"]) - a.center()).length() / u
		assert_between(d, 142.0, 194.0, "inside the firmware zone (master 142..194)")
		var off := Vector2(s["at"]) - a.center()
		assert_lt(absf(wrapf(off.angle() - a.slot_angle(slot, scene._player_view.shown_rotation()), -PI, PI)), 0.01, "on the slice midline")


func test_the_daemon_rack_stands_beside_the_operative_and_folds_past_six() -> void:
	var scene := await _combat(&"collections_agent")
	var st: CombatState = scene.engine.state()
	st.daemon_ids.clear()
	for id in [&"clean_signal", &"cascade", &"botnet_seed", &"twin_pointer", &"zero_day", &"kernel_sync", &"scrubber"]:
		st.daemon_ids.append(id)
	scene._refresh(st)
	await _frames(2)
	var rack: DaemonRack = scene._player_view.get_node("DaemonRack")
	assert_true(rack.visible, "the rack shows with Daemons installed")
	var pv: WheelView = scene._player_view
	assert_lt(rack.get_global_rect().end.x, pv.global_center().x, "on the left, beside the wheel")
	assert_eq(rack.plate_rect(7).size, rack.plate_rect(6).size, "past six the last tile says +N")
	assert_true(rack._get_tooltip(rack.tile_rect(0).get_center()) != "", "a tile says what its Daemon does")


# --- The card-play preview (§3.17): it is the result ------------------------------------------------

func test_the_card_play_preview_lands_where_the_card_lands() -> void:
	var checked := 0
	for enemy in [&"collections_agent", &"the_manifest", &"civic_core"]:
		for card in SPIN_CARDS:
			var scene := await _combat(enemy, 1.0, 11)
			var st: CombatState = scene.engine.state()
			st.hand[0] = card
			st.ram = maxi(st.ram, 6)
			var options := CardTargeting.options(scene.engine.resolver, st, 0)
			if options.is_empty():
				continue
			var action: CombatAction = options[options.size() - 1]
			scene._preview_action(action)
			var predicted := {}
			for v in scene._views():
				var ov: CardPreviewOverlay = v.attachments.preview
				ov._process(0.0)
				if not ov.ghost.is_empty():
					predicted[v.combatant.id] = ov.landing_slots()
			if predicted.is_empty():
				continue
			assert_true(scene.engine.submit(action), "%s plays" % card)
			var after: CombatState = scene.engine.state()
			for id in predicted:
				var c := after.get_combatant(id)
				var real: Array[int] = []
				for p in c.wheel.pointer_ticks:
					real.append(WheelMath.slice_at(WheelMath.tick_at(c.wheel.rotation, p), c.wheel.slice_count))
				assert_eq(predicted[id], real, "%s on %s: the ghost blades stand where the needles land" % [card, enemy])
				checked += 1
	assert_gt(checked, 0, "some spin previews were checked")


func test_the_preview_holds_at_half_while_aimed_and_goes_when_the_hover_ends() -> void:
	var scene := await _combat(&"collections_agent")
	var v: WheelView = scene._player_view
	var ov: CardPreviewOverlay = v.attachments.preview
	var rot: int = v.combatant.wheel.rotation
	v.set_ghost(posmod(rot + 4, RC.TICKS))
	ov._process(0.016)
	assert_eq(ov.shown_amount, 1.0, "headless: in at once")
	assert_eq(ov.delta_ticks(), 4, "the turn it shows")
	assert_eq(ov.chase, 1.0, "headless: every chevron lit, nothing to wait for")
	v.set_ghost(null)
	ov._process(0.016)
	ov._process(0.016)
	assert_true(ov.ghost.is_empty(), "the hover ends: the ghost goes")


func test_new_motion_ids_are_in_the_table() -> void:
	for id in [CombatBackdrop.WON_MOTION, DroneDock.BLOOM_MOTION, CardPreviewOverlay.CHASE_MOTION, CardPreviewOverlay.GHOST_MOTION, DaemonRack.SCAN_MOTION]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in ui_motion.tres" % id)
