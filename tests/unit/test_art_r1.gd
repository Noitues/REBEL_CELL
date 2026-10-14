extends GutTest
## ART-R1 (art-pass review of the overnight sheets): 9a the route page never shows the empty map
## (a cover holds the page that left until the city has drawn).


func test_the_cover_lifts_only_when_the_city_is_ready_for_a_few_frames_or_after_the_cap() -> void:
	assert_false(RouteCover.lifts(0, 0.0))
	assert_false(RouteCover.lifts(RouteCover.READY_FRAMES - 1, 1.0), "not yet ready for long enough")
	assert_true(RouteCover.lifts(RouteCover.READY_FRAMES, 0.1))
	assert_true(RouteCover.lifts(0, RouteCover.MAX_WAIT), "a city that never reports ready cannot hold the screen")


func test_the_map_is_not_revealed_before_its_city_is_drawn() -> void:
	var state := {"ready": false}
	var cover := RouteCover.make(ImageTexture.create_from_image(Image.create(4, 4, false, Image.FORMAT_RGBA8)), func() -> bool: return state["ready"])
	add_child_autofree(cover)
	for i in 10:
		cover._process(1.0 / 60.0)
	assert_true(cover.holding(), "the city is not drawn: the previous frame stays up")
	assert_eq(cover.mouse_filter, Control.MOUSE_FILTER_STOP, "and the hidden map takes no clicks")
	state["ready"] = true
	for i in RouteCover.READY_FRAMES - 1:
		cover._process(1.0 / 60.0)
	assert_true(cover.holding(), "one ready frame is not enough")
	state["ready"] = false
	cover._process(1.0 / 60.0)
	state["ready"] = true
	for i in RouteCover.READY_FRAMES - 1:
		cover._process(1.0 / 60.0)
	assert_true(cover.holding(), "a flicker restarts the count")
	cover._process(1.0 / 60.0)
	assert_false(cover.holding(), "the city has drawn: the page shows")
