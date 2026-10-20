class_name EventRules
extends RefCounted
## Plan 2 EV-01: the pure rules of the event schema extension (N16 / N17 subset): pending combat
## modifiers, event wheel geometry and nudges, the stake check and the raid modifiers. No Node,
## no RNG here: the one random draw each (wheel start tick, "rumor" roll, common Firmware)
## is made by NetrunSession from the `events` stream and passed in or stored.

## RNG stream of the event draws (the existing `events` stream; no new one).
const STREAM := &"events"


# --- Pending combat modifiers ----------------------------------------------------------

## A pending-modifier entry as the run stores it (JSON-safe), `left` = completed fights to go.
## `drawn_extra` is the escort a random_normal modifier drew (empty otherwise).
static func mods_entry(mods: EventCombatModsData, drawn_extra: StringName = &"") -> Dictionary:
	return {"frozen": mods.enemy_wheel_frozen, "res": mods.enemy_resistance_delta, "hp_pct": mods.enemy_hp_pct,
		"nudges": mods.player_extra_free_nudges, "reveal": mods.reveal_phases, "tier": mods.tier_delta,
		"extra": String(drawn_extra if mods.extra_enemy_random_normal else mods.extra_enemy_id), "left": mods.duration_combats}


## Folds pending entries (and the fight's own mods, if any) into one summary:
## {"frozen", "res", "hp_pct", "nudges", "reveal", "tier", "extras": Array[StringName]}.
static func fold(entries: Array[Dictionary], own: EventCombatModsData = null) -> Dictionary:
	var all: Array[Dictionary] = entries.duplicate()
	if own != null:
		all.append(mods_entry(own))
	var out := {"frozen": false, "res": 0, "hp_pct": 0, "nudges": 0, "reveal": false, "tier": 0, "extras": [] as Array[StringName]}
	for e in all:
		out["frozen"] = out["frozen"] or bool(e.get("frozen", false))
		out["res"] += int(e.get("res", 0))
		out["hp_pct"] += int(e.get("hp_pct", 0))
		out["nudges"] += int(e.get("nudges", 0))
		out["reveal"] = out["reveal"] or bool(e.get("reveal", false))
		out["tier"] += int(e.get("tier", 0))
		if String(e.get("extra", "")) != "":
			(out["extras"] as Array[StringName]).append(StringName(String(e["extra"])))
	return out


## Whether a folded summary changes nothing.
static func fold_is_empty(f: Dictionary) -> bool:
	return not f["frozen"] and f["res"] == 0 and f["hp_pct"] == 0 and f["nudges"] == 0 and not f["reveal"] \
		and f["tier"] == 0 and (f["extras"] as Array).is_empty()


## The CombatResolver override keys for a folded summary at run tier `run_tier`
## (the tier clamped to 1..tier_cap). Empty when the summary changes nothing.
static func combat_overrides(f: Dictionary, run_tier: int, tier_cap: int) -> Dictionary:
	var out := {}
	if f["frozen"]:
		out["event_enemy_frozen"] = true
	if f["res"] != 0:
		out["event_resistance_delta"] = f["res"]
	if f["hp_pct"] != 0:
		out["event_hp_pct"] = f["hp_pct"]
	if f["reveal"]:
		out["reveal_phases"] = true
	if f["tier"] != 0:
		out["tier"] = clampi(run_tier + int(f["tier"]), 1, maxi(1, tier_cap))
	return out


