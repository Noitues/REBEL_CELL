class_name RaidOutcome
extends RefCounted
## RAID-FIX A: the one place a raid's verdict and outcome are decided. Pure: it reads a
## `RaidResolver.RaidResult` (a projection or a played raid; they are the same object) and
## the config, so the forecast chip, the playout stamp and the report all say what
## `RaidResolver.apply` does (preview == result). Words live in `RaidVerdict` (TextDb keys).

## The raid's verdict: REPELLED (every threat destroyed: +Schematics), OVERRUN (the Cell
## survived but the raid is lost: +Heat), BREACHED (Home fell: the campaign is lost).
enum Verdict { REPELLED, OVERRUN, BREACHED }

## Severity tiers, mildest first: HOLDS clean, HOLDS with a Home loss over the config's
## percent (amber), a node DOWN (orange), a node TAKEN or Home BREACHED (red).
enum Tier { CLEAN, AMBER, DOWN, TAKEN }

## Why a placed asset changes nothing (see `if_placed`).
const REASON_OUT_OF_REACH := &"out_of_reach"
const REASON_TOO_STRONG := &"too_strong"
const REASON_WRONG_LANE := &"wrong_lane"

## The verdict of a raid with these flags (RaidResult.won / .campaign_lost).
static func verdict_of(won: bool, campaign_lost: bool) -> Verdict:
	if campaign_lost:
		return Verdict.BREACHED
	return Verdict.REPELLED if won else Verdict.OVERRUN


## The verdict of a `RaidResult`.
static func verdict_of_result(r: RaidResolver.RaidResult) -> Verdict:
	return verdict_of(r.won, r.campaign_lost)


## The verdict of a raid dictionary (`RaidResult.to_dict`, `campaign.last_raid`).
static func verdict_of_dict(r: Dictionary) -> Verdict:
	return verdict_of(bool(r.get("won", false)), bool(r.get("campaign_lost", false)))


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


## The severity tier of a raid dictionary (see `Tier`).
static func tier_of_dict(r: Dictionary, config: CampaignConfigData) -> Tier:
	var l := node_losses(r.get("nodes", {}))
	if bool(r.get("campaign_lost", false)) or int(l["taken"]) > 0:
		return Tier.TAKEN
	if int(l["down"]) > 0:
		return Tier.DOWN
	var before := int(r.get("home_before", 0))
	var lost := before - int(r.get("home_after", 0))
	if before > 0 and lost * 100 > before * config.raid_amber_home_loss_pct:
		return Tier.AMBER
	return Tier.CLEAN


## The whole outcome of a `RaidResult` as a dictionary: "verdict" (Verdict), "tier" (Tier),
## "home_before", "home_after", "home_delta" (<= 0), "down", "taken" (node counts),
## "heat_delta", "schematics_delta" (what `RaidResolver.apply` adds), "threats_killed",
## "threats_total". The forecast for a setup equals the result of playing it.
static func project(r: RaidResolver.RaidResult, config: CampaignConfigData) -> Dictionary:
	var d := r.to_dict()
	var l := node_losses(r.nodes)
	return {"verdict": verdict_of_result(r), "tier": tier_of_dict(d, config),
		"home_before": r.home_before, "home_after": r.home_after, "home_delta": r.home_after - r.home_before,
		"down": int(l["down"]), "taken": int(l["taken"]),
		"heat_delta": r.heat_delta, "schematics_delta": r.schematics_delta,
		"threats_killed": r.threats_destroyed, "threats_total": r.threats_total}


## The outcome of a raid dictionary already played (`campaign.last_raid`), the same keys as `project`.
static func of_dict(r: Dictionary, config: CampaignConfigData) -> Dictionary:
	var l := node_losses(r.get("nodes", {}))
	var before := int(r.get("home_before", 0))
	var after := int(r.get("home_after", 0))
	return {"verdict": verdict_of_dict(r), "tier": tier_of_dict(r, config),
		"home_before": before, "home_after": after, "home_delta": after - before,
		"down": int(l["down"]), "taken": int(l["taken"]),
		"heat_delta": int(r.get("heat_delta", 0)), "schematics_delta": int(r.get("schematics_delta", 0)),
		"threats_killed": int(r.get("threats_destroyed", 0)), "threats_total": int(r.get("threats_total", 0))}


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
