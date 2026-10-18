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
## Guards the final Server Rack of a netrun (designer ruling 2026-09-24); may have phases.
@export var is_mini_boss: bool = false
@export var cycle_reward: int = 15
@export var spawns: Array[SatelliteSpawnData] = []
## Bosses only. Order by descending hp_threshold_pct.
@export var phases: Array[BossPhaseData] = []
@export var heat_effects: Array[HeatGatedEffectData] = []
@export var art: Texture2D


## The class the per-class tables index (RC.EnemyClass): boss, then mini-boss, then elite.
func enemy_class() -> int:
	if is_boss:
		return RC.EnemyClass.BOSS
	if is_mini_boss:
		return RC.EnemyClass.MINI_BOSS
	if is_elite:
		return RC.EnemyClass.ELITE
	return RC.EnemyClass.NORMAL


## `config` gives the per-class phase counts (plan 2 R1); null reads the schema defaults.
## Phase errors start with a reason name and carry the content id.
func validate(config: CampaignConfigData = null) -> PackedStringArray:
	var errors := PackedStringArray()
	if wheel == null:
		errors.append("Enemy %s has no wheel." % id)
	else:
		errors.append_array(wheel.validate())
	errors.append_array(_validate_phases(config if config != null else CampaignConfigData.new()))
	return errors


func _validate_phases(config: CampaignConfigData) -> PackedStringArray:
	var errors := PackedStringArray()
	var cls := enemy_class()
	var count := phases.size() + 1  # the base phase counts, as R1's table does
	if cls < config.phase_count_min_by_class.size() and cls < config.phase_count_max_by_class.size():
		var lo := config.phase_count_min_by_class[cls]
		var hi := config.phase_count_max_by_class[cls]
		if count < lo or count > hi:
			var reason: String = ["normal_has_phases", "elite_too_many_phases", "mini_boss_phase_count", "boss_phase_count"][cls]
			errors.append("%s: Enemy %s has %d phases (base included); its class allows %d-%d." % [reason, id, count, lo, hi])
	var last := 1.0
	for p in phases:
		if p == null:
			errors.append("phase_missing: Enemy %s has an empty phase entry." % id)
			continue
		if p.hp_threshold_pct >= last:
			errors.append("threshold_order: Enemy %s phase thresholds must strictly descend (%s after %s)." % [id, p.hp_threshold_pct, last])
		last = p.hp_threshold_pct
		for problem in p.validate():
			errors.append("%s (enemy %s)" % [problem, id])
	return errors
