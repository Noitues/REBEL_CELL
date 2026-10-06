extends GutTest
## Parity fix: the netrun route map (designer group ruling 2026-10-05: netrun pages match the
## concepts; round 37 `city_default` / `city_legend_hover`). Ids ROUTE-01 (the whole run drawn:
## hidden nodes as "not yet" discs, the district plates), ROUTE-04 (the ROUTE list is the pad and
## keyboard path of the map's own choices), ROUTE-05 (the key strip's states as the concept
## words and draws them), ROUTE-06 (THE GRID title; the fit frames YOU ARE HERE for every
## corporation at 1.0 / 1.6 / 2.0). Views never change state. Headless.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]

var _scale: float
var _all_nodes: bool


func before_each() -> void:
	_scale = Settings.text_scale
	_all_nodes = Settings.always_show_all_nodes
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
	if Settings.always_show_all_nodes != _all_nodes:
		Settings.set_always_show_all_nodes(_all_nodes)
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


func _overlay(scene: Control) -> RouteOverlay:
	return scene.city_overlay as RouteOverlay


# --- ROUTE-01: the whole run drawn ---------------------------------------------------------------

## B3 (review Q15, round 44 `route_page.png`; supersedes ROUTE-01's "not yet" discs): a hidden
## node is fully hidden (not drawn, no label); the strip's hover shows links only (Q4).
func test_hidden_nodes_are_fully_hidden_and_the_hover_brings_links_not_nodes() -> void:
	Settings.set_always_show_all_nodes(false)
	var scene := _netrun()
	await _frames()
	var ov := _overlay(scene)
	var before := RunManager.campaign.state_hash()
	var run_before := RunManager.netrun.state_hash()
	var hidden := ov.hidden_ids()
	var drawn := ov.drawn_ids()
	assert_false(hidden.is_empty(), "the rest of the run is hidden")
	for n in ov.nodes:
		if ov.icon_pos(n).x == INF:
			continue
		var id: StringName = n["id"]
		assert_ne(hidden.has(id), drawn.has(id), "%s is either drawn or hidden" % id)
		if RouteOverlay.pinned(n):
			assert_true(drawn.has(id), "%s: walked, a choice or the TARGET is a full sticker" % id)
		else:
			assert_true(hidden.has(id), "%s: hidden" % id)
			assert_eq(ov.shown(n), 0.0, "%s: nothing of it is drawn" % id)
			assert_true(ov.label_lines(id).is_empty(), "%s: no label" % id)
			assert_false(ov.marker_shown(n), "%s: takes no room in the fit" % id)
	scene.route_legend.show_links_hovered.emit(true)
	ov.links_t = 1.0
	assert_eq(ov.hidden_ids(), hidden, "the hover keeps the hidden nodes hidden")
	assert_true(ov.show_links, "the hover shows every link")
	scene.route_legend.show_links_hovered.emit(false)
	assert_false(ov.show_links, "and lets them go")
	assert_eq(RunManager.campaign.state_hash(), before, "views never change the campaign")
	assert_eq(RunManager.netrun.state_hash(), run_before, "views never change the run")


## B3 (the clutter rule, round 44 `route_page.png`; supersedes ROUTE-01's plates): the route
## page draws no district plates.
func test_the_route_page_draws_no_district_plates() -> void:
	var scene := _netrun()
	await _frames()
	var ov := _overlay(scene)
	assert_false(ov.landmarks, "no plates on the route page")
	assert_true(ov.landmark_plates().is_empty())


# --- ROUTE-04: the choices are picked on the map ---------------------------------------------------

func test_the_choices_are_focus_stops_on_their_map_stickers_in_numbered_order() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.reset()
		var scene := _netrun()
		await _frames(4)
		var ov := _overlay(scene)
		var s := RunManager.netrun
		var choices: Array = scene.view_choices(s)
		var buttons: Array = scene._route_buttons
		assert_gt(choices.size(), 1, "x%.1f: a route start with a choice to make" % scale)
		assert_eq(buttons.size(), choices.size(), "x%.1f: one stop per choice" % scale)
		for n in ov.nodes:
			if int(n.get("number", 0)) > 0:
				assert_true(choices.has(n["id"]), "x%.1f: every numbered sticker has its stop" % scale)
		var xf := ov.get_global_transform_with_canvas()
		var row := scene._panel.find_child("RouteNodes", true, false) as Control
		# The ROUTE window lists no rows (the concept picks on the map); B3 (bible 4.6, round 44):
		# no "then:" line either: the window holds GRID VIEW and Save & quit only.
		var shown_lines := 0
		for c in row.get_children():
			if c is Control and (c as Control).visible and not (c as Control).top_level:
				shown_lines += 1
		assert_eq(shown_lines, 0, "x%.1f: no list rows in the ROUTE window" % scale)
		var grid := scene._panel.find_child("GridZoom", true, false) as Control
		for i in choices.size():
			var b := buttons[i] as Button
			var n := ov._node_dict(choices[i])
			assert_eq(int(n.get("number", 0)), i + 1, "x%.1f: stop %d is the map's choice %d" % [scale, i + 1, i + 1])
			assert_eq(b.focus_mode, Control.FOCUS_ALL, "x%.1f: stop %d takes the pad's and the keys' focus" % [scale, i + 1])
			assert_true(b.top_level, "x%.1f: stop %d is on the map, not in the window's column" % [scale, i + 1])
			assert_true(b.get_global_rect().has_point(xf * ov.icon_pos(n)), "x%.1f: stop %d sits on its sticker" % [scale, i + 1])
			assert_eq(b.get_theme_color(&"font_color").a, 0.0, "x%.1f: the map's label speaks for stop %d" % [scale, i + 1])
			# Down walks the stops in the map's numbered order, then GRID VIEW.
			var down := b.get_node_or_null(b.focus_neighbor_bottom)
			var want: Control = buttons[i + 1] if i + 1 < buttons.size() else grid
			assert_eq(down, want, "x%.1f: down from stop %d" % [scale, i + 1])
		# Focus lights the sticker.
		var last := buttons[buttons.size() - 1] as Button
		last.grab_focus()
		await _frames(2)
		assert_eq(ov.hover_id, choices[choices.size() - 1], "x%.1f: the focused stop lights its sticker" % scale)
		assert_lt(ov._hi.get_index(), ov._tags.get_index(), "the focus ring draws under the labels")
		Settings.set_text_scale(1.0)
		scene.get_parent().queue_free()
		await _frames(1)


