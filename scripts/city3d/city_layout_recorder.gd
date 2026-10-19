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
	var p := CityPlan.for_seed(city_seed)
	if p.a2 != null:
		_record_a2(p, box)
		return
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


## CITY-A2 step 1: the lots of `box` from the seed's A2 subdivision (CityA2Builder.lots_for), in the same draw order
## (diagonals i + j, then i) and the same record forms; a building is recorded at its front lot. Lots past the city
## rect hold nothing.
func _record_a2(p: CityPlan, box: Rect2i) -> void:
	var cfg := CityPlan.plan_config()
	var lots := CityA2Builder.lots_for(p, cfg, HQ_LOTS, FIST_TERRITORY, 1.0 / CityView3D.CONFIG.height_px_bu)
	var rects := p.hq_rects(HQ_LOTS)
	var ids: Array = rects.keys()
	IdSort.sort_ids(ids)
	for cid: StringName in ids:
		if cid != FIST_TERRITORY and (rects[cid] as Rect2i).intersects(box):
			hqs[cid] = rects[cid]
	var R: Rect2i = lots["rect"]
	var b := box.intersection(R)
	if b.size.x <= 0 or b.size.y <= 0:
		return
	var w := R.size.x
	var streets_in: Dictionary = lots["streets"]
	var plazas_in: Dictionary = lots["plazas"]
	var front: Dictionary = lots["front"]
	var cells: Array = lots["cells"]
	for s in range(b.position.x + b.position.y, b.end.x + b.end.y):
		for i in range(b.position.x, b.end.x):
			var j := s - i
			if j < b.position.y or j >= b.end.y:
				continue
			var k := (j - R.position.y) * w + (i - R.position.x)
			if plazas_in.has(k):
				plazas.append({"lot": Vector2i(i, j), "terr": plazas_in[k]})
			elif streets_in.has(k):
				streets.append((streets_in[k] as Dictionary).duplicate())
			elif front.has(k):
				for e: Dictionary in cells[front[k]]["extrusions"]:
					extrusions.append(e.duplicate())


## Lot point of a placement-space point (the painter camera: origin at lot (0, 0)).
func _lots_of(p: Vector2) -> Vector2:
	var d := p.x / TILE_A
	var s := p.y / TILE_B
	return Vector2((s + d) * 0.5, (s - d) * 0.5)
