extends SceneTree
## Bake crash (dev tool, DECISIONS "Animation pass - bake crash"): opens the route and the
## HQ's Grid and raid setup over and over while their city bakes run (lots, slices, chunk
## submission, the GPU copy), and frees them at varied points: with free() inside the tree's
## process_frame emission (as GUT's autofree does), with queue_free, and with
## CityBakeCache.shutdown() mid-bake. A real display bakes for real (never headless: there
## nothing bakes; `--simulate` then takes the tests' simulated path).
##
##   godot --path . -s tools/design_lab/bake_stress.gd [-- --cycles=40 --simulate]
##
## Prints "bake_stress: <n> cycles, <b> bakes landed, <s> shutdowns mid-bake, busy <k>" and
## exits 0; a crash is the failure. Autoload-touching classes load at run time (a -s script
## compiles before the autoloads exist).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "bake_stress"

var _cycles := 40
var _cache: GDScript
var _rm: Node
var _holder: Control
var _hq: Control
var _nr: Control
var _cycle := 0
var _step := 0
var _wait := 0
var _shutdowns := 0
var _frames := 0


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--cycles="):
			_cycles = int(a.trim_prefix("--cycles="))
	_cache = load("res://scripts/ui/kit/city_bake_cache.gd")
	_cache.set("simulate", "--simulate" in OS.get_cmdline_user_args())
	process_frame.connect(_tick)


## Deterministic spread of the frames waited at each step (no global RNG).
func _spread(n: int) -> int:
	return (_cycle * 37 + n * 11) % 60 + 1


func _tick() -> void:
	_frames += 1
	if _frames > 60 * 60 * 20:
		_finish()
		return
	if _wait > 0:
		_wait -= 1
		return
	match _step:
		0:
			_rm = root.get_node("RunManager")
			_rm.set("save_slot", SLOT)
			_rm.set("scene_switching_enabled", false)
			_step = 1
		1:
			_rm.call("delete_save")
			_rm.call("reset")
			_holder = Control.new()
			_holder.size = Vector2(1280, 720)
			root.add_child(_holder)
			_nr = (load(NETRUN) as PackedScene).instantiate()
			_holder.add_child(_nr)
			_nr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			_step = 2
			_wait = 1
		2:
			_nr.call("new_campaign", 1)
			_nr.call("start_run", 1)
			_step = 3
			_wait = _spread(1)
		3:
			_hq = (load(HQ) as PackedScene).instantiate()
			_holder.add_child(_hq)
			_hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			_step = 4
			_wait = 1
		4:
			_hq.call("new_campaign", 1)
			_hq.call("show_grid")
			_step = 5
			_wait = _spread(2)
		5:
			if _cycle % 2 == 0:
				_hq.call("show_raid")
			_step = 6
			_wait = _spread(3) % 7
		6:
			# Freed mid-bake, three ways in turn.
			match _cycle % 3:
				0:
					_holder.free()  # inside process_frame's emission
				1:
					_holder.queue_free()
				2:
					_cache.call("shutdown")
					_shutdowns += 1
					_holder.free()
			_holder = null
			_cycle += 1
			_step = 1 if _cycle < _cycles else 7
			_wait = _spread(4) % 5
		7:
			_finish()


func _finish() -> void:
	process_frame.disconnect(_tick)
	print("bake_stress: %d cycles, %d bakes landed, %d shutdowns mid-bake, busy %d%s" % [_cycle, int(_cache.get("bakes_done")),
		_shutdowns, int(_cache.call("busy")), " (simulated)" if bool(_cache.get("simulate")) else ""])
	_cache.call("shutdown")
	_rm.call("delete_save")
	_rm.set("save_slot", _rm.get("DEFAULT_SLOT"))
	quit(0)
