class_name CacheRules
extends RefCounted
## RG-04: the Cache's mini-puzzle gate. The Cache is a plain reward until a puzzle passes the vetting rubric
## (deterministic, solvable by the validator, no soft-lock, no gameplay stream, mouse-only, under 60 s). No puzzle
## is vetted yet, so the config switch alone cannot turn one on.

## Ids of the puzzles that passed vetting (none yet).
const VETTED_PUZZLES: Array[StringName] = []


## Whether a Cache plays its puzzle: the config switch is on AND a vetted puzzle exists.
static func puzzle_active(config: CampaignConfigData) -> bool:
	return config.cache_puzzle_enabled and not VETTED_PUZZLES.is_empty()
