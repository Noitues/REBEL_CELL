extends GutTest
## The Grid and route map sweeps of the H21-H24 city passes, merged (Test suite
## optimization, docs/TEST_SUITE.md): each pass opened its own Grid for every corporation
## (50 settled Grids in all) to check the same maps. Here each corporation's Grid is opened
## once per text size (1.0, 1.3, 1.6) and campaign stage (early, late) and every check of
## those passes runs on it:
## - H24 K1/K6: the key folds only at big text, the steps go icon-only inside the column,
##   node icons apart, labels apart, below the top bar, on the map area, within reach, and
##   no Site with room left unlabelled;
## - H23 #3/#5: the key on screen, over the map, clear of the column, its text at the
##   scale, covering no node; every node icon and tier pips on the map beside the column;
## - H21: icons never on one another, labels never on one another or on an icon (every
##   campaign stage and text size; H21 checked 1.0 and a live 1.5; ANIM-R1 M13 added the
##   late campaign);
## - with every node selected in turn (early, 1.0 and 1.6, as H22 and H23 did): the selected
##   Site labelled, labels apart, inside the label area and clear of its blocks (the side
##   column), within reach; the landmarks labelled (H22); the selection ring clear of the
##   labels (H21, at 1.0); the run rows and Site steps carry their map icons (H23 #7,
##   Solace);
## - a live text size change on an open Grid keeps labels apart and on screen (H21 at 1.5,
##   H22 at 1.6 set live: here 1.0 -> 1.6 live).
## The route sweep merges H21 (labels never overlap, at the start and under way) and H22
## (YOU ARE HERE labelled and on screen at 1.0 and 1.6, clear of the route window).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, 1.3, 1.6]
## The text sizes the every-node selection sweeps ran at (H22, H23).
const SELECT_SCALES: Array[float] = [1.0, 1.6]
const SCREEN := Rect2(0, 0, 1280, 720)
## Frames for the Grid map to settle (the fit waits for the city to redraw each pass).
const SETTLE := 12
## Runs completed for the "late" Grid state (H24 K1).
const LATE_RUNS := 6

var _text_scale_before: float = 1.0
var _legend_before: bool = true


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_legend_before = Settings.map_legend


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_city_sweeps"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
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


## A 1280x720 holder (the headless window is tiny) with `path` instanced in it.
func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _open_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


## Completes the first `n` runs open now (in id order), as the real rules do.
func _advance(n: int) -> void:
	for i in n:
		var open := RunManager.launchable_sites().filter(func(s: SiteData) -> bool: return s.objective != RC.SiteObjective.BOSS)
		if open.is_empty():
			return
		var run := RunState.new()
		run.site_id = open[0].id
		run.kind = CampaignRules.run_kind_for(RunManager.campaign, open[0])
		CampaignRules.on_run_completed(RunManager.campaign, RunManager.corporation, RunManager.config(), run, RunManager.lookup())


## The HQ on `corp`'s Grid at `scale` (`late`: some runs done), settled.
func _hq_grid(corp: StringName, scale: float, late: bool = false) -> Control:
	RunManager.reset()
	Settings.set_text_scale(scale)
	var hq := _scene(HQ)
	_open_all()
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
	if late:
		_advance(LATE_RUNS)
	hq.selected_site = &""
	hq.show_grid()
	await _frames(SETTLE)
	return hq


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(1)


func _screen_rect(overlay: CityMapOverlay, r: Rect2) -> Rect2:
	var xf := overlay.get_global_transform()
	return Rect2(xf * r.position, r.size * xf.get_scale())


## Screen centre of `overlay`'s node `n` icon.
func _screen_at(overlay: CityMapOverlay, n: Dictionary) -> Vector2:
	return overlay.get_global_transform() * overlay.icon_pos(n)


## The legend's rect on screen (its scale included).
func _legend_rect(legend: MapLegend) -> Rect2:
	return Rect2(legend.get_global_rect().position, legend.size * legend.scale)


func _assert_apart(rects: Dictionary, what: String) -> void:
	var keys := rects.keys()
	keys.sort()
	for i in keys.size():
		for j in range(i + 1, keys.size()):
			var a: Rect2 = rects[keys[i]]
			var b: Rect2 = rects[keys[j]]
			assert_false(a.intersects(b), "%s: %s %s and %s %s overlap" % [what, keys[i], a, keys[j], b])


