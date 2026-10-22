extends RcLookLabStage
## LOOK-TOOLBOX module 13 in the lab: the vinyl sticker look. Rows, top to bottom:
##   1 the seven kit stocks at rest (rc_vinyl_kit);
##   2 pink kit poses on the rc_vinyl_kit wrapper (rest, hover peel, fold, band, dissolve, disabled, slap);
##   3 the same poses on the OLD shaders/kit/vinyl_sticker.gdshader (must look the same);
##   4 chrome verbs on rc_vinyl_chrome (pink, yellow, blue, grey, glitch, glitch burst, sweep);
##   5 the same on the OLD shaders/chrome/vinyl_sticker.gdshader;
##   6 holo foil fill, card stand-in (scan front, gloss) as wrapper | old, and the GDScript mirror of the kit shader
##     (rim, gloss, flap, band, grey; no shadow) beside the shader.
## With the user arg --prove every pair is also rendered into a SubViewport and compared pixel for pixel: the lab prints
## "vinyl_prove: <case> max <n>" (0 = identical) and "vinyl_prove: total ..."; with --prove-only the lab then quits.
## Reduce effects (the quality state) sets the global reduce_effects: the old white sweep, the holo drift and the card
## gloss go still. Day / night changes nothing here (stickers are UI). View only.

const KIT_OLD := "res://shaders/kit/vinyl_sticker.gdshader"
const CHROME_OLD := "res://shaders/chrome/vinyl_sticker.gdshader"
const FILL_OLD := "res://shaders/kit/sticker_fill.gdshader"
const CARD_OLD := "res://shaders/fx/card_sticker_fx.gdshader"
const STOCKS: Array[StringName] = [&"kit_pink", &"kit_red", &"kit_yellow", &"kit_white", &"kit_ink", &"kit_kraft", &"kit_holo"]
const POSES: Array[StringName] = [&"rest", &"hover", &"fold", &"band", &"dissolve", &"disabled", &"slap"]
const VERBS: Array[StringName] = [&"chrome_pink", &"chrome_yellow", &"chrome_blue", &"chrome_grey", &"chrome_glitch"]
## Layout (canvas px): the art is shown at CELL_SCALE, rows start at ROW_Y with ROW_H between them.
const CELL_SCALE := 0.45
const MARGIN := Vector2(12.0, 22.0)
const ROW_H := 112.0
const LABEL_PX := 11
const LABEL_COLOR := Color(0.85, 0.88, 0.95)
## The chrome word: its fill gradient runs over the glyph box (px in the word control), a burst has this many bands.
const FILL_TOP := 14.0
const FILL_BOTTOM := 54.0
const BURST_BANDS := 5
const BURST_SHIFT := 6.0
const WORD_SIZE := Vector2(300.0, 70.0)
## The chrome sweep frozen mid-crossing (local x + y) and the card's frozen scan and gloss.
const SWEEP_AT := 96.0
const CARD_SIZE := Vector2(112.0, 148.0)
const CARD_SCAN := 0.5
const CARD_GLOSS := 0.5
const HOLO_SEED := 11
const HOLO_FIELD := Vector2(260.0, 96.0)
const HOLO_TIME_NOTE := "holo hue drifts with rc_time(TIME): both shaders read the same frame"
## Pixel-compare viewport padding and frames to wait before reading it back.
const PROVE_FRAMES := 3
const BYTE := 255.0

var _stage_args: PackedStringArray = OS.get_cmdline_user_args()
var _arts: Dictionary = {}
var _proved := false


