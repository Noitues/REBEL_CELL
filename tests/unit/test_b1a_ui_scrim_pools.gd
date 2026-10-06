extends GutTest
## B1a (M14 integration review D1, D19, section d; DECISIONS "B1a — UI scrim pools, light spill,
## panel shadows (integration review)"): the shared layer that darkens the world under the UI
## (UiScrimPools) and its light spill and panel shadows (UiSpillShadows). The pools darken the
## world under registered rects by the configured amount and nowhere else; shadows and spill
## fall under and round their elements; city quality tier 0 keeps the pools only; UI words over
## the pooled world keep their contrast; the combat scene registers its wheels, bars, panels and
## SEND IT.

const LOOK: UiScrimLook = preload("res://content/config/ui_scrim_look.tres")
const COMBAT := "res://scenes/combat/combat_scene.tscn"
## The layer's size: the look's reference height, so its px lengths are 1:1 here.
const SCREEN := Vector2(1920, 1080)
const STILLS := "res://assets/backdrops/combat/"
const CORPS: Array[String] = ["meridian", "solace", "halcyon", "orbital", "rebel_cell"]
## WCAG 2.1 floor for words.
const TEXT_MIN := 4.5
const STILL_STEP := 6
const EPS := 0.002
const FIXTURES := "res://tests/fixtures/ui_scrim/"
const ScrimLuma := preload("res://tools/visual_qa/scrim_luma.gd")
## The art director's acceptance (B1a review, 2026-10-06): a wheel pool's mean luma at most 0.6 x
## the backdrop between the wheels; a map's pool margin and foot band 0.55 to 0.65 of the open city.
const RING_VS_BETWEEN_MAX := 0.6
const MAP_RATIO := Vector2(0.55, 0.65)

var _settings: Dictionary = {}


## A wheel stand-in: what UiScrimPools reads of a WheelView.
class FakeWheel:
	extends Control
	var combatant: Variant = 1
	var radius: float = 100.0

	func global_center() -> Vector2:
		return global_position + size * 0.5

	func disc_radius() -> float:
		return radius


func before_all() -> void:
	_settings = Settings.snapshot()


func after_each() -> void:
	Settings.restore(_settings)


func after_all() -> void:
	Settings.restore(_settings)


func _frames(n: int = 2) -> void:
	for i in n:
		await get_tree().process_frame


## A host the size of the screen with a world and a scrim after it.
func _host() -> Dictionary:
	var host: Control = add_child_autofree(Control.new())
	host.size = SCREEN
	var world := ColorRect.new()
	world.name = "World"
	world.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	host.add_child(world)
	var scrim := UiScrimPools.attach_after(world)
	return {"host": host, "world": world, "scrim": scrim}


func _panel(host: Control, rect: Rect2) -> Control:
	var c := Control.new()
	host.add_child(c)
	c.position = rect.position
	c.size = rect.size
	return c


# --- Pools ----------------------------------------------------------------------------------

func test_a_panel_pool_darkens_the_world_under_it_by_the_configured_amount_and_nowhere_else() -> void:
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var rect := Rect2(200, 300, 400, 200)
	UiScrimPools.mark_panel(_panel(h["host"], rect))
	scrim.refresh()
	assert_eq(scrim.shapes.size(), 1, "one pool")
	assert_almost_eq(scrim.factor_at(rect.get_center()), LOOK.panel_pool_multiply, EPS, "under the panel: panel_pool_multiply")
	assert_almost_eq(scrim.factor_at(rect.position + Vector2(1, 1)), LOOK.panel_pool_multiply, EPS, "at its corner too")
	var m := LOOK.panel_pool_margin_px
	assert_almost_eq(scrim.factor_at(Vector2(rect.end.x + m * LOOK.panel_pool_hold * 0.95, rect.get_center().y)), LOOK.panel_pool_multiply, EPS,
		"held out to panel_pool_hold of the margin")
	var edge := scrim.factor_at(Vector2(rect.end.x + m * (1.0 + LOOK.panel_pool_hold) * 0.5, rect.get_center().y))
	assert_between(edge, LOOK.panel_pool_multiply + EPS, 1.0 - EPS, "then fading")
	assert_almost_eq(scrim.factor_at(Vector2(rect.end.x + m + 1.0, rect.get_center().y)), 1.0, EPS,
		"past the margin: the world untouched")
	assert_almost_eq(scrim.factor_at(Vector2(1700, 900)), 1.0, EPS, "elsewhere: untouched")


