class_name HeatGatedEffectData
extends Resource
## Extra enemy behaviour that is active only while campaign Heat >= min_heat.

@export_range(0, 100) var min_heat: int = 25
@export var effects: Array[TriggeredEffectData] = []
## Slice triggers fire only on the enemy's ATTACK and CRIT slices ("each of its attacks").
@export var offensive_slices_only: bool = false
