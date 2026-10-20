class_name NetrunSession
extends RefCounted
## One netrun from launch to completion or death (GDD 4.2, 6.3, 11): map movement,
## node contents, combats, rewards, Mainframe shops, Terminal events, banking and the
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
## RunState.kind of the Solace HQ ladder run.
const HQ_LADDER_KIND := "hq"

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
## Tooling hook (tools/balance): called with (action, result, combat state) after every accepted combat
## action, before a finished fight is settled. Empty in the game; it observes and never changes state.
var combat_observer: Callable = Callable()
var _pools: Dictionary = {}


# --- Lifecycle -------------------------------------------------------------------

## Launches a netrun for the roster operative `operative_id` at `tier`. MINOR Heat
## complications queued on the campaign are consumed here (shop stock, elite frequency).
static func start(p_resolver: CombatResolver, p_campaign: CampaignState, operative_id: StringName, tier: int, site_id: StringName, run_seed: int, corp: CorporationData = null) -> NetrunSession:
	var s := NetrunSession.new()
	s._bind(p_resolver, p_campaign)
	s.corporation = corp
	s._build_pools()  # a built REBEL_CELL picks its own elites
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
	var left_post := s._leave_post(operative_id)
	if corp != null and corp.city_grid != null and p_campaign.grid != null:
		var site := CampaignRules.site_data(corp, site_id)
		s.run.patrol = site != null and CampaignRules.is_patrol(p_campaign, site)
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
	BloomRules.begin(s.run.corp_theme.solace, s.config, corp, tier, false)
	s._bloom_load_keys(corp)
	p_campaign.runs_started += 1
	s.last_events = [{"type": "run_start", "text": "Netrun started: %s, tier %d, seed %d." % [op.name, tier, run_seed]}]
	s.last_events.append_array(left_post)
	s._apply_bug_cards()
	s._apply_boosts()
	s._compiler_rack_bonus()
	s._maybe_raid_interlude()
	s._sync()
	NetrunArtExport.on_run_start(s)  # NA-02 tooling hook: observes only, empty in the game
	return s


## A stationed operative leaves its Safehouse to run (GDD 5.4: stationed instead of running).
func _leave_post(operative_id: StringName) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var post := CampaignRules.stationed_site(campaign, operative_id)
	if post != &"":
		CampaignRules.recall(campaign, operative_id)
		out.append({"type": "recalled", "operative": operative_id, "site": post, "text": "%s leaves the post on %s to run." % [run.operative.name, post]})
	return out


## Heat entering `node_id` adds, as it will be applied (ICE scaling included).
func node_heat(node_id: StringName) -> int:
	var node := run.map.get_node(node_id)
	if node.is_empty():
		return 0
	var heat := int(node.get("heat", 0))
	if int(node["type"]) == RC.InfilNodeType.SERVER_RACK:
		heat = _rack_heat_override(heat)
	return HeatRules.scaled_delta(campaign, heat, config)


## The Rack capture Heat after a Daemon's override (Scrubber), without running the hooks.
func _rack_heat_override(heat: int) -> int:
	for id in run.operative.daemon_ids:
		var d := lookup.get_content(id) as DaemonData
		if d == null or d.custom_handler == null:
			continue
		for e in d.custom_handler.new().handle({"trigger": RC.Trigger.ON_SERVER_RACK_CAPTURE, "source_id": d.id, "daemon": d, "run": run}, run, null):
			if e.get("type", "") == "heat_override":
				heat = int(e["amount"])
	return heat


## node_heat for every node of the map (what the map labels show).
func map_heat() -> Dictionary:
	var out := {}
	for node in run.map.all_nodes():
		out[node["id"]] = node_heat(node["id"])
	return out


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
	s._build_pools()  # a built REBEL_CELL picks its own elites
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
	var left_post := s._leave_post(operative_id)
	var graph := MapGraph.new()
	graph.layers.append([{"id": MapGraph.make_id(1, 0), "layer": 1, "index": 0, "type": RC.InfilNodeType.SERVER_RACK,
		"elite": true, "next": [] as Array[StringName], "heat": 0}])
	s.run.map = graph
	if kind == "boss":
		BloomRules.begin(s.run.corp_theme.solace, s.config, corp, tier, true)
		s._bloom_load_keys(corp)
	p_campaign.runs_started += 1
	s.last_events = [{"type": "run_start", "text": "%s run started: %s vs %s." % [kind.capitalize(), op.name, enemy_id]}]
	s.last_events.append_array(left_post)
	s._apply_bug_cards()
	s._apply_boosts()  # HQ boosts apply to the final breach and Reclaim runs too
	s._sync()
	return s


