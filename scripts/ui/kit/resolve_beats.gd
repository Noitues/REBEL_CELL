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
## with their host take no damage event). ANIM-R2: a damage beat also carries `raw` (the hit
## before block and shield: amount + soaked), `blocked` and `shielded` (what each soaked).
## ANIM-R4 C6: `side` ("player" for the operative and its drones, "enemy" for the enemies
## and their satellites; "" when the source is unknown) and `wheel_source` (the source is a
## whole wheel, not a drone or satellite) let the schedule play one side's hits after the
## other's; `source_slot` is the slice the resolving needle's own resolution landed on.

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
	"damage": [RC.SliceType.SHIM, RC.SliceType.OVERFLOW], "evaded": [RC.SliceType.SHIM, RC.SliceType.OVERFLOW],
	"block": [RC.SliceType.DEFRAG], "shield": [RC.SliceType.SANDBOX], "evade": [RC.SliceType.DETOUR],
	"heal": [RC.SliceType.HOTFIX], "status": [RC.SliceType.INFECT], "absorbed": [RC.SliceType.INFECT],
}
## Kinds whose actor is the event's target (it acts on itself: its own needle resolves).
const SELF_KINDS: Array[String] = ["block", "shield", "evade", "heal"]
## Event types that name who acts next (the source of the status events after them).
const ACTOR_TYPES := {"attack": "attacker", "afflict": "attacker", "retrigger": "owner", "null": "owner"}


## The beats of `events` applied to `before` (the state the action or SEND IT started
## from). `lookup` (optional) tells an OVERFLOW slice's hit from a plain one.
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
	# ANIM-R4 C6a: the side of a combatant spawned during the resolve (its host's).
	var spawned_side := {}
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
			"host": host, "source_slot": -1, "source_tier": -1, "raw": int(e.get("amount", 0)), "blocked": int(e.get("blocked", 0)),
			"shielded": int(e.get("shielded", 0))}
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
		var resolving := {}
		if phase == "resolve" and KIND_SLICES.has(kind) and b["source"] != &"":
			# ANIM-R4 C6b: the needle's own resolution (a SHUNT / MIRROR neighbour resolves as
			# a second entry under the same needle): its slice is where the hit leaves from.
			resolving = _landing_for(before, landings, used, b["source"], kind, lookup)
			b["pointer_index"] = int(resolving.get("pointer_index", -1))
		if resolving.is_empty() and int(b["pointer_index"]) >= 0 and b["source"] != &"":
			for l in landings.get(b["source"], []):
				if int(l.get("pointer_index", 0)) == int(b["pointer_index"]):
					resolving = l
					break
		if not resolving.is_empty():
			b["source_slot"] = int(resolving.get("slice_index", -1))
			# ANIM-R3 A6c: how well that needle landed (the hit's aim multiplier shows).
			b["source_tier"] = int(resolving.get("tier", -1))
		var src_id := StringName(String(b["source"]))
		if kind == "spawn":
			var hc := before.get_combatant(host)
			spawned_side[target] = "player" if hc != null and hc.is_player else String(spawned_side.get(host, "enemy"))
		elif kind == "phase":
			for sp in e.get("spawned", []):
				spawned_side[StringName(String(sp.get("id", "")))] = "enemy"
		b["side"] = side_of(before, src_id, spawned_side)
		var sc := before.get_combatant(src_id)
		b["wheel_source"] = sc != null and not sc.is_satellite and not before.drones.has(sc)
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


