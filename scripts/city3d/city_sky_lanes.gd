class_name CitySkyLanes
extends RefCounted
## ART-5 5c: the sky lanes as baked paths (ART_BIBLE §4.2 "sky lanes v4", §6.1; round 26
## `roads.py`): the 16 road shapes (A's double deck, B's high deck, C with its flyover
## crossings and 1.75-turn spiral ramp, F's cloverleaf of four 270-degree loops with A, the
## four-level stack of D and E) laid on the city's own busiest avenues, plus the street
## traffic's avenues. Each road becomes one row per direction (a two-way road two rows,
## either side of its centre line; a ramp, loop or spiral one row), resampled uniformly by
## arc length into `bake_samples` world points: the cars' vertex shader reads the rows from
## `bake()`'s float texture (xyz = position, a = the row's length) and the tests read
## `sample()`, which interpolates exactly as the shader does. Pure data, deterministic.

## Road roles (round 26 names).
const ROAD_NAMES: Array[String] = ["A_low", "A_high", "B", "C", "C_spiral", "F", "clover_0", "clover_1", "clover_2",
	"clover_3", "D", "E", "stack_0", "stack_1", "stack_2", "stack_3"]
## Guide-dot colour per road (an index into the lane palette: 0 pink, 1 cyan, 2 amber,
## 3 violet, 4 mint, 5 orange; round 26's rails).
const ROAD_COLORS := {"A_low": 0, "A_high": 1, "B": 2, "C": 4, "C_spiral": 4, "F": 3, "clover": 3, "D": 5, "E": 1,
	"stack_tight": 2, "stack_wide": 0}

## Roads: {"name": String, "oneway": bool, "color": int, "rows": PackedInt32Array}.
var roads: Array[Dictionary] = []
## Sky rows: {"road": int, "points": PackedVector3Array (bake_samples, uniform by arc
## length), "length": float, "dir": +1 forward / -1 the reverse direction}.
var rows: Array[Dictionary] = []
## Street rows (the street traffic, two-way avenues at street height), the same shape.
var street_rows: Array[Dictionary] = []
var samples: int = 512


## The sky lanes and street rows on `site`.
static func build(cfg: CityMotionConfigData, site: CityMotionSite) -> CitySkyLanes:
	var l := CitySkyLanes.new()
	l.samples = cfg.bake_samples
	var picks := pick_avenues(cfg, site)
	var hz: Array = picks["h"]
	var vt: Array = picks["v"]
	# A: double deck on the busiest horizontal avenue; F: the busiest vertical, cloverleaf.
	if hz.size() > 0:
		var a: Dictionary = hz[0]
		l._straight(cfg, site, "A_low", a["a"], a["b"], cfg.deck_a_low, false, 0.0)
		l._straight(cfg, site, "A_high", a["a"], a["b"], cfg.deck_a_high, false, cfg.ramp_lots)
	if vt.size() > 0:
		l._straight(cfg, site, "F", vt[0]["a"], vt[0]["b"], cfg.deck_f, false, 0.0)
	if hz.size() > 0 and vt.size() > 0:
		var x := crossing(hz[0], vt[0], cfg.clover_radius * 2.0 + 1.0)
		if x != Vector2.INF:
			for q in 4:
				var sq: Vector2 = [Vector2(1, 1), Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1)][q]
				l._loop(cfg, site, "clover_%d" % q, x, sq, cfg.clover_radius, cfg.deck_a_low, cfg.deck_f, true)
	# B: the second vertical, high deck; C: the second horizontal under B and F, then its spiral.
	if vt.size() > 1:
		l._straight(cfg, site, "B", vt[1]["a"], vt[1]["b"], cfg.deck_b, false, 0.0)
	if hz.size() > 1:
		var c: Dictionary = hz[1]
		var ca: Vector2 = c["a"]
		var cb: Vector2 = c["b"]
		var end := cb - (cb - ca).normalized() * (cfg.spiral_radius + 1.0)
		l._straight(cfg, site, "C", ca, end, cfg.deck_c, true, 0.0)
		l._spiral(cfg, site, end, (end - ca).normalized())
	# D and E: the third of each, crossing in the four-level stack.
	if hz.size() > 2:
		l._straight(cfg, site, "D", hz[2]["a"], hz[2]["b"], cfg.deck_d, false, 0.0)
	if vt.size() > 2:
		l._straight(cfg, site, "E", vt[2]["a"], vt[2]["b"], cfg.deck_e, false, 0.0)
	if hz.size() > 2 and vt.size() > 2:
		var x := crossing(hz[2], vt[2], cfg.stack_wide_radius * 2.0 + 1.0)
		if x != Vector2.INF:
			for q in 4:
				var sq: Vector2 = [Vector2(1, 1), Vector2(-1, -1), Vector2(1, -1), Vector2(-1, 1)][q]
				var tight := q < 2
				l._quarter(cfg, site, "stack_%d" % q, x, sq, cfg.stack_tight_radius if tight else cfg.stack_wide_radius,
					cfg.deck_d, cfg.deck_e, cfg.stack_tight_peak if tight else cfg.stack_wide_peak, tight)
	# Street traffic: every avenue busy enough, both ways at street height.
	for av in site.avenues:
		if float(av["traffic"]) >= cfg.street_min_traffic:
			var pts := l._line_pts(cfg, site, av["a"], av["b"], func(_u: float) -> float: return cfg.street_height)
			l._add_rows(cfg, l.street_rows, -1, pts, false)
	return l


