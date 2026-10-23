class_name L4Config
extends RefCounted
## Lab config for the round-4 (L4) sweep raid. Rule numbers mirror tools/raid_concepts/sweep_l4.py (which builds on sweep_l3.py and
## sweep_l2.py); parity_check.gd compares them to the "config" block of data/l4_golden.json.
## Lab keys F1 / F2 change the two toggles; the command line sets them too (--spoofview=range|off, --key=<label>).

const W: int = 4
const H: int = 3
const ASSETS: int = 6
const CANDIDATES: int = 3
const HOME_HP: int = 3
const EXTRA_AT: int = 50
const STRONG_AT: int = 75
const START_HEAT: int = 44
const START_BANK: int = 10
const GHOST_HEAT: int = 5
const EVADE_HEAT: int = 10
const HOME_LOSS_COST: int = 8
const BREACH: int = 100
const RAIDS: int = 3
const MAX_GHOST: int = 1
const MAX_DECOY: int = 2
const MAX_DARK: int = 1
## Leg kit: ghosts, decoys, spoofs and go-dark charges for the whole leg (decoys cost no Schematics; dark still costs the asset next income).
const KIT_START: Dictionary = {"ghost": 2, "decoy": 2, "spoof": 2, "dark": 2}
## One shop buy between raids (Schematics).
const PRICES: Dictionary = {"ghost": 4, "decoy": 3, "spoof": 3, "dark": 3}
## Run intensity: Heat added between raids and the income multiplier (as num / den, income rounded down).
const INTENSITIES: Array = ["LOW", "NORMAL", "HOT"]
const INTENSITY_HEAT: Dictionary = {"LOW": 6, "NORMAL": 12, "HOT": 18}
const INTENSITY_NUM: Dictionary = {"LOW": 1, "NORMAL": 2, "HOT": 3}
const INTENSITY_DEN: int = 2
## The leg score charges this per Heat point above the start Heat.
const HEAT_CARRY: int = 1
## Income divisor (sum of v // 3 over OK, not-dark assets) and repair divisor (v // 2); sweep_l2.py hard-codes both.
const INCOME_DIV: int = 3
const REPAIR_DIV: int = 2
## Display only: the Heat meter's full scale.
const HEAT_MAX: int = 100
## The golden legs the lab can play. The real sealed line is raid.real (seeded per raid), the shape of each candidate raid.shapes.
const LEGS: Array = [0, 3, 5, 8, 11, 14]
const KITS: Array = ["ghost", "decoy", "spoof", "dark"]

## Playout timing in seconds at 1x.
const STEP_T: float = 0.32
const UNSEAL_T: float = 1.1
const TURN_T: float = 1.1
const END_T: float = 0.9

const SPOOF_VIEWS: Array = ["range", "off"]
const KEY_LABELS: Array = ["Schematics", "Scrap", "Credits"]

static var toggles: Dictionary = {"SPOOF_VIEW": "range", "KEY_LABEL": "Schematics"}


## True while the forecast shows where a spoof could save and the result range (it never names a best spoof).
static func spoof_view() -> bool:
	return String(toggles["SPOOF_VIEW"]) == "range"


static func key_label() -> String:
	return String(toggles["KEY_LABEL"])


## Cycle one toggle (lab keys F1, F2).
static func cycle(tog_name: String) -> void:
	var opts: Array = {"SPOOF_VIEW": SPOOF_VIEWS, "KEY_LABEL": KEY_LABELS}[tog_name]
	toggles[tog_name] = opts[(opts.find(toggles[tog_name]) + 1) % opts.size()]


static func reset() -> void:
	toggles = {"SPOOF_VIEW": "range", "KEY_LABEL": "Schematics"}
