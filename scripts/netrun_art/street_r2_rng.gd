class_name StreetR2Rng
extends RefCounted
## Street r2 art streams (twin of `tools/netrun_art/r2/streams.py`): a Python-compatible `random.Random` (Mersenne Twister, seeded by
## an integer the way CPython does) behind the plate's stream keys. The plate's rules (art-pass `r2_rules.rng`) draw from
## `random.Random(fnv64(json.dumps([seed, "art/<stream>", *keys])))`; this class draws the same numbers: `random()`, `randrange`,
## `randint`, `uniform`, `choice`, `choices`, `sample`. Pure arithmetic on its arguments; no RngService stream, no global RNG.
##
## GDScript ints are signed 64-bit: u64 seeds are kept as their two's-complement bits (`ArtSeed.u64_str` prints them unsigned).

const N := 624
const M := 397
const UPPER := 0x80000000
const LOWER := 0x7fffffff
const MATRIX := 0x9908b0df
const MASK32 := 0xFFFFFFFF
const KEY_DECIMALS := 4

static var _base: PackedInt64Array = PackedInt64Array()

var _mt: PackedInt64Array = PackedInt64Array()
var _index: int = 0       # next output word of the current block
var _done: int = 0        # words of the current block already generated (the block is generated lazily, in order)


## `random.Random(seed)` for an int seed given as its u64 bits (a negative int is the bit pattern of a u64).
static func from_seed(seed_bits: int) -> StreetR2Rng:
	var r := StreetR2Rng.new()
	var lo := seed_bits & MASK32
	var hi := (seed_bits >> 32) & MASK32
	r._init_by_array([lo] if hi == 0 else [lo, hi])
	return r


## The stream of (`seed`, `stream_name`, `keys`): `seed` is an int (u64 bits) or a String; keys are ints, Strings or floats.
static func stream(seed: Variant, stream_name: String, keys: Array = []) -> StreetR2Rng:
	return from_seed(art_seed(seed, stream_name, keys))


## The u64 art seed (signed bits) of a stream: FNV-1a 64 of `key_text`.
static func art_seed(seed: Variant, stream_name: String, keys: Array = []) -> int:
	return ArtSeed.fnv1a64(key_text(seed, stream_name, keys).to_utf8_buffer())


## The hashed text: `json.dumps([seed, "art/<stream>", *keys])` (default separators) with float keys rounded to 4 decimals.
static func key_text(seed: Variant, stream_name: String, keys: Array = []) -> String:
	var parts := PackedStringArray()
	parts.append(_item(seed, true))
	parts.append(ArtSeed.json_quote("art/" + stream_name))
	for k: Variant in keys:
		parts.append(_item(k, false))
	return "[" + ", ".join(parts) + "]"


static func _item(v: Variant, is_seed: bool) -> String:
	match typeof(v):
		TYPE_INT:
			return ArtSeed.u64_str(v) if is_seed else str(v)
		TYPE_FLOAT:
			return py_repr_round(float(v), KEY_DECIMALS)
		_:
			return ArtSeed.json_quote(String(v))


## Python `repr(round(x, n))` for the small magnitudes the keys have (at most 15 significant digits): the decimal text, trailing zeros trimmed.
static func py_repr_round(x: float, n: int) -> String:
	var p := int(pow(10.0, n))
	var r := int(half_even(x * float(p)))
	var neg := r < 0 or (r == 0 and (x < 0.0 or (x == 0.0 and 1.0 / x < 0.0)))
	var a := absi(r)
	var frac := str(a % p).pad_zeros(n).rstrip("0")
	if frac == "":
		frac = "0"
	return ("-" if neg else "") + str(a / p) + "." + frac


## Round half to even (Python `round`) on a float, as a float.
static func half_even(y: float) -> float:
	var f := floorf(y)
	var d := y - f
	if d > 0.5 or (d == 0.5 and fmod(f, 2.0) != 0.0):
		f += 1.0
	return f


func _init_genrand(s: int) -> void:
	if _base.is_empty():
		var b := PackedInt64Array()
		b.resize(N)
		b[0] = 19650218
		for i in range(1, N):
			var prev := b[i - 1]
			b[i] = (1812433253 * (prev ^ (prev >> 30)) + i) & MASK32
		_base = b
	_mt = _base.duplicate()


