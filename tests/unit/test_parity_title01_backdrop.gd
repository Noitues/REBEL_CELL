extends GutTest
## Parity fix TITLE-01 (designer 2026-10-05, concept round 33 `title_screen.png`): the title's
## backdrop is the blurred 3D city (BlurredCityBackdrop through CyberdeckBackground) at city
## quality tiers 1-2 and the 2D NeonCity below them and headless; every other
## CyberdeckBackground user is unchanged; the menu's words stay legible over either backdrop.

const TITLE := "res://scenes/menu/title_scene.tscn"
const LOOK_PATH := "res://content/config/title_city_backdrop.tres"
## The worst city behind a word: pure white (no light of the city is brighter).
const WORST_CITY := Color(1, 1, 1)
## The text and component contrast floors (WCAG 2.1: words 4.5:1, a component's edge 3:1).
const TEXT_MIN := 4.5
const EDGE_MIN := 3.0

var _saved_settings: Dictionary


func before_each() -> void:
	AudioDirector.muted = true
	_saved_settings = Settings.to_dict()
	RunManager.scene_switching_enabled = false
	RunManager.delete_slot("gut_title01")
	RunManager.save_slot = "gut_title01"
	RunManager.reset()


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.delete_slot("gut_title01")
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true
	Settings.from_dict(_saved_settings)
	Settings.save_settings()


func _look() -> CityBackdropLook:
	return load(LOOK_PATH) as CityBackdropLook


func test_the_title_takes_the_3d_city_at_tiers_1_and_2_and_the_2d_city_at_tier_0() -> void:
	var look := _look()
	assert_false(CyberdeckBackground.blurred_city_mode(look, 0, true), "tier 0: the 2D city")
	assert_true(CyberdeckBackground.blurred_city_mode(look, 1, true), "tier 1 (Deck): the 3D city")
	assert_true(CyberdeckBackground.blurred_city_mode(look, 2, true), "tier 2: the 3D city")
	assert_eq(CyberdeckBackground.blurred_city_mode(look, -1, true), look.city_tiers[CityView3D.CONFIG.quality_default], "the renderer's default tier")
	for t in 3:
		assert_false(CyberdeckBackground.blurred_city_mode(look, t, false), "no renderer (headless): the 2D city at tier %d" % t)
	assert_true(CyberdeckBackground.city_2d_demo(PackedStringArray(["--demo-overview"])), "a 2D design review keeps the 2D city")
	assert_true(CyberdeckBackground.city_2d_demo(PackedStringArray(["--demo-district=solace"])))
	assert_false(CyberdeckBackground.city_2d_demo(PackedStringArray(["--demo-options", "--demo-set=a"])), "other demos take the 3D city")


func test_the_title_asks_for_the_blurred_city_and_keeps_the_2d_fallback_headless() -> void:
	Settings.set_city_quality(2)
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	var bg: CyberdeckBackground = title.background
	assert_false(bg.on_blurred_city(), "headless: no renderer, the 2D fallback")
	assert_true(bg.city.visible, "the 2D city shows")
	var dim := title.get_node("CityDim") as ColorRect
	assert_true(dim.visible, "with its dim")
	assert_almost_eq(dim.color.a, float(title.CITY_DIM), 0.0001)
	var src := FileAccess.get_file_as_string("res://scripts/ui/title_scene.gd")
	assert_true(src.contains("background.use_blurred_city(CITY_LOOK"), "the title asks for the blurred city")
	assert_true(src.contains("dim.visible = not background.on_blurred_city()"), "the 3D city darkens itself")


func test_other_cyberdeck_background_users_are_unchanged() -> void:
	var callers: Array[String] = []
	for dir in ["res://scripts", "res://tools", "res://scenes"]:
		_scan(dir, callers)
	assert_eq(callers, ["res://scripts/ui/title_scene.gd"], "only the title swaps in the blurred city")
	var bg: CyberdeckBackground = add_child_autofree(CyberdeckBackground.new())
	assert_null(bg.blurred, "a plain CyberdeckBackground keeps the 2D city")
	assert_true(bg.city.visible)
	assert_eq(bg.city.process_mode, Node.PROCESS_MODE_INHERIT)
	assert_almost_eq(bg.city.dim, 0.2, 0.0001, "its window dim as before")
	assert_true(bg.city.rain and bg.city.follow_campaign, "rain and the territory follow, as before")
	assert_eq(bg.get_child_count(), 2, "the city and the deck frame, nothing more")


