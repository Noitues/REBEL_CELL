extends RefCounted
## The schema smoke test's checks (every `scripts/data/` schema: validation, defaults, save
## round trips). Run by tools/schema_smoke_test.gd, which loads this file only after the
## content is loaded (ANIM-R5 P17: see that file). A schema change adds its check here.


## Runs every check; returns the number that failed (each prints what it saw).
func run() -> int:
	return _batch1() + _batch2() + _batch3() + _art1_glyphs() + _art5_city_motion() + _art8_hq_compound() + _m14_letterhead() \
		+ _t2_heuristic_strategist() + _n1_amount_mode() + _n3_phases() + _n4_enrage() + _n13_undock() + _n11_pointer_ticks() + _n12_slot_sizes() + _n21_resistance() + _n14_sandbox_charges() + _n22_normal_pool() + _na21_netrun_art_config() + _n8_status_stacks() + _na22_city_shader_config() + _n20_slice_riders() + _na23_street_route_config() + _n6_listeners() + _na24_dressing_config() + _na12_city_gen() \
		+ _wh02_corp_theme_config() + _p2_street_r2_config() + _p2_street_r2_render_config() + _city_a2_config() + _raid_fix_a_config() + _ev01_event_schema() + _solace_tide_config() + _raid_model_switch()


## Plan 2 WH-02: CampaignConfigData's "Corp theme" section ships the WH-01 tables' defaults
## (one key per corporation spot-checked, the shipped config reading them) and a save keeps a
## changed key.
func _wh02_corp_theme_config() -> int:
	var fails := 0
	var d := CampaignConfigData.new()
	print("WH-02 corp theme defaults (expect 3000 45 3 1 5 [ROOF, STREET, SEWER]): ", d.bloom_hq_start_gap_milli, " ", d.eye_step_deg,
		" ", d.hq_lanes_required, " ", d.street_dark_nodes, " ", d.meridian_capacity_base, " ", d.hq_lane_ids)
	if d.bloom_hq_start_gap_milli != 3000 or d.eye_step_deg != 45 or d.hq_lanes_required != 3 or d.street_dark_nodes != 1 or d.meridian_capacity_base != 5: fails += 1
	if d.hq_lane_ids != ([&"ROOF", &"STREET", &"SEWER"] as Array[StringName]) or d.lane_tag_default != &"STREET": fails += 1
	if d.raid_infection_lost_bp != 10000 or d.meridian_weigh_station_layers != PackedInt32Array([4, 7, 10]): fails += 1
	# Solace v2: Heat pace table, Exploit forms, decay keys; ExploitData flags default off.
	if d.bloom_pace_heat_pct_by_band != PackedInt32Array([100, 110, 125, 140, 160]) or d.bloom_breach_setback_milli != 1000 or d.bloom_intel_turn_pct != 50: fails += 1
	if d.raid_infection_decay_hold_bp != 1000 or d.raid_infection_decay_per_kill_bp != 100 or d.raid_infection_decay_cure_bp != 1500: fails += 1
	# Halcyon v2: the Eye keys, Blade level, Alert and Lockdown, HQ graph tables.
	if d.eye_move_per_turn != 1 or d.eye_fix_turns != 2 or d.blade_level_max != 2 or d.hq_lockdown_alert != 4 or d.hq_power_cut_steps != 2: fails += 1
	if d.hq_alert_gain_eye_fight != 1 or d.hq_alert_gain_stall != 1 or d.hq_alert_gain_power_cut != 2 or d.hq_gaze_step_per_stall != 1: fails += 1
	if d.halcyon_hq_layer_kinds.size() != 13 or d.halcyon_hq_layer_face_deg.size() != 13 or d.halcyon_hq_rest_heal_pct != 35: fails += 1
	var ex_flags := ExploitData.new()
	if ex_flags.bloom_pace_cut or ex_flags.bloom_setback or ex_flags.bloom_turn_cut: fails += 1
	var shipped: CampaignConfigData = load("res://content/config/campaign_config.tres")
	if shipped == null or shipped.bloom_max_gap_milli != d.bloom_max_gap_milli or shipped.hq_lead_limit != d.hq_lead_limit: fails += 1
	# RG-01: the run_graph v2 keys (shipped = default).
	if shipped == null or not shipped.map_v2_enabled or shipped.map_unique_allow != PackedStringArray(["orbital_uplink_dish"]): fails += 1
	# RG-02: the REST keys (shipped = default).
	if shipped == null or shipped.rest_heal_pct != 35 or shipped.rest_rewire_swaps != 1 or shipped.node_weight_rest != 100 or shipped.rest_guaranteed_layers != Vector2i(4, 5) or shipped.rest_extra_chance_pct_by_tier != PackedInt32Array([0, 15, 35, 35]) or shipped.rest_max_per_run != 2: fails += 1
	# RG-03: the Workshop keys (shipped = default).
	if shipped == null or shipped.workshop_offers_per_visit != 3 or shipped.workshop_buys_per_visit != 1 or shipped.workshop_slice_price != 60 or shipped.workshop_null_slice_price != 90 or shipped.node_weight_workshop != 90 or shipped.workshop_min_tier != 2 or shipped.workshop_layers != Vector2i(3, 6): fails += 1
	# RG-04: the Cache keys (shipped = default; the puzzle is off).
	if shipped == null or shipped.node_weight_cache != 60 or shipped.cache_layers != Vector2i(2, 6) or shipped.cache_cycles_range != Vector2i(30, 60) or shipped.cache_card_choices != 3 or shipped.cache_puzzle_enabled: fails += 1
	# Solace vertical: campaign_focus_corp ships off ("" = all corporations).
	if shipped == null or shipped.campaign_focus_corp != &"" or d.campaign_focus_corp != &"": fails += 1
	# WH-10: the Solace HQ ladder keys.
	if d.solace_hq_rungs != 9 or d.solace_hq_mini_boss_rung != 9 or d.solace_hq_ward_rest_rungs != PackedInt32Array([5, 8]) or d.solace_hq_ward_weights.size() != 5 or d.solace_hq_billing_weights.size() != 5: fails += 1
	# EX-02 / EX-03: the exploit building keys.
	if d.exploit_building_kinds != {"solace/virus": "culture_garden"} or d.exploit_building_clearance_bu != 8.0 or d.exploit_building_lot_w_bu != 48.0 or d.exploit_building_lot_d_bu != 42.0 or d.exploit_building_outside_layers != 4 or d.exploit_building_inside_layers != 5 or d.exploit_building_max_width != 3: fails += 1
	d.bloom_dose_price = 21
	d.blade_classes_l1 = [&"ELITE"] as Array[StringName]
	var err := ResourceSaver.save(d, "user://smoke_wh02_config.tres")
	var back: CampaignConfigData = ResourceLoader.load("user://smoke_wh02_config.tres", "", ResourceLoader.CACHE_MODE_IGNORE)
	print("WH-02 corp theme save=", err, " dose price ", back.bloom_dose_price if back != null else -1)
	if err != OK or back == null or back.bloom_dose_price != 21 or back.blade_classes_l1 != ([&"ELITE"] as Array[StringName]): fails += 1
	return fails


## Plan 2 N6: ListenerData defaults (ON_PERFECT, unauthored caps, WEAK), the two appended
## triggers, a bad listener refused by code, a save keeps it on an EnemyData and a HubCoreData,
## the config default ships 1 and 0 is refused.
func _n6_listeners() -> int:
	var fails := 0
	var l := ListenerData.new()
	print("N6 listener defaults (expect 6 -1 -1 0; triggers 15 16): ", l.trigger, " ", l.max_per_turn, " ", l.max_per_combat, " ", l.min_tier,
		"; ", RC.Trigger.ON_RAM_SPENT, " ", RC.Trigger.ON_HIT_DEALT)
	if l.trigger != RC.Trigger.ON_PERFECT or l.max_per_turn != -1 or l.max_per_combat != -1 or l.min_tier != RC.PrecisionTier.WEAK: fails += 1
	if RC.Trigger.ON_RAM_SPENT != RC.Trigger.ON_SATELLITE_DESTROYED + 1 or RC.Trigger.ON_HIT_DEALT != RC.Trigger.ON_RAM_SPENT + 1: fails += 1
	l.trigger = RC.Trigger.ON_TURN_START
	l.max_per_turn = 0
	var codes := ",".join(l.validate())
	print("N6 bad listener: ", codes)
	if not (codes.contains("trigger_not_listenable") and codes.contains("no_effects") and codes.contains("cap_not_positive")): fails += 1
	var block := EffectData.new(); block.type = RC.EffectType.GAIN_BLOCK; block.target = RC.EffectTarget.SELF; block.amount = 2
	l.trigger = RC.Trigger.ON_HIT_DEALT; l.max_per_turn = 2; l.max_per_combat = 3
	var fx_list: Array[EffectData] = [block]
	l.effects = fx_list
	var ls: Array[ListenerData] = [l]
	var e := EnemyData.new(); e.id = &"smoke_listener_enemy"; e.listeners = ls
	var h := HubCoreData.new(); h.id = &"smoke_listener_hub"; h.listeners = ls
	var err := ResourceSaver.save(e, "user://smoke_listener_enemy.tres")
	var err2 := ResourceSaver.save(h, "user://smoke_listener_hub.tres")
	var back: EnemyData = ResourceLoader.load("user://smoke_listener_enemy.tres", "", ResourceLoader.CACHE_MODE_IGNORE)
	var back_h: HubCoreData = ResourceLoader.load("user://smoke_listener_hub.tres", "", ResourceLoader.CACHE_MODE_IGNORE)
	var ok := back != null and back_h != null and back.listeners.size() == 1 and back_h.listeners.size() == 1
	print("N6 listener save=", err, " ", err2, " back ", [back.listeners[0].trigger, back.listeners[0].max_per_turn, back.listeners[0].max_per_combat] if ok else [])
	if err != OK or err2 != OK or not ok or back.listeners[0].trigger != RC.Trigger.ON_HIT_DEALT or back.listeners[0].max_per_combat != 3 \
			or back.listeners[0].validate().size() != 0: fails += 1
	var d := CampaignConfigData.new()
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N6 listener default cap (expect 1 1): ", d.listener_max_per_turn_default, " ", cfg.listener_max_per_turn_default)
	if d.listener_max_per_turn_default != 1 or cfg.listener_max_per_turn_default != 1: fails += 1
	d.listener_max_per_turn_default = 0
	if not ",".join(d.validate()).contains("listener_max_per_turn_default"): fails += 1
	return fails


## Plan 2 N20: SliceData riders default to a plain slice; a bad one is refused by code; a
## save keeps all four; riders on a non-damage slice are refused.
func _n20_slice_riders() -> int:
	var fails := 0
	var s := SliceData.new(); s.id = &"smoke_rider"; s.slice_type = RC.SliceType.SHIM; s.base_output = 2
	print("N20 rider defaults (expect 1 0 0 1 false false): ", s.hits, " ", s.hits_per_target_status, " ", s.hits_per_status_slice, " ", s.perfect_multiplier, " ", s.pierce, " ", s.has_riders())
	if s.hits != 1 or s.hits_per_target_status != RC.Status.NONE or s.hits_per_status_slice != 0 or s.perfect_multiplier != 1.0 or s.pierce or s.has_riders(): fails += 1
	s.hits = 0; s.perfect_multiplier = 0.0
	var codes := ",".join(s.validate())
	print("N20 bad riders: ", codes)
	if not (codes.contains("hits_lt_1") and codes.contains("perfect_multiplier_not_positive")): fails += 1
	s.hits = 3; s.perfect_multiplier = 4.0; s.pierce = true
	s.hits_per_target_status = RC.Status.CORRUPTED; s.hits_per_status_slice = 1
	var err := ResourceSaver.save(s, "user://smoke_riders.tres")
	var back: SliceData = ResourceLoader.load("user://smoke_riders.tres", "", ResourceLoader.CACHE_MODE_IGNORE)
	print("N20 rider save=", err, " back ", [back.hits, back.hits_per_target_status, back.hits_per_status_slice, back.perfect_multiplier, back.pierce] if back != null else [])
	if err != OK or back == null or back.hits != 3 or back.hits_per_target_status != RC.Status.CORRUPTED or back.hits_per_status_slice != 1 \
			or back.perfect_multiplier != 4.0 or not back.pierce or back.validate().size() != 0: fails += 1
	s.slice_type = RC.SliceType.DEFRAG
	if not ",".join(s.validate()).contains("riders_on_non_damage"): fails += 1
	return fails




