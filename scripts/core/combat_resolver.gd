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
## Where an extra boss pointer goes (ICE 18 BOSS_EXTRA_POINTER): offsets from pointer 0
## tried in order, the first free one wins (evenly spaced, GDD 2.1).
const EXTRA_POINTER_OFFSETS := [15, 10, 20, 5, 25]


func _init(p_config: CampaignConfigData, p_lookup: ContentLookup) -> void:
	config = p_config
	lookup = p_lookup
	fx = EffectInterpreter.new(p_config, p_lookup)


# --- Setup -----------------------------------------------------------------------

## Builds turn-0 state for an operative of `class_data` (with an optional installed
## Inner Ring) against `enemy_datas`. Satellites with ON_COMBAT_START spawns dock now.
## `overrides` (all optional, from the operative's run state and the campaign):
##   "slot_slice_ids", "slot_firmware_ids", "ring_segment_ids" (Rank 3 swaps), "deck"
##   (Array of ids as Strings or StringNames), "extra_cards" (ids added to the deck),
##   "daemon_ids", "hp", "max_hp", "max_ram", "hub_id",
##   "enemy_scale" (GDD 11.6 tier multiplier for enemy HP and outputs),
##   "heat" (campaign Heat, gates HeatGatedEffectData),
##   ICE / Heat rule modifiers (GDD 11.9): "enemy_resistance" (+N passive resistance on
##   every non-satellite enemy), "boss_strength_pct" (+N% HP and output on bosses and
##   mini-bosses), "boss_extra_pointer" (+N pointers on the final boss),
##   "no_first_turn_free_nudge" (bool),
##   "extra_free_nudges" (int, assist mode),
##   Exploit effects: "remove_boss_pointers", "boss_corrupt_slices", "reveal_phases".
## Call begin_combat() next to run the first START_TURN.
func create_combat(class_data: ClassData, enemy_datas: Array[EnemyData], rng: RandomNumberGenerator, ring: InnerRingData = null, heat_majors_crossed: int = 0, overrides: Dictionary = {}) -> CombatState:
	var s := CombatState.new()
	s.heat_majors_crossed = heat_majors_crossed
	s.campaign_heat = int(overrides.get("heat", 0))
	s.max_ram = int(overrides.get("max_ram", class_data.max_ram))
	var p := CombatantState.new()
	p.id = &"player"
	p.source_id = class_data.id
	p.display_name = class_data.display_name if class_data.display_name != "" else String(class_data.id)
	p.is_player = true
	p.max_hp = int(overrides.get("max_hp", class_data.base_hp))
	p.hp = int(overrides.get("hp", p.max_hp))
	p.wheel = WheelState.from_wheel_data(class_data.starting_wheel, ring,
		_to_names(overrides.get("slot_slice_ids", [])), _to_names(overrides.get("slot_firmware_ids", [])),
		_to_names(overrides.get("ring_segment_ids", [])))
	p.hub_resistance = class_data.starting_wheel.hub.hub_resistance if class_data.starting_wheel.hub != null else 0
	var hub_override := StringName(String(overrides.get("hub_id", "")))
	if hub_override != &"":
		var hub := lookup.get_content(hub_override) as HubCoreData
		if hub != null:
			p.wheel.hub_id = hub.id
			p.hub_resistance = hub.hub_resistance
	s.player = p
	var active_hub := lookup.get_content(p.wheel.hub_id) as HubCoreData if p.wheel.hub_id != &"" else null
	if active_hub != null:
		s.max_ram += active_hub.max_ram_bonus
	s.ram = class_data.starting_ram
	# Botnet drones carried over from earlier fights of the run (HubCoreData.drones_persist).
	for d in overrides.get("drones", []):
		var template := lookup.get_content(StringName(String(d.get("source_id", "")))) as EnemyData
		if template == null:
			continue
		var events: Array[Dictionary] = []
		var drone := fx.deploy_drone(s, p, template, int(d.get("dock_slot", 0)), events)
		if drone != null:
			drone.hp = clampi(int(d.get("hp", drone.max_hp)), 1, drone.max_hp)
	if overrides.has("deck"):
		s.draw_pile = _to_names(overrides["deck"])
	else:
		for card in class_data.starting_deck:
			if card != null:
				s.draw_pile.append(card.id)
	s.draw_pile.append_array(_to_names(overrides.get("extra_cards", [])))
	s.daemon_ids = _to_names(overrides.get("daemon_ids", []))
	var enemy_scale := float(overrides.get("enemy_scale", 1.0))
	var enemy_output_scale := float(overrides.get("enemy_output_scale", enemy_scale))
	var boss_scale := 1.0 + maxf(0.0, float(overrides.get("boss_strength_pct", 0.0))) / 100.0
	var extra_resistance := int(overrides.get("enemy_resistance", 0))
	s.flags["boss_pointer_removal"] = int(overrides.get("remove_boss_pointers", 0))
	if bool(overrides.get("reveal_phases", false)):
		s.flags["reveal_phases"] = 1
	if bool(overrides.get("no_first_turn_free_nudge", false)):
		s.flags["no_first_turn_free_nudge"] = 1
	s.flags["extra_free_nudges"] = int(overrides.get("extra_free_nudges", 0))
	# ICE extras that boss phases must keep (H14): the extra pointer and bonus resistance.
	s.flags["boss_extra_pointer"] = int(overrides.get("boss_extra_pointer", 0))
	s.flags["enemy_resistance"] = int(overrides.get("enemy_resistance", 0))
	for i in enemy_datas.size():
		var e := EffectInterpreter.make_combatant(enemy_datas[i], StringName("enemy_%d" % i), false)
		_scale_enemy(e, enemy_scale, enemy_output_scale)
		if enemy_datas[i].is_boss or enemy_datas[i].is_mini_boss:
			_scale_enemy(e, boss_scale)
		if extra_resistance > 0:
			e.wheel.passive_resistance += extra_resistance
			e.resistance = e.full_resistance()
		if enemy_datas[i].is_boss:
			_add_pointers(e, int(overrides.get("boss_extra_pointer", 0)))
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
				_scale_enemy(_spawn_satellite(s, e, spawn, rng), e.hp_scale, e.output_scale)
	if not s.enemies.is_empty():
		s.target_id = s.enemies[0].id
	return s


