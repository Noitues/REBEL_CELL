extends GutTest
## S-MAPVIEW (designer ruling 2026-10-05, DECISIONS "Designer ruling — city as a map in raid and
## netrun views"): on the raid views and the netrun route the city is a map (greyed, its
## contrast and opacity lowered, its ambient motion under a veil; CityView3D map mode, numbers
## in CityConfig), on for the RAID and NETRUN bands and off everywhere else; the marks keep
## their contrast over the dimmed city (fixtures: the map-mode render, windowed); the raid view
## keeps the major (raid) nodes only (RaidMapNodes); a netrun's route nodes sit along the link
## it jacks along (RouteLinkLayout), deterministic on seeded replays, the jack riding the same
## link. Headless (nothing renders; the looks are read windowed with raid_lab / netrun_states).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CFG := preload("res://content/config/city_config.tres")
const FIXTURES := "res://tests/fixtures/mapview/"
## WCAG 1.4.11: non-text marks (rings, links, pencil) against what is next to them.
const MARK_MIN := 3.0
## The model part for the CityView3D checks (lots).
const PART := Rect2i(20, -4, 20, 20)
const NODE_TYPES: Array[StringName] = [&"firewall_relay", &"vault_terminal", &"relay", &"safehouse", &"proxy_relay"]

var cfg: CityConfig = CFG
var model: CityModel


func before_all() -> void:
	model = CityModel.build(cfg, 7, PART)


func before_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_s_mapview"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


## raid_lab's campaign: five claimed nodes against `corp`, raids pending.
func _raid_campaign(corp: StringName = &"solace") -> void:
	RunManager.new_campaign(7, corp)
	var c := RunManager.campaign
	c.schematics = 500
	for t in NODE_TYPES:
		var open := CampaignRules.launchable_sites(c, RunManager.corporation, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), run)
		CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), open[0].id, t)
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")


# --- Map mode --------------------------------------------------------------------------------

func test_map_mode_is_on_for_the_raid_and_netrun_bands_only() -> void:
	assert_true(CityView3D.map_band(cfg, CityLod.Band.RAID), "raid views")
	assert_true(CityView3D.map_band(cfg, CityLod.Band.NETRUN), "the netrun route")
	assert_false(CityView3D.map_band(cfg, CityLod.Band.GRID), "the Grid (and the blurred backdrop, which holds GRID)")
	assert_false(CityView3D.map_band(cfg, -1), "no band: the title, the combat backdrop, the HQ-run views")
	var view := CityView3D.new()
	view.size = Vector2i(320, 180)
	view.use_model(model)
	add_child_autofree(view)
	assert_false(view.map_mode, "off by default")
	assert_eq(view.map_look(), {"map_on": false, "veil": false, "halo": cfg.net_halo})
	for band in [CityLod.Band.RAID, CityLod.Band.NETRUN]:
		view.band_lock = band
		assert_true(view.map_mode)
		assert_eq(view.map_look(), {"map_on": true, "veil": true, "halo": cfg.net_halo * cfg.map_net_halo}, "band %d" % band)
	view.band_lock = CityLod.Band.GRID
	assert_eq(view.map_look(), {"map_on": false, "veil": false, "halo": cfg.net_halo}, "back off on the Grid")


func test_the_veil_dims_the_ambient_layers_and_never_the_network() -> void:
	# Drawn after the post (-100) and the ambient layers (holo / pools 10, beams 11), before the
	# network decal (19, its x-ray 20): the city's life is veiled, the links stay full.
	assert_gt(CityMaterials.MAP_VEIL_PRIORITY, 11)
	assert_lt(CityMaterials.MAP_VEIL_PRIORITY, CityMaterials.network(cfg, false).render_priority)
	assert_lt(CityMaterials.MAP_VEIL_PRIORITY, CityMaterials.network(cfg, true).render_priority)
	assert_gt(cfg.map_veil_alpha, 0.0)
	assert_lt(cfg.map_veil_alpha, 0.5, "slightly: the city still reads through it")
	assert_lt(cfg.map_saturation, 1.0, "greyed")
	assert_gt(cfg.map_saturation, 0.0, "slightly: the night look stays underneath")


func test_the_map_grade_greys_and_dims_but_keeps_the_night_hue() -> void:
	var neon := Color(0.95, 0.2, 0.75)
	var g := CityView3D.map_graded(cfg, neon)
	assert_lt(g.s, neon.s, "greyer")
	assert_lt(Palette.luminance(g), Palette.luminance(neon), "dimmer")
	assert_almost_eq(g.h, neon.h, 0.08, "the same hue")
	var night := Color(0.2, 0.19, 0.27)
	assert_lt(absf(Palette.luminance(CityView3D.map_graded(cfg, night)) - Palette.luminance(night)), 0.05,
		"the mid-tones stay about where they were (the night look underneath)")


