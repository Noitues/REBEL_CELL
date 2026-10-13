extends RefCounted
## HeuristicStrategist (Tooling 1 T2; docs/process/PLAYTEST_COST_REVIEW.md §3): a deterministic,
## LLM-free answer to every state-tester decision of tools/agent/agent_simulator.gd. Each call
## gets the decision kind, a context dictionary and one structured `meta` dictionary per menu
## option (the same menu the LLM reads as text) and returns {"choice": int, "reason": String}.
## Every threshold comes from HeuristicStrategistConfigData (content/config/heuristic_strategist.tres).
## Pure: no RNG of its own, ties by menu order (the menu is built in a deterministic order), so the
## same seed plays the same campaign.
##   combat  TurnPlanner option 0; plans tied on score go to the least HP taken, then most kills;
##           with lookahead_turns 2, each plan adds the best plan of the next turn after it.
##   node    HP-aware value: Elites avoided under elite_min_hp_share; events and shops preferred
##           under low_hp_share; Heat costs more as campaign Heat climbs.
##   reward  CampaignSimulator's card / Firmware / Daemon scores plus rarity and deck synergy;
##           skip under the thresholds.
##   event   the built-in pick (the last allowed, safest choice).
##   launch  SA-001's rules: breach when Heat is low, then Exploits, then the biggest Heat cut
##           above scrub_min_heat, else a low tier; the trailing operative takes the easy runs.
##   raid    the placement whose exact projection holds best.
##   hq/shop the v2 sinks by a priority list.

const TurnPlanner := preload("res://tools/agent/turn_planner.gd")
## Planner plans asked for when scoring the next turn of the lookahead (the best comes first).
const NEXT_TURN_PLANS := 2

var config: HeuristicStrategistConfigData
var lookup: ContentLookup
## Turns the combat planner looks ahead: the config's value unless the caller overrides it
## (the bridge's `lookahead=2`); the loaded config itself stays read-only.
var lookahead_turns: int = 1


func _init(p_config: HeuristicStrategistConfigData, p_lookup: ContentLookup) -> void:
	config = p_config
	lookup = p_lookup
	lookahead_turns = config.lookahead_turns


## Answers one decision: {"choice": int, "reason": String}. `meta` has one entry per option.
func choose(kind: String, ctx: Dictionary, meta: Array) -> Dictionary:
	if meta.size() <= 1:
		return _pick(0, "only option")
	match kind:
		"combat":
			return _combat(ctx, meta)
		"node":
			return _node(ctx, meta)
		"reward":
			return _reward(ctx, meta)
		"launch":
			return _launch(ctx, meta)
		"raid":
			return _raid(meta)
		"shop":
			return _shop(ctx, meta)
		"hq":
			return _hq(ctx, meta)
		"event":
			return _pick(0, "event: the safest allowed choice")
	return _pick(0, "unknown kind %s: option 0" % kind)


static func _pick(i: int, reason: String) -> Dictionary:
	return {"choice": i, "reason": reason}


# --- Combat -----------------------------------------------------------------------------------

func _combat(ctx: Dictionary, meta: Array) -> Dictionary:
	var values: Array[float] = []
	var session: CombatSession = ctx.get("session")
	for m in meta:
		var v := float(m["score"])
		if lookahead_turns >= 2 and session != null:
			v += _next_turn_value(session, m["actions"])
		values.append(v)
	var best := 0
	for i in range(1, meta.size()):
		var dv := values[i] - values[best]
		if dv > config.combat_tie_epsilon:
			best = i
		elif absf(dv) <= config.combat_tie_epsilon:
			var a: Dictionary = meta[i]
			var b: Dictionary = meta[best]
			if int(a["taken"]) < int(b["taken"]) or (int(a["taken"]) == int(b["taken"]) and int(a["kills"]) > int(b["kills"])):
				best = i
	return _pick(best, "combat: value %.1f (deal %d, take %d, %d kill(s))%s" % [values[best], int(meta[best]["dealt"]),
		int(meta[best]["taken"]), int(meta[best]["kills"]), " with 2-turn lookahead" if lookahead_turns >= 2 else ""])


