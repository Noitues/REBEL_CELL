class_name MapGraph
extends RefCounted
## A netrun map (GDD 4.2, TECH_SPEC 6): layers of nodes joined by forward edges. Plain
## data with validation; the generator builds it, RunState carries it.
##
## Node dictionary keys: id (StringName), layer (1-based), index (0-based within the
## layer), type (RC.InfilNodeType), elite (bool), next (Array[StringName]), heat (int).

var layers: Array = []  # Array of Array[Dictionary], layer 1 first


func node_count() -> int:
	var n := 0
	for layer in layers:
		n += layer.size()
	return n


func layer_count() -> int:
	return layers.size()


func get_node(id: StringName) -> Dictionary:
	for layer in layers:
		for node in layer:
			if node["id"] == id:
				return node
	return {}


func nodes_in_layer(layer_number: int) -> Array:
	return layers[layer_number - 1] if layer_number >= 1 and layer_number <= layers.size() else []


func all_nodes() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for layer in layers:
		for node in layer:
			out.append(node)
	return out


func first_layer_ids() -> Array[StringName]:
	var out: Array[StringName] = []
	for node in nodes_in_layer(1):
		out.append(node["id"])
	return out


func final_node_id() -> StringName:
	var last: Array = layers[layers.size() - 1] if not layers.is_empty() else []
	return last[0]["id"] if not last.is_empty() else &""


static func make_id(layer: int, index: int) -> StringName:
	return StringName("L%dN%d" % [layer, index])


## Structural checks: layer sizes, edges only to the next layer, 1-2 edges per node,
## no crossing edges, every node reachable from layer 1 and able to reach the last
## layer, and the GDD guarantees (layer 1 Routers, Rack at each rack layer, a Modem in
## the modem band, one final node). Returns the problems found.
func validate(config: CampaignConfigData) -> PackedStringArray:
	var errors := PackedStringArray()
	if layers.size() != config.map_layers:
		errors.append("Map has %d layers, expected %d." % [layers.size(), config.map_layers])
		return errors
	for li in layers.size():
		var layer: Array = layers[li]
		var number := li + 1
		var is_last := number == layers.size()
		if is_last and layer.size() != 1:
			errors.append("Final layer must hold exactly one node, has %d." % layer.size())
		elif not is_last and (layer.size() < config.map_nodes_min or layer.size() > config.map_nodes_max):
			errors.append("Layer %d has %d nodes, expected %d-%d." % [number, layer.size(), config.map_nodes_min, config.map_nodes_max])
		var last_target := -1
		for ni in layer.size():
			var node: Dictionary = layer[ni]
			if node["id"] != make_id(number, ni):
				errors.append("Node id %s does not match its position (layer %d index %d)." % [node["id"], number, ni])
			if number == 1 and (node["type"] != RC.InfilNodeType.ROUTER or node["elite"]):
				errors.append("Layer 1 must be plain Routers (%s)." % node["id"])
			var next: Array = node["next"]
			if is_last:
				if not next.is_empty():
					errors.append("Final node has outgoing edges.")
				continue
			if next.is_empty() or next.size() > 2:
				errors.append("%s has %d edges, expected 1-2." % [node["id"], next.size()])
			var targets: Array[int] = []
			for target in next:
				var t := get_node(target)
				if t.is_empty() or t["layer"] != number + 1:
					errors.append("%s links to %s which is not in layer %d." % [node["id"], target, number + 1])
				else:
					targets.append(t["index"])
			targets.sort()
			if not targets.is_empty() and targets[0] < last_target:
				errors.append("Edges cross between layers %d and %d at %s." % [number, number + 1, node["id"]])
			if not targets.is_empty():
				last_target = targets[targets.size() - 1]
	# Reachability both ways.
	var forward := _reachable_from(first_layer_ids())
	var backward := _can_reach_final()
	for node in all_nodes():
		if not forward.has(node["id"]):
			errors.append("%s is unreachable from layer 1." % node["id"])
		if not backward.has(node["id"]):
			errors.append("%s cannot reach the final node." % node["id"])
	# Guarantees.
	for rack_layer in config.rack_layers:
		var racks := 0
		for node in nodes_in_layer(rack_layer):
			if node["type"] == RC.InfilNodeType.SERVER_RACK:
				racks += 1
		if racks != 1:
			errors.append("Layer %d has %d Server Racks, expected 1." % [rack_layer, racks])
	var modems := 0
	for layer_number in range(config.map_modem_layers.x, config.map_modem_layers.y + 1):
		for node in nodes_in_layer(layer_number):
			if node["type"] == RC.InfilNodeType.MODEM:
				modems += 1
	if modems < 1:
		errors.append("No Modem in layers %d-%d." % [config.map_modem_layers.x, config.map_modem_layers.y])
	return errors


func _reachable_from(start: Array[StringName]) -> Dictionary:
	var seen := {}
	var queue: Array[StringName] = start.duplicate()
	while not queue.is_empty():
		var id: StringName = queue.pop_front()
		if seen.has(id):
			continue
		seen[id] = true
		for n in get_node(id).get("next", []):
			queue.append(n)
	return seen


func _can_reach_final() -> Dictionary:
	var ok := {}
	var final_id := final_node_id()
	ok[final_id] = true
	for li in range(layers.size() - 2, -1, -1):
		for node in layers[li]:
			for n in node["next"]:
				if ok.has(n):
					ok[node["id"]] = true
					break
	return ok


func duplicate_graph() -> MapGraph:
	return from_dict(to_dict())


func to_dict() -> Dictionary:
	var out := []
	for layer in layers:
		var l := []
		for node in layer:
			var nxt := []
			for n in node["next"]:
				nxt.append(String(n))
			l.append({"id": String(node["id"]), "layer": node["layer"], "index": node["index"], "type": node["type"],
				"elite": node["elite"], "next": nxt, "heat": node["heat"]})
		out.append(l)
	return {"layers": out}


static func from_dict(d: Dictionary) -> MapGraph:
	var g := MapGraph.new()
	for layer in d.get("layers", []):
		var l := []
		for node in layer:
			var nxt: Array[StringName] = []
			for n in node.get("next", []):
				nxt.append(StringName(String(n)))
			l.append({"id": StringName(String(node["id"])), "layer": int(node["layer"]), "index": int(node["index"]),
				"type": int(node["type"]), "elite": bool(node["elite"]), "next": nxt, "heat": int(node.get("heat", 0))})
		g.layers.append(l)
	return g


func graph_hash() -> int:
	return hash(JSON.stringify(to_dict()))
