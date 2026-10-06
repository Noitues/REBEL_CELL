extends GutTest
## B1b (integration review D3 / D25, DECISIONS "B1b — wax pencil material and pencil audit
## (integration review)"): one wax grease-pencil material for every pencil stroke and word.
## - static: no view draws pencil as vector lines or plain text (every pencil ink or the pencil
##   face reaches the screen only through the material: GreasePencilMark / GreasePencilWord /
##   GreasePencilArt, alone or through PencilSet);
## - the look: 9 px at 1080p (8-10), the under-shadow copy at (2, 3) in #060308 at 85 %, wax at
##   0.96, the 1 px sheen at 35 %, the 20 degree loop tail, one screen width whatever the zoom;
## - motion: write-on and wipe take their entries' ~0.4 s, a mark writes itself on when it
##   shows, MotionSkip / reduce effects / headless show the end state;
## - the users: each converted view's pencil is the material, and the audit's removals.

## Files that are the material itself (they may draw the pencil's inks and face).
const MATERIAL_FILES: Array[String] = [
	"res://scripts/ui/kit/materials/grease_pencil_mark.gd",
	"res://scripts/ui/kit/materials/grease_pencil_word.gd",
	"res://scripts/ui/kit/materials/grease_pencil_art.gd",
]
## Draws that use a pencil token but are not pencil (the audit's calls), file -> why.
const NOT_PENCIL := {
	"res://scripts/ui/kit/raid_vehicle.gd": "the vehicle icon's filled heading chevron (an icon part in the plan hue)",
	"res://scripts/ui/kit/city_minimap.gd": "the minimap terminal's view box and boss dot (CRT glyphs in the inks' hues)",
	"res://tools/design_lab/kit_sheet.gd": "the lab's round 3 board: printed glass brackets and a waypoint disc in the inks' hues (its pencil is the material)",
}
const SCAN_DIRS: Array[String] = ["res://scripts", "res://tools/design_lab"]
## Tokens that are the pencil's inks or its face.
const TOKENS: Array[String] = ["PENCIL_PLAN", "PENCIL_THREAT", "PENCIL_SHADOW", "pencil_red(", "pencil_font(", "Palette.pencil("]
const TEXT_SCALE_KEEP := "text_scale"

var _reduce := false
var _scale := 1.0


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if Settings.text_scale != _scale:
		Settings.text_scale = _scale
	Fx.apply_settings()


func _effects(reduce: bool) -> void:
	if Settings.reduce_effects != reduce:
		Settings.set_reduce_effects(reduce)
	Fx.apply_settings()


func _gd_files(dir: String, out: Array[String]) -> void:
	for f in DirAccess.get_files_at(dir):
		if f.ends_with(".gd"):
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		_gd_files(dir.path_join(d), out)


# --- Static: one material ---------------------------------------------------------------------

func test_no_view_draws_pencil_ink_or_the_pencil_face_outside_the_material() -> void:
	var files: Array[String] = []
	for d in SCAN_DIRS:
		_gd_files(d, files)
	assert_gt(files.size(), 100, "the scripts were found")
	var bad: Array[String] = []
	for path in files:
		if MATERIAL_FILES.has(path) or NOT_PENCIL.has(path):
			continue
		var lines := FileAccess.get_file_as_string(path).split("\n")
		# Names (consts, locals) that hold a pencil token, file-wide (a conservative read).
		var aliases: Array[String] = []
		for line in lines:
			var m := RegEx.create_from_string("^\\s*(?:const|var)\\s+(\\w+)\\s*(?::\\s*\\w+\\s*)?:?=\\s*(.*)$").search(line)
			if m == null:
				continue
			for t in TOKENS:
				if m.get_string(2).contains(t):
					aliases.append(m.get_string(1))
		for i in lines.size():
			var line := lines[i]
			if line.strip_edges().begins_with("#") or not line.contains("draw_"):
				continue
			var hit := ""
			for t in TOKENS:
				if line.contains(t):
					hit = t
			for a in aliases:
				if RegEx.create_from_string("\\b%s\\b" % a).search(line) != null:
					hit = a
			if hit != "":
				bad.append("%s:%d (%s)" % [path, i + 1, hit])
	assert_eq(bad, [] as Array[String], "pencil drawn as vector lines or plain text: %s" % [bad])


