extends GutTest
## RAID-FIX C: the threat map reads (no player-target red in a raid, one hue for the threat routes, shared
## segments drawn once with a count, HP pips) and the Heat-to-raid countdown rule (HeatRules.next_raid /
## raid_crossed_by).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_raid_fix_c"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _campaign() -> CampaignState:
	RunManager.new_campaign(1)
	return RunManager.campaign


# --- C4: the rule -----------------------------------------------------------------------------

func test_next_raid_is_the_lowest_unfired_raid_threshold_above_the_heat() -> void:
	var c := _campaign()
	var cfg := RunManager.config()
	c.heat = 0
	var n := HeatRules.next_raid(c, cfg)
	assert_false(n.is_empty(), "a raid threshold lies ahead")
	var want := 9999
	for t in cfg.heat_thresholds:
		if t != null and t.event_raid != null:
			want = mini(want, HeatRules.effective_heat(t, c, cfg))
	assert_eq(int(n["at"]), want)
	assert_eq(int(n["away"]), want - c.heat)
	c.heat = want - 3
	assert_eq(int(HeatRules.next_raid(c, cfg)["away"]), 3)
	c.heat = want
	c.thresholds_fired.append(want)
	var after := HeatRules.next_raid(c, cfg)
	assert_true(after.is_empty() or int(after["at"]) > want, "a crossed threshold is not the next one")
	c.heat = cfg.heat_max
	for t in cfg.heat_thresholds:
		c.thresholds_fired.append(t.heat)
	assert_true(HeatRules.next_raid(c, cfg).is_empty(), "none left at the top of the scale")


func test_raid_crossed_by_matches_the_forecast() -> void:
	var c := _campaign()
	var cfg := RunManager.config()
	c.heat = 0
	var n := HeatRules.next_raid(c, cfg)
	var at := int(n["at"])
	assert_eq(HeatRules.raid_crossed_by(c, at - 1, cfg), 0, "one short of it: no raid")
	var crossed := HeatRules.raid_crossed_by(c, at + 1, cfg)
	assert_gte(crossed, at, "past it: the tag names the threshold")
	assert_true(bool(HeatRules.forecast(c, at + 1, cfg)["raid"]), "the tag is the forecast's own answer")
	assert_eq(c.heat, 0, "the campaign is not changed")


# --- C2: shared segments ----------------------------------------------------------------------

func test_shared_segments_are_drawn_once_with_a_count() -> void:
	var paths: Array = [[&"a", &"x", &"h"], [&"b", &"x", &"h"], [&"c", &"h"]]
	var m := RaidRouteLayer.merge_routes(paths)
	var runs: Array = m["runs"]
	var drawn := 0
	for r: Dictionary in runs:
		drawn += (r["nodes"] as Array).size() - 1
	assert_eq(drawn, 4, "a-x, x-h, b-x and c-h: x-h once")
	var ticks: Array = m["ticks"]
	assert_eq(ticks.size(), 1, "one count tick for the shared stretch")
	assert_eq(int(ticks[0]["count"]), 2)
	var arrows := 0
	for r: Dictionary in runs:
		if bool(r["arrow"]):
			arrows += 1
	assert_eq(arrows, 2, "the first route and the lone one carry heads; b-x ends short on the shared stretch")


func test_unshared_routes_come_back_whole() -> void:
	var m := RaidRouteLayer.merge_routes([[&"a", &"b", &"h"], [&"c", &"d", &"h2"]])
	assert_eq((m["runs"] as Array).size(), 2)
	assert_true((m["ticks"] as Array).is_empty())


# --- C3: HP pips ------------------------------------------------------------------------------

func test_pip_state_lights_the_integrity_left() -> void:
	var s := RaidFxLayer.pip_state(0.5, 4)
	assert_eq(int(s["pips"]), 4)
	assert_eq(int(s["filled"]), 2)
	assert_eq(int(RaidFxLayer.pip_state(0.01, 4)["filled"]), 1, "alive keeps one pip")
	assert_eq(int(RaidFxLayer.pip_state(0.0, 4)["filled"]), 0)
	var big := RaidFxLayer.pip_state(0.5, RaidFxLayer.PIP_MAX + 5)
	assert_eq(int(big["pips"]), 0, "past the cap the bar is solid")
	assert_almost_eq(float(big["share"]), 0.5, 0.001)


# --- C1 / C2: the map ---------------------------------------------------------------------------

func test_threat_route_hue_is_its_own() -> void:
	assert_eq(GreasePencilMark.ink_color(GreasePencilMark.Ink.THREAT_ROUTE), Palette.THREAT_ROUTE)
	assert_ne(Palette.THREAT_ROUTE, Palette.PENCIL_THREAT, "not the player's target red")
	for c: Color in [Palette.CELL_ACID, Palette.CELL_PINK, Palette.NET_CYAN, Palette.CORP_SOLACE, Palette.CORP_MERIDIAN,
			Palette.CORP_HALCYON, Palette.CORP_ORBITAL, Palette.CORP_REBEL_CELL]:
		assert_ne(Palette.THREAT_ROUTE, c)


func test_no_target_pencil_while_a_raid_is_pending() -> void:
	var c := _campaign()
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for i in 4:
		await get_tree().process_frame
	var ov: CityMapOverlay = hq.city_overlay
	if ov == null:
		pending("no city overlay in this build")
		return
	assert_true(ov.raid_lens, "the HQ map is in the raid lens with a raid pending")
	var word := ov.target_word()
	assert_true(word == null or not word.visible, "the TARGET word is hidden")
	if hq.grid_target != null:
		assert_false(hq.grid_target.showing(), "the TARGET edge arrow is hidden")
	c.pending_raids.clear()
	hq.get_parent().queue_free()
	await get_tree().process_frame
