extends GutTest
## NA-22 (full tier, windowed only: it renders). The pixel acceptance of the netrun city shaders. Headless there is no
## renderer, so every test is pending there; run it with
## `python tools/run_windowed.py --log <file> -- -s addons/gut/gut_cmdln.gd -gselect=test_city_shaders_render -gexit`.
## 1 look_blend 0 = the old page (<= 1/255, per-instance state ignored), 2 four instances: cut, Bayer ghost, dissolve and
## edge lines each change their own channel, 3 a Bayer ghost at opacity 0.5 covers 50 % +- 3 % and is identical in two
## runs, 4 a streak lane at t = 0 equals t = 4.0 s, 5 emission_multiplier is linear at 0, 1, 2, 6 reduce effects freezes the
## beam sweep and the streaks at the plate's anim_t, 7 the fog volume appears with look_blend and not at 0.

const CFG := preload("res://content/config/city_config.tres")
const OLD_BUILDING := "res://tests/fixtures/na22/city_building_before.gdshader.txt"
const SIZE := Vector2i(256, 128)
## Slot x centres (BU) of the four instances in the row.
const SLOTS: Array[float] = [-9.0, -3.0, 3.0, 9.0]

var _reduce_before: float = 0.0


func before_each() -> void:
	pass


func after_each() -> void:
	RenderingServer.global_shader_parameter_set(&"reduce_effects", 0.0)


func _headless() -> bool:
	if DisplayServer.get_name() == "headless":
		pending("needs a renderer (run windowed)")
		return true
	return false


## Renders `root` (a Node3D) in its own world with an orthographic camera of `ortho` BU width looking along -Z (or `look`
## down), after `frames` frames; returns the image.
func _shot(root: Node3D, ortho: float, cam_at: Vector3, look_down: bool = false, env: Environment = null, size: Vector2i = SIZE, fov: float = 0.0) -> Image:
	var vp := SubViewport.new()
	vp.size = size
	vp.own_world_3d = true
	vp.msaa_3d = Viewport.MSAA_DISABLED
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var e: Environment = env
	if e == null:
		e = Environment.new()
		e.background_mode = Environment.BG_COLOR
		e.background_color = Color.BLACK
		e.ambient_light_source = Environment.AMBIENT_SOURCE_DISABLED
		e.reflected_light_source = Environment.REFLECTION_SOURCE_DISABLED
		e.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	var we := WorldEnvironment.new()
	we.environment = e
	vp.add_child(we)
	vp.add_child(root)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = ortho
	if fov > 0.0:
		cam.projection = Camera3D.PROJECTION_PERSPECTIVE
		cam.fov = fov
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	cam.near = 0.5
	cam.far = 500.0
	vp.add_child(cam)
	cam.current = true
	if look_down:
		cam.look_at_from_position(cam_at, cam_at - Vector3.UP, Vector3.FORWARD)
	else:
		cam.position = cam_at
	for i in 4:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img: Image = vp.get_texture().get_image()
	vp.queue_free()
	return img


func _sun() -> DirectionalLight3D:
	var l := DirectionalLight3D.new()
	l.rotation_degrees = Vector3(-35.0, 25.0, 0.0)
	l.shadow_enabled = false
	return l


## Four buildings (6 x 10 BU) in a row, `w[i]` the packed INSTANCE_CUSTOM.w of slot i.
func _row(mat: ShaderMaterial, w: Array[float]) -> Node3D:
	var root := Node3D.new()
	root.add_child(_sun())
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_colors = true
	mm.use_custom_data = true
	mm.mesh = CityMeshKit.unit_prism(4, 6, 4, 0.0, 0.0, 1)
	mm.instance_count = w.size()
	for i in w.size():
		var poly := PackedVector2Array([Vector2(SLOTS[i] - 2.5, -2.5), Vector2(SLOTS[i] + 2.5, -2.5), Vector2(SLOTS[i] + 2.5, 2.5), Vector2(SLOTS[i] - 2.5, 2.5)])
		mm.set_instance_transform(i, CityMeshKit.instance_transform(poly, 0.0, 10.0))
		mm.set_instance_color(i, Color(0.55, 0.5, 0.6))
		mm.set_instance_custom_data(i, Color(1.0, 0.0, 0.3, w[i]))
	var mi := MultiMeshInstance3D.new()
	mi.multimesh = mm
	mi.material_override = mat
	mi.custom_aabb = AABB(Vector3(-30, -5, -30), Vector3(60, 40, 60))
	root.add_child(mi)
	return root