func test_no_pencil_user_sets_its_own_stroke_width() -> void:
	var files: Array[String] = []
	for d in SCAN_DIRS:
		_gd_files(d, files)
	var bad: Array[String] = []
	var re := RegEx.create_from_string("(?i)(pencil|mark|target|_x|arrow|ring)\\w*\\.width\\s*=")
	for path in files:
		if MATERIAL_FILES.has(path):
			continue
		var lines := FileAccess.get_file_as_string(path).split("\n")
		for i in lines.size():
			if re.search(lines[i]) != null and not lines[i].strip_edges().begins_with("#"):
				bad.append("%s:%d" % [path, i + 1])
	assert_eq(bad, [] as Array[String], "the width is the material's: %s" % [bad])


# --- The look ---------------------------------------------------------------------------------

func _mark(parent: Node = null) -> GreasePencilMark:
	var m := GreasePencilMark.new()
	if parent == null:
		add_child_autofree(m)
	else:
		parent.add_child(m)
	m.add_stroke(PencilShapes.hand_circle(Vector2(100, 100), Vector2(40, 30), 3))
	return m


func test_the_stroke_is_nine_px_at_1080p_with_its_under_shadow_copy() -> void:
	Settings.text_scale = 1.0
	var m := _mark()
	var line := m.wax_lines()[0]
	var shadow := m.shadow_lines()[0]
	var at_1080 := line.width / GreasePencilMark.BOARD_TO_CANVAS
	assert_almost_eq(at_1080, 9.0, 0.01, "9 px at 1080p")
	assert_between(at_1080, GreasePencilMark.WIDTH_MIN_1080, GreasePencilMark.WIDTH_MAX_1080, "in the 8-10 range")
	assert_eq(line.begin_cap_mode, Line2D.LINE_CAP_ROUND, "round caps")
	assert_almost_eq((shadow.width - line.width) / GreasePencilMark.BOARD_TO_CANVAS, GreasePencilMark.SHADOW_GROW_1080, 0.01,
		"the shadow is a copy of the stroke, 2 px wider so it shows as a dark rim on a light street")
	assert_almost_eq(shadow.position / GreasePencilMark.BOARD_TO_CANVAS, Vector2(2, 3), Vector2(0.01, 0.01), "offset (2, 3) at 1080p")
	var smat := shadow.material as ShaderMaterial
	assert_eq(int(smat.get_shader_parameter(&"mode")), 1, "drawn as the under-shadow")
	var sc: Color = smat.get_shader_parameter(&"ink")
	assert_almost_eq(sc.a, 0.85, 0.005, "#060308 at 85 %")
	assert_eq(Color(sc, 1.0).to_html(false), "060308")
	var wmat := line.material as ShaderMaterial
	assert_eq(wmat.shader, GreasePencilMark.SHADER, "the wax shader")
	assert_almost_eq(float(wmat.get_shader_parameter(&"alpha_max")), 0.96, 0.001, "opaque wax 0.96")
	assert_almost_eq(float(wmat.get_shader_parameter(&"sheen")), 0.35, 0.001, "the sheen at 35 % white")
	assert_almost_eq(float(wmat.get_shader_parameter(&"width_px")), line.width, 0.001, "the dropouts know the width")
	assert_almost_eq(float(wmat.get_shader_parameter(&"dropout_alpha")), 0.35, 0.001, "the dropouts reach the shader")
	assert_almost_eq(float(wmat.get_shader_parameter(&"dropout_scale")), 1.0 / GreasePencilMark.BOARD_TO_CANVAS, 0.001, "in 1080p px")
	assert_eq((shadow.material as ShaderMaterial).get_shader_parameter(&"dropout_gap"), GreasePencilMark.DROPOUT_GAP,
		"the shadow thins with the wax")


