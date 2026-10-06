extends GutTest
## Parity fix: overlap defects (M14, designer approved 2026-10-05; DECISIONS "Parity fix —
## overlap defects"; docs/art_review/PARITY/GAPS.md SHOP-01, GRID-03, GRID-12, GRID-13,
## RAID-02, RAID-08, RAID-11, END-06). Each is wrong whichever look is chosen: these check
## the rects (at text 1.0, 1.6 and the largest size), never the look.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, Settings.TEXT_SCALE_MAX]
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
## Frames for the Grid map to settle (the fit waits for the city each pass).
const SETTLE := 12
## GRID-12: the share of the map area's sample points that must show the city (not the fog
## past its edge), and the samples per side.
const ON_CITY_MIN := 0.75
const SAMPLES := 12

var _scale: float = 1.0
var _reduce: bool = false


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_overlaps"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
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


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _close(scene: Control) -> void:
	if is_instance_valid(scene) and scene.get_parent() != null:
		scene.get_parent().queue_free()
	await _frames(2)


func _open_all() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10


# --- SHOP-01 ------------------------------------------------------------------------------------

func test_shop_01_the_clerk_note_sits_under_the_clerk_words() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var net := _scene(NETRUN)
		net.new_campaign(1)
		net.start_run(1)
		await _frames()
		DemoSetup.open_shop(RunManager.netrun, 400)
		net._show_current()
		await _frames(4)
		var root: Control = net._panel
		var note := root.find_child("ClerkNote", true, false) as PencilNote
		var clerk := root.find_child("Clerk", true, false) as Control
		assert_not_null(note, "%.1f: the clerk's note" % scale)
		if note == null or not note.is_visible_in_tree() or clerk == null or not clerk.is_visible_in_tree():
			# Big words: the clerk steps aside and its note with it.
			assert_false(note != null and note.is_visible_in_tree() and (clerk == null or not clerk.is_visible_in_tree()), "%.1f: no note without its clerk" % scale)
			await _close(net)
			continue
		var words := clerk.find_child("ClerkWords", true, false) as Control
		var wallet := root.find_child("Wallet", true, false) as Control
		var r := note.get_global_rect()
		assert_false(r.intersects(words.get_global_rect()), "%.1f: the note %s never covers the clerk's words %s" % [scale, r, words.get_global_rect()])
		assert_true(r.position.y >= words.get_global_rect().end.y - 0.5, "%.1f: the note sits under the last clerk line" % scale)
		assert_true(r.position.x > words.get_global_rect().position.x, "%.1f: offset right of the words' start" % scale)
		if wallet != null and wallet.is_visible_in_tree():
			assert_false(r.intersects(wallet.get_global_rect()), "%.1f: the note keeps off the wallet" % scale)
		assert_true(SCREEN.encloses(r), "%.1f: the note on screen" % scale)
		await _close(net)


# --- GRID-03 / GRID-13 / GRID-12 ------------------------------------------------------------------

func _hq_grid(corp: StringName, scale: float) -> Control:
	RunManager.reset()
	Settings.set_text_scale(scale)
	var hq := _scene(HQ)
	_open_all()
	hq.new_campaign(1, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, corp)
	hq.selected_site = &""
	hq.show_grid()
	await _frames(SETTLE)
	return hq


func _boss(overlay: CityMapOverlay) -> Dictionary:
	for n in overlay.nodes:
		if n.has("marker") and n["marker"].get("kind") == SiteMarker.KIND_CENTRAL_SERVER:
			return n
	return {}


func test_grid_03_13_the_central_server_chip_and_target_pencil_cover_nothing_and_labels_keep_apart() -> void:
	for corp in CORPS:
		for scale in SCALES:
			var hq := await _hq_grid(corp, scale)
			var ov: CityMapOverlay = hq.city_overlay
			var boss := _boss(ov)
			var labels := ov.label_rects()
			var what := "%s %.1f" % [corp, scale]
			var pencil: Array[Rect2] = []
			if not boss.is_empty() and ov.icon_pos(boss).x != INF and ov.marker_shown(boss):
				pencil = ov.boss_rects(boss)
				assert_eq(pencil.size(), 3, "%s: the chip, the circle and the word" % what)
			for key in labels:
				var lr: Rect2 = labels[key]
				for p in pencil:
					assert_false(lr.intersects(p), "%s: label %s %s clear of the boss's chip / TARGET pencil %s" % [what, key, lr, p])
				for other in labels:
					if String(other) > String(key):
						assert_false(lr.grow(0.5).intersects((labels[other] as Rect2).grow(0.5)),
							"%s: labels %s and %s never touch" % [what, key, other])
				for n in ov.nodes:
					if ov.icon_pos(n).x == INF or not ov.marker_shown(n) or String(key).begins_with(String(n["id"])) or n == boss:
						continue
					assert_false(CityMapOverlay._rect_hits_disc(lr, ov.icon_pos(n), ov.icon_radius(n) + 0.5), "%s: label %s off %s's marker" % [what, key, n["id"]])
			for n in ov.nodes:
				if n == boss or ov.icon_pos(n).x == INF or not ov.marker_shown(n):
					continue
				for p in pencil:
					assert_false(ov.icon_rect(n).intersects(p), "%s: %s's marker %s clear of the boss's chip / TARGET pencil %s" % [what, n["id"], ov.icon_rect(n), p])
			await _close(hq)


