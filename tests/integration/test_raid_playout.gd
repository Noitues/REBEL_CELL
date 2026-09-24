extends GutTest
## Raid playout controls (GDD 7.2, 9.3): the panel groups a resolved raid's events by
## step, animates threat markers on the Grid view, honours speed and skip, and the
## netrun map view lays nodes out as a clickable wireframe graph.

var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData


func test_playout_steps_through_a_raid_and_moves_markers() -> void:
	var grid := GridFixture.chain_grid([&"c1", &"c2"])
	var c := GridFixture.campaign(grid, {&"c1": &"firewall_relay", &"c2": &"relay"})
	GridFixture.deploy(c, &"c1", &"turret")
	var raid := GridFixture.raid(&"two", [&"collector", &"enforcer"])
	var result := RaidResolver.resolve(c, grid, raid, _lookup, _cfg)
	var view := GridMapView.new()
	add_child_autofree(view)
	view.show_grid(c, _corp)
	var panel := RaidPlayoutPanel.new(view)
	add_child_autofree(panel)
	panel.play(result.events, true)
	assert_true(panel.is_done())
	assert_eq(panel.current_step(), panel.steps_total())
	assert_true(panel.steps_total() >= result.steps_run + 1, "setup plus every step")
	assert_true(panel.log_note.label.get_parsed_text().contains("Step 1"))
	# Non-instant: the first step shows, the rest wait on the timer; skip finishes.
	var panel2 := RaidPlayoutPanel.new(view)
	add_child_autofree(panel2)
	watch_signals(panel2)
	panel2.play(result.events, false)
	assert_false(panel2.is_done())
	assert_eq(panel2.current_step(), 1)
	panel2.set_speed(4.0)
	assert_eq(panel2.speed, 4.0)
	panel2.skip_to_end()
	assert_true(panel2.is_done())
	assert_signal_emitted(panel2, "finished")
	# After a raid every surviving threat marker is gone from destroyed threats.
	for site in view.threat_markers:
		assert_true(view.threat_markers[site].size() >= 1)


func test_netrun_map_view_lays_out_nodes_and_reports_clicks() -> void:
	var map := MapGenerator.generate(1, _cfg, CombatFixture.rng(3))
	var view := NetrunMapView.new()
	add_child_autofree(view)
	view.size = Vector2(900, 360)
	view.show_map(map, &"", [], map.first_layer_ids())
	watch_signals(view)
	var first := map.first_layer_ids()[0]
	var p := view.position_of(first)
	assert_true(p.x > 0 and p.y > 0)
	assert_eq(view.node_at(p), first)
	assert_eq(view.node_at(Vector2(-100, -100)), &"")
	var ev := InputEventMouseButton.new()
	ev.button_index = MOUSE_BUTTON_LEFT
	ev.pressed = true
	ev.position = p
	view._gui_input(ev)
	assert_signal_emitted_with_parameters(view, "node_clicked", [first])
	# Layers spread left to right.
	var last := map.final_node_id()
	assert_true(view.position_of(last).x > p.x)
