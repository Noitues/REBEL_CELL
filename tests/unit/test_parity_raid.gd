extends GutTest
## Parity fix — raid (designer group ruling 2026-10-05: the raid matches the round 40 concept,
## `raid_view_v3`; docs/art_review/PARITY/GAPS.md RAID-01, 03, 07, 08 (threat arrow), 09; DECISIONS
## "Parity fix — raid (designer group ruling)"). Kit-level checks (the raid kit's cards, holo,
## drag pencil, feed and playout framing) at text 1.0, 1.6 and the largest size.

const SCALES: Array[float] = [1.0, 1.6, Settings.TEXT_SCALE_MAX]
const ASSET_DIR := "res://content/assets/"
## RAID-08: frames the playout is watched for, and how often CORE's spot is checked.
const PLAYOUT_FRAMES := 360
const CHECK_EVERY := 20

var _scale: float = 1.0


func before_all() -> void:
	_scale = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.text_scale = _scale


func _assets() -> Array[DefenseAssetData]:
	var out: Array[DefenseAssetData] = []
	for f in DirAccess.get_files_at(ASSET_DIR):
		if f.ends_with(".tres"):
			var d := load(ASSET_DIR + f) as DefenseAssetData
			if d != null:
				out.append(d)
	return out


# --- RAID-01: the concept's dark defence card ------------------------------------------------------

func test_every_defence_asset_has_the_concepts_baked_card_and_colour() -> void:
	var assets := _assets()
	assert_gt(assets.size(), 0, "the content has defence assets")
	var m := AssetCard.manifest()
	assert_eq(String(m.get("source", {}).get("tag", "")), "art-concepts-r43", "baked from the concept tag")
	for d in assets:
		var tex := AssetCard.texture_of(d.id)
		assert_not_null(tex, "%s has the concept's card (bake_defence_cards.py)" % d.id)
		assert_true((m.get("cards", {}) as Dictionary).has(String(d.id)), "%s is in the manifest" % d.id)
		var col: Array = ((m.get("cards", {}) as Dictionary).get(String(d.id), {}) as Dictionary).get("color", [])
		assert_eq(col.size(), 3, "%s has its concept colour" % d.id)
		if col.size() == 3:
			assert_eq(AssetCard.color_of(d.id), Color8(int(col[0]), int(col[1]), int(col[2])), "%s is drawn in it" % d.id)


func test_card_words_are_the_concepts_and_sit_on_the_face_at_every_text_size() -> void:
	for scale in SCALES:
		Settings.text_scale = scale
		for d in _assets():
			var card: AssetCard = add_child_autofree(AssetCard.new(d.id, d.display_name, d.integrity, 2))
			card.set_effect(d)
			card.size = AssetCard.card_size()
			assert_eq(card.integrity_text(), "INT %d" % d.integrity)
			assert_eq(card.count_text(), "x2")
			assert_ne(card.effect_text, "", "%s says what it does" % d.id)
			var face := card.face_rect()
			assert_true(Rect2(Vector2.ZERO, card.size).grow(0.5).encloses(card.card_rect()), "%s: the card fits its control at %.1f" % [d.id, scale])
			assert_true(face.grow(0.5).encloses(card.effect_rect()), "%s: the effect line on the face at %.1f" % [d.id, scale])
			var lay: Dictionary = card._layout()
			assert_true(float(lay["end"]) <= face.end.y + 0.5, "%s: the words end on the face at %.1f (%s > %s)" % [d.id, scale, lay["end"], face.end.y])


func test_rule_lines_say_how_a_defence_picks() -> void:
	var by_id := {}
	for d in _assets():
		by_id[d.id] = d
	assert_eq(AssetCard.rule_of(by_id[&"turret"]), "first in path")
	assert_eq(AssetCard.rule_of(by_id[&"flak_array"]), "weakest threat")
	assert_eq(AssetCard.rule_of(by_id[&"railgun"]), "hardest hitter")
	assert_eq(AssetCard.rule_of(by_id[&"decoy"]), "threats route to it")
	assert_eq(AssetCard.rule_of(by_id[&"ice_lock"]), "", "a hold has its effect line only")


func test_a_narrowed_card_shrinks_evenly_never_squashed() -> void:
	var card: AssetCard = add_child_autofree(AssetCard.new(&"turret", "Turret", 10, 1))
	card.size = AssetCard.card_size()
	var full := card.card_rect()
	card.custom_minimum_size.x = AssetCard.card_size().x * 0.8  # as the row fit narrows it
	card.size = Vector2(AssetCard.card_size().x * 0.8, AssetCard.card_size().y)
	var narrow := card.card_rect()
	assert_almost_eq(narrow.size.x / narrow.size.y, full.size.x / full.size.y, 0.01, "the card keeps its aspect")
	assert_true(narrow.size.x < full.size.x)
	assert_gt(card.die_cut_radius(), 0.0, "the parked vinyl matches the die-cut")


