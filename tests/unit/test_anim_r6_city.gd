extends GutTest
## Animation pass ANIM-R6, city, raid, HQ and bake part (C1-C16; DECISIONS "Animation pass -
## ANIM-R6 city, raid, HQ and bake"). Views only. The bakes run headless under
## CityBakeCache.simulate (a test lands them with `_land_all`).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HqScript := preload("res://scripts/ui/hq_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const LAND_ROUNDS := 5

var _reduce: bool
var _scale: float


class Counter extends Node:
	## Counts the presses that reach it (it sits before the pieces under test in the tree, so
	## they see each event first).
	var got: int = 0

	func _input(event: InputEvent) -> void:
		if MotionSkip.is_press(event):
			got += 1


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r6_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	Motion.force_live = false
	Motion.set_speed(1.0)
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
		Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx._set_jacking(false)
	Fx._hide_connect()
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _live() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()


## A copy of the motion table with entries `ids` switched off (the loaded table never changes).
func _switch_off(ids: Array) -> void:
	var dup: UiMotionData = Motion.config().duplicate(true)
	for id in ids:
		dup.find(StringName(id)).enabled = false
	Motion.use_config(dup)


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _tex() -> ImageTexture:
	return ImageTexture.create_from_image(Image.create(8, 8, false, Image.FORMAT_RGBA8))


func _entry(look: String, region: Rect2, tex: Texture2D) -> Dictionary:
	return {"look": look, "region": region, "texture": tex, "scale": 1.0, "roofs": {},
		"beacons": [] as Array[Dictionary], "lights": [] as Array[Dictionary], "trails": [] as Array[Dictionary], "signs": [] as Array[Dictionary]}


func _land_all() -> int:
	var n := 0
	for key: String in CityBakeCache._pending.keys():
		var p: Dictionary = CityBakeCache._pending[key]
		CityBakeCache.store(key, _entry(p["look"], p["region"], _tex()))
		n += 1
	return n


func _settle_bakes() -> void:
	for r in LAND_ROUNDS:
		await _frames(NeonCity.BAKE_SETTLE_FRAMES + 2)
		_land_all()
	await _frames(2)


