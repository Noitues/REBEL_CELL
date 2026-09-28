class_name ResolveBeats
extends RefCounted
## The beats of a combat replay (Animation pass ANIM-2): what the SEND IT sequence (and a
## card's effect) shows, one beat per engine event worth seeing, in the engine's own event
## order. Built only from the `events` array the engine returned and the state before the
## action (for the landing pointers and the HP it starts from); it never runs a rule, so
## the replay equals the result (GDD 2.10). Pure and view-side: no nodes, no RNG.
##
## A beat: {kind, event_index, phase ("act" / "resolve" / "turn_start"), pass
## ("defensive" / "offensive" / "statuses" / ""), source (id whose needle resolves, or
## &""), pointer_index, target, amount, crit, hp_after (target's HP once this beat lands,
## -1 when it doesn't change), slot, status, tier, soaked, source_slot (the slice the
## resolving needle landed on, -1 when unknown)}. ANIM-R1: "spawn" beats (a satellite
## launched or a drone deployed: target = the newcomer, host = where it docks, hp_after =
## the HP it starts on, from the event) and "phase" beats (a boss enters a phase: spawned
## = [{id, hp, slot}], ticks = its needles now); "died" sets HP 0 (satellites going down
## with their host take no damage event).

## Event types that become a beat, and the beat kind each makes.
const KINDS := {
	"pointer": "land", "damage": "damage", "evaded": "evaded", "heal": "heal", "block": "block",
	"shield": "shield", "evade": "evade", "corrupted": "corrupted", "status": "status",
	"status_absorbed": "absorbed", "died": "died", "hub_breach": "breach", "respin": "spin",
	"spin": "spin", "nudge": "nudge", "flip": "flip", "snap": "snap", "orbit": "orbit",
	"boss_migrate": "migrate", "ram": "ram", "draw": "draw", "combat_end": "end",
	"satellite_spawn": "spawn", "deploy": "spawn", "boss_phase": "phase",
}
## Beat kinds that change HP (the tests check every one of their events has a beat).
const HP_KINDS: Array[String] = ["damage", "heal", "corrupted"]
## Which slice types resolve each kind (a beat pulses the source's needle on such a slice).
const KIND_SLICES := {
	"damage": [RC.SliceType.ATTACK, RC.SliceType.CRIT], "evaded": [RC.SliceType.ATTACK, RC.SliceType.CRIT],
	"block": [RC.SliceType.DEFEND], "shield": [RC.SliceType.SHIELD], "evade": [RC.SliceType.EVADE],
	"heal": [RC.SliceType.HEAL], "status": [RC.SliceType.AFFLICT], "absorbed": [RC.SliceType.AFFLICT],
}
## Kinds whose actor is the event's target (it acts on itself: its own needle resolves).
const SELF_KINDS: Array[String] = ["block", "shield", "evade", "heal"]
## Event types that name who acts next (the source of the status events after them).
const ACTOR_TYPES := {"attack": "attacker", "afflict": "attacker", "retrigger": "owner", "miss": "owner"}


