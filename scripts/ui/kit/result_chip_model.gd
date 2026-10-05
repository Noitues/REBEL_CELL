class_name ResultChipModel
extends RefCounted
## ART-2 2D, D15 (ART_BIBLE v2 §3.1): the result chips beside a wheel's HP: what SEND IT does
## to that wheel if pressed now, in the bible's order:
##   [final damage] (red, boxed)  (N shield) (absorbed, blue)  +N shield (gained, green)
##   +N HP (healed)  −N <icon> (other losses: RAM, Heat)  <status ×N>
## Read from the resolve's own events and the states before and after it (the engine's
## preview: GDD 2.10, the chip is the preview), never from a rule of its own. Pure and
## view-side: nothing here changes state. `parts_sum` lets tests hold a chip row to the real
## resolve (preview == result).

const DAMAGE := &"damage"
const ABSORBED := &"absorbed"
const GAINED := &"gained"
const HEALED := &"healed"
const EVADE := &"evade"
const RAM := &"ram"
const HEAT := &"heat"
const HP_OTHER := &"hp_other"
const STATUS := &"status"
const CLEARS := &"clears"
## A random roll (a random card, a respin): the odds are in the tooltip, never the roll (GDD 2.10).
const ODDS := &"odds"
## The order the chips stand in (D15).
const ORDER: Array[StringName] = [DAMAGE, ABSORBED, GAINED, HEALED, EVADE, RAM, HEAT, HP_OTHER, STATUS, CLEARS, ODDS]


## The chips for combatant `id` between `before` and `after` (the state the resolve leaves),
## from the resolve's `events`. `random_status` (a status a random slice pick will put on it;
## -1 = none) shows as one chip with odds instead of the slot the roll picked (GDD 2.10).
## `heat` is the run's Heat change this turn, already scaled (shown on the operative's row).
## Each chip: {kind, value, icon, good, lethal, status, count, random, beats}.
static func build(before: CombatState, after: CombatState, events: Array[Dictionary], id: StringName,
		random_status: int = -1, heat: int = 0) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var b := before.get_combatant(id)
	if b == null:
		return out
	var a := after.get_combatant(id)
	var sums := sums_for(events, id, b.is_player)
	var hp_after := a.hp if a != null else 0
	var dmg := int(sums["damage"])
	var healed := int(sums["healed"])
	var rest := hp_after - b.hp + dmg - healed
	var lethal := b.is_alive() and (a == null or not a.is_alive())
	if dmg > 0 or lethal:
		out.append({"kind": DAMAGE, "value": dmg, "icon": "", "good": false, "lethal": lethal,
			"beats": ForecastTicks.filter(["damage", "corrupted"], &"", id, true)})
	if int(sums["absorbed"]) > 0:
		out.append({"kind": ABSORBED, "value": int(sums["absorbed"]), "icon": "shield", "good": true,
			"beats": ForecastTicks.filter(["damage"], &"", id)})
	if int(sums["gained"]) > 0:
		out.append({"kind": GAINED, "value": int(sums["gained"]), "icon": "shield", "good": true,
			"beats": ForecastTicks.filter(["block", "shield"], &"", id)})
	if healed > 0:
		out.append({"kind": HEALED, "value": healed, "icon": "hp", "good": true,
			"beats": ForecastTicks.filter(["heal"], &"", id, true)})
	if int(sums["evade"]) > 0:
		out.append({"kind": EVADE, "value": int(sums["evade"]), "icon": "evade", "good": true,
			"beats": ForecastTicks.filter(["evade"], &"", id)})
	if int(sums["ram_lost"]) > 0:
		out.append({"kind": RAM, "value": int(sums["ram_lost"]), "icon": "ram", "good": false,
			"beats": ForecastTicks.filter(["ram"])})
	if b.is_player and heat != 0:
		out.append({"kind": HEAT, "value": heat, "icon": "heat", "good": heat < 0})
	if rest != 0:
		out.append({"kind": HP_OTHER, "value": rest, "icon": "hp", "good": rest > 0})
	if random_status >= 0 and random_status != RC.Status.NONE:
		out.append({"kind": STATUS, "status": random_status, "count": 1, "random": true,
			"good": WheelView.status_good_for_you(random_status, b.is_player),
			"beats": ForecastTicks.filter(["status", "absorbed"], &"", id)})
	elif a != null and a.wheel != null and b.wheel != null:
		var put := {}
		var cleared := {}
		for i in mini(a.wheel.slice_statuses.size(), b.wheel.slice_statuses.size()):
			var was: int = b.wheel.slice_statuses[i]
			var now: int = a.wheel.slice_statuses[i]
			if was == now:
				continue
			if now != RC.Status.NONE:
				put[now] = int(put.get(now, 0)) + 1
			else:
				cleared[was] = int(cleared.get(was, 0)) + 1
		for s in _sorted_keys(put):
			out.append({"kind": STATUS, "status": s, "count": int(put[s]), "random": false,
				"good": WheelView.status_good_for_you(s, b.is_player),
				"beats": ForecastTicks.filter(["status", "absorbed"], &"", id)})
		for s in _sorted_keys(cleared):
			out.append({"kind": CLEARS, "status": s, "count": int(cleared[s]),
				"good": not WheelView.status_good_for_you(s, b.is_player),
				"beats": ForecastTicks.filter(["status", "absorbed"], &"", id)})
	return out