## Breach Exploit: the boss keeps `removal` fewer pointers (never below one).
static func _trim_pointers(e: CombatantState, removal: int) -> void:
	e.wheel.pointer_ticks = _trimmed(e.wheel.pointer_ticks, removal)


static func _trimmed(ticks: PackedInt32Array, removal: int) -> PackedInt32Array:
	if removal <= 0:
		return ticks.duplicate()
	return ticks.slice(0, maxi(1, ticks.size() - removal))


## ICE BOSS_EXTRA_POINTER: `count` more pointers, evenly spaced from pointer 0.
static func _add_pointers(e: CombatantState, count: int) -> void:
	e.wheel.pointer_ticks = _with_extra(e.wheel.pointer_ticks, count)


## `ticks` plus `count` more pointers, evenly spaced from pointer 0.
static func _with_extra(ticks: PackedInt32Array, count: int) -> PackedInt32Array:
	var out := ticks.duplicate()
	if out.is_empty():
		return out
	for i in count:
		for offset in EXTRA_POINTER_OFFSETS:
			var tick := posmod(out[0] + int(offset), RC.TICKS)
			if not out.has(tick):
				out.append(tick)
				break
	return out


## A phase's pointer layout with the ICE extra pointer (bosses) and the Breach removal.
## Also what Intel's phase reveal shows.
static func phase_layout(s: CombatState, data: EnemyData, ticks: PackedInt32Array) -> PackedInt32Array:
	return _phase_layout(s, data, ticks)


static func _phase_layout(s: CombatState, data: EnemyData, ticks: PackedInt32Array) -> PackedInt32Array:
	var extra := int(s.flags.get("boss_extra_pointer", 0)) if data.is_boss else 0
	return _trimmed(_with_extra(ticks, extra), int(s.flags.get("boss_pointer_removal", 0)))


## Scales an enemy's HP by `hp_scale` and its slice outputs by `out_scale` (defaults to
## the HP scale).
static func _scale_enemy(e: CombatantState, hp_scale: float, out_scale: float = -1.0) -> void:
	if out_scale < 0.0:
		out_scale = hp_scale
	if not is_equal_approx(hp_scale, 1.0):
		e.max_hp = roundi(e.max_hp * hp_scale)
		e.hp = e.max_hp
		e.hp_scale *= hp_scale
	e.output_scale *= out_scale


