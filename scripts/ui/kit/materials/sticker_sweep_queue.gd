class_name StickerSweepQueue
extends RefCounted
## The sticker sweep scheduler (designer 2026-10-06, art-pass review D22: "one slow sweep on one sticker at a
## time"; ART_BIBLE v2 1.2). Of the stickers that take part (`ambient_sweep`) ONE is the screen's primary verb
## and only it sweeps: first the one that is named primary (rank 0), else the first pink verb (rank 1), else
## the first to join (rank 2); ties by join order, never dictionary order. One rainbow sweep runs on it every
## 4 to 6 seconds (the period is drawn from the `sticker_sweep_period` entry's range with a seeded stream, no
## global randomness) and never two at once. A member offers `sweep_rank() -> int`, `sweep_ready() -> bool`
## and `run_sweep() -> float`. View only: no state of the game is read or changed.

## The period's entry: delay = the shortest period, duration = the longest (seconds); amplitude = the seed.
const PERIOD := &"sticker_sweep_period"
const STREAM := &"sticker_sweep"

static var _members: Array[int] = []
static var _sweeping: int = 0
static var _next_at_ms: int = 0
static var _rng: RandomNumberGenerator = null


## Adds `sticker` to the queue (once).
static func join(sticker: Object) -> void:
	var id := sticker.get_instance_id()
	if not _members.has(id):
		_members.append(id)


## Removes `sticker`; when it was sweeping, the turn is free again.
static func leave(sticker: Object) -> void:
	var id := sticker.get_instance_id()
	var i := _members.find(id)
	if i < 0:
		return
	_members.remove_at(i)
	if _sweeping == id:
		_sweeping = 0


## The member that is the screen's primary verb now (null when none can sweep): the lowest rank among the
## members that are ready, in join order.
static func primary() -> Object:
	_prune()
	var best: Object = null
	var best_rank := 1 << 30
	for id in _members:
		var o := instance_from_id(id)
		if o == null or not o.has_method(&"sweep_ready") or not bool(o.call(&"sweep_ready")):
			continue
		var r := int(o.call(&"sweep_rank"))
		if r < best_rank:
			best_rank = r
			best = o
	return best


## True when it is `sticker`'s turn to sweep now (it then sweeps; `done` hands the turn back).
static func take_turn(sticker: Object, now_ms: int) -> bool:
	if _sweeping != 0 or now_ms < _next_at_ms:
		return false
	if primary() != sticker:
		return false
	_sweeping = sticker.get_instance_id()
	return true


## The sweeping sticker is done: the next sweep comes one period (4 to 6 s from the start of this one) later.
static func done(sticker: Object, now_ms: int, sweep_seconds: float) -> void:
	if _sweeping != sticker.get_instance_id():
		return
	_sweeping = 0
	_next_at_ms = now_ms + int(maxf(0.0, next_period() - sweep_seconds) * 1000.0)


## The next period (seconds at the current speed) from the entry's range, by the seeded stream.
static func next_period() -> float:
	var lo := Motion.delay_of(PERIOD)
	var hi := maxf(lo, Motion.seconds(PERIOD))
	if _rng == null:
		_rng = RngStreams.make_stream(int(Motion.amplitude(PERIOD)), STREAM)
	return _rng.randf_range(lo, hi)


## The sticker sweeping now (0 when none): at most one at a time.
static func sweeping() -> int:
	return _sweeping


## How many stickers take part.
static func size() -> int:
	_prune()
	return _members.size()


## Forgets every member and restarts the stream (tests).
static func reset() -> void:
	_members.clear()
	_sweeping = 0
	_next_at_ms = 0
	_rng = null


static func _prune() -> void:
	var i := _members.size() - 1
	while i >= 0:
		if not is_instance_id_valid(_members[i]):
			if _sweeping == _members[i]:
				_sweeping = 0
			_members.remove_at(i)
		i -= 1