func _key(k: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = true
	return e


## A campaign with the first Site off home claimed; a raid pending; `defended`: a turret on it.
func _raid_campaign(defended: bool = false) -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 400
	var corp := RunManager.corporation
	var first: StringName = corp.city_grid.get_site(c.grid.home_site_id).links[0]
	var run := RunState.new()
	run.site_id = first
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	if defended:
		c.armory = [&"turret"]
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


# --- C1 / C5: the Heat poster ------------------------------------------------------------------

func test_the_heat_poster_is_one_press_motion_and_its_reading_hold_is_not() -> void:
	_live()
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var counter := Counter.new()
	holder.add_child(counter)
	var p := HeatPoster.new(true)
	holder.add_child(p)
	p.position = Vector2(40, 100)
	p.size = p.custom_minimum_size
	assert_true(p.is_in_group(MotionSkip.GROUP), "the poster joins the one press rule")
	var marks: Array[int] = [25, 50, 75]
	p.set_heat(10, 100, marks)
	p.set_heat(60, 100, marks)
	await BoundedWait.frozen_frames(get_tree(), 1)  # ANIM-R6 D9: a slow frame must not end the roll first
	assert_true(p.motion_running(), "the number rolls to its thresholds")
	var got := counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_eq(counter.got, got, "the press that completes it is consumed")
	assert_false(p.motion_running(), "the roll, the crossings and their stamps are at their end")
	assert_eq(roundi(p.shown_heat), 60, "the number on the Heat")
	assert_eq(p.shown_band(), 2)
	assert_eq(p._banner_at, 50, "the last crossing's banner shows")
	assert_true(p.banner_holding(), "held to be read (a reading time, not motion)")
	assert_true(p.note_showing(), "with its consequence")
	assert_eq(p.number_scale, 1.0)
	assert_eq(p.stamp_scale, 1.0)
	got = counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_eq(counter.got, got + 1, "a press during the reading hold passes (nothing moves)")
	assert_true(p.banner_holding(), "and the banner stays its hold")
	p._start_fade()
	assert_true(p.motion_running(), "the banner fading out is motion")
	p.complete_motion()
	assert_eq(p.banner_alpha, 0.0, "completed, the banner is gone")
	assert_false(p.note_showing())
	p.free()


func test_under_reduce_effects_the_heat_note_shows_static_for_its_hold_and_keeps_off_words() -> void:
	Settings.set_reduce_effects(true)
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var p := HeatPoster.new(true)
	holder.add_child(p)
	p.position = Vector2(980, 100)
	p.size = p.custom_minimum_size
	# A card of words right under the poster (the HQ's PIRATE RADIO sits there).
	var radio := Label.new()
	radio.text = "PIRATE RADIO\nThe voice giving the orders does not breathe between sentences."
	holder.add_child(radio)
	radio.position = Vector2(980, p.get_global_rect().end.y + 4.0)
	radio.size = Vector2(290, 140)
	var marks: Array[int] = [25, 50, 75]
	p.set_heat(10, 100, marks)
	p.set_heat(30, 100, marks)
	await _frames(2)
	assert_eq(p.banner_alpha, 1.0, "the banner shows, static")
	assert_true(p.banner_holding())
	assert_true(p.note_showing(), "its consequence shows too (it never did under reduce effects)")
	var r := p.note_rect()
	assert_false(r.intersects(radio.get_global_rect()), "the note covers no words (%s over %s)" % [r, radio.get_global_rect()])
	assert_true(SCREEN.grow(0.5).encloses(r), "on the screen")
	assert_false(p.note_text().begins_with("The corporation raids"), "its first sentence no longer reads as a raid happening now")
	assert_string_contains(p.note_text(), "queued")
	p.free()


# --- C2: the home-hit number is a FlightFx flight ----------------------------------------------

func test_a_home_hit_number_is_a_flight_a_press_lands() -> void:
	_live()
	_raid_campaign(true)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(3)
	hq.fight_raid()
	await _frames(4)
	assert_eq(hq.panel_name, "raid_playout")
	var home := RunManager.campaign.grid.home_site_id
	hq.hud_home_shown = 50
	hq._fly_home_number(5, home)
	assert_eq(FlightFx.active_count(hq), 1, "the number flies on the FlightFx layer")
	assert_eq(hq.hud_home_shown, 50, "HOME drops when it lands")
	MotionSkip.complete_all(hq)
	assert_eq(FlightFx.active_count(hq), 0, "a press completes it")
	assert_eq(hq.hud_home_shown, 45, "and it has landed: HOME shows the hit")
	hq.playout.skip_to_end()


# --- C3: a drawn bake outlives its cache entry ------------------------------------------------

func test_a_view_holds_the_bake_it_draws_past_its_eviction() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	await _frames(2)
	city._camera()
	var look := city.look_key()
	var region := city.bake_region()
	var key := look + "@" + var_to_str(Rect2i(region))
	var vp := SubViewport.new()
	vp.size = Vector2i(8, 8)
	CityBakeCache._holder().add_child(vp)
	var tex: Texture2D = BakedTexture.of_viewport(vp)
	var kept := tex != null
	if not kept:
		vp.free()
		tex = _tex()
	var tex_id := tex.get_instance_id()
	CityBakeCache.store(key, _entry(look, region, tex))
	city.refresh()
	await _frames(3)
	assert_eq(city.drawn_texture, tex, "the view holds the picture it draws")
	tex = null
	for k in CityBakeCache.CAPACITY + 2:
		CityBakeCache.store("filler_%d" % k, _entry("x", Rect2(), _tex()))
	assert_false(CityBakeCache.has(key), "the entry was evicted")
	await _frames(3)
	assert_not_null(instance_from_id(tex_id), "its picture lives on while the view holds it")
	if kept:
		assert_true(is_instance_valid(vp), "its viewport is not freed under the canvas")
	# The view draws another picture: the old one goes.
	var next := _tex()
	CityBakeCache.store(key + "#2", _entry(look, region.grow(8.0), next))
	city.refresh()
	await _frames(3)
	assert_eq(city.drawn_texture, next, "it holds the new one")
	await _frames(2)
	if kept:
		assert_false(is_instance_valid(vp), "and the old viewport went with the last reference")


# --- C4: switched-off entries show their end state where views run their own clock --------------

func test_raid_motion_switched_off_shows_its_end_state_with_no_motion() -> void:
	_live()
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(4)
	var c := RunManager.campaign
	var overlay: CityMapOverlay = hq.city_overlay
	var home := c.grid.home_site_id
	var site: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != home else c.grid.claimed_ids()[1]
	var r := {"nodes": {}, "home_before": 50, "home_after": 50}
	for off in [false, true]:
		Motion.use_config(null)
		if off:
			_switch_off([&"node_pop", &"raid_move", &"raid_flip", &"raid_result_banner", &"home_lag", &"node_damage_number",
				&"ice_lock_ring", &"decoy_fire", &"raid_hit_effect", &"turret_trace", &"route_crawl", &"raid_step_gap", &"raid_shot_stagger"])
		var fx := RaidFxLayer.new(overlay)
		overlay.add_child(fx)
		fx.setup(r, home, 50, Palette.CORP_SOLACE)
		fx.play_beat({"type": "threat_enters", "event": {"threat": "t0", "site": site}, "dur": 1.0}, 0.0)
		fx.play_beat({"type": "move", "event": {"threat": "t0", "from": site, "to": home}, "dur": 1.0}, 2.0)
		fx.clock = 0.5
		var tag := "off" if off else "on"
		assert_almost_eq(fx.beat_u(&"node_pop", 0.0, 1.0), 1.0 if off else 0.5, 0.001, "%s: the token's pop" % tag)
		fx.clock = 2.5
		var at: Vector2 = fx._token_positions()["t0"]
		var dest := overlay.marker_slot(home, 0, 1)
		if off:
			assert_eq(at, dest, "off: the token stands on its new node from the move's start")
		else:
			assert_ne(at, dest, "on: it travels")
		fx.home_shown = 40
		fx._home_from = 50
		fx._home_lag_t0 = 2.4
		assert_eq(fx._home_lag_value() == float(fx.home_shown), off, "%s: home's lag bar" % tag)
		assert_eq(overlay.crawl_speed() == 0.0, off, "%s: the routes' crawl" % tag)
		assert_eq(RaidBeats.raw_seconds(&"raid_step_gap") == 0.0, off, "%s: the gap between steps (a part)" % tag)
		var shots := RaidBeats.timeline([{"type": "shot", "step": 1, "site": site, "threat": "a", "damage": 1},
			{"type": "shot", "step": 1, "site": site, "threat": "b", "damage": 1}])
		var b: Array = shots["beats"]
		assert_eq(is_equal_approx(float(b[0]["t0"]), float(b[1]["t0"])), off, "%s: a volley's stagger (a part: together when off)" % tag)
		if not off:
			assert_almost_eq(float(b[1]["t0"]) - float(b[0]["t0"]), RaidBeats.raw_seconds(&"turret_trace") * Motion.amplitude(&"raid_shot_stagger"), 0.0001,
				"the stagger reads the table (it was the inline 0.5)")
		fx.free()
	assert_true(UiMotionData.OFF_PARTS.has(&"raid_step_gap"), "the step gap is a part")
	assert_true(UiMotionData.ALWAYS_ON.has(&"heat_pulse_rise"), "the pulse's rise tunes heat_pulse")


func test_no_inline_motion_numbers_left_in_the_raid_heat_and_marks() -> void:
	assert_false(FileAccess.get_file_as_string("res://scripts/ui/kit/raid_beats.gd").contains("SHOT_STAGGER := "), "the volley's stagger is a table entry")
	assert_false(FileAccess.get_file_as_string("res://scripts/autoload/fx.gd").contains("HEAT_PULSE_RISE := "), "the pulse's rise is a table entry")
	assert_false(FileAccess.get_file_as_string("res://scripts/ui/kit/neon_city.gd").contains("mark_t * 2.0"), "a mark's fade-in reads stamp_fade_in")


# --- C6: the Polaroid caption follows the text size ----------------------------------------------

func test_a_polaroid_caption_follows_the_text_size_and_is_never_cut() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		assert_eq(Polaroid.caption_floor(), roundi(12 * scale), "%.1f: the floor is 12 px x the text size" % scale)
		RunManager.new_campaign(1)
		var hq := _scene(HQ)
		await _frames(3)
		var seen := 0
		var list: Array = hq.find_children("*", "Polaroid", true, false)
		for w in [110.0, 80.0, 64.0]:
			var extra := Polaroid.new("Breaker 1 R0", "[BREAKER PORTRAIT]")
			add_child_autofree(extra)
			extra.size = Vector2(w, w * 134.0 / 110.0)
			list.append(extra)
		for n in list:
			var pol := n as Polaroid
			if pol.caption == "" or (not pol.is_visible_in_tree() and pol.get_parent() == hq):
				continue
			seen += 1
			var lay := pol.caption_layout()
			var fs := int(lay["fs"])
			var tag := "%.1f %.0f px '%s'" % [scale, pol.size.x, pol.caption]
			assert_gte(fs, Polaroid.caption_floor(), "%s: never under the floor" % tag)
			assert_lte(fs, Polaroid.caption_top(), "%s: never over its rest size" % tag)
			var joined := ""
			for line: String in lay["lines"]:
				joined += line
				assert_true(Palette.marker().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x <= pol.size.x - Polaroid.CAPTION_INSET * 2.0 + 0.5, "%s: '%s' fits its line" % [tag, line])
			assert_eq(joined.replace(" ", ""), pol.caption.replace(" ", ""), "%s: every letter shown" % tag)
		assert_gt(seen, 3, "%.1f: Polaroids checked" % scale)
		hq.get_parent().queue_free()
		await _frames(1)


# --- C7: the maps' drawn words are exported --------------------------------------------------------

func test_the_maps_drawn_words_are_exported_once() -> void:
	var keys := TextDb.code_keys(PackedStringArray(["res://scripts/ui", "res://scripts/autoload"]))
	for k in ["WIN", "EXPLOIT", "HEAT %s", "NO GAIN", "MAP KEY", "T%d", "difficulty %d of %d", "Clearing it gives %s Schematics.",
			"Clearing it changes Heat by %s.", "Key", "none"]:
		assert_true(keys.has(k), "'%s' is a code key" % k)
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for k in keys:
		if k.begins_with("Clearing it") or k in ["WIN", "MAP KEY", "T%d", "Key", "HEAT %s", "none"]:
			assert_true(csv.contains("\n" + k + ",") or csv.contains("\n\"" + k + "\","), "'%s' is in strings.csv" % k)
	var re := RegEx.create_from_string(TextDb.CODE_CALLS)
	for path in ["res://scripts/ui/hq_scene.gd", "res://scripts/ui/kit/map_legend.gd", "res://scripts/ui/kit/city_layout.gd", "res://scripts/ui/kit/city_map_overlay.gd"]:
		for m in re.search_all(FileAccess.get_file_as_string(path)):
			assert_false(m.get_string(1).contains("%+"), "%s: '%s' has no %%+ format (TextDb.signed)" % [path, m.get_string(1)])


# --- C8: YOUR NODES fills its window and never cuts a row --------------------------------------------

func test_your_nodes_fills_its_window_and_counts_the_withdraw_row() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		_raid_campaign()
		var c := RunManager.campaign
		var home := c.grid.home_site_id
		c.armory = [&"turret", &"ice_lock", &"decoy"]
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, home)
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, home)
		var hq := _scene(HQ)
		await _frames(1)
		hq.selected_site = home
		hq.show_raid()
		await _frames(8)
		var tag := "%.1f" % scale
		var win := hq._panel.find_child("NodeOrders", true, false) as TerminalWindow
		var scroll := hq._panel.find_child("OrdersScroll", true, false) as ScrollContainer
		assert_not_null(scroll)
		var hint: ScrollHint = hq.side_hint
		var room := hint.room.size.y if hint.room != null else 0.0
		assert_lte(win.get_global_rect().end.y - (scroll.get_global_rect().end.y + room), 24.0,
			"%s: the list takes the window's height (it scrolled in a strip over empty window)" % tag)
		assert_not_null(hq._panel.find_child("Moves", true, false), "%s: the target's withdraw row is there" % tag)
		if hint.overflows():
			var foot := scroll.get_global_rect().end.y
			for b in scroll.find_children("*", "Button", true, false):
				var r := (b as Control).get_global_rect()
				if (b as Control).is_visible_in_tree() and r.position.y > scroll.get_global_rect().position.y:
					assert_false(r.position.y < foot - 0.5 and r.end.y > foot + 0.5, "%s: '%s' is not cut by the view's foot" % [tag, (b as Button).text])
			assert_true(hint.visible, "%s: MORE BELOW says there is more" % tag)
			assert_true(hint.get_global_rect().position.y >= foot - 0.5, "%s: in its own room under the list" % tag)
		hq.get_parent().queue_free()
		await _frames(1)