func _ready() -> void:
	for id in STOCKS:
		_arts[id] = RcLookVinyl.lab_art(id)
	var y := MARGIN.y
	_label("kit stocks at rest (rc_vinyl_kit)", Vector2(MARGIN.x, y - LABEL_PX - 4.0))
	for i in STOCKS.size():
		add_child(_kit_cell(STOCKS[i], &"rest", false, Vector2(MARGIN.x + i * _cell_w(), y)))
	y += ROW_H
	_label("pink poses: rest, hover peel, fold, band, dissolve, disabled, slap shine (rc_vinyl_kit)", Vector2(MARGIN.x, y - LABEL_PX - 4.0))
	for i in POSES.size():
		add_child(_kit_cell(&"kit_pink", POSES[i], false, Vector2(MARGIN.x + i * _cell_w(), y)))
	y += ROW_H
	_label("same, OLD shaders/kit/vinyl_sticker.gdshader", Vector2(MARGIN.x, y - LABEL_PX - 4.0))
	for i in POSES.size():
		add_child(_kit_cell(&"kit_pink", POSES[i], true, Vector2(MARGIN.x + i * _cell_w(), y)))
	y += ROW_H
	_label("chrome verbs: pink, yellow, blue, grey, glitch, glitch burst, sweep (rc_vinyl_chrome)", Vector2(MARGIN.x, y - LABEL_PX - 4.0))
	var cases := _chrome_cases()
	for i in cases.size():
		add_child(_chrome_cell(cases[i], false, Vector2(MARGIN.x + i * (WORD_SIZE.x * 0.6 + 8.0), y)))
	y += ROW_H * 0.6
	_label("same, OLD shaders/chrome/vinyl_sticker.gdshader", Vector2(MARGIN.x, y - LABEL_PX - 4.0))
	for i in cases.size():
		add_child(_chrome_cell(cases[i], true, Vector2(MARGIN.x + i * (WORD_SIZE.x * 0.6 + 8.0), y)))
	y += ROW_H * 0.6 + LABEL_PX
	_label("holo fill | old, card scan + gloss | old, GDScript mirror | shader (no shadow)", Vector2(MARGIN.x, y - LABEL_PX - 4.0))
	var x := MARGIN.x
	for old in [false, true]:
		add_child(_holo_cell(old, Vector2(x, y)))
		x += HOLO_FIELD.x * CELL_SCALE + 8.0
	for old in [false, true]:
		add_child(_card_cell(old, Vector2(x, y)))
		x += CARD_SIZE.x * 0.7 + 8.0
	var mirror := _mirror_cell(&"kit_pink", &"hover", true, Vector2(x, y))
	add_child(mirror)
	x += _cell_w()
	add_child(_kit_cell(&"kit_pink", &"hover", false, Vector2(x, y), 0.0))
	x += _cell_w()
	var mirror2 := _mirror_cell(&"kit_kraft", &"band", true, Vector2(x, y))
	add_child(mirror2)
	x += _cell_w()
	add_child(_kit_cell(&"kit_kraft", &"band", false, Vector2(x, y), 0.0))


func apply(_time: StringName, quality: RcLookQualityState) -> void:
	RenderingServer.global_shader_parameter_set(&"reduce_effects", 1.0 if quality.reduce_effects else 0.0)
	if _stage_args.has("--prove") and not _proved:
		_proved = true
		_prove.call_deferred()


func settle_frames() -> int:
	return 8


func _cell_w() -> float:
	return (RcLookVinyl.config().lab_body.x + RcLookVinyl.config().lab_pad * 2.0) * CELL_SCALE + 4.0


func _label(text: String, at: Vector2) -> void:
	var l := Label.new()
	l.text = text
	l.position = at
	l.add_theme_font_size_override(&"font_size", LABEL_PX)
	l.add_theme_color_override(&"font_color", LABEL_COLOR)
	add_child(l)


# ---- cells ------------------------------------------------------------------------------------------------------

## A kit sticker: the stand-in art on a white blank of the same size with the kit material (old = the old shader).
func _kit_cell(id: StringName, pose: StringName, old: bool, at: Vector2, shadow_k: float = 1.0) -> Control:
	var art: Dictionary = _arts.get(id, RcLookVinyl.lab_art(id))
	var node := _kit_node(id, pose, old, art, shadow_k)
	node.position = at
	node.scale = Vector2(CELL_SCALE, CELL_SCALE)
	return node


func _kit_node(id: StringName, pose: StringName, old: bool, art: Dictionary, shadow_k: float) -> TextureRect:
	var img: Image = art["image"]
	var tex := ImageTexture.create_from_image(img)
	var blank := Image.create(img.get_width(), img.get_height(), false, Image.FORMAT_RGBA8)
	blank.fill(Color.WHITE)
	var node := TextureRect.new()
	node.texture = ImageTexture.create_from_image(blank)
	node.stretch_mode = TextureRect.STRETCH_SCALE
	node.size = Vector2(img.get_width(), img.get_height())
	var over := RcLookVinyl.kit_pose(pose)
	over[&"shadow_k"] = shadow_k
	var mat := RcLookVinyl.kit_material(id, tex, art["body"], over)
	if old:
		var m := ShaderMaterial.new()
		m.shader = load(KIT_OLD)
		for p in mat.shader.get_shader_uniform_list():
			var n: StringName = p["name"]
			m.set_shader_parameter(n, mat.get_shader_parameter(n))
		mat = m
	node.material = mat
	return node


