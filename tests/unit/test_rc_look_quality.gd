extends GutTest
## LOOK-TOOLBOX module 2 (fast tier): one resolver maps the quality tier and the accessibility flags to a module's
## settings. The precedence is base < tier < high contrast < reduce motion < reduce effects; the result is pure; the
## shipped config validates; a bad config is reported.

var _cfg: RcLookQualityConfig


func before_all() -> void:
	_cfg = RcLookQualityConfig.new()
	_cfg.modules = {"m": {
		"a": {"base": 1.0, "tiers": [0.25, 0.5, 1.0], "high_contrast": 0.7, "reduce_motion": 0.3, "reduce_effects": 0.0},
		"b": {"base": true},
	}}


func test_shipped_config_validates() -> void:
	assert_eq(RcLookQuality.default_config().validate(), PackedStringArray())


func test_tier_picks_its_value_and_clamps() -> void:
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(0))["a"], 0.25)
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(1))["a"], 0.5)
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(2))["a"], 1.0)
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(9))["a"], 1.0, "above the top tier: the top")
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(-3))["a"], 0.25, "below: the low tier")


func test_flags_apply_strictest_last() -> void:
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(2, false, false, true))["a"], 0.7, "high contrast")
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(2, false, true, true))["a"], 0.3, "reduce motion over high contrast")
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(2, true, true, true))["a"], 0.0, "reduce effects over all")
	assert_eq(RcLookQuality.resolve(_cfg, &"m", RcLookQualityState.make(0, true))["b"], true, "a param with no rule for the flag keeps base")


func test_unknown_module_is_empty_and_resolve_is_pure() -> void:
	assert_eq(RcLookQuality.resolve(_cfg, &"nope", RcLookQualityState.make(2)), {})
	var s := RcLookQualityState.make(1, false, true)
	assert_eq(RcLookQuality.resolve(_cfg, &"m", s), RcLookQuality.resolve(_cfg, &"m", s))
	assert_eq(s.label(), "t1_rm")


func test_bad_config_is_reported() -> void:
	var bad := RcLookQualityConfig.new()
	bad.modules = {"m": {"nobase": {"tiers": [1, 2, 3]}, "short": {"base": 1.0, "tiers": [1.0]},
		"typo": {"base": 1.0, "reduce_effect": 0.0}, "type": {"base": 1.0, "reduce_motion": true}}}
	var errs := bad.validate()
	assert_eq(errs.size(), 4, "one error per bad rule: %s" % [errs])
