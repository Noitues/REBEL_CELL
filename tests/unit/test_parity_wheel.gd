extends GutTest
## Parity S-WHEEL (M14; designer group ruling 2026-10-05: combat matches the concept; GAPS CMB-02,
## CMB-03, CMB-09, BOSS-04; DECISIONS "Parity fix — combat wheels (designer group ruling)"):
## the slice screens' tone step keeps every slice kind apart (OKLab distance between kinds, the read
## block's contrast on every palette skin, NULL darker than any lit kind, a glyph per kind for
## greyscale), the semantic slice colours never follow a skin, every corp frame wears its rim and
## the wider corp frame, a multi-needle wheel keeps two full blades with short rails (round 2:
## designer, keep main's needles), Meridian's screens read its palette orange (round 2), and the
## card-play preview's label stands clear of the target reticle.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const BOSSES := {&"meridian": &"the_manifest", &"solace": &"renewal_engine", &"halcyon": &"civic_core",
	&"orbital": &"commons_array", &"rebel_cell": &"dispatch_core"}
## The slice families that must read apart by screen colour (Palette.slice_color's groups).
const FAMILIES := [[RC.SliceType.SHIM, RC.SliceType.OVERFLOW], [RC.SliceType.DEFRAG, RC.SliceType.SANDBOX],
	[RC.SliceType.DETOUR, RC.SliceType.HOTFIX], [RC.SliceType.INFECT], [RC.SliceType.TROJAN]]
## Minimum OKLab distance between two families' toned screens (a just-noticeable step is ~0.02).
const MIN_FAMILY_DE := 0.06
## Minimum OKLab distance between two families' program colours (rim, LED, rail tint).
const MIN_PROGRAM_DE := 0.08
## The read block's white over the darkened plate: the large-text WCAG line is 3.0; ask for 4.5.
const MIN_READ_CONTRAST := 4.5
## The disc's read plate darkens the screen by this share (wheel_disc.gdshader `in_plate`, 0.62).
const PLATE_DARK := 0.62
## How much brighter (WCAG contrast) the brightest lit kind's screen is than the empty NULL screen.
const MIN_NULL_CONTRAST := 1.5

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_wheel"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Settings.restore(_settings)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(enemy: StringName = &"the_manifest", combat_seed: int = 5) -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, combat_seed)
	await _frames()
	return scene


## The mean colour of slice kind `row`'s first flipbook frame in the player kit's screen atlas
## (the baked art-pass screens, assets/wheel/screens), sampled every `step` px.
func _screen_mean(img: Image, row: int, step: int = 3) -> Color:
	var meta := WheelKit.meta()
	var frames := int(meta.get("frames", 12))
	var rows := (meta.get("kinds", []) as Array).size()
	var cw := img.get_width() / frames
	var ch := img.get_height() / rows
	var sum := Vector3.ZERO
	var n := 0
	for y in range(row * ch, (row + 1) * ch, step):
		for x in range(0, cw, step):
			var c := img.get_pixel(x, y)
			sum += Vector3(c.r, c.g, c.b)
			n += 1
	sum /= maxf(1.0, float(n))
	return Color(sum.x, sum.y, sum.z)


## The kind's screen as the disc shows it: the atlas mean through the screen gain and the tone step.
func _shown(img: Image, row: int) -> Color:
	var c := _screen_mean(img, row)
	c = Color(c.r * SCREEN_GAIN, c.g * SCREEN_GAIN, c.b * SCREEN_GAIN)
	var t := WheelKit.new().tone(c)
	return Color(clampf(t.r, 0.0, 1.0), clampf(t.g, 0.0, 1.0), clampf(t.b, 0.0, 1.0))


## The disc shader's default screen gain (wheel_disc.gdshader `screen_gain`).
const SCREEN_GAIN := 1.6


func _player_atlas() -> Image:
	var tex := load(WheelKit.SCREENS % "player") as Texture2D
	assert_not_null(tex, "the player kit's screens are baked")
	return tex.get_image() if tex != null else null


# --- CMB-02: slice kinds stay apart ---------------------------------------------------------------

