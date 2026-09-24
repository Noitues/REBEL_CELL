class_name CombatResolver
extends RefCounted
## The combat rules (GDD 2, TECH_SPEC 5.3-5.5). Pure: apply() duplicates the state it
## is given and returns a new one plus events. Randomness only through the RNG passed
## in. Content is read through a ContentLookup and never modified.

var config: CampaignConfigData
var lookup: ContentLookup
var fx: EffectInterpreter

const DEFENSIVE_TYPES := [RC.SliceType.DEFEND, RC.SliceType.SHIELD, RC.SliceType.EVADE, RC.SliceType.HEAL]
const OFFENSIVE_TYPES := [RC.SliceType.ATTACK, RC.SliceType.CRIT, RC.SliceType.DEPLOY]
const STATUS_TYPES := [RC.SliceType.AFFLICT]


func _init(p_config: CampaignConfigData, p_lookup: ContentLookup) -> void:
	config = p_config
	lookup = p_lookup
	fx = EffectInterpreter.new(p_config, p_lookup)


# --- Setup -----------------------------------------------------------------------

## Builds turn-0 state for an operative of `class_data` (with an optional installed
## Inner Ring) against `enemy_datas`. Satellites with ON_COMBAT_START spawns dock now.
## `overrides` (all optional, from the operative's run state): "slot_slice_ids",
## "slot_firmware_ids", "deck" (Array of ids as Strings or StringNames), "daemon_ids",
## "hp", "max_hp", "enemy_scale" (GDD 11.6 tier multiplier for enemy HP and outputs).
## Call begin_combat() next to run the first START_TURN.
func create_combat(class_data: ClassData, enemy_datas: Array[EnemyData], rng: RandomNumberGenerator, ring: InnerRingData = null, heat_majors_crossed: int = 0, overrides: Dictionary = {}) -> CombatState:
	var s := CombatState.new()
	s.heat_majors_crossed = heat_majors_crossed
	var p := CombatantState.new()
	p.id = &"player"
	p.source_id = class_data.id
	p.display_name = class_data.display_name if class_data.display_name != "" else String(class_data.id)
	p.is_player = true
	p.max_hp = int(overrides.get("max_hp", class_data.base_hp))
	p.hp = int(overrides.get("hp", p.max_hp))
	p.wheel = WheelState.from_wheel_data(class_data.starting_wheel, ring,
		_to_names(overrides.get("slot_slice_ids", [])), _to_names(overrides.get("slot_firmware_ids", [])))
	p.hub_resistance = class_data.starting_wheel.hub.hub_resistance if class_data.starting_wheel.hub != null else 0
	s.player = p
	s.ram = class_data.starting_ram
	if overrides.has("deck"):
		s.draw_pile = _to_names(overrides["deck"])
	else:
		for card in class_data.starting_deck:
			if card != null:
				s.draw_pile.append(card.id)
	s.daemon_ids = _to_names(overrides.get("daemon_ids", []))
	var enemy_scale := float(overrides.get("enemy_scale", 1.0))
	s.flags["boss_pointer_removal"] = int(overrides.get("remove_boss_pointers", 0))
	for i in enemy_datas.size():
		var e := _make_combatant(enemy_datas[i], StringName("enemy_%d" % i), false)
		_scale_enemy(e, enemy_scale)
		if enemy_datas[i].is_boss:
			_trim_pointers(e, int(s.flags["boss_pointer_removal"]))
			for k in int(overrides.get("boss_corrupt_slices", 0)):
				var slot := fx.pick_slot(s, e, RC.SlicePick.RANDOM_NON_MISS, {}, rng)
				if slot >= 0:
					e.wheel.slice_statuses[slot] = RC.Status.CORRUPTED
		s.enemies.append(e)
		for spawn in enemy_datas[i].spawns:
			if spawn == null or spawn.satellite == null or spawn.trigger != RC.Trigger.ON_COMBAT_START:
				continue
			for k in spawn.max_active:
				_scale_enemy(_spawn_satellite(s, e, spawn, rng), enemy_scale)
	if not s.enemies.is_empty():
		s.target_id = s.enemies[0].id
	return s


## Breach Exploit: the boss keeps `removal` fewer pointers (never below one).
static func _trim_pointers(e: CombatantState, removal: int) -> void:
	if removal <= 0:
		return
	var keep := maxi(1, e.wheel.pointer_ticks.size() - removal)
	e.wheel.pointer_ticks = e.wheel.pointer_ticks.slice(0, keep)


