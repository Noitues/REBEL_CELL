extends GutTest
## ART-1 1B, the material kit (DECISIONS "Art direction — ART-1 1B material kit"; ART_BIBLE v2
## §1.2, §1.3, §5.3-5.4, §6.3-6.4): every component's states, the reduce-effects end states,
## headless never waits, the pencil lint rule, the bits' precomputed arrivals, every shader's
## reduce_effects global and every material's VfxTier.

const KIT_SHADERS := "res://shaders/kit"
const INCLUDE := "res://shaders/lib/rc_common.gdshaderinc"
const LAB_SCRIPT := "res://tools/design_lab/motion_lab.gd"

var _reduce: bool = false


func before_each() -> void:
	_reduce = Settings.reduce_effects
	Motion.force_live = false
	StickerSweepQueue.reset()


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	StickerSweepQueue.reset()


## Sets Settings.reduce_effects to `reduce` (and Fx with it).
func _effects(reduce: bool) -> void:
	if Settings.reduce_effects != reduce:
		Settings.set_reduce_effects(reduce)
	Fx.apply_settings()


# --- The register: shaders, tiers, motion entries ------------------------------------------

func test_every_kit_shader_reads_the_reduce_effects_global_and_freezes_its_clock() -> void:
	var files := DirAccess.get_files_at(KIT_SHADERS)
	var shaders: Array[String] = []
	for f in files:
		if f.ends_with(".gdshader"):
			shaders.append(KIT_SHADERS.path_join(f))
	assert_gt(shaders.size(), 8, "the kit's shaders")
	var registered := KitMaterials.shader_paths()
	for path in shaders:
		assert_true(registered.has(path), "%s is in the kit register (it has a material and a tier)" % path)
		var src := FileAccess.get_file_as_string(path)
		assert_true(src.contains("#include \"%s\"" % INCLUDE), "%s includes rc_common (the global)" % path)
		assert_false(src.contains("uniform float reduce_effects"), "%s declares no reduce_effects of its own" % path)
		for line in src.split("\n"):
			var code := line.split("//")[0]
			if code.contains("TIME"):
				assert_true(code.contains("rc_time(") or code.contains("rc_live()"), "%s: animated line goes static under reduce effects (%s)" % [path, line.strip_edges()])
		assert_not_null(load(path) as Shader, "%s loads" % path)
	for path in registered:
		assert_true(FileAccess.file_exists(path), "%s exists" % path)


func test_every_material_has_a_vfx_tier_and_its_motions_are_table_entries_with_lab_demos() -> void:
	var demos: Dictionary = (load(LAB_SCRIPT) as GDScript).get_script_constant_map()["DEMOS"]
	for k in KitMaterials.ALL:
		var m: Dictionary = KitMaterials.ALL[k]
		assert_true(VfxTier.valid(int(m["tier"])), "%s has a VfxTier" % k)
		assert_true(ClassDB.class_exists(m["component"]) or _global_class(m["component"]), "%s's component %s exists" % [k, m["component"]])
	for id in KitMaterials.motion_ids():
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		var e := Motion.entry(id)
		assert_not_null(e, "%s has a ui_motion.tres entry" % id)
		if e != null:
			assert_true(VfxTier.valid(e.tier), "%s has a tier" % id)
			if e.tier == VfxTier.T2:
				assert_true(e.duration <= VfxTier.MAX_SECONDS[VfxTier.T2] + 0.0001, "%s fits T2's 0.6 s" % id)
		assert_true(demos.has(id) and String((demos[id] as Array)[0]) == "kit", "%s has a kit demo in the motion lab" % id)


func _global_class(n: String) -> bool:
	for c in ProjectSettings.get_global_class_list():
		if String(c["class"]) == n:
			return true
	return false


func test_the_pencil_and_vinyl_tokens_are_the_bible_values() -> void:
	assert_eq(Palette.PENCIL_PLAN, Color("#FFE200"), "§1.2 yellow = plan / valid")
	assert_eq(Palette.PENCIL_THREAT, Color("#FF1C2C"), "§1.2 red = threat / invalid / loss")
	assert_eq(GreasePencilMark.ink_color(GreasePencilMark.Ink.PLAN), Palette.PENCIL_PLAN)
	assert_eq(GreasePencilMark.ink_color(GreasePencilMark.Ink.THREAT), Palette.PENCIL_THREAT)
	assert_almost_eq(Palette.HOLO_SCRIM.a, 0.88, 0.001, "§1.2 the holo's scrim")


