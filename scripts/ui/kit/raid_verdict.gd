class_name RaidVerdict
extends RefCounted
## ANIM-R4 H3: a raid's one verdict, in the same words everywhere it is shown (the raid
## setup's and the interlude's forecast stamps, the playout's resolved stamp, the report's
## stamp, the forecast's tooltip). "CELL HOLDS" only when the raid costs nothing (home loses no
## integrity and no node is DOWN or TAKEN); otherwise it names the losses, one line
## each ("HOME -5", "1 DOWN", "1 TAKEN"), in the words the nodes' own labels and stamps
## use; "BREACHED" when home falls. There is no "HOME HIT": home's loss is its number,
## as on the map's banner ("HOME -5 · HOLDS"). View words only; the raid is resolved by the
## core (RaidResolver) and read here.

const BREACHED := "BREACHED" # TR
const CELL_HOLDS := "CELL HOLDS" # TR
const HOME_LOSS := "HOME %s" # TR
const DOWN := "%d DOWN" # TR
const TAKEN := "%d TAKEN" # TR


## The verdict for a raid where the campaign is lost (`lost`), home loses `home_lost`
## integrity and `down` / `taken` nodes fall: translated, a line per loss.
static func words(lost: bool, home_lost: int, down: int, taken: int) -> String:
	if lost:
		return TranslationServer.translate(BREACHED)
	var lines := PackedStringArray()
	if home_lost > 0:
		lines.append(TranslationServer.translate(HOME_LOSS) % TextDb.signed(-home_lost))
	if down > 0:
		lines.append(TranslationServer.translate(DOWN) % down)
	if taken > 0:
		lines.append(TranslationServer.translate(TAKEN) % taken)
	if lines.is_empty():
		return TranslationServer.translate(CELL_HOLDS)
	return "\n".join(lines)


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


## The verdict of a resolved raid (see `losses`).
static func of_result(r: Dictionary) -> String:
	var l := losses(r)
	return words(l["lost"], l["home"], l["down"], l["taken"])


## The verdict a projection forecasts (RaidResolver.RaidResult).
static func of_projection(p: RaidResolver.RaidResult) -> String:
	return of_result(_dict(p))


## True when the raid costs nothing: the verdict is CELL HOLDS.
static func clean(r: Dictionary) -> bool:
	var l := losses(r)
	return not bool(l["lost"]) and int(l["home"]) == 0 and int(l["down"]) == 0 and int(l["taken"]) == 0


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
