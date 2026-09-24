class_name EventChoiceData
extends Resource

@export var label: String
@export_multiline var result_text: String
@export var cycle_cost: int = 0
@export var hp_cost: int = 0
@export var effects: Array[EffectData] = []
## Card, Firmware, Daemon, DefenseAsset or ClassData (rescued operative).
@export var reward: Resource
