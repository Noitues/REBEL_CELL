extends GutTest
## 1,000 seeds generate valid maps (reachability + guarantees); same seed = same map
## (M2 acceptance). Also the GDD 4.2 pacing shape (about 5 combats per path).

const SEEDS := 1000

var _cfg: CampaignConfigData


func before_all() -> void:
	_cfg = CombatFixture.config()


func _generate(seed: int, tier: int = 1) -> MapGraph:
	return MapGenerator.generate(tier, _cfg, RngStreams.make_stream(seed, &"map"))


func test_1000_seeds_generate_valid_maps() -> void:
	var invalid := 0
	var first_error := ""
	for seed in SEEDS:
		var graph := _generate(seed)
		var errors := graph.validate(_cfg)
		if not errors.is_empty():
			invalid += 1
			if first_error == "":
				first_error = "seed %d: %s" % [seed, errors]
	assert_eq(invalid, 0, "every seed valid (%s)" % first_error)


func test_same_seed_gives_the_same_map() -> void:
	for seed in [1, 42, 777, 31337]:
		assert_eq(_generate(seed).graph_hash(), _generate(seed).graph_hash(), "seed %d" % seed)
		assert_eq(JSON.stringify(_generate(seed).to_dict()), JSON.stringify(_generate(seed).to_dict()))


func test_different_seeds_give_different_maps() -> void:
	var hashes := {}
	for seed in 50:
		hashes[_generate(seed).graph_hash()] = true
	assert_true(hashes.size() > 45, "%d distinct maps out of 50 seeds" % hashes.size())


func test_map_round_trips_through_json() -> void:
	var graph := _generate(9)
	var loaded := MapGraph.from_dict(JSON.parse_string(JSON.stringify(graph.to_dict())))
	assert_eq(loaded.graph_hash(), graph.graph_hash())
	assert_eq(loaded.validate(_cfg).size(), 0)


func test_guarantees_hold_on_a_sample() -> void:
	for seed in 100:
		var g := _generate(seed)
		assert_eq(g.layer_count(), _cfg.map_layers)
		for node in g.nodes_in_layer(1):
			assert_eq(node["type"], RC.InfilNodeType.ROUTER, "layer 1 is Routers")
			assert_false(node["elite"])
		assert_eq(g.nodes_in_layer(_cfg.map_layers).size(), 1)
		assert_eq(g.nodes_in_layer(_cfg.map_layers)[0]["type"], RC.InfilNodeType.SERVER_RACK, "final node is a Rack")
		var racks_l4 := 0
		for node in g.nodes_in_layer(4):
			if node["type"] == RC.InfilNodeType.SERVER_RACK:
				racks_l4 += 1
		assert_eq(racks_l4, 1, "one Rack in layer 4 (seed %d)" % seed)
		var modems := 0
		for layer in range(3, 6):
			for node in g.nodes_in_layer(layer):
				if node["type"] == RC.InfilNodeType.MODEM:
					modems += 1
		assert_true(modems >= 1, "a Modem in layers 3-5 (seed %d)" % seed)
		for layer in range(3, 7):
			var elites := 0
			for node in g.nodes_in_layer(layer):
				if node["elite"] and node["type"] != RC.InfilNodeType.SERVER_RACK:
					elites += 1
			assert_true(elites >= 1 or g.nodes_in_layer(layer).size() <= 2, "an Elite in layer %d (seed %d)" % [layer, seed])
		for node in g.all_nodes():
			if node["type"] == RC.InfilNodeType.SERVER_RACK:
				assert_eq(node["heat"], _cfg.rack_heat_by_tier[0], "T1 Rack heat")
			elif node["elite"]:
				assert_eq(node["heat"], _cfg.elite_heat)
			else:
				assert_eq(node["heat"], 0)


func test_terminals_are_about_a_quarter_of_the_free_nodes() -> void:
	var terminals := 0
	var candidates := 0
	for seed in 200:
		var g := _generate(seed)
		for node in g.all_nodes():
			if node["layer"] == 1 or node["layer"] == _cfg.map_layers or node["elite"] or node["type"] == RC.InfilNodeType.MODEM:
				continue
			candidates += 1
			if node["type"] == RC.InfilNodeType.TERMINAL:
				terminals += 1
	var ratio := float(terminals) / candidates
	assert_true(ratio > 0.18 and ratio < 0.32, "terminal ratio %.2f near 0.25" % ratio)


func test_a_random_path_has_about_five_combats() -> void:
	var total_combats := 0
	var paths := 0
	var walk := CombatFixture.rng(5)
	for seed in 200:
		var g := _generate(seed)
		var ids := g.first_layer_ids()
		var id: StringName = ids[walk.randi_range(0, ids.size() - 1)]
		var combats := 0
		while id != &"":
			var node := g.get_node(id)
			if node["type"] in [RC.InfilNodeType.ROUTER, RC.InfilNodeType.SERVER_RACK]:
				combats += 1
			var next: Array = node["next"]
			id = next[walk.randi_range(0, next.size() - 1)] if not next.is_empty() else &""
		total_combats += combats
		paths += 1
	var mean := float(total_combats) / paths
	assert_true(mean >= 4.0 and mean <= 6.5, "mean combats per path %.2f (GDD: about 5)" % mean)


func _elite_routers(g: MapGraph) -> int:
	var n := 0
	for node in g.all_nodes():
		if node["elite"] and node["type"] == RC.InfilNodeType.ROUTER:
			n += 1
	return n


func test_elite_frequency_flips_extra_routers_to_elite_once_a_whole_node_accumulates() -> void:
	# +100%: every band layer gets a second elite when it has room. +25%: one extra elite
	# per four band layers. Types are fixed at generation, so the player sees them first.
	var base := 0
	var doubled := 0
	var quarter := 0
	for seed in 100:
		base += _elite_routers(MapGenerator.generate(1, _cfg, RngStreams.make_stream(seed, &"map"), 0.0))
		doubled += _elite_routers(MapGenerator.generate(1, _cfg, RngStreams.make_stream(seed, &"map"), 100.0))
		quarter += _elite_routers(MapGenerator.generate(1, _cfg, RngStreams.make_stream(seed, &"map"), 25.0))
	assert_true(doubled > base * 1.4, "+100%%: %d elites vs %d" % [doubled, base])
	assert_true(quarter > base and quarter < doubled, "+25%%: %d elites between %d and %d" % [quarter, base, doubled])
	for seed in 100:
		var g := MapGenerator.generate(1, _cfg, RngStreams.make_stream(seed, &"map"), 100.0)
		assert_eq(g.validate(_cfg).size(), 0, "still valid with extra elites")
		for layer in g.layers:
			if layer.size() < 3:
				continue  # two-node layers may be Rack + base elite by the GDD guarantees alone
			var normal := 0
			for node in layer:
				if not node["elite"]:
					normal += 1
			assert_true(normal >= 1, "extra elites leave a non-elite route (seed %d, layer %d)" % [seed, layer[0]["layer"]])


func test_elite_frequency_is_deterministic() -> void:
	var a := MapGenerator.generate(1, _cfg, RngStreams.make_stream(3, &"map"), 50.0)
	var b := MapGenerator.generate(1, _cfg, RngStreams.make_stream(3, &"map"), 50.0)
	assert_eq(a.graph_hash(), b.graph_hash())


func test_tier_changes_rack_heat_only() -> void:
	var g := _generate(3, 3)
	assert_eq(g.validate(_cfg).size(), 0)
	for node in g.all_nodes():
		if node["type"] == RC.InfilNodeType.SERVER_RACK:
			assert_eq(node["heat"], _cfg.rack_heat_by_tier[2])
