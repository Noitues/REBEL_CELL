extends NeonCity
## Design lab (round 6 restyle): a NeonCity that records what it would draw instead of
## drawing it. Every extrusion (footprint, base lift, height, taper, fill, ink), the raw
## decoration the HQs add, the streets with their neon ink and traffic, the plazas and
## the fist roads, each tagged with the building or HQ it belongs to and kept in draw
## order. Used only by tools/design_lab/city_export.gd; game code is untouched.

var prims: Array = []
var ctxs: Array = []
var streets: Array = []
var plazas: Array = []
var _ctx: int = -1
var _mode: String = ""


func _c(c: Color) -> Array:
	return [snappedf(c.r, 0.001), snappedf(c.g, 0.001), snappedf(c.b, 0.001), snappedf(c.a, 0.001)]


func _pts(p: PackedVector2Array) -> Array:
	var out := []
	for q in p:
		out.append(snappedf(q.x, 0.1))
		out.append(snappedf(q.y, 0.1))
	return out


func _new_ctx(d: Dictionary) -> void:
	ctxs.append(d)
	_ctx = ctxs.size() - 1


func _extrude(base: PackedVector2Array, z0: float, h: float, top_scale: float, fill: Color, ink: Color, lit: float = 0.2, key: int = 0) -> PackedVector2Array:
	var n := base.size()
	var c := Vector2.ZERO
	for p in base:
		c += p
	c /= n
	var top := PackedVector2Array()
	for p in base:
		top.append(c + (p - c) * top_scale + Vector2(0, -z0 - h))
	prims.append({"t": "ext", "b": _pts(base), "z0": snappedf(z0, 0.1), "h": snappedf(h, 0.1), "ts": snappedf(top_scale, 0.001),
		"fill": _c(fill), "ink": _c(ink), "lit": snappedf(lit, 0.01), "key": key, "ctx": _ctx})
	return top


func _raw(kind: String, pts: PackedVector2Array, cols: Array) -> void:
	if _mode != "standing":
		return
	prims.append({"t": kind, "p": _pts(pts), "c": cols, "ctx": _ctx})


func _tri(a: Vector2, b: Vector2, c: Vector2, ca: Color, cb: Color, cc: Color) -> void:
	_raw("tri", PackedVector2Array([a, b, c]), [_c(ca)])


func _quad(a: Vector2, b: Vector2, c: Vector2, d: Vector2, ca: Color, cb: Color, cc: Color, cd: Color) -> void:
	_raw("quad", PackedVector2Array([a, b, c, d]), [_c(ca), _c(cc)])


func _poly(pts: PackedVector2Array, col: Color) -> void:
	_raw("poly", pts, [_c(col)])


func _ink_line(a: Vector2, b: Vector2, col: Color, width: float = 1.3, glow: bool = true) -> void:
	if _mode != "standing":
		return
	prims.append({"t": "ink", "p": _pts(PackedVector2Array([a, b])), "c": [_c(col)], "w": snappedf(width, 0.01),
		"glow": glow, "ctx": _ctx})


func _street(i: int, j: int, along_i: bool, along_j: bool) -> void:
	var rec := {"i": i, "j": j, "ai": along_i, "aj": along_j, "p": _pts(_rect_pts(i, j, i + 1, j + 1))}
	if not (along_i and along_j):
		var col := _street_ink(i if along_i else 0, j if along_j else 0)
		var a := _iso(i + 0.5, j) if along_i else _iso(i, j + 0.5)
		var b := _iso(i + 0.5, j + 1) if along_i else _iso(i + 1, j + 0.5)
		rec["col"] = _c(col)
		rec["traffic"] = snappedf(_traffic(i, j, along_i), 0.001)
		rec["ab"] = _pts(PackedVector2Array([a, b]))
	streets.append(rec)
	var m := _mode
	_mode = "street"
	super._street(i, j, along_i, along_j)  # for its traffic trails (its strokes are not recorded)
	_mode = m


