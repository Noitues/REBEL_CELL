class_name SolaceHqGraph
extends RefCounted
## Plan 2 WH-10 (drafts/hq/solace.md, D10): the Solace HQ netrun, THE GENOME CORE, as a MapGraph.
## A ladder of two towers, WARD (index 0) and BILLING (index 1): layer 1 is the Clinic Gate, then
## `solace_hq_rungs` rungs of two rooms each (layers 2..rungs+1), then the crown (the boss).
## From a room the operative goes UP (same tower, next rung) or ACROSS (the other tower, next
## rung; the target lists its ACROSS sources in `across_from`, and NetrunSession charges
## `bloom_pace_cross_milli` for entering by one). Pure: the same config and stream state give
## the same graph; every number is config.

const TOWER_WARD := "ward"
const TOWER_BILLING := "billing"
## Order of the kind weights in `solace_hq_ward_weights` / `solace_hq_billing_weights`.
enum Kind { FIGHT, REST, EVENT, ELITE, SHOP }


## Builds the ladder, drawing the room kinds from `rng` (stream `hq_graph`, made with
## `RngStreams.make_stream(seed, RngStreams.HQ_GRAPH_STREAM)`).
static func build(config: CampaignConfigData, rng: RandomNumberGenerator) -> MapGraph:
	var g := MapGraph.new()
	var rungs := config.solace_hq_rungs
	g.layers.append([_node(1, 0, RC.InfilNodeType.ROUTER, false, config)])
	for r in range(1, rungs + 1):
		var layer := []
		for t in 2:
			var kind := _draw_kind(config, rng, r, t)
			layer.append(_room(r + 1, t, kind, r, config))
		g.layers.append(layer)
	var crown := _node(rungs + 2, 0, RC.InfilNodeType.SERVER_RACK, true, config)
	crown["boss"] = true
	crown["tower"] = TOWER_WARD
	g.layers.append([crown])
	# Edges. Gate to both first rooms; rung r room to both rooms of rung r+1 (UP, then ACROSS);
	# the last rung's rooms to the crown.
	g.layers[0][0]["next"] = [MapGraph.make_id(2, 0), MapGraph.make_id(2, 1)] as Array[StringName]
	for r in range(1, rungs + 1):
		var layer_no := r + 1
		for t in 2:
			var src: Dictionary = g.layers[layer_no - 1][t]
			if r == rungs:
				src["next"] = [crown["id"]] as Array[StringName]
				continue
			var up := MapGraph.make_id(layer_no + 1, t)
			var across := MapGraph.make_id(layer_no + 1, 1 - t)
			src["next"] = [up, across] as Array[StringName]
			var target: Dictionary = g.layers[layer_no][1 - t]
			var from: Array[StringName] = target.get("across_from", [] as Array[StringName])
			from.append(src["id"])
			target["across_from"] = from
	return g


## The HQ validator: returns the problems found (empty = valid).
static func validate(g: MapGraph, config: CampaignConfigData) -> PackedStringArray:
	var errors := PackedStringArray()
	var rungs := config.solace_hq_rungs
	if g.layers.size() != rungs + 2:
		errors.append("HQ ladder has %d layers, expected %d." % [g.layers.size(), rungs + 2])
		return errors
	if g.layers[0].size() != 1:
		errors.append("The Clinic Gate layer must hold one node.")
	if g.layers[rungs + 1].size() != 1 or not bool(g.layers[rungs + 1][0].get("boss", false)):
		errors.append("The last layer must hold the one boss crown.")
	for li in g.layers.size():
		var layer: Array = g.layers[li]
		var is_rung := li >= 1 and li <= rungs
		if is_rung and layer.size() != 2:
			errors.append("Rung layer %d has %d rooms, expected 2." % [li + 1, layer.size()])
		for ni in layer.size():
			var node: Dictionary = layer[ni]
			if node["id"] != MapGraph.make_id(li + 1, ni):
				errors.append("Node id %s does not match its position." % node["id"])
			if is_rung and node.get("tower", "") != (TOWER_WARD if ni == 0 else TOWER_BILLING):
				errors.append("%s is on the wrong tower." % node["id"])
			var next: Array = node["next"]
			if li == g.layers.size() - 1:
				if not next.is_empty():
					errors.append("The crown has outgoing edges.")
				continue
			var expected: Array[StringName] = []
			if li == 0:
				expected = [MapGraph.make_id(2, 0), MapGraph.make_id(2, 1)]
			elif li == rungs:
				expected = [g.layers[rungs + 1][0]["id"]]
			else:
				expected = [MapGraph.make_id(li + 2, ni), MapGraph.make_id(li + 2, 1 - ni)]
			if next != expected:
				errors.append("%s has edges %s, expected %s." % [node["id"], next, expected])
			if bool(node.get("across", false)):
				errors.append("%s carries a node-wide across flag; ACROSS is an edge (across_from)." % node["id"])
		# across_from: the other tower's room of the previous rung, on rungs 2..rungs.
		if is_rung:
			for ni in layer.size():
				var want: Array[StringName] = []
				if li >= 2:
					want = [MapGraph.make_id(li, 1 - ni)]
				var have: Array = layer[ni].get("across_from", [])
				if have != want:
					errors.append("%s across_from is %s, expected %s." % [layer[ni]["id"], have, want])
	# Reachability both ways (the ladder has no dead end).
	var forward := _reach(g, [g.layers[0][0]["id"]], true)
	var backward := _reach(g, [g.final_node_id()], false)
	for node in g.all_nodes():
		if not forward.has(node["id"]):
			errors.append("%s is unreachable from the gate." % node["id"])
		if not backward.has(node["id"]):
			errors.append("%s cannot reach the crown." % node["id"])
	# Guarantees: rung 1 is fights, the mini-boss rung's rooms are mini-bosses, every
	# configured Ward rest rung has its rest, and the ladder has at least one rest.
	for node in g.nodes_in_layer(2):
		if node["type"] != RC.InfilNodeType.ROUTER or node["elite"]:
			errors.append("Rung 1 room %s must be a plain fight." % node["id"])
	var mb := config.solace_hq_mini_boss_rung
	if mb < 1 or mb > rungs:
		errors.append("Mini-boss rung %d is outside 1..%d." % [mb, rungs])
	else:
		for node in g.nodes_in_layer(mb + 1):
			if not bool(node.get("mini_boss", false)):
				errors.append("%s should hold the mini-boss." % node["id"])
	var rests := 0
	for node in g.all_nodes():
		if bool(node.get("rest", false)):
			rests += 1
	for r in config.solace_hq_ward_rest_rungs:
		if r >= 1 and r <= rungs and not bool(g.layers[r][0].get("rest", false)):
			errors.append("Ward room of rung %d should be a rest." % r)
	if rests < 1:
		errors.append("The ladder has no rest room.")
	return errors