## The share of the map area's sample points whose ground lies on the city (inside the
## config's city rect, not the fog past its edge).
func _on_city_share(hq: Control) -> float:
	var city: NeonCity = hq.wireframe.city
	var area: Rect2 = (hq.grid_legend.get_parent() as Control).get_global_rect()
	var to_page: Transform2D = hq.get_global_transform().affine_inverse()
	var r := Rect2(CityView3D.CONFIG.city_rect)
	var on := 0
	for i in SAMPLES:
		for j in SAMPLES:
			var p := to_page * (area.position + area.size * Vector2((i + 0.5) / SAMPLES, (j + 0.5) / SAMPLES))
			var g := CityMapCamera.grid_at(p, hq.size, city.focus_grid, city.focus_anchor, city.scale.x, city.tile_b())
			if r.has_point(g):
				on += 1
	return float(on) / float(SAMPLES * SAMPLES)


func test_grid_12_every_corps_fitted_camera_stays_on_the_city() -> void:
	for corp in CORPS:
		for scale in SCALES:
			var hq := await _hq_grid(corp, scale)
			var share := _on_city_share(hq)
			gut.p("GRID-12 %s %.1f: %.2f of the map on the city" % [corp, scale, share])
			assert_true(share >= ON_CITY_MIN, "%s %.1f: the map shows the city, not the fog past its edge (%.2f on the city)" % [corp, scale, share])
			# The fit still holds every node on the map beside the column.
			var area: Rect2 = (hq.grid_legend.get_parent() as Control).get_global_rect()
			for r in LegendSpot.node_rects(hq.city_overlay, false):
				assert_true(area.grow(LegendSpot.MARGIN).has_point(r.get_center()), "%s %.1f: node %s stays on the map area %s (the fit's margin)" % [corp, scale, r, area])
			# The TARGET pencil stays on the map beside the column, off the minimap and the key.
			for p in hq._grid_pencil_rects():
				assert_true(p.position.x >= area.position.x - 1.0 and p.end.x <= area.end.x + 1.0, "%s %.1f: the TARGET pencil %s on the map, never under the column (%s)" % [corp, scale, p, area])
				for c in [hq.grid_minimap, hq.grid_legend]:
					if c != null and is_instance_valid(c) and (c as Control).is_visible_in_tree():
						assert_false(p.intersects(Rect2((c as Control).global_position, (c as Control).size * (c as Control).scale)), "%s %.1f: the TARGET pencil %s off %s" % [corp, scale, p, (c as Control).name])
			await _close(hq)


# --- RAID-02 / RAID-08 / RAID-11 --------------------------------------------------------------------

func _raid_campaign() -> void:
	RunManager.new_campaign(7)
	var c := RunManager.campaign
	var g := RunManager.corporation.city_grid
	var first: StringName = g.get_site(g.home_site_id).links[0]
	DemoSetup.set_schematics(c, 100)
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	var armory: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]
	DemoSetup.set_armory(c, armory)
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)


## The value Labels on a raid paper (its rows' right-hand Anton words).
func _values(paper: RaidPaper) -> Array[Label]:
	var out: Array[Label] = []
	for l in paper.find_children("*", "Label", true, false):
		var lab := l as Label
		if lab.is_visible_in_tree() and lab.get_parent() is HBoxContainer and lab.horizontal_alignment == HORIZONTAL_ALIGNMENT_RIGHT:
			out.append(lab)
	return out


func _paper_rows(paper: RaidPaper) -> Array[Control]:
	var out: Array[Control] = []
	for l in paper.find_children("*", "Label", true, false):
		var lab := l as Label
		if lab.is_visible_in_tree() and lab.text != "":
			out.append(lab)
	return out


