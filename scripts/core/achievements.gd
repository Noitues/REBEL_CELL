class_name Achievements
extends RefCounted
## Achievements (gap analysis 2.5): definitions in code, evaluated over the profile and
## the current campaign. Pure: check() returns the ids newly earned; the caller records
## them. "final_final" (GDD 8.5) needs REBEL_CELL and stays unreachable until it exists.

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


static func definition(id: StringName) -> Dictionary:
	for d in DEFS:
		if d["id"] == id:
			return d
	return {}


## Ids earned by the profile (and the campaign just concluded, if any) that it does not
## have yet, in definition order.
static func check(profile: ProfileState, campaign: CampaignState = null) -> Array[StringName]:
	var out: Array[StringName] = []
	var won := campaign != null and campaign.outcome == CampaignState.Outcome.WON
	var earned := {
		&"first_blood": profile.runs_completed >= 1,
		&"banked": int(profile.stats.get("racks", 0)) >= 10,
		&"breach": profile.campaigns_won >= 1,
		&"clean_hands": won and campaign.deaths == 0,
		&"ice_5": won and campaign.ice_level >= 5,
		&"ice_10": won and campaign.ice_level >= 10,
		&"purge_survivor": won and campaign.thresholds_fired.has(100),
		&"wall": profile.raids_won >= 20,
		&"perfectionist": int(profile.stats.get("perfects", 0)) >= 500,
		&"final_final": false,
	}
	for d in DEFS:
		var id: StringName = d["id"]
		if bool(earned.get(id, false)) and not profile.achievements.has(id):
			out.append(id)
	return out
