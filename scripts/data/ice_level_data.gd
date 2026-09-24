class_name IceLevelData
extends Resource
## One ICE difficulty level. Cumulative: level N applies all levels 1..N.

@export_range(1, 20) var level: int = 1
@export var description: String
@export var modifiers: Array[RuleModifierData] = []