# --- Vinyl sticker ------------------------------------------------------------------------

func _sticker(text: String = "SEND IT") -> VinylSticker:
	var s := VinylSticker.new()
	s.text = text
	add_child_autofree(s)
	return s


func test_a_word_sticker_builds_its_die_cut_body_round_the_lettering() -> void:
	var s := _sticker()
	assert_gt(s.body_rect.size.x, 100.0, "the body spans the word")
	assert_true(Rect2(Vector2.ZERO, s.size).encloses(s.body_rect), "room round the body for the shadow")
	assert_eq(s.pivot_offset, s.body_rect.get_center(), "turns and scales about its body")
	assert_almost_eq(s.gloss_k, 0.22, 0.0001, "gloss 0.22 at rest (round 19 gloss_k)")
	assert_true(s.art_texture() != null, "the art is baked into a texture")


func test_sticker_states_show_their_end_states_at_once_headless() -> void:
	var s := _sticker()
	s.rest_curl = 0.0
	s.set_state(VinylSticker.State.HOVER)
	assert_false(s.motion_running(), "headless never waits")
	assert_almost_eq(s.scale.x, Motion.amplitude(&"sticker_hover"), 0.001, "hover grows to the entry's scale")
	assert_almost_eq(s.lift, VinylSticker.HOVER_LIFT, 0.001, "hover lifts 0.6")
	assert_eq(s.peel_back, 1.0, "hover peels the corner back")
	s.set_state(VinylSticker.State.PRESSED)
	assert_almost_eq(s.scale.y, Motion.amplitude(&"sticker_press"), 0.001, "pressed squashes y")
	assert_almost_eq(s.scale.x, VinylSticker.PRESS_X, 0.001, "and x to 1.04")
	assert_almost_eq(s.lift, 0.0, 0.001, "the shadow snaps in")
	s.set_state(VinylSticker.State.DISABLED)
	assert_almost_eq(s.grey, 1.0, 0.001, "disabled: greyscale vinyl")
	assert_almost_eq(s.modulate.a, VinylSticker.DISABLED_ALPHA, 0.001, "at 80 %")
	s.set_state(VinylSticker.State.REST)
	assert_eq(s.scale, Vector2.ONE)
	assert_almost_eq(s.grey, 0.0, 0.001)


func test_slap_peel_and_dissolve_end_states_under_reduce_effects() -> void:
	Motion.force_live = true
	_effects(false)
	var s := _sticker()
	s.tilt_deg = 5.0
	_effects(true)
	assert_eq(s.slap(), 0.0, "reduce effects: no slap")
	assert_eq(s.scale, Vector2.ONE, "the end state: rest scale")
	assert_almost_eq(s.rotation_degrees, 5.0, 0.001, "at its tilt")
	assert_true(s.visible and is_equal_approx(s.modulate.a, 1.0), "shown")
	assert_eq(s.peel(), 0.0, "reduce effects: no peel")
	assert_false(s.visible, "the end state: gone")
	s.slap()
	assert_eq(s.dissolve(), 0.0, "reduce effects: no dissolve")
	assert_false(s.visible, "the end state: gone")
	assert_eq(s.sweep(), 0.0, "no sweep")
	assert_almost_eq(s.gloss_k, VinylSticker.GLOSS_REST, 0.0001)


func test_a_running_slap_and_peel_end_with_one_press_at_their_end_states() -> void:
	Motion.force_live = true
	_effects(false)
	var s := _sticker()
	s.tilt_deg = -4.0
	assert_gt(s.slap(), 0.0, "the slap plays")
	assert_true(s.motion_running())
	assert_true(s.is_in_group(MotionSkip.GROUP), "a press that ends motion ends it (MotionSkip)")
	assert_gt(s.scale.x, 1.0, "it starts big (1.24x)")
	s.complete_motion()
	assert_false(s.motion_running())
	assert_eq(s.scale, Vector2.ONE)
	assert_almost_eq(s.rotation_degrees, -4.0, 0.001)
	assert_gt(s.peel(), 0.0, "the peel plays")
	var from := s.position
	s.complete_motion()
	assert_false(s.visible, "peeled off")
	assert_eq(s.position, from, "its place is kept for the next slap")
	assert_almost_eq(s.fold, Motion.amplitude(&"sticker_peel"), 0.001, "folded to the entry's depth")


