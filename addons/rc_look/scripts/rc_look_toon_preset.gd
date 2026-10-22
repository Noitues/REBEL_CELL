class_name RcLookToonPreset
extends Resource
## LOOK-TOOLBOX module 4: one toon look's band edges and shades (RcLookToon, rc_toon.gdshaderinc). Read only.

## Band edges on the lit share (n . l): shadow below `lo`, lit above `hi`.
@export var lo: float = 0.12
@export var hi: float = 0.55
## The mid and shadow bands' share of full light, and the shadow band's tint.
@export var shade_mid: float = 0.62
@export var shade_low: float = 0.32
@export var shadow_tint: Color = Color(1, 1, 1)
## A three-colour ramp by band (shadow, mid, lit) for looks that colour by band (the city), else unused.
@export var ramp: PackedColorArray = PackedColorArray()


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if not (lo < hi):
		errs.append("lo must be below hi (%s, %s)" % [lo, hi])
	if shade_low < 0.0 or shade_low > shade_mid or shade_mid > 1.0:
		errs.append("shades must rise 0 <= low <= mid <= 1 (%s, %s)" % [shade_low, shade_mid])
	if ramp.size() != 0 and ramp.size() != 3:
		errs.append("ramp holds 0 or 3 colours (%d)" % ramp.size())
	return errs
