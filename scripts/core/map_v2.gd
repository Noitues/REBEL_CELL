class_name MapV2
extends RefCounted
## RG-01: the v2 pass of the netrun map generator. A v2 graph is a valid v1 graph (built with the
## v1 draws) whose Terminal slots may become REST, WORKSHOP or CACHE nodes. Pure: the `map`
## stream passed in is the only randomness, and every placement draws a fixed count (a chance
## roll is always drawn, a pick only when a candidate exists), so the draw order is part of the
## contract. Ties break by layer, then node index (the candidate order).


## Places the v2 node kinds on `graph` (already version 2) for `tier`.
static func place(graph: MapGraph, tier: int, config: CampaignConfigData, rng: RandomNumberGenerator) -> void:
	pass


## Free Terminal slots (non-elite, plain TERMINAL) in layers `from_layer`..`to_layer`, in layer then index order.
static func terminals(graph: MapGraph, from_layer: int, to_layer: int) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for layer_number in range(maxi(2, from_layer), mini(graph.layer_count() - 1, to_layer) + 1):
		for node in graph.nodes_in_layer(layer_number):
			if int(node["type"]) == RC.InfilNodeType.TERMINAL and not node["elite"]:
				out.append(node)
	return out
