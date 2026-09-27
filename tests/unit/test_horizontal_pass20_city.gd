extends GutTest
## H20 city backdrop: the baked city's cache key (same look = same key, a territory change
## = a new key), the territory influence (deterministic; claimed Sites lean to the Cell,
## Seized ones to the corporation), the headless fallback (procedural, no bake, no
## crash), map legends on the raid maps following the Options switch live, non-colour
## marks for claimed / Seized Sites, REBEL_CELL's colour apart from the Cell pink, and the
## mid-run raid playout on the city overlay.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"

var _legend_before: bool = true


func before_all() -> void:
	_legend_before = Settings.map_legend


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_city_h20"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
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


func _first_link() -> StringName:
	var grid_data := RunManager.corporation.city_grid
	return grid_data.get_site(grid_data.home_site_id).links[0]


func _net_city() -> NeonCity:
	var city: NeonCity = autofree(NeonCity.new())
	city.net_mode = true
	city.district = RunManager.corporation.id
	return city


# --- Bake cache key --------------------------------------------------------------------------

func test_the_same_look_gives_the_same_bake_key() -> void:
	RunManager.new_campaign(1)
	var a := _net_city()
	var b := _net_city()
	a.set_influence(CityInfluence.of(RunManager.campaign, RunManager.corporation))
	b.set_influence(CityInfluence.of(RunManager.campaign, RunManager.corporation))
	var region := Rect2(-640, -360, 1280, 720)
	assert_eq(a.bake_key(region), b.bake_key(region), "two cities with one look share one bake")
	assert_eq(a.bake_key(region), a.bake_key(region), "stable")
	# Re-applying an equal influence is a no-op (no re-frame, no re-bake).
	var before := a.influence
	a.set_influence(CityInfluence.of(RunManager.campaign, RunManager.corporation))
	assert_same(a.influence, before, "an unchanged territory keeps the same influence object")


func test_a_territory_change_gives_a_new_bake_key() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var city := _net_city()
	city.set_influence(CityInfluence.of(c, RunManager.corporation))
	var region := Rect2(-640, -360, 1280, 720)
	var k0 := city.bake_key(region)
	c.grid.sites[_first_link()]["status"] = GridState.SiteStatus.CLAIMED
	city.sync_influence()  # not following: nothing bound, so nothing changes
	assert_eq(city.bake_key(region), k0, "an unbound city ignores the campaign")
	city.bind_campaign(c, RunManager.corporation)
	assert_ne(city.bake_key(region), k0, "a claimed Site re-keys the bake")
	var k1 := city.bake_key(region)
	c.grid.sites[_first_link()]["status"] = GridState.SiteStatus.SEIZED
	city.sync_influence()
	assert_ne(city.bake_key(region), k1, "a Seized Site re-keys it again")
	assert_ne(city.bake_key(Rect2(0, 0, 1280, 720)), city.bake_key(region), "the region is part of the key")
	var look := city.look_key()
	city.focus_grid = Vector2(5, 5)
	assert_eq(city.look_key(), look, "the camera is not part of the look")


func test_heat_creep_is_baked_in_steps() -> void:
	var city: NeonCity = autofree(NeonCity.new())
	var region := Rect2(0, 0, 640, 360)
	city.corp_creep = 0.30
	var k := city.bake_key(region)
	city.corp_creep = 0.31
	assert_eq(city.bake_key(region), k, "a Heat point alone does not re-bake")
	city.corp_creep = 0.30 + NeonCity.CREEP_STEP
	assert_ne(city.bake_key(region), k)


func test_bake_scale_fits_the_pixel_budget() -> void:
	var huge := Rect2(0, 0, 10000, 6000)
	assert_true(CityBakeCache.fit_scale(huge, 1.5) * CityBakeCache.fit_scale(huge, 1.5) * huge.get_area() <= CityBakeCache.MAX_PIXELS + 1.0)
	assert_eq(CityBakeCache.fit_scale(Rect2(0, 0, 100, 100), 1.5), 1.5, "small regions keep the wanted scale")