func test_slice_kinds_read_apart_by_screen_colour() -> void:
	var img := _player_atlas()
	if img == null:
		return
	var reps: Array[Color] = []
	for fam: Array in FAMILIES:
		# a family's look is its brightest member's (the one a player most often sees lit)
		var best := Color.BLACK
		for t: int in fam:
			var c := _shown(img, t)
			if Palette.luminance(c) >= Palette.luminance(best):
				best = c
		reps.append(best)
	var bad: Array[String] = []
	for i in reps.size():
		for j in range(i + 1, reps.size()):
			var de := PaletteSkins.delta_e(reps[i], reps[j])
			if de < MIN_FAMILY_DE:
				bad.append("families %s and %s: OKLab dE %.3f < %.2f" % [str(FAMILIES[i]), str(FAMILIES[j]), de, MIN_FAMILY_DE])
	assert_eq(bad, [] as Array[String], "\n".join(bad))


func test_the_tone_step_saturates_and_lifts_the_screens() -> void:
	var img := _player_atlas()
	if img == null:
		return
	for t in [RC.SliceType.SHIM, RC.SliceType.DEFRAG, RC.SliceType.INFECT]:
		var raw := _screen_mean(img, t)
		raw = Color(raw.r * SCREEN_GAIN, raw.g * SCREEN_GAIN, raw.b * SCREEN_GAIN)
		var toned := WheelKit.new().tone(raw)
		assert_gt(toned.s, raw.s, "kind %d: the tone step saturates its screen (CMB-02)" % t)
		assert_gte(Palette.luminance(toned) + 0.0001, Palette.luminance(raw) * 0.9, "kind %d: and never darkens it much" % t)
	# a bright pixel is lifted, a dark one only saturated
	var hi := WheelKit.new().tone(Color(0.8, 0.8, 0.8))
	assert_gt(hi.r, 0.8, "the part over the threshold is lifted (the recipe's bloom)")
	var lo := WheelKit.new().tone(Color(0.1, 0.1, 0.1))
	assert_almost_eq(lo.r, 0.1, 0.0001, "a dark grey is left as it is")


func test_null_reads_empty_against_every_lit_kind() -> void:
	var img := _player_atlas()
	if img == null:
		return
	var null_c := _shown(img, RC.SliceType.NULL)
	var clear := 0
	for fam: Array in FAMILIES:
		var best := 1.0
		for t: int in fam:
			assert_gt(Palette.luminance(_shown(img, t)), Palette.luminance(null_c), "kind %d's screen is brighter than the empty NULL" % t)
			best = maxf(best, Palette.contrast(_shown(img, t), null_c))
		if best >= MIN_NULL_CONTRAST:
			clear += 1
	# TROJAN's screen is a dark one (the art pass's smiley on violet): it is told from NULL by its
	# glyph and its colour (the tests above), so most families, not all, must clear the line; round 2
	# (designer: less colour pop on the player kit) leaves a second dark family under it, still
	# brighter than NULL (asserted above) and told by glyph and colour.
	assert_gte(clear, FAMILIES.size() - 2, "the lit families stand off the NULL screen without colour")


func test_the_read_block_keeps_its_contrast_on_every_skin() -> void:
	var img := _player_atlas()
	if img == null:
		return
	for skin in PaletteSkins.IDS:
		var fg := PaletteSkins.chrome(Palette.TEXT_HI, skin)
		for t in RC.SliceType.values():
			var c := _shown(img, t)
			var plate := Color(c.r * (1.0 - PLATE_DARK), c.g * (1.0 - PLATE_DARK), c.b * (1.0 - PLATE_DARK))
			assert_gte(Palette.contrast(fg, plate), MIN_READ_CONTRAST, "skin %s, kind %d: the read block's value reads" % [skin, t])


func test_every_kind_keeps_its_own_glyph_for_greyscale() -> void:
	var seen := {}
	for t in RC.SliceType.values():
		var g := WheelGlyphs.table().glyph_for(GlyphTableData.key_for_slice_type(t))
		assert_ne(g, &"", "kind %d has a glyph" % t)
		assert_false(seen.has(g), "kind %d's glyph is its own" % t)
		seen[g] = t


