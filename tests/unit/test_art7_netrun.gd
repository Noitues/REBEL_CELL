extends GutTest
## ART-7 3B (ART_BIBLE v2 §4.6; D13, D14): the netrun route's presentation. Option A rings by
## state, the numbered choices and the TARGET; hidden nodes (D13) with the legend's hover, the
## pointer's reveal and Options "Always show all nodes"; calm Heat marks only from the current
## rules; the dossier and the decrypted node panel's words; transit v3 cable runs; the jack
## along a link (one press skips it, reduce effects keeps the fade, headless never waits);
## the node backdrops. Views never change state. Headless.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
const KINDS: Array[String] = ["fight", "elite", "event", "shop", "rack"]

var _reduce: bool
var _scale: float
var _all_nodes: bool


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	_all_nodes = Settings.always_show_all_nodes
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art7_netrun"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	Motion.force_live = false
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.always_show_all_nodes != _all_nodes:
		Settings.set_always_show_all_nodes(_all_nodes)
	Fx._set_jacking(false)
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


func _netrun(heat: int = 0) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	RunManager.campaign.heat = heat
	scene.start_run(1)
	return scene


func _overlay(scene: Control) -> RouteOverlay:
	return scene.city_overlay as RouteOverlay


# --- 3B.1 node states, TARGET, hidden nodes, calm Heat ------------------------------------------

func test_the_route_view_draws_option_a_states_and_the_target() -> void:
	var scene := _netrun()
	await _frames()
	var ov := _overlay(scene)
	assert_not_null(ov, "the route draws with RouteOverlay")
	var s := RunManager.netrun
	var final_id: StringName = s.run.map.final_node_id()
	var targets := 0
	for n in ov.nodes:
		if n.get("target", false):
			targets += 1
			assert_eq(n["id"], final_id, "the TARGET is the final Rack")
		if n.get("next", false):
			assert_eq(ov.state_of(n), RouteOverlay.STATE_NEXT)
			assert_gt(int(n["number"]), 0, "a choice is numbered")
			assert_eq(RouteInk.ring_of(ov.state_of(n)), Palette.RING_AVAILABLE, "selectable is orange")
		else:
			assert_eq(int(n.get("number", 0)), 0, "only choices are numbered")
	assert_eq(targets, 1)
	assert_eq(RouteInk.ring_of(RouteOverlay.STATE_WALKED), Palette.CELL_ACID, "walked is lime")
	assert_eq(RouteInk.ring_of(RouteOverlay.STATE_LATER), Palette.RING_UNAVAILABLE, "not yet is white")
	assert_eq(RouteInk.ring_of(RouteOverlay.STATE_CUT), Palette.RING_CUT, "cut off is dim grey")


func test_every_state_has_a_second_cue_besides_colour() -> void:
	# The greyscale audit: each ring state has its own style, so states differ without colour.
	var styles := {}
	for st in [RouteOverlay.STATE_WALKED, RouteOverlay.STATE_NEXT, RouteOverlay.STATE_LATER, RouteOverlay.STATE_CUT]:
		var style := String(RouteOverlay.RING_STYLES.get(st, ""))
		assert_ne(style, "", "%s has a style" % st)
		assert_false(styles.has(style), "%s's style is its own" % st)
		styles[style] = st
	var legend: RouteLegend = add_child_autofree(RouteLegend.new(RouteLegend.ORDER))
	for key in RouteLegend.COLOR_KEYS:
		var sw := legend.strip.get_node("Color_%s/Swatch" % key) as Control
		assert_eq(String(sw.get_meta(&"ring_style", "")), String(RouteOverlay.RING_STYLES[key]), "the key draws %s's style" % key)