# --- The Grid ------------------------------------------------------------------------------

func test_the_grid_for_every_corporation_text_size_and_stage() -> void:
	Settings.set_map_legend(true)
	var reaches := {}
	var zooms := PackedStringArray()
	for corp in CORPS:
		for scale in SCALES:
			for late in [false, true]:
				var hq: Control = await _hq_grid(corp, scale, late)
				var what := "%s x%.1f %s" % [corp, scale, "late" if late else "early"]
				var overlay: CityMapOverlay = hq.city_overlay
				zooms.append("%s zoom %.2f" % [what, overlay.city.scale.x])
				_check_key_and_steps(hq, what, scale)
				_check_icons_apart(overlay, what)
				if not reaches.has(scale):
					reaches[scale] = [] as Array[float]
				_check_labels_k1(hq, what, reaches[scale])
				_check_legend(hq, what, scale)
				_check_nodes_beside_the_column(hq, what)
				# ANIM-R1 M13: late too (the selected Site's long name lay over other nodes'
				# icons in a late campaign at 1.3 / 1.6: now asserted everywhere).
				_assert_no_overlap(overlay, what)
				if not late and SELECT_SCALES.has(scale):
					_check_every_selection(hq, what, is_equal_approx(scale, 1.0))
					if corp == &"solace":
						_check_run_rows_and_steps(hq, what)
				if not late and is_equal_approx(scale, 1.0):
					_check_live_text_size(hq, what)
				await _close(hq)
	gut.p("H24 K1 zooms: %s" % ", ".join(zooms))
	for scale in reaches:
		var r: Array[float] = reaches[scale]
		r.sort()
		if not r.is_empty():
			gut.p("H24 K1 label reach x%.1f (screen px): n=%d median %.1f p90 %.1f max %.1f" % [scale, r.size(), r[r.size() / 2],
				r[int(r.size() * 0.9)], r[r.size() - 1]])


## H24 K1: the key folds to one line at big text (open at 1.0); the step buttons go
## icon-only at big text and keep inside the column.
func _check_key_and_steps(hq: Control, what: String, scale: float) -> void:
	var legend: MapLegend = hq.grid_legend
	var big := scale >= MapLegend.FOLD_SCALE - 0.001
	assert_eq(legend.is_folded(), big, "%s: the key folds only at big text" % what)
	if big:
		assert_not_null(legend.fold_button, "%s: the folded key is its MAP KEY button" % what)
		var line := legend.fold_button.get_combined_minimum_size().y
		assert_true(legend.size.y <= line * 2.0 + 24.0, "%s: folded, the key is one line (%.0f px)" % [what, legend.size.y])
	var card := (hq.find_child("SelectedSite", true, false) as Control).get_global_rect()
	for name in ["PrevSite", "NextSite", "BackToHq"]:
		var b := hq.find_child(name, true, false) as Button
		assert_not_null(b, "%s: %s" % [what, name])
		if big:
			assert_true(b.text.length() <= 1, "%s: %s shows its icon (and arrow) only: '%s'" % [what, name, b.text])
			assert_ne(b.tooltip_text, "", "%s: %s keeps its words in the tooltip" % [what, name])
		assert_true(b.get_global_rect().end.x <= card.end.x + 0.5, "%s: %s inside the column (%s vs %s)" % [what, name, b.get_global_rect(), card])


## H24 K6: no two node icons (with their tier pips) overlap.
func _check_icons_apart(overlay: CityMapOverlay, what: String) -> void:
	var rects := {}
	for n in overlay.nodes:
		var r := overlay.icon_rect(n)
		if r.has_area():
			rects[String(n["id"])] = r
	assert_eq(rects.size(), overlay.nodes.size(), "%s: every node has its icon" % what)
	_assert_apart(rects, "%s icons" % what)


