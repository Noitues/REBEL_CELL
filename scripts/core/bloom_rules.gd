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
## corporation or when the pace table gives 0. R-D (Infected Tide): each of the `infected` INFECTED cards moves the start
## front one step closer (`start_front_gap`), a step being the entry pace at the campaign's Heat band `heat_band` and with the
## Virus key `virus`. A start gap of 0 or less is CAUGHT at the first entry.
static func begin(b: BloomState, cfg: CampaignConfigData, corp: CorporationData, tier: int, hq: bool, infected: int = 0,
		heat_band: int = 0, virus: bool = false) -> void:
	var fresh := BloomState.new()
	b.front_milli = fresh.front_milli
	b.layer_milli = 0
	b.doses_taken = 0
	b.caught = false
	b.doses_held = 0
	b.heat_pct = 100
	b.breach_applied = false
	b.hq = hq
	b.enabled = corp != null and corp.id == SOLACE_ID and _pace_node(b, cfg, tier) > 0
	if not b.enabled:
		return
	var gaps := cfg.bloom_start_gap_milli_by_tier
	var start_gap: int = cfg.bloom_hq_start_gap_milli if hq else int(gaps[clampi(tier - 1, 0, gaps.size() - 1)])
	if infected > 0:
		start_gap = start_front_gap(cfg, tier, hq, start_gap, infected, heat_band, virus)
	b.front_milli = -start_gap


## The start gap with `infected` INFECTED cards (R-D): `SolaceTideRules.bloom_start_gap` over this netrun's real entry pace
## (the node pace of `tier`, or the HQ's, scaled by the Heat band and the Virus key).
static func start_front_gap(cfg: CampaignConfigData, tier: int, hq: bool, start_gap: int, infected: int, heat_band: int, virus: bool) -> int:
	var probe := BloomState.new()
	probe.hq = hq
	probe.heat_pct = heat_pct_for_band(cfg, heat_band)
	var pace := scaled_with_virus(probe, cfg, _pace_node(probe, cfg, tier), false, virus)
	return SolaceTideRules.bloom_start_gap(start_gap, pace, infected, cfg)


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


## The base node pace at `tier` (before any multiplier; the HQ number in an HQ run).
static func base_pace_node(b: BloomState, cfg: CampaignConfigData, tier: int) -> int:
	return _pace_node(b, cfg, tier)


static func _pace_node(b: BloomState, cfg: CampaignConfigData, tier: int) -> int:
	if b.hq:
		return cfg.bloom_hq_pace_node_milli
	var t := cfg.bloom_pace_node_milli_by_tier
	return int(t[clampi(tier - 1, 0, t.size() - 1)]) if t.size() > 0 else 0


## Percent of base pace the Heat band `band_idx` (0 COOL .. 4 PURGE) gives (100 = no change).
static func heat_pct_for_band(cfg: CampaignConfigData, band_idx: int) -> int:
	var t := cfg.bloom_pace_heat_pct_by_band
	if t.is_empty():
		return 100
	return int(t[clampi(band_idx, 0, t.size() - 1)])


## Sets the Heat multiplier the next pace reads (the session refreshes it before each entry
## and fight end, so it is read once per event and never drifts).
static func set_heat_band(b: BloomState, cfg: CampaignConfigData, band_idx: int) -> void:
	b.heat_pct = heat_pct_for_band(cfg, band_idx)


## Effective pace of `base` (S2/S6): floor(base x heat% x virus% [x intel% when `turn`] /
## 100^n), minimum 1, computed in one step. A base of 0 or less stays as it is.
static func scaled(b: BloomState, cfg: CampaignConfigData, base: int, turn: bool = false) -> int:
	return _scaled(b, cfg, base, turn, b.key_virus)


## EX-11: the pace `scaled` gives for `base` with the Virus key held (`virus`) or not, whatever `b` holds now (the
## key preview: what the next netrun applies once the Exploit is taken).
static func scaled_with_virus(b: BloomState, cfg: CampaignConfigData, base: int, turn: bool, virus: bool) -> int:
	return _scaled(b, cfg, base, turn, virus)


static func _scaled(b: BloomState, cfg: CampaignConfigData, base: int, turn: bool, virus: bool) -> int:
	if base <= 0:
		return base
	var num := base * b.heat_pct
	var den := 100
	if virus:
		num *= cfg.bloom_virus_pace_pct
		den *= 100
	if turn and b.key_intel:
		num *= cfg.bloom_intel_turn_pct
		den *= 100
	return maxi(1, num / den)


## EX-11: the free start of an exploit building (O0): the operative stands on `layer` and the front does not move.
static func enter_free(b: BloomState, layer: int) -> void:
	if b.enabled and not b.caught:
		b.layer_milli = layer * 1000


## Front advance for entering a node at `tier`; `across` adds the HQ ACROSS cost (free with
## the Breach key). The ACROSS cost is a flat toll, not scaled by pace.
static func entry_pace(b: BloomState, cfg: CampaignConfigData, tier: int, across: bool = false) -> int:
	var p := scaled(b, cfg, _pace_node(b, cfg, tier))
	if across and b.hq and not b.key_breach:
		p += cfg.bloom_pace_cross_milli
	return p


## Front advance for a fight that took `turns` turns. Every fight class pays (no exemption).
static func fight_pace(b: BloomState, cfg: CampaignConfigData, turns: int) -> int:
	return scaled(b, cfg, cfg.bloom_pace_turn_milli, true) * maxi(0, turns)


## The one-time setback the next node entry applies (Breach key, first entry only).
static func pending_setback(b: BloomState, cfg: CampaignConfigData) -> int:
	return cfg.bloom_breach_setback_milli if b.key_breach and not b.breach_applied else 0


## Enters layer `layer` (1-based): the operative moves there and the front advances. Latches
## CAUGHT at gap <= 0. Returns true when this entry caught the operative.
static func enter(b: BloomState, cfg: CampaignConfigData, tier: int, layer: int, across: bool = false) -> bool:
	if not b.enabled or b.caught:
		return b.caught
	b.layer_milli = layer * 1000
	b.front_milli += entry_pace(b, cfg, tier, across) - pending_setback(b, cfg)
	if b.key_breach:
		b.breach_applied = true
	return _latch(b)


## A fight ended after `turns` turns: advance the front (never called mid-fight).
static func end_fight(b: BloomState, cfg: CampaignConfigData, turns: int) -> bool:
	if not b.enabled or b.caught:
		return b.caught
	b.front_milli += fight_pace(b, cfg, turns)
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
	return layer * 1000 - (b.front_milli + entry_pace(b, cfg, tier, across) - pending_setback(b, cfg))


## Intel key: the exact gap on entering each of `layers` (a ladder's layer numbers) assuming
## one node entry per layer from here and no fight turns; no "?" anywhere.
static func ladder_gaps(b: BloomState, cfg: CampaignConfigData, tier: int, layers: Array) -> Dictionary:
	var out := {}
	var cur_layer := b.layer_milli / 1000
	for l in layers:
		var steps := maxi(1, int(l) - cur_layer)
		out[int(l)] = int(l) * 1000 - (b.front_milli + steps * entry_pace(b, cfg, tier) - pending_setback(b, cfg))
	return out
