extends GutTest
## HEAT-ALL (M14, designer rulings Q1 / Q2 / Q10 2026-10-05): the Heat gauge is the top bar's
## first slot on every screen with a bar (netrun route, event, loot, Mainframe, run end; the
## HQ pages are HQ-B's), read-only in a run (the Heat terminal without SCRUB); the screens'
## titles are yellow title stickers, not bar lettering; the route dossier has no Heat stamp.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const HEAT := 58

var _scale: float
var _reduce: bool


func before_each() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_heat_all"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()
	HeatPoster._seen_heat.clear()


func after_each() -> void:
	CityBakeCache.shutdown()
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx._set_jacking(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _netrun() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	RunManager.campaign.heat = HEAT
	scene.start_run(1)
	return scene


func _check_gauge(scene: Control, what: String) -> void:
	var bar: HudBar = scene.hud
	var g := bar.heat_gauge
	assert_true(g.is_visible_in_tree(), "%s: the gauge shows" % what)
	assert_eq(g.get_index(), 0, "%s: first in the bar's row" % what)
	assert_eq(g.heat, RunManager.campaign.heat, "%s: the campaign's Heat" % what)
	assert_eq(g.marks, HeatRules.band_levels(RunManager.campaign, RunManager.config()), "%s: the band levels" % what)
	assert_lt(g.get_global_rect().position.x, bar.stats.get_global_rect().position.x, "%s: left of the stat tags" % what)
	for it in bar.stats.items:
		assert_ne(String(it[0]), TextDb.mark("HEAT"), "%s: no second Heat tag" % what)
	assert_true(g.interactive, "%s: it opens the Heat terminal" % what)


func test_the_gauge_is_first_on_every_run_screen_with_the_campaigns_heat() -> void:
	var scene := _netrun()
	await _frames()
	_check_gauge(scene, "route")
	assert_not_null(scene.hud.title_sticker, "the route's title is a sticker")
	var s := RunManager.netrun
	DemoSetup.open_shop(s, 50)
	scene._show_current()
	await _frames()
	_check_gauge(scene, "mainframe")
	DemoSetup.offer_loot(s, ["barbed_wire"], "firmware")
	scene._show_current()
	await _frames()
	_check_gauge(scene, "loot")
	DemoSetup.end_run(s, "died")
	scene._show_current()
	await _frames()
	_check_gauge(scene, "run end")


func test_titles_are_yellow_stickers_not_bar_lettering() -> void:
	var scene := _netrun()
	await _frames()
	var bar: HudBar = scene.hud
	assert_eq(bar._title, tr("THE GRID"))  # parity ROUTE-06
	assert_not_null(bar.title_sticker, "a sticker names the screen")
	assert_eq(bar.title_sticker.fill, VerbSticker.Fill.YELLOW, "yellow (v2 page-title rule)")
	assert_eq(bar.title_sticker.text, tr("THE GRID"))
	assert_false(bar.title_box.draw.is_connected(Callable(bar, "_draw_title")), "no paper lettering in the bar")
	bar.set_screen("", "CELL DEFENSE RAID SETUP")
	assert_lte(bar.title_box.custom_minimum_size.x, HudBar.TITLE_MAX_WIDTH + HudBar.TITLE_PAD + 60.0, "a long title letters smaller, not wider")
	bar.set_screen("", "")
	assert_null(bar.title_sticker, "a screen without a title has no sticker (combat)")
	assert_false(bar.title_box.visible, "and the gauge keeps the slot")


func test_in_a_run_the_gauge_opens_a_read_only_terminal() -> void:
	var scene := _netrun()
	await _frames()
	scene.hud.heat_gauge.pressed.emit()
	await _frames()
	var term: HeatTerminal = scene.heat_terminal
	assert_not_null(term, "the terminal drops")
	assert_true(term.read_only, "read-only in a run (Q2)")
	assert_null(term.scrub, "no SCRUB HEAT in a run")
	assert_not_null(term.find_child("ReadOnly", true, false), "it says where Heat is scrubbed")
	var heat := RunManager.campaign.heat
	var schematics := RunManager.campaign.schematics
	assert_true(scene.get_global_rect().encloses(term.get_global_rect()), "on screen")
	scene.toggle_heat_terminal()
	await _frames()
	assert_null(scene.heat_terminal, "pressed again it folds away")
	assert_eq(RunManager.campaign.heat, heat, "a view changes nothing")
	assert_eq(RunManager.campaign.schematics, schematics)


func test_the_route_dossier_has_no_heat_stamp() -> void:
	var scene := _netrun()
	await _frames()
	var d: Dictionary = scene.dossier_data()
	assert_false(d.has("heat"), "the file carries no Heat")
	assert_false(d.has("band"))
	assert_false(scene.dossier.has_method("heat_words"), "the dossier draws no Heat stamp (Q10)")
	assert_true(scene.dossier.is_visible_in_tree(), "the dossier itself stays")
	assert_eq(String(d["subject"]), RunManager.netrun.run.operative.name)


func test_the_gauge_and_title_fit_at_every_text_scale() -> void:
	for s in SCALES:
		Settings.set_text_scale(s)
		var scene := _netrun()
		await _frames()
		var bar: HudBar = scene.hud
		var g := bar.heat_gauge
		assert_true(bar.get_global_rect().encloses(g.get_global_rect()), "x%.1f: the gauge in the bar" % s)
		assert_false(g.get_global_rect().intersects(bar.stats.get_global_rect()), "x%.1f: clear of the stat tags" % s)
		assert_false(g.get_global_rect().intersects(bar.title_box.get_global_rect()), "x%.1f: clear of the title" % s)
		assert_false(bar.title_box.get_global_rect().intersects(bar.stats.get_global_rect()), "x%.1f: the title clear of the tags" % s)
		assert_true(scene.get_global_rect().encloses(bar.title_sticker.get_global_rect()), "x%.1f: the sticker on screen" % s)
		scene.toggle_heat_terminal()
		await _frames()
		assert_true(scene.get_global_rect().encloses(scene.heat_terminal.get_global_rect()), "x%.1f: the terminal on screen" % s)
		scene.close_heat_terminal(false)
		scene.get_parent().free()


func test_the_gauge_in_the_run_keeps_the_one_press_and_reduce_effects_rules() -> void:
	Motion.force_live = true
	var scene := _netrun()
	await _frames()
	var bar: HudBar = scene.hud
	var g := bar.heat_gauge
	assert_true(g.is_in_group(MotionSkip.GROUP), "the gauge joins the one press rule in a run")
	var marks: Array[int] = [25, 50, 75, 100]
	g.set_heat(10, 100, marks)
	g.set_heat(60, 100, marks)
	await BoundedWait.frozen_frames(get_tree(), 1)
	g.complete_motion()
	assert_false(g.motion_running(), "one press ends the roll")
	assert_eq(roundi(g.shown_heat), 60)
	Motion.force_live = false
	Settings.set_reduce_effects(true)
	g.set_heat(20, 100, marks)
	g.set_heat(80, 100, marks)
	await _frames(2)
	assert_eq(roundi(g.shown_heat), 80, "reduce effects: the end state at once")


func test_the_hq_pages_keep_the_gauge_first_and_a_sticker_title() -> void:
	RunManager.new_campaign(1)
	RunManager.campaign.heat = HEAT
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	await _frames()
	hq.show_grid()
	await _frames()
	var bar: HudBar = hq.hud
	assert_eq(bar.heat_gauge.get_index(), 0)
	assert_true(bar.heat_gauge.is_visible_in_tree())
	assert_eq(bar.heat_gauge.heat, HEAT)
	# HQ-B (Q6): the HQ (the Grid folded in) shows no title; a titled page's is a yellow sticker.
	assert_null(bar.title_sticker, "no title sticker on the HQ")
	hq.show_start()
	await _frames()
	assert_not_null(bar.title_sticker, "the start page's title is a sticker")
	assert_eq(bar.title_sticker.fill, VerbSticker.Fill.YELLOW)
