extends GutTest
## Halcyon v2 THE EYE, HQ slices 5-8 (fast): the gaze is a pure function of (phase, step), a climb adds
## 2 and a Stall 1, fight nodes in the eye are SPOTTED, non-fight nodes (Annex included) SHUTTERED and
## the beam BLOCKED; Alert starts at the launch level, gains per rule 16 and Lockdown doubles the beam
## and raises the Blade; Stall is once per layer and previews exactly; Cut the Power is once per run;
## the state survives a save; at most 7 Stalls open any node.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _halcyon: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_halcyon = ContentRegistry.get_content(&"halcyon") as CorporationData


func _hq(eye: int = 2, seed: int = 7) -> NetrunSession:
	var c := CampaignRules.new_campaign(_halcyon, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	c.corp_theme.halcyon.eye_index = eye
	return NetrunSession.start_hq_ladder(_resolver, c, c.roster[0].id, &"t1_a", 4, seed, _halcyon)


func _node(az: int, fight: bool = true) -> Dictionary:
	return {"az": az, "type": RC.InfilNodeType.ROUTER if fight else RC.InfilNodeType.TERMINAL, "next": []}


func test_hq_gaze_pure() -> void:
	for phase in 8:
		for step in 20:
			assert_eq(EyeRules.gaze_centre(phase, step, _cfg), EyeRules.gaze_centre(phase + 8, step, _cfg))
			assert_eq(EyeRules.gaze_centre(phase, step, _cfg), 45 * ((phase + step) % 8))
	var s := _hq()
	var h := s.run.corp_theme.halcyon
	assert_eq(h.eye_step, 0)
	s.stall()
	assert_eq(h.eye_step, _cfg.hq_gaze_step_per_stall, "a Stall adds 1")
	var s2 := _hq()
	var first: Dictionary = s2.run.map.layers[0][0]
	var opts := s2.hq_enterable_nodes()
	assert_false(opts.is_empty())
	s2.enter_node(opts[0])
	assert_eq(s2.run.corp_theme.halcyon.eye_step, _cfg.hq_gaze_step_per_node, "a node adds 1")
	assert_ne(first, {})


func test_climb_adds_two_steps() -> void:
	var s := _hq(0)
	var g := s.run.map
	var from_node: Dictionary = {}
	var to_node: Dictionary = {}
	for node in g.all_nodes():
		if not (node.get("climb_from", []) as Array).is_empty():
			to_node = node
			from_node = g.get_node((node["climb_from"] as Array)[0])
			break
	assert_false(from_node.is_empty())
	s.run.current_node_id = from_node["id"]
	s.run.corp_theme.halcyon.eye_step = 5
	var prev := s.hq_edge_preview(to_node["id"])
	assert_eq(prev["step"], 5 + _cfg.hq_gaze_step_per_climb - _cfg.hq_gaze_step_per_node, "the arrival gaze counts the climb")
	to_node["az"] = (EyeRules.gaze_centre(0, int(prev["step"]), _cfg) + 180) % 360  # dark side so it is enterable
	s.enter_node(to_node["id"])
	assert_eq(s.run.corp_theme.halcyon.eye_step, 5 + _cfg.hq_gaze_step_per_climb, "a climb adds 2")


func test_hq_node_states() -> void:
	var centre := EyeRules.gaze_centre(2, 3, _cfg)
	var fight_in := _node(centre + 30)
	var rest_in := _node(centre - 30, false)
	var fight_out := _node(centre + 180)
	var rest_out := _node(centre + 180, false)
	var beam_fight := _node(centre + 3)
	var beam_rest := _node(centre - 4, false)
	var annex := _node(centre + 20, false)
	annex["annex"] = true
	annex["rest"] = true
	assert_eq(EyeRules.node_state(fight_in, 2, 3, 0, false, _cfg), EyeRules.NodeState.SPOTTED)
	assert_eq(EyeRules.node_state(rest_in, 2, 3, 0, false, _cfg), EyeRules.NodeState.SHUTTERED)
	assert_eq(EyeRules.node_state(annex, 2, 3, 0, false, _cfg), EyeRules.NodeState.SHUTTERED, "Annex rooms follow the shuttered rule")
	assert_eq(EyeRules.node_state(fight_out, 2, 3, 0, false, _cfg), EyeRules.NodeState.OPEN)
	assert_eq(EyeRules.node_state(rest_out, 2, 3, 0, false, _cfg), EyeRules.NodeState.OPEN)
	assert_eq(EyeRules.node_state(beam_fight, 2, 3, 0, false, _cfg), EyeRules.NodeState.BLOCKED, "the beam blocks any kind")
	assert_eq(EyeRules.node_state(beam_rest, 2, 3, 0, false, _cfg), EyeRules.NodeState.BLOCKED)
	assert_eq(EyeRules.node_state(_node(centre + 5), 2, 3, 0, false, _cfg), EyeRules.NodeState.SPOTTED, "5 degrees is outside the normal beam")
	assert_eq(EyeRules.node_state(_node(centre + 5), 2, 3, _cfg.hq_lockdown_alert, false, _cfg), EyeRules.NodeState.BLOCKED, "Lockdown doubles the beam")
	assert_eq(EyeRules.node_state(rest_in, 2, 3, 0, true, _cfg), EyeRules.NodeState.OPEN, "asleep: no sector, no beam")


func test_a_shuttered_or_blocked_option_cannot_be_entered() -> void:
	var s := _hq(0)
	var id: StringName = s.available_nodes()[0]
	var node := s.run.map.get_node(id)
	node["az"] = 10
	node["type"] = RC.InfilNodeType.TERMINAL
	assert_eq(s.hq_option_state(id), EyeRules.NodeState.SHUTTERED)
	var ev := s.enter_node(id)
	assert_eq(ev[0]["type"], "refused")
	assert_eq(s.run.current_node_id, &"", "nothing was entered")
	node["az"] = 0
	assert_eq(s.hq_option_state(id), EyeRules.NodeState.BLOCKED)
	assert_eq(s.enter_node(id)[0]["type"], "refused")
	assert_false(s.hq_enterable_nodes().has(id))


func test_hq_alert_lockdown() -> void:
	var s := _hq(0)
	var h := s.run.corp_theme.halcyon
	assert_eq(h.hq_alert, h.spotted_level, "Alert starts at the launch level")
	h.hq_alert = 0
	assert_false(EyeRules.lockdown(3, _cfg))
	assert_true(EyeRules.lockdown(4, _cfg))
	assert_eq(EyeRules.beam_half_width(3, _cfg), 4)
	assert_eq(EyeRules.beam_half_width(4, _cfg), 8)
	assert_eq(EyeRules.hq_blade_level(0, 4, _cfg), 1)
	assert_eq(EyeRules.hq_blade_level(1, 4, _cfg), 2)
	assert_eq(EyeRules.hq_blade_level(2, 5, _cfg), 2, "capped at 2")
	# +1 per fight won IN THE EYE, +1 per Stall, +2 per Cut the Power.
	s.stall()
	assert_eq(h.hq_alert, 1)
	h.entered_state = EyeRules.NodeState.SPOTTED
	s.run.current_node_id = s.run.map.layers[0][0]["id"]
	s.combat = null
	var before := h.hq_alert
	h.hq_alert += _cfg.hq_alert_gain_eye_fight
	assert_eq(h.hq_alert, before + 1)
	# The Blade level at a SPOTTED fight follows Alert.
	h.spotted_level = 0
	h.hq_alert = 4
	assert_eq(s.eye_blade_level(), 1)
	h.entered_state = EyeRules.NodeState.OPEN
	assert_eq(s.eye_blade_level(), 0, "a fight outside the eye has no Blade")


func test_a_fight_won_in_the_eye_adds_alert() -> void:
	var s := _hq(0)
	var h := s.run.corp_theme.halcyon
	var id: StringName = s.available_nodes()[0]
	s.run.map.get_node(id)["az"] = 20  # in the eye (octant 0), off the beam
	h.hq_alert = 0
	h.spotted_level = 0
	s.enter_node(id)
	assert_eq(h.entered_state, EyeRules.NodeState.SPOTTED)
	assert_true(s.in_combat())
	s.combat.state.player.max_hp = 9999
	var turns := 0
	while s.in_combat() and turns < 40:
		turns += 1
		s.combat.state.player.hp = 9999
		for e in s.combat.state.living_enemies():
			e.hp = 1
		CombatFixture.land(s.combat.state.player, 0, 0)
		s.combat_action(CombatAction.end_turn())
	assert_eq(h.hq_alert, _cfg.hq_alert_gain_eye_fight, "+1 for a fight completed IN THE EYE")


func test_stall_once_per_layer_and_preview_equals_result() -> void:
	var s := _hq(0)
	var h := s.run.corp_theme.halcyon
	var prev := s.stall_preview()
	assert_false(prev.is_empty())
	assert_true(s.can_stall())
	s.stall()
	assert_eq(h.eye_step, prev["step"], "preview == result")
	assert_eq(h.hq_alert, prev["alert"])
	assert_eq(s.hq_option_states(), prev["states"])
	if not s.hq_enterable_nodes().is_empty():
		assert_false(s.can_stall(), "a second Stall on the same layer is refused")
		assert_eq(s.stall()[0]["type"], "refused")
		assert_eq(h.eye_step, 1)
	# Entering a node opens a new layer: Stall is back.
	var open := s.hq_enterable_nodes()
	if not open.is_empty():
		s.enter_node(open[0])
		s.run.phase = RunState.Phase.MAP
		s.combat = null
		assert_false(h.stalled_this_layer)


func test_at_most_seven_stalls_open_any_node() -> void:
	for az in range(0, 360, 7):
		var node := _node(az, false)
		var opened := false
		for stalls in 8:
			if EyeRules.enterable(EyeRules.node_state(node, 1, stalls, 0, false, _cfg)):
				opened = true
				assert_lte(stalls, 7)
				break
		assert_true(opened, "az %d" % az)
		var hard := _node(az, false)
		var opened_lock := false
		for stalls in 8:
			if EyeRules.enterable(EyeRules.node_state(hard, 1, stalls, 9, false, _cfg)):
				opened_lock = true
				break
		assert_true(opened_lock, "az %d in Lockdown" % az)


func test_cut_the_power() -> void:
	var s := _hq(0)
	var h := s.run.corp_theme.halcyon
	var power: Dictionary = {}
	for node in s.run.map.all_nodes():
		if bool(node.get("power", false)):
			power = node
	assert_false(power.is_empty())
	assert_false(s.can_cut_power(), "only in the Power Room")
	s.run.current_node_id = power["id"]
	var prev := s.cut_power_preview()
	assert_eq(prev["asleep"], _cfg.hq_power_cut_steps)
	var alert := h.hq_alert
	s.cut_the_power()
	assert_eq(h.hq_asleep_left, 2)
	assert_eq(h.hq_alert, alert + _cfg.hq_alert_gain_power_cut)
	assert_eq(h.hq_alert, prev["alert"], "preview == result")
	assert_true(s.hq_asleep())
	for id in s.available_nodes():
		assert_eq(s.hq_option_state(id), EyeRules.NodeState.OPEN, "asleep: every option is open")
	assert_false(s.can_cut_power(), "once per run")
	assert_eq(s.cut_the_power()[0]["type"], "refused")
	s.stall()
	assert_true(s.hq_asleep())
	h.stalled_this_layer = false
	s.stall()
	assert_false(s.hq_asleep(), "two gaze steps, then it wakes")


func test_no_blade_while_asleep() -> void:
	var s := _hq(0)
	var h := s.run.corp_theme.halcyon
	h.hq_asleep_left = 2
	var id: StringName = s.available_nodes()[0]
	s.run.map.get_node(id)["az"] = 20
	s.enter_node(id)
	assert_eq(h.entered_state, EyeRules.NodeState.OPEN, "asleep: not SPOTTED")
	assert_eq(s.eye_blade_level(), 0)
	assert_false(s.combat.state.flags.has("blade"))


func test_eye_save_roundtrip() -> void:
	var s := _hq(5)
	var h := s.run.corp_theme.halcyon
	h.eye_step = 4
	h.hq_alert = 3
	h.hq_asleep_left = 1
	h.power_cut_used = true
	h.stalled_this_layer = true
	h.entered_state = EyeRules.NodeState.SPOTTED
	var back := RunState.from_dict(JSON.parse_string(JSON.stringify(s.run.to_dict())))
	var b := back.corp_theme.halcyon
	assert_eq([b.hq, b.eye_phase, b.eye_step, b.hq_alert, b.hq_asleep_left, b.power_cut_used, b.stalled_this_layer, b.entered_state], [true, 5, 4, 3, 1, true, true, 1])
	assert_eq(back.state_hash(), s.run.state_hash())
	var c2 := CampaignState.from_dict(JSON.parse_string(JSON.stringify(s.campaign.to_dict())))
	assert_eq(c2.corp_theme.halcyon.eye_index, 5, "eye_start is not redrawn")


func test_the_eye_chip_and_dial() -> void:
	var s := _hq(3)
	assert_eq(s.hq_dial().size(), _cfg.hq_dial_steps)
	assert_eq(s.hq_dial()[0]["centre"], EyeRules.gaze_centre(3, 0, _cfg))
	assert_false(s.theme_chip().is_empty())
	assert_eq(s.theme_chip()["value"], "%d/%d" % [s.run.corp_theme.halcyon.hq_alert, _cfg.hq_lockdown_alert])