## H24 K1: labels apart, on the map area (below the top bar, beside the column, above the
## key), within LABEL_REACH, and no Site with room left without its label.
func _check_labels_k1(hq: Control, what: String, reaches: Array[float]) -> void:
	var overlay: CityMapOverlay = hq.city_overlay
	var hud_bottom: float = (hq.hud as Control).get_global_rect().end.y
	var area := (hq.find_child("GridMapArea", true, false) as Control).get_global_rect()
	var rects := overlay.label_rects()
	assert_false(rects.is_empty(), "%s: labels shown" % what)
	_assert_apart(rects, "%s labels" % what)
	var reach := CityMapOverlay.LABEL_REACH * overlay._k()
	for key in rects:
		var r: Rect2 = rects[key]
		var sr := _screen_rect(overlay, r)
		assert_true(sr.position.y >= hud_bottom, "%s: %s below the top bar (%.0f vs %.0f)" % [what, key, sr.position.y, hud_bottom])
		assert_true(area.grow(0.5).encloses(sr), "%s: %s on the map area" % [what, key])
		var n := overlay._node_dict(StringName(String(key).get_slice("#", 0)))
		var d := CityMapOverlay.reach_of(r, overlay.icon_pos(n))
		assert_true(d <= reach + 0.01, "%s: %s within reach" % [what, key])
		reaches.append(d / overlay._k())
	var missing := overlay.unplaced_with_room()
	assert_eq(missing.size(), 0, "%s: every Site with room has its label: %s" % [what, missing])
	var named := 0
	for n in overlay.nodes:
		if not overlay.label_lines(n["id"]).is_empty():
			named += 1
	gut.p("%s: %d of %d named Sites labelled" % [what, rects.size(), named])


## H23 #3: the key is on screen, over the map, clear of the column and of every node, and
## its text follows the text size.
func _check_legend(hq: Control, what: String, scale: float) -> void:
	var legend: MapLegend = hq.grid_legend
	assert_not_null(legend, "%s: the Grid has its key" % what)
	assert_true(legend.is_visible_in_tree(), what)
	var lr := _legend_rect(legend)
	assert_true(SCREEN.encloses(lr), "%s: the key %s is on screen" % [what, lr])
	var area := (hq.find_child("GridMapArea", true, false) as Control).get_global_rect()
	assert_true(area.grow(0.5).encloses(lr), "%s: over the map %s" % [what, area])
	var column := (hq.find_child("GridColumn", true, false) as Control).get_global_rect()
	assert_false(lr.intersects(column), "%s: clear of the side column" % what)
	assert_eq(legend.font_size(), roundi(MapLegend.COMPACT_FONT * scale), "%s: its text follows the scale" % what)
	var labels := legend.body.find_children("*", "Label", true, false)
	assert_false(labels.is_empty())
	for l in labels:
		assert_eq((l as Label).get_theme_font_size("font_size"), legend.font_size(), "%s: row text at the scale" % what)
	assert_eq(LegendSpot.covered(lr, LegendSpot.node_rects(hq.city_overlay, false)), 0.0, "%s: the key covers no node" % what)


## H23 #5: every node's icon centre and tier pips on the map area, none under the column.
func _check_nodes_beside_the_column(hq: Control, what: String) -> void:
	var overlay: CityMapOverlay = hq.city_overlay
	var area := (hq.find_child("GridMapArea", true, false) as Control).get_global_rect()
	var column := (hq.find_child("GridColumn", true, false) as Control).get_global_rect()
	var xf := overlay.get_global_transform()
	for n in overlay.nodes:
		var at := _screen_at(overlay, n)
		var where := "%s %s at %s" % [what, n["id"], at]
		assert_true(area.has_point(at), "%s: on the map %s" % [where, area])
		assert_false(column.has_point(at), "%s: not under the column" % where)
		var pips := overlay.tier_pips_rect(n)
		if pips.has_area():
			assert_true(area.grow(0.5).encloses(Rect2(xf * pips.position, pips.size * xf.get_scale())), "%s: its tier pips too" % where)


