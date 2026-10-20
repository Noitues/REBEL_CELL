extends GutTest
## RG-04: the CACHE node, a plain reward. Placement is v2 only and config-weighted; entering pays Cycles in the
## configured range (reward scale applied) and queues a card offer on the rewards stream; the same seed pays the
## same; the puzzle switch cannot turn a puzzle on while none is vetted; the payout page is the existing REWARD page.

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _corp: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_corp = ContentRegistry.get_content(&"meridian") as CorporationData


func _gen(seed: int, tier: int, v2: bool = true, cfg: CampaignConfigData = null) -> MapGraph:
	return MapGenerator.generate(tier, cfg if cfg != null else _cfg, RngStreams.make_stream(seed, &"map"), 0.0, v2)


func _count(g: MapGraph, type: int) -> int:
	var n := 0
	for node in g.all_nodes():
		if int(node["type"]) == type:
			n += 1
	return n


func _session(seed: int = 5, tier: int = 1) -> NetrunSession:
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, tier, &"m1_a", seed, _corp)
	var first := s.available_nodes()[0]
	s.run.map.get_node(first)["type"] = RC.InfilNodeType.CACHE
	s.run.cycles = 0
	s.enter_node(first)
	return s


func test_caches_appear_only_in_v2_graphs_at_most_one_in_the_configured_layers() -> void:
	var seen := 0
	for seed in 300:
		var tier := 1 + seed % 4
		var g := _gen(seed, tier)
		var n := _count(g, RC.InfilNodeType.CACHE)
		assert_lte(n, 1)
		seen += n
		assert_eq(_count(_gen(seed, tier, false), RC.InfilNodeType.CACHE), 0, "a v1 map has none")
		for node in g.all_nodes():
			if int(node["type"]) == RC.InfilNodeType.CACHE:
				assert_gte(int(node["layer"]), _cfg.cache_layers.x)
				assert_lte(int(node["layer"]), _cfg.cache_layers.y)
				assert_false(node["elite"])
	assert_gt(seen, 100, "the weight yields Caches")
	assert_lt(seen, 280, "and not on every map")


func test_weight_zero_places_none() -> void:
	var cfg := _cfg.duplicate() as CampaignConfigData
	cfg.node_weight_cache = 0
	for seed in 40:
		assert_eq(_count(_gen(seed, 2, true, cfg), RC.InfilNodeType.CACHE), 0)


func test_entering_pays_cycles_in_range_and_offers_cards_and_the_same_seed_pays_the_same() -> void:
	for tier in [1, 2, 3]:
		var s := _session(5, tier)
		var scale := s.reward_scale()
		assert_gte(s.run.cycles, roundi(_cfg.cache_cycles_range.x * scale))
		assert_lte(s.run.cycles, roundi(_cfg.cache_cycles_range.y * scale))
		assert_eq(s.run.phase, RunState.Phase.REWARD, "the existing reward page shows the card offer")
		var offer := s.current_reward()
		assert_eq(offer["kind"], "card")
		assert_eq(offer["options"].size(), _cfg.cache_card_choices)
		var again := _session(5, tier)
		assert_eq(again.run.cycles, s.run.cycles)
		assert_eq(again.current_reward(), offer)
		assert_eq(again.state_hash(), s.state_hash(), "seeded replay matches")


func test_taking_the_card_adds_it_and_returns_to_the_map() -> void:
	var s := _session()
	var deck := s.run.operative.deck.size()
	s.choose_reward(0)
	assert_eq(s.run.operative.deck.size(), deck + 1, "taking the card adds it")
	assert_eq(s.run.phase, RunState.Phase.MAP)


func test_the_puzzle_switch_changes_nothing_while_no_puzzle_is_vetted() -> void:
	assert_false(_cfg.cache_puzzle_enabled, "off by config")
	assert_true(CacheRules.VETTED_PUZZLES.is_empty())
	var cfg := _cfg.duplicate() as CampaignConfigData
	cfg.cache_puzzle_enabled = true
	assert_false(CacheRules.puzzle_active(cfg), "on in config, still no vetted puzzle")
	var a := _session(9)
	_cfg.cache_puzzle_enabled = true
	var b := _session(9)
	_cfg.cache_puzzle_enabled = false
	assert_eq(a.run.cycles, b.run.cycles)
	assert_eq(a.current_reward(), b.current_reward())
