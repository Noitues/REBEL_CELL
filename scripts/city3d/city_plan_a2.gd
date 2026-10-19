class_name CityPlanA2
extends RefCounted
## CITY-A2 step 1 (designer ruling D3, 2026-10-19): the art-pass planner city `city_A2.json` (schema v1, metres, origin =
## map centre, +X east, +Y north), loaded and validated as plain data. The plan is hand-made (fixed coordinates):
## every campaign's city uses its districts, coast, terrain, roads and rails; CityA2Builder lays a seed's lots,
## buildings, HQ spots and Site headings inside it. Pure: no Node, no RNG. Loaded once per path (`shared`).
##
## Districts: {"id": StringName (A2 id: centre, halcyon, ...), "name": String, "colour": Color, "polygon":
## PackedVector2Array (m), "centre": Vector2 (m), "hq": Vector2 (m; the Old City has none: Vector2.INF)}.

## The road classes of schema v1, widest first (CityA2Raster ranks a lot's road by this order).
const ROAD_CLASSES: Array[StringName] = [&"ring", &"motorway", &"truck", &"arterial", &"collector"]
const SCHEMA_VERSION := 1

var path: String = ""
## What failed to load or validate (empty = the plan is usable).
var errors: PackedStringArray = PackedStringArray()
var districts: Array[Dictionary] = []
## The open sea (m).
var ocean: PackedVector2Array = PackedVector2Array()
## Lakes (m).
var lakes: Array[PackedVector2Array] = []
## Rivers and canals: {"name", "kind": StringName, "polyline": PackedVector2Array (m), "width": Vector2 (start, end m)}.
var rivers: Array[Dictionary] = []
## Hills, A2's Gaussians: {"centre": Vector2 (m), "sigma": Vector2 (m), "height": float (m), "rotation": float (rad)}.
var hills: Array[Dictionary] = []
## Roads: {"id": StringName, "name", "class": StringName, "width": float (m), "polyline": PackedVector2Array (m;
## a closed road repeats its first point last)}.
var roads: Array[Dictionary] = []
## Neighbourhoods: {"name", "kind": StringName, "centre": Vector2 (m), "radius": float (m)}.
var neighbourhoods: Array[Dictionary] = []
## Parks (m).
var parks: Array[PackedVector2Array] = []
var old_city_centre: Vector2 = Vector2.ZERO

static var _shared: Dictionary = {}
static var _mutex: Mutex = Mutex.new()


## The plan at `p_path`, loaded once per process (thread-safe).
static func shared(p_path: String) -> CityPlanA2:
	_mutex.lock()
	var p: CityPlanA2 = _shared.get(p_path)
	if p == null:
		p = load_path(p_path)
		_shared[p_path] = p
	_mutex.unlock()
	return p


## A fresh load of `p_path` (errors in `errors`).
static func load_path(p_path: String) -> CityPlanA2:
	var p := CityPlanA2.new()
	p.path = p_path
	var f := FileAccess.open(p_path, FileAccess.READ)
	if f == null:
		p.errors.append("city_a2: cannot open %s" % p_path)
		return p
	var data: Variant = JSON.parse_string(f.get_as_text())
	if not data is Dictionary:
		p.errors.append("city_a2: %s is not a JSON object" % p_path)
		return p
	p.errors = validate(data)
	if p.errors.is_empty():
		p._read(data)
	return p