func test_the_width_is_one_screen_width_whatever_the_marks_zoom_and_grows_with_the_text() -> void:
	Settings.text_scale = 1.0
	var holder := Node2D.new()
	add_child_autofree(holder)
	holder.scale = Vector2(2.5, 2.5)
	var m := _mark(holder)
	await get_tree().process_frame
	var line := m.wax_lines()[0]
	assert_almost_eq(line.width * 2.5, GreasePencilMark.stroke_width(), 0.01, "the zoom is undone on the line")
	assert_almost_eq(m.shadow_lines()[0].position * 2.5, GreasePencilMark.SHADOW_OFFSET, Vector2(0.01, 0.01), "and on the shadow")
	Settings.text_scale = 2.0
	assert_almost_eq(GreasePencilMark.stroke_width(), GreasePencilMark.WIDTH * VerbSticker.SCALE_MAX, 0.001, "scaled with the text as the stickers are")
	for s in [1.0, 1.3, 1.6, 2.0]:
		Settings.text_scale = s
		var w := GreasePencilMark.stroke_width() / GreasePencilMark.ui_scale() / GreasePencilMark.BOARD_TO_CANVAS
		assert_between(w, 8.0, 10.0, "8-10 px at 1080p before the text scale (%s)" % s)


## The dropout stretches along `length` 1080p px of a stroke: [{centre, length}].
func _dropouts(seed: int, length: float, gap: Vector2 = GreasePencilMark.DROPOUT_GAP) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var run_from := -1.0
	var d := 0.0
	while d <= length:
		var inside := GreasePencilMark.dropout_factor(seed, d, gap) >= 0.5
		if inside and run_from < 0.0:
			run_from = d
		elif not inside and run_from >= 0.0:
			out.append({"centre": (run_from + d) * 0.5, "length": d - run_from})
			run_from = -1.0
		d += 0.05
	return out


func test_wax_dropouts_every_40_to_70_px_two_to_four_px_long_to_alpha_0_35() -> void:
	for seed in [1, 3, 11, 351, 9001]:
		var drops := _dropouts(seed, 1200.0)
		assert_gt(drops.size(), 15, "seed %d: dropouts all along the stroke" % seed)
		for i in drops.size():
			assert_between(float(drops[i]["length"]), 1.9, 4.1, "seed %d: a 2-4 px stretch" % seed)
			if i > 0:
				var gap := float(drops[i]["centre"]) - float(drops[i - 1]["centre"])
				assert_between(gap, 39.9, 70.1, "seed %d: one every 40-70 px" % seed)
	# each gap drawn uniformly from the whole 40-70 range (not 55 +- 7.5): about a third in each
	# third of the range, and gaps near both ends
	var bins := [0, 0, 0]
	var gaps := 0
	var lo := 1000.0
	var hi := 0.0
	for seed in range(1, 41):
		var drops := _dropouts(seed, 2400.0)
		for i in range(1, drops.size()):
			var gap := float(drops[i]["centre"]) - float(drops[i - 1]["centre"])
			lo = minf(lo, gap)
			hi = maxf(hi, gap)
			bins[clampi(int((gap - 40.0) / 10.0), 0, 2)] += 1
			gaps += 1
	assert_lt(lo, 43.0, "short gaps near 40 px")
	assert_gt(hi, 67.0, "long gaps near 70 px")
	for b in bins:
		assert_between(float(b) / gaps, 0.25, 0.42, "uniform over the range: %s of %d gaps a third" % [b, gaps])
	assert_ne(str(_dropouts(1, 400.0)), str(_dropouts(2, 400.0)), "seeded: another seed, other places")
	assert_eq(str(_dropouts(5, 400.0)), str(_dropouts(5, 400.0)), "the same seed, the same places")
	# the depth: the shader takes the wax's alpha down to DROPOUT_ALPHA inside a stretch
	assert_almost_eq(GreasePencilMark.DROPOUT_ALPHA, 0.35, 0.001)
	var words := _dropouts(7, 1200.0, GreasePencilMark.WORD_DROPOUT_GAP)
	assert_lt(words.size(), _dropouts(7, 1200.0).size(), "words take fewer")
	var w := GreasePencilWord.new()
	add_child_autofree(w)
	var wm := w.wax_node().material as ShaderMaterial
	assert_eq(wm.get_shader_parameter(&"dropout_gap"), GreasePencilMark.WORD_DROPOUT_GAP, "words drop out too")
	assert_almost_eq(float(wm.get_shader_parameter(&"dropout_alpha")), 0.35, 0.001)