## The best plan's score on the turn after `actions` and End Turn (a win ends the fight: bonus).
func _next_turn_value(session: CombatSession, actions: Array) -> float:
	var rng := CombatResolver.clone_rng(session.rng)
	var st := session.state
	for a in actions:
		var r := session.resolver.apply(st, a, rng)
		if not r.ok():
			break
		st = r.state
	var end := session.resolver.apply(st, CombatAction.end_turn(), rng)
	if not end.ok():
		return 0.0
	st = end.state
	if st.player.hp <= 0:
		return 0.0  # the plan's own score already carries the death
	if st.living_enemies(false).is_empty():
		return config.lookahead_win_bonus
	var probe := CombatSession.new()
	probe.resolver = session.resolver
	probe.state = st
	probe.rng = rng
	var next := TurnPlanner.plans(probe, NEXT_TURN_PLANS)
	if next.is_empty():
		return 0.0
	return config.lookahead_next_weight * float(next[0]["score"])


# --- Map nodes --------------------------------------------------------------------------------

func _node(ctx: Dictionary, meta: Array) -> Dictionary:
	var hp_share := float(ctx["hp"]) / maxf(1.0, float(ctx["max_hp"]))
	var low := hp_share < config.low_hp_share
	var heat_mult := 1.0 + float(ctx.get("campaign_heat", 0)) / config.node_heat_scale
	var best := 0
	var best_v := -INF
	for i in meta.size():
		var m: Dictionary = meta[i]
		var v := 0.0
		match int(m["type"]):
			RC.InfilNodeType.SERVER_RACK:
				v = config.node_value_server_rack - (config.node_low_hp_bonus if low else 0.0)
			RC.InfilNodeType.MAINFRAME:
				v = config.node_value_mainframe_rich if int(ctx["cycles"]) >= config.mainframe_rich_cycles else config.node_value_mainframe
				v += config.node_low_hp_bonus if low else 0.0
			RC.InfilNodeType.TERMINAL:
				v = config.node_value_terminal + (config.node_low_hp_bonus if low else 0.0)
			_:
				if bool(m["elite"]):
					v = config.node_value_elite_low if hp_share < config.elite_min_hp_share else config.node_value_elite
				else:
					v = config.node_value_router - (config.node_low_hp_bonus if low else 0.0)
		v -= config.node_heat_weight * heat_mult * float(int(m["heat"]))
		if v > best_v:
			best_v = v
			best = i
	return _pick(best, "node: value %.1f at %d%% HP" % [best_v, roundi(hp_share * 100.0)])


# --- Rewards ----------------------------------------------------------------------------------

## Card value: CampaignSimulator._card_score, plus rarity, plus synergy with the deck's effects.
func card_value(card: CardData, deck: Array) -> float:
	var base := CampaignSimulator._card_score(card)
	if base < 0.0:
		return base
	var types := {}
	for e in card.effects:
		if e != null:
			types[e.type] = true
	var synergy := 0.0
	for id in deck:
		var other := lookup.get_content(StringName(String(id))) as CardData
		if other == null:
			continue
		for e in other.effects:
			if e != null and types.has(e.type):
				synergy += config.synergy_per_match
				break
	return base + config.rarity_bonus * float(mini(int(card.rarity), RC.Rarity.RARE)) + minf(synergy, config.synergy_cap)


func _offer_value(m: Dictionary, deck: Array) -> float:
	var res := lookup.get_content(StringName(String(m["id"])))
	match String(m["kind"]):
		"card":
			if deck.size() >= config.deck_max:
				return -INF
			var v := card_value(res as CardData, deck)
			return v if v > config.card_min_value else -INF
		"firmware":
			var fw := res as FirmwareData
			if fw == null or CampaignSimulator._costs_heat(fw):
				return -INF
			var f := CampaignSimulator._firmware_score(fw)
			return f if f > config.firmware_min_score else -INF
		"daemon":
			var d := CampaignSimulator._daemon_score(res as DaemonData)
			return d if d > config.daemon_min_score else -INF
	return -INF