func test_a_wheel_pool_is_a_soft_disc_of_its_reach() -> void:
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var w := FakeWheel.new()
	(h["host"] as Control).add_child(w)
	w.position = Vector2(400, 300)
	w.size = Vector2(200, 200)
	scrim.add_wheels(func() -> Array: return [w])
	scrim.refresh()
	var c := Vector2(500, 400)
	assert_almost_eq(scrim.factor_at(c), LOOK.wheel_pool_multiply, EPS, "at the wheel's centre: wheel_pool_multiply")
	assert_almost_eq(scrim.factor_at(c), UiScrimPools.wheel_factor(0.0), EPS, "wheel_factor mirrors it")
	assert_almost_eq(scrim.factor_at(c + Vector2(w.radius, 0)), LOOK.wheel_pool_multiply, EPS, "at the rim: the pool is whole (it shows past the disc)")
	assert_almost_eq(scrim.factor_at(c + Vector2(w.radius * LOOK.wheel_pool_reach * 0.99, 0)), LOOK.wheel_pool_multiply, EPS,
		"held out to wheel_pool_reach x R (D1: 1.25 R)")
	var fading := scrim.factor_at(c + Vector2(w.radius * (LOOK.wheel_pool_reach + LOOK.wheel_pool_fade * 0.5), 0))
	assert_between(fading, LOOK.wheel_pool_multiply + EPS, 1.0 - EPS, "then fading over wheel_pool_fade x R")
	assert_almost_eq(fading, UiScrimPools.wheel_factor(LOOK.wheel_pool_reach + LOOK.wheel_pool_fade * 0.5), EPS, "wheel_factor mirrors it")
	assert_almost_eq(scrim.factor_at(c + Vector2(w.radius * (LOOK.wheel_pool_reach + LOOK.wheel_pool_fade) + 1.0, 0)), 1.0, EPS,
		"past it: untouched")
	w.combatant = null
	scrim.refresh()
	assert_true(scrim.shapes.is_empty(), "a wheel with no combatant has no pool")


func test_bands_lie_under_their_bars_and_fade_out_past_them() -> void:
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var top := _panel(h["host"], Rect2(500, 0, 900, 60))
	var hand := _panel(h["host"], Rect2(300, 820, 1200, 260))
	UiScrimPools.mark_band(top, SIDE_TOP)
	UiScrimPools.mark_band(hand, SIDE_BOTTOM)
	scrim.refresh()
	assert_almost_eq(scrim.factor_at(Vector2(20, 30)), LOOK.band_multiply, EPS, "the top band runs the whole width under the bar")
	assert_almost_eq(scrim.factor_at(Vector2(1900, 1000)), LOOK.band_multiply, EPS, "the hand's band reaches the screen's foot")
	assert_almost_eq(scrim.factor_at(Vector2(960, 60 + LOOK.band_reach_top_px * 2.0)), 1.0, EPS, "past the top band's reach: untouched")
	assert_almost_eq(scrim.factor_at(Vector2(960, 820 - LOOK.band_reach_bottom_px * 2.0)), 1.0, EPS, "past the hand band's reach: untouched")
	assert_almost_eq(scrim.factor_at(Vector2(960, 820 - LOOK.band_reach_bottom_px * LOOK.band_hold * 0.95)), LOOK.band_multiply, EPS,
		"held over band_hold of the reach")
	var fade := scrim.factor_at(Vector2(960, 820 - LOOK.band_reach_bottom_px * (1.0 + LOOK.band_hold) * 0.5))
	assert_between(fade, LOOK.band_multiply + EPS, 1.0 - EPS, "then fading")