## NA-24: DressingConfigData (the street dressing's reveal groups, palettes, districts, bands): the shipped one validates, an
## empty one reports its gaps, a district naming an unknown palette set is refused by name.
## CITY-A2 step 1: CampaignConfigData's planner-city fields (`city_a2_*`): the shipped ones match the defaults and
## validate, the vendored city_A2.json loads clean, a bad block range is refused. Step 2: the terrain numbers (shipped =
## defaults, a bad beach range and land step refused by name), the step 2 sections of city_A2.json (rails, stations,
## landmarks, interchanges, walls, checkpoints, the drowned quarter, the port, undercity tunnels) and the removed grid
## generator's fields gone.
func _city_a2_config() -> int:
	var fails := 0
	var d := CampaignConfigData.new()
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("CITY-A2 config (expect Vector2i(4, 7) 121.212): ", cfg.city_a2_block_lots, " ", cfg.city_a2_metres_per_lot)
	if d.city_a2_block_lots != cfg.city_a2_block_lots or d.city_a2_path != cfg.city_a2_path or d.city_a2_budget_s != cfg.city_a2_budget_s: fails += 1
	if ",".join(cfg.validate()).contains("city_a2"): fails += 1
	var a2 := CityPlanA2.load_path(cfg.city_a2_path)
	print("CITY-A2 file (expect 0 7 53): ", a2.errors.size(), " ", a2.districts.size(), " ", a2.roads.size())
	if not a2.errors.is_empty() or a2.districts.size() != 7: fails += 1
	var bad: CampaignConfigData = cfg.duplicate()
	bad.city_a2_block_lots = Vector2i(5, 3)
	var codes := ",".join(bad.validate())
	print("CITY-A2 bad: ", codes.contains("city_a2_block_lots"))
	if not codes.contains("city_a2_block_lots"): fails += 1
	print("CITY-A2 step 2 terrain (expect road_001 1.5 3 120 5101): ", cfg.city_a2_outer_ring, " ", cfg.city_a2_hill_exag, " ",
		cfg.city_a2_land_step, " ", cfg.city_a2_land_margin, " ", cfg.city_a2_terrain_seed)
	if d.city_a2_outer_ring != cfg.city_a2_outer_ring or d.city_a2_beach != cfg.city_a2_beach \
			or d.city_a2_land_step != cfg.city_a2_land_step or d.city_a2_noise_cells != cfg.city_a2_noise_cells: fails += 1
	var bad_t: CampaignConfigData = cfg.duplicate()
	bad_t.city_a2_beach = Vector2(3, 1)
	bad_t.city_a2_land_step = 0
	var t_codes := ",".join(bad_t.validate())
	print("CITY-A2 step 2 bad terrain: ", t_codes.contains("city_a2_beach"), " ", t_codes.contains("city_a2_land_step"))
	if not (t_codes.contains("city_a2_beach") and t_codes.contains("city_a2_land_step")): fails += 1
	# CITY-A2 r2: one land surface, open land, corridors.
	print("CITY-A2 r2 (expect 12 42 0.3 (4.0, 22.0) 1): ", cfg.city_a2_land_blend, " ", cfg.city_a2_max_build_h, " ",
		cfg.city_a2_max_build_slope, " ", cfg.city_a2_sprawl_fade, " ", cfg.city_a2_corridor.get(&"ring", 0))
	if d.city_a2_land_blend != cfg.city_a2_land_blend or d.city_a2_max_build_h != cfg.city_a2_max_build_h \
			or d.city_a2_mountain_edge != cfg.city_a2_mountain_edge \
			or int(cfg.city_a2_corridor.get(&"ring", 0)) != 1 or d.city_a2_land_margin != cfg.city_a2_land_margin \
			or d.city_a2_hill_exag != cfg.city_a2_hill_exag: fails += 1
	var bad_r2: CampaignConfigData = cfg.duplicate()
	bad_r2.city_a2_sprawl_fade = Vector2(6, 1)
	print("CITY-A2 r2 bad: ", ",".join(bad_r2.validate()).contains("city_a2_sprawl_fade"))
	if not ",".join(bad_r2.validate()).contains("city_a2_sprawl_fade"): fails += 1
	print("CITY-A2 step 2 sections (expect 12 45 40 21 6 24 true true 5): ", a2.rails.size(), " ", a2.stations.size(), " ", a2.landmarks.size(),
		" ", a2.interchanges.size(), " ", a2.walls.size(), " ", a2.checkpoints.size(), " ", not a2.drowned.is_empty(), " ",
		not a2.port.is_empty(), " ", a2.undercity_tunnels.size())
	if a2.rails.size() != 12 or a2.stations.size() != 45 or a2.landmarks.size() != 40 or a2.interchanges.size() != 21 or a2.walls.size() != 6 \
			or a2.checkpoints.size() != 24 or a2.drowned.is_empty() or a2.port.is_empty() or a2.undercity_tunnels.size() != 5: fails += 1
	for gone: String in ["city_layout_source", "city_gen_ring_lots", "city_gen_bay_depth", "city_gen_budget_s"]:
		if gone in d:
			print("CITY-A2 step 2: removed field still there: ", gone)
			fails += 1
	# LOOK L5 (whole-city plate parity, designer 2026-10-20): the cliff, dwindle, height spread, drowned sink, coast setback,
	# street prune and coast smoothing default off (the old city), and the shipped config turns them on.
	print("CITY-A2 LOOK L5 (expect 14 0.7 2 1 2 (0.45, 0.5, 14) (0.06, 1.9)): ", cfg.city_a2_cliff, " ", cfg.city_a2_sink_share, " ",
		cfg.city_a2_coast_setback, " ", cfg.city_a2_prune_streets, " ", cfg.city_a2_coast_smooth, " ", cfg.city_a2_dwindle, " ",
		cfg.city_a2_height_spike)
	if d.city_a2_cliff != 0.0 or d.city_a2_sink_share != 0.0 or d.city_a2_coast_setback != 0 or d.city_a2_prune_streets != 0 \
			or d.city_a2_coast_smooth != 0.0 or d.city_a2_dwindle.z != 0.0 or d.city_a2_height_spike.x != 0.0: fails += 1
	if cfg.city_a2_cliff != 14.0 or cfg.city_a2_coast_setback != 2 or cfg.city_a2_prune_streets != 1 or cfg.city_a2_coast_smooth != 2.0: fails += 1
	# Solace district layout (A-069 / A-070): off in the script default, on in the shipped config with the ruled numbers.
	print("Solace layout (expect false true (2, 3) 0.5 3 35): ", d.city_sol_layout, " ", cfg.city_sol_layout, " ", cfg.city_sol_block_lots, " ",
		cfg.city_sol_height_k, " ", cfg.city_sol_min_floors, " ", cfg.city_sol_plinth_r_bu)
	if d.city_sol_layout or not cfg.city_sol_layout or cfg.city_sol_block_lots != Vector2i(2, 3) or cfg.city_sol_height_k != 0.5 \
			or cfg.city_sol_min_floors != 3 or cfg.city_sol_plinth_r_bu != 35.0: fails += 1
	# ... and its shipped terrain numbers differ from the step 2 defaults: taller mountains nearer the ring, the sprawl fading
	# over 4..22 lots past it.
	print("CITY-A2 LOOK L5 terrain (expect 125 (24, 78) (4, 22)): ", cfg.city_a2_mountain_h, " ", cfg.city_a2_mountain, " ",
		cfg.city_a2_sprawl_fade)
	if cfg.city_a2_mountain_h != 125.0 or cfg.city_a2_mountain != Vector2(24, 78) or cfg.city_a2_sprawl_fade != Vector2(4, 22): fails += 1
	return fails


## NA-12: CampaignState keeps its city seed through to_dict / from_dict as a u64 decimal string (CITY-A2 step 2: the
## grid generator's numbers are gone; the three the planner city keeps validate).
func _na12_city_gen() -> int:
	var fails := 0
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	if ",".join(cfg.validate()).contains("city_gen"): fails += 1
	var bad: CampaignConfigData = cfg.duplicate()
	bad.city_gen_aim_step_deg = 0.0
	var codes := ",".join(bad.validate())
	print("NA-12 bad city gen: ", codes.contains("city_gen_aim_step_deg"))
	if not codes.contains("city_gen_aim_step_deg"): fails += 1
	var c := CampaignState.new()
	c.city_seed = -2
	var back := CampaignState.from_dict(c.to_dict())
	print("NA-12 city_seed save (expect 18446744073709551614 -2): ", c.to_dict()["city_seed"], " ", back.city_seed)
	if c.to_dict()["city_seed"] != "18446744073709551614" or back.city_seed != -2: fails += 1
	return fails



func _na24_dressing_config() -> int:
	var fails := 0
	var cfg: DressingConfigData = load(DressingConfigData.CONFIG_PATH)
	var errs := cfg.validate() if cfg != null else PackedStringArray(["missing"])
	print("NA-24 shipped dressing config errors (expect 0): ", errs)
	if errs.size() != 0 or cfg == null: return fails + 1
	if DressingConfigData.new().validate().size() <= 5: fails += 1
	var bad: DressingConfigData = cfg.duplicate(true)
	bad.districts["halcyon"] = {"palette": "no_such_set"}
	if not ",".join(bad.validate()).contains("districts.halcyon"): fails += 1
	var no_acc: DressingConfigData = cfg.duplicate(true)
	(no_acc.palettes["solace_mint"] as Dictionary).erase("accent")
	if not ",".join(no_acc.validate()).contains("palettes.solace_mint.accent"): fails += 1
	return fails


## NA-23: StreetRouteConfigData (the street netrun view's tuning numbers): the shipped one validates, an empty one reports its
## gaps, a bad hover level is refused by name.
func _na23_street_route_config() -> int:
	var fails := 0
	var cfg: StreetRouteConfigData = load(StreetRouteConfigData.CONFIG_PATH)
	var errs := cfg.validate() if cfg != null else PackedStringArray(["missing"])
	print("NA-23 shipped street route config errors (expect 0): ", errs)
	if errs.size() != 0 or cfg == null: return fails + 1
	if StreetRouteConfigData.new().validate().size() <= 20: fails += 1
	var bad: StreetRouteConfigData = cfg.duplicate(true)
	bad.hover["cut_level"] = 2.0
	if not ",".join(bad.validate()).contains("hover.cut_level"): fails += 1
	return fails


## NA-22: CityShaderConfigData (the netrun city shaders' tuning numbers): the shipped one validates, an empty one reports
## its gaps, a bad loop is refused by name.
func _na22_city_shader_config() -> int:
	var fails := 0
	var cfg: CityShaderConfigData = load(CityShaderConfigData.CONFIG_PATH)
	var errs := cfg.validate() if cfg != null else PackedStringArray(["missing"])
	print("NA-22 shipped city shader config errors (expect 0): ", errs)
	if errs.size() != 0 or cfg == null: return fails + 1
	var empty := CityShaderConfigData.new()
	if empty.validate().size() <= 20: fails += 1
	var bad: CityShaderConfigData = cfg.duplicate(true)
	bad.streak["loop_s"] = 0.0
	if not ",".join(bad.validate()).contains("streak.loop_s"): fails += 1
	# A-022: the `aaa` block (the plates' street look) is required and each of its sections is named when missing.
	var no_post: CityShaderConfigData = cfg.duplicate(true)
	no_post.aaa.erase("post")
	if not ",".join(no_post.validate()).contains("aaa.post"): fails += 1
	return fails


## NA-21: NetrunArtConfigData (the netrun-art twins' tuning numbers): the shipped one validates, the timings are
## the frozen 0.9 s step and 1.0 s Z, an empty one reports its gaps, and a save keeps the rig.
func _na21_netrun_art_config() -> int:
	var fails := 0
	var cfg: NetrunArtConfigData = load(NetrunArtConfigData.CONFIG_PATH)
	var errs := cfg.validate() if cfg != null else PackedStringArray(["missing"])
	print("NA-21 shipped netrun art config errors (expect 0): ", errs)
	if errs.size() != 0 or cfg == null: return fails + 1
	print("NA-21 timings (expect 0.9 1.0): ", cfg.rig["t_step"], " ", cfg.rig["t_zoom"])
	if not is_equal_approx(float(cfg.rig["t_step"]), 0.9) or not is_equal_approx(float(cfg.rig["t_zoom"]), 1.0): fails += 1
	var empty := NetrunArtConfigData.new()
	var ee := empty.validate()
	print("NA-21 empty config errors (expect more than 10): ", ee.size())
	if ee.size() <= 10: fails += 1
	var t := NetrunArtConfigData.new()
	t.rig = {"t_step": 1.5}
	var err := ResourceSaver.save(t, "user://smoke_netrun_art.tres")
	var back: NetrunArtConfigData = load("user://smoke_netrun_art.tres")
	if err != OK or back == null or not is_equal_approx(float(back.rig["t_step"]), 1.5): fails += 1
	return fails


