class_name MapEditRules
extends RefCounted
## Plan 2 EV-01 (N16 subset): applies an event's MapEditData list to a run map. Pure: the map,
## the closed and revealed node lists are passed in. Every pick is deterministic (fewest
## inbound links, then node id), so `preview` (the same edits on copies) names exactly what
## `apply` changes. It does not touch the run graph generator or the node kinds.


## Applies `edits` in order to `map`, `closed` and `revealed` (mutating them) from the node
## `current_id`. Returns one entry per edit: {"op": MapEditData.Op, "ok": bool, "from": id,
## "to": id, "nodes": ids touched, "text": a short line for the preview and the log}.
static func apply(map: MapGraph, current_id: StringName, closed: Array[StringName], revealed: Array[StringName], edits: Array[MapEditData]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var previous: StringName = &""
	var current := map.get_node(current_id) if map != null else {}
	for edit in edits:
		if edit == null:
			continue
		var r := {"op": edit.op, "ok": false, "from": current_id, "to": &"", "nodes": [] as Array[StringName], "text": ""}
		if current.is_empty():
			out.append(r)
			continue
		match edit.op:
			MapEditData.Op.ADD_LINK:
				_add_link(map, current, closed, edit, previous, r)
			MapEditData.Op.CLOSE_NODE:
				_close_node(map, current, closed, edit, r)
			MapEditData.Op.CONVERT_NODE:
				_convert_node(map, current, closed, edit, previous, r)
			MapEditData.Op.REVEAL_TYPE:
				_reveal(map, current, revealed, edit, previous, r)
			MapEditData.Op.SKIP_LAYER:
				_skip_layer(map, current, closed, r)
		if r["to"] != &"":
			previous = r["to"]
		out.append(r)
	return out


## The result `apply` would give, computed on copies (nothing passed in changes).
static func preview(map: MapGraph, current_id: StringName, closed: Array[StringName], revealed: Array[StringName], edits: Array[MapEditData]) -> Array[Dictionary]:
	return apply(map.duplicate_graph(), current_id, closed.duplicate(), revealed.duplicate(), edits)


## Inbound link count of `id` (links from any node of the map).
static func inbound(map: MapGraph, id: StringName) -> int:
	var n := 0
	for node in map.all_nodes():
		if (node["next"] as Array).has(id):
			n += 1
	return n


## Candidates of the layer `offset` ahead of `current`, ordered fewest inbound first, then id.
static func _ordered(map: MapGraph, candidates: Array) -> Array:
	var out := candidates.duplicate()
	var counts := {}
	for node in out:
		counts[node["id"]] = inbound(map, node["id"])
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		if counts[a["id"]] != counts[b["id"]]:
			return counts[a["id"]] < counts[b["id"]]
		return String(a["id"]) < String(b["id"]))
	return out


static func _add_link(map: MapGraph, current: Dictionary, closed: Array[StringName], edit: MapEditData, previous: StringName, r: Dictionary) -> void:
	var target: Dictionary = {}
	if edit.use_previous_target:
		target = map.get_node(previous) if previous != &"" else {}
	else:
		var layer := int(current["layer"]) + edit.layer_offset
		var cands: Array = []
		for node in map.nodes_in_layer(layer):
			if not closed.has(node["id"]) and not (current["next"] as Array).has(node["id"]):
				cands.append(node)
		var ordered := _ordered(map, cands)
		target = ordered[0] if not ordered.is_empty() else {}
	if target.is_empty() or int(target["layer"]) <= int(current["layer"]) or closed.has(target["id"]):
		r["text"] = "NO LINK"
		return
	r["to"] = target["id"]
	if (current["next"] as Array).has(target["id"]):
		r["text"] = "LINK EXISTS: %s" % target["id"]
		return
	(current["next"] as Array).append(target["id"])
	r["ok"] = true
	r["text"] = "LINK ADDED: %s" % target["id"]


