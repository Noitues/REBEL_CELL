class_name SolaceTideRaid
extends RefCounted
## One Infected Tide raid of a campaign, as the player lives it (SOLACE_RAID_SPEC.md section 2 and 10 item 4): `open` runs
## DECAY and draws the lines and the hand; PLAN (`set_place`) and RESPONSE (`set_response`) can be changed and undone
## (`rewind`) any number of times; `resolve` plays the raid and applies it to the campaign. The raid is ONE checkpoint:
## nothing before `resolve` touches the campaign except DECAY, and DECAY is never undone (it is part of the campaign the
## moment the raid opens, and an opened raid that is saved and loaded does not decay twice); after `resolve` nothing rewinds.
## `preview` is the forecast of the current setup and equals what `resolve` plays (SolaceTideRules.forecast == play).

var campaign: CampaignState
var corp: CorporationData
var cfg: CampaignConfigData
var pending: Dictionary = {}
## The raid's index (raids fought so far) and its context: the state after DECAY, the lines and the hand.
var raid_idx: int = 0
var st: SolaceTideState = null
var ctx: SolaceTideRules.Ctx = null
## The current setup: the placement ({"sentries": {site: card}, "ghost": &"" | HOME}) and the response (["HOLD"], ...).
var place: Dictionary = {"sentries": {}, "ghost": &""}
var resp: Array = ["HOLD"]
## True once DECAY ended the campaign (CITY LOST) or the raid was resolved.
var over: bool = false
var resolved: bool = false
## Events DECAY produced when the raid opened.
var open_events: Array[Dictionary] = []
var _history: Array = []


## Opens the pending raid: DECAY (every raid after the first, never undone, once), then the lines and the hand from the
## `raids` stream of this raid. Returns the raid; `over` is true when DECAY ended the campaign.
static func open(p_campaign: CampaignState, p_corp: CorporationData, p_cfg: CampaignConfigData, p_pending: Dictionary = {}) -> SolaceTideRaid:
	var r := SolaceTideRaid.new()
	r.campaign = p_campaign
	r.corp = p_corp
	r.cfg = p_cfg
	r.pending = p_pending
	r.raid_idx = SolaceTideCampaign.raids_fought(p_campaign)
	var tide := p_campaign.corp_theme.solace.tide
	var start := SolaceTideCampaign.load_state(p_campaign, p_corp, p_cfg)
	if r.raid_idx > 0 and not tide.decayed:
		start.netruns_since_raid = 0
		SolaceTideRules.decay(start, p_cfg)
		start.decayed = true
		r.open_events = SolaceTideCampaign.store_state(p_campaign, start)  # DECAY is committed here
		if start.lost != SolaceTideState.LOST_NONE:
			r.st = start
			r.over = true
			r.resolved = true
			p_campaign.raids_lost += 1
			p_campaign.last_raid = {"raid_id": String(p_pending.get("raid_id", "")), "model": "tide", "raid": r.raid_idx, "tier": "CITY LOST",
				"won": false, "campaign_lost": true, "lost": start.lost, "home_before": start.home, "home_after": start.home,
				"heat_delta": 0, "schematics_delta": 0, "taken": [], "down": [], "infected": start.wound_count(), "trace": []}
			return r
		start = SolaceTideCampaign.load_state(p_campaign, p_corp, p_cfg)
	start.netruns_since_raid = 0
	start.raid_n = r.raid_idx
	r.st = start
	var board := SolaceTideCampaign.board_for(p_corp, p_cfg)
	var rng := SolaceTideCampaign.raid_streams(p_campaign.campaign_seed, r.raid_idx)
	var draw := SolaceTideRules.draw_lines(board, start, p_cfg, rng)
	var hand := SolaceTideRules.draw_hand(start, p_cfg, rng)
	r.ctx = SolaceTideRules.make_ctx(board, start, p_cfg, draw, hand, r.raid_idx)
	return r


## Every legal placement of the hand (SolaceTideRules.placements).
func placements() -> Array:
	return SolaceTideRules.placements(ctx, st) if not over else []


