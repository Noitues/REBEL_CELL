extends GutTest
## B2 (M14 art-direction integration review; DECISIONS "B2 — combat composition (integration
## review)"): the fight composed as the concepts (round 41 combat_typical_v4): the perspective
## close-up camera with an open street, haze toward the night sky (D1); the hub an emblem and a
## tiny name, shield and the rest as chips (D2); no lime reticle while aiming (D4); the aimed
## play's result in the HP result chips, underlined in yellow wax that writes on and wipes, never
## fades (designer 2026-10-06); the fanned hand (D15); EXECUTE washed out under SEND IT (D16);
## the Heat corner chip (Q1 c); key hints in tooltips, key letters with an ink keyline (Q2, B1a
## Q2); the Settings icon chip; the tutorial a cyan-edged terminal.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_b2_combat"
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


func _several_target_card(scene: Control) -> int:
	for i in scene.engine.state().hand.size():
		if CardTargeting.options(scene.engine.resolver, scene.engine.state(), i).size() > 1:
			return i
	return -1


# --- D1: the perspective close-up ------------------------------------------------------------------

func test_every_close_up_is_a_low_perspective_view_with_an_open_street() -> void:
	var cfg := CityView3D.CONFIG
	assert_between(cfg.backdrop_close_pitch_deg, 6.0, 10.0, "D1: 6 to 10 degrees above the street")
	assert_between(cfg.backdrop_close_fov_deg, 39.6, 54.4, "D1: a 35 to 50 mm lens (horizontal field on a 36 mm frame)")
	assert_between(cfg.backdrop_haze_k, 0.15, 0.2, "D1: depth haze 15 to 20 %")
	var size := Vector2(1280, 720)
	for corp: StringName in [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]:
		var shot := BackdropCatalog.city_shot(cfg, BackdropCatalog.place(corp, true, false), {}, size)
		var cam: CityIsoCamera = shot["camera"]
		assert_true(cam.perspective(), "%s boss: a perspective close-up (designer 2026-10-06)" % corp)
		if String(shot["focus"]) == "hq":
			assert_almost_eq(cam.pitch_deg, cfg.backdrop_close_pitch_deg, 0.001, "%s: the street-level pitch" % corp)
			assert_true(shot.has("subject"), "%s: the subject's box (for the open street)" % corp)
			var box: AABB = shot["subject"]
			var px := BackdropCatalog.projected_box(cam, box)
			assert_true(px.has_area(), "%s: the landmark in front of the eye" % corp)
			var frame: Rect2 = cfg.backdrop_hq_frame_by_corp.get(corp, cfg.backdrop_hq_frame)
			var want := Rect2(frame.position * size, frame.size * size)
			assert_true(px.size.x <= want.size.x * 1.05 and px.size.y <= want.size.y * 1.05, "%s: fitted into its frame (%s in %s)" % [corp, px, want])
			assert_almost_eq(px.get_center().x, want.get_center().x, want.size.x * 0.1, "%s: centred between the wheels" % corp)
	var look := BackdropCatalog.city_look(cfg, "hq")
	assert_eq(look["haze"], cfg.backdrop_sky, "D1: the haze goes toward the night sky colour")
	assert_eq(float(look["haze_k"]), cfg.backdrop_haze_k)
	assert_true(bool(look["night"]), "the lit night look keeps the round 11 rain")


func test_the_view_cut_clears_only_what_hides_the_subject() -> void:
	var cfg := CityView3D.CONFIG
	var box := AABB(Vector3(-15, 0, -15), Vector3(30, 40, 30))
	var cam := BackdropCatalog.fit_box(cfg, box, cfg.backdrop_site_frame, cfg.backdrop_site_ortho, Vector2(1280, 720), cfg.backdrop_close_pitch_deg)
	var cut := BackdropCatalog.view_cut(cfg, cam, box)
	var eye := cam.eye()
	var e2 := Vector2(eye.x, eye.z)
	var sub := Vector2(box.get_center().x, box.get_center().z)
	var mid := e2.lerp(sub, 0.5)
	assert_true(BackdropCatalog.occludes(mid, 200.0, cut), "a tower between the eye and the subject gives way")
	assert_false(BackdropCatalog.occludes(mid, 0.5, cut), "a low roof under the sight line stays")
	var side := mid + (cut["right"] as Vector2) * 400.0
	assert_false(BackdropCatalog.occludes(side, 200.0, cut), "the city to the sides stays")
	assert_false(BackdropCatalog.occludes(sub, 200.0, cut), "the subject stands")
	assert_false(BackdropCatalog.occludes(e2 - (cut["fwd"] as Vector2) * 20.0, 200.0, cut), "behind the eye: not its business")
	var v := CityView3D.new()
	v.set_view_cut(BackdropCatalog.occludes.bind(cut), str(cut))
	assert_true(v.in_view_cut(mid, 200.0), "the city view skips it")
	assert_false(v.in_view_cut(sub, 200.0))
	v.set_view_cut(Callable())
	assert_false(v.in_view_cut(mid, 200.0), "no cut: every building is built")
	assert_true(v.outer_ground_shown(), "the asphalt plane round the city shows by default")
	v.show_outer_ground(false)
	assert_false(v.outer_ground_shown(), "a close-up hides it (the sky past the city's edge)")
	v.free()
	var src := FileAccess.get_file_as_string("res://scripts/ui/arena/combat_backdrop.gd")
	assert_true(src.contains("city.show_outer_ground(not cam.perspective())"), "the perspective close-up hides it")


