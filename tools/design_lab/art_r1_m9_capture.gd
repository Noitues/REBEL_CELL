extends Node
## ART-R1 9b: ANIM-FLOW M9 (the HQ's entrance after the jack cover lifts), a Movie Maker capture
## (dev tool, windowed only through tools/run_windowed.py, `--write-movie <dir>/f.png --fixed-fps 30
## --quit-after N`). The HQ sits on the raid page; a jack out switches it back to the HQ page under the
## opaque cover (the cover lifts, and the page's layout then settles in where it can be seen).
## Frame ~DEFAULT_START begins the jack out.

const HQ := "res://scenes/hq/hq_scene.tscn"
const START_FRAME := 20

var _frame: int = 0
var _hq: Control


func _ready() -> void:
	RunManager.save_slot = "art_r1_m9"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.reset()
	RunManager.new_campaign(1)
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	_hq = load(HQ).instantiate()
	holder.add_child(_hq)
	_hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _process(_delta: float) -> void:
	_frame += 1
	if _frame == START_FRAME and _hq != null:
		print("m9: jack out at frame ", Engine.get_frames_drawn())
		Fx.jack_out(func() -> void: _hq.show_hq(), -1.0, "HQ")
