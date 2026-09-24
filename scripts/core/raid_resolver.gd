class_name RaidResolver
extends RefCounted
## Cell Defense resolution (GDD 7, TECH_SPEC 7). Pure: resolve() works on copies and
## returns a RaidResult with a per-step event log; the setup-phase projection calls the
## same function, so projection always equals the real result. apply() writes a result
## into the campaign. Ties are broken by content id, then site id, never by dictionary
## order.
##
## Per step: threats move (edges_per_step, routing rule, decoys pull), ICE Locks hold,
## assets and built-in defenses fire, threats damage the node they stand on (0 ->
## Disabled, 50% of the excess cascades to adjacent claimed nodes; a Disabled node hit
## again is Seized; damage at home reduces home integrity, 0 = campaign lost). The raid
## ends when no threat is active or at the step cap; threats still on nodes Seize them.

class RaidResult:
	extends RefCounted
	var raid_id: StringName = &""
	var steps_run: int = 0
	var won: bool = false
	var campaign_lost: bool = false
	var home_before: int = 0
	var home_after: int = 0
	var threats_destroyed: int = 0
	var threats_reached_home: int = 0
	## site_id (String) -> {"before": int, "after": int, "outcome": "holds"|"disabled"|"seized"|"passed"}
	var nodes: Dictionary = {}
	var seized: Array[String] = []
	var disabled: Array[String] = []
	var events: Array[Dictionary] = []
	var grid_after: GridState = null

	func to_dict() -> Dictionary:
		return {"raid_id": String(raid_id), "steps_run": steps_run, "won": won, "campaign_lost": campaign_lost,
			"home_before": home_before, "home_after": home_after, "threats_destroyed": threats_destroyed,
			"threats_reached_home": threats_reached_home, "nodes": nodes.duplicate(true),
			"seized": seized.duplicate(), "disabled": disabled.duplicate()}

	func summary_hash() -> int:
		return hash(JSON.stringify(to_dict()))


## Resolves `raid` against the campaign's Grid. `entry_site_ids` overrides the wave's
## entries when non-empty. `strength_pct` scales threat integrity and damage
## (RAID_STRENGTH_PCT modifiers); `extra_waves` repeats the last wave (RAID_EXTRA_WAVE).
## Nothing passed in is modified.
static func resolve(campaign: CampaignState, grid_data: CityGridData, raid: RaidData, lookup: ContentLookup, config: CampaignConfigData, entry_site_ids: Array[StringName] = [], strength_pct: float = 0.0, extra_waves: int = 0) -> RaidResult:
	var result := RaidResult.new()
	result.raid_id = raid.id
	var grid := campaign.grid.duplicate_state()
	grid.frozen_links.clear()
	result.grid_after = grid
	result.home_before = grid.home_integrity
	var entries := entry_site_ids if not entry_site_ids.is_empty() else default_entry_sites(campaign, grid_data)
	var threats: Array[Dictionary] = []
	var waves := _waves(raid, entries, campaign, strength_pct, extra_waves)
	_prepare_links(waves, grid, grid_data, result)
	var before := {}
	for id in grid.claimed_ids():
		before[String(id)] = int(grid.site(id)["integrity"]) if id != grid.home_site_id else grid.home_integrity
	var seized_now: Array[String] = []
	var disabled_now: Array[String] = []
	var step := 0
	while step < config.raid_step_cap:
		step += 1
		if waves.has(step):
			for t in waves[step]:
				threats.append(t)
				result.events.append({"type": "threat_enters", "step": step, "threat": t["id"], "site": t["site"],
					"text": "Step %d: %s enters at %s." % [step, t["name"], t["site"]]})
		if _active(threats).is_empty():
			if waves.is_empty() or step > _last_wave_step(waves):
				step -= 1
				break
			continue
		_move_threats(threats, grid, grid_data, lookup, step, result)
		_hold_threats(threats, grid, lookup, step, result)
		_fire_assets(campaign, threats, grid, grid_data, lookup, step, result)
		_damage_nodes(threats, grid, grid_data, lookup, config, step, result, seized_now, disabled_now)
		if grid.home_integrity <= 0:
			result.campaign_lost = true
			result.events.append({"type": "home_lost", "step": step, "text": "Step %d: HOME SERVER integrity 0. Campaign lost." % step})
			break
		if _active(threats).is_empty() and step >= _last_wave_step(waves):
			break
	result.steps_run = step
	# Step cap: threats still standing on a node Seize it.
	for t in _active(threats):
		var site: StringName = t["site"]
		if grid.is_claimed(site) and site != grid.home_site_id:
			_seize(grid, site, seized_now)
			result.events.append({"type": "seized", "site": site, "text": "Raid over: %s still on %s -> SEIZED." % [t["name"], site]})
	for t in threats:
		if t["integrity"] <= 0:
			result.threats_destroyed += 1
		elif t.get("reached_home", false):
			result.threats_reached_home += 1
	result.home_after = grid.home_integrity
	result.won = result.threats_destroyed == threats.size() and not result.campaign_lost
	for id in before:
		var sid := StringName(id)
		var after: int = grid.home_integrity if sid == grid.home_site_id else int(grid.site(sid)["integrity"])
		var outcome := "holds"
		if seized_now.has(id):
			outcome = "seized"
		elif disabled_now.has(id):
			outcome = "disabled"
		result.nodes[id] = {"before": before[id], "after": after, "outcome": outcome}
	result.seized = seized_now
	result.disabled = disabled_now
	result.events.append({"type": "raid_end", "won": result.won, "steps": result.steps_run,
		"text": "Raid %s after %d step(s): %d threat(s) destroyed, %d reached home, %d Disabled, %d Seized." % [
			"REPELLED" if result.won else "ENDED", result.steps_run, result.threats_destroyed, result.threats_reached_home, disabled_now.size(), seized_now.size()]})
	return result


