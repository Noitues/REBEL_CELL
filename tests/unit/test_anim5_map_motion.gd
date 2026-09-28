extends GutTest
## Animation pass ANIM-5 (map, raid, jack and Heat motion; ANIMATION_HANDOFF 4.1, 4.12,
## 4.14-4.16): reduce effects and headless show every end state at once; the raid playout's
## beats come from the resolver's events and end on the resolved campaign; Skip jumps to
## the summary; speed scales the playout; the territory tint ends on CityInfluence's own
## colours; a Heat pulse fires once per crossing and never on a steady value; a netrun move
## ends with the marker on the chosen node; a jack transition never shows both scenes; the
## Grid camera's lean keeps the fitted map; nothing here changes game state.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SETTLE := 12
## Frames of a reduce-effects jack that are not the fade's own time (the two held frames
## and each of the two fades' last, overshooting frame).
const FADE_OVERHEAD_FRAMES := 4

var _reduce: bool
var _speed: float
var _scale: float
var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_speed = Motion.speed
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim5"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx.apply_settings()
	Motion.force_live = false
	Motion.speed = _speed
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


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


## The HQ with a campaign set up like --demo-raid: the first Site cleared and claimed, an
## asset deployed on it, a raid pending.
func _hq_raid() -> Control:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var grid_data := RunManager.corporation.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	return hq


## A small raid on a fixture Grid (a turret on c1).
func _fixture_raid() -> RaidResolver.RaidResult:
	var grid := GridFixture.chain_grid([&"c1", &"c2"])
	var c := GridFixture.campaign(grid, {&"c1": &"firewall_relay", &"c2": &"relay"})
	GridFixture.deploy(c, &"c1", &"turret")
	var raid := GridFixture.raid(&"two", [&"collector", &"enforcer"])
	return RaidResolver.resolve(c, grid, raid, _lookup, _cfg)


# --- Raid execution: beats from the resolver's events ----------------------------------------

func test_raid_beats_are_built_from_the_resolver_events_in_order() -> void:
	var result := _fixture_raid()
	var groups := RaidBeats.group(result.events)
	assert_true(groups.size() >= result.steps_run + 1, "setup, every step, and the end")
	var played: Array[Dictionary] = []
	var count := 0
	for g in groups:
		var tl := RaidBeats.timeline(g)
		var last_phase := -1
		var last_t0 := 0.0
		for b: Dictionary in tl["beats"]:
			assert_true((g as Array).has(b["event"]), "each beat is one of its group's events")
			assert_eq(String(b["type"]), String(b["event"]["type"]), "a beat plays its event's type")
			assert_true(float(b["t0"]) >= last_t0 - 0.0001, "beats start in order")
			assert_true(float(b["t0"]) + float(b["dur"]) <= float(tl["seconds"]) + 0.0001, "and inside their step")
			var phase := RaidBeats.PHASES.find(String(b["phase"]))
			assert_true(phase >= last_phase, "in the resolver's phase order")
			last_phase = phase
			last_t0 = float(b["t0"])
			played.append(b["event"])
		count += (g as Array).size()
	assert_eq(count, result.events.size(), "every event lands in one group")
	var beat_events := 0
	for e in result.events:
		if RaidBeats.is_beat(String(e["type"])):
			beat_events += 1
			assert_true(played.has(e), "%s plays as a beat" % e["type"])
	assert_eq(played.size(), beat_events, "no event plays twice, none is made up")


func test_the_resolver_says_when_a_decoy_pulls_a_threat() -> void:
	var grid := GridFixture.chain_grid([&"c1", &"c2"])
	var c := GridFixture.campaign(grid, {&"c1": &"firewall_relay", &"c2": &"relay"})
	GridFixture.deploy(c, &"c2", &"decoy")
	var raid := GridFixture.raid(&"one", [&"collector"])
	var result := RaidResolver.resolve(c, grid, raid, _lookup, _cfg)
	var moves := result.events.filter(func(e: Dictionary) -> bool: return e["type"] == "move")
	assert_false(moves.is_empty(), "the threat moves")
	for e in moves:
		assert_true(e.has("target"), "a move names where it is headed")
		assert_eq(bool(e["decoy"]), StringName(e["target"]) == &"c2", "the decoy's pull is named when it is the target")
	var again := RaidResolver.resolve(c, grid, raid, _lookup, _cfg)
	assert_eq(again.summary_hash(), result.summary_hash(), "the added facts change no result")


