extends GutTest
## ART-2 2A, the wheel stack (DECISIONS "Art direction — ART-2 2A wheel stack"; ART_BIBLE v2 3.2-3.10,
## 3.16, 3.19): the kit each wheel wears (2A.6), a glyph for everything the stack draws (2A.2-2A.5),
## the lifted slice and the rail read the slice that resolves (preview == result, GDD 2.10), the
## disc layer gets what the view shows (2A.1-2A.5), precision landings and the hub states keep the
## motion rules (one press ends them, reduce effects = the end state, headless never waits; 2A.7,
## 2A.4), and the stack fits its view at text scale 1.0 / 1.6 / 2.0.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const BOSSES := {&"meridian": &"the_manifest", &"solace": &"renewal_engine", &"halcyon": &"civic_core",
	&"orbital": &"commons_array", &"rebel_cell": &"dispatch_core"}

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art2_wheel"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.use_config(null)
	Motion.force_live = false
	Settings.restore(_settings)
	Fx.apply_settings()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(scale: float = 1.0, enemy: StringName = &"the_manifest", combat_seed: int = 5) -> Control:
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


func _engine(enemy: StringName) -> CombatEngine:
	var eng: CombatEngine = add_child_autofree(CombatEngine.new())
	var foes: Array[StringName] = [enemy]
	eng.start_fight(&"breaker", foes, 3, &"rank:1")
	return eng


func _lookup() -> ContentLookup:
	return ContentLookup.new().add_registry(ContentRegistry)


# --- 2A.6 kits ------------------------------------------------------------------------------

func test_every_corp_has_its_kit_and_rank_picks_the_tier() -> void:
	var lookup := _lookup()
	for corp: StringName in BOSSES:
		var eng := _engine(BOSSES[corp])
		var boss := WheelKit.of(eng.state().enemies[0], lookup)
		assert_eq(boss.kit_name(), corp, "%s's boss wears its corp's kit" % corp)
		assert_eq(boss.tier, 3, "a boss is tier III (3.7)")
		assert_true(boss.is_boss)
		assert_not_null(boss.screens, "%s has its screens" % corp)
		assert_not_null(boss.scenes, "%s has its upright corp scenes" % corp)
		assert_true(WheelGlyphs.has(boss.crest), "%s's crest has a glyph" % corp)
		assert_eq(boss.accent, Palette.corp_color(corp), "the frame accent is the corp hue (2.4)")
	var player := WheelKit.of(_engine(&"the_manifest").state().player, lookup, &"breaker")
	assert_eq(player.kit_name(), &"player")
	assert_eq(player.tier, 1)
	assert_eq(player.accent, Palette.class_accent(&"breaker"), "the player's frame wears the class accent (2.5)")
	assert_null(player.scenes, "the Cell runs its own programs, no corp scene")
	var elite := WheelKit.of(_engine(&"port_authority").state().enemies[0], lookup)
	assert_eq(elite.tier, 2, "an elite is tier II (3.7)")


# --- glyphs ------------------------------------------------------------------------------------

func test_everything_the_stack_draws_has_a_glyph() -> void:
	for type in RC.SliceType.values():
		var s := SliceData.new()
		s.id = &"x"
		s.slice_type = type
		assert_true(WheelGlyphs.has(WheelGlyphs.slice_id(s)), "slice type %s" % RC.SliceType.keys()[type])
	for st in RC.Status.values():
		if st != RC.Status.NONE:
			assert_true(WheelGlyphs.has(WheelGlyphs.status_id(st)), "status %s" % RC.Status.keys()[st])
	var lookup := _lookup()
	for id in ContentRegistry.all_ids():
		var data: Resource = ContentRegistry.get_content(id)
		if data is HubCoreData:
			var c := CombatantState.new()
			c.wheel = WheelState.new()
			c.wheel.hub_id = id
			assert_true(WheelGlyphs.has(WheelKit.new().hub_glyph(c)), "hub %s has its emblem (3.3)" % id)
		elif data is RingSegmentData:
			assert_true(WheelGlyphs.has(WheelGlyphs.segment_id(id)), "segment %s has its plate glyph (3.10)" % id)
	assert_not_null(lookup)


# --- preview == result ---------------------------------------------------------------------------