## Writes a resolved raid into the campaign: node states, home integrity, Seized Sites
## (their nodes and assets are lost), counters, Heat for a lost raid, reward for a win.
static func apply(campaign: CampaignState, result: RaidResult, raid: RaidData, config: CampaignConfigData) -> Array[Dictionary]:
	var events: Array[Dictionary] = []
	campaign.grid = result.grid_after.duplicate_state()
	campaign.grid.frozen_links.clear()  # freezes last one raid; opened links stay open
	campaign.last_raid = result.to_dict()
	for sid in result.seized:
		var s := campaign.grid.site(StringName(sid))
		if s.get("stationed", "") != "":
			events.append({"type": "recalled", "operative": s["stationed"], "text": "%s returns to the reserves from Seized %s." % [s["stationed"], sid]})
	if result.campaign_lost:
		campaign.outcome = CampaignState.Outcome.LOST
		campaign.raids_lost += 1
		events.append({"type": "campaign_lost", "text": "The home server is gone. Campaign lost."})
		return events
	if result.won:
		campaign.raids_won += 1
		campaign.schematics += raid.schematic_reward
		events.append({"type": "raid_won", "schematics": raid.schematic_reward, "text": "Raid repelled: +%d Schematics." % raid.schematic_reward})
	else:
		campaign.raids_lost += 1
		events.append_array(HeatRules.add_heat(campaign, config.lost_raid_heat, config, "lost raid"))
	return events


## Corporate Sites adjacent to the territory, plus Seized Sites adjacent to it; the boss
## Site as a last resort. Sorted by id.
static func default_entry_sites(campaign: CampaignState, grid_data: CityGridData) -> Array[StringName]:
	var grid := campaign.grid
	var out := {}
	for id in grid.claimed_ids():
		for n in grid.neighbors(id, grid_data):
			if grid.is_corporate(n) or grid.is_seized(n):
				out[n] = true
	var ids: Array[StringName] = []
	for k in out.keys():
		ids.append(k)
	ids.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	if ids.is_empty():
		ids.append(grid_data.boss_site_id)
	return ids


# --- Internals -----------------------------------------------------------------------------