func test_program_colours_stay_apart_and_semantic_on_every_skin() -> void:
	var reps: Array[Color] = []
	for fam: Array in FAMILIES:
		reps.append(Palette.slice_color(fam[0]))
	for i in reps.size():
		for j in range(i + 1, reps.size()):
			assert_gte(PaletteSkins.delta_e(reps[i], reps[j]), MIN_PROGRAM_DE, "program colours %d / %d read apart" % [i, j])
	assert_eq(Palette.slice_color(RC.SliceType.DEFRAG), Color("#5CE1FF"), "PROTECT stays #5CE1FF (12s)")
	var scene := await _combat()
	var v: WheelView = scene._player_view
	for skin in PaletteSkins.IDS:
		Settings.set_palette_skin(skin)
		v._sync_disc(v._center(), v._radius(), v.shown_rotation())
		var cols: PackedColorArray = v.disc.mat.get_shader_parameter(&"cols")
		var st: CombatState = scene.engine.state()
		for i in st.player.wheel.slice_count:
			var sl := scene.engine.content(st.player.wheel.slot_slice_ids[i]) as SliceData
			assert_eq(cols[i], Palette.slice_color(sl.slice_type), "skin %s: slot %d keeps its semantic colour" % [skin, i])
	scene.skip_motion()


func test_the_disc_gets_the_tone_and_the_lit_frame() -> void:
	var scene := await _combat()
	var v: WheelView = scene._player_view
	var m := v.disc.mat
	var t := v.kit.tone_params()
	assert_eq(t, WheelKit.TONE[&"player"], "the player wheel takes the player's tone (round 2: per kit)")
	for key in [["screen_sat", "sat"], ["bloom_thresh", "thresh"], ["bloom_gain", "gain"], ["corp_pull", "pull"], ["screen_expo", "expo"]]:
		assert_almost_eq(float(m.get_shader_parameter(StringName(key[0]))), float(t[key[1]]), 0.0001, "the disc gets %s" % key[0])
	assert_almost_eq(float(m.get_shader_parameter(&"frame_tint")), WheelKit.PLAYER_FRAME_TINT, 0.0001, "the player's frame is lit in its class accent")
	assert_eq(int(m.get_shader_parameter(&"rim_kind")), 0, "the player's frame wears no corp rim")
	assert_almost_eq(float(m.get_shader_parameter(&"r_frame")), WheelKit.R_FRAME_PLAYER, 0.0001)
	scene.skip_motion()


# --- CMB-03: the corp kit ---------------------------------------------------------------------

func test_every_corp_frame_wears_its_rim() -> void:
	for corp: StringName in BOSSES:
		var scene := await _combat(BOSSES[corp])
		var foe: WheelView = null
		for w: WheelView in scene._views():
			if w.combatant != null and not w.combatant.is_player:
				foe = w
		assert_not_null(foe, "%s: the boss has a wheel" % corp)
		if foe == null:
			continue
		var m := foe.disc.mat
		assert_eq(foe.kit.kit_name(), corp, "%s wears its own kit" % corp)
		assert_eq(int(m.get_shader_parameter(&"rim_kind")), WheelKit.THEMES.find(corp), "%s: its corp rim (d4corp.corp_rim)" % corp)
		assert_almost_eq(float(m.get_shader_parameter(&"r_frame")), WheelKit.R_FRAME_CORP, 0.0001, "%s: the wider corp frame" % corp)
		assert_almost_eq(foe.frame_master(), WheelKit.R_FRAME_CORP + WheelFace.THREAT_DEPTH, 0.0001, "%s: blades and HP sit past the corp frame and the threat ring" % corp)
		assert_almost_eq(float(m.get_shader_parameter(&"frame_tint")), 0.0, 0.0001, "%s: the rim, not the player's wash" % corp)
		scene.skip_motion()
		scene.get_parent().queue_free()
		await _frames(2)
	# an elite's collar sits beyond its corp frame
	var scene2 := await _combat(&"port_authority")
	for w: WheelView in scene2._views():
		if w.combatant != null and not w.combatant.is_player:
			assert_true(w.kit.is_elite, "the Port Authority is an elite")
			assert_almost_eq(w.frame_master(), WheelKit.R_FRAME_CORP + WheelKit.ELITE_COLLAR, 0.0001, "the elite collar sits beyond the corp frame")
	scene2.skip_motion()


# --- BOSS-04 (round 2: designer, keep main's needles) ------------------------------------------

