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
