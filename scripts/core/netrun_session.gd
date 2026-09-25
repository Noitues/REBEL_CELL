class_name NetrunSession
extends RefCounted
## One netrun from launch to completion or death (GDD 4.2, 6.3, 11): map movement,
## node contents, combats, rewards, Modem shops, Terminal events, banking and the
## campaign write-back. Pure data + rules; RunManager (autoload) wraps it.
##
## Randomness: the run's own RngStreams derived from the run seed. Stream use:
##   map     - map generation
##   combat  - enemy pick and each combat's seed
##   rewards - Cycles rolled, asset drops, reward offers, shop stock and prices
##   events  - Terminal event pick
## Every public method appends to `last_events` (plain dictionaries with "text").

const CYCLES_PER_SCHEMATIC_FALLBACK := 10
const BUG_CARD_ID := &"bug"

var config: CampaignConfigData
var lookup: ContentLookup
var resolver: CombatResolver
var campaign: CampaignState
## The corporation being run against (null in bare rule tests: no Grid effects then).
var corporation: CorporationData = null
var run: RunState
var streams: RngStreams
var combat: CombatSession = null
var last_events: Array[Dictionary] = []
var _pools: Dictionary = {}


# --- Lifecycle -------------------------------------------------------------------

## Launches a netrun for the roster operative `operative_id` at `tier`. MINOR Heat
## complications queued on the campaign are consumed here (shop stock, elite frequency).
static func start(p_resolver: CombatResolver, p_campaign: CampaignState, operative_id: StringName, tier: int, site_id: StringName, run_seed: int, corp: CorporationData = null) -> NetrunSession:
	var s := NetrunSession.new()
	s._bind(p_resolver, p_campaign)
	s.corporation = corp
	var op := p_campaign.get_operative(operative_id)
	if op == null or not op.alive:
		push_error("NetrunSession: no living operative '%s'." % operative_id)
		return null
	s.run = RunState.new()
	s.run.run_seed = run_seed
	s.run.tier = tier
	s.run.site_id = site_id
	s.run.operative = op.duplicate_state()
	s.streams = RngStreams.seeded(run_seed)
	var elite_pct := p_campaign.elite_frequency_pct(s.config)
	var shop_delta := 0
	for m in p_campaign.pending_complications:
		match int(m["type"]):
			RC.RuleModifierType.ELITE_FREQUENCY_PCT:
				elite_pct += float(m["value"])
			RC.RuleModifierType.SHOP_STOCK:
				shop_delta += int(m["value"])
	s.run.combat_overrides["shop_stock_delta"] = shop_delta
	p_campaign.pending_complications.clear()
	s.run.map = MapGenerator.generate(tier, s.config, s.streams.get_stream(&"map"), elite_pct)
	p_campaign.runs_started += 1
	s.last_events = [{"type": "run_start", "text": "Netrun started: %s, tier %d, seed %d." % [op.name, tier, run_seed]}]
	s._apply_bug_cards()
	s._apply_boosts()
	s._compiler_rack_bonus()
	s._maybe_raid_interlude()
	s._sync()
	return s


## Netrun boosts bought at HQ (GDD 11.4): starting Cycles, run-only cards, extra max RAM.
func _apply_boosts() -> void:
	for id in campaign.pending_boosts:
		var boost: NetrunBoostData = null
		for b in config.netrun_boosts:
			if b != null and b.id == id:
				boost = b
		if boost == null:
			continue
		run.cycles += boost.cycles
		for card in boost.temp_cards:
			if card != null:
				run.operative.deck.append(card.id)
				run.temp_cards.append(card.id)
		if boost.max_ram_bonus != 0:
			run.combat_overrides["max_ram"] = int(run.combat_overrides.get("max_ram", (lookup.get_content(run.operative.class_id) as ClassData).max_ram)) + boost.max_ram_bonus
		last_events.append({"type": "boost", "boost": boost.id, "text": "Boost: %s." % boost.display_name})
	campaign.pending_boosts.clear()


## Compiler Rack (GDD 3.2): a run launched next to an active one starts with a bonus card
## offer (one per adjacent Rack).
func _compiler_rack_bonus() -> void:
	if corporation == null:
		return
	var racks := CampaignRules.compiler_racks_next_to(campaign, corporation, lookup, run.site_id)
	for i in racks:
		_offer(&"card", _card_pool(), config.card_reward_choices, streams.get_stream(&"rewards"))
	if racks > 0:
		run.phase = RunState.Phase.REWARD
		last_events.append({"type": "compiler_rack", "count": racks, "text": "Compiler Rack: %d bonus card offer(s) before jacking in." % racks})


## A single-combat run (GDD 3.3 Reclaim, 11.7 final breach): one node, one fight.
static func start_special(p_resolver: CombatResolver, p_campaign: CampaignState, operative_id: StringName, kind: String, site_id: StringName, tier: int, run_seed: int, enemy_id: StringName, overrides: Dictionary, corp: CorporationData = null) -> NetrunSession:
	var s := NetrunSession.new()
	s._bind(p_resolver, p_campaign)
	s.corporation = corp
	var op := p_campaign.get_operative(operative_id)
	if op == null or not op.alive:
		push_error("NetrunSession: no living operative '%s'." % operative_id)
		return null
	s.run = RunState.new()
	s.run.run_seed = run_seed
	s.run.tier = tier
	s.run.site_id = site_id
	s.run.kind = kind
	s.run.forced_enemy_id = enemy_id
	s.run.combat_overrides = overrides.duplicate(true)
	s.run.operative = op.duplicate_state()
	s.streams = RngStreams.seeded(run_seed)
	var graph := MapGraph.new()
	graph.layers.append([{"id": MapGraph.make_id(1, 0), "layer": 1, "index": 0, "type": RC.InfilNodeType.SERVER_RACK,
		"elite": true, "next": [] as Array[StringName], "heat": 0}])
	s.run.map = graph
	p_campaign.runs_started += 1
	s.last_events = [{"type": "run_start", "text": "%s run started: %s vs %s." % [kind.capitalize(), op.name, enemy_id]}]
	s._apply_bug_cards()
	s._sync()
	return s


