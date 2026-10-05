extends GutTest
## ART-2 2C, cards and FX (ART_BIBLE v2 §3.15, §3.18, §3.20, §5.3-5.4, §6.3; DECISIONS "Art
## direction — ART-2 2C cards and FX"): the hit shake held to T2 (carry-over); every 2C
## effect has its ui_motion entry with a tier it fits, a REQUIRED_IDS line and a motion lab
## demo; the flash limiter holds every local flash to 3 a second and keeps the bits; D16,
## a card-caused effect stems from the card's slap point on its target wheel, never from the
## hand; reduce effects shows the end state (no FX added, nothing waits); the bits' arrival
## times are precomputed and deterministic; dissolve A's layout; the temporary label's
## dissolve; shard severity and the Heat city's bands from the campaign config.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const LAB_SCRIPT := "res://tools/design_lab/motion_lab.gd"
const SCREEN := Rect2(0, 0, 1280, 720)
## The 2C motion entries (each needs a tier it fits, a REQUIRED_IDS line and a lab demo).
const FX_IDS: Array[StringName] = [&"card_peel", &"card_slap_ring", &"hit_shards", &"hit_crit_streaks", &"hit_blocked_wall", &"block_wall",
	&"shield_hex", &"heal_inflow", &"evade_token", &"corrupt_apply", &"corrupt_tick", &"drone_deploy", &"drone_attack", &"drone_destroyed",
	&"enemy_defeated_bits", &"phase_change_bits", &"respin_bits", &"nudge_resist_bits", &"ram_gain_bits", &"temp_label",
	&"daemon_trigger", &"firmware_trigger", &"heat_city_beacon", &"heat_city_sweep"]
## Hits fired in one burst for the limiter test.
const BURST_HITS := 10

var _settings: Dictionary = {}
var _limiter_on: bool = true


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)
	Fx.apply_settings()


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art2_cards_fx"
	RunManager.scene_switching_enabled = false
	RunManager.reset()
	Motion.force_live = false
	_limiter_on = Fx.limiter.enabled


func after_each() -> void:
	Motion.use_config(null)
	Motion.force_live = false
	Settings.restore(_settings)
	Fx.apply_settings()
	Fx.limiter.enabled = _limiter_on
	Fx.limiter.reset()
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	Motion.force_live = true


func _layer() -> CombatFxLayer:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var fx := CombatFxLayer.new()
	holder.add_child(fx)
	return fx


func _combat() -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene):
		scene.skip_motion()
		scene.get_parent().queue_free()
	await _frames(2)


func _kinds(fx: CombatFxLayer, kind: String) -> Array:
	return fx.sprites.filter(func(s: Dictionary) -> bool: return String(s["kind"]) == kind)


# --- 2C.5 carry-over: the hit shake within T2 -------------------------------------------------

func test_hit_shake_is_held_to_t2() -> void:
	var tier := VfxTier.of(&"hit_shake")
	assert_eq(tier, VfxTier.T2, "a hit is T2")
	assert_true(Motion.amplitude(&"hit_shake") <= VfxTier.MAX_SHAKE_PX[tier], "the combat hit_shake is within T2's 2 px (was 3)")
	assert_eq(Motion.amplitude(&"hit_shake"), 2.0)


# --- Every effect: an entry, a tier it fits, REQUIRED_IDS, a lab demo ---------------------------

