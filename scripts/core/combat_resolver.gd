class_name CombatResolver
extends RefCounted
## The combat rules (GDD 2, TECH_SPEC 5.3-5.5). Pure: apply() duplicates the state it
## is given and returns a new one plus events. Randomness only through the RNG passed
## in. Content is read through a ContentLookup and never modified.

var config: CampaignConfigData
var lookup: ContentLookup
var fx: EffectInterpreter
## Simulation switch (tools/balance): events carry no `text`. Rules, states and hashes are unchanged; only the
## string building of the hottest events is skipped (it was ~1/4 of an End Turn simulation).
var quiet: bool = false:
	set(v):
		quiet = v
		fx.quiet = v

const DEFENSIVE_TYPES := [RC.SliceType.DEFRAG, RC.SliceType.SANDBOX, RC.SliceType.DETOUR, RC.SliceType.HOTFIX]
const OFFENSIVE_TYPES := [RC.SliceType.SHIM, RC.SliceType.OVERFLOW, RC.SliceType.TROJAN]
const STATUS_TYPES := [RC.SliceType.INFECT]
## validate_action's refusal (code SATELLITE_FIXED) when a player action would move a
## satellite or drone without the Undock keyword (designer 2026-10-18, Q7/Q10).
const SATELLITE_FIXED := "Satellites are fixed to their slice: only Undock moves them."
## N7 refusals (codes NUDGE_LOCKED / RESPIN_LOCKED; the source ids are in lock_refusal()).
const NUDGE_LOCKED := "That wheel's nudges are locked this turn."
const RESPIN_LOCKED := "That wheel's respins are locked this turn."
## Effect types that move the wheel they hit (refused on satellites without Undock).
const SATELLITE_MOVING_EFFECTS := [RC.EffectType.NUDGE, RC.EffectType.SPIN, RC.EffectType.FLIP,
	RC.EffectType.RESPIN, RC.EffectType.FREEZE, RC.EffectType.SNAP_TO_CENTER]


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
##   "enemy_scale" (N2 legacy HP multiplier for enemies without hp_by_tier / hp_bands),
##   "enemy_output_scale" (N2 R2 tier damage factor for enemy outputs; defaults to
##   enemy_scale), "tier" (1..4, clamped; picks hp_by_tier, default 1),
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
	# Combat-start docking reports nothing (no content docks two on one slice at setup).
	var setup_events: Array[Dictionary] = []
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
	var tier := int(overrides.get("tier", 1))
	var boss_scale := 1.0 + maxf(0.0, float(overrides.get("boss_strength_pct", 0.0))) / 100.0
	var extra_resistance := int(overrides.get("enemy_resistance", 0))
	s.flags["boss_pointer_removal"] = int(overrides.get("remove_boss_pointers", 0))
	if bool(overrides.get("reveal_phases", false)):
		s.flags["reveal_phases"] = 1
	if bool(overrides.get("no_first_turn_free_nudge", false)):
		s.flags["no_first_turn_free_nudge"] = 1
	s.flags["extra_free_nudges"] = int(overrides.get("extra_free_nudges", 0))
	if bool(overrides.get("blade", false)):
		s.flags["blade"] = 1  # Halcyon v2: the Blade scans one slice a turn
	# ICE extras that boss phases must keep (H14): the extra pointer and bonus resistance.
	s.flags["boss_extra_pointer"] = int(overrides.get("boss_extra_pointer", 0))
	s.flags["enemy_resistance"] = int(overrides.get("enemy_resistance", 0))
	for i in enemy_datas.size():
		var e := EffectInterpreter.make_combatant(enemy_datas[i], StringName("enemy_%d" % i), false)
		_scale_enemy(e, enemy_scale, enemy_output_scale)
		if enemy_datas[i].is_boss or enemy_datas[i].is_mini_boss:
			_scale_enemy(e, boss_scale)
		_apply_hp_table(e, enemy_datas[i], tier, boss_scale)
		if extra_resistance > 0:
			e.wheel.passive_resistance += extra_resistance
			e.resistance = e.full_resistance()
		# Plan 2 EV-01: Terminal event modifiers (static values, no RNG).
		var event_res := int(overrides.get("event_resistance_delta", 0))
		if event_res != 0:
			e.wheel.passive_resistance = maxi(0, e.wheel.passive_resistance + event_res)
			e.resistance = e.full_resistance()
		var event_hp_pct := int(overrides.get("event_hp_pct", 0))
		if event_hp_pct != 0:
			e.max_hp = maxi(1, roundi(e.max_hp * (100 + event_hp_pct) / 100.0))
			e.hp = e.max_hp
		if bool(overrides.get("event_enemy_frozen", false)):
			e.wheel.frozen = true
		if enemy_datas[i].is_boss:
			_add_pointers(e, int(overrides.get("boss_extra_pointer", 0)))
			_trim_pointers(e, int(s.flags["boss_pointer_removal"]))
			for k in int(overrides.get("boss_corrupt_slices", 0)):
				var slot := fx.pick_slot(s, e, RC.SlicePick.RANDOM_NON_NULL, {}, rng)
				if slot >= 0:
					e.wheel.add_stacks(slot, RC.Status.CORRUPTED, 1, config.status_stack_cap)
		s.enemies.append(e)
		for spawn in enemy_datas[i].spawns:
			if spawn == null or spawn.satellite == null or spawn.trigger != RC.Trigger.ON_COMBAT_START:
				continue
			for k in spawn.max_active:
				_scale_enemy(_spawn_satellite(s, e, spawn, rng, setup_events), e.hp_scale, e.output_scale)
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


## ICE BOSS_EXTRA_POINTER: `count` more pointers, placed by the config offsets.
func _add_pointers(e: CombatantState, count: int) -> void:
	e.wheel.pointer_ticks = with_extra_pointers(e.wheel.pointer_ticks, count, config.boss_extra_pointer_offsets)


## N11 (GDD 2.1, Q27): `ticks` plus `count` more pointers. Each goes on the first of
## `offsets` (ticks after pointer 0; any tick 0-29) that no pointer holds yet, so two
## pointers never share a tick. Draws no RNG.
static func with_extra_pointers(ticks: PackedInt32Array, count: int, offsets: PackedInt32Array) -> PackedInt32Array:
	var out := ticks.duplicate()
	if out.is_empty():
		return out
	for i in count:
		for offset in offsets:
			var tick := posmod(out[0] + offset, RC.TICKS)
			if not out.has(tick):
				out.append(tick)
				break
	return out


## A phase's pointer layout with the ICE extra pointer (bosses) and the Breach removal.
## Also what Intel's phase reveal shows. The single placement path: preview and resolve
## both enter phases through `_check_boss_phases`, which calls this.
func phase_layout(s: CombatState, data: EnemyData, ticks: PackedInt32Array) -> PackedInt32Array:
	var extra := int(s.flags.get("boss_extra_pointer", 0)) if data.is_boss else 0
	return _trimmed(with_extra_pointers(ticks, extra, config.boss_extra_pointer_offsets), int(s.flags.get("boss_pointer_removal", 0)))


