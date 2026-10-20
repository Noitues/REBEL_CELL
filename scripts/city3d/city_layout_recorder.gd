class_name CityLayoutRecorder
extends RefCounted
## ART-1 1D, CITY-A2 step 2: reads the game's city layout (a seed's A2 subdivision, CityA2Builder.lots_for) one box of lots
## at a time, without drawing it: every building extrusion (footprint, base, height, taper, ink) and every street lot
## (lane colour, traffic), in lot space. CITY-A2 step 2 made it a pure recorder of A2 lots (it extended NeonCity and ran
## its placement mode before): RefCounted, safe on a worker thread, nothing to free. A fallback plan (A2 could not be
## made) records nothing.

## Recorded extrusions: {"base": PackedVector2Array (lots), "z0", "h" (height px), "taper",
## "ink": Color, "terr": StringName, "key": int, "cell": Rect2i}.
var extrusions: Array[Dictionary] = []
## Recorded street lots: {"lot": Vector2i, "along_i", "along_j", "col": Color, "traffic"}.
var streets: Array[Dictionary] = []
## Plaza (HQ) lots: {"lot": Vector2i, "terr": StringName}.
var plazas: Array[Dictionary] = []
## HQ rects in the box: corp id -> Rect2i.
var hqs: Dictionary = {}
## The city seed whose layout is recorded.
var city_seed: int = 0


## Records every lot of `box` (lots) from the seed's A2 subdivision, in draw order (diagonals i + j, then i), a building
## at its front lot; lots past the city rect hold nothing.
func record(box: Rect2i) -> void:
	var p := CityPlan.for_seed(city_seed)
	if p.a2 == null:
		return
	var cfg := CityPlan.plan_config()
	var lots := CityA2Builder.lots_for(p, cfg, NeonCity.HQ_LOTS, NeonCity.FIST_TERRITORY, 1.0 / CityView3D.CONFIG.height_px_bu)
	var rects := p.hq_rects(NeonCity.HQ_LOTS)
	var ids: Array = rects.keys()
	IdSort.sort_ids(ids)
	for cid: StringName in ids:
		if cid != NeonCity.FIST_TERRITORY and (rects[cid] as Rect2i).intersects(box):
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