## WH-HQ-LAUNCH: the Solace HQ breach as the GENOME CORE ladder (run kind "hq"): a map from
## SolaceHqGraph.generate (stream `hq_graph` of the run seed), the crown fight is the final boss,
## winning it completes the HQ run (campaign WON). A mid-ladder won fight continues the run.
static func start_hq_ladder(p_resolver: CombatResolver, p_campaign: CampaignState, operative_id: StringName, site_id: StringName, tier: int, run_seed: int, corp: CorporationData) -> NetrunSession:
	var s := NetrunSession.new()
	s._bind(p_resolver, p_campaign)
	s.corporation = corp
	s._build_pools()
	var op := p_campaign.get_operative(operative_id)
	if op == null or not op.alive:
		push_error("NetrunSession: no living operative '%s'." % operative_id)
		return null
	s.run = RunState.new()
	s.run.run_seed = run_seed
	s.run.tier = tier
	s.run.site_id = site_id
	s.run.kind = HQ_LADDER_KIND
	s.run.operative = op.duplicate_state()
	s.streams = RngStreams.seeded(run_seed)
	var left_post := s._leave_post(operative_id)
	var graph_stream := RngStreams.make_stream(run_seed, RngStreams.HQ_GRAPH_STREAM)
	if EyeRules.applies(corp):
		s._halcyon_begin_hq(corp, site_id, graph_stream)
	else:
		s.run.map = SolaceHqGraph.generate(s.config, graph_stream)
	BloomRules.begin(s.run.corp_theme.solace, s.config, corp, tier, true)
	s._bloom_load_keys(corp)
	p_campaign.runs_started += 1
	s.last_events = [{"type": "run_start", "text": "HQ ladder started: %s, tier %d, seed %d." % [op.name, tier, run_seed]}]
	s.last_events.append_array(left_post)
	s._apply_bug_cards()
	s._apply_boosts()
	s._sync()
	return s


## Halcyon v2 (WH-20 / WH-22): the HQ run's Eye state and graph. The launch snapshot (`spotted_level`)
## is taken once from the campaign's Eye and the HQ site's bearing; Alert starts at it; the graph is
## rebuilt from stream `hq_graph` until it is reachable for the launch phase.
func _halcyon_begin_hq(corp: CorporationData, site_id: StringName, graph_stream: RandomNumberGenerator) -> void:
	var h := run.corp_theme.halcyon
	h.hq = true
	h.eye_phase = campaign.corp_theme.halcyon.eye_index
	h.eye_step = 0
	h.spotted_level = EyeRules.spotted_level(campaign.corp_theme.halcyon, EyeRules.bearing_deg(corp.city_grid, site_id), config)
	h.hq_alert = h.spotted_level
	run.map = HalcyonHqGraph.generate(config, graph_stream, h.eye_phase)


## Halcyon HQ non-fight rooms: a rest bay heals, an Evidence Locker offers a Daemon, the Power Room
## waits for Cut the Power. Returns the events, or [] when `node` is a fight / event / shop.
func _halcyon_room(node: Dictionary) -> Array[Dictionary]:
	if bool(node.get("rest", false)):
		var healed := mini(run.operative.max_hp - run.operative.hp, run.operative.max_hp * config.halcyon_hq_rest_heal_pct / 100)
		run.operative.hp += healed
		last_events.append({"type": "hq_rest", "amount": healed, "text": "Maintenance Bay: +%d HP (%d/%d)." % [healed, run.operative.hp, run.operative.max_hp]})
		_sync()
		return last_events
	if bool(node.get("cache", false)):
		var daemons: Array = []
		for d in _pools["daemons"]:
			if not run.operative.daemon_ids.has(d):
				daemons.append(d)
		_offer(&"daemon", daemons, config.halcyon_hq_cache_choices, streams.get_stream(&"rewards"))
		if not run.pending_rewards.is_empty():
			run.phase = RunState.Phase.REWARD
		_sync()
		return last_events
	if bool(node.get("power", false)):
		last_events.append({"type": "power_room", "text": "The Power Room: the Eye's feed can be cut once."})
		_sync()
		return last_events
	return [] as Array[Dictionary]


## Whether the HQ breach of `corp` runs through the ladder (Solace and Halcyon so far; the other
## corporations keep the single-node "boss" run until their HQ slices).
static func uses_hq_ladder(corp: CorporationData) -> bool:
	return corp != null and (corp.id == BloomRules.SOLACE_ID or corp.id == EyeRules.HALCYON_ID)


static func from_dict(p_resolver: CombatResolver, p_campaign: CampaignState, d: Dictionary, corp: CorporationData = null) -> NetrunSession:
	var s := NetrunSession.new()
	s._bind(p_resolver, p_campaign)
	s.corporation = corp
	s._build_pools()  # a built REBEL_CELL picks its own elites
	s.run = RunState.from_dict(d.get("run", {}))
	if s.run.normal_fights_started < 0:
		s.run.normal_fights_started = legacy_normal_fights(s.run, s.config)
	s.streams = RngStreams.from_dict(s.run.streams)
	if not s.run.combat.is_empty():
		s.combat = CombatSession.from_dict(p_resolver, s.run.combat)
	return s


## N22 (designer call 2026-10-18): a save from before the normal-fight counter counts as no
## normal fight started while the run's current node is in layers 1..config.easy_normal_fights
## (or the run has not entered a node), and as config.easy_normal_fights (EASY exhausted) once
## its current node lies past that layer.
static func legacy_normal_fights(r: RunState, cfg: CampaignConfigData) -> int:
	var node := r.current_node()
	if node.is_empty() or int(node.get("layer", 1)) <= cfg.easy_normal_fights:
		return 0
	return cfg.easy_normal_fights


func to_dict() -> Dictionary:
	_sync()
	return {"run": run.to_dict()}


func state_hash() -> int:
	_sync()
	return run.state_hash()


