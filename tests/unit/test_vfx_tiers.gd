extends GutTest
## ART-0 E (S4), ported from art-pass W6 (ART_BIBLE v2 5.3, 5.4): VFX tiers. Every motion
## entry declares a valid tier (T0-T4) in ui_motion.tres; the tier limits live in one place
## (VfxTier) and clamp; Fx.flash is full screen and T4 only (refused below T4, nothing under
## reduce effects) and the one limiter governs every flash; no code path asks for a
## full-screen flash below T4; the Perfect and a boss phase burst on their own wheel. And
## the shader side: every shader reads the one `reduce_effects` global shader uniform
## (rc_common, registered in project.godot), and Fx sets it from the setting (ART-0 E2).

const MOTION_TRES := "res://content/config/ui_motion.tres"
const SHADER_DIR := "res://shaders"
const INCLUDE := "res://shaders/lib/rc_common.gdshaderinc"

var _reduce: bool
var _limiter_on: bool


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_limiter_on = Fx.limiter.enabled
	Motion.use_config(null)


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	Fx.limiter.enabled = _limiter_on
	Fx.limiter.reset()
	Fx.flash_rect.color.a = 0.0
	Motion.force_live = false


# --- Every entry has a valid tier -----------------------------------------------------------

func test_every_motion_entry_declares_a_valid_tier() -> void:
	var table := load(MOTION_TRES) as UiMotionData
	assert_gt(table.entries.size(), 100)
	for e in table.entries:
		assert_true(VfxTier.valid(int(e.tier)), "%s has a tier T0..T4" % e.id)
		assert_eq(e.validate().size(), 0, "%s validates" % e.id)
	# Written out, not left to the default: one `tier =` line per entry in the file.
	var src := FileAccess.get_file_as_string(MOTION_TRES)
	assert_eq(src.count("\ntier = "), src.count("[sub_resource type=\"Resource\""), "every entry names its tier")


func test_tiers_follow_the_bibles_examples() -> void:
	# ART_BIBLE v2 5.3's examples, one or two per tier.
	var expect := {&"city_traffic": VfxTier.T0, &"beacon_blink": VfxTier.T0, &"menu_cursor_blink": VfxTier.T0,
		&"card_hover": VfxTier.T1, &"wheel_nudge": VfxTier.T1, &"sticky_bump": VfxTier.T1,
		&"hit_line": VfxTier.T2, &"card_stamp": VfxTier.T2, &"drop_stamp": VfxTier.T2, &"buy_fly": VfxTier.T2,
		&"precision_perfect": VfxTier.T3, &"enemy_break": VfxTier.T3, &"boss_phase_flash": VfxTier.T3, &"heat_banner": VfxTier.T3,
		&"influence_mark": VfxTier.T3, &"wheel_burst_perfect": VfxTier.T3, &"wheel_burst_phase": VfxTier.T3,
		&"jack_in": VfxTier.T4, &"jack_out": VfxTier.T4, &"screen_flash": VfxTier.T4}
	for id in expect:
		assert_true(Motion.has(id), "%s is in the table" % id)
		assert_eq(VfxTier.of(id), expect[id], "%s is %s" % [id, VfxTier.NAMES[expect[id]]])
	assert_eq(VfxTier.of(&"no_such_entry"), VfxTier.T1, "no entry: T1")


func test_the_fx_layers_effects_fit_their_tier() -> void:
	# The effects the FX layers draw (flashes, bursts, raid effects) run within their tier's
	# duration and are local (below T4).
	for id in [&"wheel_burst_perfect", &"wheel_burst_phase", &"victory_flash", &"raid_hit_effect", &"turret_trace",
			&"ice_lock_ring", &"node_damage_number", &"raid_flip", &"raid_result_banner"]:
		assert_true(Motion.has(id), "%s is in the table" % id)
		assert_true(VfxTier.fits(Motion.entry(id)), "%s runs within its tier" % id)
		assert_lt(VfxTier.of(id), VfxTier.T4, "%s is below T4 (local)" % id)