## Plan 2 N8 (×N status stacks): RC.Status.OUTPUT_DOWN = 5 (PARASITE stays 4 for v2 saves),
## EffectData.stacks (default 1) and cleanse_mode (default ALL) survive a save, the config's
## stack fields default 0.25 / 2 / 5 and ship so, and bad stack counts are refused.
func _n8_status_stacks() -> int:
	var fails := 0
	print("N8: OUTPUT_DOWN = ", RC.Status.OUTPUT_DOWN, " PARASITE = ", RC.Status.PARASITE, " CleanseMode = ", RC.CleanseMode.keys())
	if RC.Status.OUTPUT_DOWN != 5 or RC.Status.PARASITE != 4 or RC.CleanseMode.ONE_STACK != 1: fails += 1
	# N9: TIER_DOWN is appended, the RAM-cost numbers default 2 / 2 and ship so.
	if RC.Status.TIER_DOWN != 6 or CampaignConfigData.new().corrupted_ram_cost_multiplier != 2 or CampaignConfigData.new().corrupted_enemy_ram_divisor != 2: fails += 1
	var e := EffectData.new()
	e.type = RC.EffectType.APPLY_STATUS
	e.status = RC.Status.OUTPUT_DOWN
	print("N8: EffectData stacks default ", e.stacks, " cleanse_mode default ", e.cleanse_mode)
	if e.stacks != 1 or e.cleanse_mode != RC.CleanseMode.ALL: fails += 1
	e.stacks = 3
	e.cleanse_mode = RC.CleanseMode.ONE_STACK
	var err := ResourceSaver.save(e, "user://smoke_n8_effect.tres")
	var back: EffectData = load("user://smoke_n8_effect.tres")
	print("N8: effect save=", err, " stacks ", back.stacks if back != null else -1, " mode ", back.cleanse_mode if back != null else -1)
	if err != OK or back == null or back.stacks != 3 or back.cleanse_mode != RC.CleanseMode.ONE_STACK: fails += 1
	e.stacks = 0
	if not " ".join(e.validate()).contains("stack_amount_lt_1"): fails += 1
	e.stacks = 6
	if not " ".join(e.validate(5)).contains("stack_amount_gt_cap"): fails += 1
	var fresh := CampaignConfigData.new()
	var shipped: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N8: config defaults ", [fresh.output_down_per_stack, fresh.parasite_output_down_stacks, fresh.status_stack_cap],
		" shipped ", [shipped.output_down_per_stack, shipped.parasite_output_down_stacks, shipped.status_stack_cap])
	if fresh.output_down_per_stack != 0.25 or fresh.parasite_output_down_stacks != 2 or fresh.status_stack_cap != 5: fails += 1
	if shipped.output_down_per_stack != 0.25 or shipped.parasite_output_down_stacks != 2 or shipped.status_stack_cap != 5: fails += 1
	return fails


## Plan 2 N14 (ruling Q39): the SANDBOX charge counts default 1 / 2, ship 1 / 2, and bad
## values are refused.
func _n14_sandbox_charges() -> int:
	var fails := 0
	var d := CampaignConfigData.new()
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N14 sandbox charges default (expect 1 2): ", d.sandbox_charges, " ", d.sandbox_charges_perfect, " shipped ", cfg.sandbox_charges, " ", cfg.sandbox_charges_perfect)
	if d.sandbox_charges != 1 or d.sandbox_charges_perfect != 2 or cfg.sandbox_charges != 1 or cfg.sandbox_charges_perfect != 2: fails += 1
	d.sandbox_charges_perfect = 0
	if not ",".join(d.validate()).contains("sandbox_charges"): fails += 1
	return fails


## Plan 2 N11: pointers on any tick. WheelData / BossPhaseData refuse a tick outside 0-29 and
## two pointers on one tick by name; adjacent ticks are valid; the config carries the cap and
## the ICE extra-pointer offsets (legacy 15 / 10 / 20 / 5 / 25).
func _n11_pointer_ticks() -> int:
	var fails := 0
	var a := _slice(&"a", RC.SliceType.SHIM, 3)
	var adjacent := _wheel([a, a], PackedInt32Array([0, 1]))
	print("N11 adjacent pointers (expect []): ", adjacent.validate())
	if not adjacent.validate().is_empty(): fails += 1
	var dup := WheelData.pointer_errors(PackedInt32Array([7, 7, 30]))
	print("N11 duplicate + out of range: ", dup)
	if dup.size() != 2 or not dup[0].begins_with("pointer_ticks_duplicate") or not dup[1].begins_with("pointer_tick_out_of_range"): fails += 1
	var p := BossPhaseData.new(); p.pointer_behavior = RC.PointerBehavior.MULTIPLY; p.pointer_ticks = PackedInt32Array([3, 3])
	print("N11 phase duplicate: ", p.validate())
	if not "pointer_ticks_duplicate" in " ".join(p.validate()): fails += 1
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N11 config cap / offsets: ", cfg.max_pointers, " ", cfg.boss_extra_pointer_offsets)
	if cfg.max_pointers != 4 or cfg.boss_extra_pointer_offsets != PackedInt32Array([15, 10, 20, 5, 25]): fails += 1
	return fails


## Plan 2 N12: WheelSlotData.size_ticks (AUTO default) and tick_quality, FirmwareData
## tick_quality_step, WheelData.slice_count up to 30, the config caps and the default reach.
func _n12_slot_sizes() -> int:
	var fails := 0
	var slot := WheelSlotData.new()
	print("N12 slot defaults (expect -1, []): ", slot.size_ticks, " ", slot.tick_quality)
	if slot.size_ticks != RC.SIZE_AUTO or not slot.tick_quality.is_empty(): fails += 1
	print("N12 firmware step default (expect 0): ", FirmwareData.new().tick_quality_step)
	if FirmwareData.new().tick_quality_step != 0: fails += 1
	var a := _slice(&"a", RC.SliceType.SHIM, 3)
	var legacy := _wheel([a, a, a, a, a, a])
	print("N12 legacy sizes (expect six 5s): ", legacy.slot_sizes(), " ", legacy.validate())
	if legacy.slot_sizes() != PackedInt32Array([5, 5, 5, 5, 5, 5]) or not legacy.validate().is_empty(): fails += 1
	var uneven := _wheel([a, a, a, a, a, a, a, a])
	var sizes := [5, 4, 3, 4, 4, 3, 4, 3]
	for i in 8:
		uneven.slots[i].size_ticks = sizes[i]
	print("N12 uneven 8-slot wheel (expect []): ", uneven.validate())
	if not uneven.validate().is_empty(): fails += 1
	uneven.slots[0].size_ticks = 6
	if not "size_sum" in " ".join(uneven.validate()): fails += 1
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N12 config caps / min / reach: ", cfg.operative_slice_cap, " ", cfg.enemy_slice_cap, " ", cfg.slice_size_min, " ", cfg.tick_quality_good_reach)
	if cfg.operative_slice_cap != 6 or cfg.enemy_slice_cap != 30 or cfg.slice_size_min != 1 or cfg.tick_quality_good_reach != 1: fails += 1
	return fails


## Plan 2 N13: EffectData.undock (the Undock keyword) defaults false and survives a save; the
## shipped Undock card carries it; ON_SATELLITE_DESTROYED is appended after ON_RESOLVE.
func _n13_undock() -> int:
	var fails := 0
	var e := EffectData.new(); e.type = RC.EffectType.NUDGE
	print("N13 undock default (expect false): ", e.undock)
	if e.undock: fails += 1
	e.undock = true
	var err := ResourceSaver.save(e, "user://smoke_undock.tres")
	var back: EffectData = load("user://smoke_undock.tres")
	print("N13 undock save=", err, " back ", back.undock if back != null else null)
	if err != OK or back == null or not back.undock: fails += 1
	var card: CardData = load("res://content/cards/undock.tres")
	print("N13 Undock card keyword (expect true): ", card.effects[0].undock if card != null else null)
	if card == null or not card.effects[0].undock: fails += 1
	print("N13 ON_SATELLITE_DESTROYED (expect ON_RESOLVE + 1): ", RC.Trigger.ON_SATELLITE_DESTROYED)
	if RC.Trigger.ON_SATELLITE_DESTROYED != RC.Trigger.ON_RESOLVE + 1: fails += 1
	return fails


## Plan 2 N4: EnrageData defaults and save round trip; bad fields are refused by name; the
## config's per-class defaults (normal off); EnemyData.enrage on a normal is refused.
## Plan 2 N22 (ruling Q12): RC.NormalPool (EASY 0, HARD 1, appended); EnemyData.normal_pool
## defaults HARD and survives a save; EASY on an elite is refused by name; the config's
## easy_normal_fights ships 2; RunState.normal_fights_started round-trips and reads -1 when absent.
func _n22_normal_pool() -> int:
	var fails := 0
	print("N22 NormalPool (expect 0 1): ", RC.NormalPool.EASY, " ", RC.NormalPool.HARD)
	if RC.NormalPool.EASY != 0 or RC.NormalPool.HARD != 1: fails += 1
	var e := EnemyData.new(); e.id = &"smoke_pool"
	print("N22 normal_pool default (expect HARD=1): ", e.normal_pool)
	if e.normal_pool != RC.NormalPool.HARD: fails += 1
	e.normal_pool = RC.NormalPool.EASY
	var err := ResourceSaver.save(e, "user://smoke_pool.tres")
	var back: EnemyData = load("user://smoke_pool.tres")
	print("N22 normal_pool save=", err, " back ", back.normal_pool if back != null else -1)
	if err != OK or back == null or back.normal_pool != RC.NormalPool.EASY: fails += 1
	e.is_elite = true
	if not ",".join(e.validate(CampaignConfigData.new())).contains("pool_on_non_normal"): fails += 1
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N22 easy_normal_fights (expect 2): ", cfg.easy_normal_fights)
	if cfg.easy_normal_fights != 2: fails += 1
	var r := RunState.new(); r.normal_fights_started = 3
	var d := r.to_dict()
	var rb := RunState.from_dict(d)
	d.erase("normal_fights_started")
	print("N22 counter round trip (expect 3 -1): ", rb.normal_fights_started, " ", RunState.from_dict(d).normal_fights_started)
	if rb.normal_fights_started != 3 or RunState.from_dict(d).normal_fights_started != -1: fails += 1
	return fails


## Plan 2 N21 (rulings Q16, Q31): the config's per-class resistance ranges; a normal at 3 and
## a boss at 4 are refused by name; CombatantState.resistance_gain survives a save round trip.
func _n21_resistance() -> int:
	var fails := 0
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N21 resistance ranges (expect [1, 3, 3, 5] [2, 4, 4, 6]): ", cfg.resistance_min_by_class, " ", cfg.resistance_max_by_class)
	if cfg.resistance_min_by_class != PackedInt32Array([1, 3, 3, 5]) or cfg.resistance_max_by_class != PackedInt32Array([2, 4, 4, 6]): fails += 1
	var n := EnemyData.new(); n.id = &"smoke_res"; n.wheel = WheelData.new(); n.wheel.passive_resistance = 3
	if not ",".join(n.validate(cfg)).contains("resistance_out_of_range"): fails += 1
	var c := CombatantState.new(); c.resistance_gain = 2
	var back := CombatantState.from_dict(c.to_dict())
	print("N21 resistance_gain round trip (expect 2): ", back.resistance_gain)
	if back.resistance_gain != 2 or CombatantState.new().to_dict().has("resistance_gain"): fails += 1
	return fails

func _n4_enrage() -> int:
	var fails := 0
	var e := EnrageData.new()
	print("N4 enrage defaults (expect 10 5 25 0): ", e.start_turn, " ", e.every_n_turns, " ", e.damage_pct_step, " ", e.resistance_step)
	if e.start_turn != 10 or e.every_n_turns != 5 or e.damage_pct_step != 25 or e.resistance_step != 0: fails += 1
	e.resistance_step = 2
	var err := ResourceSaver.save(e, "user://smoke_enrage.tres")
	var back: EnrageData = load("user://smoke_enrage.tres")
	print("N4 enrage save=", err, " resistance_step ", back.resistance_step if back != null else -1)
	if err != OK or back == null or back.resistance_step != 2 or not back.validate().is_empty(): fails += 1
	e.start_turn = 0; e.every_n_turns = 0; e.damage_pct_step = -1; e.resistance_step = -1
	print("N4 bad enrage errors (expect 4): ", e.validate())
	if e.validate().size() != 4: fails += 1
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N4 enrage start by class ", cfg.enrage_start_turn_by_class)
	if cfg.enrage_default(RC.EnemyClass.NORMAL) != null or cfg.enrage_default(RC.EnemyClass.BOSS) == null: fails += 1
	var n := EnemyData.new(); n.id = &"smoke_norm"; n.enrage = EnrageData.new()
	if not ",".join(n.validate(CampaignConfigData.new())).contains("normal_has_enrage"): fails += 1
	return fails