## Plan 2 WH-02: the HUD theme chip a corporation theme rule fills from the run's corp_theme
## block: {"key": text key for the words (tr, may hold % placeholders), "args": Array for them,
## "value": the live number as a String (drawn in Anton apart from the words; optional), "kind":
## RunThemeState.ChipKind}; {} hides the chip. No theme rule fills it yet (WH-11 and the
## later corp slices add theirs here); like every preview it reads state and changes nothing.
func theme_chip() -> Dictionary:
	var b := run.corp_theme.solace
	if not b.enabled or run.is_over():
		return {}
	var band := bloom_band()
	var kind := RunThemeState.ChipKind.INFO
	if band == BloomRules.Band.CLOSE:
		kind = RunThemeState.ChipKind.WARN
	elif band >= BloomRules.Band.CATCHING:
		kind = RunThemeState.ChipKind.DANGER
	return {"key": TextDb.mark("FRONT"), "args": [], "value": bloom_gap_text(BloomRules.gap_milli(b)), "kind": kind}


## WH-11: a gap in thousandths as "n.n" layers (truncated toward zero to the shown tenth).
static func bloom_gap_text(gap_milli: int) -> String:
	var tenths: int = absi(gap_milli) / 100
	return "%s%d.%d" % ["-" if gap_milli < 0 and tenths > 0 else "", tenths / 10, tenths % 10]


## WH-11: the Bloom's band now (DORMANT before the first node is entered).
func bloom_band() -> BloomRules.Band:
	return BloomRules.band(run.corp_theme.solace, config, run.current_node_id != &"")


## WH-11: Exploit keys held this run (EX-03 sets them): Intel, Virus.
func bloom_set_keys(intel: bool, virus: bool, breach: bool = false) -> void:
	run.corp_theme.solace.key_intel = intel
	run.corp_theme.solace.key_virus = virus
	run.corp_theme.solace.key_breach = breach
	_sync()


## Solace v2: the Exploits held this campaign (and in the corporation's ExploitData) set the
## Bloom keys at netrun start: each flag on the ExploitData is one form of slowdown.
func _bloom_load_keys(corp: CorporationData) -> void:
	var b := run.corp_theme.solace
	if not b.enabled or corp == null:
		return
	for ex in corp.exploits:
		if ex == null or not campaign.has_exploit(ex.exploit_type):
			continue
		b.key_virus = b.key_virus or ex.bloom_pace_cut
		b.key_breach = b.key_breach or ex.bloom_setback
		b.key_intel = b.key_intel or ex.bloom_turn_cut


## Reads the campaign's Heat band into the Bloom's pace multiplier (before each entry, fight end
## and preview, so the preview and the result read the same Heat).
func _bloom_refresh_heat() -> void:
	var b := run.corp_theme.solace
	if b.enabled:
		BloomRules.set_heat_band(b, config, SolaceRaidRules.heat_band_index(campaign, config))


## WH-11 preview, nothing random: for each node `available_nodes()` offers (every unvisited
## node of the ladder with the Intel key), {node: {"gap_milli": exact gap after entering,
## "caught": bool, "fight": bool, "turn_cost_milli": front cost per fight turn}}. A node
## entered by ACROSS (node["across"]) includes `pace_cross`. The gap equals the real
## `enter_node` result (fight turns come after the fight, at `turn_cost_milli` each).
func bloom_preview() -> Dictionary:
	var b := run.corp_theme.solace
	var out := {}
	if not b.enabled or run.map == null or run.phase != RunState.Phase.MAP:
		return out
	_bloom_refresh_heat()
	var ids: Array = available_nodes()
	if b.key_intel:
		ids = []
		for n in run.map.all_nodes():
			if int(n["layer"]) > b.layer_milli / 1000:
				ids.append(n["id"])
		IdSort.sort_ids(ids)
	for id in ids:
		var node := run.map.get_node(id)
		var across := entered_across(node, run.current_node_id)
		var steps := 1
		if b.key_intel:
			steps = maxi(1, int(node["layer"]) - b.layer_milli / 1000)
		var gap := int(node["layer"]) * 1000 - (b.front_milli + (steps - 1) * BloomRules.entry_pace(b, config, run.tier) + BloomRules.entry_pace(b, config, run.tier, across) - BloomRules.pending_setback(b, config))
		var fight := int(node["type"]) == RC.InfilNodeType.ROUTER or int(node["type"]) == RC.InfilNodeType.SERVER_RACK
		out[id] = {"gap_milli": gap, "caught": gap <= 0, "fight": fight,
			"turn_cost_milli": BloomRules.fight_pace(b, config, 1) if fight else 0,
			"across_milli": BloomRules.entry_pace(b, config, run.tier, true) - BloomRules.entry_pace(b, config, run.tier) if across else 0}
	return out


## CAUGHT's consequence: the operative is lost and the netrun abandoned (Q24.1), the same
## path as 0 HP. The raid is untouched.
func _bloom_caught() -> void:
	combat = null
	last_events.append({"type": "bloom_caught", "text": "THE BLOOM CAUGHT %s." % run.operative.name})
	_die()
	_sync()


## Buys a dose at a Mainframe (price from config); it is held until used.
func buy_dose() -> Array[Dictionary]:
	last_events = []
	var b := run.corp_theme.solace
	if not b.enabled or run.phase != RunState.Phase.SHOP:
		return _refuse("No antiviral for sale here.")
	if run.cycles < config.bloom_dose_price:
		return _refuse("Not enough Cycles for a dose (%d)." % config.bloom_dose_price)
	run.cycles -= config.bloom_dose_price
	b.doses_held += 1
	last_events.append({"type": "purchase", "kind": "dose", "price": config.bloom_dose_price, "text": "Bought an antiviral dose."})
	_sync()
	return last_events