func test_a_dropout_is_a_partial_width_nibble_from_one_seeded_edge() -> void:
	var sides := {}
	var n := 0
	for seed in [1, 3, 11, 351]:
		for drop in _dropouts(seed, 1200.0):
			var b := GreasePencilMark.dropout_bite(seed, float(drop["centre"]))
			assert_between(float(b["bite"]), 0.4, 0.7, "a bite of 40-70 % of the width, never a full-width break")
			sides[int(b["side"])] = true
			n += 1
	assert_gt(n, 50)
	assert_eq(sides.size(), 2, "the seed picks either edge")
	var m := _mark()
	var wm := m.wax_lines()[0].material as ShaderMaterial
	assert_eq(wm.get_shader_parameter(&"dropout_bite"), GreasePencilMark.DROPOUT_BITE, "the shader bites that share")
	var src := FileAccess.get_file_as_string("res://shaders/kit/marker_stroke.gdshader")
	assert_true(src.contains("bite_at(dropout_hit("), "the wax thins only under the bite")


func test_the_shadow_fades_over_the_whole_gap_so_no_dark_tick_shows() -> void:
	var m := _mark()
	var sm := m.shadow_lines()[0].material as ShaderMaterial
	assert_almost_eq(float(sm.get_shader_parameter(&"dropout_alpha")), 0.35, 0.001, "the shadow fades to ~0.35 with the wax")
	assert_gte(float(sm.get_shader_parameter(&"dropout_pad")), GreasePencilMark.SHADOW_1080.length() - 0.001,
		"past the gap by its own offset, so the shifted shadow never shows under the nibble")
	var src := FileAccess.get_file_as_string("res://shaders/kit/marker_stroke.gdshader")
	assert_true(src.contains("vec4 hs = dropout_hit(along_px * dropout_scale, dropout_pad);"), "the shadow fades past the gap's ends")
	assert_true(src.contains("a = mix(a, a * dropout_alpha, bite_at(hs, across, grain));"), "under the bite only")
	assert_true(src.contains("uniform float dropout_shadow_max = 0.75;"), "never across the far edge: the rim there runs on (never dashed)")


func test_dropouts_are_spaced_in_screen_px_on_a_curved_zoomed_stroke() -> void:
	Settings.text_scale = 1.0
	var holder := Node2D.new()
	add_child_autofree(holder)
	holder.scale = Vector2(2.5, 2.5)
	var m := GreasePencilMark.new()
	m.auto_write = false
	holder.add_child(m)
	m.add_stroke(PencilShapes.bezier(Vector2(0, 0), Vector2(120, -90), Vector2(260, 40), 40))
	await get_tree().process_frame
	m.progress = 0.6
	var line := m.wax_lines()[0]
	var mat := line.material as ShaderMaterial
	assert_eq(line.texture_mode, Line2D.LINE_TEXTURE_STRETCH, "UV.x runs over the drawn part, not in widths")
	var span := float(mat.get_shader_parameter(&"seg_to_px")) - float(mat.get_shader_parameter(&"seg_from_px"))
	assert_almost_eq(span, PencilShapes.length_of(line.points), 0.5, "the part's span is its arc length (local px)")
	var screen_1080 := span * float(mat.get_shader_parameter(&"dropout_scale"))
	assert_almost_eq(screen_1080, PencilShapes.length_of(line.points) * 2.5 / GreasePencilMark.BOARD_TO_CANVAS, 0.5,
		"the dropouts are placed along its screen length in 1080p px (40-70 apart)")
	assert_ne(m.wax_lines()[0].material, m.shadow_lines()[0].material, "each line has its own span")


