extends Node3D
## M14 asset parity: a close look at the art pass's vehicles and billboards (windowed only):
## the CLOSE flying car (CityMotionMeshes, sky_car's toon bands off the lane), the police chopper and
## the drone (toon + ink), and the four holo billboard panels. Writes one PNG and quits.
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/city/vehicle_lab.tscn -- --out=<png>

const FRAMES := 20


func _ready() -> void:
	var out := "user://vehicle_lab.png"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
	var cfg := CityMotionConfigData.shipped()
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.05, 0.04, 0.09)
	add_child(env)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 16.0
	add_child(cam)
	cam.look_at_from_position(Vector3(10, 9, 10), Vector3(0, 0.5, 0), Vector3.UP)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, 40, 0)
	add_child(sun)
	# the car: sky_car's material needs a path texture; draw its mesh with a plain unshaded part colouring instead
	var car := CityMotionMeshes.car(cfg, CitySkyTraffic.CarTier.CLOSE)
	var cm := MeshInstance3D.new()
	cm.mesh = car
	var mat := StandardMaterial3D.new()
	mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color = cfg.close_body_color
	cm.material_override = mat
	cm.position = Vector3(-4, 0, 3)
	cm.scale = Vector3.ONE * 2.0
	add_child(cm)
	for i in 2:
		var model := CityMotionMeshes.chopper(cfg.chopper_length * 2.0) if i == 0 else CityMotionMeshes.drone(cfg.drone_size * 3.0)
		var holder := Node3D.new()
		var m := ToonInkMaterial.make(cfg.chopper_color if i == 0 else cfg.drone_color)
		var body := MeshInstance3D.new()
		body.mesh = model["body"] as Mesh
		body.material_override = m
		body.scale = Vector3.ONE * float(model["scale"])
		body.position = model["offset"] as Vector3
		holder.add_child(body)
		if model["neon"] != null:
			var lit := MeshInstance3D.new()
			lit.mesh = model["neon"] as Mesh
			var nm := StandardMaterial3D.new()
			nm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			nm.vertex_color_use_as_albedo = true
			lit.material_override = nm
			lit.scale = body.scale
			lit.position = body.position
			holder.add_child(lit)
		holder.position = Vector3(1.5 + i * 3.0, 1.0, -2.0 + i * 4.0)
		add_child(holder)
	# the four billboard panels, steady (one panel each), in the lane colours
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	var bm := MultiMesh.new()
	bm.transform_format = MultiMesh.TRANSFORM_3D
	bm.use_colors = true
	bm.use_custom_data = true
	bm.mesh = quad
	bm.instance_count = cfg.billboard_panels
	var bmat := ShaderMaterial.new()
	bmat.shader = load("res://shaders/city/holo_billboard.gdshader")
	bmat.set_shader_parameter(&"steady", true)
	bmat.set_shader_parameter(&"size", cfg.billboard_size)
	bmat.set_shader_parameter(&"scanlines", cfg.billboard_scanlines)
	bmat.set_shader_parameter(&"panels", cfg.billboard_panels)
	bmat.set_shader_parameter(&"panel_tex", CityMotionLayers.BILLBOARD_PANELS)
	for k in cfg.billboard_panels:
		bm.set_instance_transform(k, Transform3D(Basis.IDENTITY, Vector3(-6.0 + k * 2.0, 4.5, -5.0 - k * 2.0)))
		bm.set_instance_color(k, cfg.lane_colors[k % cfg.lane_colors.size()])
		bm.set_instance_custom_data(k, Color(0.0, float(k), 0.0, 0.0))
	var bmi := MultiMeshInstance3D.new()
	bmi.multimesh = bm
	bmi.material_override = bmat
	add_child(bmi)
	for _f in FRAMES:
		await get_tree().process_frame
	get_viewport().get_texture().get_image().save_png(out)
	print("vehicle_lab wrote ", out)
	get_tree().quit()
