class_name HeatThresholdData
extends Resource
## A Heat threshold (4.2). Events fire the first time it is crossed and
## never again. Ongoing modifiers apply only while Heat >= heat.

@export_range(1, 100) var heat: int = 10
@export var kind: RC.ThresholdKind = RC.ThresholdKind.MINOR
## One-time events.
@export var event_raid: RaidData
@export var event_complications: Array[RuleModifierData] = []
## Active while at or above this threshold.
@export var ongoing_modifiers: Array[RuleModifierData] = []
@export_multiline var event_text: String