static func _to_names(values: Array) -> Array[StringName]:
	var out: Array[StringName] = []
	for v in values:
		out.append(StringName(String(v)))
	return out


## Runs the first START_TURN (shuffle, ON_COMBAT_START Daemon hooks, respins, draw).
## Returns a new state.
func begin_combat(state: CombatState, rng: RandomNumberGenerator) -> CombatResult:
	var result := CombatResult.new()
	var s := state.duplicate_state()
	EffectInterpreter.shuffle(s.draw_pile, rng)
	result.events.append({"type": "combat_start", "text": "Combat begins."})
	var ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0, "source_id": &"combat_start"}
	fx.run_triggers(s, RC.Trigger.ON_COMBAT_START, ctx, _player_listeners(s), rng, result.events)
	for e in s.enemies:
		var hub := fx.hub_of(e.wheel)
		if hub != null and e.is_alive():
			var ectx := {"owner": e, "target": s.player, "pointer_index": 0, "source_id": &"combat_start"}
			fx.run_triggers(s, RC.Trigger.ON_COMBAT_START, ectx, [{"source_id": hub.id, "effects": hub.passive_effects}], rng, result.events)
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
		CombatAction.Type.RESPIN:
			if state.ram < config.respin_ram_cost:
				return "Not enough RAM for a respin (%d needed)." % config.respin_ram_cost
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
				if e.type == RC.EffectType.NUDGE and EffectInterpreter.nudge_ring(e, action, target) == RC.RingScope.INNER and not target.wheel.has_inner_ring():
					return "Target has no inner ring."
				if e.slice_pick == RC.SlicePick.CHOSEN and e.type in [RC.EffectType.APPLY_STATUS, RC.EffectType.CLEANSE, RC.EffectType.DEPLOY_DRONE] and action.slot_index < 0:
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
		CombatAction.Type.RESPIN:
			s.ram -= config.respin_ram_cost
			result.events.append({"type": "ram", "amount": -config.respin_ram_cost, "text": "Respin costs %d RAM (%d)." % [config.respin_ram_cost, s.ram]})
			fx.respin(s.player, rng, result.events, true)
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

