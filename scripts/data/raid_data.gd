class_name RaidData
extends Resource
## A raid template. Strength scales with Heat; reward depends on trigger.

@export var id: StringName
@export var display_name: String
@export var trigger_source: RC.RaidTriggerSource = RC.RaidTriggerSource.HEAT_THRESHOLD
@export var waves: Array[RaidWaveData] = []
@export var schematic_reward: int = 10
@export_multiline var warning_text: String
## Corporation this raid belongs to (empty = shared). With `replaces`, a corporation's
## raid stands in for a shared raid id (the Heat-threshold raids in the config).
@export var corporation_id: StringName = &""
@export var replaces: StringName = &""
