class_name HubCoreData
extends Resource
## Center zone. Always applies; grants passives, never actions.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var passive_effects: Array[TriggeredEffectData] = []
## Player classes: the signature Perfect hook. Leave empty for enemies.
@export var perfect_hook: TriggeredEffectData
## Hub-sourced spin resistance. Switched off by HUB_BREACH.
@export var hub_resistance: int = 0
## Botnet and similar classes: how many drones DEPLOY may keep docked on the wheel.
@export var max_drones: int = 0
## The drone DEPLOY slices and DEPLOY_DRONE effects create (an EnemyData whose wheel
## has 2-3 slices). Null = the wheel cannot deploy.
@export var drone: EnemyData
## Botnet: the operative's drones survive between the combats of a netrun.
@export var drones_persist: bool = false
## Rigger: added to the class max RAM.
@export var max_ram_bonus: int = 0
## Ghost: this many nudges on enemy wheels each turn ignore resistance.
@export var free_resistance_nudges: int = 0
