extends GutTest
## Plan 2 W2 HQ-LADDER-UI (flow test for the netrun scene, run kind "hq"): the Solace HQ ladder is readable and
## playable in the netrun scene. Walks Clinic Gate -> UP -> ACROSS -> rest -> mini-boss -> crown with fixture
## fights and asserts the words, icons, bridge links, tower captions, Bloom gap preview and fight labels the scene
## shows equal what the session says (the preview is exact: gap_milli equals the real enter_node result).

const SCENE := "res://scenes/netrun_map/netrun_scene.tscn"
const SEED := 5

var _scene: Control
var _s: NetrunSession


func before_each() -> void:
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	_scene = add_child_autofree(load(SCENE).instantiate())
	RunManager.new_campaign(3, &"solace")
	var c := RunManager.campaign
	_s = NetrunSession.start_hq_ladder(RunManager.resolver, c, c.roster[0].id, &"t1_a", 4, SEED, RunManager.corporation)
	_s.run.corp_theme.solace.front_milli = -90000  # the Bloom is far behind: no room is caught
	RunManager.netrun = _s
	_scene._show_current()
	await get_tree().process_frame


func after_each() -> void:
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


## Wins the fight in the session (fixture), takes the payout and shows the page again.
func _win_fight() -> void:
	_s.combat.state.player.max_hp = 9999
	var turns := 0
	while _s.in_combat() and turns < 40:
		turns += 1
		_s.combat.state.player.hp = 9999
		for e in _s.combat.state.living_enemies():
			e.hp = 1
		CombatFixture.land(_s.combat.state.player, 0, 0)
		_s.combat_action(CombatAction.end_turn())
	if _s.run.phase == RunState.Phase.REWARD:
		_s.proceed_rewards()


## Enters room `id` through the scene and clears whatever it holds back to the map.
func _walk_to(id: StringName) -> void:
	assert_true(_s.available_nodes().has(id), "%s is a choice" % id)
	_scene.enter_node(id)
	await _clear_room()


func _clear_room() -> void:
	var guard := 0
	while _s.run.phase != RunState.Phase.MAP and not _s.run.is_over() and guard < 8:
		guard += 1
		match _s.run.phase:
			RunState.Phase.COMBAT, RunState.Phase.REWARD:
				_win_fight()
			RunState.Phase.EVENT:
				_scene.choose_event(_s.current_event().choices.size() - 1)
			RunState.Phase.SHOP:
				_scene.leave_shop()
		_scene._show_current()
	await get_tree().process_frame


func _overlay() -> StreetRouteOverlay:
	return _scene.street_view.overlay


func _tag(id: StringName) -> String:
	return String(_overlay().tags[String(id)])


func test_the_gate_page_labels_the_towers_and_marks_the_bridges() -> void:
	assert_not_null(_scene.street_view, "the ladder is drawn by the street view")
	var ov := _overlay()
	var g := _s.run.map
	# Every ACROSS link of the graph is a bridge on the overlay, and no UP link is.
	var across := HqLadderWords.across_keys(g)
	assert_eq(ov.across_keys, across)
	var n_across := 0
	for n in g.all_nodes():
		n_across += (n.get("across_from", []) as Array).size()
	assert_eq(across.size(), n_across)
	assert_gt(across.size(), 0)
	for e: Dictionary in ov.data.derive["edges"]:
		var key := "%s>%s" % [e["a"], e["b"]]
		var b := g.get_node(StringName(e["b"]))
		var is_bridge := NetrunSession.entered_across(b, StringName(e["a"]))
		assert_eq(ov.across_keys.has(key), is_bridge, "link %s" % key)
	# No tower caption at rest: the overlay holds no tower names (the tower stays in the hover tag and the room file).
	assert_false("tower_names" in ov, "no tower captions on the overlay")
	assert_false("ACROSS_DASH" in ov.get_script().get_script_constant_map(), "bridges are not dashed")
	# A bridge is a raised arc: its stroke lifts above the straight link between the same rooms and lands on both ends.
	var flat := PackedVector2Array([Vector2(0, 100), Vector2(50, 100), Vector2(100, 100), Vector2(150, 100), Vector2(200, 100)])
	var arc := StreetRouteOverlay._arched(flat)
	assert_eq(arc[0], flat[0], "lifts from the first room")
	assert_eq(arc[arc.size() - 1], flat[flat.size() - 1], "lands on the second")
	var peak := arc[arc.size() / 2]
	assert_lt(peak.y, flat[2].y, "peaks above the gap")
	assert_gte(arc.size(), StreetRouteOverlay.ACROSS_MIN_POINTS, "dense: at least the minimum points")
	var long_flat := PackedVector2Array([Vector2(0, 100), Vector2(600, 100)])
	var long_arc := StreetRouteOverlay._arched(long_flat)
	assert_gte(long_arc.size(), int(600.0 / StreetRouteOverlay.ACROSS_STEP_PX), "one point per step px")
	for pts in [arc, long_arc, StreetRouteOverlay._arched(PackedVector2Array([Vector2(0, 0), Vector2(10, 90)])), StreetRouteOverlay._arched(PackedVector2Array([Vector2(0, 100), Vector2(120, 100), Vector2(100, 10), Vector2(200, 0)]))]:
		for i in range(1, pts.size() - 1):
			var turn := absf((pts[i] - pts[i - 1]).angle_to(pts[i + 1] - pts[i]))
			assert_lt(turn, deg_to_rad(15.0), "no corner: the stroke bends gently at %d" % i)
	# The gate itself is named.
	var gate := g.first_layer_ids()[0]
	assert_eq(_word(g.get_node(gate)), "Clinic Gate")
	var ids := _s.available_nodes()
	assert_eq(ids, [gate] as Array[StringName])


