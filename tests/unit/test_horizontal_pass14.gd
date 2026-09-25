extends GutTest
## Horizontal pass 14 fixes (GAP_ANALYSIS H14): boss phases keep their pointer layout, the
## ICE extra pointer and bonus resistance; Audit rides attacks only; Mirror hubs and
## Daemons work on their own; Rig Core's free nudge arrives; Ghost Core covers card
## nudges; Firmware limits count per slot; Terminal Firmware that fits nothing is refused;
## start-of-turn kills end fights; achievements read the config; modals trap focus;
## netrun screens fit at text scale 1.6; closing the window saves; resumed runs record.

var _cfg: CampaignConfigData
var _text_scale_before: float = 1.0


func before_all() -> void:
	_cfg = CombatFixture.config()
	_text_scale_before = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _boss(id: StringName, overrides: Dictionary = {}) -> CombatSession:
	return CombatSession.start(CombatFixture.resolver(), &"breaker", [id], 7, &"", 0, overrides)


## Drops the boss to `pct` of its HP and resolves a turn so its phases fire.
func _to_hp(s: CombatSession, pct: float) -> CombatantState:
	s.state.get_combatant(&"enemy_0").hp = int(s.state.get_combatant(&"enemy_0").max_hp * pct)
	s.apply(CombatAction.end_turn())
	return s.state.get_combatant(&"enemy_0")


func test_an_orbit_phase_sets_its_pointers() -> void:
	var boss := _to_hp(_boss(&"commons_array"), 0.6)
	assert_eq(boss.wheel.pointer_ticks.size(), 2, "the 66% phase has two readers")
	assert_eq(boss.wheel.pointer_orbit, 4)


func test_the_ice_extra_pointer_survives_multiply() -> void:
	var plain := _to_hp(_boss(&"renewal_engine"), 0.6)
	var hard := _to_hp(_boss(&"renewal_engine", {"boss_extra_pointer": 1}), 0.6)
	assert_eq(hard.wheel.pointer_ticks.size(), plain.wheel.pointer_ticks.size() + 1)


func test_a_wheel_swap_keeps_bonus_resistance() -> void:
	var boss := _to_hp(_boss(&"renewal_engine", {"enemy_resistance": 1}), 0.3)
	assert_true(boss.wheel.passive_resistance >= 1, "ICE / Heat resistance survives the swap")


func test_audit_rides_attack_slices_only() -> void:
	var r := CombatFixture.resolver()
	var s := CombatSession.start(r, &"breaker", [&"compliance_officer"], 4, &"", 0, {"heat": 50})
	var officer := s.state.get_combatant(&"enemy_0")
	var atk: SliceData = null
	var def: SliceData = null
	for id in officer.wheel.slot_slice_ids:
		var sl := r.lookup.get_content(id) as SliceData
		if sl.slice_type == RC.SliceType.ATTACK:
			atk = sl
		elif sl.slice_type == RC.SliceType.DEFEND:
			def = sl
	assert_eq(r._heat_listeners(s.state, officer, def).size(), 0, "no Audit on a Defend")
	assert_eq(r._heat_listeners(s.state, officer, atk).size(), 1, "Audit on an attack")


func test_mirror_hubs_run_their_combat_start_daemons() -> void:
	var template := ContentRegistry.get_content(&"rebel_cell") as CorporationData
	var lookup := GridFixture.lookup()
	var corp := RebelCellBuilder.build(template, {"classes": ["breaker"], "daemons": ["shield_cache"], "nodes": ["relay"], "assets": ["turret"]}, lookup)
	lookup.add(corp)
	var s := CombatSession.start(CombatResolver.new(_cfg, lookup), &"breaker", [corp.elites[0].id], 3)
	assert_true(s.state.get_combatant(&"enemy_0").shield > 0, "Shield Cache fired for the Mirror")


func test_enemy_perfect_hooks_need_no_player_streak() -> void:
	var r := CombatFixture.resolver()
	var s := _boss(&"renewal_engine")
	var te := CombatFixture.triggered(RC.Trigger.ON_PERFECT, [CombatFixture.effect(RC.EffectType.HEAL, RC.EffectTarget.SELF, 2)])
	s.state.consecutive_perfects = 0
	assert_true(r.fx.trigger_matches(s.state, te, RC.Trigger.ON_PERFECT, {"owner": s.state.get_combatant(&"enemy_0"), "tier": RC.PrecisionTier.PERFECT}))


func test_rig_core_banks_its_free_nudge_for_next_turn() -> void:
	var s := CombatSession.start(CombatFixture.resolver(), &"rigger", [&"triage_unit"], 5)
	var cls := ContentRegistry.get_content(&"rigger") as ClassData
	CombatFixture.land(s.state.player, 0)  # dead centre: Perfect
	s.apply(CombatAction.end_turn())
	assert_true(s.state.free_nudges > cls.free_nudges_per_turn, "the Perfect's free nudge arrives (%d)" % s.state.free_nudges)


func test_ghost_core_covers_card_nudges() -> void:
	var deck := ["fine_tune", "fine_tune", "fine_tune", "fine_tune", "fine_tune"]
	var s := CombatSession.start(CombatFixture.resolver(), &"ghost", [&"compliance_officer"], 4, &"", 0, {"deck": deck})
	var a := CombatAction.play_card(0, &"enemy_0")
	a.ring = RC.RingScope.OUTER
	a.direction = 1
	var r := s.apply(a)
	assert_true(r.ok(), r.error)
	assert_eq(CombatFixture.events_of(r, "ghost_nudge").size(), 1, "the first nudge slips past resistance")