static func from_dict(p_resolver: CombatResolver, p_campaign: CampaignState, d: Dictionary, corp: CorporationData = null) -> NetrunSession:
	var s := NetrunSession.new()
	s._bind(p_resolver, p_campaign)
	s.corporation = corp
	s.run = RunState.from_dict(d.get("run", {}))
	s.streams = RngStreams.from_dict(s.run.streams)
	if not s.run.combat.is_empty():
		s.combat = CombatSession.from_dict(p_resolver, s.run.combat)
	return s


func to_dict() -> Dictionary:
	_sync()
	return {"run": run.to_dict()}


func state_hash() -> int:
	_sync()
	return run.state_hash()


func _bind(p_resolver: CombatResolver, p_campaign: CampaignState) -> void:
	resolver = p_resolver
	lookup = p_resolver.lookup
	config = p_resolver.config
	campaign = p_campaign
	_build_pools()


func _sync() -> void:
	run.streams = streams.to_dict()
	run.combat = combat.to_dict() if combat != null else {}


# --- Map -------------------------------------------------------------------------

## Node ids the operative may enter now (none during a raid interlude).
func available_nodes() -> Array[StringName]:
	if run.phase != RunState.Phase.MAP or run.is_over():
		return []
	if run.current_node_id == &"":
		return run.map.first_layer_ids()
	var out: Array[StringName] = []
	for n in run.current_node().get("next", []):
		out.append(n)
	return out


## Moves to `node_id` and opens whatever it holds. Returns the events.
func enter_node(node_id: StringName) -> Array[Dictionary]:
	last_events = []
	if not available_nodes().has(node_id):
		return _refuse("Node %s is not reachable from here." % node_id)
	var node := run.map.get_node(node_id)
	run.current_node_id = node_id
	run.visited.append(node_id)
	last_events.append({"type": "enter_node", "node": node_id, "node_type": node["type"],
		"text": "Entered %s (%s%s)." % [node_id, RC.InfilNodeType.keys()[node["type"]], ", elite" if node["elite"] and node["type"] != RC.InfilNodeType.SERVER_RACK else ""]})
	if node["elite"] and node["type"] != RC.InfilNodeType.SERVER_RACK and node["heat"] != 0:
		_add_heat(node["heat"], "elite node")
	match int(node["type"]):
		RC.InfilNodeType.ROUTER:
			_start_combat(node["elite"])
		RC.InfilNodeType.SERVER_RACK:
			_start_combat(true)
		RC.InfilNodeType.TERMINAL:
			_open_event()
		RC.InfilNodeType.MODEM:
			_open_shop()
	_sync()
	return last_events


# --- Combat ------------------------------------------------------------------------

func in_combat() -> bool:
	return run.phase == RunState.Phase.COMBAT and combat != null


## Forwards a player action to the live combat; settles the fight when it ends.
func combat_action(action: CombatAction) -> CombatResult:
	if not in_combat():
		var r := CombatResult.new()
		r.error = "Not in combat."
		return r
	var result := combat.apply(action)
	if result.ok():
		_apply_campaign_effects(result.events)
		if combat.state.is_over():
			last_events = []
			_finish_combat()
		_sync()
	return result


func combat_rewind() -> CombatResult:
	if not in_combat():
		var r := CombatResult.new()
		r.error = "Not in combat."
		return r
	var result := combat.rewind()
	_sync()
	return result


## Picks the enemy: the final Rack gets a mini-boss (designer ruling 2026-09-24), other
## elite nodes an elite, Routers a normal enemy; special runs force theirs.
func _start_combat(elite: bool) -> void:
	var final_rack := run.kind == "netrun" and run.current_node_id == run.map.final_node_id()
	var pool: Array = _pools["elites"] if elite else _pools["enemies"]
	if final_rack and not _pools["mini_bosses"].is_empty():
		pool = _pools["mini_bosses"]
	if pool.is_empty():
		pool = _pools["enemies"] if elite else _pools["elites"]
	var combat_rng := streams.get_stream(&"combat")
	var enemy_id: StringName = pool[combat_rng.randi_range(0, pool.size() - 1)]
	if run.forced_enemy_id != &"":
		enemy_id = run.forced_enemy_id
	var seed := combat_rng.randi()
	var op := run.operative
	var cls := lookup.get_content(op.class_id) as ClassData
	var overrides := {
		"slot_slice_ids": _strings(op.slot_slice_ids), "slot_firmware_ids": _strings(op.slot_firmware_ids),
		"ring_segment_ids": _strings(op.ring_segment_ids),
		"deck": _strings(op.deck), "daemon_ids": _strings(op.daemon_ids),
		"hp": op.hp, "max_hp": op.max_hp, "enemy_scale": enemy_scale(), "enemy_output_scale": enemy_output_scale(), "hub_id": String(op.hub_id(cls)),
	}
	for k in rule_overrides():
		overrides[k] = rule_overrides()[k]
	if campaign.is_assisted():
		overrides["extra_free_nudges"] = int(campaign.assist.get("free_nudges", 0))
	if not run.drones.is_empty():
		overrides["drones"] = run.drones.duplicate(true)
	for k in run.combat_overrides:
		if k != "shop_stock_delta":
			overrides[k] = run.combat_overrides[k]
	combat = CombatSession.start(resolver, op.class_id, [enemy_id], seed, op.ring_id(cls), campaign.heat_majors_crossed(config), overrides)
	run.phase = RunState.Phase.COMBAT
	last_events.append({"type": "combat_start", "enemy_id": enemy_id, "elite": elite, "mini_boss": final_rack,
		"text": "Combat: %s%s." % [enemy_id, " (mini-boss)" if final_rack else (" (elite)" if elite else "")]})
	_apply_campaign_effects(combat.last_events)


