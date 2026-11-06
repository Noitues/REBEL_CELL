

func test_the_rest_page_is_the_event_layout_in_the_rest_hue() -> void:
	var first := _s.available_nodes()[0]
	_s.run.map.get_node(first)["type"] = RC.InfilNodeType.REST
	_scene.enter_node(first)
	assert_true(await _wait_btn("RestPatch", false), "the REST page shows")
	var win := _page().find_child("RestWindow", true, false) as CrtWindow
	assert_not_null(win)
	assert_eq(win.glass.corp_color, RouteInk.accent_of(CityMapOverlay.KIND_REST), "the window is tinted in the REST hue")
	assert_eq(_btn("RestSlot0").theme_type_variation, ChoiceSticker.TYPE, "a wheel slot is the event page's choice sticker")
	assert_not_null(_btn("RestSlot0").get_node_or_null("ChoiceNumber"), "its number stands on the tab")
	assert_true(_btn("RestPatch") is HoloSticker, "PATCH is a vinyl verb sticker")
	var side := _scene.find_child("NodeSide", true, false)
	assert_not_null(side, "the side column stands beside the window")
	assert_not_null(side.find_child("EventRun", true, false), "the RUN terminal is in it")
	assert_eq((side.find_child("NodeIcon", true, false) as TextureRect).texture, RouteOverlay.sticker_art(CityMapOverlay.KIND_REST), "the kind's route sticker is stamped under the title")


func test_the_workshop_page_wears_the_workshop_hue_and_icon() -> void:
	var first := _s.available_nodes()[0]
	_s.run.map.get_node(first)["type"] = RC.InfilNodeType.WORKSHOP
	_s.run.cycles = 500
	_scene.enter_node(first)
	assert_true(await _wait_btn("WorkshopBuy", true), "the Workshop page shows")
	var win := _page().find_child("WorkshopWindow", true, false) as CrtWindow
	assert_eq(win.glass.corp_color, RouteInk.accent_of(CityMapOverlay.KIND_WORKSHOP), "the window is tinted in the WORKSHOP hue")
	assert_eq(_btn("WorkshopOffer0").theme_type_variation, ChoiceSticker.TYPE, "an offer is a choice sticker")
	var side := _scene.find_child("NodeSide", true, false)
	assert_eq((side.find_child("NodeIcon", true, false) as TextureRect).texture, RouteOverlay.sticker_art(CityMapOverlay.KIND_WORKSHOP))


func test_a_cache_loot_title_carries_the_cache_sticker_and_the_strip_says_cache() -> void:
	var first := _s.available_nodes()[0]
	_s.run.map.get_node(first)["type"] = RC.InfilNodeType.CACHE
	_scene.enter_node(first)
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return _s.run.phase == RunState.Phase.REWARD, 5.0), "the card offer opens")
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return _scene.find_child("LootKindStamp", true, false) != null, 5.0), "the kind stamp is on the title")
	assert_eq((_scene.find_child("LootKindStamp", true, false) as TextureRect).texture, RouteOverlay.sticker_art(CityMapOverlay.KIND_CACHE))
	assert_eq((_scene.find_child("LootTitle", true, false) as HoloSticker).verb, NetrunScene.LOOT_PLAIN, "the title stays LOOT")
	assert_true(NetrunScene.loot_strip(_s).to_upper().contains("CACHE"), "the strip names the node: CACHE")