# --- C9: the HQ after New campaign and the Grid's first open are baked ahead ---------------------

func test_the_start_page_bakes_the_new_campaigns_hq_and_the_hq_bakes_the_first_grid() -> void:
	CityBakeCache.simulate = true
	var hq := _scene(HQ)
	await _frames(2)
	assert_eq(hq.panel_name, "start")
	await _settle_bakes()
	assert_not_null(hq._start_warm, "a twin warms the new campaign's HQ")
	hq.new_campaign(1)
	await _frames(2)
	assert_true(hq.background.city.view_covered(), "the HQ opens on its baked city, not the silhouette")
	# From the HQ page, the Grid's first open.
	await _settle_bakes()
	var region: Rect2 = hq.first_grid_region()
	assert_true(region.has_area(), "the first Grid's region is known from the HQ")
	hq.show_grid()
	await _frames(2)
	assert_true(hq.wireframe.city.view_covered(), "the Grid's first open is covered on its first frames")


# --- C10 / C11: the raid's end ---------------------------------------------------------------------

func test_a_finished_raid_turns_its_speed_controls_off_on_1x_and_opens_on_core() -> void:
	_live()
	_raid_campaign(true)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(3)
	hq.fight_raid()
	await _frames(1)
	var c := RunManager.campaign
	var overlay: CityMapOverlay = hq.city_overlay
	var entry: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
	var events: Array[Dictionary] = [{"type": "threat_enters", "step": 1, "threat": "t0", "site": entry}]
	var pts: PackedVector2Array = hq.playout_frame_points(events)
	assert_eq(pts.size(), 2, "the playout opens on CORE and the entries")
	assert_true(pts.has(Vector2(overlay.lot_of(c.grid.home_site_id)) + Vector2(0.5, 0.5)), "CORE among them")
	var panel: RaidPlayoutPanel = hq.playout
	panel.set_speed(2.0)
	for b in panel.speed_buttons():
		assert_eq(b.button_pressed, b.name == "Speed2x", "%s lit only when it plays" % b.name)
	panel.skip_to_end()
	await _frames(1)
	for b in panel.controls():
		assert_true(b.disabled, "%s is off once the raid is over" % b.name)
	for b in panel.speed_buttons():
		assert_eq(b.button_pressed, b.name == "Speed1x", "%s: 1x lit again" % b.name)


