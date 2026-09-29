class_name HubQueue
extends Node
## Art pass W3 (ART_BIBLE §6.1, §6.6): one stamp at a time in a wheel's hub. PHASE, NO DAMAGE,
## ALL BLOCKED and the like queue instead of stacking (critique 44/45: three layers of words
## in one hub). The equivalent of W2's BannerQueue for stamps the effects layer draws (they
## are sprites with a delay, not nodes): `book` returns when a stamp may start in a hub (after
## the stamp before it and `banner_gap`, and after any number resting in that hub, whose own
## timing is the replay's and never moves: `note`), and keeps the hub until it is done.
## Its clock is game time (it follows the resolve speed). View only.

## The hub's bookings: hub key -> the game time (s) it is free again.
var _free_at: Dictionary = {}
## Game seconds since the queue started (advanced while anything is booked).
var clock: float = 0.0


func _init() -> void:
	name = "HubQueue"
	set_process(false)


func _process(delta: float) -> void:
	clock += delta
	for k in _free_at.keys():
		if float(_free_at[k]) <= clock:
			_free_at.erase(k)
	if _free_at.is_empty():
		set_process(false)


## Books hub `key` for a stamp that wants to start `delay` s from now and shows for `seconds`:
## returns the delay (s from now) it may start at, never while another stamp or a resting
## number holds that hub.
func book(key: Variant, delay: float, seconds: float) -> float:
	var want := clock + maxf(0.0, delay)
	var free := float(_free_at.get(key, -INF))
	var start := want if free <= want else free + gap()
	_free_at[key] = start + seconds
	set_process(true)
	return start - clock


## A number rests in hub `key` from `delay` s from now for `seconds`: a stamp booked later
## waits for it (the number keeps its time).
func note(key: Variant, delay: float, seconds: float) -> void:
	var until := clock + maxf(0.0, delay) + seconds
	_free_at[key] = maxf(float(_free_at.get(key, -INF)), until)
	set_process(true)


## When hub `key` is free again (s from now; 0 when it is free).
func free_in(key: Variant) -> float:
	return maxf(0.0, float(_free_at.get(key, -INF)) - clock)


## Drops every booking (a skip: the end state has no stamp in any hub).
func clear() -> void:
	_free_at.clear()
	set_process(false)


## The gap between two stamps in one hub (W2's `banner_gap`).
static func gap() -> float:
	return Motion.seconds(BannerQueue.GAP_MOTION) if Motion.has(BannerQueue.GAP_MOTION) else 0.0
