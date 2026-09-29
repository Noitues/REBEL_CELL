class_name RaidVerdict
extends RefCounted
## ANIM-R4 H3: a raid's one verdict, in the same words everywhere it is shown (the raid
## setup's and the interlude's forecast stamps, the playout's resolved stamp, the report's
## stamp, the forecast's tooltip). "ALL HOLD" only when the raid costs nothing (home loses no
## integrity and no node is Disabled or Seized); otherwise it names the losses, one line
## each ("HOME -5", "1 DISABLED", "1 SEIZED"), in the words the nodes' own labels and stamps
## use; "CAMPAIGN LOST" when home falls. There is no "HOME HIT": home's loss is its number,
## as on the map's banner ("HOME -5 · HOLDS"). View words only; the raid is resolved by the
## core (RaidResolver) and read here.

const LOST := "CAMPAIGN LOST" # TR
const ALL_HOLD := "ALL HOLD" # TR
const HOME_LOSS := "HOME %s" # TR
const DISABLED := "%d DISABLED" # TR
const SEIZED := "%d SEIZED" # TR


## The verdict for a raid where the campaign is lost (`lost`), home loses `home_lost`
## integrity and `disabled` / `seized` nodes fall: translated, a line per loss.
static func words(lost: bool, home_lost: int, disabled: int, seized: int) -> String:
	if lost:
		return TranslationServer.translate(LOST)
	var lines := PackedStringArray()
	if home_lost > 0:
		lines.append(TranslationServer.translate(HOME_LOSS) % TextDb.signed(-home_lost))
	if disabled > 0:
		lines.append(TranslationServer.translate(DISABLED) % disabled)
	if seized > 0:
		lines.append(TranslationServer.translate(SEIZED) % seized)
	if lines.is_empty():
		return TranslationServer.translate(ALL_HOLD)
	return "\n".join(lines)


## The losses of a resolved raid (`RaidResult.to_dict`, campaign.last_raid, or a projection's
## fields): {"lost", "home", "disabled", "seized"}, counted from the nodes' own outcomes (the
## words their labels and stamps show). ANIM-R5 P18: each node counts once, by its outcome: a
## node Disabled and then Seized in the same raid (it sits in both of the result's lists) is
## one SEIZED node, the stronger loss, everywhere (the forecast, the result, the report, the
## feed's tally); the feed still tells both of its lines as they happen.
static func losses(r: Dictionary) -> Dictionary:
	var disabled := 0
	var seized := 0
	var nodes: Dictionary = r.get("nodes", {})
	for id in nodes:
		match String((nodes[id] as Dictionary).get("outcome", "")):
			"disabled":
				disabled += 1
			"seized":
				seized += 1
	return {"lost": bool(r.get("campaign_lost", false)), "home": maxi(0, int(r.get("home_before", 0)) - int(r.get("home_after", 0))),
		"disabled": disabled, "seized": seized}


## The verdict of a resolved raid (see `losses`).
static func of_result(r: Dictionary) -> String:
	var l := losses(r)
	return words(l["lost"], l["home"], l["disabled"], l["seized"])


## The verdict a projection forecasts (RaidResolver.RaidResult).
static func of_projection(p: RaidResolver.RaidResult) -> String:
	return of_result(_dict(p))


## True when the raid costs nothing: the verdict is ALL HOLD.
static func clean(r: Dictionary) -> bool:
	var l := losses(r)
	return not bool(l["lost"]) and int(l["home"]) == 0 and int(l["disabled"]) == 0 and int(l["seized"]) == 0


## `clean` for a projection.
static func clean_projection(p: RaidResolver.RaidResult) -> bool:
	return clean(_dict(p))


## The verdict's colour: acid when all hold, pink when anything is lost.
static func color_of(is_clean: bool) -> Color:
	return Palette.CELL_ACID if is_clean else Palette.CELL_PINK


## The verdict's icon: the raid shield when all hold, home when anything is lost.
static func icon_of(is_clean: bool) -> StringName:
	return StatIcon.RAIDS if is_clean else StatIcon.HOME


static func _dict(p: RaidResolver.RaidResult) -> Dictionary:
	return {"campaign_lost": p.campaign_lost, "home_before": p.home_before, "home_after": p.home_after, "nodes": p.nodes}
