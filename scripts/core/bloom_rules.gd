class_name BloomRules
extends RefCounted
## Plan 2 WH-11 (Solace THE BLOOM, docs/handoff/plan2/drafts/themes/solace.md): the virus front
## that trails the operative. Pure functions over a BloomState and the config; no randomness
## (nothing here reads an RngService stream), every number from CampaignConfigData.
## Units: thousandths of a layer. Gap = layer_milli - front_milli. The front moves only on
## node entry and when a fight ends, never inside one (so a fight can't latch CAUGHT).

enum Band { DORMANT, CREEPING, CLOSE, CATCHING, CAUGHT }

## The corporation whose netruns carry the Bloom (identity, not a tuning number).
const SOLACE_ID := &"solace"


## Starts the Bloom on `b` for a netrun of `tier` (1..4) or an HQ run. Disabled for any other
## corporation or when the pace table gives 0.
static func begin(b: BloomState, cfg: CampaignConfigData, corp: CorporationData, tier: int, hq: bool) -> void:
	var fresh := BloomState.new()
	b.front_milli = fresh.front_milli
	b.layer_milli = 0
	b.doses_taken = 0
	b.caught = false
	b.doses_held = 0
	b.hq = hq
	b.enabled = corp != null and corp.id == SOLACE_ID and _pace_node(b, cfg, tier) > 0
	if not b.enabled:
		return
	var gaps := cfg.bloom_start_gap_milli_by_tier
	var start_gap: int = cfg.bloom_hq_start_gap_milli if hq else int(gaps[clampi(tier - 1, 0, gaps.size() - 1)])
	b.front_milli = -start_gap
	if tier == 1 and not hq:
		b.doses_held = cfg.bloom_free_doses_t1


static func gap_milli(b: BloomState) -> int:
	return b.layer_milli - b.front_milli


## The band of the current gap. `entered` false (no node entered yet) = DORMANT.
static func band(b: BloomState, cfg: CampaignConfigData, entered: bool = true) -> Band:
	if not b.enabled or not entered:
		return Band.DORMANT
	return band_for_gap(gap_milli(b), cfg)


static func band_for_gap(gap: int, cfg: CampaignConfigData) -> Band:
	if gap <= 0:
		return Band.CAUGHT
	if gap <= cfg.bloom_catch_gap_milli:
		return Band.CATCHING
	if gap <= cfg.bloom_close_gap_milli:
		return Band.CLOSE
	return Band.CREEPING


static func _pace_node(b: BloomState, cfg: CampaignConfigData, tier: int) -> int:
	if b.hq:
		return cfg.bloom_hq_pace_node_milli
	var t := cfg.bloom_pace_node_milli_by_tier
	return int(t[clampi(tier - 1, 0, t.size() - 1)]) if t.size() > 0 else 0


## Virus key: floor(pace x pct / 100), minimum 1; applied once to a base pace.
static func scaled(b: BloomState, cfg: CampaignConfigData, base: int) -> int:
	if not b.key_virus or base <= 0:
		return base
	return maxi(1, base * cfg.bloom_virus_pace_pct / 100)


## Front advance for entering a node at `tier`; `across` adds the HQ ACROSS cost.
static func entry_pace(b: BloomState, cfg: CampaignConfigData, tier: int, across: bool = false) -> int:
	var p := scaled(b, cfg, _pace_node(b, cfg, tier))
	if across and b.hq:
		p += cfg.bloom_pace_cross_milli
	return p


## Front advance for a fight that took `turns` turns; bosses and mini-bosses are exempt (S3).
static func fight_pace(b: BloomState, cfg: CampaignConfigData, turns: int, boss: bool) -> int:
	if boss and cfg.bloom_exempt_boss_turn_cost:
		return 0
	return scaled(b, cfg, cfg.bloom_pace_turn_milli) * maxi(0, turns)


## Enters layer `layer` (1-based): the operative moves there and the front advances. Latches
## CAUGHT at gap <= 0. Returns true when this entry caught the operative.
static func enter(b: BloomState, cfg: CampaignConfigData, tier: int, layer: int, across: bool = false) -> bool:
	if not b.enabled or b.caught:
		return b.caught
	b.layer_milli = layer * 1000
	b.front_milli += entry_pace(b, cfg, tier, across)
	return _latch(b)


## A fight ended after `turns` turns: advance the front (never called mid-fight).
static func end_fight(b: BloomState, cfg: CampaignConfigData, turns: int, boss: bool) -> bool:
	if not b.enabled or b.caught:
		return b.caught
	b.front_milli += fight_pace(b, cfg, turns, boss)
	return _latch(b)


static func _latch(b: BloomState) -> bool:
	if gap_milli(b) <= 0:
		b.caught = true
	return b.caught


## The front after pushing it back by one dose, with the gap clamped to max_gap.
static func push(b: BloomState, cfg: CampaignConfigData) -> void:
	if not b.enabled or b.caught:
		return
	b.front_milli -= cfg.bloom_dose_push_milli
	if gap_milli(b) > cfg.bloom_max_gap_milli:
		b.front_milli = b.layer_milli - cfg.bloom_max_gap_milli


## Uses a held dose. False (state unchanged) with none held.
static func use_dose(b: BloomState, cfg: CampaignConfigData) -> bool:
	if not b.enabled or b.caught or b.doses_held <= 0:
		return false
	b.doses_held -= 1
	b.doses_taken += 1
	push(b, cfg)
	return true


## HQ ward rest: the REST node's dose_push (no dose consumed), after the rung's entry pace.
static func ward_rest(b: BloomState, cfg: CampaignConfigData) -> void:
	push(b, cfg)


## A room on `layer` (1-based; the same layer on both HQ towers) is INFECTED when the front
## has reached it: layer <= floor(front). Display only.
static func room_infected(b: BloomState, layer: int) -> bool:
	return b.enabled and b.front_milli >= 0 and layer <= b.front_milli / 1000


## Gap after entering `layer` from the current state (exact, same as `enter` would give).
static func gap_after_entry(b: BloomState, cfg: CampaignConfigData, tier: int, layer: int, across: bool = false) -> int:
	return layer * 1000 - (b.front_milli + entry_pace(b, cfg, tier, across))


## Intel key: the exact gap on entering each of `layers` (a ladder's layer numbers) assuming
## one node entry per layer from here and no fight turns; no "?" anywhere.
static func ladder_gaps(b: BloomState, cfg: CampaignConfigData, tier: int, layers: Array) -> Dictionary:
	var out := {}
	var cur_layer := b.layer_milli / 1000
	for l in layers:
		var steps := maxi(1, int(l) - cur_layer)
		out[int(l)] = int(l) * 1000 - (b.front_milli + steps * entry_pace(b, cfg, tier))
	return out
