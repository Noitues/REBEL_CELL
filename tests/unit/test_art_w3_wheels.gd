extends GutTest
## Art pass W3 (ART_BIBLE §6.1, §6.2, §3.5, §7.1, §8, §10, §11 Combat, §12): wheel hardware
## and combat presentation. Presentation only: every assert reads the views, never a rule.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_art_w3"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(false)
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


func _combat(enemy: StringName = &"compliance_officer", scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, 5)
	await _frames()
	return scene


func _enemy_view(scene: Control) -> WheelView:
	return scene._enemy_views.values()[0]


# --- 1. Bezel ownership (§6.1) -----------------------------------------------------------------

func test_the_bezel_says_who_owns_the_wheel() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	var ev := _enemy_view(scene)
	assert_eq(WheelBezel.owner_of(pv.look), WheelBezel.Owner.OPERATIVE, "the operative's bezel")
	assert_eq(pv.look["rim"], Palette.CELL_PINK, "a CELL_PINK rim")
	assert_eq(WheelBezel.owner_of(ev.look), WheelBezel.Owner.ENEMY, "an enemy's bezel")
	var corp := ev._corporation_of(ev.combatant)
	assert_eq(ev.look["rim"], Palette.corp_color(corp), "machined in its corp hue")
	assert_eq(int(ev.look["pattern"]), Palette.corp_pattern_id(corp), "with its corp pattern")
	assert_ne(int(ev.look["pattern"]), CorpPattern.Kind.NONE, "the enemy has a pattern")


func test_owners_differ_in_shape_not_only_colour() -> void:
	var c := Vector2(200, 200)
	assert_eq(WheelBezel.sticker_polys(c, 100.0, 126.0).size(), WheelBezel.STICKERS, "paper stickers on the operative's bezel")
	assert_eq(WheelBezel.notch_cuts(c, 126.0).size(), WheelBezel.NOTCHES, "notches cut into the enemy's rim")
	var outline := WheelBezel.notch_outline(c, 126.0)
	var near := INF
	for p in outline:
		near = minf(near, p.distance_to(c))
	assert_almost_eq(near, 126.0 - WheelBezel.NOTCH_DEPTH, 0.01, "the teeth are NOTCH_DEPTH deep")
	# Greyscale: the stickers are light paper on dark metal.
	assert_gt(Palette.luminance(Palette.PAPER) - Palette.luminance(Palette.NIGHT_BLOCK), 0.5, "stickers read in greyscale")


func test_the_portraits_have_their_places() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	var ev := _enemy_view(scene)
	var inset := pv.inset_rect()
	assert_true(inset.has_area(), "the operative's Polaroid inset")
	var c := pv._center()
	for p in [inset.position, inset.end, Vector2(inset.end.x, inset.position.y), Vector2(inset.position.x, inset.end.y)]:
		assert_lt((p as Vector2).distance_to(c), pv.hub_radius(), "inside the hub")
	assert_lt(inset.get_center().y, c.y, "at the hub's top")
	assert_false(ev.inset_rect().has_area(), "an enemy has no inset")
	var badge := ev.badge_rect()
	assert_true(badge.has_area(), "the enemy's portrait above its bezel")
	assert_lt(badge.end.y, ev._center().y - ev.needle_reach(), "above every needle's reach")
	assert_false(badge.intersects(ev._intent_rect_local()), "never under the tag")
	assert_false(pv.badge_rect().has_area(), "the operative has no badge")
	var ext := pv.hub_text_extent()
	assert_gt(pv._center().y + ext.x, inset.end.y, "the name sits under the inset")


func test_focus_brackets_only_mark_the_target() -> void:
	var scene := await _combat()
	assert_false(scene._player_view.highlighted, "the operative's own wheel is never bracketed")
	var targeted := 0
	for v in scene._enemy_views.values():
		if (v as WheelView).highlighted:
			targeted += 1
			assert_eq((v as WheelView).combatant.id, scene.engine.state().target_id, "the bracketed wheel is the target")
	assert_eq(targeted, 1, "one target")


