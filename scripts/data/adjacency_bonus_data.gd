class_name AdjacencyBonusData
extends Resource
## Bonus a network node gets while linked to a node of partner_type.

@export var partner_type: RC.NetworkNodeType = RC.NetworkNodeType.RELAY
@export var effects: Array[TriggeredEffectData] = []
