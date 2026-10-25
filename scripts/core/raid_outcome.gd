class_name RaidOutcome
extends RefCounted
## RAID-FIX A: the one place a raid's verdict and outcome are decided. Pure: it reads a
## `RaidResolver.RaidResult` (a projection or a played raid; they are the same object) and
## the config, so the forecast chip, the playout stamp and the report all say what
## `RaidResolver.apply` does (preview == result). Words live in `RaidVerdict` (TextDb keys).

## The raid's verdict (designer R3, D28): CELL_HOLDS (Home survives) or BREACHED (Home fell: the
## campaign is lost). How well the Cell held is the `Tier`; the consequence is the Heat and
## Schematics delta. A CLEAN defense (`RaidResult.won`) gains Heat and Schematics; damage gains no Heat (D27).
## CITY_LOST (Solace tide, R-E): INFECTED cards outnumber healthy cards; a campaign loss apart from BREACHED.
enum Verdict { CELL_HOLDS, BREACHED, CITY_LOST }

## Severity tiers, mildest first: a clean defense, any Home loss (amber), a node DOWN (orange), a
## node TAKEN or Home BREACHED (red). A damaged CELL HOLDS is never CLEAN.
enum Tier { CLEAN, AMBER, DOWN, TAKEN }

## Why a placed asset changes nothing (see `if_placed`).
const REASON_OUT_OF_REACH := &"out_of_reach"
const REASON_TOO_STRONG := &"too_strong"
const REASON_WRONG_LANE := &"wrong_lane"

## The verdict of a raid with this flag (RaidResult.campaign_lost).
static func verdict_of(campaign_lost: bool) -> Verdict:
	return Verdict.BREACHED if campaign_lost else Verdict.CELL_HOLDS


## The verdict of a Solace tide raid from the state's `lost` word (see SolaceTideState): "" holds, "BREACHED" (HOME 0),
## "CITY_LOST" (INFECTED outnumber healthy cards).
static func verdict_of_tide(lost_word: String) -> Verdict:
	match lost_word:
		"BREACHED":
			return Verdict.BREACHED
		"CITY_LOST":
			return Verdict.CITY_LOST
	return Verdict.CELL_HOLDS


## The verdict of a `RaidResult`.
static func verdict_of_result(r: RaidResolver.RaidResult) -> Verdict:
	return verdict_of(r.campaign_lost)


## The verdict of a raid dictionary (`RaidResult.to_dict`, `campaign.last_raid`).
static func verdict_of_dict(r: Dictionary) -> Verdict:
	return verdict_of(bool(r.get("campaign_lost", false)))


## The nodes DOWN and TAKEN in a `nodes` map, each node once by its own outcome (a node DOWN and
## then TAKEN is one TAKEN node): {"down": int, "taken": int}.
static func node_losses(nodes: Dictionary) -> Dictionary:
	var down := 0
	var taken := 0
	for id in nodes:
		match String((nodes[id] as Dictionary).get("outcome", "")):
			"down":
				down += 1
			"taken":
				taken += 1
	return {"down": down, "taken": taken}


## Per-node outcome data for the visuals: an Array of {"id": StringName, "outcome": "holds" | "down" | "taken",
## "before": int, "after": int} (integrity before and after the raid), sorted by node id.
static func node_outcomes(nodes: Dictionary) -> Array[Dictionary]:
	var ids: Array = nodes.keys()
	ids.sort_custom(func(a, b) -> bool: return String(a) < String(b))
	var out: Array[Dictionary] = []
	for id in ids:
		var n: Dictionary = nodes[id]
		out.append({"id": StringName(id), "outcome": String(n.get("outcome", "holds")),
			"before": int(n.get("before", 0)), "after": int(n.get("after", 0))})
	return out


## The severity tier of a raid dictionary (see `Tier`).
static func tier_of_dict(r: Dictionary, _config: CampaignConfigData = null) -> Tier:
	var l := node_losses(r.get("nodes", {}))
	if bool(r.get("campaign_lost", false)) or int(l["taken"]) > 0:
		return Tier.TAKEN
	if int(l["down"]) > 0:
		return Tier.DOWN
	var before := int(r.get("home_before", 0))
	var lost := before - int(r.get("home_after", 0))
	if lost > 0:
		return Tier.AMBER
	return Tier.CLEAN


## The whole outcome of a `RaidResult` as a dictionary: "verdict" (Verdict), "tier" (Tier),
## "home_before", "home_after", "home_delta" (<= 0), "down", "taken" (node counts),
## "heat_delta", "schematics_delta" (what `RaidResolver.apply` adds), "threats_killed",
## "threats_total", "nodes" (see `node_outcomes`), "clean" (a clean defense: Heat + Schematics). The forecast for a setup equals the result of playing it.
static func project(r: RaidResolver.RaidResult, config: CampaignConfigData) -> Dictionary:
	var d := r.to_dict()
	var l := node_losses(r.nodes)
	return {"verdict": verdict_of_result(r), "tier": tier_of_dict(d, config),
		"home_before": r.home_before, "home_after": r.home_after, "home_delta": r.home_after - r.home_before,
		"down": int(l["down"]), "taken": int(l["taken"]),
		"heat_delta": r.heat_delta, "schematics_delta": r.schematics_delta,
		"threats_killed": r.threats_destroyed, "threats_total": r.threats_total,
		"nodes": node_outcomes(r.nodes), "clean": r.won}


