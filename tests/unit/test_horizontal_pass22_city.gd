extends GutTest
## H22 city maps: labels stay inside the visible map and out of a screen's side column
## (every node of every corporation selected in turn, at text scale 1.0 and 1.6; the
## route's YOU ARE HERE too); map labels and tips use translated Site names (TextDb); the
## map legend and the HQ mini-map follow the text size; the tier difficulty pips are on
## the map, the mini-map and in the legend.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, 1.6]
const TEST_LOCALE := "xx"

var _text_scale_before: float = 1.0
var _translation: Translation = null
var _locale_before: String = "en"


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_c22_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	if _translation != null:
		TranslationServer.set_locale(_locale_before)
		TranslationServer.remove_translation(_translation)
		_translation = null
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
	holder.size = Vector2(1280, 720)
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _open_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


func _hq_grid(corp: StringName) -> Control:
	var hq := _scene(HQ)
	_open_all()
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
	hq.show_grid()
	await _frames()
	return hq


## Every label inside the overlay's label area and off its blocked screen areas.
func _assert_on_screen(overlay: CityMapOverlay, what: String) -> void:
	var area := overlay.label_area()
	var blocks := overlay.label_blocks()
	var rects := overlay.label_rects()
	for key in rects:
		var r: Rect2 = rects[key]
		assert_true(area.grow(0.01).encloses(r), "%s: label %s %s inside the map %s" % [what, key, r, area])
		for b in blocks:
			assert_false(r.intersects(b), "%s: label %s %s clear of the side column %s" % [what, key, r, b])


# --- Labels on screen -----------------------------------------------------------------------

func test_the_overlay_covers_the_screen_and_reads_the_side_column() -> void:
	var hq: Control = await _hq_grid(&"solace")
	var overlay: CityMapOverlay = hq.city_overlay
	var screen := overlay.get_global_transform_with_canvas() * Rect2(Vector2.ZERO, overlay.size)
	assert_almost_eq(screen.position.x, 0.0, 1.0, "the overlay starts at the screen's left edge")
	assert_almost_eq(screen.size.x, 1280.0, 2.0, "and spans it")
	# The Grid registers its side column (H22 screens wired avoid_controls).
	assert_false(overlay.label_blocks().is_empty(), "the Grid's column is blocked for labels")
	var column := hq.find_child("GridColumn", true, false) as Control
	overlay.avoid_controls([column])
	assert_eq(overlay.label_blocks().size(), 1, "the side column is blocked")
	var local_col: Rect2 = overlay.label_blocks()[0]
	var back := overlay.get_global_transform_with_canvas() * local_col
	assert_almost_eq(back.position.x, column.get_global_rect().position.x, 1.0, "at the column's place on screen")
	assert_true(column.item_rect_changed.is_connected(overlay._top.queue_redraw), "labels move when the column does")
	# Rects work too (viewport px), and an explicit screen rect narrows the area.
	overlay.set_blocked_rects([Rect2(0, 0, 100, 720)])
	assert_eq(overlay.label_blocks().size(), 2)
	overlay.screen_rect = Rect2(0, 0, 640, 720)
	assert_true(overlay.label_area().end.x <= (overlay.get_global_transform_with_canvas().affine_inverse() * Rect2(0, 0, 640, 720)).end.x + 0.01)


func test_grid_labels_stay_on_screen_for_every_node_of_every_corporation() -> void:
	for corp in CORPS:
		RunManager.reset()
		var hq: Control = await _hq_grid(corp)
		var overlay: CityMapOverlay = hq.city_overlay
		overlay.avoid_controls([hq.find_child("GridColumn", true, false) as Control])
		var c := RunManager.campaign
		var paths := CityLayout.threat_paths(c, RunManager.corporation)
		var ids: Array[StringName] = []
		for n in overlay.nodes:
			ids.append(n["id"])
		for scale in SCALES:
			Settings.set_text_scale(scale)
			for id in ids:
				var g := CityLayout.grid_graph(c, RunManager.corporation, paths, id)
				overlay.set_graph(g["nodes"], g["edges"])
				overlay.selected_id = id
				var rects := overlay.label_rects()
				assert_true(rects.has(String(id)), "%s x%.1f: the selected %s has its label" % [corp, scale, id])
				_assert_on_screen(overlay, "%s x%.1f selected %s" % [corp, scale, id])
			# The landmarks keep their labels too (the boss Site was clipped for four
			# corporations).
			var g0 := CityLayout.grid_graph(c, RunManager.corporation, paths, c.grid.home_site_id)
			overlay.set_graph(g0["nodes"], g0["edges"])
			overlay.selected_id = c.grid.home_site_id
			for n in overlay.nodes:
				if n.get("big", false):
					assert_true(overlay.label_rects().has(String(n["id"])), "%s x%.1f: landmark %s labelled" % [corp, scale, n["id"]])
		Settings.set_text_scale(1.0)
		hq.get_parent().queue_free()
		await _frames(1)


