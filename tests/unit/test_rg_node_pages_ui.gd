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
