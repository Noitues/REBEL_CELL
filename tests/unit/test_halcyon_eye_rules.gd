extends GutTest
## Halcyon v2 THE EYE, slices 1-4 (fast): bearings and the half-open sector, the Eye moves each
## campaign turn (win, death, abandon), an Exploit fixes it for two turns after that turn's tick, the
## launch snapshot, the Blade (slot, level, ENCRYPTED, preview == result, replay, rewind) and the
## raid wedge (+25 percent, preview == result). Numbers only from config.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _halcyon: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_halcyon = ContentRegistry.get_content(&"halcyon") as CorporationData


func _campaign(seed: int = 1) -> CampaignState:
	return CampaignRules.new_campaign(_halcyon, _cfg, _lookup, seed, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())


func _street(c: CampaignState, site: StringName = &"t1_a") -> NetrunSession:
	return NetrunSession.start(_resolver, c, c.roster[0].id, 1, site, 5, _halcyon)


# --- Slice 1: the pure Eye ---------------------------------------------------------------------

func test_bearing_deterministic_and_clockwise_from_up() -> void:
	var grid := _halcyon.city_grid
	for s in grid.sites:
		assert_eq(EyeRules.bearing_deg(grid, s.id), EyeRules.bearing_deg(grid, s.id))
		var b := EyeRules.bearing_deg(grid, s.id)
		assert_true(b >= 0 and b < 360)
	var g := GridFixture.chain_grid([&"r1"])
	g.sites[0].map_position = Vector2(0, 0)
	g.sites[1].map_position = Vector2(0, -50)
	g.sites[2].map_position = Vector2(50, 0)
	assert_eq(EyeRules.bearing_deg(g, &"r1"), 0)
	assert_eq(EyeRules.bearing_deg(g, &"entry"), 90)


func test_sector_membership_edges_are_half_open() -> void:
	assert_true(EyeRules.in_sector(315, 0, _cfg), "centre - 45 is in")
	assert_false(EyeRules.in_sector(45, 0, _cfg), "centre + 45 is out")
	assert_true(EyeRules.in_sector(44, 0, _cfg))
	assert_false(EyeRules.in_sector(314, 0, _cfg))
	assert_eq(EyeRules.octant_of(22, _cfg), 0)
	assert_eq(EyeRules.octant_of(23, _cfg), 1)
	assert_eq(EyeRules.octant_of(359, _cfg), 0)
	assert_eq(EyeRules.octant_of(180, _cfg), 4)