func test_hidden_freed_and_world_marks_take_no_pool() -> void:
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var hidden := _panel(h["host"], Rect2(0, 0, 100, 100))
	hidden.visible = false
	UiScrimPools.mark_panel(hidden)
	var gone := _panel(h["host"], Rect2(200, 0, 100, 100))
	UiScrimPools.mark_panel(gone)
	# A mark inside the world (drawn before the layer) is world, not UI.
	var in_world := Control.new()
	(h["world"] as Control).add_child(in_world)
	in_world.size = Vector2(50, 50)
	UiScrimPools.mark_panel(in_world)
	scrim.refresh()
	assert_eq(scrim.shapes.size(), 1, "only the shown UI panel")
	gone.free()
	scrim.refresh()
	assert_true(scrim.shapes.is_empty(), "a freed panel drops out")
	hidden.visible = true
	scrim.refresh()
	assert_eq(scrim.shapes.size(), 1, "shown again: its pool is back")


func test_a_mark_belongs_to_the_nearest_layer() -> void:
	var outer := _host()
	var inner_host := Control.new()
	(outer["host"] as Control).add_child(inner_host)
	inner_host.size = SCREEN
	var inner_world := Control.new()
	inner_host.add_child(inner_world)
	var inner := UiScrimPools.attach_after(inner_world)
	var p := _panel(inner_host, Rect2(100, 100, 200, 100))
	UiScrimPools.mark_panel(p)
	(outer["scrim"] as UiScrimPools).refresh()
	inner.refresh()
	assert_eq(inner.shapes.size(), 1, "the inner layer (a fight inside a run page) pools its own panel")
	assert_true((outer["scrim"] as UiScrimPools).shapes.is_empty(), "the outer layer leaves it (no double darkening)")


func test_mark_panels_in_marks_the_outermost_windows_only() -> void:
	var root := Control.new()
	add_child_autofree(root)
	var outer := TerminalWindow.new("A")
	root.add_child(outer)
	var nested := TerminalWindow.new("B")
	outer.body.add_child(nested)
	var other := TerminalWindow.new("C")
	root.add_child(other)
	UiScrimPools.mark_panels_in(root, ["TerminalWindow"] as Array[String], false)
	assert_true(outer.is_in_group(UiScrimPools.PANEL_GROUP), "the outer window")
	assert_true(other.is_in_group(UiScrimPools.PANEL_GROUP), "a second window")
	assert_false(nested.is_in_group(UiScrimPools.PANEL_GROUP), "a window inside a marked one is not marked again")
	assert_false(bool(outer.get_meta(UiScrimPools.META_POOL)), "pool off as asked")
	assert_true(bool(outer.get_meta(UiScrimPools.META_SHADOW)), "shadow on")


func test_pools_cap_the_world_s_saturation_and_keep_its_luma() -> void:
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var rect := Rect2(200, 300, 400, 200)
	UiScrimPools.mark_panel(_panel(h["host"], rect))
	scrim.refresh()
	var c := Color(0.15, 0.6, 0.45)  # B2: under the emissive band (its brightest channel < emissive_from)
	var l := ScrimLuma.luma(c)
	var under := scrim.apply_at(rect.get_center(), c)
	assert_almost_eq(ScrimLuma.luma(under), l * LOOK.panel_pool_multiply, 0.002, "the pool multiplies the luma")
	# Chroma: the channels' spread round the luma, scaled by pool_saturation (D1: 0.6) then the pool.
	assert_almost_eq(under.g - under.r, (c.g - c.r) * LOOK.pool_saturation * LOOK.panel_pool_multiply, 0.002, "saturation capped")
	# B2 (art director): an emissive (a sign, a lit window) is never capped, only darkened.
	var neon := Color(1.0, 0.24, 0.66)
	var lit := scrim.apply_at(rect.get_center(), neon)
	assert_almost_eq(lit.r - lit.g, (neon.r - neon.g) * LOOK.panel_pool_multiply, 0.002, "emissive: chroma kept")
	var out := scrim.apply_at(Vector2(1700, 900), c)
	assert_true(out.is_equal_approx(c), "outside every shape: untouched")
	assert_lt(LOOK.pool_saturation, 1.0, "a cap")
	assert_true(FileAccess.get_file_as_string(UiScrimPools.SHADER.resource_path).contains("pool_saturation"), "the shader applies it")


