extends GutTest
## LOOK-TOOLBOX module 12 (grease pencil polish; addons/rc_look/AUDIT.md "Grease pencil: fail", DECISIONS "LOOK-TOOLBOX
## 12"): the wax face and word path, pressure and the hero width, the hand geometry, the netrun plan's orange, no
## pencil spill (the halo), hand marks on the engine, and the world-anchor API.

const LOOK: RcPencilLook = preload("res://addons/rc_look/config/pencil_look.tres")

var _scale := 1.0


func before_each() -> void:
	_scale = Settings.text_scale
	Settings.text_scale = 1.0


func after_each() -> void:
	Settings.text_scale = _scale


# --- The face and the one word path ------------------------------------------------------------

func test_the_pencil_face_is_rc_wax_and_its_strokes_measure_as_the_face() -> void:
	assert_eq(Palette.FONT_PENCIL, "res://assets/fonts/RcWax-Regular.ttf")
	var font := Palette.pencil()
	for px in [20, 30, 44]:
		for word in ["TARGET", "HIT IT", "Down with the Oligarchy!", "+1 = 12"]:
			var lay := RcWaxFont.layout(word, float(px), 7, LOOK)
			assert_almost_eq(float(lay["width"]), font.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, 1.0,
				"%s at %d: the stroke twin advances as the TrueType face measures" % [word, px])
	for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!?.,'-:/+%()":
		assert_true(RcWaxFont.has_char(c), "RC Wax draws %s" % c)


func test_the_faces_wax_width_is_the_words_wax_width() -> void:
	var f := FileAccess.open(RcWaxFont.STROKES_PATH, FileAccess.READ)
	var data: Dictionary = JSON.parse_string(f.get_as_text())
	assert_almost_eq(float(data["width"]) / float(data["upm"]), LOOK.word_width_em, 0.0001,
		"the outline's width (build_wax_font.py WIDTH) and the stroke word's width agree")


func test_a_word_has_a_seeded_hand_and_writes_on_letter_by_letter() -> void:
	var a := RcWaxFont.layout("TARGET", 30.0, 5, LOOK)
	var b := RcWaxFont.layout("TARGET", 30.0, 5, LOOK)
	var c := RcWaxFont.layout("TARGET", 30.0, 6, LOOK)
	assert_eq(str(a["strokes"]), str(b["strokes"]), "the same seed, the same hand")
	assert_ne(str(a["strokes"]), str(c["strokes"]), "another seed, another hand")
	var w := GreasePencilWord.new()
	w.auto_write = false
	w.text = "TARGET"
	add_child_autofree(w)
	w.shown_to = 0.0
	assert_almost_eq(w.wax_mark().progress, 0.0, 0.0001, "nothing written")
	w.shown_to = 1.0
	var one := w.wax_mark().progress
	assert_between(one, 0.05, 0.3, "the T alone")
	w.shown_to = 6.0
	assert_almost_eq(w.wax_mark().progress, 1.0, 0.0001, "the whole word")
	w.shown_from = 1.0
	assert_almost_eq(w.wax_mark().wiped_share, one, 0.0001, "the wipe takes letters from the first")
	var r := w.global_rect()
	for s in w.wax_mark().strokes():
		for p in s:
			assert_true(r.grow(0.5).has_point(w.get_global_transform() * p), "the rect no UI may cover holds every stroke")


func test_every_view_word_is_the_one_word_class() -> void:
	# PencilSet.word, PencilWords and PencilNote all make GreasePencilWord; nothing else draws the face as text
	for path in ["res://scripts/ui/kit/pencil_set.gd", "res://scripts/ui/kit/chrome/pencil_words.gd", "res://scripts/ui/kit/pencil_note.gd"]:
		var src := FileAccess.get_file_as_string(path)
		assert_true(src.contains("GreasePencilWord.new()"), "%s lays a GreasePencilWord" % path)
		assert_false(src.contains("draw_string(") and src.contains("pencil()"), "%s draws no pencil text itself" % path)


# --- Pressure and width -----------------------------------------------------------------------

