class_name RcLookRamp
extends RefCounted
## LOOK-TOOLBOX module 10: the distance ramps of the street views. Exact forms of the code that repeats them, so a caller moves
## onto them with identical numbers:
##   - log01(d, far, near): where camera distance d sits between far (0) and near (1) in log space, clamped (RevealTiers.band,
##     tier_weight, zoom_dive, zoom_detail).
##   - log_smooth(d, far, near): its smoothstep (the reveal tier and band weights).
##   - log_lerp(a, b, u): a to b interpolated in log space (NetrunSection.zcut's cut height).
## Pure: no Node, no Settings.

## Guard against a zero distance in the log (RevealTiers.MIN_DIST).
const MIN_DIST := 1e-3


## Where d sits between far (0) and near (1), in log space, clamped to 0..1.
static func log01(d: float, far: float, near: float) -> float:
	return maxf(0.0, minf(1.0, log(far / maxf(d, MIN_DIST)) / log(far / near)))


## The smoothstep of log01: a reveal weight that eases in from far to near.
static func log_smooth(d: float, far: float, near: float) -> float:
	return smooth01(log01(d, far, near))


## a to b at u (0..1) in log space: exp(ln a + (ln b - ln a) u).
static func log_lerp(a: float, b: float, u: float) -> float:
	return exp(log(a) + (log(b) - log(a)) * u)


## Smoothstep of a parameter clamped to 0..1 (NetrunArtUnits.smoothstep01).
static func smooth01(t: float) -> float:
	var c := maxf(0.0, minf(1.0, t))
	return c * c * (3.0 - 2.0 * c)