func _building_mat(old: bool, look_blend: float) -> ShaderMaterial:
	var m := CityMaterials.building(CFG, [])
	if old:
		var sh := Shader.new()
		sh.code = FileAccess.get_file_as_string(OLD_BUILDING)
		m.shader = sh
	else:
		NetrunShaderKit.setup_building(m, look_blend)
		m.set_shader_parameter(&"look_blend", look_blend)
	return m


## Pixels of slot `i` that are not background.
func _drawn(img: Image, i: int) -> int:
	var n := 0
	var cx: float = float(SIZE.x) * 0.5 + SLOTS[i] / 24.0 * float(SIZE.x)
	for y in img.get_height():
		for x in range(int(cx - 0.125 * SIZE.x), int(cx + 0.125 * SIZE.x)):
			var c: Color = img.get_pixel(x, y)
			if maxf(c.r, maxf(c.g, c.b)) > 2.0 / 255.0:
				n += 1
	return n


func _max_diff(a: Image, b: Image) -> int:
	var d := 0
	for y in a.get_height():
		for x in a.get_width():
			var p: Color = a.get_pixel(x, y)
			var q: Color = b.get_pixel(x, y)
			d = maxi(d, maxi(absi(roundi(p.r * 255.0) - roundi(q.r * 255.0)), maxi(absi(roundi(p.g * 255.0) - roundi(q.g * 255.0)), absi(roundi(p.b * 255.0) - roundi(q.b * 255.0)))))
	return d


func _mean(img: Image, linear: bool = false) -> float:
	var s := 0.0
	for y in img.get_height():
		for x in img.get_width():
			var c: Color = img.get_pixel(x, y).srgb_to_linear() if linear else img.get_pixel(x, y)
			s += c.r + c.g + c.b
	return s / float(img.get_width() * img.get_height())


func test_look_blend_zero_is_the_old_page_within_one_level() -> void:
	if _headless():
		return
	var states: Array[float] = [0.0, NetrunInstancePack.pack(10.0, 3.8, 0.5, 1.0, 0.5), NetrunInstancePack.pack(10.0, 99.0, 0.18, 0.6, 0.0), 1.0]
	var old: Image = await _shot(_row(_building_mat(true, 0.0), [0.0, 0.0, 0.0, 1.0]), 24.0, Vector3(0, 5, 40))
	var now: Image = await _shot(_row(_building_mat(false, 0.0), states), 24.0, Vector3(0, 5, 40))
	assert_gt(_drawn(old, 0), 100, "the old page draws the buildings")
	assert_lte(_max_diff(old, now), 1, "at look_blend 0 the page is unchanged (<= 1/255) whatever the per-instance state")