func test_the_lifted_slice_and_the_rail_read_the_slice_that_resolves() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var st: CombatState = scene.engine.state()
	for r in RC.TICKS:
		st.player.wheel.rotation = r
		scene._refresh(st)
		var ro: Dictionary = scene.engine.readouts(st.player)[0]
		assert_eq(v.active_slot(), int(ro["slice_index"]), "rotation %d: the lifted slice is the one the needle resolves" % r)
		var slice: SliceData = ro["slice"]
		var rail := v.rail_text(0, slice)
		if slice.slice_type != RC.SliceType.NULL:
			assert_string_contains(rail, str(slice.base_output), "the rail reads its value")
	scene.skip_motion()


func test_the_disc_gets_what_the_view_shows() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var st: CombatState = scene.engine.state()
	st.player.wheel.slice_statuses[1] = RC.Status.CORRUPTED
	scene._refresh(st)
	v._sync_disc(v._center(), v._radius(), v.shown_rotation())
	var mids: PackedFloat32Array = v.disc.mat.get_shader_parameter(&"mids")
	var stats: PackedInt32Array = v.disc.mat.get_shader_parameter(&"stat")
	var kinds: PackedInt32Array = v.disc.mat.get_shader_parameter(&"kinds")
	for i in st.player.wheel.slice_count:
		assert_almost_eq(mids[i], v.slice_deg(i, v.shown_rotation()), 0.01, "slot %d sits where the view puts it" % i)
		var slice := scene.engine.content(st.player.wheel.slot_slice_ids[i]) as SliceData
		assert_eq(kinds[i], slice.slice_type, "slot %d shows its program's screen" % i)
	assert_eq(stats[1], RC.Status.CORRUPTED, "the state overlay is the status (3.8)")
	assert_eq(int(v.disc.mat.get_shader_parameter(&"active")), v.active_slot())
	assert_true(bool(v.disc.mat.get_shader_parameter(&"ring_on")), "the Breaker's inner ring shows (3.10)")
	assert_eq(v.disc.size.x, v.disc.size.y, "the disc is square on the wheel")
	assert_almost_eq(v.disc.position.x + v.disc.size.x * 0.5, v._center().x, 0.5, "and centred on it")
	scene.skip_motion()


# --- 2A.7 precision landings ----------------------------------------------------------------------

func test_a_landing_headless_shows_its_end_state_at_once() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	for tier in [RC.PrecisionTier.PERFECT, RC.PrecisionTier.GOOD, RC.PrecisionTier.WEAK]:
		v.play_precision(tier, v.active_slot())
		assert_false(v.motion_busy(), "headless never waits (tier %d)" % tier)
		assert_eq(v.land_fx, 0.0)
		assert_eq(v.land_word, 0.0)
		assert_eq(v.latch, 0.0)
		assert_eq(v.stutter_deg, 0.0)
	scene.skip_motion()


func test_a_landing_plays_live_and_one_press_ends_it() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	Motion.force_live = true
	v.play_precision(RC.PrecisionTier.WEAK, v.active_slot())
	assert_true(v.motion_busy(), "the WEAK stutter and word play")
	await _frames(2)
	assert_gt(v.land_word, 0.0, "the word is up")
	MotionSkip.complete_all(v)
	assert_false(v.motion_busy(), "one press ends it")
	assert_eq(v.stutter_deg, 0.0, "the wheel back on its tick")
	assert_eq(v.land_word, 0.0, "the word gone")
	v.play_precision(RC.PrecisionTier.PERFECT, v.active_slot())
	assert_true(v.motion_busy(), "the PERFECT latch and word play")
	v.stop_motion()
	assert_eq(v.latch, 0.0)
	scene.skip_motion()


func test_reduce_effects_lands_with_the_rail_only() -> void:
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	Motion.force_live = true
	var scene := await _combat()
	var v: WheelView = scene._player_view
	v.play_precision(RC.PrecisionTier.PERFECT, v.active_slot())
	assert_false(v.motion_busy(), "no latch, word or flash under reduce effects (3.19)")
	assert_eq(v.land_fx, 0.0)
	assert_eq(v.landing_tint(), Palette.RESIST_GOLD, "the landing's tier still reads (gold)")
	v.disc.run_screens()
	assert_false(v.disc.is_processing(), "the CRT loop holds its first frame")
	assert_eq(float(v.disc.mat.get_shader_parameter(&"frame_pos_in")), 0.0)
	assert_false(WheelTelemetry.scrolls(), "the telemetry ring stands still")
	scene.skip_motion()


