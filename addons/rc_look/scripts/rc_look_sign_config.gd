class_name RcLookSignConfig
extends Resource
## LOOK-TOOLBOX module 11: the neon presets and the flicker numbers (addons/rc_look/config/look_sign.tres).

## Preset name -> RcLookSignPreset.
@export var presets: Dictionary = {}
## Flicker (dress_neon's): a burst's length as a share of its slot, hum cycles per loop, the hum's floor.
@export var burst_len: float = 0.14
@export var hum_hz: float = 4.0
@export var hum_floor: float = 0.6
## Blink and beacon (city_glow's): the blink's lit share of its period and its off level.
@export var blink_duty: float = 0.35
@export var blink_off: float = 0.25


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in RcLookSign.REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookSignPreset:
			errs.append("%s is not an RcLookSignPreset" % n)
			continue
		for e in (presets[n] as RcLookSignPreset).validate():
			errs.append("%s: %s" % [n, e])
	if burst_len <= 0.0 or burst_len >= 1.0:
		errs.append("burst_len must be in (0, 1) (%s)" % burst_len)
	if hum_floor < 0.0 or hum_floor > 1.0:
		errs.append("hum_floor must be 0..1 (%s)" % hum_floor)
	if blink_duty <= 0.0 or blink_duty >= 1.0:
		errs.append("blink_duty must be in (0, 1) (%s)" % blink_duty)
	return errs
