extends GutTest
## NA-21 pixel parity (DERIVE_V2_REVIEW Q1.8, AD 5): a stored pose, set on a real Godot Camera3D through
## `NetrunFrustum.apply` (PROJECTION_FRUSTUM, `size` = frame width at the near plane, `frustum_offset` = shift x width),
## projects the room corners to the same pixels as the Python / twin `Pose.proj` in the 1920 x 1080 reference frame.
## The tolerance is a config value (`NetrunArtConfigData.frustum_tolerance`, a fraction of the frame width).

const NEAR := 0.5
const FAR := 8000.0

var _vp: SubViewport
var _cam: Camera3D


func before_each() -> void:
	_vp = SubViewport.new()
	_vp.size = Vector2i(1920, 1080)
	add_child_autoqfree(_vp)
	_cam = Camera3D.new()
	_vp.add_child(_cam)


## Godot pixel of plan point `p` through the camera's own projection matrix, or an empty Array behind it.
func _godot_px(p: Array) -> Array:
	var view: Vector3 = _cam.global_transform.affine_inverse() * NetrunFrustum.to_world(p)
	if view.z >= -NEAR:
		return []
	var clip: Vector4 = _cam.get_camera_projection() * Vector4(view.x, view.y, view.z, 1.0)
	var nx: float = clip.x / clip.w
	var ny: float = clip.y / clip.w
	return [(nx * 0.5 + 0.5) * 1920.0, (1.0 - (ny * 0.5 + 0.5)) * 1080.0]


func _corners(derive: Dictionary) -> Array:
	var pts: Array = []
	var ids: Array = (derive["rooms"] as Dictionary).keys()
	IdSort.sort_ids(ids)
	for id: String in ids:
		pts.append_array(NetrunCameraRig.room_corners(derive["rooms"][id]))
	return pts


func _check_pose(pose: NetrunPose, pts: Array, label: String) -> int:
	NetrunFrustum.apply(_cam, pose, NEAR, FAR)
	var tol_px: float = NetrunArtConfigData.shipped().frustum_tolerance * float(NetrunArtConfigData.shipped().rig["ref_w"])
	var checked := 0
	for p: Array in pts:
		var want := pose.proj(p)
		var got := _godot_px(p)
		if want.is_empty() or got.is_empty():
			continue
		checked += 1
		var err := maxf(absf(got[0] - want[0]), absf(got[1] - want[1]))
		if err > tol_px:
			fail_test("%s: Godot pixel %s vs twin %s (error %.4f px, tolerance %.4f px)" % [label, str(got), str(want), err, tol_px])
			return checked
	return checked


func _poses_of(poses: Dictionary) -> Array:
	var out: Array = [["overview", NetrunPose.from_json(poses["overview"]["pose"])],
		["decision", NetrunPose.from_json(poses["decision"]["pose"])]]
	for f: Dictionary in poses["fixtures"]:
		out.append(["decision_" + String(f["name"]), NetrunPose.from_json(f["decision"]["pose"])])
		out.append(["hover_" + String(f["name"]), NetrunPose.from_json(f["hover_pose"])])
	if poses.has("dive"):
		var d: Dictionary = poses["dive"]
		out.append(["dive_hq", NetrunPose.from_json(d["hq_pose"])])
		for s: Dictionary in d["samples"]:
			out.append(["dive_%s" % str(s["u"]), NetrunPose.from_json(s["pose"])])
	return out


func test_frustum_offset_matches_shift_for_street_and_hq_poses() -> void:
	var total := 0
	for seed_name in ["101", "104", "109"]:
		var w := NaFixture.load_inputs(seed_name)
		var street := NetrunArtDeriver.derive_street(w["city"], w["net"], w["run_graph"], w["site"], w["partial_street"])
		var hq := NetrunArtDeriver.derive_hq(w["city"], w["run_graph"], w["corp"], w["partial_hq"])
		var sp := NetrunArtDeriver.poses(street, w["city"], w["run_graph"], w["net"])
		var hp := NetrunArtDeriver.poses(hq, w["city"], w["run_graph"])
		for pair: Array in _poses_of(sp):
			total += _check_pose(pair[1], _corners(street), "street %s %s" % [seed_name, pair[0]])
		for pair: Array in _poses_of(hp):
			total += _check_pose(pair[1], _corners(hq), "hq %s %s" % [seed_name, pair[0]])
	assert_gt(total, 500, "many projected points were compared")


func test_shift_sign_moves_the_picture_left_and_down() -> void:
	# a positive shift_x moves content to screen left, a positive shift_y moves it down (Blender sign, Q1.8)
	var base := NetrunPose.make([0.0, 0.0, 0.0], 0.0, 10.0, 50.0, 40.0)
	var shifted := NetrunPose.make([0.0, 0.0, 0.0], 0.0, 10.0, 50.0, 40.0, 0.1, 0.05)
	var a := base.proj([0.0, 0.0, 0.0])
	var b := shifted.proj([0.0, 0.0, 0.0])
	assert_lt(b[0], a[0], "shift_x > 0 moves left")
	assert_gt(b[1], a[1], "shift_y > 0 moves down")
	NetrunFrustum.apply(_cam, shifted, NEAR, FAR)
	var g := _godot_px([0.0, 0.0, 0.0])
	assert_almost_eq(g[0], b[0], 0.2)
	assert_almost_eq(g[1], b[1], 0.2)


func test_tolerance_is_a_config_value() -> void:
	assert_gt(NetrunArtConfigData.shipped().frustum_tolerance, 0.0)
	assert_lt(NetrunArtConfigData.shipped().frustum_tolerance, 0.01)
