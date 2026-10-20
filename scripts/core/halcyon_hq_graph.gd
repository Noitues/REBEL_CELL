class_name HalcyonHqGraph
extends RefCounted
## Plan 2 WH-20 (drafts/hq/halcyon.md, v2 themes/v2/halcyon.md): the Halcyon HQ netrun, THE LONG
## WAY ROUND, as a MapGraph. 12 route layers and a vault layer (the Panopticon boss); layer 12 is
## the Antechamber (the Halcyon mini-boss). Each node carries an azimuth `az` (degrees) for the
## Eye's gaze. Annex rooms are extra non-fight nodes in their layer (rest, cache, or the Power Room
## that holds Cut the Power). Climb edges skip layers: the target lists its sources in
## `climb_from`. Pure: the same config, phase and stream state give the same graph; every number is
## config. The graph is rebuilt (the stream advances) until every layer keeps an open node for the
## launch phase.


## Builds the layers, kinds, azimuths, edges and climbs, drawing from `rng` (stream `hq_graph`).
static func build(config: CampaignConfigData, rng: RandomNumberGenerator) -> MapGraph:
	var g := MapGraph.new()
	var count := config.halcyon_hq_layer_kinds.size()
	for li in count:
		var layer_no := li + 1
		var kinds: Array[String] = []
		for k in String(config.halcyon_hq_layer_kinds[li]).split(","):
			kinds.append(k.strip_edges())
		for ai in config.halcyon_hq_annex_layers.size():
			if config.halcyon_hq_annex_layers[ai] == layer_no and ai < config.halcyon_hq_annex_kinds.size():
				kinds.append("A:" + String(config.halcyon_hq_annex_kinds[ai]))
		# Fisher-Yates over the kinds (always draws, so the stream position never depends on the table).
		for i in range(kinds.size() - 1, 0, -1):
			var j := rng.randi_range(0, i)
			var tmp := kinds[i]
			kinds[i] = kinds[j]
			kinds[j] = tmp
		var jitter := rng.randi_range(-config.halcyon_hq_face_jitter_deg, config.halcyon_hq_face_jitter_deg)
		var face := config.halcyon_hq_layer_face_deg[li] if li < config.halcyon_hq_layer_face_deg.size() else 0
		var layer := []
		for i in kinds.size():
			var node := _make_node(layer_no, i, kinds[i], config)
			var off := roundi((float(i) - float(kinds.size() - 1) / 2.0) * config.halcyon_hq_node_spread_deg)
			node["az"] = posmod(face + jitter + off, 360)
			layer.append(node)
		g.layers.append(layer)
	_link(g, rng)
	_add_climbs(g, config, rng)
	return g


static func _make_node(layer_no: int, index: int, kind: String, config: CampaignConfigData) -> Dictionary:
	var code := kind
	var annex := kind.begins_with("A:")
	if annex:
		code = kind.substr(2)
	var node := {"id": MapGraph.make_id(layer_no, index), "layer": layer_no, "index": index, "type": RC.InfilNodeType.ROUTER,
		"elite": false, "next": [] as Array[StringName], "heat": 0}
	match code:
		"R":
			pass
		"E":
			node["elite"] = true
			node["heat"] = config.elite_heat
		"T":
			node["type"] = RC.InfilNodeType.TERMINAL
		"M":
			node["type"] = RC.InfilNodeType.MAINFRAME
		"B", "rest":
			node["type"] = RC.InfilNodeType.TERMINAL
			node["rest"] = true
		"C", "cache":
			node["type"] = RC.InfilNodeType.TERMINAL
			node["cache"] = true
		"power":
			node["type"] = RC.InfilNodeType.TERMINAL
			node["power"] = true
		"K", "X", "V":
			node["type"] = RC.InfilNodeType.SERVER_RACK
			node["elite"] = true
			node["heat"] = config.rack_heat_by_tier[config.rack_heat_by_tier.size() - 1]
			if code == "X":
				node["mini_boss"] = true
			elif code == "V":
				node["boss"] = true
	if annex:
		node["annex"] = true
	return node


static func _link(g: MapGraph, rng: RandomNumberGenerator) -> void:
	for li in g.layers.size() - 1:
		var src: Array = g.layers[li]
		var dst: Array = g.layers[li + 1]
		var n := src.size()
		var m := dst.size()
		var incoming := {}
		for i in n:
			var pos := 0 if n == 1 else (i * (m - 1) * 2 + (n - 1)) / (2 * (n - 1))
			var second := rng.randi_range(0, 1) == 1
			var picks: Array[int] = [pos]
			if second and pos + 1 < m:
				picks.append(pos + 1)
			elif second and pos > 0:
				picks.append(pos - 1)
			picks.sort()
			for j in picks:
				src[i]["next"].append(dst[j]["id"])
				incoming[j] = true
		for j in m:
			if incoming.has(j):
				continue
			var i := 0 if m == 1 else (j * (n - 1) * 2 + (m - 1)) / (2 * (m - 1))
			src[i]["next"].append(dst[j]["id"])
			(src[i]["next"] as Array).sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))