# --- RAID-03: DECRYPTED under the holo's header ------------------------------------------------------

func test_decrypted_stamp_never_covers_the_holo_header_or_a_row() -> void:
	for scale in SCALES:
		Settings.text_scale = scale
		for with_strip in [false, true]:
			var holo: RaidHolo = add_child_autofree(RaidHolo.new(&"meridian", "THREAT INTEL // SCAN", "4C-E7"))
			for i in 3:
				holo.add_line("COLLECTOR + HAULER > CORE (home)  //  Continuum Billing Farm")
			var strip: RaidIntelStrip = null
			if with_strip:
				var units: Array[Dictionary] = []
				for i in 3:
					units.append({"type": RaidVehicle.HEAVY, "name": "HAULER", "letter": "A%d" % (i + 1)})
				strip = RaidIntelStrip.new(&"meridian", units)
				holo.body.add_child(strip)
			holo.size = Vector2(300 * scale, 0)
			for f in 3:
				await get_tree().process_frame
			holo.size = Vector2(300 * scale, holo.get_combined_minimum_size().y)
			await get_tree().process_frame
			var stamp := holo.stamp_rect()
			assert_true(stamp.has_area())
			assert_true(stamp.position.y >= holo.head_bottom(), "the stamp is not on the header at %.1f (%s)" % [scale, stamp])
			for l in holo.body.get_children():
				if l is Label:
					var r := Rect2((l as Control).position + holo.body.position, (l as Control).size)
					assert_false(r.intersects(stamp), "the stamp covers no row at %.1f, strip %s (%s vs %s)" % [scale, with_strip, r, stamp])
			assert_true(stamp.end.x <= holo.size.x + 0.5 and stamp.end.y <= holo.size.y + 0.5, "the stamp on the holo")
			if strip != null:
				var cols := floori((strip.size.x - strip.reserve_right) / (RaidIntelStrip.COLUMN * scale))
				assert_true(holo.body.position.x + cols * RaidIntelStrip.COLUMN * scale <= stamp.position.x + 0.5, "the scanned threats end left of the stamp at %.1f" % scale)


# --- RAID-07: the carried card's arrow ends on a node ------------------------------------------------

func _drops() -> DropLayer:
	var drops: DropLayer = add_child_autofree(DropLayer.new())
	var rects := {"node:a": Rect2(400, 300, 20, 20), "node:b": Rect2(600, 300, 20, 20), "node:c": Rect2(500, 450, 20, 20)}
	for id: String in rects:
		var r: Rect2 = rects[id]
		drops.add_target(id, ["asset"], "node", StringName(id), func() -> Rect2: return r)
	drops.reasons = {"node:a": "", "node:b": "", "node:c": "NO SLOT"}
	return drops


func test_off_the_map_the_arrow_ends_on_the_nearest_node_that_takes_it() -> void:
	var pencil: RaidDragPencil = add_child_autofree(RaidDragPencil.new(_drops()))
	var start := Vector2(300, 650)
	var corner := pencil.aim_end(start, Vector2(1279, 719))
	assert_eq(String(corner[1]), "node:b", "the pointer in the screen's corner: the nearest node that takes it (not the refusing one)")
	var end: Vector2 = corner[0]
	assert_true(end.distance_to(Rect2(600, 300, 20, 20).get_center()) < 40.0, "the arrow ends at that node")
	var on_map := pencil.aim_end(start, Vector2(520, 350))
	assert_eq(String(on_map[1]), "", "over the map the arrow follows the pointer")
	assert_eq(on_map[0], Vector2(520, 350))


# --- RAID-08: the playout keeps CORE and the route's end in frame ----------------------------------

func test_each_step_frames_core_and_the_route_ends() -> void:
	var events: Array = [
		{"type": "threat_enters", "step": 1, "threat": "t1", "site": &"entry"},
		{"type": "move", "step": 1, "threat": "t1", "from": &"entry", "to": &"mid"},
		{"type": "move", "step": 2, "threat": "t1", "from": &"mid", "to": &"home"},
	]
	var ends := RaidBeats.route_ends(events)
	assert_eq(ends["t1"], &"home", "the route ends where the threat last goes")
	var steps := RaidBeats.group(events)
	var framed := RaidBeats.framed_sites(steps[1], {}, ends, &"core")
	assert_true(framed.has(&"core"), "CORE is in every step's frame")
	assert_true(framed.has(&"home"), "the route's end (its arrow head) is in the frame")
	assert_true(framed.has(&"entry") and framed.has(&"mid"), "the step's own fight stays framed")
	assert_eq(RaidBeats.framed_sites([], {}, ends, &"core").size(), 0, "a step with nothing to show is not framed")


