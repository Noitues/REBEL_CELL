class_name SliceData
extends Resource
## A wheel slice type: Attack, Defend, Crit, Miss, etc.

@export var id: StringName
@export var display_name: String
@export var slice_type: RC.SliceType = RC.SliceType.ATTACK
@export var target_rule: RC.TargetRule = RC.TargetRule.POINTER
## Damage for ATTACK/CRIT, block for DEFEND/SHIELD, drone count for DEPLOY.
@export var base_output: int = 0
@export var extra_effects: Array[TriggeredEffectData] = []
@export var icon: Texture2D
