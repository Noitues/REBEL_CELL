extends Node
## Plan 1 ANIM-COMBAT capture (dev tool, windowed only through tools/run_windowed.py, Movie Maker at 30 fps):
## a scripted fight. Frame 20: Fine Tune is played (M1). Frame 60: a PERFECT landing tag is forced on the
## player's wheel (M3). Frame 100: SEND IT (M2 numbers and beams, M7 the enemy's return strike).
## Same script runs on main (before) and the branch (after); it only uses the scene's public API.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const PLAY_FRAME := 20
const PERFECT_FRAME := 60
const SEND_FRAME := 100
const END_FRAME := 240

var _scene: Control
var _frame: int = 0


func _ready() -> void:
	RunManager.new_campaign(1)
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	var idx := -1
	for s in range(1, 80):
		_scene = load(SCENE).instantiate()
		_scene.auto_start = false
		holder.add_child(_scene)
		_scene.start_fight(&"collections_agent", s)
		var hand: Array = _scene.engine.state().hand
		for i in hand.size():
			if StringName(String(hand[i])) == &"fine_tune":
				idx = i
		if idx >= 0:
			break
		_scene.free()
	print("p1_combat_capture: seed found, fine_tune at ", idx)
	_scene.set_meta("idx", idx)


func _process(_delta: float) -> void:
	_frame += 1
	if _scene == null:
		return
	if _frame == PLAY_FRAME:
		_scene.play_card(int(_scene.get_meta("idx")))
	elif _frame == PERFECT_FRAME:
		var v: WheelView = _scene._player_view
		if "payoff_to" in v:
			v.payoff_to = _scene._payoff_point(_scene.engine.state())
		v.play_precision(RC.PrecisionTier.PERFECT, 0, 0)
	elif _frame == SEND_FRAME:
		_scene.end_turn()
	elif _frame >= END_FRAME:
		get_tree().quit()
