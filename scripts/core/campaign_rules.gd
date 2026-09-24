class_name CampaignRules
extends RefCounted
## Campaign-layer rules (GDD 3, 4.1, 4.4, 5.3-5.4, 7.3, 8.4, 11.4, 11.7): new campaigns,
## Site availability and Rank gating, what a finished run does to the Grid (clearing,
## Exploits, story beats, Intel links, win), claiming and nodes, repair, recruiting,
## stationing, Heat purchases, Armory deployment and raid setup/projection/playout.
## Pure functions over CampaignState + content; every mutating call returns events.

const RELAY_TYPES := [RC.NetworkNodeType.RELAY, RC.NetworkNodeType.FIREWALL_RELAY]


# --- Campaign start ------------------------------------------------------------------

## GDD 5.4 opening: rookies, Schematics, the Grid with home claimed, a random story path.
static func new_campaign(corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, campaign_seed: int, class_data: ClassData, home_node: NetworkNodeData) -> CampaignState:
	var c := CampaignState.new()
	c.corporation_id = corp.id
	c.campaign_seed = campaign_seed
	c.schematics = config.starting_schematics
	for i in config.starting_rookies:
		c.recruit(class_data)
	c.grid = GridState.from_grid(corp.city_grid, home_node)
	if home_node != null:
		c.grid.sites[c.grid.home_site_id]["node_type"] = String(home_node.id)
	c.story_path_id = pick_story_path(corp, campaign_seed)
	return c


static func pick_story_path(corp: CorporationData, campaign_seed: int) -> StringName:
	if corp.story_paths.is_empty():
		return &""
	var rng := RngStreams.make_stream(campaign_seed, &"events")
	var total := 0.0
	for p in corp.story_paths:
		if p != null:
			total += p.weight
	var roll := rng.randf() * total
	for p in corp.story_paths:
		if p == null:
			continue
		roll -= p.weight
		if roll <= 0.0:
			return p.id
	return corp.story_paths[corp.story_paths.size() - 1].id


static func story_path(campaign: CampaignState, corp: CorporationData) -> StoryPathData:
	for p in corp.story_paths:
		if p != null and p.id == campaign.story_path_id:
			return p
	return null


## Beats the player has earned so far (one per Exploit; the finale after the win).
static func revealed_beats(campaign: CampaignState, corp: CorporationData) -> Array[StoryBeatData]:
	var out: Array[StoryBeatData] = []
	var p := story_path(campaign, corp)
	if p == null:
		return out
	for i in mini(campaign.story_beats_revealed, p.beats.size()):
		out.append(p.beats[i])
	for i in range(p.beats.size(), campaign.story_beats_revealed):
		var bonus := i - p.beats.size()
		if bonus < p.bonus_beats.size():
			out.append(p.bonus_beats[bonus])
	if campaign.outcome == CampaignState.Outcome.WON and p.finale != null:
		out.append(p.finale)
	return out


# --- Sites and launching --------------------------------------------------------------------

static func site_data(corp: CorporationData, site_id: StringName) -> SiteData:
	return corp.city_grid.get_site(site_id)


## Whether the Site touches the player's territory (home or a claimed/cleared Site).
static func touches_territory(campaign: CampaignState, corp: CorporationData, site_id: StringName) -> bool:
	for n in campaign.grid.neighbors(site_id, corp.city_grid):
		if campaign.grid.is_claimed(n) or campaign.grid.is_cleared(n):
			return true
	return false


## Sites a netrun can target now, sorted by id: corporate Sites next to the territory
## (the boss only with enough Exploits) and Seized Sites (Reclaim).
static func launchable_sites(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData) -> Array[SiteData]:
	var out: Array[SiteData] = []
	for s in corp.city_grid.sites:
		if s == null or s.id == corp.city_grid.home_site_id:
			continue
		if campaign.grid.is_seized(s.id):
			out.append(s)
		elif campaign.grid.is_corporate(s.id) and touches_territory(campaign, corp, s.id):
			if s.objective == RC.SiteObjective.BOSS and campaign.exploits.size() < config.min_exploits_for_breach:
				continue
			out.append(s)
	out.sort_custom(func(a: SiteData, b: SiteData) -> bool: return String(a.id) < String(b.id))
	return out


## Highest netrun tier the operative's Rank allows (GDD 5.3).
static func max_tier_for(op: OperativeState, class_data: ClassData) -> int:
	var tier := 1
	for r in class_data.rank_rewards:
		if r != null and r.rank <= op.rank:
			tier = maxi(tier, r.max_netrun_tier)
	return tier


