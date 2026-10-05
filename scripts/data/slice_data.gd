class_name SliceData
extends Resource
## A wheel slice type: Attack, Defend, Crit, Null, etc.

@export var id: StringName
@export var display_name: String
@export var slice_type: RC.SliceType = RC.SliceType.SHIM
@export var target_rule: RC.TargetRule = RC.TargetRule.POINTER
## Damage for SHIM/OVERFLOW, block for DEFRAG/SANDBOX, drone count for TROJAN.
@export var base_output: int = 0
@export var extra_effects: Array[TriggeredEffectData] = []
@export var icon: Texture2D
