class_name RC
extends RefCounted
## Shared constants and enums for every REBEL_CELL data resource.

const TICKS: int = 30
const SLICES: int = 6
const TICKS_PER_SLICE: int = 5
const RING_SEGMENTS: int = 3
const TICKS_PER_RING_SEGMENT: int = 10

# --- Combat ---
## AFFLICT applies statuses via extra_effects (e.g. Solace DOSE). HEAL is enemy-facing.
enum SliceType { ATTACK, CRIT, DEFEND, EVADE, SHIELD, DEPLOY, HEAL, AFFLICT, MISS }
enum TargetRule { SELF, POINTER, SWEEP, CHOSEN }
## Ordered low to high so tiers can be compared with >=. There is no Miss
## tier: every landing is within 2 ticks of some slice centre (GDD 2.4).
enum PrecisionTier { PARTIAL, GOOD, PERFECT }
enum Status { NONE, CORRUPTED, OVERCLOCKED, ENCRYPTED }
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
	## The Miss *slice* resolved (not a precision tier).
	ON_MISS_SLICE,
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
## the slice under the pointer (Overdrive, Corrupt segment), a random non-Miss slice
## (Solace DOSE), or one the player picks (Cleanse, Encrypt).
enum SlicePick { UNDER_POINTER, RANDOM_NON_MISS, CHOSEN }

# --- Netrun map ---
enum InfilNodeType { ROUTER, TERMINAL, MODEM, SERVER_RACK }

# --- City Grid & network ---
enum SiteObjective { NONE, EXPLOIT, HEAT_REDUCTION, RECLAIM, BOSS }
enum ExploitType { NONE, INTEL, BREACH, VIRUS }
enum NetworkNodeType { HOME_SERVER, RELAY, FIREWALL_RELAY, COMPILER_RACK, VAULT_TERMINAL, PROXY_RELAY, SAFEHOUSE }

# --- Cell Defense ---
enum AssetType { TURRET, ICE_LOCK, DECOY }
enum AssetTargeting { FIRST_IN_PATH, LOWEST_INTEGRITY, HIGHEST_DAMAGE }
enum ThreatRouting { SHORTEST_TO_HOME, HIGHEST_VALUE, WEAKEST_NODE }

# --- Enemies & bosses ---
enum PointerBehavior { FIXED, MULTIPLY, MIGRATE, ORBIT }

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
	SEIZED_RAID_STRENGTH_PCT,
	PURGE_THRESHOLD,
	## Boss HP and damage +N% (ICE ladder).
	BOSS_STRENGTH_PCT,
}

# --- Narrative ---
enum Voice { NARRATOR, STREET_MERC, CORPO, AI_OBSERVER, DISPATCH }

# --- Profile ---
enum UnlockKind { CLASS, CLASS_ALTERNATIVE, CORPORATION, HOME_SERVER, NODE_TYPE, SKIN }
