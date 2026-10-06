extends GutTest
## M14 parity fix S-END (designer group ruling 2026-10-05: match the concepts; the campaign won
## keeps the M13 build's CORP DOWN poster beat reworked in v2; DECISIONS "Parity fix — endings
## (designer group ruling)"; docs/art_review/PARITY/GAPS.md END-03, END-05, END-06). Per id:
## END-03 the won file's CORP DOWN poster (the corporation's notice, the Cell's red pencil X,
## the CORP DOWN vinyl) and annex A's story in full; END-05 the lock's camera spreads the network
## round the notice; END-06 the corp paper covers its sheets, the stamp keeps off the values, the
## personnel notes stay on their page, the stickers keep off the signature. The abandoned
## campaign's own words, and ART-12 12p: the dossier is built in the lock's hold, so the cut
## shows a file already built.

const HQ := "res://scenes/hq/hq_scene.tscn"
const LAB_SCRIPT := "res://tools/design_lab/motion_lab.gd"
const SCREEN := Rect2(0, 0, 1280, 720)
const CUT_FRAMES := 240
const BEAT_TEXT := "The meters measure power and water. The firmware also measures voices, footsteps and how many people sleep in a room."

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_parity_endings"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
		Fx.apply_settings()
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


func _live() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()


func _key(k: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = true
	return e


## The facts of a campaign ending `outcome`, with a crew of four (one lost) and two story beats.
func _facts(outcome: int) -> DossierFacts:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	for cls in [&"ghost", &"rigger", &"breaker"]:
		var cd := RunManager.lookup().get_content(cls) as ClassData
		if cd != null:
			c.recruit(cd)
	c.roster[1].alive = false
	c.heat = 82
	c.outcome = outcome
	var beats: Array[Dictionary] = [{"title": "Smart Meters I", "text": BEAT_TEXT}, {"title": "Smart Meters II", "text": BEAT_TEXT + " " + BEAT_TEXT}]
	return DossierFacts.build(c, RunManager.corporation, RunManager.profile, RunManager.config(), func(id: StringName) -> String: return String(id),
		func(id: StringName) -> String: return String(id), beats, 3)


func _dossier(outcome: int, photos: Array[Dictionary] = []) -> AuditDossier:
	var d: AuditDossier = add_child_autofree(AuditDossier.new(_facts(outcome), photos))
	d.size = SCREEN.size
	return d


## The screen-space box of control `c` as drawn (its rotation and scale included).
static func _drawn(c: Control) -> Rect2:
	return _drawn_rect(c, Rect2(Vector2.ZERO, c.size))


## The screen-space box of `local` (in `c`'s space) as drawn.
static func _drawn_rect(c: CanvasItem, local: Rect2) -> Rect2:
	var xf := c.get_global_transform()
	var r := Rect2(xf * local.position, Vector2.ZERO)
	for p in [Vector2(local.end.x, local.position.y), local.end, Vector2(local.position.x, local.end.y)]:
		r = r.expand(xf * p)
	return r


# --- END-03 -------------------------------------------------------------------------------------

func test_end_03_a_won_file_leads_with_the_corp_down_poster() -> void:
	var prints: Array[Dictionary] = [{"caption": "BOSS - OFFLINE"}, {"caption": "NODES AT THE END"}, {"caption": "VEX - AT LARGE"}]
	var d := _dossier(CampaignState.Outcome.WON, prints)
	await _frames(3)
	var p := d.poster
	assert_not_null(p, "a won file has its CORP DOWN poster")
	assert_eq(p.style.corp_id, d.facts.corporation_id, "the corporation's own notice, in its house style")
	assert_eq(p.boss_name, d.facts.boss_name, "it names the boss that went offline")
	assert_eq(p.sticker.text, tr("CORP DOWN"), "CORP DOWN is the Cell's vinyl")
	assert_eq(p.sticker.fill, VinylSticker.Fill.YELLOW)
	assert_eq(p.pencil.ink, GreasePencilMark.Ink.THREAT, "the Cell's red pencil X (spray is a rejected medium)")
	assert_eq(p.pencil.strokes().size(), 2, "an X: two strokes")
	assert_true(p.pencil.is_in_group(GreasePencilMark.GROUP))
	var row := d.left_page.get_node("Prints")
	assert_eq(row.get_child_count(), prints.size(), "the poster takes the boss print's place, the others stay")
	assert_eq(row.get_child(0).get_child(0), p, "first on the left page")
	# Headless: the end state at once.
	assert_false(d.motion_running())
	assert_eq(p.write_t, 1.0, "the X is written")
	assert_true(p.sticker.visible and p.visible, "the poster and CORP DOWN at rest")
	for outcome in [CampaignState.Outcome.LOST, CampaignState.Outcome.ABANDONED]:
		var other := _dossier(outcome)
		assert_null(other.poster, "only a won file has the poster")


func test_end_03_the_corp_down_sticker_never_covers_the_pencil() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var d := _dossier(CampaignState.Outcome.WON)
		await _frames(3)
		var p := d.poster
		var body := _drawn_rect(p.sticker, p.sticker.body_rect)
		for seg in p.pencil.segment_rects():
			assert_false(seg.intersects(body), "%.1f: no UI covers grease pencil (the sticker's body %s, a stroke %s)" % [scale, body, seg])
		var paper := _drawn_rect(p, p.paper_rect())
		assert_true(body.get_center().x > paper.position.x and body.get_center().x < paper.end.x, "%.1f: CORP DOWN across the poster's foot" % scale)
		d.queue_free()
		await _frames(1)


func test_end_03_the_poster_beat_plays_after_the_stamp_and_one_press_completes_it() -> void:
	_live()
	var d := _dossier(CampaignState.Outcome.WON)
	await _frames(1)
	assert_true(d.motion_running())
	assert_true(d.MOTIONS.has(AuditDossier.POSTER))
	assert_gt(d.poster_write_at(), Motion.delay_of(AuditDossier.STAMP), "the poster lands after the AT LARGE stamp")
	assert_gte(d.poster_slap_at(), d.poster_write_at(), "the X writes on, then CORP DOWN slaps on")
	assert_gte(d.motion_end(), d.poster_slap_at(), "the file's motion runs to the sticker's slap")
	assert_false(d.poster.sticker.visible, "CORP DOWN waits for its slap")
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(d.motion_running(), "one press: the open file")
	assert_eq(d.poster.write_t, 1.0, "the X written")
	assert_true(d.poster.sticker.visible, "CORP DOWN on the poster")
	assert_eq(d.poster.sticker.scale, Vector2.ONE)
	assert_eq(d.poster.scale, Vector2.ONE)


func test_end_03_reduce_effects_shows_the_poster_at_rest() -> void:
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	var d := _dossier(CampaignState.Outcome.WON)
	await _frames(3)
	assert_false(d.motion_running())
	assert_eq(d.poster.in_t, 1.0)
	assert_eq(d.poster.write_t, 1.0)
	assert_true(d.poster.sticker.visible)


func test_end_03_annex_a_types_the_story_in_full_and_the_file_fits_at_1_0() -> void:
	for outcome in [CampaignState.Outcome.LOST, CampaignState.Outcome.WON]:
		var d := _dossier(outcome)
		await _frames(4)
		var texts := d.find_children("BeatText*", "Label", true, false)
		var titles := d.find_children("BeatTitle*", "Label", true, false)
		assert_eq(texts.size(), d.facts.beats.size(), "every intercept's words")
		assert_eq(titles.size(), d.facts.beats.size(), "every intercept's title")
		if not texts.is_empty():
			assert_eq((texts[0] as Label).text, BEAT_TEXT, "the words, not a tooltip")
			assert_eq((titles[0] as Label).text, "SMART METERS I")
		assert_not_null(d.story_view, "the story scrolls inside its sheet when long")
		assert_false(d.spread.vertical, "1.0: the pages side by side")
		var col := d.get_child(0) as Control
		assert_lte(d.global_position.y + col.get_combined_minimum_size().y, SCREEN.size.y + 1.0, "%d: the file fits the screen at 1.0" % outcome)
		d.queue_free()
		await _frames(1)


func test_end_03_the_hqs_end_page_fits_its_page_at_1_0_with_the_stickers_on_it() -> void:
	for outcome in [CampaignState.Outcome.LOST, CampaignState.Outcome.WON]:
		RunManager.reset()
		RunManager.new_campaign(1)
		var c := RunManager.campaign
		for cls in [&"ghost", &"rigger", &"breaker"]:
			var cd := RunManager.lookup().get_content(cls) as ClassData
			if cd != null:
				c.recruit(cd)
		c.story_beats_revealed = 2
		DemoSetup.end_campaign(c, outcome)
		var holder: Control = add_child_autofree(Control.new())
		holder.size = SCREEN.size
		var hq: Control = load(HQ).instantiate()
		holder.add_child(hq)
		hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		await _frames(2)
		hq.show_end()
		await _frames(6)
		var d := hq._panel as AuditDossier
		assert_not_null(d)
		var page := d._page_bottom()
		for b: Control in [d.main_menu_button, d.new_campaign_button]:
			assert_lte(b.get_global_rect().end.y, page + 1.0, "%d: %s on the page, no scrolling for it at 1.0 (page foot %.0f)" % [outcome, b.name, page])
		holder.queue_free()
		await _frames(2)


func test_end_03_and_end_06_the_ends_fit_at_every_text_size() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		for outcome in [CampaignState.Outcome.WON, CampaignState.Outcome.LOST, CampaignState.Outcome.ABANDONED]:
			var d := _dossier(outcome)
			await _frames(3)
			for c in d.find_children("*", "PaperSheet", true, false) + ([d.poster] if d.poster != null else []):
				var r := (c as Control).get_global_rect()
				assert_true(r.end.x <= SCREEN.size.x + 1.0 and r.position.x >= -1.0, "%.1f/%d: %s on the screen's width: %s" % [scale, outcome, c.name, r])
			for b: Control in [d.main_menu_button, d.new_campaign_button]:
				assert_true(b.get_global_rect().end.x <= SCREEN.size.x + 1.0, "%.1f: %s on the screen" % [scale, b.name])
			d.queue_free()
			await _frames(1)


# --- END-06 -------------------------------------------------------------------------------------

func test_end_06_the_corp_paper_covers_its_whole_sheet() -> void:
	var d := _dossier(CampaignState.Outcome.LOST)
	await _frames(3)
	for sheet: PaperSheet in d.find_children("*", "PaperSheet", true, false):
		var stock := sheet._paper
		assert_eq(stock.position, Vector2.ZERO, "%s: the stock from the sheet's corner (no inset by its pads)" % sheet.name)
		assert_eq(stock.size, sheet.size, "%s: the stock is the whole sheet (no shadow band round it)" % sheet.name)


func test_end_06_the_stamp_keeps_off_the_reports_values() -> void:
	for outcome in [CampaignState.Outcome.LOST, CampaignState.Outcome.WON, CampaignState.Outcome.ABANDONED]:
		var d := _dossier(outcome)
		await _frames(4)
		var stamp := _drawn(d.case_stamp)
		var f := d.fields.get_theme_font(&"font")
		var fs := d.fields.get_theme_font_size(&"font_size")
		var line_h := f.get_height(fs) + d.fields.get_theme_constant(&"line_spacing")
		var lines := d.report_lines()
		for i in AuditDossier.STAMP_CLEAR_LINES:
			var core := AuditDossier.value_core(lines[i])
			var at := d.fields.get_global_transform() * Vector2(0, line_h * i)
			var value := Rect2(at, Vector2(f.get_string_size(core, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x, line_h))
			assert_false(stamp.intersects(value.grow(-1.0)), "%d: the stamp %s keeps off \"%s\" %s" % [outcome, stamp, core, value])
		d.queue_free()
		await _frames(1)


func test_end_06_the_personnel_notes_stay_on_their_page_and_the_stickers_off_the_signature() -> void:
	var d := _dossier(CampaignState.Outcome.LOST)
	await _frames(4)
	var report := d.report.get_global_rect()
	for i in 2:
		var n := _drawn(d.notes[i])
		assert_lte(n.end.x, report.position.x + 1.0, "note %d stays on the left page (it cut the report's typed lines)" % i)
	for b: Control in [d.main_menu_button, d.new_campaign_button]:
		var r := b.get_global_rect()
		assert_lte(r.position.y, SCREEN.size.y, "%s on the screen" % b.name)
		assert_false(r.intersects(report.grow(-2.0)), "%s keeps off the report (its signature): %s vs %s" % [b.name, r, report])


# --- Abandoned ----------------------------------------------------------------------------------

func test_an_abandoned_campaign_is_a_loss_in_its_own_words() -> void:
	var d := _dossier(CampaignState.Outcome.ABANDONED)
	await _frames(3)
	assert_true(d.facts.abandoned)
	assert_false(d.facts.won)
	assert_eq(d.case_stamp.text, tr("CASE CLOSED"), "the lost file's stamp (DECISIONS Abandon campaign)")
	var lines := "\n".join(d.report_lines())
	assert_string_contains(lines, tr("STOOD DOWN  (operations abandoned)"))
	assert_false(lines.contains("BREACHED"), "the home server did not fall")
	assert_eq(d.note_words()[2], tr("they walked away at heat %d. nobody walks away.") % d.facts.heat)


func test_an_abandoned_campaign_shows_the_dossier_without_the_lock_even_live() -> void:
	_live()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	DemoSetup.end_campaign(c, CampaignState.Outcome.ABANDONED)
	var before := c.state_hash()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(2)
	hq.show_end()
	await _frames(2)
	assert_null(hq.end_lock, "the ransom lock is the breach's (LOST) alone")
	assert_eq(hq.panel_name, "end")
	assert_true((hq._panel as AuditDossier).facts.abandoned)
	assert_eq(c.state_hash(), before, "the end screens change nothing")


# --- END-05 and 12p -----------------------------------------------------------------------------

func test_end_05_the_lock_camera_fit_spreads_the_network_on_the_screen() -> void:
	var c := SCREEN.get_center()
	var room := SCREEN.grow(-40.0)
	var notice := Rect2(c - Vector2(350, 170), Vector2(700, 340))
	# Off the screen at 2.0 (the old camera): a node 700 px left, one 500 / 300 off the centre.
	var far: Array = [{"at": c + Vector2(-700, 0)}, {"at": c + Vector2(500, 300)}, {"at": c + Vector2(0, -250)}]
	var z := RansomLock.fit_zoom(far, c, room, notice, 2.0, 0.5, 2.0)
	for p: Dictionary in far:
		var at := c + ((p["at"] as Vector2) - c) * z / 2.0
		assert_true(room.has_point(at) and not notice.has_point(at), "every padlock on the city round the notice after the fit: %s (zoom %.2f)" % [at, z])
	# A tight network spreads out of the notice, up to the most zoom.
	var near: Array = [{"at": c + Vector2(-200, 0)}, {"at": c + Vector2(200, 100)}]
	var zn := RansomLock.fit_zoom(near, c, room, notice, 1.0, 0.5, 1.9)
	assert_gt(zn, 1.0, "a tight network spreads out")
	for p: Dictionary in near:
		assert_false(notice.has_point(c + ((p["at"] as Vector2) - c) * zn), "out from under the notice")
	assert_eq(RansomLock.fit_zoom([{"at": c}], c, room, notice, 1.3, 0.5, 1.9), 1.9, "nothing to gain: the largest zoom")
	assert_eq(RansomLock.fit_zoom([], c, room, notice, 1.3, 0.5, 1.9), 1.3, "no network: as it was")
	assert_gte(RansomLock.fit_zoom(far, c, room, notice, 2.0, 1.5, 2.0), 1.5, "never under the least zoom")


func test_12p_the_dossier_is_built_in_the_locks_hold_and_the_cut_shows_it() -> void:
	_live()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	DemoSetup.end_campaign(c, CampaignState.Outcome.LOST)
	var before := c.state_hash()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(2)
	hq.show_end()
	await _frames(2)
	var lock: RansomLock = hq.end_lock
	assert_not_null(lock)
	assert_eq(hq._below(Rect2(0, 10, 50, 50), 57.0), Rect2(0, 57, 50, 50), "END-06: a print's crop starts under the top bar")
	assert_eq(hq._below(Rect2(0, 90, 50, 50), 57.0), Rect2(0, 90, 50, 50), "a crop under it keeps its place")
	await BoundedWait.until(get_tree(), func() -> bool: return lock.started, 10.0, RansomLock.START_FRAMES + 2)
	assert_true(lock.started)
	var held := [false]
	lock.holding.connect(func() -> void: held[0] = true)
	lock.complete_motion()
	await BoundedWait.until(get_tree(), func() -> bool: return held[0] or lock.done, 5.0)
	assert_true(held[0], "the countdown at zero: the reading hold")
	if not lock.done:
		var pre: AuditDossier = hq._end_dossier
		assert_not_null(pre, "the file is built in the hold, before the cut")
		if pre != null:
			assert_true(pre.is_inside_tree(), "mounted behind the lock")
			assert_true(pre.held and not pre.motion_running(), "held still: its motion waits for the cut")
			assert_eq(pre.modulate.a, 0.0, "unseen behind the lock (its glass reads the screen)")
			assert_eq(hq.panel_name, "end_lock", "the lock's page still")
		lock.cut()
		await BoundedWait.until(get_tree(), func() -> bool: return hq.panel_name == "end", 5.0, CUT_FRAMES)
		assert_eq(hq.panel_name, "end")
		assert_eq(hq._panel, pre, "the cut shows the file built in the hold (no build at the switch)")
		if pre != null and is_instance_valid(pre):
			assert_false(pre.held, "released: the cover swings open now")
			assert_eq(pre.modulate.a, 1.0)
			assert_true(pre.motion_running(), "its own motion plays from the start")
	assert_eq(c.state_hash(), before, "the end screens change nothing")


# --- Motion table -------------------------------------------------------------------------------

func test_the_poster_motion_is_required_and_has_its_lab_demo() -> void:
	var demos: Dictionary = (load(LAB_SCRIPT) as GDScript).get_script_constant_map()["DEMOS"]
	var id := AuditDossier.POSTER
	assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
	assert_true(Motion.has(id), "%s is in ui_motion.tres" % id)
	assert_true(demos.has(id) and String((demos[id] as Array)[0]) == "screen", "%s has a demo on its real piece" % id)
