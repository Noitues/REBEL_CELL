class_name EnemyData
extends Resource
## Any combat enemy: normal, elite, boss, or satellite.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var corporation_id: StringName
@export var hp: int = 30
@export var wheel: WheelData
@export var is_elite: bool = false
@export var is_boss: bool = false
@export var cycle_reward: int = 15
@export var spawns: Array[SatelliteSpawnData] = []
## Bosses only. Order by descending hp_threshold_pct.
@export var phases: Array[BossPhaseData] = []
@export var heat_effects: Array[HeatGatedEffectData] = []
@export var art: Texture2D


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if wheel == null:
		errors.append("Enemy %s has no wheel." % id)
	else:
		errors.append_array(wheel.validate())
	if not phases.is_empty() and not is_boss:
		errors.append("Enemy %s has phases but is not a boss." % id)
	var last := 1.01
	for p in phases:
		if p == null:
			continue
		if p.hp_threshold_pct >= last:
			errors.append("Enemy %s phases must be in descending HP order." % id)
		last = p.hp_threshold_pct
		errors.append_array(p.validate())
	return errors
