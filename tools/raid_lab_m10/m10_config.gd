class_name M10Config
extends RefCounted
## Lab config for the M10 sweep raid. Rule numbers mirror tools/raid_concepts/ghost2.py (checked by parity_check.gd
## against data/m10_golden.json "config"). The three designer toggles live in `toggles` and are changed in the lab
## with F1 / F2 / F3 or the command line (--spoof=choice|press, --repair=value|half, --key=<label>).

const W: int = 4
const H: int = 3
const GHOST_HEAT: int = 5
const HEAT_VALUE: float = 0.4
const DECOY_COST: int = 3
const EVADE: int = 6
const MAX_GHOST: int = 1
const MAX_DECOY: int = 1
const MAX_DARK: int = 3
const BEAMS: int = 3
## Campaign numbers of the lab leg (from concept_m9_base.py: KEY 25, KEY_HAVE 19, Heat 52, notch 50).
const KEY_MAX: int = 25
const KEY_START: int = 19
const HEAT_START: int = 52
const HEAT_NOTCH: int = 50
const HEAT_MAX: int = 100
const EVADE_HEAT: int = 10
## Between two raids of the leg a run happens: it adds Heat (the cause of the next contact) and key income.
const RUN_HEAT: int = 12
const RUN_KEY: int = 12
const RUN_NODES: int = 4
## The lab leg: golden network seeds, reveal = candidate 0 for each.
const LEG_SEEDS: Array = [22, 17, 25]
const LEG_REVEAL: int = 0

## Playout timing in seconds at 1x.
const STEP_T: float = 0.32
const LEAD_T: float = 0.5
const UNSEAL_T: float = 1.1
const HUNTER_T: float = 1.2
const END_T: float = 0.9
## SPOOF_MODE "press": the ring converges on the node and is exact at PRESS_PERFECT; SPACE within PRESS_TOL lands it.
const PRESS_WINDOW: float = 1.0
const PRESS_PERFECT: float = 0.7
const PRESS_TOL: float = 0.22

const SPOOF_MODES: Array = ["choice", "press"]
const REPAIR_MODES: Array = ["value", "half"]
const KEY_LABELS: Array = ["Schematics", "Scrap", "Credits"]

static var toggles: Dictionary = {"SPOOF_MODE": "choice", "REPAIR": "value", "KEY_LABEL": "Schematics"}


static func spoof_mode() -> String:
	return String(toggles["SPOOF_MODE"])


static func repair_mode() -> String:
	return String(toggles["REPAIR"])


static func key_label() -> String:
	return String(toggles["KEY_LABEL"])


## Cycle one toggle (lab keys F1..F3).
static func cycle(name: String) -> void:
	var opts: Array = {"SPOOF_MODE": SPOOF_MODES, "REPAIR": REPAIR_MODES, "KEY_LABEL": KEY_LABELS}[name]
	toggles[name] = opts[(opts.find(toggles[name]) + 1) % opts.size()]


static func reset() -> void:
	toggles = {"SPOOF_MODE": "choice", "REPAIR": "value", "KEY_LABEL": "Schematics"}
