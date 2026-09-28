extends GutTest
## Test suite optimization (docs/TEST_SUITE.md): under GUT the headless city keeps each
## built geometry by its inputs (NeonCity.geometry_memo_enabled) and skips emitting the
## triangles the dummy renderer never shows (NeonCity.emit_triangles). A reused geometry
## must be exactly the one a fresh build makes, any input that changes the city must change
## the key, and a build without triangles must place every roof, light, trail, beacon and
## sign exactly as a full build does, so neither switch changes what a test sees. Every
## district is still built with its triangles here, so the drawing code keeps running.

const DISTRICTS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell", &""]

var _memo_before: bool = true
var _emit_before: bool = false


func before_each() -> void:
	_memo_before = NeonCity.geometry_memo_enabled
	_emit_before = NeonCity.emit_triangles
	NeonCity.clear_geometry_memo()


func after_each() -> void:
	NeonCity.geometry_memo_enabled = _memo_before
	NeonCity.emit_triangles = _emit_before
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


## What a build places for the overlays and the live layer (everything but triangles).
func _placed(city: NeonCity) -> Dictionary:
	var b := _built(city)
	b.erase("verts")
	b.erase("cols")
	return b


func test_the_switches_are_on_under_the_test_runner_only() -> void:
	assert_true(NeonCity._is_gut_run(), "this process runs GUT")
	assert_true(_memo_before, "so the memo is on by default here (and off in the game)")
	assert_false(_emit_before, "and triangles are skipped here (and drawn in the game)")


func test_a_build_without_triangles_places_everything_a_full_build_does() -> void:
	NeonCity.geometry_memo_enabled = false
	for district in DISTRICTS:
		for net in [false, true]:
			NeonCity.emit_triangles = true
			var full := _city(district)
			full.net_mode = net
			full._camera()
			full._build_geometry()
			var what := "%s%s" % [district, " net" if net else ""]
			assert_gt(full._verts.size(), 1000, "%s: the full build draws the city" % what)
			assert_eq(full._verts.size(), full._cols.size(), what)
			NeonCity.emit_triangles = false
			var lean := _city(district)
			lean.net_mode = net
			lean._camera()
			lean._build_geometry()
			assert_eq(lean._verts.size(), 0, "%s: no triangles" % what)
			assert_false(lean._roofs.is_empty(), "%s: roofs placed" % what)
			# Compared with == (a failing assert_eq would print megabytes).
			assert_true(_placed(lean) == _placed(full), "%s: the same roofs, lights, trails, beacons, signs, streets and fist" % what)
			full.queue_free()
			lean.queue_free()


func test_a_reused_geometry_equals_a_fresh_build() -> void:
	NeonCity.emit_triangles = true
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
		assert_true(got[k] == want[k], "reused %s equals a fresh build" % k)
	# A drawn city with the memo on ends with the same roofs and camera as one without.
	var drawn := _city()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_true(drawn.camera_settled())
	assert_true(drawn._roofs == want["roofs"], "a memo hit draws the same roofs")


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
	NeonCity.emit_triangles = not NeonCity.emit_triangles
	assert_ne(base._memo_key(), k0, "triangles drawn or not")
	NeonCity.emit_triangles = not NeonCity.emit_triangles
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