func test_one_gloss_sweep_on_one_sticker_at_a_time() -> void:
	var a := _sticker("LEAVE")
	var b := _sticker("OURS")
	a.ambient_sweep = true
	b.ambient_sweep = true
	assert_eq(StickerSweepQueue.size(), 2)
	assert_true(StickerSweepQueue.take_turn(a, 0), "the first to join sweeps first")
	assert_false(StickerSweepQueue.take_turn(b, 0), "never two at once")
	StickerSweepQueue.done(a, 100, 1.4)
	assert_false(StickerSweepQueue.take_turn(a, 200), "the rest between sweeps")
	assert_false(StickerSweepQueue.take_turn(b, 10000), "only the primary sweeps (designer 2026-10-06): never b")
	assert_true(StickerSweepQueue.take_turn(a, 10000), "the primary again after its period")


func test_the_verb_sticker_sits_over_its_system_word_which_stays_readable() -> void:
	var w := SystemWordSticker.new()
	w.size = Vector2(300, 92)
	add_child_autofree(w)
	w.set_verb("SEND IT", VinylSticker.Fill.HOLO)
	var body := w.sticker.get_rect()
	var font := Palette.mono()
	var px := UiTheme.font_px(w.word_step)
	var word_bottom := font.get_ascent(px) + UiTheme.SP_S
	var sticker_top := w.sticker.position.y + w.sticker.body_rect.position.y
	assert_gt(sticker_top, word_bottom * 0.5, "the sticker leaves the system word's upper half readable")
	assert_true(Rect2(Vector2.ZERO, w.size).intersects(Rect2(w.sticker.position + w.sticker.body_rect.position, w.sticker.body_rect.size)), "slapped over the panel")
	assert_almost_eq(w.sticker.rotation_degrees, SystemWordSticker.STICKER_TILT_DEG, 0.001, "at an angle")
	assert_true(body.size.x > 0.0)


# --- CRT terminal -------------------------------------------------------------------------

func test_the_crt_panel_takes_its_accent_and_the_bible_look() -> void:
	var p := CrtTerminalPanel.new()
	p.size = Vector2(300, 60)
	add_child_autofree(p)
	var accents := {CrtTerminalPanel.Accent.CELL: Palette.NET_CYAN, CrtTerminalPanel.Accent.FIRMWARE: Palette.CELL_ACID,
		CrtTerminalPanel.Accent.SCHEMATICS: Palette.RESIST_GOLD, CrtTerminalPanel.Accent.DISPATCH: Palette.HARM}
	for k in accents:
		p.accent_kind = k
		assert_eq(p.accent(), accents[k])
	p.accent_kind = CrtTerminalPanel.Accent.CORP
	p.corp_color = Palette.CORP_MERIDIAN
	assert_eq(p.accent(), Palette.CORP_MERIDIAN, "the corp colour inside corp Terminals")
	assert_eq(CrtTerminalPanel.SCAN_PX, 3.0, "3 px scanlines")
	assert_almost_eq(CrtTerminalPanel.SCAN_STRENGTH, 0.10, 0.0001, "at 10 %")
	assert_almost_eq(CrtTerminalPanel.HEX_ALPHA, 0.06, 0.0001, "hex dump 6 %")
	assert_eq(p.label.get_theme_font(&"font"), Palette.mono(), "Share Tech Mono")


func test_crt_text_types_on_behind_the_prompt_and_shows_whole_headless() -> void:
	var p := CrtTerminalPanel.new()
	p.size = Vector2(400, 60)
	add_child_autofree(p)
	assert_eq(p.type_on("RAM 5/12"), 0.0, "headless never waits")
	assert_eq(p.label.text, "> RAM 5/12", "the > prompt")
	assert_false(p.typing())
	var at := p.caret_position()
	assert_gt(at.x, p.label.position.x + 40.0, "the caret sits after the text")


# --- Grease pencil ------------------------------------------------------------------------

func _mark() -> GreasePencilMark:
	var m := GreasePencilMark.new()
	add_child_autofree(m)
	m.add_stroke(PencilShapes.hand_circle(Vector2(100, 100), Vector2(40, 30), 3))
	return m