## GDD 11.6: enemy HP and damage scale by enemy_scale_per_tier^(tier - 1), for every
## enemy including mini-bosses and the final boss (designer ruling 2026-09-24).
func enemy_scale() -> float:
	return pow(config.enemy_scale_per_tier, run.tier - 1)


## Enemy slice outputs per tier (enemy_damage_scale_per_tier^(tier - 1)).
func enemy_output_scale() -> float:
	return pow(config.enemy_damage_scale_per_tier, run.tier - 1)


## Combat-side ICE and Heat rule modifiers (GDD 11.9, 4.3) as CombatResolver overrides:
## enemy resistance (Heat 50 / ICE 7), boss strength (ICE 9), the extra boss pointer
## (ICE 18), no free nudge on turn 1 (ICE 12) and the campaign Heat for gated behaviour.
func rule_overrides() -> Dictionary:
	return {
		"enemy_resistance": int(campaign.rule_modifier(config, RC.RuleModifierType.ENEMY_RESISTANCE)),
		"boss_strength_pct": campaign.rule_modifier(config, RC.RuleModifierType.BOSS_STRENGTH_PCT),
		"boss_extra_pointer": int(campaign.rule_modifier(config, RC.RuleModifierType.BOSS_EXTRA_POINTER)),
		"no_first_turn_free_nudge": campaign.rule_modifier(config, RC.RuleModifierType.NO_FIRST_TURN_FREE_NUDGE) > 0.0,
		"heat": campaign.heat,
	}


## ICE 11 STARTING_BUG_CARD: the working deck carries at least N Bug cards (a Modem can
## remove them; removal is the counterplay). Applied at run start.
func _apply_bug_cards() -> void:
	var wanted := int(campaign.rule_modifier(config, RC.RuleModifierType.STARTING_BUG_CARD))
	if wanted <= 0 or not lookup.has(BUG_CARD_ID):
		return
	var have := run.operative.deck.count(BUG_CARD_ID)
	for i in wanted - have:
		run.operative.deck.append(BUG_CARD_ID)
	if wanted > have:
		last_events.append({"type": "bug_cards", "amount": wanted - have, "text": "ICE: %d Bug card(s) infest the deck." % (wanted - have)})


func reward_scale() -> float:
	return pow(config.reward_scale_per_tier, run.tier - 1)


func _finish_combat() -> void:
	var cs := combat.state
	var node := run.current_node()
	if cs.outcome == CombatState.Outcome.DEFEAT:
		combat = null
		_die()
		return
	run.operative.hp = cs.player.hp
	run.miss_resolved = run.miss_resolved or cs.miss_resolved
	# Daemons with ON_COMBAT_END effects (salvage, field repairs) after a won fight.
	_apply_hook_effects(_run_daemon_hooks(RC.Trigger.ON_COMBAT_END))
	# Botnet (GDD 5.2): surviving drones ride along to the next fight of the run.
	run.drones.clear()
	var hub := lookup.get_content(cs.player.wheel.hub_id) as HubCoreData if cs.player.wheel.hub_id != &"" else null
	if hub != null and hub.drones_persist:
		for d in cs.living_drones():
			run.drones.append({"source_id": String(d.source_id), "hp": d.hp, "dock_slot": d.dock_slot})
	run.combats_won += 1
	var elite: bool = node["elite"]
	var is_rack: bool = node["type"] == RC.InfilNodeType.SERVER_RACK
	if elite:
		run.elites_defeated += 1
	var rewards := streams.get_stream(&"rewards")
	var range_: Vector2i = config.cycles_elite_range if elite else config.cycles_router_range
	if run.kind == "reclaim":
		range_ = config.cycles_combat_range  # tiny rewards (GDD 3.3)
	var cycles := roundi(rewards.randi_range(range_.x, range_.y) * reward_scale())
	run.cycles += cycles
	last_events.append({"type": "cycles", "amount": cycles, "text": "Won the fight: +%d Cycles (%d)." % [cycles, run.cycles]})
	if rewards.randf() < config.asset_drop_chance and not _pools["assets"].is_empty():
		var asset: StringName = _pools["assets"][rewards.randi_range(0, _pools["assets"].size() - 1)]
		run.unbanked_assets.append(asset)
		last_events.append({"type": "asset_drop", "asset": asset, "text": "Found a defense asset: %s (unbanked until a Server Rack)." % asset})
	if run.kind != "netrun":
		combat = null
		_complete_run()
		return
	_offer(&"card", _card_pool(), config.card_reward_choices, rewards)
	if elite and not is_rack:
		_offer(&"firmware", _pools["firmware"], config.elite_firmware_choices, rewards)
	elif not elite and rewards.randf() < config.router_firmware_chance:
		_offer(&"firmware", _pools["common_firmware"], config.router_firmware_choices, rewards)
	if is_rack:
		_capture_rack()
		var daemons: Array = []
		for d in _pools["daemons"]:
			if not run.operative.daemon_ids.has(d):
				daemons.append(d)
		_offer(&"daemon", daemons, config.rack_daemon_choices, rewards)
	combat = null
	if is_rack and run.current_node_id == run.map.final_node_id():
		_complete_run()
		return
	run.phase = RunState.Phase.REWARD if not run.pending_rewards.is_empty() else RunState.Phase.MAP
	_maybe_raid_interlude()