func test_a_camera_inside_a_baked_region_reuses_it() -> void:
	RunManager.new_campaign(1)
	var city := _net_city()
	city.set_anchors_preset(Control.PRESET_TOP_LEFT)
	city.size = Vector2(1280, 720)
	city._camera()
	var region := city.bake_region()
	assert_true(region.encloses(city.view_rect().grow(NeonCity.REGION_MARGIN - 1.0)), "a bake covers the view and a margin")
	var look := city.look_key()
	CityBakeCache.clear()
	# Stand-in entries (headless has no renderer to bake with).
	CityBakeCache.store(city.bake_key(region), {"look": look, "region": region})
	assert_eq(CityBakeCache.find(look, city.view_rect()), city.bake_key(region), "the same camera reuses the bake")
	city.focus_grid = NeonCity.hq_of(city.district) + Vector2(3, 2)  # a small camera move
	city._camera()
	if region.encloses(city.view_rect()):
		assert_eq(CityBakeCache.find(look, city.view_rect()), city.bake_key(region), "a move inside the region reuses it")
	assert_eq(CityBakeCache.find("another look", city.view_rect()), "", "another look never borrows it")
	city.focus_grid = Vector2(200, -200)  # far away
	city._camera()
	assert_eq(CityBakeCache.find(look, city.view_rect()), "", "a view outside every region bakes anew")
	for k in CityBakeCache.CAPACITY + 2:
		CityBakeCache.store("k%d" % k, {"look": "x", "region": Rect2()})
	assert_eq(CityBakeCache._entries.size(), CityBakeCache.CAPACITY, "least recently used entries drop out")
	CityBakeCache.clear()


# --- Territory influence -----------------------------------------------------------------------

func test_influence_is_deterministic_and_leans_the_right_way() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var site := _first_link()
	var at: Vector2 = CityLayout.site_points(corp)[site]
	var base := CityInfluence.value_at(CityInfluence.of(c, corp), at)
	c.grid.sites[site]["status"] = GridState.SiteStatus.CLAIMED
	var claimed := CityInfluence.of(c, corp)
	assert_eq(CityInfluence.signature(claimed), CityInfluence.signature(CityInfluence.of(c, corp)), "deterministic")
	assert_gt(CityInfluence.value_at(claimed, at), base, "a claimed Site pulls toward the Cell")
	assert_eq(CityInfluence.color_for(claimed, 0.5), Palette.CELL_PINK)
	c.grid.sites[site]["status"] = GridState.SiteStatus.SEIZED
	var seized := CityInfluence.of(c, corp)
	assert_lt(CityInfluence.value_at(seized, at), CityInfluence.value_at(claimed, at), "Seized pulls back")
	assert_lt(CityInfluence.value_at(seized, at), base, "toward the corporation")
	assert_eq(CityInfluence.color_for(seized, -0.5), Palette.corp_color(corp.id))
	var far := at + Vector2(CityInfluence.RADIUS * 4.0, 0)
	assert_eq(CityInfluence.value_at(claimed, far) - CityInfluence.value_at(seized, far), 0.0, "the pull is local")


func test_raid_results_sway_the_corporate_territory() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var p := NeonCity.hq_of(corp.id)
	c.raids_won = 2
	var won := CityInfluence.value_at(CityInfluence.of(c, corp), p, corp.id)
	c.raids_won = 0
	c.raids_lost = 2
	var lost := CityInfluence.value_at(CityInfluence.of(c, corp), p, corp.id)
	assert_gt(won, lost, "won raids lean the district to the Cell, lost ones to the corporation")
	assert_eq(CityInfluence.value_at(CityInfluence.of(c, corp), p, &"meridian" if corp.id != &"meridian" else &"solace"), 0.0, "other territories are untouched")
	assert_eq(CityInfluence.of(null, corp), {}, "no campaign, no influence")


# --- Headless fallback ---------------------------------------------------------------------

func test_headless_never_bakes_and_still_draws_the_city() -> void:
	RunManager.new_campaign(1)
	assert_false(CityBakeCache.can_bake(), "the dummy renderer never bakes")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var bg := WireframeBackground.new()
	holder.add_child(bg)
	await _frames()
	assert_false(bg.city.is_baked(), "procedural fallback")
	assert_true(bg.city.follow_campaign, "the backdrop follows the campaign's territory")
	assert_false(bg.city.influence.is_empty(), "and reads its influence")
	assert_true(CityBakeCache._pending.is_empty(), "nothing waits on a readback")
	var overlay := CityMapOverlay.new(bg.city)
	bg.city.add_child(overlay)
	var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, [])
	overlay.set_graph(g["nodes"], g["edges"])
	await _frames()
	assert_eq(overlay.nodes.size(), g["nodes"].size(), "the overlay lays out on the procedural city")


# --- Legends and marks ----------------------------------------------------------------------

func _hq_with_raid() -> Control:
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var first := _first_link()
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	return hq