func test_every_one_shot_entry_fits_its_tier() -> void:
	# ART-0 audit E2: every entry, not a hand-picked few. A one-shot effect runs within its
	# tier's longest duration; holds, waits and loops say so with their `kind`.
	var table := load(MOTION_TRES) as UiMotionData
	var over: Array[String] = []
	for e in table.entries:
		assert_true(e.kind >= UiMotionEntryData.Kind.ONE_SHOT and e.kind <= UiMotionEntryData.Kind.LOOP, "%s has a valid kind" % e.id)
		if e.kind == UiMotionEntryData.Kind.ONE_SHOT and e.duration > VfxTier.MAX_SECONDS[int(e.tier)] + 0.0001:
			over.append("%s %.2f s > %s's %.2f s" % [e.id, e.duration, VfxTier.NAMES[int(e.tier)], VfxTier.MAX_SECONDS[int(e.tier)]])
		assert_true(VfxTier.fits(e), "%s fits (or is marked a hold or a loop)" % e.id)
	assert_eq(over, [] as Array[String], "one-shot effects over their tier")


func test_holds_and_loops_are_marked_and_only_one_shots_are_held_to_the_duration() -> void:
	for id in [&"toast_note_hold", &"combat_end_hold", &"jack_arrival_wait", &"asset_drop_wait", &"resolve_sequence", &"saved_stamp"]:
		assert_eq(int(Motion.entry(id).kind), UiMotionEntryData.Kind.HOLD, "%s is a hold" % id)
	for id in [&"drop_zone_pulse", &"ram_pending_blink", &"send_it_ready", &"tutorial_next_pulse", &"pointer_orbit"]:
		assert_eq(int(Motion.entry(id).kind), UiMotionEntryData.Kind.LOOP, "%s is a loop" % id)
	assert_eq(int(Motion.entry(&"buy_fly").kind), UiMotionEntryData.Kind.ONE_SHOT, "a flight is an effect")
	assert_true(Motion.seconds(&"buy_fly") <= VfxTier.MAX_SECONDS[VfxTier.T2] + 0.0001, "buy_fly fits T2 (the bible's example)")
	var e := UiMotionEntryData.new()
	e.id = &"gut_kind"
	e.tier = UiMotionEntryData.Tier.T1_FEEDBACK
	e.duration = 3.0
	assert_false(VfxTier.fits(e), "a 3 s one-shot is over T1")
	e.kind = UiMotionEntryData.Kind.HOLD
	assert_true(VfxTier.fits(e), "a 3 s hold is not an effect length")
	e.kind = UiMotionEntryData.Kind.LOOP
	assert_true(VfxTier.fits(e), "nor is a loop's period")


# --- The limits clamp ------------------------------------------------------------------------