func test_hidden_nodes_show_on_the_legend_hover_the_pointer_and_the_setting() -> void:
	Settings.set_always_show_all_nodes(false)
	var scene := _netrun()
	await _frames()
	var ov := _overlay(scene)
	var before := RunManager.campaign.state_hash()
	var run_before := RunManager.netrun.state_hash()
	var drawn := ov.drawn_ids()
	for n in ov.nodes:
		assert_eq(drawn.has(n["id"]), RouteOverlay.pinned(n), "%s: only walked, choices and the TARGET show" % n["id"])
	assert_lt(drawn.size(), ov.nodes.size(), "some nodes are hidden at the start")
	# The legend strip's hover shows every node; leaving it hides them again.
	scene.route_legend.show_all_hovered.emit(true)
	assert_true(ov.show_all)
	ov.all_t = 1.0
	assert_eq(ov.drawn_ids().size(), ov.nodes.size(), "every node shows on the legend hover")
	scene.route_legend.show_all_hovered.emit(false)
	assert_false(ov.show_all)
	# The pointer reveals the hidden node under it.
	var hidden: Dictionary = {}
	for n in ov.nodes:
		if not RouteOverlay.pinned(n) and ov.icon_pos(n).x != INF:
			hidden = n
			break
	assert_false(hidden.is_empty(), "a hidden node to reveal")
	assert_eq(ov.hidden_near(ov.icon_pos(hidden)), hidden["id"])
	ov._reveal(ov.hidden_near(ov.icon_pos(hidden)))
	ov.reveal_t = 1.0
	assert_true(ov.drawn_ids().has(hidden["id"]), "the node under the pointer shows")
	# Options: always show every node (D13).
	Settings.set_always_show_all_nodes(true)
	assert_true(ov.show_all, "the setting shows every node")
	assert_eq(scene.route_legend.cue.text, tr(RouteLegend.SHOWING_WORDS))
	Settings.set_always_show_all_nodes(false)
	assert_eq(RunManager.campaign.state_hash(), before, "views never change the campaign")
	assert_eq(RunManager.netrun.state_hash(), run_before, "views never change the run")


func test_the_setting_round_trips_and_has_an_options_row() -> void:
	var d := Settings.to_dict()
	assert_true(d.has("always_show_all_nodes"), "saved")
	Settings.set_always_show_all_nodes(true)
	assert_true(bool(Settings.to_dict()["always_show_all_nodes"]))
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	panel.show_section("Display")
	await _frames(1)
	assert_not_null(panel.find_child("AllNodesCheck", true, false), "Options > Display has the row")
	assert_true(panel.all_nodes_check.button_pressed)


func test_calm_heat_marks_come_from_the_rules_and_only_on_choices() -> void:
	var cool := _netrun(0)
	await _frames()
	assert_true(cool.route_heat_marks(RunManager.netrun).is_empty(), "no Heat marks while Heat has made nothing harder")
	assert_false(cool.route_heat_sweeps(), "no searchlights at COOL")
	cool.get_parent().queue_free()
	await _frames(1)
	RunManager.reset()
	var hot := _netrun(60)
	await _frames()
	var s := RunManager.netrun
	var resist := 0
	for m in HeatRules.active_modifiers(s.campaign, s.config):
		if m.type == RC.RuleModifierType.ENEMY_RESISTANCE:
			resist += int(m.value)
	assert_gt(resist, 0, "Heat 60 adds enemy resistance (GDD 4.3)")
	assert_true(hot.route_heat_sweeps(), "the searchlights sweep")
	for n in hot.city_overlay.nodes:
		var chip := String(n.get("heat_chip", ""))
		var node := s.run.map.get_node(n["id"])
		var fight := int(node["type"]) == RC.InfilNodeType.ROUTER or int(node["type"]) == RC.InfilNodeType.SERVER_RACK
		if n.get("next", false) and fight:
			assert_string_contains(chip, str(resist), "a choice that is a fight carries the resistance")
		elif not n.get("next", false):
			assert_eq(chip, "", "only selectable nodes carry markers (4.3)")


