class_name SolaceRaidRules
extends RefCounted
## Plan 2 WH-12 (Solace raid hook, docs/handoff/plan2/drafts/themes/solace.md section 1 rules
## 15-20): the population infection figure of a Solace raid. Basis points (0..10000, the
## percentage is bp / 100). v2 (S1): it is ONE campaign figure (CampaignState.corp_theme.solace),
## never reset per raid. It rises each resolution step by base + per_threat x living threats,
## falls only by the decay hooks (a raid that CELL HOLDS, cure objectives), and at the config
## threshold the city is infected and Solace wins the raid. Pure functions of (heat, per-step living-threat counts)
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


## Infection (bp) a raid starts at: the campaign's figure.
static func start_bp(campaign: CampaignState, cfg: CampaignConfigData) -> int:
	return clampi(campaign.corp_theme.solace.infection_bp, 0, cfg.raid_infection_lost_bp)


## Whether a raid ended CELL HOLDS: the campaign survived and no node was TAKEN.
static func cell_holds(campaign_lost: bool, taken_count: int) -> bool:
	return not campaign_lost and taken_count <= 0


## Decay (bp) a raid that CELL HOLDS gives: the flat amount plus the per-kill amount.
static func hold_decay_bp(threats_destroyed: int, cfg: CampaignConfigData) -> int:
	return maxi(0, cfg.raid_infection_decay_hold_bp + cfg.raid_infection_decay_per_kill_bp * maxi(0, threats_destroyed))


## `bp` after a fall of `amount`, never below 0.
static func after_decay(bp: int, amount: int) -> int:
	return maxi(0, bp - maxi(0, amount))


## A cure (Heat objective Site or Proxy Relay completion) on a Solace campaign: the figure falls by
## decay_cure_bp. Returns the bp removed (0 outside Solace or at 0).
static func cure(campaign: CampaignState, cfg: CampaignConfigData) -> int:
	if not applies(campaign):
		return 0
	var before := campaign.corp_theme.solace.infection_bp
	campaign.corp_theme.solace.infection_bp = after_decay(before, cfg.raid_infection_decay_cure_bp)
	return before - campaign.corp_theme.solace.infection_bp


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


## The raid setup's exact projection of the infection from a resolved raid `r` (the projection or
## the played-out result: the same numbers): {"applies", "now_pct", "end_pct" (after the decay),
## "peak_pct" (before it), "lost_step" (-1 = never), "holds" (CELL HOLDS), "rate_pct" (the first
## step's rise, +n%/step), "decay_pct" (what CELL HOLDS takes off)}.
static func preview(r: RaidResolver.RaidResult, cfg: CampaignConfigData) -> Dictionary:
	if r == null or not r.infection_applies:
		return {"applies": false}
	var rate := 0
	if r.infection_figures.size() > 1:
		rate = r.infection_figures[1] - r.infection_figures[0]
	else:
		rate = step_rise_bp(0, cfg)
	return {"applies": true, "now_pct": pct(r.infection_start_bp), "end_pct": pct(r.infection_end_bp), "peak_pct": pct(r.infection_bp),
		"lost_step": lost_step(r.infection_figures, cfg), "holds": not r.campaign_lost and r.taken.is_empty(),
		"rate_pct": rate / BP_PER_PERCENT, "decay_pct": hold_decay_potential_pct(r, cfg)}


## What CELL HOLDS would take off with the threats this raid destroys (a held raid's decay).
static func hold_decay_potential_pct(r: RaidResolver.RaidResult, cfg: CampaignConfigData) -> int:
	return pct(hold_decay_bp(r.threats_destroyed, cfg))


## The raid HUD's whole-percent figure (0..100) for `bp`.
static func pct(bp: int) -> int:
	return bp / BP_PER_PERCENT


## The raid HUD's chip value for "+n%/step" (whole percent, rounded down) with `living` threats.
static func rate_pct(living: int, cfg: CampaignConfigData) -> int:
	return step_rise_bp(living, cfg) / BP_PER_PERCENT
