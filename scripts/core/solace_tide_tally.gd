class_name SolaceTideTally
extends RefCounted
## Phase 3b: where INFECTED cards come from, as a tally the raid screen can show. Pure reads over SolaceTideState: nothing here
## changes a rule, it only explains the numbers the rules produced (DECAY TAKEN, the spread, DOSE cures, Sites lost in the raid,
## HOME hits).


## DECAY's INFECTED accounting for `pre`, the state as it stood before DECAY ran: {before, after, taken (DOWN Sites that went TAKEN,
## one card each), spread (the spread card was added), cancelled (a DOSE stopped the spread), cured (INFECTED cards a DOSE removed),
## doses (DOSE cards spent)}. `before + taken + spread - cured == after` always (the tally test pins it). Runs the real DECAY on a copy.
static func decay_tally(pre: SolaceTideState, cfg: CampaignConfigData) -> Dictionary:
	var downs := 0
	for s in pre.owned.keys():
		if int(pre.owned[s]) == SolaceTideState.Cond.DOWN:
			downs += 1
	var spread_start := pre.lost_since_raid + downs >= cfg.solace_tide_spread_min
	var run := pre.duplicate_state()
	SolaceTideRules.decay(run, cfg)
	var doses := run.dose_spent
	var cancelled := spread_start and doses > 0
	var spread_card := spread_start and not cancelled
	var cured := doses - (1 if cancelled else 0)
	var out := {"before": pre.wound_count(), "after": run.wound_count(), "taken": downs, "spread": spread_card, "cancelled": cancelled,
		"cured": cured, "doses": doses}
	return out


## The raid's INFECTED accounting: `before` (after DECAY) and `after` INFECTED cards, `sites` Sites lost in the raid (one card each),
## the rest is HOME hits: {before, after, added, sites, home}.
static func raid_tally(before: int, after: int, sites: int) -> Dictionary:
	var added := maxi(0, after - before)
	var from_sites := mini(sites, added)
	return {"before": before, "after": after, "added": added, "sites": from_sites, "home": added - from_sites}


# ------------------------------------------------------------------------------------------------ Phase 3d: read-only queries
## The raid tiers, worst first: the order the odds bar draws them in.
const TIERS_WORST_FIRST: Array[String] = ["BREACHED", "DAMAGED", "SITES LOST", "HOLDS", "EVADED"]


## The odds of a forecast: how many of its outcome rows end in each tier, worst tier first, tiers with no row left out:
## [{tier, n}]. The sum of `n` is the number of rows (12 for a full forecast).
static func tier_odds(rows: Array) -> Array:
	var counts := {}
	for r in rows:
		counts[String(r["tier"])] = int(counts.get(String(r["tier"]), 0)) + 1
	var out: Array = []
	for t in TIERS_WORST_FIRST:
		if counts.has(t):
			out.append({"tier": t, "n": int(counts[t])})
	return out


## What a set of outcome rows (SolaceTideRules.forecast rows) does to the board relative to `before`, for the map to draw: {down (Sites that
## go OK -> DOWN on some row), taken (Sites a beam newly TAKES on some row), falls (H7c: Sites that fall at the close, DOWN with no sentry
## -> TAKEN, on some row and taken by a beam on none), home (the most HOME integrity any row loses), n}. The lists are sorted by id.
static func outcome_marks(rows: Array, before: SolaceTideState) -> Dictionary:
	var down := {}
	var taken := {}
	var falls := {}
	var home := 0
	for r in rows:
		var ns: SolaceTideState = r["result"]["state"]
		var fell: Array = []
		if r["result"].has("sweep"):
			fell = (r["result"]["sweep"] as SolaceTideRules.Sweep).fell
		for s in ns.owned.keys():
			var was := int(before.owned.get(s, -1))
			var now := int(ns.owned[s])
			if now == SolaceTideState.Cond.DOWN and was == SolaceTideState.Cond.OK:
				down[s] = true
			elif now == SolaceTideState.Cond.TAKEN and was != SolaceTideState.Cond.TAKEN:
				if fell.has(s):
					falls[s] = true
				else:
					taken[s] = true
		home = maxi(home, before.home - ns.home)
	for s in taken.keys():
		falls.erase(s)
	var d: Array = down.keys()
	var t: Array = taken.keys()
	var f: Array = falls.keys()
	IdSort.sort_ids(d)
	IdSort.sort_ids(t)
	IdSort.sort_ids(f)
	return {"down": d, "taken": t, "falls": f, "home": home, "n": rows.size()}


