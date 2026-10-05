extends GutTest
## H21 city maps: hover tooltips on the Grid, route and raid map nodes; the "you are here"
## mark on the route's current node; unreachable route nodes dimmed; distinct drawn node
## icons shared with the legend; map labels that follow the text size and never overlap
## (Grid and route, every corporation); the raid sway following each corporation's own
## Sites (Halcyon's Grid reaches past its district).
## The every-corporation Grid and route label sweeps are in test_city_map_sweeps.gd (Test
## suite optimization, docs/TEST_SUITE.md).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_c21_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
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


## Opens every corporation in the (test slot's) profile.
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


func _route(corp: StringName) -> Control:
	_open_all()
	RunManager.new_campaign(1, corp)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	await _frames()
	return scene


## Every placed node with a tooltip at its icon equal to the overlay's folded tip.
func _assert_tooltips(overlay: CityMapOverlay, what: String) -> void:
	var placed := 0
	for n in overlay.nodes:
		var at := overlay.icon_pos(n)
		if at.x == INF or not overlay.marker_shown(n):
			continue  # ART-5 5d: a hidden v4 Site is not on the map (no tooltip)
		placed += 1
		var tip := overlay._get_tooltip(at)
		assert_ne(tip, "", "%s node %s has a tooltip" % [what, n["id"]])
		assert_eq(tip, UiTip.fold(overlay.tip_of(n["id"])), "%s: the tooltip is the node's tip" % what)
	assert_gt(placed, 0, "%s nodes stand on buildings" % what)
	assert_eq(overlay._get_tooltip(Vector2(-5000, -5000)), "", "no tooltip off the nodes")


# --- Tooltips -------------------------------------------------------------------------------

func test_grid_nodes_have_tooltips() -> void:
	var hq: Control = await _hq_grid(&"solace")
	var overlay: CityMapOverlay = hq.city_overlay
	_assert_tooltips(overlay, "Grid")
	var home := RunManager.campaign.grid.home_site_id
	assert_string_contains(overlay.tip_of(home), CityLayout.HOME_LABEL)
	for n in overlay.nodes:
		var sd := CampaignRules.site_data(RunManager.corporation, n["id"])
		if n["id"] != home:
			assert_string_contains(overlay.tip_of(n["id"]), sd.display_name, "the tip names the Site")
			assert_string_contains(overlay.tip_of(n["id"]), "T%d" % sd.tier, "and its tier")


func test_route_nodes_have_tooltips() -> void:
	var scene: Control = await _route(&"solace")
	var overlay: CityMapOverlay = scene.city_overlay
	_assert_tooltips(overlay, "route")
	for n in overlay.nodes:
		assert_ne(String(n.get("kind", "")), "", "route node %s has an icon kind" % n["id"])