func test_enter_on_a_focused_stop_picks_that_choice() -> void:
	var scene := _netrun()
	await _frames(4)
	var s := RunManager.netrun
	var choices: Array = scene.view_choices(s)
	var buttons: Array = scene._route_buttons
	var last := buttons[buttons.size() - 1] as Button
	last.grab_focus()
	await _frames(1)
	# Enter / A (ui_accept) on the focused stop is its press: the choice is asked for.
	var asked := [false]
	last.pressed.connect(func() -> void: asked[0] = true)
	var press := InputEventAction.new()
	press.action = &"ui_accept"
	press.pressed = true
	Input.parse_input_event(press)
	var release := InputEventAction.new()
	release.action = &"ui_accept"
	Input.parse_input_event(release)
	await _frames(1)
	assert_true(asked[0], "Enter / A picks the focused choice")
	assert_true(s.run.current_node_id == choices[choices.size() - 1] or s.run.visited.has(choices[choices.size() - 1]),
		"the run goes to that choice (%s)" % s.run.current_node_id)


# --- B3: no YOU ARE HERE words (supersedes S-ROUTE c's placed label) -------------------------------

## B3 (round 44 `route_page.png`): the operative's token marks the position, with no words; no
## node carries a text tag (the choices keep their number chips).
func test_no_you_are_here_words_and_no_node_tags_for_every_corporation() -> void:
	for corp in CORPORATIONS:
		RunManager.reset()
		var scene := _netrun(corp)
		await _frames(4)
		var ov := _overlay(scene)
		assert_eq(ov.here_id(), &"", "%s: before the first node the marker stands on the street" % corp)
		assert_ne(ov.here_point().x, INF, "%s: the marker (the token) still stands" % corp)
		assert_false(ov.here_label_shown(), "%s: no YOU ARE HERE words" % corp)
		var rects: Dictionary = ov.label_rects()
		assert_false(rects.has(CityMapOverlay.HERE_KEY), "%s: no YOU ARE HERE label" % corp)
		for key in rects:
			var n := ov._node_dict(StringName(key))
			assert_true(bool(n.get("target", false)), "%s: only the TARGET's pencil word is placed (%s)" % [corp, key])
		for n in ov.nodes:
			if int(n.get("number", 0)) > 0:
				assert_ne(ov.number_rect(ov.icon_pos(n), ov.icon_radius(n)).size, Vector2.ZERO, "%s: choice %d keeps its number chip" % [corp, int(n["number"])])
		scene.get_parent().queue_free()
		await _frames(1)


# --- The dossier's letterhead (ROUTE-02 follow-up) ----------------------------------------------

func test_the_dossier_letterhead_keeps_every_word_whole_at_each_text_size() -> void:
	var scene := _netrun(&"meridian")
	await _frames()
	for scale in SCALES:
		Settings.set_text_scale(scale)
		await _frames(2)
		var d: OperativeDossier = scene.dossier
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
	for scale in SCALES:
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


func test_the_fit_frames_you_are_here_for_every_corporation_and_text_size() -> void:
	for corp in CORPORATIONS:
		RunManager.reset()
		var scene := _netrun(corp)
		await _frames()
		var s := RunManager.netrun
		s.run.current_node_id = s.run.map.first_layer_ids()[0]
		scene._show_map()
		await _frames()
		var ov := _overlay(scene)
		for scale in SCALES:
			Settings.set_text_scale(scale)
			await _frames(2)
			assert_lte(scene._route_fits, NetrunScript.ROUTE_FITS_MAX + NetrunScript.ROUTE_RESCUE_PASSES, "%s x%.1f: the fit ends" % [corp, scale])
			var here := ov.get_global_transform_with_canvas() * ov.icon_pos(ov._node_dict(ov.here_id()))
			assert_true(scene.route_free_area().has_point(here), "%s x%.1f: you are in the map's free area (%s)" % [corp, scale, here])
			assert_false(scene.route_legend.get_global_rect().has_point(here), "%s x%.1f: not on the key strip" % [corp, scale])
		Settings.set_text_scale(1.0)
		scene.get_parent().queue_free()
		await _frames(1)