## The RESPONSE options of the current placement.
func response_options() -> Array:
	if over:
		return []
	return SolaceTideRules.response_options(ctx, SolaceTideRules.launch(ctx, st, place))


## PLAN: a placement. The response is reset to HOLD (its options depend on the placement). Returns false after the resolve.
func set_place(p: Dictionary) -> bool:
	if over or resolved:
		return false
	_history.append([place, resp])
	place = p
	resp = ["HOLD"]
	return true


## RESPONSE: one of `response_options`. Returns false after the resolve.
func set_response(r: Array) -> bool:
	if over or resolved:
		return false
	_history.append([place, resp])
	resp = r
	return true


## True while a PLAN or RESPONSE can be undone: never after the resolve (the checkpoint).
func can_rewind() -> bool:
	return not resolved and not over and not _history.is_empty()


## Undoes the last PLAN or RESPONSE. Refused (false) at the start of the raid and after the resolve; DECAY is not undone.
func rewind() -> bool:
	if not can_rewind():
		return false
	var prev: Array = _history.pop_back()
	place = prev[0]
	resp = prev[1]
	return true


## The forecast of the current setup: the 12 outcomes (SolaceTideRules.forecast).
func preview() -> Array:
	return SolaceTideRules.forecast(ctx, st, place, resp) if not over else []


## The automatic defense (SolaceTideCampaign.auto_plan) becomes the setup.
func plan_auto() -> void:
	var plan := SolaceTideCampaign.auto_plan(ctx, st, cfg)
	place = plan["place"]
	resp = plan["resp"]


## Plays the raid and applies it to the campaign (the checkpoint: nothing rewinds after this). Returns events.
func resolve() -> Array[Dictionary]:
	var events: Array[Dictionary] = open_events.duplicate()
	if resolved:
		return events
	resolved = true
	var home_before := st.home
	var heat_before := st.heat
	var schem_before := st.schematics
	var res := SolaceTideRules.play(ctx, st, place, resp, int(ctx.draw["real_a"]), int(ctx.draw["hunter_real"]))
	var ns: SolaceTideState = res["state"]
	SolaceTideRules.finish_raid(ns, resp, raid_idx)
	ns.decayed = false
	var clean := ns.home >= home_before and SolaceTideCampaign.owned_same(st.owned, ns.owned)
	var taken: Array[String] = []
	var down: Array[String] = []
	var ids: Array = ns.owned.keys()
	IdSort.sort_ids(ids)
	for id in ids:
		var was := int(st.owned.get(id, -1))
		var now := int(ns.owned[id])
		if now == SolaceTideState.Cond.TAKEN and was != SolaceTideState.Cond.TAKEN:
			taken.append(String(id))
		elif now == SolaceTideState.Cond.DOWN and was == SolaceTideState.Cond.OK:
			down.append(String(id))
	var tier_word := String(res["tier"])
	events.append({"type": "raid_end", "won": clean, "tier": tier_word,
		"text": "Tide raid %d: %s. HOME %d -> %d, %d DOWN, %d TAKEN, %d INFECTED." % [raid_idx + 1, tier_word, home_before, ns.home, down.size(), taken.size(), ns.wound_count()]})
	events.append_array(SolaceTideCampaign.store_state(campaign, ns))
	campaign.last_raid = {"raid_id": String(pending.get("raid_id", "")), "model": "tide", "raid": raid_idx, "tier": tier_word, "won": clean,
		"campaign_lost": ns.lost != SolaceTideState.LOST_NONE, "lost": ns.lost, "home_before": home_before, "home_after": ns.home,
		"heat_delta": ns.heat - heat_before, "schematics_delta": ns.schematics - schem_before, "taken": taken, "down": down,
		"infected": ns.wound_count(), "trace": (res["trace"] as Array).duplicate(true)}
	if ns.lost != SolaceTideState.LOST_NONE:
		campaign.raids_lost += 1
	elif clean:
		campaign.raids_won += 1
		events.append({"type": "raid_won", "schematics": ns.schematics - schem_before,
			"text": "Clean defense: +%d Schematics." % (ns.schematics - schem_before)})
	else:
		campaign.raids_lost += 1
	return events