## START_TURN: respin non-frozen wheels, apply telegraphed migrations, expire block,
## restore resistance, tick hub breaches, turn-start satellite spawns, RAM regen,
## refresh the free nudge (none on turn 1 under NO_FIRST_TURN_FREE_NUDGE), draw to
## hand size (GDD 2.2 step 1).
func start_turn(s: CombatState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	s.turn += 1
	s.phase = CombatState.Phase.START_TURN
	events.append({"type": "turn_start", "turn": s.turn, "text": "--- Turn %d ---" % s.turn})
	var cls := fx.class_of(s)
	s.ring_locked = false
	s.flags.erase("steady_hand")
	s.flags.erase("resist_free_nudges_used")
	s.double_nudge_cards = s.double_nudge_cards_next
	s.double_nudge_cards_next = false
	for c in s.combatants_in_order():
		if c.wheel.frozen:
			c.wheel.frozen = false
			c.wheel.respin_skipped = true
			events.append({"type": "frozen_skip", "target": c.id, "text": "%s is frozen and skips its respin." % c.display_name})
		else:
			c.wheel.respin_skipped = false
			fx.respin(c, rng, events, true)
		if c.wheel.pointer_orbit != 0 and s.turn > 1:
			c.wheel.orbit_pointers()
			events.append({"type": "orbit", "target": c.id, "text": "%s's pointer orbits to tick %d." % [c.display_name, c.wheel.pointer_ticks[0]]})
		if c.wheel.apply_pending_pointers():
			events.append({"type": "boss_migrate", "target": c.id, "ticks": Array(c.wheel.pointer_ticks),
				"text": "%s's pointers migrate to %s." % [c.display_name, str(Array(c.wheel.pointer_ticks))]})
		c.block = 0
		c.evade_charges = 0
		# Hub start-of-turn passives (Auto-Renew) run while the breach still holds, so a
		# Hub Breach played last turn stops this turn's heal; then the breach expires.
		if not c.is_player:
			_run_enemy_turn_start(s, c, rng, events)
		if c.hub_breached_turns > 0:
			c.hub_breached_turns -= 1
			if c.hub_breached_turns == 0:
				events.append({"type": "hub_restored", "target": c.id, "text": "%s Hub is back online." % c.display_name})
		if not c.is_player:
			c.resistance = maxi(0, c.full_resistance() + c.resistance_carry)
			c.resistance_carry = 0
	for e in s.enemies:
		if e.is_alive() and not e.is_satellite:
			_spawn_turn_start(s, e, rng, events)
	if s.turn > 1:
		s.ram = mini(s.ram + cls.ram_regen, s.max_ram)
		events.append({"type": "ram", "amount": cls.ram_regen, "text": "RAM +%d (%d/%d)." % [cls.ram_regen, s.ram, s.max_ram]})
	if s.ram_bonus_next_turn > 0:
		fx.gain_ram(s, s.ram_bonus_next_turn, events)
		s.ram_bonus_next_turn = 0
	s.free_nudges = cls.free_nudges_per_turn + int(s.flags.get("extra_free_nudges", 0)) + s.free_nudges_next_turn
	s.free_nudges_next_turn = 0
	if s.turn == 1 and int(s.flags.get("no_first_turn_free_nudge", 0)) > 0:
		s.free_nudges = 0
		events.append({"type": "no_free_nudge", "text": "ICE: no free nudge on the first turn."})
	s.spins_this_turn = 0
	_retarget_if_needed(s)
	fx.draw_cards(s, maxi(0, config.hand_size - s.hand.size()), rng, events)
	var ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0, "source_id": &"turn"}
	fx.run_triggers(s, RC.Trigger.ON_TURN_START, ctx, _player_listeners(s), rng, events)
	_settle_deaths(s, events)
	if not s.is_over():
		s.phase = CombatState.Phase.PLAYER_PHASE


## RESOLVE: every pointer of every wheel, defensive -> offensive -> statuses, both
## sides at once (GDD 2.2 step 3). Ends with deaths, outcome and the discard.
func resolve_turn(s: CombatState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	s.phase = CombatState.Phase.RESOLVE
	events.append({"type": "resolve_start", "text": "End turn: resolving."})
	var alive_before: Array[StringName] = []
	for c in s.enemies + s.drones:
		if c.is_alive():
			alive_before.append(c.id)
	var resolutions := _collect_resolutions(s)
	# Rule-breaking Daemons may rewrite the resolutions before anything fires (Stolen Intent).
	var resolve_ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0,
		"source_id": &"resolve", "resolutions": resolutions}
	fx.run_triggers(s, RC.Trigger.ON_RESOLVE, resolve_ctx, _player_listeners(s), rng, events)
	# Consecutive Perfects are counted on the player's first pointer, before hooks run.
	for r in resolutions:
		if r["owner"] == s.player and is_landing(r) and r["slice"].slice_type == RC.SliceType.MISS:
			s.miss_resolved = true  # any read head, Twin Pointer's included (GDD 6.2 Cold Exit)
		if r["owner"] == s.player and r["pointer_index"] == 0 and is_landing(r):
			s.consecutive_perfects = s.consecutive_perfects + 1 if r["tier"] == RC.PrecisionTier.PERFECT else 0
			if r["tier"] == RC.PrecisionTier.PERFECT and int(s.flags.get("steady_hand", 0)) > 0:
				s.ram_bonus_next_turn += int(s.flags["steady_hand"])
				events.append({"type": "steady_hand", "amount": s.ram_bonus_next_turn, "text": "Steady Hand: Perfect at end of turn, +%d RAM next turn." % s.ram_bonus_next_turn})

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
		if r["status"] == RC.Status.CORRUPTED and is_landing(r):
			_corrupted_trigger(s, r, events)
	var end_ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0, "source_id": &"turn"}
	fx.run_triggers(s, RC.Trigger.ON_TURN_END, end_ctx, _player_listeners(s), rng, events)
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