## Server Rack capture (GDD 4.2, 11.5): bank Schematics and assets, add Heat (or what a
## Daemon says instead), fire ON_SERVER_RACK_CAPTURE hooks.
func _capture_rack() -> void:
	var tier_index := clampi(run.tier - 1, 0, 3)
	var schematics := config.rack_schematics_by_tier[tier_index]
	run.banked_schematics += schematics
	run.banked_assets.append_array(run.unbanked_assets)
	run.unbanked_assets.clear()
	last_events.append({"type": "rack_captured", "schematics": schematics,
		"text": "Server Rack captured: %d Schematics banked (%d total), assets banked." % [schematics, run.banked_schematics]})
	var heat := config.rack_heat_by_tier[tier_index]
	var hooks := _run_daemon_hooks(RC.Trigger.ON_SERVER_RACK_CAPTURE)
	for e in hooks:
		if e.get("type", "") == "heat_override":
			heat = int(e["amount"])
	_add_heat(heat, "Server Rack")
	_apply_hook_effects(hooks)


func _offer(kind: StringName, pool: Array, count: int, rng: RandomNumberGenerator) -> void:
	if pool.is_empty() or count <= 0:
		return
	var remaining: Array = pool.duplicate()
	var options := []
	for i in mini(count, remaining.size()):
		var idx := rng.randi_range(0, remaining.size() - 1)
		options.append(String(remaining[idx]))
		remaining.remove_at(idx)
	run.pending_rewards.append({"kind": String(kind), "options": options})
	last_events.append({"type": "reward_offer", "kind": kind, "options": options,
		"text": "Choose a %s: %s (or skip)." % [kind, ", ".join(options)]})


# --- Rewards -----------------------------------------------------------------------

func current_reward() -> Dictionary:
	return run.pending_rewards[0] if not run.pending_rewards.is_empty() else {}


## Takes option `index` of the current offer. Firmware needs the wheel `slot` to socket.
func choose_reward(index: int, slot: int = -1) -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.REWARD or run.pending_rewards.is_empty():
		return _refuse("No reward to choose.")
	var offer := run.pending_rewards[0]
	var options: Array = offer["options"]
	if index < 0 or index >= options.size():
		return _refuse("No such option.")
	var id := StringName(String(options[index]))
	var err := _grant(String(offer["kind"]), id, slot)
	if err != "":
		return _refuse(err)
	run.pending_rewards.pop_front()
	_after_reward()
	_sync()
	return last_events


func skip_reward() -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.REWARD or run.pending_rewards.is_empty():
		return _refuse("No reward to skip.")
	run.pending_rewards.pop_front()
	last_events.append({"type": "reward_skipped", "text": "Reward skipped."})
	_after_reward()
	_sync()
	return last_events


func _after_reward() -> void:
	if run.pending_rewards.is_empty():
		run.phase = RunState.Phase.MAP
		_maybe_raid_interlude()


## Gives `id` of `kind` to the operative. Returns an error string when it cannot.
func _grant(kind: String, id: StringName, slot: int) -> String:
	match kind:
		"card":
			run.operative.deck.append(id)
			last_events.append({"type": "card_gained", "card": id, "text": "Added %s to the deck." % id})
		"firmware":
			var fw := lookup.get_content(id) as FirmwareData
			if fw == null:
				return "Unknown Firmware."
			if slot < 0 or slot >= run.operative.slot_slice_ids.size():
				return "Choose a wheel slot for the Firmware."
			var slice := lookup.get_content(run.operative.slot_slice_ids[slot]) as SliceData
			if not fw.allowed_slice_types.is_empty() and not (slice.slice_type in fw.allowed_slice_types):
				return "%s does not fit a %s slice." % [id, RC.SliceType.keys()[slice.slice_type]]
			run.operative.slot_firmware_ids[slot] = id
			last_events.append({"type": "firmware_socketed", "firmware": id, "slot": slot, "text": "Socketed %s into slot %d." % [id, slot]})
		"daemon":
			if run.operative.daemon_ids.has(id):
				return "Already installed."
			run.operative.daemon_ids.append(id)
			last_events.append({"type": "daemon_gained", "daemon": id, "text": "Daemon installed: %s." % id})
		"asset":
			run.unbanked_assets.append(id)
			last_events.append({"type": "asset_drop", "asset": id, "text": "Found a defense asset: %s." % id})
		_:
			return "Unknown reward kind %s." % kind
	return ""


# --- Terminal events ---------------------------------------------------------------

func current_event() -> TerminalEventData:
	return (lookup.get_content(run.event_id) as TerminalEventData) if run.event_id != &"" else null


func _open_event() -> void:
	var pool: Array = []
	for id in _pools["events"]:
		if (lookup.get_content(id) as TerminalEventData).min_tier <= run.tier:
			pool.append(id)
	if pool.is_empty():
		last_events.append({"type": "event_none", "text": "The Terminal is silent."})
		run.phase = RunState.Phase.MAP
		return
	var rng := streams.get_stream(&"events")
	# Weighted pick, deterministic in pool (id) order.
	var total := 0.0
	for id in pool:
		total += (lookup.get_content(id) as TerminalEventData).weight
	var roll := rng.randf() * total
	var chosen: StringName = pool[pool.size() - 1]
	for id in pool:
		roll -= (lookup.get_content(id) as TerminalEventData).weight
		if roll <= 0.0:
			chosen = id
			break
	run.event_id = chosen
	run.phase = RunState.Phase.EVENT
	var ev := lookup.get_content(chosen) as TerminalEventData
	last_events.append({"type": "event", "event_id": chosen, "text": "Terminal: %s" % ev.title})


