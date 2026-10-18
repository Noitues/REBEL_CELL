class_name ArtSeed
extends RefCounted
## NA-02 (netrun-art data contract v1, NA02_FIELDS.md section 7, contract C3): the art seeds.
## art_seed(layout_seed, stream, *keys) = FNV-1a 64 over the UTF-8 of the compact JSON
## `[str(layout_seed as u64), "art/" + stream, *keys]` (ensure_ascii). Pure arithmetic on
## its arguments: no RngService stream is read or advanced, no global RNG is touched, and a
## seed depends only on its inputs (never on call order).
##
## GDScript ints are signed 64-bit; multiply and xor wrap mod 2^64, so the u64 maths is done
## on the signed bit pattern and printed unsigned (`u64_str`) wherever it is stored.

const FNV_OFFSET: int = -3750763034362895579  # 0xcbf29ce484222325 as a signed int64
const FNV_PRIME: int = 0x100000001b3
const SM_GAMMA: int = -7046029254386353131  # 0x9E3779B97F4A7C15
const SM_MUL1: int = -4658895280553007687  # 0xBF58476D1CE4E5B9
const SM_MUL2: int = -7723592293110705685  # 0x94D049BB133111EB
const LOW63: int = 0x7FFFFFFFFFFFFFFF
const HEX := "0123456789abcdef"


## The art seed of (`layout_seed`, `stream`, `keys`) as a signed int holding the u64 bits.
## `layout_seed` is the signed seed (written as its two's-complement u64); `keys` are ints or
## Strings / StringNames only (a float or bool key is refused: push_error, returns 0).
static func derive(layout_seed: int, stream: String, keys: Array = []) -> int:
	var parts := PackedStringArray([json_quote(u64_str(layout_seed)), json_quote("art/" + stream)])
	for k: Variant in keys:
		match typeof(k):
			TYPE_INT:
				parts.append(str(k))
			TYPE_STRING, TYPE_STRING_NAME:
				parts.append(json_quote(String(k)))
			_:
				push_error("ArtSeed: keys are ints or strings only (got %s)." % type_string(typeof(k)))
				return 0
	return fnv1a64(("[" + ",".join(parts) + "]").to_utf8_buffer())


## `derive` printed as the u64 decimal string the contract stores.
static func derive_str(layout_seed: int, stream: String, keys: Array = []) -> String:
	return u64_str(derive(layout_seed, stream, keys))


## FNV-1a 64 of `data` (offset 0xcbf29ce484222325, prime 0x100000001b3), u64 bits.
static func fnv1a64(data: PackedByteArray) -> int:
	var h := FNV_OFFSET
	for b in data:
		h = (h ^ b) * FNV_PRIME
	return h


## The next splitmix64 draw from `state` (contract C3 draws): returns [next_state, value].
static func splitmix64(state: int) -> Array[int]:
	var s := state + SM_GAMMA
	var z := s
	z = (z ^ _shr(z, 30)) * SM_MUL1
	z = (z ^ _shr(z, 27)) * SM_MUL2
	return [s, z ^ _shr(z, 31)]


## A draw `x` (u64 bits) as a float in [0, 1): (x >> 11) * 2^-53.
static func uniform(x: int) -> float:
	return float(_shr(x, 11)) / 9007199254740992.0


## Logical (unsigned) right shift of the u64 bits of `v` by `n` (1..63).
static func _shr(v: int, n: int) -> int:
	return (v >> n) & (LOW63 >> (n - 1))


## The u64 bits of `v` as an unsigned decimal string (two's complement for a negative int).
static func u64_str(v: int) -> String:
	if v >= 0:
		return str(v)
	# floor(u / 10) = floor((u >> 1) / 5); the remainder fits in 0..9.
	var q := _shr(v, 1) / 5
	var r := v - q * 10
	return str(q) + str(r)


## A u64 decimal string (or a signed one, "-1") as the signed int holding its bits.
static func u64_from_str(s: String) -> int:
	var t := s.strip_edges()
	var neg := t.begins_with("-")
	if neg:
		t = t.substr(1)
	var v := 0
	for ch in t:
		v = v * 10 + (ch.unicode_at(0) - 48)
	return -v if neg else v


## `s` as a JSON string literal the way Python's json.dumps(ensure_ascii=True) writes it:
## `"` and `\` escaped, \b \f \n \r \t, other controls and every non-ASCII code point as a
## lowercase \uXXXX (a surrogate pair above U+FFFF).
static func json_quote(s: String) -> String:
	var out := "\""
	for i in s.length():
		var c := s.unicode_at(i)
		match c:
			0x22:
				out += "\\\""
			0x5c:
				out += "\\\\"
			0x08:
				out += "\\b"
			0x0c:
				out += "\\f"
			0x0a:
				out += "\\n"
			0x0d:
				out += "\\r"
			0x09:
				out += "\\t"
			_:
				if c < 0x20 or c > 0x7e and c != 0x7f:
					if c > 0xffff:
						var u := c - 0x10000
						out += _u4(0xd800 + (u >> 10)) + _u4(0xdc00 + (u & 0x3ff))
					else:
						out += _u4(c)
				else:
					out += String.chr(c)
	return out + "\""


static func _u4(c: int) -> String:
	return "\\u" + HEX[(c >> 12) & 15] + HEX[(c >> 8) & 15] + HEX[(c >> 4) & 15] + HEX[c & 15]