static func _scale_enemy(e: CombatantState, scale: float) -> void:
	if is_equal_approx(scale, 1.0):
		return
	e.max_hp = roundi(e.max_hp * scale)
	e.hp = e.max_hp
	e.output_scale = scale


static func _to_names(values: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for v in values:
		out.append(StringName(String(v)))
	return out


## Runs the first START_TURN (respins, shuffle, draw). Returns a new state.
func begin_combat(state: CombatState, rng: RandomNumberGenerator) -> CombatResult:
	var result := CombatResult.new()
	var s := state.duplicate_state()
	EffectInterpreter.shuffle(s.draw_pile, rng)
	result.events.append({"type": "combat_start", "text": "Combat begins."})
	start_turn(s, rng, result.events)
	result.state = s
	return result


# --- Actions ---------------------------------------------------------------------

## Empty string when `action` is legal in `state`; otherwise the reason it is not.
func validate_action(state: CombatState, action: CombatAction) -> String:
	if state.is_over():
		return "Combat is over."
	if state.phase != CombatState.Phase.PLAYER_PHASE:
		return "Not in the player phase."
	match action.type:
		CombatAction.Type.TARGET:
			var t := state.get_combatant(action.wheel_id)
			if t == null or not t.is_alive() or t.is_player:
				return "Invalid target."
		CombatAction.Type.NUDGE:
			var t := state.get_combatant(action.wheel_id)
			if t == null or not t.is_alive():
				return "Invalid wheel."
			if action.ring == RC.RingScope.INNER and not t.wheel.has_inner_ring():
				return "That wheel has no inner ring."
			if state.free_nudges <= 0 and state.ram < config.extra_nudge_ram_cost:
				return "Not enough RAM for an extra nudge."
		CombatAction.Type.PLAY_CARD:
			if action.hand_index < 0 or action.hand_index >= state.hand.size():
				return "No such card in hand."
			var card := lookup.get_content(state.hand[action.hand_index]) as CardData
			if card == null:
				return "Unknown card."
			if state.ram < card.ram_cost:
				return "Not enough RAM (%d needed)." % card.ram_cost
			var target := card_target(state, card, action)
			if target == null or not target.is_alive():
				return "Card has no valid target wheel."
			if card.wheel_target == RC.WheelTarget.SATELLITE and not target.is_satellite:
				return "Card must target a satellite."
			for e in card.effects:
				if e == null:
					continue
				if (e.type == RC.EffectType.FLIP or e.type == RC.EffectType.RESPIN) and target != state.player and target.resistance > 0:
					return "%s blocked: %s has %d resistance." % [RC.EffectType.keys()[e.type], target.display_name, target.resistance]
				if e.type == RC.EffectType.NUDGE and e.ring_scope == RC.RingScope.INNER and not target.wheel.has_inner_ring():
					return "Target has no inner ring."
				if e.slice_pick == RC.SlicePick.CHOSEN and (e.type == RC.EffectType.APPLY_STATUS or e.type == RC.EffectType.CLEANSE) and action.slot_index < 0:
					return "Choose a slice."
	return ""


## Applies `action` to a copy of `state`. Consumes RNG only when the rules do (respins,
## random targets, reshuffles), which is what makes checkpoints.
func apply(state: CombatState, action: CombatAction, rng: RandomNumberGenerator) -> CombatResult:
	var result := CombatResult.new()
	result.error = validate_action(state, action)
	if not result.ok():
		result.state = state
		return result
	var s := state.duplicate_state()
	result.state = s
	match action.type:
		CombatAction.Type.TARGET:
			s.target_id = action.wheel_id
			result.events.append({"type": "target", "target": action.wheel_id, "text": "Targeting %s." % s.get_combatant(action.wheel_id).display_name})
		CombatAction.Type.NUDGE:
			_apply_nudge(s, action, rng, result.events)
		CombatAction.Type.PLAY_CARD:
			_apply_card(s, action, rng, result.events)
		CombatAction.Type.END_TURN:
			resolve_turn(s, rng, result.events)
			result.resolved_state = s.duplicate_state()
			if not s.is_over():
				start_turn(s, rng, result.events)
	return result


## Same as apply() on a copy of the RNG: the state and RNG passed in stay untouched.
## Preview must equal the real result (tested).
func preview(state: CombatState, action: CombatAction, rng: RandomNumberGenerator) -> CombatResult:
	return apply(state, action, clone_rng(rng))


## The End Turn preview: RESOLVE only, on copies. Equals apply(END_TURN).resolved_state.
func preview_end_turn(state: CombatState, rng: RandomNumberGenerator) -> CombatResult:
	var result := CombatResult.new()
	var s := state.duplicate_state()
	resolve_turn(s, clone_rng(rng), result.events)
	result.state = s
	result.resolved_state = s
	return result


static func clone_rng(rng: RandomNumberGenerator) -> RandomNumberGenerator:
	var copy := RandomNumberGenerator.new()
	copy.seed = rng.seed
	copy.state = rng.state
	return copy


## Wheel a card aims at under `action` (null when none qualifies).
func card_target(state: CombatState, card: CardData, action: CombatAction) -> CombatantState:
	match card.wheel_target:
		RC.WheelTarget.OWN:
			return state.player
		RC.WheelTarget.ENEMY, RC.WheelTarget.SATELLITE:
			if action.wheel_id != &"" and action.wheel_id != state.player.id:
				return state.get_combatant(action.wheel_id)
			return state.get_combatant(state.target_id)
		_:
			if action.wheel_id != &"":
				return state.get_combatant(action.wheel_id)
			return state.get_combatant(state.target_id)


# --- Turn machine ----------------------------------------------------------------

## START_TURN: respin non-frozen wheels, expire block, restore resistance, tick hub
## breaches, RAM regen, refresh free nudge, draw to hand size (GDD 2.2 step 1).
func start_turn(s: CombatState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	s.turn += 1
	s.phase = CombatState.Phase.START_TURN
	events.append({"type": "turn_start", "turn": s.turn, "text": "--- Turn %d ---" % s.turn})
	var cls := fx.class_of(s)
	s.ring_locked = false
	s.flags.erase("steady_hand")
	for c in s.combatants_in_order():
		if c.wheel.frozen:
			c.wheel.frozen = false
			events.append({"type": "frozen_skip", "target": c.id, "text": "%s is frozen and skips its respin." % c.display_name})
		else:
			fx.respin(c, rng, events, true)
		if c.wheel.pointer_orbit != 0 and s.turn > 1:
			c.wheel.orbit_pointers()
			events.append({"type": "orbit", "target": c.id, "text": "%s's pointer orbits to tick %d." % [c.display_name, c.wheel.pointer_ticks[0]]})
		c.block = 0
		c.evade_charges = 0
		# Hub start-of-turn passives (Auto-Renew) run while the breach still holds, so a
		# Hub Breach played last turn stops this turn's heal; then the breach expires.
		if not c.is_player:
			_run_hub_turn_start(s, c, rng, events)
		if c.hub_breached_turns > 0:
			c.hub_breached_turns -= 1
			if c.hub_breached_turns == 0:
				events.append({"type": "hub_restored", "target": c.id, "text": "%s Hub is back online." % c.display_name})
		if not c.is_player:
			c.resistance = c.full_resistance()
	if s.turn > 1:
		s.ram = mini(s.ram + cls.ram_regen, cls.max_ram)
		events.append({"type": "ram", "amount": cls.ram_regen, "text": "RAM +%d (%d/%d)." % [cls.ram_regen, s.ram, cls.max_ram]})
	if s.ram_bonus_next_turn > 0:
		fx.gain_ram(s, s.ram_bonus_next_turn, events)
		s.ram_bonus_next_turn = 0
	s.free_nudges = cls.free_nudges_per_turn
	s.spins_this_turn = 0
	_retarget_if_needed(s)
	fx.draw_cards(s, maxi(0, config.hand_size - s.hand.size()), rng, events)
	var ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0, "source_id": &"turn"}
	fx.run_triggers(s, RC.Trigger.ON_TURN_START, ctx, _player_listeners(s), rng, events)
	s.phase = CombatState.Phase.PLAYER_PHASE


## RESOLVE: every pointer of every wheel, defensive -> offensive -> statuses, both
## sides at once (GDD 2.2 step 3). Ends with deaths, outcome and the discard.
func resolve_turn(s: CombatState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	s.phase = CombatState.Phase.RESOLVE
	events.append({"type": "resolve_start", "text": "End turn: resolving."})
	var resolutions := _collect_resolutions(s)
	# Consecutive Perfects are counted on the player's first pointer, before hooks run.
	for r in resolutions:
		if r["owner"] == s.player and r["pointer_index"] == 0 and not r.get("derived", false):
			s.consecutive_perfects = s.consecutive_perfects + 1 if r["tier"] == RC.PrecisionTier.PERFECT else 0
			if r["tier"] == RC.PrecisionTier.PERFECT and int(s.flags.get("steady_hand", 0)) > 0:
				s.ram_bonus_next_turn += 2 * int(s.flags["steady_hand"])
				events.append({"type": "steady_hand", "amount": s.ram_bonus_next_turn, "text": "Steady Hand: Perfect at end of turn, +%d RAM next turn." % s.ram_bonus_next_turn})
			if r["slice"].slice_type == RC.SliceType.MISS:
				s.miss_resolved = true
	for r in resolutions:
		events.append({"type": "pointer", "owner": r["owner"].id, "pointer_index": r["pointer_index"], "tick": r["tick"],
			"slice_index": r["slice_index"], "offset": r["offset"], "tier": r["tier"], "segment_index": r["segment_index"],
			"text": "%s pointer %d: tick %d -> %s (offset %+d, %s%s)." % [r["owner"].display_name, r["pointer_index"], r["tick"],
				r["slice"].display_name if r["slice"].display_name != "" else String(r["slice"].id), r["offset"],
				RC.PrecisionTier.keys()[r["tier"]] if r["owner"].wheel.slice_count == RC.SLICES else "full output",
				(", ring " + r["segment"].display_name) if r["segment"] != null else ""]})
	events.append({"type": "pass", "pass": "defensive", "text": "[defensive pass]"})
	for r in resolutions:
		if r["slice"].slice_type in DEFENSIVE_TYPES:
			_resolve_pointer(s, r, rng, events)
	events.append({"type": "pass", "pass": "offensive", "text": "[offensive pass]"})
	for r in resolutions:
		if r["slice"].slice_type in OFFENSIVE_TYPES:
			_resolve_pointer(s, r, rng, events)
	events.append({"type": "pass", "pass": "statuses", "text": "[status pass]"})
	for r in resolutions:
		if r["slice"].slice_type in STATUS_TYPES or r["slice"].slice_type == RC.SliceType.MISS:
			_resolve_pointer(s, r, rng, events)
	for r in resolutions:
		if r["status"] == RC.Status.CORRUPTED and not r.get("derived", false):
			_corrupted_trigger(s, r, events)
	var end_ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0, "source_id": &"turn"}
	fx.run_triggers(s, RC.Trigger.ON_TURN_END, end_ctx, _player_listeners(s), rng, events)
	var alive_before: Array[StringName] = []
	for r in resolutions:
		if not alive_before.has(r["owner"].id):
			alive_before.append(r["owner"].id)
	_apply_deaths(s, alive_before, events)
	_check_boss_phases(s, rng, events)
	_check_outcome(s, events)
	s.discard_pile.append_array(s.hand)
	s.hand.clear()
	_retarget_if_needed(s)


# --- Readouts (HUD / preview) ----------------------------------------------------

## What sits under each pointer of `c` right now: tick, slice, offset, tier, ring
## segment and the satellite that would guard that pointer.
func pointer_readouts(s: CombatState, c: CombatantState) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for i in c.wheel.pointer_ticks.size():
		out.append(_readout(s, c, i))
	return out


func _readout(s: CombatState, c: CombatantState, pointer_index: int) -> Dictionary:
	var wheel := c.wheel
	var tick := wheel.tick_at(pointer_index)
	var slice_index := WheelMath.slice_at(tick, wheel.slice_count)
	var offset := WheelMath.offset_at(tick, wheel.slice_count)
	var tier: int = WheelMath.tier(offset) if wheel.slice_count == RC.SLICES else RC.PrecisionTier.PERFECT
	var segment_index := -1
	var segment: RingSegmentData = null
	if wheel.has_inner_ring():
		segment_index = WheelMath.ring_segment(wheel.inner_tick_at(pointer_index))
		segment = fx.segment_of(wheel, segment_index)
	var guard := s.satellite_at(c.id, slice_index)
	var status: int = wheel.slice_statuses[slice_index]
	var permanent := fx.permanent_status(wheel, slice_index)
	return {
		"owner": c, "pointer_index": pointer_index, "tick": tick, "slice_index": slice_index,
		"slice": fx.slice_of(wheel, slice_index), "firmware": fx.firmware_of(wheel, slice_index),
		"offset": offset, "tier": tier, "segment_index": segment_index, "segment": segment,
		"guard_id": guard.id if guard != null else &"",
		"status": status, "permanent_status": permanent,
	}


# --- Internals: actions ----------------------------------------------------------

func _apply_nudge(s: CombatState, action: CombatAction, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	if s.free_nudges > 0:
		s.free_nudges -= 1
	else:
		s.ram -= config.extra_nudge_ram_cost
		events.append({"type": "ram", "amount": -config.extra_nudge_ram_cost, "text": "Extra nudge costs %d RAM (%d)." % [config.extra_nudge_ram_cost, s.ram]})
	var target := s.get_combatant(action.wheel_id)
	fx.nudge(s, s.player, target, action.ring, action.direction, false, events)
	var ctx := {"owner": s.player, "target": target, "action": action}
	fx.run_triggers(s, RC.Trigger.ON_NUDGE, ctx, _player_listeners(s), rng, events)


func _apply_card(s: CombatState, action: CombatAction, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var card_id := s.hand[action.hand_index]
	var card := lookup.get_content(card_id) as CardData
	var target := card_target(s, card, action)
	s.hand.remove_at(action.hand_index)
	s.ram -= card.ram_cost
	events.append({"type": "card", "card_id": card_id, "target": target.id, "cost": card.ram_cost,
		"text": "Play %s on %s (RAM -%d, %d left)." % [card.display_name if card.display_name != "" else String(card_id), target.display_name, card.ram_cost, s.ram]})
	var ctx := {"owner": s.player, "target": target, "action": action, "source_id": card_id,
		"spin_bonus": fx.spin_bonus_of(s.player), "pointer_index": 0}
	for e in card.effects:
		if e != null:
			fx.apply_effect(s, e, ctx, rng, events)
	fx.run_triggers(s, RC.Trigger.ON_CARD_PLAYED, ctx, _player_listeners(s), rng, events)
	if card.exhaust:
		s.exhaust_pile.append(card_id)
	else:
		s.discard_pile.append(card_id)


# --- Internals: resolution -------------------------------------------------------

## Every pointer's readout plus the extra resolutions Firmware neighbour rules add
## (GDD 6.1). Mirror: copy the neighbour on the side you landed (both on Perfect).
## Shunt: resolve that neighbour instead at neighbor_multiplier; nothing special on
## Perfect. Derived entries keep the landing's tier and carry "derived": true.
func _collect_resolutions(s: CombatState) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for c in s.combatants_in_order():
		for i in c.wheel.pointer_ticks.size():
			var r := _readout(s, c, i)
			var fw: FirmwareData = r["firmware"]
			if fw == null or fw.neighbor_rule == RC.NeighborRule.NONE:
				out.append(r)
				continue
			var offset: int = r["offset"]
			var sides: Array[int] = []
			if offset != 0:
				sides.append(signi(offset))
			elif fw.neighbor_rule == RC.NeighborRule.MIRROR:
				sides = [1, -1]
			if fw.neighbor_rule == RC.NeighborRule.MIRROR or sides.is_empty():
				out.append(r)
			for side in sides:
				out.append(_neighbor_resolution(s, r, side, fw.neighbor_multiplier))
	return out


func _neighbor_resolution(s: CombatState, r: Dictionary, side: int, multiplier: float) -> Dictionary:
	var c: CombatantState = r["owner"]
	var slot := posmod(int(r["slice_index"]) + side, c.wheel.slice_count)
	var d := r.duplicate()
	d["slice_index"] = slot
	d["slice"] = fx.slice_of(c.wheel, slot)
	d["firmware"] = null
	d["status"] = c.wheel.slice_statuses[slot]
	d["permanent_status"] = fx.permanent_status(c.wheel, slot)
	d["derived"] = true
	d["extra_multiplier"] = multiplier
	return d


## Listeners for the slice at `r`, in TECH_SPEC order: slice, Firmware, ring segment,
## Hub, Daemons.
func _slice_listeners(s: CombatState, r: Dictionary) -> Array:
	var owner: CombatantState = r["owner"]
	var slice: SliceData = r["slice"]
	var out := [{"source_id": slice.id, "effects": slice.extra_effects}]
	var fw: FirmwareData = r["firmware"]
	if fw != null:
		out.append({"source_id": fw.id, "effects": fw.triggered_effects})
	var seg: RingSegmentData = r["segment"]
	if seg != null:
		out.append({"source_id": seg.id, "effects": seg.triggered_effects})
	var hub := fx.hub_of(owner.wheel)
	if hub != null and not owner.is_hub_breached():
		var hub_effects: Array[TriggeredEffectData] = hub.passive_effects.duplicate()
		if owner.is_player and hub.perfect_hook != null:
			hub_effects.append(hub.perfect_hook)
		out.append({"source_id": hub.id, "effects": hub_effects})
	if owner.is_player:
		out.append_array(_daemon_listeners(s))
	return out


func _player_listeners(s: CombatState) -> Array:
	var out := []
	var hub := fx.hub_of(s.player.wheel)
	if hub != null and not s.player.is_hub_breached():
		out.append({"source_id": hub.id, "effects": hub.passive_effects})
	out.append_array(_daemon_listeners(s))
	return out


## The operative's Daemons as listeners, in id order (deterministic).
func _daemon_listeners(s: CombatState) -> Array:
	var out := []
	for id in s.daemon_ids:
		var d := lookup.get_content(id) as DaemonData
		if d != null:
			out.append({"source_id": d.id, "effects": d.triggered_effects, "handler": d.custom_handler})
	return out


## Resolves one pointer: computes multipliers and extra resolutions, runs the base
## slice action per instance, then the slice's own listeners.
func _resolve_pointer(s: CombatState, r: Dictionary, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	# No liveness check: resolution is simultaneous, so a combatant that dropped to 0 HP
	# earlier in this resolve still fires everything it landed on. Deaths apply at the end.
	var owner: CombatantState = r["owner"]
	var slice: SliceData = r["slice"]
	var wheel := owner.wheel
	var slot: int = r["slice_index"]
	var ctx := {"owner": owner, "target": _pointer_target(s, owner), "pointer_index": r["pointer_index"],
		"tier": r["tier"], "slice_index": slot, "source_id": slice.id}
	var listeners := _slice_listeners(s, r)
	var mult: float = owner.output_scale * float(r.get("extra_multiplier", 1.0))
	if r["tier"] == RC.PrecisionTier.PARTIAL:
		mult *= config.partial_multiplier
	var fw: FirmwareData = r["firmware"]
	if fw != null:
		mult *= fw.output_multiplier
	var overclocked: bool = r["status"] == RC.Status.OVERCLOCKED or r["permanent_status"] == RC.Status.OVERCLOCKED
	if overclocked:
		mult *= config.overclock_multiplier
	var pierce := false
	var seg: RingSegmentData = r["segment"]
	if seg != null:
		mult *= seg.output_multiplier
		pierce = seg.pierce
	var instances: Array[float] = [mult]
	for extra in fx.retrigger_multipliers(s, RC.Trigger.ON_SLICE_TRIGGER, ctx, listeners):
		instances.append(mult * extra)
	if r["tier"] == RC.PrecisionTier.PERFECT:
		for extra in fx.retrigger_multipliers(s, RC.Trigger.ON_PERFECT, ctx, listeners):
			instances.append(mult * extra)
	if instances.size() > 1:
		events.append({"type": "retrigger", "owner": owner.id, "count": instances.size(),
			"text": "%s's %s resolves %d times." % [owner.display_name, _slice_name(slice), instances.size()]})
	for m in instances:
		var output := roundi(slice.base_output * m)
		if owner.is_player and slice.slice_type in [RC.SliceType.ATTACK, RC.SliceType.CRIT] and s.damage_bonus > 0:
			output += s.damage_bonus
		_slice_action(s, owner, slice, output, pierce, ctx, events)
		fx.run_triggers(s, RC.Trigger.ON_SLICE_TRIGGER, ctx, listeners, rng, events)
		if r["tier"] == RC.PrecisionTier.PERFECT:
			fx.run_triggers(s, RC.Trigger.ON_PERFECT, ctx, listeners, rng, events)
		if slice.slice_type == RC.SliceType.MISS:
			fx.run_triggers(s, RC.Trigger.ON_MISS_SLICE, ctx, listeners, rng, events)
	if r["status"] == RC.Status.OVERCLOCKED and not r.get("derived", false):
		wheel.slice_statuses[slot] = RC.Status.CORRUPTED
		events.append({"type": "status", "target": owner.id, "slot": slot, "status": RC.Status.CORRUPTED,
			"text": "%s slot %d burns out: OVERCLOCKED -> CORRUPTED." % [owner.display_name, slot]})


func _slice_action(s: CombatState, owner: CombatantState, slice: SliceData, output: int, pierce: bool, ctx: Dictionary, events: Array[Dictionary]) -> void:
	match slice.slice_type:
		RC.SliceType.ATTACK, RC.SliceType.CRIT:
			var target: CombatantState = ctx["target"]
			if target == null or not target.is_alive():
				return
			events.append({"type": "attack", "attacker": owner.id, "target": target.id, "amount": output, "pierce": pierce,
				"text": "%s %s for %d at %s." % [owner.display_name, _slice_name(slice), output, target.display_name]})
			for q in target.wheel.pointer_ticks.size():
				# Bodyguard applies even to Pierce (designer ruling: Pierce ignores block
				# and shield only).
				var victim := target
				var guard := s.satellite_at(target.id, target.wheel.slice_at(q))
				if guard != null:
					victim = guard
					events.append({"type": "bodyguard", "target": target.id, "guard": guard.id, "pointer_index": q,
						"text": "%s takes the hit for %s (pointer %d)." % [guard.display_name, target.display_name, q]})
				fx.deal_hit(s, owner, victim, output, pierce, true, events, slice.id)
		RC.SliceType.DEFEND:
			fx.gain_block(owner, output, events)
		RC.SliceType.SHIELD:
			fx.gain_shield(owner, output, events)
		RC.SliceType.EVADE:
			fx.gain_evade(owner, maxi(1, output), events)
		RC.SliceType.HEAL:
			fx.heal(owner, output, events)
		RC.SliceType.AFFLICT:
			events.append({"type": "afflict", "attacker": owner.id, "text": "%s %s." % [owner.display_name, _slice_name(slice)]})
		RC.SliceType.MISS:
			events.append({"type": "miss", "owner": owner.id, "text": "%s lands on MISS." % owner.display_name})
		_:
			events.append({"type": "unsupported_slice", "slice_type": slice.slice_type,
				"text": "%s slice type %s is not implemented yet." % [owner.display_name, RC.SliceType.keys()[slice.slice_type]]})


## Who `owner`'s pointer attacks: the player's chosen target, or the player.
func _pointer_target(s: CombatState, owner: CombatantState) -> CombatantState:
	if owner.is_player:
		var t := s.get_combatant(s.target_id)
		return t if t != null and t.is_alive() else null
	return s.player


func _corrupted_trigger(s: CombatState, r: Dictionary, events: Array[Dictionary]) -> void:
	var owner: CombatantState = r["owner"]
	if not owner.is_alive():
		return
	var damage := config.corrupted_self_damage + config.corrupted_damage_per_major * s.heat_majors_crossed
	var dealt := mini(owner.hp, damage)
	owner.hp -= dealt
	events.append({"type": "corrupted", "target": owner.id, "amount": dealt,
		"text": "%s's CORRUPTED slice bites: %d self-damage (%d HP)." % [owner.display_name, dealt, owner.hp]})
	if owner.is_player:
		fx.drain_ram(s, config.corrupted_ram_drain, events)


func _run_hub_turn_start(s: CombatState, c: CombatantState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var hub := fx.hub_of(c.wheel)
	if hub == null or c.is_hub_breached():
		return
	var ctx := {"owner": c, "target": s.player, "source_id": hub.id}
	fx.run_triggers(s, RC.Trigger.ON_TURN_START, ctx, [{"source_id": hub.id, "effects": hub.passive_effects}], rng, events)


## Reports every combatant in `alive_before` that is no longer alive; satellites go
## down with their host. Dead combatants stay in the list (filtered by is_alive()).
func _apply_deaths(s: CombatState, alive_before: Array[StringName], events: Array[Dictionary]) -> void:
	for e in s.enemies:
		if e.hp <= 0 and not e.is_satellite:
			for sat in s.satellites_of(e.id):
				sat.hp = 0
				events.append({"type": "died", "target": sat.id, "text": "%s goes down with its host." % sat.display_name})
	for id in alive_before:
		var c := s.get_combatant(id)
		if c != null and not c.is_alive() and not c.is_player:
			events.append({"type": "died", "target": c.id, "text": "%s is destroyed." % c.display_name})


## Boss pointer phases (GDD 2.11): entered when HP falls to the threshold. MULTIPLY /
## MIGRATE set the pointer layout (minus any Breach removal), ORBIT sets the per-turn
## drift, spawns dock satellites, a hub override swaps the Hub.
func _check_boss_phases(s: CombatState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	for e in s.enemies:
		if e.is_satellite or not e.is_alive():
			continue
		var data := lookup.get_content(e.source_id) as EnemyData
		if data == null or data.phases.is_empty():
			continue
		while e.phase_index < data.phases.size():
			var phase := data.phases[e.phase_index]
			if phase == null or float(e.hp) > e.max_hp * phase.hp_threshold_pct:
				break
			e.phase_index += 1
			match phase.pointer_behavior:
				RC.PointerBehavior.MULTIPLY, RC.PointerBehavior.MIGRATE:
					e.wheel.pointer_ticks = phase.pointer_ticks.duplicate()
					_trim_pointers(e, int(s.flags.get("boss_pointer_removal", 0)))
				RC.PointerBehavior.ORBIT:
					e.wheel.pointer_orbit = phase.orbit_ticks_per_turn
			if phase.hub_override != null:
				e.wheel.hub_id = phase.hub_override.id
				e.hub_resistance = phase.hub_override.hub_resistance
			for spawn in phase.spawns:
				if spawn != null and spawn.satellite != null:
					for k in spawn.max_active:
						_scale_enemy(_spawn_satellite(s, e, spawn, rng), e.output_scale)
			events.append({"type": "boss_phase", "target": e.id, "phase": e.phase_index, "behavior": phase.pointer_behavior,
				"text": "%s enters phase %d (%s)%s" % [e.display_name, e.phase_index, RC.PointerBehavior.keys()[phase.pointer_behavior],
					(": " + phase.phase_line) if phase.phase_line != "" else "."]})


func _check_outcome(s: CombatState, events: Array[Dictionary]) -> void:
	if s.player.hp <= 0:
		s.outcome = CombatState.Outcome.DEFEAT
		s.phase = CombatState.Phase.END_COMBAT
		events.append({"type": "combat_end", "outcome": s.outcome, "text": "DEFEAT: the operative is flatlined."})
	elif s.living_enemies(false).is_empty():
		s.outcome = CombatState.Outcome.VICTORY
		s.phase = CombatState.Phase.END_COMBAT
		events.append({"type": "combat_end", "outcome": s.outcome, "text": "VICTORY: all enemies destroyed."})


func _retarget_if_needed(s: CombatState) -> void:
	var t := s.get_combatant(s.target_id)
	if t != null and t.is_alive():
		return
	var living := s.living_enemies(false)
	s.target_id = living[0].id if not living.is_empty() else &""


func _make_combatant(data: EnemyData, id: StringName, is_satellite: bool) -> CombatantState:
	var c := CombatantState.new()
	c.id = id
	c.source_id = data.id
	c.display_name = data.display_name if data.display_name != "" else String(data.id)
	c.is_satellite = is_satellite
	c.max_hp = data.hp
	c.hp = data.hp
	c.wheel = WheelState.from_wheel_data(data.wheel)
	c.hub_resistance = data.wheel.hub.hub_resistance if data.wheel.hub != null else 0
	c.resistance = c.full_resistance()
	return c


func _spawn_satellite(s: CombatState, host: CombatantState, spawn: SatelliteSpawnData, rng: RandomNumberGenerator) -> CombatantState:
	var sat := _make_combatant(spawn.satellite, StringName("%s_sat_%d" % [host.id, s.spawn_counter]), true)
	s.spawn_counter += 1
	sat.host_id = host.id
	if spawn.dock_slot >= 0:
		sat.dock_slot = spawn.dock_slot
	else:
		var free: Array[int] = []
		for i in host.wheel.slot_slice_ids.size():
			if s.satellite_at(host.id, i) == null:
				free.append(i)
		sat.dock_slot = free[rng.randi_range(0, free.size() - 1)] if not free.is_empty() else 0
	s.enemies.append(sat)
	return sat


static func _slice_name(slice: SliceData) -> String:
	return slice.display_name if slice.display_name != "" else String(slice.id)