func _word(node: Dictionary) -> String:
	return _scene.node_word(node)


func test_the_ladder_walk_shows_what_the_session_says() -> void:
	var g := _s.run.map
	var cfg := _s.config
	# Clinic Gate (a fight).
	await _walk_to(g.first_layer_ids()[0])
	assert_eq(_s.run.phase, RunState.Phase.MAP)
	var ward1 := MapGraph.make_id(2, 0)
	var bill1 := MapGraph.make_id(2, 1)
	assert_eq(_s.available_nodes(), [ward1, bill1] as Array[StringName], "pick a tower")
	assert_true(_tag(ward1).contains("UP") and _tag(bill1).contains("UP"), "the gate's two rooms read UP")
	assert_true(_tag(ward1).begins_with("WARD"))
	assert_true(_tag(bill1).begins_with("BILLING"))
	# UP: Ward rung 1 -> Ward rung 2. ACROSS: -> Billing rung 3.
	await _walk_to(ward1)
	var up := MapGraph.make_id(3, 0)
	var across := MapGraph.make_id(3, 1)
	assert_true(_s.available_nodes().has(up) and _s.available_nodes().has(across))
	var prev := _s.bloom_preview()
	assert_true(_tag(up).contains("UP"))
	assert_true(_tag(across).contains("ACROSS"))
	assert_false(_tag(up).contains("ACROSS"))
	for id in [up, across]:
		var gap := NetrunSession.bloom_gap_text(int(prev[id]["gap_milli"]))
		assert_true(_tag(id).contains("GAP %s" % gap), "%s shows the exact gap %s: %s" % [id, gap, _tag(id)])
		assert_false(_tag(id).contains("?"))
	# The preview equals the real result: the gap read before the move is the gap after it.
	var expect_gap := int(prev[across]["gap_milli"])
	_scene.enter_node(across)
	assert_eq(BloomRules.gap_milli(_s.run.corp_theme.solace), expect_gap, "preview == the gap after entering")
	await _clear_room()
	# The room file shows tower, move and gap rows (the node panel's extra rows).
	var options := _s.available_nodes()
	var data: Dictionary = _scene.node_panel_data(options[0])
	var labels: Array = []
	for row in data["extra"]:
		labels.append(row[0])
	assert_true(labels.has("TOWER") and labels.has("MOVE") and labels.has("BLOOM GAP"), "extra rows %s" % [labels])
	# Rest room: its word, icon and what it pays.
	var rest := _first_with(&"rest")
	assert_false(rest.is_empty(), "the ladder holds a rest room")
	assert_eq(_scene.node_word(rest), "Rest")
	assert_eq(_scene.node_icon(rest), StatIcon.HP)
	var rest_data: Dictionary = _scene.node_panel_data(rest["id"])
	assert_eq(rest_data["rewards"], ["the Bloom front goes back %s layers" % NetrunSession.bloom_gap_text(cfg.bloom_dose_push_milli)])
	assert_eq(_scene.street_view.overlay.kind_overrides[String(rest["id"])], "rest")
	# Mini-boss and the crown: walk there (the rooms before them are skipped; the ladder rules are covered elsewhere).
	var mb_layer := cfg.solace_hq_mini_boss_rung + 1
	var mb: Dictionary = g.nodes_in_layer(mb_layer)[0]
	_s.run.current_node_id = g.nodes_in_layer(mb_layer - 1)[0]["id"]
	_scene._show_current()
	await get_tree().process_frame
	assert_eq(_scene.node_word(mb), "Mini-boss")
	assert_eq(_scene.node_icon(mb), StatIcon.ELITE)
	assert_eq(_scene.street_view.overlay.kind_overrides[String(mb["id"])], "elite")
	_scene.enter_node(mb["id"])
	await get_tree().process_frame
	assert_true(_s.in_combat())
	assert_true(_scene.combat_scene.address_line().contains("MINI-BOSS: "), _scene.combat_scene.address_line())
	assert_false(_scene.combat_scene.address_line().contains(" BOSS: "))
	_win_fight()
	_scene._show_current()
	await get_tree().process_frame
	var crown: Dictionary = g.layers[g.layer_count() - 1][0]
	_s.run.current_node_id = g.layers[g.layer_count() - 2][1]["id"]
	_scene._show_current()
	await get_tree().process_frame
	assert_eq(_scene.node_word(crown), "Genome Core")
	assert_true(_tag(crown["id"]).contains("Genome Core"), _tag(crown["id"]))
	assert_true(_tag(crown["id"]).contains("UP") and not _tag(crown["id"]).contains("ACROSS"), "the crown reads UP")
	_scene.enter_node(crown["id"])
	await get_tree().process_frame
	assert_true(_s.in_combat())
	var line: String = _scene.combat_scene.address_line()
	assert_true(line.contains("BOSS: ") and not line.contains("MINI-BOSS"), line)
	assert_true(HqLadderWords.fight_label(_s.run).begins_with("BOSS"))


func _first_with(kind: StringName) -> Dictionary:
	for n in _s.run.map.all_nodes():
		if HqLadderWords.room_kind(n) == kind:
			return n
	return {}


func test_other_runs_keep_their_words() -> void:
	# A plain node reads as before and the combat address keeps its BOSS rule for the single-node HQ run.
	assert_eq(HqLadderWords.fight_label(null), "")
	_s.run.kind = "netrun"
	assert_eq(HqLadderWords.fight_label(_s.run), "")
	_s.run.kind = NetrunSession.HQ_LADDER_KIND