func test_pressure_lands_light_swells_and_lifts_off_thin() -> void:
	var p := LOOK.mark_pressure
	var w := 10.0
	var length := 400.0
	assert_almost_eq(p.factor(0.0, length, w, 3), p.land_width, 0.2, "the pen lands light")
	assert_lt(p.factor(length, length, w, 3), 0.5, "it lifts off in a thin flick")
	var lo := 9.0
	var hi := 0.0
	for d in range(60, 300, 4):
		var f := p.factor(float(d), length, w, 3)
		lo = minf(lo, f)
		hi = maxf(hi, f)
	assert_gt(hi - lo, p.swell * 0.5, "it swells along the stroke (never one even width)")
	assert_between(lo, 1.0 - p.swell - 0.01, 1.0 + p.swell + 0.01)
	assert_eq(p.factor(120.0, length, w, 3), p.factor(120.0, length, w, 3), "seeded: no RNG")
	var flick := p.factor(15.0, 30.0, w, 3)
	assert_gt(flick, 0.75, "a short flick (an arrow head) stays pressed")


func test_hero_marks_are_14_to_18_px_and_the_pressure_never_slides_while_writing() -> void:
	assert_between(LOOK.hero_width_1080, 14.0, 18.0, "AUDIT pencil 2: hero marks 14-18 px at 1080p")
	var m := GreasePencilMark.new()
	m.auto_write = false
	m.hero = true
	add_child_autofree(m)
	m.add_stroke(PackedVector2Array([Vector2(0, 0), Vector2(300, 0)]))
	assert_almost_eq(m.wax_lines()[0].width, GreasePencilMark.stroke_width(true), 0.001)
	m.progress = 1.0
	var full := m.wax_lines()[0].width_curve.sample(0.5)
	m.progress = 0.5
	var half := m.wax_lines()[0].width_curve.sample(1.0)
	assert_almost_eq(half, full, 0.08, "the width at a point is the same written half or whole (sampled at its own distance)")


# --- The hand ----------------------------------------------------------------------------------

func test_an_underline_overshoots_and_ends_in_a_hooked_downstroke() -> void:
	var w := GreasePencilMark.stroke_width()
	var a := Vector2(100, 200)
	var b := Vector2(400, 200)
	var pts := PencilShapes.hand_line(a, b, 17, w)
	var min_x := INF
	var max_x := -INF
	for p in pts:
		min_x = minf(min_x, p.x)
		max_x = maxf(max_x, p.x)
	assert_lt(min_x, a.x, "it starts before the chip")
	assert_gt(max_x, b.x + w * LOOK.line_overshoot_min * 0.9, "it runs past the end")
	var tip := pts[pts.size() - 1]
	assert_gt(tip.y, b.y + w, "the hook turns down")
	assert_lt(tip.x, max_x, "and back")
	assert_eq(PencilShapes.hand_line(a, b, 17, w), PencilShapes.hand_line(a, b, 17, w), "seeded: no RNG")
	assert_ne(PencilShapes.hand_line(a, b, 17, w), PencilShapes.hand_line(a, b, 18, w))


func test_a_hand_path_wobbles_but_keeps_its_ends_and_a_route_rounds_its_corners() -> void:
	var w := GreasePencilMark.stroke_width()
	var straight := PackedVector2Array([Vector2(0, 0), Vector2(400, 0)])
	var hp := PencilShapes.hand_path(straight, 3, w)
	var off := 0.0
	for p in hp:
		off = maxf(off, absf(p.y))
	assert_gt(off, w * 0.05, "not ruler straight")
	assert_lte(off, w * LOOK.path_wobble + 0.01, "within the look's wobble")
	assert_almost_eq(hp[0], straight[0], Vector2(0.01, 0.01), "the pen lands where it means to")
	assert_almost_eq(hp[hp.size() - 1], straight[1], Vector2(0.01, 0.01), "the tip hits")
	var corner := Vector2(200, 0)
	var route := PencilShapes.hand_route(PackedVector2Array([Vector2(0, 0), corner, Vector2(200, 200)]), 5, w)
	var nearest := INF
	for p in route:
		nearest = minf(nearest, p.distance_to(corner))
	assert_gt(nearest, w * 0.3, "no polyline corner: it rounds")
	assert_lt(nearest, w * LOOK.corner_radius, "but stays on the street")


