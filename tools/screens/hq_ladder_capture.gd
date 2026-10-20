extends Control
## HQ-LADDER-UI capture (windowed only, through tools/run_windowed.py): the Solace HQ ladder in the real netrun scene.
## Shots (PNG into --shots=<dir>): overview (the whole ladder, OVERVIEW view), across (an ACROSS option hovered), minimb
## (the mini-boss room hovered), crown (the crown fight's address line). tools/screens/hq_ladder_sheet.py joins them.
## User args: --shots=<dir>  --size=WxH (default 1280x720)  --seed=<n> (campaign seed, default 3)

const SCENE := "res://scenes/netrun_map/netrun_scene.tscn"
const SETTLE := 150
const STEPS := ["overview", "across", "minimb", "crown"]

var _args: Dictionary = {}
var _scene: Control
var _s: NetrunSession
var _i := -1
var _frame := 0
var _phase := "boot"
var _shots := ""


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	var wh := String(_args.get("size", "1280x720")).split("x")
	DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	get_window().size = Vector2i(int(wh[0]), int(wh[1]))
	_shots = String(_args.get("shots", "user://hq_ladder"))
	DirAccess.make_dir_recursive_absolute(_shots)
	AudioDirector.muted = true
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.save_slot = "lab_hq_ladder"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.new_campaign(int(_args.get("seed", "3")), &"solace")
	var c := RunManager.campaign
	_s = NetrunSession.start_hq_ladder(RunManager.resolver, c, c.roster[0].id, &"t1_a", 4, 5, RunManager.corporation)
	RunManager.netrun = _s
	_scene = load(SCENE).instantiate()
	add_child(_scene)
	_stand_at(3)
	_scene._show_current()
	_next.call_deferred()


## Puts the run on rung `layer` (a tower-Ward room, the gate and the earlier ward rooms walked), the Bloom front close behind.
func _stand_at(layer: int) -> void:
	var g := _s.run.map
	_s.run.visited = []
	for l in range(1, layer):
		_s.run.visited.append(g.nodes_in_layer(l)[0]["id"])
	_s.run.current_node_id = g.nodes_in_layer(layer)[0]["id"]
	var b := _s.run.corp_theme.solace
	b.layer_milli = layer * 1000
	b.front_milli = (layer - 2) * 1000 + 300


func _next() -> void:
	_i += 1
	_frame = 0
	if _i >= STEPS.size():
		print("HQLAD done")
		get_tree().quit()
		return
	var view: StreetRouteView = _scene.street_view
	match STEPS[_i]:
		"overview":
			if view != null:
				view.set_base_view(StreetRouteRules.View.OVERVIEW)
		"across":
			view.set_base_view(StreetRouteRules.View.DECISION)
			var opts := _s.available_nodes()
			for id in opts:
				if NetrunSession.entered_across(_s.run.map.get_node(id), _s.run.current_node_id):
					view._set_hover(String(id))
					_scene.show_node_panel(id)
		"minimb":
			var mb_layer := _s.config.solace_hq_mini_boss_rung + 1
			_stand_at(mb_layer - 1)
			_scene._show_current()
			view = _scene.street_view
			view.set_base_view(StreetRouteRules.View.DECISION)
			var mb: Dictionary = _s.run.map.nodes_in_layer(mb_layer)[0]
			view._set_hover(String(mb["id"]))
			_scene.show_node_panel(mb["id"])
		"crown":
			var g := _s.run.map
			_s.run.current_node_id = g.layers[g.layer_count() - 2][0]["id"]
			_scene._show_current()
			_scene.enter_node(g.layers[g.layer_count() - 1][0]["id"])
	_phase = "settle"


func _process(_delta: float) -> void:
	if _phase != "settle":
		return
	_frame += 1
	if _frame == SETTLE:
		get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_shots, STEPS[_i]])
		print("HQLAD shot ", STEPS[_i])
		_phase = ""
		_next()