## Plan 2 N3: BossPhaseData.cleanse_on_enter defaults NONE and survives a save; an unknown
## scope and a threshold outside (0, 1) are refused; the config's per-class phase counts.
func _n3_phases() -> int:
	var fails := 0
	var p := BossPhaseData.new()
	print("N3 cleanse default (expect 0): ", p.cleanse_on_enter)
	if p.cleanse_on_enter != RC.CleanseScope.NONE: fails += 1
	p.hp_threshold_pct = 0.68
	if p.threshold_bp() != 6800 or BossPhaseData.floor_of(100, p.threshold_bp()) != 68: fails += 1
	p.cleanse_on_enter = RC.CleanseScope.BOTH
	var err := ResourceSaver.save(p, "user://smoke_phase.tres")
	var back: BossPhaseData = load("user://smoke_phase.tres")
	print("N3 phase save=", err, " cleanse ", back.cleanse_on_enter if back != null else -1)
	if err != OK or back == null or back.cleanse_on_enter != RC.CleanseScope.BOTH or not back.validate().is_empty(): fails += 1
	p.set("cleanse_on_enter", 9)
	p.hp_threshold_pct = 1.0
	print("N3 bad phase errors (expect 2): ", p.validate())
	if p.validate().size() != 2: fails += 1
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("N3 phase counts min ", cfg.phase_count_min_by_class, " max ", cfg.phase_count_max_by_class)
	if cfg.phase_count_min_by_class.size() != RC.EnemyClass.size() or cfg.phase_count_max_by_class.size() != RC.EnemyClass.size(): fails += 1
	return fails


## Plan 2 N1: EffectData / SliceData.amount_mode: FLAT by default; PERCENT out of 0..100 or on a
## type without a percent reading is refused; a save keeps PERCENT.
func _n1_amount_mode() -> int:
	var fails := 0
	var e := EffectData.new(); e.type = RC.EffectType.HEAL; e.amount = 5
	var s := SliceData.new(); s.id = &"smoke_pct"; s.slice_type = RC.SliceType.HOTFIX; s.base_output = 5
	print("N1 amount_mode defaults (expect 0 0): ", e.amount_mode, " ", s.amount_mode)
	if e.amount_mode != RC.AmountMode.FLAT or s.amount_mode != RC.AmountMode.FLAT: fails += 1
	e.amount_mode = RC.AmountMode.PERCENT; e.amount = 101
	s.amount_mode = RC.AmountMode.PERCENT; s.slice_type = RC.SliceType.SHIM
	print("N1 bad PERCENT effect / slice errors (expect 1 1): ", e.validate(), " ", s.validate())
	if e.validate().size() != 1 or s.validate().size() != 1: fails += 1
	s.slice_type = RC.SliceType.HOTFIX
	var err := ResourceSaver.save(s, "user://smoke_amount_mode.tres")
	var back: SliceData = load("user://smoke_amount_mode.tres")
	print("N1 slice save=", err, " mode ", back.amount_mode if back != null else -1)
	if err != OK or back == null or back.amount_mode != RC.AmountMode.PERCENT or back.validate().size() != 0: fails += 1
	return fails


## Tooling 1 T2: HeuristicStrategistConfigData (the playtest strategist's thresholds): the shipped
## one validates; a 3-turn lookahead and an unknown HQ action are each refused; a save keeps its values.
func _t2_heuristic_strategist() -> int:
	var fails := 0
	var shipped := HeuristicStrategistConfigData.shipped()
	var se := shipped.validate() if shipped != null else PackedStringArray(["missing"])
	print("T2 shipped heuristic strategist config errors (expect 0): ", se)
	if se.size() != 0: fails += 1
	var bad := HeuristicStrategistConfigData.new()
	bad.lookahead_turns = 3
	bad.hq_priority = ["scrub", "buy_everything"]
	var be := bad.validate()
	print("T2 bad heuristic strategist config errors (expect 2): ", be)
	if be.size() != 2: fails += 1
	var t := HeuristicStrategistConfigData.new()
	t.breach_max_heat = 7
	t.hq_priority = ["recruit", "scrub"]
	var err := ResourceSaver.save(t, "user://smoke_heuristic_strategist.tres")
	var back: HeuristicStrategistConfigData = load("user://smoke_heuristic_strategist.tres")
	print("T2 heuristic strategist config save=", err, " breach_max_heat ", back.breach_max_heat if back != null else -1)
	if err != OK or back == null or back.breach_max_heat != 7 or back.hq_priority != ["recruit", "scrub"] or back.validate().size() != 0: fails += 1
	return fails


## M14 FOLLOW-UP: CorporationData.letterhead_name: "" by default (no error: the letterhead letters
## the display name), saved and loaded, and when set in capitals, no longer than the display name.
func _m14_letterhead() -> int:
	var fails := 0
	var corp := CorporationData.new(); corp.id = &"smoke_corp"; corp.display_name = "Meridian Freight Systems"
	var e := corp.letterhead_errors(); print("M14 letterhead default '", corp.letterhead_name, "' errors (expect 0): ", e)
	if corp.letterhead_name != "" or e.size() != 0: fails += 1
	corp.letterhead_name = "MERIDIAN FREIGHT"
	var err := ResourceSaver.save(corp, "user://smoke_corp_letterhead.tres")
	var loaded: CorporationData = load("user://smoke_corp_letterhead.tres")
	print("M14 letterhead save=", err, " loaded='", loaded.letterhead_name, "' errors (expect 0): ", loaded.letterhead_errors())
	if err != OK or loaded.letterhead_name != "MERIDIAN FREIGHT" or loaded.letterhead_errors().size() != 0: fails += 1
	corp.letterhead_name = "Meridian Freight"
	e = corp.letterhead_errors(); print("M14 letterhead lower case (expect 1): ", e)
	if e.size() != 1: fails += 1
	corp.letterhead_name = "MERIDIAN FREIGHT SYSTEMS INTERNATIONAL"
	e = corp.letterhead_errors(); print("M14 letterhead longer than the name (expect 1): ", e)
	if e.size() != 1: fails += 1
	return fails


func _mk_effect(t, target, amount := 0, scope := RC.RingScope.OUTER, mult := 1.0) -> EffectData:
	var e := EffectData.new()
	e.type = t; e.target = target; e.amount = amount; e.ring_scope = scope; e.multiplier = mult
	return e

func _batch1() -> int:
	var fails := 0
	# Slices
	var atk := SliceData.new(); atk.id = &"attack"; atk.slice_type = RC.SliceType.SHIM; atk.base_output = 6
	var crit := SliceData.new(); crit.id = &"crit"; crit.slice_type = RC.SliceType.OVERFLOW; crit.base_output = 12
	var def := SliceData.new(); def.id = &"defend"; def.slice_type = RC.SliceType.DEFRAG; def.target_rule = RC.TargetRule.SELF; def.base_output = 5
	var null_slice := SliceData.new(); null_slice.id = &"null"; null_slice.slice_type = RC.SliceType.NULL
	# Mirror firmware
	var mirror := FirmwareData.new(); mirror.id = &"mirror"; mirror.neighbor_rule = RC.NeighborRule.MIRROR
	var leech := FirmwareData.new(); leech.id = &"leech"
	leech.allowed_slice_types = [RC.SliceType.SHIM]
	var t := TriggeredEffectData.new(); t.min_tier = RC.PrecisionTier.GOOD
	t.effects = [_mk_effect(RC.EffectType.GAIN_RAM, RC.EffectTarget.SELF, 1)]
	leech.triggered_effects = [t]
	# Breaker hub
	var hub := HubCoreData.new(); hub.id = &"breaker_core"
	var hook := TriggeredEffectData.new(); hook.trigger = RC.Trigger.ON_PERFECT
	hook.effects = [_mk_effect(RC.EffectType.RETRIGGER, RC.EffectTarget.SELF)]
	hub.perfect_hook = hook
	# Wheel
	var w := WheelData.new(); w.hub = hub
	var layout = [crit, atk, atk, atk, def, null_slice]
	var slots: Array[WheelSlotData] = []
	for s in layout:
		var sl := WheelSlotData.new(); sl.slice = s; slots.append(sl)
	slots[1].firmware = leech
	slots[4].firmware = leech   # should fail: leech only fits SHIM
	w.slots = slots
	var errs := w.validate()
	print("Breaker wheel errors (expect 1): ", errs)
	if errs.size() != 1: fails += 1
	# Satellite wheel with 3 slices
	var sat := WheelData.new(); sat.slice_count = 3
	var sslots: Array[WheelSlotData] = []
	for s in [atk, def, atk]:
		var sl := WheelSlotData.new(); sl.slice = s; sslots.append(sl)
	sat.slots = sslots
	print("Satellite errors (expect 0): ", sat.validate(), " ticks/slice=", sat.ticks_per_slice())
	if sat.validate().size() != 0: fails += 1
	# Boss with 3 pointers, bad 4-slice
	var bad := WheelData.new(); bad.slice_count = 4
	print("4-slice errors (expect >=1): ", bad.validate())
	# Clean Signal daemon
	var cs := DaemonData.new(); cs.id = &"clean_signal"
	var ct := TriggeredEffectData.new(); ct.trigger = RC.Trigger.ON_PERFECT; ct.consecutive_required = 3
	ct.effects = [_mk_effect(RC.EffectType.MODIFY_HEAT, RC.EffectTarget.CAMPAIGN, -2)]
	cs.triggered_effects = [ct]
	print("Clean Signal errors (expect 0): ", ct.validate())
	# Bad effects
	var spin_bad := _mk_effect(RC.EffectType.SPIN, RC.EffectTarget.TARGET_WHEEL, 4)
	print("Spin on outer ring (expect 1): ", spin_bad.validate())
	if spin_bad.validate().size() != 1: fails += 1
	# Card
	var nudge := CardData.new(); nudge.id = &"nudge"
	nudge.effects = [_mk_effect(RC.EffectType.NUDGE, RC.EffectTarget.TARGET_WHEEL, 1, RC.RingScope.INNER)]
	print("Card errors (expect 0): ", nudge.validate())
	# Site
	var site := SiteData.new(); site.id = &"t2_a"; site.objective = RC.SiteObjective.HEAT_REDUCTION; site.heat_change = 5
	print("Site errors (expect 1): ", site.validate())
	# Save round trip
	var err := ResourceSaver.save(w, "user://smoke_breaker_wheel.tres")
	var loaded: WheelData = load("user://smoke_breaker_wheel.tres")
	print("Save=", err, " reload slots=", loaded.slots.size(), " slot1 fw=", loaded.slots[1].firmware.id)
	# Instantiate every schema
	for c in [NetworkNodeData, DefenseAssetData, ThreatData, InfiltrationNodeData, AdjacencyBonusData, RingSegmentData, InnerRingData]:
		c.new()
	return fails


func _slice(id, t, out, rule := RC.TargetRule.POINTER) -> SliceData:
	var s := SliceData.new(); s.id = id; s.slice_type = t; s.base_output = out; s.target_rule = rule
	return s

func _wheel(slices: Array, ptrs := PackedInt32Array([0])) -> WheelData:
	var w := WheelData.new(); w.slice_count = slices.size(); w.pointer_ticks = ptrs
	var slots: Array[WheelSlotData] = []
	for s in slices:
		var sl := WheelSlotData.new(); sl.slice = s; slots.append(sl)
	w.slots = slots
	return w

func _site(id, tier, links: Array[StringName], obj := RC.SiteObjective.NONE, ex := RC.ExploitType.NONE) -> SiteData:
	var s := SiteData.new(); s.id = id; s.tier = tier; s.links = links; s.objective = obj; s.exploit_type = ex
	return s