## One completed fight spent: every entry's `left` falls by one; spent entries go.
static func spend(entries: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for e in entries:
		var kept := e.duplicate()
		kept["left"] = int(e.get("left", 1)) - 1
		if kept["left"] > 0:
			out.append(kept)
	return out


## The stake check: true when the operative ends at or above `min_pct` percent of max HP
## (always true with no stake). Integer math, no rounding.
static func stake_held(hp: int, max_hp: int, min_pct: int) -> bool:
	return min_pct <= 0 or hp * 100 >= min_pct * max_hp


# --- Event wheel ----------------------------------------------------------------------

## Index of the slice that holds `tick` (any integer; wraps).
static func slice_index(wheel: EventWheelData, tick: int) -> int:
	var t := posmod(tick, RC.TICKS)
	var start := 0
	for i in wheel.slices.size():
		start += wheel.slices[i].size_ticks
		if t < start:
			return i
	return wheel.slices.size() - 1


## A fresh wheel state for the run: the pointer on `start_tick`, no nudges taken.
static func wheel_open(choice_index: int, start_tick: int) -> Dictionary:
	return {"choice": choice_index, "tick": posmod(start_tick, RC.TICKS), "free_used": 0, "extra_used": 0}


## What nudging by `dir` (-1 or +1) would do now, without doing it:
## {"ok", "why", "tick" (after), "slice" (index after), "free": bool (costs nothing),
## "pay": options as {"hp","heat","cycles"} amounts offered ([] when free)}.
static func nudge_preview(wheel: EventWheelData, state: Dictionary, dir: int) -> Dictionary:
	var out := {"ok": false, "why": "", "tick": int(state["tick"]), "slice": slice_index(wheel, int(state["tick"])), "free": false, "pay": {}}
	if dir != -1 and dir != 1:
		out["why"] = "A nudge is one tick either way."
		return out
	var tick := posmod(int(state["tick"]) + dir, RC.TICKS)
	if int(state["free_used"]) < wheel.free_nudges:
		out["free"] = true
	elif int(state["extra_used"]) < wheel.max_extra_nudges:
		var pay := {}
		if wheel.extra_nudge_hp > 0:
			pay["hp"] = wheel.extra_nudge_hp
		if wheel.extra_nudge_heat > 0:
			pay["heat"] = wheel.extra_nudge_heat
		if wheel.extra_nudge_cycles > 0:
			pay["cycles"] = wheel.extra_nudge_cycles
		out["pay"] = pay
	else:
		out["why"] = "No nudges left."
		return out
	out["ok"] = true
	out["tick"] = tick
	out["slice"] = slice_index(wheel, tick)
	return out


## Free nudges still unspent.
static func free_left(wheel: EventWheelData, state: Dictionary) -> int:
	return maxi(0, wheel.free_nudges - int(state["free_used"]))


## Paid nudges still allowed.
static func extra_left(wheel: EventWheelData, state: Dictionary) -> int:
	return maxi(0, wheel.max_extra_nudges - int(state["extra_used"]))


# --- Raid modifiers -------------------------------------------------------------------

## The pending raid modifier the campaign stores (JSON-safe), the chance already rolled:
## `waves_hit` says whether `extra_waves` applies.
static func raid_entry(mods: EventRaidModsData, waves_hit: bool) -> Dictionary:
	return {"strength_pct": mods.strength_pct, "extra_waves": mods.extra_waves if waves_hit else 0, "scout": mods.scout_bonus}


## Adds `entry` into the campaign's pending raid modifier `into` (a second event stacks).
static func raid_merge(into: Dictionary, entry: Dictionary) -> Dictionary:
	return {"strength_pct": int(into.get("strength_pct", 0)) + int(entry.get("strength_pct", 0)),
		"extra_waves": int(into.get("extra_waves", 0)) + int(entry.get("extra_waves", 0)),
		"scout": bool(into.get("scout", false)) or bool(entry.get("scout", false))}


# --- Venue hosts (RAID_WIN after a won raid, HQ_VIEW at the hub) -------------------------

## Ids of the events of `venue` that corporation `corporation_id` can draw at `tier`, sorted by id.
## An event with no corporation is open to all.
static func venue_pool(lookup: ContentLookup, venue: int, corporation_id: StringName, tier: int) -> Array[StringName]:
	var out: Array[StringName] = []
	for id in lookup.ids_of_class(&"TerminalEventData"):
		var ev := lookup.get_content(id) as TerminalEventData
		if ev.venue == venue and ev.min_tier <= tier and (ev.corporation_id == &"" or ev.corporation_id == corporation_id):
			out.append(id)
	return out


## The weighted draw over `pool` (id order): one `randf` of `rng` (the `events` stream), the same
## arithmetic as the Terminal draw. Empty when the pool is empty (nothing drawn).
static func venue_pick(lookup: ContentLookup, pool: Array[StringName], rng: RandomNumberGenerator) -> StringName:
	if pool.is_empty():
		return &""
	var total := 0.0
	for id in pool:
		total += (lookup.get_content(id) as TerminalEventData).weight
	var roll := rng.randf() * total
	for id in pool:
		roll -= (lookup.get_content(id) as TerminalEventData).weight
		if roll <= 0.0:
			return id
	return pool[pool.size() - 1]


## Whether completing netrun number `runs_completed` owes the HQ an event (every `hq_event_every_runs`-th).
static func hq_event_due(config: CampaignConfigData, runs_completed: int) -> bool:
	return config.hq_event_every_runs > 0 and runs_completed > 0 and runs_completed % config.hq_event_every_runs == 0


## The Cycles a hub event opens with: the campaign's Schematics at the config ratio.
static func purse_for(schematics: int, cycles_per_schematic: int) -> int:
	return maxi(0, schematics) * cycles_per_schematic


## The Schematics a hub event nets from the Cycles it ended with against its purse (whole
## Schematics, rounded down: spending 15 Cycles costs 2, gaining 25 pays 2).
static func purse_schematics_delta(cycles_left: int, purse: int, cycles_per_schematic: int) -> int:
	return floori(float(cycles_left - purse) / float(cycles_per_schematic))