func test_the_verdict_withdraws_the_threats_and_home_holds_reads_green() -> void:
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(4)
	var c := RunManager.campaign
	var overlay: CityMapOverlay = hq.city_overlay
	var home := c.grid.home_site_id
	var fx := RaidFxLayer.new(overlay)
	overlay.add_child(fx)
	fx.setup({"nodes": {}, "home_before": 50, "home_after": 45}, home, 50, Palette.CORP_SOLACE)
	var events: Array[Dictionary] = [{"type": "threat_enters", "step": 1, "threat": "t0", "site": home},
		{"type": "home_hit", "step": 2, "threat": "t0", "damage": 5},
		{"type": "raid_end", "won": false, "steps": 2}]
	var at := 0.0
	for group in RaidBeats.group(events):
		var tl := RaidBeats.timeline(group)
		for b: Dictionary in tl["beats"]:
			fx.play_beat(b, at + float(b["t0"]))
		at += float(tl["seconds"])
	fx.clock = at + 100.0
	assert_false(fx.token_alive("t0"), "the Collector left CORE at the verdict")
	assert_true(fx._tokens["t0"].get("withdrawn", false), "struck out, not destroyed")
	var parts := fx.banner_parts()
	assert_eq(parts.size(), 2, "HOME -5 · HOLDS in two colours")
	assert_eq(parts[0][1], Palette.CELL_PINK, "the damage pink")
	assert_eq(parts[1][1], Palette.CELL_ACID, "HOLDS acid, as every HOLDS")
	assert_eq(String(parts[0][0]) + String(parts[1][0]), fx.banner_text())
	# The feed's markers keep the threat that hit home named until the verdict.
	var marker_map := CityMapOverlay.new()
	add_child_autofree(marker_map)
	var panel := RaidPlayoutPanel.new(marker_map)
	add_child_autofree(panel)
	var groups := RaidBeats.group(events)
	panel._apply_step(groups[1])
	panel._apply_step(groups[2])
	assert_true(marker_map.threat_markers.has(home), "named on CORE after its hit")
	panel._apply_step(groups[3])
	assert_true(marker_map.threat_markers.is_empty(), "gone with the verdict")