func _scan(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd") and FileAccess.get_file_as_string(dir.path_join(f)).contains(".use_blurred_city("):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_scan(dir.path_join(d), out)


func test_the_frame_shows_the_last_played_corp_else_halcyon() -> void:
	var look := _look()
	assert_eq(look.default_corp, &"halcyon", "round 33's ziggurat")
	assert_eq(BlurredCityBackdrop.frame_corp(look, &""), &"halcyon", "no campaign: the default")
	assert_eq(BlurredCityBackdrop.frame_corp(look, &"solace"), &"solace", "a campaign's target")
	assert_eq(BlurredCityBackdrop.frame_corp(look, &"rebel_cell"), &"halcyon", "the Cell is no target")
	assert_eq(BlurredCityBackdrop.frame_corp(look, &"made_up_corp"), &"halcyon", "a corp with no HQ on the city")
	RunManager.new_campaign(4, &"solace")
	RunManager.autosave()
	assert_eq(BlurredCityBackdrop.corp_of_slot("gut_title01"), &"solace", "the slot's corp")
	assert_eq(BlurredCityBackdrop.frame_corp(look, BlurredCityBackdrop.corp_of_slot("gut_title01")), &"solace", "framed on it")
	assert_eq(BlurredCityBackdrop.corp_of_slot("gut_nothing_here"), &"", "an empty slot")


func test_the_camera_puts_the_hq_on_the_anchor() -> void:
	var look := _look()
	var cfg := CityView3D.CONFIG
	for view: Vector2 in [Vector2(1280, 720), Vector2(1920, 1080)]:
		for corp: StringName in [&"halcyon", &"solace", &"meridian", &"orbital"]:
			var cam := BlurredCityBackdrop.camera(cfg, look, corp, view)
			var hq := NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
			var p := cam.project(CityIsoCamera.lot_to_world(cfg, hq, look.lift))
			assert_almost_eq(p.x, view.x * look.anchor.x, 1.0, "%s at %s: x" % [corp, view])
			assert_almost_eq(p.y, view.y * look.anchor.y, 1.0, "%s at %s: y" % [corp, view])
			assert_almost_eq(cam.ortho, look.ortho, 0.0001)


func test_the_darkening_is_round_33s() -> void:
	var look := _look()
	# title.py backdrop(): dark = 1 - 0.62 * clip(1 - x / 900) ^ 1.4 - 0.35 * clip((y / H - 0.82) / 0.18);
	# vig = 1 - 0.35 * (((x / W - 0.6) * 1.3) ^ 2 + ((y / H - 0.5) * 1.1) ^ 2); * 0.86 (1920x1080).
	for px: Vector2 in [Vector2(0, 0), Vector2(450, 540), Vector2(1200, 600), Vector2(1900, 1070), Vector2(300, 1000)]:
		var x := px.x
		var y := px.y
		var dark := 1.0 - 0.62 * pow(clampf(1.0 - x / 900.0, 0.0, 1.0), 1.4) - 0.35 * clampf((y / 1080.0 - 0.82) / 0.18, 0.0, 1.0)
		var vig := 1.0 - 0.35 * (pow((x / 1920.0 - 0.6) * 1.3, 2.0) + pow((y / 1080.0 - 0.5) * 1.1, 2.0))
		assert_almost_eq(look.field_at(px / Vector2(1920, 1080)), maxf(dark * vig * 0.86, 0.0), 0.0005, "field at %s" % px)
		var band := pow(clampf(1.0 - absf(y / 1080.0 - 0.56) / 0.36, 0.0, 1.0), 0.8)
		assert_almost_eq(look.focus_at(px / Vector2(1920, 1080)), band, 0.0005, "focus at %s" % px)
	var shader := FileAccess.get_file_as_string("res://shaders/city/city_tilt_shift.gdshader")
	for u in ["focus_centre", "focus_half", "focus_power", "side_dark", "side_reach", "side_power", "foot_dark", "foot_from",
			"vignette", "vignette_centre", "vignette_scale", "gain", "sigma_px", "hint_screen_texture"]:
		assert_true(shader.contains(u), "the shader takes %s" % u)


func test_the_arrival_is_a_motion_entry_that_skips_and_stills() -> void:
	assert_true(Motion.has(BlurredCityBackdrop.ARRIVE_MOTION), "the city's arrival has its entry")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/blurred_city_backdrop.gd")
	assert_true(src.contains("MotionSkip.register_passive(self)"), "a press lands it")
	Settings.set_reduce_effects(true)
	assert_true(BlurredCityBackdrop.still(), "reduce effects: a still frame")
	Settings.set_reduce_effects(false)
	Settings.set_reduce_motion(true)
	assert_true(BlurredCityBackdrop.still(), "reduce motion: a still frame")
	Settings.set_reduce_motion(false)
	assert_false(BlurredCityBackdrop.still())
	var b: BlurredCityBackdrop = add_child_autofree(BlurredCityBackdrop.new(_look(), &"solace"))
	assert_null(b.city, "headless builds no 3D city")
	assert_false(b.motion_running())


## The words of the main page over the backdrop: the verb chips (label TEXT_HI, line TEXT_MID),
## MORE and PROFILE (their labels' colours) on their terminal glass over the worst city the
## backdrop leaves behind them, and the verb stickers' white die-cut against it.
func test_the_menu_reads_over_both_backdrops() -> void:
	Settings.set_text_scale(1.0)
	var title: Control = add_child_autofree(load(TITLE).instantiate())
	await get_tree().process_frame
	await get_tree().process_frame
	var size: Vector2 = title.size
	var look := _look()
	var glass_alphas: Array[Color] = [Palette.TERMINAL_BG, Color(Palette.CRT_GLASS_TOP, 0.94)]
	var city_2d := Palette.over(WORST_CITY, Color(Palette.NET_BG_OUTER, float(title.CITY_DIM)))
	var checked := 0
	for row_name in ["Breach", "Simulate", "Overthrow"]:
		var sticker := title.find_child(row_name, true, false) as Control
		assert_not_null(sticker, row_name)
		if sticker == null:
			continue
		var r := sticker.get_global_rect()
		var city_3d := WORST_CITY * look.max_field(r, size)
		# The sticker's edge is two-tone (the white die-cut and its VINYL_INK rim): one of them
		# stands off any city behind it.
		for city: Color in [Color(city_3d, 1.0), city_2d]:
			var edge := maxf(Palette.contrast(Palette.PAPER, city), Palette.contrast(Palette.VINYL_INK, city))
			assert_gte(edge, EDGE_MIN, "%s's die-cut over the city" % row_name)
		var row := sticker.get_parent().get_parent()
		for chip in row.find_children("*", "MenuChip", true, false):
			var cr := (chip as Control).get_global_rect()
			var c3 := Color(WORST_CITY * look.max_field(cr, size), 1.0)
			for city: Color in [c3, city_2d]:
				for g: Color in glass_alphas:
					var bg := Palette.over(city, g)
					for ink: Color in [Palette.TEXT_HI, Palette.TEXT_MID]:
						assert_gte(Palette.contrast(ink, bg), TEXT_MIN, "%s chip words" % row_name)
						checked += 1
	for panel_name in ["More", "ProfileTags"]:
		var panel := title.find_child(panel_name, true, false) as Control
		assert_not_null(panel, panel_name)
		if panel == null:
			continue
		for l in panel.find_children("*", "Label", true, false):
			var label := l as Label
			if not label.is_visible_in_tree() or label.text.strip_edges() == "":
				continue
			var lr := label.get_global_rect()
			var c3 := Color(WORST_CITY * look.max_field(lr, size), 1.0)
			for city: Color in [c3, city_2d]:
				for g: Color in glass_alphas:
					var ink := label.get_theme_color(&"font_color")
					assert_gte(Palette.contrast(ink, Palette.over(city, g)), TEXT_MIN, "%s '%s' over the city" % [panel_name, label.text])
					checked += 1
	assert_gt(checked, 20, "the words were found and checked")
