class_name EffectInterpreter
extends RefCounted
## Turns EffectData into state changes (TECH_SPEC 5.5) and owns every primitive
## mutation the resolver shares: hits, statuses, nudges, spins, flips, respins.
## Pure: it only touches the CombatState it is handed. Randomness comes from the
## RandomNumberGenerator parameter.
##
## Context dictionary keys (all optional unless noted):
##   owner (CombatantState, required) - who the effect belongs to
##   target (CombatantState) - the wheel/combatant the effect is aimed at
##   pointer_index (int) - pointer of `target` for UNDER_POINTER picks (default 0)
##   tier (int) - precision tier of the triggering slice
##   source_id (StringName) - content id of the card/slice/etc. for logs and limits
##   action (CombatAction) - the player input, for chosen slices/rings/directions
##   spin_bonus (int) - added to SPIN amounts (Breaker hub passive)
##   is_card (bool) - the effect comes from a played card (Accelerator doubles nudges)
##   drone_id (StringName) - drone template for DEPLOY_DRONE instead of the Hub's

var config: CampaignConfigData
var lookup: ContentLookup


func _init(p_config: CampaignConfigData, p_lookup: ContentLookup) -> void:
	config = p_config
	lookup = p_lookup


# --- Content helpers -------------------------------------------------------------

func slice_of(wheel: WheelState, slot: int) -> SliceData:
	return lookup.get_content(wheel.slot_slice_ids[slot]) as SliceData


func firmware_of(wheel: WheelState, slot: int) -> FirmwareData:
	var id := wheel.slot_firmware_ids[slot]
	return (lookup.get_content(id) as FirmwareData) if id != &"" else null


func hub_of(wheel: WheelState) -> HubCoreData:
	return (lookup.get_content(wheel.hub_id) as HubCoreData) if wheel.hub_id != &"" else null


func segment_of(wheel: WheelState, segment_index: int) -> RingSegmentData:
	if not wheel.has_inner_ring():
		return null
	var id := wheel.ring_segment_ids[segment_index]
	return (lookup.get_content(id) as RingSegmentData) if id != &"" else null


func class_of(state: CombatState) -> ClassData:
	return lookup.get_content(state.player.source_id) as ClassData


## Spin bonus a combatant's hub grants to cards (PASSIVE trigger, SPIN effect).
func spin_bonus_of(c: CombatantState) -> int:
	var hub := hub_of(c.wheel)
	if hub == null or c.is_hub_breached():
		return 0
	var bonus := 0
	for te in hub.passive_effects:
		if te == null or te.trigger != RC.Trigger.PASSIVE:
			continue
		for e in te.effects:
			if e != null and e.type == RC.EffectType.SPIN:
				bonus += e.amount
	return bonus


## Permanent status from Firmware in `slot`, or NONE.
func permanent_status(wheel: WheelState, slot: int) -> int:
	var fw := firmware_of(wheel, slot)
	return fw.permanent_status if fw != null else RC.Status.NONE


# --- Effect dispatch -------------------------------------------------------------

