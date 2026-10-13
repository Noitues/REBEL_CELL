class_name PointerTag
extends RefCounted
## Plan 1 W2-A1: the precision tag on a pointer. One entry per needle, read from the resolver's own
## pointer readouts (`CombatResolver.pointer_readouts`): `tier` (RC.PrecisionTier), `is_null` (the needle
## sits on a NULL slice), and what the needle reads now (`now_tier`, `now_null`). The view draws it
## on the needle; the words are the tier SEND IT will resolve for that needle.

const NULL_WORD := "NULL" # TR
const TIP_HEAD := "PRECISION TAG: how well this needle lands on its slice." # TR
const TIP_NULL := "NULL: the needle sits on a NULL slice, so nothing happens." # TR
const TIP_AFTER_ENEMY := "It shows where the needle lands after this play." # TR
const TIP_AFTER_YOU := "It follows the plays you queue or hover: this is the tier SEND IT resolves." # TR
const TIP_NOW := "Reads %s now." # TR


## The tag model for a wheel: `after` are the readouts of the state the tag forecasts, `now` those of the
## state on screen (same needle order). A missing `after` entry reads as `now`.
static func model(after: Array[Dictionary], now: Array[Dictionary]) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var count := maxi(after.size(), now.size())
	for i in count:
		var a: Dictionary = after[i] if i < after.size() else now[i]
		var n: Dictionary = now[i] if i < now.size() else a
		out.append({"tier": int(a.get("tier", RC.PrecisionTier.GOOD)), "is_null": _is_null(a),
			"now_tier": int(n.get("tier", RC.PrecisionTier.GOOD)), "now_null": _is_null(n)})
	return out


static func _is_null(readout: Dictionary) -> bool:
	var slice := readout.get("slice") as SliceData
	return slice != null and slice.slice_type == RC.SliceType.NULL


## The one word a tag says for a tier ("NULL" on a NULL slice).
static func word(tier: int, is_null: bool) -> String:
	if is_null:
		return String(TranslationServer.translate(NULL_WORD))
	return String(TranslationServer.translate(String(Palette.TIER_NAMES.get(tier, ""))))


## The text on the tag: the word, and "NOW > AFTER" when the forecast moves the needle's tier.
static func text(tag: Dictionary) -> String:
	var after := word(int(tag["tier"]), bool(tag["is_null"]))
	if changed(tag):
		return "%s → %s" % [word(int(tag["now_tier"]), bool(tag["now_null"])), after]
	return after


## True when the forecast tier differs from what the needle reads now.
static func changed(tag: Dictionary) -> bool:
	return int(tag["tier"]) != int(tag["now_tier"]) or bool(tag["is_null"]) != bool(tag["now_null"])


## The tag's tint (gold PERFECT, white GOOD, amber WEAK, grey NULL); the word carries the meaning too.
static func tint(tag: Dictionary) -> Color:
	if bool(tag["is_null"]):
		return Palette.TEXT_MID
	match int(tag["tier"]):
		RC.PrecisionTier.PERFECT:
			return Palette.RESIST_GOLD
		RC.PrecisionTier.WEAK:
			return Palette.CRT_AMBER
	return Palette.TEXT_HI


## The tag's tooltip: what it is, what each tier does, and whose needle it is.
static func tooltip(tag: Dictionary, own: bool) -> String:
	var tr_ := func(s: String) -> String: return String(TranslationServer.translate(s))
	var lines := PackedStringArray([tr_.call(TIP_HEAD), tr_.call(TIP_AFTER_YOU if own else TIP_AFTER_ENEMY)])
	for t in [RC.PrecisionTier.PERFECT, RC.PrecisionTier.GOOD, RC.PrecisionTier.WEAK]:
		lines.append(tr_.call(Codex.tier_text(t)))
	lines.append(tr_.call(TIP_NULL))
	if changed(tag):
		lines.append(tr_.call(TIP_NOW) % word(int(tag["now_tier"]), bool(tag["now_null"])))
	return "\n".join(lines)