func test_every_2c_effect_has_its_entry_tier_and_demo() -> void:
	var demos: Dictionary = (load(LAB_SCRIPT) as GDScript).get_script_constant_map()["DEMOS"]
	for id in FX_IDS:
		assert_true(Motion.has(id), "%s is in ui_motion.tres" % id)
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(VfxTier.fits(Motion.entry(id)), "%s runs within its tier (%s)" % [id, VfxTier.NAMES[VfxTier.of(id)]])
		assert_true(demos.has(id), "%s has a motion lab demo" % id)
		assert_ne(String((demos.get(id, ["pop"]) as Array)[0]), "pop", "%s plays on the real piece, not a stand-in pop" % id)
	assert_eq(VfxTier.of(&"enemy_defeated_bits"), VfxTier.T3, "enemy defeated is a T3 moment")
	assert_eq(VfxTier.of(&"phase_change_bits"), VfxTier.T3, "a phase change is a T3 moment")
	assert_eq(VfxTier.of(&"hit_crit_streaks"), VfxTier.T3, "a crit is T3")
	assert_eq(VfxTier.of(&"ram_gain_bits"), VfxTier.T1, "RAM gain is T1 feedback")
	assert_eq(VfxTier.of(&"heat_city_beacon"), VfxTier.T0, "Heat lights are T0 ambient")


# --- The flash limiter (<= 3 a second) ------------------------------------------------------------

func test_the_flash_limiter_holds_local_fx_flashes_to_three_a_second() -> void:
	_live()
	Fx.limiter.enabled = true
	Fx.limiter.reset()
	var shown_before := Fx.flashes_shown.size()
	var fx := _layer()
	var center := Vector2(600, 360)
	var targets: Array[Vector2] = [center + Vector2(80, 80)]
	for k in BURST_HITS:
		fx.hit_shards(center + Vector2(0, -100), center, 100.0, targets, Palette.CELL_PINK, 7, false)
	fx.corrupt_tick(center + Vector2(40, -40), center, 100.0, targets)
	var shown: Array[float] = []
	for k in range(shown_before, Fx.flashes_shown.size()):
		shown.append(Fx.flashes_shown[k])
	assert_true(shown.size() <= 3, "at most 3 local flashes in the burst's second (%d shown)" % shown.size())
	assert_true(FlashLimiter.stream_is_safe(shown), "no rolling second holds more than 3")
	assert_eq(_kinds(fx, "disc").size(), shown.size(), "a denied flash draws no disc")
	assert_eq(_kinds(fx, "bits").size(), BURST_HITS + 2, "a denied flash keeps its bits (every hit's shards still fly)")
	assert_gt(Fx.limiter.suppressed_count, 0, "the limiter denied the rest")


# --- D16: a card's effect stems from its slap point ---------------------------------------------

func test_d16_origin_rule() -> void:
	var slap := Vector2(640, 300)
	var slice := Vector2(500, 420)
	assert_eq(CardFx.origin({"phase": "act"}, slap, slice), slap, "a card-caused beat starts at the slap point")
	assert_eq(CardFx.origin({"phase": "resolve"}, slap, slice), slice, "a slice's beat keeps its own source")
	assert_eq(CardFx.origin({"phase": "turn_start"}, slap, slice), slice, "a turn start keeps its own source")
	assert_eq(CardFx.origin({"phase": "act"}, Vector2.INF, slice), slice, "no slap known: its own source")


