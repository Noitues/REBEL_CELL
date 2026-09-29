class_name RaidBeats
extends RefCounted
## The raid playout's timeline (Animation pass ANIM-5, raid execution): built from a
## resolved raid's events (RaidResolver.resolve / CampaignRules.fight_raid), never from
## the rules. Events are grouped by step as the resolver ran them; inside a step each beat
## takes the resolver's phase order: threats enter, move (or stay held), ICE LOCKs and
## ghosts hold, guns fire (shots one after another), then nodes take damage, are
## Disabled or Seized. The raid's end is its own group (the outcome stamps, the forecast
## resolving). Times are seconds at 1x from the motion table's raw durations; the
## playout divides by Motion.speed (1x / 2x / 4x). Pure: reads events and the motion
## table, writes nothing.

## Phases of a step, in the resolver's order.
const PHASES: Array[String] = ["enter", "move", "hold", "fire", "damage", "end"]
## Which phase each event type plays in (types not listed only log).
const PHASE_OF := {
	"link_altered": "enter", "link_frozen": "enter", "threat_enters": "enter",
	"move": "move", "held": "move",
	"ice_lock": "hold", "station_hold": "hold",
	"shot": "fire", "threat_destroyed": "fire",
	"node_hit": "damage", "home_hit": "damage", "cascade": "damage", "disabled": "damage",
	"seized": "damage", "station_regen": "damage", "home_lost": "damage",
	"raid_end": "end",
}
## The motion entry timing each beat type.
const MOTION_OF := {
	"link_altered": &"route_pulse", "link_frozen": &"ice_lock_ring", "threat_enters": &"node_pop",
	"move": &"raid_move", "held": &"ice_lock_ring",
	"ice_lock": &"ice_lock_ring", "station_hold": &"ice_lock_ring",
	"shot": &"turret_trace", "threat_destroyed": &"raid_hit_effect",
	"node_hit": &"node_damage_number", "home_hit": &"node_damage_number", "cascade": &"node_damage_number",
	"station_regen": &"node_damage_number", "disabled": &"raid_flip", "seized": &"raid_flip", "home_lost": &"raid_flip",
	"raid_end": &"forecast_stamp_resolve",
}
## Shots in one step start `raid_shot_stagger`'s amplitude (a share) of a trace apart (a
## volley reads one by one; ANIM-R6 C4: it was the inline SHOT_STAGGER 0.5). Off, together.
const STAGGER_MOTION := &"raid_shot_stagger"
const GAP_MOTION := &"raid_step_gap"


## Splits `events` into playout groups: group 0 is the setup (step 0: link changes), then
## one group per step, then the end (the raid_end event and everything after the last
## step without a step of its own: step-cap seizures, recalls, the reward, Heat).
static func group(events: Array) -> Array[Array]:
	var by_step := {}
	var max_step := 0
	var tail: Array = []
	var stepped := false
	for e: Dictionary in events:
		var t := String(e.get("type", ""))
		if t == "raid_end" or (stepped and not e.has("step")):
			tail.append(e)
			continue
		var step := int(e.get("step", 0))
		if step > 0:
			stepped = true
		(by_step.get_or_add(step, []) as Array).append(e)
		max_step = maxi(max_step, step)
	var out: Array[Array] = []
	for s in max_step + 1:
		out.append(by_step.get(s, []))
	if not tail.is_empty():
		out.append(tail)
	return out