func test_the_shader_hash_is_the_scripts_hash() -> void:
	var src := FileAccess.get_file_as_string("res://shaders/kit/marker_stroke.gdshader")
	for token in ["374761393u", "668265263u", "1274126177u", ">> 13u", ">> 16u", "65535u", "dhash(p, s + 4)", "dhash(0, s + 5)",
			"dhash(kk, s + 1)", "dhash(kk, s + 2)", "dhash(kk, s + 3)"]:
		assert_true(src.contains(token), "the shader's dhash has %s (GreasePencilMark.dhash's constants)" % token)
	var gd := FileAccess.get_file_as_string("res://scripts/ui/kit/materials/grease_pencil_mark.gd")
	for token in ["374761393", "668265263", "1274126177", ">> 13", ">> 16", "0xFFFF", "dhash(p, sd + 4)", "dhash(0, sd + 5)",
			"dhash(kk, sd + 1)", "dhash(kk, sd + 2)", "dhash(kk, sd + 3)"]:
		assert_true(gd.contains(token), "the script's dhash has %s" % token)


func test_a_hash_seed_reaches_the_shader_folded_so_the_wax_keeps_its_grain() -> void:
	var m := _mark()
	m.seed = absi(hash("route_target_node"))
	var s := float((m.wax_lines()[0].material as ShaderMaterial).get_shader_parameter(&"seed"))
	assert_between(s, 0.0, float(GreasePencilMark.SEED_FOLD - 1), "a big hash seed folds into the shader's range")
	assert_eq(s, GreasePencilMark.shader_seed(m.seed), "the same fold for the shadow and the wax")


func test_a_loops_radius_jitter_is_seeded_and_about_three_percent() -> void:
	var lo := 1.0
	var hi := -1.0
	for seed in [1, 5, 7, 351, 352, 9001]:
		for i in 400:
			var j := PencilShapes.jitter(seed, i / 360.0)
			lo = minf(lo, j)
			hi = maxf(hi, j)
	assert_gte(lo, -PencilShapes.JITTER - 0.0001, "never more than 3 % in")
	assert_lte(hi, PencilShapes.JITTER + 0.0001, "never more than 3 % out")
	assert_gt(hi - lo, PencilShapes.JITTER, "it does wobble (not a perfect circle)")
	assert_eq(PencilShapes.hand_circle(Vector2.ZERO, Vector2(40, 30), 7), PencilShapes.hand_circle(Vector2.ZERO, Vector2(40, 30), 7),
		"the same seed draws the same loop")
	assert_ne(PencilShapes.hand_circle(Vector2.ZERO, Vector2(40, 30), 7), PencilShapes.hand_circle(Vector2.ZERO, Vector2(40, 30), 8),
		"another seed another loop")


func test_the_loops_start_and_end_never_meet_cleanly() -> void:
	var r := 50.0
	var loops := {
		"plain": PencilShapes.hand_circle(Vector2.ZERO, Vector2(r, r), 9),
		"aim": AimLinePencil.shapes({"from": Vector2(0, 300), "to": Vector2.ZERO, "loop": {"key": "w", "center": Vector2.ZERO, "radius": r}})["loop"][0],
		"route TARGET": RouteOverlay.target_loop(Vector2.ZERO, r, 351)[0],
	}
	for k: String in loops:
		var pts: PackedVector2Array = loops[k]
		var a := pts[0]
		var b := pts[pts.size() - 1]
		assert_gt(a.distance_to(b), r * 0.08, "%s: the tail ends well clear of where the pen landed" % k)
		assert_gt(b.length(), a.length() * 1.06, "%s: the tail runs out past the start, the start sits inside" % k)
		# 20 degrees past the start, the line runs outside its own start (an overrun, not a join)
		var start_ang := a.angle()
		var end_ang := b.angle()
		assert_almost_eq(rad_to_deg(absf(wrapf(end_ang - start_ang, -PI, PI))), 20.0, 3.0, "%s: a 20 degree tail" % k)


