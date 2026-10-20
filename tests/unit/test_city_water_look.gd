extends GutTest
## NA-12 r3 (A-030), fast tier: the sea wall's coping reads at whole-city zoom (its width and gain are zoom-scaled
## functions of the config, monotonic and clamped), and the shore-light reflections hang straight down the screen,
## stay on water and within their reach, and are the same for the same plan (no randomness).

const CITY_CONFIG := "res://content/config/city_config.tres"
const SEEDS: Array[int] = [1, 7, -1, 424242, 99]

var _cfg: CityConfig


func before_all() -> void:
	_cfg = load(CITY_CONFIG)


func test_coping_scale_is_one_up_close_and_clamped_far() -> void:
	assert_eq(CityWater.coping_scale_at(_cfg, _cfg.coping_ref_ortho * 0.5), 1.0, "closer than the reference: 1")
	assert_eq(CityWater.coping_scale_at(_cfg, _cfg.coping_ref_ortho), 1.0)
	assert_eq(CityWater.coping_scale_at(_cfg, _cfg.coping_ref_ortho * 1000.0), _cfg.coping_zoom_max, "clamped at the max")


func test_coping_width_and_gain_grow_with_the_zoom_out() -> void:
	var last_w := 0.0
	var last_g := 0.0
	for ortho: float in [60.0, 240.0, 480.0, 900.0, 1400.0, 2400.0]:
		var sc := CityWater.coping_scale_at(_cfg, ortho)
		var w := CityWater.coping_width_bu(_cfg, sc)
		var g := CityWater.coping_gain(_cfg, sc)
		assert_gte(w, last_w, "width never narrows as the camera zooms out (ortho %s)" % ortho)
		assert_gte(g, last_g, "gain never dims as the camera zooms out (ortho %s)" % ortho)
		last_w = w
		last_g = g
	assert_eq(CityWater.coping_width_bu(_cfg, 1.0), _cfg.seawall_coping_bu, "up close: the configured width")
	assert_almost_eq(CityWater.coping_gain(_cfg, 1.0), _cfg.seawall_light_gain, 0.0001)
	assert_almost_eq(CityWater.coping_gain(_cfg, _cfg.coping_zoom_max), _cfg.seawall_light_gain * _cfg.coping_gain_far, 0.0001)


func test_screen_down_points_toward_the_camera() -> void:
	var cam := CityIsoCamera.new()
	cam.yaw_deg = _cfg.yaw_deg
	var f := cam.forward()
	var d := CityWater.screen_down(_cfg)
	assert_almost_eq(d.x, -f.x / Vector2(f.x, f.z).length(), 0.0001)
	assert_almost_eq(d.y, -f.z / Vector2(f.x, f.z).length(), 0.0001)
	assert_almost_eq(d.dot(Vector2(cam.right().x, cam.right().z)), 0.0, 0.0001, "straight down: no sideways drift")


func test_edge_hash_is_stable_and_in_range() -> void:
	for k in 200:
		var l := Vector2i(k * 7 - 50, k * 3 - 20)
		var h := CityWater.edge_hash(l, Vector2i(1, 0), 1)
		assert_gte(h, 0.0)
		assert_lte(h, 1.0)
		assert_eq(h, CityWater.edge_hash(l, Vector2i(1, 0), 1))


func test_smears_hang_down_within_reach_and_are_deterministic() -> void:
	var total := 0
	var reach := _cfg.water_reflect_reach_lots * _cfg.lot_bu
	var down := CityWater.screen_down(_cfg)
	for s in SEEDS:
		var plan := CityPlan.for_seed(s)
		if plan.coast.is_empty():
			continue
		var a := CityWater._smear_mesh(_cfg, plan, [])
		var b := CityWater._smear_mesh(_cfg, plan, [])
		assert_eq(a["count"], b["count"], "seed %d: same plan, same smears" % s)
		total += int(a["count"])
		var mesh: ArrayMesh = a["mesh"]
		if mesh == null:
			continue
		var v: PackedVector3Array = mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
		var uv: PackedVector2Array = mesh.surface_get_arrays(0)[Mesh.ARRAY_TEX_UV]
		# Triangles 0,1,2 and 0,2,3 of each quad: vertex 0 is the foot (left), 3 the far end (left): the far end lies
		# `down` of the foot (no sideways drift) and no farther than the reach.
		for q in v.size() / 6:
			var foot := v[q * 6]
			var far := v[q * 6 + 5]
			var rel := Vector2(far.x - foot.x, far.z - foot.z)
			assert_lte(rel.length(), reach + 0.01, "seed %d: within the reach" % s)
			assert_gt(rel.dot(down), 0.0, "seed %d: runs down the screen" % s)
			assert_lt(absf(rel.cross(down)), 0.01, "seed %d: straight down" % s)
			assert_gte(uv[q * 6 + 5].x, 0.0)
	assert_gt(total, 0, "some shore lights reflect on these seeds")
