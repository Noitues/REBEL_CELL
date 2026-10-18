class_name SiteText
extends RefCounted
## The one place a Site's player-facing name is decided (designer 2026-10-16: Site names are
## removed). A Site is shown by its type word; only the Central Server Site (the HQ building
## and the boss) keeps its translated name. `SiteData.display_name` stays as data.


## The Site's label: its type word ("Site", "Exploit", "Heat reduction", "HOME SERVER"), or
## the translated name for the Central Server Site. `home_site_id` marks the home Site.
static func label(site: SiteData, home_site_id: StringName = &"") -> String:
	if site == null:
		return ""
	if home_site_id != &"" and site.id == home_site_id:
		return CityMapOverlay.kind_word(CityMapOverlay.KIND_HOME)
	match site.objective:
		RC.SiteObjective.CENTRAL_SERVER:
			return TextDb.t(site, "display_name")
		RC.SiteObjective.EXPLOIT:
			return CityMapOverlay.kind_word(CityMapOverlay.KIND_EXPLOIT)
		RC.SiteObjective.HEAT_REDUCTION:
			return CityMapOverlay.kind_word(CityMapOverlay.KIND_HEAT)
	return CityMapOverlay.kind_word(CityMapOverlay.KIND_TIER)


## True when `site` keeps a proper name (the HQ / boss Site).
static func is_named(site: SiteData) -> bool:
	return site != null and site.objective == RC.SiteObjective.CENTRAL_SERVER


## `label` with the tier in front ("T2 Site") for lines that must tell two Sites apart.
static func tiered(site: SiteData, home_site_id: StringName = &"") -> String:
	if site == null:
		return ""
	if is_named(site) or (home_site_id != &"" and site.id == home_site_id):
		return label(site, home_site_id)
	return "%s %s" % [CityMapOverlay.tier_text(site.tier), label(site, home_site_id)]
