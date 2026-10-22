class_name RcLookQualityConfig
extends Resource
## LOOK-TOOLBOX module 2: every rc_look module's settings by quality tier and accessibility flag, in one resource
## (addons/rc_look/config/look_quality.tres). Read only through RcLookQuality.resolve; no module checks the tier or a
## Settings flag itself.
##
## `modules` = { module id: { param: rule } }, where a rule is a Dictionary with
##   "base": the value at the top tier with every flag off (required),
##   "tiers": [low, mid, high] values by quality tier (optional; replaces base),
##   "high_contrast", "reduce_motion", "reduce_effects": the value under that flag (optional).
## Flags apply after the tier, in that order, so reduce effects (the strictest) wins.

const DEFAULT_PATH := "res://addons/rc_look/config/look_quality.tres"
## The keys a rule may hold.
const RULE_KEYS: Array[String] = ["base", "tiers", "high_contrast", "reduce_motion", "reduce_effects"]
## Quality tiers: 0 low, 1 medium, 2 high (Settings.CITY_QUALITY_MAX).
const TIER_COUNT := 3

@export var modules: Dictionary = {}


## Problems with the config (empty when good): a rule with no base, an unknown key, a tiers list of the wrong length,
## a value whose type differs from its base.
func validate() -> PackedStringArray:
	var errs := PackedStringArray()
	for m: String in modules:
		var params: Dictionary = modules[m]
		for p: String in params:
			var rule: Variant = params[p]
			var where := "%s.%s" % [m, p]
			if not (rule is Dictionary) or not (rule as Dictionary).has("base"):
				errs.append("%s: a rule needs a base" % where)
				continue
			var base: Variant = rule["base"]
			for k: String in rule:
				if not RULE_KEYS.has(k):
					errs.append("%s: unknown key %s" % [where, k])
				elif k == "tiers":
					var t: Variant = rule[k]
					if not (t is Array) or (t as Array).size() != TIER_COUNT:
						errs.append("%s: tiers needs %d values" % [where, TIER_COUNT])
					else:
						for v: Variant in t:
							if typeof(v) != typeof(base):
								errs.append("%s: a tier value's type differs from base" % where)
				elif typeof(rule[k]) != typeof(base):
					errs.append("%s: %s's type differs from base" % [where, k])
	return errs