## The beats of `events` applied to `before` (the state the action or SEND IT started
## from). `lookup` (optional) tells a CRIT slice's hit from a plain one.
static func build(before: CombatState, events: Array[Dictionary], lookup: ContentLookup = null) -> Array[Dictionary]:
	var beats: Array[Dictionary] = []
	var hp := {}
	for c in _everyone(before):
		hp[c.id] = c.hp
	var phase := "act"
	var pass_name := ""
	# The landing needles per owner, and how many of each owner's needles a kind has used.
	var landings := {}
	var used := {}
	var actor: StringName = &""
	for i in events.size():
		var e: Dictionary = events[i]
		var t := String(e.get("type", ""))
		if t == "resolve_start":
			phase = "resolve"
			continue
		if t == "turn_start":
			phase = "turn_start"
			pass_name = ""
			continue
		if t == "pass":
			pass_name = String(e.get("pass", ""))
			continue
		if ACTOR_TYPES.has(t):
			actor = StringName(String(e.get(ACTOR_TYPES[t], "")))
		if not KINDS.has(t):
			continue
		var kind: String = KINDS[t]
		var target := StringName(String(e.get("target", e.get("owner", ""))))
		var host: StringName = &""
		if kind == "spawn":
			# The newcomer is the beat's target; the wheel it docks on is its host.
			host = target
			target = StringName(String(e.get("satellite", e.get("drone", ""))))
		var b := {"kind": kind, "event_index": i, "phase": phase, "pass": pass_name, "source": &"",
			"pointer_index": -1, "target": target, "amount": int(e.get("amount", 0)), "crit": false,
			"hp_after": -1, "slot": int(e.get("slot", e.get("slice_index", -1))), "status": int(e.get("status", 0)),
			"tier": int(e.get("tier", -1)), "soaked": int(e.get("blocked", 0)) + int(e.get("shielded", 0)),
			"host": host, "source_slot": -1}
		match kind:
			"land":
				b["source"] = target
				b["pointer_index"] = int(e.get("pointer_index", 0))
				var list: Array = landings.get(target, [])
				list.append(e)
				landings[target] = list
			"damage", "evaded":
				b["source"] = StringName(String(e.get("attacker", "")))
				b["amount"] = int(e.get("hp_damage", e.get("amount", 0))) if kind == "damage" else int(e.get("amount", 0))
				b["crit"] = _is_crit(e, before, landings, lookup)
			"corrupted":
				b["source"] = target
			"status", "absorbed":
				b["source"] = actor
			_:
				if SELF_KINDS.has(kind):
					b["source"] = target
		if phase == "resolve" and KIND_SLICES.has(kind) and b["source"] != &"":
			b["pointer_index"] = _pointer_for(before, landings, used, b["source"], kind, lookup)
		if int(b["pointer_index"]) >= 0 and b["source"] != &"":
			for l in landings.get(b["source"], []):
				if int(l.get("pointer_index", 0)) == int(b["pointer_index"]):
					b["source_slot"] = int(l.get("slice_index", -1))
					break
		if kind == "spawn":
			hp[target] = int(e.get("hp", 0))
			b["hp_after"] = hp[target]
		elif kind == "phase":
			var spawned: Array = e.get("spawned", [])
			b["spawned"] = spawned
			b["ticks"] = e.get("ticks", [])
			b["behavior"] = int(e.get("behavior", -1))
			b["phase_index"] = int(e.get("phase", 0))
			for sp in spawned:
				hp[StringName(String(sp.get("id", "")))] = int(sp.get("hp", 0))
		elif kind == "died":
			hp[target] = 0
			b["hp_after"] = 0
			# A whole wheel going down (not a satellite or drone): its HP is seen at 0 first.
			var dc := before.get_combatant(target)
			b["wheel"] = dc != null and not dc.is_satellite and not before.drones.has(dc)
		if kind == "damage" or kind == "corrupted":
			hp[target] = maxi(0, int(hp.get(target, 0)) - b["amount"])
			b["hp_after"] = hp[target]
		elif kind == "heal":
			hp[target] = int(hp.get(target, 0)) + b["amount"]
			b["hp_after"] = hp[target]
		beats.append(b)
	return beats


## HP each combatant ends on once every beat has landed (id -> HP), from `before`.
static func final_hp(before: CombatState, beats: Array[Dictionary]) -> Dictionary:
	var hp := {}
	for c in _everyone(before):
		hp[c.id] = c.hp
	for b in beats:
		for sp in b.get("spawned", []):
			hp[StringName(String(sp.get("id", "")))] = int(sp.get("hp", 0))
		if int(b["hp_after"]) >= 0:
			hp[b["target"]] = int(b["hp_after"])
	return hp


