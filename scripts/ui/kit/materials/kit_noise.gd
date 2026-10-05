class_name KitNoise
extends RefCounted
## Decoration randomness for the material kit (ART-1 1B): integer hashes, never the game's
## RNG or randf() (ANIMATION_HANDOFF ground rule 1). The same inputs always give the same
## jitter, so a sticker or a pencil mark looks the same every time it is built. View only.


## A hash of up to three integers in 0..1.
static func h01(a: int, b: int, c: int = 0) -> float:
	var n := (a * 73856093) ^ (b * 19349663) ^ (c * 83492791)
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xFFFF) / 65535.0


## A hash of up to three integers in -1..1.
static func h11(a: int, b: int, c: int = 0) -> float:
	return h01(a, b, c) * 2.0 - 1.0


## A smooth 1D value noise at `x` (period 1 per knot) for seed `seed`, in 0..1.
static func smooth(seed: int, x: float) -> float:
	var i := floori(x)
	var f := x - float(i)
	var u := f * f * (3.0 - 2.0 * f)
	return lerpf(h01(seed, i), h01(seed, i + 1), u)