## Applies one effect. Returns false when the effect could not apply (blocked or
## unsupported); an event explains why.
func apply_effect(state: CombatState, e: EffectData, ctx: Dictionary, rng: RandomNumberGenerator, events: Array[Dictionary]) -> bool:
	var owner: CombatantState = ctx["owner"]
	var targets := _targets_of(state, e.target, ctx)
	match e.type:
		RC.EffectType.DEAL_DAMAGE:
			for t in targets:
				deal_hit(state, owner, t, _scaled(e.amount, e.multiplier), false, false, events, ctx.get("source_id", &""))
		RC.EffectType.GAIN_BLOCK:
			for t in targets:
				gain_block(t, _scaled(e.amount, e.multiplier), events)
		RC.EffectType.GAIN_SHIELD:
			for t in targets:
				gain_shield(t, _scaled(e.amount, e.multiplier), events)
		RC.EffectType.EVADE:
			for t in targets:
				gain_evade(t, maxi(1, e.amount), events)
		RC.EffectType.HEAL:
			for t in targets:
				heal(t, _scaled(e.amount, e.multiplier), events)
		RC.EffectType.APPLY_STATUS:
			for t in targets:
				var slot := pick_slot(state, t, e.slice_pick, ctx, rng)
				if slot >= 0:
					apply_status(t, slot, e.status, events)
		RC.EffectType.CLEANSE:
			for t in targets:
				var slot := pick_slot(state, t, e.slice_pick, ctx, rng)
				if slot >= 0:
					cleanse(t, slot, events)
		RC.EffectType.NUDGE:
			var action: CombatAction = ctx.get("action")
			var ring: int = e.ring_scope
			var direction: int = 1
			if action != null:
				direction = action.direction
				if action.ring == RC.RingScope.INNER or action.ring == RC.RingScope.OUTER:
					ring = action.ring
			# Convention: a NUDGE effect with multiplier 0.0 ignores resistance (Jam).
			# Accelerator segment (GDD 6.4): nudge cards resolve twice this turn.
			var repeat := 1
			if state.double_nudge_cards and bool(ctx.get("is_card", false)):
				repeat = 2
				events.append({"type": "accelerator", "text": "Accelerator: the nudge card resolves twice."})
			for t in targets:
				for i in maxi(1, e.amount) * repeat:
					nudge(state, owner, t, ring, direction, e.multiplier == 0.0, events)
		RC.EffectType.SPIN:
			var amount: int = e.amount
			if amount != 0:
				amount += signi(amount) * int(ctx.get("spin_bonus", 0))
			for t in targets:
				spin(state, owner, t, amount, events)
		RC.EffectType.FLIP:
			var flipped_any := false
			for t in targets:
				flipped_any = flip(state, t, events) or flipped_any
			return flipped_any
		RC.EffectType.RESPIN:
			var respun := false
			for t in targets:
				respun = respin(t, rng, events, false) or respun
			return respun
		RC.EffectType.FREEZE:
			for t in targets:
				if t.wheel.respin_skipped:
					events.append({"type": "freeze_blocked", "target": t.id, "text": "%s skipped its respin this turn: it cannot be frozen again yet." % t.display_name})
					continue
				t.wheel.frozen = true
				events.append({"type": "freeze", "target": t.id, "text": "%s is FROZEN: it skips its next respin." % t.display_name})
		RC.EffectType.MODIFY_RESISTANCE:
			for t in targets:
				modify_resistance(t, e.amount, events)
		RC.EffectType.HUB_BREACH:
			for t in targets:
				hub_breach(t, maxi(1, e.amount), events)
		RC.EffectType.GAIN_RAM:
			gain_ram(state, e.amount, events)
		RC.EffectType.DRAIN_RAM:
			for t in targets:
				if t.is_player:
					drain_ram(state, e.amount, events)
		RC.EffectType.SNAP_TO_CENTER:
			for t in targets:
				snap_to_center(t, e.ring_scope, events)
		RC.EffectType.DRAW_CARDS:
			draw_cards(state, e.amount, rng, events)
		RC.EffectType.RETRIGGER:
			pass  # Counted by the resolver before the slice resolves.
		RC.EffectType.DOUBLE_NUDGE_CARDS:
			state.double_nudge_cards_next = true
			events.append({"type": "double_nudge_armed", "text": "Accelerator: nudge cards trigger twice next turn."})
		RC.EffectType.DEPLOY_DRONE:
			var template: EnemyData = null
			var drone_id := StringName(String(ctx.get("drone_id", "")))
			if drone_id != &"":
				template = lookup.get_content(drone_id) as EnemyData
			else:
				var hub := hub_of(owner.wheel)
				template = hub.drone if hub != null else null
			if template == null:
				events.append({"type": "deploy_failed", "text": "%s has no drone template to deploy." % owner.display_name})
				return false
			var cap: int = int(ctx.get("drone_cap", -1))
			if cap < 0:
				var hub2 := hub_of(owner.wheel)
				cap = hub2.max_drones if hub2 != null else 0
			var deployed := 0
			for i in maxi(1, e.amount):
				if state.satellites_of(owner.id).size() >= cap:
					events.append({"type": "drone_cap", "text": "%s cannot dock more than %d drone(s)." % [owner.display_name, cap]})
					break
				var slot := pick_slot(state, owner, e.slice_pick, ctx, rng)
				if deploy_drone(state, owner, template, maxi(0, slot), events) != null:
					deployed += 1
			return deployed > 0
		RC.EffectType.MODIFY_HEAT, RC.EffectType.GAIN_CYCLES, RC.EffectType.GAIN_SCHEMATICS:
			events.append({"type": "campaign_effect", "effect": e.type, "amount": e.amount, "source_id": ctx.get("source_id", &""),
				"text": "%s: %+d (campaign)" % [RC.EffectType.keys()[e.type], e.amount]})
		RC.EffectType.CUSTOM:
			if e.custom_handler == null:
				events.append({"type": "unsupported_effect", "effect": e.type, "text": "CUSTOM effect without a handler."})
				return false
			var handler: Object = e.custom_handler.new()
			var sub := ctx.duplicate()
			sub["effect"] = e
			sub["fx"] = self
			events.append_array(handler.handle(sub, state, rng))
		_:
			events.append({"type": "unsupported_effect", "effect": e.type,
				"text": "Effect %s is not implemented yet." % RC.EffectType.keys()[e.type]})
			return false
	return true