# --- 2. Class identity (§6.1, §7.1) -------------------------------------------------------------

const CLASSES: Array[StringName] = [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]


func test_every_class_has_its_own_ornament_pattern_and_glyph() -> void:
	assert_eq(Palette.CLASS_ACCENTS.keys().size(), CLASSES.size(), "the eight §7.1 classes")
	for key in ["ornament", "hub_pattern", "hub_glyph"]:
		var seen := {}
		for c in CLASSES:
			var look := WheelBezel.operative_look(c)
			assert_ne(look[key], WheelBezel.PLAIN, "%s has a %s" % [c, key])
			assert_false(seen.has(look[key]), "%s: no two classes share a %s" % [c, key])
			seen[look[key]] = c
	for c in CLASSES:
		assert_eq(WheelBezel.operative_look(c)["accent"], Palette.class_accent(c), "%s's accent" % c)


func test_class_bezels_differ_pairwise_in_shape() -> void:
	var at := Vector2(200, 200)
	var keys := {}
	for c in CLASSES:
		var look := WheelBezel.operative_look(c)
		var k := "%s|%s|%s" % [WheelBezel.marks_key(WheelBezel.ornament_marks(look, at, 100.0, 126.0)),
			WheelBezel.marks_key(WheelBezel.hub_marks(look, at, 60.0)), WheelBezel.marks_key(WheelBezel.glyph_marks(look["hub_glyph"], at, 10.0))]
		assert_false((WheelBezel.ornament_marks(look, at, 100.0, 126.0).lines as Array).is_empty() and (WheelBezel.ornament_marks(look, at, 100.0, 126.0).dots as Array).is_empty()
			and (WheelBezel.ornament_marks(look, at, 100.0, 126.0).polys as Array).is_empty(), "%s draws an ornament" % c)
		for other in keys:
			assert_ne(k, keys[other], "%s and %s never share a bezel" % [c, other])
		keys[c] = k
	# Pairwise per part too: the critique's pairs (Botnet/Hivemind, Rigger/Overclocker) apart.
	for part in ["ornament", "hub"]:
		var seen := {}
		for c in CLASSES:
			var look := WheelBezel.operative_look(c)
			var m := WheelBezel.ornament_marks(look, at, 100.0, 126.0) if part == "ornament" else WheelBezel.hub_marks(look, at, 60.0)
			var key := WheelBezel.marks_key(m)
			assert_false(seen.has(key), "%s %s is unique" % [c, part])
			seen[key] = true


func test_the_ghost_flicker_is_ambient_and_rests_under_reduce_effects() -> void:
	var look := WheelBezel.operative_look(&"ghost")
	assert_true(WheelBezel.is_ambient(look), "the Ghost's rim flickers (T0)")
	assert_eq(VfxTier.of(&"bezel_ambient"), VfxTier.T0, "a T0 loop")
	assert_gte(Motion.seconds(&"bezel_ambient"), VfxTier.T0_MIN_PERIOD, "slow: at least the T0 period")
	assert_eq(float(WheelBezel.ornament_marks(look, Vector2.ZERO, 100.0, 126.0, 0.0).alpha), 1.0, "at rest the rim is whole")
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	var v := WheelView.new()
	v.look = look
	assert_false(v.ambient_on(), "static under reduce effects")
	v.free()
	Settings.reduce_effects = was
	assert_false(WheelBezel.is_ambient(WheelBezel.operative_look(&"breaker")), "rivets don't move")


# --- 3. The HP arc (§6.1, §3.5) -------------------------------------------------------------------