func test_d16_a_played_cards_effect_leaves_from_its_slap_never_the_hand() -> void:
	var scene := await _combat()
	_live()
	var fx: CombatFxLayer = scene.fx_layer
	var pv: WheelView = scene._player_view
	var hand := Rect2(100, 560, 112, 148)
	var card := ZineCard.new("BULWARK", 1, "Gain 5 block.", 0)
	var slap := pv.global_center() + Vector2(0, -pv.hub_radius() * 0.3)
	fx.play_card(card, hand, 0.0, slap, false, Callable(), pv.global_center())
	assert_eq(fx.slap_point, slap, "the card's slap point is known once it is played")
	var s: CombatState = scene.engine.state()
	for kind in ["block", "shield"]:
		var b := {"kind": kind, "phase": "act", "pass": "", "source": &"", "pointer_index": -1, "target": s.player.id, "amount": 5, "crit": false,
			"hp_after": -1, "slot": -1, "status": RC.Status.NONE, "tier": -1, "soaked": 0, "host": &"", "source_slot": -1, "source_tier": -1,
			"raw": 5, "blocked": 0, "shielded": 0, "side": "player", "wheel_source": true, "event_index": 0}
		fx.last_origin = Vector2.INF
		scene._play_beat(b, s, s)
		assert_eq(fx.last_origin, slap, "%s: the card's bits leave from its slap point on the target wheel" % kind)
		assert_false(hand.has_point(fx.last_origin), "%s: never from the hand" % kind)
		var walls := _kinds(fx, "bits")
		assert_false(walls.is_empty(), "%s: its bits stream" % kind)
		var first: Dictionary = (walls[-1]["path"] as BitPath).bits[0]
		assert_eq(first["from"], slap, "%s: the stream's first bit leaves from the slap point" % kind)
	# The same beat from a slice (a SEND IT) keeps the slice as its source.
	var r := {"kind": "block", "phase": "resolve", "pass": "", "source": s.player.id, "pointer_index": 0, "target": s.player.id, "amount": 5,
		"crit": false, "hp_after": -1, "slot": 0, "status": RC.Status.NONE, "tier": -1, "soaked": 0, "host": &"", "source_slot": 0, "source_tier": -1,
		"raw": 5, "blocked": 0, "shielded": 0, "side": "player", "wheel_source": true, "event_index": 0}
	fx.last_origin = Vector2.INF
	scene._play_beat(r, s, s)
	assert_ne(fx.last_origin, slap, "a slice's block leaves from its slice, not the last card's slap")
	await _close(scene)


# --- Reduce effects: the end state at once ----------------------------------------------------

func test_reduce_effects_adds_no_fx_and_nothing_waits() -> void:
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	var fx := _layer()
	var c := Vector2(600, 360)
	var t: Array[Vector2] = [c + Vector2(50, 80)]
	assert_eq(fx.hit_shards(c, c, 100.0, t, Palette.CELL_PINK, 9, true, 0.0, true).size(), 0, "no shards, no arrivals to wait on")
	fx.wall(c, 100.0, c + Vector2(400, 0), "brick", c)
	fx.wall(c, 100.0, c + Vector2(400, 0), "hex", c)
	assert_eq(fx.heal_inflow(c, 100.0, t).size(), 0)
	fx.evade_gain(c, c)
	fx.evade_token(c, c + Vector2(300, 0), Palette.HARM)
	fx.corrupt_apply(c, c)
	assert_eq(fx.corrupt_tick(c, c, 100.0, t).size(), 0)
	fx.drone_deploy(c, c, Palette.SLICE_TROJAN)
	fx.drone_attack(c, Palette.SLICE_TROJAN)
	fx.drone_destroyed(c, Palette.SLICE_TROJAN)
	fx.phase_bits(c, 100.0, c + Vector2(0, 100))
	fx.respin_bits(t, c, "RESPIN")
	fx.nudge_resist(c, "RESIST")
	fx.ram_gain(c, t)
	fx.trigger_fx(c, c + Vector2(100, 0), Palette.NEON_VIOLET)
	fx.temp_label(c, "EVADED", Palette.GAIN)
	assert_eq(fx.sprites.size(), 0, "reduce effects: no particles, streams, walls, tears or labels (the end state shows at once)")
	assert_false(fx.busy(), "nothing for the scene to wait on")
	var done := [false]
	var card := ZineCard.new("JOLT", 1, "Spin 3.", 0)
	var wait := fx.play_card(card, Rect2(100, 500, 112, 148), 0.0, c, false, func() -> void: done[0] = true)
	assert_eq(wait, 0.0, "the card play takes no time")
	assert_true(done[0], "and lands at once")
	assert_eq(fx.slap_point, c, "its slap point is still known (D16 holds under reduce effects)")


func test_headless_without_force_live_adds_nothing() -> void:
	Motion.force_live = false
	var fx := _layer()
	var c := Vector2(600, 360)
	var t: Array[Vector2] = [c]
	assert_eq(fx.hit_shards(c, c, 100.0, t, Palette.CELL_PINK, 5, false).size(), 0, "headless: the end state, no waits")
	fx.wall(c, 100.0, c + Vector2.RIGHT * 300.0, "brick", c)
	assert_eq(fx.sprites.size(), 0)


