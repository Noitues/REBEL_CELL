class_name SolaceRaidRules
extends RefCounted
## Plan 2 WH-12 (Solace raid hook, docs/handoff/plan2/drafts/themes/solace.md section 1 rules
## 15-20): the population infection figure of a Solace raid. Basis points (0..10000, the
## percentage is bp / 100). It starts at the Heat band's value, rises each resolution step by
## base + per_threat x living threats, never falls, and at the config threshold the city is
## infected and Solace wins the raid. Pure functions of (heat, per-step living-threat counts)
## and the config: no randomness, every number from CampaignConfigData. Operatives are never
## touched here (Q24.1 / RD-03: operatives are never killed during raids).

const SOLACE_ID := &"solace"
## Unit conversion, not tuning: basis points per whole percent.
const BP_PER_PERCENT := 100


## True when raids of `campaign` carry the infection figure (Solace only).
static func applies(campaign: CampaignState) -> bool:
	return campaign != null and campaign.corporation_id == SOLACE_ID


## The Heat band index (0 COOL, 1 NOTICED, 2 FLAGGED, 3 HUNTED, 4 PURGE) for `heat`.
static func heat_band_index(campaign: CampaignState, cfg: CampaignConfigData) -> int:
	var idx := 0
	for lv in HeatRules.band_levels(campaign, cfg):
		if campaign.heat >= lv:
			idx += 1
	return idx


## Infection (bp) a raid starts at for the campaign's current Heat band.
static func start_bp(campaign: CampaignState, cfg: CampaignConfigData) -> int:
	var t := cfg.raid_infection_start_bp_by_band
	if t.is_empty():
		return 0
	return clampi(int(t[clampi(heat_band_index(campaign, cfg), 0, t.size() - 1)]), 0, cfg.raid_infection_lost_bp)


## Rise of one resolution step with `living` threats still alive (never negative).
static func step_rise_bp(living: int, cfg: CampaignConfigData) -> int:
	return maxi(0, cfg.raid_infection_bp_base + cfg.raid_infection_bp_per_threat * maxi(0, living))


## One step: the new figure, capped at the lost threshold.
static func advance(current_bp: int, living: int, cfg: CampaignConfigData) -> int:
	return mini(cfg.raid_infection_lost_bp, current_bp + step_rise_bp(living, cfg))


## True when `bp` has reached the CITY LOST threshold.
static func is_lost(bp: int, cfg: CampaignConfigData) -> bool:
	return bp >= cfg.raid_infection_lost_bp


## The figures after each step for a living-threat count per step: index 0 is the start,
## index i the figure after step i. Stops growing once lost. Pure: the same counts give the
## same figures.
static func figures(start: int, living_per_step: Array[int], cfg: CampaignConfigData) -> Array[int]:
	var out: Array[int] = [start]
	var cur := start
	for n in living_per_step:
		if not is_lost(cur, cfg):
			cur = advance(cur, n, cfg)
		out.append(cur)
	return out


## First step (1-based) at which the figures reach CITY LOST, or -1 if never.
static func lost_step(fig: Array[int], cfg: CampaignConfigData) -> int:
	for i in fig.size():
		if is_lost(fig[i], cfg):
			return i
	return -1


## The raid HUD's whole-percent figure (0..100) for `bp`.
static func pct(bp: int) -> int:
	return bp / BP_PER_PERCENT


## The raid HUD's chip value for "+n%/step" (whole percent, rounded down) with `living` threats.
static func rate_pct(living: int, cfg: CampaignConfigData) -> int:
	return step_rise_bp(living, cfg) / BP_PER_PERCENT