# --- D4: no lime reticle while aiming ----------------------------------------------------------------

func test_the_lime_brackets_never_draw_while_a_card_is_aimed() -> void:
	var scene := await _combat()
	var ev: WheelView = scene._enemy_views.values()[0]
	assert_true(ev.highlighted, "the enemy is the target")
	assert_false(ev.reticle_shown, "one wheel to hit: no brackets (lime = focus only)")
	assert_false(ev.reticle_visible())
	ev.reticle_shown = true  # two wheels to choose between
	assert_true(ev.reticle_visible(), "with a choice of wheels, the attacks' focus wears them")
	var picked := _several_target_card(scene)
	assert_true(picked >= 0)
	scene.select_card(picked)
	ev.reticle_shown = true
	assert_false(ev.reticle_visible(), "never while a card is aimed: the pencil loop is the mark")
	scene.cancel_selection()
	await _close(scene)


# --- D2: the hub ---------------------------------------------------------------------------------------

func test_the_hub_is_an_emblem_and_a_tiny_name_and_shield_moves_to_chips() -> void:
	var scene := await _combat()
	var st: CombatState = scene.engine.state()
	st.player.shield = 4
	st.player.block = 3
	scene._refresh(st)
	await _frames(2)
	var pv: WheelView = scene._player_view
	var k := pv.art_scale()
	assert_almost_eq(pv.hub_emblem_px(k), pv.hub_px(k) * 0.9, 0.01, "D2: the emblem at 0.45 of the hub's radius each side")
	assert_eq(WheelView.NAME_FONT_SIZE, roundi(10.0 * GreasePencilMark.BOARD_TO_CANVAS), "D2: the name at 10 px at 1080p")
	assert_true(pv.hub_name_shown(k), "a wheel this size shows its name")
	var standing: Array = scene.hud_layer.row_for(pv).standing
	var words := PackedStringArray()
	for c in standing:
		words.append(String(c["text"]))
	assert_true(words.has(tr("SHIELD %d") % 4) and words.has(tr("BLOCK %d") % 3), "D2: shield and block are chips beside the HP (%s)" % [words])
	var tip: String = pv._get_tooltip(pv.global_center() - pv.global_position)
	assert_string_contains(tip, tr("Shield %d: soaks damage, lasts.") % 4, "and the hub's tooltip")
	var src := FileAccess.get_file_as_string("res://scripts/ui/wheel_view.gd")
	assert_false(src.contains("func _hub_lines"), "the hub writes no lines under its name")
	await _close(scene)


func test_the_hub_name_hides_under_r_90_at_1080() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	var r90 := WheelView.HUB_NAME_MIN_R_1080 * GreasePencilMark.BOARD_TO_CANVAS
	assert_almost_eq(r90, 60.0, 0.001, "r 90 at 1080 = 60 canvas px (WheelFace.LOD_RADIUS)")
	assert_false(WheelView.name_shows_at(r90 - 1.0), "a smaller wheel is the emblem alone")
	assert_true(WheelView.name_shows_at(r90), "from r 90 up the name shows")
	assert_true(pv.hub_name_shown(), "the fight's wheels are big enough")
	await _close(scene)


# --- The aiming result: chips underlined in wax, never faded ------------------------------------------

