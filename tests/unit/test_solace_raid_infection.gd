extends GutTest
## Plan 2 WH-12 (Solace raid), fast tier: the population infection figure is a pure function
## of the raid's steps (living threats per step), the Heat band and the config; a replay gives
## identical figures; slower play infects more; the config threshold means the city is infected
## and Solace wins the raid; operatives are never killed in any raid (RD-03, Q24.1); numbers only
## from config; the figure survives the (v5, additive) save.

const SaveServiceScript := preload("res://scripts/autoload/save_service.gd")

var _cfg: CampaignConfigData
var _lookup: ContentLookup


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func _setup(middle: Array[StringName], claims: Dictionary, corp: StringName = &"solace") -> Array:
	var grid := GridFixture.chain_grid(middle)
	var c := GridFixture.campaign(grid, claims)
	c.corporation_id = corp
	return [c, grid]


func _res(c: CampaignState, grid: CityGridData, ids: Array, cfg: CampaignConfigData = null) -> RaidResolver.RaidResult:
	return RaidResolver.resolve(c, grid, GridFixture.raid(&"wh12", ids), _lookup, cfg if cfg != null else _cfg, [&"entry"])


func test_figures_are_a_pure_function_of_living_threats_and_config() -> void:
	var living: Array[int] = [2, 2, 1, 0, 3]
	var a := SolaceRaidRules.figures(500, living, _cfg)
	var b := SolaceRaidRules.figures(500, living, _cfg)
	assert_eq(a, b, "same turns, same figures")
	var want := 500
	for i in living.size():
		want += _cfg.raid_infection_bp_base + _cfg.raid_infection_bp_per_threat * living[i]
		assert_eq(a[i + 1], want, "step %d rise is base + per_threat x living" % (i + 1))
	assert_eq(a.size(), living.size() + 1)


func test_the_figure_never_decreases_and_caps_at_the_threshold() -> void:
	var living: Array[int] = []
	for i in 40:
		living.append(i % 3)
	var f := SolaceRaidRules.figures(0, living, _cfg)
	for i in range(1, f.size()):
		assert_true(f[i] >= f[i - 1], "monotonic at step %d" % i)
	assert_true(f.back() <= _cfg.raid_infection_lost_bp, "capped at the lost threshold")
	assert_eq(SolaceRaidRules.lost_step(f, _cfg), f.find(_cfg.raid_infection_lost_bp), "first lost step")
	var calm: Array[int] = [0, 100]
	assert_eq(SolaceRaidRules.lost_step(calm, _cfg), -1, "never lost")


func test_the_start_figure_follows_the_heat_band() -> void:
	var s := _setup([&"r1"], {&"r1": &"relay"})
	var c: CampaignState = s[0]
	var levels := HeatRules.band_levels(c, _cfg)
	for band in _cfg.raid_infection_start_bp_by_band.size():
		c.heat = 0 if band == 0 else levels[band - 1]
		assert_eq(SolaceRaidRules.heat_band_index(c, _cfg), band)
		assert_eq(SolaceRaidRules.start_bp(c, _cfg), _cfg.raid_infection_start_bp_by_band[band], "band %d start" % band)
	assert_eq(SolaceRaidRules.pct(1250), 12)


func test_a_resolved_raid_carries_the_figures_and_a_replay_matches() -> void:
	var s := _setup([&"r1", &"r2"], {&"r1": &"relay", &"r2": &"relay"})
	var c: CampaignState = s[0]
	c.heat = 40
	var a := _res(c, s[1], [&"collector", &"auditor"])
	var b := _res(c, s[1], [&"collector", &"auditor"])
	assert_true(a.infection_applies)
	assert_eq(a.infection_figures[0], SolaceRaidRules.start_bp(c, _cfg), "starts at the band value")
	assert_eq(a.infection_figures.size(), a.steps_run + 1, "one figure per step plus the start")
	assert_eq(a.infection_figures, b.infection_figures, "a replay gives identical figures")
	assert_eq(a.infection_bp, a.infection_figures.back())
	assert_eq(a.summary_hash(), b.summary_hash())
	for i in range(1, a.infection_figures.size()):
		assert_true(a.infection_figures[i] > a.infection_figures[i - 1], "rises every resolution step")
	assert_eq(a.infection_pct_at(0), a.infection_start_bp / 100)
	assert_eq(a.infection_pct_at(999), a.infection_bp / 100, "clamped to the last step")


func test_slower_play_infects_more() -> void:
	var short := _setup([&"r1"], {&"r1": &"relay"})
	var long := _setup([&"r1", &"r2", &"r3", &"r4"], {&"r1": &"relay", &"r2": &"relay", &"r3": &"relay", &"r4": &"relay"})
	var a := _res(short[0], short[1], [&"collector"])
	var b := _res(long[0], long[1], [&"collector"])
	assert_true(b.steps_run > a.steps_run)
	assert_true(b.infection_bp > a.infection_bp, "more steps, more infection")
	var many := _res(short[0], short[1], [&"collector", &"collector", &"collector"])
	assert_true(many.infection_figures[1] - many.infection_figures[0] > a.infection_figures[1] - a.infection_figures[0], "more living threats rise faster")


