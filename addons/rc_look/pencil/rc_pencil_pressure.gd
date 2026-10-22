class_name RcPencilPressure
extends Resource
## LOOK-TOOLBOX module 12: a hand's pressure along one wax stroke, as a width factor. Lengths are in stroke widths so a
## profile reads the same at any size (a hero ring, a map word). The pen lands at `land_width` of the width and reaches
## full pressure over `land_len`; it lifts off to `lift_width` over the last `lift_len` (the flick); in between the
## width swells by up to `swell` either way, in waves `swell_wave` long (a seeded smooth hash: never an RNG). A stroke
## shorter than land + lift scales both down to fit. LOOK-TOOLBOX 12 review (broken wax): every `gap_every` widths
## (seeded, +-half of it; 0 = none) the pen lifts for `gap_len` widths to `gap_width` of the width, never in the land
## or the lift. Pure data; RcPencilPressure.factor is the one reader.

@export var land_width: float = 0.55
@export var land_len: float = 1.6
@export var lift_width: float = 0.22
@export var lift_len: float = 3.2
@export var swell: float = 0.16
@export var swell_wave: float = 7.0
@export var gap_every: float = 0.0
@export var gap_len: float = 1.2
@export var gap_width: float = 0.12


## The width factor at `d` px along a stroke `length` px long and `width` px wide, for `seed`.
func factor(d: float, length: float, width: float, seed: int) -> float:
	var w := maxf(width, 0.001)
	var land := land_len * w
	var lift := lift_len * w
	var room := land + lift
	var lw := land_width
	var fw := lift_width
	if room > length and room > 0.0:
		# a short flick (an arrow head) is one press: its taper shortens and blunts to fit
		var fit := length / room
		land *= fit
		lift *= fit
		lw = lerpf(1.0, land_width, fit * fit)
		fw = lerpf(1.0, lift_width, fit * fit)
	var f := 1.0
	if land > 0.0:
		f *= lerpf(lw, 1.0, smoothstep(0.0, land, d))
	if lift > 0.0:
		f *= lerpf(fw, 1.0, smoothstep(0.0, lift, length - d))
	if swell > 0.0 and swell_wave > 0.0:
		f *= 1.0 + swell * (KitNoise.smooth(seed + 101, d / (swell_wave * w)) * 2.0 - 1.0)
	if gap_every > 0.0 and gap_len > 0.0:
		f *= lerpf(1.0, gap_width, gap_at(d, length, w, seed))
	return f


## How far into a pressure gap `d` px is (0 none, 1 the gap's middle) on a stroke `length` px long and `w` px wide.
func gap_at(d: float, length: float, w: float, seed: int) -> float:
	var every := gap_every * w
	var half := gap_len * w * 0.5
	if every <= 0.0 or d < (land_len * w + half) or d > length - (lift_len * w + half):
		return 0.0
	var k := floori(d / every)
	var best := 0.0
	for j in range(k - 1, k + 2):
		var c := (float(j) + 0.5 + (KitNoise.h01(seed + 131, j) - 0.5) * 0.5) * every
		best = maxf(best, 1.0 - smoothstep(half * 0.35, half, absf(d - c)))
	return best