## The avenues the roads go on: {"h": horizontal (axis 1), "v": vertical (axis 0)}, each
## busiest first, at least `road_min_span` lots long and `road_min_spacing` lots from a
## parallel pick (ties: the site's order, which breaks them by axis then line).
static func pick_avenues(cfg: CityMotionConfigData, site: CityMotionSite) -> Dictionary:
	var out := {"h": [], "v": []}
	for av in site.avenues:
		var span := (av["a"] as Vector2).distance_to(av["b"])
		if span < cfg.road_min_span:
			continue
		var key := "h" if int(av["axis"]) == 1 else "v"
		var list: Array = out[key]
		if list.size() >= 3:
			continue
		var ok := true
		for p: Dictionary in list:
			if absi(int(p["line"]) - int(av["line"])) < cfg.road_min_spacing:
				ok = false
		if ok:
			list.append(av)
	return out


## Where horizontal avenue `h` and vertical `v` cross (lots), at least `margin` lots inside
## both, or Vector2.INF.
static func crossing(h: Dictionary, v: Dictionary, margin: float) -> Vector2:
	var y := float((h["a"] as Vector2).y)
	var x := float((v["a"] as Vector2).x)
	var hx0 := minf(h["a"].x, h["b"].x)
	var hx1 := maxf(h["a"].x, h["b"].x)
	var vy0 := minf(v["a"].y, v["b"].y)
	var vy1 := maxf(v["a"].y, v["b"].y)
	if x < hx0 + margin or x > hx1 - margin or y < vy0 + margin or y > vy1 - margin:
		return Vector2.INF
	return Vector2(x, y)


## World position on row `row` (of `list`, the sky rows by default) at share `s` (0..1),
## interpolated between baked samples as the shader does.
func sample(row: int, s: float, list: Array[Dictionary] = []) -> Vector3:
	var r: Dictionary = (rows if list.is_empty() else list)[row]
	var pts: PackedVector3Array = r["points"]
	var f := clampf(s, 0.0, 1.0) * float(pts.size() - 1)
	var i := mini(int(floor(f)), pts.size() - 2)
	return pts[i].lerp(pts[i + 1], f - float(i))


## The rows of `list` (the sky rows by default) as an RGBAF image: one texel row per lane
## row, `samples` texels each (xyz = world position, a = the row's length in BU).
func bake(list: Array[Dictionary] = []) -> Image:
	var src: Array[Dictionary] = rows if list.is_empty() else list
	var img := Image.create_empty(samples, maxi(1, src.size()), false, Image.FORMAT_RGBAF)
	for y in src.size():
		var pts: PackedVector3Array = src[y]["points"]
		var ln := float(src[y]["length"])
		for x in samples:
			var p := pts[x]
			img.set_pixel(x, y, Color(p.x, p.y, p.z, ln))
	return img