func test_a_hand_loop_is_one_ellipse_with_a_twenty_degree_tail() -> void:
	assert_almost_eq(PencilShapes.LOOP_TURNS, 1.0 + 20.0 / 360.0, 0.0001)
	var pts := PencilShapes.hand_circle(Vector2.ZERO, Vector2(50, 50), 9)
	var turned := 0.0
	for i in range(1, pts.size()):
		turned += absf(wrapf(pts[i].angle() - pts[i - 1].angle(), -PI, PI))
	assert_almost_eq(rad_to_deg(turned), 380.0, 4.0, "one turn and its 20 degree tail")


func test_a_word_is_the_wax_text_over_its_shadow_copy() -> void:
	var w := GreasePencilWord.new()
	add_child_autofree(w)
	assert_eq((w.wax_node().material as ShaderMaterial).shader, GreasePencilMark.SHADER, "the wax shader")
	assert_eq(int((w.wax_node().material as ShaderMaterial).get_shader_parameter(&"mode")), 2, "text mode")
	assert_eq(w.shadow_node().position, GreasePencilMark.SHADOW_OFFSET, "the shared under-shadow offset")
	assert_true(w.is_in_group(GreasePencilMark.GROUP))


# --- Motion -----------------------------------------------------------------------------------

func test_the_write_on_and_the_wipe_take_about_point_four_seconds_from_their_entries() -> void:
	for id: StringName in [&"pencil_write_on", &"pencil_wipe", &"aim_line_draw", &"raid_route_write", &"raid_route_wipe",
			&"raid_drag_arrow", &"raid_dock_circle", &"raid_mark_write", &"raid_mark_wipe"]:
		assert_between(Motion.entry(id).duration, 0.35, 0.45, "%s: ~0.4 s" % id)
	Motion.force_live = true
	_effects(false)
	var m := _mark()
	assert_almost_eq(m.write_on(), Motion.seconds(GreasePencilMark.WRITE), 0.001, "the write takes its entry's duration")
	m.complete_motion()
	assert_almost_eq(m.wipe(), Motion.seconds(GreasePencilMark.WIPE), 0.001, "the wipe takes its entry's duration")
	m.complete_motion()
	var w := GreasePencilWord.new()
	add_child_autofree(w)
	w.complete_motion()
	assert_almost_eq(w.write_on(), Motion.seconds(GreasePencilWord.WRITE), 0.001, "a word too")
	w.complete_motion()


func test_a_mark_writes_itself_on_when_it_shows_never_whole_and_skip_shows_the_end() -> void:
	Motion.force_live = true
	_effects(false)
	var m := _mark()
	assert_almost_eq(m.progress, 0.0, 0.001, "not whole when it appears")
	await BoundedWait.until(get_tree(), func() -> bool: return m.motion_running() or m.progress >= 1.0, 2.0)
	assert_true(m.motion_running(), "it writes on by itself")
	assert_eq(m.modulate.a, 1.0, "never an alpha fade")
	m.complete_motion()
	assert_almost_eq(m.progress, 1.0, 0.001, "skip: written whole")
	m.visible = false
	m.visible = true
	assert_almost_eq(m.progress, 0.0, 0.001, "shown again: it writes on again")
	m.complete_motion()
	assert_almost_eq(m.progress, 1.0, 0.001)


func test_reduce_effects_and_headless_show_every_pencil_whole_at_once() -> void:
	var m := _mark()
	assert_almost_eq(m.progress, 1.0, 0.001, "headless: whole")
	Motion.force_live = true
	_effects(true)
	var m2 := _mark()
	assert_almost_eq(m2.progress, 1.0, 0.001, "reduce effects: whole from the start")
	assert_false(m2.motion_running(), "nothing to write on")
	var w := GreasePencilWord.new()
	w.text = "TARGET"
	add_child_autofree(w)
	# The auto write runs on its first shown frame and ends at once (no motion).
	await BoundedWait.until(get_tree(), func() -> bool: return w.shown_to == float(w.text.length()), 1.0)
	assert_eq(w.shown_to, float(w.text.length()), "a word whole")
	assert_false(w.motion_running(), "with no motion")
	var art := GreasePencilArt.new(PlaceholderTexture2D.new(), Vector2(40, 20))
	add_child_autofree(art)
	assert_almost_eq(art.progress, 1.0, 0.001, "baked art whole")
	assert_false(art.motion_running(), "with no motion")
	assert_eq(m2.wipe(), 0.0, "and wiped at once")


