class_name HeatThresholdData
extends Resource
## A Heat threshold (4.2). Events fire the first time it is crossed and
## never again. Ongoing modifiers apply only while Heat >= heat.

## ANIM-R4 H5: names the threshold for its text's translation key
## (`HeatThresholdData.<id>.event_text`, TextDb); "heat_<level>" by convention.
@export var id: StringName = &""
@export_range(1, 100) var heat: int = 10
@export var kind: RC.ThresholdKind = RC.ThresholdKind.MINOR
## One-time events.
@export var event_raid: RaidData
@export var event_complications: Array[RuleModifierData] = []
## Active while at or above this threshold.
@export var ongoing_modifiers: Array[RuleModifierData] = []
## What crossing it brings, as whole sentences (the Heat banner's sub-line and tooltip).
@export_multiline var event_text: String