static func _waves(raid: RaidData, entries: Array[StringName], campaign: CampaignState, strength_pct: float, extra_waves: int = 0) -> Dictionary:
	var waves := {}
	var counter := 0
	var scale := 1.0 + maxf(0.0, strength_pct) / 100.0
	var wave_list: Array[RaidWaveData] = []
	for w in raid.waves:
		if w != null:
			wave_list.append(w)
	# RAID_EXTRA_WAVE (ICE 19): the last wave comes again.
	for i in maxi(0, extra_waves):
		if not wave_list.is_empty():
			wave_list.append(wave_list[wave_list.size() - 1])
	for wi in wave_list.size():
		var wave := wave_list[wi]
		var step := 1 + wi * 5
		var wave_entries: Array[StringName] = entries
		if not wave.entry_site_ids.is_empty():
			wave_entries = wave.entry_site_ids
		var list: Array[Dictionary] = []
		for ti in wave.threats.size():
			var td := wave.threats[ti]
			if td == null:
				continue
			var heat_scale := 1.0 + td.heat_integrity_scaling * (campaign.heat / 10)
			list.append({
				"id": "t%d" % counter, "content_id": td.id, "name": td.display_name if td.display_name != "" else String(td.id),
				"integrity": roundi(td.integrity * scale * heat_scale), "damage": roundi(td.damage * scale),
				"edges_per_step": td.edges_per_step, "routing": td.routing,
				"freezes_edges": td.freezes_edges, "alters_edges": td.alters_edges,
				"site": wave_entries[counter % wave_entries.size()], "hold": 0, "held_by": [], "reached_home": false,
			})
			counter += 1
		waves[step] = list
	return waves


## Threats that freeze or alter links before the raid starts (GDD 7.1), in step order and
## threat order so the projection matches the playout. An altering threat opens the first
## locked link (by site id) touching its entry Site; it stays open afterwards. A freezing
## threat freezes the link between the home server and its neighbour holding the most
## deployed assets (ties by id): nothing routes or shoots across it during this raid.
static func _prepare_links(waves: Dictionary, grid: GridState, grid_data: CityGridData, result: RaidResult) -> void:
	var steps: Array = waves.keys()
	steps.sort()
	for step in steps:
		for t in waves[step]:
			if bool(t.get("alters_edges", false)):
				var entry: StringName = t["site"]
				var site := grid_data.get_site(entry)
				var opened := false
				if site != null:
					var candidates: Array[StringName] = site.locked_links.duplicate()
					for s in grid_data.sites:
						if s != null and s.locked_links.has(entry):
							candidates.append(s.id)
					candidates.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
					for other in candidates:
						if not grid.is_link_open(entry, other):
							grid.open_link(entry, other)
							opened = true
							result.events.append({"type": "link_altered", "step": 0, "threat": t["id"], "a": entry, "b": other,
								"text": "Setup: %s cuts a new route %s - %s." % [t["name"], entry, other]})
							break
				if not opened:
					result.events.append({"type": "link_altered", "step": 0, "threat": t["id"], "a": entry, "b": &"",
						"text": "Setup: %s finds no locked route to open near %s." % [t["name"], entry]})
			if bool(t.get("freezes_edges", false)):
				var best: StringName = &""
				var best_assets := -1
				for n in grid.neighbors(grid.home_site_id, grid_data):
					var count := grid.assets_on(n).size() if grid.is_claimed(n) else 0
					if count > best_assets:
						best_assets = count
						best = n
				if best != &"":
					grid.freeze_link(grid.home_site_id, best)
					result.events.append({"type": "link_frozen", "step": 0, "threat": t["id"], "a": grid.home_site_id, "b": best,
						"text": "Setup: %s freezes the link %s - %s for this raid." % [t["name"], grid.home_site_id, best]})


static func _last_wave_step(waves: Dictionary) -> int:
	var last := 0
	for k in waves:
		last = maxi(last, int(k))
	return last


