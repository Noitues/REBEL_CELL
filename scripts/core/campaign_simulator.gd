class_name CampaignSimulator
extends RefCounted
## Plays whole campaigns with simple, fair policies (CombatBot in fights) to measure
## pacing against GDD 11.8 and to catch soft-locks (gap analysis V4). Pure: builds its own
## CampaignState from content; same seed + ICE = same report.
##
## Policies: fight pending raids first with the Armory on home; patch home, repair, recruit to two
## living operatives, scrub Heat at 70+; claim one Firewall Relay next to home when rich;
## launch the highest-ranked operative at the breach when open, else an Exploit Site,
## else a Heat objective at Heat 50+, else the deepest Site its Rank allows (ties by id).
## In a run: avoid elites below half HP, visit a Modem with 75+ Cycles, take the first
## card while the deck is under 16, socket Firmware (never Heat-costing Burner) in the first slot that fits, take
## Daemons, pick the last (safest) event choice, remove Bug cards at Modems.

## GDD 11.8 time budget per netrun and per raid, for the hour estimate.
const MINUTES_PER_RUN := 15.0
const MINUTES_PER_RAID := 5.0
const MAX_TURNS_PER_FIGHT := 60
const MAX_STEPS_PER_RUN := 400

var resolver: CombatResolver
var lookup: ContentLookup
var config: CampaignConfigData
var corp: CorporationData
var class_data: ClassData
var home: HomeServerVariantData


func _init(p_resolver: CombatResolver, corporation_id: StringName = &"solace", class_id: StringName = &"breaker", home_id: StringName = &"home_standard") -> void:
	resolver = p_resolver
	lookup = p_resolver.lookup
	config = p_resolver.config
	corp = lookup.get_content(corporation_id) as CorporationData
	class_data = lookup.get_content(class_id) as ClassData
	home = lookup.get_content(home_id) as HomeServerVariantData


## Plays a campaign; returns the report dictionary (see _report()).
func run_campaign(campaign_seed: int, ice: int = 0, max_runs: int = 60) -> Dictionary:
	var c := CampaignRules.new_campaign(corp, config, lookup, campaign_seed, class_data, home.core, ice, home)
	var seeds := RngStreams.make_stream(campaign_seed, &"map")
	var stats := {"runs": 0, "completed": 0, "deaths": 0, "raids": 0, "heat_peak": 0, "stuck": 0, "turns": 0,
		"fights": 0, "runs_to_first_exploit": -1, "heat_at_breach": -1, "log": []}
	while not c.is_over() and int(stats["runs"]) < max_runs:
		_fight_raids(c, stats)
		if c.is_over():
			break
		_maintain(c)
		var pick := _pick_launch(c)
		if pick.is_empty():
			stats["log"].append("no launchable Site")
			break
		var op: OperativeState = pick["op"]
		var site: SiteData = pick["site"]
		var s := _start(c, op, site, seeds.randi())
		if site.objective == RC.SiteObjective.BOSS:
			stats["heat_at_breach"] = c.heat
		_play_run(s, stats)
		stats["runs"] = int(stats["runs"]) + 1
		if s.run.outcome == RunState.Outcome.COMPLETED:
			stats["completed"] = int(stats["completed"]) + 1
		elif s.run.outcome == RunState.Outcome.DIED:
			stats["deaths"] = int(stats["deaths"]) + 1
		if int(stats["runs_to_first_exploit"]) < 0 and not c.exploits.is_empty():
			stats["runs_to_first_exploit"] = stats["runs"]
		stats["heat_peak"] = maxi(int(stats["heat_peak"]), c.heat)
		stats["log"].append("run %d: %s R%d T%d %s -> %s, Heat %d, Exploits %d, home %d/%d, Schematics %d, armory %d" % [stats["runs"], op.name, op.rank, site.tier, site.id,
			RunState.Outcome.keys()[s.run.outcome], c.heat, c.exploits.size(), c.grid.home_integrity, c.grid.home_max_integrity, c.schematics, c.armory.size()])
	return _report(c, stats, campaign_seed, ice)


