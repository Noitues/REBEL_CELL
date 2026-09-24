class_name BossPhaseData
extends Resource
## A boss phase. Entered when HP falls to hp_threshold_pct (7.4).

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


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
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
