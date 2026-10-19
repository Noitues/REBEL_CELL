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
## See CombatResolver.quiet.
var quiet: bool = false


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
				deal_hit(state, owner, t, damage_amount(e, owner), false, false, events, ctx.get("source_id", &""))
		RC.EffectType.GAIN_BLOCK:
			for t in targets:
				gain_block(t, effect_amount(e, owner), events)
		RC.EffectType.GAIN_SHIELD:
			for t in targets:
				gain_shield(t, effect_amount(e, owner), events)
		RC.EffectType.EVADE:
			for t in targets:
				gain_evade(t, maxi(1, e.amount), events)
		RC.EffectType.HEAL:
			for t in targets:
				heal(t, effect_amount(e, owner), events)
		RC.EffectType.APPLY_STATUS:
			for t in targets:
				for k in status_count(e, t):
					var slot := pick_slot(state, t, e.slice_pick, ctx, rng)
					if slot >= 0 and apply_status(t, slot, e.status, events, e.stacks) and e.slice_pick == RC.SlicePick.RANDOM_NON_NULL:
						events[events.size() - 1]["random"] = true
		RC.EffectType.CLEANSE:
			for t in targets:
				var slot := pick_slot(state, t, e.slice_pick, ctx, rng)
				if slot >= 0:
					cleanse(t, slot, events, e.cleanse_mode)
		RC.EffectType.NUDGE:
			var action: CombatAction = ctx.get("action")
			var direction: int = 1
			if action != null:
				direction = action.direction
			# Convention: a NUDGE effect with multiplier 0.0 ignores resistance (Jam).
			# Accelerator segment (GDD 6.4): nudge cards resolve twice this turn.
			var repeat := 1
			if state.double_nudge_cards and bool(ctx.get("is_card", false)):
				repeat = 2
				events.append({"type": "accelerator", "text": "Accelerator: the nudge card resolves twice."})
			for t in targets:
				var ring := nudge_ring(e, action, t)
				for i in maxi(1, e.amount) * repeat:
					var ignore := e.multiplier == 0.0
					if owner == state.player and bool(ctx.get("is_card", false)):
						ignore = ghost_bypass(state, t, events) or ignore
					nudge(state, owner, t, ring, direction, ignore, events)
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
				modify_resistance(t, e.amount, events, state.phase == CombatState.Phase.RESOLVE)
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
				# A swap on an occupied slice (Q10 replace) never hits the cap. A random pick at
				# the cap stops before drawing (the RNG draws stay as before N13).
				var at_cap := state.satellites_of(owner.id).size() >= cap
				if at_cap and e.slice_pick == RC.SlicePick.RANDOM_NON_NULL:
					events.append({"type": "drone_cap", "text": "%s cannot dock more than %d drone(s)." % [owner.display_name, cap]})
					break
				var slot := pick_slot(state, owner, e.slice_pick, ctx, rng)
				if at_cap and state.satellite_at(owner.id, maxi(0, slot)) == null:
					events.append({"type": "drone_cap", "text": "%s cannot dock more than %d drone(s)." % [owner.display_name, cap]})
					break
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
			sub_h["daemon"] = listener.get("daemon")
			sub_h["fx"] = self
			events.append_array(handler_script.new().handle(sub_h, state, rng))
		var effects: Array = listener["effects"]
		for i in effects.size():
			var te: TriggeredEffectData = effects[i]
			if te == null or not trigger_matches(state, te, trigger, ctx):
				continue
			var key := "%s:%d" % [listener.get("limit_key", listener["source_id"]), i]
			if te.limit_per_combat > 0:
				if int(state.per_combat_uses.get(key, 0)) >= te.limit_per_combat * int(listener.get("limit_scale", 1)):
					continue
				state.per_combat_uses[key] = int(state.per_combat_uses.get(key, 0)) + 1
			var sub := ctx.duplicate()
			sub["source_id"] = listener["source_id"]
			events.append({"type": "trigger", "source_id": listener["source_id"], "trigger": trigger,
				"text": "" if quiet else "%s triggers (%s)." % [listener["source_id"], RC.Trigger.keys()[trigger]]})
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
	if te.trigger == RC.Trigger.ON_PERFECT:
		var owner = ctx.get("owner")
		if owner != null and owner != state.player:
			return te.consecutive_required <= 1  # enemies (Mirrors) keep no Perfect streak
		if state.consecutive_perfects < te.consecutive_required:
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
			var key := "%s:%d" % [listener.get("limit_key", listener["source_id"]), i]
			if te.limit_per_combat > 0 and int(state.per_combat_uses.get(key, 0)) >= te.limit_per_combat * int(listener.get("limit_scale", 1)):
				continue
			for e in te.effects:
				if e != null and e.type == RC.EffectType.RETRIGGER:
					out.append(e.multiplier)
	return out


