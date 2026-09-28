extends GutTest
## Test suite optimization (docs/TEST_SUITE.md): under GUT the headless city keeps each
## built geometry by its inputs (NeonCity.geometry_memo_enabled). A reused geometry must be
## exactly the one a fresh build makes, and any input that changes the city must change
## the key, so the memo never changes what a test sees.

var _memo_before: bool = true


func before_each() -> void:
	_memo_before = NeonCity.geometry_memo_enabled
	NeonCity.clear_geometry_memo()


func after_each() -> void:
	NeonCity.geometry_memo_enabled = _memo_before
	NeonCity.clear_geometry_memo()


func _city(district: StringName = &"solace") -> NeonCity:
	var city: NeonCity = add_child_autofree(NeonCity.new())
	city.set_anchors_preset(Control.PRESET_TOP_LEFT)
	city.size = Vector2(1280, 720)
	city.district = district
	return city


## What a build leaves behind: the triangles and everything overlays and the live layer read.
func _built(city: NeonCity) -> Dictionary:
	return {"verts": city._verts, "cols": city._cols, "roofs": city._roofs, "lights": city._lights,
		"trails": city._trails, "beacons": city._beacons, "signs": city._signs, "hq_rects": city._hq_rects,
		"streets": [city._street_i, city._street_j, city._local_i, city._local_j],
		"fist": [city._fist_segs, city._fist_box, city._fist_hull]}


func test_the_memo_is_on_under_the_test_runner_only() -> void:
	assert_true(NeonCity._is_gut_run(), "this process runs GUT")
	assert_true(_memo_before, "so the memo is on by default here (and off in the game)")


func test_a_reused_geometry_equals_a_fresh_build() -> void:
	NeonCity.geometry_memo_enabled = false
	var fresh := _city()
	fresh._camera()
	fresh._build_geometry()
	var want := _built(fresh)
	assert_gt((want["verts"] as PackedVector2Array).size(), 1000, "a real city was built")
	NeonCity.geometry_memo_enabled = true
	var first := _city()
	first._camera()
	var key := first._memo_key()
	assert_ne(key, "")
	first._build_geometry()
	first._memo_store(key)
	var second := _city()
	second._camera()
	assert_eq(second._memo_key(), key, "the same look and camera share a key")
	second._memo_restore(key)
	var got := _built(second)
	for k in want:
		assert_eq(var_to_str(got[k]), var_to_str(want[k]), "reused %s equals a fresh build" % k)
	# A drawn city with the memo on ends with the same roofs and camera as one without.
	var drawn := _city()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_true(drawn.camera_settled())
	assert_eq(var_to_str(drawn._roofs), var_to_str(want["roofs"]), "a memo hit draws the same roofs")


func test_every_input_of_the_city_changes_the_key() -> void:
	var base := _city()
	base._camera()
	var k0 := base._memo_key()
	var other := _city(&"meridian")
	other._camera()
	assert_ne(other._memo_key(), k0, "district")
	var sized := _city()
	sized.size = Vector2(1000, 600)
	sized._camera()
	assert_ne(sized._memo_key(), k0, "size")
	var moved := _city()
	moved.focus_grid = Vector2(3, 4)
	moved._camera()
	assert_ne(moved._memo_key(), k0, "camera")
	for change in ["city_seed", "net_mode", "ink_set", "face_texture", "corp_creep"]:
		var c := _city()
		match change:
			"city_seed":
				c.city_seed = 99
			"net_mode":
				c.net_mode = true
			"ink_set":
				c.ink_set = 0
			"face_texture":
				c.face_texture = 1
			"corp_creep":
				c.corp_creep = 0.31
		c._camera()
		assert_ne(c._memo_key(), k0, change)
	var cult := _city()
	cult.cultures = {&"solace": "egyptian"}
	cult._camera()
	assert_ne(cult._memo_key(), k0, "cultures")
	var infl := _city()
	# The exact influence, not its rounded signature (the procedural city reads the values).
	infl.influence = {"corp": &"solace", "sway": 0.5, "sources": [], "sites": PackedVector2Array()}
	infl._camera()
	var k1 := infl._memo_key()
	assert_ne(k1, k0, "influence")
	infl.influence = {"corp": &"solace", "sway": 0.5001, "sources": [], "sites": PackedVector2Array()}
	assert_ne(infl._memo_key(), k1, "a change below the bake signature's step still re-keys")
	NeonCity.geometry_memo_enabled = false
	assert_eq(base._memo_key(), "", "switched off: no key, every draw builds")


func test_the_memo_keeps_a_bounded_number_of_geometries() -> void:
	for n in NeonCity.GEOMETRY_MEMO_CAP + 3:
		NeonCity._geometry_memo["k%d" % n] = {}
		var c := _city()
		c._memo_store("s%d" % n)
	assert_true(NeonCity._geometry_memo.size() <= NeonCity.GEOMETRY_MEMO_CAP, "least recently used drop out")
