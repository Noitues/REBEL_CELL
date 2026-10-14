extends Node
## Plan 1 ANIM-FLOW capture (dev tool, windowed only through tools/run_windowed.py, Movie Maker at 30 fps):
## a scripted run on the netrun screen. Frame 60: the first fight is entered from the route (M5: the move, the
## page opening, the backdrop). Then the fight is won, and the reward page's first pick is taken (M6).
## Same script runs on main (before) and the branch (after): it only uses the scene's public API and guards
## the methods the branch adds.

const SCENE := "res://scenes/netrun_map/netrun_scene.tscn"
const ENTER_FRAME := 60
const WIN_FRAME := 200
const PICK_WAIT_FRAMES := 40
const END_FRAME := 560

var _scene: Control
var _frame: int = 0
var _picked_at: int = -1
var _list_open_at: int = -1


func _ready() -> void:
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	_scene = load(SCENE).instantiate()
	holder.add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	_scene.start_run(1)
	print("p1_flow_capture: ready")


func _process(_delta: float) -> void:
	_frame += 1
	if _scene == null or not is_instance_valid(_scene):
		return
	if _frame == ENTER_FRAME:
		print("p1_flow_capture: enter at frame ", Engine.get_frames_drawn())
		_scene._demo_enter_fight()
	elif _frame == WIN_FRAME:
		_scene._demo_combat_end("win")
	elif _frame > WIN_FRAME and _picked_at < 0:
		var s := RunManager.netrun
		if s != null and s.run.phase == RunState.Phase.REWARD and _scene._panel != null and not PageTransition.running(_scene):
			if _list_open_at < 0:
				_list_open_at = _frame
				if _scene.rewards_list_on():
					_scene.open_reward(0)
			elif _frame >= _list_open_at + PICK_WAIT_FRAMES:
				print("p1_flow_capture: pick at frame ", Engine.get_frames_drawn())
				_picked_at = _frame
				_scene.choose_reward(0)
	if _frame >= END_FRAME:
		get_tree().quit()
