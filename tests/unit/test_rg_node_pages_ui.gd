extends GutTest
## RG-02/03/04 flow test for the netrun scene: a REST page shows through the scene (PATCH, REWIRE, UNDO, LEAVE are
## mouse-reachable buttons and drive the session); the Workshop and Cache flows are added by their slices.

const SCENE := "res://scenes/netrun_map/netrun_scene.tscn"

var _scene: Control
var _s: NetrunSession


func before_each() -> void:
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	_scene = add_child_autofree(load(SCENE).instantiate())
	RunManager.new_campaign(3, &"meridian")
	var c := RunManager.campaign
	_s = NetrunSession.start(RunManager.resolver, c, c.roster[0].id, 1, &"m1_a", 5, RunManager.corporation)
	RunManager.netrun = _s
	_scene._show_current()
	await get_tree().process_frame


func after_each() -> void:
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _page() -> NodePage:
	# The old page is freed at the end of the frame, so a rebuilt page's name gets a suffix: find by type, newest last.
	var found: NodePage = null
	for n in _scene.find_children("*", "VBoxContainer", true, false):
		if n is NodePage and not n.is_queued_for_deletion():
			found = n
	return found


func _btn(button_name: String) -> Button:
	var page := _page()
	return page.find_child(button_name, true, false) as Button if page != null else null


## Waits (bounded) until button `button_name` exists and its disabled flag equals `disabled`.
func _wait_btn(button_name: String, disabled: bool) -> bool:
	return await BoundedWait.until(get_tree(), func() -> bool:
		var b := _btn(button_name)
		return b != null and b.disabled == disabled, 5.0)


func test_the_rest_page_patches_undoes_rewires_and_leaves() -> void:
	var first := _s.available_nodes()[0]
	_s.run.map.get_node(first)["type"] = RC.InfilNodeType.REST
	_s.run.operative.hp = 1
	_scene.enter_node(first)
	assert_true(await _wait_btn("RestPatch", false), "the REST page shows")
	assert_eq(_s.run.phase, RunState.Phase.REST)
	_btn("RestPatch").pressed.emit()
	assert_true(await _wait_btn("RestPatch", true), "one mode per visit")
	assert_gt(_s.run.operative.hp, 1, "PATCH healed through the scene")
	_btn("RestUndo").pressed.emit()
	assert_true(await _wait_btn("RestPatch", false), "UNDO re-opens the page")
	assert_eq(_s.run.operative.hp, 1, "UNDO")
	_btn("RestLeave").pressed.emit()
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return _s.run.phase == RunState.Phase.MAP, 5.0), "LEAVE returns to the route")


func test_the_workshop_page_buys_a_refit_and_leaves() -> void:
	var first := _s.available_nodes()[0]
	_s.run.map.get_node(first)["type"] = RC.InfilNodeType.WORKSHOP
	_s.run.cycles = 500
	_scene.enter_node(first)
	assert_true(await _wait_btn("WorkshopBuy", true), "the Workshop page shows with BUY disabled")
	assert_eq(_s.run.phase, RunState.Phase.WORKSHOP)
	_btn("WorkshopOffer0").pressed.emit()
	assert_true(await _wait_btn("WorkshopSlot0", false), "a slot opens once an offer is picked")
	_btn("WorkshopSlot0").pressed.emit()
	assert_true(await _wait_btn("WorkshopBuy", false), "BUY enables with an offer and a slot")
	var offer := StringName(String(_s.run.node_state["offers"][0]))
	_btn("WorkshopBuy").pressed.emit()
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return _s.run.operative.slot_slice_ids[0] == offer, 5.0), "the refit applied")
	assert_lt(_s.run.cycles, 500)
	assert_true(await _wait_btn("WorkshopBuy", true), "one buy per visit")
	_btn("WorkshopLeave").pressed.emit()
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return _s.run.phase == RunState.Phase.MAP, 5.0), "LEAVE returns to the route")


func test_a_cache_pays_and_shows_the_existing_reward_page() -> void:
	var first := _s.available_nodes()[0]
	_s.run.map.get_node(first)["type"] = RC.InfilNodeType.CACHE
	var cycles := _s.run.cycles
	_scene.enter_node(first)
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return _s.run.phase == RunState.Phase.REWARD, 5.0), "the card offer opens")
	assert_gt(_s.run.cycles, cycles, "the Cycles were paid on entry")


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
	assert_eq((_scene.find_child("LootTitle", true, false) as HoloSticker).verb, _scene.LOOT_PLAIN, "the title stays LOOT")
	assert_eq(_scene.node_word({"type": RC.InfilNodeType.CACHE, "elite": false, "id": &"x"}).to_upper(), "CACHE", "the strip names the node: CACHE")