## The problems of a parsed city_A2.json (empty = valid): schema version and unit, seven districts with unique ids,
## polygons and colours (every one but the Old City with an HQ position), the ocean polygon, hills, and roads with unique
## ids, a known class, a positive width and a polyline.
static func validate(d: Dictionary) -> PackedStringArray:
	var out := PackedStringArray()
	var meta: Dictionary = d.get("meta", {})
	if int(meta.get("version", -1)) != SCHEMA_VERSION or String(meta.get("unit", "")) != "metre":
		out.append("city_a2: meta must be version %d, unit metre" % SCHEMA_VERSION)
	if not _is_pair(meta.get("old_city_centre_m")):
		out.append("city_a2: meta.old_city_centre_m missing")
	var ds: Array = d.get("districts", [])
	var ids := {}
	var no_hq := 0
	for di: Variant in ds:
		if not di is Dictionary:
			out.append("city_a2: a district is not an object")
			continue
		var id := String(di.get("id", ""))
		if id == "" or ids.has(id):
			out.append("city_a2: district id '%s' empty or repeated" % id)
		ids[id] = true
		if not _is_poly(di.get("polygon")):
			out.append("city_a2: district %s polygon needs 3+ [x, y] points" % id)
		var col: Variant = di.get("colour_rgb")
		if not (col is Array and (col as Array).size() == 3):
			out.append("city_a2: district %s colour_rgb must be [r, g, b]" % id)
		if di.has("hq_position"):
			if not _is_pair(di["hq_position"]):
				out.append("city_a2: district %s hq_position must be [x, y]" % id)
		else:
			no_hq += 1
	if ds.size() != 7 or no_hq != 1:
		out.append("city_a2: 7 districts expected, exactly one (the Old City) without an HQ (got %d, %d)" % [ds.size(), no_hq])
	var terrain: Dictionary = d.get("terrain", {})
	if not _is_poly(terrain.get("ocean_polygon")):
		out.append("city_a2: terrain.ocean_polygon needs 3+ points")
	for h: Variant in terrain.get("hills", []):
		if not (h is Dictionary and _is_pair(h.get("centre")) and float(h.get("sigma_x_m", 0.0)) > 0.0
				and float(h.get("sigma_y_m", 0.0)) > 0.0 and h.has("height_m")):
			out.append("city_a2: a hill needs centre, sigma_x_m > 0, sigma_y_m > 0, height_m")
	var rids := {}
	var rs: Array = d.get("roads", [])
	if rs.is_empty():
		out.append("city_a2: no roads")
	for r: Variant in rs:
		if not r is Dictionary:
			out.append("city_a2: a road is not an object")
			continue
		var rid := String(r.get("id", ""))
		if rid == "" or rids.has(rid):
			out.append("city_a2: road id '%s' empty or repeated" % rid)
		rids[rid] = true
		if not StringName(String(r.get("class", ""))) in ROAD_CLASSES:
			out.append("city_a2: road %s class '%s' unknown" % [rid, r.get("class", "")])
		if float(r.get("width_m", 0.0)) <= 0.0:
			out.append("city_a2: road %s width_m must be > 0" % rid)
		var pl: Variant = r.get("polyline")
		if not (pl is Array and (pl as Array).size() >= 2 and _is_pair(pl[0])):
			out.append("city_a2: road %s polyline needs 2+ points" % rid)
	return out


## The district whose id is `id`, or {}.
func district(id: StringName) -> Dictionary:
	for d in districts:
		if d["id"] == id:
			return d
	return {}


func _read(d: Dictionary) -> void:
	old_city_centre = _v(d["meta"]["old_city_centre_m"])
	for di: Dictionary in d["districts"]:
		var c: Array = di["colour_rgb"]
		districts.append({"id": StringName(String(di["id"])), "name": String(di.get("name", "")),
			"colour": Color8(int(c[0]), int(c[1]), int(c[2])), "polygon": _poly(di["polygon"]),
			"centre": _v(di["centre"]) if _is_pair(di.get("centre")) else Vector2.ZERO,
			"hq": _v(di["hq_position"]) if di.has("hq_position") else Vector2.INF})
	var t: Dictionary = d["terrain"]
	ocean = _poly(t["ocean_polygon"])
	for l: Variant in t.get("lakes", []):
		if l is Dictionary and _is_poly(l.get("polygon")):
			lakes.append(_poly(l["polygon"]))
	for r: Variant in t.get("rivers", []):
		if r is Dictionary and r.get("polyline") is Array and (r["polyline"] as Array).size() >= 2:
			rivers.append({"name": String(r.get("name", "")), "kind": StringName(String(r.get("kind", "river"))),
				"polyline": _poly(r["polyline"]), "width": Vector2(float(r.get("width_start_m", 0.0)), float(r.get("width_end_m", 0.0)))})
	for h: Dictionary in t.get("hills", []):
		hills.append({"centre": _v(h["centre"]), "sigma": Vector2(float(h["sigma_x_m"]), float(h["sigma_y_m"])),
			"height": float(h["height_m"]), "rotation": float(h.get("rotation_rad", 0.0))})
	for r: Dictionary in d["roads"]:
		roads.append({"id": StringName(String(r["id"])), "name": String(r.get("name", "")), "class": StringName(String(r["class"])),
			"width": float(r["width_m"]), "polyline": _poly(r["polyline"])})
	for n: Variant in d.get("neighbourhoods", []):
		if n is Dictionary and _is_pair(n.get("centre")):
			neighbourhoods.append({"name": String(n.get("name", "")), "kind": StringName(String(n.get("kind", ""))),
				"centre": _v(n["centre"]), "radius": float(n.get("radius_m", 0.0))})
	for pk: Variant in d.get("parks", []):
		if pk is Dictionary and _is_poly(pk.get("polygon")):
			parks.append(_poly(pk["polygon"]))


static func _is_pair(v: Variant) -> bool:
	return v is Array and (v as Array).size() >= 2 and (v[0] is float or v[0] is int) and (v[1] is float or v[1] is int)


static func _is_poly(v: Variant) -> bool:
	return v is Array and (v as Array).size() >= 3 and _is_pair(v[0])


static func _v(a: Array) -> Vector2:
	return Vector2(float(a[0]), float(a[1]))


static func _poly(a: Array) -> PackedVector2Array:
	var out := PackedVector2Array()
	for p: Array in a:
		out.append(_v(p))
	return out