func test_the_tier_limits_clamp() -> void:
	assert_eq(VfxTier.clamp_alpha(VfxTier.T0, 0.5), 0.0, "T0: no flashes")
	assert_almost_eq(VfxTier.clamp_alpha(VfxTier.T1, 0.9), 0.2, 0.0001, "T1: a +20% glow")
	assert_almost_eq(VfxTier.clamp_alpha(VfxTier.T2, 0.9), 0.6, 0.0001, "T2: 60%")
	assert_almost_eq(VfxTier.clamp_alpha(VfxTier.T3, 0.9), 0.7, 0.0001, "T3: 70%")
	assert_almost_eq(VfxTier.clamp_alpha(VfxTier.T4, 0.9), 0.4, 0.0001, "T4: white at 40%")
	assert_almost_eq(VfxTier.clamp_alpha(VfxTier.T3, 0.3), 0.3, 0.0001, "under the limit: unchanged")
	assert_almost_eq(VfxTier.clamp_seconds(VfxTier.T1, 1.0), 0.25, 0.0001)
	assert_almost_eq(VfxTier.clamp_seconds(VfxTier.T2, 1.0), 0.6, 0.0001)
	assert_almost_eq(VfxTier.clamp_seconds(VfxTier.T3, 2.0), 1.2, 0.0001)
	assert_almost_eq(VfxTier.clamp_seconds(VfxTier.T4, 9.0), 2.5, 0.0001)
	assert_eq(VfxTier.clamp_shake(VfxTier.T1, 3.0), 0.0, "no shake below T2")
	assert_eq(VfxTier.clamp_shake(VfxTier.T2, 3.0), 2.0)
	assert_eq(VfxTier.clamp_shake(VfxTier.T3, 9.0), 4.0)
	assert_eq(VfxTier.clamp_shake(VfxTier.T4, 9.0), 0.0, "T4 moves the camera instead")
	assert_eq(VfxTier.clamp_hit_stop(VfxTier.T2, 5), 2)
	assert_eq(VfxTier.clamp_hit_stop(VfxTier.T3, 5), 3)
	assert_eq(VfxTier.clamp_radius(VfxTier.T1, 500.0, 40.0, 100.0), 56.0, "T1: element + 16 px")
	assert_eq(VfxTier.clamp_radius(VfxTier.T2, 500.0, 40.0, 100.0), 65.0, "T2: element + 25% of the region")
	assert_eq(VfxTier.clamp_radius(VfxTier.T3, 500.0, 40.0, 100.0), 100.0, "T3: the region")
	assert_eq(VfxTier.clamp_radius(VfxTier.T4, 500.0, 40.0, 100.0), 500.0, "T4: the screen")
	assert_false(VfxTier.allows_full_screen(VfxTier.T3))
	assert_true(VfxTier.allows_full_screen(VfxTier.T4))
	assert_false(VfxTier.valid(5))


func test_fx_caps_shake_and_hit_stop_by_tier() -> void:
	assert_true(Fx.shake_px(&"hit_shake") <= VfxTier.MAX_SHAKE_PX[VfxTier.of(&"hit_shake")], "a hit's shake held to its tier")
	assert_true(VfxTier.clamp_hit_stop(VfxTier.of(&"hit_freeze"), roundi(Motion.amplitude(&"hit_freeze"))) == roundi(Motion.amplitude(&"hit_freeze")),
		"the shipped hit-stop already fits its tier (the clamp changes nothing today)")
	Settings.set_reduce_effects(true)
	assert_eq(Fx.shake_px(&"hit_shake"), 0.0, "no shake under reduce effects")


## ART-0 audit E1: the ids the code passes to Motion.shake (read from the scripts).
func _shake_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	var call := RegEx.create_from_string("Motion\\.shake\\([^,]+,\\s*&\"([a-z0-9_]+)\"")
	var files := PackedStringArray()
	_gd_files("res://scripts", files)
	for path in files:
		for m in call.search_all(FileAccess.get_file_as_string(path)):
			var id := StringName(m.get_string(1))
			if not out.has(id):
				out.append(id)
	out.sort()
	return out


func test_every_shake_fits_its_tier() -> void:
	# ART-0 audit E1 (ART_BIBLE v2 5.3): Motion.shake holds every shake to its tier, and the
	# shipped amplitudes already fit, so the clamp changes nothing on screen.
	var ids := _shake_ids()
	for id in [&"hit_shake", &"heat_letters_shake", &"precision_weak"]:
		assert_true(ids.has(id), "%s is shaken through Motion.shake" % id)
	for id in ids:
		assert_true(Motion.has(id), "%s is in the table" % id)
		var tier := VfxTier.of(id)
		assert_true(Motion.amplitude(id) <= VfxTier.MAX_SHAKE_PX[tier] + 0.0001,
			"%s: %.1f px fits %s's %.0f px" % [id, Motion.amplitude(id), VfxTier.NAMES[tier], VfxTier.MAX_SHAKE_PX[tier]])
		assert_eq(Motion.shake_px(id), Motion.amplitude(id), "%s plays its own amplitude" % id)
	assert_eq(Motion.amplitude(&"hit_shake"), 2.0, "a hit shakes 2 px (ART-2 2C)")
	assert_eq(VfxTier.of(&"hit_shake"), VfxTier.T2)