## Runs every TriggeredEffectData in `listeners` whose trigger and conditions match.
## `listeners` is an ordered list of {source_id, effects: Array[TriggeredEffectData],
## handler: Script (optional)}. A handler (rule-breaking Daemon) is called for every
## trigger with the trigger in the context and decides for itself.
func run_triggers(state: CombatState, trigger: int, ctx: Dictionary, listeners: Array, rng: RandomNumberGenerator, events: Array[Dictionary]) -> void:
	for listener in listeners:
		var handler_script: Script = listener.get("handler")
		if handler_script != null:
			var sub_h := ctx.duplicate()
			sub_h["trigger"] = trigger
			sub_h["source_id"] = listener["source_id"]
			sub_h["fx"] = self
			events.append_array(handler_script.new().handle(sub_h, state, rng))
		var effects: Array = listener["effects"]
		for i in effects.size():
			var te: TriggeredEffectData = effects[i]
			if te == null or not trigger_matches(state, te, trigger, ctx):
				continue
			var key := "%s:%d" % [listener["source_id"], i]
			if te.limit_per_combat > 0:
				if int(state.per_combat_uses.get(key, 0)) >= te.limit_per_combat:
					continue
				state.per_combat_uses[key] = int(state.per_combat_uses.get(key, 0)) + 1
			var sub := ctx.duplicate()
			sub["source_id"] = listener["source_id"]
			events.append({"type": "trigger", "source_id": listener["source_id"], "trigger": trigger,
				"text": "%s triggers (%s)." % [listener["source_id"], RC.Trigger.keys()[trigger]]})
			for e in te.effects:
				if e != null and e.type != RC.EffectType.RETRIGGER:
					apply_effect(state, e, sub, rng, events)


## Whether `te` fires for `trigger` under `ctx` (tier, consecutive Perfects, limits).
func trigger_matches(state: CombatState, te: TriggeredEffectData, trigger: int, ctx: Dictionary) -> bool:
	if te.trigger != trigger:
		return false
	var tier: int = ctx.get("tier", RC.PrecisionTier.PERFECT)
	if tier < te.min_tier:
		return false
	if te.trigger == RC.Trigger.ON_PERFECT and state.consecutive_perfects < te.consecutive_required:
		return false
	return true


