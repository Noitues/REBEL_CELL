class_name BossPhaseData
extends Resource
## A phase of an enemy with phases (elite, mini-boss, boss; plan 2 R1). Entered when HP
## falls to its floor, ceil(max HP x hp_threshold_pct) (R3); until then damage parks there.

@export_range(0.0, 1.0) var hp_threshold_pct: float = 0.5
@export var pointer_behavior: RC.PointerBehavior = RC.PointerBehavior.FIXED
## New pointer layout on entering the phase (MULTIPLY / MIGRATE).
@export var pointer_ticks: PackedInt32Array = PackedInt32Array()
## ORBIT: pointers move this many ticks each turn (negative = counter-clockwise).
@export var orbit_ticks_per_turn: int = 0
## Optional swaps on entering the phase.
@export var wheel_override: WheelData
@export var hub_override: HubCoreData
@export var spawns: Array[SatelliteSpawnData] = []
@export_multiline var phase_line: String
## Whose statuses clear on entering the phase, after the remap (R6; Q31: NONE by default).
@export var cleanse_on_enter: RC.CleanseScope = RC.CleanseScope.NONE


## The threshold in basis points (RC.THRESHOLD_SCALE), the integer every floor is read from.
func threshold_bp() -> int:
	return roundi(hp_threshold_pct * RC.THRESHOLD_SCALE)


## The HP floor this phase's threshold puts under `max_hp`: ceil(max HP x threshold), in
## integers (0.68 of 100 is 68, never 69 from float error).
static func floor_of(max_hp: int, bp: int) -> int:
	if bp <= 0 or max_hp <= 0:
		return 0
	return (max_hp * bp + RC.THRESHOLD_SCALE - 1) / RC.THRESHOLD_SCALE


## Each error starts with a reason name ("threshold_range:", "cleanse_mode:", ...).
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if hp_threshold_pct <= 0.0 or hp_threshold_pct >= 1.0:
		errors.append("threshold_range: phase threshold %s must be inside (0, 1)." % hp_threshold_pct)
	if int(cleanse_on_enter) < 0 or int(cleanse_on_enter) >= RC.CleanseScope.size():
		errors.append("cleanse_mode: cleanse_on_enter %d is not a CleanseScope." % int(cleanse_on_enter))
	for t in pointer_ticks:
		if t < 0 or t >= RC.TICKS:
			errors.append("Phase pointer tick %d outside 0-%d." % [t, RC.TICKS - 1])
	if pointer_behavior == RC.PointerBehavior.ORBIT and orbit_ticks_per_turn == 0:
		errors.append("ORBIT phase needs orbit_ticks_per_turn.")
	if pointer_behavior in [RC.PointerBehavior.MULTIPLY, RC.PointerBehavior.MIGRATE] and pointer_ticks.is_empty():
		errors.append("MULTIPLY/MIGRATE phase needs pointer_ticks.")
	if wheel_override:
		errors.append_array(wheel_override.validate())
	return errors
