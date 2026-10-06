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