func test_world_items_in_the_lift_group_draw_over_the_layer() -> void:
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var world: Control = h["world"]
	var map := Control.new()
	map.name = "Map"
	world.add_child(map)
	map.add_to_group(UiScrimPools.LIFT_GROUP)
	var card := Control.new()
	map.add_child(card)
	card.size = Vector2(100, 100)
	UiScrimPools.mark_panel(card)
	var ui := _panel(h["host"], Rect2(0, 0, 50, 50))
	scrim.refresh()
	assert_true(scrim.lifted.has(map), "lifted")
	assert_false(map.z_as_relative, "its own z")
	assert_eq(world.z_index, UiScrimPools.WORLD_Z, "the world sinks under the layer")
	assert_eq(scrim.z_index, UiScrimPools.SCRIM_Z, "the layer over the world")
	assert_gt(map.z_index, scrim.z_index, "the lifted item over the layer")
	assert_eq(map.z_index, ui.z_index, "at the UI's own z: under the UI by tree order")
	assert_true(scrim.owns(card), "a panel inside a lifted item belongs to the layer")
	assert_eq(scrim.shapes.size(), 1, "and pools")
	var overlay := CityMapOverlay.new()
	assert_true(overlay.is_in_group(UiScrimPools.LIFT_GROUP), "the city map (markers, labels, pencil, TARGET) is lifted")
	assert_true(overlay.is_in_group(UiScrimPools.NETWORK_GROUP), "and its ground decal network kept")
	overlay.free()


func test_the_ground_decal_network_is_kept_out_of_the_pools() -> void:
	var net := CityNetworkData.new()
	net.segments.append({"a": Vector3(0, 0, 0), "b": Vector3(100, 0, 0), "color": Color.WHITE, "flags": 0, "u0": 0.0, "len": 100.0, "width": 1.0})
	net.nodes.append({"world": Vector3(50, 0, 50), "color": Color.WHITE, "big": false, "state": 0, "tier": 1})
	# px -> ground: identity, 1 BU per decal px.
	var k := UiScrimPools.keep_from(net, Vector2.ZERO, Vector2(1, 0), Vector2(0, 1), 1.0, 0.0)
	assert_almost_eq(UiScrimPools.keep_at(Vector2(40, 0), k), 1.0, EPS, "on a link: kept")
	assert_almost_eq(UiScrimPools.keep_at(Vector2(50, 50), k), 1.0, EPS, "on a node: kept")
	assert_almost_eq(UiScrimPools.keep_at(Vector2(40, 30), k), 0.0, EPS, "off the network: pooled")
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	UiScrimPools.mark_panel(_panel(h["host"], Rect2(-10, -10, 20, 20)))
	scrim.refresh()
	scrim.keep = k
	assert_almost_eq(scrim.factor_at(Vector2(40, 0)), 1.0, EPS, "the link at full strength inside the pool")
	assert_almost_eq(scrim.factor_at(Vector2(40, 30)), LOOK.panel_pool_multiply, EPS, "the city beside it pooled")


# --- Luma on the real screens (fixtures) --------------------------------------------------------

## The settled world under a screen's scrim, UI hidden (tests/fixtures/ui_scrim/<screen>.png, the
## windowed perf pack's scrim_luma_<screen> probe at 1920x1080 tier 2, 480x270) and the scrim's
## sources then (<screen>.json): the layer's maths applied to it now.
func _fixture_luma(screen: String) -> Dictionary:
	var img := Image.load_from_file(ProjectSettings.globalize_path(FIXTURES + screen + ".png"))
	var src: Variant = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path(FIXTURES + screen + ".json")))
	assert_not_null(img, "%s fixture" % screen)
	assert_not_null(src, "%s sources" % screen)
	if img == null or src == null:
		return {}
	return ScrimLuma.measure(img, null, ScrimLuma.from_json(src))