func _batch2() -> int:
	var fails := 0
	var atk := _slice(&"atk", RC.SliceType.SHIM, 6)
	var def := _slice(&"def", RC.SliceType.DEFRAG, 5, RC.TargetRule.SELF)
	var null_slice := _slice(&"null", RC.SliceType.NULL, 0)
	var crit := _slice(&"crit", RC.SliceType.OVERFLOW, 12)

	# Class
	var hub := HubCoreData.new(); hub.id = &"breaker_core"
	var hook := TriggeredEffectData.new(); hook.trigger = RC.Trigger.ON_PERFECT
	var re := EffectData.new(); re.type = RC.EffectType.RETRIGGER; re.target = RC.EffectTarget.SELF
	hook.effects = [re]; hub.perfect_hook = hook
	var cls := ClassData.new(); cls.id = &"breaker"
	cls.starting_wheel = _wheel([crit, atk, atk, atk, def, null_slice]); cls.starting_wheel.hub = hub
	var card := CardData.new(); card.id = &"spin"; cls.starting_deck = [card]
	var r1 := RankRewardData.new(); r1.rank = 1
	var r1b := RankRewardData.new(); r1b.rank = 1
	cls.rank_rewards = [r1, r1b]
	var ce := cls.validate(); print("Class (expect 1 dup rank): ", ce)
	if ce.size() != 1: fails += 1

	# Boss with satellites + phases (cyclic EnemyData <-> SatelliteSpawnData)
	var sat := EnemyData.new(); sat.id = &"drone"; sat.wheel = _wheel([atk, def, atk])
	var sp := SatelliteSpawnData.new(); sp.satellite = sat
	var p1 := BossPhaseData.new(); p1.hp_threshold_pct = 0.66; p1.pointer_behavior = RC.PointerBehavior.MULTIPLY; p1.pointer_ticks = PackedInt32Array([0, 15])
	var p2 := BossPhaseData.new(); p2.hp_threshold_pct = 0.33; p2.pointer_behavior = RC.PointerBehavior.ORBIT; p2.orbit_ticks_per_turn = 2
	var boss := EnemyData.new(); boss.id = &"renewal_engine"; boss.is_boss = true
	boss.wheel = _wheel([atk, atk, def, def, crit, null_slice]); boss.wheel.passive_resistance = 5; boss.spawns = [sp]; boss.phases = [p1, p2]
	var be := boss.validate(); print("Boss (expect 0): ", be)
	if be.size() != 0: fails += 1
	boss.phases = [p2, p1]
	print("Boss wrong order (expect 1): ", boss.validate())

	# Grid: home, 3 chains, T3, boss. Also a bad T1 with two T2s.
	var sites: Array[SiteData] = [
		_site(&"home", 1, [&"a1", &"b1", &"c1"]),
		_site(&"a1", 1, [&"a2"]), _site(&"a2", 2, [&"t3"], RC.SiteObjective.EXPLOIT, RC.ExploitType.INTEL),
		_site(&"b1", 1, [&"b2"]), _site(&"b2", 2, [&"t3"], RC.SiteObjective.EXPLOIT, RC.ExploitType.BREACH),
		_site(&"c1", 1, [&"c2"]), _site(&"c2", 2, [&"t3"], RC.SiteObjective.EXPLOIT, RC.ExploitType.VIRUS),
		_site(&"t3", 3, [&"boss"]), _site(&"boss", 4, [], RC.SiteObjective.CENTRAL_SERVER),
	]
	var grid := CityGridData.new(); grid.sites = sites; grid.home_site_id = &"home"; grid.boss_site_id = &"boss"
	var ge := grid.validate(); print("Grid (expect 0): ", ge, " warnings: ", grid.size_warnings())
	if ge.size() != 0: fails += 1
	sites[1].links = [&"a2", &"b2"]
	print("Grid T1 double (expect 1): ", grid.validate())
	sites[1].links = [&"a2"]
	sites[7].links = []  # cut t3 -> boss
	print("Grid unreachable (expect 1): ", grid.validate())
	sites[7].links = [&"boss"]

	# Story + corp
	var beat := StoryBeatData.new(); beat.id = &"b"
	var paths: Array[StoryPathData] = []
	for i in 5:
		var p := StoryPathData.new(); p.id = StringName("p%d" % i); p.beats = [beat, beat, beat]; p.finale = beat
		paths.append(p)
	var corp := CorporationData.new(); corp.id = &"solace"; corp.city_grid = grid; corp.final_boss = boss; corp.story_paths = paths
	boss.phases = [p1, p2]
	var coe := corp.validate(); print("Corp (expect 0): ", coe)
	if coe.size() != 0: fails += 1

	# Config
	var cfg := CampaignConfigData.new()
	var h1 := HeatThresholdData.new(); h1.heat = 25; h1.kind = RC.ThresholdKind.MAJOR; h1.id = &"heat_25"
	var h2 := HeatThresholdData.new(); h2.heat = 10; h2.id = &"heat_10"
	cfg.heat_thresholds = [h1, h2]
	print("Config wrong order (expect 1): ", cfg.validate())
	# ANIM-R4 H5: a threshold's id keys its text for translation.
	var h3 := HeatThresholdData.new(); h3.heat = 50
	cfg.heat_thresholds = [h2, h1, h3]
	print("Config threshold without id (expect 1): ", cfg.validate())
	if cfg.validate().size() != 1: fails += 1

	# Home server
	var core := NetworkNodeData.new(); core.node_type = RC.NetworkNodeType.HOME_SERVER
	var hs := HomeServerVariantData.new(); hs.id = &"std"; hs.core = core; hs.internal_nodes = [NetworkNodeData.new()]
	hs.internal_links = [Vector2i(0, 1), Vector2i(0, 5)]
	print("Home server (expect 1 bad link): ", hs.validate())

	# Save/load the whole corp graph
	var err := ResourceSaver.save(corp, "user://smoke_solace.tres")
	var loaded: CorporationData = load("user://smoke_solace.tres")
	print("Save=", err, " boss phases=", loaded.final_boss.phases.size(), " sat=", loaded.final_boss.spawns[0].satellite.id, " sites=", loaded.city_grid.sites.size())
	for c in [ExploitData, TerminalEventData, EventChoiceData, RaidData, RaidWaveData, RuleModifierData, IceLevelData, ProfileUnlockData, HeatGatedEffectData]:
		c.new()
	return fails


## M0: CampaignConfigData carries the whole of GDD Section 11 (shop, costs, RAM ranges).
func _batch3() -> int:
	var fails := 0
	var cfg := CampaignConfigData.new()
	var ce := cfg.validate(); print("Config defaults (expect 0): ", ce)
	if ce.size() != 0: fails += 1
	cfg.card_price_range = Vector2i(75, 50)
	cfg.node_upgrade_costs = PackedInt32Array()
	ce = cfg.validate(); print("Config bad range + empty upgrades (expect 2): ", ce)
	if ce.size() != 2: fails += 1
	var err := ResourceSaver.save(cfg, "user://smoke_config.tres")
	var loaded: CampaignConfigData = load("user://smoke_config.tres")
	print("Save=", err, " reload card_price_range=", loaded.card_price_range, " respin=", loaded.respin_ram_cost)
	if loaded.card_price_range != Vector2i(75, 50) or loaded.respin_ram_cost != 4: fails += 1
	return fails + _batch4()


## Vertical-slice fixes (2026-09-24): CardData.offered (Bug card), HubCoreData.drone
## (TROJAN template), RankRewardData.ring_segment_options, WheelState migrations.
func _batch4() -> int:
	var fails := 0
	var bug := CardData.new(); bug.id = &"bug"; bug.offered = false; bug.exhaust = true
	bug.effects = [_mk_effect(RC.EffectType.DRAIN_RAM, RC.EffectTarget.SELF, 1)]
	print("Bug card (expect 0 errors, offered=false): ", bug.validate(), " ", bug.offered)
	if bug.validate().size() != 0 or bug.offered: fails += 1
	var atk := _slice(&"atk", RC.SliceType.SHIM, 3)
	var def := _slice(&"def", RC.SliceType.DEFRAG, 3, RC.TargetRule.SELF)
	var drone := EnemyData.new(); drone.id = &"drone"; drone.hp = 5; drone.wheel = _wheel([atk, def])
	var hub := HubCoreData.new(); hub.id = &"botnet_core"; hub.max_drones = 3; hub.drone = drone
	var seg := RingSegmentData.new(); seg.id = &"seg_echo"
	var r3 := RankRewardData.new(); r3.rank = 3; r3.ring_segment_options = [seg]
	var err := ResourceSaver.save(hub, "user://smoke_hub.tres")
	var loaded: HubCoreData = load("user://smoke_hub.tres")
	print("Hub save=", err, " drone=", loaded.drone.id, " max=", loaded.max_drones, " rank3 options=", r3.ring_segment_options.size())
	if err != OK or loaded.drone == null or loaded.max_drones != 3: fails += 1
	var w := WheelState.from_wheel_data(drone.wheel)
	w.pending_pointer_ticks = PackedInt32Array([5, 20])
	var back := WheelState.from_dict(w.to_dict())
	print("WheelState pending pointers round trip: ", back.pending_pointer_ticks)
	if back.pending_pointer_ticks != PackedInt32Array([5, 20]): fails += 1
	if not back.apply_pending_pointers() or back.pointer_ticks != PackedInt32Array([5, 20]): fails += 1
	return fails + _batch5()


## Vertical-slice fixes batch 2: NetrunBoostData, StoryBeatData.triggers_raid, GridState
## home-variant capacity and frozen links, CampaignState boosts/objectives/home variant.
func _batch5() -> int:
	var fails := 0
	var empty := NetrunBoostData.new(); empty.id = &"nothing"
	print("Empty boost (expect 1): ", empty.validate())
	if empty.validate().size() != 1: fails += 1
	var boost := NetrunBoostData.new(); boost.id = &"cache"; boost.cost = 10; boost.cycles = 40
	var cfg := CampaignConfigData.new(); cfg.netrun_boosts = [boost]
	print("Config with a 10-Schematic boost (expect 0): ", cfg.validate())
	if cfg.validate().size() != 0: fails += 1
	boost.cost = 99
	print("Config with a 99-Schematic boost (expect 1): ", cfg.validate())
	if cfg.validate().size() != 1: fails += 1
	var beat := StoryBeatData.new(); beat.id = &"b"; beat.triggers_raid = true
	var err := ResourceSaver.save(beat, "user://smoke_beat.tres")
	var loaded: StoryBeatData = load("user://smoke_beat.tres")
	print("Beat save=", err, " triggers_raid=", loaded.triggers_raid)
	if err != OK or not loaded.triggers_raid: fails += 1
	var g := GridState.new(); g.home_site_id = &"home"; g.home_asset_slots = 3; g.home_built_in = ["turret"]
	g.freeze_link(&"home", &"c1")
	var back := GridState.from_dict(g.to_dict())
	print("GridState round trip: slots=", back.home_asset_slots, " built_in=", back.home_built_in, " frozen=", back.is_link_frozen(&"c1", &"home"))
	if back.home_asset_slots != 3 or back.home_built_in != ["turret"] or not back.is_link_frozen(&"c1", &"home"): fails += 1
	var c := CampaignState.new(); c.pending_boosts = [&"cache"]; c.disabled_objectives = [&"scrub"]; c.home_variant_id = &"home_bunker"
	var cb := CampaignState.from_dict(c.to_dict())
	print("CampaignState round trip: ", cb.pending_boosts, cb.disabled_objectives, cb.home_variant_id)
	if cb.pending_boosts != [&"cache"] or cb.disabled_objectives != [&"scrub"] or cb.home_variant_id != &"home_bunker": fails += 1
	var cfg2 := CampaignConfigData.new()
	print("Config home repair / retaliation defaults: ", cfg2.home_repair_cost_per_point, " ", cfg2.retaliation_min_heat)
	if cfg2.home_repair_cost_per_point != 1.0 or cfg2.retaliation_min_heat != 50: fails += 1
	print("Config damage table default: ", cfg2.enemy_damage_by_tier)
	if cfg2.enemy_damage_by_tier != PackedFloat64Array([1.0, 1.3, 1.69, 2.2]): fails += 1
	# N2: tier tables, bands and the EnemyData HP table fields.
	print("Config N2 tables: ", cfg2.reference_dpt_by_tier, " ", cfg2.target_turns_per_phase, " ", cfg2.hp_band_normal)
	if cfg2.reference_dpt_by_tier != PackedInt32Array([9, 11, 14, 18]) or cfg2.target_turns_per_phase != 3.5: fails += 1
	if cfg2.hp_band(&"normal", 3) != Vector2i(44, 56) or cfg2.enemy_damage_factor(9) != 2.2: fails += 1
	var en := EnemyData.new()
	print("EnemyData N2 defaults: ", en.hp_by_tier, " ", en.hp_bands, " uses table: ", en.uses_hp_table())
	if not en.hp_by_tier.is_empty() or not en.hp_bands.is_empty() or en.uses_hp_table(): fails += 1
	return fails + _m6()


## M6 class roster: HubCoreData drones_persist / max_ram_bonus / free_resistance_nudges,
## Status.PARASITE, config parasite_output_down_stacks (N8, was parasite_multiplier) / station_deploy_asset, RunState.drones and
## WheelState.respin_skipped (freeze cooldown).
func _m6() -> int:
	var fails := 0
	var hub := HubCoreData.new(); hub.id = &"rig"; hub.drones_persist = true; hub.max_ram_bonus = 1; hub.free_resistance_nudges = 2
	var err := ResourceSaver.save(hub, "user://smoke_hub_m6.tres")
	var loaded: HubCoreData = load("user://smoke_hub_m6.tres")
	print("M6 hub save=", err, " persist=", loaded.drones_persist, " ram=", loaded.max_ram_bonus, " nudges=", loaded.free_resistance_nudges)
	if err != OK or not loaded.drones_persist or loaded.max_ram_bonus != 1 or loaded.free_resistance_nudges != 2: fails += 1
	print("Status.PARASITE = ", RC.Status.PARASITE)
	if RC.Status.PARASITE != 4: fails += 1
	var cfg := CampaignConfigData.new()
	print("Config parasite OUTPUT_DOWN stacks default (N8): ", cfg.parasite_output_down_stacks, " station asset: ", cfg.station_deploy_asset)
	if cfg.parasite_output_down_stacks != 2 or cfg.station_deploy_asset != null: fails += 1
	var r := RunState.new(); r.drones = [{"source_id": "botnet_drone", "hp": 4, "dock_slot": 1}]
	var rb := RunState.from_dict(r.to_dict())
	print("RunState drones round trip: ", rb.drones)
	if rb.drones.size() != 1 or int(rb.drones[0]["hp"]) != 4: fails += 1
	var w := WheelState.new(); w.respin_skipped = true
	var wb := WheelState.from_dict(w.to_dict())
	print("WheelState respin_skipped round trip: ", wb.respin_skipped)
	if not wb.respin_skipped: fails += 1
	return fails + _m8()


