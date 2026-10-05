extends GutTest
## Animation pass ANIM-1 (ANIMATION_HANDOFF 1, 3; STYLE_GUIDE 5-6): the UI motion table and the
## Motion kit. The table loads and carries every id; every helper applies its end state
## at once (no running tween) under reduce effects and headless; motion never touches
## game state; the speed multiplier scales durations; timings come from the table.

const MOTION_SRC := "res://scripts/ui/kit/motion.gd"

var _reduce: bool
var _speed: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_speed = Motion.speed
	Motion.force_live = false
	Motion.use_config(null)


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	Motion.force_live = false
	Motion.speed = _speed
	Motion.use_config(null)


## A 1280x720 holder with a 100x40 control at (200, 100), rest scale and alpha 1.
func _node() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var c := Control.new()
	c.position = Vector2(200, 100)
	c.size = Vector2(100, 40)
	holder.add_child(c)
	return c


## A duplicate of the table the test may change (the loaded resource stays untouched).
func _tunable() -> UiMotionData:
	var cfg: UiMotionData = (load(Motion.CONFIG_PATH) as UiMotionData).duplicate(true)
	Motion.use_config(cfg)
	return cfg


func _live_all() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Motion.force_live = true


# --- The table ---------------------------------------------------------------------------

func test_config_loads_and_has_every_id() -> void:
	var cfg := Motion.config()
	assert_not_null(cfg, "ui_motion.tres loads")
	assert_eq(cfg.resource_path, Motion.CONFIG_PATH)
	assert_eq(cfg.validate().size(), 0, "no repeated ids")
	for id in UiMotionData.REQUIRED_IDS:
		assert_true(Motion.has(id), "entry %s" % id)
		var e := Motion.entry(id)
		if e != null:
			assert_eq(e.validate().size(), 0, "%s valid" % id)
			assert_true(e.enabled, "%s on by default" % id)
	assert_eq(cfg.entries.size(), UiMotionData.REQUIRED_IDS.size(), "no stray entries")


func test_every_roadmap_section_has_an_entry() -> void:
	# Handoff 4.1-4.24: one id per section at least, as the REQUIRED_IDS comments tag.
	var src := FileAccess.get_file_as_string("res://scripts/data/ui_motion_data.gd")
	for n in range(1, 25):
		assert_true(src.contains("# 4.%d\n" % n) or src.contains("# 4.%d\r\n" % n), "section 4.%d has ids" % n)


func test_registry_finds_the_motion_table() -> void:
	assert_not_null(ContentRegistry.motion, "ContentRegistry picks up the UiMotionData")
	assert_eq(ContentRegistry.motion.resource_path, ContentRegistry.MOTION_PATH)
	assert_eq(ContentRegistry.validate().size(), 0, "content still validates")


func test_values_come_from_the_config() -> void:
	var e := Motion.entry(&"card_hover")
	assert_almost_eq(Motion.seconds(&"card_hover"), e.duration, 0.0001)
	assert_almost_eq(Motion.amplitude(&"card_hover"), e.amplitude, 0.0001)
	assert_almost_eq(Motion.delay_of(&"card_draw"), Motion.entry(&"card_draw").delay, 0.0001)
	# A tuned copy (the lab's way) changes what the helpers read; the file does not change.
	var cfg := _tunable()
	cfg.find(&"card_hover").duration = 0.9
	cfg.find(&"card_hover").amplitude = 1.5
	assert_almost_eq(Motion.seconds(&"card_hover"), 0.9, 0.0001)
	_live_all()
	var n := _node()
	var tw := Motion.pop(n, &"card_hover")
	assert_not_null(tw)
	tw.custom_step(0.9 * Motion.POP_GROW_SHARE)
	assert_almost_eq(n.scale.x, 1.5, 0.01, "the pop grows to the tuned amplitude")
	tw.custom_step(1.0)
	assert_almost_eq(n.scale.x, 1.0, 0.001, "and settles at rest")
	Motion.use_config(null)
	assert_almost_eq(Motion.seconds(&"card_hover"), e.duration, 0.0001, "the loaded table is untouched")