## Boss phases still ahead of `c` (empty for non-bosses); shown when Intel revealed them.
func upcoming_phases(s: CombatState, c: CombatantState) -> Array[BossPhaseData]:
	var out: Array[BossPhaseData] = []
	var data := lookup.get_content(c.source_id) as EnemyData
	if data == null:
		return out
	for i in range(c.phase_index, data.phases.size()):
		if data.phases[i] != null:
			out.append(data.phases[i])
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
	var ignore := fx.ghost_bypass(s, target, events)
	fx.nudge(s, s.player, target, action.ring, action.direction, ignore, events)
	var ctx := {"owner": s.player, "target": target, "action": action, "pointer_index": 0}
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
		"spin_bonus": fx.spin_bonus_of(s.player), "pointer_index": 0, "is_card": true}
	for e in card.effects:
		if e != null:
			fx.apply_effect(s, e, ctx, rng, events)
	fx.run_triggers(s, RC.Trigger.ON_CARD_PLAYED, ctx, _player_listeners(s), rng, events)
	if card.exhaust:
		s.exhaust_pile.append(card_id)
	else:
		s.discard_pile.append(card_id)
	_settle_deaths(s, events)


## Deaths outside resolution (cards, start-of-turn Daemons): mark them, end the fight when
## a side is gone, else keep the target on a living wheel.
func _settle_deaths(s: CombatState, events: Array[Dictionary]) -> void:
	_apply_deaths(s, [], events)
	_check_outcome(s, events)
	if not s.is_over():
		_retarget_if_needed(s)


# --- Internals: resolution -------------------------------------------------------

## Every pointer's readout plus the extra resolutions Firmware neighbour rules add
## (GDD 6.1). Mirror: copy the neighbour on the side you landed (both on Perfect).
## Shunt: resolve that neighbour instead at neighbor_multiplier; nothing special on
## Perfect. Derived entries keep the landing's tier and carry "derived": true.
## The operative's drones (GDD 5.2) resolve only when the slice they dock on does.
func _collect_resolutions(s: CombatState) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var player_slots: Array[int] = []
	for c in s.combatants_in_order():
		if c.is_player and c.is_satellite:
			if not player_slots.has(c.dock_slot):
				continue
			out.append(_readout(s, c, 0))
			continue
		var first := out.size()
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
				var n := _neighbor_resolution(s, r, side, fw.neighbor_multiplier)
				if fw.neighbor_rule == RC.NeighborRule.SHUNT:
					n["landing"] = true  # the shunted slice resolves instead of the landing
				elif n["status"] == RC.Status.OVERCLOCKED:
					n["status"] = RC.Status.NONE  # H18/H19: no Overclock boost without its burn-out
				out.append(n)
		# GDD 5.2: a drone triggers when its slice does, so after the neighbour rules.
		if c == s.player:
			for k in range(first, out.size()):
				if is_landing(out[k]):
					player_slots.append(int(out[k]["slice_index"]))
	return out


func _neighbor_resolution(s: CombatState, r: Dictionary, side: int, multiplier: float) -> Dictionary:
	var c: CombatantState = r["owner"]
	var slot := posmod(int(r["slice_index"]) + side, c.wheel.slice_count)
	var d := r.duplicate()
	d["slice_index"] = slot
	d["slice"] = fx.slice_of(c.wheel, slot)
	# The neighbour's Firmware and the permanent status it grants (Burner) belong to that
	# socket's own landing (H17). A Mirror copy also drops the slot's statuses (H18); a
	# Shunt, which is the landing, keeps them.
	d["firmware"] = null
	d["status"] = c.wheel.slice_statuses[slot]
	d["permanent_status"] = RC.Status.NONE
	d["derived"] = true
	d["extra_multiplier"] = multiplier
	return d


