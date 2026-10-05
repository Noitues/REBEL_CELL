extends GutTest
## ART-8 8p: every node of an HQ run has a place on its corporation's compound, and the
## places are deterministic (HqCompoundLayout over content/city/hq_compounds/<corp>.tres).
## Today's HQ run is the breach (NetrunSession.start_special "boss": one node); a full run
## map (MapGenerator, GDD 4.2) at the HQ is covered too, so the table holds either way.

const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
const SEEDS: Array[int] = [1, 7, 42, 2026]
const HQ_TIER := 4

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _solace: CorporationData


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_solace = ContentRegistry.get_content(&"solace") as CorporationData


func _layout(corp: StringName) -> HqCompoundLayoutData:
	return ContentRegistry.get_content(HqCompoundLayoutData.id_for(corp)) as HqCompoundLayoutData


func _breach_graph(run_seed: int) -> MapGraph:
	var c := CampaignRules.new_campaign(_solace, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start_special(_resolver, c, c.roster[0].id, "boss", &"t1_a", HQ_TIER, run_seed, &"triage_unit", {})
	return s.run.map


func _map_graph(run_seed: int) -> MapGraph:
	return MapGenerator.generate(HQ_TIER, _cfg, RngStreams.make_stream(run_seed, &"map"))


func test_every_corporation_has_a_layout_that_fits_the_run_rules() -> void:
	for corp in CORPS:
		var l := _layout(corp)
		assert_not_null(l, "layout for %s" % corp)
		if l == null:
			continue
		assert_eq(l.corporation_id, corp)
		assert_eq(l.validate().size(), 0, "%s validates: %s" % [corp, l.validate()])
		assert_eq(l.slots_per_layer, _cfg.map_nodes_max, "%s: one slot per possible node of a layer" % corp)
		assert_eq(l.layer_rows(), _cfg.map_layers - 1, "%s: a row for every layer before the final one" % corp)
		assert_true(FileAccess.file_exists(l.asset_dir + "/manifest.json"), "%s has its model manifest" % corp)


func test_every_node_of_the_breach_run_stands_on_the_central_server() -> void:
	for run_seed in SEEDS:
		var g := _breach_graph(run_seed)
		assert_eq(g.node_count(), 1, "today's HQ run is the single breach node")
		for corp in CORPS:
			var l := _layout(corp)
			var p: Variant = HqCompoundLayout.position_of(l, g, g.final_node_id())
			assert_eq(p, l.central_server, "%s seed %d: the breach is at the Central Server" % [corp, run_seed])


func test_every_node_of_a_generated_run_map_has_a_distinct_position() -> void:
	for run_seed in SEEDS:
		var g := _map_graph(run_seed)
		for corp in CORPS:
			var l := _layout(corp)
			var pos := HqCompoundLayout.positions(l, g)
			assert_eq(pos.size(), g.node_count(), "%s seed %d: every node placed" % [corp, run_seed])
			assert_eq(pos[g.final_node_id()], l.central_server, "%s seed %d: the final node is the Central Server" % [corp, run_seed])
			var seen := {}
			for id in pos:
				seen[pos[id]] = true
			assert_eq(seen.size(), pos.size(), "%s seed %d: no two nodes share a place" % [corp, run_seed])


func test_positions_are_deterministic() -> void:
	for run_seed in SEEDS:
		for corp in CORPS:
			var l := _layout(corp)
			var a := HqCompoundLayout.positions(l, _map_graph(run_seed))
			var b := HqCompoundLayout.positions(l, _map_graph(run_seed))
			assert_eq(a, b, "%s seed %d: same seed, same places" % [corp, run_seed])
			assert_eq(a.keys(), b.keys(), "and the same order")


func test_a_layer_keeps_its_left_to_right_order_on_the_row() -> void:
	# The generator's edges never cross by index; slots keep index order, ends included.
	for count in range(1, _cfg.map_nodes_max + 1):
		var last := -1
		for i in count:
			var s := HqCompoundLayout.slot_for(i, count, _cfg.map_nodes_max)
			assert_true(s > last, "count %d index %d -> slot %d after %d" % [count, i, s, last])
			last = s
		if count > 1:
			assert_eq(HqCompoundLayout.slot_for(0, count, _cfg.map_nodes_max), 0)
			assert_eq(HqCompoundLayout.slot_for(count - 1, count, _cfg.map_nodes_max), _cfg.map_nodes_max - 1)
	assert_eq(HqCompoundLayout.slot_for(0, _cfg.map_nodes_max + 1, _cfg.map_nodes_max), -1, "a layer wider than the row has no slot")


func test_a_node_without_a_slot_has_no_position() -> void:
	var l := _layout(&"meridian")
	var g := _map_graph(SEEDS[0])
	assert_null(HqCompoundLayout.position_of(l, g, &"L9N9"), "unknown node")
	assert_null(HqCompoundLayout.position_of(null, g, g.final_node_id()), "no layout")