func test_moved_inline_numbers_read_the_config() -> void:
	# The old inline constants are gone; the owners read motion ids instead.
	var owners := {
		"res://scripts/ui/kit/toast.gd": ["SHOW_SECONDS", "FADE_SECONDS"],
		"res://scripts/ui/combat_scene.gd": ["PASS_DELAY", "\"shake\", Vector2(4", "\"modulate:a\", 0.4, 0.04", "\"pointer_alpha\", 0.2, 0.25", "0.35, 0.12)"],
		"res://scripts/ui/kit/neon_city.gd": ["BEACON_PERIOD", "BEACON_DUTY"],
		"res://scripts/autoload/fx.gd": ["1.2).set_delay(0.6)", "seconds: float = 0.7", "strength: float = 0.45", "frames: int = 2"],
	}
	for path in owners:
		var src := FileAccess.get_file_as_string(path)
		for old in owners[path]:
			assert_false(src.contains(old), "%s no longer has %s" % [path, old])
	assert_true(FileAccess.get_file_as_string("res://scripts/ui/kit/drip_button.gd").contains("&\"drip_halo\""))


func test_fx_defaults_come_from_the_config() -> void:
	var was := Fx.limiter.enabled
	Fx.limiter.enabled = false
	# ART-0 E (ported from art-pass W6): a full-screen flash is T4 only, held to T4's alpha.
	assert_true(Fx.flash(Color.WHITE, -1.0, -1.0, VfxTier.T4))
	assert_almost_eq(Fx.flash_rect.color.a, VfxTier.clamp_alpha(VfxTier.T4, Motion.amplitude(&"screen_flash")), 0.001,
		"flash strength = screen_flash amplitude, held to T4")
	Fx.limiter.enabled = was
	Fx.flash_rect.color.a = 0.0


# --- Reduce effects and headless ---------------------------------------------------------

func _run_every_helper(n: Control, label: Label) -> Array:
	return [
		Motion.run(&"panel_in", n, ^"position:x", 300.0),
		Motion.fade(n, 0.25, &"visited_dim"),
		Motion.pop(n, &"sticky_bump"),
		Motion.slide_in(n, Vector2(-48, 0), &"panel_in"),
		Motion.shake(n, &"precision_partial"),
		Motion.blink(n, &"precision_blink"),
		Motion.loop_pulse(n, ^"modulate:a", &"pointer_flicker"),
		Motion.number_roll(label, 3, 42, &"number_roll"),
	]


func _assert_end_state(n: Control, label: Label, tweens: Array, why: String) -> void:
	for tw in tweens:
		assert_null(tw, "%s: no tween" % why)
	assert_almost_eq(n.position, Vector2(300, 100), Vector2.ONE * 0.001, "%s: moved at once, slide and shake end home" % why)
	assert_almost_eq(n.scale, Vector2.ONE, Vector2.ONE * 0.001, "%s: pop ends at rest" % why)
	assert_almost_eq(n.modulate.a, 1.0, 0.001, "%s: blink ends lit" % why)
	assert_eq(label.text, "42", "%s: number shows its end value" % why)
	assert_eq(n.get_meta_list().size(), 0, "%s: nothing held" % why)


func test_reduce_effects_applies_the_end_state_at_once() -> void:
	Settings.set_reduce_effects(true)
	Motion.force_live = true  # reduce effects wins even when forced
	var n := _node()
	var label: Label = add_child_autofree(Label.new())
	_assert_end_state(n, label, _run_every_helper(n, label), "reduce effects")
	assert_false(Motion.animating())


func test_headless_applies_the_end_state_at_once() -> void:
	assert_eq(DisplayServer.get_name(), "headless")
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Motion.force_live = false
	var n := _node()
	var label: Label = add_child_autofree(Label.new())
	_assert_end_state(n, label, _run_every_helper(n, label), "headless")


