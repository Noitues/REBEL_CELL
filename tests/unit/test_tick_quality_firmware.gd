extends GutTest
## Plan 2 N12 (R11, ruling Q20 follow-up): a Calibrated step raises every sub-tick of its slot
## one tier, capped at PERFECT, on every slice size; an authored map beats the default; the
## fight reads the raised tier.

const W := RC.PrecisionTier.WEAK
const G := RC.PrecisionTier.GOOD
const P := RC.PrecisionTier.PERFECT

var _fx: EffectInterpreter


func _calibrated() -> FirmwareData:
	var fw := FirmwareData.new()
	fw.id = &"tq_calibrated"
	fw.display_name = "Calibrated"
	fw.tick_quality_step = 1
	return fw


func before_each() -> void:
	_fx = EffectInterpreter.new(CombatFixture.config(), ContentLookup.new().add(_calibrated()))


func _wheel(sizes: Array, calibrated_slot: int = -1) -> WheelState:
	var w := WheelFixtures.state(PackedInt32Array(sizes))
	if calibrated_slot >= 0:
		w.slot_firmware_ids[calibrated_slot] = &"tq_calibrated"
	return w


func test_calibrated_raises_each_subtick_one_tier() -> void:
	assert_eq(_fx.tick_tiers(_wheel([4, 26], 0), 0), PackedInt32Array([G, P, P, G]), "W G G W -> G P P G")
	assert_eq(_fx.tick_tiers(_wheel([4, 26]), 0), PackedInt32Array([W, G, G, W]), "no Firmware: the default")


func test_calibrated_caps_at_perfect() -> void:
	assert_eq(_fx.tick_tiers(_wheel([5, 25], 0), 0), PackedInt32Array([G, P, P, P, G]))
	assert_eq(_fx.tick_tiers(_wheel([3, 27], 0), 0), PackedInt32Array([P, P, P]), "a whole slice may read PERFECT (Q20)")


func test_calibrated_works_on_every_size() -> void:
	for size in range(1, 30):
		var tiers := _fx.tick_tiers(_wheel([size, 30 - size], 0), 0)
		var base := WheelMath.default_quality(size, 1)
		assert_eq(tiers.size(), size)
		for i in size:
			assert_eq(tiers[i], mini(base[i] + 1, P), "size %d tick %d" % [size, i])


func test_override_map_beats_default() -> void:
	var w := _wheel([5, 25])
	var maps: Array[PackedInt32Array] = [PackedInt32Array([P, W, W, W, P]), PackedInt32Array()]
	w.set_quality_maps(maps)
	assert_eq(_fx.tick_tiers(w, 0), PackedInt32Array([P, W, W, W, P]))
	assert_eq(_fx.tick_tiers(w, 1), WheelMath.default_quality(25, 1), "the other slot keeps its default")


func test_calibrated_on_override_map() -> void:
	var w := _wheel([5, 25], 0)
	var maps: Array[PackedInt32Array] = [PackedInt32Array([P, W, W, W, P]), PackedInt32Array()]
	w.set_quality_maps(maps)
	assert_eq(_fx.tick_tiers(w, 0), PackedInt32Array([P, G, G, G, P]))


func test_firmware_removed_restores_default_map() -> void:
	var w := _wheel([4, 26], 0)
	w.slot_firmware_ids[0] = &""
	assert_eq(_fx.tick_tiers(w, 0), PackedInt32Array([W, G, G, W]))


func test_default_reach_is_config() -> void:
	var cfg := CombatFixture.config().duplicate() as CampaignConfigData
	cfg.tick_quality_good_reach = 2
	var fx := EffectInterpreter.new(cfg, ContentLookup.new())
	assert_eq(fx.tick_tiers(_wheel([5, 25]), 0), PackedInt32Array([G, G, P, G, G]))