## Climb edges: origin layer -> target layer, a random node each (drawn from `rng`).
static func _add_climbs(g: MapGraph, config: CampaignConfigData, rng: RandomNumberGenerator) -> void:
	for ci in mini(config.halcyon_hq_climb_origins.size(), config.halcyon_hq_climb_targets.size()):
		var o := config.halcyon_hq_climb_origins[ci]
		var t := config.halcyon_hq_climb_targets[ci]
		if o < 1 or t > g.layers.size() or t <= o + 1:
			continue
		var from_node: Dictionary = g.layers[o - 1][rng.randi_range(0, g.layers[o - 1].size() - 1)]
		var to_node: Dictionary = g.layers[t - 1][rng.randi_range(0, g.layers[t - 1].size() - 1)]
		if (from_node["next"] as Array).has(to_node["id"]):
			continue
		from_node["next"].append(to_node["id"])
		var cf: Array[StringName] = to_node.get("climb_from", [] as Array[StringName])
		cf.append(from_node["id"])
		to_node["climb_from"] = cf


## Whether the edge `from_id` -> `node` is a climb edge.
static func is_climb(node: Dictionary, from_id: StringName) -> bool:
	return from_id != &"" and (node.get("climb_from", []) as Array).has(from_id)


## The HQ validator: structure and the Eye's reachability for `phase`. Empty = valid.
static func validate(g: MapGraph, config: CampaignConfigData, phase: int) -> PackedStringArray:
	var errors := PackedStringArray()
	var count := config.halcyon_hq_layer_kinds.size()
	if g.layers.size() != count:
		errors.append("HQ graph has %d layers, expected %d." % [g.layers.size(), count])
		return errors
	if g.layers[count - 1].size() != 1 or not bool(g.layers[count - 1][0].get("boss", false)):
		errors.append("The last layer must hold the one boss.")
	if count >= 2 and (g.layers[count - 2].size() != 1 or not bool(g.layers[count - 2][0].get("mini_boss", false))):
		errors.append("The Antechamber must hold the one mini-boss.")
	var rests := 0
	var power := 0
	for li in g.layers.size():
		for ni in g.layers[li].size():
			var node: Dictionary = g.layers[li][ni]
			if node["id"] != MapGraph.make_id(li + 1, ni):
				errors.append("Node id %s does not match its position." % node["id"])
			if li < g.layers.size() - 1 and (node["next"] as Array).is_empty():
				errors.append("%s has no way out." % node["id"])
			if bool(node.get("rest", false)):
				rests += 1
			if bool(node.get("power", false)):
				power += 1
	if rests < 1:
		errors.append("The HQ has no rest room.")
	if power != 1:
		errors.append("The HQ must hold exactly one Power Room (has %d)." % power)
	var firsts: Array = []
	for first in g.layers[0]:
		firsts.append(first["id"])
	var forward := _reach(g, firsts, true)
	var backward := _reach(g, [g.final_node_id()], false)
	for node in g.all_nodes():
		if int(node["layer"]) == 1:
			continue
		if not forward.has(node["id"]):
			errors.append("%s is unreachable." % node["id"])
		if not backward.has(node["id"]):
			errors.append("%s cannot reach the boss." % node["id"])
	errors.append_array(eye_errors(g, config, phase))
	return errors


## Rule 15: with the Eye at launch `phase`, the boss is reachable by an open path on the climb-free
## route, and every layer after a climb target keeps an open node under that climb's step offset,
## at the normal beam width (Alert 0, awake).
static func eye_errors(g: MapGraph, config: CampaignConfigData, phase: int) -> PackedStringArray:
	var errors := PackedStringArray()
	var pn := config.hq_gaze_step_per_node
	var open := func(node: Dictionary, step: int) -> bool:
		return EyeRules.enterable(EyeRules.node_state(node, phase, step, 0, false, config))
	# Climb-free path.
	var live := {}
	for node in g.layers[0]:
		if open.call(node, 0):
			live[node["id"]] = true
	for li in range(1, g.layers.size()):
		var next_live := {}
		for node in g.layers[li - 1]:
			if not live.has(node["id"]):
				continue
			for nid in node["next"]:
				var target := g.get_node(nid)
				if int(target["layer"]) != li + 1 or is_climb(target, node["id"]):
					continue
				if open.call(target, li * pn):
					next_live[nid] = true
		live = next_live
		if live.is_empty():
			errors.append("Layer %d has no open node on the climb-free path (phase %d)." % [li + 1, phase])
			return errors
	# Each climb: every layer from the target on keeps an open node at the shifted step.
	var extra := config.hq_gaze_step_per_climb - pn
	for ci in mini(config.halcyon_hq_climb_origins.size(), config.halcyon_hq_climb_targets.size()):
		var o := config.halcyon_hq_climb_origins[ci]
		var t := config.halcyon_hq_climb_targets[ci]
		if t > g.layers.size():
			continue
		for l in range(t, g.layers.size() + 1):
			var step := o * pn + extra + (l - t) * pn
			var any := false
			for node in g.layers[l - 1]:
				if open.call(node, step):
					any = true
			if not any:
				errors.append("Layer %d has no open node after the climb from layer %d (phase %d)." % [l, o, phase])
	return errors


## Builds and validates; the stream advances once per attempt, so a failed attempt is replaced from
## the next values (deterministic). Up to config.halcyon_hq_max_attempts tries.
static func generate(config: CampaignConfigData, rng: RandomNumberGenerator, phase: int) -> MapGraph:
	var g: MapGraph = null
	for attempt in config.halcyon_hq_max_attempts:
		g = build(config, rng)
		if validate(g, config, phase).is_empty():
			return g
	push_error("HalcyonHqGraph: no valid graph after %d attempts." % config.halcyon_hq_max_attempts)
	return g


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