func test_a_pencil_set_wipes_a_mark_it_no_longer_lays() -> void:
	Motion.force_live = true
	_effects(false)
	var s := PencilSet.new()
	add_child_autofree(s)
	s.begin()
	var m := s.circle("a", Vector2(50, 50), Vector2(20, 14), GreasePencilMark.Ink.PLAN)
	s.end()
	m.complete_motion()
	s.begin()
	s.end()
	assert_true(is_instance_valid(m) and m.motion_running(), "the cloth wipe runs (never a pop or a fade)")
	m.complete_motion()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_false(is_instance_valid(m), "freed once wiped")


# --- The users --------------------------------------------------------------------------------

func _pencil_nodes(root: Node) -> Array[Node]:
	var out: Array[Node] = []
	for n in get_tree().get_nodes_in_group(GreasePencilMark.GROUP):
		if root == n or root.is_ancestor_of(n):
			out.append(n)
	return out


func test_every_pencil_node_in_the_group_is_the_material() -> void:
	var notes := PencilWords.new("No Going Back", -3.0)
	notes.color = Palette.PENCIL_THREAT
	add_child_autofree(notes)
	var crown := PencilWords.new("NEVER SLEEP", 0.0, true)
	add_child_autofree(crown)
	var motto := PencilWords.new("", 0.0, false, PencilWords.MOTTO_ART)
	add_child_autofree(motto)
	var plan := PencilPlan.new()
	add_child_autofree(plan)
	var note := PencilNote.new("BIN IT", Palette.PENCIL_PLAN)
	add_child_autofree(note)
	note.with_arrow(Vector2(0, 10), Vector2(60, 10))
	var polaroid := Polaroid.new()
	polaroid.kia = true
	polaroid.size = Vector2(120, 150)
	add_child_autofree(polaroid)
	polaroid.queue_redraw()
	await get_tree().process_frame
	await get_tree().process_frame
	for root: Node in [notes, crown, motto, plan, note, polaroid]:
		var found := _pencil_nodes(root)
		assert_false(found.is_empty(), "%s shows its pencil" % root.name)
		for n in found:
			assert_true(n is GreasePencilMark or n is GreasePencilWord or n is GreasePencilArt, "%s: the material (%s)" % [root.name, n])
	assert_eq((notes.pencil_nodes()[0] as GreasePencilWord).ink, GreasePencilMark.Ink.THREAT, "red ink")
	assert_true(plan.art() is GreasePencilArt, "the title's plan writes on through the material")
	assert_eq(int((plan.art().material as ShaderMaterial).get_shader_parameter(&"mode")), 3, "the baked-art mode")


func test_the_backdrops_ours_now_is_a_wax_word_shown_only_once_won() -> void:
	var b := CombatBackdrop.new()
	add_child_autofree(b)
	b.show_place(BackdropCatalog.place_for(null, [] as Array[EnemyData], &""))
	assert_false(b.ours_now().visible, "not won: no pencil")
	b.play_won(true)
	assert_true(b.ours_now().visible, "won: OURS NOW in pencil")
	assert_eq(b.ours_now().ink, GreasePencilMark.Ink.PLAN, "yellow: our plan")
	assert_eq(b.ours_now().modulate.a, 1.0, "never faded in")


func test_the_audit_removed_the_new_campaign_motto() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/hq_scene.gd")
	assert_false(src.contains("PencilWords.new(tr(\"TRUST NO ONE\")"), "TRUST NO ONE is gone (a joke in pencil)")
	var mark := FileAccess.get_file_as_string("res://scripts/ui/kit/raid_route_mark.gd")
	assert_true(mark.contains("Palette.HARM"), "the intel row's route ring is the concept's HARM ring, not pencil")
