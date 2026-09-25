class_name CampaignCode
extends RefCounted
## Shareable campaign codes and the daily seed (GAP_ANALYSIS P2 12). A code fixes every
## choice that shapes a campaign, so two players with the same code play the same seeded
## campaign (the core is deterministic): RC1-<corporation>-<ice>-<seed>-<home>-<class>.
## Pure: the UI reads the calendar and passes the date in.

const PREFIX := "RC1"


static func encode(campaign_seed: int, corporation_id: StringName, ice_level: int, home_variant_id: StringName, class_id: StringName) -> String:
	return "%s-%s-%d-%d-%s-%s" % [PREFIX, corporation_id, ice_level, campaign_seed, home_variant_id, class_id]


## {seed, corporation, ice, home, class} or {} when `code` is not a valid code.
static func decode(code: String) -> Dictionary:
	var parts := code.strip_edges().split("-")
	if parts.size() != 6 or parts[0] != PREFIX or not parts[2].is_valid_int() or not parts[3].is_valid_int():
		return {}
	if parts[1] == "" or parts[4] == "" or parts[5] == "":
		return {}
	return {"corporation": StringName(parts[1]), "ice": int(parts[2]), "seed": int(parts[3]),
		"home": StringName(parts[4]), "class": StringName(parts[5])}


## The code of a running campaign.
static func of(campaign: CampaignState, class_id: StringName) -> String:
	return encode(campaign.campaign_seed, campaign.corporation_id, campaign.ice_level, campaign.home_variant_id, class_id)


## The same seed for everyone on a calendar day: YYYYMMDD.
static func daily_seed(year: int, month: int, day: int) -> int:
	return year * 10000 + month * 100 + day
