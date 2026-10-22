class_name HeatRules
extends RefCounted
## Heat (GDD 4.3): one campaign meter. Threshold *events* fire the first time a
## threshold is crossed upward and never again; *modifiers* apply only while Heat is at
## or above the threshold (CampaignState.rule_modifier reads them live, so they switch
## off by themselves when Heat drops).


## Heat gain scaled by HEAT_GAIN_PCT, sinks by HEAT_SINK_PCT (ICE 1 / ICE 6). A non-zero
## delta never rounds to zero.
static func scaled_delta(campaign: CampaignState, delta: int, config: CampaignConfigData) -> int:
	if delta == 0:
		return 0
	var pct := campaign.rule_modifier(config, RC.RuleModifierType.HEAT_GAIN_PCT if delta > 0 else RC.RuleModifierType.HEAT_SINK_PCT)
	var scaled := roundi(delta * (1.0 + pct / 100.0))
	if scaled == 0:
		scaled = signi(delta)
	return scaled


## The Heat a threshold fires at: PURGE_THRESHOLD (ICE 17) pulls the Purge down.
static func effective_heat(t: HeatThresholdData, campaign: CampaignState, config: CampaignConfigData) -> int:
	if t.kind == RC.ThresholdKind.PURGE:
		var purge := int(campaign.rule_modifier(config, RC.RuleModifierType.PURGE_THRESHOLD))
		if purge > 0:
			return mini(t.heat, purge)
	return t.heat


## Where the Heat bands start for this campaign, ascending (GDD 4.3): the MAJOR levels and
## the PURGE level as it fires (effective_heat: ICE 17 pulls the PURGE band down with it).
## `campaign` null reads the config's levels (CampaignConfigData.heat_band_levels).
static func band_levels(campaign: CampaignState, config: CampaignConfigData) -> Array[int]:
	var out: Array[int] = []
	for t in config.heat_thresholds:
		if t != null and (t.kind == RC.ThresholdKind.MAJOR or t.kind == RC.ThresholdKind.PURGE):
			out.append(effective_heat(t, campaign, config) if campaign != null else t.heat)
	out.sort()
	return out


## Adds `delta` Heat (scaled by the gain/sink modifiers) and fires newly crossed
## thresholds. Returns events.
static func add_heat(campaign: CampaignState, delta: int, config: CampaignConfigData, reason: String = "") -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var before := campaign.heat
	delta = scaled_delta(campaign, delta, config)
	var applied := campaign.add_heat(delta, config)
	if applied == 0 and delta != 0:
		events.append({"type": "heat", "amount": 0, "reason": reason, "before": before, "after": campaign.heat, "text": "Heat unchanged (%s) at %d." % [reason, campaign.heat]})
		return events
	events.append({"type": "heat", "amount": applied, "reason": reason, "before": before, "after": campaign.heat, "text": "Heat %+d (%s) -> %d." % [applied, reason, campaign.heat]})
	if applied <= 0:
		return events
	for t in config.heat_thresholds:
		if t == null:
			continue
		var at := effective_heat(t, campaign, config)
		if at <= before or at > campaign.heat or campaign.thresholds_fired.has(t.heat):
			continue
		campaign.thresholds_fired.append(t.heat)
		events.append_array(fire_threshold(campaign, t))
	return events