func test_motion_shake_clamps_an_amplitude_over_its_tier() -> void:
	var table := UiMotionData.new()
	var loud := UiMotionEntryData.new()
	loud.id = &"gut_loud_shake"
	loud.duration = 0.2
	loud.amplitude = 9.0
	loud.tier = UiMotionEntryData.Tier.T2_OUTCOME
	var quiet := UiMotionEntryData.new()
	quiet.id = &"gut_t1_shake"
	quiet.duration = 0.2
	quiet.amplitude = 9.0
	quiet.tier = UiMotionEntryData.Tier.T1_FEEDBACK
	table.entries = [loud, quiet]
	Motion.use_config(table)
	assert_eq(Motion.shake_px(&"gut_loud_shake"), VfxTier.MAX_SHAKE_PX[VfxTier.T2], "9 px at T2 plays 2 px")
	assert_eq(Motion.shake_px(&"gut_t1_shake"), 0.0, "no shake below T2")
	# The real tween: after its first step the node stands at the clamped offset.
	Motion.force_live = true
	var node: Node2D = add_child_autofree(Node2D.new())
	var tw := Motion.shake(node, &"gut_loud_shake")
	assert_not_null(tw, "it plays")
	if tw != null:
		tw.custom_step(0.2 / Motion.SHAKE_STEPS)
		assert_almost_eq(node.position.x, VfxTier.MAX_SHAKE_PX[VfxTier.T2], 0.05, "the first swing is held to 2 px")
		tw.custom_step(1.0)
		assert_almost_eq(node.position.x, 0.0, 0.01, "and it ends where it started")
	Motion.use_config(null)


# --- Fx.flash -------------------------------------------------------------------------------

func test_fx_flash_refuses_full_screen_below_t4() -> void:
	Fx.limiter.enabled = false
	for tier in [VfxTier.T0, VfxTier.T1, VfxTier.T2, VfxTier.T3]:
		var refused := Fx.refused_flashes
		var shown := Fx.flashes_shown.size()
		assert_false(Fx.flash(Color.WHITE, 0.3, 0.1, tier), "%s may not flash the screen" % VfxTier.NAMES[tier])
		assert_eq(Fx.refused_flashes, refused + 1, "counted as refused")
		assert_eq(Fx.flashes_shown.size(), shown, "nothing shown")
		assert_eq(Fx.flash_rect.color.a, 0.0, "the screen stays clear")
	assert_false(Fx.flash(Color.WHITE), "no tier given: refused (a caller must say T4)")
	assert_true(Fx.flash(Color.WHITE, 0.9, 0.1, VfxTier.T4), "T4 may")
	assert_almost_eq(Fx.flash_rect.color.a, VfxTier.MAX_FLASH_ALPHA[VfxTier.T4], 0.0001, "held to T4's 40%")


func test_fx_flash_does_nothing_under_reduce_effects() -> void:
	Fx.limiter.enabled = false
	Settings.set_reduce_effects(true)
	var shown := Fx.flashes_shown.size()
	assert_false(Fx.flash(Color.WHITE, 0.3, 0.1, VfxTier.T4), "no flash at all")
	assert_eq(Fx.flash_rect.color.a, 0.0)
	assert_false(Fx.request_flash(), "no local flash either")
	assert_eq(Fx.flashes_shown.size(), shown)


func test_one_limiter_governs_local_and_full_screen_flashes() -> void:
	Fx.limiter.enabled = true
	Fx.limiter.reset()
	var granted := 0
	for k in 3:
		if Fx.request_flash():
			granted += 1
	assert_eq(granted, 3, "three local flashes in a second")
	assert_false(Fx.request_flash(), "a fourth waits")
	assert_false(Fx.flash(Color.WHITE, 0.3, 0.1, VfxTier.T4), "and a full-screen one counts against the same limit")
	assert_true(FlashLimiter.stream_is_safe(Fx.flashes_shown.slice(-3)))