## M8 corporations: RaidData.corporation_id / replaces (a corporation's raid standing in
## for a shared Heat-threshold raid).
func _m8() -> int:
	var fails := 0
	var raid := RaidData.new(); raid.id = &"raid_x"; raid.corporation_id = &"meridian"; raid.replaces = &"raid_heat_25"
	var err := ResourceSaver.save(raid, "user://smoke_raid_m8.tres")
	var loaded: RaidData = load("user://smoke_raid_m8.tres")
	print("M8 raid save=", err, " corp=", loaded.corporation_id, " replaces=", loaded.replaces)
	if err != OK or loaded.corporation_id != &"meridian" or loaded.replaces != &"raid_heat_25": fails += 1
	var plain := RaidData.new()
	print("Raid defaults: corp='", plain.corporation_id, "' replaces='", plain.replaces, "'")
	if plain.corporation_id != &"" or plain.replaces != &"": fails += 1
	return fails + _m11()


## M11 REBEL_CELL: CampaignState.generated (usage snapshot) and ProfileState usage stats.
func _m11() -> int:
	var fails := 0
	var c := CampaignState.new(); c.generated = {"classes": ["ghost"], "daemons": [], "nodes": ["relay"], "assets": ["turret"]}
	var back := CampaignState.from_dict(c.to_dict())
	print("CampaignState.generated round trip: ", back.generated)
	if back.generated.get("classes", []) != ["ghost"]: fails += 1
	var p := ProfileState.new(); p.record_usage("class", &"rigger", 3)
	var pb := ProfileState.from_dict(p.to_dict())
	print("Profile usage round trip: ", pb.top_used("class", 1))
	if pb.top_used("class", 1) != [&"rigger"]: fails += 1
	return fails + _m12()


## M12: config assist_free_nudges / assist_hp_multiplier, CampaignState.assist.
func _m12() -> int:
	var fails := 0
	var cfg := CampaignConfigData.new()
	print("Config assist defaults: ", cfg.assist_free_nudges, " ", cfg.assist_hp_multiplier)
	if cfg.assist_free_nudges != 1 or cfg.assist_hp_multiplier != 1.25: fails += 1
	var c := CampaignState.new(); c.enable_assist(1, 1.25)
	var back := CampaignState.from_dict(c.to_dict())
	print("CampaignState.assist round trip: ", back.assist)
	if not back.is_assisted(): fails += 1
	return fails + _h2()


## Horizontal pass 2: config mirror_* / final_final_ice / major_heat_levels(),
## CampaignState.start_class_id.
func _h2() -> int:
	var fails := 0
	var cfg := CampaignConfigData.new()
	print("Config mirror defaults: ", cfg.mirror_output_factor, " ", cfg.mirror_threat_integrity, " ", cfg.mirror_threat_damage_bonus, " final ", cfg.final_final_ice)
	if cfg.mirror_output_factor != 1.5 or cfg.mirror_threat_integrity != 1.5 or cfg.mirror_threat_damage_bonus != 2 or cfg.final_final_ice != 20: fails += 1
	var loaded: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("Major Heat levels: ", loaded.major_heat_levels())
	if loaded.major_heat_levels().is_empty(): fails += 1
	print("Mirror extras: ", cfg.mirror_resistance, " ", cfg.mirror_trojan_base, " ", cfg.mirror_threat_min_integrity, " ", cfg.mirror_threat_min_damage, " ", cfg.mirror_decoy_speed)
	if cfg.mirror_resistance != 1 or cfg.mirror_trojan_base != 6 or cfg.mirror_threat_min_integrity != 10 or cfg.mirror_threat_min_damage != 4 or cfg.mirror_decoy_speed != 2: fails += 1
	var c := CampaignState.new(); c.start_class_id = &"rigger"
	if CampaignState.from_dict(c.to_dict()).start_class_id != &"rigger": fails += 1
	return fails + _h11()


## Horizontal pass 11: config ICE caps, Mainframe stock, emergency rookie, max_ice_level().
func _h11() -> int:
	var fails := 0
	var cfg := CampaignConfigData.new()
	print("H11 config: ICE ", cfg.ice_base_cap, " +", cfg.ice_unlock_step, " shop ", cfg.shop_card_stock, "/", cfg.shop_firmware_stock, "/", cfg.shop_daemon_stock, " rookie ", cfg.emergency_rookie_cost)
	if cfg.ice_base_cap != 3 or cfg.ice_unlock_step != 3 or cfg.shop_card_stock != 3 or cfg.shop_firmware_stock != 2 or cfg.shop_daemon_stock != 1 or cfg.emergency_rookie_cost != 0: fails += 1
	var loaded: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("Top ICE level: ", loaded.max_ice_level())
	if loaded.max_ice_level() != 20: fails += 1
	return fails + _h12()


## Horizontal pass 12: DaemonData.amount, config raid pacing and drift stages,
## RunState.racks_captured / patrol.
func _h12() -> int:
	var fails := 0
	var d := DaemonData.new()
	var cfg := CampaignConfigData.new()
	print("H12: daemon amount ", d.amount, " raid ", cfg.raid_wave_interval, "/", cfg.raid_heat_scaling_step, " drift ", cfg.dispatch_drift_mid, "/", cfg.dispatch_drift_late)
	if d.amount != 0 or cfg.raid_wave_interval != 5 or cfg.raid_heat_scaling_step != 10 or cfg.dispatch_drift_mid != 3 or cfg.dispatch_drift_late != 6: fails += 1
	var cold: DaemonData = load("res://content/daemons/cold_exit.tres")
	if cold.amount != 3: fails += 1
	var r := RunState.new()
	r.racks_captured = 2
	r.patrol = true
	var back := RunState.from_dict(r.to_dict())
	if back.racks_captured != 2 or not back.patrol: fails += 1
	return fails + _h14()


## Horizontal pass 14: HeatGatedEffectData.offensive_slices_only, achievement thresholds.
func _h14() -> int:
	var fails := 0
	var hg := HeatGatedEffectData.new()
	var cfg := CampaignConfigData.new()
	print("H14: offensive_slices_only ", hg.offensive_slices_only, " achievements ", cfg.achievement_racks, "/", cfg.achievement_raids, "/", cfg.achievement_perfects)
	if hg.offensive_slices_only or cfg.achievement_racks != 10 or cfg.achievement_raids != 20 or cfg.achievement_perfects != 500: fails += 1
	var officer: EnemyData = load("res://content/enemies/compliance_officer.tres")
	if not officer.heat_effects[0].offensive_slices_only: fails += 1
	print("H15: achievement ICE ", cfg.achievement_ice_low, "/", cfg.achievement_ice_high)
	if cfg.achievement_ice_low != 5 or cfg.achievement_ice_high != 10: fails += 1
	return fails + _anim1()


## Animation pass ANIM-1: UiMotionData / UiMotionEntryData (the UI motion table) round-trip, and
## content/config/ui_motion.tres carries every required id.
func _anim1() -> int:
	var fails := 0
	var e := UiMotionEntryData.new()
	print("ANIM-1: entry defaults ", e.duration, "/", e.delay, "/", e.ease, "/", e.trans, "/", e.amplitude, "/", e.enabled, " errors ", e.validate())
	if e.validate().size() != 1 or not e.enabled: fails += 1  # no id
	e.id = &"smoke_pop"
	e.duration = 0.3
	e.ease = Tween.EASE_IN_OUT
	e.trans = Tween.TRANS_BACK
	e.amplitude = 1.2
	var table := UiMotionData.new()
	table.entries = [e]
	if table.validate().size() != 0 or e.validate().size() != 0: fails += 1
	var err := ResourceSaver.save(table, "user://smoke_motion.tres")
	var back: UiMotionData = load("user://smoke_motion.tres")
	var be := back.find(&"smoke_pop")
	print("Save=", err, " reload ", be.duration if be != null else -1.0, " ease ", be.ease if be != null else -1, " trans ", be.trans if be != null else -1)
	if be == null or be.ease != Tween.EASE_IN_OUT or be.trans != Tween.TRANS_BACK or not is_equal_approx(be.amplitude, 1.2): fails += 1
	table.entries = [e, e]
	if table.validate().size() != 1: fails += 1  # repeated id
	# ANIM-R5: a tuning of another entry (UiMotionData.ALWAYS_ON) is refused switched off.
	var tuning := UiMotionEntryData.new()
	tuning.id = UiMotionData.ALWAYS_ON[0]
	tuning.enabled = false
	table.entries = [tuning]
	print("ANIM-R5: ", tuning.id, " off -> ", table.validate())
	if table.validate().size() != 1: fails += 1
	var shipped: UiMotionData = load("res://content/config/ui_motion.tres")
	var missing := 0
	for id in UiMotionData.REQUIRED_IDS:
		if shipped == null or shipped.find(id) == null:
			missing += 1
	print("ANIM-1: ui_motion.tres entries ", shipped.entries.size() if shipped != null else -1, " missing ", missing)
	if shipped == null or missing != 0 or shipped.validate().size() != 0: fails += 1
	fails += _art0_tier(shipped)
	return fails + _art0()


## ART-0 E (ported from art-pass W6): every motion entry carries a VFX tier (T0..T4, default
## T1) that round-trips; an out-of-range tier is an error; every shipped entry names a valid one.
func _art0_tier(shipped: UiMotionData) -> int:
	var fails := 0
	var te := UiMotionEntryData.new()
	te.id = &"smoke_tier"
	var tier_default := te.tier
	te.tier = UiMotionEntryData.Tier.T3_MOMENT
	var tier_table := UiMotionData.new()
	tier_table.entries = [te]
	var tier_err := ResourceSaver.save(tier_table, "user://smoke_motion_tier.tres")
	var tier_back: UiMotionData = load("user://smoke_motion_tier.tres")
	var tb := tier_back.find(&"smoke_tier") if tier_back != null else null
	print("ART-0 E: tier default ", tier_default, " save=", tier_err, " reload ", tb.tier if tb != null else -1)
	if tier_default != UiMotionEntryData.Tier.T1_FEEDBACK or tb == null or tb.tier != UiMotionEntryData.Tier.T3_MOMENT: fails += 1
	te.set("tier", 7)
	if te.validate().size() != 1: fails += 1  # tier out of range
	# ART-0 audit E2: an entry's kind (ONE_SHOT default, HOLD, LOOP) round-trips; out of range is an error.
	var ke := UiMotionEntryData.new()
	ke.id = &"smoke_kind"
	var kind_default := ke.kind
	ke.kind = UiMotionEntryData.Kind.HOLD
	var kind_table := UiMotionData.new()
	kind_table.entries = [ke]
	var kind_err := ResourceSaver.save(kind_table, "user://smoke_motion_kind.tres")
	var kind_back: UiMotionData = load("user://smoke_motion_kind.tres")
	var kb := kind_back.find(&"smoke_kind") if kind_back != null else null
	print("ART-0 audit E2: kind default ", kind_default, " save=", kind_err, " reload ", kb.kind if kb != null else -1, " kinds ", UiMotionEntryData.Kind.keys())
	if kind_default != UiMotionEntryData.Kind.ONE_SHOT or kb == null or kb.kind != UiMotionEntryData.Kind.HOLD: fails += 1
	ke.set("kind", 5)
	if ke.validate().size() != 1: fails += 1  # kind out of range
	var bad_tier := 0
	if shipped != null:
		for se in shipped.entries:
			if se == null or se.validate().size() != 0:
				bad_tier += 1
	print("ART-0 E: ui_motion.tres entries with a bad tier ", bad_tier)
	if bad_tier != 0: fails += 1
	return fails