## Empty when `op` may launch at `site`; otherwise why not.
static func launch_error(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, op: OperativeState, class_data: ClassData, site: SiteData) -> String:
	if campaign.is_over():
		return "The campaign is over."
	if op == null or not op.alive:
		return "That operative is not available."
	var allowed := false
	for s in launchable_sites(campaign, corp, config):
		if s.id == site.id:
			allowed = true
	if not allowed:
		if site.objective == RC.SiteObjective.BOSS:
			return "The breach needs %d Exploits (%d held)." % [config.min_exploits_for_breach, campaign.exploits.size()]
		return "%s is not reachable from your territory." % site.id
	if campaign.grid.is_seized(site.id):
		return ""
	if site.tier > max_tier_for(op, class_data):
		return "%s is Rank %d: Tier %d needs a higher Rank." % [op.name, op.rank, site.tier]
	return ""


## "netrun", "boss" or "reclaim" for a launch at `site`.
static func run_kind_for(campaign: CampaignState, site: SiteData) -> String:
	if campaign.grid.is_seized(site.id):
		return "reclaim"
	if site.objective == RC.SiteObjective.BOSS:
		return "boss"
	return "netrun"


## Exploit effects on the final breach (GDD 11.7) as CombatSession overrides.
static func boss_overrides(campaign: CampaignState, corp: CorporationData) -> Dictionary:
	var out := {"remove_boss_pointers": 0, "boss_corrupt_slices": 0, "reveal_phases": false}
	for ex in corp.exploits:
		if ex == null or not campaign.has_exploit(ex.exploit_type):
			continue
		out["remove_boss_pointers"] = int(out["remove_boss_pointers"]) + ex.removes_boss_pointers
		out["reveal_phases"] = bool(out["reveal_phases"]) or ex.reveals_boss_phases
		for te in ex.breach_effects:
			if te == null:
				continue
			for e in te.effects:
				if e != null and e.type == RC.EffectType.APPLY_STATUS and e.status == RC.Status.CORRUPTED:
					out["boss_corrupt_slices"] = int(out["boss_corrupt_slices"]) + maxi(1, e.amount)
	return out


# --- Run outcomes -----------------------------------------------------------------------------

## What a completed run does to the campaign: clears the Site, extracts its Exploit
## (+Heat, story beat, Intel links), applies Heat objectives, or wins the breach.
static func on_run_completed(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, run: RunState) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var site := site_data(corp, run.site_id)
	if site == null:
		return events
	if run.kind == "boss":
		campaign.outcome = CampaignState.Outcome.WON
		var p := story_path(campaign, corp)
		events.append({"type": "campaign_won", "text": "The Renewal Engine is down. Campaign WON."})
		if p != null and p.finale != null:
			events.append({"type": "story_beat", "beat_id": p.finale.id, "text": "[%s] %s" % [p.finale.title, p.finale.text]})
		return events
	campaign.grid.sites[site.id]["status"] = GridState.SiteStatus.CLEARED
	events.append({"type": "site_cleared", "site": site.id, "text": "%s cleared: it can be claimed now." % site.id})
	if run.kind == "reclaim":
		return events
	match site.objective:
		RC.SiteObjective.EXPLOIT:
			campaign.exploits.append(site.exploit_type)
			events.append({"type": "exploit", "exploit": site.exploit_type, "text": "Exploit extracted: %s (%d held)." % [RC.ExploitType.keys()[site.exploit_type], campaign.exploits.size()]})
			events.append_array(HeatRules.add_heat(campaign, config.exploit_heat, config, "Exploit extracted"))
			for ex in corp.exploits:
				if ex != null and ex.exploit_type == site.exploit_type and ex.opens_locked_links:
					for s in corp.city_grid.sites:
						if s == null:
							continue
						for l in s.locked_links:
							campaign.grid.open_link(s.id, l)
							events.append({"type": "link_opened", "a": s.id, "b": l, "text": "Intel opened the link %s - %s." % [s.id, l]})
			var p := story_path(campaign, corp)
			campaign.story_beats_revealed += 1
			var beats := revealed_beats(campaign, corp)
			if p != null and not beats.is_empty():
				var beat := beats[beats.size() - 1]
				events.append({"type": "story_beat", "beat_id": beat.id, "text": "[%s] %s" % [beat.title, beat.text]})
		RC.SiteObjective.HEAT_REDUCTION:
			events.append_array(HeatRules.add_heat(campaign, site.heat_change, config, "Heat objective %s" % site.id))
	return events