func test_past_the_threshold_the_city_is_infected_and_solace_wins() -> void:
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.raid_infection_lost_bp = 200
	var s := _setup([&"r1", &"r2", &"r3"], {&"r1": &"relay", &"r2": &"relay", &"r3": &"relay"})
	var c: CampaignState = s[0]
	var r := _res(c, s[1], [&"collector"], cfg)
	assert_true(r.city_lost)
	assert_true(r.campaign_lost)
	assert_false(r.won)
	assert_eq(r.infection_bp, 200)
	assert_eq(r.steps_run, SolaceRaidRules.lost_step(r.infection_figures, cfg), "ends on the step the threshold is reached")
	var events := RaidResolver.apply(c, r, GridFixture.raid(&"wh12", [&"collector"]), cfg)
	assert_eq(c.outcome, CampaignState.Outcome.LOST)
	assert_eq(events.back()["type"], "city_lost", "its own end text")
	assert_eq(c.corp_theme.raid.solace.infection_bp, 200, "the figure is stored for the HUD")
	var calm := _res(c, s[1], [&"collector"])
	assert_false(calm.city_lost, "the default threshold does not lose this raid")


func test_a_holding_raid_ends_normally() -> void:
	var s := _setup([&"r1"], {&"r1": &"relay"})
	var r := _res(s[0], s[1], [&"collector"])
	assert_false(r.city_lost)
	assert_false(r.campaign_lost)


func test_other_corporations_have_no_infection() -> void:
	var s := _setup([&"r1"], {&"r1": &"relay"}, &"halcyon")
	var r := _res(s[0], s[1], [&"collector"])
	assert_false(r.infection_applies)
	assert_true(r.infection_figures.is_empty())
	assert_false(r.city_lost)
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.raid_infection_lost_bp = 1
	assert_false(_res(s[0], s[1], [&"collector"], cfg).city_lost, "even at a tiny threshold")


func test_infection_resets_per_raid() -> void:
	var s := _setup([&"r1"], {&"r1": &"relay"})
	var c: CampaignState = s[0]
	var raid := GridFixture.raid(&"wh12", [&"collector"])
	var first := RaidResolver.resolve(c, s[1], raid, _lookup, _cfg, [&"entry"])
	RaidResolver.apply(c, first, raid, _cfg)
	assert_true(c.corp_theme.raid.solace.infection_bp > 0)
	var second := RaidResolver.resolve(c, s[1], raid, _lookup, _cfg, [&"entry"])
	assert_eq(second.infection_figures[0], SolaceRaidRules.start_bp(c, _cfg), "nothing carries over")


func test_rd03_operatives_are_never_killed_in_any_raid() -> void:
	var cls := ContentRegistry.get_content(&"breaker") as ClassData
	var cases: Array = []
	for corp in [&"solace", &"halcyon"]:
		for lost_bp in [_cfg.raid_infection_lost_bp, 200]:
			cases.append([corp, lost_bp])
	for case in cases:
		var cfg: CampaignConfigData = _cfg.duplicate()
		cfg.raid_infection_lost_bp = case[1]
		var s := _setup([&"r1", &"r2"], {&"r1": &"relay", &"r2": &"relay"}, case[0])
		var c: CampaignState = s[0]
		var op := OperativeState.from_class(cls, &"op_a")
		c.roster.append(op)
		c.grid.site(&"r1")["stationed"] = String(op.id)
		var before := op.hp
		var raid := GridFixture.raid(&"wh12", [&"enforcer", &"enforcer", &"enforcer", &"enforcer"])
		var r := RaidResolver.resolve(c, s[1], raid, _lookup, cfg, [&"entry"])
		RaidResolver.apply(c, r, raid, cfg)
		assert_eq(c.roster.size(), 1, "no operative lost (%s, %d)" % [case[0], case[1]])
		assert_eq(c.roster[0].hp, before, "no operative damaged")
		assert_true(c.roster[0].hp > 0)


func test_the_figure_round_trips_the_save_without_a_version_bump() -> void:
	var s := _setup([&"r1"], {&"r1": &"relay"})
	var c: CampaignState = s[0]
	var raid := GridFixture.raid(&"wh12", [&"collector"])
	RaidResolver.apply(c, RaidResolver.resolve(c, s[1], raid, _lookup, _cfg, [&"entry"]), raid, _cfg)
	var c2 := CampaignState.from_dict(JSON.parse_string(JSON.stringify(c.to_dict())))
	assert_eq(c2.corp_theme.raid.solace.infection_bp, c.corp_theme.raid.solace.infection_bp)
	assert_eq(c2.state_hash(), c.state_hash())
	assert_eq(SaveServiceScript.SAVE_VERSION, 5)


func test_the_rules_hold_no_inline_tuning_numbers() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/core/solace_raid_rules.gd")
	var re := RegEx.new()
	re.compile("\\b([2-9]|[1-9][0-9]+)\\b")  # 0 and 1 are structural
	for line in src.split("\n"):
		var code := line.split("##")[0]
		if code.strip_edges().begins_with("const") or code.strip_edges().is_empty():
			continue
		assert_null(re.search(code), "no inline number: %s" % line)