# --- Bits: precomputed arrivals, deterministic ------------------------------------------------

func test_shard_arrivals_are_precomputed_and_deterministic() -> void:
	var c := Vector2(400, 300)
	var targets := BitPath.arc_points(c, 120.0, PI * 0.2, PI * 0.5, 6)
	var a := BitPath.shards(7, c + Vector2(0, -110), Vector2.UP, 18, 1.3, 46.0, 0.18, 0.12, 0.19, targets, c, 110.0, 12.0, 20.0, 0.45)
	var b := BitPath.shards(7, c + Vector2(0, -110), Vector2.UP, 18, 1.3, 46.0, 0.18, 0.12, 0.19, targets, c, 110.0, 12.0, 20.0, 0.45)
	assert_eq(a.bits.size(), 18)
	assert_eq(a.arrivals(), b.arrivals(), "the same hit makes the same shards (hashed scatter, no RNG)")
	var times := a.arrivals()
	for k in range(1, times.size()):
		assert_true(times[k] >= times[k - 1], "arrivals ascend")
	for i in a.bits.size():
		var t := a.arrival(i)
		var near := a.sample(i, t - 0.0002)
		assert_true(bool(near["shown"]), "bit %d still shows just before it lands" % i)
		assert_true((near["at"] as Vector2).distance_to(a.bits[i]["to"]) < 4.0, "bit %d lands on its target" % i)
		assert_false(bool(a.sample(i, t + 0.001)["shown"]), "bit %d is absorbed on arrival" % i)
	# Round the rim, never across the face: the control point lies outside the wheel.
	for bit in a.bits:
		assert_true((bit["ctrl"] as Vector2).distance_to(c) >= 110.0, "the Bezier's control point is outside the rim")


func test_hit_shards_scale_with_damage_and_report_their_arrivals() -> void:
	_live()
	var fx := _layer()
	var c := Vector2(600, 360)
	var targets: Array[Vector2] = [c + Vector2(60, 90), c + Vector2(30, 100)]
	var small := fx.hit_shards(c + Vector2(0, -100), c, 100.0, targets, Palette.CELL_PINK, 2, false)
	var big := fx.hit_shards(c + Vector2(0, -100), c, 100.0, targets, Palette.CELL_PINK, 20, false)
	var crit := fx.hit_shards(c + Vector2(0, -100), c, 100.0, targets, Palette.CELL_PINK, 4, true)
	var cfg := RunManager.config()
	assert_eq(small.size(), cfg.fx_shard_count(2), "a small hit: few shards")
	assert_eq(big.size(), cfg.fx_shard_count(20), "a big hit: more")
	assert_eq(crit.size(), cfg.fx_shard_max, "a crit: the most")
	assert_eq(_kinds(fx, "crit").size(), 1, "a crit's cracks and code streaks")
	assert_true(big[big.size() - 1] <= Motion.seconds(&"hit_shards") + 0.001, "the last shard lands within the entry's time")
	var blocked := fx.hit_shards(c + Vector2(0, -100), c, 100.0, targets, Palette.CELL_PINK, 10, false, 0.0, true)
	assert_eq(blocked.size(), roundi(cfg.fx_shard_count(10) * Motion.amplitude(&"hit_blocked_wall")), "blocked: only the wall's share gets through")
	assert_gt(_kinds(fx, "wall").size(), 0, "blocked: the DEFRAG wall pops")


# --- Card play: peel, slap, dissolve A --------------------------------------------------------