## Uses a held dose: the front goes back by dose_push, the gap clamped to max_gap.
func use_dose() -> Array[Dictionary]:
	last_events = []
	var b := run.corp_theme.solace
	if run.is_over() or in_combat() or not BloomRules.use_dose(b, config):
		return _refuse("No dose to use.")
	last_events.append({"type": "dose", "gap_milli": BloomRules.gap_milli(b), "text": "Antiviral dose taken."})
	_sync()
	return last_events


## The gap after using a dose now (exact); -1 with none to use.
func dose_preview() -> int:
	var b := run.corp_theme.solace
	if not b.enabled or b.caught or b.doses_held <= 0:
		return -1
	var c := b.copy() as BloomState
	BloomRules.push(c, config)
	return BloomRules.gap_milli(c)


## HQ ward rest (the existing HQ rest node binds here): pushes the front back by dose_push.
func bloom_ward_rest() -> void:
	BloomRules.ward_rest(run.corp_theme.solace, config)
	_sync()


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


## WH-10: whether entering `node` from `from_id` is an HQ ACROSS move: the node is flagged
## `across`, or `from_id` is one of its `across_from` sources (the ladder's bridge edges).
static func entered_across(node: Dictionary, from_id: StringName) -> bool:
	if bool(node.get("across", false)):
		return true
	return from_id != &"" and (node.get("across_from", []) as Array).has(from_id)


## Moves to `node_id` and opens whatever it holds. Returns the events.
func enter_node(node_id: StringName) -> Array[Dictionary]:
	last_events = []
	if not available_nodes().has(node_id):
		return _refuse("Node %s is not reachable from here." % node_id)
	var node := run.map.get_node(node_id)
	var across := entered_across(node, run.current_node_id)
	run.current_node_id = node_id
	run.visited.append(node_id)
	var bloom := run.corp_theme.solace
	_bloom_refresh_heat()
	if bloom.enabled and BloomRules.enter(bloom, config, run.tier, int(node["layer"]), across):
		_bloom_caught()
		return last_events
	last_events.append({"type": "enter_node", "node": node_id, "node_type": node["type"],
		"text": "Entered %s (%s%s)." % [node_id, RC.InfilNodeType.keys()[node["type"]], ", elite" if node["elite"] and node["type"] != RC.InfilNodeType.SERVER_RACK else ""]})
	if node["elite"] and node["type"] != RC.InfilNodeType.SERVER_RACK and node["heat"] != 0:
		_add_heat(node["heat"], "elite node")
	if run.corp_theme.halcyon.hq:
		var room := _halcyon_room(node)
		if not room.is_empty():
			return room
	elif bool(node.get("rest", false)):
		# WH-10: the Solace HQ rest room is the ward rest (the front goes back by dose_push).
		bloom_ward_rest()
		last_events.append({"type": "ward_rest", "gap_milli": BloomRules.gap_milli(bloom), "text": "Ward rest: the front falls back."})
		return last_events
	match int(node["type"]):
		RC.InfilNodeType.ROUTER:
			_start_combat(node["elite"])
		RC.InfilNodeType.SERVER_RACK:
			_start_combat(true)
		RC.InfilNodeType.TERMINAL:
			_open_event()
		RC.InfilNodeType.MAINFRAME:
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
		if combat_observer.is_valid():
			combat_observer.call(action, result, combat.state)
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
	var final_rack := (run.kind == "netrun" and run.current_node_id == run.map.final_node_id()) or bool(run.current_node().get("mini_boss", false))
	var setup := _combat_setup(elite, final_rack, streams.get_stream(&"combat"))
	var enemy_id: StringName = setup["enemy_id"]
	if not elite and not final_rack:
		run.normal_fights_started += 1
	combat = _combat_from(setup)
	run.phase = RunState.Phase.COMBAT
	last_events.append({"type": "combat_start", "enemy_id": enemy_id, "elite": elite, "mini_boss": final_rack,
		"text": "Combat: %s%s." % [enemy_id, " (mini-boss)" if final_rack else (" (elite)" if elite else "")]})
	_apply_campaign_effects(combat.last_events)