## Listeners for the slice at `r`, in TECH_SPEC order: slice, Firmware, ring segment,
## Hub, Heat-gated enemy behaviour, Daemons.
func _slice_listeners(s: CombatState, r: Dictionary) -> Array:
	var owner: CombatantState = r["owner"]
	var slice: SliceData = r["slice"]
	var out := [{"source_id": slice.id, "effects": slice.extra_effects}]
	var fw: FirmwareData = r["firmware"]
	if fw != null:
		out.append({"source_id": fw.id, "effects": fw.triggered_effects, "limit_scale": maxi(1, owner.wheel.slot_firmware_ids.count(fw.id))})
	var seg: RingSegmentData = r["segment"]
	if seg != null:
		out.append({"source_id": seg.id, "effects": seg.triggered_effects})
	var hub := fx.hub_of(owner.wheel)
	if hub != null and not owner.is_hub_breached():
		var hub_effects: Array[TriggeredEffectData] = hub.passive_effects.duplicate()
		if owner == s.player and hub.perfect_hook != null:
			hub_effects.append(hub.perfect_hook)
		out.append({"source_id": hub.id, "effects": hub_effects})
	if not owner.is_player:
		out.append_array(_heat_listeners(s, owner, slice))
	if owner == s.player:
		for d in _daemon_listeners(s):
			d["once"] = true  # Daemons fire once per landing, not per extra resolution (H15)
			out.append(d)
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
			out.append({"source_id": d.id, "effects": d.triggered_effects, "handler": d.custom_handler, "daemon": d})
	return out


## Enemy behaviour gated on campaign Heat (HeatGatedEffectData, GDD 4.3): active while
## the Heat at combat start is at or above min_heat.
func _heat_listeners(s: CombatState, owner: CombatantState, slice: SliceData = null) -> Array:
	var out := []
	var data := lookup.get_content(owner.source_id) as EnemyData
	if data == null:
		return out
	for i in data.heat_effects.size():
		var he := data.heat_effects[i]
		if he != null and s.campaign_heat >= he.min_heat:
			if he.offensive_slices_only and (slice == null or not (slice.slice_type in [RC.SliceType.ATTACK, RC.SliceType.CRIT])):
				continue
			out.append({"source_id": StringName("%s:heat%d" % [data.id, he.min_heat]), "effects": he.effects})
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
	if r["status"] == RC.Status.PARASITE:
		mult *= config.parasite_multiplier
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
	# The slice, its Firmware, segment and Hub repeat with every resolution (M1/M6 rulings);
	# Daemons fire once per landing, so their text ("each Perfect: +1 damage") holds.
	var per_instance := listeners.filter(func(l: Dictionary) -> bool: return not l.get("once", false))
	# Daemons fire once per landing: never on a Mirror copy of a neighbour (H16).
	var once := listeners.filter(func(l: Dictionary) -> bool: return l.get("once", false)) if is_landing(r) else []
	for m in instances:
		var output := roundi(slice.base_output * m)
		if owner == s.player and slice.slice_type in [RC.SliceType.ATTACK, RC.SliceType.CRIT] and s.damage_bonus > 0:
			output += s.damage_bonus
		_slice_action(s, owner, slice, output, pierce, ctx, events)
		_landing_triggers(s, r, slice, ctx, per_instance, rng, events)
	_landing_triggers(s, r, slice, ctx, once, rng, events)
	if r["status"] == RC.Status.OVERCLOCKED and is_landing(r):
		wheel.slice_statuses[slot] = RC.Status.CORRUPTED
		events.append({"type": "status", "target": owner.id, "slot": slot, "status": RC.Status.CORRUPTED,
			"text": "%s slot %d burns out: OVERCLOCKED -> CORRUPTED." % [owner.display_name, slot]})


## Whether resolution `r` stands for its pointer's landing: the landing itself, or the
## slice a Shunt resolves instead. A Mirror copy of a neighbour is not (Daemons skip it and
## it doesn't resolve the Miss for Cold Exit).
static func is_landing(r: Dictionary) -> bool:
	return not r.get("derived", false) or r.get("landing", false)