func test_raid_nodes_have_tooltips() -> void:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var first: StringName = RunManager.corporation.city_grid.get_site(c.grid.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	assert_false(c.pending_raids.is_empty(), "the claim provoked a raid")
	hq.show_raid()
	await _frames()
	_assert_tooltips(hq.city_overlay, "raid")


func test_a_node_without_a_tip_gets_one_from_what_it_carries() -> void:
	var overlay: CityMapOverlay = autofree(CityMapOverlay.new())
	var ns: Array[Dictionary] = [{"id": &"a", "at": Vector2.ZERO, "label": "Relay Nine", "kind": CityMapOverlay.KIND_EXPLOIT, "mark": CityMapOverlay.MARK_SPRAY}]
	var es: Array[Dictionary] = []
	overlay.set_graph(ns, es)
	overlay.markers = {&"a": ["Sweeper"]}
	var tip := overlay.tip_of(&"a")
	assert_string_contains(tip, "Relay Nine")
	assert_string_contains(tip, "Exploit")
	assert_string_contains(tip, "Claimed")
	assert_string_contains(tip, "Sweeper", "threats on the node are named")


# --- You are here, unreachable nodes --------------------------------------------------------

func test_the_route_marks_you_are_here_and_dims_what_you_cannot_reach() -> void:
	var scene: Control = await _route(&"solace")
	var s := RunManager.netrun
	var first := s.run.map.first_layer_ids()
	assert_gt(first.size(), 0)
	# At the start nothing is behind you: every node lies ahead.
	var overlay: CityMapOverlay = scene.city_overlay
	assert_eq(overlay.here_id(), &"", "not on the map yet")
	for n in overlay.nodes:
		assert_false(overlay.is_dimmed(n["id"]), "everything is still reachable at the start")
	# Step onto the first node (view state only) and redraw the route.
	s.run.current_node_id = first[0]
	scene._show_map()
	await _frames()
	overlay = scene.city_overlay
	assert_eq(overlay.here_id(), first[0], "the current node carries the you-are-here mark")
	assert_false(overlay.is_dimmed(first[0]))
	assert_true(Array(overlay.label_lines(first[0])).has(CityMapOverlay.HERE_LABEL), "and says so")
	assert_true(overlay.label_rects().has(String(first[0])), "the you-are-here label is drawn")
	assert_string_contains(overlay.tip_of(first[0]), "You are here")
	for id in s.available_nodes():
		assert_false(overlay.is_dimmed(id), "open nodes stay lit")
		assert_string_contains(overlay.tip_of(id), "move here")
	var dimmed := 0
	for n in overlay.nodes:
		if n["id"] in first and n["id"] != first[0]:
			assert_true(overlay.is_dimmed(n["id"]), "the other entry nodes are out of reach")
			assert_eq(overlay.label_lines(n["id"]).size(), 0, "dimmed nodes carry no label")
			dimmed += 1
	assert_eq(dimmed, first.size() - 1)
	# The Server Rack stays ahead of you (every path ends there).
	for n in overlay.nodes:
		if n["kind"] == CityMapOverlay.KIND_RACK:
			assert_false(overlay.is_dimmed(n["id"]), "the Rack is still ahead")


func test_grid_nodes_are_never_dimmed() -> void:
	var hq: Control = await _hq_grid(&"solace")
	for n in hq.city_overlay.nodes:
		assert_false(hq.city_overlay.is_dimmed(n["id"]))


# --- Icons ----------------------------------------------------------------------------------

func test_node_icons_are_distinct_and_the_legend_draws_them() -> void:
	var route := [CityMapOverlay.KIND_FIGHT, CityMapOverlay.KIND_ELITE, CityMapOverlay.KIND_SHOP, CityMapOverlay.KIND_EVENT, CityMapOverlay.KIND_RACK]
	var grid := [CityMapOverlay.KIND_EXPLOIT, CityMapOverlay.KIND_HEAT, CityMapOverlay.KIND_CENTRAL_SERVER, CityMapOverlay.KIND_HOME, CityMapOverlay.KIND_TIER]
	for kinds in [route, grid]:
		var shapes := {}
		for kind in kinds:
			shapes[str(CityMapOverlay.icon_shape(kind, Vector2.ZERO, 10.0))] = kind
		assert_eq(shapes.size(), kinds.size(), "each kind on a map has its own silhouette: %s" % [kinds])
	assert_eq(CityMapOverlay.route_kind(RC.InfilNodeType.ROUTER, true), CityMapOverlay.KIND_ELITE)
	assert_eq(CityMapOverlay.route_kind(RC.InfilNodeType.MAINFRAME, false), CityMapOverlay.KIND_SHOP)
	assert_eq(CityMapOverlay.route_kind(RC.InfilNodeType.SERVER_RACK, false), CityMapOverlay.KIND_RACK)
	assert_true(CityMapOverlay.ICON_RADIUS >= 12.0, "icons read at a glance")
	# The legend's icon rows are exactly the Grid's kinds, drawn by the map's painter.
	var legend: MapLegend = autofree(MapLegend.new(&"solace"))
	for kind in grid:
		assert_not_null(legend.body.get_node_or_null("Icon_%s" % kind), "legend row for %s" % kind)
	RunManager.new_campaign(1)
	var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, [])
	for n in g["nodes"]:
		assert_true(String(n["kind"]) in grid, "every Grid node's icon is in the legend")