static func _close_node(map: MapGraph, current: Dictionary, closed: Array[StringName], edit: MapEditData, r: Dictionary) -> void:
	var layer := int(current["layer"]) + edit.layer_offset
	var nodes := map.nodes_in_layer(layer)
	var open := 0
	for node in nodes:
		if not closed.has(node["id"]):
			open += 1
	if open <= 1:
		r["text"] = "NO NODE CLOSED"
		return
	var cands: Array = []
	for node in nodes:
		if closed.has(node["id"]) or int(node["type"]) == RC.InfilNodeType.SERVER_RACK:
			continue
		cands.append(node)
	for node in _ordered(map, cands):
		closed.append(node["id"])
		if _final_reachable(map, current, closed):
			r["ok"] = true
			r["to"] = node["id"]
			r["nodes"] = [node["id"]] as Array[StringName]
			r["text"] = "NODE CLOSED: %s" % node["id"]
			return
		closed.erase(node["id"])
	r["text"] = "NO NODE CLOSED"


static func _convert_node(map: MapGraph, current: Dictionary, closed: Array[StringName], edit: MapEditData, previous: StringName, r: Dictionary) -> void:
	var target: Dictionary = {}
	if edit.use_previous_target:
		target = map.get_node(previous) if previous != &"" else {}
		if not target.is_empty() and int(target["type"]) != edit.convert_from:
			target = {}
	else:
		var cands: Array = []
		for node in map.nodes_in_layer(int(current["layer"]) + edit.layer_offset):
			if not closed.has(node["id"]) and int(node["type"]) == edit.convert_from:
				cands.append(node)
		# Prefer a node the current one already links to (no link needed), then fewest inbound, then id.
		var linked: Array = []
		for node in cands:
			if (current["next"] as Array).has(node["id"]):
				linked.append(node)
		var ordered := _ordered(map, linked if not linked.is_empty() else cands)
		target = ordered[0] if not ordered.is_empty() else {}
	if target.is_empty():
		r["text"] = "NO NODE CONVERTED"
		return
	target["type"] = edit.convert_to
	target["elite"] = false
	target["heat"] = 0
	r["ok"] = true
	r["to"] = target["id"]
	r["nodes"] = [target["id"]] as Array[StringName]
	r["text"] = "NODE CONVERTED: %s" % target["id"]


static func _reveal(map: MapGraph, current: Dictionary, revealed: Array[StringName], edit: MapEditData, previous: StringName, r: Dictionary) -> void:
	var ids: Array[StringName] = []
	if edit.use_previous_target:
		if previous != &"":
			ids.append(previous)
	else:
		for k in edit.layer_count:
			for node in map.nodes_in_layer(int(current["layer"]) + edit.layer_offset + k):
				ids.append(node["id"])
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ids:
		if not revealed.has(id):
			revealed.append(id)
	r["nodes"] = ids
	r["ok"] = not ids.is_empty()
	if edit.use_previous_target and not ids.is_empty():
		r["text"] = "TYPE REVEALED: %s" % ids[0]
	else:
		r["text"] = "TYPES REVEALED" if not ids.is_empty() else "NO TYPES REVEALED"


## Bypasses the next layer: the current node links to the successors of its open next nodes.
## Refused when that layer holds a Rack (or is the last one) or leaves no successor.
static func _skip_layer(map: MapGraph, current: Dictionary, closed: Array[StringName], r: Dictionary) -> void:
	var layer := int(current["layer"]) + 1
	if layer >= map.layer_count():
		r["text"] = "NO SKIP"
		return
	var successors: Array[StringName] = []
	for id in current["next"]:
		var node := map.get_node(id)
		if node.is_empty() or closed.has(id):
			continue
		if int(node["type"]) == RC.InfilNodeType.SERVER_RACK:
			r["text"] = "NO SKIP"
			return
		for n in node["next"]:
			if not successors.has(n) and not closed.has(n):
				successors.append(n)
	if successors.is_empty():
		r["text"] = "NO SKIP"
		return
	successors.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	current["next"] = successors
	r["ok"] = true
	r["to"] = successors[0]
	r["nodes"] = successors
	r["text"] = "LAYER SKIPPED"


## Whether the final node can still be reached from `current` through open nodes.
static func _final_reachable(map: MapGraph, current: Dictionary, closed: Array[StringName]) -> bool:
	var final_id := map.final_node_id()
	var seen := {}
	var queue: Array[StringName] = []
	for id in current["next"]:
		if not closed.has(id):
			queue.append(id)
	while not queue.is_empty():
		var id: StringName = queue.pop_front()
		if seen.has(id):
			continue
		seen[id] = true
		if id == final_id:
			return true
		for n in map.get_node(id).get("next", []):
			if not closed.has(n):
				queue.append(n)
	return false
