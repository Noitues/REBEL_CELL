class_name CityMotionClock
extends RefCounted
## ART-5 5c: when the city's ambient layers move (ART_BIBLE §5.4, §6.1; STYLE_GUIDE 5.1).
## Each layer keeps its own time, advanced by `rate()` every frame:
## - paused (the map is covered or the window has lost focus): every layer stops where it
##   is (rate 0, its look kept);
## - not live (reduce effects, a headless display or its motion entry switched off): the
##   layer shows its end state at once and holds it (time 0, steady: lights on and still,
##   one billboard panel, searchlights at rest, aircraft parked);
## - reduce motion (bible 5.4): street traffic keeps moving at the config's
##   `reduce_motion_street_rate` (40 %) without streaks; every other layer pauses in its
##   steady look (no blink, sweep or orbit); the sky lanes show their markers without cars
##   (ART-5 5e: the art pass's rule replaces 5c's "street traffic pauses").
## Pure and deterministic: a test steps it with fixed deltas.

enum Layer { SKY_CARS, STREET_CARS, BILLBOARDS, AVIATION, SEARCHLIGHTS, CHOPPERS, DRONES, STROBES, ALARMS, NODE_LIGHTS }
const COUNT := 10

var times: PackedFloat64Array = PackedFloat64Array()


func _init() -> void:
	times.resize(COUNT)
	times.fill(0.0)


## The rate (seconds of layer time per second) of `layer`.
static func rate(cfg: CityMotionConfigData, layer: int, paused: bool, reduce_motion: bool, live: bool) -> float:
	if paused or not live:
		return 0.0
	if reduce_motion:
		return cfg.reduce_motion_street_rate if layer == Layer.STREET_CARS and cfg != null else 0.0
	return 1.0


## True when `layer` shows its still, steady look (lights on, nothing turning).
static func steady(_layer: int, reduce_motion: bool, live: bool) -> bool:
	return not live or reduce_motion


## True when the sky-lane cars draw at all: not under reduce motion (markers only) and
## not in the netrun transit (bible 4.1).
static func sky_cars_shown(reduce_motion: bool, netrun_view: bool) -> bool:
	return not reduce_motion and not netrun_view


## True when street cars draw their streaks (none under reduce motion).
static func street_streaks(reduce_motion: bool) -> bool:
	return not reduce_motion


## Advances every layer by `delta`; a layer that is not live goes back to its end state
## (time 0). `live` and `rates` are per layer.
func advance(delta: float, rates: PackedFloat64Array, live: Array[bool]) -> void:
	for k in COUNT:
		if not live[k]:
			times[k] = 0.0
		else:
			times[k] += delta * rates[k]