## What `events` do to combatant `id`: {damage (HP its hits and CORRUPTED bites take),
## absorbed (what block and shield soak of its hits), gained (block and shield it gains),
## healed, evade (charges gained), ram_lost (RAM spent or drained, on the operative)}.
static func sums_for(events: Array[Dictionary], id: StringName, is_player: bool) -> Dictionary:
	var s := {"damage": 0, "absorbed": 0, "gained": 0, "healed": 0, "evade": 0, "ram_lost": 0}
	for e in events:
		var t := String(e.get("type", ""))
		var on_me := StringName(String(e.get("target", ""))) == id
		match t:
			"damage":
				if on_me:
					s["damage"] = int(s["damage"]) + int(e.get("hp_damage", 0))
					s["absorbed"] = int(s["absorbed"]) + int(e.get("blocked", 0)) + int(e.get("shielded", 0))
			"corrupted":
				if on_me:
					s["damage"] = int(s["damage"]) + int(e.get("amount", 0))
			"heal":
				if on_me:
					s["healed"] = int(s["healed"]) + int(e.get("amount", 0))
			"block", "shield":
				if on_me and int(e.get("amount", 0)) > 0:
					s["gained"] = int(s["gained"]) + int(e.get("amount", 0))
			"evade":
				if on_me and int(e.get("amount", 0)) > 0:
					s["evade"] = int(s["evade"]) + int(e.get("amount", 0))
			"ram":
				if is_player and int(e.get("amount", 0)) < 0:
					s["ram_lost"] = int(s["ram_lost"]) - int(e.get("amount", 0))
	return s


## The HP change a chip row says: −damage +healed ± the rest (tests: equals the resolve's).
static func hp_change(chips: Array) -> int:
	var n := 0
	for c in chips:
		match StringName(c["kind"]):
			DAMAGE:
				n -= int(c["value"])
			HEALED, HP_OTHER:
				n += int(c["value"])
	return n


## The value of the chip of `kind` (0 when the row has none).
static func value_of(chips: Array, kind: StringName) -> int:
	for c in chips:
		if StringName(c["kind"]) == kind:
			return int(c.get("value", 0))
	return 0


## The chip's short words as drawn (numbers and marks; the icon is drawn beside them).
static func label(c: Dictionary) -> String:
	var v := int(c.get("value", 0))
	match StringName(c["kind"]):
		DAMAGE:
			return "-%d" % v
		ABSORBED:
			return "(%d" % v
		GAINED, HEALED, EVADE:
			return "+%d" % v
		RAM:
			return "-%d" % v
		HEAT, HP_OTHER:
			return ("+%d" % v) if v > 0 else ("%d" % v)
		STATUS:
			return "%s%s" % [Palette.STATUS_GLYPHS.get(int(c["status"]), "?"), "?" if bool(c.get("random", false)) else ("×%d" % int(c["count"]))]
		CLEARS:
			return "×%s" % Palette.STATUS_GLYPHS.get(int(c["status"]), "?")
		ODDS:
			return "?"
	return ""


## The chip in words (its tooltip line and what a screen reader would say), translated.
static func words(c: Dictionary) -> String:
	var v := int(c.get("value", 0))
	match StringName(c["kind"]):
		DAMAGE:
			return (String(TranslationServer.translate("%d HP lost: LETHAL")) % v) if bool(c.get("lethal", false)) else (String(TranslationServer.translate("%d HP lost")) % v)
		ABSORBED:
			return String(TranslationServer.translate("%d absorbed by block and shield")) % v
		GAINED:
			return String(TranslationServer.translate("+%d block and shield gained")) % v
		HEALED:
			return String(TranslationServer.translate("+%d HP healed")) % v
		EVADE:
			return String(TranslationServer.translate("+%d EVADE")) % v
		RAM:
			return String(TranslationServer.translate("%d RAM lost")) % v
		HEAT:
			return String(TranslationServer.translate("HEAT %s")) % (("+%d" % v) if v > 0 else str(v))
		HP_OTHER:
			return String(TranslationServer.translate("HP %s (other effects)")) % (("+%d" % v) if v > 0 else str(v))
		STATUS:
			var w := String(TranslationServer.translate(String(Palette.STATUS_WORDS.get(int(c["status"]), ""))))
			if bool(c.get("random", false)):
				return String(TranslationServer.translate("%s on a random slice")) % w
			return String(TranslationServer.translate("%s on %d slice(s)")) % [w, int(c["count"])]
		CLEARS:
			return String(TranslationServer.translate("CLEARS %s")) % String(TranslationServer.translate(String(Palette.STATUS_WORDS.get(int(c["status"]), ""))))
		ODDS:
			return String(TranslationServer.translate("A random roll: the odds are in the breakdown"))
	return ""


## The chip a random roll shows (its odds go in the breakdown).
static func odds_chip() -> Dictionary:
	return {"kind": ODDS, "value": 0, "icon": "", "good": false}


static func _sorted_keys(d: Dictionary) -> Array:
	var k := d.keys()
	k.sort()
	return k