func test_combat_wheel_pools_read_against_the_backdrop_between_the_wheels() -> void:
	var m := _fixture_luma("combat_start")
	if m.is_empty():
		return
	assert_gt(int(m["n_ring"]), 500, "the pools' rings measured")
	assert_gt(int(m["n_between"]), 500, "the backdrop between the wheels measured")
	assert_lte(float(m["ring_vs_between"]), RING_VS_BETWEEN_MAX, "mean luma in the wheel pools <= 0.6 x between the wheels (%.2f)" % m["ring_vs_between"])


func test_map_pages_pool_margins_and_foot_bands_read() -> void:
	for screen in ["hq", "raid_setup"]:
		var m := _fixture_luma(screen)
		if m.is_empty():
			continue
		assert_gt(int(m["n_margin"]), 500, "%s: panel pool margins measured" % screen)
		assert_gt(int(m["n_foot"]), 300, "%s: the foot band measured" % screen)
		assert_between(float(m["margin_same"]), MAP_RATIO.x, MAP_RATIO.y, "%s: city luma in the panels' pool margins vs open (%.2f)" % [screen, m["margin_same"]])
		assert_between(float(m["foot_same"]), MAP_RATIO.x, MAP_RATIO.y, "%s: city luma under the foot band vs open (%.2f)" % [screen, m["foot_same"]])


# --- Shadows and spill ----------------------------------------------------------------------

func _quality(tier: int) -> void:
	Settings.set_city_quality(tier)


func test_a_panel_casts_its_soft_drop_shadow_under_it() -> void:
	_quality(2)
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var rect := Rect2(600, 400, 300, 200)
	UiScrimPools.mark_panel(_panel(h["host"], rect), false)
	scrim.refresh()
	scrim.spill.refresh()
	assert_true(scrim.shapes.is_empty(), "pool off: no pool")
	assert_eq(scrim.spill.shadows.size(), 1, "one shadow")
	var drop := LOOK.shadow_offset_px
	assert_almost_eq(scrim.spill.shadow_at(rect.get_center()), 1.0 - LOOK.shadow_alpha, EPS, "under the panel: black at shadow_alpha")
	var below := Vector2(rect.get_center().x, rect.end.y + drop.y * 0.5)
	assert_almost_eq(scrim.spill.shadow_at(below), 1.0 - LOOK.shadow_alpha, EPS, "the drop shows under its foot")
	var soft := scrim.spill.shadow_at(Vector2(rect.get_center().x, rect.end.y + drop.y + LOOK.shadow_soft_px * 0.5))
	assert_between(soft, 1.0 - LOOK.shadow_alpha, 1.0, "its soft edge fades")
	assert_almost_eq(scrim.spill.shadow_at(Vector2(rect.get_center().x, rect.end.y + drop.y + LOOK.shadow_soft_px + 1.0)), 1.0, EPS,
		"past the soft edge: nothing")
	assert_almost_eq(scrim.spill.shadow_at(Vector2(100, 100)), 1.0, EPS, "elsewhere: nothing")


func test_an_emissive_element_spills_its_colour_round_it_out_to_its_reach() -> void:
	_quality(2)
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var rect := Rect2(1400, 850, 300, 120)
	UiSpillShadows.mark_spill(_panel(h["host"], rect), Palette.CELL_PINK)
	scrim.spill.refresh()
	assert_eq(scrim.spill.spills.size(), 1, "one spill")
	var radius := rect.size.length() * 0.5
	var reach := radius * (LOOK.spill_radius_scale - 1.0)
	var under := scrim.spill.spill_at(rect.get_center())
	assert_almost_eq(under.r, Palette.CELL_PINK.r * LOOK.spill_strength, 0.01, "under it: spill_strength of its colour")
	assert_almost_eq(under.b, Palette.CELL_PINK.b * LOOK.spill_strength, 0.01, "the colour's own hue")
	assert_between(LOOK.spill_strength, 0.2, 0.3, "D19: 20 to 30 %")
	var at_edge := scrim.spill.spill_at(Vector2(rect.position.x - 0.5, rect.get_center().y))
	assert_between(at_edge.r, 0.0001, under.r, "at its edge: lit, less than under it (no box edge)")
	var corner := scrim.spill.spill_at(rect.position + Vector2(-1, -1))
	assert_lt(corner.r, at_edge.r, "its corner lit less than its side's middle (a stadium, not a box)")
	var mid := scrim.spill.spill_at(Vector2(rect.position.x - reach * 0.5, rect.get_center().y))
	assert_between(mid.r, 0.0001, at_edge.r, "half its reach out: fading")
	var out := scrim.spill.spill_at(Vector2(rect.position.x - reach - 1.0, rect.get_center().y))
	assert_almost_eq(out.r + out.g + out.b, 0.0, EPS, "past its reach (spill_radius_scale x its radius): no light")