func test_a_disabled_entry_applies_the_end_state_at_once() -> void:
	var cfg := _tunable()
	cfg.find(&"sticky_bump").enabled = false
	_live_all()
	var n := _node()
	assert_null(Motion.pop(n, &"sticky_bump"))
	var other := Motion.pop(n, &"node_pop")
	assert_not_null(other, "others still play")
	if other != null:
		other.custom_step(10.0)


func test_live_helpers_end_where_the_instant_path_does() -> void:
	_live_all()
	var home := Vector2(200, 100)
	var n := _node()
	_finish(Motion.run(&"panel_in", n, ^"position:x", 300.0), "run")
	assert_almost_eq(n.position.x, 300.0, 0.01, "run reaches its target")
	n = _node()
	_finish(Motion.fade(n, 0.25, &"visited_dim"), "fade")
	assert_almost_eq(n.modulate.a, 0.25, 0.01)
	n = _node()
	_finish(Motion.pop(n, &"sticky_bump"), "pop")
	assert_almost_eq(n.scale, Vector2.ONE, Vector2.ONE * 0.01, "pop settles at rest")
	n = _node()
	var slide := Motion.slide_in(n, Vector2(-48, 0), &"panel_in")
	assert_almost_eq(n.position, home + Vector2(-48, 0), Vector2.ONE * 0.01, "slide starts off its rest spot")
	_finish(slide, "slide_in")
	assert_almost_eq(n.position, home, Vector2.ONE * 0.01, "slide ends home")
	n = _node()
	_finish(Motion.shake(n, &"precision_partial"), "shake")
	assert_almost_eq(n.position, home, Vector2.ONE * 0.01, "shake ends home")
	n = _node()
	_finish(Motion.blink(n, &"precision_blink"), "blink")
	assert_almost_eq(n.modulate.a, 1.0, 0.01, "blink ends lit")
	n = _node()
	var pulse := Motion.loop_pulse(n, ^"modulate:a", &"pointer_flicker")
	assert_not_null(pulse, "loop plays when live")
	pulse.custom_step(Motion.seconds(&"pointer_flicker"))
	assert_almost_eq(n.modulate.a, Motion.amplitude(&"pointer_flicker"), 0.01, "dips to the amplitude")
	pulse.kill()
	var label: Label = add_child_autofree(Label.new())
	_finish(Motion.number_roll(label, 3, 42, &"number_roll"), "number_roll")
	assert_eq(label.text, "42")


func _finish(tw: Tween, what: String) -> void:
	assert_not_null(tw, "%s plays when live" % what)
	if tw != null:
		tw.custom_step(10.0)
		assert_false(tw.is_running(), "%s finished" % what)


func test_a_restarted_helper_settles_on_the_rest_value() -> void:
	_live_all()
	var n := _node()
	var tw := Motion.shake(n, &"heat_letters_shake")
	tw.custom_step(Motion.seconds(&"heat_letters_shake") * 0.2)
	assert_ne(n.position, Vector2(200, 100), "mid-shake")
	var again := Motion.shake(n, &"heat_letters_shake")
	assert_false(tw.is_valid(), "the first shake stops")
	again.custom_step(10.0)
	assert_almost_eq(n.position, Vector2(200, 100), Vector2.ONE * 0.001, "home, not a mid-shake spot")


# --- Game state ---------------------------------------------------------------------------

func test_motion_never_touches_game_state() -> void:
	var src := FileAccess.get_file_as_string(MOTION_SRC)
	for banned in ["RunManager", "RngService", "SaveService", "ContentRegistry", "CombatState", "CampaignState", "randi(", "randf(", "randomize(", "ResourceSaver"]:
		assert_false(src.contains(banned), "Motion never uses %s" % banned)
	var rng_before := RngService.to_dict()
	var camp_before: Variant = RunManager.campaign.to_dict() if RunManager.campaign != null else null
	_live_all()
	var n := _node()
	var label: Label = add_child_autofree(Label.new())
	for tw in _run_every_helper(n, label):
		if tw != null:
			(tw as Tween).kill()
	assert_eq(RngService.to_dict(), rng_before, "no game RNG drawn")
	if camp_before != null:
		assert_eq(RunManager.campaign.to_dict(), camp_before, "campaign untouched")
	var cfg: UiMotionData = load(Motion.CONFIG_PATH)
	assert_same(Motion.config(), cfg, "the kit reads the loaded table")
	assert_false(cfg.find(&"card_hover") == null)


