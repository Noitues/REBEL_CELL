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
## Plan 2 N12 (R11, ruling Q20 follow-up; placeholder "Calibrated"): every sub-tick of the
## socketed slot reads this many tiers higher, capped at PERFECT (WheelMath.raised_tier). Works
## on every slice size; 0 = no change.
@export var tick_quality_step: int = 0
@export var triggered_effects: Array[TriggeredEffectData] = []