## N2 (R2): an enemy with hp_by_tier / hp_bands starts at the authored HP, not the legacy
## multiplier: a boss reads hp_bands by the ICE boss-strength multiplier; a mini-boss's
## hp_by_tier still takes that multiplier. hp_scale is left as is (satellites inherit it).
static func _apply_hp_table(e: CombatantState, data: EnemyData, tier: int, boss_scale: float) -> void:
	if not data.uses_hp_table():
		return
	var hp := data.hp_for(boss_scale) if data.is_boss else data.hp_at_tier(tier)
	if data.is_mini_boss and not data.is_boss:
		hp = roundi(hp * boss_scale)
	e.max_hp = maxi(1, hp)
	e.hp = e.max_hp


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
			if state.player.wheel.is_locked(WheelState.LOCK_RESPIN):
				return RESPIN_LOCKED
			var respin_cost := RamCost.of_action(state, action, self)
			if state.ram < respin_cost:
				return "Not enough RAM for a respin (%d needed)." % respin_cost
		CombatAction.Type.NUDGE:
			var t := state.get_combatant(action.wheel_id)
			if t == null or not t.is_alive():
				return "Invalid wheel."
			if t.is_satellite:
				return SATELLITE_FIXED
			if t.wheel.is_locked(WheelState.LOCK_NUDGE):
				return NUDGE_LOCKED  # free and paid nudges alike; costs nothing
			if action.ring == RC.RingScope.INNER and not t.wheel.has_inner_ring():
				return "That wheel has no inner ring."
			var nudge_cost := RamCost.of_action(state, action, self)
			if state.free_nudges <= 0 and state.ram < nudge_cost:
				return "No free nudge left, and an extra nudge costs %d RAM." % nudge_cost
		CombatAction.Type.PLAY_CARD:
			if action.hand_index < 0 or action.hand_index >= state.hand.size():
				return "No such card in hand."
			var card := lookup.get_content(state.hand[action.hand_index]) as CardData
			if card == null:
				return "Unknown card."
			var card_cost := RamCost.of_action(state, action, self)
			if state.ram < card_cost:
				return "Not enough RAM (%d needed)." % card_cost
			var target := card_target(state, card, action)
			if target == null or not target.is_alive():
				return "Card has no valid target wheel."
			if card.wheel_target == RC.WheelTarget.SATELLITE and not target.is_satellite:
				return "Card must target a satellite."
			for e in card.effects:
				if e != null and effect_moves_satellite(state, e, target):
					return SATELLITE_FIXED
			for e in card.effects:
				if e == null:
					continue
				if e.type == RC.EffectType.RESPIN and _effect_wheel(state, e, target).wheel.is_locked(WheelState.LOCK_RESPIN):
					return RESPIN_LOCKED
				if (e.type == RC.EffectType.FLIP or e.type == RC.EffectType.RESPIN) and target != state.player and target.resistance > 0:
					return "%s blocked: %s has %d resistance." % [RC.EffectType.keys()[e.type], target.display_name, target.resistance]
				if e.type == RC.EffectType.NUDGE and EffectInterpreter.nudge_ring(e, action, target) == RC.RingScope.INNER and not target.wheel.has_inner_ring():
					return "Target has no inner ring."
				if e.slice_pick == RC.SlicePick.CHOSEN and e.type in [RC.EffectType.APPLY_STATUS, RC.EffectType.CLEANSE, RC.EffectType.DEPLOY_DRONE] and action.slot_index < 0:
					return "Choose a slice."
	return ""


## The wheel the card effect `e` hits when the card's target wheel is `target`.
func _effect_wheel(state: CombatState, e: EffectData, target: CombatantState) -> CombatantState:
	match e.target:
		RC.EffectTarget.SELF, RC.EffectTarget.OWN_WHEEL, RC.EffectTarget.CAMPAIGN:
			return state.player
	return target


## N7: the lock behind a refusal, {"code": "NUDGE_LOCKED" | "RESPIN_LOCKED", "sources": [ids]}, or
## {} when `action` is not refused by a lock. Same checks, same order as validate_action.
func lock_refusal(state: CombatState, action: CombatAction) -> Dictionary:
	var reason := validate_action(state, action)
	if reason != NUDGE_LOCKED and reason != RESPIN_LOCKED:
		return {}
	var kind := WheelState.LOCK_NUDGE if reason == NUDGE_LOCKED else WheelState.LOCK_RESPIN
	var wheel_of: CombatantState = state.player
	if action.type == CombatAction.Type.NUDGE:
		wheel_of = state.get_combatant(action.wheel_id)
	elif action.type == CombatAction.Type.PLAY_CARD:
		var card := lookup.get_content(state.hand[action.hand_index]) as CardData
		var target := card_target(state, card, action)
		for e in card.effects:
			if e != null and e.type == RC.EffectType.RESPIN and _effect_wheel(state, e, target).wheel.is_locked(kind):
				wheel_of = _effect_wheel(state, e, target)
				break
	return {"code": "NUDGE_LOCKED" if kind == WheelState.LOCK_NUDGE else "RESPIN_LOCKED", "sources": wheel_of.wheel.lock_sources(kind)}


## Whether `e`, played by the operative at `target`, would move a satellite or drone (its
## slice or its mini-wheel) without the Undock keyword: satellites are fixed to their slice
## (designer 2026-10-18, Q7/Q10). Nudge, spin, flip, respin, freeze and snap count, and so
## does a custom handler that declares MOVES_SATELLITE (Undock).
static func effect_moves_satellite(state: CombatState, e: EffectData, target: CombatantState) -> bool:
	if e.undock:
		return false
	var moves: bool = e.type in SATELLITE_MOVING_EFFECTS
	if e.type == RC.EffectType.CUSTOM and e.custom_handler != null:
		moves = bool(e.custom_handler.get_script_constant_map().get("MOVES_SATELLITE", false))
	if not moves:
		return false
	match e.target:
		RC.EffectTarget.SELF, RC.EffectTarget.OWN_WHEEL, RC.EffectTarget.CAMPAIGN:
			return false
		RC.EffectTarget.ALL_ENEMIES:
			for c in state.living_enemies(true):
				if c.is_satellite:
					return true
			return false
	return target != null and target.is_satellite


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
			var respin_cost := RamCost.of_action(state, action, self)
			s.ram -= respin_cost
			result.events.append({"type": "ram", "amount": -respin_cost, "text": "Respin costs %d RAM (%d)." % [respin_cost, s.ram]})
			fx.respin(s.player, rng, result.events, true)
			if fire_listeners(s, RC.Trigger.ON_RAM_SPENT, {"amount": respin_cost, "action": action}, rng, result.events) > 0:
				_settle_deaths(s, rng, result.events)
		CombatAction.Type.PLAY_CARD:
			_apply_card(s, action, rng, result.events)
		CombatAction.Type.END_TURN:
			resolve_turn(s, rng, result.events)
			result.resolved_state = s.duplicate_state()
			if not s.is_over():
				end_turn(s, result.events)
				start_turn(s, rng, result.events)
	return result


## Same as apply() on a copy of the RNG: the state and RNG passed in stay untouched.
## Preview must equal the real result (tested).
func preview(state: CombatState, action: CombatAction, rng: RandomNumberGenerator) -> CombatResult:
	return apply(state, action, clone_rng(rng))


## Plan 2 Q19: the forecast of `action`: its result with every known part exact and each random
## part (a respin's landing, a RANDOM_NON_NULL pick, a reshuffle) left undecided and listed in
## `unknowns`. Draws nothing from `rng` and leaves `state` untouched. A play with no random part
## forecasts exactly what apply() then does (tested over seeded states).
func forecast(state: CombatState, action: CombatAction, rng: RandomNumberGenerator) -> PreviewResult:
	var out := PreviewResult.new()
	var fork := clone_rng(rng)
	var drawn_from := fork.state
	var marks: Array = []
	fx.forecast_marks = marks
	fx.forecast_in_listener = false
	out.result = apply(state, action, fork)
	fx.forecast_marks = null
	fx.forecast_in_listener = false
	for m in marks:
		out.unknowns.append(m)
	if fork.state != drawn_from and marks.is_empty():
		out.unknowns.append({"kind": PreviewResult.UNMODELLED, "target": &"", "listener": false})
	return out


