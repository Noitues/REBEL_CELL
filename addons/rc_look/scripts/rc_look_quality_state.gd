class_name RcLookQualityState
extends RefCounted
## LOOK-TOOLBOX module 2: the player's look settings in one value, the only input RcLookQuality.resolve reads. A view
## builds it from Settings (`from_settings`) and passes it down; tests and labs build it directly. Pure data.

## Settings.reduce_effects: no particles, flashes, scanline roll or flicker (ART_BIBLE §5.4).
var reduce_effects: bool = false
## Settings.reduce_motion: no camera moves, parallax, shake; static fog and rain sheen (§5.4).
var reduce_motion: bool = false
## Settings.high_contrast: opaque panels, no glass, blur or holo transparency (§5.6).
var high_contrast: bool = false
## Settings.colorblind_mode (&"off" or a mode id).
var colorblind: StringName = &"off"
## The quality tier 0 low .. 2 high (Settings.city_quality; -1 there means "the default", resolved to `default_tier`).
var tier: int = 2


## The state from the live Settings autoload; a city_quality of -1 becomes `default_tier`.
static func from_settings(default_tier: int = 2) -> RcLookQualityState:
	var s := RcLookQualityState.new()
	s.reduce_effects = Settings.reduce_effects
	s.reduce_motion = Settings.reduce_motion
	s.high_contrast = Settings.high_contrast
	s.colorblind = Settings.colorblind_mode
	s.tier = default_tier if Settings.city_quality < 0 else Settings.city_quality
	return s


## A state with the given flags (labs and tests).
static func make(p_tier: int, p_reduce_effects: bool = false, p_reduce_motion: bool = false,
		p_high_contrast: bool = false) -> RcLookQualityState:
	var s := RcLookQualityState.new()
	s.tier = p_tier
	s.reduce_effects = p_reduce_effects
	s.reduce_motion = p_reduce_motion
	s.high_contrast = p_high_contrast
	return s


## A short stable label for sheets and file names ("t2", "t0_re_rm_hc").
func label() -> String:
	var parts := PackedStringArray(["t%d" % tier])
	if reduce_effects:
		parts.append("re")
	if reduce_motion:
		parts.append("rm")
	if high_contrast:
		parts.append("hc")
	return "_".join(parts)