func test_raids_drops_with_the_verdict_not_the_raid_over_line() -> void:
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(2)
	hq.hud_raids_shown = 1
	hq._on_raid_event_shown({"type": "raid_end", "won": false, "steps": 2})
	assert_eq(hq.hud_raids_shown, 1, "RAIDS holds through the Raid over line")


# --- C12: the claim's cross-stamp, one stamp per mark -----------------------------------------------

func test_a_claim_cross_stamps_cleared_into_claimed_and_a_map_draws_its_marks_alone() -> void:
	_live()
	_raid_campaign()
	RunManager.campaign.pending_raids.clear()
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	await _frames(2)
	var site: StringName = &""
	for s in CampaignRules.launchable_sites(c, corp, RunManager.config()):
		if c.grid.is_corporate(s.id):
			site = s.id
			break
	var inf0 := CityInfluence.of(c, corp)
	var run := RunState.new()
	run.site_id = site
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
	var inf1 := CityInfluence.of(c, corp)
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), site, &"firewall_relay")
	var inf2 := CityInfluence.of(c, corp)
	city.mark_changes(inf0, inf1)
	city.mark_t = 1.0
	assert_false(city.marks.is_empty(), "the clear left its CLEARED mark")
	var cleared: String = city.marks[0]["word"]
	city.mark_changes(inf1, inf2)
	assert_false(city.fading_marks.is_empty(), "CLEARED stays while CLAIMED stamps on")
	assert_eq(String(city.fading_marks[0]["word"]), cleared)
	assert_ne(String(city.marks[0]["word"]), cleared, "the new word")
	city.mark_t = 1.0
	assert_true(city.fading_marks.is_empty(), "then only CLAIMED")
	assert_false(city.marks_on_map(), "no map: the city draws its own marks")
	var overlay := CityMapOverlay.new(city)
	city.add_child(overlay)
	assert_true(city.marks_on_map(), "a map draws them: the city's layer draws none (never two stamps)")