func test_hp_colour_follows_the_fraction() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	var mx := float(pv.combatant.max_hp)
	for pair in [[1.0, Palette.GAIN], [0.5, Palette.GAIN], [0.49, Palette.WARN], [0.25, Palette.WARN], [0.2, Palette.HARM], [1.0 / mx, Palette.HARM]]:
		pv.anim_hp = roundf(float(pair[0]) * mx) if float(pair[0]) * mx >= 1.0 else 1.0
		assert_eq(pv.hp_color_now(), Palette.hp_color(pv.anim_hp / mx), "HP %d/%d" % [pv.anim_hp, mx])
	pv.anim_hp = 1.0
	assert_eq(pv.hp_color_now(), Palette.HARM, "1/60 is red, never green")
	pv.anim_hp = NAN
	assert_ne(WheelView.HP_COLOR, Color("#3DFF8B"), "the hard-coded green is gone")


func test_the_arc_is_thick_and_shows_the_forecast_loss_as_a_ghost() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	assert_gte(WheelView.HP_ARC_OUT - WheelView.HP_ARC_IN, 10.0, "at least 10 px")
	var hp := pv.combatant.hp
	pv.outcome = {"hp_after": hp - pv.combatant.max_hp / 4, "alive_after": true, "statuses": [], "satellites": {}}
	var ghosts := 0
	var full := 0
	for s in pv.hp_segments():
		ghosts += 1 if s["state"] == "ghost" else 0
		full += 1 if s["state"] == "full" else 0
	assert_gt(ghosts, 0, "a hatched ghost for the forecast loss")
	assert_gt(full, 0, "the HP that stays")
	pv.outcome = {}
	for s in pv.hp_segments():
		assert_ne(s["state"], "ghost", "no forecast, no ghost")


func test_the_drain_is_two_stage() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	pv.anim_hp = 20.0
	pv.lag_hp = 40.0
	var lag := 0
	for s in pv.hp_segments():
		lag += 1 if s["state"] == "lag" else 0
	assert_gt(lag, 0, "the white lag trails the fill")


func test_hp_is_never_under_a_needle_sweep() -> void:
	var scene := await _combat()
	for v in scene._views():
		var wv := v as WheelView
		var st := wv.combatant.duplicate_state()
		st.wheel.pointer_ticks = PackedInt32Array([0, 8, 15, 22])
		wv.shown_state = st
		var hp: Rect2 = wv.hp_layout()["hp"]
		for p in wv.shown_pointers():
			var a := WheelView._ang(p)
			var hub := wv._center() + Vector2(cos(a), sin(a)) * (wv._radius() + wv._band() * WheelView.NEEDLE_HUB_OUT)
			var reach := WheelView.NEEDLE_HUB_R * maxf(1.0, Motion.amplitude(&"resolve_pulse"))
			var nearest := Vector2(clampf(hub.x, hp.position.x, hp.end.x), clampf(hub.y, hp.position.y, hp.end.y))
			assert_gt(nearest.distance_to(hub), reach, "%s: the HP number is off the needle at tick %d" % [wv.combatant.display_name, p])
		wv.shown_state = null


func test_the_heartbeat_beats_under_a_quarter_and_rests_under_reduce_effects() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	assert_eq(VfxTier.of(&"hp_heartbeat"), VfxTier.T1, "T1")
	Motion.force_live = true
	pv.anim_hp = 1.0
	assert_true(pv.heartbeat_on(), "under 25% it beats")
	pv.heart_t = Motion.seconds(&"hp_heartbeat") * 0.5
	assert_gt(pv.heartbeat_swell(), 0.0, "the arc swells mid-beat")
	pv.anim_hp = float(pv.combatant.max_hp)
	assert_false(pv.heartbeat_on(), "healthy: no beat")
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	pv.anim_hp = 1.0
	assert_false(pv.heartbeat_on(), "static under reduce effects")
	Settings.reduce_effects = was
	Motion.force_live = false
	pv.anim_hp = NAN


func test_a_beaten_wheel_dims_to_thirty_percent() -> void:
	assert_almost_eq(WheelView.DEFEATED_DIM, 0.3, 0.001, "30%")
	assert_almost_eq(WheelView.FLATLINE_VEIL, 0.7, 0.001, "the operative's disc under DEFEAT")


# --- 4. Boss wheels (§6.1, §7.2) -------------------------------------------------------------------

const BOSS := &"civic_core"


