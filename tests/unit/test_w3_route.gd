extends GutTest
## W3-ROUTE (C7 + 7A, R5 static): node types differ by shape, every link between drawn nodes is
## drawn, a click selects and a confirm travels, and the HP the route shows is the run's HP.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Vector2(1280, 720)

var _resolver: CombatResolver
var _all_nodes: bool


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func before_each() -> void:
	_all_nodes = Settings.always_show_all_nodes
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w3_route"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	Motion.force_live = false
	if Settings.always_show_all_nodes != _all_nodes:
		Settings.set_always_show_all_nodes(_all_nodes)
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _netrun() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	return scene


func test_every_node_kind_has_its_own_badge_shape() -> void:
	var seen := {}
	for kind in RouteLegend.ORDER:
		var pts := RouteOverlay.shape_polygon(kind, Vector2.ZERO, 10.0)
		assert_gt(pts.size(), 3, "%s has a polygon" % kind)
		var key := "%s" % [pts]
		assert_false(seen.has(key), "%s's silhouette is its own" % kind)
		seen[key] = kind
	assert_eq(seen.size(), RouteLegend.ORDER.size())


func test_a_click_selects_and_the_confirm_travels() -> void:
	var scene := _netrun()
	await _frames(4)
	var s := RunManager.netrun
	var first: StringName = s.available_nodes()[0]
	var prompt := scene._panel.find_child("RoutePrompt", true, false) as Label
	var confirm := scene._panel.find_child("RouteConfirm", true, false) as Button
	assert_not_null(prompt, "the pick prompt shows")
	assert_not_null(confirm)
	assert_true(confirm.disabled, "nothing to confirm before a pick")
	var b := scene._panel.find_child("Node1", true, false) as Button
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	b.gui_input.emit(click)
	b.pressed.emit()
	assert_eq(scene.route_selected(), first, "the click selected the node")
	assert_eq(s.run.phase, RunState.Phase.MAP, "a click alone does not travel")
	assert_false(confirm.disabled)
	assert_string_contains(confirm.text, "Enter")
	confirm.pressed.emit()
	assert_ne(s.run.current_node_id, &"", "the confirm travelled")
	assert_eq(s.run.current_node_id, first)


func test_the_keyboard_press_still_travels_directly() -> void:
	var scene := _netrun()
	await _frames(4)
	var s := RunManager.netrun
	var first: StringName = s.available_nodes()[0]
	(scene._panel.find_child("Node1", true, false) as Button).pressed.emit()
	assert_eq(s.run.current_node_id, first)


func test_the_node_file_shows_the_hp_the_run_arrives_with() -> void:
	var scene := _netrun()
	await _frames(3)
	var s := RunManager.netrun
	s.run.operative.hp = maxi(1, s.run.operative.max_hp - 7)
	for id in s.available_nodes():
		var d: Dictionary = scene.node_panel_data(id)
		var hp := RouteHp.arrival(s)
		assert_eq(int(hp["hp"]), s.run.operative.hp)
		assert_string_contains(String(d["hp"]), "%d" % s.run.operative.hp)
		assert_string_contains(String(d["hp"]), "%d" % s.run.operative.max_hp)
		assert_ne(String(d["heals"]), "", "says where it heals")


func test_links_between_drawn_nodes_are_drawn() -> void:
	Settings.set_always_show_all_nodes(false)
	var scene := _netrun()
	await _frames(4)
	var ov := scene.city_overlay as RouteOverlay
	var both := 0
	for e in ov.edges:
		var a := ov.shown(ov._node_dict(e["a"]))
		var b := ov.shown(ov._node_dict(e["b"]))
		if a > 0.0 and b > 0.0:
			both += 1
			assert_gt(ov.edge_shown(e), 0.0, "a link between two drawn nodes is drawn")
		else:
			assert_eq(ov.edge_shown(e), 0.0, "a link to a hidden node waits for it")
	Settings.set_always_show_all_nodes(true)
	ov.all_t = 1.0
	await _frames(2)
	for e in ov.edges:
		assert_gt(ov.edge_shown(e), 0.0, "with every node shown, every link is")
	assert_gte(both, 0)


func _walk_hp(seed: int) -> void:
	var c := CampaignState.new()
	c.campaign_seed = 99
	c.schematics = _resolver.config.starting_schematics
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	var s := NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_a", seed)
	for step in 4:
		if s.run.is_over() or s.run.phase != RunState.Phase.MAP or s.available_nodes().is_empty():
			return
		var arrive := RouteHp.arrival(s)
		assert_eq(int(arrive["hp"]), s.run.operative.hp, "the route shows the run's HP")
		assert_eq(int(arrive["max_hp"]), s.run.operative.max_hp)
		s.enter_node(s.available_nodes()[0])
		if s.in_combat():
			assert_eq(s.combat.state.player.hp, int(arrive["hp"]), "the fight starts with the HP shown")
			var turns := 0
			while s.in_combat() and turns < 80:
				CombatFixture.land(s.combat.state.player, 0)
				for i in range(s.combat.state.hand.size() - 1, -1, -1):
					if i < s.combat.state.hand.size():
						s.combat_action(CombatAction.play_card(i, s.combat.state.target_id))
				s.combat_action(CombatAction.end_turn())
				turns += 1
		while s.run.phase == RunState.Phase.REWARD:
			s.skip_reward()
		if s.run.phase == RunState.Phase.EVENT:
			s.choose_event_option(s.current_event().choices.size() - 1)
		if s.run.phase == RunState.Phase.SHOP:
			s.leave_shop()
		if s.run.phase == RunState.Phase.MAP:
			assert_eq(int(RouteHp.arrival(s)["hp"]), s.run.operative.hp, "after the node the carry-over is the run's HP")


func test_shown_carry_over_hp_is_the_run_states_hp_after_each_node() -> void:
	for seed in [11, 12, 13]:
		_walk_hp(seed)