## Picks choice `index` of the open event.
func choose_event_option(index: int) -> Array[Dictionary]:
	last_events = []
	var ev := current_event()
	if run.phase != RunState.Phase.EVENT or ev == null:
		return _refuse("No event open.")
	if index < 0 or index >= ev.choices.size():
		return _refuse("No such choice.")
	var choice := ev.choices[index]
	if choice.cycle_cost > run.cycles:
		return _refuse("Not enough Cycles (%d needed)." % choice.cycle_cost)
	run.cycles -= choice.cycle_cost
	run.operative.hp = maxi(0, run.operative.hp - choice.hp_cost)
	last_events.append({"type": "event_choice", "label": choice.label, "text": "%s -> %s" % [choice.label, choice.result_text]})
	for e in choice.effects:
		if e != null:
			_apply_run_effect(e)
	if choice.reward != null:
		_grant_resource(choice.reward)
	run.event_id = &""
	if run.operative.hp <= 0:
		_die()
		_sync()
		return last_events
	run.phase = RunState.Phase.REWARD if not run.pending_rewards.is_empty() else RunState.Phase.MAP
	_maybe_raid_interlude()
	_sync()
	return last_events


func _apply_run_effect(e: EffectData) -> void:
	match e.type:
		RC.EffectType.GAIN_CYCLES:
			run.cycles = maxi(0, run.cycles + e.amount)
			last_events.append({"type": "cycles", "amount": e.amount, "text": "Cycles %+d (%d)." % [e.amount, run.cycles]})
		RC.EffectType.MODIFY_HEAT:
			_add_heat(e.amount, "event")
		RC.EffectType.HEAL:
			var healed := mini(e.amount, run.operative.max_hp - run.operative.hp)
			run.operative.hp += healed
			last_events.append({"type": "heal", "amount": healed, "text": "Healed %d (%d/%d)." % [healed, run.operative.hp, run.operative.max_hp]})
		RC.EffectType.DEAL_DAMAGE:
			run.operative.hp = maxi(0, run.operative.hp - e.amount)
			last_events.append({"type": "damage", "amount": e.amount, "text": "Took %d damage (%d HP)." % [e.amount, run.operative.hp]})
		RC.EffectType.GAIN_SCHEMATICS:
			run.banked_schematics += e.amount
			last_events.append({"type": "schematics", "amount": e.amount, "text": "Schematics %+d banked." % e.amount})
		_:
			last_events.append({"type": "unsupported_effect", "text": "Run-level effect %s ignored." % RC.EffectType.keys()[e.type]})


func _grant_resource(res: Resource) -> void:
	if res is CardData:
		_grant("card", res.id, -1)
	elif res is FirmwareData:
		run.pending_rewards.append({"kind": "firmware", "options": [String(res.id)]})
	elif res is DaemonData:
		_grant("daemon", res.id, -1)
	elif res is DefenseAssetData:
		_grant("asset", res.id, -1)
	elif res is ClassData:
		var rescued := campaign.recruit(_rescue_class(res as ClassData))
		last_events.append({"type": "rescued", "operative": rescued.id, "text": "Rescued operative %s joins the roster." % rescued.name})



## A rescued operative (GDD 5.4) is one of the classes already on the roster (ids sorted,
## seeded "events" draw): rescues never bypass the Profile class unlocks. `fallback` when
## the roster is empty.
func _rescue_class(fallback: ClassData) -> ClassData:
	var ids: Array[String] = []
	for op in campaign.roster:
		if not ids.has(String(op.class_id)):
			ids.append(String(op.class_id))
	if ids.is_empty():
		return fallback
	ids.sort()
	var pick := lookup.get_content(StringName(ids[streams.get_stream(&"events").randi_range(0, ids.size() - 1)])) as ClassData
	return pick if pick != null else fallback

# --- Modem shop ----------------------------------------------------------------------

func _open_shop() -> void:
	var rng := streams.get_stream(&"rewards")
	var stock := {"cards": [], "card_prices": [], "firmware": [], "firmware_prices": [], "daemons": [], "daemon_prices": [], "slices": []}
	var card_count := maxi(1, 3 + int(run.combat_overrides.get("shop_stock_delta", 0)))
	_stock(stock, "cards", "card_prices", _card_pool(), card_count, config.card_price_range, rng)
	_stock(stock, "firmware", "firmware_prices", _pools["firmware"], 2, config.firmware_price_range, rng)
	var daemons: Array = []
	for d in _pools["daemons"]:
		if not run.operative.daemon_ids.has(d):
			daemons.append(d)
	_stock(stock, "daemons", "daemon_prices", daemons, 1, config.daemon_price_range, rng)
	# Slice overwrites come from the config catalogue (designer ruling 2026-09-24).
	var catalogue: Array = []
	for slice in config.shop_slices:
		if slice != null:
			catalogue.append(slice.id)
	var remaining: Array = catalogue.duplicate()
	for i in mini(config.shop_slice_choices, remaining.size()):
		var idx := rng.randi_range(0, remaining.size() - 1)
		stock["slices"].append(String(remaining[idx]))
		remaining.remove_at(idx)
	run.shop = stock
	run.phase = RunState.Phase.SHOP
	last_events.append({"type": "shop", "text": "Modem: %d cards, %d Firmware, %d Daemon(s) for sale." % [stock["cards"].size(), stock["firmware"].size(), stock["daemons"].size()]})


