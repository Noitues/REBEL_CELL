extends GutTest
## Solace at full size (GDD 4.1, 8.3, 4.2): the 32-Site Grid validates and follows the
## tier-chain rules, the Terminal events validate and resolve, tier gating and the
## DISPATCH clue chain hold, and the rescue event recruits.

var _cfg: CampaignConfigData
var _corp: CorporationData
var _lookup: ContentLookup
var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = _resolver.config
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"solace") as CorporationData


func test_grid_is_30_to_40_sites_with_chains_objectives_and_cross_links() -> void:
	var grid := _corp.city_grid
	assert_eq(grid.validate(_cfg.min_exploits_for_breach).size(), 0, str(grid.validate()))
	assert_eq(grid.size_warnings().size(), 0)
	var tiers := {1: 0, 2: 0, 3: 0, 4: 0}
	var objectives := 0
	var exploits := {}
	var locked := 0
	for s in grid.sites:
		tiers[s.tier] += 1
		if s.objective == RC.SiteObjective.HEAT_REDUCTION:
			objectives += 1
			assert_true(s.heat_change < 0)
		if s.objective == RC.SiteObjective.EXPLOIT:
			exploits[s.exploit_type] = true
		locked += s.locked_links.size()
	assert_eq(tiers[4], 1, "one boss Site")
	assert_true(tiers[1] >= 10 and tiers[2] >= 8 and tiers[3] >= 8)
	assert_eq(objectives, 4, "four Heat objectives")
	assert_eq(exploits.size(), 3, "each Exploit type at a different Site")
	assert_true(locked >= 8, "cross-links start locked")
	# Every T3 reaches the boss and the minimum path is T1 -> T2 -> T3 -> boss.
	for s in grid.sites:
		if s.tier == 3 and s.objective != RC.SiteObjective.HEAT_REDUCTION:
			assert_true(s.links.has(grid.boss_site_id), "%s reaches the boss" % s.id)
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	assert_eq(c.grid.distance(&"home", grid.boss_site_id, grid), 4)


func test_events_validate_resolve_and_respect_tier_gating() -> void:
	assert_true(_corp.events.size() >= 19, "%d events" % _corp.events.size())
	var clues := 0
	for ev in _corp.events:
		assert_not_null(ev)
		assert_true(ev.choices.size() >= 1, String(ev.id))
		for ch in ev.choices:
			assert_true(ch.label != "" and ch.result_text != "", String(ev.id))
			for e in ch.effects:
				assert_true(e.type in [RC.EffectType.MODIFY_HEAT, RC.EffectType.GAIN_CYCLES, RC.EffectType.GAIN_SCHEMATICS, RC.EffectType.HEAL, RC.EffectType.DEAL_DAMAGE], "%s uses a run-level effect" % ev.id)
		if ev.dispatch_clue:
			clues += 1
			assert_eq(ev.foreshadows, &"dispatch")
	assert_true(clues >= 3, "the DISPATCH clue chain has at least three events")
	# A tier-1 run never opens a tier-2+ event.
	var c := CampaignState.new()
	c.campaign_seed = 8
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	for seed in range(1, 40):
		var s := NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_a", seed)
		s.run.phase = RunState.Phase.MAP
		s._open_event()
		var ev := s.current_event()
		if ev != null:
			assert_true(ev.min_tier <= 1, "%s is tier %d" % [ev.id, ev.min_tier])


func test_rescue_event_recruits_a_rookie_and_choices_apply_costs() -> void:
	var c := CampaignState.new()
	c.campaign_seed = 8
	c.recruit(ContentRegistry.get_content(&"breaker") as ClassData, "Vex")
	var s := NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_a", 3)
	s.run.event_id = &"ev_rescue_operative"
	s.run.phase = RunState.Phase.EVENT
	var hp := s.run.operative.hp
	s.choose_event_option(0)
	assert_eq(c.roster.size(), 2, "a fresh rookie joined")
	assert_eq(s.run.operative.hp, hp - 12)
	var s2 := NetrunSession.start(_resolver, c, &"op_1", 1, &"t1_b", 4)
	s2.run.event_id = &"ev_honeypot"
	s2.run.phase = RunState.Phase.EVENT
	var heat := c.heat
	s2.choose_event_option(0)
	assert_eq(s2.run.cycles, 80)
	assert_true(c.heat >= heat + 5)
