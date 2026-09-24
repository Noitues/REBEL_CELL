class_name ProfileUnlockData
extends Resource
## A permanent Profile-layer unlock (3.3).

@export var id: StringName
@export var kind: RC.UnlockKind = RC.UnlockKind.CLASS
@export var display_name: String
@export_multiline var description: String
## Schematics spent from the current campaign. 0 = free once requirements met.
@export var schematic_cost: int = 80
## ClassData, CorporationData, HomeServerVariantData, NetworkNodeData, etc.
@export var unlocks: Resource
## -1 = none. e.g. REBEL_CELL: every other corporation cleared at ICE 10.
@export var requires_all_corporations_at_ice: int = -1
@export var requires_unlock_ids: Array[StringName] = []