# --- No full-screen flash below T4 anywhere (grep) ---------------------------------------------

func _gd_files(dir: String, out: PackedStringArray) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_gd_files(dir.path_join(d), out)


func test_no_code_path_calls_a_full_screen_flash_below_t4() -> void:
	# Every `Fx.flash(` call under scripts/ and tools/ must pass VfxTier.T4.
	var files := PackedStringArray()
	_gd_files("res://scripts", files)
	_gd_files("res://tools", files)
	var calls := 0
	for path in files:
		var lines := FileAccess.get_file_as_string(path).split("\n")
		for i in lines.size():
			var code := lines[i].split("#")[0]
			if not code.contains("Fx.flash("):
				continue
			calls += 1
			# The call may run over the next lines: read to its closing parenthesis.
			var call := code.substr(code.find("Fx.flash("))
			var j := i
			while call.count("(") > call.count(")") and j + 1 < lines.size():
				j += 1
				call += lines[j].split("#")[0]
			assert_true(call.contains("VfxTier.T4"), "%s:%d asks for a full-screen flash without T4: %s" % [path, i + 1, call.strip_edges()])
	gut.p("Fx.flash calls checked: %d" % calls)


# --- Wheel-local T3 bursts ----------------------------------------------------------------------

func _layer() -> CombatFxLayer:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var layer := CombatFxLayer.new()
	holder.add_child(layer)
	return layer


func _bursts(layer: CombatFxLayer) -> Array:
	return layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "wheel_burst")


func test_wheel_burst_is_the_end_state_at_once_headless_and_under_reduce_effects() -> void:
	var layer := _layer()
	var shown := Fx.flashes_shown.size()
	assert_false(layer.wheel_burst(Vector2(400, 300), 120.0, CombatFxLayer.BURST_PERFECT), "headless: nothing plays")
	assert_true(_bursts(layer).is_empty())
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	assert_false(layer.wheel_burst(Vector2(400, 300), 120.0, CombatFxLayer.BURST_PHASE, Palette.CORP_SOLACE), "reduce effects: nothing")
	assert_true(_bursts(layer).is_empty())
	assert_false(layer.busy(), "nothing left running")
	assert_eq(Fx.flashes_shown.size(), shown, "no flash counted")


func test_wheel_burst_stays_on_its_wheel_within_t3() -> void:
	var layer := _layer()
	Motion.force_live = true
	Fx.limiter.enabled = false
	for kind in [CombatFxLayer.BURST_PERFECT, CombatFxLayer.BURST_PHASE]:
		assert_true(layer.wheel_burst(Vector2(400, 300), 120.0, kind, Palette.CORP_SOLACE if kind == CombatFxLayer.BURST_PHASE else Palette.AUTO), "%s plays" % kind)
	var bursts := _bursts(layer)
	assert_eq(bursts.size(), 2)
	for s in bursts:
		assert_true(float(s["alpha"]) <= VfxTier.MAX_FLASH_ALPHA[VfxTier.T3] + 0.0001, "<= 70% alpha")
		assert_true(float(s["dur"]) <= VfxTier.MAX_SECONDS[VfxTier.T3] + 0.0001, "<= 1.2 s")
		assert_true(float(s["reach"]) <= 120.0 * CombatFxLayer.WHEEL_REGION + 0.001, "inside the wheel's region, never the screen")
	assert_eq(bursts[0]["color"], Palette.CELL_PINK, "Perfect in the Cell's pink")
	assert_eq(bursts[1]["color"], Palette.CORP_SOLACE, "a phase in the boss's corp hue")
	assert_false(layer.wheel_burst(Vector2(400, 300), 120.0, &"nope"), "an unknown kind plays nothing")
	# It draws (a frame with the bursts on) without an error.
	layer.queue_redraw()
	await get_tree().process_frame
	layer.clear()