func test_the_route_sweeps_every_corporation_with_labels_and_you_are_here() -> void:
	for corp in CORPORATIONS:
		RunManager.reset()
		var holder: Control = add_child_autofree(Control.new())
		holder.size = SCREEN.size
		var scene: Control = load(NETRUN).instantiate()
		holder.add_child(scene)
		scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
			RunManager.profile.add_unlock(u)
		for id in ["solace", "meridian", "halcyon", "orbital"]:
			RunManager.profile.best_ice_by_corp[id] = 10
		RunManager.new_campaign(1, corp)
		scene.start_run(1)
		await _frames()
		var s := RunManager.netrun
		s.run.current_node_id = s.run.map.first_layer_ids()[0]
		scene._show_map()
		await _frames()
		var ov := _overlay(scene)
		assert_not_null(ov, "%s: RouteOverlay" % corp)
		for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
			Settings.set_text_scale(scale)
			await _frames(2)
			assert_true(ov.label_rects().has(String(ov.here_id())), "%s x%.1f: YOU ARE HERE shows" % [corp, scale])
			var rects: Dictionary = ov.label_rects()
			var keys: Array = rects.keys()
			for i in keys.size():
				for j in range(i + 1, keys.size()):
					assert_false((rects[keys[i]] as Rect2).intersects(rects[keys[j]]), "%s x%.1f: labels overlap" % [corp, scale])
			if scene.dossier.is_visible_in_tree():
				for r in LegendSpot.node_rects(ov, false, scene.route_focus_ids()):
					assert_false(scene.dossier.get_global_rect().intersects(r), "%s x%.1f: the dossier covers no choice" % [corp, scale])
			var legend: Rect2 = scene.route_legend.get_global_rect()
			assert_true(SCREEN.grow(1.0).encloses(legend), "%s x%.1f: the strip fits (%s)" % [corp, scale, legend])
		Settings.set_text_scale(1.0)
		holder.queue_free()
		await _frames(1)


func test_cables_run_along_the_city_axes_with_one_turn() -> void:
	var scene := _netrun()
	await _frames()
	var ov := _overlay(scene)
	var pts := ov.cable(Vector2(10, 10), Vector2(200, 90))
	assert_eq(pts.size(), 3, "start, one corner, end")
	var ax: Array[Vector2] = ov._axes()
	var leg := pts[1] - pts[0]
	assert_almost_eq(absf(leg.normalized().cross(ax[0].normalized())), 0.0, 0.001, "the first leg runs along one axis")
	var leg2 := pts[2] - pts[1]
	assert_almost_eq(absf(leg2.normalized().cross(ax[1].normalized())), 0.0, 0.001, "the second along the other")


# --- 3B.2 dossier and the decrypted node panel --------------------------------------------------

func test_the_dossier_and_node_panel_say_what_the_rules_say() -> void:
	var scene := _netrun(52)
	await _frames()
	var d: Dictionary = scene.dossier_data()
	var op := RunManager.netrun.run.operative
	assert_eq(d["subject"], op.name)
	assert_eq(int(d["hp"]), op.hp)
	assert_eq(int(d["deck"]), op.deck.size())
	assert_ne(String(d["hub"]), "", "the hub core is named")
	assert_eq(scene.dossier.heat_words(), tr(OperativeDossier.HEAT_STAMP) % [52, String(d["band"]).to_upper()])
	var s := RunManager.netrun
	for id in s.available_nodes():
		var p: Dictionary = scene.node_panel_data(id)
		assert_eq(int(p["tier"]), s.run.tier, "the tier")
		assert_false((p["rewards"] as Array).is_empty(), "rewards")
		var node := s.run.map.get_node(id)
		if int(node["type"]) == RC.InfilNodeType.ROUTER and not bool(node["elite"]):
			var pay: Vector2i = s.config.cycles_router_range
			assert_string_contains(String(p["rewards"][0]), "%d-%d" % [pay.x, pay.y], "pays what the config says")
	# The focused choice's file shows.
	var b := scene._panel.find_child("Node1", true, false) as Button
	b.grab_focus()
	await _frames(1)
	assert_eq(scene.node_panel.node_id, s.available_nodes()[0])