# --- C13: the page's pops complete with a press -------------------------------------------------------

func test_the_hq_pages_pops_complete_with_a_press() -> void:
	_live()
	RunManager.new_campaign(1)
	var hq := _scene(HQ)
	await _frames(3)
	assert_true(hq.is_in_group(MotionSkip.GROUP))
	var badge := hq._panel.find_child("NetworkBadge", true, false) as Control
	assert_not_null(badge)
	Motion.pop(badge, &"sticky_bump")
	assert_true(hq.motion_running(), "the SITES badge's bump is motion")
	assert_true(hq.popping().has(badge))
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(hq.motion_running(), "a press completes it")
	assert_eq(badge.scale, Vector2.ONE, "at rest")
	hq.show_end()
	await _frames(3)
	# ART-11 4D: the audit dossier's own motion (cover, stamp, notes) completes with a press.
	var dossier := hq._panel as AuditDossier
	assert_true(dossier.motion_running(), "the dossier opens")
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(dossier.motion_running(), "a press completes it")
	assert_true(dossier.case_stamp.visible, "the stamp has landed")
	assert_eq(dossier.case_stamp.scale, Vector2.ONE, "at rest")


# --- C14: RAID INCOMING's hold ------------------------------------------------------------------------

func test_raid_incoming_holds_by_its_own_switch_and_the_lab_says_what_the_game_says() -> void:
	_switch_off([&"jack_connect"])
	Fx._note = "RAID INCOMING\nSOLACE"
	Fx._show_note(SCREEN.size)
	assert_true(Fx.note_label.visible)
	assert_almost_eq(Fx.note_hold(), Motion.seconds(&"raid_incoming_hold"), 0.0001, "read through the kit")
	assert_gte(Fx.connect_hold(), Fx.note_hold(), "jack_connect off: RAID INCOMING still holds")
	assert_gt(Fx.connect_hold(), 0.0)
	Fx._hide_connect()
	var lab: GDScript = load("res://tools/design_lab/motion_lab.gd")
	var corp := RunManager.lookup().get_content(&"solace")
	assert_eq(lab.call(&"_raid_note"), tr("RAID INCOMING\n%s") % TextDb.t(corp, "display_name"), "the lab's stamp is the game's")


# --- C15: words a newcomer reads ------------------------------------------------------------------------

