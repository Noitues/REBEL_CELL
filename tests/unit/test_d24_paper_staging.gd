extends GutTest
## D24: the raid papers and the operative dossier sit on the table like the case files: a 1 to 2
## degree tilt from a seeded stream (the same for the same id), a 6 px contact shadow and the
## paper clip. Headless; the looks are read windowed.

const SCALES: Array[float] = [1.0, 1.6, 2.0]
const SCREEN := Vector2(1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)


func _dossier_data(op: String) -> Dictionary:
	return {"corp": "Halcyon Systems", "corp_color": Palette.CORP_MERIDIAN, "subject": "Vex", "class_word": "Runner",
		"class_id": "runner", "operative_id": op, "rank": 2, "hp": 20, "max_hp": 24, "ram": 4,
		"wheel": ["A", "B"], "hub": "Core", "deck": 12, "station": ["+1 ICE"]}


func test_tilt_is_one_to_two_degrees_and_deterministic() -> void:
	var signs := {}
	for i in 40:
		var id := "doc_%d" % i
		var t := PaperStaging.tilt_degrees(id)
		assert_between(absf(t), PaperStaging.TILT_MIN, PaperStaging.TILT_MAX, "%s: 1 to 2 degrees" % id)
		assert_eq(PaperStaging.tilt_degrees(id), t, "%s: the same every time" % id)
		signs[signf(t)] = true
	assert_eq(signs.size(), 2, "it leans both ways across ids")
	assert_ne(PaperStaging.tilt_degrees("a"), PaperStaging.tilt_degrees("b"), "ids differ")


func test_shadow_is_six_px() -> void:
	assert_eq(PaperStaging.SHADOW_PX, 6.0, "a 6 px contact shadow")
	assert_gt(PaperStaging.CLIP_RISE, 0.0, "the clip rises over the top edge")


func test_raid_paper_is_tilted_with_clip_room_at_every_scale() -> void:
	for k in SCALES:
		Settings.set_text_scale(k)
		var p := RaidPaper.new(&"meridian", "MANIFEST AUDIT", RaidPaper.STAMP_INTERCEPTED, "WO 52-MF-114")
		p.add_row("Loss", "12")
		p.add_row("Gain", "3")
		add_child_autofree(p)
		p.size = p.get_combined_minimum_size()
		await get_tree().process_frame
		assert_between(absf(p.rotation_degrees), PaperStaging.TILT_MIN, PaperStaging.TILT_MAX, "x%s: tilted" % k)
		assert_almost_eq(p.rotation_degrees, p.tilt(), 0.001, "x%s: the seeded tilt" % k)
		assert_eq(p.pivot_offset, p.size * 0.5, "x%s: about its centre" % k)
		var twin := RaidPaper.new(&"meridian", "MANIFEST AUDIT", RaidPaper.STAMP_INTERCEPTED, "WO 52-MF-114")
		assert_eq(twin.tilt(), p.tilt(), "x%s: the same id, the same tilt" % k)
		# The tilt's reach stays inside the paper's own margin, so no word leaves the sheet.
		var reach := PaperStaging.reach(p.size, p.rotation_degrees)
		assert_lte(reach.x, RaidPaper.PAD * k, "x%s: the tilt stays inside the side margin" % k)
		twin.free()


func test_dossier_is_tilted_at_every_scale_and_keeps_its_fit() -> void:
	for k in SCALES:
		Settings.set_text_scale(k)
		var d := OperativeDossier.new()
		add_child_autofree(d)
		d.show_file(_dossier_data("op_vex"))
		d.size = d.custom_minimum_size
		await get_tree().process_frame
		assert_between(absf(d.rotation_degrees), PaperStaging.TILT_MIN, PaperStaging.TILT_MAX, "x%s: tilted" % k)
		assert_almost_eq(d.rotation_degrees, d.tilt(), 0.001, "x%s: the seeded tilt" % k)
		assert_eq(d.tilt(), PaperStaging.tilt_degrees("dossier|op_vex"), "x%s: seeded from the operative id" % k)
		assert_not_null(d.find_child("ContactShadow", false, false), "x%s: the contact shadow" % k)
		# The sheet's width still stays within its screen share, and the tilt's reach inside the
		# map area's corner margin plus the shadow.
		assert_lte(d.size.x, maxf(OperativeDossier.WIDTH * k, 1.0), "x%s: the file's own width" % k)
		var reach := PaperStaging.reach(d.size, d.rotation_degrees)
		assert_lte(reach.x + PaperStaging.SHADOW_PX * k, SCREEN.x * 0.1, "x%s: the tilt leaves the map room alone" % k)


const SHEET_FLOOR := 320.0
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]


func test_the_clip_bites_into_padding_and_the_letterhead_starts_below_it() -> void:
	assert_eq(PaperStaging.CLIP_BITE, 14.0, "the clip's bite is 14 px at 1.0")
	for k in SCALES:
		Settings.set_text_scale(k)
		var p := RaidPaper.new(&"solace", "T", RaidPaper.STAMP_CLASSIFIED, "WO 1")
		add_child_autofree(p)
		assert_almost_eq(p.top_pad(), PaperStaging.CLIP_BITE * k, 0.001, "x%s: RaidPaper's top padding" % k)
		assert_almost_eq(p.paper.top_pad, p.top_pad(), 0.001, "x%s: the sheet's letterhead sits below the jaw" % k)
		var d := OperativeDossier.new()
		add_child_autofree(d)
		d.show_file(_dossier_data("op_vex"))
		assert_almost_eq(d.paper.top_pad, PaperStaging.CLIP_BITE * k, 0.001, "x%s: the dossier's too" % k)


func test_every_letterhead_label_fits_the_sheet_width() -> void:
	for k in SCALES:
		Settings.set_text_scale(k)
		for corp in CORPS:
			var p := RaidPaper.new(corp, "T", RaidPaper.STAMP_CLASSIFIED, "WO 1")
			add_child_autofree(p)
			var w := maxf(p.get_combined_minimum_size().x, SHEET_FLOOR * k)
			var room := w - UiTheme.SP_L * 2.0
			var div := Palette.paper().get_string_size(p.skin.division(), HORIZONTAL_ALIGNMENT_LEFT, -1, p.division_px(w)).x
			assert_lte(div, room, "%s x%s: the division line fits the sheet" % [corp, k])
			var head := Palette.body_medium().get_string_size(p.paper.corp_name, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.LABEL)).x
			assert_lte(head, room, "%s x%s: the corp name fits the sheet" % [corp, k])
		var d := OperativeDossier.new()
		add_child_autofree(d)
		d.show_file(_dossier_data("op_vex"))
		for line in d.sub_lines(d.custom_minimum_size.x):
			var lw := RouteInk.paper_font().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, maxi(roundi(OperativeDossier.SUB_FONT * k), 1)).x
			assert_lte(lw, d.custom_minimum_size.x - OperativeDossier.MARGIN * k * 2.0, "x%s: the dossier's sub line fits" % k)