func _stock(stock: Dictionary, key: String, price_key: String, pool: Array, count: int, price_range: Vector2i, rng: RandomNumberGenerator) -> void:
	var remaining: Array = pool.duplicate()
	for i in mini(count, remaining.size()):
		var idx := rng.randi_range(0, remaining.size() - 1)
		stock[key].append(String(remaining[idx]))
		stock[price_key].append(roundi(rng.randi_range(price_range.x, price_range.y) * _price_scale()))
		remaining.remove_at(idx)


## CYCLE_PRICE_PCT (ICE 4): every Modem price scales with it.
func _price_scale() -> float:
	return 1.0 + campaign.rule_modifier(config, RC.RuleModifierType.CYCLE_PRICE_PCT) / 100.0


func card_removal_price() -> int:
	return roundi((config.card_removal_price + config.card_removal_increment * run.card_removals) * _price_scale())


func slice_overwrite_price(slot: int) -> int:
	var slice := lookup.get_content(run.operative.slot_slice_ids[slot]) as SliceData
	var base := config.miss_slice_overwrite_price if slice.slice_type == RC.SliceType.MISS else config.slice_overwrite_price
	return roundi(base * _price_scale())


## Buys stock item `index` of `kind` ("cards", "firmware", "daemons"); Firmware needs `slot`.
func buy(kind: String, index: int, slot: int = -1) -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.SHOP:
		return _refuse("No shop open.")
	var items: Array = run.shop.get(kind, [])
	var prices: Array = run.shop.get(kind.trim_suffix("s") + "_prices", [])
	if index < 0 or index >= items.size():
		return _refuse("No such item.")
	var price := int(prices[index])
	if run.cycles < price:
		return _refuse("Not enough Cycles (%d needed, %d held)." % [price, run.cycles])
	var reward_kind := kind.trim_suffix("s")
	var err := _grant(reward_kind, StringName(String(items[index])), slot)
	if err != "":
		return _refuse(err)
	run.cycles -= price
	items.remove_at(index)
	prices.remove_at(index)
	last_events.append({"type": "purchase", "kind": kind, "price": price, "text": "Bought for %d Cycles (%d left)." % [price, run.cycles]})
	_sync()
	return last_events


## Removes the deck card at `deck_index` for the current removal price.
func remove_card(deck_index: int) -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.SHOP:
		return _refuse("No shop open.")
	if deck_index < 0 or deck_index >= run.operative.deck.size():
		return _refuse("No such card.")
	var price := card_removal_price()
	if run.cycles < price:
		return _refuse("Not enough Cycles (%d needed)." % price)
	var removed := run.operative.deck[deck_index]
	run.operative.deck.remove_at(deck_index)
	run.cycles -= price
	run.card_removals += 1
	last_events.append({"type": "card_removed", "card": removed, "price": price, "text": "Removed %s for %d Cycles." % [removed, price]})
	_sync()
	return last_events


## Overwrites wheel slot `slot` with shop slice `stock_index` (100 Cycles; 150 for the Miss slot).
func overwrite_slice(slot: int, stock_index: int) -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.SHOP:
		return _refuse("No shop open.")
	var slices: Array = run.shop.get("slices", [])
	if slot < 0 or slot >= run.operative.slot_slice_ids.size() or stock_index < 0 or stock_index >= slices.size():
		return _refuse("No such slot or slice.")
	var price := slice_overwrite_price(slot)
	if run.cycles < price:
		return _refuse("Not enough Cycles (%d needed)." % price)
	var new_id := StringName(String(slices[stock_index]))
	var fw_id := run.operative.slot_firmware_ids[slot]
	if fw_id != &"":
		var fw := lookup.get_content(fw_id) as FirmwareData
		var slice := lookup.get_content(new_id) as SliceData
		if not fw.allowed_slice_types.is_empty() and not (slice.slice_type in fw.allowed_slice_types):
			return _refuse("Socketed %s would not fit the new slice." % fw_id)
	run.operative.slot_slice_ids[slot] = new_id
	run.cycles -= price
	last_events.append({"type": "slice_overwritten", "slot": slot, "slice": new_id, "price": price, "text": "Slot %d is now %s (%d Cycles)." % [slot, new_id, price]})
	_sync()
	return last_events


func leave_shop() -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.SHOP:
		return _refuse("No shop open.")
	run.shop = {}
	run.phase = RunState.Phase.MAP
	last_events.append({"type": "shop_left", "text": "Left the Modem."})
	_maybe_raid_interlude()
	_sync()
	return last_events


# --- Mid-run raid interlude (GDD 4.4, 7.3) ---------------------------------------------------

## Whenever the run would return to the map with a raid queued on the campaign, the raid
## is fought first. Needs the corporation (bare rule tests have none: no interludes).
func _maybe_raid_interlude() -> void:
	if corporation == null or run.phase != RunState.Phase.MAP or campaign.pending_raids.is_empty() or run.is_over():
		return
	run.phase = RunState.Phase.RAID
	var raid := CampaignRules.raid_data(campaign.pending_raids[0], lookup)
	last_events.append({"type": "raid_interlude", "raid_id": raid.id if raid != null else &"",
		"text": "RAID INTERLUDE: %s. %s" % [raid.display_name if raid != null else "?", raid.warning_text if raid != null else ""]})


func in_raid() -> bool:
	return run.phase == RunState.Phase.RAID


func raid_pending() -> Dictionary:
	return CampaignRules.pending_raid(campaign)