func test_newcomer_words_and_places() -> void:
	# The interlude's empty asset rows say none.
	RunManager.new_campaign(2)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	HeatRules.add_heat(RunManager.campaign, RunManager.config().major_heat_levels()[0] + 1, RunManager.config(), "test")
	RunManager.netrun._maybe_raid_interlude()
	RunManager.campaign.armory.clear()
	scene._show_current()
	await _frames(3)
	var chips: Node = scene._panel.find_child("RaidAssets", true, false)
	if chips != null:
		for row_name in ["RunAssetChips", "ArmoryChips"]:
			var row := chips.find_child(row_name, true, false) as Control
			if row != null and row.get_child_count() == 1 + row.find_children("NoAssets", "Label", false, false).size():
				assert_eq(row.find_children("NoAssets", "Label", false, false).size(), 1, "%s says none" % row_name)
	scene.get_parent().queue_free()
	await _frames(1)
	# YOU ARE HERE stands on the street.
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	await _frames(2)
	var overlay := CityMapOverlay.new(city)
	city.add_child(overlay)
	overlay.set_graph([{"id": &"n0", "at": Vector2(12, 12)}], [])
	var lot := Vector2i(12, 9)
	for y in range(9, 20):
		if not city.is_street(12, y):
			lot = Vector2i(12, y)
			break
	overlay.here_at = Vector2(lot)
	var p := overlay.here_point()
	var found := false
	for dy in range(-6, 7):
		for dx in range(-6, 7):
			var l := lot + Vector2i(dx, dy)
			if city.is_street(l.x, l.y) and overlay.grid_point_local(Vector2(l) + Vector2(0.5, 0.5)).is_equal_approx(p):
				found = true
	assert_true(found, "the marker stands on a street lot, not the block beside the road")
	# The words and the icon.
	assert_ne(HqScript.GAIN_CLAIMABLE, "CLAIMABLE", "the claim badge says what claiming means")
	RunManager.new_campaign(1)
	RunManager.campaign.outcome = CampaignState.Outcome.WON
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_end()
	await _frames(2)
	var dossier := hq._panel as AuditDossier
	assert_eq(dossier.stamp_word(), tr("AT LARGE"), "a won campaign's file: the Cell is AT LARGE (ART-11 4D)")
	hq.show_hq()
	await _frames(1)
	assert_true(hq.more_hint.snap_rows, "the HQ page never ends in a half-cut row (the crew's Loadout at TEXT_SCALE_MAX)")
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	hq.show_hq()
	await _frames(8)
	var hint: ScrollHint = hq.more_hint
	if hint.overflows():
		var foot := hint.scroll.get_global_rect().end.y
		for b in hq._panel.find_children("*", "Button", true, false):
			var r := (b as Control).get_global_rect()
			if (b as Control).is_visible_in_tree():
				assert_false(r.position.y < foot - 0.5 and r.end.y > foot + 0.5, "TEXT_SCALE_MAX: '%s' is not cut by MORE BELOW" % (b as Button).text)


# --- C16: the campaign end in context, and demo waits that never resume on a freed scene ---------------

func test_the_campaign_end_demo_and_one_shot_demo_waits() -> void:
	assert_eq(HqScript.demo_end_of("--demo-campaign-end=won"), CampaignState.Outcome.WON)
	assert_eq(HqScript.demo_end_of("--demo-campaign-end=lost"), CampaignState.Outcome.LOST)
	assert_eq(HqScript.demo_end_of("--demo-campaign-end=maybe"), -1)
	assert_eq(HqScript.demo_end_of("--demo-hq"), -1)
	var hq := _scene(HQ)
	await _frames(1)
	hq.demo_campaign_end(CampaignState.Outcome.LOST)
	await _frames(2)
	assert_eq(hq.panel_name, "end")
	assert_eq(RunManager.campaign.outcome, CampaignState.Outcome.LOST)
	assert_eq(RunManager.save_slot, "demo", "in the demo's own slot")
	RunManager.delete_save()
	RunManager.save_slot = "gut_anim_r6_city"
	var src := FileAccess.get_file_as_string("res://scripts/ui/hq_scene.gd")
	var body := src.substr(src.find("func _demo_anim("), src.find("func _still_active(") - src.find("func _demo_anim("))
	assert_false(body.contains("await get_tree()") or body.contains("await _demo"), "the demos wait by one-shot connections, never an await")
	# A wait whose scene is freed never runs its step.
	var ran := [0]
	hq._demo_wait(2, func() -> void: ran[0] += 1)
	hq.get_parent().free()
	await _frames(4)
	assert_eq(ran[0], 0, "a freed HQ drops its demo step")
