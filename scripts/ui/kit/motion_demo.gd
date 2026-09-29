class_name MotionDemo
extends RefCounted
## Capture support for screen demos (Animation pass ANIM-6, ANIMATION_HANDOFF 6.2): a scene
## started with `--demo-set=<id>.<field>=<v>,...` tunes a duplicate of the motion table (the
## file never changes), like the motion lab, so variant strips can be captured in context;
## `--demo-speed=<x>` sets the speed. `after_frames` runs a demo step a few frames in.
## Dev use only: without those flags nothing changes.

## The frame a scene demo's action starts on (as the lab's DEMO_START_FRAME).
const START_FRAME := 6


## Applies `--demo-set` / `--demo-speed` from the command line. Returns true when any did.
static func apply_args() -> bool:
	var any := false
	var cfg: UiMotionData = null
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--demo-speed="):
			Motion.set_speed(float(arg.trim_prefix("--demo-speed=")))
			any = true
		elif arg.begins_with("--demo-set="):
			if cfg == null:
				cfg = Motion.config().duplicate(true) as UiMotionData
				Motion.use_config(cfg)
			for part in arg.trim_prefix("--demo-set=").split(",", false):
				var kv := part.split("=")
				var path := kv[0].split(".")
				var e := cfg.find(StringName(path[0])) if path.size() == 2 else null
				if kv.size() != 2 or e == null:
					push_error("MotionDemo: bad --demo-set part '%s'." % part)
					continue
				var field := StringName(path[1])
				if field in [&"ease", &"trans"]:
					e.set(field, int(kv[1]))
				elif field == &"enabled":
					e.set(field, kv[1] == "true")
				else:
					e.set(field, float(kv[1]))
				print("MotionDemo: %s.%s = %s" % [path[0], path[1], kv[1]])
			any = true
	return any


## Runs `step` `frames` process frames from now (a demo's action), while `node` stays in
## the tree. ANIM-R6: one-shot connections checked each frame, never an `await` (a
## coroutine awaiting the tree resumed on a node freed meanwhile: a scene left mid-demo).
static func after_frames(node: Node, frames: int, step: Callable) -> void:
	var w := Waiter.new()
	w.ref = weakref(node)
	w.left = frames
	w.step = step
	w.tick()


## One demo step's wait: a one-shot connection per frame (its own, so two waits never share
## a connection), checking its node each frame; it frees itself when done or when the node
## has gone.
class Waiter extends Object:
	var ref: WeakRef
	var left: int = 0
	var step: Callable

	func tick() -> void:
		var node := ref.get_ref() as Node
		if node == null or not node.is_inside_tree() or node.is_queued_for_deletion():
			call_deferred(&"free")
			return
		if left > 0:
			left -= 1
			node.get_tree().process_frame.connect(tick, CONNECT_ONE_SHOT)
			return
		print("MotionDemo: step on frame %d" % Engine.get_process_frames())
		step.call()
		call_deferred(&"free")