func test_pencil_writes_on_and_wipes_by_trimming_points_never_alpha() -> void:
	Motion.force_live = true
	_effects(false)
	var m := _mark()
	var full := (m.get_child(1) as Line2D).points.size()
	assert_gt(full, 20, "a resampled circle")
	assert_gt(m.write_on(), 0.0, "it writes on")
	var line := m.get_child(1) as Line2D
	await BoundedWait.until(get_tree(), func() -> bool: return line.points.size() > 1, 2.0)
	assert_lt(line.points.size(), full, "written part only: points trimmed")
	assert_eq(m.modulate.a, 1.0, "never an alpha fade")
	m.complete_motion()
	assert_eq(line.points.size(), full, "written whole")
	assert_gt(m.wipe(), 0.0, "it wipes")
	m.complete_motion()
	assert_eq(line.points.size(), 0, "wiped: no points left")
	assert_eq(m.modulate.a, 1.0, "still never alpha")
	assert_true(m.is_in_group(GreasePencilMark.GROUP), "the lint sees it")


func test_pencil_end_states_under_reduce_effects_and_headless() -> void:
	var m := _mark()
	assert_eq(m.write_on(), 0.0, "headless: written whole at once")
	assert_almost_eq(m.progress, 1.0, 0.0001)
	Motion.force_live = true
	_effects(true)
	assert_eq(m.wipe(), 0.0, "reduce effects: wiped at once")
	assert_almost_eq(m.wiped_share, 1.0, 0.0001)
	var w := GreasePencilWord.new()
	add_child_autofree(w)
	assert_eq(w.write_on(), 0.0)
	assert_eq(w.shown_to, float(w.text.length()), "the word is whole")


func test_pencil_look_uniforms_width_dashes_and_shadow() -> void:
	var m := _mark()
	m.dashed = true
	var line := m.get_child(1) as Line2D
	var shadow := m.get_child(0) as Line2D
	assert_between(line.width, 8.0, 10.0, "§6.3 width 8-10")
	assert_eq(line.begin_cap_mode, Line2D.LINE_CAP_ROUND, "round caps")
	assert_true(bool((line.material as ShaderMaterial).get_shader_parameter(&"dashed")), "dashed = what-if")
	assert_eq(shadow.position, GreasePencilMark.SHADOW_OFFSET, "the offset under-shadow")
	assert_eq(int((shadow.material as ShaderMaterial).get_shader_parameter(&"mode")), 1, "drawn in shadow mode")


func test_pencil_shapes_trim_and_snap_to_a_real_edge() -> void:
	var pts := PackedVector2Array([Vector2(0, 0), Vector2(100, 0)])
	var half := PencilShapes.trim(pts, 0.0, 50.0)
	assert_eq(half[half.size() - 1], Vector2(50, 0), "trimmed at its length")
	var r := PencilShapes.resample(pts, 10.0)
	assert_eq(r.size(), 11)
	var edge := PackedVector2Array([Vector2(0, 50), Vector2(200, 50)])
	var snapped := PencilShapes.snap_to(PackedVector2Array([Vector2(20, 40), Vector2(80, 70)]), edge)
	for p in snapped:
		assert_almost_eq(p.y, 50.0, 0.001, "on the edge: the mark says what the rules will do")
	var a := PencilShapes.hand_circle(Vector2.ZERO, Vector2(10, 10), 4)
	var b := PencilShapes.hand_circle(Vector2.ZERO, Vector2(10, 10), 4)
	assert_eq(a, b, "the same seed draws the same hand circle")


# --- The pencil lint rule -----------------------------------------------------------------