## Extra resolutions granted by RETRIGGER effects in `listeners` for `trigger`.
## Returns one output multiplier per extra resolution.
func retrigger_multipliers(state: CombatState, trigger: int, ctx: Dictionary, listeners: Array) -> Array[float]:
	var out: Array[float] = []
	for listener in listeners:
		var effects: Array = listener["effects"]
		for i in effects.size():
			var te: TriggeredEffectData = effects[i]
			if te == null or not trigger_matches(state, te, trigger, ctx):
				continue
			var key := "%s:%d" % [listener["source_id"], i]
			if te.limit_per_combat > 0 and int(state.per_combat_uses.get(key, 0)) >= te.limit_per_combat:
				continue
			for e in te.effects:
				if e != null and e.type == RC.EffectType.RETRIGGER:
					out.append(e.multiplier)
	return out


# --- Primitive mutations ---------------------------------------------------------

## One hit of `amount` on `victim`. Evade cancels attacks; block then shield absorb
## unless `pierce` (designer ruling: Pierce ignores block and shield, not satellites);
## the rest is HP damage. HP never drops below 0.
func deal_hit(state: CombatState, attacker: CombatantState, victim: CombatantState, amount: int, pierce: bool, is_attack: bool, events: Array[Dictionary], source_id: StringName = &"") -> int:
	if amount <= 0:
		return 0
	if is_attack and victim.evade_charges > 0:
		victim.evade_charges -= 1
		events.append({"type": "evaded", "attacker": attacker.id, "target": victim.id, "amount": amount,
			"text": "%s EVADES %d from %s." % [victim.display_name, amount, attacker.display_name]})
		return 0
	var remaining := amount
	var blocked := 0
	var shielded := 0
	if not pierce:
		blocked = mini(victim.block, remaining)
		victim.block -= blocked
		remaining -= blocked
		shielded = mini(victim.shield, remaining)
		victim.shield -= shielded
		remaining -= shielded
	var hp_damage := mini(victim.hp, remaining)
	victim.hp -= hp_damage
	events.append({"type": "damage", "attacker": attacker.id, "target": victim.id, "amount": amount,
		"blocked": blocked, "shielded": shielded, "hp_damage": hp_damage, "pierce": pierce, "source_id": source_id,
		"text": "%s hits %s for %d%s%s -> %d HP damage (%d HP left)." % [attacker.display_name, victim.display_name, amount,
			" (pierce)" if pierce else "", _absorb_text(blocked, shielded), hp_damage, victim.hp]})
	return hp_damage


func gain_block(c: CombatantState, amount: int, events: Array[Dictionary]) -> void:
	c.block += amount
	events.append({"type": "block", "target": c.id, "amount": amount, "text": "%s gains %d block (%d)." % [c.display_name, amount, c.block]})


func gain_shield(c: CombatantState, amount: int, events: Array[Dictionary]) -> void:
	c.shield = mini(c.shield + amount, config.shield_cap)
	events.append({"type": "shield", "target": c.id, "amount": amount, "text": "%s gains %d shield (%d/%d)." % [c.display_name, amount, c.shield, config.shield_cap]})


func gain_evade(c: CombatantState, charges: int, events: Array[Dictionary]) -> void:
	c.evade_charges += charges
	events.append({"type": "evade", "target": c.id, "amount": charges, "text": "%s will EVADE the next %d attack(s)." % [c.display_name, c.evade_charges]})


func heal(c: CombatantState, amount: int, events: Array[Dictionary]) -> void:
	var healed := mini(amount, c.max_hp - c.hp)
	c.hp += healed
	events.append({"type": "heal", "target": c.id, "amount": healed, "text": "%s heals %d (%d/%d)." % [c.display_name, healed, c.hp, c.max_hp]})