func test_a_hand_loop_is_an_egg_tilted_by_its_seed() -> void:
	var a := PencilShapes.hand_circle(Vector2.ZERO, Vector2(50, 50), 1)
	var radii := PackedFloat32Array()
	for i in PencilShapes.CIRCLE_POINTS:
		radii.append(a[i].length())
	var lo := INF
	var hi := 0.0
	for r in radii:
		lo = minf(lo, r)
		hi = maxf(hi, r)
	assert_gt((hi - lo) / 50.0, LOOK.loop_egg, "not a perfect ellipse")


# --- Inks, the halo, the hand marks ------------------------------------------------------------

func test_the_netrun_plan_is_orange_and_every_other_plan_yellow() -> void:
	assert_eq(GreasePencilMark.ink_color(GreasePencilMark.Ink.PLAN_NETRUN), Palette.PENCIL_PLAN_NETRUN, "art-pass ruling d")
	assert_eq(GreasePencilMark.ink_color(GreasePencilMark.Ink.PLAN), Palette.PENCIL_PLAN)
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/hq_plan_pencil.gd")
	assert_true(src.contains("Ink.PLAN_NETRUN"), "the HQ page's plan pencil (the netrun plan) takes the orange")
	assert_false(src.contains("Ink.PLAN,"), "and not the yellow")


func test_no_pencil_lights_the_world_under_it() -> void:
	# AUDIT pencil 4: the soft halo round yellow and red strokes was UiSpillShadows' pencil spill; wax never glows
	var files: Array[String] = []
	_gd_files("res://scripts", files)
	var bad: Array[String] = []
	for path in files:
		var src := FileAccess.get_file_as_string(path)
		for line in src.split("\n"):
			if line.contains("add_spill_source") and line.contains("PENCIL_"):
				bad.append(path)
			if line.contains("mark_spill(") and line.contains("PENCIL_"):
				bad.append(path)
	assert_eq(bad, [] as Array[String], "no pencil spill source: %s" % [bad])


func test_hand_marks_are_wax_on_the_engine() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/hand_marks.gd")
	assert_false(src.contains("draw_"), "HandMarks draws nothing itself")
	assert_eq(HandMarks.x_strokes(Rect2(0, 0, 80, 110), 3).size(), 2, "an X is two strokes")
	var card := Control.new()
	card.size = Vector2(80, 110)
	add_child_autofree(card)
	HandMarks.show_x(card, Rect2(Vector2.ZERO, card.size), 3)
	await get_tree().process_frame
	var set: PencilSet = card.get_meta(PencilSet.META)
	assert_not_null(set)
	var m := set.mark("one")
	assert_not_null(m, "the X is a GreasePencilMark")
	assert_eq(m.ink, GreasePencilMark.Ink.THREAT, "a remove is red")


# --- The world anchor ------------------------------------------------------------------------

func test_a_world_point_projects_through_a_camera_and_hides_behind_it() -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(640, 360)
	vp.own_world_3d = true
	add_child_autofree(vp)
	var cam := Camera3D.new()
	vp.add_child(cam)
	cam.look_at_from_position(Vector3(0, 0, 5), Vector3.ZERO)
	var front := RcPencilAnchor.screen_point(cam, Vector3.ZERO)
	assert_almost_eq(front, Vector2(320, 180), Vector2(1, 1), "the look-at point is the screen centre")
	assert_eq(RcPencilAnchor.screen_point(cam, Vector3(0, 0, 10)), Vector2.INF, "behind the camera: INF")
	var runs := RcPencilAnchor.screen_path(cam, PackedVector3Array([Vector3(-1, 0, 0), Vector3(1, 0, 0), Vector3(0, 0, 9),
		Vector3(0, 1, 0), Vector3(0, 2, 0)]))
	assert_eq(runs.size(), 2, "a point behind breaks the path into its visible runs")
	assert_gt(RcPencilAnchor.px_per_unit(cam, Vector3.ZERO), 10.0)
	var proj := func(p: Vector3) -> Vector2: return Vector2.INF if p.z > 1.0 else Vector2(p.x, p.y) * 10.0
	var pin := RcPencilWorldAnchor.new(proj, Vector3(3, 4, 0))
	add_child_autofree(pin)
	pin.follow()
	assert_true(pin.visible)
	assert_almost_eq(pin.position, Vector2(30, 40), Vector2(0.01, 0.01), "a Callable projector (a view's own projection)")
	pin.world = Vector3(0, 0, 3)
	pin.follow()
	assert_false(pin.visible, "hidden while its point is behind")