func test_pencil_lint_finds_ui_over_a_stroke_and_ui_layers_above_the_pencil() -> void:
	var root := Control.new()
	add_child_autofree(root)
	var pencil_layer := CanvasLayer.new()
	pencil_layer.layer = 10
	root.add_child(pencil_layer)
	var m := GreasePencilMark.new()
	pencil_layer.add_child(m)
	m.add_stroke(PackedVector2Array([Vector2(100, 100), Vector2(300, 100)]))
	var under := Label.new()
	under.text = "under"
	under.position = Vector2(150, 90)
	root.add_child(under)
	assert_eq(PencilLint.violations(root).size(), 0, "UI under the pencil's layer is fine")
	var bare := Control.new()
	bare.position = Vector2(90, 80)
	bare.size = Vector2(300, 60)
	pencil_layer.add_child(bare)
	assert_eq(PencilLint.violations(root).size(), 0, "a bare layout node draws nothing")
	var over := Panel.new()
	over.position = Vector2(200, 90)
	over.size = Vector2(40, 30)
	pencil_layer.add_child(over)
	var v := PencilLint.violations(root)
	assert_eq(v.size(), 1, "a panel drawn over the stroke")
	assert_eq(String(v[0]["rule"]), "cover")
	over.position = Vector2(200, 300)
	assert_eq(PencilLint.violations(root).size(), 0, "away from the stroke it is fine")
	var hud := CanvasLayer.new()
	hud.layer = 20
	root.add_child(hud)
	var top := Label.new()
	top.text = "HUD"
	hud.add_child(top)
	v = PencilLint.violations(root)
	assert_eq(v.size(), 1, "a UI layer above the pencil breaks the layer order")
	assert_eq(String(v[0]["rule"]), "layer")
	hud.layer = PencilLint.CURSOR_LAYER_MIN
	assert_eq(PencilLint.violations(root).size(), 0, "only the cursor may sit above the pencil")


# --- Binary bits --------------------------------------------------------------------------

func test_bits_go_round_the_rim_never_across_the_face() -> void:
	var c := Vector2(0, 0)
	var r := 100.0
	var s := Vector2.from_angle(deg_to_rad(200)) * r
	var t := Vector2.from_angle(deg_to_rad(330)) * r
	var ctrl := BitsPath.control_point(s, t, c, r)
	assert_almost_eq(ctrl.length(), BitsPath.RIM_CONTROL * r, 0.01, "control point at 1.5 x R_out")
	for i in 11:
		var p := BitsPath.at(s, ctrl, t, i / 10.0)
		assert_gt(p.length(), r * 0.85, "round the rim, never across the face, at t=%.1f" % (i / 10.0))
	var opposite := BitsPath.control_point(Vector2(r, 0), Vector2(-r, 0), c, r)
	assert_almost_eq(opposite.length(), BitsPath.RIM_CONTROL * r, 0.01, "opposite ends still bow round the rim")


func test_bit_arrivals_are_precomputed_deterministic_and_left_to_right() -> void:
	var starts := BitsPath.points_in_rect(Rect2(0, 0, 200, 40), 24)
	assert_eq(starts.size(), 24)
	var a := BitsPath.plan(starts, Vector2(500, 0), 0.5, 0.12, 9)
	var b := BitsPath.plan(starts, Vector2(500, 0), 0.5, 0.12, 9)
	assert_eq(BitsPath.arrivals(a), BitsPath.arrivals(b), "same seed, same arrivals")
	var left := INF
	var right := -INF
	for bit in a:
		assert_almost_eq(float(bit["arrive"]), float(bit["delay"]) + float(bit["flight"]), 0.0001)
		var x: float = (bit["start"] as Vector2).x
		if x <= 10.0:
			left = minf(left, float(bit["delay"]))
		if x >= 190.0:
			right = maxf(right, float(bit["delay"]))
	assert_almost_eq(left, 0.0, 0.0001, "the left cells go first")
	assert_almost_eq(right, 0.12, 0.0001, "the right ones last (delay proportional to x)")


func test_bits_burst_returns_arrivals_and_never_flies_under_reduce_effects() -> void:
	var bits := BinaryBits.new()
	add_child_autofree(bits)
	var src := BitsPath.points_in_rect(Rect2(0, 0, 100, 20), 30)
	var none := bits.burst(src, Vector2(400, 0), Palette.CELL_PINK)
	assert_eq(none.size(), 30, "an arrival per bit")
	for t in none:
		assert_eq(t, 0.0, "headless: every arrival at once (the end state)")
	assert_eq(bits.active_bursts(), 0, "no bits fly")
	Motion.force_live = true
	_effects(false)
	var arr := bits.burst(src, Vector2(400, 0), Palette.CELL_PINK, Vector2.ZERO, 0.0, 2)
	assert_gt(arr[arr.size() - 1], 0.0, "the view schedules on these")
	assert_eq(bits.active_bursts(), 1)
	assert_eq(bits.pool_size(), 1, "one pooled emitter per burst")
	bits.complete_motion()
	assert_eq(bits.active_bursts(), 0)
	bits.use_cpu_fallback = true
	var many := BitsPath.points_in_rect(Rect2(0, 0, 100, 20), 60)
	assert_eq(bits.burst(many, Vector2(400, 0), Palette.CELL_PINK).size(), BinaryBits.CPU_MAX, "the CPU fallback caps at 44")
	_effects(true)
	var reduced := bits.burst(src, Vector2(400, 0), Palette.CELL_PINK)
	assert_eq(reduced[reduced.size() - 1], 0.0, "reduce effects: no particles, the end state at once")


