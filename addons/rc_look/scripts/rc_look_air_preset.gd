class_name RcLookAirPreset
extends Resource
## LOOK-TOOLBOX module 7: one time of day's air and sky (RcLookAir, rc_air.gdshaderinc). Read only. Distances and heights
## are in the caller's unit (BU in the city; a 2D view passes its own depth proxy). The air's colour IS the sky's horizon
## colour (`air_color`): distant things converge on the horizon, so depth reads right (art-pass 2026-10-22).

## The air term: start distance, density per unit, the height over which it thins, the share left high up.
@export var start: float = 0.0
@export var density: float = 0.01
@export var height: float = 30.0
@export var high: float = 0.15
## Share of the air that hides what is behind it (1: a plain mix; lower: the air adds its colour, lit windows stay).
@export var extinct: float = 1.0
## Sky (sRGB): zenith, horizon, below the horizon; the horizon glow's falloff and the ground's.
@export var sky_top: Color = Color(0.003, 0.003, 0.01)
@export var sky_horizon: Color = Color(0.42, 0.14, 0.09)
@export var sky_ground: Color = Color(0.01, 0.008, 0.016)
@export var glow_k: float = 12.0
@export var ground_k: float = 8.0


## The air's colour: the sky's horizon (sRGB).
func air_color() -> Color:
	return sky_horizon


## The air term's four numbers as the shader's vec4.
func air_vec() -> Vector4:
	return Vector4(start, density, height, high)


## Problems with the numbers (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	if density < 0.0:
		errs.append("density must be >= 0 (%s)" % density)
	if height <= 0.0:
		errs.append("height must be > 0 (%s)" % height)
	if high < 0.0 or high > 1.0:
		errs.append("high must be in 0..1 (%s)" % high)
	if extinct < 0.0 or extinct > 1.0:
		errs.append("extinct must be in 0..1 (%s)" % extinct)
	if glow_k < 0.0 or ground_k < 0.0:
		errs.append("glow_k and ground_k must be >= 0")
	return errs