## The fight a node would start: the foe and the fight seed drawn from `combat_rng` (the
## run's combat stream, or a copy of it for a preview), and the operative's overrides.
func _combat_setup(elite: bool, final_rack: bool, combat_rng: RandomNumberGenerator) -> Dictionary:
	var boss_exploits := {}
	var pool: Array = _pools["elites"] if elite else normal_pool()
	if final_rack and not _pools["mini_bosses"].is_empty():
		pool = _pools["mini_bosses"]
	if pool.is_empty():
		pool = _pools["enemies"] if elite else _pools["elites"]
	var enemy_id: StringName = pool[combat_rng.randi_range(0, pool.size() - 1)]
	if run.forced_enemy_id != &"":
		enemy_id = run.forced_enemy_id
	elif bool(run.current_node().get("boss", false)) and corporation != null and corporation.final_boss != null:
		enemy_id = corporation.final_boss.id  # WH-10: the HQ ladder's crown is the final boss
		if run.kind == HQ_LADDER_KIND:
			boss_exploits = CampaignRules.boss_overrides(campaign, corporation)  # the Exploits bite the crown only
	var seed := combat_rng.randi()
	var op := run.operative
	var cls := lookup.get_content(op.class_id) as ClassData
	var overrides := boss_exploits.duplicate(true)
	overrides.merge({
		"slot_slice_ids": _strings(op.slot_slice_ids), "slot_firmware_ids": _strings(op.slot_firmware_ids),
		"ring_segment_ids": _strings(op.ring_segment_ids),
		"deck": _strings(op.deck), "daemon_ids": _strings(op.daemon_ids),
		"hp": op.hp, "max_hp": op.max_hp, "enemy_scale": enemy_scale(), "enemy_output_scale": enemy_output_scale(), "tier": run.tier, "hub_id": String(op.hub_id(cls)),
	}, true)
	for k in rule_overrides():
		overrides[k] = rule_overrides()[k]
	if campaign.is_assisted():
		overrides["extra_free_nudges"] = int(campaign.assist.get("free_nudges", 0))
	if not run.drones.is_empty():
		overrides["drones"] = run.drones.duplicate(true)
	for k in run.combat_overrides:
		if k != "shop_stock_delta":
			overrides[k] = run.combat_overrides[k]
	return {"enemy_id": enemy_id, "seed": seed, "overrides": overrides, "class_id": op.class_id, "ring_id": op.ring_id(cls)}


func _combat_from(setup: Dictionary) -> CombatSession:
	return CombatSession.start(resolver, setup["class_id"], [setup["enemy_id"]], int(setup["seed"]), setup["ring_id"],
		campaign.heat_majors_crossed(config), setup["overrides"])


## ART-8 8w (bible 4.9 "the gate preview equals the fight start"): the fight the Central
## Server's breach would start, without starting it: the same setup drawn from a COPY of the
## combat stream, so the run, its streams and the campaign stay as they were. Null outside
## an HQ breach run or when its node is not open.
func breach_preview() -> CombatSession:
	if run.kind != "boss" or run.phase != RunState.Phase.MAP or available_nodes().is_empty():
		return null
	var copy := RngStreams.from_dict(streams.to_dict())
	return _combat_from(_combat_setup(true, false, copy.get_stream(&"combat")))


## N22 (ruling Q12): the normal enemies the next Router fight draws from: the EASY pool while
## fewer than config.easy_normal_fights normal fights have started this run, else HARD; an
## empty pool falls back to the other one (both sorted by content id).
func normal_pool() -> Array:
	var easy: Array = _pools["easy_enemies"]
	var hard: Array = _pools["hard_enemies"]
	var want_easy := run.normal_fights_started < config.easy_normal_fights
	var first := easy if want_easy else hard
	return first if not first.is_empty() else (hard if want_easy else easy)


## N2 (R2): the legacy HP multiplier at this run's tier (config enemy_hp_scale_by_tier),
## used only by enemies without hp_by_tier / hp_bands; those read their own table in
## CombatResolver.create_combat.
func enemy_scale() -> float:
	return config.enemy_hp_scale(run.tier)


## N2 (R2): the enemy output factor at this run's tier (config enemy_damage_by_tier), for
## every enemy including mini-bosses and the final boss. Flat enemy amounts read it (N1).
func enemy_output_scale() -> float:
	return config.enemy_damage_factor(run.tier)


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


## ICE 11 STARTING_BUG_CARD: the working deck carries at least N Bug cards (a Mainframe can
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
	_bloom_refresh_heat()
	if run.corp_theme.solace.enabled and BloomRules.end_fight(run.corp_theme.solace, config, cs.turn):
		_bloom_caught()
		return
	run.null_resolved = run.null_resolved or cs.null_resolved
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
	var ladder := run.kind == HQ_LADDER_KIND
	var is_rack: bool = node["type"] == RC.InfilNodeType.SERVER_RACK and not ladder  # the ladder has no Rack captures
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
	if run.kind != "netrun" and not ladder:
		combat = null
		_complete_run()
		return
	if ladder and bool(node.get("boss", false)):
		combat = null  # the crown is down: the HQ run completes (campaign WON)
		_complete_run()
		return
	_offer(&"card", _card_pool(), config.card_reward_choices, rewards)
	if elite and not is_rack:
		_offer(&"firmware", _pools["firmware"], config.elite_firmware_choices, rewards)
	elif not elite and rewards.randf() < config.router_firmware_chance:
		_offer(&"firmware", _pools["common_firmware"], config.router_firmware_choices, rewards)
	if is_rack:
		_capture_rack()
		# The layer-4 Rack offers a Daemon; the final Rack's prize is the Site's objective
		# (GDD 4.2) plus the fight's card offer (decision 2026-09-24, H12).
		if not _at_final_rack():
			var daemons: Array = []
			for d in _pools["daemons"]:
				if not run.operative.daemon_ids.has(d):
					daemons.append(d)
			_offer(&"daemon", daemons, config.rack_daemon_choices, rewards)
	combat = null
	if is_rack and _at_final_rack():
		if run.pending_rewards.is_empty():
			_complete_run()
		else:
			run.phase = RunState.Phase.REWARD  # the run completes once the Rack's offers are resolved
		return
	run.phase = RunState.Phase.REWARD if not run.pending_rewards.is_empty() else RunState.Phase.MAP
	_maybe_raid_interlude()


