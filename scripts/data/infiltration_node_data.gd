class_name InfiltrationNodeData
extends Resource
## A node on the map inside a netrun.

@export var node_type: RC.InfilNodeType = RC.InfilNodeType.ROUTER
## Campaign Heat added on entry, shown to the player before choosing.
@export var heat_cost: int = 0
@export var cycles_min: int = 0
@export var cycles_max: int = 0
## Server Racks bank this immediately on capture.
@export var schematics: int = 0
@export var has_combat: bool = true
@export var is_elite: bool = false
## Firmware, Daemons, cards or events this node can offer.
@export var loot_pool: Array[Resource] = []
