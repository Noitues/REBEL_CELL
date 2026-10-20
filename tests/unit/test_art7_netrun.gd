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


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
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


# --- 3B.1 node states, TARGET, hidden nodes, calm Heat ------------------------------------------

func test_the_route_draws_option_a_states_and_the_target() -> void:
	# NA-26: the ring colours are the kit's (static); the street page offers exactly the session's choices and names one TARGET.
	var scene := _netrun()
	await _frames()
	var s := RunManager.netrun
	var view: StreetRouteView = scene.street_view
	assert_not_null(view, "the route is the street page")
	var opts: Array = view.run_state()["options"]
	var avail: Array[StringName] = s.available_nodes()
	assert_eq(opts.size(), avail.size(), "every choice is an option")
	assert_ne(s.run.map.final_node_id(), &"", "the run has its TARGET (the final Rack)")
	assert_eq(RouteInk.ring_of(RouteOverlay.STATE_WALKED), Palette.CELL_ACID, "walked is lime")
	assert_eq(RouteInk.ring_of(RouteOverlay.STATE_LATER), Palette.RING_UNAVAILABLE, "not yet is white")
	assert_eq(RouteInk.ring_of(RouteOverlay.STATE_CUT), Palette.RING_CUT, "cut off is dim grey")
	assert_eq(RouteInk.ring_of(RouteOverlay.STATE_NEXT), Palette.RING_AVAILABLE, "selectable is orange")


func test_every_state_has_a_second_cue_besides_colour() -> void:
	if TestScope.deferred():
		pending(TestScope.REASON)
		return
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


func test_the_key_hover_lights_every_link_and_changes_no_state() -> void:
	# NA-26: ported from the hidden-node test: the key strip's hover lights every run link on the street page (the full
	# graph is always drawn now; the hidden-node reveal and the Options row are retired).
	var scene := _netrun()
	await _frames()
	var before := RunManager.campaign.state_hash()
	var run_before := RunManager.netrun.state_hash()
	scene.route_legend.show_links_hovered.emit(true)
	assert_true(scene.street_view._lit_all, "the hover lights every link")
	assert_eq(scene.route_legend.cue.text, tr(RouteLegend.LINKS_WORDS))
	scene.route_legend.show_links_hovered.emit(false)
	assert_false(scene.street_view._lit_all)
	assert_eq(RunManager.campaign.state_hash(), before, "views never change the campaign")
	assert_eq(RunManager.netrun.state_hash(), run_before, "views never change the run")


func test_the_retired_show_all_nodes_key_loads_and_is_ignored() -> void:
	# NA-26: the legacy key stays one version: an old file carrying it loads, the value is not read or saved again.
	var d := Settings.to_dict()
	assert_false(d.has("always_show_all_nodes"), "no longer saved")
	d["always_show_all_nodes"] = true
	Settings.from_dict(d)
	assert_false("always_show_all_nodes" in Settings, "no setting reads it")
	var panel: SettingsPanel = add_child_autofree(SettingsPanel.new())
	panel.show_section("Display")
	await _frames(1)
	assert_null(panel.find_child("AllNodesCheck", true, false), "Options > Display has no row for it")


func test_calm_heat_marks_come_from_the_rules() -> void:
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
	var marks: Dictionary = hot.route_heat_marks(s)
	assert_string_contains(String(marks[RC.InfilNodeType.ROUTER]), str(resist), "a fight carries the resistance")
	assert_string_contains(String(marks[RC.InfilNodeType.SERVER_RACK]), str(resist))
	# The street tag a hovered room shows carries the Heat entering it changes (the preview equals the rules).
	for id in s.available_nodes():
		var heat := s.node_heat(id)
		if heat != 0:
			assert_string_contains(hot._street_tag(String(id)), TextDb.signed(heat), "the room's tag names its Heat")


func test_the_route_sweeps_every_corporation_on_the_street_page() -> void:
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
		if scene.street_view == null:
			# A street that cannot be derived keeps the transit page: the choices are list rows (the fallback stays usable).
			assert_not_null(scene._panel.find_child("Node1", true, false), "%s: the fallback page lists the choices" % corp)
			holder.queue_free()
			await _frames(1)
			continue
		var opts: Array = scene.street_view.run_state()["options"]
		assert_eq(opts.size(), RunManager.netrun.available_nodes().size(), "%s: every choice is an option" % corp)
		var legend: Rect2 = scene.route_legend.get_global_rect()
		assert_true(SCREEN.grow(1.0).encloses(legend), "%s: the strip fits (%s)" % [corp, legend])
		holder.queue_free()
		await _frames(1)


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
	assert_false(d.has("heat"), "Q10: no Heat on the file (the gauge is the one place)")
	var s := RunManager.netrun
	for id in s.available_nodes():
		var p: Dictionary = scene.node_panel_data(id)
		assert_eq(int(p["tier"]), s.run.tier, "the tier")
		assert_false((p["rewards"] as Array).is_empty(), "rewards")
		var node := s.run.map.get_node(id)
		if int(node["type"]) == RC.InfilNodeType.ROUTER and not bool(node["elite"]):
			var pay: Vector2i = s.config.cycles_router_range
			assert_string_contains(String(p["rewards"][0]), "%d-%d" % [pay.x, pay.y], "pays what the config says")
	# The shown choice's file shows.
	scene.show_node_panel(s.available_nodes()[0])
	assert_eq(scene.node_panel.node_id, s.available_nodes()[0])


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
	assert_lt(t, Motion.seconds(&"jack_crt_collapse") + limit, "well before the sequence's own end")


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
	assert_eq(String(link["to"]), RunManager.TERMINAL_NODE % RunManager.corporation.city_grid.sites.find(site), "the terminal names the Site by its node number (two Sites can share a type word)")
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


func test_f13_the_key_hover_never_resizes_the_strip() -> void:
	var scene := _netrun()
	await _frames()
	var legend: RouteLegend = scene.route_legend
	var size_before := legend.get_combined_minimum_size()
	scene.route_legend.show_links_hovered.emit(true)
	await _frames()
	assert_eq(legend.get_combined_minimum_size(), size_before, "the SHOWING words take the cue's room: the strip keeps its size")
	scene.route_legend.show_links_hovered.emit(false)
	await _frames()
	assert_eq(legend.get_combined_minimum_size(), size_before)
