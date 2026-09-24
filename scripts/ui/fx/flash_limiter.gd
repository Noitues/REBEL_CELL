class_name FlashLimiter
extends RefCounted
## Flash limiter (GDD 9.6, STYLE_GUIDE 6): never more than `max_per_second` flashes in
## any rolling one-second window. Pure: feed it timestamps (seconds) and it says whether
## a flash may show. Views and the automated event-stream check both use this.

const WINDOW_SECONDS := 1.0

var max_per_second: int = 3
var enabled: bool = true
var _times: Array[float] = []
var allowed_count: int = 0
var suppressed_count: int = 0


func _init(p_max_per_second: int = 3) -> void:
	max_per_second = p_max_per_second


## True when a flash at time `now` (seconds) may be shown; records it if so.
func request(now: float) -> bool:
	if not enabled:
		allowed_count += 1
		return true
	_prune(now)
	if _times.size() >= max_per_second:
		suppressed_count += 1
		return false
	_times.append(now)
	allowed_count += 1
	return true


func reset() -> void:
	_times.clear()
	allowed_count = 0
	suppressed_count = 0


func _prune(now: float) -> void:
	while not _times.is_empty() and now - _times[0] >= WINDOW_SECONDS:
		_times.pop_front()


## Checks a list of flash timestamps: true when no rolling one-second window holds more
## than `max_per_second` of them (the automated acceptance check).
static func stream_is_safe(times: Array[float], p_max_per_second: int = 3) -> bool:
	var sorted := times.duplicate()
	sorted.sort()
	for i in sorted.size():
		var count := 0
		for j in range(i, sorted.size()):
			if sorted[j] - sorted[i] < WINDOW_SECONDS:
				count += 1
			else:
				break
		if count > p_max_per_second:
			return false
	return true


## Event types that would flash the screen (Perfect latch, boss phase, Heat threshold,
## Miss static burst is not a flash).
const FLASH_EVENT_TYPES := ["retrigger", "boss_phase", "heat_threshold", "combat_end", "zero_day"]


## Filters a combat/campaign event stream through a limiter, returning the timestamps of
## the flashes that would actually be shown. `seconds_per_event` spaces the events.
static func filter_event_stream(events: Array[Dictionary], seconds_per_event: float, p_max_per_second: int = 3) -> Array[float]:
	var limiter := FlashLimiter.new(p_max_per_second)
	var shown: Array[float] = []
	for i in events.size():
		if FLASH_EVENT_TYPES.has(String(events[i].get("type", ""))):
			var t := i * seconds_per_event
			if limiter.request(t):
				shown.append(t)
	return shown