# --- Primitive mutations ---------------------------------------------------------

## One hit of `amount` on `victim`, in the N14 order: the attacker's enrage, then a SANDBOX
## charge negates the whole hit (any damage source but self-damage: slices, counters,
## listeners; Pierce never touches it, ruling Q39), then block, then shield (both skipped
## by `pierce`), then HP through lose_hp (never below 0 or the phase floor; the event's
## "parked" says what the floor stopped). A bodyguard redirect sits between SANDBOX and
## block: callers that redirect check `sandboxed` on the guarded target first. `_is_attack`
## (a slice hit) no longer changes the rule.
func deal_hit(state: CombatState, attacker: CombatantState, victim: CombatantState, amount: int, pierce: bool, _is_attack: bool, events: Array[Dictionary], source_id: StringName = &"") -> int:
	amount = enraged(attacker, amount)
	if amount <= 0:
		return 0
	if _negate(attacker, victim, amount, events, source_id):
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
	# Pierce skips block and shield, never the phase floor (R3).
	var loss := lose_hp(victim, remaining)
	var hp_damage := loss.x
	events.append({"type": "damage", "attacker": attacker.id, "target": victim.id, "amount": amount,
		"blocked": blocked, "shielded": shielded, "hp_damage": hp_damage, "parked": loss.y, "pierce": pierce, "source_id": source_id,
		"text": "" if quiet else "%s hits %s for %d%s%s -> %d HP damage (%d HP left)." % [attacker.display_name, victim.display_name, amount,
			" (pierce)" if pierce else "", _absorb_text(blocked, shielded), hp_damage, victim.hp]})
	return hp_damage


## N14 (ruling Q39): whether `victim` spends a SANDBOX charge on a hit of `amount` from
## `attacker` (before enrage; the bodyguard step calls this on the guarded target before it
## redirects). A spent charge logs an "evaded" event with "sandboxed": true and 0 HP damage.
func sandboxed(attacker: CombatantState, victim: CombatantState, amount: int, events: Array[Dictionary], source_id: StringName = &"") -> bool:
	var hit := enraged(attacker, amount)
	return hit > 0 and _negate(attacker, victim, hit, events, source_id)


func _negate(attacker: CombatantState, victim: CombatantState, hit: int, events: Array[Dictionary], source_id: StringName) -> bool:
	if victim.evade_charges <= 0 or attacker == victim:
		return false
	victim.evade_charges -= 1
	events.append({"type": "evaded", "sandboxed": true, "attacker": attacker.id, "target": victim.id, "amount": hit,
		"hp_damage": 0, "source_id": source_id, "charges_left": victim.evade_charges,
		"text": "" if quiet else "%s's SANDBOX negates %d from %s (%d charge(s) left)." % [victim.display_name, hit, attacker.display_name, victim.evade_charges]})
	return true


## N4 (plan 2 R4): `amount` as an enemy `attacker`'s hit lands under its enrage (hits only:
## heal, block and shield never read it; the operative's hits never scale). Applied before
## evade, block, shield and the phase clamp.
static func enraged(attacker: CombatantState, amount: int) -> int:
	if attacker == null or attacker.is_player or attacker.enrage_step <= 0:
		return amount
	return EnrageData.scale_hit(amount, attacker.enrage_percent)


## The one clamp every HP-loss path goes through (plan 2 R3): hits (pierce too), self-damage,
## parasites and CORRUPTED bites. Takes up to `amount` HP from `c`, never below 0 and never
## below its phase floor; what the floor stops is parked (lost, not carried). Healing never
## comes here. Returns Vector2i(HP lost, HP parked).
static func lose_hp(c: CombatantState, amount: int) -> Vector2i:
	if amount <= 0:
		return Vector2i.ZERO
	var plain := mini(c.hp, amount)
	var lost := mini(maxi(0, c.hp - c.hp_floor()), amount)
	c.hp -= lost
	return Vector2i(lost, plain - lost)