func _plaza(i: int, j: int) -> void:
	plazas.append({"i": i, "j": j, "p": _pts(_rect_pts(i, j, i + 1, j + 1)), "terr": String(_terr)})


func _fist_roads() -> void:
	pass  # exported as segments (see city_export.gd)


func _building(cell: Rect2i) -> void:
	var shape := _pick_shape(cell.position.x, cell.position.y)
	_new_ctx({"kind": "bld", "terr": String(_terr), "next": String(_terr_next), "border": snappedf(_border, 0.01),
		"shape": shape, "cell": [cell.position.x, cell.position.y, cell.size.x, cell.size.y],
		"base": _pts(PackedVector2Array([_iso(cell.position.x + cell.size.x * 0.5, cell.position.y + cell.size.y * 0.5)]))})
	_mode = "standing"
	super._building(cell)
	_ctx = -1


func _hq(corp: StringName, rect: Rect2i) -> void:
	_new_ctx({"kind": "hq", "terr": String(corp), "rect": [rect.position.x, rect.position.y, rect.size.x, rect.size.y],
		"base": _pts(PackedVector2Array([_iso(rect.position.x + HQ_LOTS * 0.5, rect.position.y + HQ_LOTS * 0.5)]))})
	_mode = "standing"
	super._hq(corp, rect)
	_ctx = -1


func _sign(at: Vector2, text: String, col: Color) -> void:
	prims.append({"t": "sign", "p": _pts(PackedVector2Array([at])), "text": text, "c": [_c(col)], "ctx": _ctx})


## Runs the build passes (ground, then standing) with recording on.
func record() -> void:
	_camera()
	_prepare_build()
	_order_lots()
	_mode = "ground"
	_pass_ground(0, _lot_list.size())
	_infl = 0.0
	_mode = "standing"
	_pass_standing(0, _lot_list.size())


func export_dict() -> Dictionary:
	var fist := []
	for sg in _fist_segs:
		fist.append(_pts(sg))
	var trails := []
	for t in _trails:
		trails.append({"a": _pts(PackedVector2Array([t["a"]])), "b": _pts(PackedVector2Array([t["b"]])), "col": _c(t["color"]),
			"traffic": snappedf(float(t.get("traffic", 0.0)), 0.01)})
	var beacons := []
	for b in _beacons:
		beacons.append({"p": _pts(PackedVector2Array([b["pos"]])), "col": _c(b["color"])})
	var lights := []
	for l in _lights:
		var rec := {}
		for k in l:
			var v: Variant = l[k]
			if v is Vector2:
				rec[k] = [snappedf(v.x, 0.1), snappedf(v.y, 0.1)]
			elif v is Color:
				rec[k] = _c(v)
			elif v is float or v is int or v is bool or v is String:
				rec[k] = v
		lights.append(rec)
	var terr := []
	for t in TERRITORIES:
		var at: Vector2 = t["at"]
		terr.append({"id": String(t["id"]), "at": [at.x, at.y], "screen": _pts(PackedVector2Array([_iso(at.x + HQ_LOTS * 0.5, at.y + HQ_LOTS * 0.5)])),
			"color": _c(Palette.corp_color(t["id"])) if t["id"] != &"" else [1, 1, 1, 1]})
	return {"size": [size.x, size.y], "camera": [_ox, _oy], "tile": [TILE_A, TILE_B], "seed": city_seed,
		"colors": {"ground": _c(GROUND), "street": _c(STREET), "face_light": _c(FACE_LIGHT), "night_sky": _c(Palette.NIGHT_SKY),
			"fist": _c(Palette.corp_color(FIST_TERRITORY))},
		"shapes": Shape.keys(), "territories": terr, "contexts": ctxs, "prims": prims, "streets": streets, "plazas": plazas,
		"fist": fist, "fist_half": FIST_ROAD_HALF, "trails": trails, "beacons": beacons, "lights": lights}
