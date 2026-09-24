class_name CampaignRules
extends RefCounted
## Campaign-layer rules (GDD 3, 4.1, 4.4, 5.3-5.4, 7.3, 8.4, 11.4, 11.7): new campaigns,
## Site availability and Rank gating, what a finished run does to the Grid (clearing,
## Exploits, story beats, Intel links, win), claiming and nodes, repair, recruiting,
## stationing, Heat purchases, Armory deployment and raid setup/projection/playout.
## Pure functions over CampaignState + content; every mutating call returns events.

const RELAY_TYPES := [RC.NetworkNodeType.RELAY, RC.NetworkNodeType.FIREWALL_RELAY, RC.NetworkNodeType.PROXY_RELAY]


# --- Campaign start ------------------------------------------------------------------

## GDD 5.4 opening: rookies, Schematics, the Grid with home claimed, a random story path.
## `ice_level` applies the ICE ladder from the start (HEAT_OBJECTIVE_SITES switches off
## that many Heat-objective Sites, the last by id); `home_variant` (GDD 3.1) adds its
## internal nodes' integrity, asset slots and built-in defenses to the home server.
static func new_campaign(corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, campaign_seed: int, class_data: ClassData, home_node: NetworkNodeData, ice_level: int = 0, home_variant: HomeServerVariantData = null) -> CampaignState:
	var c := CampaignState.new()
	c.corporation_id = corp.id
	c.campaign_seed = campaign_seed
	c.ice_level = ice_level
	c.schematics = config.starting_schematics
	for i in config.starting_rookies:
		c.recruit(class_data)
	c.grid = GridState.from_grid(corp.city_grid, home_node)
	if home_node != null:
		c.grid.sites[c.grid.home_site_id]["node_type"] = String(home_node.id)
	if home_variant != null:
		c.home_variant_id = home_variant.id
		for n in home_variant.internal_nodes:
			if n == null:
				continue
			c.grid.home_max_integrity += n.integrity
			c.grid.home_asset_slots += n.asset_slots
			if n.built_in_asset != null:
				c.grid.home_built_in.append(String(n.built_in_asset.id))
		c.grid.home_integrity = c.grid.home_max_integrity
		c.grid.sites[c.grid.home_site_id]["integrity"] = c.grid.home_max_integrity
		c.grid.sites[c.grid.home_site_id]["max_integrity"] = c.grid.home_max_integrity
	c.story_path_id = pick_story_path(corp, campaign_seed)
	var fewer := -int(c.rule_modifier(config, RC.RuleModifierType.HEAT_OBJECTIVE_SITES))
	if fewer > 0:
		var objectives: Array[StringName] = []
		for s in corp.city_grid.sites:
			if s != null and s.objective == RC.SiteObjective.HEAT_REDUCTION:
				objectives.append(s.id)
		objectives.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
		for i in mini(fewer, objectives.size()):
			c.disabled_objectives.append(objectives[objectives.size() - 1 - i])
	return c


## The Site's objective for this campaign (NONE when ICE switched it off).
static func site_objective(campaign: CampaignState, site: SiteData) -> int:
	if site == null:
		return RC.SiteObjective.NONE
	if campaign.disabled_objectives.has(site.id):
		return RC.SiteObjective.NONE
	return site.objective


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


## Patrol targets (decision 2026-09-24, fixes a soft-lock found by the balance
## simulation): cleared or claimed Sites other than home and the boss can be run again
## as a full netrun with normal loot, Heat and Rank but no objective, so rookies
## recruited late can always rank up. Sorted by id.
static func patrol_sites(campaign: CampaignState, corp: CorporationData) -> Array[SiteData]:
	var out: Array[SiteData] = []
	for s in corp.city_grid.sites:
		if s == null or s.id == corp.city_grid.home_site_id or s.objective == RC.SiteObjective.BOSS:
			continue
		if campaign.grid.is_cleared(s.id) or campaign.grid.is_claimed(s.id):
			out.append(s)
	out.sort_custom(func(a: SiteData, b: SiteData) -> bool: return String(a.id) < String(b.id))
	return out