## The guide dots (round 26 v3): world positions and palette indices, every
## `guide_spacing` BU; a two-way road gets a row along each edge, a one-way ramp one row
## down its centre.
func guide_dots(cfg: CityMotionConfigData) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for rd in roads:
		var rr: PackedInt32Array = rd["rows"]
		for k in rr.size():
			var r: Dictionary = rows[rr[k]]
			var n := maxi(1, int(float(r["length"]) / cfg.guide_spacing))
			var edge := 0.0 if bool(rd["oneway"]) else cfg.lane_side
			for i in n + 1:
				var s := float(i) / float(n)
				var p := sample(rr[k], s)
				if edge > 0.0:
					var t := sample(rr[k], minf(1.0, s + 0.01)) - sample(rr[k], maxf(0.0, s - 0.01))
					var side := Vector3(-t.z, 0.0, t.x).normalized()
					p += side * edge * 0.6
				out.append({"pos": p, "color": int(rd["color"])})
	return out


## Every sky row's points, for bounds.
func aabb() -> AABB:
	var box := AABB()
	var first := true
	for list: Array[Dictionary] in [rows, street_rows]:
		for r in list:
			for p: Vector3 in r["points"]:
				if first:
					box = AABB(p, Vector3.ZERO)
					first = false
				else:
					box = box.expand(p)
	return box.grow(4.0)


func _color_of(name: String, tight: bool = false) -> int:
	if name.begins_with("clover"):
		return ROAD_COLORS["clover"]
	if name.begins_with("stack"):
		return ROAD_COLORS["stack_tight" if tight else "stack_wide"]
	return ROAD_COLORS.get(name, 0)


## A straight road from `a` to `b` (lots) at deck `e`, ramping down at both ends (the far
## end only from `trim_far` lots short of `b`; `flat_end` keeps the far end at deck height).
func _straight(cfg: CityMotionConfigData, site: CityMotionSite, name: String, a: Vector2, b: Vector2, e: float,
		flat_end: bool, trim_far: float) -> void:
	var span := a.distance_to(b)
	var bb := b - (b - a).normalized() * trim_far
	var len_ := a.distance_to(bb)
	var rl := cfg.ramp_lots
	var fl := cfg.ramp_floor
	var elev := func(u: float) -> float:
		var d0 := u * len_
		var d1 := (1.0 - u) * len_
		var v := e
		if d0 < rl:
			v = lerpf(fl, e, smoothstep(0.0, 1.0, d0 / rl))
		if not flat_end and d1 < rl:
			v = minf(v, lerpf(fl, e, smoothstep(0.0, 1.0, d1 / rl)))
		return v
	if span <= 0.0:
		return
	var pts := _line_pts(cfg, site, a, bb, elev)
	_add_road(cfg, name, pts, false, _color_of(name))


## Lot points from `a` to `b` every path step, at elevation elev.call(u).
func _line_pts(cfg: CityMotionConfigData, site: CityMotionSite, a: Vector2, b: Vector2, elev: Callable) -> PackedVector3Array:
	var n := maxi(2, int(ceil(a.distance_to(b) / cfg.path_step_lots)) + 1)
	var pts := PackedVector3Array()
	for k in n:
		var u := float(k) / float(n - 1)
		pts.append(site.lot_to_world(a.lerp(b, u), float(elev.call(u))))
	return pts


## C's spiral ramp: from `start` (heading `dir`), `spiral_turns` turns round a column,
## down to `spiral_floor`, one way.
func _spiral(cfg: CityMotionConfigData, site: CityMotionSite, start: Vector2, dir: Vector2) -> void:
	var nrm := Vector2(-dir.y, dir.x)
	var r := cfg.spiral_radius
	var centre := start + nrm * r
	var a0 := (start - centre).angle()
	# Turning toward the centre keeps the heading continuous (+ when the centre is on the left).
	var sweep := cfg.spiral_turns * TAU * (1.0 if dir.cross(nrm) > 0.0 else -1.0)
	var n := maxi(8, int(absf(sweep) * r / cfg.path_step_lots))
	var pts := PackedVector3Array()
	for k in n + 1:
		var u := float(k) / float(n)
		var ang := a0 + sweep * u
		pts.append(site.lot_to_world(centre + Vector2(cos(ang), sin(ang)) * r, lerpf(cfg.deck_c, cfg.spiral_floor, u)))
	_add_road(cfg, "C_spiral", pts, true, _color_of("C_spiral"))