func test_four_instances_each_change_their_own_channel() -> void:
	if _headless():
		return
	var base: Image = await _shot(_row(_building_mat(false, 0.5), [0.0, 0.0, 0.0, 0.0]), 24.0, Vector3(0, 5, 40))
	var w: Array[float] = [NetrunInstancePack.pack(10.0, 4.0, 1.0, 0.0, 0.0), NetrunInstancePack.pack(10.0, 99.0, 0.5, 0.0, 0.0),
		NetrunInstancePack.pack(10.0, 99.0, 1.0, 0.0, 0.5), NetrunInstancePack.pack(10.0, 99.0, 0.5, 1.0, 0.0)]
	var img: Image = await _shot(_row(_building_mat(false, 0.5), w), 24.0, Vector3(0, 5, 40))
	var b0 := _drawn(base, 0)
	assert_gt(b0, 500, "baseline building has pixels")
	assert_lt(_drawn(img, 0), int(float(_drawn(base, 0)) * 0.75), "cut: the top is gone (4 of 10 BU left)")
	assert_almost_eq(float(_drawn(img, 1)) / float(_drawn(base, 1)), 0.5, 0.03, "ghost 0.5: half the pixels")
	assert_almost_eq(float(_drawn(img, 2)) / float(_drawn(base, 2)), 0.5, 0.03, "dissolve 0.5: half the pixels")
	assert_gt(_drawn(img, 3), _drawn(img, 1), "edge lines add pixels to the ghost")
	# Untouched buildings are identical to the baseline.
	var w_one: Array[float] = [0.0, 0.0, 0.0, 0.0]
	var again: Image = await _shot(_row(_building_mat(false, 0.5), w_one), 24.0, Vector3(0, 5, 40))
	assert_eq(_max_diff(base, again), 0, "the same state renders the same twice")


func test_the_bayer_ghost_is_deterministic_and_covers_its_opacity() -> void:
	if _headless():
		return
	var w: Array[float] = [NetrunInstancePack.pack(10.0, 99.0, 0.5, 0.0, 0.0), NetrunInstancePack.pack(10.0, 99.0, 0.5, 0.0, 0.0), 0.0, 0.0]
	var a: Image = await _shot(_row(_building_mat(false, 1.0), w), 24.0, Vector3(0, 5, 40))
	var b: Image = await _shot(_row(_building_mat(false, 1.0), w), 24.0, Vector3(0, 5, 40))
	assert_eq(_max_diff(a, b), 0, "two runs render identically: pixel position only, no randomness")
	var solid: Image = await _shot(_row(_building_mat(false, 1.0), [0.0, 0.0, 0.0, 0.0]), 24.0, Vector3(0, 5, 40))
	for i in 2:
		assert_almost_eq(float(_drawn(a, i)) / float(_drawn(solid, i)), 0.5, 0.03, "slot %d covers 50 %% +- 3 %%" % i)


func test_emission_multiplier_is_linear_at_0_1_2() -> void:
	if _headless():
		return
	var means: Array[float] = []
	for k in [0.0, 1.0, 2.0]:
		var m := _building_mat(false, 0.0)
		m.set_shader_parameter(&"window_gain", 0.2)
		m.set_shader_parameter(&"emission_multiplier", k)
		var root := _row(m, [0.0, 0.0, 0.0, 0.0])
		root.get_child(0).queue_free()  # no sun: the windows are the only light
		var img: Image = await _shot(root, 24.0, Vector3(0, 5, 40))
		means.append(_mean(img, true))
	assert_lt(means[0], 0.0005, "0 = dark")
	assert_gt(means[1], 0.002, "1 = the windows glow")
	assert_almost_eq(means[2] / means[1], 2.0, 0.04, "2 = twice (linear)")


func _lane() -> Dictionary:
	return {"a": [0.0, 0.0], "b": [80.0, 0.0], "z": 0.5, "speed": 20.0,
		"streaks": [{"u0": 3.0, "len": 12.0, "gap": 8.0, "bright": 1.0}, {"u0": 30.0, "len": 6.0, "gap": 20.0, "bright": 0.7}, {"u0": 55.0, "len": 15.0, "gap": 9.0, "bright": 1.2}]}


func _streak_img(t: float, frozen: float = NAN) -> Image:
	var root := Node3D.new()
	var node := NetrunShaderKit.streak_node(_lane(), Color(1.0, 0.8, 0.5))
	NetrunShaderKit.set_clock([node.material_override], t, frozen)
	root.add_child(node)
	return await _shot(root, 90.0, Vector3(40.0, 20.0, 0.0), true, null, Vector2i(512, 64))


func test_a_streak_lane_loops_seamlessly_on_four_seconds() -> void:
	if _headless():
		return
	var t0: Image = await _streak_img(0.0)
	var t4: Image = await _streak_img(4.0)
	var t1: Image = await _streak_img(1.0)
	assert_gt(_mean(t0), 0.001, "the lane draws")
	assert_lte(_max_diff(t0, t4), 1, "t = 4.0 s equals t = 0 (<= 1/255)")
	assert_gt(_max_diff(t0, t1), 8, "and it moves in between")