func test_eye_start_is_drawn_once_and_saved() -> void:
	var c := _campaign(11)
	assert_eq(c.corp_theme.halcyon.eye_index, EyeRules.draw_start(11, _cfg), "stream eye_start")
	assert_eq(_campaign(11).corp_theme.halcyon.eye_index, c.corp_theme.halcyon.eye_index, "same seed, same draw")
	c.corp_theme.halcyon.eye_index = 6
	var back := CampaignState.from_dict(JSON.parse_string(JSON.stringify(c.to_dict())))
	assert_eq(back.corp_theme.halcyon.eye_index, 6, "load does not redraw")
	var m := CampaignRules.new_campaign(ContentRegistry.get_content(&"meridian") as CorporationData, _cfg, _lookup, 11, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	assert_eq(m.corp_theme.halcyon.eye_index, 0, "only Halcyon draws")


func test_eye_moves_each_campaign_turn_win_death_abandon() -> void:
	var c := _campaign()
	c.corp_theme.halcyon.eye_index = 7
	var s := _street(c)
	s._complete_run()
	assert_eq(c.corp_theme.halcyon.eye_index, 0, "a win moves it, mod 8")
	var c2 := _campaign()
	c2.corp_theme.halcyon.eye_index = 2
	_street(c2)._die()
	assert_eq(c2.corp_theme.halcyon.eye_index, 3, "a death moves it")
	var c3 := _campaign()
	c3.corp_theme.halcyon.eye_index = 4
	_street(c3).abandon()
	assert_eq(c3.corp_theme.halcyon.eye_index, 5, "an abandon moves it")


func test_exploit_fixes_two_turns_after_the_tick() -> void:
	var h := HalcyonCampaignTheme.new()
	h.eye_index = 0
	EyeRules.campaign_turn(h, _cfg, 90)
	assert_eq([h.eye_index, h.eye_fixed_left], [2, 2], "ticked to 1, then re-aimed at octant 2")
	EyeRules.campaign_turn(h, _cfg)
	assert_eq([h.eye_index, h.eye_fixed_left], [2, 1])
	EyeRules.campaign_turn(h, _cfg)
	assert_eq([h.eye_index, h.eye_fixed_left], [2, 0], "two turns held")
	EyeRules.campaign_turn(h, _cfg)
	assert_eq(h.eye_index, 3, "the third moves it")
	# A second Exploit re-aims and resets to 2, never stacks.
	EyeRules.campaign_turn(h, _cfg, 0)
	EyeRules.campaign_turn(h, _cfg)
	assert_eq(h.eye_fixed_left, 1)
	EyeRules.campaign_turn(h, _cfg, 180)
	assert_eq([h.eye_index, h.eye_fixed_left], [4, 2])


func test_a_real_exploit_run_fixes_the_eye() -> void:
	var c := _campaign()
	var site: SiteData = null
	for s in _halcyon.city_grid.sites:
		if s != null and s.objective == RC.SiteObjective.EXPLOIT and EyeRules.bearing_deg(_halcyon.city_grid, s.id) >= 0:
			site = s
			break
	assert_not_null(site)
	var run := _street(c, site.id)
	run._complete_run()
	assert_eq(c.corp_theme.halcyon.eye_fixed_left, _cfg.eye_fix_turns)
	assert_eq(c.corp_theme.halcyon.eye_index, EyeRules.octant_of(EyeRules.bearing_deg(_halcyon.city_grid, site.id), _cfg))


# --- Slice 2: the launch snapshot ---------------------------------------------------------------

func test_spotted_level_is_0_1_2_and_constant_mid_run() -> void:
	var h := HalcyonCampaignTheme.new()
	h.eye_index = 0
	assert_eq(EyeRules.spotted_level(h, 10, _cfg), 1, "inside, moving")
	assert_eq(EyeRules.spotted_level(h, 180, _cfg), 0, "outside")
	assert_eq(EyeRules.spotted_level(h, -1, _cfg), 0, "unknown")
	h.eye_fixed_left = 1
	assert_eq(EyeRules.spotted_level(h, 10, _cfg), 2, "inside, FIXED")
	var c := _campaign()
	c.corp_theme.halcyon.eye_index = 0
	var site: SiteData = null
	for s in _halcyon.city_grid.sites:
		if s != null and s.id != _halcyon.city_grid.home_site_id and EyeRules.in_sector(EyeRules.bearing_deg(_halcyon.city_grid, s.id), 0, _cfg):
			site = s
			break
	assert_not_null(site)
	var run := _street(c, site.id)
	assert_eq(run.run.corp_theme.halcyon.spotted_level, 1)
	c.corp_theme.halcyon.eye_fixed_left = 2
	c.corp_theme.halcyon.eye_index = 4
	assert_eq(run.run.corp_theme.halcyon.spotted_level, 1, "the snapshot never changes mid-run")
	assert_false(run.theme_chip().is_empty(), "the Spotted chip shows")


func test_launch_preview_equals_the_turn() -> void:
	var c := _campaign()
	c.corp_theme.halcyon.eye_index = 3
	var p := EyeRules.launch_preview(c, _halcyon, _cfg, &"h1_a")
	assert_eq(p["next_index"], 4)
	assert_true(bool(p["failed_moves"]))
	_street(c, &"h1_a")._die()
	assert_eq(c.corp_theme.halcyon.eye_index, p["next_index"], "preview == result")
	assert_false(EyeRules.launch_lines(p).is_empty())
	assert_false(EyeRules.launch_preview(c, ContentRegistry.get_content(&"meridian") as CorporationData, _cfg, &"x")["applies"])


# --- Slice 3: the Blade -----------------------------------------------------------------------

func test_blade_levels_classes_and_heat() -> void:
	var normal := {"type": RC.InfilNodeType.ROUTER, "elite": false}
	var elite := {"type": RC.InfilNodeType.ROUTER, "elite": true}
	var rack := {"type": RC.InfilNodeType.SERVER_RACK, "elite": true}
	assert_eq(EyeRules.fight_class(normal), &"NORMAL")
	assert_eq(EyeRules.fight_class(elite), &"ELITE")
	assert_eq(EyeRules.fight_class(rack), &"RACK")
	assert_eq(EyeRules.fight_class(rack, true), &"MINI_BOSS")
	for cls in [&"NORMAL", &"ELITE", &"RACK", &"MINI_BOSS"]:
		assert_false(EyeRules.blade_applies(0, cls, _cfg), "level 0 never")
	assert_false(EyeRules.blade_applies(1, &"NORMAL", _cfg), "level 1 skips normals")
	assert_true(EyeRules.blade_applies(1, &"ELITE", _cfg))
	assert_true(EyeRules.blade_applies(1, &"RACK", _cfg))
	assert_true(EyeRules.blade_applies(2, &"NORMAL", _cfg), "level 2 is every fight")
	assert_eq(EyeRules.spotted_heat(2, &"ELITE", _cfg), _cfg.spotted_elite_heat)
	assert_eq(EyeRules.spotted_heat(1, &"ELITE", _cfg), 0)
	assert_eq(EyeRules.spotted_heat(2, &"NORMAL", _cfg), 0)


func test_the_session_turns_the_blade_on_by_level_and_adds_elite_heat() -> void:
	var c := _campaign()
	var s := _street(c)
	s.run.corp_theme.halcyon.spotted_level = 1
	s.run.map = MapGenerator.generate(1, _cfg, s.streams.get_stream(&"map"), 0)
	s.run.current_node_id = s.run.map.layers[0][0]["id"]
	assert_true(s._blade_overrides(false).is_empty(), "level 1: a Router is a normal fight")
	s.run.corp_theme.halcyon.spotted_level = 2
	assert_true(bool(s._blade_overrides(false).get("blade", false)), "level 2: every fight")
	s.run.corp_theme.halcyon.spotted_level = 0
	assert_true(s._blade_overrides(false).is_empty())


func test_blade_slot_skips_empty_slots_and_is_pure() -> void:
	var sizes := PackedInt32Array([5, 0, 5, 5, 0, 5])
	assert_eq(EyeRules.blade_slot(sizes, 1), 0)
	assert_eq(EyeRules.blade_slot(sizes, 2), 2)
	assert_eq(EyeRules.blade_slot(sizes, 4), 5)
	assert_eq(EyeRules.blade_slot(sizes, 5), 0, "wraps over the four non-empty slots")
	assert_eq(EyeRules.blade_slot(PackedInt32Array([0, 0]), 1), -1)


func _combat(blade: bool, seed: int = 4242) -> CombatSession:
	var atk := CombatFixture.slice(&"bl_atk", RC.SliceType.SHIM, 8)
	var nul := CombatFixture.slice(&"bl_null", RC.SliceType.NULL, 0, RC.TargetRule.SELF)
	var cls := CombatFixture.operative_class(&"bl_class", 60, CombatFixture.wheel([atk, atk, atk, atk, atk, nul]), [] as Array[CardData])
	var enemy := CombatFixture.enemy(&"bl_enemy", 500, CombatFixture.wheel([nul, nul, nul, nul, nul, nul]))
	var res := CombatFixture.resolver([cls, enemy])
	var s := CombatSession.start(res, cls.id, [enemy.id], seed, &"", 0, {"blade": true} if blade else {})
	CombatFixture.land(s.state.player, 0, 1)
	return s


func test_the_scan_marks_slot_turn_minus_one_and_clears_after_the_resolve() -> void:
	var s := _combat(true)
	assert_eq(int(s.state.flags.get("blade_slot", 0)) - 1, 0, "turn 1 scans slot 0")
	assert_eq(s.state.player.wheel.stacks_of(0, RC.Status.TIER_DOWN), 1)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.turn, 2)
	assert_eq(int(s.state.flags.get("blade_slot", 0)) - 1, 1, "turn 2 scans slot 1")
	assert_eq(s.state.player.wheel.stacks_of(0, RC.Status.TIER_DOWN), 0, "the mark lasted the one resolve")
	assert_eq(s.state.player.wheel.stacks_of(1, RC.Status.TIER_DOWN), 1)
	var off := _combat(false)
	assert_false(off.state.flags.has("blade_slot"), "no Blade, no scan")