# --- Speed ------------------------------------------------------------------------------

func test_speed_scales_durations() -> void:
	var base := Motion.entry(&"raid_move").duration
	Motion.set_speed(2.0)
	assert_almost_eq(Motion.seconds(&"raid_move"), base / 2.0, 0.0001, "2x = half the seconds")
	Motion.set_speed(0.25)
	assert_almost_eq(Motion.seconds(&"raid_move"), base * 4.0, 0.0001, "0.25x = four times")
	Motion.set_speed(10.0)
	assert_eq(Motion.speed, Motion.SPEED_MAX, "clamped")
	Motion.set_speed(0.0)
	assert_eq(Motion.speed, Motion.SPEED_MIN, "clamped")
	Motion.set_speed(1.0)
	assert_almost_eq(Motion.seconds(&"raid_move"), base, 0.0001)


func test_speed_scales_a_running_tween() -> void:
	_live_all()
	Motion.set_speed(2.0)
	var n := _node()
	var d := Motion.entry(&"panel_in").duration
	var tw := Motion.run(&"panel_in", n, ^"position:x", 500.0)
	tw.custom_step(d / 2.0 + 0.001)
	assert_almost_eq(n.position.x, 500.0, 0.01, "done in half the time at 2x")
	Motion.set_speed(1.0)


func test_tres_lines_round_trip_an_entry() -> void:
	var e := Motion.entry(&"card_hover")
	var lines := Motion.tres_lines(e)
	assert_true(lines.contains("id = &\"card_hover\""))
	assert_true(lines.contains("duration = %s" % Motion._num(e.duration)))
	assert_true(lines.contains("ease = %d" % e.ease))
	assert_true(lines.contains("trans = %d" % e.trans))


func test_stop_puts_every_motion_back_at_rest() -> void:
	_live_all()
	var n := _node()
	var slide := Motion.slide_in(n, Vector2(0, -40), &"panel_drop")
	var pop := Motion.pop(n, &"node_pop")
	var pulse := Motion.loop_pulse(n, ^"modulate:a", &"pointer_flicker")
	for tw in [slide, pop, pulse]:
		(tw as Tween).custom_step(0.05)
	Motion.stop(n)
	for tw in [slide, pop, pulse]:
		assert_false((tw as Tween).is_valid(), "stopped")
	assert_almost_eq(n.position, Vector2(200, 100), Vector2.ONE * 0.001)
	assert_almost_eq(n.scale, Vector2.ONE, Vector2.ONE * 0.001)
	assert_almost_eq(n.modulate.a, 1.0, 0.001)
	assert_eq(n.get_meta_list().size(), 0, "nothing held")


func test_the_motion_lab_shows_every_id() -> void:
	var lab: Script = load("res://tools/design_lab/motion_lab.gd")
	var demos: Dictionary = lab.get_script_constant_map()["DEMOS"]
	for id in UiMotionData.REQUIRED_IDS:
		assert_true(demos.has(id), "the lab has a demo for %s" % id)


func test_animation_pass_scope_ids_are_in_the_table() -> void:
	# The designer's Animation pass scope beyond handoff 4 (raid execution, card targeting
	# and execution, end-turn resolution, spinner movement, drag and drop, city influence).
	for id in [&"ice_lock_ring", &"forecast_stamp_resolve", &"card_pickup", &"drag_cancel_return", &"card_stamp",
			&"resolve_beat", &"last_turn_reveal", &"wheel_respin", &"enemy_turn_spin", &"drop_settle",
			&"loadout_swap", &"crew_assign", &"influence_crossfade", &"influence_spread"]:
		assert_true(Motion.has(id), "entry %s" % id)
