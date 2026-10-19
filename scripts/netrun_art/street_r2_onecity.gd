class_name StreetR2OneCity
extends RefCounted
## Street r2 one-city helpers (twin of `tools/netrun_art/r2/onecity.py`): lot -> BU, building info, merged buildings, frontage rows and the
## perspective projection of the plate's cameras. Pure functions of the data passed in; the numbers come from `StreetR2ConfigData`.

const GRID := 16.0     # BU per cell of the containment index (an acceleration only: the first containing base in list order still wins)

static var _c: Dictionary = {}


static func _cfg() -> Dictionary:
	if _c.is_empty():
		_c = StreetR2ConfigData.shipped().onecity
	return _c


## Lot size in BU.
static func lot_u() -> float:
	return float(_cfg()["u"])


## The height factor of a lot-height unit: `u / kh[0] * kh[1]`.
static func kh() -> float:
	return lot_u() / float(_cfg()["kh"][0]) * float(_cfg()["kh"][1])


## BU per storey.
static func floor_bu() -> float:
	return float(_cfg()["floor_bu"])


## Frame width in px.
static func frame_w() -> float:
	return float(_cfg()["w"])


## Frame height in px.
static func frame_h() -> float:
	return float(_cfg()["h"])


## A lot point in BU (y flipped).
static func w_of(p: Array) -> Array:
	return [(float(p[0]) - float(_cfg()["cx"])) * lot_u(), -(float(p[1]) - float(_cfg()["cy"])) * lot_u()]


## BU record of a raw lot building (`ci`, `key`, `q` in lots, `z0`, `h` in lot-height units, `ts`).
static func bld_info(b: Dictionary) -> Dictionary:
	var q: Array = []
	for p: Array in b["q"]:
		q.append(w_of(p))
	var xs: Array = []
	var ys: Array = []
	for p: Array in q:
		xs.append(p[0])
		ys.append(p[1])
	var k := kh()
	return {"key": b["key"], "uid": "%d_%d" % [b["ci"], b["key"]], "q": q, "x0": StreetR2Util.amin(xs), "x1": StreetR2Util.amax(xs),
		"y0": StreetR2Util.amin(ys), "y1": StreetR2Util.amax(ys), "z0": float(b["z0"]) * k, "h": float(b["h"]) * k, "ts": b["ts"]}


## Street-level bases with their stacked parts merged in (height = top of the highest part).
static func merged_buildings(buildings: Array) -> Array:
	var bases: Array = []
	var ups: Array = []
	for raw: Dictionary in buildings:
		var b := bld_info(raw)
		if float(b["z0"]) <= 0.05:
			bases.append(b)
		else:
			ups.append(b)
	var grid := {}
	for i in bases.size():
		var b: Dictionary = bases[i]
		b["top"] = b["h"]
		b["parts"] = [b["key"]]
		b["parts_uid"] = [b["uid"]]
		for ix in range(int(floorf(float(b["x0"]) / GRID)), int(floorf(float(b["x1"]) / GRID)) + 1):
			for iy in range(int(floorf(float(b["y0"]) / GRID)), int(floorf(float(b["y1"]) / GRID)) + 1):
				var key := Vector2i(ix, iy)
				if not grid.has(key):
					grid[key] = []
				(grid[key] as Array).append(i)
	for u: Dictionary in ups:
		var cx := (float(u["x0"]) + float(u["x1"])) / 2
		var cy := (float(u["y0"]) + float(u["y1"])) / 2
		var cell := Vector2i(int(floorf(cx / GRID)), int(floorf(cy / GRID)))
		for i: int in grid.get(cell, []):
			var b: Dictionary = bases[i]
			if float(b["x0"]) <= cx and cx <= float(b["x1"]) and float(b["y0"]) <= cy and cy <= float(b["y1"]):
				b["top"] = maxf(float(b["top"]), float(u["z0"]) + float(u["h"]))
				(b["parts"] as Array).append(u["key"])
				(b["parts_uid"] as Array).append(u["uid"])
				break
	for b: Dictionary in bases:
		b["h"] = b["top"]
	return bases


