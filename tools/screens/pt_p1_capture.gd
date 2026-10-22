extends Control
## PB-SOL-1 P1 capture (windowed only, through tools/run_windowed.py): the RESPIN warning (I2) and a fight resumed
## mid-turn (B-14) in the real netrun scene. Shots (PNG into --shots=<dir>): staged (a nudge and a card staged, the
## THIS TURN list up), warning (RESPIN asks first), resumed (the same fight after Quit and Continue: the list is back).
## User args: --shots=<dir>  --size=WxH (default 1280x720)  --seed=<n> (campaign seed, default 1)

const SCENE := "res://scenes/netrun_map/netrun_scene.tscn"
const SETTLE := 120

var _args: Dictionary = {}
var _net: Control
var _shots := ""
var _step := 0
var _frame := 0
var _waiting := false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	var wh := String(_args.get("size", "1280x720")).split("x")
	DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	get_window().size = Vector2i(int(wh[0]), int(wh[1]))
	_shots = String(_args.get("shots", "user://pt_p1"))
	DirAccess.make_dir_recursive_absolute(_shots)
	AudioDirector.muted = true
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.save_slot = "lab_pt_p1"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	_open_net()
	_net.new_campaign(int(_args.get("seed", "1")))
	_net.start_run(1)
	_net.enter_node(RunManager.netrun.available_nodes()[0])
	_frame = 0
	_waiting = true


func _open_net() -> void:
	_net = load(SCENE).instantiate()
	add_child(_net)


func _combat() -> Control:
	return _net.combat_scene


func _process(_delta: float) -> void:
	if not _waiting:
		return
	_frame += 1
	if _step == 0 and _frame == SETTLE and _combat() != null:
		var c := _combat()
		c.skip_motion()
		c.nudge(1)
		var st: CombatState = c.engine.state()
		for i in st.hand.size():
			if not CardTargeting.options(c.engine.resolver, st, i).is_empty():
				c.play_card(i)
				break
		c.skip_motion()
		_frame = 0
		_step = 1
	elif _step == 1 and _frame == SETTLE:
		_shot("staged")
		_combat().request_respin()
		_frame = 0
		_step = 2
	elif _step == 2 and _frame == SETTLE:
		_shot("warning")
		_combat().get_node("RespinConfirm").no_button.pressed.emit()
		RunManager.autosave()
		_net.queue_free()
		_frame = 0
		_step = 3
	elif _step == 3 and _frame == 10:
		RunManager.reset()
		RunManager.resume()
		_open_net()
		_net.resume()
		_frame = 0
		_step = 4
	elif _step == 4 and _frame == SETTLE:
		_shot("resumed")
		_waiting = false
		RunManager.delete_save()
		print("PTP1 done")
		get_tree().quit()


func _shot(nm: String) -> void:
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_shots, nm])
	print("PTP1 shot ", nm)