static func is_patrol(campaign: CampaignState, site: SiteData) -> bool:
	return site != null and site.objective != RC.SiteObjective.BOSS and site.id != campaign.grid.home_site_id \
		and (campaign.grid.is_cleared(site.id) or campaign.grid.is_claimed(site.id))


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
	var allowed := is_patrol(campaign, site)
	for s in launchable_sites(campaign, corp, config):
		if s.id == site.id:
			allowed = true
	if not allowed:
		if site.objective == RC.SiteObjective.BOSS:
			return "The breach needs %d Exploits (%d held)." % [config.min_exploits_for_breach, campaign.exploits.size()]
		return "%s is not reachable from your territory." % site.id
	if campaign.grid.is_seized(site.id):
		return ""
	if class_data == null or class_data.id != op.class_id:
		return "Class data for %s does not match its class %s." % [op.name, op.class_id]
	if site.tier > max_tier_for(op, class_data):
		return "%s is Rank %d: Tier %d needs a higher Rank." % [op.name, op.rank, site.tier]
	return ""


## "netrun", "patrol", "boss" or "reclaim" for a launch at `site`. A patrol plays as a
## full netrun (NetrunSession kind "netrun"); only its completion differs.
static func run_kind_for(campaign: CampaignState, site: SiteData) -> String:
	if campaign.grid.is_seized(site.id):
		return "reclaim"
	if site.objective == RC.SiteObjective.BOSS:
		return "boss"
	if is_patrol(campaign, site):
		return "patrol"
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
static func on_run_completed(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, run: RunState, lookup: ContentLookup = null) -> Array[Dictionary]:
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
	if run.kind == "netrun" and is_patrol(campaign, site):
		events.append({"type": "patrol_complete", "site": site.id, "text": "Patrol of %s complete: no objective, the Grid is unchanged." % site.id})
		if lookup != null:
			events.append_array(_node_passives_on_completion(campaign, corp, config, lookup))
		return events
	campaign.grid.sites[site.id]["status"] = GridState.SiteStatus.CLEARED
	events.append({"type": "site_cleared", "site": site.id, "text": "%s cleared: it can be claimed now." % site.id})
	if run.kind == "reclaim":
		return events
	match site_objective(campaign, site):
		RC.SiteObjective.EXPLOIT:
			campaign.exploits.append(site.exploit_type)
			events.append({"type": "exploit", "exploit": site.exploit_type, "text": "Exploit extracted: %s (%d held)." % [RC.ExploitType.keys()[site.exploit_type], campaign.exploits.size()]})
			var exploit_heat := config.exploit_heat + int(campaign.rule_modifier(config, RC.RuleModifierType.EXPLOIT_HEAT))
			events.append_array(HeatRules.add_heat(campaign, exploit_heat, config, "Exploit extracted"))
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
				if beat.triggers_raid:
					events.append_array(queue_raid(campaign, corp, RC.RaidTriggerSource.STORY, &"", "The story beat %s" % beat.title))
			if campaign.heat >= config.retaliation_min_heat:
				events.append_array(queue_raid(campaign, corp, RC.RaidTriggerSource.RETALIATION, site.id, "Extracting the Exploit at %s under Heat %d" % [site.id, campaign.heat]))
		RC.SiteObjective.HEAT_REDUCTION:
			events.append_array(HeatRules.add_heat(campaign, site.heat_change, config, "Heat objective %s" % site.id))
	if lookup != null:
		events.append_array(_node_passives_on_completion(campaign, corp, config, lookup))
	return events


## Queues the corporation's raid for `source` (GDD 4.4: story, retaliation, node-built).
## `entry` names the Site the threats enter from (empty = default entries). No raid of
## that source in the content = nothing happens.
static func queue_raid(campaign: CampaignState, corp: CorporationData, source: int, entry: StringName, why: String) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var raid := _raid_for(corp, source)
	if raid == null:
		return events
	campaign.pending_raids.append({"raid_id": String(raid.id), "source": source, "site_id": String(entry), "corporation": String(campaign.corporation_id)})
	events.append({"type": "raid_pending", "raid_id": raid.id, "source": source,
		"text": "%s provoked a raid: %s." % [why, raid.display_name]})
	return events