func _legends(root: Node) -> Array[MapLegend]:
	var out: Array[MapLegend] = []
	for n in root.find_children("MapLegend", "", true, false):
		if n is MapLegend and not n.is_queued_for_deletion():
			out.append(n)
	return out


func test_raid_setup_and_summary_maps_have_a_legend() -> void:
	var hq := _hq_with_raid()
	assert_false(RunManager.campaign.pending_raids.is_empty(), "the claim provoked a raid")
	hq.show_raid()
	await _frames()
	assert_eq(hq.panel_name, "raid")
	assert_eq(_legends(hq).size(), 1, "raid setup map has its key")
	hq.fight_raid()
	await _frames()
	assert_true(hq.panel_name in ["raid_summary", "end"])
	if hq.panel_name == "raid_summary":
		assert_eq(_legends(hq).size(), 1, "raid summary map has its key")


func test_raid_playout_map_has_a_legend() -> void:
	var hq := _hq_with_raid()
	# Headless plays out at once and moves on to the summary in the same call; the
	# playout panel is still in the tree (queued for deletion) with its legend.
	var none: Array[Dictionary] = []
	hq.show_raid_playout(none)
	var all := hq.find_children("MapLegend", "", true, false)
	assert_true(all.size() >= 2, "the playout (and then the summary) carry a legend")


func test_the_grid_legend_and_site_list_follow_the_switch_live() -> void:
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	hq.new_campaign(1)
	Settings.set_map_legend(true)
	hq.show_grid()
	await _frames()
	var legends := _legends(hq)
	assert_eq(legends.size(), 1)
	var legend := legends[0]
	var scroll: Control = legend._linked
	assert_not_null(scroll, "the Site list is linked to the legend")
	var with_legend := scroll.custom_minimum_size.y
	Settings.set_map_legend(false)
	assert_false(legend.visible, "legend hides live")
	assert_gt(scroll.custom_minimum_size.y, with_legend, "the Site list takes the room back live")
	Settings.set_map_legend(true)
	assert_true(legend.visible)
	assert_eq(scroll.custom_minimum_size.y, with_legend)


func test_claimed_and_seized_sites_carry_a_non_colour_mark() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var first := _first_link()
	c.grid.sites[first]["status"] = GridState.SiteStatus.SEIZED
	var g := CityLayout.grid_graph(c, RunManager.corporation, [])
	var marks := {}
	for n in g["nodes"]:
		marks[n["id"]] = n["mark"]
	assert_eq(marks[c.grid.home_site_id], CityMapOverlay.MARK_SPRAY, "claimed: spray ring")
	assert_eq(marks[first], CityMapOverlay.MARK_CROSS, "Seized: cross")
	var corporate := 0
	for id in marks:
		if c.grid.is_corporate(id):
			corporate += 1
			assert_eq(marks[id], "", "corporate Sites unmarked")
	assert_gt(corporate, 0)
	var overlay: CityMapOverlay = autofree(CityMapOverlay.new())
	overlay.set_graph(g["nodes"], g["edges"])
	assert_eq(overlay.mark_of(c.grid.home_site_id), CityMapOverlay.MARK_SPRAY)
	# The legend's status rows each have their own glyph (never colour alone).
	assert_ne(MapLegend.ROWS[0][0], MapLegend.ROWS[2][0], "claimed and corporate rows differ by glyph")
	assert_ne(MapLegend.ROWS[3][0], MapLegend.ROWS[2][0], "seized and corporate rows differ by glyph")


func test_rebel_cell_red_is_apart_from_the_cell_pink() -> void:
	var red := Palette.corp_color(&"rebel_cell")
	var pink := Palette.CELL_PINK
	var hue_gap := absf(red.h - pink.h)
	hue_gap = minf(hue_gap, 1.0 - hue_gap)
	assert_gt(hue_gap, 0.06, "hues apart (%.3f)" % hue_gap)
	assert_gt(absf(red.get_luminance() - pink.get_luminance()), 0.1, "and lightness apart")


# --- Mid-run raid playout -------------------------------------------------------------------

func test_the_mid_run_raid_playout_plays_on_the_city() -> void:
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load(NETRUN).instantiate())
	scene.start_run(1)
	await _frames()
	var none: Array[Dictionary] = []
	scene._show_raid_playout(none)
	assert_true(scene.playout.grid_view is CityMapOverlay, "threat markers drive the city overlay")
	assert_eq((scene.playout.grid_view as CityMapOverlay).city, scene.background.city)
	var legends := 0
	for n in scene.find_children("MapLegend", "", true, false):
		legends += 1
	assert_gt(legends, 0, "the raid map has its key")
	await _frames()