func test_encrypted_absorbs_the_blade_and_is_consumed() -> void:
	var s := _combat(true)
	s.state.player.wheel.set_status(1, RC.Status.ENCRYPTED, 1)
	s.apply(CombatAction.end_turn())
	assert_eq(s.state.player.wheel.stacks_of(1, RC.Status.TIER_DOWN), 0, "absorbed")
	assert_eq(s.state.player.wheel.stacks_of(1, RC.Status.ENCRYPTED), 0, "consumed")
	assert_eq(int(s.state.flags.get("blade_stacks", 0)), 0)


func test_blade_preview_equals_result_and_lowers_the_hit() -> void:
	var a := _combat(true)
	var preview := a.preview_end_turn()
	var result := a.apply(CombatAction.end_turn())
	assert_eq(preview.resolved_state.get_combatant(&"enemy_0").hp, result.resolved_state.get_combatant(&"enemy_0").hp, "preview == result")
	var b := _combat(false)
	var plain := b.apply(CombatAction.end_turn())
	assert_gt(result.resolved_state.get_combatant(&"enemy_0").hp, plain.resolved_state.get_combatant(&"enemy_0").hp, "the Blade lowered the tier")


func test_blade_replay_and_rewind() -> void:
	var a := _combat(true, 99)
	var b := _combat(true, 99)
	for s in [a, b]:
		s.apply(CombatAction.end_turn())
		s.apply(CombatAction.end_turn())
	assert_eq(a.state_hash(), b.state_hash(), "seeded replay matches")
	var c := _combat(true)
	c._set_checkpoint()
	var before := c.state_hash()
	c.apply(CombatAction.nudge(&"enemy_0", 1))
	assert_true(c.rewind().ok())
	assert_eq(c.state_hash(), before)
	assert_eq(int(c.state.flags.get("blade_slot", 0)), 1, "the scanned slot is the same after undo")


