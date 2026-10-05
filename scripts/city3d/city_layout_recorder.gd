class_name CityLayoutRecorder
extends NeonCity
## ART-1 1D: reads the game's own city layout (NeonCity's streets, lots, territories,
## buildings and HQ lots, same seed) without drawing it: every building extrusion
## (footprint, base, height, taper, ink) and every street lot (lane colour, traffic), in
## lot space. The successor of the round 6 `city_export_probe.gd` the concept rounds were
## built from. Runs NeonCity's placement mode (nothing is emitted); game code untouched.
## Round 34 lock (concept `grid27.patch`): the Cell's district keeps the normal street
## grid, so the fist roads are not laid out.

## Recorded extrusions: {"base": PackedVector2Array (lots), "z0", "h" (height px), "taper",
## "ink": Color, "terr": StringName, "key": int, "cell": Rect2i}.
var extrusions: Array[Dictionary] = []
## Recorded street lots: {"lot": Vector2i, "along_i", "along_j", "col": Color, "traffic"}.
var streets: Array[Dictionary] = []
## Plaza (HQ) lots: {"lot": Vector2i, "terr": StringName}.
var plazas: Array[Dictionary] = []
## HQ rects in the box: corp id -> Rect2i.
var hqs: Dictionary = {}

var _cell: Rect2i = Rect2i()


func _build_fist() -> void:
	_fist_segs.clear()
	_fist_hull.clear()
	_fist_cache.clear()
	_fist_box = Rect2()


func _building(cell: Rect2i) -> void:
	_cell = cell
	super._building(cell)


func _extrude(base: PackedVector2Array, z0: float, h: float, top_scale: float, fill: Color, ink: Color, lit: float = 0.2, key: int = 0) -> PackedVector2Array:
	var lots := PackedVector2Array()
	for p in base:
		lots.append(_lots_of(p))
	extrusions.append({"base": lots, "z0": z0, "h": h, "taper": top_scale, "ink": ink, "terr": _terr, "key": key,
		"cell": _cell})
	return super._extrude(base, z0, h, top_scale, fill, ink, lit, key)


## Records every lot of `box` (lots), in draw order.
func record(box: Rect2i) -> void:
	_placing = true
	_painter = true
	_camera()
	_prepare_build()
	for cid: StringName in _hq_rects:
		var r: Rect2i = _hq_rects[cid]
		if cid != FIST_TERRITORY and r.intersects(box):
			hqs[cid] = r
	for s in range(box.position.x + box.position.y, box.end.x + box.end.y):
		for i in range(box.position.x, box.end.x):
			var j := s - i
			if j < box.position.y or j >= box.end.y:
				continue
			_apply_context(_territory_pair(i, j))
			_infl = 0.0
			var hq := _hq_at(i, j)
			if hq != &"":
				plazas.append({"lot": Vector2i(i, j), "terr": hq})
				continue
			if _is_street_lot(i, j):
				var ai := _street_i.has(i)
				var aj := _street_j.has(j)
				var rec := {"lot": Vector2i(i, j), "along_i": ai, "along_j": aj, "col": Color.BLACK, "traffic": 0.0}
				if not (ai and aj):
					rec["col"] = _street_ink(i if ai else 0, j if aj else 0)
					rec["traffic"] = _traffic(i, j, ai)
				streets.append(rec)
				continue
			_lot(i, j)


## Lot point of a placement-space point (the painter camera: origin at lot (0, 0)).
func _lots_of(p: Vector2) -> Vector2:
	var d := p.x / TILE_A
	var s := p.y / TILE_B
	return Vector2((s + d) * 0.5, (s - d) * 0.5)
