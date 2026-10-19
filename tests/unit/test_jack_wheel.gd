extends GutTest
## NA-25b r3 (art-pass A-019): the jack's wheel is the real class wheel (the combat's WheelView), its hub core covers the screen before the
## switch runs (so the HQ side never shows the city under a half-drawn hub), the hub holds as a CRT terminal only past `jack_hub_crt`, and
## the hole the lens opens grows from nothing to past the screen.

const SCREENS: Array[Vector2] = [Vector2(1280.0, 720.0), Vector2(1920.0, 1080.0), Vector2(2560.0, 1080.0)]


func _link() -> Dictionary:
	return {"from": "S-00", "to": "S-07", "build": "site_x", "street": true, "points": PackedVector2Array([Vector2(300, 400), Vector2(600, 200)])}


func test_the_hubs_cover_scale_covers_every_screen_from_the_middle() -> void:
	var jw := JackWheel.new()
	add_child_autofree(jw)
	jw.setup(_link(), SCREENS[0])
	var share := jw.hub_share()
	assert_gt(share, 0.0, "the real wheel has a hub")
	assert_lt(share, 1.0)
	for screen in SCREENS:
		var scale := JackSequence.cover_scale_for(screen, share, JackSequence.WHEEL_R)
		var hub_r := JackSequence.WHEEL_R * scale * share
		assert_true(JackWheel.covers(screen * 0.5, hub_r, 0.0, screen), "the covering hub reaches every corner of %s" % str(screen))
		assert_false(JackWheel.covers(screen * 0.5, hub_r * 0.5, 0.0, screen), "half that hub does not")


func test_a_hole_in_the_hub_never_counts_as_covered() -> void:
	var screen := SCREENS[0]
	assert_false(JackWheel.covers(screen * 0.5, 5000.0, 4.0, screen), "the lens open even a little shows the run")
	assert_true(JackWheel.covers(screen * 0.5, 5000.0, 0.0, screen), "closed, a huge hub covers")


func test_the_hole_grows_from_nothing_past_the_screen() -> void:
	var screen := SCREENS[0]
	var hub := 5000.0
	assert_eq(JackWheel.hole_radius(0.0, hub, screen), 0.0, "closed at the start (the jack-out's end is the covering frame)")
	var last := -1.0
	for i in 11:
		var r := JackWheel.hole_radius(float(i) / 10.0, hub, screen)
		assert_gte(r, last, "never shrinks while opening")
		last = r
	assert_gte(last, screen.length() * 0.5, "open, it clears the farthest corner")


func test_the_short_hold_breathes_and_the_long_one_becomes_a_crt_terminal() -> void:
	var was := Motion.force_live
	Motion.force_live = true
	var seq := JackSequence.new()
	add_child_autofree(seq)
	seq._begin(_link())
	assert_not_null(seq.wheel_view, "the class wheel is there")
	assert_not_null(seq.wheel_view.wheel, "it is the combat's own WheelView")
	assert_eq(seq._hold_line, "routing ... building street_site_x", "the CRT line names the building")
	seq.wheel_r = JackSequence.WHEEL_R
	seq.wheel_scale = 40.0
	seq.switched = true
	seq._holding = true
	seq._process(Motion.seconds(&"jack_hub_crt") * 0.4)
	assert_false(seq.wheel_view.holding(), "under the threshold: the plain breathe")
	seq._process(Motion.seconds(&"jack_hub_crt"))
	assert_true(seq.wheel_view.holding(), "past it: the CRT terminal")
	assert_not_null(seq.wheel_view.hold, "navy glass, scanlines, hex dump and edge glow are the CRT panel's own")
	seq._holding = false
	seq._end()
	assert_false(seq.wheel_view.holding(), "the sequence's end clears the hold")
	Motion.force_live = was