# --- Slice 4: the raid wedge ------------------------------------------------------------------

func _wedge_raid(eye: int) -> RaidResolver.RaidResult:
	var grid := GridFixture.chain_grid([&"r1"])
	grid.sites[0].map_position = Vector2(0, 0)
	grid.sites[1].map_position = Vector2(0, -100)
	grid.sites[2].map_position = Vector2(0, -200)
	var c := GridFixture.campaign(grid, {&"r1": &"relay"})
	c.corporation_id = &"halcyon"
	c.corp_theme.halcyon.eye_index = eye
	return RaidResolver.resolve(c, grid, GridFixture.raid(&"wedge", [&"enforcer"]), _lookup, _cfg, [&"entry"])


func _first_hit(r: RaidResolver.RaidResult) -> int:
	for e in r.events:
		if e["type"] == "node_hit" or e["type"] == "down":
			return int(e.get("damage", -1))
	return -1


func test_raid_wedge_damage_inside_and_outside_and_fixed_holds() -> void:
	var inside := _wedge_raid(0)
	var outside := _wedge_raid(4)
	assert_true(inside.eye_wedge.has("r1"), "r1 is due north: inside the octant 0 sector")
	assert_true(outside.eye_wedge.is_empty())
	assert_eq(EyeRules.wedge_damage(10, 25), 13)
	assert_eq(EyeRules.wedge_damage(10, 0), 10)
	var base := _first_hit(outside)
	if base > 0:
		assert_eq(_first_hit(inside), EyeRules.wedge_damage(base, _cfg.raid_eye_damage_pct), "+25 percent inside, 0 outside")
	assert_eq(_wedge_raid(0).summary_hash(), inside.summary_hash(), "a replay matches (preview == result)")
	var h := HalcyonCampaignTheme.new()
	h.eye_index = 0
	h.eye_fixed_left = 2
	assert_eq(EyeRules.raid_damage_pct(h, 10, _cfg), _cfg.raid_eye_damage_pct, "a FIXED Eye holds the same wedge")
	assert_eq(EyeRules.raid_damage_pct(h, 200, _cfg), 0)
