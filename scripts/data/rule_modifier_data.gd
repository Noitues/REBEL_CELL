class_name RuleModifierData
extends Resource
## A numeric rule change, shared by ICE levels and Heat thresholds.
## PCT types use percentage points (10 = +10%); others are flat values.

@export var type: RC.RuleModifierType = RC.RuleModifierType.HEAT_GAIN_PCT
@export var value: float = 0.0