func gain_block(c: CombatantState, amount: int, events: Array[Dictionary]) -> void:
	c.block += amount
	events.append({"type": "block", "target": c.id, "amount": amount, "text": "" if quiet else "%s gains %d block (%d)." % [c.display_name, amount, c.block]})


func gain_shield(c: CombatantState, amount: int, events: Array[Dictionary]) -> void:
	var before := c.shield
	c.shield = mini(c.shield + amount, config.shield_cap)
	# The shield actually gained (H24: at the cap LAST TURN read "+5 SHIELD" with no gain).
	var gained := c.shield - before
	events.append({"type": "shield", "target": c.id, "amount": gained, "requested": amount, "text": "" if quiet else "%s gains %d shield (%d/%d)." % [c.display_name, gained, c.shield, config.shield_cap]})


func gain_evade(c: CombatantState, charges: int, events: Array[Dictionary]) -> void:
	c.evade_charges += charges
	events.append({"type": "evade", "target": c.id, "amount": charges, "text": "" if quiet else "%s gains %d SANDBOX charge(s) (%d)." % [c.display_name, charges, c.evade_charges]})


func heal(c: CombatantState, amount: int, events: Array[Dictionary]) -> void:
	var healed := mini(amount, c.max_hp - c.hp)
	c.hp += healed
	events.append({"type": "heal", "target": c.id, "amount": healed, "text": "" if quiet else "%s heals %d (%d/%d)." % [c.display_name, healed, c.hp, c.max_hp]})


## Applies `stacks` stacks of `status` to slot `slot` (plan 2 N8): they add to what the slot
## holds, up to config.status_stack_cap (ENCRYPTED and CORRUPTED uncapped). A PARASITE is
## config.parasite_output_down_stacks OUTPUT_DOWN stacks per stack (R8). Hardened (permanent
## ENCRYPTED) absorbs every apply; a temporary ENCRYPTED stack absorbs one apply of any other
## status, whatever its stacks, and is used up (ENCRYPTED on ENCRYPTED adds a stack). Returns
## true when the status landed.
func apply_status(c: CombatantState, slot: int, status: int, events: Array[Dictionary], stacks: int = 1) -> bool:
	var wheel := c.wheel
	if status == RC.Status.PARASITE:
		status = RC.Status.OUTPUT_DOWN
		stacks *= config.parasite_output_down_stacks
	if permanent_status(wheel, slot) == RC.Status.ENCRYPTED:
		events.append({"type": "status_absorbed", "target": c.id, "slot": slot, "status": status,
			"text": "%s slot %d is Hardened: %s absorbed." % [c.display_name, slot, RC.Status.keys()[status]]})
		return false
	if status != RC.Status.ENCRYPTED and wheel.has_status(slot, RC.Status.ENCRYPTED):
		wheel.remove_stacks(slot, RC.Status.ENCRYPTED, 1)
		events.append({"type": "status_absorbed", "target": c.id, "slot": slot, "status": status,
			"text": "%s slot %d ENCRYPTED absorbs %s." % [c.display_name, slot, RC.Status.keys()[status]]})
		return false
	wheel.add_stacks(slot, status, maxi(1, stacks), config.status_stack_cap)
	var now := wheel.stacks_of(slot, status)
	events.append({"type": "status", "target": c.id, "slot": slot, "status": status, "stacks": now,
		"text": "%s slot %d becomes %s%s." % [c.display_name, slot, RC.Status.keys()[status], (" x%d" % now) if now > 1 else ""]})
	return true


## Cleanses slot `slot` (N8): every stack of every status (CleanseMode.ALL, the default), or
## one stack of each status on it (ONE_STACK).
func cleanse(c: CombatantState, slot: int, events: Array[Dictionary], mode: int = RC.CleanseMode.ALL) -> void:
	if mode == RC.CleanseMode.ONE_STACK:
		for st in c.wheel.statuses_at(slot):
			c.wheel.remove_stacks(slot, st, 1)
	else:
		c.wheel.clear_slot(slot)
	events.append({"type": "cleanse", "target": c.id, "slot": slot, "text": "%s slot %d cleansed." % [c.display_name, slot]})