func _reward(ctx: Dictionary, meta: Array) -> Dictionary:
	var deck: Array = ctx.get("deck", [])
	var best := 0
	var best_v := -INF
	for i in meta.size():
		var m: Dictionary = meta[i]
		if not m.has("id"):
			continue
		var v := _offer_value(m, deck)
		if v > best_v:
			best_v = v
			best = i
	if best_v == -INF:
		return _pick(0, "reward: nothing above the thresholds, skip")
	return _pick(best, "reward: %s %s value %.2f" % [meta[best]["kind"], meta[best]["id"], best_v])


# --- Launch, Heat, crew -----------------------------------------------------------------------

func _launch(ctx: Dictionary, meta: Array) -> Dictionary:
	var heat := int(ctx["heat"])
	var top_rank := int(meta[0]["op_rank"])
	var low_rank := top_rank
	for m in meta:
		top_rank = maxi(top_rank, int(m["op_rank"]))
		low_rank = mini(low_rank, int(m["op_rank"]))
	var rotate := top_rank - low_rank >= config.rotate_rank_gap
	# 1. The breach, with the best operative, when Heat is low.
	if heat <= config.breach_max_heat:
		var b := _best_launch(meta, func(m: Dictionary) -> bool: return int(m["objective"]) == RC.SiteObjective.CENTRAL_SERVER and int(m["op_rank"]) >= config.breach_min_rank, true)
		if b >= 0:
			return _pick(b, "launch: breach at Heat %d with the best operative" % heat)
	# 2. An Exploit, with the best operative.
	if heat <= config.exploit_max_heat:
		var e := _best_launch(meta, func(m: Dictionary) -> bool: return int(m["objective"]) == RC.SiteObjective.EXPLOIT, true)
		if e >= 0:
			return _pick(e, "launch: Exploit Site at Heat %d" % heat)
	# 3. The biggest Heat cut.
	if heat >= config.scrub_min_heat:
		var cut := 0
		for m in meta:
			cut = mini(cut, int(m["heat_change"]))
		if cut < 0:
			var h := _best_launch(meta, func(m: Dictionary) -> bool: return int(m["heat_change"]) == cut, not rotate)
			if h >= 0:
				return _pick(h, "launch: Heat %d, take the %d Heat Site%s" % [heat, cut, " (crew rotation)" if rotate else ""])
	# 4. The deepest Heat-neutral Site up to idle_max_tier, no Heat added.
	var deepest := -1
	for m in meta:
		if int(m["heat_change"]) <= 0 and int(m["objective"]) != RC.SiteObjective.CENTRAL_SERVER and int(m["tier"]) <= config.idle_max_tier:
			deepest = maxi(deepest, int(m["tier"]))
	if deepest >= 0:
		var t := _best_launch(meta, func(m: Dictionary) -> bool: return int(m["heat_change"]) <= 0 and int(m["objective"]) != RC.SiteObjective.CENTRAL_SERVER and int(m["tier"]) == deepest, not rotate)
		if t >= 0:
			return _pick(t, "launch: idle run, tier %d%s" % [deepest, " (crew rotation)" if rotate else ""])
	return _pick(0, "launch: nothing better than the built-in pick")


## The first option matching `want` sent with the highest-ranked (`strongest`) or lowest-ranked
## operative among the matches; -1 when none matches. Ties keep the menu order.
static func _best_launch(meta: Array, want: Callable, strongest: bool) -> int:
	var best := -1
	for i in meta.size():
		if not want.call(meta[i]):
			continue
		if best < 0:
			best = i
			continue
		var r := int(meta[i]["op_rank"])
		var rb := int(meta[best]["op_rank"])
		if (strongest and r > rb) or (not strongest and r < rb):
			best = i
	return best