# --- Holo, paper, spill, toon -------------------------------------------------------------

func test_the_holo_panel_drops_its_rgb_split_under_reduce_effects() -> void:
	_effects(false)
	var h := DecryptedHoloPanel.new()
	h.size = Vector2(300, 200)
	add_child_autofree(h)
	var glass := h.get_child(1, true) as Control
	var mat := glass.material as ShaderMaterial
	assert_almost_eq(float(mat.get_shader_parameter(&"split_px")), DecryptedHoloPanel.SPLIT_PX, 0.001, "+-2 px on the edge")
	assert_almost_eq(float(mat.get_shader_parameter(&"tint_share")), 0.78, 0.001, "corp tint at about 78 %")
	assert_almost_eq(float(mat.get_shader_parameter(&"scan_px")), 4.0, 0.001, "4 px scanlines")
	_effects(true)
	assert_almost_eq(float(mat.get_shader_parameter(&"split_px")), 0.0, 0.001, "reduce effects: no RGB split")


func test_the_corp_paper_types_its_fields_and_stamps() -> void:
	var p := CorpPaperPanel.new()
	p.size = Vector2(400, 240)
	add_child_autofree(p)
	var l := p.add_field("TARGET", "sector 7")
	assert_eq(l.text, "TARGET: sector 7")
	assert_eq(l.get_theme_font(&"font"), CorpPaperPanel.courier(), "Courier Prime fields (mono until it ships)")
	assert_eq(p.stamp, "CLASSIFIED", "an Anton stamp in its slot")


func test_light_spill_breathes_only_while_effects_play_and_packs_3d_sources() -> void:
	var s := LightSpill.new()
	add_child_autofree(s)
	assert_eq(s.breathe_at(0.7), 1.0, "headless: steady")
	var u := LightSpill.uniforms_3d([{"position": Vector3(1, 2, 3), "radius": 5.0, "color": Palette.CELL_PINK, "intensity": 2.0}])
	assert_eq(int(u["spill_count"]), 1)
	assert_eq((u["spill_lights"] as Array).size(), LightSpill.MAX_3D, "padded to the shader's arrays")
	assert_eq((u["spill_lights"] as Array)[0], Vector4(1, 2, 3, 5))
	assert_eq((u["spill_colors"] as Array)[0].w, 2.0)


func test_the_toon_material_has_three_bands_an_ink_hull_and_spill_uniforms() -> void:
	var m := ToonInkMaterial.make(Palette.NIGHT_BLOCK_LIT)
	assert_not_null(m.next_pass, "the ink hull pass")
	assert_eq((m.next_pass as ShaderMaterial).shader, ToonInkMaterial.HULL)
	assert_eq(ToonInkMaterial.band_of(0.9), 2)
	assert_eq(ToonInkMaterial.band_of(0.3), 1)
	assert_eq(ToonInkMaterial.band_of(0.05), 0, "three hard bands")
	var names: Array[String] = []
	for u in ToonInkMaterial.TOON.get_shader_uniform_list():
		names.append(String(u["name"]))
	for n in ["spill_lights", "spill_colors", "spill_count", "band_hi", "band_lo", "tone_jitter", "haze_color"]:
		assert_true(names.has(n), "1D's uniform %s" % n)
	ToonInkMaterial.set_spill(m, [{"position": Vector3.ZERO, "radius": 3.0}])
	assert_eq(int(m.get_shader_parameter(&"spill_count")), 1)
	assert_null(ToonInkMaterial.make(Palette.NIGHT_BLOCK_LIT, 0.0).next_pass, "no ink when asked")
