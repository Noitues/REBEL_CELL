class_name BoundedWait
extends RefCounted
## Test helper (DECISIONS "Test suite: bounded waits"): wait for a real condition, never a
## fixed time. A test that starts an animation and then waits a fixed time (a timer, a
## frame count, the wall clock) before asserting the animation finished flakes under load:
## a slow frame, a chained tween that starts a frame late or a timer that fires before the
## tween it waits for all land the assertion before the end state. `until` polls the
## condition once a frame and gives up only after BOTH `limit` seconds of game time (the
## frames' process delta, the clock tweens and timers run on) and `min_frames` frames, so
## neither a few long frames nor many short ones cut a chain of tweens short. It returns as
## soon as the condition holds, so a generous limit costs nothing on a passing run; assert
## on the end state afterwards (the return value says whether it was reached).

## Seconds of game time added to a Motion-derived limit (tween start-up, chained steps).
const SLACK := 2.0
## Frames every wait allows at least, however long each frame took.
const MIN_FRAMES := 60


## Awaits frames until `done.call()` is true, or until `limit` seconds of game time and
## `min_frames` frames have passed. Returns `done.call()`.
static func until(tree: SceneTree, done: Callable, limit: float, min_frames: int = MIN_FRAMES) -> bool:
	var waited := 0.0
	var frames := 0
	while not done.call():
		if waited >= limit and frames >= min_frames:
			return false
		await tree.process_frame
		waited += tree.root.get_process_delta_time()
		frames += 1
	return true


## Like `until`, for a test that also asserts how long the motion took: returns the game
## time the wait took less its `drop_longest` longest frames (a motion is a short chain of
## tweens and each link can end on a frame that overshoots it; a stalled frame is not the
## motion's length), or INF when the condition never held.
static func timed(tree: SceneTree, done: Callable, limit: float, drop_longest: int = 2) -> float:
	var deltas: Array[float] = []
	var frames := 0
	var waited := 0.0
	while not done.call():
		if waited >= limit and frames >= MIN_FRAMES:
			return INF
		await tree.process_frame
		var d := tree.root.get_process_delta_time()
		deltas.append(d)
		waited += d
		frames += 1
	deltas.sort()
	var took := 0.0
	for i in maxi(0, deltas.size() - drop_longest):
		took += deltas[i]
	return took


## Awaits `frames` frames with game time stopped (Engine.time_scale 0: tweens and timers
## hold where they are) for a test that asserts a motion is still under way after the
## layout has had its frames. A fixed frame count with the clock running lets one slow
## frame finish the motion first. Layout, deferred calls and redraws still run.
static func frozen_frames(tree: SceneTree, frames: int) -> void:
	var scale := Engine.time_scale
	Engine.time_scale = 0.0
	for i in frames:
		await tree.process_frame
	Engine.time_scale = scale


## A limit for a wait on animations from the Motion table: their seconds summed, plus SLACK.
static func motion_limit(ids: Array[StringName], extra: float = 0.0) -> float:
	var s := SLACK + extra
	for id in ids:
		s += Motion.seconds(id) + Motion.delay_of(id)
	return s
