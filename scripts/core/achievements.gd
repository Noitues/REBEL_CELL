class_name Achievements
extends RefCounted
## Achievements (gap analysis 2.5): definitions in code, evaluated over the profile and
## the current campaign. Pure: check() returns the ids newly earned; the caller records
## them. "final_final" (GDD 8.5): REBEL_CELL and every other corporation at ICE 20.

const DEFS: Array[Dictionary] = [
	{"id": &"first_blood", "title": "First Blood", "text": "Complete a netrun."},
	{"id": &"banked", "title": "Banked", "text": "Capture ten Server Racks."},
	{"id": &"breach", "title": "Breach", "text": "Win a campaign."},
	{"id": &"clean_hands", "title": "Clean Hands", "text": "Win a campaign without losing an operative."},
	{"id": &"ice_5", "title": "Average Is a Lie", "text": "Win a campaign at ICE 5 or higher."},
	{"id": &"ice_10", "title": "Cold Storage", "text": "Win a campaign at ICE 10 or higher."},
	{"id": &"purge_survivor", "title": "Purge Survivor", "text": "Win a campaign after the Heat reached 100."},
	{"id": &"wall", "title": "The Wall", "text": "Repel twenty raids."},
	{"id": &"perfectionist", "title": "Perfectionist", "text": "Land five hundred Perfects."},
	{"id": &"final_final", "title": "Final Final", "text": "Clear REBEL_CELL at ICE 20 after every other corporation at ICE 20."},
]


## Default for config.final_final_ice when no config is passed.
const FINAL_FINAL_ICE := 20


static func definition(id: StringName) -> Dictionary:
	for d in DEFS:
		if d["id"] == id:
			return d
	return {}


## Ids earned by the profile (and the campaign just concluded, if any) that it does not
## have yet, in definition order.
static func check(profile: ProfileState, campaign: CampaignState = null, corporation_ids: Array = [], final_final_ice: int = FINAL_FINAL_ICE, config: CampaignConfigData = null) -> Array[StringName]:
	var out: Array[StringName] = []
	if config == null:
		config = CampaignConfigData.new()  # schema defaults
	var won := campaign != null and campaign.outcome == CampaignState.Outcome.WON
	var earned := {
		&"first_blood": profile.runs_completed >= 1,
		&"banked": int(profile.stats.get("racks", 0)) >= config.achievement_racks,
		&"breach": profile.campaigns_won >= 1,
		&"clean_hands": won and campaign.deaths == 0,
		&"ice_5": won and campaign.ice_level >= config.achievement_ice_low,
		&"ice_10": won and campaign.ice_level >= config.achievement_ice_high,
		&"purge_survivor": won and campaign.thresholds_fired.has(_top_threshold(config)),
		&"wall": profile.raids_won >= config.achievement_raids,
		&"perfectionist": int(profile.stats.get("perfects", 0)) >= config.achievement_perfects,
		&"final_final": _final_final(profile, corporation_ids, final_final_ice),
	}
	for d in DEFS:
		var id: StringName = d["id"]
		if bool(earned.get(id, false)) and not profile.achievements.has(id):
			out.append(id)
	return out


## GDD 8.5 "final final": REBEL_CELL cleared at ICE 20 and every other corporation in
## `corporation_ids` (the non-generated ones) cleared at ICE 20.
static func _final_final(profile: ProfileState, corporation_ids: Array, ice: int) -> bool:
	if corporation_ids.is_empty() or profile.best_ice_for(RebelCellBuilder.ID) < ice:
		return false
	for id in corporation_ids:
		if profile.best_ice_for(StringName(String(id))) < ice:
			return false
	return true


## The highest Heat threshold (the Purge); heat_max when the config lists none.
static func _top_threshold(config: CampaignConfigData) -> int:
	var top := -1
	for t in config.heat_thresholds:
		if t != null:
			top = maxi(top, t.heat)
	return top if top >= 0 else config.heat_max