func _chrome_cases() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for id in [&"chrome_pink", &"chrome_yellow", &"chrome_blue", &"chrome_grey", &"chrome_glitch"]:
		out.append({"id": id, "over": {}, "burst": false})
	out.append({"id": &"chrome_glitch", "over": {}, "burst": true})
	out.append({"id": &"chrome_pink", "over": {&"sweep": SWEEP_AT, &"rainbow": RcLookVinyl.config().band_alpha}, "burst": false})
	return out


func _chrome_cell(case: Dictionary, old: bool, at: Vector2) -> Control:
	var w := _chrome_node(case, old)
	w.position = at
	w.scale = Vector2(0.6, 0.6)
	return w


func _chrome_node(case: Dictionary, old: bool) -> RcLookVinylMarkerText:
	var id: StringName = case["id"]
	var w := RcLookVinylMarkerText.new()
	w.size = WORD_SIZE
	w.marker = RcLookVinyl.marker_color(id)
	var over: Dictionary = (case["over"] as Dictionary).duplicate()
	if id == &"chrome_glitch":
		over[&"band_h"] = (FILL_BOTTOM - FILL_TOP) / float(BURST_BANDS)
		if case["burst"]:
			for i in BURST_BANDS:
				w.extra.append({"marker": Color(0, 1, float(i + 1) / 8.0), "dx": BURST_SHIFT * (1.0 if i % 2 == 0 else -1.0)})
			w.marker = Color(0, 1, 0, 0)
	var mat := RcLookVinyl.chrome_material(id, float(RcLookVinylMarkerText.FONT_PX), FILL_TOP, FILL_BOTTOM, over)
	if old:
		var m := ShaderMaterial.new()
		m.shader = load(CHROME_OLD)
		for p in mat.shader.get_shader_uniform_list():
			var n: StringName = p["name"]
			m.set_shader_parameter(n, mat.get_shader_parameter(n))
		mat = m
	w.material = mat
	return w


func _holo_cell(old: bool, at: Vector2) -> Control:
	var n := _holo_node(old)
	n.position = at
	n.scale = Vector2(CELL_SCALE, CELL_SCALE)
	return n


func _holo_node(old: bool) -> ColorRect:
	var n := ColorRect.new()
	n.size = HOLO_FIELD
	n.color = Color.WHITE
	var mat := RcLookVinyl.fill_material(&"kit_holo", 0.0, HOLO_FIELD.y, HOLO_FIELD, HOLO_SEED)
	if old:
		var m := ShaderMaterial.new()
		m.shader = load(FILL_OLD)
		for p in mat.shader.get_shader_uniform_list():
			var k: StringName = p["name"]
			m.set_shader_parameter(k, mat.get_shader_parameter(k))
		mat = m
	n.material = mat
	return n


func _card_cell(old: bool, at: Vector2) -> Control:
	var n := _card_node(old)
	n.position = at
	n.scale = Vector2(0.7, 0.7)
	return n


func _card_node(old: bool) -> ColorRect:
	var n := ColorRect.new()
	n.size = CARD_SIZE
	n.color = Color(0.2, 0.55, 0.9)
	var mat := RcLookVinyl.card_material(CARD_SIZE)
	mat.set_shader_parameter(&"scan_y", CARD_SCAN)
	mat.set_shader_parameter(&"gloss_t", CARD_GLOSS)
	if old:
		var m := ShaderMaterial.new()
		m.shader = load(CARD_OLD)
		for p in mat.shader.get_shader_uniform_list():
			var k: StringName = p["name"]
			m.set_shader_parameter(k, mat.get_shader_parameter(k))
		mat = m
	n.material = mat
	return n


# ---- the GDScript mirror of the kit shader -------------------------------------------------------------------------

