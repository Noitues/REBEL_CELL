extends GutTest
## ART-0 audit B1 (ART_BIBLE v2 §3.15, §5.3, §5.5, Appendix B): the Heat glitch Options extra
## is built and the toggle reaches it. Off by default; grows with the Heat band; exempt from
## VfxTier; off under reduce effects; flash-limiter safe (no dip, no roll brightening); with
## the option off only the static corp edge tint at HUNTED+ remains; a motion entry, in
## REQUIRED_IDS and the motion lab; in the combat scene between the backdrop and the wheels.

var _glitch: bool
var _reduce: bool
var _limiter: bool


func before_each() -> void:
	_glitch = Settings.heat_glitch
	_reduce = Settings.reduce_effects
	_limiter = Settings.flash_limiter
	Motion.use_config(null)


func after_each() -> void:
	Motion.force_live = false
	if Settings.heat_glitch != _glitch:
		Settings.set_heat_glitch(_glitch)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if Settings.flash_limiter != _limiter:
		Settings.set_flash_limiter(_limiter)


func _cfg() -> CampaignConfigData:
	return CombatFixture.config()


func test_it_is_off_by_default_and_only_the_static_edge_tint_shows() -> void:
	var fresh: Node = autofree(load("res://scripts/autoload/settings.gd").new())
	assert_false(fresh.heat_glitch, "the option is off by default")
	for b in HeatGlitchLayer.BANDS:
		var lk := HeatGlitchLayer.look(b, false, true, false, _cfg())
		assert_false(bool(lk["animated"]), "band %d: no glitch while the option is off" % b)
		for k in ["tears", "blocks", "tear_px", "slip_px", "split_px", "scan", "dip"]:
			assert_eq(float(lk[k]), 0.0, "band %d: no %s while off" % [b, k])
		if b >= HeatGlitchLayer.HUNTED:
			assert_almost_eq(float(lk["edge"]), Motion.amplitude(&"heat_glitch"), 0.0001, "band %d: the static corp edge tint (§5.5)" % b)
		else:
			assert_eq(float(lk["edge"]), 0.0, "band %d: no tint below HUNTED" % b)


func test_the_glitch_grows_with_the_heat_band() -> void:
	var cfg := _cfg()
	var prev := {}
	var prev_layers := -1
	for b in HeatGlitchLayer.BANDS:
		var lk := HeatGlitchLayer.look(b, true, true, false, cfg)
		assert_true(bool(lk["animated"]))
		assert_lt(float(lk["burst"]), float(lk["period"]), "band %d: a burst is short and periodic" % b)
		var layers := 1 + int(int(lk["tears"]) > 0) + int(bool(lk["roll"]) or int(lk["blocks"]) > 0) + int(float(lk["slip_px"]) > 0.0)
		if not prev.is_empty():
			assert_lte(float(lk["period"]), float(prev["period"]), "band %d: bursts come as often or more" % b)
			assert_gte(float(lk["burst"]), float(prev["burst"]), "band %d: and last as long or longer" % b)
			for k in ["tears", "blocks", "tear_px", "split_px", "slip_px", "scan"]:
				assert_gte(float(lk[k]), float(prev[k]), "band %d: %s never shrinks" % [b, k])
			assert_gte(layers, prev_layers, "band %d keeps every layer of the band before" % b)
		if b > 0 and b <= HeatGlitchLayer.HUNTED:
			assert_gt(layers, prev_layers, "band %d adds a layer" % b)
		prev = lk
		prev_layers = layers


func test_it_is_off_under_reduce_effects_and_headless() -> void:
	for b in HeatGlitchLayer.BANDS:
		assert_false(bool(HeatGlitchLayer.look(b, true, false, false, _cfg())["animated"]), "band %d: motion off, glitch off" % b)
	var layer: HeatGlitchLayer = add_child_autofree(HeatGlitchLayer.new())
	layer.set_band(3)
	Settings.set_heat_glitch(true)
	assert_false(layer.animated(), "headless: never animates")
	Motion.force_live = true
	layer.refresh()
	assert_true(layer.animated(), "on, with motion: it animates")
	assert_true(layer.is_processing() and layer.visible, "and runs")
	Settings.set_reduce_effects(true)
	assert_false(layer.animated(), "reduce effects: off")
	assert_false(layer.is_processing(), "nothing moves (Settings.changed reached it)")
	assert_true(layer.visible, "the static edge tint stays at HUNTED")


