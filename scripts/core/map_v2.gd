class_name MapV2
extends RefCounted
## RG-01: the v2 pass of the netrun map generator. A v2 graph is a valid v1 graph (built with the
## v1 draws) whose Terminal slots may become REST, WORKSHOP or CACHE nodes. Pure: the `map`
## stream passed in is the only randomness, and every placement draws a fixed count (a chance
## roll is always drawn, a pick only when a candidate exists), so the draw order is part of the
## contract. Ties break by layer, then node index (the candidate order).


## Places the v2 node kinds on `graph` (already version 2) for `tier`.
static func place(graph: MapGraph, tier: int, config: CampaignConfigData, rng: RandomNumberGenerator) -> void:
	_place_rest(graph, tier, config, rng)
	_place_workshop(graph, tier, config, rng)
	_place_cache(graph, config, rng)


## RG-02: the guaranteed REST (layers `rest_guaranteed_layers`, chance `node_weight_rest`), then an
## extra one (chance by tier, layers `rest_extra_layers`), at most `rest_max_per_run`, one per layer.
## Draws: roll, pick (if candidates), roll, pick (if rolled and candidates).
static func _place_rest(graph: MapGraph, tier: int, config: CampaignConfigData, rng: RandomNumberGenerator) -> void:
	var placed := 0
	var roll := rng.randi_range(1, 100)
	if roll <= config.node_weight_rest and config.rest_max_per_run > 0:
		# No free slot in the guaranteed layers: the wider extra span, so the guarantee holds.
		if _convert(graph, RC.InfilNodeType.REST, config.rest_guaranteed_layers, rng, true) 				or _convert(graph, RC.InfilNodeType.REST, config.rest_extra_layers, rng, true):
			placed += 1
	var pct := config.rest_extra_chance_pct_by_tier[clampi(tier - 1, 0, config.rest_extra_chance_pct_by_tier.size() - 1)] if not config.rest_extra_chance_pct_by_tier.is_empty() else 0
	roll = rng.randi_range(1, 100)
	if roll <= pct and placed < config.rest_max_per_run:
		_convert(graph, RC.InfilNodeType.REST, config.rest_extra_layers, rng, false)


## RG-03: one WORKSHOP from `workshop_min_tier` up (chance `node_weight_workshop` percent), on a Terminal in
## `workshop_layers`, never in a layer that holds a Mainframe. Draws: roll, pick (if rolled and a candidate exists).
static func _place_workshop(graph: MapGraph, tier: int, config: CampaignConfigData, rng: RandomNumberGenerator) -> void:
	var roll := rng.randi_range(1, 100)
	if tier >= config.workshop_min_tier and roll <= config.node_weight_workshop:
		_convert(graph, RC.InfilNodeType.WORKSHOP, config.workshop_layers, rng, false, RC.InfilNodeType.MAINFRAME)


## RG-04: one CACHE (chance `node_weight_cache` percent) on a Terminal in `cache_layers`.
## Draws: roll, pick (if rolled and a candidate exists).
static func _place_cache(graph: MapGraph, config: CampaignConfigData, rng: RandomNumberGenerator) -> void:
	var roll := rng.randi_range(1, 100)
	if roll <= config.node_weight_cache:
		_convert(graph, RC.InfilNodeType.CACHE, config.cache_layers, rng, false)


## Turns one candidate in layers `span` into `type`: a free Terminal, else (when `router_fallback`) a plain
## Router, in a layer that holds none of `type` yet (and none of `avoid_type` when given). Draws one pick when a
## candidate exists. True when placed.
static func _convert(graph: MapGraph, type: int, span: Vector2i, rng: RandomNumberGenerator, router_fallback: bool, avoid_type: int = -1) -> bool:
	var taken_layers := {}
	for n in graph.all_nodes():
		if int(n["type"]) == type or (avoid_type >= 0 and int(n["type"]) == avoid_type):
			taken_layers[int(n["layer"])] = true
	var cands := terminals(graph, span.x, span.y)
	if cands.is_empty() and router_fallback:
		cands = routers(graph, span.x, span.y)
	var open: Array[Dictionary] = []
	for c in cands:
		if not taken_layers.has(int(c["layer"])):
			open.append(c)
	if open.is_empty():
		return false
	var pick := open[rng.randi_range(0, open.size() - 1)]
	pick["type"] = type
	return true


## Free Terminal slots (non-elite, plain TERMINAL) in layers `from_layer`..`to_layer`, in layer then index order.
static func terminals(graph: MapGraph, from_layer: int, to_layer: int) -> Array[Dictionary]:
	return _of_type(graph, RC.InfilNodeType.TERMINAL, from_layer, to_layer)


## Plain (non-elite) Routers in the span, in layer then index order.
static func routers(graph: MapGraph, from_layer: int, to_layer: int) -> Array[Dictionary]:
	return _of_type(graph, RC.InfilNodeType.ROUTER, from_layer, to_layer)


static func _of_type(graph: MapGraph, type: int, from_layer: int, to_layer: int) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for layer_number in range(maxi(2, from_layer), mini(graph.layer_count() - 1, to_layer) + 1):
		for node in graph.nodes_in_layer(layer_number):
			if int(node["type"]) == type and not node["elite"]:
				out.append(node)
	return out