# --- 2A.4 hub states ------------------------------------------------------------------------------

func test_lockdown_fills_while_breached_and_drains_after() -> void:
	var scene := await _combat()
	var v: WheelView = scene._view_of(scene.engine.state().enemies[0].id)
	var foe: CombatantState = scene.engine.state().enemies[0]
	foe.hub_breached_turns = 2
	scene._refresh(scene.engine.state())
	assert_eq(v.lockdown_level, 1.0, "the waterline fills the hub (3.3)")
	foe.hub_breached_turns = 0
	scene._refresh(scene.engine.state())
	assert_eq(v.lockdown_level, 0.0, "headless: drained at once")
	Motion.force_live = true
	foe.hub_breached_turns = 1
	scene._refresh(scene.engine.state())
	foe.hub_breached_turns = 0
	scene._refresh(scene.engine.state())
	assert_true(v.motion_busy(), "live: it drains")
	v.stop_motion()
	assert_eq(v.lockdown_level, 0.0, "a press: drained")
	scene.skip_motion()


func test_the_defeat_drains_the_core_then_stamps_flatlined() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	v.play_flatline()
	assert_eq(v.drain_p, 1.0, "headless: the core is gone at once")
	assert_eq(v.flatline_pop, 1.0)
	assert_eq(String(v.flatline_box()["word"]), tr("FLATLINED"), "FLATLINED stamps in (3.3)")
	Motion.force_live = true
	v.flatlined = false
	v.play_flatline()
	assert_true(v.motion_busy())
	v.stop_motion()
	assert_eq(v.drain_p, 1.0, "the end state after a press")
	scene.skip_motion()


# --- layouts --------------------------------------------------------------------------------------

func test_the_stack_fits_its_view_at_every_text_scale() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		for v: WheelView in scene._views():
			if v.combatant == null:
				continue
			var k := v.art_scale()
			var c := v._center()
			var top := c.y - (v.frame_master() + WheelFace.BLADE_TOP) * k
			assert_gt(v._radius(), 0.0)
			assert_gte(v.global_position.y + top, 0.0, "scale %.1f: %s's blade stays on screen" % [scale, v.combatant.id])
			var side := (v.frame_master() + WheelFace.LUG_R) * k
			assert_gte(v.global_position.x + c.x - side, 0.0, "scale %.1f: the frame stays on screen (left)" % scale)
			assert_lte(v.global_position.x + c.x + side, SCREEN.size.x, "scale %.1f: the frame stays on screen (right)" % scale)
		scene.skip_motion()
		scene.get_parent().queue_free()
		await _frames(2)


# --- seams for 2C (cards and FX) ------------------------------------------------------------------

func test_the_fx_seams_reach_the_disc() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var full := v.hp_arc_spot(1.0)
	var empty := v.hp_arc_spot(0.0)
	assert_ne(full, empty, "the HP arc runs between two ends")
	assert_almost_eq(v.hp_ring_spot().distance_to(full), 0.0, 0.5, "full HP ends at the arc's full end")
	assert_gt(full.y, v.global_center().y, "the arc sits under the wheel (3.2)")
	v.rgb_split = 6.0
	v.pixelate = 8.0
	assert_eq(float(v.disc.mat.get_shader_parameter(&"rgb_split")), 6.0)
	assert_eq(float(v.disc.mat.get_shader_parameter(&"pixelate")), 8.0)
	v.stop_motion()
	assert_eq(v.rgb_split, 0.0, "a press ends the split")
	assert_null(v.wheel_texture(), "headless: no readback, the caller falls back")
	scene.skip_motion()


func test_the_guards_stand_after_their_effect() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var st: CombatState = scene.engine.state()
	assert_eq(v.foe_side(), 90.0, "the player's wall faces right, at its foe")
	st.player.block = 5
	st.player.shield = 4
	st.player.evade_charges = 1
	scene._refresh(st)
	await _frames(2)
	assert_eq(scene._view_of(st.enemies[0].id).foe_side(), 270.0, "an enemy's faces left")
	scene.skip_motion()
