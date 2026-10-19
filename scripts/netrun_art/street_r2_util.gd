class_name StreetR2Util
extends RefCounted
## Street r2 helpers shared by the twin modules (twin of `tools/netrun_art/r2/canon.py` and of the Python built-ins the rules lean on):
## the canonical text of a product (the parity contract with the Python port), Python's `round`, a stable sort.

const FLOAT_SCALE := 1000000.0
const M64_KEY := "seed"


## Canonical text of `obj` (see `canon.py`): compact JSON, keys sorted by text, ints as ints, floats rounded half up to 1e-6 and written
## fixed with the zeros trimmed to one decimal, a `seed` int as its u64 decimal string; the first `split` levels put one member per line.
static func dumps(obj: Variant, split: int = 2) -> String:
	var out := PackedStringArray()
	_emit(obj, 0, split, "", out)
	out.append("\n")
	return "".join(out)


## SHA-256 (hex) of the one-line canonical text of `obj`.
static func digest(obj: Variant) -> String:
	return dumps(obj, 0).sha256_text()


## Fixed 1e-6 text of a float (zeros trimmed to one decimal, `0.0` for -0.0).
static func fmt_float(x: float) -> String:
	var s := "%.6f" % (floorf(x * FLOAT_SCALE + 0.5) / FLOAT_SCALE)
	s = s.rstrip("0")
	if s.ends_with("."):
		s += "0"
	if s == "-0.0" or s == "-0.":
		s = "0.0"
	return s


static func _str(s: String) -> String:
	var out := "\""
	for i in s.length():
		var c := s.unicode_at(i)
		match c:
			0x22:
				out += "\\\""
			0x5c:
				out += "\\\\"
			0x0a:
				out += "\\n"
			0x0d:
				out += "\\r"
			0x09:
				out += "\\t"
			0x08:
				out += "\\b"
			0x0c:
				out += "\\f"
			_:
				if c < 0x20:
					out += "\\u%04x" % c
				else:
					out += String.chr(c)
	return out + "\""


static func _emit(v: Variant, depth: int, split: int, key: String, out: PackedStringArray) -> void:
	match typeof(v):
		TYPE_NIL:
			out.append("null")
		TYPE_BOOL:
			out.append("true" if v else "false")
		TYPE_INT:
			out.append("\"" + ArtSeed.u64_str(v) + "\"" if key == M64_KEY else str(v))
		TYPE_FLOAT:
			out.append(fmt_float(v))
		TYPE_STRING, TYPE_STRING_NAME:
			out.append(_str(String(v)))
		TYPE_ARRAY, TYPE_PACKED_FLOAT64_ARRAY, TYPE_PACKED_INT64_ARRAY, TYPE_PACKED_STRING_ARRAY:
			var arr: Array = v if v is Array else Array(v)
			if arr.is_empty():
				out.append("[]")
				return
			var lines := depth < split
			out.append("[\n" if lines else "[")
			for i in arr.size():
				_emit(arr[i], depth + 1, split, key, out)
				if i < arr.size() - 1:
					out.append(",\n" if lines else ",")
			out.append("\n]" if lines else "]")
		TYPE_DICTIONARY:
			var d: Dictionary = v
			if d.is_empty():
				out.append("{}")
				return
			var keys: Array = d.keys()
			IdSort.sort_ids(keys)
			var lines := depth < split
			out.append("{\n" if lines else "{")
			for i in keys.size():
				out.append(_str(String(keys[i])) + ":")
				_emit(d[keys[i]], depth + 1, split, String(keys[i]), out)
				if i < keys.size() - 1:
					out.append(",\n" if lines else ",")
			out.append("\n}" if lines else "}")
		_:
			push_error("StreetR2Util: unsupported value type %s" % type_string(typeof(v)))


## Python `round(x, n)` for the small n the rules use: half to even on the scaled value, then back by one division, so the result is the
## double nearest the decimal (as CPython's).
static func py_round(x: float, n: int) -> float:
	var p := pow(10.0, n)
	return StreetR2Rng.half_even(x * p) / p


## Python `round(x)` (no digits): half to even, as an int.
static func py_round0(x: float) -> int:
	return int(StreetR2Rng.half_even(x))


## A stable sort of `arr` by the strict ordering `less(a, b) -> bool` (Python `sorted`; Array.sort_custom is not stable). Returns a new Array.
static func sorted_by(arr: Array, less: Callable) -> Array:
	var n := arr.size()
	if n < 2:
		return arr.duplicate()
	var mid := n / 2
	var a := sorted_by(arr.slice(0, mid), less)
	var b := sorted_by(arr.slice(mid), less)
	var out: Array = []
	out.resize(n)
	var i := 0
	var j := 0
	var k := 0
	while i < a.size() and j < b.size():
		if less.call(b[j], a[i]):
			out[k] = b[j]
			j += 1
		else:
			out[k] = a[i]
			i += 1
		k += 1
	while i < a.size():
		out[k] = a[i]
		i += 1
		k += 1
	while j < b.size():
		out[k] = b[j]
		j += 1
		k += 1
	return out


## Python's `a < b` on two lists of numbers / strings (element-wise, shorter first): the tuple keys of `sorted`.
static func tuple_less(a: Array, b: Array) -> bool:
	var n := mini(a.size(), b.size())
	for i in n:
		if a[i] < b[i]:
			return true
		if b[i] < a[i]:
			return false
	return a.size() < b.size()


## Python `min(a)` / `max(a)` of a number array.
static func amin(a: Array) -> Variant:
	var m: Variant = a[0]
	for i in range(1, a.size()):
		if a[i] < m:
			m = a[i]
	return m


static func amax(a: Array) -> Variant:
	var m: Variant = a[0]
	for i in range(1, a.size()):
		if m < a[i]:
			m = a[i]
	return m


## The u64 bits of a decimal string (any length up to 20 digits; wraps like the u64 does).
static func u64(s: String) -> int:
	return ArtSeed.u64_from_str(s)
