extends GutTest
## LOOK-TOOLBOX module 15 (fast tier): the decrypted holo. The quality rules drop the split on the low tier, freeze the
## bands under reduce motion (still drawn), zero the motion under reduce effects and go opaque with no effects under high
## contrast; the cracked seal's fracture is deterministic and shaped (not colour alone); DecryptedHoloPanel, the one
## call site (THREAT INTEL, the Site file), carries the module's values and the old shader is gone.

const OLD_SHADER := "res://shaders/kit/decrypted_holo.gdshader"


func _s(tier: int, re: bool = false, rm: bool = false, hc: bool = false) -> Dictionary:
	return RcLookHolo.settings(RcLookQualityState.make(tier, re, rm, hc))


func test_shipped_configs_load_and_validate() -> void:
	assert_not_null(RcLookHolo.config(), "look_holo.tres loads")
	assert_eq(RcLookQuality.default_config().validate(), PackedStringArray())
	assert_false(RcLookQuality.of(RcLookHolo.MODULE, RcLookQualityState.make(2)).is_empty(), "module holo has rules")
	assert_not_null(load(RcLookHolo.SHADER_PATH), "the shader compiles")


func test_top_tier_has_every_part() -> void:
	var s := _s(2)
	assert_gt(float(s[&"split_px"]), 0.0, "the edge split")
	assert_gt(float(s[&"blur_lod"]), 0.0, "the blurred city")
	assert_lt(float(s[&"glass_alpha"]), 1.0, "translucent: the city shows through")
	assert_gt(float(s[&"scan_strength"]), 0.0, "scanlines")
	assert_gt(float(s[&"band_strength"]), 0.0, "scan bands")
	assert_eq(float(s[&"band_roll"]), 1.0, "the bands roll")


func test_low_tier_drops_the_split_and_the_blur_and_backs_harder() -> void:
	var low := _s(0)
	var top := _s(2)
	assert_eq(float(low[&"split_px"]), 0.0, "low tier: no RGB split")
	assert_eq(float(low[&"blur_lod"]), 0.0, "low tier: no screen blur")
	assert_gt(float(low[&"backing_alpha"]), float(top[&"backing_alpha"]), "no blur, so a stronger backing")
	assert_gt(float(low[&"glass_alpha"]), float(top[&"glass_alpha"]), "and a stronger glass")
	assert_gt(float(_s(1)[&"split_px"]), 0.0, "the middle tier keeps the split")


func test_reduce_motion_freezes_the_bands_but_keeps_them() -> void:
	var s := _s(2, false, true)
	assert_eq(float(s[&"band_roll"]), 0.0, "frozen")
	assert_gt(float(s[&"band_strength"]), 0.0, "still drawn at their pose")
	assert_gt(float(s[&"split_px"]), 0.0, "the split is not motion")


func test_reduce_effects_zeroes_the_motion_and_the_split() -> void:
	var s := _s(2, true)
	assert_eq(float(s[&"band_roll"]), 0.0)
	assert_eq(float(s[&"split_px"]), 0.0)


func test_high_contrast_is_opaque_and_plain() -> void:
	var s := _s(2, false, false, true)
	assert_eq(float(s[&"glass_alpha"]), 1.0, "opaque")
	assert_eq(float(s[&"backing_alpha"]), 1.0)
	for k: StringName in [&"fill_share", &"blur_lod", &"scan_strength", &"band_strength", &"split_px", &"edge_glow_strength"]:
		assert_eq(float(s[k]), 0.0, "%s off" % k)


func test_settings_are_pure_and_scale_with_the_corp_body() -> void:
	assert_eq(_s(1, false, true), _s(1, false, true))
	var dim := RcLookHolo.settings(RcLookQualityState.make(2), 0.5)
	assert_almost_eq(float(dim[&"fill_share"]), float(_s(2)[&"fill_share"]) * 0.5, 0.0001)
	assert_almost_eq(float(dim[&"scan_strength"]), float(_s(2)[&"scan_strength"]) * 0.5, 0.0001)


func test_crack_is_deterministic_and_jagged() -> void:
	var a := RcLookHolo.crack(Vector2(100.0, 100.0), 30.0, 7)
	var b := RcLookHolo.crack(Vector2(100.0, 100.0), 30.0, 7)
	assert_eq(a["line"], b["line"], "same seed, same fracture")
	assert_ne(a["line"], RcLookHolo.crack(Vector2(100.0, 100.0), 30.0, 8)["line"], "another seed, another fracture")
	var line: PackedVector2Array = a["line"]
	assert_eq(line.size(), RcLookHolo.config().crack_segments + 1)
	assert_almost_eq(line[0].y, 70.0, 0.001, "starts at the seal's top")
	assert_almost_eq(line[line.size() - 1].y, 130.0, 0.001, "ends at its foot")
	var xs := {}
	for p in line:
		xs[snappedf(p.x, 0.01)] = true
	assert_gt(xs.size(), 2, "it kinks sideways: the crack reads by shape, not by colour alone")
	assert_eq((a["branches"] as Array).size(), RcLookHolo.config().crack_branches)


func test_panel_carries_the_modules_values() -> void:
	var h := DecryptedHoloPanel.new()
	h.size = Vector2(300.0, 200.0)
	add_child_autofree(h)
	h.state_override = RcLookQualityState.make(2)
	var m := h.get_node("Glass").material as ShaderMaterial
	assert_eq(float(m.get_shader_parameter(&"split_px")), float(_s(2)[&"split_px"]))
	assert_eq(m.get_shader_parameter(&"panel"), Vector4(0.0, 0.0, 300.0, 200.0))
	h.state_override = RcLookQualityState.make(0)
	assert_eq(float(m.get_shader_parameter(&"split_px")), 0.0, "low tier drops the split on the live panel")
	assert_eq(float(m.get_shader_parameter(&"blur_lod")), 0.0)


func test_panel_hooks_high_contrast_reduce_motion_and_colourblind_still_work() -> void:
	var h := DecryptedHoloPanel.new()
	h.size = Vector2(300.0, 200.0)
	add_child_autofree(h)
	h.state_override = RcLookQualityState.make(2, false, false, true)
	var m := h.get_node("Glass").material as ShaderMaterial
	assert_eq(float(m.get_shader_parameter(&"glass_alpha")), 1.0, "high contrast: opaque")
	assert_eq(m.get_shader_parameter(&"deep"), HighContrast.BG, "on the high-contrast black")
	assert_gt(float(m.get_shader_parameter(&"edge_px")), RcLookHolo.config().edge_px, "a thicker edge")
	h.state_override = RcLookQualityState.make(2, false, true)
	assert_eq(float(m.get_shader_parameter(&"band_roll")), 0.0, "reduce motion: bands held")
	# colour-blind mode is a post filter over the final frame; the holo's own colours do not change, and its cues
	# (the cut ring, the kinked crack, the stamp's word) are shapes
	var s := RcLookQualityState.make(2)
	s.colorblind = &"deutan"
	assert_eq(RcLookHolo.settings(s), _s(2), "colour-blind mode leaves the holo's settings alone")


func test_the_old_copy_is_gone() -> void:
	assert_false(FileAccess.file_exists(OLD_SHADER), "decrypted_holo.gdshader is deleted")
	assert_false(FileAccess.get_file_as_string("res://scripts/ui/kit/materials/decrypted_holo_panel.gd").contains(OLD_SHADER))
