class_name ForecastTicks
extends RefCounted
## ANIM-R3 A6b (the SEND IT replay keeps its forecast): when each line of a held forecast
## tag ticks. A tag chip names the replay beats that make it happen (`filter`: beat kinds,
## and the source and target they must have); it ticks once the last such beat has landed
## (a hit on impact, an HP change once its number has entered the HP counter), and a chip
## no beat makes (RAM, Heat, odds...) ticks when the result holds. Pure and view-side: it
## reads the beats and their schedule (ResolveBeats), never a rule, so a tick is the
## replay's own event (preview = result).


## A chip's beat filter: beats of `kinds` whose source is `source` and target `target`
## (&"" = any); `settle` waits for an HP change to settle rather than for its impact.
static func filter(kinds: Array, source: StringName = &"", target: StringName = &"", settle: bool = false) -> Dictionary:
	return {"kinds": kinds.duplicate(), "source": source, "target": target, "settle": settle}


## True when beat `b` is one `f` names.
static func matches(f: Dictionary, b: Dictionary) -> bool:
	if not (f.get("kinds", []) as Array).has(String(b["kind"])):
		return false
	var src := StringName(String(f.get("source", "")))
	if src != &"" and StringName(String(b.get("source", ""))) != src:
		return false
	var tgt := StringName(String(f.get("target", "")))
	if tgt != &"" and StringName(String(b.get("target", ""))) != tgt:
		return false
	return true


## Seconds (from the replay's start) at which each chip of `chips` ticks: {chip index:
## seconds}. `times` are the beats' own times (ResolveBeats.schedule), `timing` the replay's
## timing (CombatScene.beat_timing); nothing ticks after `cap` (the result's hold).
static func schedule(chips: Array, beats: Array[Dictionary], times: PackedFloat32Array, timing: Dictionary, cap: float) -> Dictionary:
	var out := {}
	for i in chips.size():
		var chip: Dictionary = chips[i]
		var t := -1.0
		var f: Dictionary = chip.get("beats", {})
		if not f.is_empty():
			for k in beats.size():
				if k >= times.size() or not matches(f, beats[k]):
					continue
				t = maxf(t, times[k] + landed_after(beats[k], timing, bool(f.get("settle", false))))
		out[i] = minf(t, cap) if t >= 0.0 else cap
	return out


## Seconds from beat `b` until what it does is on screen: an HP change once its number has
## entered the counter (`settle`), a hit on impact, anything else at once.
static func landed_after(b: Dictionary, timing: Dictionary, settle: bool) -> float:
	if settle and ResolveBeats.changes_hp(b):
		return ResolveBeats.settle_after(b, timing)
	if ResolveBeats.flies(b):
		return float(timing.get("impact", 0.0))
	return 0.0