func _init_by_array(key: Array) -> void:
	_init_genrand(19650218)
	var klen := key.size()
	var i := 1
	var j := 0
	var k := maxi(N, klen)
	while k > 0:
		var prev := _mt[i - 1]
		_mt[i] = ((_mt[i] ^ ((prev ^ (prev >> 30)) * 1664525)) + int(key[j]) + j) & MASK32
		i += 1
		j += 1
		if i >= N:
			_mt[0] = _mt[N - 1]
			i = 1
		if j >= klen:
			j = 0
		k -= 1
	k = N - 1
	while k > 0:
		var prev := _mt[i - 1]
		_mt[i] = ((_mt[i] ^ ((prev ^ (prev >> 30)) * 1566083941)) - i) & MASK32
		i += 1
		if i >= N:
			_mt[0] = _mt[N - 1]
			i = 1
		k -= 1
	_mt[0] = 0x80000000
	_index = 0
	_done = 0


func _next_word() -> int:
	if _index >= N:
		_index = 0
		_done = 0
	while _done <= _index:
		var kk := _done
		var y: int
		if kk < N - M:
			y = (_mt[kk] & UPPER) | (_mt[kk + 1] & LOWER)
			_mt[kk] = _mt[kk + M] ^ (y >> 1) ^ (MATRIX if (y & 1) != 0 else 0)
		elif kk < N - 1:
			y = (_mt[kk] & UPPER) | (_mt[kk + 1] & LOWER)
			_mt[kk] = _mt[kk + (M - N)] ^ (y >> 1) ^ (MATRIX if (y & 1) != 0 else 0)
		else:
			y = (_mt[N - 1] & UPPER) | (_mt[0] & LOWER)
			_mt[N - 1] = _mt[M - 1] ^ (y >> 1) ^ (MATRIX if (y & 1) != 0 else 0)
		_done += 1
	var w := _mt[_index]
	_index += 1
	w ^= w >> 11
	w ^= (w << 7) & 0x9d2c5680
	w ^= (w << 15) & 0xefc60000
	w ^= w >> 18
	return w & MASK32


## `random()`: a float in [0, 1) from two words (53 bits).
func random() -> float:
	var a := _next_word() >> 5
	var b := _next_word() >> 6
	return (float(a) * 67108864.0 + float(b)) * (1.0 / 9007199254740992.0)


## `getrandbits(k)` for 1 <= k <= 32.
func getrandbits(k: int) -> int:
	return _next_word() >> (32 - k)


## `_randbelow(n)`: an int in [0, n), n >= 1 (draws `getrandbits(bit_length(n))` until it is below n).
func randbelow(n: int) -> int:
	if n <= 0:
		return 0
	var k := 0
	var t := n
	while t > 0:
		k += 1
		t >>= 1
	var r := getrandbits(k)
	while r >= n:
		r = getrandbits(k)
	return r


## `randrange(n)`.
func randrange(n: int) -> int:
	return randbelow(n)


## `randint(a, b)`, both inclusive.
func randint(a: int, b: int) -> int:
	return a + randbelow(b - a + 1)


## `uniform(a, b)`.
func uniform(a: float, b: float) -> float:
	return a + (b - a) * random()


## `choice(seq)`.
func choice(seq: Array) -> Variant:
	return seq[randbelow(seq.size())]


## `choices(population, weights)[0]`: one weighted pick (the cumulative weights are bisected right, like CPython).
func choices(population: Array, weights: Array) -> Variant:
	var cum: Array[float] = []
	var total := 0.0
	for w: Variant in weights:
		total += float(w)
		cum.append(total)
	var x := random() * total
	var lo := 0
	var hi := population.size() - 1
	while lo < hi:
		var mid := (lo + hi) / 2
		if x < cum[mid]:
			hi = mid
		else:
			lo = mid + 1
	return population[lo]


## `sample(population, k)` for the small populations the rules use (the pool method: n <= 21 + 4 ** ceil(log(3k, 4))).
func sample(population: Array, k: int) -> Array:
	var n := population.size()
	var pool: Array = population.duplicate()
	var out: Array = []
	for i in k:
		var j := randbelow(n - i)
		out.append(pool[j])
		pool[j] = pool[n - i - 1]
	return out
