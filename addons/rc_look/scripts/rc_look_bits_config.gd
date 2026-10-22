class_name RcLookBitsConfig
extends Resource
## LOOK-TOOLBOX module 16: the binary bits' look numbers (addons/rc_look/config/look_bits.tres). The numbers that were
## constants in BitsPath, BinaryBits, BitsSeam and combat_fx_layer. Timings stay in ui_motion.tres (bits_flight, the
## stream and shard entries); fx_shard_* counts stay in campaign_config.tres.

## Preset name -> RcLookBitsPreset.
@export var presets: Dictionary = {}
## Path (BitsPath): the control point's rim radii; the free bow as a share of the length; a bit's flight varies by +- this
## share; the tumble speed range (rad/s); the ease's smoothstep and quadratic shares (they sum to 1).
@export var rim_control: float = 1.5
@export var free_bow: float = 0.25
@export var flight_spread: float = 0.15
@export var spin_min: float = 4.0
@export var spin_max: float = 11.0
@export var ease_smooth: float = 0.35
@export var ease_quad: float = 0.65
## The flip's rhythm and atlas (BinaryBits): seconds a glyph shows, atlas frames (0, 1, +, bit-rot), the flip phase
## spread (flips), a bit's drawn size share of the atlas cell, the end size share, the lifetime past the last arrival.
@export var flip_seconds: float = 0.06
@export var frames: int = 4
@export var flip_spread: float = 7.0
@export var bit_scale: float = 0.5
@export var end_scale: float = 0.55
@export var linger: float = 0.1
## Pool and caps (BinaryBits): bits per GPU burst, the CPU fallback's cap, emitters kept, bits a rect source gives.
@export var max_bits: int = 64
@export var cpu_max: int = 44
@export var pool_size: int = 4
@export var rect_bits: int = 36
## The CPU draw (BitsSeam): the dark rim's alpha, the outline width as a share of the size, the rim's least width (px),
## the trail copy's alpha and lag (s), the smallest lettering (px).
@export var rim_alpha: float = 0.95
@export var outline_share: float = 1.0 / 22.0
@export var rim_px: int = 3
@export var trail_alpha: float = 0.28
@export var trail_lag: float = 0.035
@export var min_px: int = 6
## Streams (combat_fx_layer): the stagger and travel as shares of the effect's time, the long travel factor, the bow (px).
@export var stream_stagger: float = 0.35
@export var stream_travel: float = 0.4
@export var stream_travel_long: float = 1.4
@export var stream_bow: float = 40.0
## Hit shards (combat_fx_layer): shares of the effect's time for the free flight, the suck's stagger and the travel, the
## spread (rad) and the smallest glyph (share of the largest).
@export var shard_free: float = 0.28
@export var shard_stagger: float = 0.24
@export var shard_travel: float = 0.46
@export var shard_spread: float = 2.4
@export var shard_min_share: float = 0.6


## Problems with the config (empty when good).
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for n in RcLookBits.REQUIRED:
		if not presets.has(n):
			errs.append("missing preset %s" % n)
	for n: StringName in presets:
		if not presets[n] is RcLookBitsPreset:
			errs.append("%s is not an RcLookBitsPreset" % n)
			continue
		for e in (presets[n] as RcLookBitsPreset).validate():
			errs.append("%s: %s" % [n, e])
	if rim_control <= 1.0:
		errs.append("rim_control must be past the rim, above 1 (%s)" % rim_control)
	if flight_spread < 0.0 or flight_spread >= 1.0:
		errs.append("flight_spread must be in [0, 1) (%s)" % flight_spread)
	if spin_min <= 0.0 or spin_max < spin_min:
		errs.append("spin range must be 0 < min <= max (%s, %s)" % [spin_min, spin_max])
	if ease_smooth < 0.0 or absf(ease_smooth + ease_quad - 1.0) > 1e-6:
		errs.append("ease_smooth must be 0 or more and sum with ease_quad to 1 (%s, %s)" % [ease_smooth, ease_quad])
	if flip_seconds <= 0.0 or frames < 2:
		errs.append("flip_seconds must be above 0 and frames 2 or more (%s, %s)" % [flip_seconds, frames])
	if end_scale <= 0.0 or end_scale > 1.0 or bit_scale <= 0.0:
		errs.append("end_scale must be in (0, 1] and bit_scale above 0 (%s, %s)" % [end_scale, bit_scale])
	if cpu_max < 1 or max_bits < cpu_max:
		errs.append("cpu_max must be 1..max_bits (%s, %s)" % [cpu_max, max_bits])
	if trail_alpha < 0.0 or trail_alpha > 1.0 or rim_alpha < 0.0 or rim_alpha > 1.0:
		errs.append("trail_alpha and rim_alpha must be 0..1 (%s, %s)" % [trail_alpha, rim_alpha])
	return errs
