extends GutTest
## Art pass W6 (ART_BIBLE 8): each slice type has its own hit shape, so an outcome reads
## without colour (crit shatter, attack slash, shield / defend hex plates, evade smear,
## afflict glitch crawl, heal plus signs, miss static). Every slice type maps to one; each
## plays within its tier (T2, T3 for a crit) and is its end state at once headless and
## under reduce effects; the layer's existing hit triggers play the shape of their kind.

var _reduce: bool


func before_each() -> void:
	_reduce = Settings.reduce_effects
	Motion.use_config(null)


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	Motion.force_live = false


func _layer() -> CombatFxLayer:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var layer := CombatFxLayer.new()
	holder.add_child(layer)
	return layer


func test_every_slice_type_maps_to_a_hit_shape() -> void:
	for t in RC.SliceType.values():
		assert_true(CombatFxLayer.HIT_BY_SLICE.has(t), "slice type %d has a hit shape" % t)
		assert_true(CombatFxLayer.HIT_KINDS.has(CombatFxLayer.hit_kind(t)), "and it is one of the seven")
	assert_eq(CombatFxLayer.hit_kind(RC.SliceType.ATTACK, true), CombatFxLayer.HIT_CRIT, "a crit landing shatters")
	var expect := {RC.SliceType.CRIT: &"crit", RC.SliceType.ATTACK: &"attack", RC.SliceType.DEFEND: &"shield", RC.SliceType.SHIELD: &"shield",
		RC.SliceType.EVADE: &"evade", RC.SliceType.AFFLICT: &"afflict", RC.SliceType.HEAL: &"heal", RC.SliceType.MISS: &"miss"}
	for t in expect:
		assert_eq(CombatFxLayer.hit_kind(t), expect[t], "ART_BIBLE 8's shape for slice type %d" % t)
	# Seven distinct shapes, each with its own motion entry and a tier (T3 only for a crit).
	assert_eq(CombatFxLayer.HIT_KINDS.size(), 7)
	for kind in CombatFxLayer.HIT_KINDS:
		var id: StringName = CombatFxLayer.HIT_MOTION[kind]
		assert_true(Motion.has(id) and UiMotionData.REQUIRED_IDS.has(id), "%s has a required entry" % id)
		assert_eq(VfxTier.of(id), VfxTier.T3 if kind == CombatFxLayer.HIT_CRIT else VfxTier.T2, "%s's tier" % kind)
		assert_true(VfxTier.fits(Motion.entry(id)), "%s runs within its tier" % kind)


func test_each_hit_shape_plays_within_its_tier() -> void:
	var layer := _layer()
	Motion.force_live = true
	for kind in CombatFxLayer.HIT_KINDS:
		assert_true(layer.hit_vfx(Vector2(300, 300), kind), "%s plays" % kind)
	assert_eq(layer.hit_kinds_playing(), CombatFxLayer.HIT_KINDS, "one sprite per shape")
	for s in layer.sprites:
		var tier := VfxTier.of(CombatFxLayer.HIT_MOTION[s["hit"]])
		assert_true(float(s["dur"]) <= VfxTier.MAX_SECONDS[tier] + 0.0001, "%s within its tier's time" % s["hit"])
		assert_true(float(s["fill"]) <= VfxTier.MAX_FLASH_ALPHA[tier] + 0.0001, "%s's fill within its tier's alpha" % s["hit"])
	assert_eq(layer.sprites[1]["color"], Palette.slice_color(RC.SliceType.ATTACK), "in its slice colour by default")
	assert_false(layer.hit_vfx(Vector2(300, 300), &"nope"), "an unknown shape plays nothing")
	# The layer draws them (a frame with every shape, no error) and they end.
	layer.queue_redraw()
	await get_tree().process_frame
	await BoundedWait.until(get_tree(), func() -> bool: return layer.hit_kinds_playing().is_empty(),
		BoundedWait.motion_limit([&"hit_vfx_crit", &"hit_vfx_heal"]))
	assert_true(layer.hit_kinds_playing().is_empty(), "every shape ends")


func test_hit_shapes_are_the_end_state_at_once_headless_and_under_reduce_effects() -> void:
	var layer := _layer()
	for kind in CombatFxLayer.HIT_KINDS:
		assert_false(layer.hit_vfx(Vector2(300, 300), kind), "headless: %s shows nothing" % kind)
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	for kind in CombatFxLayer.HIT_KINDS:
		assert_false(layer.hit_vfx(Vector2(300, 300), kind), "reduce effects: %s shows nothing" % kind)
	assert_false(layer.busy(), "nothing left running")


func test_the_layers_hit_triggers_play_their_kinds_shape() -> void:
	var layer := _layer()
	Motion.force_live = true
	# A crit number shatters; a heal number rises in plus signs; a guard number shows its guard.
	layer.number(Vector2(300, 300), "-12", Palette.CELL_PINK, &"number_float", Vector2.UP, true)
	assert_true(layer.hit_kinds_playing().has(CombatFxLayer.HIT_CRIT), "crit: shattered glass")
	layer.clear()
	layer.number(Vector2(300, 300), "+4 HP", Palette.CELL_ACID, &"heal_number")
	assert_eq(layer.hit_kinds_playing(), [CombatFxLayer.HIT_HEAL] as Array[StringName], "heal: plus signs")
	layer.clear()
	layer.number(Vector2(300, 300), "+3", Palette.NET_CYAN, &"block_number", Vector2.UP, false, -1.0, -1, "", 0.0, RC.SliceType.DEFEND)
	assert_eq(layer.hit_kinds_playing(), [CombatFxLayer.HIT_SHIELD] as Array[StringName], "block: hex plates")
	layer.clear()
	# What gets through travels in with a slash; a travelling heal with plus signs.
	layer.travel_number(Vector2(300, 300), Vector2(300, 400), "-5", Palette.CELL_PINK, false, 24, "b")
	assert_eq(layer.hit_kinds_playing(), [CombatFxLayer.HIT_ATTACK] as Array[StringName], "a hit: a slash")
	layer.clear()
	layer.travel_number(Vector2(300, 300), Vector2(300, 400), "+5 HP", Palette.CELL_ACID, false, 24, "b")
	assert_eq(layer.hit_kinds_playing(), [CombatFxLayer.HIT_HEAL] as Array[StringName])
	layer.clear()
	# A hit soaked or evaded where it struck: the guard's shape.
	layer.impact(Vector2(300, 300), "0", RC.SliceType.EVADE, Palette.NET_CYAN)
	assert_eq(layer.hit_kinds_playing(), [CombatFxLayer.HIT_EVADE] as Array[StringName], "evaded: an afterimage smear")
	layer.clear()
	var eq := [{"icon": RC.SliceType.ATTACK, "text": "8"}, {"icon": RC.SliceType.SHIELD, "text": "8", "sep": "-"}, {"text": "0", "sep": "="}]
	layer.impact(Vector2(300, 300), "0", -1, Palette.NET_CYAN, 0.0, eq)
	assert_eq(layer.hit_kinds_playing(), [CombatFxLayer.HIT_SHIELD] as Array[StringName], "soaked: hex plates")
	layer.clear()
	# A status landing on a slice: the afflict's glitch crawl.
	layer.stamp(Vector2(300, 300), "X", Palette.CELL_PINK, 0.2)
	assert_eq(layer.hit_kinds_playing(), [CombatFxLayer.HIT_AFFLICT] as Array[StringName], "afflict: a glitch crawl")
	layer.clear()