## Whether the operative stands on the captured final Server Rack of a netrun.
func _at_final_rack() -> bool:
	return run.kind == "netrun" and run.map != null and run.current_node_id == run.map.final_node_id() and run.racks_captured > 0


## Server Rack capture (GDD 4.2, 11.5): bank Schematics and assets, add Heat (or what a
## Daemon says instead), fire ON_SERVER_RACK_CAPTURE hooks.
func _capture_rack() -> void:
	var tier_index := clampi(run.tier - 1, 0, mini(config.rack_schematics_by_tier.size(), config.rack_heat_by_tier.size()) - 1)
	var schematics := config.rack_schematics_by_tier[tier_index]
	run.banked_schematics += schematics
	run.racks_captured += 1
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
	return reward_at(0)


## W4-REWARDS: offer `index` of the payout (the rewards screen lists them all); empty when none.
func reward_at(index: int) -> Dictionary:
	return run.pending_rewards[index] if index >= 0 and index < run.pending_rewards.size() else {}


## Takes option `index` of the current offer (or of offer `offer_index` of the payout: the
## rewards screen picks from any row). Firmware needs the wheel `slot` to socket.
func choose_reward(index: int, slot: int = -1, offer_index: int = 0) -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.REWARD or run.pending_rewards.is_empty():
		return _refuse("No reward to choose.")
	if offer_index < 0 or offer_index >= run.pending_rewards.size():
		return _refuse("No such reward.")
	var offer := run.pending_rewards[offer_index]
	var options: Array = offer["options"]
	if index < 0 or index >= options.size():
		return _refuse("No such option.")
	var id := StringName(String(options[index]))
	var err := _grant(String(offer["kind"]), id, slot)
	if err != "":
		return _refuse(err)
	run.pending_rewards.remove_at(offer_index)
	_after_reward()
	_sync()
	return last_events


## Skips offer `offer_index` only (F12: a SKIP on one pick leaves the others).
func skip_reward(offer_index: int = 0) -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.REWARD or run.pending_rewards.is_empty():
		return _refuse("No reward to skip.")
	if offer_index < 0 or offer_index >= run.pending_rewards.size():
		return _refuse("No such reward.")
	run.pending_rewards.remove_at(offer_index)
	last_events.append({"type": "reward_skipped", "text": "Reward skipped."})
	_after_reward()
	_sync()
	return last_events


## W4-REWARDS: PROCEED. Leaves the rewards screen, skipping every offer still untaken (the
## same state as skipping each in turn).
func proceed_rewards() -> Array[Dictionary]:
	last_events = []
	if run.phase != RunState.Phase.REWARD:
		return _refuse("No reward to proceed from.")
	while not run.pending_rewards.is_empty():
		run.pending_rewards.pop_front()
		last_events.append({"type": "reward_skipped", "text": "Reward skipped."})
	_after_reward()
	_sync()
	return last_events


func _after_reward() -> void:
	if run.pending_rewards.is_empty():
		if _at_final_rack():
			_complete_run()
			return
		run.phase = RunState.Phase.MAP
		_maybe_raid_interlude()


## Gives `id` of `kind` to the operative. Returns an error string when it cannot.
func _grant(kind: String, id: StringName, slot: int) -> String:
	match kind:
		"card":
			run.operative.deck.append(id)
			last_events.append({"type": "card_gained", "card": id, "text": "Added %s to the deck." % id})
		"firmware":
			var why := firmware_slot_error(id, slot)
			if why != "":
				return why
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
	var err := choice_error(choice)
	if err != "":
		return _refuse(err)
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


## Why `choice` can't be taken now ("" when it can): too few Cycles, an HP cost that
## would flatline the operative, or a Daemon already installed.
func choice_error(choice: EventChoiceData) -> String:
	if choice.cycle_cost > run.cycles:
		return "Not enough Cycles (%d needed)." % choice.cycle_cost
	if choice_hp_loss(choice) >= run.operative.hp and choice_hp_loss(choice) > 0:
		return "That would flatline %s (%d HP left)." % [run.operative.name, run.operative.hp]
	if choice.reward is DaemonData and run.operative.daemon_ids.has((choice.reward as DaemonData).id):
		return "%s is already installed." % (choice.reward as DaemonData).display_name
	if choice.reward is FirmwareData and not _firmware_fits(choice.reward as FirmwareData):
		return "%s fits no slice on %s's wheel." % [(choice.reward as FirmwareData).display_name, run.operative.name]
	return ""


## Why Firmware `id` cannot be socketed into wheel slot `slot` of the running operative ("" when
## it can): the socket rule `_grant` applies (parity SHOP-06: the screens read it to grey the
## slots a chip does not fit; read-only).
func firmware_slot_error(id: StringName, slot: int) -> String:
	var fw := lookup.get_content(id) as FirmwareData
	if fw == null:
		return "Unknown Firmware."
	if slot < 0 or slot >= run.operative.slot_slice_ids.size():
		return "Choose a wheel slot for the Firmware."
	var slice := lookup.get_content(run.operative.slot_slice_ids[slot]) as SliceData
	if not fw.allowed_slice_types.is_empty() and not (slice.slice_type in fw.allowed_slice_types):
		return "%s does not fit a %s slice." % [id, RC.SliceType.keys()[slice.slice_type]]
	return ""