## ANIM-R5 combat 5: the resolve is simultaneous (GDD 2.2): a wheel that goes down this
## SEND IT still acts in it. In the engine's order its HP could reach 0 on screen and then
## its INFECT fly, a dead enemy acting. The replay plays a doomed wheel's own actions (and
## its satellites') of the resolve before the hit that takes its HP to 0, keeping their
## order (each moved beat is marked `same_moment`), and recounts every beat's `hp_after`
## from `before` in the new order. Presentation only: the events and the result are the
## engine's.
static func doomed_first(before: CombatState, beats: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = beats.duplicate()
	for b in beats:
		if b["kind"] != "died" or b["phase"] != "resolve" or not bool(b.get("wheel", false)):
			continue
		var w := StringName(String(b["target"]))
		var fatal := -1
		for k in out.size():
			var f := out[k]
			if f["phase"] == "resolve" and StringName(String(f["target"])) == w and String(f["kind"]) in HP_KINDS and int(f["hp_after"]) == 0:
				fatal = k
				break
		if fatal < 0:
			continue
		var moved: Array[Dictionary] = []
		var kept: Array[Dictionary] = []
		for k in range(fatal + 1, out.size()):
			var m := out[k]
			if m["phase"] == "resolve" and _acts_for(before, StringName(String(m["source"])), w) and not (String(m["kind"]) in ["died", "end", "land", "spawn", "phase"]):
				m["same_moment"] = true
				moved.append(m)
			else:
				kept.append(m)
		if moved.is_empty():
			continue
		var head: Array[Dictionary] = out.slice(0, fatal)
		head.append_array(moved)
		head.append(out[fatal])
		head.append_array(kept)
		out = head
	_recount_hp(before, out)
	return out


## True when `source` is wheel `w` or one of its satellites.
static func _acts_for(before: CombatState, source: StringName, w: StringName) -> bool:
	if source == &"":
		return false
	if source == w:
		return true
	var c := before.get_combatant(source)
	return c != null and c.is_satellite and c.host_id == w


## Sets every beat's `hp_after` again from `before`, in the beats' order (as `build`).
static func _recount_hp(before: CombatState, beats: Array[Dictionary]) -> void:
	var hp := {}
	for c in _everyone(before):
		hp[c.id] = c.hp
	for b in beats:
		var t := StringName(String(b["target"]))
		match String(b["kind"]):
			"damage", "corrupted":
				hp[t] = maxi(0, int(hp.get(t, 0)) - int(b["amount"]))
				b["hp_after"] = hp[t]
			"heal":
				hp[t] = int(hp.get(t, 0)) + int(b["amount"])
				b["hp_after"] = hp[t]
			"died":
				hp[t] = 0
			"spawn":
				hp[t] = int(b["hp_after"])
			"phase":
				for sp in b.get("spawned", []):
					hp[StringName(String(sp.get("id", "")))] = int(sp.get("hp", 0))


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


## True when `b` is a hit (ANIM-R2): a damage or evaded beat from another combatant. A hit
## flies as a projectile from its attacker to its victim, one at a time.
static func is_hit(b: Dictionary) -> bool:
	var src := StringName(String(b.get("source", "")))
	return String(b["kind"]) in ["damage", "evaded"] and src != &"" and src != StringName(String(b.get("target", "")))


## True when `b` flies a projectile (a hit, or a status another combatant puts on a slice).
static func flies(b: Dictionary) -> bool:
	if is_hit(b):
		return true
	var src := StringName(String(b.get("source", "")))
	return String(b["kind"]) in ["status", "absorbed"] and src != &"" and src != StringName(String(b.get("target", "")))


## True when `b` changes an HP by a number the replay shows (damage, heal, corrupted).
static func changes_hp(b: Dictionary) -> bool:
	return String(b["kind"]) in HP_KINDS and int(b["amount"]) > 0 and int(b["hp_after"]) >= 0


## Seconds from `b`'s beat until its HP change has settled on screen (ANIM-R2): the
## projectile's flight to the victim (`impact`, hits only), the soaked part coming off
## (`absorb`, a partly blocked hit) and the number travelling into the HP counter and the
## HP rolling (`settle`). 0 for a beat that changes no HP.
static func settle_after(b: Dictionary, timing: Dictionary) -> float:
	if not changes_hp(b):
		return 0.0
	var t := float(timing.get("settle", 0.0))
	if is_hit(b):
		t += float(timing.get("impact", 0.0))
		if int(b.get("soaked", 0)) > 0:
			t += float(timing.get("absorb", 0.0))
	return t


## Seconds from hit `b`'s launch until its number has entered the victim's HP counter
## (ANIM-R3 A6d: the next hit waits for it): its impact, a partly blocked hit's absorb, the
## number's hold and travel (`timing` "arrive"). A hit that changes no HP: its impact. 0 for
## a beat that doesn't fly.
static func arrive_after(b: Dictionary, timing: Dictionary) -> float:
	if not flies(b):
		return 0.0
	var t := float(timing.get("impact", 0.0))
	if is_hit(b) and changes_hp(b):
		t += float(timing.get("arrive", 0.0))
		if int(b.get("soaked", 0)) > 0:
			t += float(timing.get("absorb", 0.0))
	return t


## When each beat plays (seconds from the start), in beat order and never decreasing:
## the landings together at 0; the landing hold (`lead`, only after landings); then the
## resolve beats one `gap` apart with a gap more at each new pass. ANIM-R2 (`timing`, all
## optional): after a hit (or any beat that flies) the next beat waits `hit_gap`, so two
## projectiles never fly at once; a whole wheel's death waits until the HP change before
## it has settled (settle_after) plus `break_delay`, so its HP is seen at 0; the result
## (`result_at`) comes once every HP change has settled, and holds `hold` seconds before
## the turn start (the spins together, then its other beats). When the fight ends on a
## wheel's death, the result shows `break_delay` before that break (THIS TURN and the
## stamps read before the wheel falls). The gap is `beat_gap`, shrunk so the beats fit
## `budget` beside the lead, the hold, the deaths' waits and, when a turn starts, `tail`
## (the spin to the next landing); the hits' spacing and the HP settling are never
## squeezed and come on top, so a turn with many hits runs longer. Without `timing` a death waits
## `death_lead` after the beat before it (card effects). ANIM-R4 C6a (`timing`
## "side_gap", "attacker_gap"): a projectile from the other side waits until every HP
## change so far has settled (its roll done) and every hit so far has landed, plus
## `side_gap` (the operative's hits land in full, then the enemies' come); a projectile
## from another attacker on the same side (a drone after its wheel, a satellite after its
## host) waits `attacker_gap` after the last one arrived. Returns {times, spin_at,
## result_at, total, gap}.
static func schedule(beats: Array[Dictionary], budget: float, beat_gap: float, tail: float, lead: float = 0.0,
		hold: float = 0.0, death_lead: float = 0.0, timing: Dictionary = {}) -> Dictionary:
	var hit_gap := float(timing.get("hit_gap", 0.0))
	var break_delay := float(timing.get("break_delay", death_lead))
	var slots := 0
	var passes := {}
	var any_land := false
	var has_turn := false
	var deaths := 0
	var ends := false
	for b in beats:
		if b["kind"] == "land":
			any_land = true
			continue
		if b["kind"] == "end":
			ends = true
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
	# The squeezable gap fits the budget beside the lead, the hold, the deaths' waits and the
	# tail, as before ANIM-R2; the hits' spacing and the HP settling come on top.
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
	var settled_at := -1.0
	var prev_flies := false
	var kill_at := -1.0
	var kill_settled := -1.0
	var last_t := 0.0
	# ANIM-R3 A6d: a projectile never launches before the last hit's number has entered its
	# HP counter (never two numbers on their way at once; one HP roll per hit).
	var fly_ready := -INF
	var side_gap := float(timing.get("side_gap", 0.0))
	var attacker_gap := float(timing.get("attacker_gap", 0.0))
	var last_side := ""
	var last_source := ""
	var landed_at := -INF
	for b in beats:
		if b["kind"] == "land":
			times.append(0.0)
			continue
		if b["phase"] == "turn_start" and spin_at < 0.0:
			result_at = maxf(t + gap if started else (lead if any_land else t), settled_at)
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
			t += maxf(gap, hit_gap) if prev_flies else gap
		last_pass = String(b["pass"])
		if b["kind"] == "died" and bool(b.get("wheel", false)):
			if timing.is_empty():
				t += death_lead
			elif settled_at >= 0.0:
				t = maxf(t, settled_at + break_delay)
			if spin_at < 0.0:
				# The last break before the fight ends (another enemy may fall earlier).
				kill_settled = maxf(settled_at, last_t)
				kill_at = t
		if flies(b) and hit_gap > 0.0:
			t = maxf(t, fly_ready)
			var side := String(b.get("side", ""))
			var src := String(b.get("source", ""))
			if last_side != "" and side != "" and side != last_side:
				t = maxf(t, maxf(settled_at, landed_at) + side_gap)
			elif last_source != "" and src != last_source:
				t = maxf(t, fly_ready + attacker_gap)
			fly_ready = maxf(fly_ready, t + maxf(hit_gap, arrive_after(b, timing)))
			landed_at = maxf(landed_at, t + float(timing.get("impact", 0.0)))
			if side != "":
				last_side = side
			last_source = src
		times.append(t)
		if spin_at < 0.0:
			var s := settle_after(b, timing)
			if s > 0.0:
				settled_at = maxf(settled_at, t + s)
		prev_flies = flies(b) and hit_gap > 0.0
		last_t = t
		started = true
	if result_at < 0.0:
		result_at = maxf(t + gap if started else (lead if any_land else t), settled_at)
		if ends and kill_at >= 0.0 and not timing.is_empty():
			# The fight ends on this break: the result reads just before the wheel falls.
			result_at = maxf(kill_settled, kill_at - break_delay)
	var end := maxf(result_at + hold, t)
	if spin_at >= 0.0:
		end = maxf(t, spin_at) + tail
	return {"times": times, "spin_at": spin_at, "result_at": result_at, "total": end, "gap": gap}


## ANIM-R4 C6a: the side `id` fights on: "player" (the operative, its drones), "enemy" (the
## enemies, their satellites), "" when unknown; `spawned` names combatants spawned mid-way.
static func side_of(before: CombatState, id: StringName, spawned: Dictionary = {}) -> String:
	if id == &"":
		return ""
	var c := before.get_combatant(id)
	if c == null:
		return String(spawned.get(id, ""))
	return "player" if c.is_player or before.drones.has(c) else "enemy"


static func _everyone(s: CombatState) -> Array[CombatantState]:
	var out: Array[CombatantState] = [s.player]
	out.append_array(s.enemies)
	out.append_array(s.drones)
	return out


## A hit is a crit when its slice is an OVERFLOW slice or its needle landed Perfect.
static func _is_crit(e: Dictionary, before: CombatState, landings: Dictionary, lookup: ContentLookup) -> bool:
	var src := StringName(String(e.get("source_id", "")))
	if lookup != null and src != &"" and lookup.has(src):
		var slice := lookup.get_content(src) as SliceData
		if slice != null and slice.slice_type == RC.SliceType.OVERFLOW:
			return true
	for l in landings.get(StringName(String(e.get("attacker", ""))), []):
		if int(l.get("tier", -1)) == RC.PrecisionTier.PERFECT:
			var owner := before.get_combatant(StringName(String(e.get("attacker", ""))))
			if owner != null and _slice_type(owner, int(l.get("slice_index", 0)), lookup) in [RC.SliceType.SHIM, RC.SliceType.OVERFLOW]:
				return true
	return false


## Which of `source`'s landings resolves a `kind` beat: the next one (in landing order) on a
## slice of that kind, else the first; the landing's event ({pointer_index, slice_index,
## tier}), {} when it has none. ANIM-R4 C6b: the landing itself, not only its needle (a
## neighbour rule's second resolution under one needle has its own slice).
static func _landing_for(before: CombatState, landings: Dictionary, used: Dictionary, source: StringName, kind: String, lookup: ContentLookup) -> Dictionary:
	var list: Array = landings.get(source, [])
	if list.is_empty():
		return {}
	var owner := before.get_combatant(source)
	var fits: Array = []
	for l in list:
		if owner != null and _slice_type(owner, int(l.get("slice_index", 0)), lookup) in KIND_SLICES[kind]:
			fits.append(l)
	if fits.is_empty():
		return list[0]
	var key := "%s:%s" % [source, kind]
	var n := int(used.get(key, 0))
	used[key] = n + 1
	return fits[n % fits.size()]


static func _slice_type(c: CombatantState, slot: int, lookup: ContentLookup) -> int:
	if lookup == null or slot < 0 or slot >= c.wheel.slot_slice_ids.size():
		return -1
	var slice := lookup.get_content(c.wheel.slot_slice_ids[slot]) as SliceData
	return slice.slice_type if slice != null else -1
