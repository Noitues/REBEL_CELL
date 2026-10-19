class_name NetrunArtUnits
extends RefCounted
## NA-21 twin of `tools/netrun_art/units.py`: unit factors and the small math helpers the netrun-art twins share.
## BU = one-city Blender unit. Plan coordinates are `[x, y]` (x east, y north); heights are BU above local ground.
## Points and vectors are plain `Array` of floats (64-bit), never Vector3 (single precision would break parity).
## Python is the oracle: every function keeps the Python operation order.

## Points nearer than this along the view axis are not projected (`rig.NEAR_Z`, a projection guard, not tuning).
const NEAR_Z := 0.1


## One storey in BU (`units.FLOOR_BU`, from config).
static func floor_bu() -> float:
	return float(NetrunArtConfigData.shipped().units["floor_bu"])


## Kit unit to BU: `FLOOR_BU / KIT_STOREY`.
static func k_units() -> float:
	var u: Dictionary = NetrunArtConfigData.shipped().units
	return float(u["floor_bu"]) / float(u["kit_storey"])


## HQ scene factor `K_FIT`.
static func k_fit() -> float:
	return float(NetrunArtConfigData.shipped().units["k_fit"])


## A kit-unit length in BU.
static func kit(v: float) -> float:
	return v * k_units()


## Round to 1e-4 half up, `floor(x * 1e4 + 0.5) / 1e4` (spec 12.8 rule 1).
static func r4(v: float) -> float:
	return floorf(v * 1e4 + 0.5) / 1e4


## Smoothstep of a parameter clamped to 0..1.
static func smoothstep01(t: float) -> float:
	t = maxf(0.0, minf(1.0, t))
	return t * t * (3.0 - 2.0 * t)


## Clamp to 0..1.
static func clamp01(x: float) -> float:
	return maxf(0.0, minf(1.0, x))


## Linear interpolation.
static func lerp_f(a: float, b: float, t: float) -> float:
	return a + (b - a) * t


## `a - b` for 3-vectors.
static func sub3(a: Array, b: Array) -> Array:
	return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


## Dot product of 3-vectors.
static func dot3(a: Array, b: Array) -> float:
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


## Cross product of 3-vectors.
static func cross3(a: Array, b: Array) -> Array:
	return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


## Unit vector of a 3-vector.
static func norm3(a: Array) -> Array:
	var n := sqrt(dot3(a, a))
	return [a[0] / n, a[1] / n, a[2] / n]


## Euclidean distance of 3-vectors.
static func dist3(a: Array, b: Array) -> float:
	return sqrt((a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1]) + (a[2] - b[2]) * (a[2] - b[2]))


## `math.hypot`.
static func hypot(x: float, y: float) -> float:
	return sqrt(x * x + y * y)


## Sum of a float array (plain left-to-right).
static func sum_f(a: Array) -> float:
	var s := 0.0
	for v: float in a:
		s += v
	return s


## `base` with the keys of `over` laid on top (Python `dict(base, **over)`). Deep copy of `base`.
static func merge(base: Dictionary, over: Dictionary) -> Dictionary:
	var out: Dictionary = base.duplicate(true)
	for k: Variant in over:
		out[k] = over[k]
	return out