## A cloverleaf loop in quadrant `sq` of crossing `x`: 270 degrees (the long way), tangent
## to both avenues, from height e0 to e1 (round 26 `loop_ramp`).
func _loop(cfg: CityMotionConfigData, site: CityMotionSite, name: String, x: Vector2, sq: Vector2, r: float, e0: float,
		e1: float, long_way: bool) -> void:
	var c := x + sq * r
	var a0 := atan2(-sq.y, 0.0)
	var a1 := atan2(0.0, -sq.x)
	var d := fposmod(a1 - a0, TAU)
	if long_way and d < PI:
		d -= TAU
	elif not long_way and d > PI:
		d -= TAU
	var n := maxi(8, int(absf(d) * r / cfg.path_step_lots))
	var pts := PackedVector3Array()
	for k in n + 1:
		var u := float(k) / float(n)
		var ang := a0 + d * u
		pts.append(site.lot_to_world(c + Vector2(cos(ang), sin(ang)) * r, lerpf(e0, e1, smoothstep(0.0, 1.0, u))))
	_add_road(cfg, name, pts, true, _color_of(name))


## A stack's directional flyover (round 26 `quarter_ramp`): 90 degrees through quadrant
## `sq`, from e0 to e1 rising to about `peak` in the middle.
func _quarter(cfg: CityMotionConfigData, site: CityMotionSite, name: String, x: Vector2, sq: Vector2, r: float, e0: float,
		e1: float, peak: float, tight: bool) -> void:
	var c := x + sq * r
	var a0 := atan2(-sq.y, 0.0)
	var a1 := atan2(0.0, -sq.x)
	var d := fposmod(a1 - a0, TAU)
	if d > PI:
		d -= TAU
	var n := maxi(8, int(absf(d) * r / cfg.path_step_lots) * 2)
	var pts := PackedVector3Array()
	for k in n + 1:
		var u := float(k) / float(n)
		var ang := a0 + d * u
		var base := lerpf(e0, e1, smoothstep(0.0, 1.0, u))
		pts.append(site.lot_to_world(c + Vector2(cos(ang), sin(ang)) * r, base + (peak - maxf(e0, e1)) * sin(PI * u)))
	_add_road(cfg, name, pts, true, _color_of(name, tight))


func _add_road(cfg: CityMotionConfigData, name: String, pts: PackedVector3Array, oneway: bool, color: int) -> void:
	var idx := roads.size()
	var first := rows.size()
	_add_rows(cfg, rows, idx, pts, oneway)
	var rr := PackedInt32Array()
	for k in range(first, rows.size()):
		rr.append(k)
	roads.append({"name": name, "oneway": oneway, "color": color, "rows": rr})


## Resamples centre line `pts` and appends its rows to `into` (one for a one-way road; two
## for a two-way one, `lane_side` either side, the second reversed).
func _add_rows(cfg: CityMotionConfigData, into: Array[Dictionary], road: int, pts: PackedVector3Array, oneway: bool) -> void:
	if pts.size() < 2:
		return
	if oneway:
		into.append(_resampled(road, pts, 0.0, 1))
	else:
		into.append(_resampled(road, pts, cfg.lane_side, 1))
		var rev := pts.duplicate()
		rev.reverse()
		into.append(_resampled(road, rev, cfg.lane_side, -1))


## `pts` offset `side` BU to its right (horizontally) and resampled into `samples` points
## uniform by arc length.
func _resampled(road: int, pts: PackedVector3Array, side: float, dir: int) -> Dictionary:
	var src := PackedVector3Array()
	for k in pts.size():
		var t := pts[mini(k + 1, pts.size() - 1)] - pts[maxi(k - 1, 0)]
		var right := Vector3(-t.z, 0.0, t.x).normalized()
		src.append(pts[k] + right * side)
	var cum := PackedFloat32Array([0.0])
	for k in range(1, src.size()):
		cum.append(cum[k - 1] + src[k].distance_to(src[k - 1]))
	var total := cum[cum.size() - 1]
	var out := PackedVector3Array()
	var j := 0
	for i in samples:
		var d := total * float(i) / float(samples - 1)
		while j < src.size() - 2 and cum[j + 1] < d:
			j += 1
		var seg := maxf(cum[j + 1] - cum[j], 0.000001)
		out.append(src[j].lerp(src[j + 1], clampf((d - cum[j]) / seg, 0.0, 1.0)))
	return {"road": road, "points": out, "length": total, "dir": dir}