func test_a_focus_label_moves_inward_when_its_node_is_at_the_edge() -> void:
	var hq: Control = await _hq_grid(&"solace")
	var overlay: CityMapOverlay = hq.city_overlay
	var area := overlay.label_area()
	# Block everything but a strip at the left: every label that shows lies in the strip,
	# and the selected one always shows. H23 #2 (on purpose): a node under the blocked part
	# has no label at all now, so the selected node is the one nearest the strip's edge.
	var strip := 260.0
	var col := overlay.get_global_transform_with_canvas() * Rect2(area.position.x + strip, area.position.y - 10.0, area.size.x, area.size.y + 20.0)
	overlay.set_blocked_rects([col])
	var id: StringName = &""
	var best := -INF
	for n in overlay.nodes:
		var x: float = overlay.icon_pos(n).x
		if x < area.position.x + strip and x > best:
			best = x
			id = n["id"]
	assert_ne(id, &"", "a node in the strip")
	var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, [], id)
	overlay.set_graph(g["nodes"], g["edges"])
	overlay.selected_id = id
	var rects := overlay.label_rects()
	assert_true(rects.has(String(id)), "the selected label shows")
	_assert_on_screen(overlay, "left strip")


func test_route_you_are_here_stays_on_screen_for_every_corporation() -> void:
	for corp in CORPS:
		RunManager.reset()
		_open_all()
		RunManager.new_campaign(1, corp)
		var scene := _scene(NETRUN)
		scene.start_run(1)
		var s := RunManager.netrun
		s.run.current_node_id = s.run.map.first_layer_ids()[0]
		scene._show_map()
		await _frames()
		var win := (scene.find_child("RouteNodes", true, false) as Control)
		while win != null and not (win is TerminalWindow):
			win = win.get_parent() as Control
		assert_not_null(win, "the route window")
		for scale in SCALES:
			Settings.set_text_scale(scale)
			var overlay: CityMapOverlay = scene.city_overlay
			overlay.avoid_controls([win])
			var here := overlay.here_id()
			assert_true(overlay.label_rects().has(String(here)), "%s x%.1f: YOU ARE HERE shows" % [corp, scale])
			_assert_on_screen(overlay, "route %s x%.1f" % [corp, scale])
		Settings.set_text_scale(1.0)
		scene.get_parent().queue_free()
		await _frames(1)


# --- Translated names -----------------------------------------------------------------------

func test_map_labels_and_tips_use_translated_site_names() -> void:
	RunManager.new_campaign(1)
	var corp := RunManager.corporation
	var c := RunManager.campaign
	var site: SiteData = null
	for sd in corp.city_grid.sites:
		if sd != null and sd.id != c.grid.home_site_id:
			site = sd
			break
	_translation = Translation.new()
	_translation.locale = TEST_LOCALE
	_translation.add_message(TextDb.key_for(site, "display_name"), "XL_SITE")
	TranslationServer.add_translation(_translation)
	_locale_before = TranslationServer.get_locale()
	TranslationServer.set_locale(TEST_LOCALE)
	var g := CityLayout.grid_graph(c, corp, [], site.id)
	var found := false
	for n in g["nodes"]:
		if n["id"] == site.id:
			found = true
			assert_eq(n["label"], "XL_SITE", "the map label is translated")
			assert_string_contains(n["tip"], "XL_SITE", "and the tooltip")
			assert_false(String(n["tip"]).contains(site.display_name), "no raw name in the tip")
	assert_true(found)
	var mini: GridMapView = add_child_autofree(GridMapView.new())
	mini.size = Vector2(760, 380)
	mini.show_grid(c, corp)
	assert_string_contains(mini.site_label(site, false), "XL_SITE", "the mini-map label too")


# --- Legend and mini-map scale -----------------------------------------------------------

func _legend_font(legend: MapLegend) -> int:
	for l in legend.body.find_children("*", "Label", true, false):
		return (l as Label).get_theme_font_size("font_size")
	return 0


func test_the_legend_follows_the_text_size_live() -> void:
	Settings.set_text_scale(1.0)
	var legend: MapLegend = add_child_autofree(MapLegend.new(&"solace", true))
	await _frames(1)
	var small := _legend_font(legend)
	var small_h := legend.get_combined_minimum_size().y
	assert_eq(small, MapLegend.COMPACT_FONT)
	Settings.set_text_scale(1.6)
	await _frames(1)
	assert_eq(_legend_font(legend), roundi(MapLegend.COMPACT_FONT * 1.6), "rows grow with the text size")
	assert_gt(legend.get_combined_minimum_size().y, small_h * 1.3, "and the legend reports its taller size")
	var full: MapLegend = add_child_autofree(MapLegend.new(&"solace"))
	await _frames(1)
	assert_eq(_legend_font(full), roundi(MapLegend.FULL_FONT * 1.6), "the full legend too")


