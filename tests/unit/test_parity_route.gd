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

func test_hidden_nodes_are_drawn_as_not_yet_discs_with_no_kind_or_label() -> void:
	Settings.set_always_show_all_nodes(false)
	var scene := _netrun()
	await _frames()
	var ov := _overlay(scene)
	var before := RunManager.campaign.state_hash()
	var run_before := RunManager.netrun.state_hash()
	var ghosts := ov.ghost_ids()
	var drawn := ov.drawn_ids()
	assert_false(ghosts.is_empty(), "the rest of the run shows as discs")
	for n in ov.nodes:
		if ov.icon_pos(n).x == INF:
			continue
		var id: StringName = n["id"]
		# Every placed node is drawn one way or the other: the whole run is on the map.
		assert_true(ghosts.has(id) or drawn.has(id), "%s is drawn" % id)
		if RouteOverlay.pinned(n):
			assert_false(ghosts.has(id), "%s: walked, a choice or the TARGET is a full sticker" % id)
		else:
			assert_true(ghosts.has(id), "%s: hidden is a disc" % id)
			assert_true(ov.label_lines(id).is_empty(), "%s: a disc has no label (D13 keeps its kind)" % id)
			assert_true(ov.state_of(n) in [RouteOverlay.STATE_LATER, RouteOverlay.STATE_CUT], "%s: a disc is not yet or cut off" % id)
	# The legend's hover shows every sticker; the discs give way.
	scene.route_legend.show_all_hovered.emit(true)
	ov.all_t = 1.0
	assert_true(ov.ghost_ids().is_empty(), "every node a sticker on the hover")
	scene.route_legend.show_all_hovered.emit(false)
	assert_eq(ov.ghost_ids(), ghosts, "the discs again")
	assert_eq(RunManager.campaign.state_hash(), before, "views never change the campaign")
	assert_eq(RunManager.netrun.state_hash(), run_before, "views never change the run")


func test_district_plates_sit_clear_of_every_node_label_and_panel() -> void:
	var plates := 0
	for corp in CORPORATIONS:
		RunManager.reset()
		var scene := _netrun(corp)
		await _frames()
		var ov := _overlay(scene)
		for scale in SCALES:
			Settings.set_text_scale(scale)
			await _frames(2)
			var area := ov.label_area()
			var avoid: Array[Rect2] = ov.label_blocks()
			# The top bar (the map runs under it).
			avoid.append(ov.get_global_transform_with_canvas().affine_inverse() * (scene.hud.get_global_transform_with_canvas() * Rect2(Vector2.ZERO, scene.hud.size)))
			for r: Rect2 in ov.label_rects().values():
				avoid.append(r)
			for n in ov.nodes:
				var at := ov.icon_pos(n)
				if at.x != INF:
					var rr := ov.icon_radius(n)
					avoid.append(Rect2(at - Vector2(rr, rr), Vector2(rr, rr) * 2.0))
			var first := ov.landmark_plates()
			assert_eq(first, ov.landmark_plates(), "%s x%.1f: the plates are placed the same every time" % [corp, scale])
			var mine: Array[Rect2] = []
			for p: Dictionary in first:
				var rect: Rect2 = p["rect"]
				plates += 1
				assert_true(area.encloses(rect), "%s x%.1f: %s inside the map" % [corp, scale, p["text"]])
				assert_false(RouteOverlay.lines_cross(ov.route_lines(), rect), "%s x%.1f: %s covers no route line" % [corp, scale, p["text"]])
				for r in avoid:
					assert_false(r.intersects(rect), "%s x%.1f: %s covers nothing" % [corp, scale, p["text"]])
				for m in mine:
					assert_false(m.intersects(rect), "%s x%.1f: plates apart" % [corp, scale])
				mine.append(rect)
				var id: StringName = p["id"]
				assert_eq(String(p["text"]), tr(RouteOverlay.SPRAWL_WORD) if id == &"" else HqRunView.corp_word(id), "the district's name")
		Settings.set_text_scale(1.0)
		scene.get_parent().queue_free()
		await _frames(1)
	assert_gt(plates, 0, "the route names its districts")


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
		# The ROUTE window lists no rows (the concept picks on the map): at most the lit choice's
		# "then:" line shows.
		var shown_lines := 0
		for c in row.get_children():
			if c is Control and (c as Control).visible and not (c as Control).top_level:
				shown_lines += 1
		assert_lte(shown_lines, 1, "x%.1f: no list rows in the ROUTE window" % scale)
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
	assert_eq(RouteLegend.COLOR_WORDS[1].get_slice(":", 0), "selectable", "round 37's word")
	assert_eq(RouteLegend.COLOR_WORDS[2], "not yet (hidden)", "round 37's word")
	var scene := _netrun()
	await _frames()
	for scale in SCALES:
		Settings.set_text_scale(scale)
		await _frames(2)
		var legend: RouteLegend = scene.route_legend
		var later := legend.strip.get_node("Color_%s/Swatch" % RouteOverlay.STATE_LATER) as Control
		assert_true(bool(later.get_meta(&"ghost", false)), "x%.1f: not yet (hidden) is the map's disc" % scale)
		for key in RouteLegend.COLOR_KEYS:
			var sw := legend.strip.get_node("Color_%s/Swatch" % key) as Control
			assert_eq(String(sw.get_meta(&"ring_style", "")), String(RouteOverlay.RING_STYLES[key]), "x%.1f: %s's style" % [scale, key])
		assert_true(SCREEN.grow(1.0).encloses(legend.get_global_rect()), "x%.1f: the strip fits" % scale)
		assert_eq(legend.cue.text, UiTip.for_input(tr(RouteLegend.HOVER_WORDS), tr(RouteLegend.PAD_WORDS)), "x%.1f: the show-all cue" % scale)


# --- ROUTE-06: THE GRID and the fit ------------------------------------------------------------

func test_the_route_is_titled_the_grid() -> void:
	assert_eq(NetrunScript.ROUTE_TITLE, "THE GRID", "round 37's title sticker")
	var scene := _netrun()
	await _frames()
	assert_eq(scene.hud._title, tr("THE GRID"))
	assert_eq(scene.hud.title_sticker.text, tr("THE GRID"))


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
			assert_true(ov.label_rects().has(String(ov.here_id())), "%s x%.1f: YOU ARE HERE shows" % [corp, scale])
			var here := ov.get_global_transform_with_canvas() * ov.icon_pos(ov._node_dict(ov.here_id()))
			assert_true(scene.route_free_area().has_point(here), "%s x%.1f: you are in the map's free area (%s)" % [corp, scale, here])
			assert_false(scene.route_legend.get_global_rect().has_point(here), "%s x%.1f: not on the key strip" % [corp, scale])
		Settings.set_text_scale(1.0)
		scene.get_parent().queue_free()
		await _frames(1)