## G14: the Firmware chip a new chip socketed into wheel slot `slot` would destroy (the socket holds
## one; `_grant` overwrites it), or &"" when the slot is empty or does not exist. The confirm names it.
func firmware_replaced_at(slot: int) -> StringName:
	if run == null or slot < 0 or slot >= run.operative.slot_firmware_ids.size():
		return &""
	return run.operative.slot_firmware_ids[slot]


## Whether `fw` can be socketed into at least one slot of the operative's wheel.
func _firmware_fits(fw: FirmwareData) -> bool:
	if fw.allowed_slice_types.is_empty():
		return true
	for id in run.operative.slot_slice_ids:
		var slice := lookup.get_content(id) as SliceData
		if slice != null and slice.slice_type in fw.allowed_slice_types:
			return true
	return false


## HP a choice costs (its HP cost plus damage effects).
func choice_hp_loss(choice: EventChoiceData) -> int:
	var loss := choice.hp_cost
	for e in choice.effects:
		if e != null and e.type == RC.EffectType.DEAL_DAMAGE:
			loss += e.amount
	return loss


## What a choice costs and gives, from its data (Heat as it will apply): shown on the
## button so no cost is hidden.
func choice_costs(choice: EventChoiceData) -> String:
	var parts := PackedStringArray()
	if choice.cycle_cost > 0:
		parts.append("-%d Cycles" % choice.cycle_cost)
	if choice_hp_loss(choice) > 0:
		parts.append("-%d HP" % choice_hp_loss(choice))
	for e in choice.effects:
		if e == null:
			continue
		match e.type:
			RC.EffectType.GAIN_CYCLES:
				if e.amount != 0:
					parts.append("%+d Cycles" % e.amount)
			RC.EffectType.MODIFY_HEAT:
				parts.append("%+d Heat" % HeatRules.scaled_delta(campaign, e.amount, config))
			RC.EffectType.HEAL:
				parts.append("+%d HP" % e.amount)
			RC.EffectType.GAIN_SCHEMATICS:
				parts.append("%+d Schematics" % e.amount)
	if choice.reward != null:
		var kind := "Card" if choice.reward is CardData else ("Firmware" if choice.reward is FirmwareData else ("Daemon" if choice.reward is DaemonData else ("Asset" if choice.reward is DefenseAssetData else "Operative")))
		if kind == "Operative":
			parts.append("rescue an operative")
		else:
			parts.append("%s: %s" % [kind, String(choice.reward.get("display_name"))])
	return ", ".join(parts)


func _apply_run_effect(e: EffectData) -> void:
	match e.type:
		RC.EffectType.GAIN_CYCLES:
			if e.amount == 0:
				return  # flavour-only choice
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

# --- Mainframe shop ----------------------------------------------------------------------

func _open_shop() -> void:
	var rng := streams.get_stream(&"rewards")
	var stock := {"cards": [], "card_prices": [], "firmware": [], "firmware_prices": [], "daemons": [], "daemon_prices": [], "slices": []}
	var card_count := maxi(1, config.shop_card_stock + int(run.combat_overrides.get("shop_stock_delta", 0)))
	_stock(stock, "cards", "card_prices", _card_pool(), card_count, config.card_price_range, rng)
	_stock(stock, "firmware", "firmware_prices", _pools["firmware"], config.shop_firmware_stock, config.firmware_price_range, rng)
	var daemons: Array = []
	for d in _pools["daemons"]:
		if not run.operative.daemon_ids.has(d):
			daemons.append(d)
	_stock(stock, "daemons", "daemon_prices", daemons, config.shop_daemon_stock, config.daemon_price_range, rng)
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
	last_events.append({"type": "shop", "text": "Mainframe: %d cards, %d Firmware, %d Daemon(s) for sale." % [stock["cards"].size(), stock["firmware"].size(), stock["daemons"].size()]})


func _stock(stock: Dictionary, key: String, price_key: String, pool: Array, count: int, price_range: Vector2i, rng: RandomNumberGenerator) -> void:
	var remaining: Array = pool.duplicate()
	for i in mini(count, remaining.size()):
		var idx := rng.randi_range(0, remaining.size() - 1)
		stock[key].append(String(remaining[idx]))
		stock[price_key].append(roundi(rng.randi_range(price_range.x, price_range.y) * _price_scale()))
		remaining.remove_at(idx)


## CYCLE_PRICE_PCT (ICE 4): every Mainframe price scales with it.
func _price_scale() -> float:
	return 1.0 + campaign.rule_modifier(config, RC.RuleModifierType.CYCLE_PRICE_PCT) / 100.0


func card_removal_price() -> int:
	return roundi((config.card_removal_price + config.card_removal_increment * run.card_removals) * _price_scale())


func slice_overwrite_price(slot: int) -> int:
	var slice := lookup.get_content(run.operative.slot_slice_ids[slot]) as SliceData
	var base := config.null_slice_overwrite_price if slice.slice_type == RC.SliceType.NULL else config.slice_overwrite_price
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


## Overwrites wheel slot `slot` with shop slice `stock_index` (100 Cycles; 150 for the NULL slot).
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
	last_events.append({"type": "shop_left", "text": "Left the Mainframe."})
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
		"queued_raid_id": String(campaign.pending_raids[0].get("raid_id", "")),
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
		var done := CampaignRules.on_run_completed(campaign, corporation, config, run, lookup)
		CampaignRules.name_pending_raids(campaign, lookup, done)
		last_events.append_array(done)