## ART-0 names pass (ruling 6.5): the shop node is the Mainframe, in the config field
## (CampaignConfigData.map_mainframe_layers) and the node-type enum; the old field is gone.
func _art0() -> int:
	var fails := 0
	var cfg := CampaignConfigData.new()
	var shipped: CampaignConfigData = load("res://content/config/campaign_config.tres")
	var names := {}
	for p in cfg.get_property_list():
		names[String(p["name"])] = true
	print("ART-0: map_mainframe_layers ", cfg.map_mainframe_layers, " shipped ", shipped.map_mainframe_layers if shipped != null else Vector2i(-1, -1),
		" MAINFRAME ", RC.InfilNodeType.MAINFRAME)
	if not names.has("map_mainframe_layers") or names.has("map_" + "mo" + "dem_layers"): fails += 1
	if shipped == null or shipped.map_mainframe_layers != Vector2i(3, 5): fails += 1
	if RC.InfilNodeType.keys().has("MO" + "DEM"): fails += 1
	# ART-0 D8: the precision tier is WEAK (was Partial); its multiplier follows.
	print("ART-0 D8: weak_multiplier ", cfg.weak_multiplier, " shipped ", shipped.weak_multiplier if shipped != null else -1.0, " tiers ", RC.PrecisionTier.keys())
	if not names.has("weak_multiplier") or names.has("par" + "tial_multiplier") or not is_equal_approx(cfg.weak_multiplier, 0.5): fails += 1
	if shipped == null or not is_equal_approx(shipped.weak_multiplier, 0.5) or RC.PrecisionTier.keys() != ["WEAK", "GOOD", "PERFECT"]: fails += 1
	# ART-0 S0: the save locations and the replay switch (CampaignConfigData).
	print("ART-0 S0: saves ", cfg.save_dir_source, " / ", cfg.save_dir_export, " replays ", cfg.replay_subdir, " on ", cfg.write_replays)
	if cfg.save_dir_source != "res://saves" or cfg.save_dir_export != "user://saves" or cfg.replay_subdir != "replays" or not cfg.write_replays: fails += 1
	if shipped == null or shipped.save_dir_source != cfg.save_dir_source or shipped.save_dir_export != cfg.save_dir_export or shipped.replay_subdir != cfg.replay_subdir or shipped.write_replays != cfg.write_replays: fails += 1
	# ART-0 audit B4: the replay folder's cap (0 = none; negative is an error).
	print("ART-0 audit B4: max_replays ", cfg.max_replays, " shipped ", shipped.max_replays if shipped != null else -1)
	if not names.has("max_replays") or cfg.max_replays != 50 or shipped == null or shipped.max_replays != 50: fails += 1
	var neg := CampaignConfigData.new()
	neg.max_replays = -1
	if neg.validate().is_empty(): fails += 1
	# ART-0 B3: the slice programs SANDBOX / TROJAN / NULL; the config fields follow the words.
	print("ART-0 B3: null_slice_overwrite_price ", cfg.null_slice_overwrite_price, " shipped ", shipped.null_slice_overwrite_price if shipped != null else -1,
		" mirror_trojan_base ", cfg.mirror_trojan_base, " slices ", RC.SliceType.keys())
	if not names.has("null_slice_overwrite_price") or names.has("mi" + "ss_slice_overwrite_price") or cfg.null_slice_overwrite_price != 150: fails += 1
	if not names.has("mirror_trojan_base") or names.has("mirror_" + "deploy_base") or cfg.mirror_trojan_base != 6: fails += 1
	if shipped == null or shipped.null_slice_overwrite_price != 150: fails += 1
	if RC.SliceType.keys() != ["SHIM", "OVERFLOW", "DEFRAG", "DETOUR", "SANDBOX", "TROJAN", "HOTFIX", "INFECT", "NULL"]: fails += 1
	# ART-0 B3: five Heat bands on the existing thresholds (MAJOR 25 / 50 / 75 and PURGE 100).
	print("ART-0 B3: heat_band_levels ", shipped.heat_band_levels() if shipped != null else [])
	if shipped == null or shipped.heat_band_levels() != ([25, 50, 75, 100] as Array[int]): fails += 1
	return fails + _art2c()


## ART-2 2C: CampaignConfigData's Combat FX group (shard severity, the Heat city's counts).
func _art2c() -> int:
	var fails := 0
	var cfg := CampaignConfigData.new()
	var shipped: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("ART-2 2C: shards ", cfg.fx_shard_base, " +", cfg.fx_shard_per_dmg, " max ", cfg.fx_shard_max, " glyph ", cfg.fx_glyph_px_base, " +", cfg.fx_glyph_px_per_dmg,
		" max ", cfg.fx_glyph_px_max, " heat city ", cfg.heat_city_side_beacons, cfg.heat_city_police_lights)
	if cfg.fx_shard_count(7) != 18 or cfg.fx_shard_count(0, true) != 40 or not is_equal_approx(cfg.fx_glyph_px(100), 38.0): fails += 1
	if cfg.heat_city_police_lights.size() != 5 or cfg.heat_city_police_lights[3] != 13 or cfg.heat_city_side_beacons[1] != 3: fails += 1
	if shipped == null or not shipped.validate().is_empty(): fails += 1
	var bad := CampaignConfigData.new()
	bad.heat_city_side_beacons = PackedInt32Array([1, 2])
	if bad.validate().is_empty(): fails += 1
	# ART-0 audit B1: the Heat glitch's per-band table (period, burst, tears, blocks).
	print("ART-0 audit B1: heat_glitch period ", cfg.heat_glitch_period, " burst ", cfg.heat_glitch_burst, " tears ", cfg.heat_glitch_tears, " blocks ", cfg.heat_glitch_blocks)
	if cfg.heat_glitch_period.size() != 5 or cfg.heat_glitch_burst.size() != 5 or cfg.heat_glitch_tears[3] != 18 or cfg.heat_glitch_blocks[2] != 48: fails += 1
	if shipped == null or shipped.heat_glitch_period.size() != 5: fails += 1
	var bad_glitch := CampaignConfigData.new()
	bad_glitch.heat_glitch_burst = PackedFloat32Array([0.08, 0.16, 0.26, 2.0, 0.32])
	if bad_glitch.validate().is_empty(): fails += 1
	return fails


## ART-1 1C: GlyphTableData (the glyph atlas and its id -> glyph table): an empty table reports
## its missing atlas and stand-in; the shipped one validates; a save keeps the ids and geometry.
func _art1_glyphs() -> int:
	var fails := 0
	var empty := GlyphTableData.new()
	var ee := empty.validate()
	print("ART-1 1C: empty glyph table errors (expect 2: no atlas, no stand-in): ", ee)
	if ee.size() != 2: fails += 1
	var shipped := GlyphTableData.shipped()
	var se := shipped.validate() if shipped != null else PackedStringArray(["missing"])
	print("ART-1 1C: shipped glyph table errors (expect 0): ", se, " glyphs ", shipped.glyph_names.size() if shipped != null else -1,
		" ids ", shipped.ids.size() if shipped != null else -1)
	if se.size() != 0: fails += 1
	if shipped == null or shipped.glyph_for(GlyphTableData.key_for_slice_type(RC.SliceType.SHIM)) != &"slice_shim": fails += 1
	var t := GlyphTableData.new()
	t.glyph_names = PackedStringArray(["slice_shim", "pending"])
	t.ids = {&"type_shim": &"slice_shim", &"effect_custom": &"pending"}
	t.box_px = 90
	var err := ResourceSaver.save(t, "user://smoke_glyph_table.tres")
	var back: GlyphTableData = load("user://smoke_glyph_table.tres")
	print("ART-1 1C: glyph table save=", err, " ids ", back.ids if back != null else {}, " box ", back.box_px if back != null else -1)
	if err != OK or back == null or back.glyph_for(&"type_shim") != &"slice_shim" or not back.is_pending(&"effect_custom") or back.box_px != 90: fails += 1
	if back == null or back.cell_region(&"pending") != Rect2(128, 0, 128, 128): fails += 1
	return fails


## ART-5 5c: CityMotionConfigData (the city's motion layers' counts, sizes and colours): the
## shipped one validates; a short palette, a short band array and an inverted LOD are each
## refused; a save keeps its values.
func _art5_city_motion() -> int:
	var fails := 0
	var shipped := CityMotionConfigData.shipped()
	var se := shipped.validate() if shipped != null else PackedStringArray(["missing"])
	print("ART-5 5c: shipped city motion config errors (expect 0): ", se)
	if se.size() != 0: fails += 1
	var bad := CityMotionConfigData.new()
	bad.lane_colors = [Color.RED]
	bad.band_drones = [0, 1]
	bad.car_close_below = 500.0
	var be := bad.validate()
	print("ART-5 5c: bad city motion config errors (expect 3): ", be)
	if be.size() != 3: fails += 1
	var t := CityMotionConfigData.new()
	t.car_gap = 21.0
	t.band_police = [0, 1, 2, 3]
	var err := ResourceSaver.save(t, "user://smoke_city_motion.tres")
	var back: CityMotionConfigData = load("user://smoke_city_motion.tres")
	print("ART-5 5c: city motion config save=", err, " gap ", back.car_gap if back != null else -1.0)
	if err != OK or back == null or back.car_gap != 21.0 or back.band_police != [0, 1, 2, 3] or back.validate().size() != 0: fails += 1
	# ART-5 5e: reduce_motion_street_rate (bible 5.4: 40 %) validated in [0, 1] and saved.
	var rm := CityMotionConfigData.new()
	rm.reduce_motion_street_rate = 1.5
	var rme := rm.validate()
	print("ART-5 5e: reduce_motion_street_rate 1.5 errors (expect 1): ", rme, " shipped ", shipped.reduce_motion_street_rate if shipped != null else -1.0)
	if rme.size() != 1 or shipped == null or not is_equal_approx(shipped.reduce_motion_street_rate, 0.4): fails += 1
	rm.reduce_motion_street_rate = 0.25
	var rerr := ResourceSaver.save(rm, "user://smoke_city_motion_rm.tres")
	var rback: CityMotionConfigData = load("user://smoke_city_motion_rm.tres")
	if rerr != OK or rback == null or not is_equal_approx(rback.reduce_motion_street_rate, 0.25): fails += 1
	# ART-5 5e: day_bloom / day_glow_threshold (the day look's post bloom) validated and saved.
	var db := CityMotionConfigData.new()
	db.day_glow_threshold = 1.5
	var dbe := db.validate()
	print("ART-5 5e: day_glow_threshold 1.5 errors (expect 1): ", dbe)
	if dbe.size() != 1: fails += 1
	db.day_glow_threshold = 0.8
	db.day_bloom = 0.3
	var derr := ResourceSaver.save(db, "user://smoke_city_motion_day.tres")
	var dback: CityMotionConfigData = load("user://smoke_city_motion_day.tres")
	if derr != OK or dback == null or not is_equal_approx(dback.day_bloom, 0.3) or not is_equal_approx(dback.day_glow_threshold, 0.8): fails += 1
	return fails


## ART-8 8p: HqCompoundLayoutData (the HQ-run node -> compound position table): an empty one
## reports its three gaps; every shipped one validates with one row per layer before the
## final one; a save keeps the slots, the Central Server and the entry.
func _art8_hq_compound() -> int:
	var fails := 0
	var empty := HqCompoundLayoutData.new()
	var ee := empty.validate()
	print("ART-8 8p: empty HQ compound layout errors (expect 3: corporation, asset_dir, slots): ", ee)
	if ee.size() != 3: fails += 1
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	for corp in [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]:
		var l := load("res://content/city/hq_compounds/%s.tres" % corp) as HqCompoundLayoutData
		var le := l.validate() if l != null else PackedStringArray(["missing"])
		print("ART-8 8p: %s layout errors %s rows %d slots %d" % [corp, le, l.layer_rows() if l != null else -1, l.slots_per_layer if l != null else -1])
		if le.size() != 0 or l.id != HqCompoundLayoutData.id_for(corp): fails += 1
		if l == null or l.layer_rows() != cfg.map_layers - 1 or l.slots_per_layer != cfg.map_nodes_max: fails += 1
	var t := HqCompoundLayoutData.new()
	t.corporation_id = &"smoke"
	t.id = HqCompoundLayoutData.id_for(&"smoke")
	t.asset_dir = "res://assets/city/hq_compounds/smoke"
	t.slots_per_layer = 2
	t.layer_slots = PackedVector3Array([Vector3(1, 2, 3), Vector3(4, 5, 6), Vector3(7, 8, 9), Vector3(10, 11, 12)])
	t.central_server = Vector3(0, 30, 0)
	t.entry = Vector3(40, 0, 0)
	var err := ResourceSaver.save(t, "user://smoke_hq_compound.tres")
	var back: HqCompoundLayoutData = load("user://smoke_hq_compound.tres")
	print("ART-8 8p: layout save=", err, " rows ", back.layer_rows() if back != null else -1, " L2S1 ", back.slot_position(2, 1) if back != null else Vector3.ZERO)
	if err != OK or back == null or back.validate().size() != 0 or back.layer_rows() != 2 or back.slot_position(2, 1) != Vector3(10, 11, 12): fails += 1
	if back == null or back.central_server != Vector3(0, 30, 0) or back.entry != Vector3(40, 0, 0): fails += 1
	return fails


