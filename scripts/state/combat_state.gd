class_name CombatState
extends RefCounted
## The whole of one combat as plain data (TECH_SPEC 5.2). Duplicable, hashable,
## serialisable. The resolver never mutates a state it was given as a preview input.

enum Phase { START_TURN, PLAYER_PHASE, RESOLVE, END_COMBAT }
enum Outcome { NONE, VICTORY, DEFEAT }

var turn: int = 0
var phase: int = Phase.START_TURN
var outcome: int = Outcome.NONE
var player: CombatantState = null
## Enemies in spawn order, satellites included (after their host).
var enemies: Array[CombatantState] = []
var draw_pile: Array[StringName] = []
var hand: Array[StringName] = []
var discard_pile: Array[StringName] = []
var exhaust_pile: Array[StringName] = []
var ram: int = 0
## Free nudges left this turn.
var free_nudges: int = 0
## Enemy wheel the player's cards and pointer attacks aim at.
var target_id: StringName = &""
var consecutive_perfects: int = 0
## Key (content id + trigger) -> times fired, for limit_per_combat.
var per_combat_uses: Dictionary = {}
var spins_this_turn: int = 0
## Campaign input: MAJOR Heat thresholds crossed (CORRUPTED scales with it).
var heat_majors_crossed: int = 0
## Grows by one per satellite spawned, to keep ids unique.
var spawn_counter: int = 0
## The operative's Daemons (run-wide rules that hook combat triggers).
var daemon_ids: Array[StringName] = []
## Per-combat markers set by cards/Daemons (String -> int), e.g. "steady_hand".
var flags: Dictionary = {}
## Kernel Sync: +N to every player attack for the rest of the combat.
var damage_bonus: int = 0
## Ring Lock: spins on the operative's wheel leave the inner ring alone this turn.
var ring_locked: bool = false
## Steady Hand: RAM granted at the next start of turn.
var ram_bonus_next_turn: int = 0
## Cold Exit: whether the operative's Miss slice resolved in this combat.
var miss_resolved: bool = false


func get_combatant(id: StringName) -> CombatantState:
	if player != null and player.id == id:
		return player
	for e in enemies:
		if e.id == id:
			return e
	return null


## Living enemies; satellites only when `include_satellites`.
func living_enemies(include_satellites: bool = true) -> Array[CombatantState]:
	var out: Array[CombatantState] = []
	for e in enemies:
		if e.is_alive() and (include_satellites or not e.is_satellite):
			out.append(e)
	return out


## Living satellites docked on `host_id`, in spawn order.
func satellites_of(host_id: StringName) -> Array[CombatantState]:
	var out: Array[CombatantState] = []
	for e in enemies:
		if e.is_alive() and e.is_satellite and e.host_id == host_id:
			out.append(e)
	return out


## The living satellite guarding `slot` of `host_id`, or null.
func satellite_at(host_id: StringName, slot: int) -> CombatantState:
	for s in satellites_of(host_id):
		if s.dock_slot == slot:
			return s
	return null


## Every living combatant in resolution order: player, then each enemy followed by
## its satellites.
func combatants_in_order() -> Array[CombatantState]:
	var out: Array[CombatantState] = []
	if player != null and player.is_alive():
		out.append(player)
	for e in enemies:
		if e.is_alive() and not e.is_satellite:
			out.append(e)
			out.append_array(satellites_of(e.id))
	return out


func is_over() -> bool:
	return outcome != Outcome.NONE


