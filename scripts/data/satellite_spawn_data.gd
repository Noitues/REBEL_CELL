class_name SatelliteSpawnData
extends Resource
## How and when an enemy launches satellites (2.9).

## An EnemyData whose wheel has slice_count 2 or 3.
@export var satellite: EnemyData
## When to spawn: ON_COMBAT_START, ON_TURN_START, etc.
@export var trigger: RC.Trigger = RC.Trigger.ON_COMBAT_START
## Spawn every N matching triggers (1 = every time).
@export var every_n: int = 1
## Enemy slot to dock on; -1 = random free slot.
@export_range(-1, 5) var dock_slot: int = -1
@export var max_active: int = 2