## The outcome of a raid dictionary already played (`campaign.last_raid`), the same keys as `project`.
static func of_dict(r: Dictionary, config: CampaignConfigData) -> Dictionary:
	var l := node_losses(r.get("nodes", {}))
	var before := int(r.get("home_before", 0))
	var after := int(r.get("home_after", 0))
	return {"verdict": verdict_of_dict(r), "tier": tier_of_dict(r, config),
		"home_before": before, "home_after": after, "home_delta": after - before,
		"down": int(l["down"]), "taken": int(l["taken"]),
		"heat_delta": int(r.get("heat_delta", 0)), "schematics_delta": int(r.get("schematics_delta", 0)),
		"threats_killed": int(r.get("threats_destroyed", 0)), "threats_total": int(r.get("threats_total", 0)),
		"nodes": node_outcomes(r.get("nodes", {})), "clean": bool(r.get("won", false))}


## IF PLACED in effect: what placing `asset_id` on `site` changes, `now` being the projection
## without it and `then` the projection with it. Returns {"changed": bool, "kills": int
## (extra threats killed), "total": int, "node_from"/"node_to" (the site's outcomes, "" when it is
## not in the network), "verdict_from"/"verdict_to" (Verdict), "home_gain": int (Home integrity
## kept), "nodes_saved" (fewer nodes DOWN or TAKEN, may be negative), "reason": StringName (when nothing changed: why the asset did nothing)}.
static func if_placed(now: RaidResolver.RaidResult, then: RaidResolver.RaidResult, site: StringName, asset_id: StringName) -> Dictionary:
	var from_node := String((now.nodes.get(String(site), {}) as Dictionary).get("outcome", ""))
	var to_node := String((then.nodes.get(String(site), {}) as Dictionary).get("outcome", ""))
	var kills := then.threats_destroyed - now.threats_destroyed
	var home_gain := then.home_after - now.home_after
	var v_from := verdict_of_result(now)
	var v_to := verdict_of_result(then)
	var changed := kills != 0 or from_node != to_node or home_gain != 0 or v_from != v_to \
		or now.taken.size() != then.taken.size() or now.down.size() != then.down.size()
	var out := {"changed": changed, "kills": kills, "total": then.threats_total, "node_from": from_node, "node_to": to_node,
		"verdict_from": v_from, "verdict_to": v_to, "home_gain": home_gain, "reason": &"",
		"nodes_saved": (now.taken.size() + now.down.size()) - (then.taken.size() + then.down.size())}
	if not changed:
		out["reason"] = _no_change_reason(now, then, site, asset_id)
	return out


## Why an asset on `site` changed nothing: it fired but the threats are too strong; it never
## got a shot though a threat passed the node (out of reach); or no threat route touches the node.
static func _no_change_reason(now: RaidResolver.RaidResult, then: RaidResolver.RaidResult, site: StringName, asset_id: StringName) -> StringName:
	if _shots(then, site, asset_id) > _shots(now, site, asset_id):
		return REASON_TOO_STRONG
	for e in then.events:
		if e.get("type", "") == "move" and (StringName(e.get("to", "")) == site or StringName(e.get("from", "")) == site):
			return REASON_OUT_OF_REACH
	return REASON_WRONG_LANE


static func _shots(r: RaidResolver.RaidResult, site: StringName, asset_id: StringName) -> int:
	var n := 0
	for e in r.events:
		if e.get("type", "") == "shot" and StringName(e.get("site", "")) == site and StringName(e.get("asset", "")) == asset_id:
			n += 1
	return n


## RAID-VIS F3 (GDD 7.2: "the summary shows DOWN/TAKEN nodes, repair costs and new entry points"): what a
## played raid left on the Grid, read from the campaign AFTER `RaidResolver.apply`:
## "down": [{"id", "cost"}] (nodes this raid put DOWN with their repair cost, `CampaignRules.repair_cost`),
## "taken": [ids] (Sites this raid took), "entries": [ids] (TAKEN Sites next to the territory: each is
## a raid entry point from now on, `RaidResolver.default_entry_sites`), all sorted by id.
static func aftermath(campaign: CampaignState, grid_data: CityGridData, config: CampaignConfigData, lookup: ContentLookup) -> Dictionary:
	var down: Array[Dictionary] = []
	var taken: Array[StringName] = []
	var entries: Array[StringName] = []
	var grid := campaign.grid
	for o in node_outcomes(campaign.last_raid.get("nodes", {})):
		var id: StringName = o["id"]
		match String(o["outcome"]):
			"down":
				if grid.is_claimed(id) and int(grid.site(id).get("condition", GridState.Condition.OK)) == GridState.Condition.DOWN:
					down.append({"id": id, "cost": CampaignRules.repair_cost(campaign, config, lookup, id)})
			"taken":
				taken.append(id)
	if not taken.is_empty():
		entries = entry_points(grid, grid_data, taken)
	return {"down": down, "taken": taken, "entries": entries}


## RAID-VIS F3: the TAKEN Sites next to the territory (a claimed Site over a link): each is a raid entry point
## (`RaidResolver.default_entry_sites`). `among` limits the answer to those Sites (the ones this raid took);
## empty = every TAKEN Site. Sorted by id.
static func entry_points(grid: GridState, grid_data: CityGridData, among: Array = []) -> Array[StringName]:
	var out: Array[StringName] = []
	var ids: Array = among if not among.is_empty() else grid.sites.keys()
	for k in ids:
		var id := StringName(k)
		if not grid.is_taken(id):
			continue
		for n in grid.neighbors(id, grid_data):
			if grid.is_claimed(n):
				out.append(id)
				break
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return out
