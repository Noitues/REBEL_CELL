extends GutTest
## Plan 2 WH-12 (Solace raid), fast tier. Phase 2b / R-G: Solace now plays the Infected Tide, so the resolver's step-based
## infection and the campaign figure `infection_bp` are retired (the tide's tests are test_solace_tide_*). What stays here:
## SolaceRaidRules' pure figure helpers (the raid views still read them until Phase 3), the resolver no longer infecting any
## campaign, operatives never killed in any raid (RD-03, Q24.1), and no inline numbers in the rules file.

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


func test_the_resolver_no_longer_infects_any_campaign() -> void:
	# R-G: a Solace-id campaign through RaidResolver (a bare grid, no raid_model) carries no infection figures either.
	var sol := _setup([&"r1"], {&"r1": &"relay"})
	var rs := _res(sol[0], sol[1], [&"collector"])
	assert_false(rs.infection_applies, "R-G: the step-based infection is gone")
	assert_true(rs.infection_figures.is_empty())
	assert_false(rs.city_lost)
	var s := _setup([&"r1"], {&"r1": &"relay"}, &"halcyon")
	var r := _res(s[0], s[1], [&"collector"])
	assert_false(r.infection_applies)
	assert_true(r.infection_figures.is_empty())
	assert_false(r.city_lost)
	var cfg: CampaignConfigData = _cfg.duplicate()
	cfg.raid_infection_lost_bp = 1
	assert_false(_res(s[0], s[1], [&"collector"], cfg).city_lost, "even at a tiny threshold")


func test_pure_helpers_after_decay_and_cell_holds() -> void:
	assert_eq(SolaceRaidRules.after_decay(50, 5000), 0, "floor at zero")
	assert_false(SolaceRaidRules.cell_holds(false, 1), "a TAKEN node: no decay")
	assert_false(SolaceRaidRules.cell_holds(true, 0), "a lost campaign: no decay")
	assert_true(SolaceRaidRules.cell_holds(false, 0))
	assert_eq(SolaceRaidRules.pct(1250), 12)
	assert_false(SolaceRaidRules.preview(null, _cfg)["applies"])


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


func test_the_rules_hold_no_inline_tuning_numbers() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/core/solace_raid_rules.gd")
	var re := RegEx.new()
	re.compile("\\b([2-9]|[1-9][0-9]+)\\b")  # 0 and 1 are structural
	for line in src.split("\n"):
		var code := line.split("##")[0]
		if code.strip_edges().begins_with("const") or code.strip_edges().is_empty():
			continue
		assert_null(re.search(code), "no inline number: %s" % line)
