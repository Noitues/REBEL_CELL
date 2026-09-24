class_name HeatRules
extends RefCounted
## Heat (GDD 4.3): one campaign meter. Threshold *events* fire the first time a
## threshold is crossed upward and never again; *modifiers* apply only while Heat is at
## or above the threshold (CampaignState.rule_modifier reads them live, so they switch
## off by themselves when Heat drops).


## Adds `delta` Heat and fires newly crossed thresholds. Returns events.
static func add_heat(campaign: CampaignState, delta: int, config: CampaignConfigData, reason: String = "") -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var before := campaign.heat
	var applied := campaign.add_heat(delta, config)
	if applied == 0 and delta != 0:
		events.append({"type": "heat", "amount": 0, "reason": reason, "text": "Heat unchanged (%s) at %d." % [reason, campaign.heat]})
		return events
	events.append({"type": "heat", "amount": applied, "reason": reason, "text": "Heat %+d (%s) -> %d." % [applied, reason, campaign.heat]})
	if applied <= 0:
		return events
	for t in config.heat_thresholds:
		if t == null or t.heat <= before or t.heat > campaign.heat or campaign.thresholds_fired.has(t.heat):
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
		campaign.pending_raids.append({"raid_id": String(t.event_raid.id), "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": t.heat})
		events.append({"type": "raid_pending", "raid_id": t.event_raid.id, "text": "Raid incoming: %s." % t.event_raid.display_name})
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