func test_the_result_underline_writes_on_and_wipes_with_the_cloth_never_fades() -> void:
	var scene := await _combat()
	Motion.force_live = true
	var picked := _several_target_card(scene)
	scene.select_card(picked)
	await BoundedWait.frozen_frames(get_tree(), 1)
	var lines: Array = scene.result_underlines()
	assert_gt(lines.size(), 0, "the aimed play's chips are underlined")
	assert_true(scene.aim_pencil.motion_running(), "the underline writes on (pencil_write_on)")
	var marks: Array = scene.aim_pencil.shown()
	var line_mark: GreasePencilMark = null
	for m in marks:
		if m is GreasePencilMark:
			line_mark = m
	assert_not_null(line_mark, "a wax mark (the B1b material)")
	for m in marks:
		assert_eq((m as CanvasItem).modulate.a, 1.0, "never faded in with alpha")
	scene.aim_pencil.complete_motion()
	assert_false(scene.aim_pencil.motion_running(), "MotionSkip: written whole")
	scene.cancel_selection()
	await BoundedWait.frozen_frames(get_tree(), 1)
	assert_true(scene.aim_pencil.motion_running(), "it wipes off (pencil_wipe)")
	for m in scene.aim_pencil.shown():
		assert_eq((m as CanvasItem).modulate.a, 1.0, "wiped, never faded")
	scene.aim_pencil.complete_motion()
	await BoundedWait.frozen_frames(get_tree(), 1)
	assert_eq(scene.aim_pencil.shown(), [], "gone")
	Motion.force_live = false
	await _close(scene)


func test_the_underline_is_a_hand_line_seeded_and_deterministic() -> void:
	var a := AimLinePencil.underline(Vector2(100, 200), Vector2(220, 200), 7)
	var b := AimLinePencil.underline(Vector2(100, 200), Vector2(220, 200), 7)
	assert_eq(a, b, "same seed, same line")
	assert_lt(a[0].x, 100.0, "it runs past its start")
	assert_gt(a[a.size() - 1].x, 220.0, "and past its end")
	var wob := 0.0
	for p in a:
		wob = maxf(wob, absf(p.y - 200.0))
	assert_between(wob, 0.1, GreasePencilMark.stroke_width(), "a hand's wobble, under the wax's width")


# --- D15: the fanned hand -------------------------------------------------------------------------------

func test_the_hand_fans_overlaps_and_rises_at_the_middle() -> void:
	var scene := await _combat()
	var n: int = scene._hand_box.get_child_count()
	assert_gt(n, 2)
	var s: float = scene._hand_scale
	assert_eq(scene._hand_box.get_theme_constant("separation"), -roundi(ZineCard.STICKER_SIZE.x * s * 0.12), "D15: 12 % overlap")
	for k in n:
		var f: Dictionary = scene.hand_fan(k, n, s)
		assert_almost_eq(float(f["deg"]), (k - (n - 1) * 0.5) * 2.5, 0.001, "D15: 2.5 degrees per card from the middle")
		var card := scene._hand_box.get_child(k) as ZineCard
		assert_almost_eq(card.rest_tilt, float(f["deg"]), 0.001, "the card rests at its fan angle")
		assert_almost_eq(card.fan_rise, float(f["rise"]), 0.001)
	var mid: Dictionary = scene.hand_fan((n - 1) / 2, n, s) if n % 2 == 1 else scene.hand_fan(n / 2, n, s)
	assert_almost_eq(float(scene.hand_fan(0, 5, 1.0)["rise"]), 0.0, 0.001, "the ends sit on the line")
	assert_almost_eq(float(scene.hand_fan(2, 5, 1.0)["rise"]), 6.0 * GreasePencilMark.BOARD_TO_CANVAS, 0.001, "D15: a 6 px arc rise at the middle")
	assert_gt(float(mid["rise"]), 0.0)
	await _close(scene)


func test_cards_rest_full_bright_dim_to_75_while_aiming_and_short_ram_goes_grey() -> void:
	var scene := await _combat()
	for c in scene._hand_box.get_children():
		assert_eq((c as Control).modulate, Color.WHITE, "at rest: full brightness")
	var picked := _several_target_card(scene)
	scene.select_card(picked)
	for c in scene._hand_box.get_children():
		var card := c as ZineCard
		if card.drag_index == picked:
			assert_eq(card.modulate, Color.WHITE, "the aimed card stays bright")
		else:
			assert_almost_eq(card.modulate.r, 0.75, 0.001, "D15: the others at 75 % (never 40 %)")
			assert_eq(card.modulate.a, 1.0, "opaque: dimmed, not see-through")
	scene.cancel_selection()
	var st: CombatState = scene.engine.state()
	st.ram = 0
	scene._refresh(st)
	await _frames(1)
	var grey := 0
	for c in scene._hand_box.get_children():
		var card := c as ZineCard
		if card.short_ram:
			grey += 1
			assert_true(card.greyed, "short of RAM: greyscale")
			assert_not_null(card.material, "through the card grey material")
			var tag := card.find_child("NeedTag", false, false) as Control
			assert_not_null(tag, "the NEED tag on its own layer")
			assert_null(tag.material, "in colour over the grey")
		else:
			assert_false(card.greyed)
	assert_gt(grey, 0, "cards it can't afford")
	await _close(scene)