## The End Turn preview: RESOLVE only, on copies. Equals apply(END_TURN).resolved_state.
func preview_end_turn(state: CombatState, rng: RandomNumberGenerator) -> CombatResult:
	var result := CombatResult.new()
	var s := state.duplicate_state()
	resolve_turn(s, clone_rng(rng), result.events)
	result.state = s
	result.resolved_state = s
	return result


## The RAM the operative starts the next turn with when the turn ends in `resolved` (the End
## Turn preview's state): the regen, then the banked bonus, both capped as `start_turn` caps
## them. Turn-start triggers a Daemon adds are not forecast. W2-A2: "RAM after SEND IT".
func ram_next_turn(resolved: CombatState) -> int:
	var cls := fx.class_of(resolved)
	var ram := mini(resolved.ram + (cls.ram_regen if cls != null else 0), resolved.max_ram)
	if resolved.ram_bonus_next_turn > 0:
		ram = mini(ram + resolved.ram_bonus_next_turn, resolved.max_ram)
	return ram


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
		c.listener_fires_turn.clear()  # N6: per-turn listener caps start over
		# Hub start-of-turn passives (Auto-Renew) run while the breach still holds, so a
		# Hub Breach played last turn stops this turn's heal; then the breach expires.
		if not c.is_player:
			_run_enemy_turn_start(s, c, rng, events)
		if c.hub_breached_turns > 0:
			c.hub_breached_turns -= 1
			if c.hub_breached_turns == 0:
				events.append({"type": "hub_restored", "target": c.id, "text": "%s Hub is back online." % c.display_name})
		if not c.is_player:
			refresh_enrage(s, c, events)
			_refresh_resistance(c, events)
	_apply_pending_locks(s, events)
	_blade_scan(s, events)
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
	_settle_deaths(s, rng, events)
	if not s.is_over():
		s.phase = CombatState.Phase.PLAYER_PHASE


## Halcyon v2 (rule 7): at the start of a turn the Blade's scan line marks slot `(turn - 1) mod n`
## over the operative's non-empty slots: that slice reads TIER_DOWN for this turn's resolve. A temporary
## ENCRYPTED stack absorbs it. Flags: "blade_slot" (slot + 1, 0 = none) and "blade_stacks" (what landed).
func _blade_scan(s: CombatState, events: Array[Dictionary]) -> void:
	s.flags.erase("blade_slot")
	s.flags.erase("blade_stacks")
	if int(s.flags.get("blade", 0)) <= 0 or s.player == null:
		return
	var slot := EyeRules.blade_slot(s.player.wheel.layout(), s.turn)
	if slot < 0:
		return
	s.flags["blade_slot"] = slot + 1
	var before := s.player.wheel.stacks_of(slot, RC.Status.TIER_DOWN)
	fx.apply_status(s.player, slot, RC.Status.TIER_DOWN, events, config.blade_tier_drop)
	var landed := s.player.wheel.stacks_of(slot, RC.Status.TIER_DOWN) - before
	if landed > 0:
		s.flags["blade_stacks"] = landed
	events.append({"type": "blade_scan", "slot": slot, "absorbed": landed <= 0,
		"text": "" if quiet else "The Blade scans slot %d%s." % [slot, " (absorbed)" if landed <= 0 else ""]})


## The Blade's mark lasts the one resolve: its stacks leave at the end of the turn.
func _blade_clear(s: CombatState) -> void:
	var landed := int(s.flags.get("blade_stacks", 0))
	var slot := int(s.flags.get("blade_slot", 0)) - 1
	if landed > 0 and slot >= 0 and s.player != null:
		s.player.wheel.remove_stacks(slot, RC.Status.TIER_DOWN, mini(landed, s.player.wheel.stacks_of(slot, RC.Status.TIER_DOWN)))
	s.flags.erase("blade_slot")
	s.flags.erase("blade_stacks")


## N7 (Q31 answer 1): the locks queued at RESOLVE take hold of their wheels, after the
## start-of-turn spin; a wheel that is gone gets none. They clear at the end of this turn.
func _apply_pending_locks(s: CombatState, events: Array[Dictionary]) -> void:
	for p in s.pending_locks:
		var c := s.get_combatant(StringName(p["wheel"]))
		if c != null and c.is_alive() and c.wheel.add_lock(StringName(p["kind"]), StringName(p["source"]), int(p["turns"])):
			events.append({"type": "lock", "target": c.id, "kind": StringName(p["kind"]), "source": StringName(p["source"]),
				"text": "%s's %s is locked this turn." % [c.display_name, p["kind"]]})
	s.pending_locks.clear()


## N21 (rulings Q16, Q31): the turn's resistance refresh. `c` regains its full per-turn
## resistance (passive + hub while up + enrage) plus any change carried from the last
## RESOLVE, from 0 (end_turn zeroed it). A gain above 0 is the HUD's "+N" mark and a
## `resistance_refresh` event. No RNG.
func _refresh_resistance(c: CombatantState, events: Array[Dictionary]) -> void:
	var gain := maxi(0, c.full_resistance() + c.resistance_carry)
	c.resistance_carry = 0
	c.resistance = gain
	c.resistance_gain = gain
	if gain > 0:
		events.append({"type": "resistance_refresh", "target": c.id, "amount": gain,
			"text": "%s regains %d resistance." % [c.display_name, gain]})


## END OF TURN (ruling Q31), after RESOLVE and before the next START_TURN: every enemy's
## resistance goes to 0 (a change RESOLVE made still waits in `resistance_carry` for the
## refresh). Not part of the End Turn preview (`resolved_state`), which shows RESOLVE only.
func end_turn(s: CombatState, _events: Array[Dictionary]) -> void:
	_blade_clear(s)
	for c in s.combatants_in_order():
		if c.wheel != null:
			c.wheel.clear_locks()  # N7 (Q31): every lock goes; Freeze alone persists (start_turn consumes it)
		if c.is_player:
			continue
		c.resistance = 0
		c.resistance_gain = 0


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
		if r["owner"] == s.player and is_landing(r) and r["slice"].slice_type == RC.SliceType.NULL:
			s.null_resolved = true  # any read head, Twin Pointer's included (GDD 6.2 Cold Exit)
		if r["owner"] == s.player and r["pointer_index"] == 0 and is_landing(r):
			s.consecutive_perfects = s.consecutive_perfects + 1 if r["tier"] == RC.PrecisionTier.PERFECT else 0
			if r["tier"] == RC.PrecisionTier.PERFECT and int(s.flags.get("steady_hand", 0)) > 0:
				s.ram_bonus_next_turn += int(s.flags["steady_hand"])
				events.append({"type": "steady_hand", "amount": s.ram_bonus_next_turn, "text": "Steady Hand: Perfect at end of turn, +%d RAM next turn." % s.ram_bonus_next_turn})

	for r in resolutions:
		events.append({"type": "pointer", "owner": r["owner"].id, "pointer_index": r["pointer_index"], "tick": r["tick"],
			"slice_index": r["slice_index"], "offset": r["offset"], "tier": r["tier"], "segment_index": r["segment_index"],
			"text": "" if quiet else "%s pointer %d: tick %d -> %s (offset %+d, %s%s)." % [r["owner"].display_name, r["pointer_index"], r["tick"],
				r["slice"].display_name if r["slice"].display_name != "" else String(r["slice"].id), r["offset"],
				RC.PrecisionTier.keys()[r["tier"]] if not r["owner"].is_satellite else "full output",
				(", ring " + r["segment"].display_name) if r["segment"] != null else ""]})
	# N6: ON_PERFECT / ON_HIT_DEALT occurrences the slice passes collect, heard after them.
	var heard: Array = []
	events.append({"type": "pass", "pass": "defensive", "text": "[defensive pass]"})
	for r in resolutions:
		if r["slice"].slice_type in DEFENSIVE_TYPES:
			_resolve_pointer(s, r, rng, events, heard)
	events.append({"type": "pass", "pass": "offensive", "text": "[offensive pass]"})
	for r in resolutions:
		if r["slice"].slice_type in OFFENSIVE_TYPES:
			_resolve_pointer(s, r, rng, events, heard)
	events.append({"type": "pass", "pass": "statuses", "text": "[status pass]"})
	for r in resolutions:
		if r["slice"].slice_type in STATUS_TYPES or r["slice"].slice_type == RC.SliceType.NULL:
			_resolve_pointer(s, r, rng, events, heard)
	# N6 (acceptance 9): enemy listeners after the slice passes, in occurrence order.
	for h in heard:
		fire_listeners(s, int(h["trigger"]), h, rng, events)
	var end_ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0, "source_id": &"turn"}
	fx.run_triggers(s, RC.Trigger.ON_TURN_END, end_ctx, _player_listeners(s), rng, events)
	_apply_deaths(s, alive_before, rng, events)
	_check_boss_phases(s, rng, events)
	_check_outcome(s, events)
	s.discard_pile.append_array(s.hand)
	s.hand.clear()
	_retarget_if_needed(s)