func test_a_pinned_legend_stays_inside_its_area_at_big_text() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var area: Control = add_child_autofree(Control.new())
		area.size = Vector2(900, 620)
		var legend := MapLegend.pin_to(area, &"solace")
		await _frames(3)
		var inner := Rect2(Vector2.ZERO, area.size)
		var r := Rect2(legend.position, legend.size)
		assert_true(inner.encloses(r), "x%.1f: legend %s inside its area" % [scale, r])
		assert_true(legend.size.y >= legend.get_combined_minimum_size().y - 0.5, "at its full height")
		assert_almost_eq(r.end.y, area.size.y - MapLegend.PIN_MARGIN, 1.0, "pinned to the bottom corner")
		# Growing the text later keeps the corner and grows it upward.
		Settings.set_text_scale(1.6 if scale < 1.6 else 1.3)
		await _frames(2)
		r = Rect2(legend.position, legend.size)
		assert_almost_eq(r.end.y, area.size.y - MapLegend.PIN_MARGIN, 1.0, "still pinned after a text size change")
		assert_true(legend.size.y >= legend.get_combined_minimum_size().y - 0.5, "at its new height")
		area.queue_free()
		await _frames(1)


func test_the_mini_map_labels_follow_the_text_size() -> void:
	RunManager.new_campaign(1)
	Settings.set_text_scale(1.0)
	var mini: GridMapView = add_child_autofree(GridMapView.new())
	mini.size = Vector2(420, 170)
	mini.show_grid(RunManager.campaign, RunManager.corporation)
	await _frames(2)
	assert_false(mini.drawn_labels.is_empty(), "the mini-map draws its labels")
	var base: int = mini.drawn_labels[0]["size"]
	assert_true(Settings.changed.is_connected(mini.queue_redraw), "redraws when the settings change")
	Settings.set_text_scale(1.6)
	await _frames(2)
	assert_eq(int(mini.drawn_labels[0]["size"]), roundi(base * 1.6), "T1/T2 labels grow with the text size")


# --- Tier pips ------------------------------------------------------------------------------

func test_tier_pips_on_the_map_the_mini_map_and_the_legend() -> void:
	var hq: Control = await _hq_grid(&"solace")
	var overlay: CityMapOverlay = hq.city_overlay
	var c := RunManager.campaign
	await _frames(1)
	assert_false(overlay.drawn_tiers.is_empty(), "the map draws tier pips")
	for n in overlay.nodes:
		var sd := CampaignRules.site_data(RunManager.corporation, n["id"])
		if n["id"] == c.grid.home_site_id:
			assert_false(overlay.drawn_tiers.has(n["id"]), "CORE has no difficulty")
		else:
			assert_eq(int(overlay.drawn_tiers.get(n["id"], 0)), sd.tier, "%s shows its tier in pips" % n["id"])
			var pips := overlay.tier_pips_rect(n)
			assert_true(pips.has_area())
			for key in overlay.label_rects():
				assert_false((overlay.label_rects()[key] as Rect2).intersects(pips), "label %s clears %s's pips" % [key, n["id"]])
	assert_string_contains(overlay.tip_of(overlay.nodes[1]["id"]), "difficulty", "the tip says what the pips mean")
	# The mini-map leads each label with the pips.
	var mini: GridMapView = add_child_autofree(GridMapView.new())
	mini.size = Vector2(420, 170)
	mini.show_grid(c, RunManager.corporation)
	await _frames(2)
	assert_eq(mini.drawn_tiers.size(), RunManager.corporation.city_grid.sites.filter(func(s: SiteData) -> bool: return s != null).size() - 1, "every Site but CORE")
	# The legend's tier row has room for the pips under its icon.
	var legend: MapLegend = add_child_autofree(MapLegend.new(&"solace"))
	var row := legend.body.get_node_or_null("Icon_%s" % CityMapOverlay.KIND_TIER)
	assert_not_null(row, "legend tier row")
	var swatch := row.get_node("Swatch") as Control
	assert_true(swatch.custom_minimum_size.y >= MapLegend.ICON_SWATCH + CityMapOverlay.tier_pips_size().y, "the row shows the pips")
	var lit := false
	for l in row.find_children("*", "Label", true, false):
		lit = lit or (l as Label).text.contains("pips")
	assert_true(lit, "and says what they mean")


func test_tier_pip_rows_scale_and_cap() -> void:
	var sz := CityMapOverlay.tier_pips_size(2.0)
	assert_almost_eq(sz.x, CityMapOverlay.tier_pips_size().x * 2.0, 0.01, "the row scales")
	assert_eq(CityMapOverlay.tier_of({"tier": 3}), 3)
	assert_eq(CityMapOverlay.tier_of({"tier": 9}), CityMapOverlay.TIER_PIPS_MAX, "capped at the row")
	assert_eq(CityMapOverlay.tier_of({}), 0, "route nodes have none")