func test_dissolve_a_cuts_the_card_into_17_px_cells_that_spiral_into_the_hub() -> void:
	var rect := Rect2(500, 200, 112, 148)
	var hub := Vector2(640, 360)
	var secs := 0.5
	var p := CardFx.dissolve_path(rect, secs, hub, 1.0)
	assert_eq(p.bits.size(), int(rect.size.x / CardFx.CELL_PX) * int(rect.size.y / CardFx.CELL_PX), "one glyph per 17 px cell")
	assert_true(p.length() <= secs + 0.001, "absorbed within the dissolve")
	var top: Dictionary = p.bits[0]
	var bottom: Dictionary = p.bits[p.bits.size() - 1]
	assert_true(float(top["appear"]) < float(bottom["appear"]), "the scan front runs top to bottom")
	for b in p.bits:
		assert_eq(b["to"], hub, "every glyph spirals into the hub")
		assert_true(float(b["size"]) >= CardFx.GLYPH_MIN and float(b["size"]) <= CardFx.GLYPH_MAX, "glyphs 19-25 px")
	# Clockwise: the control point is the cell turned a quarter round the hub, clockwise on screen.
	var cell: Vector2 = top["from"]
	var ctrl: Vector2 = top["ctrl"]
	assert_true((cell - hub).cross(ctrl - hub) > 0.0, "it spirals clockwise")


func test_the_card_play_peels_slaps_and_dissolves_before_its_effect() -> void:
	_live()
	var fx := _layer()
	var card := ZineCard.new("JOLT", 1, "Spin the target 3 ticks.", 0)
	var to := Vector2(600, 300)
	var wait := fx.play_card(card, Rect2(100, 500, 112, 148), 0.0, to, false, Callable(), Vector2(640, 360))
	assert_almost_eq(wait, Motion.seconds(&"card_play") + Motion.seconds(&"card_stamp") + Motion.seconds(&"effect_burst"), 0.001,
		"the effect waits for the slap and the dissolve")
	assert_eq(_kinds(fx, "liner").size(), 1, "the peel leaves a faint liner in the slot")
	assert_true(card.material is ShaderMaterial, "the card wears the sticker material (StickerSeam)")
	assert_eq(fx.slap_point, to, "its slap point is its target")
	fx.clear()


func test_slap_squashes_overshoots_and_settles() -> void:
	assert_eq(CardFx.slap_scale(0.0), Vector2.ONE)
	var squash := CardFx.slap_scale(CardFx.SQUASH_SHARE - 0.0001)
	assert_almost_eq(squash.x, 1.13, 0.01, "squash 1.13 wide")
	assert_almost_eq(squash.y, 0.86, 0.01, "and 0.86 tall")
	assert_eq(CardFx.slap_scale(1.0), Vector2.ONE, "settles at 1")


# --- Temporary labels -------------------------------------------------------------------------

func test_a_temporary_label_dissolves_left_to_right_into_bits() -> void:
	_live()
	var fx := _layer()
	fx.temp_label(Vector2(600, 300), "EVADED", Palette.GAIN)
	var tags := _kinds(fx, "tag")
	assert_eq(tags.size(), 1, "the word sticker")
	var tag: Dictionary = tags[0]
	assert_almost_eq(float(tag["dissolve"]), Motion.seconds(&"temp_label"), 0.001, "it ends dissolving")
	var hold := float(tag["dur"]) - float(tag["land"]) - float(tag["dissolve"])
	assert_almost_eq(hold, Motion.amplitude(&"temp_label"), 0.001, "it holds ~0.85 s first")
	var bits := _kinds(fx, "bits")
	assert_eq(bits.size(), 1, "its bits")
	var path: BitPath = bits[0]["path"]
	var left: Dictionary = path.bits[0]
	var right: Dictionary = path.bits[path.bits.size() - 1]
	assert_true(float(left["appear"]) < float(right["appear"]), "left to right")
	assert_true((right["to"] as Vector2).y < (right["from"] as Vector2).y, "the bits drift up")
	assert_almost_eq(float(bits[0]["delay"]), float(tag["dur"]) - float(tag["dissolve"]), 0.001, "as the word goes")


# --- Config: shard severity and the Heat city ---------------------------------------------------

