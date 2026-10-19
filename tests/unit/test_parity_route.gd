extends GutTest
## Parity fix: the netrun route page (designer group ruling 2026-10-05: netrun pages match the
## concepts). Ids ROUTE-05 (the key strip's states as the concept words and draws them), ROUTE-06 (the NETRUN title) and the
## operative dossier's letterhead. NA-26: ROUTE-01 (hidden nodes, district plates), ROUTE-04 (focus stops on the 2D map's
## stickers) and the YOU ARE HERE fit belonged to the retired 2D route page (see NA26_PORT_MAP.md); the street page's
## selection, keys and confirm are asserted by test_na23_route_flow. Views never change state. Headless.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_route"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
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


func _netrun(corp: StringName = &"solace") -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10
	RunManager.new_campaign(1, corp)
	scene.start_run(1)
	return scene


# --- The dossier's letterhead (ROUTE-02 follow-up) ----------------------------------------------

func test_the_dossier_letterhead_keeps_every_word_whole_at_each_text_size() -> void:
	var scene := _netrun(&"meridian")
	await _frames()
	var d: OperativeDossier = add_child_autofree(OperativeDossier.new())
	d.show_file(scene.dossier_data())
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		await _frames(2)
		d.size = d.custom_minimum_size
		var w := d.size.x
		var lines := d.sub_lines(w)
		assert_eq(" ".join(lines), d.sub_text(), "x%.1f: every word of the sub line is there, in order" % scale)
		var fs := maxi(roundi(OperativeDossier.SUB_FONT * scale), 1)
		for line in lines:
			var lw := RouteInk.paper_font().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
			assert_lte(lw, w - OperativeDossier.MARGIN * scale * 2.0 + 0.5, "x%.1f: '%s' fits the file" % [scale, line])
		assert_gte(d.size.y, d.get_combined_minimum_size().y, "x%.1f: the file is as tall as its lines" % scale)


# --- ROUTE-05: the key strip -------------------------------------------------------------------

func test_the_key_strip_says_the_concepts_states_and_fits() -> void:
	# B3 (round 44 `route_page.png`): walked and next only (hidden nodes are never drawn).
	assert_eq(RouteLegend.COLOR_KEYS, ["walked", "next"] as Array[String])
	assert_eq(RouteLegend.COLOR_WORDS[1].get_slice(":", 0), "next", "round 44's word")
	assert_eq(RouteLegend.SHORT[CityMapOverlay.KIND_FIGHT], "FIGHT", "round 44's word")
	var scene := _netrun()
	await _frames()
	for scale in TestScope.scales(SCALES):
		Settings.set_text_scale(scale)
		await _frames(2)
		var legend: RouteLegend = scene.route_legend
		assert_null(legend.strip.get_node_or_null("Color_%s" % RouteOverlay.STATE_LATER), "x%.1f: no not-yet entry" % scale)
		for key in RouteLegend.COLOR_KEYS:
			var sw := legend.strip.get_node("Color_%s/Swatch" % key) as Control
			assert_eq(String(sw.get_meta(&"ring_style", "")), String(RouteOverlay.RING_STYLES[key]), "x%.1f: %s's style" % [scale, key])
		assert_true(SCREEN.grow(1.0).encloses(legend.get_global_rect()), "x%.1f: the strip fits" % scale)
		assert_eq(legend.cue.text, UiTip.for_input(tr(RouteLegend.HOVER_WORDS), tr(RouteLegend.PAD_WORDS)), "x%.1f: the show-all-links cue" % scale)


# --- ROUTE-06: THE GRID and the fit ------------------------------------------------------------

func test_the_route_is_titled_netrun() -> void:
	assert_eq(NetrunScript.ROUTE_TITLE, "NETRUN", "round 44's title sticker (B3)")
	var scene := _netrun()
	await _frames()
	assert_eq(scene.hud._title, tr("NETRUN"))
	assert_eq(scene.hud.title_sticker.text, tr("NETRUN"))