func _mirror_cell(id: StringName, pose: StringName, _shadowless: bool, at: Vector2) -> Control:
	var art: Dictionary = _arts.get(id, RcLookVinyl.lab_art(id))
	var r := TextureRect.new()
	r.texture = ImageTexture.create_from_image(mirror_image(id, pose, art))
	r.stretch_mode = TextureRect.STRETCH_SCALE
	r.size = r.texture.get_size()
	r.position = at
	r.scale = Vector2(CELL_SCALE, CELL_SCALE)
	return r


## The kit shader's pipeline (rim, gloss, band, flap, grey; no shadow, no dissolve) run per pixel through RcLookVinyl.
static func mirror_image(id: StringName, pose: StringName, art: Dictionary) -> Image:
	var c := RcLookVinyl.config()
	var src: Image = art["image"]
	var body: Rect2 = art["body"]
	var u := RcLookVinyl.kit_uniforms(id, body)
	u.merge(RcLookVinyl.kit_pose(pose), true)
	var alpha_at := func(p: Vector2) -> float: return _bilinear_alpha(src, p)
	var fr := RcLookVinyl.fold_frame(body, int(u[&"corner"]), float(u.get(&"fold", 0.0)), float(u.get(&"peel_back", 0.0)),
			float(u[&"peel_px"]))
	var backing := _v3(u[&"backing_color"])
	var out := Image.create(src.get_width(), src.get_height(), false, Image.FORMAT_RGBA8)
	var glossy: float = u[&"glossy"]
	for y in src.get_height():
		for x in src.get_width():
			var px := Vector2(x, y) + Vector2(0.5, 0.5)
			var base := src.get_pixel(x, y)
			var s := RcLookVinyl.fold_s(px, fr)
			if fr["on"] and s < 0.0:
				base = Color(0, 0, 0, 0)
			var rgb := Vector3(base.r, base.g, base.b)
			var a := base.a
			if a > 0.0:
				rgb = RcLookVinyl.kit_rim(rgb, a, alpha_at, px, float(u[&"rim"]), glossy)
				rgb = RcLookVinyl.kit_gloss(rgb, px, body, float(u[&"gloss_k"]), float(u[&"gloss_pos"]),
						float(u[&"gloss_angle_deg"]), glossy)
				if float(u.get(&"rainbow", 0.0)) > 0.0 and float(u.get(&"band_t", -1.0)) >= 0.0:
					var dd := RcLookVinyl.kit_band_dd(px, body, float(u[&"band_t"]), float(u[&"band_width"]), float(u[&"band_deg"]))
					rgb = RcLookVinyl.band_mix(rgb, RcLookVinyl.foil(dd), RcLookVinyl.band_w(dd), float(u[&"band_alpha"]), 1.0)
			var fl := RcLookVinyl.kit_flap(alpha_at, px, fr, backing, float(u.get(&"peel_back", 0.0)), rgb, a)
			rgb = fl["rgb"]
			a = fl["a"]
			rgb = RcLookVinyl.grey(rgb, float(u.get(&"grey", 0.0)))
			out.set_pixel(x, y, Color(rgb.x, rgb.y, rgb.z, a * float(u.get(&"opacity", 1.0))))
	return out


static func _v3(col: Color) -> Vector3:
	return Vector3(col.r, col.g, col.b)


## texture() with linear filtering and clamped edges, alpha only (px in texel units, texel centres at +0.5).
static func _bilinear_alpha(img: Image, p: Vector2) -> float:
	var q := p - Vector2(0.5, 0.5)
	var x0 := floori(q.x)
	var y0 := floori(q.y)
	var fx := q.x - x0
	var fy := q.y - y0
	var w := img.get_width() - 1
	var h := img.get_height() - 1
	var a00 := img.get_pixel(clampi(x0, 0, w), clampi(y0, 0, h)).a
	var a10 := img.get_pixel(clampi(x0 + 1, 0, w), clampi(y0, 0, h)).a
	var a01 := img.get_pixel(clampi(x0, 0, w), clampi(y0 + 1, 0, h)).a
	var a11 := img.get_pixel(clampi(x0 + 1, 0, w), clampi(y0 + 1, 0, h)).a
	return lerpf(lerpf(a00, a10, fx), lerpf(a01, a11, fx), fy)


# ---- the pixel proof -----------------------------------------------------------------------------------------------

