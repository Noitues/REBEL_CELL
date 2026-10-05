class_name CitySkyTraffic
extends RefCounted
## ART-5 5c: the cars on the sky lanes and the streets (ART_BIBLE §4.1 car LOD, §4.2 sky lanes
## v4, §6.1). Each lane row carries cars spaced evenly (about `car_gap` apart, some slots
## skipped); each sky row moves a whole number of gaps (14-20) per loop so the loop is
## seamless; every car picks one of the six lane colours and its speed-line length from the
## seeded `city_traffic` stream (RngStreams.make_stream: derived from the city's seed, never
## the campaign's own streams, so a view never moves game state). A car's share along its
## row at time t is fract(phase + t * speed); the shader does the same on the GPU.

const STREAM := &"city_traffic"

enum CarTier { FAR, MEDIUM, CLOSE }

## Sky cars: {"row": int, "phase": 0-1, "speed": row shares per second, "color": int (lane
## palette), "streak": float (BU)}. Street cars: the same, plus "tail": true for the cars
## showing their tail lights at night (the reverse direction of a street).
var cars: Array[Dictionary] = []
var street_cars: Array[Dictionary] = []


## The cars on `lanes`, seeded by `seed`; one loop takes `loop_s` seconds (the
## `sky_lane_cars` motion's period) and a street car crosses a lot in `lot_s` seconds (the
## `street_cars` motion's).
static func build(cfg: CityMotionConfigData, lanes: CitySkyLanes, seed: int, loop_s: float, lot_s: float,
		lot_bu: float) -> CitySkyTraffic:
	var t := CitySkyTraffic.new()
	var rng := RngStreams.make_stream(seed, STREAM)
	var loop := maxf(loop_s, 0.01)
	for r in lanes.rows.size():
		var ln := float(lanes.rows[r]["length"])
		var n := maxi(1, roundi(ln / cfg.car_gap))
		var gaps := rng.randi_range(cfg.gaps_per_loop.x, cfg.gaps_per_loop.y)
		var speed := float(gaps) / float(n) / loop
		var off := rng.randf()
		for c in n:
			# Draw every value for every slot so a skip never shifts the next car's colour.
			var skip := rng.randf() < cfg.car_skip
			var col := rng.randi_range(0, cfg.lane_colors.size() - 1)
			var streak := rng.randf_range(cfg.streak_length.x, cfg.streak_length.y)
			if skip:
				continue
			t.cars.append({"row": r, "phase": fposmod((float(c) + off) / float(n), 1.0), "speed": speed, "color": col,
				"streak": streak})
	var bu_s := lot_bu / maxf(lot_s, 0.01)
	for r in lanes.street_rows.size():
		var ln := float(lanes.street_rows[r]["length"])
		var n := maxi(1, roundi(ln / cfg.street_gap))
		var off := rng.randf()
		var tail := int(lanes.street_rows[r]["dir"]) < 0
		for c in n:
			var skip := rng.randf() < cfg.car_skip
			var jitter := rng.randf_range(-cfg.street_jitter, cfg.street_jitter)
			var col := rng.randi_range(0, cfg.lane_colors.size() - 1)
			if skip:
				continue
			t.street_cars.append({"row": r, "phase": fposmod((float(c) + off + jitter) / float(n), 1.0), "speed": bu_s / ln,
				"color": col, "streak": cfg.street_streak, "tail": tail})
	return t


## World position of sky car `c` at time `time` (s).
func position_at(lanes: CitySkyLanes, c: int, time: float) -> Vector3:
	var car: Dictionary = cars[c]
	return lanes.sample(int(car["row"]), share_at(car, time))


## Share along its row of `car` at time `time`.
static func share_at(car: Dictionary, time: float) -> float:
	return fposmod(float(car["phase"]) + time * float(car["speed"]), 1.0)


## The car tier at `ortho` (bible 4.1: FAR above `car_far_above`, CLOSE below
## `car_close_below`), staying on `current` (-1 = none yet) until the zoom is past that
## tier's edge by the hysteresis share.
static func car_tier(cfg: CityMotionConfigData, ortho: float, current: int = -1) -> int:
	var h := cfg.lod_hysteresis
	var raw := CarTier.MEDIUM
	if ortho > cfg.car_far_above:
		raw = CarTier.FAR
	elif ortho < cfg.car_close_below:
		raw = CarTier.CLOSE
	if current < 0 or current == raw:
		return raw
	match current:
		CarTier.FAR:
			if ortho > cfg.car_far_above * (1.0 - h):
				return CarTier.FAR
		CarTier.CLOSE:
			if ortho < cfg.car_close_below * (1.0 + h):
				return CarTier.CLOSE
		CarTier.MEDIUM:
			if ortho <= cfg.car_far_above * (1.0 + h) and ortho >= cfg.car_close_below * (1.0 - h):
				return CarTier.MEDIUM
	return raw
