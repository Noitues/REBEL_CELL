class_name FirmwareData
extends Resource
## Socketed into one slice. Firmware changes what that slice does.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var rarity: RC.Rarity = RC.Rarity.COMMON
@export var cycle_cost: int = 100
## Empty = fits any slice type.
@export var allowed_slice_types: Array[RC.SliceType] = []
@export var output_multiplier: float = 1.0
@export var permanent_status: RC.Status = RC.Status.NONE
## MIRROR copies the neighbour on the side you landed (both on Perfect).
## SHUNT resolves that neighbour instead, and does nothing on Perfect.
@export var neighbor_rule: RC.NeighborRule = RC.NeighborRule.NONE
@export var neighbor_multiplier: float = 1.0
@export var triggered_effects: Array[TriggeredEffectData] = []
