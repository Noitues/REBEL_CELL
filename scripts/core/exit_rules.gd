class_name ExitRules
extends RefCounted
## Leaving the campaign (designer ruling 2026-10-05, GDD 4.5). Abandon campaign ends it
## through the campaign's own end (`CampaignState.outcome`, read by `is_over`) with the
## ABANDONED outcome; the profile counts it as a lost campaign. (Abandon run is
## `NetrunSession.abandon`: the operative's death. Quit is a save: `RunManager.quit_game`.)
## Pure rules: no Nodes, no randomness.


## Ends `campaign` as abandoned. Refuses (a "refused" event, nothing changed) when it is
## already over or a netrun is still running (`run_active`: abandon the run first).
static func abandon_campaign(campaign: CampaignState, run_active: bool = false) -> Array[Dictionary]:
	var error := abandon_campaign_error(campaign, run_active)
	var events: Array[Dictionary] = []
	if error != "":
		events.append({"type": "refused", "text": error})
		return events
	campaign.outcome = CampaignState.Outcome.ABANDONED
	events.append({"type": "campaign_abandoned", "text": "The campaign against %s is abandoned." % String(campaign.corporation_id)})
	return events


## Why the campaign cannot be abandoned now ("" when it can).
static func abandon_campaign_error(campaign: CampaignState, run_active: bool = false) -> String:
	if campaign == null:
		return "No campaign."
	if campaign.is_over():
		return "The campaign is already over."
	if run_active:
		return "A netrun is running: abandon the run first."
	return ""


## What abandoning loses, worked out by abandoning a copy (preview == result); {} when it
## cannot be abandoned. Keys: corporation, runs (completed), operatives (living), schematics,
## sites (claimed, the home server not counted), armory, heat, ice, outcome (the copy's).
static func abandon_campaign_preview(campaign: CampaignState, run_active: bool = false) -> Dictionary:
	if abandon_campaign_error(campaign, run_active) != "":
		return {}
	var copy := campaign.duplicate_state()
	abandon_campaign(copy)
	var sites := 0
	if copy.grid != null:
		for id in copy.grid.claimed_ids():
			if id != copy.grid.home_site_id:
				sites += 1
	return {"corporation": String(copy.corporation_id), "runs": copy.runs_completed, "operatives": copy.living_operatives().size(),
		"schematics": copy.schematics, "sites": sites, "armory": copy.armory.size(), "heat": copy.heat,
		"ice": copy.ice_level, "outcome": copy.outcome}