## One string that is equal for two forecasts exactly when every outcome ends alike (tier, HOME, Heat, every Site's condition).
static func outcome_signature(rows: Array) -> String:
	var parts := PackedStringArray()
	for r in rows:
		var ns: SolaceTideState = r["result"]["state"]
		var ks: Array = ns.owned.keys()
		IdSort.sort_ids(ks)
		var s := ""
		for k in ks:
			s += "%s=%d," % [k, int(ns.owned[k])]
		parts.append("%s/%d/%d/%s" % [r["tier"], ns.home, ns.heat, s])
	return "|".join(parts)


## Does card `card_id` standing on `site` do anything in `place` (under HOLD)? The type rule (a sentry only stops a beam of its own type) and the
## outcome test (the forecast with the card against the forecast without it) both count: {useless, why ("" | "type" | "none" | "same"),
## card_type, beam_types (the types of the beams that reach `site`, sorted)}. "type" = beams reach the Site but none is the card's type; "none" = no
## beam that fires reaches it; "same" = every outcome ends alike with or without the card. A card not yet in the placement is tried as if it stood
## on `site` (the ghost shown before it is placed); when that placement would hold more cards than the rules allow, only the type rule is applied.
static func sentry_check(ctx: SolaceTideRules.Ctx, st: SolaceTideState, place: Dictionary, site: StringName, card_id: String) -> Dictionary:
	var ctype := String(ctx.cards[card_id][0])
	var types := {}
	var fired := SolaceTideRules.known_count(st.heat + (ctx.cfg.solace_tide_ghost_heat if place["ghost"] != &"" else 0), ctx.cfg)
	var lines: Array = []
	for i in mini(fired, (ctx.draw["known"] as Array).size()):
		lines.append(ctx.draw["known"][i])
	lines.append_array(ctx.draw["cands"])
	lines.append_array(ctx.draw["hunters"])
	for ln in lines:
		if (ln["cells"] as Array).has(site):
			types[String(ln["type"])] = true
	var bt: Array = types.keys()
	IdSort.sort_ids(bt)
	var out := {"useless": false, "why": "", "card_type": ctype, "beam_types": bt}
	if bt.is_empty():
		out["useless"] = true
		out["why"] = "none"
		return out
	if not types.has(ctype):
		out["useless"] = true
		out["why"] = "type"
		return out
	var with_s: Dictionary = (place["sentries"] as Dictionary).duplicate()
	with_s[site] = card_id
	if with_s.size() > ctx.cfg.solace_tide_max_placed:
		return out
	var without_s := with_s.duplicate()
	without_s.erase(site)
	var a := SolaceTideRules.forecast(ctx, st, {"sentries": with_s, "ghost": place["ghost"]}, ["HOLD"])
	var b := SolaceTideRules.forecast(ctx, st, {"sentries": without_s, "ghost": place["ghost"]}, ["HOLD"])
	if outcome_signature(a) == outcome_signature(b):
		out["useless"] = true
		out["why"] = "same"
	return out


## True when no response can save the city: the INFECTED cards already outnumber the healthy ones (or HOME is gone) when the raid opens, and
## the raid only adds INFECTED cards, so every placement, every response and every outcome ends the campaign.
static func forced_loss(st: SolaceTideState) -> bool:
	return st.lost != SolaceTideState.LOST_NONE or st.home <= 0 or SolaceTideRules.loss_margin(st) == 0


## What the next DECAY does to `st` (the state at an HQ step, with the picks applied): runs the real DECAY on a copy. {downs (the DOWN Sites that
## fall), added (INFECTED cards net), margin (loss_margin after it), fatal (the city is lost the moment that raid closes, whatever the player does),
## near (one more INFECTED card after DECAY ends the city)}.
static func next_decay(st: SolaceTideState, cfg: CampaignConfigData) -> Dictionary:
	var downs: Array = []
	for s in st.owned.keys():
		if int(st.owned[s]) == SolaceTideState.Cond.DOWN:
			downs.append(s)
	IdSort.sort_ids(downs)
	var run := st.duplicate_state()
	SolaceTideRules.decay(run, cfg)
	var margin := SolaceTideRules.loss_margin(run)
	var fatal := run.lost != SolaceTideState.LOST_NONE or margin == 0
	return {"downs": downs, "added": run.wound_count() - st.wound_count(), "margin": margin, "fatal": fatal, "near": not fatal and margin == 1}