func test_playout_ends_on_the_resolved_campaign_and_speed_scales_it() -> void:
	var hq := _hq_raid()
	await _frames()
	var c := RunManager.campaign
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	hq.fight_raid()  # the rule, then the playout from the Grid as it stood
	var resolved := c.to_dict()
	await BoundedWait.frozen_frames(get_tree(), 3)  # the playout must still be under way after the layout frames
	var p: RaidPlayoutPanel = hq.playout
	assert_false(p.is_done(), "live, the raid plays over time")
	assert_not_null(p.fx, "on the city map it plays as motion")
	assert_not_null(wireframe_pin(hq), "the city holds the pre-raid tint while it plays")
	# Speed: the clock runs at Motion.speed; the table's seconds divide by it.
	p.set_speed(4.0)
	assert_eq(Motion.speed, 4.0, "4x sets the motion speed")
	assert_almost_eq(Motion.seconds(&"raid_move"), Motion.entry(&"raid_move").duration / 4.0, 0.0001, "durations scale")
	var t := p.clock()
	p._process(0.1)
	assert_almost_eq(p.clock() - t, 0.4, 0.0001, "a frame at 4x moves the playout 4x as far")
	p.skip_to_end()
	assert_true(p.is_done())
	assert_eq(Motion.speed, 1.0, "the speed goes back to 1x when the playout ends")
	var r := c.last_raid
	assert_eq(p.fx.home_value, int(r["home_after"]), "home integrity ends on the resolved value")
	assert_eq(p.fx.home_value, c.grid.home_integrity)
	for id in r["nodes"]:
		if StringName(String(id)) == c.grid.home_site_id:
			continue
		assert_eq(p.fx.stamp_word(StringName(String(id))), RaidFxLayer.stamp_text(String(r["nodes"][id]["outcome"])),
			"%s's stamp is its resolved outcome" % id)
	var hit := int(r["home_after"]) < int(r["home_before"])
	assert_eq(p.fx.stamp_word(c.grid.home_site_id), "BREACHED" if hit else "HOLDS", "home's stamp")
	var forecast := hq.find_child("PlayoutForecast", true, false) as ForecastStamp
	assert_not_null(forecast)
	assert_true(forecast.resolved, "the forecast resolved into the verdict")
	assert_eq(forecast.verdict, hq.VERDICT_HOLDS if bool(r["won"]) else (hq.VERDICT_LOST if bool(r["campaign_lost"]) else hq.VERDICT_HIT))
	assert_null(wireframe_pin(hq), "the result's tint is let through at the end")
	assert_eq(c.to_dict(), resolved, "playing the raid changed no game state")


func wireframe_pin(hq: Control) -> Variant:
	return (hq.wireframe as WireframeBackground).city.influence_pin


func test_skip_jumps_to_the_summary() -> void:
	var hq := _hq_raid()
	await _frames()
	var before := RunManager.campaign.duplicate_state()
	var events := RunManager.fight_raid()
	var resolved := RunManager.campaign.to_dict()
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	hq.show_raid_playout(events, before)
	await _frames()
	assert_eq(hq.panel_name, "raid_playout")
	(hq.playout.find_child("Skip", true, false) as Button).pressed.emit()
	assert_eq(hq.panel_name, "raid_summary" if not RunManager.campaign.is_over() else "end", "Skip shows the summary")
	assert_eq(RunManager.campaign.to_dict(), resolved, "and changed no game state")


func test_instant_playout_under_reduce_effects_and_headless() -> void:
	for reduce in [true, false]:
		RunManager.reset()
		var hq := _hq_raid()
		await _frames()
		if Settings.reduce_effects != reduce:
			Settings.set_reduce_effects(reduce)
		hq.fight_raid()
		assert_true(hq.panel_name in ["raid_summary", "end"], "reduce %s: the result at once" % reduce)
		assert_null(wireframe_pin(hq), "reduce %s: the city shows the result" % reduce)
		hq.get_parent().queue_free()
		await _frames(1)


# --- Territory tint -----------------------------------------------------------------------------

