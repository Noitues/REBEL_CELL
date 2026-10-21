class_name RcLookQuality
extends RefCounted
## LOOK-TOOLBOX module 2: the one place that turns the player's look settings (RcLookQualityState: quality tier,
## reduce effects, reduce motion, high contrast) into a module's settings, from RcLookQualityConfig. Pure: the same
## config and state always give the same values. Modules call `resolve` and never read the tier or Settings flags.

static var _default: RcLookQualityConfig = null


## The default config (addons/rc_look/config/look_quality.tres), loaded once.
static func default_config() -> RcLookQualityConfig:
	if _default == null:
		_default = load(RcLookQualityConfig.DEFAULT_PATH)
	return _default


## `module`'s settings (param -> value) under `state`: base, then the tier's value, then high contrast, reduce motion
## and reduce effects in that order (the strictest last). An unknown module gives an empty Dictionary.
static func resolve(cfg: RcLookQualityConfig, module: StringName, state: RcLookQualityState) -> Dictionary:
	var out := {}
	var params: Dictionary = cfg.modules.get(String(module), {})
	var tier := clampi(state.tier, 0, RcLookQualityConfig.TIER_COUNT - 1)
	for p: String in params:
		var rule: Dictionary = params[p]
		var v: Variant = rule["base"]
		if rule.has("tiers"):
			v = (rule["tiers"] as Array)[tier]
		if state.high_contrast and rule.has("high_contrast"):
			v = rule["high_contrast"]
		if state.reduce_motion and rule.has("reduce_motion"):
			v = rule["reduce_motion"]
		if state.reduce_effects and rule.has("reduce_effects"):
			v = rule["reduce_effects"]
		out[p] = v
	return out


## `resolve` on the default config.
static func of(module: StringName, state: RcLookQualityState) -> Dictionary:
	return resolve(default_config(), module, state)
