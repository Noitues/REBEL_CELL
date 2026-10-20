class_name EventRaidModsData
extends Resource
## Plan 2 EV-01: what a Terminal event does to the next raid. The campaign stores it
## (CampaignState.next_raid_mods) and the next raid that is projected or fought reads it; the
## raid's resolution spends it.

## Added to the raid's strength percent (RAID_STRENGTH_PCT).
@export var strength_pct: int = 0
## Waves the last wave repeats (RAID_EXTRA_WAVE), if the roll below succeeds.
@export var extra_waves: int = 0
## Chance (percent) that `extra_waves` applies. Below 100 the choice rolls the `events` stream
## once, when it is taken; a preview shows "?" for it.
@export_range(1, 100) var extra_waves_chance_pct: int = 100
## The raid setup reveals one threat route a step earlier.
@export var scout_bonus: bool = false


func is_empty() -> bool:
	return strength_pct == 0 and extra_waves == 0 and not scout_bonus


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if is_empty():
		errors.append("raid_mods_empty: an EventRaidModsData that changes nothing.")
	if extra_waves < 0:
		errors.append("raid_mods_waves_lt_0: extra_waves is %d." % extra_waves)
	if extra_waves == 0 and extra_waves_chance_pct != 100:
		errors.append("raid_mods_chance_unused: a chance with no extra_waves.")
	return errors