# --- Enrage (plan 2 R4, N4) -------------------------------------------------------

## The enrage `c` fights with (authored, else its class default), or null: normals,
## satellites and the operative have none.
func enrage_of(c: CombatantState) -> EnrageData:
	if c == null or c.is_player or c.is_satellite:
		return null
	return config.enrage_for(lookup.get_content(c.source_id) as EnemyData)


## Sets `c`'s enrage step, hit factor and resistance for `s.turn` (a pure function of the
## turn: calling it again on the same turn changes nothing). Logs an "enrage" event when
## the step rises. Runs at the start of each turn, before the resistance restore.
func refresh_enrage(s: CombatState, c: CombatantState, events: Array[Dictionary]) -> void:
	var data := enrage_of(c)
	var step := data.enrage_step(s.turn) if data != null else 0
	var before := c.enrage_step
	c.enrage_step = step
	c.enrage_percent = data.damage_percent_at_step(step) if data != null else RC.PERCENT_MAX
	c.enrage_resistance = data.resistance_at_step(step) if data != null else 0
	if step > before:
		events.append({"type": "enrage", "target": c.id, "step": step, "percent": c.enrage_percent,
			"text": "%s enrages (step %d): its hits deal %d%%." % [c.display_name, step, c.enrage_percent]})


## What the enemy's enrage buff shows (N4, ruling Q33: no countdown before step 1):
## {visible, step, percent (hit factor, 100 = unchanged), resistance (added per turn),
## step_percent, step_resistance (what each step adds), next_turn (the turn of the next
## step), turns_to_next (from the current turn)}. Hidden (visible false) for normals,
## satellites, the operative and any enemy at step 0.
func enrage_buff_state(s: CombatState, c: CombatantState) -> Dictionary:
	var data := enrage_of(c)
	if data == null or c.enrage_step < 1:
		return {"visible": false, "step": 0, "percent": RC.PERCENT_MAX, "resistance": 0,
			"step_percent": 0, "step_resistance": 0, "next_turn": 0, "turns_to_next": 0}
	var next_turn := data.next_step_turn(c.enrage_step)
	return {"visible": true, "step": c.enrage_step, "percent": c.enrage_percent, "resistance": c.enrage_resistance,
		"step_percent": data.damage_pct_step, "step_resistance": data.resistance_step,
		"next_turn": next_turn, "turns_to_next": maxi(0, next_turn - s.turn)}


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
	# N12 (R11): cumulative slot boundaries; the tier is the slot's sub-tick quality map
	# (Calibrated included). Satellites and drones resolve at full output.
	var slice_index := wheel.slot_of_tick(tick)
	var offset := WheelMath.offset_in(tick, wheel.layout())
	var map_tier: int = fx.tier_at_tick(wheel, tick)
	var tier: int = map_tier if not c.is_satellite else RC.PrecisionTier.PERFECT
	var segment_index := -1
	var segment: RingSegmentData = null
	if wheel.has_inner_ring():
		segment_index = WheelMath.ring_segment(wheel.inner_tick_at(pointer_index))
		segment = fx.segment_of(wheel, segment_index)
	var guard := s.satellite_at(c.id, slice_index)
	var stacks: Dictionary = wheel.slice_stacks[slice_index].duplicate() if slice_index < wheel.slice_stacks.size() else {}
	var permanent := fx.permanent_status(wheel, slice_index)
	tier = downgraded_tier(tier, int(stacks.get(RC.Status.TIER_DOWN, 0)))  # N9: Perfect hooks read the lowered tier
	return {
		"owner": c, "pointer_index": pointer_index, "tick": tick, "slice_index": slice_index,
		"slice": fx.slice_of(wheel, slice_index), "firmware": fx.firmware_of(wheel, slice_index),
		"offset": offset, "tier": tier, "segment_index": segment_index, "segment": segment,
		"side": WheelMath.side_in(tick, wheel.layout()) if map_tier != RC.PrecisionTier.PERFECT else 0,
		"guard_id": guard.id if guard != null else &"",
		"stacks": stacks, "permanent_status": permanent,
	}


# --- Internals: actions ----------------------------------------------------------