# --- RAID-09: the feed never shows a cut line ---------------------------------------------------------

func test_the_feed_shows_its_newest_line_and_a_whole_top_line() -> void:
	for scale in SCALES:
		Settings.text_scale = scale
		var feed: RaidFeed = add_child_autofree(RaidFeed.new("PLAYOUT", Vector2(330, 150)))
		feed.label.add_theme_font_override("normal_font", Palette.mono_arrows())
		feed.size = Vector2(330, 150)
		for i in 14:
			feed.append("Step %d: Collector moves from Continuum Billing Farm to CORE: HP 50 → 45." % i)
		await get_tree().process_frame
		await get_tree().process_frame
		var tops: Array[float] = []
		for i in feed.label.get_paragraph_count():
			tops.append(feed.label.get_paragraph_offset(i))
		var top := feed.view_top()
		var on_line := false
		for t in tops:
			on_line = on_line or absf(t - top) < 0.5
		assert_true(on_line, "the view starts on a line at %.1f (top %s)" % [scale, top])
		var view := feed.size.y - RaidFeed.EDGE
		assert_true(top + view >= feed.label.get_content_height() - 0.5, "the newest line is in view at %.1f" % scale)
		assert_true(feed.clip_contents, "lines past the view are clipped")


# --- RAID-08: the playout frames only the Sites on its map ------------------------------------------

func test_the_playout_frames_only_sites_on_its_map() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var hq: Control = load("res://scenes/hq/hq_scene.tscn").instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for i in 3:
		await get_tree().process_frame
	hq.show_raid()
	for i in 4:
		await get_tree().process_frame
	var ov: CityMapOverlay = hq.city_overlay
	var panel := RaidPlayoutPanel.new(ov)
	add_child_autofree(panel)
	var home: StringName = c.grid.home_site_id
	assert_true(ov.has_site(home), "CORE is on the raid map")
	var kept := panel.on_map([home, &"no_such_site_off_the_map"] as Array[StringName])
	assert_eq(kept, [home] as Array[StringName], "a Site off the raid map is never framed (it had no spot and pulled the camera off CORE)")
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false


func test_core_stays_in_the_fight_frame_through_the_playout() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = true
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, RunManager.corporation, RC.RaidTriggerSource.STORY, &"", "test")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var hq: Control = load("res://scenes/hq/hq_scene.tscn").instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for i in 3:
		await get_tree().process_frame
	hq.show_raid()
	for i in 6:
		await get_tree().process_frame
	hq.fight_raid()
	var home: StringName = c.grid.home_site_id
	var checked := 0
	for i in PLAYOUT_FRAMES:
		await get_tree().process_frame
		if not is_instance_valid(hq.playout) or hq.playout.is_done():
			break
		if i % CHECK_EVERY == 0 and hq.playout.current_step() >= 2:
			var ov: CityMapOverlay = hq.city_overlay
			var p: Vector2 = ov.get_global_transform() * ov.icon_at(home)
			var area: Rect2 = hq.fight_area(hq._fight_area)
			assert_true(area.has_point(p), "CORE in the fight's frame at step %d (%s, %s)" % [hq.playout.current_step(), p, area])
			checked += 1
	assert_gt(checked, 0, "the playout was checked mid-way")
	Motion.force_live = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false


func test_the_fight_frame_centres_on_its_points_box_not_their_mean() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var hq: Control = load("res://scenes/hq/hq_scene.tscn").instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for i in 3:
		await get_tree().process_frame
	var wf: WireframeBackground = hq.wireframe
	# CORE far from a cluster of three entries (the playout's first frame adds CORE and the entries
	# again): the mean sits by the cluster, the box's centre between them.
	var core := Vector2(10.5, 10.5)
	var pts := PackedVector2Array([core, Vector2(30.5, 4.5), Vector2(31.5, 4.5), Vector2(30.5, 5.5)])
	wf.frame_points(pts, Rect2(300, 80, 900, 560), 4.0, 0.01)
	var tb: float = wf.city.tile_b()
	var box := Rect2(Vector2((core.x - core.y) * NeonCity.TILE_A, (core.x + core.y) * tb), Vector2.ZERO)
	for p in pts:
		box = box.expand(Vector2((p.x - p.y) * NeonCity.TILE_A, (p.x + p.y) * tb))
	var m := box.get_center()
	var want := Vector2(m.x / NeonCity.TILE_A + m.y / tb, m.y / tb - m.x / NeonCity.TILE_A) * 0.5
	assert_almost_eq(wf.city.focus_grid.x, want.x, 0.01, "the frame centres on the box")
	assert_almost_eq(wf.city.focus_grid.y, want.y, 0.01)
	await get_tree().process_frame
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	AudioDirector.muted = false