func _gd_files(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_gd_files(dir.path_join(d), out)


# --- The TARGET word stays in frame (LOOK-TOOLBOX 12 review, grid_target) ------------------------

func test_the_target_word_stays_inside_the_frame_for_rings_near_every_edge() -> void:
	var area := Rect2(0, 0, 1920, 1080)
	var unit := CityMapOverlay.TARGET_RADIUS
	var half := Vector2(unit, unit * CityMapOverlay.TARGET_FLAT)
	var box := Rect2(0, -40, 150, 52)
	var blocks: Array[Rect2] = []
	var spots: Array[Vector2] = [Vector2(20, 540), Vector2(1900, 540), Vector2(960, 15), Vector2(960, 1065),
		Vector2(25, 20), Vector2(1895, 20), Vector2(25, 1060), Vector2(1895, 1060), Vector2(960, 540)]
	for at in spots:
		var circle := Rect2(at - half, half * 2.0)
		var avoid: Array[Rect2] = [circle]
		var tries := CityMapOverlay.target_word_tries(at, unit, circle, box.size.x)
		var p := CityMapOverlay.pick_word_spot(tries, box, area, blocks, avoid, true)
		var w := Rect2(p + box.position, box.size)
		assert_true(area.encloses(w), "a ring at %s keeps its word %s inside the frame" % [at, w])


# --- Review: HUD words, broken hero wax, fat hero words ------------------------------------------

func test_the_aim_shaft_never_crosses_a_hud_word() -> void:
	var hud: Array[Rect2] = [Rect2(180, 560, 260, 40), Rect2(450, 560, 520, 40)]
	for to in [Vector2(900, 200), Vector2(1500, 300), Vector2(300, 150)]:
		var aim := {"from": Vector2(390, 640), "to": to, "stop": 0.0, "loop": {}, "avoid": hud}
		var arrow: Array[PackedVector2Array] = AimLinePencil.shapes(aim)["arrow"]
		assert_false(arrow.is_empty(), "an arrow is drawn to %s" % to)
		var pad := GreasePencilMark.stroke_width(true) * 0.5
		var grown: Array[Rect2] = []
		for r in hud:
			grown.append(r.grow(pad))
		assert_eq(AimLinePencil.crossing(arrow[0], grown), 0.0, "the shaft to %s clears the HUD words" % to)
		assert_lt(arrow[0][arrow[0].size() - 1].distance_to(to), GreasePencilMark.stroke_width(true) * 2.0,
			"the shaft still ends at its target")


func test_a_hero_stroke_lifts_into_pressure_gaps_and_its_wax_is_dry() -> void:
	var p := LOOK.hero_pressure
	var w := 16.0
	var length := 1500.0
	var lo := INF
	var gaps := 0
	var was_in := false
	for i in int(length):
		var f := p.factor(float(i), length, w, 5)
		lo = minf(lo, f) if float(i) > p.land_len * w and float(i) < length - p.lift_len * w else lo
		var inside := p.gap_at(float(i), length, w, 5) > 0.9
		if inside and not was_in:
			gaps += 1
		was_in = inside
	assert_lt(lo, 0.3, "the pen nearly lifts in a pressure gap")
	assert_between(gaps, 2, 6, "a ring has a few pressure gaps, not a dashed line")
	var m := GreasePencilMark.new()
	m.hero = true
	m.add_stroke(PackedVector2Array([Vector2.ZERO, Vector2(length, 0)]))
	add_child_autofree(m)
	var mat := m.wax_lines()[0].material as ShaderMaterial
	assert_gt(float(mat.get_shader_parameter("edge_grain")), 0.0, "hero wax has dry edges")
	assert_gt(float(mat.get_shader_parameter("core_break")), 0.0, "hero wax breaks in its core")


func test_a_hero_word_is_fatter_with_a_lighter_core() -> void:
	var plain := GreasePencilWord.new()
	var hero := GreasePencilWord.new()
	hero.hero = true
	add_child_autofree(plain)
	add_child_autofree(hero)
	assert_gt(hero.wax_mark().local_width, plain.wax_mark().local_width * 1.2, "a hero word's wax is fatter")
	assert_gt(hero.wax_mark().core_light, 0.0, "a hero word has a lighter core")
	assert_eq(plain.wax_mark().core_light, 0.0, "a plain word has none")
