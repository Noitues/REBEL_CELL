class_name CombatantState
extends RefCounted
## Runtime state of one combatant: the operative, an enemy, or a docked satellite
## (TECH_SPEC 5.2). Content is referenced by id.

## Unique within one combat (e.g. &"player", &"enemy_0", &"enemy_0_sat_0").
var id: StringName = &""
## ClassData id for the player, EnemyData id otherwise.
var source_id: StringName = &""
var display_name: String = ""
var is_player: bool = false
var is_satellite: bool = false
## Satellites: the combatant they dock on and the host slot they guard.
var host_id: StringName = &""
var dock_slot: int = -1
var hp: int = 1
var max_hp: int = 1
## Block expires at the start of the owner's next turn.
var block: int = 0
## Shield persists across turns, capped by config.shield_cap.
var shield: int = 0
## Pending EVADE cancels for incoming SHIM/OVERFLOW this turn.
var evade_charges: int = 0
var wheel: WheelState = null
## Spin resistance remaining this turn (passive + hub while the hub is up).
var resistance: int = 0
## Hub-sourced resistance at full strength (0 when the hub has none).
var hub_resistance: int = 0
## Resistance change made while the turn resolved; applied to the next restore, then cleared.
var resistance_carry: int = 0
## > 0 while the hub is breached; counts down at the owner's start of turn.
var hub_breached_turns: int = 0
## Tier scaling for enemy slice outputs (GDD 11.6); 1.0 for the operative.
var output_scale: float = 1.0
## Tier/boss HP multiplier applied to this enemy (satellites it launches inherit it).
var hp_scale: float = 1.0
## Bosses: how many BossPhaseData entries have been entered (GDD 2.11).
var phase_index: int = 0
## Plan 2 R3: the threshold of the next phase in basis points (RC.THRESHOLD_SCALE), 0 when
## there is none (normals, satellites, the last phase). Damage parks at hp_floor().
var next_threshold_bp: int = 0
## N4 (plan 2 R4): the enemy's enrage step this turn (0 = not enraged), its hit factor in
## percent (RC.PERCENT_MAX = unchanged) and the resistance it adds. Set by
## CombatResolver.refresh_enrage at the start of each turn from the turn counter.
var enrage_step: int = 0
var enrage_percent: int = RC.PERCENT_MAX
var enrage_resistance: int = 0


func is_alive() -> bool:
	return hp > 0


## The HP this combatant cannot drop below while its phase lasts (R3): ceil(max HP x the
## next threshold); 0 without a next phase.
func hp_floor() -> int:
	return BossPhaseData.floor_of(max_hp, next_threshold_bp)


func is_hub_breached() -> bool:
	return hub_breached_turns > 0


## Resistance this combatant restores to at the start of a player turn.
func full_resistance() -> int:
	var total := wheel.passive_resistance if wheel != null else 0
	if not is_hub_breached():
		total += hub_resistance
	return total + enrage_resistance


func duplicate_state() -> CombatantState:
	var c := CombatantState.new()
	c.id = id
	c.source_id = source_id
	c.display_name = display_name
	c.is_player = is_player
	c.is_satellite = is_satellite
	c.host_id = host_id
	c.dock_slot = dock_slot
	c.hp = hp
	c.max_hp = max_hp
	c.block = block
	c.shield = shield
	c.evade_charges = evade_charges
	c.wheel = wheel.duplicate_state() if wheel != null else null
	c.resistance = resistance
	c.resistance_carry = resistance_carry
	c.hub_resistance = hub_resistance
	c.hub_breached_turns = hub_breached_turns
	c.output_scale = output_scale
	c.hp_scale = hp_scale
	c.phase_index = phase_index
	c.next_threshold_bp = next_threshold_bp
	c.enrage_step = enrage_step
	c.enrage_percent = enrage_percent
	c.enrage_resistance = enrage_resistance
	return c


func to_dict() -> Dictionary:
	var d := _base_dict()
	# Only combatants with a next phase carry it, so fights without phases save (and hash)
	# exactly as before N3.
	if next_threshold_bp != 0:
		d["next_threshold_bp"] = next_threshold_bp
	# N4: likewise only an enraged combatant carries its enrage.
	if enrage_step != 0:
		d["enrage_step"] = enrage_step
		d["enrage_percent"] = enrage_percent
		d["enrage_resistance"] = enrage_resistance
	return d


func _base_dict() -> Dictionary:
	return {
		"id": String(id),
		"source_id": String(source_id),
		"display_name": display_name,
		"is_player": is_player,
		"is_satellite": is_satellite,
		"host_id": String(host_id),
		"dock_slot": dock_slot,
		"hp": hp,
		"max_hp": max_hp,
		"block": block,
		"shield": shield,
		"evade_charges": evade_charges,
		"wheel": wheel.to_dict() if wheel != null else {},
		"resistance": resistance, "resistance_carry": resistance_carry,
		"hub_resistance": hub_resistance,
		"hub_breached_turns": hub_breached_turns,
		"output_scale": output_scale,
		"hp_scale": hp_scale,
		"phase_index": phase_index,
	}


static func from_dict(d: Dictionary) -> CombatantState:
	var c := CombatantState.new()
	c.id = StringName(String(d.get("id", "")))
	c.source_id = StringName(String(d.get("source_id", "")))
	c.display_name = String(d.get("display_name", ""))
	c.is_player = bool(d.get("is_player", false))
	c.is_satellite = bool(d.get("is_satellite", false))
	c.host_id = StringName(String(d.get("host_id", "")))
	c.dock_slot = int(d.get("dock_slot", -1))
	c.hp = int(d.get("hp", 1))
	c.max_hp = int(d.get("max_hp", 1))
	c.block = int(d.get("block", 0))
	c.shield = int(d.get("shield", 0))
	c.evade_charges = int(d.get("evade_charges", 0))
	var wd: Dictionary = d.get("wheel", {})
	c.wheel = WheelState.from_dict(wd) if not wd.is_empty() else null
	c.resistance = int(d.get("resistance", 0))
	c.resistance_carry = int(d.get("resistance_carry", 0))
	c.hub_resistance = int(d.get("hub_resistance", 0))
	c.hub_breached_turns = int(d.get("hub_breached_turns", 0))
	c.output_scale = float(d.get("output_scale", 1.0))
	c.hp_scale = float(d.get("hp_scale", 1.0))
	c.phase_index = int(d.get("phase_index", 0))
	c.next_threshold_bp = int(d.get("next_threshold_bp", 0))
	c.enrage_step = int(d.get("enrage_step", 0))
	c.enrage_percent = int(d.get("enrage_percent", RC.PERCENT_MAX))
	c.enrage_resistance = int(d.get("enrage_resistance", 0))
	return c