## Picks the slot an effect hits on `c`'s wheel, or -1 when nothing qualifies.
func pick_slot(state: CombatState, c: CombatantState, pick: int, ctx: Dictionary, rng: RandomNumberGenerator) -> int:
	match pick:
		RC.SlicePick.UNDER_POINTER:
			# The target may have fewer pointers than the owner (Corrupt segment on a boss
			# pointer 1 vs. a one-pointer operative): clamp to its last pointer.
			return c.wheel.slice_at(clampi(int(ctx.get("pointer_index", 0)), 0, c.wheel.pointer_ticks.size() - 1))
		RC.SlicePick.RANDOM_NON_NULL:
			var candidates: Array[int] = []
			for i in c.wheel.slot_slice_ids.size():
				if slice_of(c.wheel, i).slice_type != RC.SliceType.NULL and not c.wheel.has_status(i, RC.Status.CORRUPTED):
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
## The ring a card's NUDGE effect moves on `target`: INNER when the card names the inner
## ring; otherwise the ring the player picked (the action's ring), falling back to OUTER
## when the target has no inner ring.
## Ghost Core (GDD 5.2): the first N nudges on enemy wheels each turn, from actions or
## cards, ignore resistance. Uses one of them when `target` is an enemy; true when it
## actually slipped past resistance.
func ghost_bypass(state: CombatState, target: CombatantState, events: Array[Dictionary]) -> bool:
	var hub := hub_of(state.player.wheel)
	if target == null or target == state.player or hub == null or state.player.is_hub_breached() or hub.free_resistance_nudges <= 0:
		return false
	if int(state.flags.get("resist_free_nudges_used", 0)) >= hub.free_resistance_nudges:
		return false
	state.flags["resist_free_nudges_used"] = int(state.flags.get("resist_free_nudges_used", 0)) + 1
	if target.resistance <= 0:
		return false
	events.append({"type": "ghost_nudge", "text": "%s slips the nudge past %s's resistance." % [hub.display_name, target.display_name]})
	return true


static func nudge_ring(e: EffectData, action: CombatAction, target: CombatantState) -> int:
	if e.ring_scope == RC.RingScope.INNER:
		return RC.RingScope.INNER
	if action != null and action.ring == RC.RingScope.INNER and target != null and target.wheel.has_inner_ring():
		return RC.RingScope.INNER
	return RC.RingScope.OUTER


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


## Changes `c`'s resistance now. During RESOLVE the change also carries into the next
## turn's restore (Ghost Core strip, Tracer, an enemy's own +resistance slice), which
## would otherwise wipe it before the player acts.
func modify_resistance(c: CombatantState, amount: int, events: Array[Dictionary], carry: bool = false) -> void:
	c.resistance = maxi(0, c.resistance + amount)
	if carry:
		c.resistance_carry += amount
	events.append({"type": "resistance", "target": c.id, "amount": amount, "text": "%s resistance %+d (%d)." % [c.display_name, amount, c.resistance]})


## Disables the hub for `turns` turns: hub resistance leaves the pool at once.
func hub_breach(c: CombatantState, turns: int, events: Array[Dictionary]) -> void:
	if not c.is_hub_breached():
		c.resistance = maxi(0, c.resistance - c.hub_resistance)
	c.hub_breached_turns = maxi(c.hub_breached_turns, turns)
	events.append({"type": "hub_breach", "target": c.id, "text": "%s hub in LOCKDOWN for %d turn(s) (resistance %d)." % [c.display_name, turns, c.resistance]})


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
	events.append({"type": "snap", "target": c.id, "text": "%s snaps to the slice center." % c.display_name})


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
	# R3: the first phase's threshold is the floor until it is entered.
	if not data.phases.is_empty() and data.phases[0] != null:
		c.next_threshold_bp = data.phases[0].threshold_bp()
	return c