func test_raid_02_the_work_order_stamp_disc_and_instruction_line_cover_no_value() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		_raid_campaign()
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(6)
		var what := "%.1f" % scale
		var card := hq._panel.find_child("RaidCard", true, false) as RaidPaper
		assert_not_null(card, what)
		var stamp := card.stamp_rect()
		for l in _paper_rows(card):
			assert_false(stamp.intersects(l.get_global_rect()), "%s: INTERCEPTED %s covers no words (%s %s)" % [what, stamp, l.text, l.get_global_rect()])
		assert_true(card.get_global_rect().grow(1.0).encloses(stamp), "%s: the stamp stays on the paper" % what)
		var disc := card.find_child("Projection", true, false) as Control
		for l in _values(card):
			assert_false(disc.get_global_rect().intersects(l.get_global_rect()), "%s: the forecast disc covers no value (%s)" % [what, l.text])
		var intro := hq._panel.find_child("RaidIntro", true, false) as Label
		var box := intro.get_parent() as PanelContainer
		assert_not_null(box, "%s: the instruction line is boxed" % what)
		if box != null:
			assert_true(box.get_theme_stylebox(&"panel") is StyleBoxFlat, "%s: on a dark plate" % what)
		assert_true(intro.get_global_rect().end.y <= card.get_global_rect().position.y - RaidPaper.CLIP_TOP * Settings.text_scale, "%s: the paper clip never reaches the instruction line" % what)
		await _close(hq)


func test_raid_11_the_report_classified_stamp_covers_no_row() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		_raid_campaign()
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(2)
		RunManager.fight_raid()
		hq.show_raid_summary()
		await _frames(4)
		var paper := hq._panel.find_child("RaidReport", true, false) as RaidPaper
		assert_not_null(paper)
		var stamp := paper.stamp_rect()
		for l in _paper_rows(paper):
			assert_false(stamp.intersects(l.get_global_rect()), "%.1f: CLASSIFIED %s covers no row (%s %s)" % [scale, stamp, l.text, l.get_global_rect()])
		await _close(hq)


func test_raid_08_start_defense_peels_off_where_it_was_never_over_the_legend() -> void:
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(6)
	var was := (hq._panel.find_child("RunRaid", true, false) as Control).get_global_rect()
	Motion.force_live = true
	hq.fight_raid()
	await _frames(1)
	var peel := hq.get_node_or_null(^"StartPeel") as RaidSticker
	assert_not_null(peel, "the sticker peels off as the playout starts")
	if peel != null:
		assert_true(peel.get_global_rect().intersects(was), "it peels from where START DEFENSE was (%s, was %s)" % [peel.get_global_rect(), was])
		var legend := hq._fight_area[1] as Control
		assert_false(peel.get_global_rect().intersects(legend.get_global_rect()), "never over the playout's MAP LEGEND")
		peel.vinyl.complete_motion()
		await _frames(2)
		assert_false(is_instance_valid(peel) and peel.is_visible_in_tree(), "gone once its peel ends")
	Motion.force_live = false
	await _close(hq)


# --- END-06 -------------------------------------------------------------------------------------

func test_end_06_the_dossiers_manila_is_held_and_drawn_not_white() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	c.outcome = CampaignState.Outcome.LOST
	var facts := DossierFacts.build(c, RunManager.corporation, RunManager.profile, RunManager.config(), func(id: StringName) -> String: return String(id),
		func(id: StringName) -> String: return String(id), [] as Array[Dictionary], 3)
	var d: AuditDossier = add_child_autofree(AuditDossier.new(facts))
	d.size = SCREEN.size
	await _frames(3)
	# The folder has drawn: its manila is held (a texture loaded inside a draw call and let go is
	# freed before the frame renders: the folder drew white).
	assert_not_null(d._manila_tex, "the manila is loaded and held at draw time")
	if d._manila_tex != null:
		assert_eq(d._manila_tex.resource_path, AuditDossier.MANILA_ART, "round 21's manila stock")
	var src := FileAccess.get_file_as_string("res://scripts/ui/campaign_end/audit_dossier.gd") + FileAccess.get_file_as_string("res://scripts/ui/campaign_end/dossier_photo.gd")
	assert_false(src.contains("draw_texture_rect(load("), "no texture is loaded inside a draw call")
	assert_false(src.contains("var t := load(MANILA_ART)"), "the folder draws the held stock")