static func _active(threats: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for t in threats:
		if t["integrity"] > 0 and not t["reached_home"]:
			out.append(t)
	return out


static func _target_of(t: Dictionary, grid: GridState, grid_data: CityGridData, lookup: ContentLookup) -> StringName:
	var home := grid.home_site_id
	var candidates: Array[StringName] = []
	for id in grid.claimed_ids():
		if id != home and grid.is_active_node(id):
			candidates.append(id)
	# Decoys pull routing toward their node: strongest pull wins, ties by site id.
	var best_pull := 0
	var pulled: StringName = &""
	for id in candidates:
		for a in grid.assets_on(id):
			var asset := lookup.get_content(a) as DefenseAssetData
			if asset != null and asset.decoy_pull > best_pull:
				best_pull = asset.decoy_pull
				pulled = id
	if pulled != &"" and grid.distance(t["site"], pulled, grid_data) >= 0:
		return pulled
	match int(t["routing"]):
		RC.ThreatRouting.HIGHEST_VALUE:
			var best: StringName = &""
			var best_score := -1
			for id in candidates:
				var node := lookup.get_content(grid.node_type_of(id)) as NetworkNodeData
				var score := (node.raid_priority * 1000 + node.install_cost) if node != null else 0
				if score > best_score and grid.distance(t["site"], id, grid_data) >= 0:
					best_score = score
					best = id
			return best if best != &"" else home
		RC.ThreatRouting.WEAKEST_NODE:
			var best: StringName = &""
			var best_integrity := 1 << 30
			for id in candidates:
				var integrity := int(grid.site(id)["integrity"])
				if integrity < best_integrity and grid.distance(t["site"], id, grid_data) >= 0:
					best_integrity = integrity
					best = id
			return best if best != &"" else home
		_:
			return home


static func _move_threats(threats: Array[Dictionary], grid: GridState, grid_data: CityGridData, lookup: ContentLookup, step: int, result: RaidResult) -> void:
	for t in _active(threats):
		if t["hold"] > 0:
			t["hold"] -= 1
			result.events.append({"type": "held", "step": step, "threat": t["id"], "site": t["site"],
				"text": "Step %d: %s is held at %s (%d more)." % [step, t["name"], t["site"], t["hold"]]})
			continue
		var target := _target_of(t, grid, grid_data, lookup)
		var from: StringName = t["site"]
		if from == target and grid.is_active_node(target):
			continue  # camp on the target until it falls
		var moved := 0
		while moved < int(t["edges_per_step"]):
			var cur: StringName = t["site"]
			if cur == target:
				break
			var nxt := grid.next_hop(cur, target, grid_data)
			if nxt == cur:
				break
			t["site"] = nxt
			moved += 1
			if nxt == grid.home_site_id or grid.is_active_node(nxt):
				break  # a live node (or home) stops the advance this step
		if moved > 0:
			result.events.append({"type": "move", "step": step, "threat": t["id"], "from": from, "to": t["site"],
				"text": "Step %d: %s moves %s -> %s (toward %s)." % [step, t["name"], from, t["site"], target]})


static func _hold_threats(threats: Array[Dictionary], grid: GridState, lookup: ContentLookup, step: int, result: RaidResult) -> void:
	for t in _active(threats):
		var site: StringName = t["site"]
		if not grid.is_active_node(site) or t["hold"] > 0:
			continue
		var assets := grid.assets_on(site)
		for i in assets.size():
			var asset := lookup.get_content(assets[i]) as DefenseAssetData
			if asset == null or asset.delay_steps <= 0:
				continue
			var key := "%s#%d" % [site, i]
			if t["held_by"].has(key):
				continue
			t["held_by"].append(key)
			t["hold"] = asset.delay_steps
			result.events.append({"type": "ice_lock", "step": step, "threat": t["id"], "site": site,
				"text": "Step %d: ICE Lock on %s holds %s for %d step(s)." % [step, site, t["name"], asset.delay_steps]})
			break


static func _fire_assets(campaign: CampaignState, threats: Array[Dictionary], grid: GridState, grid_data: CityGridData, lookup: ContentLookup, step: int, result: RaidResult) -> void:
	for site in grid.claimed_ids():
		if not grid.is_active_node(site):
			continue
		var guns: Array[DefenseAssetData] = []
		if site == grid.home_site_id:
			for id in grid.home_built_in:
				var built := lookup.get_content(StringName(id)) as DefenseAssetData
				if built != null:
					guns.append(built)
		else:
			var node := lookup.get_content(grid.node_type_of(site)) as NetworkNodeData
			if node != null and node.built_in_asset != null:
				guns.append(node.built_in_asset)
		for a in grid.assets_on(site):
			var asset := lookup.get_content(a) as DefenseAssetData
			if asset != null:
				guns.append(asset)
		var station_mult := station_damage_multiplier(campaign, grid, grid_data, lookup, site)
		for gun in guns:
			if gun.damage <= 0:
				continue
			var damage := roundi(gun.damage * station_mult)
			for shot in gun.shots_per_step:
				var target := _pick_target(gun, site, threats, grid, grid_data)
				if target.is_empty():
					break
				target["integrity"] -= damage
				result.events.append({"type": "shot", "step": step, "site": site, "asset": gun.id, "threat": target["id"], "damage": damage,
					"text": "Step %d: %s at %s hits %s for %d (%d left)." % [step, gun.display_name if gun.display_name != "" else String(gun.id), site, target["name"], damage, maxi(0, target["integrity"])]})
				if target["integrity"] <= 0:
					result.events.append({"type": "threat_destroyed", "step": step, "threat": target["id"], "text": "Step %d: %s destroyed." % [step, target["name"]]})


## Station bonus (GDD 5.2, 5.3; numbers per designer ruling 2026-09-24): a stationed
## operative's class `station_bonus` DEAL_DAMAGE multiplier applies to the assets on its
## node and on adjacent Firewall Relays; Rank scales the bonus part by the class's
## RankRewardData.station_bonus_multiplier. The strongest applicable bonus wins.
static func station_damage_multiplier(campaign: CampaignState, grid: GridState, grid_data: CityGridData, lookup: ContentLookup, site: StringName) -> float:
	var best := 1.0
	var here_node := lookup.get_content(grid.node_type_of(site)) as NetworkNodeData
	var candidates: Array[StringName] = [site]
	if here_node != null and here_node.node_type == RC.NetworkNodeType.FIREWALL_RELAY:
		candidates.append_array(grid.neighbors(site, grid_data))
	for s in candidates:
		if not grid.is_active_node(s):
			continue
		var op_id := grid.stationed_on(s)
		if op_id == &"":
			continue
		var op := campaign.get_operative(op_id)
		if op == null or not op.alive:
			continue
		var cls := lookup.get_content(op.class_id) as ClassData
		if cls == null:
			continue
		for te in cls.station_bonus:
			if te == null:
				continue
			for e in te.effects:
				if e != null and e.type == RC.EffectType.DEAL_DAMAGE and e.multiplier > 1.0:
					best = maxf(best, 1.0 + (e.multiplier - 1.0) * op.station_multiplier(cls))
	return best


static func _pick_target(gun: DefenseAssetData, site: StringName, threats: Array[Dictionary], grid: GridState, grid_data: CityGridData) -> Dictionary:
	var best: Dictionary = {}
	var best_key := []
	for t in _active(threats):
		var d := grid.distance(site, t["site"], grid_data)
		if d < 0 or d > gun.range_hops:
			continue
		var key := []
		match int(gun.targeting):
			RC.AssetTargeting.LOWEST_INTEGRITY:
				key = [t["integrity"], grid.distance(t["site"], grid.home_site_id, grid_data), String(t["content_id"]), t["id"]]
			RC.AssetTargeting.HIGHEST_DAMAGE:
				key = [-t["damage"], grid.distance(t["site"], grid.home_site_id, grid_data), String(t["content_id"]), t["id"]]
			_:
				key = [grid.distance(t["site"], grid.home_site_id, grid_data), String(t["content_id"]), t["id"]]
		if best.is_empty() or _key_less(key, best_key):
			best = t
			best_key = key
	return best


static func _key_less(a: Array, b: Array) -> bool:
	for i in mini(a.size(), b.size()):
		if a[i] < b[i]:
			return true
		if a[i] > b[i]:
			return false
	return false


static func _damage_nodes(threats: Array[Dictionary], grid: GridState, grid_data: CityGridData, lookup: ContentLookup, config: CampaignConfigData, step: int, result: RaidResult, seized_now: Array[String], disabled_now: Array[String]) -> void:
	for t in _active(threats):
		var site: StringName = t["site"]
		var damage := int(t["damage"])
		if site == grid.home_site_id:
			grid.home_integrity = maxi(0, grid.home_integrity - damage)
			t["reached_home"] = true
			result.events.append({"type": "home_hit", "step": step, "threat": t["id"], "damage": damage,
				"text": "Step %d: %s reaches the HOME SERVER: -%d integrity (%d left)." % [step, t["name"], damage, grid.home_integrity]})
			continue
		if not grid.is_claimed(site):
			continue
		var s := grid.site(site)
		if int(s["condition"]) == GridState.Condition.DISABLED:
			_seize(grid, site, seized_now)
			result.events.append({"type": "seized", "step": step, "site": site, "text": "Step %d: %s hits Disabled %s -> SEIZED." % [step, t["name"], site]})
			continue
		var integrity := int(s["integrity"]) - damage
		if integrity > 0:
			s["integrity"] = integrity
			result.events.append({"type": "node_hit", "step": step, "site": site, "damage": damage,
				"text": "Step %d: %s damages %s for %d (%d left)." % [step, t["name"], site, damage, integrity]})
			continue
		var excess := -integrity
		s["integrity"] = 0
		s["condition"] = GridState.Condition.DISABLED
		if not disabled_now.has(String(site)):
			disabled_now.append(String(site))
		result.events.append({"type": "disabled", "step": step, "site": site, "text": "Step %d: %s DISABLED by %s." % [step, site, t["name"]]})
		_recall_from(s, site, step, result)
		var cascade := int(floor(excess * config.cascade_ratio))
		if cascade <= 0:
			continue
		for n in grid.neighbors(site, grid_data):
			if n == grid.home_site_id:
				grid.home_integrity = maxi(0, grid.home_integrity - cascade)
				result.events.append({"type": "cascade", "step": step, "site": n, "damage": cascade, "text": "Step %d: cascade hits HOME for %d (%d left)." % [step, cascade, grid.home_integrity]})
			elif grid.is_active_node(n):
				var ns := grid.site(n)
				ns["integrity"] = maxi(0, int(ns["integrity"]) - cascade)
				result.events.append({"type": "cascade", "step": step, "site": n, "damage": cascade, "text": "Step %d: cascade hits %s for %d (%d left)." % [step, n, cascade, ns["integrity"]]})
				if int(ns["integrity"]) == 0:
					ns["condition"] = GridState.Condition.DISABLED
					if not disabled_now.has(String(n)):
						disabled_now.append(String(n))
					_recall_from(ns, n, step, result)


## A stationed operative on a node that goes Disabled returns to the reserves unharmed
## (GDD 3.3); Seized nodes do the same through _seize + apply().
static func _recall_from(s: Dictionary, site: StringName, step: int, result: RaidResult) -> void:
	if String(s.get("stationed", "")) == "":
		return
	result.events.append({"type": "recalled", "step": step, "operative": s["stationed"], "site": site,
		"text": "Step %d: %s returns to the reserves from Disabled %s." % [step, s["stationed"], site]})
	s["stationed"] = ""


static func _seize(grid: GridState, site: StringName, seized_now: Array[String]) -> void:
	var s := grid.site(site)
	s["status"] = GridState.SiteStatus.SEIZED
	s["node_type"] = ""
	s["integrity"] = 0
	s["max_integrity"] = 0
	s["condition"] = GridState.Condition.OK
	s["assets"] = []
	s["stationed"] = ""
	if not seized_now.has(String(site)):
		seized_now.append(String(site))