# --- Labels ---------------------------------------------------------------------------------

func test_label_size_follows_the_text_scale_live() -> void:
	var hq: Control = await _hq_grid(&"solace")
	var overlay: CityMapOverlay = hq.city_overlay
	Settings.set_text_scale(1.0)
	var base := overlay.label_font_size()
	assert_true(base * overlay.city.scale.x >= CityMapOverlay.TAG_FONT - 1, "labels read at %d px on screen" % CityMapOverlay.TAG_FONT)
	Settings.set_text_scale(1.5)
	assert_almost_eq(float(overlay.label_font_size()), base * 1.5, 1.0, "labels grow with the text size")
	assert_true(Settings.changed.is_connected(overlay._queue_top), "and redraw when it changes")
	# H24 K1: a label may take two lines where one has no room, so compare the height of a
	# line (the box over its line count).
	var wide := {}
	for l: Dictionary in overlay._layout_labels():
		wide[l["key"]] = (l["rect"] as Rect2).size.y / (l["lines"] as PackedStringArray).size()
	Settings.set_text_scale(1.0)
	var narrow := {}
	for l: Dictionary in overlay._layout_labels():
		narrow[l["key"]] = (l["rect"] as Rect2).size.y / (l["lines"] as PackedStringArray).size()
	for key in narrow:
		if wide.has(key):
			assert_gt(float(wide[key]), float(narrow[key]), "bigger boxes at a bigger text size")
			break


func test_label_layout_is_deterministic() -> void:
	var hq: Control = await _hq_grid(&"halcyon")
	var overlay: CityMapOverlay = hq.city_overlay
	assert_eq(str(overlay.label_rects()), str(overlay.label_rects()), "same graph, same camera, same layout")


# --- Influence follows each corporation's Sites ----------------------------------------------

func test_raid_sway_covers_each_corporations_own_sites() -> void:
	var city: NeonCity = autofree(NeonCity.new())
	var outside_halcyon := 0
	for corp in CORPS:
		RunManager.reset()
		_open_all()
		RunManager.new_campaign(1, corp)
		var c := RunManager.campaign
		var corporation := RunManager.corporation
		assert_eq(corporation.id, corp)
		c.raids_won = 4
		var inf := CityInfluence.of(c, corporation)
		var points := CityLayout.site_points(corporation)
		for id in points:
			var p: Vector2 = points[id]
			var terr := city.territory_at(floori(p.x), floori(p.y))
			if corp == &"halcyon" and terr != corp:
				outside_halcyon += 1
			assert_eq(CityInfluence.sway_share(inf, p, terr), 1.0, "%s: the sway reaches Site %s" % [corp, id])
			# The building the maps put the Site on (within a few lots) is swayed too.
			for off: Vector2 in [Vector2(2, 0), Vector2(0, -2), Vector2(-2, 2)]:
				var q := p + off
				assert_eq(CityInfluence.sway_share(inf, q, city.territory_at(floori(q.x), floori(q.y))), 1.0)
			assert_gt(CityInfluence.value_at(inf, p, terr), 0.0, "%s: a won raid tints Site %s toward the Cell" % [corp, id])
		c.raids_won = 0
		c.raids_lost = 4
		var lost := CityInfluence.of(c, corporation)
		assert_ne(CityInfluence.signature(lost), CityInfluence.signature(inf), "a different sway re-keys the bake")
	assert_gt(outside_halcyon, 0, "Halcyon's Grid reaches past its district (the case H21 #22 fixes)")


func test_the_sway_stays_local_to_the_sites() -> void:
	_open_all()
	RunManager.new_campaign(1, &"halcyon")
	var c := RunManager.campaign
	c.raids_won = 4
	var inf := CityInfluence.of(c, RunManager.corporation)
	var far := NeonCity.hq_of(&"solace")
	assert_eq(CityInfluence.sway_share(inf, far, &"solace"), 0.0, "another corporation's district far from the Sites is untouched")
	assert_eq(CityInfluence.signature(inf), CityInfluence.signature(CityInfluence.of(c, RunManager.corporation)), "deterministic")