## Queues the one-time effects of a threshold: a raid and/or netrun complications.
static func fire_threshold(campaign: CampaignState, t: HeatThresholdData) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	events.append({"type": "heat_threshold", "heat": t.heat, "kind": t.kind,
		"text": "Heat threshold %d (%s): %s" % [t.heat, RC.ThresholdKind.keys()[t.kind], t.event_text]})
	if t.event_raid != null:
		campaign.pending_raids.append({"raid_id": String(t.event_raid.id), "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": t.heat,
			"corporation": String(campaign.corporation_id)})
		# The name comes from the corporation's own raid when one replaces the shared one
		# (CampaignRules.raid_data); HeatRules has no lookup, so callers rename it.
		events.append({"type": "raid_pending", "raid_id": t.event_raid.id, "shared_name": t.event_raid.display_name,
			"text": "Raid incoming: %s." % t.event_raid.display_name})
	for m in t.event_complications:
		if m != null:
			campaign.pending_complications.append({"type": m.type, "value": m.value})
			events.append({"type": "complication", "modifier": m.type, "value": m.value,
				"text": "Next netrun complication: %s %+.0f." % [RC.RuleModifierType.keys()[m.type], m.value]})
	return events


## Ongoing modifiers active at the current Heat, for HUDs.
static func active_modifiers(campaign: CampaignState, config: CampaignConfigData) -> Array[RuleModifierData]:
	var out: Array[RuleModifierData] = []
	for t in config.heat_thresholds:
		if t == null or campaign.heat < t.heat:
			continue
		for m in t.ongoing_modifiers:
			if m != null:
				out.append(m)
	return out


## The Heat an operative's death adds on a run of `tier` (death_heat_base + tier + the
## DEATH_HEAT modifier, before the gain scaling `add_heat` applies). The netrun's death and
## the HQ's flatline warning both read this.
static func death_heat(campaign: CampaignState, config: CampaignConfigData, tier: int) -> int:
	return config.death_heat_base + tier + int(campaign.rule_modifier(config, RC.RuleModifierType.DEATH_HEAT))


## W3-GRID (C3): what adding `delta` Heat would do now, worked out by applying `add_heat` to
## a copy (the forecast is the real result; the campaign is not changed): {before, after,
## delta (applied: scaled and clamped), crosses: Array[int] (the threshold Heats that would
## fire), raid: bool (one of them queues a raid)}.
static func forecast(campaign: CampaignState, delta: int, config: CampaignConfigData) -> Dictionary:
	var copy := campaign.duplicate_state()
	var events := add_heat(copy, delta, config, "forecast")
	var crosses: Array[int] = []
	var raid := false
	for e in events:
		if String(e.get("type", "")) == "heat_threshold":
			crosses.append(int(e["heat"]))
		elif String(e.get("type", "")) == "raid_pending":
			raid = true
	return {"before": campaign.heat, "after": copy.heat, "delta": copy.heat - campaign.heat, "crosses": crosses, "raid": raid}


## RAID-FIX C4: the next raid the Heat will queue: {"at": the threshold's Heat (as it fires, effective_heat), "away":
## Heat still to gain}, the lowest unfired raid threshold above the current Heat; {} when none is left. Ties by
## threshold Heat, then id.
static func next_raid(campaign: CampaignState, config: CampaignConfigData) -> Dictionary:
	var best: HeatThresholdData = null
	var best_at := 0
	for t in config.heat_thresholds:
		if t == null or t.event_raid == null or campaign.thresholds_fired.has(t.heat):
			continue
		var at := effective_heat(t, campaign, config)
		if at <= campaign.heat:
			continue
		if best == null or at < best_at or (at == best_at and String(t.id) < String(best.id)):
			best = t
			best_at = at
	if best == null:
		return {}
	return {"at": best_at, "away": best_at - campaign.heat}


## RAID-FIX C4: the Heat of the last raid threshold that adding `delta` Heat now would cross (the forecast's own
## answer, so the RAID tag on a Site card is the real result); 0 when it queues no raid.
static func raid_crossed_by(campaign: CampaignState, delta: int, config: CampaignConfigData) -> int:
	var f := forecast(campaign, delta, config)
	if not bool(f["raid"]):
		return 0
	var raid_heat := 0
	for h in f["crosses"] as Array:
		for t in config.heat_thresholds:
			if t != null and t.heat == int(h) and t.event_raid != null:
				raid_heat = maxi(raid_heat, effective_heat(t, campaign, config))
	return raid_heat