## Applies `status` to slot `slot`. ENCRYPTED (temporary or Hardened) absorbs it.
func apply_status(c: CombatantState, slot: int, status: int, events: Array[Dictionary]) -> bool:
	var wheel := c.wheel
	if permanent_status(wheel, slot) == RC.Status.ENCRYPTED:
		events.append({"type": "status_absorbed", "target": c.id, "slot": slot, "status": status,
			"text": "%s slot %d is Hardened: %s absorbed." % [c.display_name, slot, RC.Status.keys()[status]]})
		return false
	if wheel.slice_statuses[slot] == RC.Status.ENCRYPTED:
		wheel.slice_statuses[slot] = RC.Status.NONE
		events.append({"type": "status_absorbed", "target": c.id, "slot": slot, "status": status,
			"text": "%s slot %d ENCRYPTED absorbs %s." % [c.display_name, slot, RC.Status.keys()[status]]})
		return false
	wheel.slice_statuses[slot] = status
	events.append({"type": "status", "target": c.id, "slot": slot, "status": status,
		"text": "%s slot %d becomes %s." % [c.display_name, slot, RC.Status.keys()[status]]})
	return true


func cleanse(c: CombatantState, slot: int, events: Array[Dictionary]) -> void:
	c.wheel.slice_statuses[slot] = RC.Status.NONE
	events.append({"type": "cleanse", "target": c.id, "slot": slot, "text": "%s slot %d cleansed." % [c.display_name, slot]})


## Picks the slot an effect hits on `c`'s wheel, or -1 when nothing qualifies.
func pick_slot(state: CombatState, c: CombatantState, pick: int, ctx: Dictionary, rng: RandomNumberGenerator) -> int:
	match pick:
		RC.SlicePick.UNDER_POINTER:
			# The target may have fewer pointers than the owner (Corrupt segment on a boss
			# pointer 1 vs. a one-pointer operative): clamp to its last pointer.
			return c.wheel.slice_at(clampi(int(ctx.get("pointer_index", 0)), 0, c.wheel.pointer_ticks.size() - 1))
		RC.SlicePick.RANDOM_NON_MISS:
			var candidates: Array[int] = []
			for i in c.wheel.slot_slice_ids.size():
				if slice_of(c.wheel, i).slice_type != RC.SliceType.MISS and c.wheel.slice_statuses[i] != RC.Status.CORRUPTED:
					candidates.append(i)
			if candidates.is_empty():
				return -1
			return candidates[rng.randi_range(0, candidates.size() - 1)]
		_:
			var action: CombatAction = ctx.get("action")
			if action != null and action.slot_index >= 0 and action.slot_index < c.wheel.slot_slice_ids.size():
				return action.slot_index
			return -1


## Moves one ring of `c`'s wheel by one tick. Enemy resistance absorbs the tick unless
## `ignore_resistance`. Returns true when the wheel moved.
func nudge(state: CombatState, owner: CombatantState, c: CombatantState, ring: int, direction: int, ignore_resistance: bool, events: Array[Dictionary]) -> bool:
	var step := signi(direction)
	if c != owner and not ignore_resistance and c.resistance > 0:
		c.resistance -= 1
		events.append({"type": "nudge_absorbed", "target": c.id, "text": "%s resistance absorbs the nudge (%d left)." % [c.display_name, c.resistance]})
		return false
	if ring == RC.RingScope.INNER:
		if not c.wheel.has_inner_ring():
			events.append({"type": "nudge_failed", "target": c.id, "text": "%s has no inner ring." % c.display_name})
			return false
		c.wheel.inner_rotation += step
	else:
		c.wheel.rotation += step
	events.append({"type": "nudge", "target": c.id, "ring": ring, "direction": step,
		"text": "%s %s ring nudged %s." % [c.display_name, "inner" if ring == RC.RingScope.INNER else "outer", "+1" if step > 0 else "-1"]})
	return true


## Spins the whole wheel (outer + inner) by `amount` ticks (sign = direction). The
## target's resistance absorbs the first ticks. Returns ticks actually moved.
func spin(state: CombatState, owner: CombatantState, c: CombatantState, amount: int, events: Array[Dictionary]) -> int:
	if owner.is_player:
		state.spins_this_turn += 1
	var step := signi(amount)
	var ticks := absi(amount)
	var absorbed := 0
	if c != owner:
		absorbed = mini(c.resistance, ticks)
		c.resistance -= absorbed
	var moved := ticks - absorbed
	c.wheel.rotation += step * moved
	if c.wheel.has_inner_ring() and not (c.is_player and state.ring_locked):
		c.wheel.inner_rotation += step * moved
	events.append({"type": "spin", "target": c.id, "amount": amount, "moved": step * moved, "absorbed": absorbed,
		"text": "%s spins %+d%s." % [c.display_name, step * moved, " (%d absorbed by resistance)" % absorbed if absorbed > 0 else ""]})
	return moved


