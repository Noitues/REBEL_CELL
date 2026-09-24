class_name MapGenerator
extends RefCounted
## Netrun map generation (TECH_SPEC 6). Pure: same tier + config + RNG state = same map.
## Regenerates with the next RNG values when validation fails.

const MAX_ATTEMPTS := 50


## Generates a valid MapGraph for `tier` using the `map` stream. `elite_frequency_pct`
## (Heat/ICE ELITE_FREQUENCY_PCT modifiers, summed) adds that fraction of an elite per
## layer of the elite band; whenever the fraction accumulates to a whole node, one more
## normal Router in that layer becomes elite. Node types are fixed before the player
## sees the map (designer ruling 2026-09-24: never surprise-elites).
static func generate(tier: int, config: CampaignConfigData, rng: RandomNumberGenerator, elite_frequency_pct: float = 0.0) -> MapGraph:
	for attempt in MAX_ATTEMPTS:
		var graph := _build(tier, config, rng, elite_frequency_pct)
		if graph.validate(config).is_empty():
			return graph
	push_error("MapGenerator: no valid map after %d attempts." % MAX_ATTEMPTS)
	return _build(tier, config, rng, elite_frequency_pct)


static func _build(tier: int, config: CampaignConfigData, rng: RandomNumberGenerator, elite_frequency_pct: float = 0.0) -> MapGraph:
	var graph := MapGraph.new()
	var layer_count := config.map_layers
	# 1. Layer sizes (the last layer is the single final Server Rack).
	for li in layer_count:
		var number := li + 1
		var size := 1 if number == layer_count else rng.randi_range(config.map_nodes_min, config.map_nodes_max)
		var layer := []
		for ni in size:
			layer.append({"id": MapGraph.make_id(number, ni), "layer": number, "index": ni,
				"type": RC.InfilNodeType.ROUTER, "elite": false, "next": [] as Array[StringName], "heat": 0})
		graph.layers.append(layer)
	# 2. Types. Layer 1 all Routers; Racks at rack layers; a Modem in the modem band;
	#    about one Elite per layer in the elite band; Terminals ~25% of the rest.
	var taken := {}  # id -> true for nodes with a fixed type
	for rack_layer in config.rack_layers:
		var layer: Array = graph.nodes_in_layer(rack_layer)
		var pick: Dictionary = layer[rng.randi_range(0, layer.size() - 1)]
		pick["type"] = RC.InfilNodeType.SERVER_RACK
		pick["elite"] = true
		taken[pick["id"]] = true
	var modem_candidates: Array[Dictionary] = _free_nodes(graph, config.map_modem_layers.x, config.map_modem_layers.y, taken)
	if not modem_candidates.is_empty():
		var modem: Dictionary = modem_candidates[rng.randi_range(0, modem_candidates.size() - 1)]
		modem["type"] = RC.InfilNodeType.MODEM
		taken[modem["id"]] = true
	var extra_accumulator := 0.0
	for layer_number in range(config.map_elite_layers.x, config.map_elite_layers.y + 1):
		var elites_here := config.map_elites_per_layer
		extra_accumulator += config.map_elites_per_layer * maxf(0.0, elite_frequency_pct) / 100.0
		while extra_accumulator >= 1.0 - 0.0001:
			elites_here += 1
			extra_accumulator -= 1.0
		for k in elites_here:
			var free := _free_nodes(graph, layer_number, layer_number, taken)
			if free.is_empty():
				break
			# Extra (modifier) elites never take the layer's last non-elite node.
			if k >= config.map_elites_per_layer and _non_elite_count(graph, layer_number) <= 1:
				break
			var elite: Dictionary = free[rng.randi_range(0, free.size() - 1)]
			elite["elite"] = true
			taken[elite["id"]] = true
	var rest := _free_nodes(graph, 2, layer_count - 1, taken)
	var terminal_count := roundi(rest.size() * config.map_terminal_ratio)
	for k in terminal_count:
		if rest.is_empty():
			break
		var idx := rng.randi_range(0, rest.size() - 1)
		var terminal: Dictionary = rest[idx]
		terminal["type"] = RC.InfilNodeType.TERMINAL
		rest.remove_at(idx)
	# 3. Heat per node (shown before choosing).
	for node in graph.all_nodes():
		if node["type"] == RC.InfilNodeType.SERVER_RACK:
			node["heat"] = config.rack_heat_by_tier[clampi(tier - 1, 0, config.rack_heat_by_tier.size() - 1)]
		elif node["elite"]:
			node["heat"] = config.elite_heat
	# 4. Edges: monotone (non-crossing) chains, 1-2 per node, every next-layer node covered.
	for li in layer_count - 1:
		_connect_layers(graph.layers[li], graph.layers[li + 1], rng)
	return graph


## Connects `sources` to `targets` without crossings. Source i takes targets [j, k]
## with k - j <= 1; the next source starts at k or k + 1. Coverage of every target is
## guaranteed by bounding k from below by what later sources can still cover.
static func _connect_layers(sources: Array, targets: Array, rng: RandomNumberGenerator) -> void:
	var b := targets.size()
	var j := 0
	for i in sources.size():
		var sources_left := sources.size() - i - 1
		var k_min := maxi(j, b - 1 - 2 * sources_left)
		var k_max := mini(j + 1, b - 1)
		var k := k_max if k_min > k_max else rng.randi_range(k_min, k_max)
		var next: Array[StringName] = []
		for t in range(j, k + 1):
			next.append(targets[t]["id"])
		sources[i]["next"] = next
		if sources_left > 0:
			if k + 1 <= b - 1 and (k_min > k or rng.randi_range(0, 1) == 1 or b - 1 - k >= 2 * sources_left):
				j = k + 1
			else:
				j = k


static func _non_elite_count(graph: MapGraph, layer_number: int) -> int:
	var n := 0
	for node in graph.nodes_in_layer(layer_number):
		if not node["elite"]:
			n += 1
	return n


static func _free_nodes(graph: MapGraph, from_layer: int, to_layer: int, taken: Dictionary) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for layer_number in range(from_layer, to_layer + 1):
		for node in graph.nodes_in_layer(layer_number):
			if not taken.has(node["id"]) and not node["elite"]:
				out.append(node)
	return out
