class_name StickerSweepQueue
extends RefCounted
## "Gloss 0.22 at rest with one slow sweep on one sticker at a time" (ART_BIBLE v2 §1.2;
## round 19 sticker_lib19 gloss_k). Stickers that take part (`VinylSticker.ambient_sweep`)
## join here; the queue hands the sweep to one of them at a time, in the order they joined
## (deterministic: never dictionary order), with `sticker_gloss_sweep`'s delay of rest
## between two sweeps. View only: no state of the game is read or changed.

static var _members: Array[int] = []
static var _current: int = 0
static var _sweeping: int = 0
static var _next_at_ms: int = 0


## Adds `sticker` to the queue (once).
static func join(sticker: Object) -> void:
	var id := sticker.get_instance_id()
	if not _members.has(id):
		_members.append(id)


## Removes `sticker`; when it was sweeping, the turn passes on.
static func leave(sticker: Object) -> void:
	var id := sticker.get_instance_id()
	var i := _members.find(id)
	if i < 0:
		return
	_members.remove_at(i)
	if _sweeping == id:
		_sweeping = 0
	if _current >= _members.size():
		_current = 0


## True when it is `sticker`'s turn to sweep now (it then sweeps; `done` hands the turn on).
static func take_turn(sticker: Object, now_ms: int) -> bool:
	_prune()
	if _members.is_empty() or _sweeping != 0 or now_ms < _next_at_ms:
		return false
	if _members[_current % _members.size()] != sticker.get_instance_id():
		return false
	_sweeping = sticker.get_instance_id()
	return true


## The sweeping sticker is done: the next one sweeps after `rest_ms`.
static func done(sticker: Object, now_ms: int, rest_ms: int) -> void:
	if _sweeping != sticker.get_instance_id():
		return
	_sweeping = 0
	_next_at_ms = now_ms + rest_ms
	if not _members.is_empty():
		_current = (_current + 1) % _members.size()


## The sticker sweeping now (0 when none): at most one at a time.
static func sweeping() -> int:
	return _sweeping


## How many stickers take part.
static func size() -> int:
	_prune()
	return _members.size()


## Forgets every member (tests).
static func reset() -> void:
	_members.clear()
	_current = 0
	_sweeping = 0
	_next_at_ms = 0


static func _prune() -> void:
	var i := _members.size() - 1
	while i >= 0:
		if not is_instance_id_valid(_members[i]):
			if _sweeping == _members[i]:
				_sweeping = 0
			_members.remove_at(i)
		i -= 1
	if _current >= _members.size():
		_current = 0