func raid_projection() -> RaidResolver.RaidResult:
	return CampaignRules.project_raid(campaign, corporation, config, lookup, raid_pending()) if in_raid() else null


## Assets the run carries (banked first, then unbanked), usable in a mid-run raid (7.3).
func run_assets() -> Array[StringName]:
	var out: Array[StringName] = run.banked_assets.duplicate()
	out.append_array(run.unbanked_assets)
	return out


## Deploys one of the run's own assets onto a node; it stays there afterwards.
func raid_deploy_run_asset(index: int, site_id: StringName) -> Array[Dictionary]:
	last_events = []
	if not in_raid():
		return _refuse("No raid in progress.")
	var assets := run_assets()
	if index < 0 or index >= assets.size():
		return _refuse("No such run asset.")
	var asset := assets[index]
	# Route through the Armory rules so slots and node state are checked the same way.
	campaign.armory.append(asset)
	var events := CampaignRules.deploy_asset(campaign, config, lookup, campaign.armory.size() - 1, site_id)
	if events[0]["type"] == "refused":
		campaign.armory.pop_back()
		last_events.append_array(events)
		return last_events
	if index < run.banked_assets.size():
		run.banked_assets.remove_at(index)
	else:
		run.unbanked_assets.remove_at(index - run.banked_assets.size())
	last_events.append_array(events)
	_sync()
	return last_events


func raid_deploy_armory(index: int, site_id: StringName) -> Array[Dictionary]:
	last_events = []
	if not in_raid():
		return _refuse("No raid in progress.")
	last_events.append_array(CampaignRules.deploy_asset(campaign, config, lookup, index, site_id))
	_sync()
	return last_events


func raid_move(from_site: StringName, index: int, to_site: StringName) -> Array[Dictionary]:
	last_events = []
	if not in_raid():
		return _refuse("No raid in progress.")
	last_events.append_array(CampaignRules.move_asset(campaign, config, lookup, from_site, index, to_site))
	_sync()
	return last_events


## Plays the raid out; the run continues on the map unless the home server fell.
func raid_fight() -> Array[Dictionary]:
	last_events = []
	if not in_raid():
		return _refuse("No raid in progress.")
	last_events.append_array(CampaignRules.fight_raid(campaign, corporation, config, lookup, raid_pending()))
	if campaign.is_over():
		run.outcome = RunState.Outcome.ABORTED
		run.phase = RunState.Phase.ENDED
		last_events.append({"type": "run_aborted", "text": "The run is over: the home server is gone."})
	else:
		run.phase = RunState.Phase.MAP
		_maybe_raid_interlude()
	_sync()
	return last_events


# --- Ending ------------------------------------------------------------------------------

## Completion (GDD 4.2): Cycles convert 10:1, the operative keeps everything, heals,
## gains a Rank; banked Schematics and assets reach the campaign.
func _complete_run() -> void:
	run.outcome = RunState.Outcome.COMPLETED
	run.phase = RunState.Phase.ENDED
	var converted := int(run.cycles / config.cycles_per_schematic)
	campaign.schematics += run.banked_schematics + converted
	var op := run.operative.duplicate_state()
	op.hp = op.max_hp
	# Rank = full netruns survived (decision 2026-09-24): Reclaim runs are one fight and do
	# not count; the final breach ends the campaign.
	if run.kind == "netrun":
		op.rank += 1
	op.runs_completed += 1
	for card in run.temp_cards:
		op.deck.erase(card)
	_replace_in_roster(op)
	_bank_assets_to_armory()
	campaign.runs_completed += 1
	last_events.append({"type": "run_complete", "schematics": run.banked_schematics + converted, "rank": op.rank,
		"text": "Netrun complete. %d Cycles -> %d Schematics; +%d banked; %s is now Rank %d." % [run.cycles, converted, run.banked_schematics, op.name, op.rank]})
	for e in _run_daemon_hooks(RC.Trigger.ON_NETRUN_COMPLETE):
		if e.get("type", "") == "campaign_effect" and int(e.get("effect", -1)) == RC.EffectType.MODIFY_HEAT:
			_add_heat(int(e["amount"]), String(e.get("source_id", "daemon")))
	if corporation != null:
		last_events.append_array(CampaignRules.on_run_completed(campaign, corporation, config, run, lookup))


## Death (GDD 4.2): permadeath, unbanked loot lost, banked loot kept, Heat +10 + tier.
func _die() -> void:
	run.outcome = RunState.Outcome.DIED
	run.phase = RunState.Phase.ENDED
	var op := campaign.get_operative(run.operative.id)
	if op != null:
		op.alive = false
		op.hp = 0
	campaign.deaths += 1
	campaign.schematics += run.banked_schematics
	_bank_assets_to_armory()
	var lost := run.unbanked_assets.size()
	run.unbanked_assets.clear()
	last_events.append({"type": "run_died", "text": "%s is flatlined. Unbanked loot lost (%d Cycles, %d asset(s)); %d banked Schematics kept." % [run.operative.name, run.cycles, lost, run.banked_schematics]})
	var extra := int(campaign.rule_modifier(config, RC.RuleModifierType.DEATH_HEAT))
	_add_heat(config.death_heat_base + run.tier + extra, "operative death")


func _replace_in_roster(op: OperativeState) -> void:
	for i in campaign.roster.size():
		if campaign.roster[i].id == op.id:
			campaign.roster[i] = op
			return
	campaign.roster.append(op)


func _bank_assets_to_armory() -> void:
	for a in run.banked_assets:
		if campaign.armory.size() >= config.armory_capacity:
			last_events.append({"type": "armory_full", "asset": a, "text": "Armory full (%d): %s discarded." % [config.armory_capacity, a]})
			continue
		campaign.armory.append(a)
	run.banked_assets.clear()


