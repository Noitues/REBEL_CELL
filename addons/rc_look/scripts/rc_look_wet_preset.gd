class_name RcLookWetPreset
extends Resource
## LOOK-TOOLBOX module 8: one wet surface's numbers (RcLookWet, rc_wet.gdshaderinc). Read only.

## How the surface's Fresnel F0 is set (each view keeps its own; the designer rules on one).
enum F0Policy { SPECULAR_X016, SPECULAR_X008, IOR }

## Puddle noise: world scale (per BU) and octaves.
@export var noise_scale: float = 0.09
@export var octaves: int = 5
## Roughness: rough_wet.x where dry to .y in a puddle, across the noise range rough_noise.x..y.
@export var rough_noise: Vector2 = Vector2(0.45, 0.6)
@export var rough_wet: Vector2 = Vector2(0.3, 0.03)
## F0: the policy and its input (the material's specular, or the index of refraction).
@export var f0_policy: F0Policy = F0Policy.SPECULAR_X016
@export var specular: float = 0.7
@export var ior: float = 1.33
## The Fresnel boost (water plane: fr * (1 + boost), capped at 1).
@export var fresnel_boost: float = 0.0


## The F0 this preset's policy gives.
func f0() -> float:
	match f0_policy:
		F0Policy.SPECULAR_X016:
			return 0.16 * specular
		F0Policy.SPECULAR_X008:
			return 0.08 * specular
	return RcLookWet.f0_ior(ior)


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if noise_scale <= 0.0:
		errs.append("noise_scale must be above 0 (%s)" % noise_scale)
	if octaves < 1 or octaves > 8:
		errs.append("octaves must be 1..8 (%d)" % octaves)
	if not (rough_noise.x < rough_noise.y):
		errs.append("rough_noise must rise (%s)" % rough_noise)
	if rough_wet.x < 0.0 or rough_wet.y < 0.0 or rough_wet.x > 1.0 or rough_wet.y > 1.0:
		errs.append("rough_wet must be 0..1 (%s)" % rough_wet)
	if ior < 1.0:
		errs.append("ior must be at least 1 (%s)" % ior)
	return errs
