class_name HomeServerVariantData
extends Resource
## A home server layout (Profile unlock).

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var core: NetworkNodeData
@export var internal_nodes: Array[NetworkNodeData] = []
## Pairs of indices into [core] + internal_nodes (0 = core).
@export var internal_links: Array[Vector2i] = []


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if core == null or core.node_type != RC.NetworkNodeType.HOME_SERVER:
		errors.append("Home server %s needs a HOME_SERVER core node." % id)
	var count := internal_nodes.size() + 1
	for l in internal_links:
		if l.x < 0 or l.y < 0 or l.x >= count or l.y >= count or l.x == l.y:
			errors.append("Home server %s has an invalid link %s." % [id, l])
	return errors
