class_name IdSort
extends RefCounted
## Text-order sorting for ids. Array.sort() on StringName elements orders by interned address,
## not text, so it changes with whatever the process interned earlier. Any sort of an array
## that can hold StringNames goes through here (CLAUDE.md rule 7: ties by content id, text order).


## True when a sorts before b: StringName / String compare by text, everything else by `<`.
static func less(a: Variant, b: Variant) -> bool:
	if (a is StringName or a is String) and (b is StringName or b is String):
		return String(a) < String(b)
	return a < b


## Sorts `arr` in place in text order (ints, floats and vectors keep their natural order).
static func sort_ids(arr: Array) -> void:
	arr.sort_custom(less)