## Node passives on netrun completion (GDD 3.2): Vault Terminal +3 Schematics, Proxy Relay
## -1 Heat (`NetworkNodeData.passive_effects`, trigger ON_NETRUN_COMPLETE, target CAMPAIGN),
## plus adjacency bonuses whose partner node type is an active neighbour. Nodes in id order.
static func _node_passives_on_completion(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	for site_id in campaign.grid.claimed_ids():
		if not campaign.grid.is_active_node(site_id) or site_id == campaign.grid.home_site_id:
			continue
		var node := lookup.get_content(campaign.grid.node_type_of(site_id)) as NetworkNodeData
		if node == null:
			continue
		var effects: Array[TriggeredEffectData] = []
		for te in node.passive_effects:
			if te != null and te.trigger == RC.Trigger.ON_NETRUN_COMPLETE:
				effects.append(te)
		for bonus in node.adjacency_bonuses:
			if bonus == null:
				continue
			var partner := false
			for n in campaign.grid.neighbors(site_id, corp.city_grid):
				if campaign.grid.is_active_node(n):
					var nt := lookup.get_content(campaign.grid.node_type_of(n)) as NetworkNodeData
					if nt != null and nt.node_type == bonus.partner_type:
						partner = true
			if partner:
				for te in bonus.effects:
					if te != null and te.trigger == RC.Trigger.ON_NETRUN_COMPLETE:
						effects.append(te)
		for te in effects:
			for e in te.effects:
				if e == null:
					continue
				match e.type:
					RC.EffectType.GAIN_SCHEMATICS:
						campaign.schematics += e.amount
						events.append({"type": "node_passive", "site": site_id, "effect": e.type, "amount": e.amount,
							"text": "%s (%s): %+d Schematics." % [node.display_name, site_id, e.amount]})
					RC.EffectType.MODIFY_HEAT:
						events.append({"type": "node_passive", "site": site_id, "effect": e.type, "amount": e.amount,
							"text": "%s (%s): Heat %+d." % [node.display_name, site_id, e.amount]})
						events.append_array(HeatRules.add_heat(campaign, e.amount, config, node.display_name))
	return events


## Active Compiler Racks next to `site_id` (GDD 3.2): netruns launched there start with a
## bonus card offer.
static func compiler_racks_next_to(campaign: CampaignState, corp: CorporationData, lookup: ContentLookup, site_id: StringName) -> int:
	var n := 0
	for neighbour in campaign.grid.neighbors(site_id, corp.city_grid):
		if campaign.grid.is_active_node(neighbour):
			var node := lookup.get_content(campaign.grid.node_type_of(neighbour)) as NetworkNodeData
			if node != null and node.node_type == RC.NetworkNodeType.COMPILER_RACK:
				n += 1
	return n


# --- Claiming and nodes -----------------------------------------------------------------------

## The Profile unlock that gates `node`, or null when the node needs none.
static func unlock_for(lookup: ContentLookup, res: Resource) -> ProfileUnlockData:
	for id in lookup.ids_of_class(&"ProfileUnlockData"):
		var u := lookup.get_content(id) as ProfileUnlockData
		if u != null and u.unlocks == res:
			return u
	return null


## Whether the node type may be installed under `profile` (null profile = no gating).
static func node_available(profile: ProfileState, lookup: ContentLookup, node: NetworkNodeData) -> bool:
	if node == null:
		return false
	if not node.profile_unlock_required or profile == null:
		return true
	var u := unlock_for(lookup, node)
	return u == null or profile.has_unlock(u.id)


## Empty when the Site can be claimed with `node_type_id`; otherwise why not.
static func claim_error(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, site_id: StringName, node_type_id: StringName, profile: ProfileState = null) -> String:
	if campaign.is_over():
		return "The campaign is over."
	if not campaign.grid.is_cleared(site_id):
		return "%s is not a cleared Site." % site_id
	var node := lookup.get_content(node_type_id) as NetworkNodeData
	if node == null or node.node_type == RC.NetworkNodeType.HOME_SERVER:
		return "Choose a node type to install."
	if not node_available(profile, lookup, node):
		return "%s is locked: buy the Profile unlock first." % node.display_name
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
static func claim(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, site_id: StringName, node_type_id: StringName, profile: ProfileState = null) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var err := claim_error(campaign, corp, config, lookup, site_id, node_type_id, profile)
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
	var entry: StringName = &""
	for n in campaign.grid.neighbors(site_id, corp.city_grid):
		if campaign.grid.is_corporate(n) or campaign.grid.is_seized(n):
			entry = n
			break
	if node.triggers_raid:
		# Node-built raids (GDD 4.4): the corporation's NODE_BUILT raid, else the claim raid.
		if _raid_for(corp, RC.RaidTriggerSource.NODE_BUILT) != null:
			events.append_array(queue_raid(campaign, corp, RC.RaidTriggerSource.NODE_BUILT, entry, "Building a %s at %s" % [node.display_name, site_id]))
		else:
			events.append_array(queue_raid(campaign, corp, RC.RaidTriggerSource.TERRITORY_CLAIM, entry, "Building a %s at %s" % [node.display_name, site_id]))
	elif entry != &"":
		events.append_array(queue_raid(campaign, corp, RC.RaidTriggerSource.TERRITORY_CLAIM, entry, "Claiming %s" % site_id))
	return events


## Node upgrade (GDD 11.4: 30 then 60 Schematics): each level adds
## node_upgrade_integrity_pct of the base integrity and node_upgrade_asset_slots slots.
static func upgrade_cost(campaign: CampaignState, config: CampaignConfigData, site_id: StringName) -> int:
	var level := campaign.grid.upgrade_level_of(site_id)
	return config.node_upgrade_costs[level] if level < config.node_upgrade_costs.size() else -1


static func upgrade_node(campaign: CampaignState, config: CampaignConfigData, lookup: ContentLookup, site_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	if not campaign.grid.is_active_node(site_id) or site_id == campaign.grid.home_site_id:
		events.append({"type": "refused", "text": "%s has no working node to upgrade." % site_id})
		return events
	var cost := upgrade_cost(campaign, config, site_id)
	if cost < 0:
		events.append({"type": "refused", "text": "%s is fully upgraded." % site_id})
		return events
	if campaign.schematics < cost:
		events.append({"type": "refused", "text": "Not enough Schematics (%d needed)." % cost})
		return events
	var node := lookup.get_content(campaign.grid.node_type_of(site_id)) as NetworkNodeData
	var s := campaign.grid.site(site_id)
	campaign.schematics -= cost
	s["upgrade_level"] = int(s["upgrade_level"]) + 1
	var gain := roundi(node.integrity * config.node_upgrade_integrity_pct / 100.0)
	s["max_integrity"] = int(s["max_integrity"]) + gain
	s["integrity"] = int(s["integrity"]) + gain
	events.append({"type": "upgraded", "site": site_id, "level": s["upgrade_level"], "cost": cost,
		"text": "Upgraded %s to level %d (-%d Schematics): integrity +%d, +%d asset slot(s)." % [site_id, s["upgrade_level"], cost, gain, config.node_upgrade_asset_slots]})
	return events


## Buys a Profile unlock with the campaign's Schematics (GDD 3.4). The unlock is permanent.
static func purchase_unlock(campaign: CampaignState, profile: ProfileState, lookup: ContentLookup, unlock_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var u := lookup.get_content(unlock_id) as ProfileUnlockData
	if u == null:
		events.append({"type": "refused", "text": "No such unlock."})
		return events
	if profile.has_unlock(u.id):
		events.append({"type": "refused", "text": "%s is already unlocked." % u.display_name})
		return events
	for req in u.requires_unlock_ids:
		if not profile.has_unlock(req):
			events.append({"type": "refused", "text": "%s needs %s first." % [u.display_name, req]})
			return events
	if u.requires_all_corporations_at_ice >= 0:
		for id in lookup.ids_of_class(&"CorporationData"):
			var corp := lookup.get_content(id) as CorporationData
			if corp == null or corp.generated_from_profile:
				continue
			if profile.best_ice_for(corp.id) < u.requires_all_corporations_at_ice:
				events.append({"type": "refused", "text": "%s needs every corporation cleared at ICE %d." % [u.display_name, u.requires_all_corporations_at_ice]})
				return events
	if campaign.schematics < u.schematic_cost:
		events.append({"type": "refused", "text": "Not enough Schematics (%d needed)." % u.schematic_cost})
		return events
	campaign.schematics -= u.schematic_cost
	profile.add_unlock(u.id)
	events.append({"type": "unlocked", "unlock": u.id, "cost": u.schematic_cost, "text": "Unlocked %s (-%d Schematics)." % [u.display_name, u.schematic_cost]})
	return events


## Buys a one-time netrun boost (GDD 11.4) for the next run launched.
static func buy_boost(campaign: CampaignState, config: CampaignConfigData, boost_id: StringName) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var boost: NetrunBoostData = null
	for b in config.netrun_boosts:
		if b != null and b.id == boost_id:
			boost = b
	if boost == null:
		events.append({"type": "refused", "text": "No such boost."})
		return events
	if campaign.pending_boosts.has(boost.id):
		events.append({"type": "refused", "text": "%s is already queued for the next run." % boost.display_name})
		return events
	if campaign.schematics < boost.cost:
		events.append({"type": "refused", "text": "Not enough Schematics (%d needed)." % boost.cost})
		return events
	campaign.schematics -= boost.cost
	campaign.pending_boosts.append(boost.id)
	events.append({"type": "boost_bought", "boost": boost.id, "cost": boost.cost, "text": "Bought %s for the next run (-%d Schematics)." % [boost.display_name, boost.cost]})
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
	var pct := campaign.rule_modifier(config, RC.RuleModifierType.REPAIR_COST_PCT)
	var cost := roundi(node.install_cost * node.repair_cost_ratio * (1.0 + pct / 100.0)) if node != null else 0
	if campaign.schematics < cost:
		events.append({"type": "refused", "text": "Not enough Schematics (%d needed)." % cost})
		return events
	campaign.schematics -= cost
	s["condition"] = GridState.Condition.OK
	s["integrity"] = s["max_integrity"]
	events.append({"type": "repaired", "site": site_id, "cost": cost, "text": "Repaired %s (-%d Schematics)." % [site_id, cost]})
	return events


## Home-server patch price for `points` of integrity (all missing points when < 0).
static func home_repair_price(campaign: CampaignState, config: CampaignConfigData, points: int = -1) -> int:
	var missing := campaign.grid.home_max_integrity - campaign.grid.home_integrity
	var n := missing if points < 0 else mini(points, missing)
	return ceili(maxi(0, n) * config.home_repair_cost_per_point)


## Patches the home server at HQ (decision 2026-09-24): restores up to `points` integrity
## (all missing points when < 0) for home_repair_cost_per_point Schematics each; with too
## few Schematics it restores what they buy.
static func repair_home(campaign: CampaignState, config: CampaignConfigData, points: int = -1) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	var missing := campaign.grid.home_max_integrity - campaign.grid.home_integrity
	if missing <= 0:
		events.append({"type": "refused", "text": "The home server is at full integrity."})
		return events
	var wanted := missing if points < 0 else mini(points, missing)
	var affordable := int(floor(campaign.schematics / maxf(0.0001, config.home_repair_cost_per_point)))
	var n := mini(wanted, affordable)
	if n <= 0:
		events.append({"type": "refused", "text": "Not enough Schematics to patch the home server."})
		return events
	var cost := ceili(n * config.home_repair_cost_per_point)
	campaign.schematics -= cost
	campaign.grid.home_integrity += n
	campaign.grid.site(campaign.grid.home_site_id)["integrity"] = campaign.grid.home_integrity
	events.append({"type": "home_repaired", "amount": n, "cost": cost,
		"text": "Patched the home server +%d (%d/%d, -%d Schematics)." % [n, campaign.grid.home_integrity, campaign.grid.home_max_integrity, cost]})
	return events


## Whether `cls` can be recruited under `profile` (GDD 3.4): classes with a Profile unlock
## need it; the rest (the Breaker) are always available. A null profile gates nothing.
static func class_available(profile: ProfileState, lookup: ContentLookup, cls: ClassData) -> bool:
	if cls == null:
		return false
	if profile == null:
		return true
	var u := unlock_for(lookup, cls)
	return u == null or profile.has_unlock(u.id)


## Whether a campaign against `corp` may start under `profile` (GDD 3.4): corporations
## with a Profile unlock need it; the rest (Solace) are always open. Null profile = open.
static func corporation_available(profile: ProfileState, lookup: ContentLookup, corp: CorporationData) -> bool:
	if corp == null:
		return false
	if profile == null:
		return true
	var u := unlock_for(lookup, corp)
	return u == null or profile.has_unlock(u.id)


## Corporations a new campaign may target, by id.
static func available_corporations(profile: ProfileState, lookup: ContentLookup) -> Array[CorporationData]:
	var out: Array[CorporationData] = []
	for id in lookup.ids_of_class(&"CorporationData"):
		var corp := lookup.get_content(id) as CorporationData
		if corp != null and not corp.generated_from_profile and corporation_available(profile, lookup, corp):
			out.append(corp)
	return out


## Base classes (no alternative_of) and alternatives the profile may recruit, by id.
static func available_classes(profile: ProfileState, lookup: ContentLookup) -> Array[ClassData]:
	var out: Array[ClassData] = []
	for id in lookup.ids_of_class(&"ClassData"):
		var cls := lookup.get_content(id) as ClassData
		if class_available(profile, lookup, cls):
			out.append(cls)
	return out


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

static func asset_slots(campaign: CampaignState, lookup: ContentLookup, site_id: StringName, config: CampaignConfigData = null) -> int:
	if site_id == campaign.grid.home_site_id:
		return campaign.grid.home_asset_slots
	var node := lookup.get_content(campaign.grid.node_type_of(site_id)) as NetworkNodeData
	var slots := node.asset_slots if node != null else 0
	if config != null:
		slots += campaign.grid.upgrade_level_of(site_id) * config.node_upgrade_asset_slots
	return slots


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
	if s["assets"].size() >= asset_slots(campaign, lookup, site_id, config):
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
	if to["assets"].size() >= asset_slots(campaign, lookup, to_site, config):
		events.append({"type": "refused", "text": "%s has no free asset slot." % to_site})
		return events
	from["assets"].remove_at(index)
	to["assets"].append(String(asset))
	events.append({"type": "moved", "asset": asset, "from": from_site, "to": to_site, "text": "%s moved %s -> %s." % [asset, from_site, to_site]})
	return events


# --- Raids ---------------------------------------------------------------------------------------

static func raid_strength_pct(campaign: CampaignState, config: CampaignConfigData, pending: Dictionary = {}, corp: CorporationData = null) -> float:
	var pct := campaign.rule_modifier(config, RC.RuleModifierType.RAID_STRENGTH_PCT)
	# SEIZED_RAID_STRENGTH_PCT (ICE 14): raids entering from a Seized Site hit harder.
	if corp != null and not pending.is_empty():
		for entry in raid_entries(campaign, corp, pending):
			if campaign.grid.is_seized(entry):
				pct += campaign.rule_modifier(config, RC.RuleModifierType.SEIZED_RAID_STRENGTH_PCT)
				break
	return pct


static func raid_extra_waves(campaign: CampaignState, config: CampaignConfigData) -> int:
	return int(campaign.rule_modifier(config, RC.RuleModifierType.RAID_EXTRA_WAVE))


static func pending_raid(campaign: CampaignState) -> Dictionary:
	return campaign.pending_raids[0] if not campaign.pending_raids.is_empty() else {}


## The RaidData for a pending raid. A corporation's raid that `replaces` the queued id
## (Heat-threshold raids are shared in the config) wins for that corporation's campaign.
static func raid_data(pending: Dictionary, lookup: ContentLookup) -> RaidData:
	var raid_id := StringName(String(pending.get("raid_id", "")))
	var corp_id := StringName(String(pending.get("corporation", "")))
	if corp_id != &"":
		for id in lookup.ids_of_class(&"RaidData"):
			var r := lookup.get_content(id) as RaidData
			if r != null and r.replaces == raid_id and r.corporation_id == corp_id:
				return r
	return lookup.get_content(raid_id) as RaidData


static func raid_entries(campaign: CampaignState, corp: CorporationData, pending: Dictionary) -> Array[StringName]:
	var site := String(pending.get("site_id", ""))
	if site != "":
		return [StringName(site)]
	return RaidResolver.default_entry_sites(campaign, corp.city_grid)


## Exact outcome if the raid ran now (setup phase, GDD 7.1).
static func project_raid(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, pending: Dictionary) -> RaidResolver.RaidResult:
	var raid := raid_data(pending, lookup)
	return RaidResolver.resolve(campaign, corp.city_grid, raid, lookup, config, raid_entries(campaign, corp, pending),
		raid_strength_pct(campaign, config, pending, corp), raid_extra_waves(campaign, config))


## Plays the raid out and applies it; the pending entry is consumed.
static func fight_raid(campaign: CampaignState, corp: CorporationData, config: CampaignConfigData, lookup: ContentLookup, pending: Dictionary) -> Array[Dictionary]:
	var raid := raid_data(pending, lookup)
	var result := project_raid(campaign, corp, config, lookup, pending)
	campaign.pending_raids.erase(pending)
	var events: Array[Dictionary] = result.events.duplicate()
	events.append_array(RaidResolver.apply(campaign, result, raid, config))
	return events
