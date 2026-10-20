class_name EventCombatModsData
extends Resource
## Plan 2 EV-01: the modifiers a Terminal event puts on a combat. Used two ways: as an
## EventChoiceData.next_combat_overrides (a pending modifier stored in the run, spent over the
## next `duration_combats` completed fights) and as an EventFightData.combat_overrides (the
## fight the event opens, this fight only). Static values only: no RNG, so previews equal results.

## The enemy skips its first start-of-turn respin (the existing Freeze rule).
@export var enemy_wheel_frozen: bool = false
## Added to each enemy's passive resistance; floor 0.
@export var enemy_resistance_delta: int = 0
## Percent change of each enemy's max HP at combat creation (-15 = 15% less); floor 1 HP.
@export_range(-90, 100) var enemy_hp_pct: int = 0
## A further free nudge each turn of the fight.
@export var player_extra_free_nudges: int = 0
## Phase list and next layouts are visible from turn 1.
@export var reveal_phases: bool = false
## Added to the run tier for this fight's enemy tables (clamped 1..CampaignConfigData.event_fight_tier_cap).
@export var tier_delta: int = 0
## One more enemy (content id) joins the fight as an escort. Empty = none.
@export var extra_enemy_id: StringName = &""
## One more normal enemy of the corporation's pool joins the fight, drawn from the `events`
## stream when the choice is taken (a "?" in the preview). Not with extra_enemy_id.
@export var extra_enemy_random_normal: bool = false
## next_combat_overrides only: completed fights it lasts (a skipped node burns no charge).
@export_range(1, 9) var duration_combats: int = 1


func is_empty() -> bool:
	return not enemy_wheel_frozen and enemy_resistance_delta == 0 and enemy_hp_pct == 0 \
		and player_extra_free_nudges == 0 and not reveal_phases and tier_delta == 0 and extra_enemy_id == &"" and not extra_enemy_random_normal


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if is_empty():
		errors.append("combat_mods_empty: an EventCombatModsData that changes nothing.")
	if enemy_hp_pct <= -100:
		errors.append("combat_mods_hp_pct: enemy_hp_pct %d would leave no HP." % enemy_hp_pct)
	if player_extra_free_nudges < 0:
		errors.append("combat_mods_nudges_lt_0: player_extra_free_nudges is %d." % player_extra_free_nudges)
	if extra_enemy_random_normal and extra_enemy_id != &"":
		errors.append("combat_mods_two_extras: extra_enemy_id and extra_enemy_random_normal together.")
	if duration_combats < 1:
		errors.append("combat_mods_duration_lt_1: duration_combats is %d." % duration_combats)
	return errors
