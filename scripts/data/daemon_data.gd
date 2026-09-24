class_name DaemonData
extends Resource
## Run-wide rule (relic). Simple Daemons are pure data; rule-breaking
## ones point custom_handler at a script that hooks the CombatEngine.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var rarity: RC.Rarity = RC.Rarity.UNCOMMON
@export var cycle_cost: int = 200
@export var triggered_effects: Array[TriggeredEffectData] = []
@export var custom_handler: Script
@export var icon: Texture2D