# --- Raid -------------------------------------------------------------------------------------

func _raid(meta: Array) -> Dictionary:
	var best := 0
	for i in range(1, meta.size()):
		if _raid_key(meta[i]) > _raid_key(meta[best]):
			best = i
	return _pick(best, "raid: best exact projection (home %d after)" % int(meta[best]["home_after"]))


## Lexicographic key: not breached, held, home after, fewest DOWN and TAKEN, most destroyed.
static func _raid_key(m: Dictionary) -> Array:
	return [0 if bool(m["campaign_lost"]) else 1, 1 if bool(m["won"]) else 0, int(m["home_after"]),
		-int(m["down"]) - int(m["taken"]), int(m["threats_destroyed"])]


# --- Shop -------------------------------------------------------------------------------------

func _shop(ctx: Dictionary, meta: Array) -> Dictionary:
	var deck: Array = ctx.get("deck", [])
	var cycles := int(ctx["cycles"])
	# 1. The Bug card goes first.
	for i in meta.size():
		var m: Dictionary = meta[i]
		if String(m["action"]) == "remove" and StringName(String(m["id"])) == &"bug":
			return _pick(i, "shop: remove the Bug card")
	# 2. The best purchase above its threshold, keeping the Cycle reserve.
	var best := -1
	var best_v := -INF
	for i in meta.size():
		var m: Dictionary = meta[i]
		if String(m["action"]) != "buy" or cycles - int(m["price"]) < config.shop_cycle_reserve:
			continue
		var v := _offer_value(m, deck)
		if String(m["kind"]) == "daemon" and v <= config.shop_daemon_min_score:
			continue
		if v > best_v:
			best_v = v
			best = i
	if best >= 0:
		return _pick(best, "shop: buy %s %s (value %.2f)" % [meta[best]["kind"], meta[best]["id"], best_v])
	# 3. Thin the deck: the weakest card at or under shop_remove_max_value.
	if deck.size() > config.shop_thin_deck_min:
		var worst := -1
		var worst_v := INF
		for i in meta.size():
			var m: Dictionary = meta[i]
			if String(m["action"]) != "remove":
				continue
			var v := CampaignSimulator._card_score(lookup.get_content(StringName(String(m["id"]))) as CardData)
			if v <= config.shop_remove_max_value and v < worst_v:
				worst_v = v
				worst = i
		if worst >= 0:
			return _pick(worst, "shop: thin the deck (%s, value %.1f)" % [meta[worst]["id"], worst_v])
	return _pick(0, "shop: nothing worth the Cycles, leave")


# --- HQ ---------------------------------------------------------------------------------------

func _hq(ctx: Dictionary, meta: Array) -> Dictionary:
	var schematics := int(ctx["schematics"])
	var reserve := config.hq_reserve_rookies * int(ctx["rookie_price"])
	for action in config.hq_priority:
		for i in meta.size():
			var m: Dictionary = meta[i]
			if String(m["action"]) != action:
				continue
			var price := int(m.get("price", 0))
			var ok := false
			match action:
				"repair_node", "repair_home":
					ok = true
				"recruit":
					ok = int(ctx["living"]) < config.hq_min_operatives
				"scrub":
					ok = int(ctx["heat"]) >= config.hq_scrub_min_heat and schematics - price >= reserve
				"boost":
					ok = schematics - price >= reserve
				"claim":
					ok = int(ctx["claims"]) < config.hq_max_claims and schematics - price >= reserve
			if ok:
				return _pick(i, "hq: %s for %d Schematics (%d held)" % [action, price, schematics])
	for i in meta.size():
		if String(meta[i]["action"]) == "done":
			return _pick(i, "hq: done, launch")
	return _pick(0, "hq: default upkeep")