# --- Claiming and nodes -----------------------------------------------------------------------

## Empty when the Site can be claimed with `node_type_id`; otherwise why not.
static func claim_error(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, site_id: StringName, node_type_id: StringName) -> String:
	if campaign.is_over():
		return "The campaign is over."
	if not campaign.grid.is_cleared(site_id):
		return "%s is not a cleared Site." % site_id
	var node := lookup.get_content(node_type_id) as NetworkNodeData
	if node == null or node.node_type == RC.NetworkNodeType.HOME_SERVER:
		return "Choose a node type to install."
	if campaign.schematics < node.install_cost:
		return "Not enough Schematics (%d needed, %d held)." % [node.install_cost, campaign.schematics]
	var reachable := false
	for n in campaign.grid.neighbors(site_id, corp.city_grid):
		if n == campaign.grid.home_site_id:
			reachable = true
		elif campaign.grid.is_active_node(n):
			var nt := lookup.get_content(campaign.grid.node_type_of(n)) as NetworkNodeData
			if nt != null and nt.node_type in RELAY_TYPES:
				reachable = true
	if not reachable:
		return "%s is beyond your Relays: claim through a Relay or next to home." % site_id
	return ""


## Claims the Site and installs the node (GDD 3.1). Claiming next to a corporate Site or
## a node that provokes raids queues a TERRITORY_CLAIM raid (GDD 4.4).
static func claim(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, site_id: StringName, node_type_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var err := claim_error(campaign, corp, config, lookup, site_id, node_type_id)
	if err != "":
		events.append({"type": "refused", "text": err})
		return events
	var node := lookup.get_content(node_type_id) as NetworkNodeData
	campaign.schematics -= node.install_cost
	var s := campaign.grid.site(site_id)
	s["status"] = GridState.SiteStatus.CLAIMED
	s["node_type"] = String(node_type_id)
	s["integrity"] = node.integrity
	s["max_integrity"] = node.integrity
	s["condition"] = GridState.Condition.OK
	s["assets"] = []
	events.append({"type": "claimed", "site": site_id, "node": node_type_id, "text": "Claimed %s with a %s (-%d Schematics)." % [site_id, node.display_name, node.install_cost]})
	var provoked := node.triggers_raid
	var entry: StringName = &""
	for n in campaign.grid.neighbors(site_id, corp.city_grid):
		if campaign.grid.is_corporate(n) or campaign.grid.is_seized(n):
			provoked = true
			entry = n
			break
	if provoked:
		var raid := _raid_for(corp, RC.RaidTriggerSource.TERRITORY_CLAIM)
		if raid != null:
			campaign.pending_raids.append({"raid_id": String(raid.id), "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": String(entry) if entry != &"" else ""})
			events.append({"type": "raid_pending", "raid_id": raid.id, "text": "Claiming %s provoked a raid: %s." % [site_id, raid.display_name]})
	return events


static func _raid_for(corp: CorporationData, source: int) -> RaidData:
	for r in corp.raids:
		if r != null and r.trigger_source == source:
			return r
	return null


## Repairs a Disabled node for repair_cost_ratio x install cost (GDD 3.3).
static func repair(campaign: CampaignState, config: CampaignConfigData, lookup: ContentLookup, site_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var s := campaign.grid.site(site_id)
	if s.is_empty() or not campaign.grid.is_claimed(site_id) or int(s["condition"]) != GridState.Condition.DISABLED:
		events.append({"type": "refused", "text": "%s is not a Disabled node." % site_id})
		return events
	var node := lookup.get_content(campaign.grid.node_type_of(site_id)) as NetworkNodeData
	var cost := roundi(node.install_cost * node.repair_cost_ratio) if node != null else 0
	if campaign.schematics < cost:
		events.append({"type": "refused", "text": "Not enough Schematics (%d needed)." % cost})
		return events
	campaign.schematics -= cost
	s["condition"] = GridState.Condition.OK
	s["integrity"] = s["max_integrity"]
	events.append({"type": "repaired", "site": site_id, "cost": cost, "text": "Repaired %s (-%d Schematics)." % [site_id, cost]})
	return events


static func recruit(campaign: CampaignState, config: CampaignConfigData, class_data: ClassData) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	if campaign.schematics < config.rookie_cost:
		events.append({"type": "refused", "text": "Not enough Schematics (%d needed)." % config.rookie_cost})
		return events
	campaign.schematics -= config.rookie_cost
	var op := campaign.recruit(class_data)
	events.append({"type": "recruited", "operative": op.id, "text": "Recruited %s (-%d Schematics)." % [op.name, config.rookie_cost]})
	return events


## Stations `op_id` on a Safehouse-type node (GDD 5.4), recalling it from elsewhere.
static func station(campaign: CampaignState, lookup: ContentLookup, op_id: StringName, site_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var op := campaign.get_operative(op_id)
	if op == null or not op.alive:
		events.append({"type": "refused", "text": "No such living operative."})
		return events
	if not campaign.grid.is_active_node(site_id):
		events.append({"type": "refused", "text": "%s has no working node." % site_id})
		return events
	var node := lookup.get_content(campaign.grid.node_type_of(site_id)) as NetworkNodeData
	if node == null or node.station_slots <= 0:
		events.append({"type": "refused", "text": "%s has no station slot." % site_id})
		return events
	if campaign.grid.stationed_on(site_id) != &"" and campaign.grid.stationed_on(site_id) != op_id:
		events.append({"type": "refused", "text": "%s is already occupied." % site_id})
		return events
	recall(campaign, op_id)
	campaign.grid.site(site_id)["stationed"] = String(op_id)
	events.append({"type": "stationed", "operative": op_id, "site": site_id, "text": "%s is stationed on %s." % [op.name, site_id]})
	return events


## Rank 3 Inner Ring segment swap (GDD 6.4): `segment_index` (0-2) of the operative's
## ring becomes `segment_id`, one of the class's rank_ring_segment_options; an empty id
## restores the class default. The swap is free and can be redone between runs.
static func swap_ring_segment(campaign: CampaignState, lookup: ContentLookup, op_id: StringName, segment_index: int, segment_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var op := campaign.get_operative(op_id)
	if op == null or not op.alive:
		events.append({"type": "refused", "text": "No such living operative."})
		return events
	var cls := lookup.get_content(op.class_id) as ClassData
	var options := ring_segment_options(op, cls)
	if options.is_empty():
		events.append({"type": "refused", "text": "%s has no segment swaps yet (Rank 3 needed)." % op.name})
		return events
	if segment_index < 0 or segment_index >= RC.RING_SEGMENTS:
		events.append({"type": "refused", "text": "No such ring segment."})
		return events
	if segment_id != &"" and not options.has(segment_id):
		events.append({"type": "refused", "text": "%s is not a swap option for %s." % [segment_id, op.name]})
		return events
	while op.ring_segment_ids.size() < RC.RING_SEGMENTS:
		op.ring_segment_ids.append(&"")
	op.ring_segment_ids[segment_index] = segment_id
	events.append({"type": "segment_swapped", "operative": op_id, "index": segment_index, "segment": segment_id,
		"text": "%s ring segment %d is now %s." % [op.name, segment_index, segment_id if segment_id != &"" else "the class default"]})
	return events


## Segment ids the operative may swap in at its Rank (highest reward with options wins).
static func ring_segment_options(op: OperativeState, cls: ClassData) -> Array[StringName]:
	var out: Array[StringName] = []
	var best := 0
	for reward in cls.rank_rewards:
		if reward != null and reward.rank <= op.rank and reward.rank >= best and not reward.ring_segment_options.is_empty():
			best = reward.rank
			out.clear()
			for seg in reward.ring_segment_options:
				if seg != null:
					out.append(seg.id)
	return out


static func recall(campaign: CampaignState, op_id: StringName) -> void:
	for id in campaign.grid.sites:
		if campaign.grid.site(id).get("stationed", "") == String(op_id):
			campaign.grid.site(id)["stationed"] = ""


static func stationed_site(campaign: CampaignState, op_id: StringName) -> StringName:
	for id in campaign.grid.sites:
		if campaign.grid.site(id).get("stationed", "") == String(op_id):
			return id
	return &""


static func heat_purchase_price(campaign: CampaignState, config: CampaignConfigData) -> int:
	return config.heat_purchase_cost + config.heat_purchase_increment * campaign.heat_purchases


## Buys -heat_purchase_amount Heat (GDD 11.4: 25 Schematics, +10 per purchase).
static func buy_heat_reduction(campaign: CampaignState, config: CampaignConfigData) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var price := heat_purchase_price(campaign, config)
	if campaign.schematics < price:
		events.append({"type": "refused", "text": "Not enough Schematics (%d needed)." % price})
		return events
	campaign.schematics -= price
	campaign.heat_purchases += 1
	events.append({"type": "purchase", "price": price, "text": "Paid %d Schematics to scrub Heat." % price})
	events.append_array(HeatRules.add_heat(campaign, -config.heat_purchase_amount, config, "Heat purchase"))
	return events


# --- Armory and assets -------------------------------------------------------------------------

static func asset_slots(campaign: CampaignState, lookup: ContentLookup, site_id: StringName) -> int:
	var node := lookup.get_content(campaign.grid.node_type_of(site_id)) as NetworkNodeData
	return node.asset_slots if node != null else 0


## Moves an Armory asset onto a claimed node (GDD 7.3).
static func deploy_asset(campaign: CampaignState, config: CampaignConfigData, lookup: ContentLookup, armory_index: int, site_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	if armory_index < 0 or armory_index >= campaign.armory.size():
		events.append({"type": "refused", "text": "No such Armory asset."})
		return events
	if not campaign.grid.is_active_node(site_id):
		events.append({"type": "refused", "text": "%s has no working node." % site_id})
		return events
	var s := campaign.grid.site(site_id)
	if s["assets"].size() >= asset_slots(campaign, lookup, site_id):
		events.append({"type": "refused", "text": "%s has no free asset slot." % site_id})
		return events
	var asset := campaign.armory[armory_index]
	campaign.armory.remove_at(armory_index)
	s["assets"].append(String(asset))
	events.append({"type": "deployed", "asset": asset, "site": site_id, "text": "Deployed %s on %s." % [asset, site_id]})
	return events


## Repositions a deployed asset to another node (or back to the Armory with `to_site` empty).
static func move_asset(campaign: CampaignState, config: CampaignConfigData, lookup: ContentLookup, from_site: StringName, index: int, to_site: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var from := campaign.grid.site(from_site)
	if from.is_empty() or index < 0 or index >= from["assets"].size():
		events.append({"type": "refused", "text": "No such deployed asset."})
		return events
	var asset := StringName(String(from["assets"][index]))
	if to_site == &"":
		if campaign.armory.size() >= config.armory_capacity:
			events.append({"type": "refused", "text": "Armory full (%d)." % config.armory_capacity})
			return events
		from["assets"].remove_at(index)
		campaign.armory.append(asset)
		events.append({"type": "withdrawn", "asset": asset, "site": from_site, "text": "%s withdrawn from %s to the Armory." % [asset, from_site]})
		return events
	if not campaign.grid.is_active_node(to_site):
		events.append({"type": "refused", "text": "%s has no working node." % to_site})
		return events
	var to := campaign.grid.site(to_site)
	if to["assets"].size() >= asset_slots(campaign, lookup, to_site):
		events.append({"type": "refused", "text": "%s has no free asset slot." % to_site})
		return events
	from["assets"].remove_at(index)
	to["assets"].append(String(asset))
	events.append({"type": "moved", "asset": asset, "from": from_site, "to": to_site, "text": "%s moved %s -> %s." % [asset, from_site, to_site]})
	return events


# --- Raids ---------------------------------------------------------------------------------------

static func raid_strength_pct(campaign: CampaignState, config: CampaignConfigData) -> float:
	return campaign.rule_modifier(config, RC.RuleModifierType.RAID_STRENGTH_PCT)


static func pending_raid(campaign: CampaignState) -> Dictionary:
	return campaign.pending_raids[0] if not campaign.pending_raids.is_empty() else {}


static func raid_data(pending: Dictionary, lookup: ContentLookup) -> RaidData:
	return lookup.get_content(StringName(String(pending.get("raid_id", "")))) as RaidData


static func raid_entries(campaign: CampaignState, corp: CorporationData, pending: Dictionary) -> Array[StringName]:
	var site := String(pending.get("site_id", ""))
	if site != "":
		return [StringName(site)]
	return RaidResolver.default_entry_sites(campaign, corp.city_grid)


## Exact outcome if the raid ran now (setup phase, GDD 7.1).
static func project_raid(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, pending: Dictionary) -> RaidResolver.RaidResult:
	var raid := raid_data(pending, lookup)
	return RaidResolver.resolve(campaign, corp.city_grid, raid, lookup, config, raid_entries(campaign, corp, pending), raid_strength_pct(campaign, config))


## Plays the raid out and applies it; the pending entry is consumed.
static func fight_raid(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, pending: Dictionary) -> Array[Dictionary]:
	var raid := raid_data(pending, lookup)
	var result := project_raid(campaign, corp, config, lookup, pending)
	campaign.pending_raids.erase(pending)
	var events: Array[Dictionary] = result.events.duplicate()
	events.append_array(RaidResolver.apply(campaign, result, raid, config))
	return events
