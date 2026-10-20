class_name MapEditData
extends Resource
## Plan 2 EV-01 (N16 subset): one edit an event makes to the run's map. MapEditRules applies a
## list of these in order; every pick is deterministic (fewest inbound links, then node id), so
## the preview names exactly what the result changes. An edit with no valid target does nothing.

enum Op {
	## A link from the current node to a node `layer_offset` layers ahead (2 skips a layer).
	ADD_LINK,
	## Closes a non-Rack node `layer_offset` layers ahead: it can no longer be entered.
	CLOSE_NODE,
	## Turns a `convert_from` node `layer_offset` layers ahead into `convert_to`.
	CONVERT_NODE,
	## Marks the node types of `layer_count` layers, from `layer_offset` ahead, as known.
	REVEAL_TYPE,
	## The next layer is bypassed: the current node links straight to that layer's successors.
	SKIP_LAYER,
}

@export var op: Op = Op.ADD_LINK
@export_range(1, 6) var layer_offset: int = 1
## REVEAL_TYPE: layers revealed.
@export_range(1, 6) var layer_count: int = 1
## CONVERT_NODE: the new node type.
@export var convert_to: RC.InfilNodeType = RC.InfilNodeType.TERMINAL
## CONVERT_NODE: only a node of this type converts.
@export var convert_from: RC.InfilNodeType = RC.InfilNodeType.ROUTER
## ADD_LINK (to a node an earlier edit picked), CONVERT_NODE and REVEAL_TYPE act on the node
## the previous edit of the list targeted instead of picking their own.
@export var use_previous_target: bool = false


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if op == Op.CONVERT_NODE and convert_to == convert_from:
		errors.append("map_edit_convert_same: CONVERT_NODE from and to the same type.")
	if op == Op.ADD_LINK and not use_previous_target and layer_offset < 2:
		errors.append("map_edit_link_offset: ADD_LINK to the next layer (offset 1) is a link that already exists; use 2 or more.")
	if op == Op.SKIP_LAYER and layer_offset != 1:
		errors.append("map_edit_skip_offset: SKIP_LAYER bypasses the next layer only.")
	return errors
