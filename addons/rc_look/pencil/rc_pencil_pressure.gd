class_name RcPencilPressure
extends Resource
## LOOK-TOOLBOX module 12: a hand's pressure along one wax stroke, as a width factor. Lengths are in stroke widths so a
## profile reads the same at any size (a hero ring, a map word). The pen lands at `land_width` of the width and reaches
## full pressure over `land_len`; it lifts off to `lift_width` over the last `lift_len` (the flick); in between the
## width swells by up to `swell` either way, in waves `swell_wave` long (a seeded smooth hash: never an RNG). A stroke
## shorter than land + lift scales both down to fit. Pure data; RcPencilPressure.factor is the one reader.

@export var land_width: float = 0.55
@export var land_len: float = 1.6
@export var lift_width: float = 0.22
@export var lift_len: float = 3.2
@export var swell: float = 0.16
@export var swell_wave: float = 7.0


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
	return f