func test_a_second_needle_keeps_its_full_blade_with_short_rails() -> void:
	var scene := await _combat(&"renewal_engine")
	var foe: WheelView = null
	for w: WheelView in scene._views():
		if w.combatant != null and not w.combatant.is_player:
			foe = w
	var wheel := foe._shown().wheel
	var keep := wheel.pointer_ticks
	wheel.pointer_ticks = PackedInt32Array([0, 10])
	foe._sync_disc(foe._center(), foe._radius(), foe.shown_rotation())
	var spot := foe.pointer_spot(1) - foe.global_center()
	assert_almost_eq(spot.length(), foe.window_radius(), 0.5, "needle 2 reads in a full blade's window, as needle 1")
	assert_almost_eq(float(foe.disc.mat.get_shader_parameter(&"rail_half")), WheelFace.RAIL_HALF_MULTI, 0.0001, "a multi-needle wheel's rails are short (d4corp)")
	wheel.pointer_ticks = PackedInt32Array([0])
	foe._sync_disc(foe._center(), foe._radius(), foe.shown_rotation())
	assert_almost_eq(float(foe.disc.mat.get_shader_parameter(&"rail_half")), WheelFace.RAIL_HALF, 0.0001)
	wheel.pointer_ticks = keep
	scene.skip_motion()


# --- round 2: Meridian reads its palette colour ---------------------------------------------------

## How far (degrees) the toned Meridian screens' hue may sit from Palette.CORP_MERIDIAN's.
const MERIDIAN_HUE_TOL := 15.0
## The least luminance (WCAG) of a toned Meridian screen (round 1 read too dark: ~0.04).
const MERIDIAN_MIN_LUM := 0.06


func test_meridian_screens_read_its_palette_orange() -> void:
	var tex := load(WheelKit.SCREENS % "meridian") as Texture2D
	assert_not_null(tex)
	if tex == null:
		return
	var img := tex.get_image()
	var kit := WheelKit.new()
	kit.theme = WheelKit.THEMES.find(&"meridian")
	kit.accent = Palette.corp_color(&"meridian")
	var want := Palette.CORP_MERIDIAN.h * 360.0
	for t in [RC.SliceType.SHIM, RC.SliceType.DEFRAG, RC.SliceType.HOTFIX]:
		var c := _screen_mean(img, t)
		c = kit.tone(Color(c.r * SCREEN_GAIN, c.g * SCREEN_GAIN, c.b * SCREEN_GAIN))
		c = Color(clampf(c.r, 0.0, 1.0), clampf(c.g, 0.0, 1.0), clampf(c.b, 0.0, 1.0))
		var dh := absf(wrapf(c.h * 360.0 - want, -180.0, 180.0))
		assert_lte(dh, MERIDIAN_HUE_TOL, "kind %d: the screen's hue %.0f sits by Meridian's %.0f" % [t, c.h * 360.0, want])
		assert_gte(Palette.luminance(c), MERIDIAN_MIN_LUM, "kind %d: and is not dark" % t)


# --- CMB-09: the card-play preview --------------------------------------------------------------

func test_the_preview_label_stands_clear_of_the_reticle() -> void:
	var scene := await _combat()
	var foe: WheelView = null
	for w: WheelView in scene._views():
		if w.combatant != null and not w.combatant.is_player:
			foe = w
	assert_not_null(foe.attachments, "the enemy wheel has its attachments")
	if foe.attachments == null:
		return
	var ov: CardPreviewOverlay = foe.attachments.preview
	var bad: Array[String] = []
	for s in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(s)
		await _frames(2)
		var center := foe.attachments.center()
		var rim := foe.attachments.rim()
		var blockers := ov.label_blockers()
		assert_gt(blockers.size(), 4, "scale %.1f: the reticle's arcs, the nudge buttons and the HP row are blockers" % s)
		# the landing angles a turn of the enemy wheel can show (its slice midlines, upper half: the
		# side where the label meets the reticle and the nudge buttons)
		for step in 12:
			var a := -PI + PI * (step + 0.5) / 12.0
			var text := tr("%d LANDS HERE") % 1
			var box := ov.label_box(center, a, ov._needle_label_distances(rim, a, text), text)
			for b in blockers:
				if b.intersects(box):
					bad.append("scale %.1f, angle %.0f: the label %s meets %s" % [s, rad_to_deg(a), box, b])
	assert_eq(bad, [] as Array[String], "\n".join(bad))
	scene.skip_motion()