## Buildings fronting the leg a -> c on `side` (+1 = left of the walking direction), ordered from a.
static func frontage(bs: Array, a: Array, c: Array, side: int) -> Array:
	var ax := 0 if absf(float(a[1]) - float(c[1])) < 1e-6 else 1
	var d := 1 if float(c[ax]) > float(a[ax]) else -1
	var lo := minf(float(a[ax]), float(c[ax]))
	var hi := maxf(float(a[ax]), float(c[ax]))
	var nrm: Array = [0.0, side * d] if ax == 0 else [-side * d, 0.0]
	var fb: Array = _cfg()["front_band"]
	var out: Array = []
	for b: Dictionary in bs:
		if float(b["z0"]) > 0.05:
			continue
		var a0: float
		var a1: float
		var near: float
		var dist: float
		if ax == 0:
			a0 = b["x0"]
			a1 = b["x1"]
			near = b["y0"] if float(nrm[1]) > 0 else b["y1"]
			dist = (near - float(a[1])) * float(nrm[1])
		else:
			a0 = b["y0"]
			a1 = b["y1"]
			near = b["x0"] if float(nrm[0]) > 0 else b["x1"]
			dist = (near - float(a[0])) * float(nrm[0])
		if a1 > lo and a0 < hi and float(fb[0]) < dist and dist < float(fb[1]) and a1 - a0 >= float(_cfg()["min_width"]):
			var mid := (a0 + a1) / 2
			var r: Dictionary = b.duplicate()
			r["along"] = (mid - float(a[ax])) * d
			r["face"] = near
			r["nrm"] = nrm
			r["axis"] = ax
			r["dirn"] = d
			out.append(r)
	return StreetR2Util.sorted_by(out, func(x: Dictionary, y: Dictionary) -> bool:
		return StreetR2Util.tuple_less([x["along"], x["key"]], [y["along"], y["key"]]))


## Camera right / up / forward vectors (layout36 basis); `c` has `yaw`, `pitch` in degrees.
static func basis(c: Dictionary) -> Array:
	var yw := deg_to_rad(float(c["yaw"]))
	var pt := deg_to_rad(float(c["pitch"]))
	var fwd: Array = [cos(yw) * cos(pt), sin(yw) * cos(pt), -sin(pt)]
	var right: Array = [sin(yw), -cos(yw), 0.0]
	var up: Array = [right[1] * fwd[2] - right[2] * fwd[1], right[2] * fwd[0] - right[0] * fwd[2], right[0] * fwd[1] - right[1] * fwd[0]]
	return [right, up, fwd]


## Pixel of a world point under the perspective camera `c` (`persp`: loc, lens, sx, sy) in a w x h frame.
static func project(c: Dictionary, x: float, y: float, z: float, w: float, h: float) -> Array:
	var bs := basis(c)
	var r: Array = bs[0]
	var u: Array = bs[1]
	var f: Array = bs[2]
	var persp: Dictionary = c["persp"]
	var lo: Array = persp["loc"]
	var d: Array = [x - float(lo[0]), y - float(lo[1]), z - float(lo[2])]
	var zc := maxf(1e-3, d[0] * f[0] + d[1] * f[1] + d[2] * f[2])
	var k := float(persp["lens"]) / 36.0
	var xc: float = (d[0] * r[0] + d[1] * r[1] + d[2] * r[2]) / zc * k - float(persp.get("sx", 0.0))
	var yc: float = (d[0] * u[0] + d[1] * u[1] + d[2] * u[2]) / zc * k - float(persp.get("sy", 0.0))
	return [(xc + 0.5) * w, h / 2.0 - yc * w]


## `project` of a 3-point at the plate's frame size.
static func proj(c: Dictionary, p: Array) -> Array:
	return project(c, float(p[0]), float(p[1]), float(p[2]), frame_w(), frame_h())
