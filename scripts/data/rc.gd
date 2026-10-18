class_name RC
extends RefCounted
## Shared constants and enums for every REBEL_CELL data resource.

const TICKS: int = 30
const SLICES: int = 6
const TICKS_PER_SLICE: int = 5
const RING_SEGMENTS: int = 3
const TICKS_PER_RING_SEGMENT: int = 10

# --- Combat ---
## INFECT applies statuses via extra_effects (e.g. Solace DOSE). HOTFIX is enemy-facing.
enum SliceType { SHIM, OVERFLOW, DEFRAG, DETOUR, SANDBOX, TROJAN, HOTFIX, INFECT, NULL }
enum TargetRule { SELF, POINTER, SWEEP, CHOSEN }
## Ordered low to high so tiers can be compared with >=. There is no Miss
## tier: every landing is within 2 ticks of some slice centre (GDD 2.4).
enum PrecisionTier { WEAK, GOOD, PERFECT }
## PARASITE (Botnet, 2026-09-24): a parasite drone halves the slice's output until cleansed.
enum Status { NONE, CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE }
enum RingScope { OUTER, INNER, WHOLE_WHEEL }
enum NeighborRule { NONE, MIRROR, SHUNT }
enum ResistanceRefresh { NONE, EACH_PLAYER_TURN }
enum WheelTarget { OWN, ENEMY, ANY, SATELLITE }
enum Rarity { COMMON, UNCOMMON, RARE, BOSS }

enum Trigger {
	PASSIVE,
	ON_COMBAT_START,
	ON_TURN_START,
	ON_CARD_PLAYED,
	ON_NUDGE,
	ON_SLICE_TRIGGER,
	ON_PERFECT,
	## The NULL *slice* resolved (not a precision tier).
	ON_NULL_SLICE,
	ON_TURN_END,
	ON_COMBAT_END,
	ON_SERVER_RACK_CAPTURE,
	ON_NETRUN_COMPLETE,
	ON_RAID_START,
	## Fired once per RESOLVE with the collected resolutions in the context
	## ("resolutions": Array[Dictionary]) so rule-breaking Daemons can rewrite them
	## before the passes run (Stolen Intent).
	ON_RESOLVE,
}

enum EffectType {
	DEAL_DAMAGE,
	GAIN_BLOCK,
	GAIN_SHIELD,
	EVADE,
	APPLY_STATUS,
	NUDGE,
	SPIN,
	FLIP,
	RESPIN,
	FREEZE,
	MODIFY_RESISTANCE,
	HUB_BREACH,
	GAIN_RAM,
	DRAIN_RAM,
	HEAL,
	CLEANSE,
	SNAP_TO_CENTER,
	DRAW_CARDS,
	DEPLOY_DRONE,
	RETRIGGER,
	DOUBLE_NUDGE_CARDS,
	MODIFY_HEAT,
	GAIN_CYCLES,
	GAIN_SCHEMATICS,
	CUSTOM,
}

enum EffectTarget { SELF, OWN_WHEEL, TARGET_WHEEL, POINTER_TARGET, ALL_ENEMIES, CHOSEN, CAMPAIGN }
## Which slice of the target wheel a slice-level effect (APPLY_STATUS, CLEANSE) hits:
## the slice under the pointer (Overdrive, Corrupt segment), a random non-NULL slice
## (Solace DOSE), or one the player picks (Cleanse, Encrypt).
enum SlicePick { UNDER_POINTER, RANDOM_NON_NULL, CHOSEN }
## How a heal, block, shield or corruption amount reads (plan 2 R5, N1). FLAT: the number
## itself (an enemy's is multiplied by its tier damage factor, R2). PERCENT: a share of the
## owner's max HP (heal, block, shield) or of the target's non-NULL slices (corruption),
## rounded to nearest, minimum 1, never rescaled. Append-only: FLAT = 0 so old content loads FLAT.
enum AmountMode { FLAT, PERCENT }
## A PERCENT amount is a share out of this (a definition, not a tuning number).
const PERCENT_MAX: int = 100

# --- Netrun map ---
enum InfilNodeType { ROUTER, TERMINAL, MAINFRAME, SERVER_RACK }

# --- City Grid & network ---
enum SiteObjective { NONE, EXPLOIT, HEAT_REDUCTION, RECLAIM, CENTRAL_SERVER }
enum ExploitType { NONE, INTEL, BREACH, VIRUS }
enum NetworkNodeType { HOME_SERVER, RELAY, FIREWALL_RELAY, COMPILER_RACK, VAULT_TERMINAL, PROXY_RELAY, SAFEHOUSE }

# --- Cell Defense ---
enum AssetType { TURRET, ICE_LOCK, DECOY }
enum AssetTargeting { FIRST_IN_PATH, LOWEST_INTEGRITY, HIGHEST_DAMAGE }
enum ThreatRouting { SHORTEST_TO_HOME, HIGHEST_VALUE, WEAKEST_NODE }

# --- Enemies & bosses ---
enum PointerBehavior { FIXED, MULTIPLY, MIGRATE, ORBIT }
## Whose wheel statuses a phase clears as it is entered, after the status remap (plan 2 R6,
## N3). OWN = the enemy and the satellites docked on it; PLAYER = the operative and its
## drones. Append-only: NONE = 0, so phases authored before N3 keep every status (Q31).
enum CleanseScope { NONE, OWN, PLAYER, BOTH }
## Phase thresholds are read in parts of this (basis points), so a floor is integer
## arithmetic: ceil(max HP x bp / THRESHOLD_SCALE) (a definition, not a tuning number).
const THRESHOLD_SCALE: int = 10000
## Enemy classes, the index of the per-class config tables (phase counts, R1).
enum EnemyClass { NORMAL, ELITE, MINI_BOSS, BOSS }

# --- Campaign ---
enum ThresholdKind { MINOR, MAJOR, PURGE }
enum RaidTriggerSource { HEAT_THRESHOLD, TERRITORY_CLAIM, NODE_BUILT, STORY, RETALIATION }
## Numeric rule changes shared by ICE levels and Heat thresholds.
enum RuleModifierType {
	HEAT_GAIN_PCT,
	HEAT_SINK_PCT,
	HEAT_OBJECTIVE_SITES,
	ELITE_FREQUENCY_PCT,
	CYCLE_PRICE_PCT,
	SHOP_STOCK,
	RAID_STRENGTH_PCT,
	RAID_EXTRA_WAVE,
	ENEMY_RESISTANCE,
	DEATH_HEAT,
	EXPLOIT_HEAT,
	## Unused since M1 (designer swapped it for BOSS_STRENGTH_PCT). Kept so stored
	## enum values keep their numbers.
	BOSS_PHASE_EARLY,
	BOSS_EXTRA_POINTER,
	STARTING_BUG_CARD,
	NO_FIRST_TURN_FREE_NUDGE,
	REPAIR_COST_PCT,
	TAKEN_RAID_STRENGTH_PCT,
	PURGE_THRESHOLD,
	## Boss HP and damage +N% (ICE ladder).
	BOSS_STRENGTH_PCT,
}

# --- Narrative ---
enum Voice { NARRATOR, STREET_MERC, CORPO, AI_OBSERVER, DISPATCH }

# --- Profile ---
enum UnlockKind { CLASS, CLASS_ALTERNATIVE, CORPORATION, HOME_SERVER, NODE_TYPE, SKIN }
