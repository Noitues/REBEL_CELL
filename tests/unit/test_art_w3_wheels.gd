extends GutTest
## Art pass W3 (ART_BIBLE §6.1, §6.2, §3.5, §7.1, §8, §10, §11 Combat, §12): wheel hardware
## and combat presentation. Presentation only: every assert reads the views, never a rule.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test_art_w3"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


func _combat(enemy: StringName = &"compliance_officer", scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(SCENE).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(enemy, 5)
	await _frames()
	return scene


func _enemy_view(scene: Control) -> WheelView:
	return scene._enemy_views.values()[0]


# --- 1. Bezel ownership (§6.1) -----------------------------------------------------------------

func test_the_bezel_says_who_owns_the_wheel() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	var ev := _enemy_view(scene)
	assert_eq(WheelBezel.owner_of(pv.look), WheelBezel.Owner.OPERATIVE, "the operative's bezel")
	assert_eq(pv.look["rim"], Palette.CELL_PINK, "a CELL_PINK rim")
	assert_eq(WheelBezel.owner_of(ev.look), WheelBezel.Owner.ENEMY, "an enemy's bezel")
	var corp := ev._corporation_of(ev.combatant)
	assert_eq(ev.look["rim"], Palette.corp_color(corp), "machined in its corp hue")
	assert_eq(int(ev.look["pattern"]), Palette.corp_pattern_id(corp), "with its corp pattern")
	assert_ne(int(ev.look["pattern"]), CorpPattern.Kind.NONE, "the enemy has a pattern")


func test_owners_differ_in_shape_not_only_colour() -> void:
	var c := Vector2(200, 200)
	assert_eq(WheelBezel.sticker_polys(c, 100.0, 126.0).size(), WheelBezel.STICKERS, "paper stickers on the operative's bezel")
	assert_eq(WheelBezel.notch_cuts(c, 126.0).size(), WheelBezel.NOTCHES, "notches cut into the enemy's rim")
	var outline := WheelBezel.notch_outline(c, 126.0)
	var near := INF
	for p in outline:
		near = minf(near, p.distance_to(c))
	assert_almost_eq(near, 126.0 - WheelBezel.NOTCH_DEPTH, 0.01, "the teeth are NOTCH_DEPTH deep")
	# Greyscale: the stickers are light paper on dark metal.
	assert_gt(Palette.luminance(Palette.PAPER) - Palette.luminance(Palette.NIGHT_BLOCK), 0.5, "stickers read in greyscale")


func test_the_portraits_have_their_places() -> void:
	var scene := await _combat()
	var pv: WheelView = scene._player_view
	var ev := _enemy_view(scene)
	var inset := pv.inset_rect()
	assert_true(inset.has_area(), "the operative's Polaroid inset")
	var c := pv._center()
	for p in [inset.position, inset.end, Vector2(inset.end.x, inset.position.y), Vector2(inset.position.x, inset.end.y)]:
		assert_lt((p as Vector2).distance_to(c), pv.hub_radius(), "inside the hub")
	assert_lt(inset.get_center().y, c.y, "at the hub's top")
	assert_false(ev.inset_rect().has_area(), "an enemy has no inset")
	var badge := ev.badge_rect()
	assert_true(badge.has_area(), "the enemy's portrait above its bezel")
	assert_lt(badge.end.y, ev._center().y - ev.needle_reach(), "above every needle's reach")
	assert_false(badge.intersects(ev._intent_rect_local()), "never under the tag")
	assert_false(pv.badge_rect().has_area(), "the operative has no badge")
	var ext := pv.hub_text_extent()
	assert_gt(pv._center().y + ext.x, inset.end.y, "the name sits under the inset")


func test_focus_brackets_only_mark_the_target() -> void:
	var scene := await _combat()
	assert_false(scene._player_view.highlighted, "the operative's own wheel is never bracketed")
	var targeted := 0
	for v in scene._enemy_views.values():
		if (v as WheelView).highlighted:
			targeted += 1
			assert_eq((v as WheelView).combatant.id, scene.engine.state().target_id, "the bracketed wheel is the target")
	assert_eq(targeted, 1, "one target")


# --- 2. Class identity (§6.1, §7.1) -------------------------------------------------------------

const CLASSES: Array[StringName] = [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]


func test_every_class_has_its_own_ornament_pattern_and_glyph() -> void:
	assert_eq(Palette.CLASS_ACCENTS.keys().size(), CLASSES.size(), "the eight §7.1 classes")
	for key in ["ornament", "hub_pattern", "hub_glyph"]:
		var seen := {}
		for c in CLASSES:
			var look := WheelBezel.operative_look(c)
			assert_ne(look[key], WheelBezel.PLAIN, "%s has a %s" % [c, key])
			assert_false(seen.has(look[key]), "%s: no two classes share a %s" % [c, key])
			seen[look[key]] = c
	for c in CLASSES:
		assert_eq(WheelBezel.operative_look(c)["accent"], Palette.class_accent(c), "%s's accent" % c)


func test_class_bezels_differ_pairwise_in_shape() -> void:
	var at := Vector2(200, 200)
	var keys := {}
	for c in CLASSES:
		var look := WheelBezel.operative_look(c)
		var k := "%s|%s|%s" % [WheelBezel.marks_key(WheelBezel.ornament_marks(look, at, 100.0, 126.0)),
			WheelBezel.marks_key(WheelBezel.hub_marks(look, at, 60.0)), WheelBezel.marks_key(WheelBezel.glyph_marks(look["hub_glyph"], at, 10.0))]
		assert_false((WheelBezel.ornament_marks(look, at, 100.0, 126.0).lines as Array).is_empty() and (WheelBezel.ornament_marks(look, at, 100.0, 126.0).dots as Array).is_empty()
			and (WheelBezel.ornament_marks(look, at, 100.0, 126.0).polys as Array).is_empty(), "%s draws an ornament" % c)
		for other in keys:
			assert_ne(k, keys[other], "%s and %s never share a bezel" % [c, other])
		keys[c] = k
	# Pairwise per part too: the critique's pairs (Botnet/Hivemind, Rigger/Overclocker) apart.
	for part in ["ornament", "hub"]:
		var seen := {}
		for c in CLASSES:
			var look := WheelBezel.operative_look(c)
			var m := WheelBezel.ornament_marks(look, at, 100.0, 126.0) if part == "ornament" else WheelBezel.hub_marks(look, at, 60.0)
			var key := WheelBezel.marks_key(m)
			assert_false(seen.has(key), "%s %s is unique" % [c, part])
			seen[key] = true


func test_the_ghost_flicker_is_ambient_and_rests_under_reduce_effects() -> void:
	var look := WheelBezel.operative_look(&"ghost")
	assert_true(WheelBezel.is_ambient(look), "the Ghost's rim flickers (T0)")
	assert_eq(VfxTier.of(&"bezel_ambient"), VfxTier.T0, "a T0 loop")
	assert_gte(Motion.seconds(&"bezel_ambient"), VfxTier.T0_MIN_PERIOD, "slow: at least the T0 period")
	assert_eq(float(WheelBezel.ornament_marks(look, Vector2.ZERO, 100.0, 126.0, 0.0).alpha), 1.0, "at rest the rim is whole")
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	var v := WheelView.new()
	v.look = look
	assert_false(v.ambient_on(), "static under reduce effects")
	v.free()
	Settings.reduce_effects = was
	assert_false(WheelBezel.is_ambient(WheelBezel.operative_look(&"breaker")), "rivets don't move")