func _apply_nudge(s: CombatState, action: CombatAction, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var spent := 0
	if s.free_nudges > 0:
		s.free_nudges -= 1
	else:
		var cost := RamCost.of_action(s, action, self)
		s.ram -= cost
		spent = cost
		events.append({"type": "ram", "amount": -cost, "text": "Extra nudge costs %d RAM (%d)." % [cost, s.ram]})
	var target := s.get_combatant(action.wheel_id)
	var ignore := fx.ghost_bypass(s, target, events)
	fx.nudge(s, s.player, target, action.ring, action.direction, ignore, events)
	var ctx := {"owner": s.player, "target": target, "action": action, "pointer_index": 0}
	fx.run_triggers(s, RC.Trigger.ON_NUDGE, ctx, _player_listeners(s), rng, events)
	# N6: the enemies hear the accepted nudge (a free one spends no RAM).
	var fired := fire_listeners(s, RC.Trigger.ON_RAM_SPENT, {"amount": spent, "action": action}, rng, events)
	fired += fire_listeners(s, RC.Trigger.ON_NUDGE, {"action": action, "victim": target}, rng, events)
	if fired > 0:
		_settle_deaths(s, rng, events)


func _apply_card(s: CombatState, action: CombatAction, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var card_id := s.hand[action.hand_index]
	var card := lookup.get_content(card_id) as CardData
	var target := card_target(s, card, action)
	var cost := RamCost.of_action(s, action, self)  # judged before the card leaves the hand or moves anything
	s.hand.remove_at(action.hand_index)
	s.ram -= cost
	events.append({"type": "card", "card_id": card_id, "target": target.id, "cost": cost,
		"text": "Play %s on %s (RAM -%d, %d left)." % [card.display_name if card.display_name != "" else String(card_id), target.display_name, cost, s.ram]})
	var ctx := {"owner": s.player, "target": target, "action": action, "source_id": card_id,
		"spin_bonus": fx.spin_bonus_of(s.player), "pointer_index": 0, "is_card": true}
	for e in card.effects:
		if e != null:
			fx.apply_effect(s, e, ctx, rng, events)
	fx.run_triggers(s, RC.Trigger.ON_CARD_PLAYED, ctx, _player_listeners(s), rng, events)
	# N6: the enemies hear the accepted play, after its effects and the operative's hooks.
	fire_listeners(s, RC.Trigger.ON_RAM_SPENT, {"amount": cost, "action": action, "card_id": card_id}, rng, events)
	fire_listeners(s, RC.Trigger.ON_CARD_PLAYED, {"action": action, "card_id": card_id, "victim": target}, rng, events)
	if card.exhaust:
		s.exhaust_pile.append(card_id)
	else:
		s.discard_pile.append(card_id)
	_settle_deaths(s, rng, events)


## Deaths outside resolution (cards, start-of-turn Daemons): mark them, end the fight when
## a side is gone, else keep the target on a living wheel.
func _settle_deaths(s: CombatState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	_apply_deaths(s, [], rng, events)
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
			# N12: the side of the slot's true middle the needle landed on (0 on a Perfect
			# tick of the map before any TIER_DOWN, or the exact middle of an odd slot).
			var side_of: int = r["side"]
			var sides: Array[int] = []
			if side_of != 0:
				sides.append(side_of)
			elif fw.neighbor_rule == RC.NeighborRule.MIRROR:
				sides = [1, -1]
			if fw.neighbor_rule == RC.NeighborRule.MIRROR or sides.is_empty():
				out.append(r)
			for side in sides:
				var n := _neighbor_resolution(s, r, side, fw.neighbor_multiplier)
				if fw.neighbor_rule == RC.NeighborRule.SHUNT:
					n["landing"] = true  # the shunted slice resolves instead of the landing
				elif stacks_in(n, RC.Status.OVERCLOCKED) > 0:
					(n["stacks"] as Dictionary).erase(RC.Status.OVERCLOCKED)  # H18/H19: no Overclock boost without its burn-out
				out.append(n)
		# GDD 5.2: a drone triggers when its slice does, so after the neighbour rules.
		if c == s.player:
			for k in range(first, out.size()):
				if is_landing(out[k]):
					player_slots.append(int(out[k]["slice_index"]))
	return out


func _neighbor_resolution(s: CombatState, r: Dictionary, side: int, multiplier: float) -> Dictionary:
	var c: CombatantState = r["owner"]
	var slot := WheelMath.neighbor_slot(int(r["slice_index"]), side, c.wheel.layout())  # N12: skips empty arcs
	var d := r.duplicate()
	d["slice_index"] = slot
	d["slice"] = fx.slice_of(c.wheel, slot)
	# The neighbour's Firmware and the permanent status it grants (Burner) belong to that
	# socket's own landing (H17). A Mirror copy also drops the slot's statuses (H18); a
	# Shunt, which is the landing, keeps them.
	d["firmware"] = null
	d["stacks"] = c.wheel.slice_stacks[slot].duplicate()
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


## N6: true while an enemy listener's effects run; fire_listeners refuses to nest (a
## listener never fires another listener: acceptance 5).
var _in_listener: bool = false


## Plan 2 N6: fires every living enemy's listeners on `trigger`, enemies in id order
## (IdSort), each enemy's own listeners then its Hub's (silent while breached), in index
## order. `info` describes the occurrence: "amount" (RAM spent, HP damage, landed output),
## "tier" (RESOLVE triggers; actions pass any min_tier), "action", "card_id", "victim".
## Caps: per turn (authored, else the config default) and per combat, counted on the
## enemy's CombatantState. ON_RAM_SPENT with amount 0 is not heard. Effects run with the
## enemy as owner and the operative as target and draw no RNG (validated). Logs one
## "listener" event per fire. Returns how many listeners fired.
func fire_listeners(s: CombatState, trigger: int, info: Dictionary, rng: RandomNumberGenerator, events: Array[Dictionary]) -> int:
	if _in_listener:
		return 0
	if trigger == RC.Trigger.ON_RAM_SPENT and int(info.get("amount", 0)) <= 0:
		return 0
	var tier := int(info.get("tier", RC.PrecisionTier.PERFECT))
	var fired := 0
	_in_listener = true
	fx.forecast_in_listener = true
	for c in _listening_enemies(s):
		for entry in enemy_listeners(c):
			var l: ListenerData = entry["data"]
			if int(l.trigger) != trigger or tier < int(l.min_tier) or not c.is_alive():
				continue
			var key: String = entry["key"]
			var turn_fires := int(c.listener_fires_turn.get(key, 0))
			var combat_fires := int(c.listener_fires_combat.get(key, 0))
			if turn_fires >= l.turn_cap(config):
				continue
			if l.max_per_combat != ListenerData.UNAUTHORED and combat_fires >= l.max_per_combat:
				continue
			c.listener_fires_turn[key] = turn_fires + 1
			c.listener_fires_combat[key] = combat_fires + 1
			fired += 1
			events.append({"type": "listener", "owner": c.id, "listener": key, "trigger": trigger,
				"amount": int(info.get("amount", 0)), "fires_turn": turn_fires + 1,
				"text": "" if quiet else "%s reacts (%s)." % [c.display_name, RC.Trigger.keys()[trigger]]})
			var ctx := {"owner": c, "target": s.player, "pointer_index": 0, "source_id": StringName(key),
				"action": info.get("action"), "trigger_amount": int(info.get("amount", 0)), "listener": true}
			for e in l.effects:
				if e != null:
					fx.apply_effect(s, e, ctx, rng, events)
	_in_listener = false
	fx.forecast_in_listener = false
	return fired


## N6: `c`'s listeners in firing order: its EnemyData's, then its current Hub's (none while
## breached), as [{key, data}]. The key ("<content id>:L<index>") names the counter.
func enemy_listeners(c: CombatantState) -> Array:
	var out := []
	if c == null or c.is_player:
		return out
	var data := lookup.get_content(c.source_id) as EnemyData
	if data != null:
		for i in data.listeners.size():
			if data.listeners[i] != null:
				out.append({"key": listener_key(data.id, i), "data": data.listeners[i]})
	var hub := fx.hub_of(c.wheel) if c.wheel != null else null
	if hub != null and not c.is_hub_breached():
		for i in hub.listeners.size():
			if hub.listeners[i] != null:
				out.append({"key": listener_key(hub.id, i), "data": hub.listeners[i]})
	return out


## N6: the counter key of listener `index` of content `owner_id`.
static func listener_key(owner_id: StringName, index: int) -> String:
	return "%s:L%d" % [owner_id, index]


## N6: the living enemies (satellites included), by combatant id in text order.
func _listening_enemies(s: CombatState) -> Array[CombatantState]:
	var ids: Array = []
	for e in s.enemies:
		if e.is_alive():
			ids.append(e.id)
	IdSort.sort_ids(ids)
	var out: Array[CombatantState] = []
	for id in ids:
		out.append(s.get_combatant(id))
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
			if he.offensive_slices_only and (slice == null or not (slice.slice_type in [RC.SliceType.SHIM, RC.SliceType.OVERFLOW])):
				continue
			out.append({"source_id": StringName("%s:heat%d" % [data.id, he.min_heat]), "effects": he.effects})
	return out


## Resolves one pointer: computes multipliers and extra resolutions, runs the base
## slice action per instance, then the slice's own listeners.
## Plan 2 N20 rider order: tier output (tier factor, WEAK factor) -> `perfect_multiplier`
## (PERFECT only) -> the other multipliers (Firmware, OVERCLOCKED, OUTPUT_DOWN, segment),
## one product and one rounding per instance -> the hit list (`hit_count` hits of that
## amount, each per target needle) -> per-hit absorption in `deal_hit` (enrage, SANDBOX
## charge, bodyguard, BLOCK and SHIELD unless pierce, then HP). A retrigger (a Breaker
## Perfect "resolves twice") repeats the whole hit list. Riders draw no RNG.
## N6: `heard` collects the enemy-listener occurrences this pointer makes (each landed hit of
## the operative's side, ON_HIT_DEALT; a Perfect landing of the operative, ON_PERFECT, once
## per needle whatever its retriggers); resolve_turn fires them after the slice passes.
func _resolve_pointer(s: CombatState, r: Dictionary, rng: RandomNumberGenerator, events: Array[Dictionary], heard: Array = []) -> void:
	# No liveness check: resolution is simultaneous, so a combatant that dropped to 0 HP
	# earlier in this resolve still fires everything it landed on. Deaths apply at the end.
	var owner: CombatantState = r["owner"]
	var slice: SliceData = r["slice"]
	var wheel := owner.wheel
	var slot: int = r["slice_index"]
	var ctx := {"owner": owner, "target": _pointer_target(s, owner), "pointer_index": r["pointer_index"],
		"tier": r["tier"], "slice_index": slot, "source_id": slice.id, "heard": heard}
	var listeners := _slice_listeners(s, r)
	# Plan 2 R5: a PERCENT slice reads the owner's max HP and skips the tier factor; the
	# precision, Firmware, status and segment multipliers still apply after it.
	var base := slice_base(owner, slice)
	var tier_factor := 1.0 if slice.amount_mode == RC.AmountMode.PERCENT else owner.output_scale
	var mult: float = tier_factor * float(r.get("extra_multiplier", 1.0))
	if r["tier"] == RC.PrecisionTier.WEAK:
		mult *= config.weak_multiplier
	elif r["tier"] == RC.PrecisionTier.PERFECT:
		mult *= slice.perfect_multiplier  # N20 rider (Medicine); 1.0 by default
	var fw: FirmwareData = r["firmware"]
	if fw != null:
		mult *= fw.output_multiplier
	# N8: OVERCLOCKED is 1.5x at any stack count; OUTPUT_DOWN takes its share per stack.
	var overclocked: bool = stacks_in(r, RC.Status.OVERCLOCKED) > 0 or r["permanent_status"] == RC.Status.OVERCLOCKED
	if overclocked:
		mult *= config.overclock_multiplier
	mult *= output_down_factor(stacks_in(r, RC.Status.OUTPUT_DOWN), config)
	var pierce := slice.pierce  # N20 rider (Adrenaline)
	var seg: RingSegmentData = r["segment"]
	if seg != null:
		mult *= seg.output_multiplier
		pierce = pierce or seg.pierce
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
	var per_instance: Array = []
	var once_all: Array = []
	for l in listeners:
		if l.get("once", false):
			once_all.append(l)
		else:
			per_instance.append(l)
	# Daemons fire once per landing: never on a Mirror copy of a neighbour (H16).
	var once: Array = once_all if is_landing(r) else []
	var landed_output := 0
	for m in instances:
		var output := roundi(base * m)
		if owner == s.player and slice.slice_type in [RC.SliceType.SHIM, RC.SliceType.OVERFLOW] and s.damage_bonus > 0:
			output += s.damage_bonus
		landed_output += output
		_slice_action(s, owner, slice, output, pierce, ctx, events)
		_landing_triggers(s, r, slice, ctx, per_instance, rng, events)
	_landing_triggers(s, r, slice, ctx, once, rng, events)
	# N6 (ruling Q8 a): one ON_PERFECT per Perfect needle of the operative (a NULL landing is
	# no Perfect slice), carrying the landed slice's output (every resolution summed, before
	# absorption).
	if owner == s.player and r["tier"] == RC.PrecisionTier.PERFECT and is_landing(r) and slice.slice_type != RC.SliceType.NULL:
		heard.append({"trigger": RC.Trigger.ON_PERFECT, "tier": r["tier"], "amount": landed_output,
			"slice_id": slice.id, "pointer_index": r["pointer_index"]})
	if stacks_in(r, RC.Status.OVERCLOCKED) > 0 and is_landing(r):
		# N8: the burn-out takes every OVERCLOCKED stack and leaves one CORRUPTED stack.
		wheel.remove_stacks(slot, RC.Status.OVERCLOCKED)
		wheel.add_stacks(slot, RC.Status.CORRUPTED, 1, config.status_stack_cap)
		events.append({"type": "status", "target": owner.id, "slot": slot, "status": RC.Status.CORRUPTED,
			"stacks": wheel.stacks_of(slot, RC.Status.CORRUPTED),
			"text": "%s slot %d burns out: OVERCLOCKED -> CORRUPTED." % [owner.display_name, slot]})


## Stacks of `status` a resolution readout `r` carries (N8; 0 when absent).
static func stacks_in(r: Dictionary, status: int) -> int:
	return int((r.get("stacks", {}) as Dictionary).get(status, 0))


## `tier` lowered one step per TIER_DOWN stack, floored at WEAK (N9, R9).
static func downgraded_tier(tier: int, stacks: int) -> int:
	return maxi(RC.PrecisionTier.WEAK, tier - maxi(0, stacks))


## The output factor of `stacks` OUTPUT_DOWN stacks (N8, R8): the per-stack shares add up
## (one signed sum, ruling Q35 b) and the factor never drops below 0. Two stacks with the
## 0.25 share are the old PARASITE's half output.
static func output_down_factor(stacks: int, cfg: CampaignConfigData) -> float:
	if stacks <= 0:
		return 1.0
	return maxf(0.0, 1.0 - cfg.output_down_per_stack * stacks)


## A slice's output before any multiplier (plan 2 R5): `base_output`, or for a PERCENT
## slice that share of `owner`'s max HP (rounded to nearest, minimum 1).
static func slice_base(owner: CombatantState, slice: SliceData) -> int:
	if slice.amount_mode == RC.AmountMode.PERCENT:
		return EffectInterpreter.percent_of(owner.max_hp, slice.base_output)
	return slice.base_output


## Whether resolution `r` stands for its pointer's landing: the landing itself, or the
## slice a Shunt resolves instead. A Mirror copy of a neighbour is not (Daemons skip it and
## it doesn't resolve the NULL for Cold Exit).
static func is_landing(r: Dictionary) -> bool:
	return not r.get("derived", false) or r.get("landing", false)


## Plan 2 N20: how many hits one resolution of attack `slice` deals to `target` (per target
## needle). `slice.hits`, or with `hits_per_target_status` set, the target wheel's non-NULL
## slices carrying that status (one per slice, not per stack) times `hits_per_status_slice`,
## never below `slice.hits` (the minimum, 1 by default). No cap (ruling Q40). Pure.
func hit_count(slice: SliceData, target: CombatantState) -> int:
	var n := maxi(1, slice.hits)
	if slice.hits_per_target_status == RC.Status.NONE or target == null:
		return n
	var carrying := 0
	for i in target.wheel.slot_slice_ids.size():
		if target.wheel.has_status(i, slice.hits_per_target_status) and fx.slice_of(target.wheel, i).slice_type != RC.SliceType.NULL:
			carrying += 1
	return maxi(n, carrying * slice.hits_per_status_slice)


## ON_SLICE_TRIGGER, then ON_PERFECT on a Perfect and ON_NULL_SLICE on the NULL, for `listeners`.
func _landing_triggers(s: CombatState, r: Dictionary, slice: SliceData, ctx: Dictionary, listeners: Array, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	if listeners.is_empty():
		return
	fx.run_triggers(s, RC.Trigger.ON_SLICE_TRIGGER, ctx, listeners, rng, events)
	if r["tier"] == RC.PrecisionTier.PERFECT:
		fx.run_triggers(s, RC.Trigger.ON_PERFECT, ctx, listeners, rng, events)
	if slice.slice_type == RC.SliceType.NULL:
		fx.run_triggers(s, RC.Trigger.ON_NULL_SLICE, ctx, listeners, rng, events)


func _slice_action(s: CombatState, owner: CombatantState, slice: SliceData, output: int, pierce: bool, ctx: Dictionary, events: Array[Dictionary]) -> void:
	match slice.slice_type:
		RC.SliceType.SHIM, RC.SliceType.OVERFLOW:
			var target: CombatantState = ctx["target"]
			if target == null or not target.is_alive():
				return
			# N20: the hit list is fixed when the slice resolves (the target's statuses now).
			var hits := hit_count(slice, target)
			# N4: the attack line reports the hit as it lands (deal_hit applies the enrage).
			events.append({"type": "attack", "attacker": owner.id, "target": target.id, "amount": EffectInterpreter.enraged(owner, output), "pierce": pierce, "hits": hits,
				"text": "" if quiet else "%s %s for %s at %s." % [owner.display_name, _slice_name(slice), ("%d x %d" % [hits, output]) if hits > 1 else str(output), target.display_name]})
			# N20: every hit runs the whole damage path on its own, hit by hit, each on
			# every needle of the target (pointer index order).
			for h in hits:
				for q in target.wheel.pointer_ticks.size():
					# N14: the target's SANDBOX charge comes before its bodyguard (Pierce too).
					if fx.sandboxed(owner, target, output, events, slice.id):
						continue
					# Bodyguard applies even to Pierce (designer ruling: Pierce ignores block
					# and shield only). The operative's drones guard the operative the same way.
					var victim := target
					var guard := s.satellite_at(target.id, target.wheel.slice_at(q))
					if guard != null:
						victim = guard
						events.append({"type": "bodyguard", "target": target.id, "guard": guard.id, "pointer_index": q,
							"text": "" if quiet else "%s takes the hit for %s (pointer %d)." % [guard.display_name, target.display_name, q]})
					var before := events.size()
					var hp_damage := fx.deal_hit(s, owner, victim, output, pierce, true, events, slice.id)
					# N6: a player-side hit that landed (not negated, not zero) is heard as
					# ON_HIT_DEALT with its HP damage after BLOCK and SHIELD.
					if owner.is_player and ctx.has("heard") and events.size() > before and events[events.size() - 1].get("type") == "damage":
						(ctx["heard"] as Array).append({"trigger": RC.Trigger.ON_HIT_DEALT, "tier": int(ctx.get("tier", RC.PrecisionTier.PERFECT)),
							"amount": hp_damage, "victim": victim, "slice_id": slice.id, "attacker": owner.id})
		RC.SliceType.DEFRAG:
			fx.gain_block(owner, output, events)
		RC.SliceType.SANDBOX:
			fx.gain_shield(owner, output, events)
		RC.SliceType.DETOUR:
			# N14 (ruling Q39): charges by precision, not output.
			var perfect: bool = int(ctx.get("tier", RC.PrecisionTier.GOOD)) == RC.PrecisionTier.PERFECT
			fx.gain_evade(owner, config.sandbox_charges_perfect if perfect else config.sandbox_charges, events)
		RC.SliceType.HOTFIX:
			fx.heal(owner, output, events)
		RC.SliceType.TROJAN:
			_deploy(s, owner, maxi(1, output), int(ctx.get("slice_index", 0)), events)
		RC.SliceType.INFECT:
			events.append({"type": "afflict", "attacker": owner.id, "text": "%s %s." % [owner.display_name, _slice_name(slice)]})
		RC.SliceType.NULL:
			events.append({"type": "null", "owner": owner.id, "text": "%s lands on NULL." % owner.display_name})
		_:
			events.append({"type": "unsupported_slice", "slice_type": slice.slice_type,
				"text": "%s slice type %s is not implemented yet." % [owner.display_name, RC.SliceType.keys()[slice.slice_type]]})


## TROJAN slice (GDD 2.6, 5.2): `count` drones of the Hub's template dock on the wheel,
## from the resolved slice clockwise, up to the Hub's max_drones.
func _deploy(s: CombatState, owner: CombatantState, count: int, from_slot: int, events: Array[Dictionary]) -> void:
	var hub := fx.hub_of(owner.wheel)
	if hub == null or hub.drone == null:
		events.append({"type": "deploy_failed", "text": "%s has no drone template to deploy." % owner.display_name})
		return
	for i in count:
		# One drone per slice (Q10): a Trojan worth N drones docks them on N slices
		# clockwise from its own, each replacing what is there (a swap never hits the cap).
		var slot := posmod(from_slot + i, owner.wheel.slice_count)
		if s.satellites_of(owner.id).size() >= hub.max_drones and s.satellite_at(owner.id, slot) == null:
			events.append({"type": "drone_cap", "text": "%s cannot dock more than %d drone(s)." % [owner.display_name, hub.max_drones]})
			return
		if fx.deploy_drone(s, owner, hub.drone, slot, events) == null:
			return


## Who `owner`'s pointer attacks: the operative's side (operative or drone) hits the
## chosen target; enemies and their satellites hit the operative.
func _pointer_target(s: CombatState, owner: CombatantState) -> CombatantState:
	if owner.is_player:
		var t := s.get_combatant(s.target_id)
		return t if t != null and t.is_alive() else null
	return s.player


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
		var sat := _spawn_satellite(s, host, spawn, rng, events)
		_scale_enemy(sat, host.hp_scale, host.output_scale)
		events.append({"type": "satellite_spawn", "target": host.id, "satellite": sat.id, "slot": sat.dock_slot, "hp": sat.hp,
			"text": "%s launches %s on slot %d." % [host.display_name, sat.display_name, sat.dock_slot]})


## Reports every enemy, satellite or drone that died this resolve (including ones spawned
## during it) exactly once; satellites go down with their host. Dead combatants stay in
## their lists (filtered by is_alive()). Every satellite or drone among them fires
## ON_SATELLITE_DESTROYED (cause killed or cleared); deaths those hooks cause are settled
## in the same call (each combatant is reported once, so the loop ends).
func _apply_deaths(s: CombatState, _alive_before: Array[StringName], rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var destroyed: Array = [null]
	while not destroyed.is_empty():
		destroyed = []
		for e in s.enemies:
			if e.hp <= 0 and not e.is_satellite:
				for sat in s.satellites_of(e.id):
					sat.hp = 0
					events.append({"type": "died", "target": sat.id, "text": "%s goes down with its host." % sat.display_name})
					s.flags["dead:%s" % sat.id] = 1
					destroyed.append([sat, &"cleared"])
		for c in s.enemies + s.drones:
			var key := "dead:%s" % c.id
			if not c.is_alive() and not s.flags.has(key):
				s.flags[key] = 1
				if s.flags.has("replaced:%s" % c.id):
					destroyed.append([c, &"replaced"])  # deploy_drone already reported it
					continue
				events.append({"type": "died", "target": c.id, "text": "%s is destroyed." % c.display_name})
				if c.is_satellite:
					destroyed.append([c, &"killed"])
		for pair in destroyed:
			_fire_satellite_destroyed(s, pair[0], pair[1], rng, events)


## ON_SATELLITE_DESTROYED (designer 2026-10-18, Q7): the operative's listeners (Hub, Daemons)
## hear every destroyed satellite or drone. `cause`: &"killed", &"replaced" or &"cleared".
func _fire_satellite_destroyed(s: CombatState, sat: CombatantState, cause: StringName, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	var ctx := {"owner": s.player, "target": s.get_combatant(s.target_id), "pointer_index": 0,
		"source_id": &"satellite_destroyed", "satellite": sat, "host_id": sat.host_id, "cause": cause}
	fx.run_triggers(s, RC.Trigger.ON_SATELLITE_DESTROYED, ctx, _player_listeners(s), rng, events)


## Enemy phases (GDD 2.11, plan 2 R1/R3): checked at the end of the resolve, when HP stands
## at (or under) the next phase's floor; at most one phase per enemy per resolve (the hit
## that reached the floor parked the rest). MULTIPLY sets the pointer layout at once (minus
## any Breach removal); MIGRATE telegraphs it and the pointers move at the next start of
## turn; ORBIT sets the per-turn drift; wheel and hub overrides swap the layout (statuses
## remapped, R6); cleanse_on_enter clears the stated side; spawns dock satellites. The new
## phase's floor is the one after it (none for the last).
func _check_boss_phases(s: CombatState, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	for e in s.enemies:
		if e.is_satellite or not e.is_alive():
			continue
		var data := lookup.get_content(e.source_id) as EnemyData
		if data == null or e.phase_index >= data.phases.size():
			continue
		var phase := data.phases[e.phase_index]
		if phase == null or e.hp > BossPhaseData.floor_of(e.max_hp, phase.threshold_bp()):
			continue
		e.phase_index += 1
		var upcoming: BossPhaseData = data.phases[e.phase_index] if e.phase_index < data.phases.size() else null
		e.next_threshold_bp = upcoming.threshold_bp() if upcoming != null else 0
		match phase.pointer_behavior:
			RC.PointerBehavior.MULTIPLY:
				e.wheel.pointer_ticks = phase_layout(s, data, phase.pointer_ticks)
				e.wheel.pointer_orbit = 0  # a new fixed layout locks on (H16)
			RC.PointerBehavior.MIGRATE:
				e.wheel.pending_pointer_ticks = phase_layout(s, data, phase.pointer_ticks)
				e.wheel.pointer_orbit = 0
				events.append({"type": "boss_migrate_telegraph", "target": e.id, "ticks": Array(e.wheel.pending_pointer_ticks),
					"text": "%s's pointers flicker: next turn they migrate to %s." % [e.display_name, str(Array(e.wheel.pending_pointer_ticks))]})
			RC.PointerBehavior.ORBIT:
				# A phase that lists pointers sets them before they start orbiting.
				if not phase.pointer_ticks.is_empty():
					e.wheel.pointer_ticks = phase_layout(s, data, phase.pointer_ticks)
				e.wheel.pointer_orbit = phase.orbit_ticks_per_turn
		if phase.wheel_override != null:
			_apply_wheel_override(e, phase.wheel_override, events, int(s.flags.get("enemy_resistance", 0)))
		if phase.hub_override != null:
			e.wheel.hub_id = phase.hub_override.id
			e.hub_resistance = phase.hub_override.hub_resistance
		_cleanse_on_enter(s, e, phase.cleanse_on_enter, events)
		# The facts the replay shows (ANIM-R1): who docked (with the HP they start on) and
		# the needles the phase left.
		var spawned: Array = []
		for spawn in phase.spawns:
			if spawn != null and spawn.satellite != null:
				for k in spawn.max_active:
					var sat := _spawn_satellite(s, e, spawn, rng, events)
					_scale_enemy(sat, e.hp_scale, e.output_scale)
					spawned.append({"id": sat.id, "hp": sat.hp, "slot": sat.dock_slot})
		events.append({"type": "boss_phase", "target": e.id, "phase": e.phase_index, "behavior": phase.pointer_behavior,
			"spawned": spawned, "ticks": Array(e.wheel.pointer_ticks), "floor": e.hp_floor(),
			"text": "%s enters phase %d (%s)%s" % [e.display_name, e.phase_index, RC.PointerBehavior.keys()[phase.pointer_behavior],
				(": " + phase.phase_line) if phase.phase_line != "" else "."]})


## R6: a phase's cleanse_on_enter clears every temporary status of the stated side, after
## the remap. OWN = `e` and the satellites docked on it; PLAYER = the operative and its
## drones; BOTH = both; NONE = nothing (the default, Q31).
func _cleanse_on_enter(s: CombatState, e: CombatantState, scope: int, events: Array[Dictionary]) -> void:
	var sides: Array[CombatantState] = []
	if scope == RC.CleanseScope.OWN or scope == RC.CleanseScope.BOTH:
		sides.append(e)
		sides.append_array(s.satellites_of(e.id))
	if scope == RC.CleanseScope.PLAYER or scope == RC.CleanseScope.BOTH:
		sides.append(s.player)
		sides.append_array(s.drones)
	for c in sides:
		if c == null or c.wheel == null:
			continue
		for slot in c.wheel.slice_stacks.size():
			if c.wheel.has_any_status(slot):
				fx.cleanse(c, slot, events)


## Swaps the boss's slices, Firmware and passive resistance for the phase layout. The
## rotation, pointers and any pending migration are kept; statuses stay, each moved to the
## new slice covering its old slice's centre tick (plan 2 R6, WheelState.remap_stacks: N8 stacks merge).
func _apply_wheel_override(e: CombatantState, data: WheelData, events: Array[Dictionary], bonus_resistance: int = 0) -> void:
	var fresh := WheelState.from_wheel_data(data)
	var w := e.wheel
	var kept := WheelState.remap_stacks_sized(w.slice_stacks, w.layout(), fresh.layout(), config.status_stack_cap)
	w.slice_count = fresh.slice_count
	w.slot_sizes = fresh.slot_sizes  # N12: the phase layout's own slot sizes and quality maps
	w.slot_quality = fresh.slot_quality
	w.slot_slice_ids = fresh.slot_slice_ids
	w.slot_firmware_ids = fresh.slot_firmware_ids
	w.slice_stacks = kept
	w.passive_resistance = fresh.passive_resistance + bonus_resistance  # ICE / Heat resistance stays
	if data.hub != null:
		w.hub_id = data.hub.id
		e.hub_resistance = data.hub.hub_resistance
	if fresh.has_inner_ring():
		w.ring_segment_ids = fresh.ring_segment_ids
	events.append({"type": "boss_wheel_override", "target": e.id, "slices": Array(w.slot_slice_ids),
		"text": "%s's wheel reconfigures: %s." % [e.display_name, ", ".join(w.slot_slice_ids)]})


func _check_outcome(s: CombatState, events: Array[Dictionary]) -> void:
	if s.player.hp <= 0 or s.living_enemies(false).is_empty():
		for c in s.combatants_in_order():
			if c.wheel != null:
				c.wheel.clear_locks()  # N7: nothing leaks past the combat
		s.pending_locks.clear()
	if s.player.hp <= 0:
		s.outcome = CombatState.Outcome.DEFEAT
		s.phase = CombatState.Phase.END_COMBAT
		# W3B B5: both sides at 0 is a DEFEAT (the operative is checked first; the GDD is silent, DECISIONS W3B-FLOW);
		# the event says so, so a DELETED enemy beside a flatline reads as the rule, not a miscount.
		if s.living_enemies(false).is_empty():
			events.append({"type": "combat_end", "outcome": s.outcome, "mutual_zero": true,
				"text": "DEFEAT: both sides reached zero; the operative is flatlined, so it counts as a loss."})
		else:
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


## Docks a satellite of `spawn` on `host`: its fixed dock_slot, else a random free slot
## (slot 0 when none is free). Max 1 satellite per slice (designer 2026-10-18, Q10): one
## already there is destroyed first (cause replaced, fires ON_SATELLITE_DESTROYED).
func _spawn_satellite(s: CombatState, host: CombatantState, spawn: SatelliteSpawnData, rng: RandomNumberGenerator, events: Array[Dictionary]) -> CombatantState:
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
	var old := s.satellite_at(host.id, sat.dock_slot)
	if old != null:
		old.hp = 0
		s.flags["dead:%s" % old.id] = 1
		events.append({"type": "died", "target": old.id, "cause": "replaced",
			"text": "%s is replaced on slot %d." % [old.display_name, sat.dock_slot]})
		_fire_satellite_destroyed(s, old, &"replaced", rng, events)
	s.enemies.append(sat)
	return sat


static func _slice_name(slice: SliceData) -> String:
	return slice.display_name if slice.display_name != "" else String(slice.id)
