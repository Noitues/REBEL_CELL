extends GutTest
## RG-03: the WORKSHOP node (the slice-refit form: N18 slice upgrades are not built). Placement is v2 only and
## config-weighted; offers come from the existing rewards stream at entry; the refit uses the Mainframe's socket
## rule at the Workshop price; preview == result; one buy per visit; the page round-trips a save.

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


func _session(seed: int = 5) -> NetrunSession:
	var c := CampaignRules.new_campaign(_corp, _cfg, _lookup, 1, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 2, &"m1_a", seed, _corp)
	var first := s.available_nodes()[0]
	s.run.map.get_node(first)["type"] = RC.InfilNodeType.WORKSHOP
	s.enter_node(first)
	return s


func test_workshops_appear_only_in_v2_graphs_from_the_min_tier_and_never_beside_a_mainframe() -> void:
	var seen := 0
	for seed in 300:
		var tier := 1 + seed % 4
		var g := _gen(seed, tier)
		var n := _count(g, RC.InfilNodeType.WORKSHOP)
		assert_lte(n, 1)
		seen += n
		if tier < _cfg.workshop_min_tier:
			assert_eq(n, 0, "tier %d has none" % tier)
		assert_eq(_count(_gen(seed, tier, false), RC.InfilNodeType.WORKSHOP), 0, "a v1 map has none")
		for node in g.all_nodes():
			if int(node["type"]) == RC.InfilNodeType.WORKSHOP:
				assert_gte(int(node["layer"]), _cfg.workshop_layers.x)
				assert_lte(int(node["layer"]), _cfg.workshop_layers.y)
				for other in g.nodes_in_layer(int(node["layer"])):
					assert_ne(int(other["type"]), RC.InfilNodeType.MAINFRAME, "never in a Mainframe layer")
	assert_gt(seen, 100, "the weight yields Workshops")


func test_weight_zero_places_none_and_the_rest_stays_where_it_was() -> void:
	var cfg := _cfg.duplicate() as CampaignConfigData
	cfg.node_weight_workshop = 0
	for seed in 40:
		var a := _gen(seed, 3, true, cfg)
		assert_eq(_count(a, RC.InfilNodeType.WORKSHOP), 0)
		assert_gte(_count(a, RC.InfilNodeType.REST), 1, "the REST pass is unchanged")


func test_entry_draws_offers_from_the_rewards_stream_only() -> void:
	var s := _session()
	assert_eq(s.run.phase, RunState.Phase.WORKSHOP)
	var offers: Array = s.run.node_state["offers"]
	assert_eq(offers.size(), mini(_cfg.workshop_offers_per_visit, _cfg.shop_slices.size()))
	var uniq := {}
	for o in offers:
		uniq[o] = true
	assert_eq(uniq.size(), offers.size(), "no duplicates")
	var again := _session()
	assert_eq(again.run.node_state["offers"], offers, "same seed, same offers")


func test_buy_preview_equals_result_and_one_buy_per_visit() -> void:
	var s := _session()
	s.run.cycles = 500
	var op := s.run.operative
	var slot := 0
	for i in op.slot_slice_ids.size():
		if op.slot_firmware_ids[i] == &"":
			slot = i
			break
	var pv := s.workshop_preview(0, slot)
	var cycles := s.run.cycles
	assert_eq(s.workshop_error(0, slot), "")
	s.workshop_buy(0, slot)
	assert_eq(op.slot_slice_ids[slot], pv["slice"], "the slice is the preview's")
	assert_eq(s.run.cycles, int(pv["cycles_after"]))
	assert_eq(cycles - s.run.cycles, s.workshop_price(slot))
	assert_ne(s.workshop_error(1, slot), "", "the visit's buy is spent")
	var after := op.slot_slice_ids.duplicate()
	s.workshop_buy(1, slot)
	assert_eq(op.slot_slice_ids, after)
	s.leave_workshop()
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_true(s.run.node_state.is_empty())


func test_too_few_cycles_and_a_firmware_that_would_not_fit_are_refused() -> void:
	var s := _session()
	s.run.cycles = 0
	assert_ne(s.workshop_error(0, 0), "")
	s.run.cycles = 500
	assert_eq(s.workshop_error(0, 0).find("Not enough"), -1)
	assert_ne(s.workshop_error(-1, 0), "")
	assert_ne(s.workshop_error(0, 99), "")
	# A chip that fits only some slice types blocks a refit with a slice of another type.
	var op := s.run.operative
	for fw_id in [&"leech", &"mirror", &"shunt"]:
		var fw := _lookup.get_content(fw_id) as FirmwareData
		if fw == null or fw.allowed_slice_types.is_empty():
			continue
		for slot in op.slot_slice_ids.size():
			if s.firmware_slot_error(fw_id, slot) != "":
				continue
			op.slot_firmware_ids[slot] = fw_id
			for offer in s.run.node_state["offers"].size():
				var slice := _lookup.get_content(StringName(String(s.run.node_state["offers"][offer]))) as SliceData
				var fits := slice.slice_type in fw.allowed_slice_types
				assert_eq(s.workshop_error(offer, slot) == "", fits, "the socket rule decides")
			op.slot_firmware_ids[slot] = &""
			return


func test_the_open_page_survives_a_save() -> void:
	var s := _session()
	var back := NetrunSession.from_dict(_resolver, s.campaign, s.to_dict(), _corp)
	assert_eq(back.state_hash(), s.state_hash())
	assert_eq(back.run.phase, RunState.Phase.WORKSHOP)
	assert_eq(back.run.node_state["offers"], s.run.node_state["offers"])
