class_name CityLayoutRuler
extends RefCounted
## NA-11: applies the layout rules (frontage of at least 6 floors, 8 BU border streets, the street r2 height passes) to the
## game's fixed city. "Fixed" (ruling NA-11-3): every link of every corporation Grid counts as a border street whatever its state,
## so the city is laid out once per seed and never re-laid out as links open. Pure on its inputs (no RNG beyond the art streams
## inside `NetrunArtLayoutRules`); HQ stand-ins are exempt and keep their rects (HQ rects are exclusive).

## The model's prisms after the rules; returns the number of parts changed. `corps` are the corporations (with a Grid) whose
## links make the net, `points_of` maps a corporation to its Site layout points (Site id -> lot point).
static func apply(model: CityModel, corps: Array, points_of: Callable) -> int:
	var job := make_job(model, corps, points_of)
	if job.is_empty():
		return 0
	run_job(job)
	return land_job(model, job)


## The rules' inputs: the model and the corporations (cheap, main thread). `run_job` does all the work.
static func make_job(model: CityModel, corps: Array, points_of: Callable) -> Dictionary:
	return {"model": model, "corps": corps, "points_of": points_of}


## Runs the rules and plans the write-back (`job["plan"]`, empty with no links). Reads the model and the corporations,
## writes only the job: safe on a worker thread while the main thread leaves the model alone.
static func run_job(job: Dictionary) -> void:
	var model: CityModel = job["model"]
	var cfg := model.cfg
	var city := NetrunArtExport.city_json(model.city_seed, cfg.lot_bu, cfg.district_centre, model.prisms, model.streets,
		model.plazas, model.hqs)
	var net := fixed_net(model.city_seed, cfg, job["corps"], job["points_of"])
	if (net["links"] as Array).is_empty():
		job["plan"] = {}
		return
	var ruled := NetrunArtLayoutRules.apply_rules(city, net, {}, "all")
	job["plan"] = plan_write_back(model, city, ruled)


## Applies a run job to `model` (main thread, a few ms); returns the count of prisms changed.
static func land_job(model: CityModel, job: Dictionary) -> int:
	return apply_plan(model, job["plan"])


## The fixed net (`net.json` shape): one node per Site (id "<corp>:<site>"), one `open` link per Grid link (locked ones too),
## each a straight 2-point polyline, sorted by `(a, b)`.
static func fixed_net(city_seed: int, cfg: CityConfig, corps: Array, points_of: Callable) -> Dictionary:
	var nodes: Array = []
	var links: Array = []
	var ids: Array = []
	for corp: CorporationData in corps:
		ids.append(corp.id)
	IdSort.sort_ids(ids)
	var by_id: Dictionary = {}
	for corp: CorporationData in corps:
		by_id[corp.id] = corp
	for cid: StringName in ids:
		var corp: CorporationData = by_id[cid]
		var pts: Dictionary = points_of.call(corp)
		var seen: Dictionary = {}
		for sd in corp.city_grid.sites:
			if sd == null or not pts.has(sd.id):
				continue
			nodes.append({"id": "%s:%s" % [cid, sd.id], "lot": NetrunArtExport.plan_point(pts[sd.id], cfg.lot_bu, cfg.district_centre),
				"state": "corporate"})
			for l: StringName in sd.links + sd.locked_links:
				if pts.has(l):
					seen[GridState.link_key(sd.id, l)] = true
		var keys: Array = seen.keys()
		keys.sort()
		for k: String in keys:
			var ab := k.split("|")
			var pa: Array = NetrunArtExport.plan_point(pts[StringName(ab[0])], cfg.lot_bu, cfg.district_centre)
			var pb: Array = NetrunArtExport.plan_point(pts[StringName(ab[1])], cfg.lot_bu, cfg.district_centre)
			links.append({"a": "%s:%s" % [cid, ab[0]], "b": "%s:%s" % [cid, ab[1]], "state": "open", "pts": [pa, pb]})
	return {"version": NetrunArtExport.VERSION, "layout_seed": ArtSeed.u64_str(city_seed), "nodes": nodes, "links": links}


## Writes the ruled parts (height, base polygon) of non-HQ buildings back to `model.prisms` and refreshes the chunk tops and
## boxes. `city` is the unruled city (the part order), `ruled` the result. Returns the count of prisms changed.
static func write_back(model: CityModel, city: Dictionary, ruled: Dictionary) -> int:
	return apply_plan(model, plan_write_back(model, city, ruled))


## The edits `write_back` makes, without making them: `{"edits": [[prism index, height, poly], ...], "tops": {chunk key:
## new top}}`. Reads the model only.
static func plan_write_back(model: CityModel, city: Dictionary, ruled: Dictionary) -> Dictionary:
	var by_bid: Dictionary = {}
	for i in model.prisms.size():
		var pr: Dictionary = model.prisms[i]
		if bool(pr.get("hq", false)):
			continue
		var cell: Rect2i = pr["cell"]
		var bid := "%d:%d" % [cell.position.x, cell.position.y]
		if not by_bid.has(bid):
			by_bid[bid] = []
		(by_bid[bid] as Array).append(i)
	var ruled_by: Dictionary = {}
	for b: Dictionary in ruled["buildings"]:
		ruled_by[b["bid"]] = b
	var edits: Array = []
	var new_h: Dictionary = {}
	var touched: Dictionary = {}
	for ob: Dictionary in city["buildings"]:
		var bid: String = ob["bid"]
		if bool(ob["hq"]) or not by_bid.has(bid):
			continue
		var idx: Array = by_bid[bid]
		# city_json sorts the parts by (z0, recorded order); the recorded order is the prism index order
		idx.sort_custom(func(x: int, y: int) -> bool:
			var zx: float = model.prisms[x]["y0"]
			var zy: float = model.prisms[y]["y0"]
			return zx < zy if zx != zy else x < y)
		var parts: Array = (ruled_by[bid] as Dictionary)["parts"]
		var old: Array = ob["parts"]
		for i in mini(idx.size(), parts.size()):
			if parts[i] == old[i]:
				continue
			var poly := PackedVector2Array()
			for q: Array in parts[i]["poly"]:
				poly.append(Vector2(float(q[0]), -float(q[1])))
			edits.append([idx[i], float(parts[i]["h"]), poly])
			new_h[idx[i]] = float(parts[i]["h"])
			touched[model.prisms[idx[i]]["chunk"]] = true
	var tops: Dictionary = {}
	for key: Vector2i in touched:
		var top := 0.0
		for pi: int in model.chunks[key]["prisms"]:
			var h: float = new_h.get(pi, float(model.prisms[pi]["h"]))
			top = maxf(top, float(model.prisms[pi]["y0"]) + h)
		tops[key] = top
	return {"edits": edits, "tops": tops}


## Makes the edits of `plan` (`plan_write_back`); returns the count of prisms changed.
static func apply_plan(model: CityModel, plan: Dictionary) -> int:
	if plan.is_empty():
		return 0
	for e: Array in plan["edits"]:
		var pr: Dictionary = model.prisms[e[0]]
		pr["h"] = e[1]
		pr["poly"] = e[2]
	for key: Vector2i in plan["tops"]:
		var ch: Dictionary = model.chunks[key]
		ch.erase("box")
		ch["top"] = plan["tops"][key]
	return (plan["edits"] as Array).size()