## H21: no two drawn labels overlap, no label covers a node icon, and no icon sits on
## another.
func _assert_no_overlap(overlay: CityMapOverlay, what: String) -> void:
	var rects := overlay.label_rects()
	assert_gt(rects.size(), 0, "%s draws labels" % what)
	for a in overlay.nodes.size():
		for b in range(a + 1, overlay.nodes.size()):
			var na: Dictionary = overlay.nodes[a]
			var nb: Dictionary = overlay.nodes[b]
			if overlay.icon_pos(na).x == INF or overlay.icon_pos(nb).x == INF:
				continue
			assert_true(overlay.icon_pos(na).distance_to(overlay.icon_pos(nb)) >= overlay.icon_radius(na) + overlay.icon_radius(nb),
				"%s: icons %s and %s overlap" % [what, na["id"], nb["id"]])
	var keys: Array = rects.keys()
	for i in keys.size():
		for j in range(i + 1, keys.size()):
			assert_false((rects[keys[i]] as Rect2).intersects(rects[keys[j]]), "%s: labels %s and %s overlap" % [what, keys[i], keys[j]])
		for n in overlay.nodes:
			var at := overlay.icon_pos(n)
			if at.x == INF:
				continue
			var r: Rect2 = rects[keys[i]]
			var q := Vector2(clampf(at.x, r.position.x, r.end.x), clampf(at.y, r.position.y, r.end.y))
			assert_true(q.distance_to(at) >= overlay.icon_radius(n) - 0.01 or String(keys[i]).ends_with("#threats"), "%s: label %s clears icon %s" % [what, keys[i], n["id"]])


## Every label inside the overlay's label area and off its blocked screen areas (H22).
func _assert_on_screen(overlay: CityMapOverlay, what: String) -> void:
	var area := overlay.label_area()
	var blocks := overlay.label_blocks()
	var rects := overlay.label_rects()
	for key in rects:
		var r: Rect2 = rects[key]
		assert_true(area.grow(0.01).encloses(r), "%s: label %s %s inside the map %s" % [what, key, r, area])
		for b in blocks:
			assert_false(r.intersects(b), "%s: label %s %s clear of the side column %s" % [what, key, r, b])


## H23 #2/#4 and H22: with each node selected in turn, the selected one is labelled, no two
## labels overlap, each lies inside the label area, clear of its blocks and within
## LABEL_REACH of its node; with home selected the landmarks keep their labels (the boss
## Site was clipped for four corporations). H21 (`ring`): the selection ring circles the
## last node's icon, clear of it and of every label.
func _check_every_selection(hq: Control, what: String, ring: bool) -> void:
	var overlay: CityMapOverlay = hq.city_overlay
	assert_false(overlay.label_blocks().is_empty(), "%s: the Grid's column is blocked for labels" % what)
	var c := RunManager.campaign
	var paths := CityLayout.threat_paths(c, RunManager.corporation)
	var ids: Array[StringName] = []
	for n in overlay.nodes:
		ids.append(n["id"])
	var reach := CityMapOverlay.LABEL_REACH * overlay._k()
	for id in ids:
		var g := CityLayout.grid_graph(c, RunManager.corporation, paths, id)
		overlay.set_graph(g["nodes"], g["edges"])
		overlay.selected_id = id
		var sel := "%s selected %s" % [what, id]
		var rects := overlay.label_rects()
		assert_true(rects.has(String(id)), "%s: the selected Site is labelled" % sel)
		_assert_apart(rects, sel)
		_assert_on_screen(overlay, sel)
		for key in rects:
			var n := overlay._node_dict(StringName(String(key).get_slice("#", 0)))
			assert_true(CityMapOverlay.reach_of(rects[key], overlay.icon_pos(n)) <= reach + 0.01, "%s: %s within reach of its node" % [sel, key])
		# ANIM-R1 M13: the selected Site's label keeps off every other node's icon.
		for other in overlay.nodes:
			var at := overlay.icon_pos(other)
			if other["id"] == id or at.x == INF:
				continue
			assert_false(CityMapOverlay._rect_hits_disc(rects[String(id)], at, overlay.icon_radius(other) - 0.01),
				"%s: its label keeps off %s's icon" % [sel, other["id"]])
	var g0 := CityLayout.grid_graph(c, RunManager.corporation, paths, c.grid.home_site_id)
	overlay.set_graph(g0["nodes"], g0["edges"])
	overlay.selected_id = c.grid.home_site_id
	for n in overlay.nodes:
		if n.get("big", false):
			assert_true(overlay.label_rects().has(String(n["id"])), "%s: landmark %s labelled" % [what, n["id"]])
	if ring:
		var last: Dictionary = overlay.nodes[overlay.nodes.size() - 1]
		overlay.selected_id = last["id"]
		var centre := overlay.ring_centre()
		assert_eq(centre, overlay.icon_pos(last), "%s: the ring circles the selected icon" % what)
		assert_gt(overlay.ring_radius(), overlay.icon_radius(last), "%s: clear of it" % what)
		for key in overlay.label_rects():
			assert_false(CityMapOverlay._rect_hits_disc(overlay.label_rects()[key], centre, overlay.ring_radius()),
				"%s: label %s clears the selection ring" % [what, key])
		_assert_no_overlap(overlay, "%s selected" % what)
	# Back to the Grid's own selection for the checks that follow.
	var g1: Dictionary = hq.grid_graph()
	overlay.set_graph(g1["nodes"], g1["edges"])
	overlay.selected_id = hq.selected_site


