class_name HpBandLint
extends RefCounted
## N2 (CONTENT_DESIGN_V2 R1 / R2): lints enemy HP tables against the class bands in
## CampaignConfigData and computes the R2 phase budget. Pure; reads only, never mutates.
## Bosses are checked against a phase-budget ceiling as a WARNING only (designer ruling
## 2026-10-18 Q29: never shorten boss phases to fit a band).


## R2 phase budget: (reference_dpt[tier] x needles - the phase's sustain per turn) x
## target_turns_per_phase, floored (Genome Core P1 at T4: (18 - 3) x 3.5 = 52).
static func phase_budget(config: CampaignConfigData, tier: int, needles: int = 1, sustain_per_turn: float = 0.0) -> int:
	return floori((config.reference_dpt(tier) * needles - sustain_per_turn) * config.target_turns_per_phase)


## The most HP a boss of `phase_count` phases should have before the lint warns: every
## phase at the top-tier budget with two needles and no sustain.
static func boss_budget_ceiling(config: CampaignConfigData, phase_count: int) -> int:
	return phase_count * phase_budget(config, config.reference_dpt_by_tier.size(), 2)


## Lints `enemies` (sorted by id, so the report is deterministic). Returns
## {"errors": PackedStringArray, "warnings": PackedStringArray}: errors are the HP-table
## problems EnemyData.validate(config) finds (each names the enemy, index and tier);
## warnings name enemies still on the legacy multiplier (not migrated) and bosses whose
## base band is above their budget ceiling.
static func lint(enemies: Array[EnemyData], config: CampaignConfigData) -> Dictionary:
	var sorted: Array[EnemyData] = []
	for e in enemies:
		if e != null:
			sorted.append(e)
	sorted.sort_custom(func(a: EnemyData, b: EnemyData) -> bool: return String(a.id) < String(b.id))
	var errors := PackedStringArray()
	var warnings := PackedStringArray()
	for e in sorted:
		if not e.uses_hp_table():
			warnings.append("Enemy %s not migrated: legacy hp %d x tier multiplier." % [e.id, e.hp])
			continue
		for problem in e.validate(config):
			if problem.contains("hp_by_tier") or problem.contains("hp_bands"):
				errors.append(problem)
		if e.is_boss:
			var phase_count := e.phases.size() + 1
			var ceiling := boss_budget_ceiling(config, phase_count)
			var base := e.hp_for(1.0)
			if base > ceiling:
				warnings.append("Enemy %s hp_bands base HP %d above boss budget %d (%d phases)." % [e.id, base, ceiling, phase_count])
	return {"errors": errors, "warnings": warnings}
