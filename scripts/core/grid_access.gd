class_name GridAccess
extends RefCounted
## W3-GRID (C4): whether a Site can be run from the campaign's territory now, and when not,
## why and which Site(s) to clear first. Reads the same rules the launch uses
## (CampaignRules.launchable_sites / is_patrol), so the map's "reachable" flag equals what
## JACK IN allows. Pure.

const WHY_OPEN := "open"
const WHY_HOME := "home"
const WHY_BREACH := "breach"
const WHY_FROM := "from"
const WHY_FAR := "far"


## {reachable: bool, why: WHY_*, prereqs: Array[StringName] (sorted Site ids linked to it,
## to clear first), exploits_needed: int, exploits_held: int}. `reachable` is true for a
## Site a run can start at now (a corporate Site next to your territory, a TAKEN Site to
## reclaim, a patrol).
static func site_access(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, site: SiteData) -> Dictionary:
	var prereqs: Array[StringName] = []
	var out := {"reachable": false, "why": WHY_FAR, "prereqs": prereqs,
		"exploits_needed": config.min_exploits_for_breach, "exploits_held": campaign.exploits.size()}
	if site.id == campaign.grid.home_site_id:
		out["why"] = WHY_HOME
		return out
	var allowed := CampaignRules.is_patrol(campaign, site)
	for s in CampaignRules.launchable_sites(campaign, corp, config):
		if s.id == site.id:
			allowed = true
	if allowed:
		out["reachable"] = true
		out["why"] = WHY_OPEN
		return out
	if site.objective == RC.SiteObjective.CENTRAL_SERVER and campaign.exploits.size() < config.min_exploits_for_breach:
		out["why"] = WHY_BREACH
		return out
	for s in corp.city_grid.sites:
		if s != null and (s.links.has(site.id) or (s.locked_links.has(site.id) and campaign.grid.is_link_open(s.id, site.id))):
			prereqs.append(s.id)
	prereqs.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	out["why"] = WHY_FROM if not prereqs.is_empty() else WHY_FAR
	return out