## Builds and validates; the stream is advanced once per attempt, so a failed attempt is
## replaced from the next values (deterministic). Up to `max_attempts` tries.
static func generate(config: CampaignConfigData, rng: RandomNumberGenerator, max_attempts: int = 50) -> MapGraph:
	var g: MapGraph = null
	for attempt in max_attempts:
		g = build(config, rng)
		if validate(g, config).is_empty():
			return g
	push_error("SolaceHqGraph: no valid ladder after %d attempts." % max_attempts)
	return g


static func _node(layer: int, index: int, type: int, elite: bool, config: CampaignConfigData) -> Dictionary:
	var heat := 0
	if type == RC.InfilNodeType.SERVER_RACK:
		heat = config.rack_heat_by_tier[config.rack_heat_by_tier.size() - 1]
	elif elite:
		heat = config.elite_heat
	return {"id": MapGraph.make_id(layer, index), "layer": layer, "index": index, "type": type,
		"elite": elite, "next": [] as Array[StringName], "heat": heat}


static func _room(layer: int, tower: int, kind: Kind, rung: int, config: CampaignConfigData) -> Dictionary:
	var room: Dictionary
	if rung == config.solace_hq_mini_boss_rung:
		room = _node(layer, tower, RC.InfilNodeType.SERVER_RACK, true, config)
		room["mini_boss"] = true
	else:
		match kind:
			Kind.ELITE:
				room = _node(layer, tower, RC.InfilNodeType.ROUTER, true, config)
			Kind.EVENT:
				room = _node(layer, tower, RC.InfilNodeType.TERMINAL, false, config)
			Kind.SHOP:
				room = _node(layer, tower, RC.InfilNodeType.MAINFRAME, false, config)
			Kind.REST:
				room = _node(layer, tower, RC.InfilNodeType.TERMINAL, false, config)
				room["rest"] = true
			_:
				room = _node(layer, tower, RC.InfilNodeType.ROUTER, false, config)
	room["tower"] = TOWER_WARD if tower == 0 else TOWER_BILLING
	return room


## The kind of the room on tower `tower` (0 Ward, 1 Billing) at `rung`. Rung 1 is fights; the
## configured Ward rest rungs are rests. Always draws once (a fixed rung still consumes its
## roll), so the stream position never depends on the fixed table.
static func _draw_kind(config: CampaignConfigData, rng: RandomNumberGenerator, rung: int, tower: int) -> Kind:
	var weights := config.solace_hq_ward_weights if tower == 0 else config.solace_hq_billing_weights
	var total := 0
	for w in weights:
		total += maxi(0, w)
	var roll := rng.randi_range(0, maxi(0, total - 1))
	var picked := Kind.FIGHT
	var acc := 0
	for i in weights.size():
		acc += maxi(0, weights[i])
		if roll < acc:
			picked = i as Kind
			break
	if rung == 1:
		return Kind.FIGHT
	if tower == 0 and config.solace_hq_ward_rest_rungs.has(rung):
		return Kind.REST
	return picked


static func _reach(g: MapGraph, start: Array, forward: bool) -> Dictionary:
	var seen := {}
	var queue: Array = start.duplicate()
	while not queue.is_empty():
		var id: StringName = queue.pop_front()
		if seen.has(id):
			continue
		seen[id] = true
		if forward:
			for n in g.get_node(id).get("next", []):
				queue.append(n)
		else:
			for node in g.all_nodes():
				if node["next"].has(id):
					queue.append(node["id"])
	return seen