func test_the_raid_and_route_pages_hold_the_map_bands_and_the_grid_does_not() -> void:
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(2)
	hq.show_raid()
	await _frames(3)
	assert_true(CityView3D.map_band(cfg, hq.wireframe.city.band_lock), "the raid setup is a map")
	hq.show_grid()
	await _frames(3)
	assert_false(CityView3D.map_band(cfg, hq.wireframe.city.band_lock), "the Grid page is not")
	var net := _scene(NETRUN)
	RunManager.new_campaign(1)
	net.start_run(1)
	await _frames(3)
	assert_true(CityView3D.map_band(cfg, net.background.city.band_lock), "the netrun route is a map")


func _fixture(shot: String) -> Image:
	var img := Image.new()
	if img.load(ProjectSettings.globalize_path(FIXTURES + shot + ".png")) != OK:
		return null
	return img


## The p-th share luminance of the fixture (the city in map mode as rendered windowed).
static func _percentile(img: Image, p: float) -> float:
	var ls: Array[float] = []
	for y in range(0, img.get_height(), 2):
		for x in range(0, img.get_width(), 2):
			ls.append(Palette.luminance(img.get_pixel(x, y)))
	ls.sort()
	return ls[clampi(int(p * ls.size()), 0, ls.size() - 1)]


static func _ratio(a: float, b: float) -> float:
	return (maxf(a, b) + 0.05) / (minf(a, b) + 0.05)


func test_the_marks_keep_their_contrast_over_the_dimmed_city() -> void:
	# The marks against the city's bright part (90th percentile luminance) as the map mode
	# renders it (fixtures `<shot>.png`: the 3D city's own render, the network decal off), and
	# the same city without the map mode (`<shot>_off.png`). Raid marks: the Cell's links and
	# nodes; route marks: the ring states. CORE (a keylined sticker) and the red pencil (a thin
	# line, which also reads by its dark shadow stroke) against the city's typical part (median).
	var raid := {"your link / node": Palette.CELL_TURF}
	var route := {"walked": RouteInk.RING_WALKED, "selectable": RouteInk.RING_AVAILABLE, "not yet": RouteInk.RING_UNAVAILABLE}
	var pencil := Palette.luminance(RouteInk.PENCIL_THREAT)
	assert_gte(_ratio(pencil, Palette.luminance(RouteInk.PENCIL_SHADOW)), MARK_MIN, "the pencil on its shadow")
	for shot in ["raid_solace", "raid_meridian", "route_solace"]:
		var img := _fixture(shot)
		var off := _fixture(shot + "_off")
		assert_not_null(img, "fixture %s" % shot)
		assert_not_null(off, "fixture %s_off" % shot)
		if img == null or off == null:
			continue
		var l90 := _percentile(img, 0.9)
		var off90 := _percentile(off, 0.9)
		assert_lt(l90, off90, "%s: the map holds the city's bright part down (%.3f, was %.3f)" % [shot, l90, off90])
		var marks: Dictionary = raid if shot.begins_with("raid") else route
		for k: String in marks:
			assert_gte(_ratio(Palette.luminance(marks[k]), l90), MARK_MIN, "%s: %s over the map (city p90 %.3f)" % [shot, k, l90])
		var l50 := _percentile(img, 0.5)
		assert_gte(_ratio(pencil, l50), MARK_MIN, "%s: the threat pencil over the map (city p50 %.3f)" % [shot, l50])
		if shot.begins_with("raid"):
			assert_gte(_ratio(Palette.luminance(Palette.CELL_PINK), l50), MARK_MIN, "%s: CORE (keylined sticker) over the map" % shot)
		assert_lte(l50, _percentile(off, 0.5), "%s: and the city's typical part no brighter than before" % shot)


# --- The raid view's nodes -------------------------------------------------------------------

func test_the_raid_view_keeps_the_major_nodes_only() -> void:
	_raid_campaign()
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var proj := RunManager.project_raid()
	var routes := RaidMapNodes.shown_routes(proj, c, corp, RunManager.config(), RunManager.lookup())
	var ids := RaidMapNodes.major_ids(c, routes, proj.nodes)
	for id in c.grid.claimed_ids():
		assert_true(ids.has(id), "the Cell's node %s" % id)
	for p in routes:
		assert_true(ids.has(p[0]), "the entry %s the raid takes" % p[0])
	var frontier := RaidResolver.default_entry_sites(c, corp.city_grid)
	var dropped := 0
	for id in frontier:
		if not ids.has(id):
			dropped += 1
	assert_gt(dropped, 0, "the frontier Sites no threat enters at are off the raid map")
	for id: StringName in ids:
		assert_not_null(CampaignRules.site_data(corp, id), "%s is a Grid Site (never a netrun sub-node)" % id)
	# The playout's start (no results) projects the same raid: the same routes.
	assert_eq(RaidMapNodes.shown_routes({}, c, corp, RunManager.config(), RunManager.lookup()), routes)