## Renders `node` alone into a transparent SubViewport of its size and returns the viewport.
func _viewport_of(node: Control) -> SubViewport:
	var vp := SubViewport.new()
	vp.size = Vector2i(node.size)
	vp.transparent_bg = true
	vp.render_target_update_mode = SubViewport.UPDATE_ONCE
	vp.add_child(node)
	add_child(vp)
	return vp


func _prove_cases() -> Array[Dictionary]:
	var cases: Array[Dictionary] = []
	for id in STOCKS:
		for pose in POSES:
			var art: Dictionary = _arts[id]
			cases.append({"name": "kit/%s/%s" % [id, pose], "a": _kit_node(id, pose, false, art, 1.0), "b": _kit_node(id, pose, true, art, 1.0)})
	for corner in 4:
		var art: Dictionary = _arts[&"kit_pink"]
		var over := {&"corner": corner, &"fold": RcLookVinyl.config().lab_fold, &"lift": RcLookVinyl.config().lab_lift}
		var a := _kit_node_with(&"kit_pink", over, false, art)
		var b := _kit_node_with(&"kit_pink", over, true, art)
		cases.append({"name": "kit/fold_corner_%d" % corner, "a": a, "b": b})
	for ch in _chrome_cases().size():
		var cs := _chrome_cases()[ch]
		cases.append({"name": "chrome/%s/%d" % [cs["id"], ch], "a": _chrome_node(cs, false), "b": _chrome_node(cs, true)})
	cases.append({"name": "fill/holo", "a": _holo_node(false), "b": _holo_node(true)})
	cases.append({"name": "card/scan_gloss", "a": _card_node(false), "b": _card_node(true)})
	return cases


func _kit_node_with(id: StringName, over: Dictionary, old: bool, art: Dictionary) -> TextureRect:
	var node := _kit_node(id, &"rest", old, art, 1.0)
	var m := node.material as ShaderMaterial
	for k: StringName in over:
		m.set_shader_parameter(k, over[k])
	return node


func _prove() -> void:
	var total_max := 0
	var failures := 0
	for case in _prove_cases():
		var va := _viewport_of(case["a"])
		var vb := _viewport_of(case["b"])
		for i in PROVE_FRAMES:
			await RenderingServer.frame_post_draw
		var ia := va.get_texture().get_image()
		var ib := vb.get_texture().get_image()
		var worst := _max_diff(ia, ib)
		total_max = maxi(total_max, worst)
		failures += 1 if worst > 0 else 0
		print("vinyl_prove: ", case["name"], " max ", worst)
		va.queue_free()
		vb.queue_free()
	await _prove_mirror()
	print("vinyl_prove: total max ", total_max, " failures ", failures)
	if _stage_args.has("--prove-only"):
		get_tree().quit(1 if failures > 0 else 0)


## The GDScript mirror against the shader (no shadow, no dissolve): reports the worst 8-bit channel gap over the
## pixels the sticker covers.
func _prove_mirror() -> void:
	for pair in [[&"kit_pink", &"rest"], [&"kit_pink", &"hover"], [&"kit_pink", &"fold"], [&"kit_kraft", &"band"],
			[&"kit_white", &"slap"], [&"kit_yellow", &"disabled"]]:
		var id: StringName = pair[0]
		var pose: StringName = pair[1]
		var art: Dictionary = _arts[id]
		var node := _kit_node(id, pose, false, art, 0.0)
		var vp := _viewport_of(node)
		for i in PROVE_FRAMES:
			await RenderingServer.frame_post_draw
		var gpu := vp.get_texture().get_image()
		var cpu := mirror_image(id, pose, art)
		print("vinyl_prove: mirror/%s/%s max %d" % [id, pose, _max_diff(gpu, cpu, true)])
		vp.queue_free()


func _max_diff(a: Image, b: Image, covered_only: bool = false) -> int:
	if a.get_size() != b.get_size():
		return 255
	var worst := 0
	for y in a.get_height():
		for x in a.get_width():
			var ca := a.get_pixel(x, y)
			var cb := b.get_pixel(x, y)
			if covered_only and ca.a < 1.0 / BYTE and cb.a < 1.0 / BYTE:
				continue
			var d := maxf(maxf(absf(ca.r - cb.r), absf(ca.g - cb.g)), maxf(absf(ca.b - cb.b), absf(ca.a - cb.a)))
			worst = maxi(worst, roundi(d * BYTE))
	return worst
