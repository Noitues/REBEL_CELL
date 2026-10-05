class_name CityTraffic
extends RefCounted
## ART-1 1D: the unified city's traffic as data (bible §4.2 sky lanes v4, §6.1). Sky lanes
## run over the district's busiest avenues (the game's own street lines), one height per
## lane, both directions; cars are spaced `car_gap` apart, some gaps skipped, each car's
## lane colour from a seeded RngStreams stream. A car's position at time t is
## start + dir * fract(phase + t * speed) * length (the renderers move it in a shader; the
## tests read `position_at`).

const STREAM := &"city_traffic"

## Lanes: {"a": Vector3, "b": Vector3 (world, at height), "side": Vector3}.
var lanes: Array[Dictionary] = []
## Cars: {"lane": int, "dir": +1/-1, "phase": 0-1, "speed": loops per second along the
## lane, "length": BU, "color": Color}.
var cars: Array[Dictionary] = []


## Lanes and cars for district `d`, seeded by `seed`.
static func build(cfg: CitySpikeConfig, d: CityDistrict, seed: int) -> CityTraffic:
	var t := CityTraffic.new()
	var lines := avenue_lines(d)
	var rng := RngStreams.make_stream(seed, STREAM)
	for k in mini(cfg.sky_lane_heights.size(), lines.size()):
		var ln: Dictionary = lines[k]
		var hgt := cfg.sky_lane_heights[k]
		var a := CityIsoCamera.lot_to_world(cfg, ln["a"], hgt)
		var b := CityIsoCamera.lot_to_world(cfg, ln["b"], hgt)
		var dir := (b - a).normalized()
		t.lanes.append({"a": a, "b": b, "side": Vector3(-dir.z, 0, dir.x) * cfg.sky_lane_side})
		var length := a.distance_to(b)
		var n := int(length / cfg.car_gap)
		# Gaps per loop: a car travels car_speed_gaps gaps per car_loop_s.
		var speed := cfg.car_speed_gaps * cfg.car_gap / cfg.car_loop_s / maxf(1.0, length)
		for side in [-1, 1]:
			var off := rng.randf()
			for c in n:
				var skip := rng.randf() < cfg.car_skip
				var col := cfg.lane_colors[rng.randi_range(0, cfg.lane_colors.size() - 1)]
				var cl := rng.randf_range(cfg.car_length.x, cfg.car_length.y)
				if skip:
					continue
				t.cars.append({"lane": k, "dir": side, "phase": fposmod((off + c) / float(n), 1.0), "speed": speed,
					"length": cl, "color": col})
	return t


## The district's avenue lines, busiest first (ties by axis, then line): {"axis": 0/1,
## "line": int, "a": Vector2, "b": Vector2 (lot points along the line's centre),
## "traffic": mean traffic}.
static func avenue_lines(d: CityDistrict) -> Array[Dictionary]:
	var acc := {}
	for s in d.streets:
		if s["along_i"] == s["along_j"]:
			continue
		var l: Vector2i = s["lot"]
		var axis := 0 if s["along_i"] else 1
		var line := l.x if axis == 0 else l.y
		var along := l.y if axis == 0 else l.x
		var key := Vector2i(axis, line)
		if not acc.has(key):
			acc[key] = {"axis": axis, "line": line, "lo": along, "hi": along, "sum": 0.0, "n": 0}
		var e: Dictionary = acc[key]
		e["lo"] = mini(e["lo"], along)
		e["hi"] = maxi(e["hi"], along)
		e["sum"] = float(e["sum"]) + float(s["traffic"])
		e["n"] = int(e["n"]) + 1
	var out: Array[Dictionary] = []
	for key: Vector2i in acc:
		var e: Dictionary = acc[key]
		var c := float(e["line"]) + 0.5
		var a := Vector2(c, e["lo"]) if e["axis"] == 0 else Vector2(e["lo"], c)
		var b := Vector2(c, int(e["hi"]) + 1) if e["axis"] == 0 else Vector2(int(e["hi"]) + 1, c)
		out.append({"axis": e["axis"], "line": e["line"], "a": a, "b": b, "traffic": float(e["sum"]) / int(e["n"]),
			"n": e["n"]})
	out.sort_custom(func(x: Dictionary, y: Dictionary) -> bool:
		var tx: float = float(x["traffic"]) * int(x["n"])
		var ty: float = float(y["traffic"]) * int(y["n"])
		if tx != ty:
			return tx > ty
		if x["axis"] != y["axis"]:
			return x["axis"] < y["axis"]
		return x["line"] < y["line"])
	return out


## World position of car `c` at time `time` (s).
func position_at(c: int, time: float) -> Vector3:
	var car: Dictionary = cars[c]
	var ln: Dictionary = lanes[car["lane"]]
	var a: Vector3 = ln["a"]
	var b: Vector3 = ln["b"]
	var s := fposmod(float(car["phase"]) + time * float(car["speed"]), 1.0)
	if int(car["dir"]) < 0:
		s = 1.0 - s
	return a.lerp(b, s) + (ln["side"] as Vector3) * float(car["dir"])