## Docks a drone of `template` on slot `preferred_slot` of `owner`'s wheel (GDD 5.2). Max 1
## drone or satellite per slice (designer 2026-10-18, Q10): one already there is destroyed
## (a `died` event with cause "replaced"; the "replaced:<id>" flag lets the resolver's death
## pass fire ON_SATELLITE_DESTROYED with that cause). Returns the new drone.
func deploy_drone(state: CombatState, owner: CombatantState, template: EnemyData, preferred_slot: int, events: Array[Dictionary]) -> CombatantState:
	var slot := posmod(preferred_slot, owner.wheel.slice_count)
	var old := state.satellite_at(owner.id, slot)
	if old != null:
		old.hp = 0
		state.flags["replaced:%s" % old.id] = 1
		events.append({"type": "died", "target": old.id, "cause": "replaced",
			"text": "%s is replaced on slot %d." % [old.display_name, slot]})
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
	events.append({"type": "deploy", "owner": owner.id, "drone": drone.id, "slot": slot, "hp": drone.hp,
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


## The heal, block or shield `e` yields for `owner` (plan 2 R2, R5). PERCENT: a share of
## the owner's max HP, never rescaled. FLAT: the amount, times the owner's tier damage
## factor (`output_scale`) unless the owner is the operative. `e.multiplier` applies to both.
func effect_amount(e: EffectData, owner: CombatantState) -> int:
	if e.amount_mode == RC.AmountMode.PERCENT:
		return _scaled(percent_of(owner.max_hp, e.amount), e.multiplier)
	var scale := 1.0 if owner.is_player else owner.output_scale
	return _scaled(e.amount, e.multiplier * scale)


## The hit a DEAL_DAMAGE `e` hands to `deal_hit` for `owner` (plan 2 N1b, R2 "tier scales
## enemy hits"): the amount times `e.multiplier`, times the owner's tier damage factor
## (`output_scale`) unless the owner is the operative or one of its drones; rounded as N1.
## This is the tier-factor step of the hit order (tier factor, enrage, SANDBOX, bodyguard,
## BLOCK, SHIELD, HP). Slice hits never come here: `_resolve_pointer` already folds the
## factor into their output, so no hit is scaled twice. A PERCENT amount is never rescaled.
func damage_amount(e: EffectData, owner: CombatantState) -> int:
	var scale := 1.0
	if owner != null and not owner.is_player and e.amount_mode != RC.AmountMode.PERCENT:
		scale = owner.output_scale
	return _scaled(e.amount, e.multiplier * scale)


## How many slices an APPLY_STATUS `e` hits on `t`. Only a CORRUPTED random pick counts:
## FLAT N (0 reads 1, the Virus Exploit's convention) or PERCENT of `t`'s non-NULL slices,
## capped by the slices still eligible (non-NULL, not CORRUPTED). Anything else: 1.
func status_count(e: EffectData, t: CombatantState) -> int:
	if e.status != RC.Status.CORRUPTED or e.slice_pick != RC.SlicePick.RANDOM_NON_NULL:
		return 1
	var non_null := 0
	var eligible := 0
	for i in t.wheel.slot_slice_ids.size():
		if slice_of(t.wheel, i).slice_type == RC.SliceType.NULL:
			continue
		non_null += 1
		if not t.wheel.has_status(i, RC.Status.CORRUPTED):
			eligible += 1
	var wanted := percent_of(non_null, e.amount) if e.amount_mode == RC.AmountMode.PERCENT else maxi(1, e.amount)
	return mini(wanted, eligible)


## `pct` percent of `base`, rounded to nearest (half up), at least 1 when both are
## positive, 0 otherwise (designer ruling Q13, 2026-10-18). Integer arithmetic only.
static func percent_of(base: int, pct: int) -> int:
	if base <= 0 or pct <= 0:
		return 0
	@warning_ignore("integer_division")
	return maxi(1, (base * pct + RC.PERCENT_MAX / 2) / RC.PERCENT_MAX)


static func _scaled(amount: int, multiplier: float) -> int:
	return roundi(amount * multiplier)


static func _absorb_text(blocked: int, shielded: int) -> String:
	var parts := PackedStringArray()
	if blocked > 0:
		parts.append("%d blocked" % blocked)
	if shielded > 0:
		parts.append("%d shielded" % shielded)
	return (", " + ", ".join(parts)) if not parts.is_empty() else ""
