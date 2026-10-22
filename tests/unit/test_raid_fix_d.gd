extends GutTest
## RAID-FIX D (A-081): the Heat countdown chip hangs under the bar with its pointer on the raid tick and the
## threshold banner stands clear of the bar and the chip; THREAT INTEL pages so no threat's numbers are only a
## "+N more"; the setup's right column lies whole on screen at Heat 25 / 75 / 76 with a target picked and IF PLACED
## showing; the cobalt route keeps a thin core and a dark edge.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Vector2(1280, 720)
const HQ_SCRIPT := preload("res://scripts/ui/hq_scene.gd")
const MARKS: Array[int] = [25, 50, 75, 100]


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_raid_fix_d"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Settings.text_scale = 1.0


func after_each() -> void:
	Settings.text_scale = 1.0
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT


func test_the_route_keeps_a_thin_core_and_a_dark_edge() -> void:
	assert_almost_eq(RaidRouteLayer.CORE_SHARE, 0.18, 0.001, "the white-hot core is about 0.18 of the width")
	assert_gt(RaidRouteLayer.EDGE_SHARE, 1.0, "the dark edge is wider than the cobalt stroke")
	assert_eq(GreasePencilMark.ink_color(GreasePencilMark.Ink.THREAT_ROUTE), Palette.THREAT_ROUTE, "the cobalt stays its token")
	assert_eq(GreasePencilMark.ink_color(GreasePencilMark.Ink.THREAT_ROUTE).a, 1.0, "at full alpha")
	assert_lt(GreasePencilMark.ink_color(GreasePencilMark.Ink.THREAT_EDGE).get_luminance(), 0.2, "the edge is dark ink")


func _gauge(heat: int, at: int) -> HeatGauge:
	var g := HeatGauge.new()
	add_child_autofree(g)
	g.size = g.custom_minimum_size
	g.set_heat(heat, 100, MARKS)
	g.raid_next = {"at": at, "away": at - heat}
	return g


func test_the_chip_pointer_stands_on_the_tick() -> void:
	for pair in [[22, 25], [72, 75], [76, 100]]:
		var g := _gauge(pair[0], pair[1])
		var ptr := g.chip_pointer()
		assert_almost_eq(ptr[0].x, g.raid_tick_x(), 0.01, "Heat %d: the pointer's apex is on the tick" % pair[0])
		var c := g.chip_rect()
		assert_gte(ptr[0].x, c.position.x, "Heat %d: the tick is over the chip" % pair[0])
		assert_lte(ptr[0].x, c.end.x, "Heat %d: the tick is over the chip" % pair[0])
		assert_gte(c.position.y, g.size.y, "Heat %d: the chip hangs under the box" % pair[0])
		assert_eq(g.chip_words(), "RAID AT %d · %d AWAY" % [pair[1], pair[1] - pair[0]], "the words")


func test_the_banner_never_covers_the_bar_or_the_chip() -> void:
	Motion.force_live = true
	for pair in [[10, 25], [60, 75], [76, 100]]:
		var g := _gauge(pair[0], pair[1])
		g.set_heat(pair[0] + 15, 100, MARKS)
		g.raid_next = {"at": pair[1], "away": pair[1] - pair[0] - 15}
		g.complete_motion()
		var banner := Rect2()
		var first := true
		for p in g.banner_corners():
			banner = Rect2(p, Vector2.ZERO) if first else banner.expand(p)
			first = false
		assert_false(banner.intersects(Rect2(Vector2.ZERO, g.size)), "Heat %d: the banner is outside the gauge's box (%s)" % [pair[0], banner])
		assert_false(banner.intersects(g.chip_rect()), "Heat %d: the banner is clear of the chip (%s, %s)" % [pair[0], banner, g.chip_rect()])
	Motion.force_live = false


func test_the_banner_never_covers_the_help_plate() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	for kind in [true, false]:
		for pair in [[10, 25], [60, 75], [72, 76]]:
			var p := HeatPoster.new(kind)
			holder.add_child(p)
			p.size = p.custom_minimum_size if kind else Vector2(170, 134)
			p.position = Vector2(40, 200)
			p.heat = pair[1]
			p._banner_at = pair[1]
			p.banner_alpha = 1.0
			var note := p.note_rect()
			var banner := p.banner_global_bounds()
			assert_false(banner.intersects(note), "poster=%s Heat %d: the banner %s is clear of the help plate %s" % [kind, pair[1], banner, note])
			assert_true(p.note_avoid().has(banner), "the plate's search keeps off the banner")
			p.free()