func test_the_options_toggle_reaches_the_layer() -> void:
	Motion.force_live = true
	var layer: HeatGlitchLayer = add_child_autofree(HeatGlitchLayer.new())
	layer.set_band(1)
	Settings.set_heat_glitch(false)
	assert_false(layer.is_processing() or layer.visible, "off at NOTICED: nothing drawn")
	Settings.set_heat_glitch(true)
	assert_true(layer.is_processing() and layer.visible, "the toggle turns it on")
	Settings.set_heat_glitch(false)
	assert_false(layer.is_processing() or layer.visible, "and off again")


func test_it_is_flash_limiter_safe_and_exempt_from_vfx_tier() -> void:
	for b in HeatGlitchLayer.BANDS:
		var lk := HeatGlitchLayer.look(b, true, true, true, _cfg())
		assert_eq(float(lk["dip"]), 0.0, "band %d: no luminance dip under the limiter (§5.5)" % b)
		assert_eq(float(lk["roll_gain"]), 0.0, "band %d: the roll adds no light" % b)
		var periods := 1.0 / float(lk["period"])
		assert_lt(periods, float(Fx.limiter.max_per_second), "band %d: fewer bursts a second than the limiter allows flashes" % b)
	assert_true(Settings.VFX_TIER_EXEMPT.has(HeatGlitchLayer.MOTION), "exempt from VfxTier (registered)")
	var src := FileAccess.get_file_as_string("res://scripts/ui/fx/heat_glitch_layer.gd")
	assert_false(src.contains("VfxTier.clamp"), "nothing clamps it to a tier")
	assert_false(src.contains("Fx.flash("), "it is no flash")
	var e := Motion.entry(HeatGlitchLayer.MOTION)
	assert_not_null(e, "a ui_motion.tres entry")
	assert_eq(int(e.kind), UiMotionEntryData.Kind.LOOP, "a loop, not an effect length")
	assert_true(UiMotionData.REQUIRED_IDS.has(HeatGlitchLayer.MOTION), "in REQUIRED_IDS")
	var lab := FileAccess.get_file_as_string("res://tools/design_lab/motion_lab.gd")
	assert_true(lab.contains("&\"heat_glitch\": [\"scene\", \"fx_glitch\"]"), "a motion-lab demo on the live fight")
	assert_false(FileAccess.get_file_as_string("res://shaders/heat_glitch.gdshader").contains("TIME"), "the script drives it (no clock of its own)")


func test_a_burst_is_periodic_short_and_steps() -> void:
	var cfg := _cfg()
	var period := cfg.heat_glitch_period[3]
	var burst := cfg.heat_glitch_burst[3]
	var step := Motion.entry(HeatGlitchLayer.MOTION).duration
	var between := HeatGlitchLayer.burst_at(burst + (period - burst) * 0.5, period, burst, step)
	assert_eq(float(between["env"]), 0.0, "quiet between bursts")
	var mid := HeatGlitchLayer.burst_at(burst * 0.3, period, burst, step)
	assert_gt(float(mid["env"]), 0.0, "glitching mid-burst")
	assert_lte(float(mid["env"]), 1.0)
	var a := HeatGlitchLayer.burst_at(burst * 0.3 + 0.001, period, burst, step)
	assert_eq(float(a["seed"]), float(mid["seed"]), "a state holds for its step")
	var next := HeatGlitchLayer.burst_at(period + burst * 0.3, period, burst, step)
	assert_ne(float(next["seed"]), float(mid["seed"]), "the next burst is a new glitch")
	assert_eq(float(next["env"]), float(mid["env"]), "with the same envelope")


func test_the_combat_scene_puts_it_over_the_backdrop_and_under_the_wheels() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/combat_scene.gd")
	var city := src.find("add_child(heat_city)")
	var glitch := src.find("add_child(heat_glitch)")
	var root := src.find("add_child(root)", city)
	assert_gt(city, -1)
	assert_gt(glitch, city, "after the Heat city (it reads the backdrop)")
	assert_lt(glitch, root, "before the UI root (wheels, FX and HUD draw above it)")
	assert_true(src.contains("heat_glitch.set_band(Palette.heat_band(heat, levels)"), "it follows the Heat band")