## ON_SLICE_TRIGGER, then ON_PERFECT on a Perfect and ON_MISS_SLICE on the Miss, for `listeners`.
func _landing_triggers(s: CombatState, r: Dictionary, slice: SliceData, ctx: Dictionary, listeners: Array, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	if listeners.is_empty():
		return
	fx.run_triggers(s, RC.Trigger.ON_SLICE_TRIGGER, ctx, listeners, rng, events)
	if r["tier"] == RC.PrecisionTier.PERFECT:
		fx.run_triggers(s, RC.Trigger.ON_PERFECT, ctx, listeners, rng, events)
	if slice.slice_type == RC.SliceType.MISS:
		fx.run_triggers(s, RC.Trigger.ON_MISS_SLICE, ctx, listeners, rng, events)


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
				# and shield only). The operative's drones guard the operative the same way.
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
		RC.SliceType.DEPLOY:
			_deploy(s, owner, maxi(1, output), int(ctx.get("slice_index", 0)), events)
		RC.SliceType.AFFLICT:
			events.append({"type": "afflict", "attacker": owner.id, "text": "%s %s." % [owner.display_name, _slice_name(slice)]})
		RC.SliceType.MISS:
			events.append({"type": "miss", "owner": owner.id, "text": "%s lands on MISS." % owner.display_name})
		_:
			events.append({"type": "unsupported_slice", "slice_type": slice.slice_type,
				"text": "%s slice type %s is not implemented yet." % [owner.display_name, RC.SliceType.keys()[slice.slice_type]]})


## DEPLOY slice (GDD 2.6, 5.2): `count` drones of the Hub's template dock on the wheel,
## from the resolved slice clockwise, up to the Hub's max_drones.
func _deploy(s: CombatState, owner: CombatantState, count: int, from_slot: int, events: Array[Dictionary]) -> void:
	var hub := fx.hub_of(owner.wheel)
	if hub == null or hub.drone == null:
		events.append({"type": "deploy_failed", "text": "%s has no drone template to deploy." % owner.display_name})
		return
	for i in count:
		if s.satellites_of(owner.id).size() >= hub.max_drones:
			events.append({"type": "drone_cap", "text": "%s cannot dock more than %d drone(s)." % [owner.display_name, hub.max_drones]})
			return
		if fx.deploy_drone(s, owner, hub.drone, from_slot, events) == null:
			return


## Who `owner`'s pointer attacks: the operative's side (operative or drone) hits the
## chosen target; enemies and their satellites hit the operative.
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
	if owner == s.player:
		fx.drain_ram(s, config.corrupted_ram_drain, events)


## Enemy start-of-turn passives: the Hub's (unless breached) and Heat-gated behaviour.
func _run_enemy_turn_start(s: CombatState, c: CombatantState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var listeners := []
	var hub := fx.hub_of(c.wheel)
	if hub != null and not c.is_hub_breached():
		listeners.append({"source_id": hub.id, "effects": hub.passive_effects})
	listeners.append_array(_heat_listeners(s, c))
	if listeners.is_empty():
		return
	var ctx := {"owner": c, "target": s.player, "pointer_index": 0, "source_id": hub.id if hub != null else c.source_id}
	fx.run_triggers(s, RC.Trigger.ON_TURN_START, ctx, listeners, rng, events)


## ON_TURN_START satellite spawns (SatelliteSpawnData): every `every_n` turns, while
## fewer than max_active of that satellite are alive on the host.
func _spawn_turn_start(s: CombatState, host: CombatantState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var data := lookup.get_content(host.source_id) as EnemyData
	if data == null:
		return
	for i in data.spawns.size():
		var spawn := data.spawns[i]
		if spawn == null or spawn.satellite == null or spawn.trigger != RC.Trigger.ON_TURN_START:
			continue
		var key := "spawn:%s:%d" % [host.id, i]
		var count := int(s.flags.get(key, 0)) + 1
		s.flags[key] = count
		if count % maxi(1, spawn.every_n) != 0:
			continue
		var active := 0
		for sat in s.satellites_of(host.id):
			if sat.source_id == spawn.satellite.id:
				active += 1
		if active >= spawn.max_active:
			continue
		var sat := _spawn_satellite(s, host, spawn, rng)
		_scale_enemy(sat, host.hp_scale, host.output_scale)
		events.append({"type": "satellite_spawn", "target": host.id, "satellite": sat.id, "slot": sat.dock_slot,
			"text": "%s launches %s on slot %d." % [host.display_name, sat.display_name, sat.dock_slot]})


## Reports every enemy, satellite or drone that died this resolve (including ones spawned
## during it) exactly once; satellites go down with their host. Dead combatants stay in
## their lists (filtered by is_alive()).
func _apply_deaths(s: CombatState, _alive_before: Array[StringName], events: Array[Dictionary]) -> void:
	for e in s.enemies:
		if e.hp <= 0 and not e.is_satellite:
			for sat in s.satellites_of(e.id):
				sat.hp = 0
				events.append({"type": "died", "target": sat.id, "text": "%s goes down with its host." % sat.display_name})
				s.flags["dead:%s" % sat.id] = 1
	for c in s.enemies + s.drones:
		var key := "dead:%s" % c.id
		if not c.is_alive() and not s.flags.has(key):
			s.flags[key] = 1
			events.append({"type": "died", "target": c.id, "text": "%s is destroyed." % c.display_name})


## Boss pointer phases (GDD 2.11): entered when HP falls to the threshold. MULTIPLY sets
## the pointer layout at once (minus any Breach removal); MIGRATE telegraphs it and the
## pointers move at the next start of turn; ORBIT sets the per-turn drift; spawns dock
## satellites; wheel and hub overrides swap the layout.
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
				RC.PointerBehavior.MULTIPLY:
					e.wheel.pointer_ticks = _phase_layout(s, data, phase.pointer_ticks)
					e.wheel.pointer_orbit = 0  # a new fixed layout locks on (H16)
				RC.PointerBehavior.MIGRATE:
					e.wheel.pending_pointer_ticks = _phase_layout(s, data, phase.pointer_ticks)
					e.wheel.pointer_orbit = 0
					events.append({"type": "boss_migrate_telegraph", "target": e.id, "ticks": Array(e.wheel.pending_pointer_ticks),
						"text": "%s's pointers flicker: next turn they migrate to %s." % [e.display_name, str(Array(e.wheel.pending_pointer_ticks))]})
				RC.PointerBehavior.ORBIT:
					# A phase that lists pointers sets them before they start orbiting.
					if not phase.pointer_ticks.is_empty():
						e.wheel.pointer_ticks = _phase_layout(s, data, phase.pointer_ticks)
					e.wheel.pointer_orbit = phase.orbit_ticks_per_turn
			if phase.wheel_override != null:
				_apply_wheel_override(e, phase.wheel_override, events, int(s.flags.get("enemy_resistance", 0)))
			if phase.hub_override != null:
				e.wheel.hub_id = phase.hub_override.id
				e.hub_resistance = phase.hub_override.hub_resistance
			for spawn in phase.spawns:
				if spawn != null and spawn.satellite != null:
					for k in spawn.max_active:
						_scale_enemy(_spawn_satellite(s, e, spawn, rng), e.hp_scale, e.output_scale)
			events.append({"type": "boss_phase", "target": e.id, "phase": e.phase_index, "behavior": phase.pointer_behavior,
				"text": "%s enters phase %d (%s)%s" % [e.display_name, e.phase_index, RC.PointerBehavior.keys()[phase.pointer_behavior],
					(": " + phase.phase_line) if phase.phase_line != "" else "."]})


## Swaps the boss's slices, Firmware and passive resistance for the phase layout. The
## rotation, pointers and any pending migration are kept; temporary statuses reset.
func _apply_wheel_override(e: CombatantState, data: WheelData, events: Array[Dictionary], bonus_resistance: int = 0) -> void:
	var fresh := WheelState.from_wheel_data(data)
	var w := e.wheel
	w.slice_count = fresh.slice_count
	w.slot_slice_ids = fresh.slot_slice_ids
	w.slot_firmware_ids = fresh.slot_firmware_ids
	w.slice_statuses = fresh.slice_statuses
	w.passive_resistance = fresh.passive_resistance + bonus_resistance  # ICE / Heat resistance stays
	if data.hub != null:
		w.hub_id = data.hub.id
		e.hub_resistance = data.hub.hub_resistance
	if fresh.has_inner_ring():
		w.ring_segment_ids = fresh.ring_segment_ids
	events.append({"type": "boss_wheel_override", "target": e.id, "slices": Array(w.slot_slice_ids),
		"text": "%s's wheel reconfigures: %s." % [e.display_name, ", ".join(w.slot_slice_ids)]})


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


func _spawn_satellite(s: CombatState, host: CombatantState, spawn: SatelliteSpawnData, rng: RandomNumberGenerator) -> CombatantState:
	var sat := EffectInterpreter.make_combatant(spawn.satellite, StringName("%s_sat_%d" % [host.id, s.spawn_counter]), true)
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