## H23 #7: each run row and each Site step carries its Site's map icon and names its kind.
func _check_run_rows_and_steps(hq: Control, what: String) -> void:
	var nodes := {}
	for n in hq.grid_graph()["nodes"]:
		nodes[n["id"]] = n
	var rows := hq.find_child("RunRows", true, false) as VBoxContainer
	assert_not_null(rows, "%s: one run a row" % what)
	var checked := 0
	for b in rows.get_children():
		if b is Button and String(b.name).begins_with("Run_"):
			var id := StringName(String(b.name).trim_prefix("Run_"))
			var kind := String(nodes[id]["kind"])
			assert_eq(IconMark.map_kind_of(b), kind, "%s %s: the map icon of its kind" % [what, id])
			assert_string_contains((b as Button).tooltip_text.replace("\n", " "), CityMapOverlay.kind_word(kind), "%s %s: the tip names the kind" % [what, id])
			if kind != CityMapOverlay.KIND_TIER:
				assert_string_contains((b as Button).text, CityMapOverlay.kind_word(kind).to_upper(), "%s %s: the row says its kind" % [what, id])
			checked += 1
	assert_gt(checked, 0, "%s: runs checked" % what)
	for pair in [["PrevSite", -1], ["NextSite", 1]]:
		var b := hq.find_child(pair[0], true, false) as Button
		var to: StringName = hq.stepped_site(pair[1])
		assert_eq(IconMark.map_kind_of(b), String(nodes[to]["kind"]), "%s: %s shows the icon of the Site it goes to" % [what, pair[0]])
		assert_string_contains(b.tooltip_text.replace("\n", " "), CityMapOverlay.kind_word(String(nodes[to]["kind"])), "%s: %s names it" % [what, pair[0]])


## H21 (1.5 live) and H22 (1.6 live): a text size change on the open Grid keeps the labels
## apart, clear of the icons and on screen; the size goes back after.
func _check_live_text_size(hq: Control, what: String) -> void:
	var overlay: CityMapOverlay = hq.city_overlay
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	_assert_no_overlap(overlay, "%s large text live" % what)
	_assert_on_screen(overlay, "%s large text live" % what)
	Settings.set_text_scale(1.0)


# --- The route -----------------------------------------------------------------------------

func test_the_route_for_every_corporation() -> void:
	for corp in CORPS:
		RunManager.reset()
		_open_all()
		RunManager.new_campaign(1, corp)
		var scene := _scene(NETRUN)
		scene.start_run(1)
		await _frames()
		_assert_no_overlap(scene.city_overlay, "route %s" % corp)
		var s := RunManager.netrun
		s.run.current_node_id = s.run.map.first_layer_ids()[0]
		scene._show_map()
		await _frames()
		_assert_no_overlap(scene.city_overlay, "route %s under way" % corp)
		var win := (scene.find_child("RouteNodes", true, false) as Control)
		while win != null and not (win is TerminalWindow):
			win = win.get_parent() as Control
		assert_not_null(win, "the route window")
		for scale in SELECT_SCALES:
			Settings.set_text_scale(scale)
			var overlay: CityMapOverlay = scene.city_overlay
			overlay.avoid_controls([win])
			var here := overlay.here_id()
			assert_true(overlay.label_rects().has(String(here)), "%s x%.1f: YOU ARE HERE shows" % [corp, scale])
			_assert_on_screen(overlay, "route %s x%.1f" % [corp, scale])
		Settings.set_text_scale(1.0)
		await _close(scene)
