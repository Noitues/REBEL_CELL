class_name HqCompoundLayout
extends RefCounted
## ART-8 8p: places an HQ run's nodes on the corporation's compound (bible 4.7) under the
## current HQ-run rules. Pure: same layout + map = same positions.
##
## A node of the map's final layer is the Central Server; this covers today's breach run
## (one node) and a full run map (GDD 4.2). A node of layer L with index i in a layer of n
## nodes takes slot round(i * (slots - 1) / (n - 1)) of row L (n = 1: the middle slot),
## so a smaller layer spreads over the row and the generator's index order (its
## non-crossing edges) keeps the slots' left-to-right order.


## The compound position of `node_id` in `graph`, or null when the layout has no slot for
## it (an unknown node, or more layers or nodes than the layout's rows).
static func position_of(layout: HqCompoundLayoutData, graph: MapGraph, node_id: StringName) -> Variant:
	if layout == null or graph == null:
		return null
	var node := graph.get_node(node_id)
	if node.is_empty():
		return null
	var layer := int(node["layer"])
	if layer == graph.layer_count():
		return layout.central_server
	if layer < 1 or layer > layout.layer_rows():
		return null
	var n: int = graph.nodes_in_layer(layer).size()
	var slot := slot_for(int(node["index"]), n, layout.slots_per_layer)
	if slot < 0:
		return null
	return layout.slot_position(layer, slot)


## The row slot of node `index` in a layer of `count` nodes, with `slots` slots a row; -1
## when the layer does not fit the row.
static func slot_for(index: int, count: int, slots: int) -> int:
	if count < 1 or count > slots or index < 0 or index >= count:
		return -1
	if count == 1:
		return floori(float(slots - 1) / 2.0)
	return roundi(float(index) * float(slots - 1) / float(count - 1))


## Every node of `graph` -> its compound position (Vector3), in node-id order; nodes
## without a slot are left out.
static func positions(layout: HqCompoundLayoutData, graph: MapGraph) -> Dictionary:
	var ids: Array[StringName] = []
	for node in graph.all_nodes():
		ids.append(node["id"])
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	var out := {}
	for id in ids:
		var p: Variant = position_of(layout, graph, id)
		if p != null:
			out[id] = p
	return out