func test_wheel_bursts_go_through_the_one_limiter() -> void:
	var layer := _layer()
	Motion.force_live = true
	Fx.limiter.enabled = true
	Fx.limiter.reset()
	var played := 0
	for k in 5:
		if layer.wheel_burst(Vector2(400, 300), 120.0, CombatFxLayer.BURST_PERFECT):
			played += 1
	assert_eq(played, 3, "at most 3 flashes a second, local ones too")
	layer.clear()


func test_a_disc_flash_is_held_to_its_tier_and_limited() -> void:
	var layer := _layer()
	Motion.force_live = true
	Fx.limiter.enabled = false
	layer.disc_flash(Vector2(400, 300), 80.0, Color.WHITE, &"victory_flash")
	var discs := layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "disc")
	assert_eq(discs.size(), 1)
	var tier := VfxTier.of(&"victory_flash")
	assert_true(float(discs[0]["alpha"]) <= VfxTier.MAX_FLASH_ALPHA[tier] + 0.0001, "the VICTORY disc is held to its tier's alpha")
	layer.clear()


func test_the_combat_scene_flashes_its_wheels_not_the_screen() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	assert_false(src.contains("Fx.flash("), "no full-screen flash left in combat")
	assert_true(src.contains("wheel_burst(view.global_center(), view.disc_radius(), CombatFxLayer.BURST_PERFECT)"), "Perfect bursts on its wheel")
	# ART-2 2C: and its orange bits stream from the crossed phase pip (the HP ring spot).
	assert_true(src.contains("CombatFxLayer.BURST_PHASE, hue, bv.hp_ring_spot())"), "a phase bursts on the boss's wheel in its corp hue")


# --- Raid FX ------------------------------------------------------------------------------------

func test_raid_effects_have_tiers_and_none_covers_the_screen() -> void:
	for kind in RaidFxLayer.FX_MOTION:
		var id: StringName = RaidFxLayer.FX_MOTION[kind]
		assert_true(Motion.has(id), "raid %s has its entry %s" % [kind, id])
		var tier := RaidFxLayer.fx_tier(kind)
		assert_true(VfxTier.valid(tier), "raid %s has a tier" % kind)
		assert_lt(tier, VfxTier.T4, "raid %s is local, never cinematic" % kind)
		assert_true(VfxTier.fits(Motion.entry(id)), "raid %s runs within its tier" % kind)
	assert_true(VfxTier.clamp_alpha(RaidFxLayer.fx_tier("tint"), RaidFxLayer.TINT_ALPHA) == RaidFxLayer.TINT_ALPHA, "the district wash is within T3")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/raid_fx_layer.gd")
	assert_false(src.contains("Fx.flash("), "no full-screen flash in the raid")
	for full in ["draw_rect(get_rect()", "draw_rect(Rect2(Vector2.ZERO, size)"]:
		assert_false(src.contains(full), "nothing drawn over the whole map (%s)" % full)


# --- Shaders: the one reduce_effects control ---------------------------------------------------

# ART-0 audit E3: every *.gdshader in the project except addons/ (res://shaders and its
# subfolders, assets/, tools/), not only the top level of res://shaders.
func _shaders() -> PackedStringArray:
	var out := PackedStringArray()
	_collect_shaders("res://", out)
	out.sort()
	return out


func _collect_shaders(dir: String, out: PackedStringArray) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gdshader"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		if d.begins_with(".") or (dir == "res://" and d == "addons"):
			continue
		_collect_shaders(dir.path_join(d), out)


func test_the_shader_scan_reaches_every_folder() -> void:
	var files := _shaders()
	for path in [SHADER_DIR.path_join("kit/crt_terminal.gdshader"), "res://assets/glyphs/glyph_sdf.gdshader",
			"res://tools/visual_qa/cvd_filter.gdshader", "res://tools/spike/city/shaders/city_post.gdshader"]:
		assert_true(files.has(path), "the scan finds %s" % path)
	for path in files:
		assert_false(path.begins_with("res://addons/"), "addons are not ours: %s" % path)