## The beats of one group: [{"event": Dictionary, "type", "phase", "motion", "t0", "dur"}]
## in event order, `t0` from the group's start (seconds at 1x), plus the group's length.
## Returns {"beats": Array[Dictionary], "seconds": float}.
static func timeline(group_events: Array) -> Dictionary:
	var by_phase := {}
	for e: Dictionary in group_events:
		var phase := String(PHASE_OF.get(String(e.get("type", "")), ""))
		if phase != "":
			(by_phase.get_or_add(phase, []) as Array).append(e)
	var beats: Array[Dictionary] = []
	var cursor := 0.0
	for phase in PHASES:
		if not by_phase.has(phase):
			continue
		var length := 0.0
		var shot_at := cursor
		var trace := raw_seconds(&"turret_trace")
		# ANIM-R1 M4: a shot reads strictly shot, hit, number: the trace flies to its target,
		# the hit lands when it arrives (`raid_hit_effect`), the number rises after the hit;
		# a threat breaks up only once the shot that kills it has hit.
		var hit := raw_seconds(&"raid_hit_effect")
		var stagger := Motion.amplitude(STAGGER_MOTION)
		var shot_end := {}
		for e: Dictionary in by_phase[phase]:
			var t := String(e["type"])
			var motion: StringName = MOTION_OF[t]
			var dur := raw_seconds(motion)
			var t0 := cursor
			if t == "shot":
				t0 = shot_at
				shot_at += trace * stagger
				dur = trace + hit
				shot_end[String(e.get("threat", ""))] = t0 + dur
			elif t == "threat_destroyed":
				t0 = maxf(cursor, float(shot_end.get(String(e.get("threat", "")), shot_at - trace * stagger + trace + hit)))
			beats.append({"event": e, "type": t, "phase": phase, "motion": motion, "t0": t0, "dur": dur})
			length = maxf(length, t0 - cursor + dur)
		cursor += length
	if not beats.is_empty():
		cursor += raw_seconds(GAP_MOTION)
	# Beats keep the events' order (the fire phase already does); sort by start, stable.
	var order: Array[int] = []
	for i in beats.size():
		order.append(i)
	order.sort_custom(func(a: int, b: int) -> bool:
		if not is_equal_approx(float(beats[a]["t0"]), float(beats[b]["t0"])):
			return float(beats[a]["t0"]) < float(beats[b]["t0"])
		return a < b)
	var sorted: Array[Dictionary] = []
	for i in order:
		sorted.append(beats[i])
	return {"beats": sorted, "seconds": cursor}


## ANIM-R1 M4: the Sites a step's fight happens at, for the playout camera: where threats
## enter and move from and to, the guns that fire and where their targets stand (the
## firing defence stays in frame before its shot), and the nodes hit. `threat_sites`: where
## each threat stood before the step (threat id -> Site); moves in the step move them.
## Sorted by id, no repeats. Pure.
static func focus_sites(events: Array, threat_sites: Dictionary) -> Array[StringName]:
	var at := threat_sites.duplicate()
	var out: Array[StringName] = []
	for e: Dictionary in events:
		match String(e.get("type", "")):
			"threat_enters":
				at[String(e["threat"])] = StringName(String(e["site"]))
				_add(out, StringName(String(e["site"])))
			"move":
				_add(out, StringName(String(e["from"])))
				at[String(e["threat"])] = StringName(String(e["to"]))
				_add(out, StringName(String(e["to"])))
			"shot":
				_add(out, StringName(String(e["site"])))
				if at.has(String(e["threat"])):
					_add(out, StringName(String(at[String(e["threat"])])))
			"node_hit", "cascade", "disabled", "seized", "home_hit":
				if e.has("site"):
					_add(out, StringName(String(e["site"])))
	out.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	return out


static func _add(list: Array[StringName], id: StringName) -> void:
	if id != &"" and not list.has(id):
		list.append(id)


## Seconds of `id` at 1x: its delay plus its duration from the motion table. ANIM-R6 C4: a
## switched-off part (UiMotionData.OFF_PARTS: the gap between steps) takes no time.
static func raw_seconds(id: StringName) -> float:
	var e := Motion.entry(id)
	if e == null or Motion.part_off(e):
		return 0.0
	return e.delay + e.duration


## True when an event of type `type` plays as a beat (not only in the log).
static func is_beat(type: String) -> bool:
	return PHASE_OF.has(type)
