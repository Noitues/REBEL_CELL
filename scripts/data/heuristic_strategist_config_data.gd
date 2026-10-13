class_name HeuristicStrategistConfigData
extends Resource
## Thresholds of the playtest HeuristicStrategist (tools/agent/heuristic_strategist.gd, slice
## Tooling 1 T2; docs/process/PLAYTEST_COST_REVIEW.md §3): the deterministic, LLM-free answer to
## every state-tester decision. Playtest tooling only: the game never reads it. Read-only at
## runtime; the shipped values live in `content/config/heuristic_strategist.tres`. Launch and
## HQ rules are distilled from SA-001's launch decisions and reasons (DECISIONS 2026-10-12).

## Where the shipped config lives.
const CONFIG_PATH := "res://content/config/heuristic_strategist.tres"
## The HQ actions `hq_priority` may name, in no particular order.
const HQ_ACTIONS: Array[String] = ["repair_node", "repair_home", "recruit", "scrub", "boost", "claim"]

@export_group("Combat")
## Plans whose planner score is within this of the best plan's count as tied; ties go to the
## plan taking the least HP, then the most kills, then the planner's order.
@export var combat_tie_epsilon: float = 0.001
## Turns the planner looks ahead (1 = the current turn only; 2 = the CP-003 3A variant: each plan
## is scored with the best plan of the next turn after it).
@export var lookahead_turns: int = 1
## Weight of the next turn's HP taken against this turn's, in the 2-turn lookahead.
@export var lookahead_next_weight: float = 1.0
## Lookahead value of a plan that wins the fight this turn (no next turn to score).
@export var lookahead_win_bonus: float = 1000.0

@export_group("Map nodes")
## Below this share of max HP an Elite node is avoided.
@export var elite_min_hp_share: float = 0.6
## Below this share of max HP Terminals (events) and Mainframes (shops) are preferred.
@export var low_hp_share: float = 0.5
## Base value per node kind (ROUTER fight, ELITE fight, TERMINAL event, MAINFRAME shop, SERVER_RACK).
@export var node_value_router: float = 40.0
@export var node_value_elite: float = 30.0
@export var node_value_terminal: float = 20.0
@export var node_value_mainframe: float = 10.0
@export var node_value_server_rack: float = 50.0
## Added to Terminals and Mainframes when HP is low; subtracted from fights.
@export var node_low_hp_bonus: float = 35.0
## Elite value when HP is under elite_min_hp_share.
@export var node_value_elite_low: float = -50.0
## A Mainframe is worth its rich value at or above this many Cycles.
@export var mainframe_rich_cycles: int = 75
@export var node_value_mainframe_rich: float = 60.0
## Value lost per point of node Heat, times (1 + campaign Heat / node_heat_scale).
@export var node_heat_weight: float = 3.0
@export var node_heat_scale: float = 25.0

@export_group("Rewards")
## A card offer is taken when its value is above this (CampaignSimulator._card_score scale).
@export var card_min_value: float = 1.5
## No more cards past this deck size.
@export var deck_max: int = 16
## Value per deck card sharing an effect type with the offer, capped at synergy_cap.
@export var synergy_per_match: float = 0.25
@export var synergy_cap: float = 1.0
## Value added per rarity step above COMMON.
@export var rarity_bonus: float = 0.25
## A Firmware offer is taken when its score is above this (Heat-costing Firmware never).
@export var firmware_min_score: float = 0.0
## A Daemon offer is taken when its score is above this.
@export var daemon_min_score: float = 0.0

@export_group("Launch, Heat and crew")
## Breach the Central Server when open, Heat is at most this and the operative's Rank is at least breach_min_rank.
@export var breach_max_heat: int = 10
@export var breach_min_rank: int = 3
## Take an Exploit Site while Heat is at most this.
@export var exploit_max_heat: int = 40
## Run the biggest Heat-reducing Site at or above this Heat.
@export var scrub_min_heat: int = 10
## With nothing to chase, run Sites up to this tier.
@export var idle_max_tier: int = 2
## The lower-ranked operative takes the Heat and idle runs while its Rank trails the best by at
## least this (crew rotation); otherwise the best operative goes.
@export var rotate_rank_gap: int = 4

@export_group("HQ")
## HQ sinks in priority order; one purchase per HQ decision while the rule allows it.
@export var hq_priority: Array[String] = ["repair_node", "repair_home", "recruit", "scrub", "boost", "claim"]
## Recruit while fewer operatives live.
@export var hq_min_operatives: int = 2
## Scrub Heat at HQ at or above this.
@export var hq_scrub_min_heat: int = 10
## Optional sinks (scrub, boost, claim) keep this many rookies' price in reserve.
@export var hq_reserve_rookies: int = 1
## Next-run boosts only while this many Schematics stay after the purchase (Heat scrubs come first).
@export var hq_boost_min_schematics: int = 150
## Claim at most this many nodes besides home.
@export var hq_max_claims: int = 2

@export_group("Shop")
## Cycles kept after any shop purchase except Bug removal.
@export var shop_cycle_reserve: int = 0
## Buy a Daemon scoring above this, a Firmware above firmware_min_score, a card above card_min_value.
@export var shop_daemon_min_score: float = 2.0
## Remove the weakest card while the deck has more than this many cards.
@export var shop_thin_deck_min: int = 10
## Remove a card only when its value is at most this.
@export var shop_remove_max_value: float = 1.0


## Errors in the thresholds; empty when valid.
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if lookahead_turns < 1 or lookahead_turns > 2:
		errors.append("Heuristic strategist: lookahead_turns must be 1 or 2.")
	if elite_min_hp_share < 0.0 or elite_min_hp_share > 1.0 or low_hp_share < 0.0 or low_hp_share > 1.0:
		errors.append("Heuristic strategist: HP shares must be in [0, 1].")
	if deck_max < 1 or shop_thin_deck_min < 1:
		errors.append("Heuristic strategist: deck sizes must be >= 1.")
	if node_heat_scale <= 0.0:
		errors.append("Heuristic strategist: node_heat_scale must be > 0.")
	for a in hq_priority:
		if a not in HQ_ACTIONS:
			errors.append("Heuristic strategist: unknown HQ action '%s'." % a)
	return errors


## The shipped config.
static func shipped() -> HeuristicStrategistConfigData:
	return load(CONFIG_PATH) as HeuristicStrategistConfigData