func test_shard_severity_comes_from_the_campaign_config() -> void:
	var cfg := RunManager.config()
	assert_true(cfg.fx_shard_count(3) < cfg.fx_shard_count(12), "more damage, more shards")
	assert_eq(cfg.fx_shard_count(1000), cfg.fx_shard_max, "capped")
	assert_true(cfg.fx_glyph_px(3) < cfg.fx_glyph_px(20), "bigger glyphs")
	assert_eq(cfg.fx_glyph_px(0, true), cfg.fx_glyph_px_max, "a crit: the biggest")


func test_the_heat_city_shows_each_band_from_the_config() -> void:
	var cool := HeatCity.counts(0)
	assert_eq(cool.values().reduce(func(a: int, v: int) -> int: return a + v, 0), 0, "COOL: nothing")
	assert_eq(int(HeatCity.counts(1)["side_beacons"]), 3, "NOTICED: three alarm beacons on side buildings")
	assert_eq(int(HeatCity.counts(1)["target_beacons"]), 0, "NOTICED: nothing on the target")
	assert_eq(int(HeatCity.counts(2)["side_searchlights"]), 2, "FLAGGED: two side searchlights")
	assert_eq(int(HeatCity.counts(2)["target_beacons"]), 2, "FLAGGED: two beacons on the target")
	assert_eq(int(HeatCity.counts(3)["police"]), 13, "HUNTED: 13 police light clusters")
	assert_eq(int(HeatCity.counts(3)["target_searchlights"]), 2, "HUNTED: two searchlights on the target")
	assert_eq(HeatCity.counts(4), HeatCity.counts(3), "PURGE = HUNTED's look for now")
	assert_true(HeatCity.POLICE_HZ <= 3.0, "police strobe never above 3 Hz")


func test_the_heat_city_holds_still_under_reduce_motion() -> void:
	_live()
	var hc := HeatCity.new()
	add_child_autofree(hc)
	hc.set_band(3, Vector2(800, 200))
	assert_true(hc.is_processing(), "HUNTED: the lights turn and sweep")
	Settings.set_reduce_motion(true)
	hc.set_band(3, Vector2(800, 200))
	assert_false(hc.is_processing(), "reduce motion: steady lights, fixed searchlights")
	hc.set_band(0)
	assert_false(hc.is_processing())


func test_the_combat_scene_shows_heat_on_its_backdrop() -> void:
	var scene := await _combat()
	assert_not_null(scene.heat_city, "the Heat city stands in the fight")
	assert_true(scene.heat_city.get_index() < scene.fx_layer.get_index() if scene.heat_city.get_parent() == scene.fx_layer.get_parent() else true,
		"behind the FX")
	assert_eq(scene.heat_city.get_index(), scene.arena_backdrop.get_index() + 1, "right over the backdrop (ART-2 2B: the close-up), behind every wheel and the HUD")
	assert_eq(scene.heat_city.mouse_filter, Control.MOUSE_FILTER_IGNORE, "it takes no input")
	await _close(scene)


# --- Views never change state ------------------------------------------------------------------

func test_beat_fx_never_change_the_fight() -> void:
	var scene := await _combat()
	_live()
	var s: CombatState = scene.engine.state()
	var before := s.to_dict()
	var enemy: StringName = s.enemies[0].id
	for kind in ["damage", "block", "shield", "heal", "evaded", "corrupted"]:
		var b := {"kind": kind, "phase": "resolve", "pass": "", "source": s.player.id if kind != "evaded" else enemy, "pointer_index": 0,
			"target": enemy if kind in ["damage", "corrupted"] else s.player.id, "amount": 4, "crit": kind == "damage", "hp_after": 10, "slot": 0,
			"status": RC.Status.CORRUPTED, "tier": -1, "soaked": 0, "host": &"", "source_slot": 0, "source_tier": -1, "raw": 4, "blocked": 0,
			"shielded": 0, "side": "player", "wheel_source": true, "event_index": 0}
		scene._play_beat(b, s, s)
	assert_eq(scene.engine.state().to_dict(), before, "the FX read the fight; they never change it")
	await _close(scene)