func test_a_pencil_stroke_spills_along_its_line() -> void:
	_quality(2)
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var line := PackedVector2Array([Vector2(200, 500), Vector2(500, 500), Vector2(800, 500)])
	scrim.spill.add_spill_source(func() -> Array: return [line], Palette.PENCIL_PLAN)
	scrim.spill.refresh()
	assert_eq(scrim.spill.spills.size(), 2, "the polyline's segments")
	var on := scrim.spill.spill_at(Vector2(650, 500))
	assert_almost_eq(on.r, Palette.PENCIL_PLAN.r * LOOK.spill_strength, 0.01, "on the line: spill_strength")
	var off := scrim.spill.spill_at(Vector2(650, 500 + LOOK.line_glow_px + 1.0))
	assert_almost_eq(off.r, 0.0, EPS, "past line_glow_px: no light")


func test_tier_0_keeps_the_pools_and_drops_spill_and_shadows() -> void:
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var p := _panel(h["host"], Rect2(600, 400, 300, 200))
	UiScrimPools.mark_panel(p)
	UiSpillShadows.mark_spill(p, Palette.CELL_PINK)
	for tier in [0, 1, 2]:
		_quality(tier)
		scrim.refresh()
		scrim.spill.refresh()
		assert_eq(scrim.shapes.size(), 1, "tier %d: the pool stays (contrast)" % tier)
		assert_eq(scrim.spill.shadows.size(), 1 if UiScrimLook.flag_at(LOOK.tier_shadows, tier) else 0, "tier %d: shadows per tier_shadows" % tier)
		assert_eq(scrim.spill.spills.size(), 1 if UiScrimLook.flag_at(LOOK.tier_spill, tier) else 0, "tier %d: spill per tier_spill" % tier)
	assert_false(UiScrimLook.flag_at(LOOK.tier_spill, 0), "tier 0 draws no spill")
	assert_false(UiScrimLook.flag_at(LOOK.tier_shadows, 0), "tier 0 draws no shadows")


func test_reduce_effects_changes_nothing_the_layer_is_its_own_end_state() -> void:
	_quality(2)
	var h := _host()
	var scrim: UiScrimPools = h["scrim"]
	var p := _panel(h["host"], Rect2(600, 400, 300, 200))
	UiScrimPools.mark_panel(p)
	UiSpillShadows.mark_spill(p, Palette.CELL_PINK)
	var probe := [Vector2(750, 500), Vector2(950, 500), Vector2(750, 640)]
	var looks: Array = []
	for reduce in [false, true]:
		Settings.set_reduce_effects(reduce)
		scrim.refresh()
		scrim.spill.refresh()
		var row: Array = []
		for q: Vector2 in probe:
			row.append([scrim.factor_at(q), scrim.spill.shadow_at(q), scrim.spill.spill_at(q)])
		looks.append(row)
	assert_eq(str(looks[0]), str(looks[1]), "static: the same look with and without reduce effects")
	for path in [UiScrimPools.SHADER.resource_path, UiSpillShadows.SHADOW_SHADER.resource_path, UiSpillShadows.SPILL_SHADER.resource_path]:
		assert_false(FileAccess.get_file_as_string(path).contains("TIME"), "%s has no clock" % path)


# --- Contrast -------------------------------------------------------------------------------