func test_intel_pages_cover_every_route() -> void:
	for n in range(0, 9):
		var levels := HQ_SCRIPT.intel_levels(n)
		assert_false(levels.is_empty())
		var rows_whole := n <= HQ_SCRIPT.INTEL_ROWS_MAX
		for lv in levels:
			if FitBuildBox.step_of(lv) >= 1:
				var per_page := HQ_SCRIPT.INTEL_ROWS_MAX + 1 - FitBuildBox.step_of(lv)
				assert_gte(FitBuildBox.pages_of(lv) * per_page, n, "%d routes: the %d pages of %d rows list every route" % [n, FitBuildBox.pages_of(lv), per_page])
			elif lv == 0:
				assert_true(rows_whole, "%d routes: the whole panel only when every route has a row" % n)


func _raid_page(heat: int) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hq.new_campaign(7)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var classes: Array[ClassData] = []
	for id in [&"breaker", &"ghost", &"rigger"]:
		var cls := lookup.get_content(id) as ClassData
		if cls != null:
			classes.append(cls)
	if not classes.is_empty():
		DemoSetup.roster_of(c, classes)
	DemoSetup.set_schematics(c, 60)
	var types: Array[StringName] = [&"safehouse", &"firewall_relay", &"vault_terminal", &"relay", &"proxy_relay"]
	for i in 5:
		var open := CampaignRules.launchable_sites(c, corp, cfg)
		if open.is_empty():
			break
		CampaignRules.on_run_completed(c, corp, cfg, hq._demo_run(open[0].id))
		CampaignRules.claim(c, corp, cfg, lookup, open[0].id, types[i % types.size()])
	c.pending_raids.clear()
	DemoSetup.set_heat(c, heat - 4)
	DemoSetup.set_armory(c, [&"turret", &"ice_lock", &"decoy"] as Array[StringName])
	HeatRules.add_heat(c, 4, cfg, "Server Rack")
	hq.show_raid()
	for i in 12:
		await get_tree().process_frame
	for id in c.grid.claimed_ids():
		if id != c.grid.home_site_id and c.grid.is_active_node(id):
			hq.select_target(id)
			break
	for i in 12:
		await get_tree().process_frame
	hq.point_card(0)
	for i in 12:
		await get_tree().process_frame
	return hq


func test_the_right_column_lies_whole_on_screen_at_each_heat() -> void:
	for heat in [25, 75, 76]:
		var hq := await _raid_page(heat)
		var page: Control = hq._panel
		var screen := Rect2(Vector2.ZERO, SCREEN)
		var column := page.get_node("CardColumn") as Control
		var verb := page.get_node("VerbSlot") as Control
		var in_column: Array[Control] = []
		for n in ["ThreatIntel"]:
			var ctl := page.find_child(n, true, false) as Control
			assert_not_null(ctl, "Heat %d: %s is built" % [heat, n])
			if ctl != null:
				in_column.append(ctl)
		var net := hq._network_win as Control
		assert_not_null(net, "Heat %d: YOUR NETWORK" % heat)
		if net != null:
			in_column.append(net)
		assert_null(page.find_child("IfPlaced", true, false), "Heat %d: the floating IF PLACED terminal is retired (A-082)" % heat)
		var all: Array[Control] = in_column.duplicate()
		for ctl in all:
			assert_true(ctl.is_visible_in_tree(), "Heat %d: %s shows" % [heat, ctl.name])
			var r := ctl.get_global_rect()
			assert_true(screen.encloses(r), "Heat %d: %s on screen (%s)" % [heat, ctl.name, r])
			assert_false(r.grow(-0.5).intersects(verb.get_global_rect()), "Heat %d: %s clear of the Crew / STATION block (%s)" % [heat, ctl.name, r])
		for ctl in in_column:
			assert_true(column.get_global_rect().grow(1.0).encloses(ctl.get_global_rect()), "Heat %d: %s lies whole in the column, nothing clipped (%s in %s)" % [heat, ctl.name, ctl.get_global_rect(), column.get_global_rect()])
		for i in all.size():
			for j in range(i + 1, all.size()):
				assert_false(all[i].get_global_rect().grow(-0.5).intersects(all[j].get_global_rect().grow(-0.5)), "Heat %d: %s and %s do not overlap" % [heat, all[i].name, all[j].name])
		var more := page.find_child("IntelMore", true, false) as Control
		if more != null and more.visible:
			assert_true(screen.encloses(more.get_global_rect()), "Heat %d: the MORE tab on screen" % heat)
			assert_false(more.get_global_rect().grow(-0.5).intersects(net.get_global_rect().grow(-0.5)), "Heat %d: the MORE tab clear of YOUR NETWORK" % heat)
		hq.get_parent().free()