## Mirrors the wheel (GDD 2.3): the opposite slice arrives at the pointer and slice
## order reverses. Docked satellites ride along to their slice's new slot. Blocked
## entirely while the target has resistance.
func flip(state: CombatState, c: CombatantState, events: Array[Dictionary]) -> bool:
	if c.resistance > 0:
		events.append({"type": "flip_blocked", "target": c.id, "text": "%s resists the FLIP (resistance %d)." % [c.display_name, c.resistance]})
		return false
	c.wheel.flip()
	for sat in state.satellites_of(c.id):
		sat.dock_slot = WheelMath.mirrored_slot(sat.dock_slot, c.wheel.slice_count)
	events.append({"type": "flip", "target": c.id, "tick": c.wheel.tick_at(0),
		"text": "%s wheel FLIPPED (mirrored; pointer now on tick %d)." % [c.display_name, c.wheel.tick_at(0)]})
	return true


## Respins both rings to random ticks (a random event). Blocked by resistance unless
## `force` (start-of-turn respins).
func respin(c: CombatantState, rng: RandomNumberGenerator, events: Array[Dictionary], force: bool) -> bool:
	if not force and c.resistance > 0:
		events.append({"type": "respin_blocked", "target": c.id, "text": "%s resists the RESPIN (resistance %d)." % [c.display_name, c.resistance]})
		return false
	var wheel := c.wheel
	wheel.rotation += 2 * RC.TICKS + rng.randi_range(0, RC.TICKS - 1)
	if wheel.has_inner_ring():
		wheel.inner_rotation += 2 * RC.TICKS + rng.randi_range(0, RC.TICKS - 1)
	events.append({"type": "respin", "target": c.id, "tick": wheel.tick_at(0),
		"text": "%s respins to tick %d." % [c.display_name, wheel.tick_at(0)]})
	return true


func modify_resistance(c: CombatantState, amount: int, events: Array[Dictionary]) -> void:
	c.resistance = maxi(0, c.resistance + amount)
	events.append({"type": "resistance", "target": c.id, "amount": amount, "text": "%s resistance %+d (%d)." % [c.display_name, amount, c.resistance]})


## Disables the hub for `turns` turns: hub resistance leaves the pool at once.
func hub_breach(c: CombatantState, turns: int, events: Array[Dictionary]) -> void:
	if not c.is_hub_breached():
		c.resistance = maxi(0, c.resistance - c.hub_resistance)
	c.hub_breached_turns = maxi(c.hub_breached_turns, turns)
	events.append({"type": "hub_breach", "target": c.id, "text": "%s Hub BREACHED for %d turn(s) (resistance %d)." % [c.display_name, turns, c.resistance]})


func gain_ram(state: CombatState, amount: int, events: Array[Dictionary]) -> void:
	state.ram = mini(state.ram + amount, state.max_ram)
	events.append({"type": "ram", "amount": amount, "text": "RAM %+d (%d)." % [amount, state.ram]})


func drain_ram(state: CombatState, amount: int, events: Array[Dictionary]) -> void:
	var drained := mini(amount, state.ram)
	state.ram -= drained
	events.append({"type": "ram", "amount": -drained, "text": "RAM drained %d (%d)." % [drained, state.ram]})