func test_a_boss_wheel_is_a_fifth_bigger() -> void:
	var scene := await _combat()
	var lookup: ContentLookup = scene.engine.resolver.lookup
	var normal := WheelView.new()
	var boss := WheelView.new()
	var holder: Control = add_child_autofree(Control.new())
	for v in [normal, boss]:
		holder.add_child(v)
		(v as WheelView).size = Vector2(700, 900)
	var s: CombatState = scene.engine.state()
	normal.show_combatant(s.enemies[0], [] as Array[CombatantState], [] as Array[Dictionary], lookup)
	var bc := s.enemies[0].duplicate_state()
	bc.source_id = BOSS
	bc.display_name = "Civic Core"
	boss.show_combatant(bc, [] as Array[CombatantState], [] as Array[Dictionary], lookup)
	assert_true(boss.is_boss(), "the boss is a boss")
	assert_false(normal.is_boss(), "the agent is not")
	assert_eq(WheelView.BOSS_SCALE, 1.2, "120%")
	assert_almost_eq(boss._radius() / normal._radius(), 1.2, 0.001, "120% of a normal wheel in the same room")
	assert_not_null(boss.backdrop, "a hologram stands behind the boss (W5 seam)")
	assert_true(boss.backdrop.show_behind_parent, "behind the wheel")
	assert_null(normal.backdrop, "no hologram behind a normal wheel")
	var plate := boss.nameplate()
	assert_false(plate.is_empty(), "a taped nameplate")
	assert_false((plate["rect"] as Rect2).intersects(boss._intent_rect_local()), "clear of the tag")
	assert_gte(int(plate["fs"]), UiTheme.CAPTION, "its name at caption or larger")
	assert_true(normal.nameplate().is_empty(), "no nameplate on a normal wheel")
	var data := lookup.get_content(BOSS) as EnemyData
	assert_eq(boss.phase_pips().size(), data.phases.size(), "a pip per phase on the HP arc")


func test_the_boss_intro_is_t4_skippable_and_quiet_headless() -> void:
	assert_eq(VfxTier.of(&"boss_intro"), VfxTier.T4, "T4")
	assert_lte(Motion.seconds(&"boss_intro"), VfxTier.MAX_SECONDS[VfxTier.T4], "within T4's 2.5 s")
	var intro: BossIntro = add_child_autofree(BossIntro.new())
	assert_false(intro.play("CIVIC CORE", Palette.CORP_HALCYON), "headless: nothing plays")
	assert_false(intro.playing())
	Motion.force_live = true
	assert_true(intro.play("CIVIC CORE", Palette.CORP_HALCYON), "it plays with motion")
	assert_true(intro.playing())
	intro._step(0.5)
	assert_gte(intro.font_size(), UiTheme.CAPTION, "its name is display, shrunk only to fit")
	intro.skip()
	assert_false(intro.playing(), "a press ends it")
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	assert_true(intro.play("CIVIC CORE", Palette.CORP_HALCYON), "under reduce effects: a cross-fade")
	intro._step(0.5)
	assert_eq(intro.slam, 1.0, "no slam under reduce effects")
	intro.skip()
	Settings.reduce_effects = was
	Motion.force_live = false


func test_a_phase_needle_draws_on_and_the_stamp_holds_to_read() -> void:
	var scene := await _combat()
	var ev := _enemy_view(scene)
	Motion.force_live = true
	ev.play_phase_needles([0, 15])
	assert_true(ev.needle_grow.has(1), "the new needle draws on")
	assert_almost_eq(float(ev.needle_grow[1]), 0.0, 0.001, "from its hub")
	ev.stop_motion()
	assert_true(ev.needle_grow.is_empty(), "a skip shows it whole")
	Motion.force_live = false
	assert_gte(ZineStamp.hold_seconds(tr("PHASE %d") % 2), Motion.seconds(&"stamp_hold"), "the PHASE stamp holds per the stamp rule")
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	assert_true(src.contains("ZineStamp.hold_seconds(word)"), "the phase stamp's hold is the stamp rule's")