func _report(c: CampaignState, stats: Dictionary, campaign_seed: int, ice: int) -> Dictionary:
	var hours := (int(stats["runs"]) * MINUTES_PER_RUN + int(stats["raids"]) * MINUTES_PER_RAID) / 60.0
	return {"seed": campaign_seed, "ice": ice, "outcome": CampaignState.Outcome.keys()[c.outcome],
		"runs": stats["runs"], "completed": stats["completed"], "deaths": stats["deaths"], "raids": stats["raids"],
		"raids_won": c.raids_won, "raids_lost": c.raids_lost, "heat_peak": stats["heat_peak"], "heat_end": c.heat,
		"heat_at_breach": stats["heat_at_breach"], "exploits": c.exploits.size(), "runs_to_first_exploit": stats["runs_to_first_exploit"],
		"fights": stats["fights"], "turns": stats["turns"], "stuck": stats["stuck"], "est_hours": snappedf(hours, 0.01),
		"hash": c.state_hash(), "log": stats["log"]}


# --- Campaign policies -------------------------------------------------------------------------

func _fight_raids(c: CampaignState, stats: Dictionary) -> void:
	var guard := 0
	while not c.pending_raids.is_empty() and not c.is_over() and guard < 10:
		guard += 1
		_deploy_armory(c)
		var raid_id := String(c.pending_raids[0].get("raid_id", ""))
		CampaignRules.fight_raid(c, corp, config, lookup, c.pending_raids[0])
		stats["raids"] = int(stats["raids"]) + 1
		stats["log"].append("  raid %s: %s, home %d/%d" % [raid_id, "won" if bool(c.last_raid.get("won", false)) else "lost", c.grid.home_integrity, c.grid.home_max_integrity])
		stats["heat_peak"] = maxi(int(stats["heat_peak"]), c.heat)


## Armory assets go to the claimed nodes nearest home first (home, then by id).
func _deploy_armory(c: CampaignState) -> void:
	for site_id in c.grid.claimed_ids():
		while not c.armory.is_empty() and c.grid.is_active_node(site_id) \
				and c.grid.assets_on(site_id).size() < CampaignRules.asset_slots(c, lookup, site_id, config):
			if CampaignRules.deploy_asset(c, config, lookup, 0, site_id)[0]["type"] == "refused":
				break


func _maintain(c: CampaignState) -> void:
	for site_id in c.grid.claimed_ids():
		if c.grid.is_claimed(site_id) and int(c.grid.site(site_id).get("condition", 0)) == GridState.Condition.DISABLED:
			CampaignRules.repair(c, config, lookup, site_id)
	if c.grid.home_integrity < c.grid.home_max_integrity:
		CampaignRules.repair_home(c, config)
	while c.living_operatives().size() < 2 and c.schematics >= config.rookie_cost:
		CampaignRules.recruit(c, config, class_data)
	if c.heat >= 70 and c.schematics >= CampaignRules.heat_purchase_price(c, config):
		CampaignRules.buy_heat_reduction(c, config)
	var claimed := c.grid.claimed_ids().size() - 1
	var relay := lookup.get_content(&"firewall_relay") as NetworkNodeData
	if claimed < 1 and relay != null and c.schematics >= relay.install_cost + config.rookie_cost:
		for n in c.grid.neighbors(c.grid.home_site_id, corp.city_grid):
			var sd := corp.city_grid.get_site(n)
			if c.grid.is_cleared(n) and sd != null and sd.claimable:
				CampaignRules.claim(c, corp, config, lookup, n, relay.id)
				break


func _pick_launch(c: CampaignState) -> Dictionary:
	var ops := c.living_operatives()
	if ops.is_empty():
		return {}
	ops.sort_custom(func(a: OperativeState, b: OperativeState) -> bool: return a.rank > b.rank if a.rank != b.rank else String(a.id) < String(b.id))
	var best: Dictionary = {}
	var best_key := -1000000
	var targets := CampaignRules.launchable_sites(c, corp, config)
	targets.append_array(CampaignRules.patrol_sites(c, corp))
	for site in targets:
		if c.grid.is_seized(site.id):
			continue
		for op in ops:
			var cls := lookup.get_content(op.class_id) as ClassData
			if CampaignRules.launch_error(c, corp, config, op, cls, site) != "":
				continue
			var objective := CampaignRules.site_objective(c, site)
			var key := site.tier * 10
			if CampaignRules.is_patrol(c, site):
				objective = RC.SiteObjective.NONE  # a patrol holds no objective
				key -= 200  # only when nothing corporate is open to this operative
			match objective:
				RC.SiteObjective.BOSS:
					key += 1000
				RC.SiteObjective.EXPLOIT:
					key += 500
				RC.SiteObjective.HEAT_REDUCTION:
					key += 400 if c.heat >= 50 else -100
			if key > best_key:
				best_key = key
				best = {"op": op, "site": site}
			break
	return best