func test_influence_spread_ends_on_city_influence_colours() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var old := CityInfluence.of(c, corp)
	var first: StringName = corp.city_grid.get_site(corp.city_grid.home_site_id).links[0]
	var run := RunState.new()
	run.site_id = first
	run.kind = CampaignRules.run_kind_for(c, corp.city_grid.get_site(first))
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run, RunManager.lookup())
	var new := CityInfluence.of(c, corp)
	assert_ne(CityInfluence.signature(old), CityInfluence.signature(new), "clearing a Site changes the tint")
	assert_eq(InfluenceSpread.changed_sites(old, new), [first] as Array[StringName], "the cleared Site changed")
	var from := InfluenceSpread.origins(old, new)
	assert_eq(from.size(), 1)
	assert_eq(from[0], CityLayout.site_points(corp)[first], "the spread starts at that Site")
	assert_eq(InfluenceSpread.front_color(old, new), Palette.CELL_PINK, "toward the Cell: the Cell's pink")
	var reach := Motion.amplitude(&"influence_spread")
	var feather := Motion.amplitude(&"influence_crossfade")
	for dx in [-6, -2, 0, 3, 7]:
		for dy in [-5, 0, 4]:
			var p: Vector2 = from[0] + Vector2(dx, dy)
			assert_eq(InfluenceSpread.reveal_at(p, from, 1.0, 1.0, reach, feather), 1.0, "the end state is all new")
			assert_almost_eq(InfluenceSpread.value_at(old, new, p, 1.0), CityInfluence.value_at(new, p), 0.00001)
			assert_eq(InfluenceSpread.tint_at(old, new, p, 1.0), CityInfluence.color_for(new, CityInfluence.value_at(new, p)),
				"the end tint is CityInfluence's")
			assert_almost_eq(InfluenceSpread.value_at(old, new, p, 0.0), CityInfluence.value_at(old, p), 0.00001, "the start is the old")
	# Mid-spread: the Site itself has turned before the far streets.
	var near := InfluenceSpread.reveal_at(from[0], from, 0.5, 0.0, reach, feather)
	var far := InfluenceSpread.reveal_at(from[0] + Vector2(reach, reach), from, 0.5, 0.0, reach, feather)
	assert_gt(near, far, "the tint spreads out from the Site")


func test_the_city_pins_and_releases_its_tint_and_never_spreads_headless() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	holder.add_child(city)
	city.bind_campaign(c, corp)
	await _frames()
	var now := CityInfluence.of(c, corp)
	assert_eq(CityInfluence.signature(city.influence), CityInfluence.signature(now))
	var pinned := {}
	city.pin_influence(pinned)
	assert_eq(CityInfluence.signature(city.influence), CityInfluence.signature(pinned), "a pinned tint holds")
	city.sync_influence()
	assert_eq(CityInfluence.signature(city.influence), CityInfluence.signature(pinned), "whatever the campaign says")
	city.release_influence()
	assert_eq(CityInfluence.signature(city.influence), CityInfluence.signature(now), "released, it follows again")
	assert_false(city.spreading(), "headless shows the end state (nothing baked, nothing spreads)")
	assert_eq(city.spread_progress(), Vector2.ONE)


# --- Heat thresholds -----------------------------------------------------------------------------

func test_heat_pulse_fires_once_per_crossing_and_never_on_a_steady_value() -> void:
	HeatPoster._seen_heat.clear()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var poster := HeatPoster.new(true)
	holder.add_child(poster)
	var marks: Array[int] = [25, 50, 75]
	var pulses := Fx.heat_pulses
	poster.set_heat(20, 100, marks)
	assert_eq(Fx.heat_pulses, pulses, "the first sight is not a crossing")
	poster.set_heat(30, 100, marks)
	assert_eq(Fx.heat_pulses, pulses + 1, "crossing 25 pulses once")
	poster.set_heat(30, 100, marks)
	poster.set_heat(40, 100, marks)
	assert_eq(Fx.heat_pulses, pulses + 1, "a steady value or a rise inside a band: no pulse")
	poster.set_heat(20, 100, marks)
	assert_eq(Fx.heat_pulses, pulses + 1, "going down never pulses")
	assert_eq(HeatPoster.crossings(20, 60, marks), 2, "two thresholds at once are two crossings")
	assert_eq(HeatPoster.crossings(80, 20, marks), 0)
	# A new poster of the same campaign remembers: the HQ rebuilt after a run.
	var again := HeatPoster.new(true)
	holder.add_child(again)
	again.set_heat(20, 100, marks)
	assert_eq(Fx.heat_pulses, pulses + 1, "the same Heat on a new poster: nothing")
	again.set_heat(55, 100, marks)
	assert_eq(Fx.heat_pulses, pulses + 2, "one pulse now, the second a pulse later")
	await BoundedWait.until(get_tree(), func() -> bool: return Fx.heat_pulses >= pulses + 3, BoundedWait.motion_limit([&"heat_pulse"]))
	assert_eq(Fx.heat_pulses, pulses + 3, "each crossing pulses once")
	await BoundedWait.until(get_tree(), func() -> bool: return not Fx.distortion.visible and not Fx.creep_rect.visible and again.stamp_scale == 1.0 and again.shake_offset == Vector2.ZERO, BoundedWait.motion_limit([&"heat_pulse", &"net_creep"]))
	assert_false(Fx.distortion.visible, "the pulse ends: nothing stays on")
	assert_false(Fx.creep_rect.visible, "the creep recedes")
	assert_eq(again.stamp_scale, 1.0, "the band stamp lands")
	assert_eq(again.shake_offset, Vector2.ZERO, "the letters settle")


