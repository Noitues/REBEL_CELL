class_name RaidVerdict
extends RefCounted
## ANIM-R4 H3 / RAID-FIX A1: a raid's one verdict, in the same words everywhere it is shown (the
## raid setup's and the interlude's forecast stamps, the playout's resolved stamp, the report, the
## forecast's tooltip). The words come from `RaidOutcome` (won / campaign_lost / breach) and
## match what `RaidResolver.apply` does: REPELLED (+N Schematics), OVERRUN (+N Heat: the raid
## is lost), BREACHED (Home fell). "CELL HOLDS" (GDD 7.2) is kept only for a REPELLED raid, as the
## report's sticker. View words only; the raid is resolved by the core and read here.

const BREACHED := "BREACHED" # TR
const CELL_HOLDS := "CELL HOLDS" # TR
const REPELLED := "REPELLED" # TR
const OVERRUN := "OVERRUN" # TR
const SCHEMATICS_GAIN := "%s SCHEMATICS" # TR
const HEAT_GAIN := "%s HEAT" # TR
const HOME_LOSS := "HOME %s" # TR
const DOWN := "%d DOWN" # TR
const TAKEN := "%d TAKEN" # TR
## The DOWN tier's hue (between the amber WARN and the HARM red).
const TIER_ORANGE_MIX := 0.5


## The verdict words for `verdict` (RaidOutcome.Verdict): translated, the word and (REPELLED /
## OVERRUN) a second line with what the raid pays or costs.
static func words(verdict: int, heat_delta: int, schematics_delta: int) -> String:
	match verdict:
		RaidOutcome.Verdict.BREACHED:
			return TranslationServer.translate(BREACHED)
		RaidOutcome.Verdict.REPELLED:
			var word := TranslationServer.translate(REPELLED)
			if schematics_delta > 0:
				word += "\n" + TranslationServer.translate(SCHEMATICS_GAIN) % TextDb.signed(schematics_delta)
			return word
	var over := TranslationServer.translate(OVERRUN)
	if heat_delta > 0:
		over += "\n" + TranslationServer.translate(HEAT_GAIN) % TextDb.signed(heat_delta)
	return over


## The losses of a resolved raid (`RaidResult.to_dict`, campaign.last_raid, or a projection's
## fields): {"lost", "home", "down", "taken"}, counted from the nodes' own outcomes (the
## words their labels and stamps show). ANIM-R5 P18: each node counts once, by its outcome: a
## node DOWN and then TAKEN in the same raid (it sits in both of the result's lists) is
## one TAKEN node, the stronger loss, everywhere (the forecast, the result, the report, the
## feed's tally); the feed still tells both of its lines as they happen.
static func losses(r: Dictionary) -> Dictionary:
	var down := 0
	var taken := 0
	var nodes: Dictionary = r.get("nodes", {})
	for id in nodes:
		match String((nodes[id] as Dictionary).get("outcome", "")):
			"down":
				down += 1
			"taken":
				taken += 1
	return {"lost": bool(r.get("campaign_lost", false)), "home": maxi(0, int(r.get("home_before", 0)) - int(r.get("home_after", 0))),
		"down": down, "taken": taken}


## The verdict of a resolved raid dictionary (`RaidResult.to_dict`, `campaign.last_raid`).
static func of_result(r: Dictionary) -> String:
	return words(RaidOutcome.verdict_of_dict(r), int(r.get("heat_delta", 0)), int(r.get("schematics_delta", 0)))


## The verdict a projection forecasts (RaidResolver.RaidResult).
static func of_projection(p: RaidResolver.RaidResult) -> String:
	return of_result(p.to_dict())


## True when the raid is REPELLED.
static func clean(r: Dictionary) -> bool:
	return RaidOutcome.verdict_of_dict(r) == RaidOutcome.Verdict.REPELLED


## `clean` for a projection.
static func clean_projection(p: RaidResolver.RaidResult) -> bool:
	return clean(p.to_dict())


## The severity tier's colour (RaidOutcome.Tier): acid clean, amber a Home loss over the config
## percent, orange a node DOWN, red a node TAKEN or Home BREACHED.
static func color_of_tier(tier: int) -> Color:
	match tier:
		RaidOutcome.Tier.AMBER:
			return Palette.WARN
		RaidOutcome.Tier.DOWN:
			return Palette.WARN.lerp(Palette.HARM, TIER_ORANGE_MIX)
		RaidOutcome.Tier.TAKEN:
			return Palette.HARM
	return Palette.CELL_ACID


## The verdict's colour: acid when all hold, pink when anything is lost.
static func color_of(is_clean: bool) -> Color:
	return Palette.CELL_ACID if is_clean else Palette.CELL_PINK


## The verdict's icon: the raid shield when all hold, home when anything is lost.
static func icon_of(is_clean: bool) -> StringName:
	return StatIcon.RAIDS if is_clean else StatIcon.HOME


## RAID-FIX A2: the stamp's colour for a projection, by severity tier (not green on 50 -> 16).
static func tier_color_projection(p: RaidResolver.RaidResult, config: CampaignConfigData) -> Color:
	return color_of_tier(RaidOutcome.project(p, config)["tier"])


## RAID-FIX A2: the stamp's colour for a resolved raid dictionary, by severity tier.
static func tier_color_result(r: Dictionary, config: CampaignConfigData) -> Color:
	return color_of_tier(RaidOutcome.of_dict(r, config)["tier"])


const IF_KILLS := "kills %d of %d" # TR
const IF_NODE := "%s > %s" # TR
const IF_HOME := "Home +%d" # TR
const IF_SAVES := "%d fewer nodes lost" # TR
const IF_NO_CHANGE := "no change: %s" # TR
const IF_OUT_OF_REACH := "the threat is out of reach" # TR
const IF_TOO_STRONG := "the threat is too strong" # TR
const IF_WRONG_LANE := "no threat comes this way" # TR


## RAID-FIX A3: `RaidOutcome.if_placed` in words of effect, one clause each, joined by ", ":
## "kills 1 of 2, TAKEN > HOLDS, Home +9", or "no change: the threat is out of reach".
## `node_word` turns a node outcome ("holds", "down", "taken", "passed") into its word.
static func if_placed_words(d: Dictionary, node_word: Callable) -> String:
	if not bool(d["changed"]):
		var reason := IF_OUT_OF_REACH
		match StringName(d["reason"]):
			RaidOutcome.REASON_TOO_STRONG:
				reason = IF_TOO_STRONG
			RaidOutcome.REASON_WRONG_LANE:
				reason = IF_WRONG_LANE
		return TranslationServer.translate(IF_NO_CHANGE) % TranslationServer.translate(reason)
	var parts := PackedStringArray()
	if int(d["kills"]) > 0:
		parts.append(TranslationServer.translate(IF_KILLS) % [int(d["kills"]), int(d["total"])])
	if String(d["node_from"]) != String(d["node_to"]):
		parts.append(TranslationServer.translate(IF_NODE) % [node_word.call(String(d["node_from"])), node_word.call(String(d["node_to"]))])
	elif int(d["nodes_saved"]) > 0:
		parts.append(TranslationServer.translate(IF_SAVES) % int(d["nodes_saved"]))
	if int(d["home_gain"]) > 0:
		parts.append(TranslationServer.translate(IF_HOME) % int(d["home_gain"]))
	if parts.is_empty():
		parts.append(words(int(d["verdict_to"]), 0, 0).get_slice("\n", 0))
	return ", ".join(parts)