func duplicate_state() -> CombatState:
	var s := CombatState.new()
	s.turn = turn
	s.phase = phase
	s.outcome = outcome
	s.player = player.duplicate_state() if player != null else null
	for e in enemies:
		s.enemies.append(e.duplicate_state())
	s.draw_pile = draw_pile.duplicate()
	s.hand = hand.duplicate()
	s.discard_pile = discard_pile.duplicate()
	s.exhaust_pile = exhaust_pile.duplicate()
	s.ram = ram
	s.free_nudges = free_nudges
	s.target_id = target_id
	s.consecutive_perfects = consecutive_perfects
	s.per_combat_uses = per_combat_uses.duplicate()
	s.spins_this_turn = spins_this_turn
	s.heat_majors_crossed = heat_majors_crossed
	s.spawn_counter = spawn_counter
	s.daemon_ids = daemon_ids.duplicate()
	s.flags = flags.duplicate()
	s.damage_bonus = damage_bonus
	s.ring_locked = ring_locked
	s.ram_bonus_next_turn = ram_bonus_next_turn
	s.miss_resolved = miss_resolved
	return s


func to_dict() -> Dictionary:
	var enemy_dicts := []
	for e in enemies:
		enemy_dicts.append(e.to_dict())
	return {
		"turn": turn,
		"phase": phase,
		"outcome": outcome,
		"player": player.to_dict() if player != null else {},
		"enemies": enemy_dicts,
		"draw_pile": _names(draw_pile),
		"hand": _names(hand),
		"discard_pile": _names(discard_pile),
		"exhaust_pile": _names(exhaust_pile),
		"ram": ram,
		"free_nudges": free_nudges,
		"target_id": String(target_id),
		"consecutive_perfects": consecutive_perfects,
		"per_combat_uses": per_combat_uses.duplicate(),
		"spins_this_turn": spins_this_turn,
		"heat_majors_crossed": heat_majors_crossed,
		"spawn_counter": spawn_counter,
		"daemon_ids": _names(daemon_ids),
		"flags": flags.duplicate(),
		"damage_bonus": damage_bonus,
		"ring_locked": ring_locked,
		"ram_bonus_next_turn": ram_bonus_next_turn,
		"miss_resolved": miss_resolved,
	}


static func from_dict(d: Dictionary) -> CombatState:
	var s := CombatState.new()
	s.turn = int(d.get("turn", 0))
	s.phase = int(d.get("phase", Phase.START_TURN))
	s.outcome = int(d.get("outcome", Outcome.NONE))
	var pd: Dictionary = d.get("player", {})
	s.player = CombatantState.from_dict(pd) if not pd.is_empty() else null
	for ed in d.get("enemies", []):
		s.enemies.append(CombatantState.from_dict(ed))
	s.draw_pile = _to_names(d.get("draw_pile", []))
	s.hand = _to_names(d.get("hand", []))
	s.discard_pile = _to_names(d.get("discard_pile", []))
	s.exhaust_pile = _to_names(d.get("exhaust_pile", []))
	s.ram = int(d.get("ram", 0))
	s.free_nudges = int(d.get("free_nudges", 0))
	s.target_id = StringName(String(d.get("target_id", "")))
	s.consecutive_perfects = int(d.get("consecutive_perfects", 0))
	for k in d.get("per_combat_uses", {}):
		s.per_combat_uses[String(k)] = int(d["per_combat_uses"][k])
	s.spins_this_turn = int(d.get("spins_this_turn", 0))
	s.heat_majors_crossed = int(d.get("heat_majors_crossed", 0))
	s.spawn_counter = int(d.get("spawn_counter", 0))
	s.daemon_ids = _to_names(d.get("daemon_ids", []))
	for k in d.get("flags", {}):
		s.flags[String(k)] = int(d["flags"][k])
	s.damage_bonus = int(d.get("damage_bonus", 0))
	s.ring_locked = bool(d.get("ring_locked", false))
	s.ram_bonus_next_turn = int(d.get("ram_bonus_next_turn", 0))
	s.miss_resolved = bool(d.get("miss_resolved", false))
	return s


## Deterministic hash of the whole state (replay and preview tests).
func state_hash() -> int:
	return hash(JSON.stringify(to_dict()))


static func _names(names: Array[StringName]) -> Array:
	var out := []
	for n in names:
		out.append(String(n))
	return out


static func _to_names(strings: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for s in strings:
		out.append(StringName(String(s)))
	return out