# --- Heat and Daemon hooks -----------------------------------------------------------------

func _add_heat(delta: int, reason: String) -> void:
	if delta == 0:
		return
	var before := campaign.heat
	var events := HeatRules.add_heat(campaign, delta, config, reason)
	run.heat_gained += campaign.heat - before
	last_events.append_array(events)


## Campaign-level effects reported by combat (Burner, Clean Signal).
func _apply_campaign_effects(events: Array[Dictionary]) -> void:
	for e in events:
		if e.get("type", "") == "campaign_effect":
			match int(e.get("effect", -1)):
				RC.EffectType.MODIFY_HEAT:
					_add_heat(int(e["amount"]), String(e.get("source_id", "combat")))
				RC.EffectType.GAIN_CYCLES:
					run.cycles = maxi(0, run.cycles + int(e["amount"]))
				RC.EffectType.GAIN_SCHEMATICS:
					run.banked_schematics += int(e["amount"])


## Applies data-driven Daemon hook results (from _run_daemon_hooks): Heat, Cycles,
## banked Schematics and healing the operative.
func _apply_hook_effects(hooks: Array[Dictionary]) -> void:
	for e in hooks:
		if e.get("type", "") != "campaign_effect":
			continue
		var amount := int(e.get("amount", 0))
		match int(e.get("effect", -1)):
			RC.EffectType.MODIFY_HEAT:
				_add_heat(amount, String(e.get("source_id", "daemon")))
			RC.EffectType.GAIN_CYCLES:
				run.cycles = maxi(0, run.cycles + amount)
			RC.EffectType.GAIN_SCHEMATICS:
				run.banked_schematics += amount
			RC.EffectType.HEAL:
				run.operative.hp = mini(run.operative.max_hp, run.operative.hp + amount)


## Runs the operative's Daemons for a run-level trigger: data-driven effects with that
## trigger and custom handlers. Returns the events (heat overrides included).
func _run_daemon_hooks(trigger: int) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in run.operative.daemon_ids:
		var d := lookup.get_content(id) as DaemonData
		if d == null:
			continue
		for te in d.triggered_effects:
			if te != null and te.trigger == trigger:
				for e in te.effects:
					if e != null:
						out.append({"type": "campaign_effect", "effect": e.type, "amount": e.amount, "source_id": d.id,
							"text": "%s: %s %+d." % [d.id, RC.EffectType.keys()[e.type], e.amount]})
		if d.custom_handler != null:
			out.append_array(d.custom_handler.new().handle({"trigger": trigger, "source_id": d.id, "run": run}, run, streams.get_stream(&"events")))
	for e in out:
		last_events.append(e)
	return out


# --- Pools ---------------------------------------------------------------------------------

func _build_pools() -> void:
	var enemies: Array = []
	var elites: Array = []
	var mini_bosses: Array = []
	for id in lookup.ids_of_class(&"EnemyData"):
		var e := lookup.get_content(id) as EnemyData
		if e.corporation_id != campaign.corporation_id or e.is_boss or e.wheel == null or e.wheel.slice_count != RC.SLICES:
			continue
		if e.is_mini_boss:
			mini_bosses.append(id)
		elif e.is_elite:
			elites.append(id)
		else:
			enemies.append(id)
	var shared_cards: Array = []
	var class_cards := {}
	for id in lookup.ids_of_class(&"CardData"):
		var c := lookup.get_content(id) as CardData
		if not c.offered:
			continue
		if c.class_id == &"":
			shared_cards.append(id)
		else:
			class_cards.get_or_add(c.class_id, []).append(id)
	var events: Array = []
	for id in lookup.ids_of_class(&"TerminalEventData"):
		var ev := lookup.get_content(id) as TerminalEventData
		if (ev.corporation_id == &"" or ev.corporation_id == campaign.corporation_id):
			events.append(id)
	# Built-in node defenses (Firewall turret) are not loot.
	var built_in := {}
	for id in lookup.ids_of_class(&"NetworkNodeData"):
		var node := lookup.get_content(id) as NetworkNodeData
		if node != null and node.built_in_asset != null:
			built_in[node.built_in_asset.id] = true
	var assets: Array = []
	for id in lookup.ids_of_class(&"DefenseAssetData"):
		if not built_in.has(id):
			assets.append(id)
	var common_firmware: Array = []
	for id in lookup.ids_of_class(&"FirmwareData"):
		if (lookup.get_content(id) as FirmwareData).rarity == RC.Rarity.COMMON:
			common_firmware.append(id)
	_pools = {
		"enemies": enemies, "elites": elites, "mini_bosses": mini_bosses, "shared_cards": shared_cards, "class_cards": class_cards,
		"firmware": lookup.ids_of_class(&"FirmwareData"), "common_firmware": common_firmware,
		"daemons": lookup.ids_of_class(&"DaemonData"), "assets": assets, "events": events,
	}


func _card_pool() -> Array:
	var out: Array = _pools["shared_cards"].duplicate()
	var cls := lookup.get_content(run.operative.class_id) as ClassData
	out.append_array(_pools["class_cards"].get(cls.pool_class_id() if cls != null else run.operative.class_id, []))
	return out


func pools() -> Dictionary:
	return _pools


func _refuse(reason: String) -> Array[Dictionary]:
	last_events.append({"type": "refused", "text": reason})
	return last_events


static func _strings(names: Array[StringName]) -> Array:
	var out := []
	for n in names:
		out.append(String(n))
	return out