func test_the_dossier_folds_at_big_text() -> void:
	var scene := _netrun()
	await _frames()
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	await _frames(2)
	assert_true(scene.dossier.compact, "at 2.0 on 1280 the file folds")
	assert_true(scene.dossier.size.x <= SCREEN.size.x * OperativeDossier.MAX_WIDTH_SHARE + 1.0)


# --- 3B.3 the jack along a link -----------------------------------------------------------------

func test_the_link_jack_terminal_lines_name_both_ends() -> void:
	var lines := JackSequence.lines_for("RELAY_4", "DEPOT_15")
	assert_eq(lines.size(), 4)
	assert_string_contains(lines[0], "--from RELAY_4 --to DEPOT_15")


func test_the_link_jack_is_immediate_headless() -> void:
	var seen := []
	await Fx.jack_in_link(func() -> void: seen.append(Fx.transitioning()), {"from": "A", "to": "B"})
	assert_eq(seen, [false], "headless: the switch at once")
	assert_false(Fx.jack_link.visible)


func test_one_press_skips_the_link_jack() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	var switched := [0]
	Fx.jack_in_link(func() -> void: switched[0] += 1, {"from": "A", "to": "B", "points": PackedVector2Array([Vector2(100, 400), Vector2(500, 200)])})
	await BoundedWait.until(get_tree(), func() -> bool: return Fx.jack_link.visible, 2.0)
	assert_true(Fx.transitioning(), "the jack runs")
	assert_true(Fx.jack_link.visible, "the sequence plays")
	var press := InputEventKey.new()
	press.keycode = KEY_SPACE
	press.pressed = true
	Fx.input_gate._input(press)
	var limit := BoundedWait.motion_limit([Fx.ARRIVAL_WAIT_MOTION, Fx.CONNECT_MOTION], 2.0)
	var t := await BoundedWait.timed(get_tree(), func() -> bool: return not Fx.transitioning(), limit)
	assert_false(Fx.transitioning(), "one press ends the jack")
	assert_eq(switched[0], 1, "the switch ran once")
	assert_false(Fx.jack_link.visible, "the end state: the run, nothing over it")
	assert_lt(t, Motion.seconds(&"jack_lens") + Motion.seconds(&"jack_wheel_spin") + limit, "well before the sequence's own end")


func test_reduce_effects_keeps_the_plain_fade() -> void:
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	var seen := []
	var limit := BoundedWait.motion_limit([&"jack_fade_reduced", Fx.ARRIVAL_WAIT_MOTION, Fx.CONNECT_MOTION])
	Fx.jack_in_link(func() -> void: seen.append(Fx.jack_link.visible), {"from": "A", "to": "B"})
	await BoundedWait.until(get_tree(), func() -> bool: return not Fx.transitioning(), limit)
	assert_eq(seen, [false], "no lens under reduce effects: the fade's end state")


func test_the_launch_jack_names_its_link() -> void:
	RunManager.new_campaign(1)
	var site := RunManager.launchable_sites()[0]
	var link := RunManager.jack_link(site.id)
	assert_ne(String(link["from"]), "", "the owned end")
	assert_eq(String(link["to"]), "_".join(TextDb.t(site, "display_name").to_upper().split(" ", false)))
	assert_false((link["slices"] as Array).is_empty(), "the operative's wheel")


# --- 3B.4 node backdrops -------------------------------------------------------------------------

func test_every_corporation_has_a_room_per_node_kind() -> void:
	for corp in CORPORATIONS:
		for kind in KINDS:
			assert_true(NodeBackdrop.has_still(kind, corp), "%s %s" % [corp, kind])


func test_the_node_room_shows_behind_an_event_only() -> void:
	var scene := _netrun()
	await _frames()
	assert_true(scene.node_backdrop == null or not scene.node_backdrop.visible, "not on the map")
	var s := RunManager.netrun
	DemoSetup.open_event(s, &"ev_leash_on_the_floor")
	scene._show_current()
	await _frames()
	if s.run.current_node_id != &"":
		assert_true(scene.node_backdrop != null and scene.node_backdrop.visible, "behind the event")