# --- Netrun route -----------------------------------------------------------------------------------

func _route_map() -> CityMapOverlay:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	holder.add_child(city)
	var overlay := CityMapOverlay.new(city)
	city.add_child(overlay)
	var nodes: Array[Dictionary] = [{"id": &"a", "at": Vector2(2, 2), "here": true, "kind": CityMapOverlay.KIND_FIGHT},
		{"id": &"b", "at": Vector2(9, 3), "next": true, "kind": CityMapOverlay.KIND_EVENT}]
	var edges: Array[Dictionary] = [{"a": &"a", "b": &"b", "flow": true}]
	overlay.set_graph(nodes, edges)
	return overlay


func test_a_netrun_move_ends_with_the_marker_on_the_chosen_node() -> void:
	var overlay := _route_map()
	await _frames(4)
	assert_ne(overlay.icon_at(&"b").x, INF, "the map is laid out")
	assert_eq(overlay.travel(&"a", &"b"), 0.0, "headless: no time taken")
	assert_eq(overlay.here_marker_pos(), overlay.icon_at(&"b"), "the marker is on the chosen node at once")
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	var overlay2 := _route_map()
	await _frames(4)
	var secs := overlay2.travel(&"a", &"b")
	assert_gt(secs, 0.0, "live, the move takes its time")
	assert_ne(overlay2.here_marker_pos(), overlay2.icon_at(&"b"), "the marker sets off from the old node")
	await BoundedWait.until(get_tree(), func() -> bool: return overlay2.here_marker_pos() == overlay2.icon_at(&"b") and overlay2.dim_t == 1.0, secs + BoundedWait.SLACK)
	assert_eq(overlay2.here_marker_pos(), overlay2.icon_at(&"b"), "and ends on the chosen node")
	assert_eq(overlay2.dim_t, 1.0, "the node left behind has dimmed")
	var overlay3 := _route_map()
	await _frames(4)
	overlay3.travel(&"a", &"b")
	overlay3.finish_travel()
	assert_eq(overlay3.here_marker_pos(), overlay3.icon_at(&"b"), "input skips to the end")


# --- Jack in / out ------------------------------------------------------------------------------------

func test_jack_transitions_never_show_both_scenes() -> void:
	var seen := []
	await Fx.jack_in(func() -> void: seen.append(Fx.cover_opaque()))
	assert_eq(seen, [false], "headless: the switch at once, no cover")
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	seen.clear()
	await Fx.jack_in(func() -> void: seen.append([Fx.cover_opaque(), Fx.jack_cover.visible, float(Fx.jack_cover.material.get_shader_parameter("progress"))]))
	assert_eq(seen.size(), 1, "the switch runs once")
	assert_true(seen[0][0] and seen[0][1], "jack in switches under the opaque cover")
	assert_eq(seen[0][2], 1.0, "fully dissolved")
	assert_false(Fx.jack_cover.visible, "the cover is gone after")
	assert_false(Fx.transitioning())
	seen.clear()
	await Fx.jack_out(func() -> void: seen.append(Fx.cover_opaque()))
	assert_eq(seen, [true], "jack out too")
	Settings.set_reduce_effects(true)
	seen.clear()
	# The fade's length in game time (the frames' deltas), less its longest frame: wall time
	# failed on a busy machine, where one stalled frame outlasts the margin (Test suite
	# optimization).
	var deltas: Array[float] = []
	var tick := func() -> void: deltas.append(get_process_delta_time())
	get_tree().process_frame.connect(tick)
	await Fx.jack_in(func() -> void: seen.append([Fx.cover_opaque(), Fx.transition_rect.color.a]))
	get_tree().process_frame.disconnect(tick)
	# Less its FADE_OVERHEAD_FRAMES longest frames (Test suite: bounded waits): besides the
	# two fades' own time the switch holds two frames and each fade ends on a frame that
	# overshoots it; on a loaded machine those frames alone can outlast the margin.
	var took := 0.0
	deltas.sort()
	for i in maxi(0, deltas.size() - FADE_OVERHEAD_FRAMES):
		took += deltas[i]
	assert_eq(seen[0][1], 1.0, "reduce effects: a fade to black, the switch at its darkest")
	assert_lt(took, Motion.entry(&"jack_fade_reduced").duration * 2.0 + 0.3, "a short fade (about 0.2 s; slack of its own length for uneven frames)")
	assert_eq(Fx.transition_rect.color.a, 0.0, "and back")