func _start(c: CampaignState, op: OperativeState, site: SiteData, run_seed: int) -> NetrunSession:
	match CampaignRules.run_kind_for(c, site):
		"boss":
			return NetrunSession.start_special(resolver, c, op.id, "boss", site.id, site.tier, run_seed, corp.final_boss.id, CampaignRules.boss_overrides(c, corp), corp)
		_:
			return NetrunSession.start(resolver, c, op.id, site.tier, site.id, run_seed, corp)


# --- Run policies ---------------------------------------------------------------------------------

func _play_run(s: NetrunSession, stats: Dictionary) -> void:
	var steps := 0
	while not s.run.is_over() and steps < MAX_STEPS_PER_RUN:
		steps += 1
		match s.run.phase:
			RunState.Phase.MAP:
				var next := _pick_node(s)
				if next == &"":
					break
				s.enter_node(next)
			RunState.Phase.COMBAT:
				stats["fights"] = int(stats["fights"]) + 1
				var turns := 0
				while s.in_combat() and turns < MAX_TURNS_PER_FIGHT:
					turns += 1
					CombatBot.play_turn(s.combat, s.combat_action)
				stats["turns"] = int(stats["turns"]) + turns
				if s.in_combat():
					stats["stuck"] = int(stats["stuck"]) + 1
					break
			RunState.Phase.REWARD:
				_take_reward(s)
			RunState.Phase.EVENT:
				s.choose_event_option(s.current_event().choices.size() - 1)
			RunState.Phase.SHOP:
				var bug := s.run.operative.deck.find(&"bug")
				if bug >= 0 and s.run.cycles >= s.card_removal_price():
					s.remove_card(bug)
				s.leave_shop()
			RunState.Phase.RAID:
				for i in range(s.run_assets().size() - 1, -1, -1):
					s.raid_deploy_run_asset(i, s.campaign.grid.home_site_id)
				s.raid_fight()
				stats["raids"] = int(stats["raids"]) + 1
			_:
				break


func _pick_node(s: NetrunSession) -> StringName:
	var hp_low := s.run.operative.hp * 2 < s.run.operative.max_hp
	var best: StringName = &""
	var best_key := -1000000000
	for id in s.available_nodes():
		var node := s.run.map.get_node(id)
		var key := 0
		match int(node["type"]):
			RC.InfilNodeType.SERVER_RACK:
				key = 50
			RC.InfilNodeType.MODEM:
				key = 60 if s.run.cycles >= 75 else 10
			RC.InfilNodeType.TERMINAL:
				key = 30 if hp_low else 20
			_:
				key = (0 if hp_low else 25) if node["elite"] else 40
		if key > best_key or (key == best_key and String(id) < String(best)):
			best_key = key
			best = id
	return best


func _take_reward(s: NetrunSession) -> void:
	var offer := s.current_reward()
	match String(offer["kind"]):
		"card":
			if s.run.operative.deck.size() < 16:
				s.choose_reward(0)
			else:
				s.skip_reward()
		"firmware":
			var fw := lookup.get_content(StringName(String(offer["options"][0]))) as FirmwareData
			if fw != null and _costs_heat(fw):
				s.skip_reward()
				return
			for slot in range(1, s.run.operative.slot_slice_ids.size()):
				if s.run.operative.slot_firmware_ids[slot] != &"":
					continue
				var ev := s.choose_reward(0, slot)
				if ev.is_empty() or ev[ev.size() - 1].get("type", "") != "refused":
					return
			s.skip_reward()
		_:
			s.choose_reward(0)


## Firmware whose triggers add Heat (Burner): the bot weighs it as a player would and passes.
static func _costs_heat(fw: FirmwareData) -> bool:
	for te in fw.triggered_effects:
		if te == null:
			continue
		for e in te.effects:
			if e != null and e.type == RC.EffectType.MODIFY_HEAT and e.amount > 0:
				return true
	return false
