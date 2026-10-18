class_name EnemyData
extends Resource
## Any combat enemy: normal, elite, boss, or satellite.

const CONFIG_PATH := "res://content/config/campaign_config.tres"
## Float tolerance for an hp_bands zone ceiling (Vector2 stores 32-bit floats).
const HP_BAND_EPSILON := 0.0001

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var corporation_id: StringName
## Legacy base HP: used (x CampaignConfigData.enemy_hp_scale) only while hp_by_tier and
## hp_bands are empty (N2 migration fallback).
@export var hp: int = 30
## N2 (R2): starting HP at T1..T4 (4 entries), checked against the class band. A mini-boss
## has no T4 band: its 4th entry is 0 and T4 reads T3. Bosses use hp_bands instead.
@export var hp_by_tier: PackedInt32Array = PackedInt32Array()
## N2 (R2), bosses only: (ICE boss-strength zone ceiling, HP) pairs, ceilings ascending; the
## last ceiling is open-ended (>= config boss_hp_band_open_ceiling). See hp_for().
@export var hp_bands: Array[Vector2] = []
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


## N2: true when starting HP comes from hp_by_tier / hp_bands, not the legacy multiplier.
func uses_hp_table() -> bool:
	return (hp_bands if is_boss else hp_by_tier).size() > 0


## N2: authored HP at `tier` (clamped to 1..4); a 0 entry (mini-boss T4) reads the last
## non-zero tier below it. 0 when hp_by_tier is empty.
func hp_at_tier(tier: int) -> int:
	if hp_by_tier.is_empty():
		return 0
	var i := mini(CampaignConfigData.tier_index(tier), hp_by_tier.size() - 1)
	while i > 0 and hp_by_tier[i] <= 0:
		i -= 1
	return hp_by_tier[i]


## N2: boss HP for the ICE boss-strength `multiplier`: the first band whose ceiling is at
## or above it, else the last (open-ended) band. 0 when hp_bands is empty.
func hp_for(multiplier: float) -> int:
	if hp_bands.is_empty():
		return 0
	for b in hp_bands:
		if multiplier <= b.x + HP_BAND_EPSILON:
			return roundi(b.y)
	return roundi(hp_bands[hp_bands.size() - 1].y)


## N2: the R2 band class of this enemy (&"normal", &"elite", &"mini_boss_2",
## &"mini_boss_3", &"boss"). A mini-boss's phase count is its phase entries + 1, held to 2..3.
func band_class() -> StringName:
	if is_boss:
		return &"boss"
	if is_mini_boss:
		return &"mini_boss_3" if phases.size() + 1 >= 3 else &"mini_boss_2"
	return &"elite" if is_elite else &"normal"


## The class the per-class tables index (RC.EnemyClass): boss, then mini-boss, then elite.
func enemy_class() -> int:
	if is_boss:
		return RC.EnemyClass.BOSS
	if is_mini_boss:
		return RC.EnemyClass.MINI_BOSS
	if is_elite:
		return RC.EnemyClass.ELITE
	return RC.EnemyClass.NORMAL


## `config` gives the per-class phase counts (plan 2 R1) and the N2 HP bands; null reads the schema
## defaults for phases and loads the game config for the HP bands.
## Phase errors start with a reason name and carry the content id.
func validate(config: CampaignConfigData = null) -> PackedStringArray:
	var errors := PackedStringArray()
	if wheel == null:
		errors.append("Enemy %s has no wheel." % id)
	else:
		errors.append_array(wheel.validate())
	errors.append_array(_validate_phases(config if config != null else CampaignConfigData.new()))
	var band_config := config
	if band_config == null and (not hp_by_tier.is_empty() or not hp_bands.is_empty()) and ResourceLoader.exists(CONFIG_PATH):
		band_config = load(CONFIG_PATH) as CampaignConfigData
	errors.append_array(_validate_hp_table(band_config))
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


func _validate_hp_table(config: CampaignConfigData) -> PackedStringArray:
	var errors := PackedStringArray()
	if is_boss:
		if not hp_by_tier.is_empty():
			errors.append("Enemy %s is a boss: it uses hp_bands, not hp_by_tier." % id)
		var prev := -INF
		for b in hp_bands:
			if b.x <= prev:
				errors.append("Enemy %s hp_bands ceilings must ascend." % id)
				break
			prev = b.x
		for b in hp_bands:
			if roundi(b.y) <= 0:
				errors.append("Enemy %s hp_bands HP must be > 0." % id)
				break
		if not hp_bands.is_empty() and config != null and hp_bands[hp_bands.size() - 1].x < config.boss_hp_band_open_ceiling:
			errors.append("Enemy %s hp_bands must cover multiplier > last ceiling (last ceiling below %s)." % [id, config.boss_hp_band_open_ceiling])
		return errors
	if not hp_bands.is_empty():
		errors.append("Enemy %s has hp_bands but is not a boss." % id)
	if hp_by_tier.is_empty():
		return errors
	if hp_by_tier.size() != 4:
		errors.append("Enemy %s hp_by_tier must have 4 entries." % id)
		return errors
	var cls := band_class()
	for t in 4:
		var v := hp_by_tier[t]
		var band := config.hp_band(cls, t + 1) if config != null else Vector2i(-1, -1)
		if is_mini_boss and t == 3:
			if v != 0:
				errors.append("Enemy %s hp_by_tier[3] %d: mini-boss has no T4 band (leave it 0)." % [id, v])
			continue
		if v <= 0:
			errors.append("Enemy %s hp_by_tier[%d] must be > 0." % [id, t])
		elif band != Vector2i(-1, -1) and (v < band.x or v > band.y):
			errors.append("Enemy %s hp_by_tier[%d] %d outside %s band %d-%d (T%d)." % [id, t, v, _band_name(cls), band.x, band.y, t + 1])
	return errors


static func _band_name(cls: StringName) -> String:
	match cls:
		&"mini_boss_2": return "mini-boss 2-phase"
		&"mini_boss_3": return "mini-boss 3-phase"
	return String(cls)