## P2-P4 step 1: StreetR2ConfigData (the street look rules' numbers): the shipped one validates, the plate's constants are intact
## (art seed 1, 4 kits, the kinds in weight order), an empty one reports its gaps, a missing kit row and a save round trip are caught.
func _p2_street_r2_config() -> int:
	var fails := 0
	var cfg: StreetR2ConfigData = load(StreetR2ConfigData.CONFIG_PATH)
	var errs := cfg.validate() if cfg != null else PackedStringArray(["missing"])
	print("P2 shipped street r2 config errors (expect 0): ", errs)
	if errs.size() != 0 or cfg == null: return fails + 1
	print("P2 plate constants (expect 1, 4, [ac, pipe, awning, small_sign, lit_room]): ", cfg.seeds["s1"], " ", (cfg.materials_mix["kits"] as Array).size(), " ", cfg.props_facade["kinds"].keys())
	if int(cfg.seeds["s1"]) != 1 or (cfg.materials_mix["kits"] as Array).size() != 4: fails += 1
	if (cfg.props_facade["kinds"] as Dictionary).keys() != ["ac", "pipe", "awning", "small_sign", "lit_room"]: fails += 1
	if StreetR2ConfigData.new().validate().size() <= 20: fails += 1
	var bad: StreetR2ConfigData = cfg.duplicate(true)
	(bad.kits["kit_w"] as Dictionary).erase("lit_atrium")
	if not ",".join(bad.validate()).contains("kits.kit_w.lit_atrium"): fails += 1
	var t := StreetR2ConfigData.new()
	t.subs = ["A", "B"]
	var err := ResourceSaver.save(t, "user://smoke_street_r2.tres")
	var back: StreetR2ConfigData = load("user://smoke_street_r2.tres")
	if err != OK or back == null or back.subs != ["A", "B"]: fails += 1
	return fails



## P2 step 2: the street r2 renderer config ships every key its builder reads, and validation catches a missing material.
func _p2_street_r2_render_config() -> int:
	var fails := 0
	var cfg: StreetR2RenderConfigData = load(StreetR2RenderConfigData.CONFIG_PATH)
	var errs := cfg.validate() if cfg != null else PackedStringArray(["missing"])
	print("P2 street r2 render config errors (expect 0): ", errs)
	if errs.size() != 0: return fails + 1
	var bad: StreetR2RenderConfigData = cfg.duplicate(true)
	(bad.materials as Dictionary).erase("neon")
	if not ",".join(bad.validate()).contains("materials.neon"): fails += 1
	var no_car: StreetR2RenderConfigData = cfg.duplicate(true)
	(no_car.lamps as Dictionary).erase("car_tail_emit")
	if not ",".join(no_car.validate()).contains("car_tail_emit"): fails += 1
	return fails


## Plan 2 EV-01: the event schema extension (rule 8). Every new field has its default (an old event
## loads unchanged), the authored wheels fill 30 ticks, a bad wheel / mod / fight / edit is reported,
## and a save round trip keeps an event wheel, a map edit and a fight.
func _ev01_event_schema() -> int:
	var fails := 0
	var old := EventChoiceData.new()
	old.label = "x"
	if old.starts_combat != null or old.next_combat_overrides != null or old.next_raid_overrides != null or old.event_wheel != null \
			or not old.map_edits.is_empty() or old.common_firmware or not old.validate().is_empty():
		fails += 1
	var ev := TerminalEventData.new()
	if ev.venue != TerminalEventData.Venue.TERMINAL: fails += 1
	var a := EventWheelSliceData.new(); a.label = "a"; a.size_ticks = 12
	var b := EventWheelSliceData.new(); b.label = "b"; b.size_ticks = 12
	var wheel := EventWheelData.new(); wheel.slices = [a, b]
	print("EV-01 wheel of 24 ticks (expect 1): ", wheel.validate())
	if wheel.validate().size() != 1: fails += 1
	b.size_ticks = 18
	if not wheel.validate().is_empty(): fails += 1
	print("EV-01 empty mods / raid mods / fight / link to the next layer (expect 1 each): ", EventCombatModsData.new().validate().size(), " ",
		EventRaidModsData.new().validate().size(), " ", EventFightData.new().validate().size(), " ", MapEditData.new().validate().size())
	if EventCombatModsData.new().validate().size() != 1 or EventRaidModsData.new().validate().size() != 1 \
			or EventFightData.new().validate().size() != 1 or MapEditData.new().validate().size() != 1: fails += 1
	var fight := EventFightData.new(); fight.enemy_id = &"collections_agent"; fight.stake_min_hp_pct = 40; fight.win_cycles = 35
	var edit := MapEditData.new(); edit.op = MapEditData.Op.CLOSE_NODE
	var choice := EventChoiceData.new(); choice.label = "go"; choice.event_wheel = wheel; choice.map_edits = [edit]
	var out := TerminalEventData.new(); out.id = &"smoke_ev01"; out.venue = TerminalEventData.Venue.RAID_WIN; out.choices = [choice]
	var err := ResourceSaver.save(out, "user://smoke_ev01.tres")
	var back: TerminalEventData = load("user://smoke_ev01.tres")
	print("EV-01 save=", err, " venue=", back.venue if back != null else -1)
	if err != OK or back == null or back.venue != TerminalEventData.Venue.RAID_WIN: return fails + 1
	var bc := back.choices[0]
	if bc.event_wheel == null or bc.event_wheel.slices.size() != 2 or bc.event_wheel.slices[1].size_ticks != 18: fails += 1
	if bc.map_edits.size() != 1 or bc.map_edits[0].op != MapEditData.Op.CLOSE_NODE: fails += 1
	var fc := EventChoiceData.new(); fc.label = "fight"; fc.starts_combat = fight
	if not fc.validate().is_empty(): fails += 1
	# EV-02 hosts: win_daemon defaults off and counts as a payload; the host keys ship (RAID_WIN on every win, HQ every 3rd run).
	var dfight := EventFightData.new(); dfight.enemy_id = &"tariff_collector"; dfight.stake_min_hp_pct = 50
	var no_payload := dfight.validate().size()
	dfight.win_daemon = true
	var shipped_cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("EV-02 hosts (expect 1 0 true 3 -1): ", no_payload, " ", dfight.validate().size(), " ", shipped_cfg.raid_win_event_enabled, " ", shipped_cfg.hq_event_every_runs, " ", CampaignState.new().venue_event_due)
	if EventFightData.new().win_daemon or no_payload != 1 or not dfight.validate().is_empty(): fails += 1
	if not shipped_cfg.raid_win_event_enabled or shipped_cfg.hq_event_every_runs != 3 or CampaignState.new().venue_event_due != -1: fails += 1
	if CampaignState.new().to_dict().has("venue_event_due") or CampaignState.new().to_dict().has("carried_combat_mods") or RunState.new().to_dict().has("purse_cycles"): fails += 1
	return fails


## RAID-RULES E (D27): a clean defense gains `clean_defense_heat` (default 5, shipped 5); the old lost-raid Heat and
## `raid_amber_home_loss_pct` are retired (damage gains no Heat; any Home loss is amber).
func _raid_fix_a_config() -> int:
	var cfg: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("RAID-RULES E clean defense Heat (expect 5): ", cfg.clean_defense_heat)
	return 0 if cfg.clean_defense_heat == CampaignConfigData.new().clean_defense_heat and cfg.clean_defense_heat > 0 else 1


## Solace tide (Phase 2a, SOLACE_RAID_SPEC section 7): the shipped keys equal the defaults, the config validates, and the
## HOME damage table equals its derivation from the raid content: the threat damage of raid_claim, raid_heat_25 / 50 / 75
## and raid_purge as if every threat reached HOME, plus the HUNTED band's raid strength from the 75 raid on.
func _solace_tide_config() -> int:
	var fails := 0
	var d := CampaignConfigData.new()
	var shipped: CampaignConfigData = load("res://content/config/campaign_config.tres")
	print("Solace tide defaults (expect 5 3 4 2 true 1 true 10): ", d.solace_tide_route_max_links, " ", d.solace_tide_candidates,
		" ", d.solace_tide_hand_base, " ", d.solace_tide_raid_every, " ", d.solace_tide_home_hit_infects,
		" ", d.solace_tide_breach_retries, " ", d.solace_tide_divert, " ", d.solace_tide_clean_price)
	if d.solace_tide_route_max_links != 5 or d.solace_tide_candidates != 3 or d.solace_tide_hand_base != 4 or d.solace_tide_raid_every != 2: fails += 1  # H7 cadence
	if not d.solace_tide_home_hit_infects or d.solace_tide_breach_retries != 1 or not d.solace_tide_divert or d.solace_tide_clean_price != 10: fails += 1
	if d.solace_tide_boss_hp_pct_per_infected != 25 or shipped == null or shipped.solace_tide_boss_hp_pct_per_infected != 25: fails += 1  # R-F, calibrated in Phase 2b
	if d.solace_tide_story_band != 2 or d.solace_tide_retaliation_band != 0 or shipped == null or shipped.solace_tide_story_band != 2: fails += 1  # designer ruling 2026-10-25
	print("Solace tide H6 (expect true true / true true): ", d.solace_tide_city_lost_at_raid_end, " ", d.solace_tide_known_target,
		" / ", shipped.solace_tide_city_lost_at_raid_end if shipped != null else null, " ", shipped.solace_tide_known_target if shipped != null else null)
	if not d.solace_tide_city_lost_at_raid_end or not d.solace_tide_known_target or shipped == null \
			or not shipped.solace_tide_city_lost_at_raid_end or not shipped.solace_tide_known_target: fails += 1  # R-I, R-J (designer 2026-10-26)
	print("Solace tide H7 (expect true 0 0 firewall_relay true / true 2): ", d.solace_tide_retake_taken, " ", d.solace_tide_retake_heat,
		" ", d.solace_tide_retake_schematics, " ", d.solace_tide_retake_node, " ", d.solace_tide_sentry_shields,
		" / ", shipped.solace_tide_sentry_shields if shipped != null else null, " ", shipped.solace_tide_raid_every if shipped != null else null)
	if not d.solace_tide_retake_taken or d.solace_tide_retake_heat != 0 or d.solace_tide_retake_schematics != 0 \
			or d.solace_tide_retake_node != &"firewall_relay" or not d.solace_tide_sentry_shields or shipped == null \
			or not shipped.solace_tide_retake_taken or not shipped.solace_tide_sentry_shields or shipped.solace_tide_raid_every != 2 \
			or shipped.solace_tide_retake_node != d.solace_tide_retake_node: fails += 1  # R-K, R-L, H7 cadence (designer 2026-10-26)
	var bad := CampaignConfigData.new()
	bad.solace_tide_retake_heat = -1
	if _tide_errors(bad).is_empty(): fails += 1  # a negative retake price is refused
	if d.solace_tide_start_cards().size() != 8 or d.solace_tide_start_cards()[7] != ["s7", "N", "JAM"]: fails += 1
	if not _tide_errors(d).is_empty(): fails += 1
	if shipped == null or shipped.solace_tide_hand_heat != d.solace_tide_hand_heat or shipped.solace_tide_beam_heat != d.solace_tide_beam_heat 			or shipped.solace_tide_home_hit_damage_by_band != d.solace_tide_home_hit_damage_by_band or shipped.solace_tide_start_deck != d.solace_tide_start_deck:
		fails += 1
	# the damage table against the raid content
	var strength := 0.0
	for t in shipped.heat_thresholds:
		if t != null and t.heat == 75:
			for m in t.ongoing_modifiers:
				if m != null and m.type == RC.RuleModifierType.RAID_STRENGTH_PCT:
					strength = m.value
	var derived: Array[int] = []
	var names := ["raid_claim", "raid_heat_25", "raid_heat_50", "raid_heat_75", "raid_purge"]
	for i in names.size():
		var raid: RaidData = load("res://content/raids/%s.tres" % names[i])
		var dmg := 0
		for w in raid.waves:
			for th in w.threats:
				dmg += th.damage
		var scale := 1.0 + (strength / 100.0 if i >= 3 else 0.0)
		derived.append(int(floor(dmg * scale + 0.5)))
	print("Solace tide HOME damage table (shipped / derived): ", Array(shipped.solace_tide_home_hit_damage_by_band), " ", derived)
	if Array(shipped.solace_tide_home_hit_damage_by_band) != derived: fails += 1
	return fails


## Phase 2b rule 8: CorporationData.raid_model defaults to resolver, only Solace ships tide, and a bad word is rejected.
func _raid_model_switch() -> int:
	var fails := 0
	var d := CorporationData.new()
	print("raid_model default (expect resolver false): ", d.raid_model, " ", d.uses_tide())
	if d.raid_model != &"resolver" or d.uses_tide(): fails += 1
	for id in ["solace", "meridian", "halcyon", "orbital", "rebel_cell"]:
		var c: CorporationData = load("res://content/corporations/%s.tres" % id)
		var want := &"tide" if id == "solace" else &"resolver"
		print("raid_model ", id, " (expect ", want, "): ", c.raid_model)
		if c.raid_model != want: fails += 1
	d.id = &"x"
	d.raid_model = &"bogus"
	var bad := false
	for e in d.validate():
		if String(e).contains("raid_model"):
			bad = true
	if not bad: fails += 1
	return fails


func _tide_errors(cfg: CampaignConfigData) -> Array:
	var out: Array = []
	for e in cfg.validate():
		if String(e).contains("solace_tide"):
			out.append(e)
	return out