## The mean luminance of still `path` once the layer leaves `f` of it (it multiplies the encoded
## colour: the canvas blends in sRGB, no HDR 2D). The mean is what stands behind a word (S-ARENA's
## measure, "Parity fix — combat backdrop, round 2"): a word's own 2 px ink outline carries it
## past a lone neon pixel.
func _pooled_mean_luma(path: String, f: float) -> float:
	var img := Image.load_from_file(ProjectSettings.globalize_path(path))
	if img == null:
		return -1.0
	var ls: Array[float] = []
	for y in range(0, img.get_height(), STILL_STEP):
		for x in range(0, img.get_width(), STILL_STEP):
			var c := img.get_pixel(x, y)
			ls.append(Palette.luminance(Color(c.r * f, c.g * f, c.b * f)))
	var total := 0.0
	for l in ls:
		total += l
	return total / maxf(1.0, float(ls.size()))


static func _contrast_l(a: float, b: float) -> float:
	return (maxf(a, b) + 0.05) / (minf(a, b) + 0.05)


func test_ui_words_over_the_pooled_world_keep_their_contrast() -> void:
	# The words that stand on the world itself (stickers' captions, the system word under the
	# verb, pencil captions) in the paper white and the plan yellow, over every corporation's
	# backdrop (day and night) as a panel pool, a wheel pool and a band over a pool leave it.
	var words: Array[Color] = [Palette.PAPER, Palette.PENCIL_PLAN]
	var leaves := {"panel pool": LOOK.panel_pool_multiply, "wheel pool": LOOK.wheel_pool_multiply,
		"band + panel pool": LOOK.band_multiply * LOOK.panel_pool_multiply}
	var checked := 0
	for corp in CORPS:
		for kind in ["hq", "site"]:
			for time in ["night", "day"]:
				var path := "%s%s_%s_%s.jpg" % [STILLS, corp, kind, time]
				if not FileAccess.file_exists(path):
					continue
				checked += 1
				for what in leaves:
					var bg := _pooled_mean_luma(path, float(leaves[what]))
					assert_gte(bg, 0.0, "%s loads" % path)
					for w in words:
						var k := _contrast_l(Palette.luminance(w), bg)
						assert_gte(k, TEXT_MIN, "%s_%s_%s under a %s: %s words keep 4.5:1 (%.2f)" % [corp, kind, time, what, w.to_html(false), k])
	assert_gt(checked, 8, "the stills were checked")


# --- The combat scene's hookup ----------------------------------------------------------------

func test_the_fight_registers_its_wheels_bars_panels_and_send_it() -> void:
	_quality(2)
	AudioDirector.muted = true
	RunManager.save_slot = "gut_b1a_scrim"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames(3)
	var scrim: UiScrimPools = scene.scrim
	assert_not_null(scrim, "the fight has its layer")
	if scrim != null:
		assert_eq(scrim.get_index(), scene.heat_city.get_index() + 1, "right over the backdrop's Heat lights")
		assert_lt(scrim.get_index(), scene.hud_layer.get_index(), "under the wheels' HUD")
		scrim.refresh()
		scrim.spill.refresh()
		var discs := 0
		var bands := 0
		for s in scrim.shapes:
			discs += 1 if int(s["kind"]) == UiScrimPools.Kind.DISC else 0
			bands += 1 if int(s["kind"]) == UiScrimPools.Kind.BAND else 0
		var wheels := 0
		for v in scene._views():
			wheels += 1 if v.is_visible_in_tree() and v.combatant != null else 0
		assert_eq(discs, wheels, "a pool round each wheel")
		assert_eq(bands, 2, "a band under the TURN strip and one under the hand")
		assert_gte(scrim.spill.shadows.size(), 2, "the TURN strip and the RAM panel cast shadows")
		assert_gte(scrim.spill.spills.size(), 1, "SEND IT spills its pink")
		# The backdrop's own darkening moved to the layer: no double pools.
		assert_false(FileAccess.get_file_as_string("res://shaders/arena/combat_backdrop.gdshader").contains("pool_dark"),
			"the backdrop shader no longer darkens its pools itself")
	scene.skip_motion()
	await _frames(2)
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false