func test_the_raid_maps_routes_are_the_raids_own() -> void:
	_raid_campaign(&"meridian")
	var proj := RunManager.project_raid()
	var preview := RaidMapNodes.shown_routes(proj, RunManager.campaign, RunManager.corporation, RunManager.config(), RunManager.lookup())
	var events := RunManager.fight_raid()
	assert_eq(preview, RaidMapNodes.route_paths(events), "preview == result: the map shows the routes the raid takes")
	var after := RaidMapNodes.major_ids(RunManager.campaign, RaidMapNodes.shown_routes(RunManager.campaign.last_raid["nodes"],
		RunManager.campaign, RunManager.corporation, RunManager.config(), RunManager.lookup()), RunManager.campaign.last_raid["nodes"])
	for id in RunManager.campaign.last_raid["nodes"]:
		assert_true(after.has(StringName(String(id))), "the report keeps %s the raid reached" % id)


# --- The netrun route along its link ---------------------------------------------------------

func _route_points(seed_v: int) -> Dictionary:
	RunManager.reset()
	var net := _scene(NETRUN)
	RunManager.new_campaign(seed_v)
	net.start_run(1)
	var g: Dictionary = net.route_graph()
	var out := {"entry": g["entry"]}
	for n in g["nodes"]:
		out[n["id"]] = n["at"]
	var s := RunManager.netrun
	out["link"] = RouteLinkLayout.link_of(cfg, RunManager.corporation, s.campaign, s.run.site_id, CityLayout.site_points(RunManager.corporation))
	out["from"] = RouteLinkLayout.from_site(RunManager.corporation, s.campaign, s.run.site_id)
	out["site"] = s.run.site_id
	out["widest"] = 0
	for li in range(1, s.run.map.layer_count() + 1):
		out["widest"] = maxi(int(out["widest"]), s.run.map.nodes_in_layer(li).size())
	out["final"] = s.run.map.final_node_id()
	net.get_parent().queue_free()
	return out


func test_every_route_node_lies_on_the_link_between_two_raid_nodes() -> void:
	for seed_v in [1, 2, 5]:
		var r := _route_points(seed_v)
		var link: PackedVector2Array = r["link"]
		var points := CityLayout.site_points(RunManager.corporation)
		assert_ne(r["from"], &"", "seed %d: the run jacks in from a node of the Cell" % seed_v)
		assert_eq(link[1], points[r["site"]], "the link ends on the run's Site")
		if (points[r["site"]] - points[r["from"]]).length() >= cfg.route_link_min_lots:
			assert_eq(link[0], points[r["from"]], "and starts on the Cell's node")
		var tol := (int(r["widest"]) - 1) * 0.5 * cfg.route_link_lateral + 0.001
		for id in r:
			if r[id] is Vector2 and String(id).begins_with("L"):
				assert_lte(RouteLinkLayout.off_link(r[id], link), tol, "seed %d: %s on the link" % [seed_v, id])
		assert_almost_eq((r[r["final"]] as Vector2).distance_to(link[1]), 0.0, 0.001, "the final Rack on the target Site")
		assert_eq(r["entry"], link[0], "the Cell starts at the link's own end")


func test_route_placement_is_deterministic_on_seeded_replays() -> void:
	var a := _route_points(3)
	var b := _route_points(3)
	assert_eq(a, b, "same seed, same places")


func test_the_jack_rides_the_link_the_route_sits_on() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	for sd in CampaignRules.launchable_sites(c, corp, RunManager.config()):
		var from := RouteLinkLayout.from_site(corp, c, sd.id)
		var jack := RunManager.jack_link(sd.id)
		var from_site := CampaignRules.site_data(corp, from)
		var want := "_".join(TextDb.t(from_site, "display_name").to_upper().split(" ", false)) if from_site != null else "RELAY"
		assert_eq(jack["from"], want, "%s: the jack starts where the route does" % sd.id)


func test_layers_spread_across_the_link_in_node_order() -> void:
	var m := MapGraph.new()
	m.layers = [[{"id": &"L1N0", "layer": 1, "index": 0, "next": []}],
		[{"id": &"L2N1", "layer": 2, "index": 1, "next": []}, {"id": &"L2N0", "layer": 2, "index": 0, "next": []}],
		[{"id": &"L3N0", "layer": 3, "index": 0, "next": []}]]
	var link := PackedVector2Array([Vector2(0, 0), Vector2(12, 0)])
	var p: Dictionary = RouteLinkLayout.place(cfg, m, link)
	var at: Dictionary = p["nodes"]
	assert_eq(at[&"L1N0"], Vector2(4, 0))
	assert_eq(at[&"L3N0"], Vector2(12, 0), "the last layer on the target")
	assert_almost_eq((at[&"L2N0"] as Vector2).x, 8.0, 0.001)
	assert_almost_eq((at[&"L2N0"] as Vector2).y, -cfg.route_link_lateral * 0.5, 0.001, "index 0 first across the link")
	assert_almost_eq((at[&"L2N1"] as Vector2).y, cfg.route_link_lateral * 0.5, 0.001)
	assert_eq(p["entry"], Vector2.ZERO)
