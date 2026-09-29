class_name BannerQueue
extends Node
## ART_BIBLE §6.6 / §10 rule 4: one banner (or stamp) per region at a time; the others
## queue. A region is a name on a host node (a wheel's hub, a map's verdict band, the
## raid panel): `BannerQueue.of(host, region)` returns that region's queue. `push` shows a
## banner at once when the region is free, else after the ones before it; each is held
## `seconds` (default: the stamp reading rule ZineStamp.hold_seconds of its words), then
## hidden (or freed with `free_after`), then the next one follows after `banner_gap`.
## The queue shows and hides the banners it is given; the caller builds and places them.
## Reading time is read raw (never sped up); under reduce effects banners still hold (their
## own entrance motion is the caller's). View only.

## A banner started showing / finished.
signal shown(banner: CanvasItem)
signal finished(banner: CanvasItem)

const GAP_MOTION := &"banner_gap"
const NODE_PREFIX := "BannerQueue_"

## The region's name.
var region: StringName = &""
## Free each banner when it is done (else hide it).
var free_after: bool = true
var _queue: Array = []  # [[banner, seconds], ...]
var _current: CanvasItem = null
var _timer: SceneTreeTimer = null


## The queue for `region` on `host` (made on first use, a child of `host`).
static func of(host: Node, p_region: StringName) -> BannerQueue:
	var n := NODE_PREFIX + String(p_region)
	var q := host.get_node_or_null(n) as BannerQueue
	if q == null:
		q = BannerQueue.new()
		q.name = n
		q.region = p_region
		host.add_child(q)
	return q


## The words a banner says (its `stamp_text`, `text`, or "").
static func words_of(banner: Object) -> String:
	for key in [&"stamp_text", &"text"]:
		var v: Variant = banner.get(key)
		if v is String:
			return v
	return ""


## Queues `banner` (hidden until its turn), held `seconds` (< 0: its words' reading time).
func push(banner: CanvasItem, seconds: float = -1.0) -> void:
	if seconds < 0.0:
		seconds = ZineStamp.hold_seconds(words_of(banner))
	banner.visible = false
	_queue.append([banner, seconds])
	if _current == null:
		_next()


## The banner showing now (null when the region is free).
func current() -> CanvasItem:
	return _current if _current != null and is_instance_valid(_current) else null


## How many banners wait.
func pending() -> int:
	return _queue.size()


## Ends the banner showing now at once (a skip); the next follows after the gap.
func finish_current() -> void:
	if _current == null:
		return
	_timer = null
	var b := _current
	_current = null
	if is_instance_valid(b):
		if free_after:
			b.queue_free()
		else:
			b.visible = false
		finished.emit(b)
	if _queue.is_empty():
		return
	var e := Motion.entry(GAP_MOTION)
	var gap := e.duration if e != null else 0.0
	if gap > 0.0 and is_inside_tree():
		get_tree().create_timer(gap).timeout.connect(_next)
	else:
		_next()


## Drops every banner (the region is cleared; e.g. the page leaves).
func clear() -> void:
	for pair in _queue:
		var b: CanvasItem = pair[0]
		if is_instance_valid(b) and free_after:
			b.queue_free()
	_queue.clear()
	if _current != null and is_instance_valid(_current) and free_after:
		_current.queue_free()
	_current = null
	_timer = null


func _next() -> void:
	if _current != null:
		return
	while not _queue.is_empty():
		var pair: Array = _queue.pop_front()
		var b: CanvasItem = pair[0]
		if not is_instance_valid(b):
			continue
		_current = b
		b.visible = true
		shown.emit(b)
		if is_inside_tree():
			var t := get_tree().create_timer(float(pair[1]))
			_timer = t
			t.timeout.connect(func() -> void:
				if _timer == t:
					finish_current())
		return