## When each beat plays (seconds from the start), in beat order and never decreasing:
## the landings together at 0; the landing hold (`lead`, only after landings); then the
## resolve beats one `gap` apart with a gap more at each new pass (a whole wheel's death
## waits `death_lead` more, so its HP is seen at 0 first); the result (`result_at`) holds
## `hold` seconds; then the turn start (the spins together, then its other beats). The
## gap is `beat_gap`, shrunk so everything fits in `budget` (the lead, the hold, the death
## leads and, when a turn starts, `tail`: the spin to the next landing). Returns {times,
## spin_at, result_at, total, gap}.
static func schedule(beats: Array[Dictionary], budget: float, beat_gap: float, tail: float, lead: float = 0.0,
		hold: float = 0.0, death_lead: float = 0.0) -> Dictionary:
	var slots := 0
	var passes := {}
	var any_land := false
	var has_turn := false
	var deaths := 0
	for b in beats:
		if b["kind"] == "land":
			any_land = true
			continue
		if b["phase"] == "turn_start":
			has_turn = true
			if b["kind"] == "spin":
				continue
		slots += 1
		if b["kind"] == "died" and bool(b.get("wheel", false)):
			deaths += 1
		if String(b["pass"]) != "" and not passes.has(b["pass"]):
			passes[b["pass"]] = true
			slots += 1
	var fixed := hold + death_lead * deaths + (lead if any_land else 0.0) + (tail if has_turn else 0.0)
	var gap := beat_gap
	if slots > 0:
		gap = minf(beat_gap, maxf(0.0, budget - fixed) / float(slots + 1))
	var times := PackedFloat32Array()
	var t := 0.0
	var started := false
	var last_pass := ""
	var spin_at := -1.0
	var result_at := -1.0
	for b in beats:
		if b["kind"] == "land":
			times.append(0.0)
			continue
		if b["phase"] == "turn_start" and spin_at < 0.0:
			result_at = t + gap if started else (lead if any_land else t)
			spin_at = result_at + hold
			t = spin_at
			started = true
		if b["kind"] == "spin" and b["phase"] == "turn_start":
			# Spins start together; one listed after another turn-start beat waits for it.
			times.append(t)
			continue
		if not started:
			t = lead if any_land else 0.0
		else:
			if String(b["pass"]) != last_pass and String(b["pass"]) != "":
				t += gap
			t += gap
		last_pass = String(b["pass"])
		if b["kind"] == "died" and bool(b.get("wheel", false)):
			t += death_lead
		times.append(t)
		started = true
	if result_at < 0.0:
		result_at = t + gap if started else (lead if any_land else t)
	var end := result_at + hold
	if spin_at >= 0.0:
		end = maxf(t, spin_at) + tail
	return {"times": times, "spin_at": spin_at, "result_at": result_at, "total": end, "gap": gap}


static func _everyone(s: CombatState) -> Array[CombatantState]:
	var out: Array[CombatantState] = [s.player]
	out.append_array(s.enemies)
	out.append_array(s.drones)
	return out


## A hit is a crit when its slice is a CRIT slice or its needle landed Perfect.
static func _is_crit(e: Dictionary, before: CombatState, landings: Dictionary, lookup: ContentLookup) -> bool:
	var src := StringName(String(e.get("source_id", "")))
	if lookup != null and src != &"" and lookup.has(src):
		var slice := lookup.get_content(src) as SliceData
		if slice != null and slice.slice_type == RC.SliceType.CRIT:
			return true
	for l in landings.get(StringName(String(e.get("attacker", ""))), []):
		if int(l.get("tier", -1)) == RC.PrecisionTier.PERFECT:
			var owner := before.get_combatant(StringName(String(e.get("attacker", ""))))
			if owner != null and _slice_type(owner, int(l.get("slice_index", 0)), lookup) in [RC.SliceType.ATTACK, RC.SliceType.CRIT]:
				return true
	return false


## Which of `source`'s landing needles resolves a `kind` beat: the next one (in landing
## order) on a slice of that kind, else the first.
static func _pointer_for(before: CombatState, landings: Dictionary, used: Dictionary, source: StringName, kind: String, lookup: ContentLookup) -> int:
	var list: Array = landings.get(source, [])
	if list.is_empty():
		return -1
	var owner := before.get_combatant(source)
	var fits: Array[int] = []
	for l in list:
		if owner != null and _slice_type(owner, int(l.get("slice_index", 0)), lookup) in KIND_SLICES[kind]:
			fits.append(int(l.get("pointer_index", 0)))
	if fits.is_empty():
		return int(list[0].get("pointer_index", 0))
	var key := "%s:%s" % [source, kind]
	var n := int(used.get(key, 0))
	used[key] = n + 1
	return fits[n % fits.size()]


static func _slice_type(c: CombatantState, slot: int, lookup: ContentLookup) -> int:
	if lookup == null or slot < 0 or slot >= c.wheel.slot_slice_ids.size():
		return -1
	var slice := lookup.get_content(c.wheel.slot_slice_ids[slot]) as SliceData
	return slice.slice_type if slice != null else -1