# --- City Grid / raid setup ---------------------------------------------------------------------------

func test_selecting_a_site_draws_on_and_the_lean_keeps_the_fit() -> void:
	Settings.set_text_scale(1.0)
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var snapshot := RunManager.campaign.to_dict()
	hq.show_grid()
	await _frames(SETTLE)
	var other: StringName = hq.stepped_site(1)
	hq.select_site(other)
	await _frames(SETTLE)
	var overlay: CityMapOverlay = hq.city_overlay
	assert_eq(overlay.selected_id, other)
	assert_eq(overlay.select_reveal, 1.0, "headless: the outline is drawn at once")
	assert_eq(overlay.ring_ease, 1.0)
	assert_false((hq.wireframe as WireframeBackground).camera_easing(), "no ease headless")
	var area := (hq.find_child("GridMapArea", true, false) as Control).get_global_rect()
	for r in LegendSpot.node_rects(overlay, false):
		assert_true(area.grow(0.5).encloses(r), "every node stays on the map after the lean (%s in %s)" % [r, area])
	var lean: Vector2 = hq.grid_lean(area.grow(-LegendSpot.MARGIN))
	assert_true(lean.length() <= Motion.amplitude(&"map_camera_ease") + 0.01, "the lean is bounded")
	assert_eq(RunManager.campaign.to_dict(), snapshot, "selecting and framing changed no game state")


func test_an_asset_drops_onto_its_node_with_a_stamp() -> void:
	var hq := _hq_raid()
	await _frames()
	hq.show_raid()
	await _frames(SETTLE)
	var target: StringName = hq.selected_site
	hq.deploy_asset(0, target)
	await _frames(2)
	assert_eq(hq.city_overlay.drop_t, 1.0, "headless: landed at once")
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	hq.play_asset_drop(target)
	assert_lt(hq.city_overlay.drop_t, 1.0, "live: it falls")
	await BoundedWait.until(get_tree(), func() -> bool: return hq.city_overlay.drop_t == 1.0, BoundedWait.motion_limit([&"asset_drop"]))
	assert_eq(hq.city_overlay.drop_t, 1.0, "and lands")


func test_the_folding_key_slides_and_frames_for_its_folded_line() -> void:
	Settings.set_text_scale(1.6)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var legend := MapLegend.pin_to(holder, &"solace", true)
	await _frames()
	assert_true(legend.foldable())
	var folded := legend.fit_size()
	legend.set_opened(true)
	assert_eq(legend.fold_slide, 1.0, "headless: open at once")
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	legend.set_opened(false)
	legend.set_opened(true)
	assert_lt(legend.fold_slide, 1.0, "live: the rows slide in")
	assert_eq(legend.fit_size(), folded, "the map is framed for the folded line throughout")
	legend.set_opened(false)
	assert_false(legend.opened, "folded at once for the layout")
	assert_eq(legend.fit_size(), folded)
	await BoundedWait.until(get_tree(), func() -> bool: return legend.fit_size() == legend.get_combined_minimum_size(), BoundedWait.motion_limit([&"legend_fold"]))
	assert_eq(legend.fit_size(), legend.get_combined_minimum_size(), "the rows hide when they have slid out")


# --- HQ mini-map ---------------------------------------------------------------------------------------

func test_the_minimap_pulses_a_changed_site_once() -> void:
	GridMapView._seen_status.clear()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var mini := GridMapView.new()
	mini.track_seen = true
	holder.add_child(mini)
	mini.show_grid(c, corp)
	assert_eq(mini.changed_ids.size(), 0, "the first sight changes nothing")
	var first: StringName = corp.city_grid.get_site(corp.city_grid.home_site_id).links[0]
	var run := RunState.new()
	run.site_id = first
	run.kind = CampaignRules.run_kind_for(c, corp.city_grid.get_site(first))
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run, RunManager.lookup())
	var snapshot := c.to_dict()
	mini.show_grid(c, corp)
	assert_true(mini.changed_ids.has(first), "the cleared Site pulses")
	await _frames(2)
	assert_eq(mini.pulse_t, 1.0, "headless: the pulse's end state at once")
	assert_eq(mini.ring_ease, 1.0)
	mini.show_grid(c, corp)
	assert_eq(mini.changed_ids.size(), 0, "once: seen now")
	var hidden := GridMapView.new()
	holder.add_child(hidden)
	hidden.show_grid(c, corp)
	assert_eq(hidden.changed_ids.size(), 0, "an untracked map never pulses")
	assert_eq(c.to_dict(), snapshot, "the mini-map changed no game state")