func test_the_include_declares_the_one_reduce_effects_control() -> void:
	var src := FileAccess.get_file_as_string(INCLUDE)
	assert_true(src.contains("global uniform float reduce_effects;"), "a global uniform, one control for every shader")
	var project := FileAccess.get_file_as_string("res://project.godot")
	assert_true(project.contains("[shader_globals]") and project.contains("reduce_effects={"), "registered in project.godot")
	for fn in ["float rc_live()", "float rc_time(float t)"]:
		assert_true(src.contains(fn), "the include offers %s" % fn)


func test_every_shader_reads_reduce_effects_and_freezes_its_clock() -> void:
	var files := _shaders()
	assert_gt(files.size(), 5, "the game's shaders")
	for path in files:
		var src := FileAccess.get_file_as_string(path)
		# Game shaders always include rc_common; a harness or spike shader under tools/ must
		# when it animates (checked below).
		if not path.begins_with("res://tools/"):
			assert_true(src.contains("#include \"%s\"" % INCLUDE), "%s includes rc_common (declares the global)" % path)
		assert_false(src.contains("uniform float reduce_effects"), "%s reads the global, never a uniform of its own" % path)
		var uses_time := false
		for line in src.split("\n"):
			var code := line.split("//")[0]
			if code.contains("TIME"):
				uses_time = true
				assert_true(code.contains("rc_time(") or code.contains("rc_live()") or code.contains("live_i"),
					"%s: an animated line goes static under reduce effects (%s)" % [path, line.strip_edges()])
		if uses_time:
			assert_true(src.contains("rc_live()") or src.contains("rc_time("), "%s reads reduce_effects" % path)
			assert_true(src.contains("#include \"%s\"" % INCLUDE), "%s animates, so it includes rc_common" % path)
		var sh := load(path) as Shader
		assert_not_null(sh, "%s loads" % path)
	# The jack cover animates on a uniform the script drives (`roll`): it reads it too.
	assert_true(FileAccess.get_file_as_string(SHADER_DIR.path_join("jack_cover.gdshader")).contains("roll * rc_live()"))


func test_the_unused_glow_shader_is_gone() -> void:
	assert_false(FileAccess.file_exists(SHADER_DIR.path_join("glow.gdshader")))


func test_no_script_keeps_a_per_material_reduce_effects() -> void:
	# ART-0 E2: the global reaches every material on rc_common; no script tracks its own copy.
	assert_false(FileAccess.file_exists("res://scripts/ui/fx/shader_reduce.gd"), "the per-material tracker is gone")
	for path in ["res://scripts/autoload/fx.gd", "res://scripts/ui/kit/neon_city.gd", "res://scripts/ui/kit/ui_theme.gd"]:
		var src := FileAccess.get_file_as_string(path)
		assert_false(src.contains("ShaderReduce"), "%s: no ShaderReduce" % path)
		assert_false(src.contains("set_shader_parameter(\"reduce_effects\""), "%s sets no per-material reduce_effects" % path)


func test_toggling_the_setting_changes_the_global() -> void:
	# Ported from art-pass 290ae4c (test_shader_library). The headless renderer keeps no
	# shader globals, so the value Fx sent is read there; a real renderer is asked as well.
	assert_eq(Fx.REDUCE_GLOBAL, &"reduce_effects", "the global rc_common declares")
	Settings.set_reduce_effects(true)
	assert_eq(Fx.shader_reduce, 1.0, "reduce effects on: 1")
	_assert_renderer_global(1.0)
	Settings.set_reduce_effects(false)
	assert_eq(Fx.shader_reduce, 0.0, "off: 0")
	_assert_renderer_global(0.0)
	Settings.set_reduce_effects(true)
	assert_eq(Fx.shader_reduce, 1.0, "on again: 1")


func _assert_renderer_global(expected: float) -> void:
	if DisplayServer.get_name() == "headless":
		return
	assert_eq(float(RenderingServer.global_shader_parameter_get(Fx.REDUCE_GLOBAL)), expected, "the renderer holds it")