# --- D16: EXECUTE ---------------------------------------------------------------------------------------

func test_execute_is_washed_out_smaller_than_send_it_and_half_covered() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		await _frames(2)
		var send := scene._end_turn_button as SendItSticker
		assert_eq(SendItSticker.SYSTEM_WORD_ALPHA, 0.25, "D16: 25 % alpha")
		assert_not_null(send.art, "the kit sticker")
		var send_cap := WheelFace.cap_height(SendItSticker.face(), UiTheme.font_px(send.art.font_step))
		var exec_cap := send.system_word_rect().size.y
		assert_almost_eq(exec_cap / send_cap, 0.8, 0.06, "x%.1f: D16: EXECUTE's cap height 0.8 x SEND IT's" % scale)
		assert_between(send.system_word_cover(), 0.35, 0.65, "x%.1f: D16: half covered by the sticker" % scale)
		await _close(scene)


# --- Q1 (c): the Heat chip ------------------------------------------------------------------------------

func test_the_heat_chip_sits_top_left_and_reuses_the_heat_gauge() -> void:
	for scale in SCALES:
		var scene := await _combat(scale)
		await _frames(2)
		var chip: Control = scene.heat_poster
		assert_true(chip is HeatGauge, "the shared HeatGauge (its motion kept)")
		assert_true(chip.is_visible_in_tree(), "x%.1f: shown in a campaign" % scale)
		var r := chip.get_global_rect()
		assert_lt(r.position.x, 20.0, "x%.1f: top left" % scale)
		assert_lt(r.position.y, 20.0)
		var want := Vector2(120, 32) * GreasePencilMark.BOARD_TO_CANVAS * clampf(scale, 1.0, (chip as HeatGauge).look.scale_max)
		assert_almost_eq(r.size.x, want.x, 2.0, "x%.1f: 120 x 32 at 1080p" % scale)
		assert_almost_eq(r.size.y, want.y, 2.0)
		for v in scene._views():
			assert_false(r.intersects((v as WheelView).wheel_rect()), "x%.1f: clear of the wheels" % scale)
		assert_false(r.intersects(scene._banner.get_global_rect()), "x%.1f: clear of the TURN strip" % scale)
		await _close(scene)


# --- Q2: key hints, Settings chip, tutorial ---------------------------------------------------------------

func test_key_letters_sit_on_the_controls_with_a_keyline_and_hints_are_tooltips() -> void:
	assert_eq(HudWheelLayer.key_letter("[Q]"), "Q", "Q2: the letter on the control")
	Settings.set_text_scale(1.0)
	assert_gte(HudWheelLayer.keyline_px() * 0.5 / GreasePencilMark.BOARD_TO_CANVAS, 3.0, "B1a Q2: an ink keyline of 3 px or more at 1080p")
	var scene := await _combat()
	var chip := scene._settings_button as SettingsIconChip
	assert_not_null(chip, "Settings is the icon chip")
	assert_eq(chip.text, "", "no words on it")
	assert_almost_eq(chip.size.x, 32.0 * GreasePencilMark.BOARD_TO_CANVAS, 1.0, "32 px at 1080p")
	assert_string_contains(chip.tooltip_text, Settings.key_text(&"open_settings"), "its key in its tooltip")
	assert_false(scene._status.visible, "no key-hint caption under the TURN strip")
	assert_false(scene._aim_hint.visible, "no aim caption over the hand")
	await _close(scene)


func test_the_tutorial_is_a_cyan_edged_terminal_never_a_sticker() -> void:
	var scene := await _combat()
	scene.start_tutorial()
	await _frames(2)
	var tut: TutorialOverlay = scene.tutorial
	assert_true(tut.note is TerminalNote, "a terminal card")
	assert_eq(Color(Palette.TERMINAL_EDGE, 1.0), Color(Palette.NET_CYAN, 1.0), "its edge is the terminal's cyan")
	for c in tut.find_children("*", "", true, false):
		assert_false(c is VinylSticker or c is VerbSticker or c is SendItSticker, "no sticker in it (%s)" % c.name)
	await _close(scene)