## Death (GDD 4.2): permadeath, unbanked loot lost, banked loot kept, Heat +10 + tier.
func _die() -> void:
	run.outcome = RunState.Outcome.DIED
	run.phase = RunState.Phase.ENDED
	var op := campaign.get_operative(run.operative.id)
	if op != null:
		op.alive = false
		op.hp = 0
	CampaignRules.recall(campaign, run.operative.id)  # a dead operative frees its post
	campaign.deaths += 1
	campaign.schematics += run.banked_schematics
	_bank_assets_to_armory()
	var lost := run.unbanked_assets.size()
	run.unbanked_assets.clear()
	last_events.append({"type": "run_died", "text": "%s is flatlined. Unbanked loot lost (%d Cycles, %d asset(s)); %d banked Schematics kept." % [run.operative.name, run.cycles, lost, run.banked_schematics]})
	_add_heat(HeatRules.death_heat(campaign, config, run.tier), "operative death")


## Abandon run (designer ruling 2026-10-05, GDD 4.5): the operative is killed on the run, so
## the consequences are the death's (`_die`, GDD 4.2: lost for good with everything unbanked,
## banked loot kept, Heat +death_heat_base + tier). A fight in progress ends with it.
func abandon() -> Array[Dictionary]:
	last_events = []
	if run.is_over():
		return _refuse("The run is already over.")
	last_events.append({"type": "run_abandoned", "operative": String(run.operative.id),
		"text": "%s abandons the run." % run.operative.name})
	combat = null
	_die()
	_sync()
	return last_events


## What `abandon` costs, worked out by abandoning a copy of the run and the campaign (so the
## dialog's numbers are the rule's own: preview == result); {} once the run is over. Keys:
## operative (name), operative_id, rank, tier; lost unbanked: cycles, assets, cards_added,
## firmware, daemons (gained this run); heat (the change), heat_before, heat_after; kept:
## schematics_kept, assets_kept (banked at Server Racks); raids (raids the Heat queues).
func abandon_preview() -> Dictionary:
	if run.is_over():
		return {}
	var c := campaign.duplicate_state()
	var copy := NetrunSession.from_dict(resolver, c, to_dict(), corporation)
	copy.abandon()
	var home := campaign.get_operative(run.operative.id)
	return {
		"operative": run.operative.name, "operative_id": String(run.operative.id), "rank": run.operative.rank,
		"tier": run.tier, "cycles": run.cycles, "assets": run.unbanked_assets.size(),
		"cards_added": _gained(home.deck if home != null else ([] as Array[StringName]), run.operative.deck, run.temp_cards),
		"firmware": _firmware_gained(home), "daemons": _gained(home.daemon_ids if home != null else ([] as Array[StringName]), run.operative.daemon_ids),
		"heat": c.heat - campaign.heat, "heat_before": campaign.heat, "heat_after": c.heat,
		"schematics_kept": c.schematics - campaign.schematics, "assets_kept": c.armory.size() - campaign.armory.size(),
		"raids": c.pending_raids.size() - campaign.pending_raids.size(),
	}


## How many ids `now` holds beyond `before` (a multiset difference), not counting `skip`
## (the run-only boost cards).
static func _gained(before: Array[StringName], now: Array[StringName], skip: Array[StringName] = []) -> int:
	var left := before.duplicate()
	left.append_array(skip)
	var n := 0
	for id in now:
		var i := left.find(id)
		if i >= 0:
			left.remove_at(i)
		else:
			n += 1
	return n


## Firmware socketed this run: slots whose Firmware is not the one the roster copy holds there.
func _firmware_gained(home: OperativeState) -> int:
	var n := 0
	for i in run.operative.slot_firmware_ids.size():
		var fw := run.operative.slot_firmware_ids[i]
		var was: StringName = home.slot_firmware_ids[i] if home != null and i < home.slot_firmware_ids.size() else &""
		if fw != &"" and fw != was:
			n += 1
	return n


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
	CampaignRules.name_pending_raids(campaign, lookup, events)
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
			out.append_array(d.custom_handler.new().handle({"trigger": trigger, "source_id": d.id, "daemon": d, "run": run}, run, streams.get_stream(&"events")))
	for e in out:
		last_events.append(e)
	return out


# --- Pools ---------------------------------------------------------------------------------

func _build_pools() -> void:
	var enemies: Array = []
	var elites: Array = []
	var mini_bosses: Array = []
	var easy_enemies: Array = []
	var hard_enemies: Array = []
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
			if e.normal_pool == RC.NormalPool.EASY:
				easy_enemies.append(id)
			else:
				hard_enemies.append(id)
	# REBEL_CELL (built at runtime): its elites are this campaign's Mirrors only. Mirrors
	# from earlier builds in the session stay in the lookup and must not leak in.
	if corporation != null and corporation.generated_from_profile:
		elites.clear()
		for e in corporation.elites:
			if e != null:
				elites.append(e.id)
		elites.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
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
		"enemies": enemies, "easy_enemies": easy_enemies, "hard_enemies": hard_enemies, "elites": elites, "mini_bosses": mini_bosses, "shared_cards": shared_cards, "class_cards": class_cards,
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