func test_firmware_limits_count_per_slot() -> void:
	var r := CombatFixture.resolver()
	var s := CombatSession.start(r, &"breaker", [&"triage_unit"], 5)
	var fw := ContentRegistry.get_content(&"coolant_loop") as FirmwareData
	var base := {"owner": s.state.player, "slice": r.lookup.get_content(s.state.player.wheel.slot_slice_ids[0]), "firmware": fw, "segment": null}
	var a := base.duplicate()
	a["slice_index"] = 0
	var b := base.duplicate()
	b["slice_index"] = 2
	var ka: String = r._slice_listeners(s.state, a)[1]["limit_key"]
	var kb: String = r._slice_listeners(s.state, b)[1]["limit_key"]
	assert_ne(ka, kb, "two copies keep separate counters")


func _netrun() -> NetrunSession:
	var corp := ContentRegistry.get_content(&"solace") as CorporationData
	var c := CampaignRules.new_campaign(corp, _cfg, GridFixture.lookup(), 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	return NetrunSession.start(CombatFixture.resolver(), c, c.roster[0].id, 1, &"t1_a", 5, corp)


func test_terminal_choices_refuse_unfit_firmware_and_missing_cycles() -> void:
	var s := _netrun()
	var fw := EventChoiceData.new()
	fw.reward = ContentRegistry.get_content(&"nanite_mesh")
	assert_string_contains(s.choice_error(fw), "fits no slice", "a Breaker has no HEAL slice")
	var pricey := EventChoiceData.new()
	pricey.cycle_cost = s.run.cycles + 1
	assert_string_contains(s.choice_error(pricey), "Not enough Cycles")


func test_a_start_of_turn_kill_ends_the_fight() -> void:
	var zap := CombatFixture.triggered(RC.Trigger.ON_TURN_START, [CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.ALL_ENEMIES, 999)])
	var hub := CombatFixture.hub(&"h14_zap", 0, [zap])
	var atk := CombatFixture.slice(&"h14_atk", RC.SliceType.ATTACK, 6)
	var deck: Array[CardData] = [CombatFixture.card(&"h14_noop", [CombatFixture.effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 0)])]
	var cls := CombatFixture.operative_class(&"h14_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, atk], hub), deck)
	var enemy := CombatFixture.enemy(&"h14_dummy", 50, CombatFixture.miss_wheel())
	var s := CombatSession.start(CombatFixture.resolver([cls, enemy]), cls.id, [enemy.id], 3)
	assert_true(s.state.is_over(), "the turn-start zap won the fight")
	assert_eq(s.state.outcome, CombatState.Outcome.VICTORY)


func test_achievement_thresholds_come_from_the_config() -> void:
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.achievement_racks = 2
	var p := ProfileState.new()
	p.stats["racks"] = 2
	assert_true(Achievements.check(p, null, [], 20, cfg).has(&"banked"))
	assert_false(Achievements.check(p, null, [], 20, _cfg).has(&"banked"))
	assert_eq(Achievements._top_threshold(_cfg), _cfg.heat_max, "Purge Survivor tracks the top threshold")


func test_an_old_per_slot_profile_is_read_when_the_shared_one_is_missing() -> void:
	var legacy := "user://gut_test_legacy_profile.json"
	var p := ProfileState.new()
	p.add_unlock(&"gut_legacy_unlock")
	SaveService.save_dict(legacy, {"profile": p.to_dict()})
	RunManager.load_profile_from("user://gut_test_missing_profile.json", legacy)
	assert_true(RunManager.profile.unlocks.has(&"gut_legacy_unlock"))
	DirAccess.remove_absolute(legacy)
	RunManager.reset()


func _neighbours_inside(root: Control, c: Control) -> bool:
	for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
		var n := c.find_valid_focus_neighbor(side)
		if n != null and not root.is_ancestor_of(n):
			return false
	return true


func test_confirm_dialogs_and_the_pause_menu_trap_focus() -> void:
	var behind := Button.new()
	behind.text = "behind"
	add_child_autofree(behind)
	var d := ConfirmDialog.new("Really?")
	add_child(d)
	await _frames()
	assert_true(_neighbours_inside(d, d.no_button) and _neighbours_inside(d, d.yes_button), "the dialog keeps focus")
	assert_eq(d.no_button.find_valid_focus_neighbor(SIDE_LEFT), d.yes_button, "Yes is reachable by D-pad")
	d.queue_free()
	var menu := PauseMenu.new()
	add_child_autofree(menu)
	await _frames()
	for b in menu.find_children("*", "Button", true, false):
		if (b as Control).is_visible_in_tree():
			assert_true(_neighbours_inside(menu, b), "%s stays in the menu" % b.text)


func test_netrun_screens_fit_at_the_largest_text_scale() -> void:
	RunManager.save_slot = "gut_test_netrun_root_h14"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var scene: Control = add_child_autofree(load("res://scenes/netrun_map/netrun_scene.tscn").instantiate())
	scene.start_run(1)
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	scene._show_current()
	await _frames()
	var root: Control = scene._status.get_parent()
	assert_true(root.get_combined_minimum_size().x <= 1280.0, "netrun root %d px" % root.get_combined_minimum_size().x)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func test_closing_the_window_saves_and_a_resumed_run_records() -> void:
	RunManager.save_slot = "gut_test_close_h14"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	RunManager.start_run()
	RunManager.delete_save()
	RunManager._notification(Node.NOTIFICATION_WM_CLOSE_REQUEST)
	assert_true(RunManager.has_save(), "closing the window saved the run")
	RunManager._history_recorded = true
	assert_true(RunManager.resume())
	assert_false(RunManager._history_recorded, "the resumed run will be recorded")
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