func test_reduce_effects_freezes_streaks_and_the_beam_sweep_at_the_plate_anim_t() -> void:
	if _headless():
		return
	var plate_t := 0.0
	var live_a: Image = await _streak_img(plate_t, plate_t)
	var live_b: Image = await _streak_img(1.7, plate_t)
	assert_gt(_max_diff(live_a, live_b), 8, "effects on: the lane moves")
	RenderingServer.global_shader_parameter_set(&"reduce_effects", 1.0)
	var red: Image = await _streak_img(1.7, plate_t)
	assert_lte(_max_diff(live_a, red), 1, "reduce effects: the plate's anim_t, whatever the clock says")
	RenderingServer.global_shader_parameter_set(&"reduce_effects", 0.0)
	var beam := {"pos": [0.0, 0.0, 0.0], "lean": [3.0, 3.0], "sweep_deg": 6.0, "phase": 0.0}
	var imgs: Array[Image] = []
	for t in [0.0, 1.0]:
		var root := Node3D.new()
		var n := NetrunShaderKit.beam_node(beam, Color(0.2, 0.8, 1.0), 14.0)
		NetrunShaderKit.set_clock([n.material_override], t, 0.0)
		root.add_child(n)
		imgs.append(await _shot(root, 60.0, Vector3(0, 25, 40)))
	assert_gt(_mean(imgs[0]), 0.0005, "the beam draws")
	assert_gt(_max_diff(imgs[0], imgs[1]), 4, "the sweep moves it")
	RenderingServer.global_shader_parameter_set(&"reduce_effects", 1.0)
	var root2 := Node3D.new()
	var n2 := NetrunShaderKit.beam_node(beam, Color(0.2, 0.8, 1.0), 14.0)
	NetrunShaderKit.set_clock([n2.material_override], 1.0, 0.0)
	root2.add_child(n2)
	var frozen: Image = await _shot(root2, 60.0, Vector3(0, 25, 40))
	assert_lte(_max_diff(imgs[0], frozen), 1, "reduce effects: the beam holds the plate's pose")


func test_the_fog_volume_shows_with_look_blend_and_not_at_zero() -> void:
	if _headless():
		return
	var lit: Array[float] = []
	for lb in [0.0, 1.0]:
		var env := Environment.new()
		env.background_mode = Environment.BG_COLOR
		env.background_color = Color.BLACK
		env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
		NetrunShaderKit.configure_environment(env)
		var root := Node3D.new()
		var fv := NetrunShaderKit.fog_volume(Vector3.ZERO)
		var fm := fv.material as ShaderMaterial
		fm.set_shader_parameter(&"look_blend", lb)
		fm.set_shader_parameter(&"density_mul", 40.0)
		# A street 30 BU behind the camera side: fog stands behind the street face everywhere in view.
		fm.set_shader_parameter(&"sec_a", Vector2(-200.0, 20.0))
		fm.set_shader_parameter(&"sec_c", Vector2(200.0, 20.0))
		fm.set_shader_parameter(&"sec_nrm", Vector2(0.0, 1.0))
		# Saturate the noise masks so the check does not depend on where the noise happens to be.
		fm.set_shader_parameter(&"remap_clump", Vector2(-2.0, -1.0))
		fm.set_shader_parameter(&"remap_oct", Vector2(-2.0, -1.0))
		fm.set_shader_parameter(&"front", Vector2(-900.0, -800.0))
		fm.set_shader_parameter(&"floor_range", Vector2(-2.0, -1.0))
		root.add_child(fv)
		var img: Image = await _shot(root, 120.0, Vector3(0, 12, 60), false, env, SIZE, 60.0)
		lit.append(_mean(img))
	assert_lt(lit[0], 0.0005, "look_blend 0: no volume")
	assert_gt(lit[1], lit[0] + 0.002, "look_blend 1: the fog glows")
