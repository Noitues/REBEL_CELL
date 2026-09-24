class_name ThreatData
extends Resource
## A corporate threat moving along Grid links during a raid.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var integrity: int = 10
@export var damage: int = 5
@export var edges_per_step: int = 1
@export var routing: RC.ThreatRouting = RC.ThreatRouting.SHORTEST_TO_HOME
## Can freeze or alter links before the raid starts (7.1).
@export var freezes_edges: bool = false
@export var alters_edges: bool = false
## Extra integrity per 10 campaign Heat, as a fraction (0.1 = +10%).
@export var heat_integrity_scaling: float = 0.0