func snap_to_center(c: CombatantState, ring: int, events: Array[Dictionary]) -> void:
	var wheel := c.wheel
	if ring == RC.RingScope.INNER and wheel.has_inner_ring():
		wheel.inner_rotation += -WheelMath.offset_at(wheel.inner_tick_at(0), RC.RING_SEGMENTS)
	else:
		wheel.rotation += WheelMath.snap_delta(wheel.tick_at(0), wheel.slice_count)
	events.append({"type": "snap", "target": c.id, "text": "%s snaps to the slice centre." % c.display_name})


## Draws up to `count` cards, reshuffling the discard pile in when the draw pile runs
## out (a random event).
func draw_cards(state: CombatState, count: int, rng: RandomNumberGenerator, events: Array[Dictionary]) -> int:
	var drawn := 0
	for i in count:
		if state.draw_pile.is_empty():
			if state.discard_pile.is_empty():
				break
			state.draw_pile = state.discard_pile.duplicate()
			state.discard_pile.clear()
			shuffle(state.draw_pile, rng)
			events.append({"type": "reshuffle", "text": "Discard pile shuffled into the draw pile."})
		state.hand.append(state.draw_pile.pop_back())
		drawn += 1
	if drawn > 0:
		events.append({"type": "draw", "amount": drawn, "text": "Drew %d card(s)." % drawn})
	return drawn


## Builds a combatant from enemy content (enemies, satellites and the operative's drones).
static func make_combatant(data: EnemyData, id: StringName, is_satellite: bool) -> CombatantState:
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


## Docks a drone of `template` on `owner`'s wheel (GDD 5.2): the first free slot from
## `preferred_slot` clockwise. Returns the drone, or null when every slot is taken.
func deploy_drone(state: CombatState, owner: CombatantState, template: EnemyData, preferred_slot: int, events: Array[Dictionary]) -> CombatantState:
	var n := owner.wheel.slice_count
	var slot := -1
	for k in n:
		var candidate := posmod(preferred_slot + k, n)
		if state.satellite_at(owner.id, candidate) == null:
			slot = candidate
			break
	if slot < 0:
		events.append({"type": "deploy_failed", "text": "%s has no free slice for a drone." % owner.display_name})
		return null
	var drone := make_combatant(template, StringName("%s_drone_%d" % [owner.id, state.spawn_counter]), true)
	state.spawn_counter += 1
	drone.is_player = owner.is_player
	drone.host_id = owner.id
	drone.dock_slot = slot
	drone.output_scale = owner.output_scale
	if owner.is_player:
		state.drones.append(drone)
	else:
		state.enemies.append(drone)
	events.append({"type": "deploy", "owner": owner.id, "drone": drone.id, "slot": slot,
		"text": "%s deploys %s on slot %d." % [owner.display_name, drone.display_name, slot]})
	return drone


## Fisher-Yates with the given RNG (never Array.shuffle(), which uses global RNG).
static func shuffle(cards: Array[StringName], rng: RandomNumberGenerator) -> void:
	for i in range(cards.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var tmp := cards[i]
		cards[i] = cards[j]
		cards[j] = tmp


# --- Internals -------------------------------------------------------------------

func _targets_of(state: CombatState, target: int, ctx: Dictionary) -> Array[CombatantState]:
	var owner: CombatantState = ctx["owner"]
	var out: Array[CombatantState] = []
	match target:
		RC.EffectTarget.SELF, RC.EffectTarget.OWN_WHEEL:
			out.append(owner)
		RC.EffectTarget.ALL_ENEMIES:
			if owner.is_player:
				out.append_array(state.living_enemies(true))
			else:
				out.append(state.player)
		RC.EffectTarget.CAMPAIGN:
			pass
		_:
			var t: CombatantState = ctx.get("target")
			if t != null:
				out.append(t)
	return out


static func _scaled(amount: int, multiplier: float) -> int:
	return roundi(amount * multiplier)


static func _absorb_text(blocked: int, shielded: int) -> String:
	var parts := PackedStringArray()
	if blocked > 0:
		parts.append("%d blocked" % blocked)
	if shielded > 0:
		parts.append("%d shielded" % shielded)
	return (", " + ", ".join(parts)) if not parts.is_empty() else ""
